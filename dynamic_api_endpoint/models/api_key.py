import secrets
from odoo import api, fields, models


class ApiKey(models.Model):
    _name = 'api.key'
    _description = 'API Key'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    key = fields.Char(string='API Key', readonly=True, copy=False)
    user_id = fields.Many2one('res.users', string='User', required=True,
                              default=lambda self: self.env.user,
                              help='API calls will execute as this user')
    active = fields.Boolean(default=True)
    endpoint_ids = fields.Many2many('api.endpoint', string='Allowed Endpoints',
                                    help='Leave empty to allow all endpoints')
    last_used = fields.Datetime(string='Last Used', readonly=True)
    call_count = fields.Integer(string='Total Calls', readonly=True, default=0)
    rate_limit = fields.Integer(string='Rate Limit (calls/min)', default=60,
                                help='Maximum API calls per minute. 0 = unlimited')

    def action_generate_key(self):
        for rec in self:
            rec.key = f"odoo_api_{secrets.token_hex(32)}"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if not rec.key:
                rec.action_generate_key()
        return records

    def action_regenerate_key(self):
        self.action_generate_key()
