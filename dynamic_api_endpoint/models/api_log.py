from odoo import fields, models


class ApiLog(models.Model):
    _name = 'api.log'
    _description = 'API Request Log'
    _order = 'create_date desc'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    _rec_name = 'path'

    endpoint_id = fields.Many2one('api.endpoint', string='Endpoint', ondelete='set null')
    webhook_id = fields.Many2one('api.webhook', string='Webhook', ondelete='set null')
    method = fields.Char(string='Method')
    path = fields.Char(string='Path')
    request_body = fields.Text(string='Request Body')
    response_code = fields.Integer(string='Response Code')
    response_body = fields.Text(string='Response Body')
    api_key_id = fields.Many2one('api.key', string='API Key', ondelete='set null')
    ip_address = fields.Char(string='IP Address')
    duration_ms = fields.Float(string='Duration (ms)')
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error'),
    ], string='Status')
