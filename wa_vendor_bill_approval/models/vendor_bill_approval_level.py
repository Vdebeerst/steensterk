from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VendorBillApprovalLevel(models.Model):
    _name = "vendor.bill.approval.level"
    _description = "Vendor Bill Approval Level"
    _order = "sequence, id"
    _check_company_auto = True

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10, required=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        ondelete="cascade",
    )
    approver_ids = fields.Many2many(
        "res.users",
        "vendor_bill_approval_level_user_rel",
        "level_id",
        "user_id",
        string="Approvers",
        required=True,
        domain="[('share', '=', False), ('company_ids', 'in', [company_id])]",
    )
    optional = fields.Boolean(
        help="If enabled, the preceding approver decides whether this level is required.",
    )
    active = fields.Boolean(default=True)

    @api.constrains("approver_ids")
    def _check_approver_ids(self):
        for level in self:
            if not level.approver_ids:
                raise ValidationError(_("At least one approver is required for every approval level."))

    def _add_approver_group(self):
        group = self.env.ref("wa_vendor_bill_approval.group_vendor_bill_approver")
        users = self.mapped("approver_ids")
        if users:
            group.sudo().write({"user_ids": [(4, user.id) for user in users]})

    @api.model
    def _sync_approver_group(self):
        self.search([])._add_approver_group()
        return True

    @api.model_create_multi
    def create(self, vals_list):
        levels = super().create(vals_list)
        levels._add_approver_group()
        return levels

    def write(self, vals):
        result = super().write(vals)
        if "approver_ids" in vals:
            self._add_approver_group()
        return result
