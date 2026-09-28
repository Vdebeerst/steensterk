from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VendorBillApprovalLine(models.Model):
    _name = "vendor.bill.approval.line"
    _description = "Vendor Bill Approval"
    _order = "sequence, id"
    _check_company_auto = True

    move_id = fields.Many2one("account.move", required=True, ondelete="cascade", check_company=True)
    company_id = fields.Many2one(related="move_id.company_id", store=True)
    level_id = fields.Many2one("vendor.bill.approval.level", ondelete="set null")
    name = fields.Char(required=True)
    sequence = fields.Integer(required=True)
    approver_ids = fields.Many2many(
        "res.users",
        "vendor_bill_approval_line_user_rel",
        "line_id",
        "user_id",
        string="Approvers",
        required=True,
    )
    optional = fields.Boolean()
    state = fields.Selection(
        [
            ("upcoming", "Upcoming"),
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("skipped", "Skipped"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="upcoming",
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approval_date = fields.Datetime(readonly=True)
    rejection_reason = fields.Text(readonly=True)
    activity_ids = fields.One2many("mail.activity", "vendor_bill_approval_line_id")
    partner_id = fields.Many2one(related="move_id.partner_id", store=True, string="Vendor")
    invoice_date = fields.Date(related="move_id.invoice_date", store=True)
    invoice_date_due = fields.Date(related="move_id.invoice_date_due", store=True)
    reference = fields.Char(related="move_id.ref", store=True)
    amount_total = fields.Monetary(related="move_id.amount_total", store=True)
    currency_id = fields.Many2one(related="move_id.currency_id", store=True)
    invoice_number = fields.Char(related="move_id.name", store=True)
    can_approve = fields.Boolean(compute="_compute_permissions")
    can_undo = fields.Boolean(compute="_compute_permissions")
    has_optional_next_approval = fields.Boolean(compute="_compute_permissions")
    has_attachment = fields.Boolean(compute="_compute_has_attachment")

    @api.depends("state", "approver_ids", "approved_by_id", "move_id.vendor_bill_approval_line_ids.state")
    def _compute_permissions(self):
        for line in self:
            line.can_approve = line.state == "pending" and self.env.user in line.approver_ids
            approved_lines = line.move_id.sudo().vendor_bill_approval_line_ids.filtered(
                lambda approval: approval.state == "approved"
            ).sorted(key=lambda approval: (approval.sequence, approval.id), reverse=True)
            last_approved = approved_lines[:1]
            line.can_undo = bool(
                line.state == "approved"
                and line.approved_by_id == self.env.user
                and last_approved == line
                and line.move_id.sudo().state == "draft"
            )
            upcoming = line.move_id.sudo().vendor_bill_approval_line_ids.filtered(
                lambda approval: approval.state == "upcoming"
            ).sorted(key=lambda approval: (approval.sequence, approval.id))[:1]
            line.has_optional_next_approval = bool(line.state == "pending" and upcoming and upcoming.optional)

    def _compute_has_attachment(self):
        for line in self:
            line.has_attachment = bool(line.move_id.sudo().message_main_attachment_id)

    def _check_current_approver(self):
        self.ensure_one()
        if self.state != "pending" or self.env.user not in self.approver_ids:
            raise UserError(_("You are not an approver for the current approval level."))
        if self.move_id.sudo().current_vendor_bill_approval_line_id != self:
            raise UserError(_("This vendor bill is not waiting for your approval."))

    def _approval_move(self):
        self._check_current_approver()
        return self.move_id.sudo().with_context(vendor_bill_approval_actor_id=self.env.uid)

    def action_approve(self):
        return self._approval_move().action_approve_vendor_bill()

    def action_approve_without_extra(self):
        return self._approval_move().action_approve_vendor_bill()

    def action_approve_with_extra(self):
        return self._approval_move().action_approve_vendor_bill_and_request_optional()

    def action_open_reject_wizard(self):
        self._check_current_approver()
        return {
            "type": "ir.actions.act_window",
            "name": _("Reject Vendor Bill"),
            "res_model": "vendor.bill.reject.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_approval_line_id": self.id},
        }

    def action_undo(self):
        self.ensure_one()
        if not self.can_undo:
            raise UserError(_("Only the most recent completed approval can be undone by its approver or an Accounting Manager."))
        return self.move_id.sudo().with_context(
            vendor_bill_approval_actor_id=self.env.uid
        ).action_undo_vendor_bill_approval()

    def action_open_attachment(self):
        self.ensure_one()
        if self.env.user not in self.approver_ids and self.approved_by_id != self.env.user:
            raise UserError(_("You are not allowed to view this vendor bill."))
        attachment = self.move_id.sudo().message_main_attachment_id
        if not attachment:
            raise UserError(_("This vendor bill has no main attachment."))
        attachment.sudo().generate_access_token()
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?access_token=%s" % (attachment.id, attachment.access_token),
            "target": "new",
        }

    def _schedule_activities(self):
        activity_type = self.env.ref("mail.mail_activity_data_todo")
        model_id = self.env["ir.model"]._get_id("account.move")
        for line in self:
            for user in line.approver_ids:
                self.env["mail.activity"].sudo().create({
                    "activity_type_id": activity_type.id,
                    "res_model_id": model_id,
                    "res_id": line.move_id.id,
                    "user_id": user.id,
                    "summary": self.env._("Approve vendor bill: %s", line.name),
                    "note": self.env._("Vendor bill %s is waiting for your approval.", line.move_id.display_name),
                    "vendor_bill_approval_line_id": line.id,
                })

    def _close_activities(self, feedback):
        for activity in self.sudo().activity_ids:
            activity.action_feedback(feedback=feedback)
