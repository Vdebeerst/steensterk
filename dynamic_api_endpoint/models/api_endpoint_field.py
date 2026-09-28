from odoo import api, fields, models


class ApiEndpointField(models.Model):
    _name = 'api.endpoint.field'
    _description = 'API Endpoint Field Configuration'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    _order = 'sequence, id'

    endpoint_id = fields.Many2one('api.endpoint', string='Endpoint',
                                  required=True, ondelete='cascade')
    field_id = fields.Many2one('ir.model.fields', string='Field', required=True,
                               ondelete='cascade')
    field_name = fields.Char(related='field_id.name', store=True, readonly=True)
    field_type = fields.Selection(related='field_id.ttype', readonly=True)
    sequence = fields.Integer(default=10)
    readable = fields.Boolean(string='Read', default=True)
    writable = fields.Boolean(string='Write', default=False)
    required_on_create = fields.Boolean(string='Required on Create', default=False)
    alias = fields.Char(string='API Alias',
                        help='Alternative field name in API responses/requests')

    # Many2one sub-field mapping
    related_model_id = fields.Many2one(
        'ir.model', string='Related Model', compute='_compute_related_model_id',
        store=True, help='The model referenced by this many2one field')
    sub_field_ids = fields.Many2many(
        'ir.model.fields', string='Sub-Fields',
        help='Select which fields from the related model to include in the API response. '
             'If empty, defaults to id and display_name.')

    # Custom Python code for many2many/one2many serialization
    custom_serialize_code = fields.Text(
        string='Custom Serialize Code',
        help='Python code to customize how many2many/one2many records are serialized.\n'
             'Available variables:\n'
             '  - records: the recordset (browse records)\n'
             '  - env: the Odoo environment\n'
             '  - result: set this variable to your desired output (list of dicts)\n\n'
             'Example:\n'
             'result = [{"id": r.id, "name": r.name, "email": r.email} for r in records]')

    @api.depends('field_id', 'field_id.relation')
    def _compute_related_model_id(self):
        for rec in self:
            if rec.field_id and rec.field_id.ttype == 'many2one' and rec.field_id.relation:
                model = self.env['ir.model'].search(
                    [('model', '=', rec.field_id.relation)], limit=1)
                rec.related_model_id = model.id
            else:
                rec.related_model_id = False
