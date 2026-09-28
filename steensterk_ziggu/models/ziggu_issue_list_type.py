# -*- coding: utf-8 -*-

from odoo import fields, models


class ziggu_issue_list_type(models.Model):
    _name = "ziggu.issue.list.type"
    _description = "Ziggu Issue List Type"
    _order = "sequence, name"

    name = fields.Char("Naam", required=True)
    sequence = fields.Integer("Sequence")
    ziggu_id = fields.Char("Ziggu Id", required=True, index=True)
    ziggu_type = fields.Char("Type")
    ziggu_description = fields.Html("Description")
    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")
    active = fields.Boolean("Active", default=True)
