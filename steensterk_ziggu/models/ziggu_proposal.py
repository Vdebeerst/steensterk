# -*- coding: utf-8 -*-

from odoo import fields, models


class ziggu_proposal(models.Model):
    _name = "ziggu.proposal"
    _description = "Ziggu Proposal"
    _order = "ziggu_created_at desc, id desc"

    name = fields.Char("Naam", required=True)
    ziggu_id = fields.Char("Ziggu Id", required=True, index=True)
    ziggu_type = fields.Char("Type")
    ziggu_description = fields.Html("Description")
    ziggu_project_id = fields.Many2one("project.project", "Project", index=True)
    ziggu_unit_id = fields.Many2one("ziggu.unit", "Unit", index=True)
    ziggu_customer_id = fields.Many2one("res.partner", "Customer", index=True)
    ziggu_status = fields.Char("Status")
    ziggu_price = fields.Float("Price")
    ziggu_price_net = fields.Float("Price Net")
    ziggu_margin = fields.Float("Margin")
    ziggu_approved_at = fields.Datetime("Approved At")
    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")
    active = fields.Boolean("Active", default=True)
