# -*- coding: utf-8 -*-

from odoo import fields, models


class ziggu_decision(models.Model):
    _name = "ziggu.decision"
    _description = "Ziggu Decision"
    _order = "ziggu_due_date desc, id desc"

    ziggu_id = fields.Char("Ziggu Id", required=True, index=True)
    ziggu_type = fields.Char("Type")

    name = fields.Char("Naam", compute="_compute_name", store=True)

    ziggu_approved_at = fields.Datetime("Approved At")
    ziggu_decision_type_id = fields.Many2one("ziggu.decision.type", "Decision Type", index=True)
    ziggu_due_date = fields.Date("Due Date")
    ziggu_employee_id = fields.Many2one("hr.employee", "Employee", index=True)
    ziggu_project_id = fields.Many2one("project.project", "Project", index=True)

    ziggu_published_customer = fields.Boolean("Published Customer")
    ziggu_published_partners = fields.Boolean("Published Partners")

    ziggu_price_approved = fields.Float("Price Approved")
    ziggu_price_approved_net = fields.Float("Price Approved Net")
    ziggu_price_budget = fields.Float("Price Budget")
    ziggu_price_budget_extra = fields.Float("Price Budget Extra")
    ziggu_price_surcharge = fields.Float("Price Surcharge")

    ziggu_margin_price_budget = fields.Float("Margin Price Budget")
    ziggu_margin_price_surcharge = fields.Float("Margin Price Surcharge")
    ziggu_margin_total = fields.Float("Margin Total")

    ziggu_note_employee = fields.Html("Employee Note")
    ziggu_unit_id = fields.Many2one("ziggu.unit", "Unit", index=True)

    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")

    active = fields.Boolean("Active", default=True)

    def _compute_name(self):
        for rec in self:
            rec.name = rec.ziggu_decision_type_id.name or rec.ziggu_id
