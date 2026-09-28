# -*- coding: utf-8 -*-

from odoo import fields, models


class ziggu_unit_customer(models.Model):
    _name = "ziggu.unit.customer"
    _description = "Ziggu Unit Customer"
    _order = "ziggu_created_at desc, id desc"

    name = fields.Char("Naam", required=True)
    ziggu_id = fields.Char("Ziggu Id", required=True, index=True)
    ziggu_type = fields.Char("Type")
    ziggu_unit_id = fields.Many2one("ziggu.unit", "Unit", index=True)
    ziggu_customer_id = fields.Many2one("res.partner", "Customer", index=True)
    ziggu_project_id = fields.Many2one("project.project", "Project", index=True)
    ziggu_role = fields.Char("Role")
    ziggu_start_date = fields.Date("Start Date")
    ziggu_end_date = fields.Date("End Date")
    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")
    active = fields.Boolean("Active", default=True)
