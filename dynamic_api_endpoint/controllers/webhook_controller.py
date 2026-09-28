import hashlib
import hmac
import json
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class WebhookReceiverController(http.Controller):
    """Controller to receive incoming webhooks from external systems."""

    @http.route('/webhook/receive/<string:token>', type='http', auth='public',
                methods=['POST'], csrf=False, cors='*')
    def receive_webhook(self, token, **kwargs):
        """Receive incoming webhook and process it."""
        body = request.httprequest.get_data(as_text=True)

        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            return Response(
                json.dumps({'error': 'Invalid JSON'}),
                status=400, content_type='application/json'
            )

        _logger.info("Received webhook with token: %s", token)

        # Log incoming webhook
        request.env['api.log'].sudo().create({
            'method': 'WEBHOOK_IN',
            'path': f'/webhook/receive/{token}',
            'request_body': body[:5000] if body else '',
            'response_code': 200,
            'status': 'success',
            'ip_address': request.httprequest.remote_addr,
        })

        return Response(
            json.dumps({'status': 'received', 'message': 'Webhook received successfully'}),
            status=200, content_type='application/json'
        )

    @http.route('/api/docs', type='http', auth='public', methods=['GET'], csrf=False)
    def api_documentation(self, **kwargs):
        """Auto-generated API documentation endpoint."""
        endpoints = request.env['api.endpoint'].sudo().search([('state', '=', 'active')])

        docs = []
        for ep in endpoints:
            methods = []
            if ep.method_get:
                methods.append('GET')
            if ep.method_post:
                methods.append('POST')
            if ep.method_put:
                methods.append('PUT')
            if ep.method_delete:
                methods.append('DELETE')

            readable = ep.get_readable_fields()
            writable = ep.get_writable_fields()

            docs.append({
                'name': ep.name,
                'route': ep.route,
                'model': ep.model_name,
                'methods': methods,
                'auth': ep.auth_type,
                'description': ep.description or '',
                'readable_fields': readable,
                'writable_fields': writable,
                'pagination': {
                    'default_limit': ep.default_limit,
                    'max_limit': ep.max_limit,
                },
            })

        result = {
            'title': 'Dynamic API Documentation',
            'version': '1.0',
            'endpoints': docs,
            'authentication': {
                'api_key': {
                    'description': 'Pass API key via X-API-Key header, Authorization: Bearer <key>, or api_key query parameter',
                },
            },
            'pagination': {
                'description': 'Use limit and offset query parameters',
            },
        }

        return Response(
            json.dumps(result, indent=2, default=str),
            status=200, content_type='application/json'
        )
