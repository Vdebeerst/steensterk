# -*- coding: utf-8 -*-

from odoo import fields, models


class ziggu_decision_type_category(models.Model):
    _name = "ziggu.decision.type.category"
    _description = "Ziggu Decision Type Category"
    _order = "name"

    ziggu_id = fields.Char("Ziggu Id", required=True, index=True)
    ziggu_type = fields.Char("Type")

    name = fields.Char("Naam", required=True)

    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")

    active = fields.Boolean("Active", default=True)
    