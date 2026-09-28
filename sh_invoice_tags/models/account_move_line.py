# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, models, fields


class AccountMoveLine(models.Model):
    """Extends account move lines to support invoice tags and set default company tags."""
    _inherit = "account.move.line"

    invoice_tag_ids = fields.Many2many('sh.invoice.tags',string="Invoice Tags")

    def insert_after(self, element, new_element):
        """Insert a new XML element immediately after the given element."""
        parent = element.getparent()
        parent.insert(parent.index(element) + 1, new_element)

    @api.model
    def default_get(self, fields_list):
        """Sets default invoice tags from the company when creating a move line."""
        res = super().default_get(fields_list)
        if self.env.company.invoice_tags_id:
            res.update({'invoice_tag_ids': [(6, 0, self.env.company.invoice_tags_id.ids)]})
        return res
