# custom_addons/ziggu_partner_sync/models/res_config_settings.py
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ziggu_base_url = fields.Char(string="Ziggu URL", config_parameter="ziggu.base_url") # https://api.ziggu.app/public
    ziggu_client_id = fields.Char(string="Ziggu Client ID", config_parameter="ziggu.client_id") # 8027
    ziggu_access_token = fields.Char(string="Ziggu Access Token", config_parameter="ziggu.access_token") # odoo-steensterk db9e7d7e-5cea-4500-9233-38a82f2621f0

    ziggu_project_template_id = fields.Many2one(
        "project.project",
        string="Project Template",
        config_parameter="ziggu.project_template_id",
        help="Template project used when creating new Odoo projects from Ziggu.",
    )

    ziggu_get_attachment_categories = fields.Boolean(string="API GET Attachment Categories", config_parameter="ziggu.get_attachment_categories")
    ziggu_get_buildings = fields.Boolean(string="API GET Buildings", config_parameter="ziggu.get_buildings")
    ziggu_get_companies = fields.Boolean(string="API GET Companies", config_parameter="ziggu.get_companies")
    ziggu_get_customers = fields.Boolean(string="API GET Customers", config_parameter="ziggu.get_customers")
    ziggu_get_decision_type_categories = fields.Boolean(string="API GET Decision Type Categories", config_parameter="ziggu.get_decision_type_categories")
    ziggu_get_decision_types = fields.Boolean(string="API GET Decision Types", config_parameter="ziggu.get_decision_types")
    ziggu_get_decisions = fields.Boolean(string="API GET Decisions", config_parameter="ziggu.get_decisions")
    ziggu_get_documents = fields.Boolean(string="API GET Documents", config_parameter="ziggu.get_documents")
    ziggu_get_employees = fields.Boolean(string="API GET Employees", config_parameter="ziggu.get_employees")
    ziggu_get_fractions = fields.Boolean(string="API GET Fractions", config_parameter="ziggu.get_fractions")
    ziggu_get_installments = fields.Boolean(string="API GET Installments", config_parameter="ziggu.get_installments")
    ziggu_get_issue_categories = fields.Boolean(string="API GET Issue Categories", config_parameter="ziggu.get_issue_categories")
    ziggu_get_issue_list_types = fields.Boolean(string="API GET Issue List Types", config_parameter="ziggu.get_issue_list_types")
    ziggu_get_issue_lists = fields.Boolean(string="API GET Issue Lists", config_parameter="ziggu.get_issue_lists")
    ziggu_get_issue_statuses = fields.Boolean(string="API GET Issue Statuses", config_parameter="ziggu.get_issue_statuses")
    ziggu_get_issues = fields.Boolean(string="API GET Issues", config_parameter="ziggu.get_issues")
    ziggu_get_lots = fields.Boolean(string="API GET Lots", config_parameter="ziggu.get_lots")
    ziggu_get_messages = fields.Boolean(string="API GET Messages", config_parameter="ziggu.get_messages")
    ziggu_get_partners = fields.Boolean(string="API GET Partners", config_parameter="ziggu.get_partners")
    ziggu_get_phases = fields.Boolean(string="API GET Phases", config_parameter="ziggu.get_phases")
    ziggu_get_projects = fields.Boolean(string="API GET Projects", config_parameter="ziggu.get_projects")
    ziggu_get_proposals = fields.Boolean(string="API GET Proposals", config_parameter="ziggu.get_proposals")
    ziggu_get_spaces = fields.Boolean(string="API GET Spaces", config_parameter="ziggu.get_spaces")
    ziggu_get_ticket_categories = fields.Boolean(string="API GET Ticket Categories", config_parameter="ziggu.get_ticket_categories")
    ziggu_get_tickets = fields.Boolean(string="API GET Tickets", config_parameter="ziggu.get_tickets")
    ziggu_get_unit_customers = fields.Boolean(string="API GET Unit Customers", config_parameter="ziggu.get_unit_customers")
    ziggu_get_units = fields.Boolean(string="API GET Units", config_parameter="ziggu.get_units")
    
    ziggu_put_attachment_categories = fields.Boolean(string="API PUT Attachment Categories", config_parameter="ziggu.put_attachment_categories")
    ziggu_put_buildings = fields.Boolean(string="API PUT Buildings", config_parameter="ziggu.put_buildings")
    ziggu_put_companies = fields.Boolean(string="API PUT Companies", config_parameter="ziggu.put_companies")
    ziggu_put_customers = fields.Boolean(string="API PUT Customers", config_parameter="ziggu.put_customers")
    ziggu_put_decision_type_categories = fields.Boolean(string="API PUT Decision Type Categories", config_parameter="ziggu.put_decision_type_categories")
    ziggu_put_decision_types = fields.Boolean(string="API PUT Decision Types", config_parameter="ziggu.put_decision_types")
    ziggu_put_decisions = fields.Boolean(string="API PUT Decisions", config_parameter="ziggu.put_decisions")
    ziggu_put_documents = fields.Boolean(string="API PUT Documents", config_parameter="ziggu.put_documents")
    ziggu_put_employees = fields.Boolean(string="API PUT Employees", config_parameter="ziggu.put_employees")
    ziggu_put_fractions = fields.Boolean(string="API PUT Fractions", config_parameter="ziggu.put_fractions")
    ziggu_put_installments = fields.Boolean(string="API PUT Installments", config_parameter="ziggu.put_installments")
    ziggu_put_issue_categories = fields.Boolean(string="API PUT Issue Categories", config_parameter="ziggu.put_issue_categories")
    ziggu_put_issue_list_types = fields.Boolean(string="API PUT Issue List Types", config_parameter="ziggu.put_issue_list_types")
    ziggu_put_issue_lists = fields.Boolean(string="API PUT Issue Lists", config_parameter="ziggu.put_issue_lists")
    ziggu_put_issue_statuses = fields.Boolean(string="API PUT Issue Statuses", config_parameter="ziggu.put_issue_statuses")
    ziggu_put_issues = fields.Boolean(string="API PUT Issues", config_parameter="ziggu.put_issues")
    ziggu_put_lots = fields.Boolean(string="API PUT Lots", config_parameter="ziggu.put_lots")
    ziggu_put_messages = fields.Boolean(string="API PUT Messages", config_parameter="ziggu.put_messages")
    ziggu_put_partners = fields.Boolean(string="API PUT Partners", config_parameter="ziggu.put_partners")
    ziggu_put_phases = fields.Boolean(string="API PUT Phases", config_parameter="ziggu.put_phases")
    ziggu_put_projects = fields.Boolean(string="API PUT Projects", config_parameter="ziggu.put_projects")
    ziggu_put_proposals = fields.Boolean(string="API PUT Proposals", config_parameter="ziggu.put_proposals")
    ziggu_put_spaces = fields.Boolean(string="API PUT Spaces", config_parameter="ziggu.put_spaces")
    ziggu_put_ticket_categories = fields.Boolean(string="API PUT Ticket Categories", config_parameter="ziggu.put_ticket_categories")
    ziggu_put_tickets = fields.Boolean(string="API PUT Tickets", config_parameter="ziggu.put_tickets")
    ziggu_put_unit_customers = fields.Boolean(string="API PUT Unit Customers", config_parameter="ziggu.put_unit_customers")
    ziggu_put_units = fields.Boolean(string="API PUT Units", config_parameter="ziggu.put_units")
