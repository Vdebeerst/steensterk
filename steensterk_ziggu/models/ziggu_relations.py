# -*- coding: utf-8 -*-

from odoo import fields, models, _


def _open_related(record, name, res_model, field_name, extra_domain=None):
    domain = [(field_name, '=', record.id)]
    if extra_domain:
        domain += extra_domain
    return {
        'type': 'ir.actions.act_window',
        'name': name,
        'res_model': res_model,
        'view_mode': 'list,form',
        'domain': domain,
        'context': {f'default_{field_name}': record.id},
    }

class project_project(models.Model):
    _inherit = 'project.project'
    ziggu_lot_ids = fields.One2many('ziggu.lot','ziggu_project_id', string='Ziggu Lots')
    ziggu_building_ids = fields.One2many('ziggu.building','ziggu_project_id', string='Ziggu Buildings')
    ziggu_unit_ids = fields.One2many('ziggu.unit','ziggu_project_id', string='Ziggu Units')
    ziggu_decision_ids = fields.One2many('ziggu.decision','ziggu_project_id', string='Ziggu Decisions')
    ziggu_issue_ticket_ids = fields.One2many('helpdesk.ticket','ziggu_project_id', string='Ziggu Issues/Tickets')
    ziggu_attachment_ids = fields.One2many('ir.attachment','ziggu_project_id', string='Ziggu Documents')
    ziggu_document_ids = fields.One2many('documents.document','res_id', string='Ziggu Documents', domain=[('res_model','=','project.project')])
    def action_ziggu_buildings(self): return _open_related(self, _('Buildings'), 'ziggu.building', 'ziggu_project_id')
    def action_ziggu_lots(self): return _open_related(self, _('Lots'), 'ziggu.lot', 'ziggu_project_id')
    def action_ziggu_units(self): return _open_related(self, _('Units'), 'ziggu.unit', 'ziggu_project_id')
    def action_ziggu_decisions(self): return _open_related(self, _('Decisions'), 'ziggu.decision', 'ziggu_project_id')
    def action_ziggu_issues(self): return _open_related(self, _('Issues'), 'helpdesk.ticket', 'ziggu_project_id', [('ziggu_source','=','issue')])
    def action_ziggu_tickets(self): return _open_related(self, _('Tickets'), 'helpdesk.ticket', 'ziggu_project_id', [('ziggu_source','=','ticket')])
    def action_ziggu_documents(self):
        self.ensure_one()
        folder = self._get_or_create_ziggu_documents_folder()
        return {'type': 'ir.actions.act_window', 'name': _('Documents'), 'res_model': 'documents.document', 'view_mode': 'kanban,list,form', 'domain': [('folder_id', '=', folder.id)], 'context': {'default_folder_id': folder.id, 'default_res_model': 'project.project', 'default_res_id': self.id}}

class ziggu_lot(models.Model):
    _inherit = 'ziggu.lot'
    ziggu_building_ids = fields.One2many('ziggu.building','ziggu_lot_id', string='Buildings')
    ziggu_unit_ids = fields.One2many('ziggu.unit','ziggu_lot_id', string='Units')
    ziggu_space_ids = fields.One2many('ziggu.space','ziggu_lot_id', string='Spaces')
    ziggu_attachment_ids = fields.One2many('ir.attachment','ziggu_lot_id', string='Documents')
    ziggu_issue_ticket_ids = fields.One2many('helpdesk.ticket','ziggu_lot_id', string='Issues/Tickets')
    def action_ziggu_buildings(self): return _open_related(self, _('Buildings'), 'ziggu.building', 'ziggu_lot_id')
    def action_ziggu_units(self): return _open_related(self, _('Units'), 'ziggu.unit', 'ziggu_lot_id')
    def action_ziggu_spaces(self): return _open_related(self, _('Spaces'), 'ziggu.space', 'ziggu_lot_id')
    def action_ziggu_documents(self): return _open_related(self, _('Documents'), 'ir.attachment', 'ziggu_lot_id')
    def action_ziggu_issues_tickets(self): return _open_related(self, _('Issues/Tickets'), 'helpdesk.ticket', 'ziggu_lot_id')

class ziggu_building(models.Model):
    _inherit = 'ziggu.building'
    ziggu_unit_ids = fields.One2many('ziggu.unit','ziggu_building_id', string='Units')
    ziggu_space_ids = fields.One2many('ziggu.space','ziggu_building_id', string='Spaces')
    ziggu_attachment_ids = fields.One2many('ir.attachment','ziggu_building_id', string='Documents')
    ziggu_issue_ticket_ids = fields.One2many('helpdesk.ticket','ziggu_building_id', string='Issues/Tickets')
    def action_ziggu_units(self): return _open_related(self, _('Units'), 'ziggu.unit', 'ziggu_building_id')
    def action_ziggu_spaces(self): return _open_related(self, _('Spaces'), 'ziggu.space', 'ziggu_building_id')
    def action_ziggu_documents(self): return _open_related(self, _('Documents'), 'ir.attachment', 'ziggu_building_id')
    def action_ziggu_issues_tickets(self): return _open_related(self, _('Issues/Tickets'), 'helpdesk.ticket', 'ziggu_building_id')

class ziggu_unit(models.Model):
    _inherit = 'ziggu.unit'
    ziggu_decision_ids = fields.One2many('ziggu.decision','ziggu_unit_id', string='Decisions')
    ziggu_fraction_ids = fields.One2many('ziggu.fraction','ziggu_unit_id', string='Fractions')
    ziggu_installment_ids = fields.One2many('ziggu.installment','ziggu_unit_id', string='Installments')
    ziggu_space_ids = fields.One2many('ziggu.space','ziggu_unit_id', string='Spaces')
    ziggu_attachment_ids = fields.One2many('ir.attachment','ziggu_unit_id', string='Documents')
    ziggu_issue_ticket_ids = fields.One2many('helpdesk.ticket','ziggu_unit_id', string='Issues/Tickets')
    def action_ziggu_decisions(self): return _open_related(self, _('Decisions'), 'ziggu.decision', 'ziggu_unit_id')
    def action_ziggu_fractions(self): return _open_related(self, _('Fractions'), 'ziggu.fraction', 'ziggu_unit_id')
    def action_ziggu_installments(self): return _open_related(self, _('Installments'), 'ziggu.installment', 'ziggu_unit_id')
    def action_ziggu_spaces(self): return _open_related(self, _('Spaces'), 'ziggu.space', 'ziggu_unit_id')
    def action_ziggu_documents(self): return _open_related(self, _('Documents'), 'ir.attachment', 'ziggu_unit_id')
    def action_ziggu_issues_tickets(self): return _open_related(self, _('Issues/Tickets'), 'helpdesk.ticket', 'ziggu_unit_id')
