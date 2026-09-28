# -*- coding: utf-8 -*-

from odoo import fields, models


class ziggu_building(models.Model):
    _name = "ziggu.building"
    _description = "Ziggu Building"
    _order = "sequence, name"

    ziggu_id = fields.Char("Ziggu Id", required=True, index=True)
    ziggu_type = fields.Char("Type")

    name = fields.Char("Naam", required=True)

    ziggu_start_date = fields.Date("Start Date")
    ziggu_end_date = fields.Date("End Date")
    ziggu_internal_note_html = fields.Html("Internal Note")
    ziggu_elevators = fields.Integer("Elevators")
    ziggu_floors = fields.Integer("Floors")
    ziggu_surface_shared = fields.Float("Shared Surface")
    ziggu_units_count = fields.Integer("Units Count")
    ziggu_units_active_count = fields.Integer("Active Units Count")

    ziggu_phase_id = fields.Many2one("project.task.type", "Phase", index=True)
    ziggu_project_id = fields.Many2one("project.project", "Project", index=True)
    ziggu_lot_id = fields.Many2one("ziggu.lot", "Lot", index=True)

    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")

    active = fields.Boolean("Active", default=True)
    sequence = fields.Integer("Sequence")
    