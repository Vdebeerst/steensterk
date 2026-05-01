# -*- coding: utf-8 -*-
"""
Short description if needed.

Changes:

"""
from odoo import fields, models, _, api
from datetime import timedelta

class project_task(models.Model):
	_inherit = "project.task"

	planned_weeks = fields.Integer('Geplande tijd (weken)', default=1, help="Aantal weken die voorzien worden voor deze taak")
	weeks_delay = fields.Integer('Weken Uitsel', default=0, tracking=True, help="Aantal weken tussen deze taak en zijn afhankelijkheden")

	@api.onchange('depend_on_ids', 'weeks_delay', 'planned_weeks', 'planned_date_begin')
	def _onchange_schedule_from_dependencies(self):
		for task in self:

			# -----------------------------
			# 1. STARTDATUM bepalen
			# -----------------------------
			start_date = task.planned_date_begin

			if task.depend_on_ids:
				dates = task.depend_on_ids.mapped(
					lambda t: t.date_deadline or t.planned_date_begin
				)
				dates = [d for d in dates if d]

				if dates:
					max_date = max(dates)
					start_date = max_date + timedelta(weeks=task.weeks_delay)

			# fallback indien leeg
			if not start_date:
				start_date = fields.Datetime.now()

			task.planned_date_begin = start_date

			# -----------------------------
			# 2. DUUR toepassen (ALTIJD)
			# -----------------------------
			if task.planned_weeks:
				duration_days = task.planned_weeks * 7
				task.date_deadline = start_date + timedelta(days=duration_days)

	@api.onchange(
		"depend_on_ids",
		"weeks_delay",
		"planned_weeks",
		"planned_date_begin",
		"date_deadline",
	)
	def _onchange_schedule_from_dependencies(self):
		for task in self:

			duration_days = int((task.planned_weeks or 0.0) * 7)

			# ----------------------------------
			# 1. MET dependencies
			# ----------------------------------
			if task.depend_on_ids:
				dates = task.depend_on_ids.mapped(
					lambda t: t.date_deadline or t.planned_date_begin
				)
				dates = [d for d in dates if d]

				if dates:
					max_date = max(dates)
					start_date = max_date + timedelta(weeks=task.weeks_delay)

					task.planned_date_begin = start_date
					task.date_deadline = start_date + timedelta(days=duration_days)
					continue

			# ----------------------------------
			# 2. GEEN dependencies
			# ----------------------------------

			# 👉 CASE A: start bestaat → bereken einde
			if task.planned_date_begin and duration_days:
				task.date_deadline = task.planned_date_begin + timedelta(days=duration_days)

			# 👉 CASE B: einde bestaat → bereken start (JOUW PROBLEEM)
			elif task.date_deadline and duration_days:
				task.planned_date_begin = task.date_deadline - timedelta(days=duration_days)

	def write(self, vals):
		res = super().write(vals)

		if any(k in vals for k in [
			'date_deadline',
			'planned_date_begin',
			'planned_weeks'
		]):
			dependent_tasks = self.search([
				('depend_on_ids', 'in', self.ids)
			])
			dependent_tasks._onchange_schedule_from_dependencies()

		return res
		