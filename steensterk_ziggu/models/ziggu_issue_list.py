# -*- coding: utf-8 -*-

from odoo import fields, models


class ziggu_issue_list(models.Model):
    _name = "ziggu.issue.list"
    _description = "Ziggu Issue List"
    _order = "ziggu_created_at desc, id desc"

    name = fields.Char("Naam", required=True)
    ziggu_id = fields.Char("Ziggu Id", required=True, index=True)
    ziggu_type = fields.Char("Type")
    ziggu_description = fields.Html("Description")
    ziggu_project_id = fields.Many2one("project.project", "Project", index=True)
    ziggu_unit_id = fields.Many2one("ziggu.unit", "Unit", index=True)
    ziggu_issue_list_type_id = fields.Many2one("ziggu.issue.list.type", "Issue List Type", index=True)
    ziggu_created_at = fields.Datetime("Ziggu Create Date")
    ziggu_updated_at = fields.Datetime("Ziggu Update Date")
    active = fields.Boolean("Active", default=True)
