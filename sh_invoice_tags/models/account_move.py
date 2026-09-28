# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, models, fields


class AccountMove(models.Model):
    """Extends account moves to support invoice tags, mass tag updates, and default company tags."""
    _inherit = "account.move"

    invoice_tag_ids = fields.Many2many('sh.invoice.tags',string="Invoice Tags")

    def insert_after(self, element, new_element):
        """Insert a new XML element immediately after the given element."""
        parent = element.getparent()
        parent.insert(parent.index(element) + 1, new_element)

    def action_mass_tag_update(self):
        """Open a wizard to update invoice tags in bulk for selected moves."""
        return {
            'name': 'Mass Tag Update',
            'res_model': 'sh.update.mass.tag.wizard',
            'view_mode': 'form',
            'context': {
                'default_account_move_ids': [(6, 0, self.env.context.get('active_ids'))]
            },
            'view_id': self.env.ref('sh_invoice_tags.sh_update_mass_tag_wizard_form_view').id,
            'target': 'new',
            'type': 'ir.actions.act_window'
        }

    @api.model
    def default_get(self, fields_list):
        """Set default invoice tags from the company when creating a move."""
        res = super().default_get(fields_list)
        if self.env.company.invoice_tags_id:
            res.update({'invoice_tag_ids': [(6, 0, self.env.company.invoice_tags_id.ids)]})
        return res
