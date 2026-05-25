# -*- coding: utf-8 -*-
from odoo import fields, models

class mail_message(models.Model):
    _inherit = 'mail.message'

    ziggu_id = fields.Char('Ziggu Id', index=True)
    ziggu_type = fields.Char('Type')
    ziggu_project_id = fields.Many2one('project.project', 'Project', index=True)
    ziggu_customer_id = fields.Many2one('res.partner', 'Customer', index=True)
    ziggu_employee_id = fields.Many2one('hr.employee', 'Employee', index=True)
    ziggu_unit_id = fields.Many2one('ziggu.unit', 'Unit', index=True)
    ziggu_created_at = fields.Datetime('Ziggu Create Date')
    ziggu_updated_at = fields.Datetime('Ziggu Update Date')
