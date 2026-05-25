# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.tools import str2bool


class ZigguAPI(models.AbstractModel):
    _name = "ziggu.api"
    _description = "Sync Ziggu to Odoo"

    def _enabled(self, key):
        return str2bool(self.env['ir.config_parameter'].sudo().get_param(key, 'False'))

    @api.model
    def sync_ziggu(self):
        if self._enabled('ziggu.get_companies'):
            self.env["ziggu.companies.sync"].sync_companies_from_ziggu()
        if self._enabled('ziggu.get_customers'):
            self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        if self._enabled('ziggu.get_partners'):
            self.env["ziggu.partners.sync"].sync_partners_from_ziggu()
        if self._enabled('ziggu.get_projects'):
            self.env["ziggu.projects.sync"].sync_projects_from_ziggu()

        sync = self.env["ziggu.generic.sync"]

        resources = [
            ('ziggu.get_attachment_categories', 'attachment_categories', 'ziggu.attachment.category', {
                'name': 'name', 'description': 'ziggu_description', 'active': 'ziggu_active', 'sequence': 'ziggu_sequence',
                'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_phases', 'phases', 'project.task.type', {
                'name': 'name', 'description_html': 'ziggu_description', 'start_date': 'ziggu_start_date', 'end_date': 'ziggu_end_date',
                'units_count': 'ziggu_units_count', 'units_active_count': 'ziggu_units_active_count',
                'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_lots', 'lots', 'ziggu.lot', {
                'name': 'name', 'start_date': 'ziggu_start_date', 'end_date': 'ziggu_end_date', 'land_register': 'ziggu_land_register',
                'surface': 'ziggu_surface', 'description_html': 'ziggu_description', 'units_count': 'ziggu_units_count',
                'units_active_count': 'ziggu_units_active_count', 'project_id': ('ziggu_project_id', 'project.project'),
                'phase_id': ('ziggu_phase_id', 'project.task.type'), 'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_buildings', 'buildings', 'ziggu.building', {
                'name': 'name', 'start_date': 'ziggu_start_date', 'end_date': 'ziggu_end_date', 'internal_note_html': 'ziggu_internal_note_html',
                'elevators': 'ziggu_elevators', 'floors': 'ziggu_floors', 'surface_shared': 'ziggu_surface_shared',
                'units_count': 'ziggu_units_count', 'units_active_count': 'ziggu_units_active_count',
                'project_id': ('ziggu_project_id', 'project.project'), 'phase_id': ('ziggu_phase_id', 'project.task.type'),
                'lot_id': ('ziggu_lot_id', 'ziggu.lot'), 'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_decision_type_categories', 'decision_type_categories', 'ziggu.decision.type.category', {
                'name': 'name', 'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_decision_types', 'decision_types', 'ziggu.decision.type', {
                'name': 'name', 'description_html': 'ziggu_description_html', 'decisions_count': 'ziggu_decisions_count',
                'project_id': ('ziggu_project_id', 'project.project'),
                'decision_type_category_id': ('ziggu_decision_type_category_id', 'ziggu.decision.type.category'),
                'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_decisions', 'decisions', 'ziggu.decision', {
                'approved_at': 'ziggu_approved_at', 'decision_type_id': ('ziggu_decision_type_id', 'ziggu.decision.type'),
                'due_date': 'ziggu_due_date', 'employee_id': ('ziggu_employee_id', 'hr.employee'),
                'project_id': ('ziggu_project_id', 'project.project'), 'published_customer': 'ziggu_published_customer',
                'published_partners': 'ziggu_published_partners', 'price_approved': 'ziggu_price_approved',
                'price_approved_net': 'ziggu_price_approved_net', 'price_budget': 'ziggu_price_budget',
                'price_budget_extra': 'ziggu_price_budget_extra', 'price_surcharge': 'ziggu_price_surcharge',
                'margin_price_budget': 'ziggu_margin_price_budget', 'margin_price_surcharge': 'ziggu_margin_price_surcharge',
                'margin_total': 'ziggu_margin_total', 'note_employee': 'ziggu_note_employee',
                'unit_id': ('ziggu_unit_id', 'ziggu.unit'), 'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_units', 'units', 'ziggu.unit', {
                'name': 'name', 'description_html': 'ziggu_description', 'project_id': ('ziggu_project_id', 'project.project'),
                'phase_id': ('ziggu_phase_id', 'project.task.type'), 'lot_id': ('ziggu_lot_id', 'ziggu.lot'),
                'building_id': ('ziggu_building_id', 'ziggu.building'), 'status': 'ziggu_status', 'number': 'ziggu_number',
                'reference': 'ziggu_reference', 'surface': 'ziggu_surface', 'price': 'ziggu_price', 'price_net': 'ziggu_price_net',
                'vat_percentage': 'ziggu_vat_percentage', 'delivery_date_actual': 'ziggu_delivery_date_actual',
                'delivery_date_contractual': 'ziggu_delivery_date_contractual', 'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_unit_customers', 'unit_customers', 'ziggu.unit.customer', {
                'unit_id': ('ziggu_unit_id', 'ziggu.unit'), 'customer_id': ('ziggu_customer_id', 'res.partner'),
                'project_id': ('ziggu_project_id', 'project.project'), 'role': 'ziggu_role',
                'start_date': 'ziggu_start_date', 'end_date': 'ziggu_end_date', 'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_documents', 'documents', 'ir.attachment', {
                'name': 'name', 'title': 'ziggu_title', 'filename': 'ziggu_filename', 'description_html': 'ziggu_description',
                'url': 'ziggu_url', 'file_url': 'ziggu_file_url', 'mime_type': 'ziggu_mime_type', 'file_size': 'ziggu_file_size',
                'project_id': ('ziggu_project_id', 'project.project'), 'building_id': ('ziggu_building_id', 'ziggu.building'),
                'lot_id': ('ziggu_lot_id', 'ziggu.lot'), 'unit_id': ('ziggu_unit_id', 'ziggu.unit'),
                'attachment_category_id': ('ziggu_attachment_category_id', 'ziggu.attachment.category'),
                'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_fractions', 'fractions', 'ziggu.fraction', {
                'name': 'name', 'description_html': 'ziggu_description', 'project_id': ('ziggu_project_id', 'project.project'),
                'unit_id': ('ziggu_unit_id', 'ziggu.unit'), 'quotity': 'ziggu_quotity', 'value': 'ziggu_value',
                'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_installments', 'installments', 'ziggu.installment', {
                'name': 'name', 'description_html': 'ziggu_description', 'project_id': ('ziggu_project_id', 'project.project'),
                'unit_id': ('ziggu_unit_id', 'ziggu.unit'), 'customer_id': ('ziggu_customer_id', 'res.partner'),
                'due_date': 'ziggu_due_date', 'invoice_date': 'ziggu_invoice_date', 'percentage': 'ziggu_percentage',
                'amount': 'ziggu_amount', 'amount_net': 'ziggu_amount_net', 'vat_amount': 'ziggu_vat_amount',
                'status': 'ziggu_status', 'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_issue_categories', 'issue_categories', 'ziggu.issue.category', {
                'name': 'name', 'description_html': 'ziggu_description', 'project_id': ('ziggu_project_id', 'project.project'),
                'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_issue_list_types', 'issue_list_types', 'ziggu.issue.list.type', {
                'name': 'name', 'description_html': 'ziggu_description', 'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_issue_lists', 'issue_lists', 'ziggu.issue.list', {
                'name': 'name', 'description_html': 'ziggu_description', 'project_id': ('ziggu_project_id', 'project.project'),
                'unit_id': ('ziggu_unit_id', 'ziggu.unit'), 'issue_list_type_id': ('ziggu_issue_list_type_id', 'ziggu.issue.list.type'),
                'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_issue_statuses', 'issue_statuses', 'ziggu.issue.status', {
                'name': 'name', 'description_html': 'ziggu_description', 'color': 'ziggu_color',
                'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_issues', 'issues', 'helpdesk.ticket', {
                'name': 'name', 'description_html': 'ziggu_description', 'internal_note_html': 'ziggu_internal_note_html',
                'project_id': ('ziggu_project_id', 'project.project'), 'building_id': ('ziggu_building_id', 'ziggu.building'),
                'lot_id': ('ziggu_lot_id', 'ziggu.lot'), 'unit_id': ('ziggu_unit_id', 'ziggu.unit'),
                'space_id': ('ziggu_space_id', 'ziggu.space'), 'issue_category_id': ('ziggu_issue_category_id', 'ziggu.issue.category'),
                'issue_status_id': ('ziggu_issue_status_id', 'ziggu.issue.status'), 'issue_list_id': ('ziggu_issue_list_id', 'ziggu.issue.list'),
                'customer_id': ('ziggu_customer_id', 'res.partner'), 'employee_id': ('ziggu_employee_id', 'hr.employee'),
                'due_date': 'ziggu_due_date', 'completed_at': 'ziggu_completed_at', 'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_messages', 'messages', 'mail.message', {
                'name': 'name', 'subject': 'ziggu_subject', 'body_html': 'ziggu_body_html',
                'project_id': ('ziggu_project_id', 'project.project'), 'customer_id': ('ziggu_customer_id', 'res.partner'),
                'partner_id': ('ziggu_partner_id', 'res.partner'), 'employee_id': ('ziggu_employee_id', 'hr.employee'),
                'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_proposals', 'proposals', 'ziggu.proposal', {
                'name': 'name', 'description_html': 'ziggu_description', 'project_id': ('ziggu_project_id', 'project.project'),
                'unit_id': ('ziggu_unit_id', 'ziggu.unit'), 'customer_id': ('ziggu_customer_id', 'res.partner'),
                'status': 'ziggu_status', 'price': 'ziggu_price', 'price_net': 'ziggu_price_net', 'margin': 'ziggu_margin',
                'approved_at': 'ziggu_approved_at', 'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_spaces', 'spaces', 'ziggu.space', {
                'name': 'name', 'description_html': 'ziggu_description', 'project_id': ('ziggu_project_id', 'project.project'),
                'building_id': ('ziggu_building_id', 'ziggu.building'), 'lot_id': ('ziggu_lot_id', 'ziggu.lot'),
                'unit_id': ('ziggu_unit_id', 'ziggu.unit'), 'surface': 'ziggu_surface',
                'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_ticket_categories', 'ticket_categories', 'ziggu.ticket.category', {
                'name': 'name', 'description_html': 'ziggu_description', 'project_id': ('ziggu_project_id', 'project.project'),
                'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_tickets', 'tickets', 'helpdesk.ticket', {
                'name': 'name', 'description_html': 'ziggu_description', 'project_id': ('ziggu_project_id', 'project.project'),
                'unit_id': ('ziggu_unit_id', 'ziggu.unit'), 'customer_id': ('ziggu_customer_id', 'res.partner'),
                'partner_id': ('ziggu_partner_id', 'res.partner'), 'employee_id': ('ziggu_employee_id', 'hr.employee'),
                'ticket_category_id': ('ziggu_ticket_category_id', 'ziggu.ticket.category'), 'status': 'ziggu_status',
                'priority': 'ziggu_priority', 'due_date': 'ziggu_due_date', 'closed_at': 'ziggu_closed_at',
                'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
            ('ziggu.get_employees', 'employees', 'hr.employee', {
                'name': 'name', 'first_name': 'ziggu_first_name', 'last_name': 'ziggu_last_name', 'email': 'ziggu_email',
                'mobile': 'ziggu_mobile', 'phone': 'ziggu_phone', 'created_at': 'ziggu_created_at', 'updated_at': 'ziggu_updated_at',
            }),
        ]

        results = {}
        for config_key, endpoint, model_name, mapping in resources:
            if self._enabled(config_key):
                results[endpoint] = sync.sync_endpoint(endpoint, model_name, mapping)
        return results
