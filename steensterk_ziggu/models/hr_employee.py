# -*- coding: utf-8 -*-

from odoo import fields, models


class hr_employee(models.Model):
    _inherit = "hr.employee"

    ziggu_id = fields.Char("Ziggu Id", index=True)
    ziggu_type = fields.Char("Ziggu Type")
    ziggu_first_name = fields.Char("First Name")
    ziggu_last_name = fields.Char("Last Name")
    ziggu_email = fields.Char("Email")
    ziggu_mobile = fields.Char("Mobile")
    ziggu_phone = fields.Char("Phone")
    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")
