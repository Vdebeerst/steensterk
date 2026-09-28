# -*- coding: utf-8 -*-

from odoo import fields, models


class ziggu_unit(models.Model):
    _name = "ziggu.unit"
    _description = "Ziggu Unit"
    _order = "sequence, name"

    name = fields.Char("Naam", required=True)
    sequence = fields.Integer("Sequence")
    ziggu_id = fields.Char("Ziggu Id", required=True, index=True)
    ziggu_type = fields.Char("Type")
    ziggu_description = fields.Html("Description")
    ziggu_project_id = fields.Many2one("project.project", "Project", index=True)
    ziggu_phase_id = fields.Many2one("project.task.type", "Phase", index=True)
    ziggu_lot_id = fields.Many2one("ziggu.lot", "Lot", index=True)
    ziggu_building_id = fields.Many2one("ziggu.building", "Building", index=True)
    ziggu_status = fields.Char("Status")
    ziggu_number = fields.Char("Number")
    ziggu_reference = fields.Char("Reference")
    ziggu_surface = fields.Float("Surface")
    ziggu_price = fields.Float("Price")
    ziggu_price_net = fields.Float("Price Net")
    ziggu_vat_percentage = fields.Float("VAT %")
    ziggu_delivery_date_actual = fields.Date("Actual Delivery Date")
    ziggu_delivery_date_contractual = fields.Date("Contractual Delivery Date")
    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")
    active = fields.Boolean("Active", default=True)
