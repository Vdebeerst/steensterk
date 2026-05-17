# -*- coding: utf-8 -*-
"""
Short description if needed.

Changes:

"""

from odoo import fields, models, _

class project_project(models.Model):
    _inherit = "project.project"

    ziggu_id = fields.Char('Ziggu Id')

    ziggu_created_at = fields.Datetime('Create Date')
    ziggu_updated_at = fields.Datetime('Update Date')

    ziggu_description = fields.Html('Description')
    ziggu_address_city = fields.Char('City')
    ziggu_country_id = fields.Many2one('res.country', 'Country')
    ziggu_address_number = fields.Char('Number')
    ziggu_address_street = fields.Char('Street')
    ziggu_address_zip = fields.Char('Zip')
    ziggu_currency_id = fields.Many2one('res.currency', 'Currency')
    ziggu_delivery_date_actual = fields.Date('Actual Delivery Date')
    ziggu_delivery_date_contractual = fields.Date('Contractual Delivery Date')
    ziggu_is_template = fields.Boolean('Is Template')
    ziggu_measurement = fields.Char('Measurement')
    ziggu_picture_login_url = fields.Char('Picture Login URL')
    ziggu_quotity_total = fields.Integer('Quotity Total')
    ziggu_skip_building = fields.Boolean('Skip Building')
    ziggu_skip_lot = fields.Boolean('Skip Lot')
    ziggu_skip_phase = fields.Boolean('Skip Phase')
    ziggu_start_date = fields.Date('Start Date')
    ziggu_status = fields.Char('Status')
    ziggu_timezone = fields.Char('Timezone')
    ziggu_units_active_count = fields.Integer('Units Active')
    ziggu_units_count_max = fields.Integer('Max. Units')
    ziggu_vat_percentage = fields.Float('VAT %')
    ziggu_website_url = fields.Char('Website URL')

    