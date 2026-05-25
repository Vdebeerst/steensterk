# -*- coding: utf-8 -*-

from odoo import fields, models


class ziggu_fraction(models.Model):
    _name = "ziggu.fraction"
    _description = "Ziggu Fraction"
    _order = "sequence, name"

    name = fields.Char("Naam", required=True)
    sequence = fields.Integer("Sequence")
    ziggu_id = fields.Char("Ziggu Id", required=True, index=True)
    ziggu_type = fields.Char("Type")
    ziggu_description = fields.Html("Description")
    ziggu_project_id = fields.Many2one("project.project", "Project", index=True)
    ziggu_unit_id = fields.Many2one("ziggu.unit", "Unit", index=True)
    ziggu_quotity = fields.Float("Quotity")
    ziggu_value = fields.Float("Value")
    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")
    active = fields.Boolean("Active", default=True)
