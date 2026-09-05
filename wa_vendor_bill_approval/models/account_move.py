from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    vendor_bill_approval_state = fields.Selection(
        [
            ("not_submitted", "Not Submitted"),
            ("waiting", "Waiting for Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Approval Status",
        default="not_submitted",
        copy=False,
        tracking=True,
    )

    vendor_bill_approval_line_ids = fields.One2many(
        "vendor.bill.approval.line",
        "move_id",
        string="Approvals",
        copy=False,
        readonly=True,
    )

    current_vendor_bill_approval_line_id = fields.Many2one(
        "vendor.bill.approval.line",
        compute="_compute_vendor_bill_approval",
        string="Current Approval Level",
    )

    can_approve_vendor_bill = fields.Boolean(
        compute="_compute_vendor_bill_approval",
    )

    can_undo_vendor_bill_approval = fields.Boolean(
        compute="_compute_vendor_bill_approval",
    )

    has_optional_next_approval = fields.Boolean(
        compute="_compute_vendor_bill_approval",
    )

    vendor_bill_approval_required = fields.Boolean(
        compute="_compute_vendor_bill_approval_required",
    )

    @api.depends(
        "move_type",
        "company_id.vendor_bill_approval_enabled",
    )
    def _compute_vendor_bill_approval_required(self):
        for move in self:
            move.vendor_bill_approval_required = (
                move.move_type in ("in_invoice", "in_refund")
                and move.company_id.vendor_bill_approval_enabled
            )

    @api.depends(
        "vendor_bill_approval_line_ids.state",
        "vendor_bill_approval_line_ids.sequence",
        "vendor_bill_approval_line_ids.approver_ids",
        "vendor_bill_approval_line_ids.approved_by_id",
    )
    def _compute_vendor_bill_approval(self):
        for move in self:
            current = move.vendor_bill_approval_line_ids.filtered(
                lambda line: line.state == "pending"
            ).sorted(
                key=lambda line: (line.sequence, line.id)
            )[:1]

            move.current_vendor_bill_approval_line_id = current

            move.can_approve_vendor_bill = bool(
                current
                and self.env.user in current.approver_ids
            )

            approved_lines = move.vendor_bill_approval_line_ids.filtered(
                lambda line: line.state == "approved"
            ).sorted(
                key=lambda line: (line.sequence, line.id),
                reverse=True,
            )

            last_approved = approved_lines[:1]

            move.can_undo_vendor_bill_approval = bool(
                move.state == "draft"
                and move.vendor_bill_approval_state in ("waiting", "approved")
                and last_approved
                and (
                    last_approved.approved_by_id == self.env.user
                    or self.env.user.has_group(
                        "account.group_account_manager"
                    )
                )
            )

            if current:
                next_line = move.vendor_bill_approval_line_ids.filtered(
                    lambda line: line.state == "upcoming"
                ).sorted(
                    key=lambda line: (line.sequence, line.id)
                )[:1]
            else:
                next_line = self.env["vendor.bill.approval.line"]

            move.has_optional_next_approval = bool(
                next_line
                and next_line.optional
            )

    def action_submit_vendor_bill_for_approval(self):
        for move in self:
            if not move.vendor_bill_approval_required:
                raise UserError(
                    _("Approval is not enabled for this vendor bill.")
                )

            if move.state != "draft":
                raise UserError(
                    _("Only draft vendor bills can be submitted for approval.")
                )

            if move.vendor_bill_approval_state not in (
                "not_submitted",
                "rejected",
            ):
                raise UserError(
                    _("This vendor bill has already been submitted for approval.")
                )

            levels = move.company_id.vendor_bill_approval_level_ids.filtered(
                "active"
            ).sorted(
                key=lambda level: (level.sequence, level.id)
            )

            if not levels:
                raise UserError(
                    _(
                        "Configure at least one approval level "
                        "before submitting vendor bills."
                    )
                )

            if any(not level.approver_ids for level in levels):
                raise UserError(
                    _("Every approval level must have at least one approver.")
                )

            move.vendor_bill_approval_line_ids.sudo().unlink()

            lines = self.env["vendor.bill.approval.line"].sudo()

            for index, level in enumerate(levels):
                lines |= lines.create({
                    "move_id": move.id,
                    "level_id": level.id,
                    "name": level.name,
                    "sequence": level.sequence,
                    "approver_ids": [
                        (6, 0, level.approver_ids.ids)
                    ],
                    "optional": level.optional,
                    "state": (
                        "pending"
                        if index == 0
                        else "upcoming"
                    ),
                })

            move.with_context(
                skip_vendor_bill_approval_lock=True
            ).write({
                "vendor_bill_approval_state": "waiting",
            })

            lines.filtered(
                lambda line: line.state == "pending"
            )._schedule_activities()

            move.message_post(
                body=_("Vendor bill submitted for approval.")
            )

        return True

    def _activate_next_vendor_bill_approval(
        self,
        request_optional=False,
    ):
        self.ensure_one()

        upcoming = self.vendor_bill_approval_line_ids.filtered(
            lambda line: line.state == "upcoming"
        ).sorted(
            key=lambda line: (line.sequence, line.id)
        )

        for line in upcoming:
            if line.optional and not request_optional:
                line.sudo().write({
                    "state": "skipped",
                })
                continue

            line.sudo().write({
                "state": "pending",
            })

            line._schedule_activities()
            return

        self.with_context(
            skip_vendor_bill_approval_lock=True
        ).write({
            "vendor_bill_approval_state": "approved",
        })

        self.message_post(
            body=_("Vendor bill fully approved.")
        )

    def _action_approve_vendor_bill(
        self,
        request_optional=False,
    ):
        for move in self:
            line = move.current_vendor_bill_approval_line_id

            if (
                move.vendor_bill_approval_state != "waiting"
                or not line
            ):
                raise UserError(
                    _("This vendor bill is not waiting for approval.")
                )

            if self.env.user not in line.approver_ids:
                raise UserError(
                    _(
                        "You are not an approver for "
                        "the current approval level."
                    )
                )

            if (
                request_optional
                and not move.has_optional_next_approval
            ):
                raise UserError(
                    _("The next approval level is not optional.")
                )

            line._close_activities(
                _(
                    "Approved by %s",
                    self.env.user.display_name,
                )
            )

            line.sudo().write({
                "state": "approved",
                "approved_by_id": self.env.user.id,
                "approval_date": fields.Datetime.now(),
            })

            move.message_post(
                body=_(
                    "Approval level '%s' approved by %s.",
                    line.name,
                    self.env.user.display_name,
                )
            )

            move._activate_next_vendor_bill_approval(
                request_optional=request_optional
            )

        return True

    def action_approve_vendor_bill(self):
        return self._action_approve_vendor_bill(
            request_optional=False
        )

    def action_approve_vendor_bill_and_request_optional(self):
        return self._action_approve_vendor_bill(
            request_optional=True
        )

    def action_undo_vendor_bill_approval(self):
        for move in self:
            approved_lines = (
                move.vendor_bill_approval_line_ids.filtered(
                    lambda line: line.state == "approved"
                ).sorted(
                    key=lambda line: (
                        line.sequence,
                        line.id,
                    ),
                    reverse=True,
                )
            )

            line = approved_lines[:1]

            if (
                not line
                or not move.can_undo_vendor_bill_approval
            ):
                raise UserError(
                    _(
                        "Only the most recent completed approval "
                        "can be undone by its approver or "
                        "an Accounting Manager."
                    )
                )

            later_lines = (
                move.vendor_bill_approval_line_ids.filtered(
                    lambda approval: (
                        approval.sequence,
                        approval.id,
                    ) > (
                        line.sequence,
                        line.id,
                    )
                )
            )

            for later_line in later_lines:
                later_line._close_activities(
                    _("Approval undone")
                )

            later_lines.sudo().write({
                "state": "upcoming",
                "approved_by_id": False,
                "approval_date": False,
                "rejection_reason": False,
            })

            line.sudo().write({
                "state": "pending",
                "approved_by_id": False,
                "approval_date": False,
            })

            move.with_context(
                skip_vendor_bill_approval_lock=True
            ).write({
                "vendor_bill_approval_state": "waiting",
            })

            line._schedule_activities()

            move.message_post(
                body=_(
                    "Approval level '%s' was undone by %s.",
                    line.name,
                    self.env.user.display_name,
                )
            )

        return True

    def action_open_vendor_bill_reject_wizard(self):
        self.ensure_one()

        if not self.can_approve_vendor_bill:
            raise UserError(
                _(
                    "You are not an approver for "
                    "the current approval level."
                )
            )

        return {
            "type": "ir.actions.act_window",
            "name": _("Reject Vendor Bill"),
            "res_model": "vendor.bill.reject.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_move_id": self.id,
            },
        }

    def action_reset_vendor_bill_approval(self):
        for move in self:
            if move.state != "draft":
                raise UserError(
                    _(
                        "Only draft vendor bills can "
                        "have their approval reset."
                    )
                )

            for line in move.vendor_bill_approval_line_ids:
                line._close_activities(
                    _("Approval reset")
                )

            move.vendor_bill_approval_line_ids.sudo().unlink()

            move.with_context(
                skip_vendor_bill_approval_lock=True
            ).write({
                "vendor_bill_approval_state": "not_submitted",
            })

            move.message_post(
                body=_("Vendor bill approval reset.")
            )

        return True

    def action_post(self):
        blocked = self.filtered(
            lambda move: (
                move.vendor_bill_approval_required
                and move.vendor_bill_approval_state != "approved"
            )
        )

        if blocked:
            raise ValidationError(
                _(
                    "Vendor bills must be fully approved "
                    "before they can be posted."
                )
            )

        return super(
            AccountMove,
            self.with_context(
                skip_vendor_bill_approval_lock=True
            ),
        ).action_post()

    def write(self, vals):
        protected_fields = {
            "partner_id",
            "currency_id",
            "invoice_date",
            "date",
            "ref",
            "payment_reference",
            "partner_bank_id",
            "fiscal_position_id",
            "invoice_line_ids",
        }

        if (
            not self.env.context.get(
                "skip_vendor_bill_approval_lock"
            )
            and protected_fields.intersection(vals)
        ):
            locked = self.filtered(
                lambda move: (
                    move.state == "draft"
                    and move.vendor_bill_approval_required
                    and move.vendor_bill_approval_state
                    in ("waiting", "approved")
                )
            )

            if locked:
                raise ValidationError(
                    _(
                        "Reset the approval before changing "
                        "an approved or submitted vendor bill."
                    )
                )

        return super().write(vals)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get(
            "skip_vendor_bill_approval_lock"
        ):
            move_ids = [
                vals.get("move_id")
                for vals in vals_list
                if vals.get("move_id")
            ]

            moves = self.env["account.move"].browse(
                move_ids
            )

            locked = moves.filtered(
                lambda move: (
                    move.state == "draft"
                    and move.vendor_bill_approval_required
                    and move.vendor_bill_approval_state
                    in ("waiting", "approved")
                )
            )

            if locked:
                raise ValidationError(
                    _(
                        "Reset the approval before adding lines "
                        "to an approved or submitted vendor bill."
                    )
                )

        return super().create(vals_list)

    def _check_vendor_bill_approval_lock(self):
        if self.env.context.get(
            "skip_vendor_bill_approval_lock"
        ):
            return

        locked = self.move_id.filtered(
            lambda move: (
                move.state == "draft"
                and move.vendor_bill_approval_required
                and move.vendor_bill_approval_state
                in ("waiting", "approved")
            )
        )

        if locked:
            raise ValidationError(
                _(
                    "Reset the approval before changing the lines "
                    "of an approved or submitted vendor bill."
                )
            )

    def write(self, vals):
        protected_fields = {
            "name",
            "account_id",
            "quantity",
            "price_unit",
            "discount",
            "tax_ids",
            "analytic_distribution",
            "partner_id",
            "currency_id",
            "date_maturity",
        }

        if protected_fields.intersection(vals):
            self._check_vendor_bill_approval_lock()

        return super().write(vals)

    def unlink(self):
        self._check_vendor_bill_approval_lock()
        return super().unlink()