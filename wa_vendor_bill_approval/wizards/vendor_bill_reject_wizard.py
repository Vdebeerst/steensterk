from odoo import fields, models, _
from odoo.exceptions import UserError


class VendorBillRejectWizard(models.TransientModel):
    _name = "vendor.bill.reject.wizard"
    _description = "Reject Vendor Bill"

    move_id = fields.Many2one(
        "account.move",
        readonly=True,
    )

    approval_line_id = fields.Many2one(
        "vendor.bill.approval.line",
        readonly=True,
    )

    reason = fields.Text(
        required=True,
    )

    def action_reject(self):
        self.ensure_one()
        actor = self.env.user
        line = self.approval_line_id

        if line:
            line._check_current_approver()
            move = line.move_id.sudo()
        else:
            move = self.move_id

            if not move:
                raise UserError(
                    _("No vendor bill was selected.")
                )

            line = move.current_vendor_bill_approval_line_id

            if (
                move.vendor_bill_approval_state != "waiting"
                or not line
            ):
                raise UserError(
                    _("This vendor bill is not waiting for approval.")
                )

            if actor not in line.approver_ids:
                raise UserError(
                    _(
                        "You are not an approver for "
                        "the current approval level."
                    )
                )

            move = move.sudo()

        line._close_activities(
            _(
                "Rejected by %s",
                actor.display_name,
            )
        )

        line.sudo().write({
            "state": "rejected",
            "approved_by_id": actor.id,
            "approval_date": fields.Datetime.now(),
            "rejection_reason": self.reason,
        })

        move.with_context(
            skip_vendor_bill_approval_lock=True
        ).write({
            "vendor_bill_approval_state": "rejected",
        })

        move.message_post(
            body=_(
                "Approval level '%s' rejected by %s."
                "<br/>Reason: %s",
                line.name,
                actor.display_name,
                self.reason,
            )
        )

        return {
            "type": "ir.actions.act_window_close",
        }
