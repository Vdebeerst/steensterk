# -*- coding: utf-8 -*-
from odoo import api, models

class ZigguMessagesSync(models.AbstractModel):
    _name = 'ziggu.messages.sync'

    def _enabled(self, key):
        value = self.env['ir.config_parameter'].sudo().get_param(key, 'False')
        return str(value).strip().lower() in ('1', 'true', 'yes', 'y', 'on')

    _description = 'Sync Ziggu messages to mail.message'

    @api.model
    def sync_messages_from_ziggu(self):
        if not self._enabled('ziggu.get_messages'):
            return {'skipped': True, 'reason': 'ziggu.get_messages disabled'}
        return self.env['ziggu.generic.sync'].sync_endpoint('messages', 'mail.message', {
            'body_html': 'body', 'body': 'body', 'subject': 'subject',
            'project_id': ('ziggu_project_id','project.project'), 'customer_id': ('ziggu_customer_id','res.partner'),
            'employee_id': ('ziggu_employee_id','hr.employee'), 'unit_id': ('ziggu_unit_id','ziggu.unit'),
            'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
        })
