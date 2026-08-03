# Dynamic API Endpoints & Webhooks

Odoo 19 module to create fully dynamic REST API endpoints and webhooks for any Odoo model — no code required.

---

## Installation

1. Place the `dynamic_api_endpoint` folder in your Odoo addons path.
2. Update the apps list: **Settings → Apps → Update Apps List**.
3. Search for **"Dynamic API Endpoints"** and install.

---

## Quick Start

### 1. Create an API Key

Navigate to **API Manager → API Keys → Create**.

| Field | Description |
|-------|-------------|
| Name | Descriptive name (e.g. "Mobile App Key") |
| User | Odoo user context for API calls |
| Rate Limit | Max calls per minute (0 = unlimited) |
| Allowed Endpoints | Restrict key to specific endpoints (empty = all) |

The key is auto-generated on creation. Click **Regenerate Key** to get a new one.

### 2. Create an API Endpoint

Navigate to **API Manager → Endpoints → Create**.

| Field | Description |
|-------|-------------|
| Endpoint Name | Display name |
| Route Path | URL path, e.g. `/api/v1/partners` (must start with `/api/`) |
| Model | Any Odoo model (res.partner, sale.order, etc.) |
| Authentication | API Key or Public (no auth) |
| GET / POST / PUT / DELETE | Enable/disable HTTP methods |
| Domain Filter | Odoo domain to filter records, e.g. `[("active","=",True)]` |
| Default Page Size | Records per page (default: 80) |
| Max Page Size | Maximum allowed limit (default: 500) |
| Log Requests | Enable request/response logging |

#### Configure Fields

Click **Auto-Populate Fields** to load all model fields, then configure:

| Column | Description |
|--------|-------------|
| Read | Include field in GET responses |
| Write | Allow field in POST/PUT requests |
| Required on Create | Validate field is present in POST |
| API Alias | Expose field under a different name |

Click **Activate** to make the endpoint live.

### 3. Create a Webhook

Navigate to **API Manager → Webhooks → Create**.

| Field | Description |
|-------|-------------|
| Webhook Name | Display name |
| Model | Odoo model to watch |
| Target URL | External URL to receive the payload |
| Signing Secret | HMAC-SHA256 secret for `X-Webhook-Signature` header |
| On Create / On Update / On Delete | Which events trigger the webhook |
| Domain Filter | Only fire for records matching this domain |
| Payload Fields | Fields to include (empty = id, name, display_name, dates) |
| Custom Headers | Additional HTTP headers sent with each webhook |

Click **Activate**, then optionally **Test Webhook** to send a sample payload.

---

## API Reference

### Authentication

Pass your API key using one of these methods (in order of priority):

```
X-API-Key: odoo_api_abc123...
Authorization: Bearer odoo_api_abc123...
GET /api/v1/partners?api_key=odoo_api_abc123...
```

### Endpoints

All endpoints follow the pattern: `{base_url}{route_path}`

#### GET — List Records

```http
GET /api/v1/partners?limit=20&offset=0&order=name asc&search=john
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 80 | Number of records to return |
| `offset` | int | 0 | Number of records to skip |
| `order` | string | `id asc` | Sort order (e.g. `name desc`) |
| `search` | string | — | Search by name (ilike) |
| `domain` | string | — | Extra Odoo domain filter as JSON |

**Response:**

```json
{
  "data": [
    {"id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
  ],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

#### GET — Single Record

```http
GET /api/v1/partners/1
```

**Response:**

```json
{
  "data": {"id": 1, "name": "John Doe", "email": "john@example.com"}
}
```

#### POST — Create Record

```http
POST /api/v1/partners
Content-Type: application/json

{"name": "New Partner", "email": "new@example.com"}
```

**Response (201):**

```json
{
  "data": {"id": 42, "name": "New Partner", "email": "new@example.com"},
  "id": 42
}
```

#### PUT/PATCH — Update Record

```http
PUT /api/v1/partners/42
Content-Type: application/json

{"email": "updated@example.com"}
```

**Response:**

```json
{
  "data": {"id": 42, "name": "New Partner", "email": "updated@example.com"}
}
```

#### DELETE — Delete Record

```http
DELETE /api/v1/partners/42
```

**Response:**

```json
{"message": "Record deleted successfully."}
```

### Auto-Generated Documentation

```http
GET /api/docs
```

Returns a JSON listing of all active endpoints, their methods, fields, and authentication requirements.

### Incoming Webhook Receiver

```http
POST /webhook/receive/{token}
Content-Type: application/json

{"event": "payment_completed", "order_id": 123}
```

All incoming webhooks are logged automatically.

---

## Webhook Payload Format (Outgoing)

When a webhook fires, it sends a POST request with this JSON body:

```json
{
  "event": "create",
  "model": "res.partner",
  "record_id": 42,
  "data": {
    "id": 42,
    "name": "New Partner",
    "display_name": "New Partner",
    "create_date": "2026-03-11 10:30:00",
    "write_date": "2026-03-11 10:30:00"
  },
  "timestamp": "2026-03-11T10:30:00.123456"
}
```

### Webhook Signature Verification

If a signing secret is configured, each request includes:

```
X-Webhook-Signature: <HMAC-SHA256 hex digest>
```

Verify in your receiving application:

```python
import hmac, hashlib

def verify_signature(payload_body, secret, signature):
    expected = hmac.new(
        secret.encode(),
        payload_body.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Bad request (invalid JSON, missing required fields) |
| 401 | Missing or invalid API key |
| 403 | API key not authorized for this endpoint |
| 404 | Endpoint or record not found |
| 405 | HTTP method not allowed on this endpoint |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

All errors return JSON:

```json
{"error": "Description of the error"}
```

---

## CORS Support

All `/api/*` endpoints include CORS headers and respond to OPTIONS preflight requests, allowing browser-based JavaScript clients to call the API directly.

---

## Security Groups

| Group | Permissions |
|-------|-------------|
| **API User** | Read-only access to endpoints, keys, webhooks, logs |
| **API Manager** | Full CRUD access to all API configuration |

Admin user is automatically added to the API Manager group on install.

---

## Field Aliases Example

Map internal Odoo field names to cleaner API names:

| Odoo Field | API Alias | Result |
|------------|-----------|--------|
| `partner_id` | `customer` | `{"customer": {"id": 1, "name": "..."}}` |
| `date_order` | `order_date` | `{"order_date": "2026-03-11"}` |
| `amount_total` | `total` | `{"total": 1500.00}` |

Configure aliases in the endpoint's **Fields** tab.

---

## Rate Limiting

Rate limits are per API key, measured in calls per minute. When exceeded, the API returns:

```json
{"error": "Rate limit exceeded. Try again later."}
```

with HTTP status **429**.

---

## Integration Examples

### Python

```python
import requests

BASE = "https://your-odoo.com"
HEADERS = {"X-API-Key": "odoo_api_abc123..."}

# List records
resp = requests.get(f"{BASE}/api/v1/partners", headers=HEADERS, params={"limit": 10})
print(resp.json())

# Create record
resp = requests.post(f"{BASE}/api/v1/partners", headers=HEADERS,
                     json={"name": "New Partner", "email": "new@example.com"})
print(resp.json())

# Update record
resp = requests.put(f"{BASE}/api/v1/partners/42", headers=HEADERS,
                    json={"email": "updated@example.com"})
print(resp.json())

# Delete record
resp = requests.delete(f"{BASE}/api/v1/partners/42", headers=HEADERS)
print(resp.json())
```

### JavaScript (fetch)

```javascript
const BASE = "https://your-odoo.com";
const HEADERS = {
  "X-API-Key": "odoo_api_abc123...",
  "Content-Type": "application/json"
};

// List records
const list = await fetch(`${BASE}/api/v1/partners?limit=10`, { headers: HEADERS });
console.log(await list.json());

// Create record
const created = await fetch(`${BASE}/api/v1/partners`, {
  method: "POST",
  headers: HEADERS,
  body: JSON.stringify({ name: "New Partner" })
});
console.log(await created.json());
```

### cURL

```bash
# List
curl -H "X-API-Key: odoo_api_abc123..." https://your-odoo.com/api/v1/partners

# Create
curl -X POST -H "X-API-Key: odoo_api_abc123..." \
     -H "Content-Type: application/json" \
     -d '{"name": "New Partner"}' \
     https://your-odoo.com/api/v1/partners

# Update
curl -X PUT -H "X-API-Key: odoo_api_abc123..." \
     -H "Content-Type: application/json" \
     -d '{"email": "updated@example.com"}' \
     https://your-odoo.com/api/v1/partners/42

# Delete
curl -X DELETE -H "X-API-Key: odoo_api_abc123..." \
     https://your-odoo.com/api/v1/partners/42
```

---

## License

LGPL-3
