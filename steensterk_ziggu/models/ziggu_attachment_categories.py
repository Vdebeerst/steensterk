# -*- coding: utf-8 -*-

from odoo import fields, models


class res_partner(models.Model):
    _name = "ziggu.attachment.category"
    _description = "Ziggu Attachment Category"
    _order = "ziggu_sequence, name"

    name = fields.Char('Naam', required=True)

    ziggu_id = fields.Char('Ziggu Id', required=True, index=True)
    ziggu_description = fields.Html('Description')
    ziggu_active = fields.Boolean('Active', default=True)
    ziggu_sequence = fields.Integer('Sequence')

    ziggu_created_at = fields.Datetime('Create Date')
    ziggu_updated_at = fields.Datetime('Update Date')
    ziggu_type = fields.Char('Ziggu Type')
