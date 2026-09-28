# -*- coding: utf-8 -*-

from odoo import fields, models


class ziggu_installment(models.Model):
    _name = "ziggu.installment"
    _description = "Ziggu Installment"
    _order = "ziggu_due_date, id"

    name = fields.Char("Naam", required=True)
    ziggu_id = fields.Char("Ziggu Id", required=True, index=True)
    ziggu_type = fields.Char("Type")
    ziggu_description = fields.Html("Description")
    ziggu_project_id = fields.Many2one("project.project", "Project", index=True)
    ziggu_unit_id = fields.Many2one("ziggu.unit", "Unit", index=True)
    ziggu_customer_id = fields.Many2one("res.partner", "Customer", index=True)
    ziggu_due_date = fields.Date("Due Date")
    ziggu_invoice_date = fields.Date("Invoice Date")
    ziggu_percentage = fields.Float("Percentage")
    ziggu_amount = fields.Float("Amount")
    ziggu_amount_net = fields.Float("Amount Net")
    ziggu_vat_amount = fields.Float("VAT Amount")
    ziggu_status = fields.Char("Status")
    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")
    active = fields.Boolean("Active", default=True)
