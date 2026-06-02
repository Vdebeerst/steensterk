# -*- coding: utf-8 -*-

import logging
from odoo import fields, models
_logger = logging.getLogger(__name__)


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
		sync = self.env["ziggu.generic.sync"]

		for rec in self:
			payload = rec._prepare_ziggu_payload()

			if rec.ziggu_id:
				result = sync._send_record(
					"PATCH",
					f"decision_types/{rec.ziggu_id}",
					payload,
				)
			else:
				result = sync._send_record(
					"POST",
					"decision_types",
					payload,
				)

			_logger.warning("RESULT=%s", result)

			if result and result.get("id"):
				rec.ziggu_id = str(result["id"])
				_logger.warning(
					"SET ziggu_id=%s for %s",
					rec.ziggu_id,
					rec.name,
				)

			if result:
				ziggu_id = (
					result.get("id")
					or result.get("data", {}).get("id")
				)

				if ziggu_id:
					rec.ziggu_id = str(ziggu_id)

			_logger.warning(
				"AFTER WRITE ziggu_id=%s",
				rec.ziggu_id,
			)

	def _prepare_ziggu_payload(self):
		self.ensure_one()

		return {
			"data": {
				"attributes": {
					"name": self.name,
					"description": self.ziggu_description_html or "",
					"project_id": self.ziggu_project_id.ziggu_id,
				}
			}
		}