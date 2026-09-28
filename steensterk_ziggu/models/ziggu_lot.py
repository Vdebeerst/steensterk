# -*- coding: utf-8 -*-

from odoo import fields, models


class ziggu_lot(models.Model):
    _name = "ziggu.lot"
    _description = "Ziggu Lot"
    _order = "sequence, name"

    ziggu_id = fields.Char("Ziggu Id", required=True, index=True)

    name = fields.Char("Naam", required=True)

    ziggu_start_date = fields.Date('Start Date')
    ziggu_end_date = fields.Date('End Date')
    ziggu_land_register = fields.Char("Land Register")
    ziggu_surface = fields.Float("Surface")
    ziggu_description = fields.Html("Omschrijving")
    ziggu_type = fields.Char("Type")
    ziggu_units_count = fields.Integer('Units Count')
    ziggu_units_active_count = fields.Integer('Active Units Count')

    ziggu_project_id = fields.Many2one('project.project', 'Project', index=True)
    ziggu_phase_id = fields.Many2one('project.task.type', 'Phase', index=True)

    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")

    active = fields.Boolean("Active", default=True)
    sequence = fields.Integer("Sequence")
