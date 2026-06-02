# -*- coding: utf-8 -*-
"""
Short description if needed.

Changes:

"""

from odoo import fields, models, _
from datetime import timedelta

class project_project(models.Model):
	_inherit = "project.project"

	ziggu_id = fields.Char('Ziggu Id', index=True)

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

	ziggu_decision_type_ids = fields.One2many('ziggu.decision.type', 'ziggu_project_id', 'Decision Types')
	ziggu_decision_ids = fields.One2many('ziggu.decision', 'ziggu_project_id', 'Decisions')
	ziggu_unit_ids = fields.One2many('ziggu.unit', 'ziggu_project_id', 'Units')
	ziggu_building_ids = fields.One2many('ziggu.building', 'ziggu_project_id', 'Buildings')
	ziggu_lot_ids = fields.One2many('ziggu.lot', 'ziggu_project_id', 'Lots')

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

	def action_fill_ziggu_decisions(self):
		Decision = self.env["ziggu.decision"]
		SteensterkType = self.env["steensterk.decision.type"]
		DecisionType = self.env["ziggu.decision.type"]

		for project in self:
			for dtype in SteensterkType.search([]):
				exists = DecisionType.search_count([
					("ziggu_project_id", "=", project.id),
					# ("steensterk_decision_type_id", "=", dtype.id),
					("name", "=", dtype.name),
				])
				if not exists:
					dt = DecisionType.create({
						"ziggu_project_id": project.id,
						"steensterk_decision_type_id": dtype.id,
						"name": dtype.name,
					})
				else:
					dt = DecisionType.search([
						("ziggu_project_id", "=", project.id),
						# ("steensterk_decision_type_id", "=", dtype.id),
						("name", "=", dtype.name),
					])[0]
					
			# for dtype in DecisionType.search([("ziggu_project_id", "=", project.id)]):
			#     exists = Decision.search_count([
			#         ("ziggu_project_id", "=", project.id),
			#         ("decision_type_id", "=", dtype.id),
			#     ])
			#     if not exists:
				if dt:
					Decision.create({
						"ziggu_project_id": project.id,
						"ziggu_decision_type_id": dt.id,
						"steensterk_decision_type_id": dtype.id,
						"name": dtype.name,
						"ziggu_due_date": project.date_start + timedelta(weeks=dtype.weeks_after_start) - timedelta(days=1)
					})

		return {
			'type': 'ir.actions.client',
			'tag': 'display_notification',
			'params': {
				'title': 'Succes',
				'message': 'Synchronisatie uitgevoerd.',
				'type': 'success',
				'next': {
					'type': 'ir.actions.client',
					'tag': 'reload',
				}
			}
		}    
	
	def action_push_ziggu_decisions(self):
		self.ensure_one()

		self.ziggu_decision_type_ids.sync_to_ziggu()
		self.ziggu_decision_ids.sync_to_ziggu()

		return {
			"type": "ir.actions.client",
			"tag": "display_notification",
			"params": {
				"title": _("Ziggu"),
				"message": _("Decision types en decisions gesynchroniseerd."),
				"type": "success",
			}
		}
	