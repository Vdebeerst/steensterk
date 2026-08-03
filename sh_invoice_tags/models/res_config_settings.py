# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class ResCompany(models.Model):
    """Extends company to define default invoice tags."""
    _inherit = 'res.company'

    invoice_tags_id = fields.Many2many('sh.invoice.tags', string="Default Invoice Tags")


class ResConfigSettings(models.TransientModel):
    """Extends settings to manage default invoice tags per company."""
    _inherit = 'res.config.settings'

    invoice_tags_id = fields.Many2many('sh.invoice.tags',string="Default Invoice Tags",related='company_id.invoice_tags_id',readonly=False)
