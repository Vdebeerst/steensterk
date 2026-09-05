from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    vendor_bill_approval_enabled = fields.Boolean(
        string="Vendor Bill Approval",
    )

    vendor_bill_approval_level_ids = fields.One2many(
        "vendor.bill.approval.level",
        "company_id",
        string="Approval Levels",
    )