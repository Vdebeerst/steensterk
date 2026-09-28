# -*- coding: utf-8 -*-
"""
Short description if needed.

Changes:

"""
from odoo import fields, models, _

class account_move_line(models.Model):
	_inherit = "account.move.line"

	# move_ref = fields.Char('Factuurreferentie', related='move_id.ref')
	move_payment_ref = fields.Char('Betaalreferentie', related='move_id.payment_reference', store="True")

