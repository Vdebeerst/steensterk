# -*- coding: utf-8 -*-
"""
Short description if needed.

Changes:

"""

from odoo import fields, models, _

class res_partner(models.Model):
    _inherit = "res.partner"

    ziggu_id = fields.Char('Ziggu Id')
    ziggu_mobile = fields.Char('Mobile')

    ziggu_created_at = fields.Datetime('Create Date')
    ziggu_updated_at = fields.Datetime('Update Date')

    ziggu_note = fields.Html('Note')
    ziggu_type = fields.Char('Ziggu Type')
    