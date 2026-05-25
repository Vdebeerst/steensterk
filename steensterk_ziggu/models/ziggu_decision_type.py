# -*- coding: utf-8 -*-

from odoo import fields, models


class ziggu_decision_type(models.Model):
    _name = "ziggu.decision.type"
    _description = "Ziggu Decision Type"
    _order = "name"

    ziggu_id = fields.Char("Ziggu Id", required=True, index=True)
    ziggu_type = fields.Char("Type")

    name = fields.Char("Naam", required=True)
    ziggu_description_html = fields.Html("Omschrijving")
    ziggu_decisions_count = fields.Integer("Decisions Count")

    ziggu_project_id = fields.Many2one("project.project", "Project", index=True)
    ziggu_decision_type_category_id = fields.Many2one("ziggu.decision.type.category", "Decision Type Category", index=True)

    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")

    active = fields.Boolean("Active", default=True)
