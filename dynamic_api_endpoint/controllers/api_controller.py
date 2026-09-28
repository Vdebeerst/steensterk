import ast
import json
import logging
import time
from odoo import http, fields
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class DynamicApiController(http.Controller):

    def _json_response(self, data, status=200):
        """Return a JSON response."""
        body = json.dumps(data, default=str, indent=2)
        return Response(body, status=status, content_type='application/json')

    def _authenticate(self, endpoint):
        """Validate API key and return the key record or error response."""
        if endpoint.auth_type == 'none':
            return None

        api_key = (request.httprequest.headers.get('X-API-Key')
                   or request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
                   or request.params.get('api_key'))

        if not api_key:
            return self._json_response(
                {'error': 'Missing API key. Provide X-API-Key header or api_key parameter.'},
                status=401
            )

        key_rec = request.env['api.key'].sudo().search([
            ('key', '=', api_key),
            ('active', '=', True),
        ], limit=1)

        if not key_rec:
            return self._json_response({'error': 'Invalid API key.'}, status=401)

        # Check endpoint restriction
        if key_rec.endpoint_ids and endpoint.id not in key_rec.endpoint_ids.ids:
            return self._json_response(
                {'error': 'API key not authorized for this endpoint.'},
                status=403
            )

        # Rate limiting
        if key_rec.rate_limit > 0:
            one_min_ago = fields.Datetime.subtract(fields.Datetime.now(), minutes=1)
            recent_calls = request.env['api.log'].sudo().search_count([
                ('api_key_id', '=', key_rec.id),
                ('create_date', '>=', one_min_ago),
            ])
            if recent_calls >= key_rec.rate_limit:
                return self._json_response(
                    {'error': 'Rate limit exceeded. Try again later.'},
                    status=429
                )

        # Update usage stats
        key_rec.sudo().write({
            'last_used': fields.Datetime.now(),
            'call_count': key_rec.call_count + 1,
        })

        return key_rec

    def _get_endpoint(self, route_path):
        """Find active endpoint by route path."""
        endpoint = request.env['api.endpoint'].sudo().search([
            ('route', '=', route_path),
            ('state', '=', 'active'),
        ], limit=1)
        return endpoint

    def _execute_custom_serialize(self, code, records, env):
        """Safely execute custom Python serialization code."""
        local_vars = {'records': records, 'env': env, 'result': None}
        try:
            exec(code.strip(), {"__builtins__": {
                'len': len, 'str': str, 'int': int, 'float': float,
                'bool': bool, 'list': list, 'dict': dict, 'tuple': tuple,
                'range': range, 'enumerate': enumerate, 'zip': zip,
                'sorted': sorted, 'min': min, 'max': max, 'sum': sum,
                'round': round, 'abs': abs, 'isinstance': isinstance,
                'True': True, 'False': False, 'None': None,
            }}, local_vars)
        except Exception as e:
            _logger.error("Custom serialize code error for field: %s", e)
            return [{'id': r.id, 'name': r.display_name} for r in records]
        return local_vars.get('result') or [{'id': r.id, 'name': r.display_name} for r in records]

    def _serialize_record(self, record, field_names, endpoint=None):
        """Convert record to dict with given fields."""
        # Build sub-field mapping and custom code mapping from endpoint configuration
        sub_field_map = {}
        custom_code_map = {}
        if endpoint and endpoint.field_ids:
            for ef in endpoint.field_ids:
                if ef.field_type == 'many2one' and ef.sub_field_ids:
                    sub_field_map[ef.field_name] = ef.sub_field_ids.mapped('name')
                if ef.field_type in ('many2many', 'one2many') and ef.custom_serialize_code:
                    custom_code_map[ef.field_name] = ef.custom_serialize_code

        data = {}
        for fname in field_names:
            if fname not in record._fields:
                continue
            field = record._fields[fname]
            value = record[fname]
            if field.type == 'many2one' and value:
                if fname in sub_field_map:
                    # Use configured sub-fields
                    sub_data = {}
                    for sf_name in sub_field_map[fname]:
                        if sf_name not in value._fields:
                            continue
                        sf = value._fields[sf_name]
                        sv = value[sf_name]
                        if sf.type == 'many2one' and sv:
                            sub_data[sf_name] = {'id': sv.id, 'name': sv.display_name}
                        elif sf.type in ('many2many', 'one2many') and sv:
                            sub_data[sf_name] = [{'id': r.id, 'name': r.display_name} for r in sv]
                        elif sf.type in ('date', 'datetime') and sv:
                            sub_data[sf_name] = str(sv)
                        elif sf.type == 'binary':
                            sub_data[sf_name] = bool(sv)
                        else:
                            sub_data[sf_name] = sv
                    data[fname] = sub_data
                else:
                    data[fname] = {'id': value.id, 'name': value.display_name}
            elif field.type in ('many2many', 'one2many') and value:
                if fname in custom_code_map:
                    data[fname] = self._execute_custom_serialize(
                        custom_code_map[fname], value, record.env)
                else:
                    data[fname] = [{'id': r.id, 'name': r.display_name} for r in value]
            elif field.type in ('date', 'datetime') and value:
                data[fname] = str(value)
            elif field.type == 'binary':
                data[fname] = bool(value)
            else:
                data[fname] = value
        return data

    def _apply_field_aliases(self, data, endpoint, reverse=False):
        """Map alias names to/from real field names."""
        alias_fields = endpoint.field_ids.filtered(lambda f: f.alias)
        if not alias_fields:
            return data
        mapped = {}
        for key, val in data.items():
            found = False
            for af in alias_fields:
                if reverse and key == af.alias:
                    mapped[af.field_name] = val
                    found = True
                    break
                elif not reverse and key == af.field_name:
                    mapped[af.alias] = val
                    found = True
                    break
            if not found:
                mapped[key] = val
        return mapped

    def _log_request(self, endpoint, method, path, req_body, resp_code, resp_body, key_rec, start_time):
        """Create log entry."""
        if not endpoint.log_requests:
            return
        request.env['api.log'].sudo().create({
            'endpoint_id': endpoint.id,
            'method': method,
            'path': path,
            'request_body': str(req_body)[:5000] if req_body else '',
            'response_code': resp_code,
            'response_body': str(resp_body)[:5000],
            'api_key_id': key_rec.id if key_rec and hasattr(key_rec, 'id') else False,
            'ip_address': request.httprequest.remote_addr,
            'duration_ms': (time.time() - start_time) * 1000,
            'status': 'success' if 200 <= resp_code < 400 else 'error',
        })

    # --- Catch-all route for /api/* ---
    @http.route(['/api/<path:endpoint_path>'], type='http', auth='public',
                methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
                csrf=False, cors='*')
    def handle_api(self, endpoint_path, **kwargs):
        """Dynamic API request handler."""
        start_time = time.time()
        route_path = f'/api/{endpoint_path}'

        # Handle OPTIONS for CORS preflight
        if request.httprequest.method == 'OPTIONS':
            return Response('', status=200, headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-API-Key, Authorization',
            })

        # Check if route ends with /<id>
        record_id = None
        base_route = route_path
        parts = route_path.rstrip('/').rsplit('/', 1)
        if len(parts) == 2 and parts[1].isdigit():
            record_id = int(parts[1])
            base_route = parts[0]

        endpoint = self._get_endpoint(base_route)
        if not endpoint:
            # Also try full path in case it was defined with ID placeholder
            endpoint = self._get_endpoint(route_path)
        if not endpoint:
            return self._json_response({'error': f'Endpoint not found: {base_route}'}, status=404)

        method = request.httprequest.method

        # Check method allowed
        method_map = {
            'GET': endpoint.method_get,
            'POST': endpoint.method_post,
            'PUT': endpoint.method_put,
            'PATCH': endpoint.method_put,
            'DELETE': endpoint.method_delete,
        }
        if not method_map.get(method):
            return self._json_response(
                {'error': f'Method {method} not allowed on this endpoint.'},
                status=405
            )

        # Authenticate
        auth_result = self._authenticate(endpoint)
        if isinstance(auth_result, Response):
            return auth_result
        key_rec = auth_result

        # Switch to API key user context if authenticated
        env = request.env
        if key_rec:
            env = request.env(user=key_rec.user_id.id)

        try:
            model = env[endpoint.model_name].sudo()
        except KeyError:
            return self._json_response({'error': f'Model {endpoint.model_name} not found.'}, status=500)

        try:
            if method == 'GET':
                resp = self._handle_get(endpoint, model, record_id, kwargs)
            elif method == 'POST':
                resp = self._handle_post(endpoint, model)
            elif method in ('PUT', 'PATCH'):
                resp = self._handle_put(endpoint, model, record_id)
            elif method == 'DELETE':
                resp = self._handle_delete(endpoint, model, record_id)
            else:
                resp = self._json_response({'error': 'Unsupported method'}, status=405)

            self._log_request(endpoint, method, route_path,
                              request.httprequest.get_data(as_text=True),
                              resp.status_code if hasattr(resp, 'status_code') else 200,
                              '', key_rec, start_time)
            return resp

        except Exception as e:
            _logger.exception("API error on %s %s", method, route_path)
            error_resp = self._json_response({'error': str(e)}, status=500)
            self._log_request(endpoint, method, route_path,
                              request.httprequest.get_data(as_text=True),
                              500, str(e), key_rec, start_time)
            return error_resp

    def _handle_get(self, endpoint, model, record_id, params):
        """Handle GET request - read records."""
        read_fields = endpoint.get_readable_fields()

        if record_id:
            record = model.browse(record_id).exists()
            if not record:
                return self._json_response({'error': 'Record not found.'}, status=404)
            data = self._serialize_record(record, read_fields, endpoint)
            data = self._apply_field_aliases(data, endpoint)
            return self._json_response({'data': data})

        # List records
        domain = ast.literal_eval(endpoint.domain or '[]')

        # Search filter from params
        search = params.get('search')
        if search:
            domain.append(('name', 'ilike', search))

        # Custom domain from params
        extra_domain = params.get('domain')
        if extra_domain:
            try:
                domain.extend(ast.literal_eval(extra_domain))
            except (ValueError, SyntaxError):
                pass

        # Pagination
        limit = min(int(params.get('limit', endpoint.default_limit)), endpoint.max_limit)
        offset = int(params.get('offset', 0))

        # Ordering
        order = params.get('order', 'id asc')

        total = model.search_count(domain)
        records = model.search(domain, limit=limit, offset=offset, order=order)

        data = []
        for rec in records:
            row = self._serialize_record(rec, read_fields, endpoint)
            row = self._apply_field_aliases(row, endpoint)
            data.append(row)

        return self._json_response({
            'data': data,
            'total': total,
            'limit': limit,
            'offset': offset,
        })

    def _handle_post(self, endpoint, model):
        """Handle POST request - create record."""
        writable_fields = endpoint.get_writable_fields()
        if not writable_fields:
            return self._json_response(
                {'error': 'No writable fields configured for this endpoint.'},
                status=400
            )

        body = request.httprequest.get_data(as_text=True)
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            return self._json_response({'error': 'Invalid JSON body.'}, status=400)

        # Map aliases back to field names
        payload = self._apply_field_aliases(payload, endpoint, reverse=True)

        # Check required fields
        for ef in endpoint.field_ids.filtered('required_on_create'):
            if ef.field_name not in payload:
                return self._json_response(
                    {'error': f'Missing required field: {ef.alias or ef.field_name}'},
                    status=400
                )

        # Filter to writable fields only
        vals = {k: v for k, v in payload.items() if k in writable_fields}

        record = model.create(vals)

        # Fire webhooks
        webhooks = request.env['api.webhook'].sudo().search([
            ('model_name', '=', endpoint.model_name),
            ('on_create', '=', True),
            ('state', '=', 'active'),
        ])
        if webhooks:
            webhooks._fire('create', record)

        read_fields = endpoint.get_readable_fields()
        data = self._serialize_record(record, read_fields, endpoint)
        data = self._apply_field_aliases(data, endpoint)
        return self._json_response({'data': data, 'id': record.id}, status=201)

    def _handle_put(self, endpoint, model, record_id):
        """Handle PUT/PATCH request - update record."""
        if not record_id:
            return self._json_response(
                {'error': 'Record ID required. Use PUT /api/.../123'},
                status=400
            )

        writable_fields = endpoint.get_writable_fields()
        if not writable_fields:
            return self._json_response(
                {'error': 'No writable fields configured for this endpoint.'},
                status=400
            )

        record = model.browse(record_id).exists()
        if not record:
            return self._json_response({'error': 'Record not found.'}, status=404)

        body = request.httprequest.get_data(as_text=True)
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            return self._json_response({'error': 'Invalid JSON body.'}, status=400)

        payload = self._apply_field_aliases(payload, endpoint, reverse=True)
        vals = {k: v for k, v in payload.items() if k in writable_fields}

        record.write(vals)

        # Fire webhooks
        webhooks = request.env['api.webhook'].sudo().search([
            ('model_name', '=', endpoint.model_name),
            ('on_write', '=', True),
            ('state', '=', 'active'),
        ])
        if webhooks:
            webhooks._fire('update', record)

        read_fields = endpoint.get_readable_fields()
        data = self._serialize_record(record, read_fields, endpoint)
        data = self._apply_field_aliases(data, endpoint)
        return self._json_response({'data': data})

    def _handle_delete(self, endpoint, model, record_id):
        """Handle DELETE request - unlink record."""
        if not record_id:
            return self._json_response(
                {'error': 'Record ID required. Use DELETE /api/.../123'},
                status=400
            )

        record = model.browse(record_id).exists()
        if not record:
            return self._json_response({'error': 'Record not found.'}, status=404)

        # Fire webhooks before delete
        webhooks = request.env['api.webhook'].sudo().search([
            ('model_name', '=', endpoint.model_name),
            ('on_unlink', '=', True),
            ('state', '=', 'active'),
        ])
        if webhooks:
            webhooks._fire('delete', record)

        record.unlink()
        return self._json_response({'message': 'Record deleted successfully.'})
