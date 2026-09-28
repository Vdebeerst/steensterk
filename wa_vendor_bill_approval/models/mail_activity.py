from odoo import fields, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    vendor_bill_approval_line_id = fields.Many2one(
        "vendor.bill.approval.line",
        ondelete="cascade",
        index=True,
    )