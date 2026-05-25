# -*- coding: utf-8 -*-
from odoo import api, models

class ZigguTicketsSync(models.AbstractModel):
    _name = 'ziggu.tickets.sync'

    def _enabled(self, key):
        value = self.env['ir.config_parameter'].sudo().get_param(key, 'False')
        return str(value).strip().lower() in ('1', 'true', 'yes', 'y', 'on')

    _description = 'Sync Ziggu tickets to helpdesk.ticket'

    @api.model
    def sync_tickets_from_ziggu(self):
        if not self._enabled('ziggu.get_tickets'):
            return {'skipped': True, 'reason': 'ziggu.get_tickets disabled'}
        res = self.env['ziggu.generic.sync'].sync_endpoint('tickets', 'helpdesk.ticket', {
            'title': 'name', 'subject': 'name', 'description_html': 'ziggu_description',
            'project_id': ('ziggu_project_id','project.project'), 'unit_id': ('ziggu_unit_id','ziggu.unit'),
            'ticket_category_id': ('ziggu_ticket_category_id','ziggu.ticket.category'), 'customer_id': ('ziggu_customer_id','res.partner'),
            'employee_id': ('ziggu_employee_id','hr.employee'), 'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
        })
        self.env['helpdesk.ticket'].sudo().search([('ziggu_source','=',False),('ziggu_id','!=',False)]).write({'ziggu_source':'ticket'})
        return res
