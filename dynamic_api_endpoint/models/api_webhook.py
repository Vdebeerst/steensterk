import json
import logging
import requests
import hashlib
import hmac
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ApiWebhook(models.Model):
    _name = 'api.webhook'
    _description = 'Webhook Configuration'
    _rec_name = 'name'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    _order = 'sequence, id'

    name = fields.Char(string='Webhook Name', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', store=True, readonly=True)

    # Trigger events
    on_create = fields.Boolean(string='On Create', default=True)
    on_write = fields.Boolean(string='On Update', default=False)
    on_unlink = fields.Boolean(string='On Delete', default=False)

    # Target
    target_url = fields.Char(string='Target URL', required=True,
                             help='URL to send webhook payload to')

    # Authentication
    secret = fields.Char(string='Signing Secret',
                         help='Secret key for HMAC signature in X-Webhook-Signature header')
    header_ids = fields.One2many('api.webhook.header', 'webhook_id', string='Custom Headers')

    # Payload
    field_ids = fields.Many2many('ir.model.fields', string='Fields to Include',
                                 help='Fields to include in payload. Empty = all fields')

    # Domain filter
    domain = fields.Char(string='Domain Filter', default='[]',
                         help='Only trigger for records matching this domain')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('disabled', 'Disabled'),
    ], string='Status', default='draft')

    log_ids = fields.One2many('api.log', 'webhook_id', string='Logs')

    def action_activate(self):
        self.write({'state': 'active'})

    def action_disable(self):
        self.write({'state': 'disabled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def _get_payload_fields(self, record):
        """Get field values for webhook payload."""
        if self.field_ids:
            field_names = self.field_ids.mapped('name')
        else:
            field_names = ['id', 'name', 'display_name', 'create_date', 'write_date']

        data = {}
        for fname in field_names:
            if fname not in record._fields:
                continue
            value = record[fname]
            field = record._fields[fname]
            if field.type == 'many2one' and value:
                data[fname] = {'id': value.id, 'name': value.display_name}
            elif field.type in ('many2many', 'one2many') and value:
                data[fname] = [{'id': r.id, 'name': r.display_name} for r in value]
            elif field.type in ('date', 'datetime') and value:
                data[fname] = str(value)
            elif field.type == 'binary':
                data[fname] = bool(value)
            else:
                data[fname] = value
        return data

    def _fire(self, event, records):
        """Fire webhook for given records."""
        for webhook in self.filtered(lambda w: w.state == 'active'):
            for record in records:
                # Check domain filter
                if webhook.domain and webhook.domain != '[]':
                    import ast
                    domain = ast.literal_eval(webhook.domain)
                    matching = record.filtered_domain(domain)
                    if not matching:
                        continue

                payload = {
                    'event': event,
                    'model': webhook.model_name,
                    'record_id': record.id,
                    'data': webhook._get_payload_fields(record),
                    'timestamp': fields.Datetime.now().isoformat(),
                }
                payload_str = json.dumps(payload, default=str)

                headers = {'Content-Type': 'application/json'}
                # Custom headers
                for h in webhook.header_ids:
                    headers[h.name] = h.value
                # HMAC signature
                if webhook.secret:
                    signature = hmac.new(
                        webhook.secret.encode(),
                        payload_str.encode(),
                        hashlib.sha256
                    ).hexdigest()
                    headers['X-Webhook-Signature'] = signature

                try:
                    resp = requests.post(
                        webhook.target_url,
                        data=payload_str,
                        headers=headers,
                        timeout=10,
                    )
                    self.env['api.log'].sudo().create({
                        'webhook_id': webhook.id,
                        'method': 'WEBHOOK',
                        'path': webhook.target_url,
                        'request_body': payload_str[:5000],
                        'response_code': resp.status_code,
                        'response_body': resp.text[:5000],
                        'status': 'success' if resp.ok else 'error',
                    })
                except Exception as e:
                    _logger.warning("Webhook %s failed: %s", webhook.name, e)
                    self.env['api.log'].sudo().create({
                        'webhook_id': webhook.id,
                        'method': 'WEBHOOK',
                        'path': webhook.target_url,
                        'request_body': payload_str[:5000],
                        'response_body': str(e)[:5000],
                        'status': 'error',
                    })

    def action_test_webhook(self):
        """Send a test payload."""
        self.ensure_one()
        model = self.env[self.model_name]
        record = model.search([], limit=1)
        if record:
            self._fire('test', record)
        else:
            self._fire('test', model.browse())


class ApiWebhookHeader(models.Model):
    _name = 'api.webhook.header'
    _description = 'Webhook Custom Header'

    webhook_id = fields.Many2one('api.webhook', required=True, ondelete='cascade')
    name = fields.Char(string='Header Name', required=True)
    value = fields.Char(string='Header Value', required=True)
