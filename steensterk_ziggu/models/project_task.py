# -*- coding: utf-8 -*-
"""
Short description if needed.

Changes:

"""

from odoo import fields, models, _

class project_task(models.Model):
	_inherit = "project.task"

	def write(self, vals):
		res = super().write(vals)

		if 'planned_date_begin' in vals or 'date_deadline' in vals:
			for task in self.filtered(lambda t: t.project_id):
				project = task.project_id
				values = {}

				# Vroegste startdatum bepalen
				start_dates = [
					fields.Datetime.to_datetime(d).date()
					for d in project.task_ids.mapped('planned_date_begin')
					if d
				]

				if start_dates:
					values['date_start'] = min(start_dates)

				# Laatste deadline bepalen
				deadlines = [
					d for d in project.task_ids.mapped('date_deadline')
					if d
				]

				if deadlines:
					values['date'] = max(deadlines)

				if values:
					project.write(values)

		return res
	