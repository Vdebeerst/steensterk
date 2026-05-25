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

    ziggu_documents_folder_id = fields.Many2one(
        'documents.document',
        string='Ziggu Documents Folder',
        copy=False,
    )

    def _get_or_create_ziggu_documents_folder(self):
        self.ensure_one()
        Document = self.env['documents.document'].sudo()

        root_domain = [('name', '=', 'Ziggu')]
        if 'type' in Document._fields:
            root_domain.append(('type', '=', 'folder'))
        if 'folder_id' in Document._fields:
            root_domain.append(('folder_id', '=', False))
        root = Document.search(root_domain, limit=1)
        if not root:
            vals = {'name': 'Ziggu'}
            if 'type' in Document._fields:
                vals['type'] = 'folder'
            root = Document.create(vals)

        if self.ziggu_documents_folder_id:
            return self.ziggu_documents_folder_id

        folder_name = self.name or self.ziggu_id or 'Project'
        folder_domain = [('name', '=', folder_name)]
        if 'type' in Document._fields:
            folder_domain.append(('type', '=', 'folder'))
        if 'folder_id' in Document._fields:
            folder_domain.append(('folder_id', '=', root.id))
        folder = Document.search(folder_domain, limit=1)
        if not folder:
            vals = {'name': folder_name}
            if 'type' in Document._fields:
                vals['type'] = 'folder'
            if 'folder_id' in Document._fields:
                vals['folder_id'] = root.id
            folder = Document.create(vals)

        self.sudo().write({'ziggu_documents_folder_id': folder.id})
        return folder

    