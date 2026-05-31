# -*- coding: utf-8 -*-

from odoo import fields, models


class steensterk_decision_type(models.Model):
    _name = "steensterk.decision.type"
    _description = "Steensterk Decision Type"
    _order = "name"

    name = fields.Char("Naam", required=True, index=True)

    ziggu_decision_type_category_id = fields.Many2one("ziggu.decision.type.category", "Decision Type Category", index=True)

    active = fields.Boolean("Active", default=True)
