from odoo import api, fields, models


class ApiEndpoint(models.Model):
    _name = 'api.endpoint'
    _description = 'Dynamic API Endpoint'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    _rec_name = 'name'
    _order = 'sequence, id'

    name = fields.Char(string='Endpoint Name', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    route = fields.Char(string='Route Path', required=True,
                        help='URL path e.g. /api/v1/partners. Must start with /api/')
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', store=True, readonly=True)
    description = fields.Text(string='Description')

    # HTTP Methods
    method_get = fields.Boolean(string='GET (Read)', default=True)
    method_post = fields.Boolean(string='POST (Create)', default=False)
    method_put = fields.Boolean(string='PUT (Update)', default=False)
    method_delete = fields.Boolean(string='DELETE (Remove)', default=False)

    # Authentication
    auth_type = fields.Selection([
        ('api_key', 'API Key'),
        ('none', 'No Authentication (Public)'),
    ], string='Authentication', default='api_key', required=True)

    # Field configuration
    field_ids = fields.One2many('api.endpoint.field', 'endpoint_id', string='Fields')

    # Domain filter
    domain = fields.Char(string='Domain Filter', default='[]',
                         help='Odoo domain to filter records e.g. [(\"active\",\"=\",True)]')

    # Pagination
    default_limit = fields.Integer(string='Default Page Size', default=80)
    max_limit = fields.Integer(string='Max Page Size', default=500)

    # Logging
    log_requests = fields.Boolean(string='Log Requests', default=True)
    log_ids = fields.One2many('api.log', 'endpoint_id', string='Logs')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('disabled', 'Disabled'),
    ], string='Status', default='draft')

    _sql_constraints = [
        ('route_unique', 'UNIQUE(route)', 'Route path must be unique!'),
    ]

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id and not self.route:
            model_path = self.model_id.model.replace('.', '_')
            self.route = f'/api/v1/{model_path}'
        if self.model_id and not self.name:
            self.name = f'{self.model_id.name} API'

    def action_activate(self):
        self.write({'state': 'active'})

    def action_disable(self):
        self.write({'state': 'disabled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_populate_fields(self):
        """Auto-populate fields from the selected model."""
        for rec in self:
            if not rec.model_id:
                continue
            existing = rec.field_ids.mapped('field_id').ids
            model_fields = self.env['ir.model.fields'].search([
                ('model_id', '=', rec.model_id.id),
                ('id', 'not in', existing),
            ])
            vals = []
            for f in model_fields:
                vals.append({
                    'endpoint_id': rec.id,
                    'field_id': f.id,
                    'readable': True,
                    'writable': f.name not in ('id', 'create_date', 'write_date',
                                                'create_uid', 'write_uid'),
                })
            self.env['api.endpoint.field'].create(vals)

    def get_readable_fields(self):
        self.ensure_one()
        if self.field_ids:
            return self.field_ids.filtered('readable').mapped('field_id.name')
        # Default: return common safe fields
        return ['id', 'name', 'display_name']

    def get_writable_fields(self):
        self.ensure_one()
        if self.field_ids:
            return self.field_ids.filtered('writable').mapped('field_id.name')
        return []
