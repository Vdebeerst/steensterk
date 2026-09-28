# -*- coding: utf-8 -*-
"""
Short description if needed.

Changes:

"""
from odoo import fields, models, _

class sale_order(models.Model):
	_inherit = "sale.order"

	partner_prive_id = fields.Many2one('res.partner', 'Privé Klant', tracking=True)

