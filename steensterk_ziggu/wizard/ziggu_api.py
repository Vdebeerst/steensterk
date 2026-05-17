# custom_addons/steensterk_ziggu/models/ziggu_sync.py

from odoo import api, models
from odoo.tools import str2bool

class ZigguAPI(models.AbstractModel):
    _name = "ziggu.api"
    _description = "Sync Ziggu to Odoo"

    @api.model
    def sync_ziggu(self):
        get_companies = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_companies', 'False'))
        if get_companies: self.env["ziggu.companies.sync"].sync_companies_from_ziggu()
        
        get_customers = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_customers', 'False'))
        if get_customers: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()

        get_partners = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_partners', 'False'))
        if get_partners: self.env["ziggu.partners.sync"].sync_partners_from_ziggu()
        
        get_projects = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_projects', 'False'))
        if get_projects: self.env["ziggu.projects.sync"].sync_projects_from_ziggu()
        
        # get_attachment_categories = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_attachment_categories', 'False'))
        # if get_attachment_categories: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_buildings = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_buildings', 'False'))
        # if get_buildings: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_decision_type_categories = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_decision_type_categories', 'False'))
        # if get_decision_type_categories: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_decision_types = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_decision_types', 'False'))
        # if get_decision_types: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_decisions = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_decisions', 'False'))
        # if get_decisions: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_documents = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_documents', 'False'))
        # if get_documents: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_employees = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_employees', 'False'))
        # if get_employees: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_fractions = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_fractions', 'False'))
        # if get_fractions: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_installments = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_installments', 'False'))
        # if get_installments: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_issue_categories = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_issue_categories', 'False'))
        # if get_issue_categories: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_issue_list_types = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_issue_list_types', 'False'))
        # if get_issue_list_types: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_issue_lists = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_issue_lists', 'False'))
        # if get_issue_lists: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_issue_statuses = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_issue_statuses', 'False'))
        # if get_issue_statuses: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_issues = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_issues', 'False'))
        # if get_issues: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_lots = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_lots', 'False'))
        # if get_lots: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_messages = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_messages', 'False'))
        # if get_messages: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
                
        # get_phases = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_phases', 'False'))
        # if get_phases: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_proposals = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_proposals', 'False'))
        # if get_proposals: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_spaces = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_spaces', 'False'))
        # if get_spaces: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_ticket_categories = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_ticket_categories', 'False'))
        # if get_ticket_categories: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_tickets = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_tickets', 'False'))
        # if get_tickets: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_unit_customers = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_unit_customers', 'False'))
        # if get_unit_customers: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
        # get_units = str2bool(self.env['ir.config_parameter'].sudo().get_param('ziggu.get_units', 'False'))
        # if get_units: self.env["ziggu.customers.sync"].sync_customers_from_ziggu()
        
