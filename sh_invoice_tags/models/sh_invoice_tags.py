# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from random import randint
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ShInvoiceTags(models.Model):
    """Defines invoice tags with unique names, company association,and random color assignment."""
    _name = 'sh.invoice.tags'
    _description = 'Invoice Tags'

    def random_color(self):
        """Return a random integer between 1 and 11 as a color code."""
        random = randint(1,11)
        return random

    name = fields.Char('Tag Name', required=True, translate=True)
    color = fields.Integer('Color Index', default= random_color)

    company_id = fields.Many2one('res.company',string='Company',required=True,default=lambda self: self.env.company)

    @api.constrains('name')
    def _check_unique_name(self):
        """Ensure invoice tag names are unique within the system."""
        for rec in self:
            dup = self.search([('name', '=', rec.name),('id', '!=', rec.id)], limit=1)
            if dup:
                raise ValidationError(_("Tag name already exists!"))
