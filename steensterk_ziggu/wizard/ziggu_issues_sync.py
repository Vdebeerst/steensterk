# -*- coding: utf-8 -*-
from odoo import api, models

class ZigguIssuesSync(models.AbstractModel):
    _name = 'ziggu.issues.sync'

    def _enabled(self, key):
        value = self.env['ir.config_parameter'].sudo().get_param(key, 'False')
        return str(value).strip().lower() in ('1', 'true', 'yes', 'y', 'on')

    _description = 'Sync Ziggu issues to helpdesk.ticket'

    @api.model
    def sync_issues_from_ziggu(self):
        if not self._enabled('ziggu.get_issues'):
            return {'skipped': True, 'reason': 'ziggu.get_issues disabled'}
        res = self.env['ziggu.generic.sync'].sync_endpoint('issues', 'helpdesk.ticket', {
            'title': 'name', 'name': 'name', 'description_html': 'ziggu_description', 'internal_note_html': 'ziggu_internal_note_html',
            'project_id': ('ziggu_project_id','project.project'), 'building_id': ('ziggu_building_id','ziggu.building'),
            'lot_id': ('ziggu_lot_id','ziggu.lot'), 'unit_id': ('ziggu_unit_id','ziggu.unit'), 'space_id': ('ziggu_space_id','ziggu.space'),
            'issue_category_id': ('ziggu_issue_category_id','ziggu.issue.category'), 'issue_status_id': ('ziggu_issue_status_id','ziggu.issue.status'),
            'issue_list_id': ('ziggu_issue_list_id','ziggu.issue.list'), 'customer_id': ('ziggu_customer_id','res.partner'),
            'employee_id': ('ziggu_employee_id','hr.employee'), 'due_date': 'ziggu_due_date', 'completed_at': 'ziggu_completed_at',
            'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
        })
        self.env['helpdesk.ticket'].sudo().search([('ziggu_source','=',False),('ziggu_id','!=',False)]).write({'ziggu_source':'issue'})
        return res
