# WA Desktop Connector v0.0.7

Version 0.0.7 introduces the first real Odoo client flow while preserving all v0.0.6 tests.

## What works

- Windows registration of the `wa://` protocol.
- Parsing and validation of WA URLs.
- Rotating logs under `%APPDATA%\WA\logs`.
- Preview mode for incomplete development URLs.
- Direct HTTPS download through `download_url`.
- Odoo metadata lookup using `server` and `document_id`.
- Support for direct JSON objects and Odoo-style `{ "result": {...} }` responses.
- Relative download URLs returned by Odoo.
- Optional Bearer authentication through `access_token`.
- Same-host validation for download URLs, unless Odoo explicitly returns `allow_external_download: true`.
- Safe local filenames and automatic opening in Windows.
- `--download-only` for controlled testing.

## Existing test

```cmd
python main.py "wa://open?document_id=123&database=demo"
```

This remains a preview because no `server` or `download_url` is supplied.

## Odoo metadata flow

```cmd
python main.py --download-only "wa://open?server=https%3A%2F%2Fodoo.example.com&document_id=123&access_token=TOKEN"
```

By default the connector requests:

```text
https://odoo.example.com/wa_desktop_connector/api/document/123
```

Odoo should return either a direct JSON object or an Odoo-style `result` wrapper:

```json
{
  "filename": "Offer.pdf",
  "mime_type": "application/pdf",
  "download_url": "/wa_desktop_connector/api/document/123/content",
  "etag": "abc123",
  "modified": "2026-07-21T12:00:00Z"
}
```

A custom endpoint can be supplied with URL-encoded `metadata_path`, containing the placeholder `{document_id}`, or with a complete `metadata_url`.

## Direct download flow

```cmd
python main.py --download-only "wa://open?download_url=https%3A%2F%2Fexample.com%2Fdocument.pdf&filename=document.pdf"
```

## Data folders

- Configuration: `%APPDATA%\WA\config.ini`
- Logs: `%APPDATA%\WA\logs\wa-desktop-connector.log`
- Downloads: `%APPDATA%\WA\downloads`
