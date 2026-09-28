# -*- coding: utf-8 -*-
from odoo import fields, models

class helpdesk_ticket(models.Model):
    _inherit = 'helpdesk.ticket'

    ziggu_id = fields.Char('Ziggu Id', index=True)
    ziggu_type = fields.Char('Type')
    ziggu_source = fields.Selection([('issue','Issue'),('ticket','Ticket')], string='Ziggu Source', index=True)
    ziggu_description = fields.Html('Description')
    ziggu_internal_note_html = fields.Html('Internal Note')
    ziggu_project_id = fields.Many2one('project.project', 'Project', index=True)
    ziggu_building_id = fields.Many2one('ziggu.building', 'Building', index=True)
    ziggu_lot_id = fields.Many2one('ziggu.lot', 'Lot', index=True)
    ziggu_unit_id = fields.Many2one('ziggu.unit', 'Unit', index=True)
    ziggu_space_id = fields.Many2one('ziggu.space', 'Space', index=True)
    ziggu_issue_category_id = fields.Many2one('ziggu.issue.category', 'Issue Category', index=True)
    ziggu_issue_status_id = fields.Many2one('ziggu.issue.status', 'Issue Status', index=True)
    ziggu_issue_list_id = fields.Many2one('ziggu.issue.list', 'Issue List', index=True)
    ziggu_ticket_category_id = fields.Many2one('ziggu.ticket.category', 'Ticket Category', index=True)
    ziggu_customer_id = fields.Many2one('res.partner', 'Customer', index=True)
    ziggu_employee_id = fields.Many2one('hr.employee', 'Employee', index=True)
    ziggu_due_date = fields.Date('Due Date')
    ziggu_completed_at = fields.Datetime('Completed At')
    ziggu_created_at = fields.Datetime('Ziggu Create Date')
    ziggu_updated_at = fields.Datetime('Ziggu Update Date')
