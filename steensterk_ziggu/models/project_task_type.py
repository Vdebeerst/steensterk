# -*- coding: utf-8 -*-

from odoo import fields, models


class project_task_type(models.Model):
    _inherit = "project.task.type"

    ziggu_id = fields.Char("Ziggu Id", index=True)
    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")
    ziggu_type = fields.Char("Ziggu Type")

    ziggu_description = fields.Html('Description')
    ziggu_start_date = fields.Date('Start Date')
    ziggu_end_date = fields.Date('End Date')
    ziggu_units_count = fields.Integer('Units Count')
    ziggu_units_active_count = fields.Integer('Active Units Count')

