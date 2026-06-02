# -*- coding: utf-8 -*-

from odoo import fields, models


class ziggu_decision_type(models.Model):
	_name = "ziggu.decision.type"
	_description = "Ziggu Decision Type"
	_order = "name"

	ziggu_id = fields.Char("Ziggu Id", index=True)
	ziggu_type = fields.Char("Type")

	name = fields.Char("Naam", required=True)
	ziggu_description_html = fields.Html("Omschrijving")
	ziggu_decisions_count = fields.Integer("Decisions Count")

	ziggu_project_id = fields.Many2one("project.project", "Project", index=True)
	ziggu_decision_type_category_id = fields.Many2one("ziggu.decision.type.category", "Decision Type Category", index=True)

	ziggu_created_at = fields.Datetime("Ziggu Create Date")
	ziggu_updated_at = fields.Datetime("Ziggu Update Date")

	active = fields.Boolean("Active", default=True)

	steensterk_decision_type_id = fields.Many2one('steensterk.decision.type', 'Steensterk Decision Type', index=True)

	def sync_to_ziggu(self):
		api = self.env["ziggu.api"]

		for rec in self:
			payload = rec._prepare_ziggu_payload()

			if rec.ziggu_id:
				result = api.call(
					"PUT",
					f"/decision-types/{rec.ziggu_id}",
					payload,
				)
			else:
				result = api.call(
					"POST",
					"/decision-types",
					payload,
				)

			if result and result.get("id"):
				rec.ziggu_id = result["id"]

	def _prepare_ziggu_payload(self):
		self.ensure_one()

		return {
			"name": self.name,
			"description": self.description or "",
		}
