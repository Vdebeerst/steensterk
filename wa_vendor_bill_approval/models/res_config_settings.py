from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    vendor_bill_approval_enabled = fields.Boolean(
        related="company_id.vendor_bill_approval_enabled",
        readonly=False,
    )

    vendor_bill_approval_level_ids = fields.One2many(
        related="company_id.vendor_bill_approval_level_ids",
        readonly=False,
    )