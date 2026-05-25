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

    ziggu_get_attachment_categories = fields.Boolean(string="API Attachment Categories", config_parameter="ziggu.get_attachment_categories")
    ziggu_get_buildings = fields.Boolean(string="API Buildings", config_parameter="ziggu.get_buildings")
    ziggu_get_companies = fields.Boolean(string="API Companies", config_parameter="ziggu.get_companies")
    ziggu_get_customers = fields.Boolean(string="API Customers", config_parameter="ziggu.get_customers")
    ziggu_get_decision_type_categories = fields.Boolean(string="API Decision Type Categories", config_parameter="ziggu.get_decision_type_categories")
    ziggu_get_decision_types = fields.Boolean(string="API Decision Types", config_parameter="ziggu.get_decision_types")
    ziggu_get_decisions = fields.Boolean(string="API Decisions", config_parameter="ziggu.get_decisions")
    ziggu_get_documents = fields.Boolean(string="API Documents", config_parameter="ziggu.get_documents")
    ziggu_get_employees = fields.Boolean(string="API Employees", config_parameter="ziggu.get_employees")
    ziggu_get_fractions = fields.Boolean(string="API Fractions", config_parameter="ziggu.get_fractions")
    ziggu_get_installments = fields.Boolean(string="API Installments", config_parameter="ziggu.get_installments")
    ziggu_get_issue_categories = fields.Boolean(string="API Issue Categories", config_parameter="ziggu.get_issue_categories")
    ziggu_get_issue_list_types = fields.Boolean(string="API Issue List Types", config_parameter="ziggu.get_issue_list_types")
    ziggu_get_issue_lists = fields.Boolean(string="API Issue Lists", config_parameter="ziggu.get_issue_lists")
    ziggu_get_issue_statuses = fields.Boolean(string="API Issue Statuses", config_parameter="ziggu.get_issue_statuses")
    ziggu_get_issues = fields.Boolean(string="API Issues", config_parameter="ziggu.get_issues")
    ziggu_get_lots = fields.Boolean(string="API Lots", config_parameter="ziggu.get_lots")
    ziggu_get_messages = fields.Boolean(string="API Messages", config_parameter="ziggu.get_messages")
    ziggu_get_partners = fields.Boolean(string="API Partners", config_parameter="ziggu.get_partners")
    ziggu_get_phases = fields.Boolean(string="API Phases", config_parameter="ziggu.get_phases")
    ziggu_get_projects = fields.Boolean(string="API Projects", config_parameter="ziggu.get_projects")
    ziggu_get_proposals = fields.Boolean(string="API Proposals", config_parameter="ziggu.get_proposals")
    ziggu_get_spaces = fields.Boolean(string="API Spaces", config_parameter="ziggu.get_spaces")
    ziggu_get_ticket_categories = fields.Boolean(string="API Ticket Categories", config_parameter="ziggu.get_ticket_categories")
    ziggu_get_tickets = fields.Boolean(string="API Tickets", config_parameter="ziggu.get_tickets")
    ziggu_get_unit_customers = fields.Boolean(string="API Unit Customers", config_parameter="ziggu.get_unit_customers")
    ziggu_get_units = fields.Boolean(string="API Units", config_parameter="ziggu.get_units")
    
