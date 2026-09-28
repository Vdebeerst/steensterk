# -*- coding: utf-8 -*-
from odoo import fields, models

class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    ziggu_id = fields.Char('Ziggu Id', index=True)
    ziggu_type = fields.Char('Type')
    ziggu_title = fields.Char('Title')
    ziggu_filename = fields.Char('Filename')
    ziggu_description = fields.Html('Description')
    ziggu_url = fields.Char('URL')
    ziggu_file_url = fields.Char('File URL')
    ziggu_mime_type = fields.Char('Mime Type')
    ziggu_file_size = fields.Integer('File Size')
    ziggu_project_id = fields.Many2one('project.project', 'Project', index=True)
    ziggu_building_id = fields.Many2one('ziggu.building', 'Building', index=True)
    ziggu_lot_id = fields.Many2one('ziggu.lot', 'Lot', index=True)
    ziggu_unit_id = fields.Many2one('ziggu.unit', 'Unit', index=True)
    ziggu_attachment_category_id = fields.Many2one('ziggu.attachment.category', 'Attachment Category', index=True)
    ziggu_created_at = fields.Datetime('Ziggu Create Date')
    ziggu_updated_at = fields.Datetime('Ziggu Update Date')
