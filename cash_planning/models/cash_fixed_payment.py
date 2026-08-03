from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CashPlanningFixedPayment(models.Model):
    _name = "cash.planning.fixed.payment"
    _description = "Cash Planning Fixed Payment"
    _order = "company_id, next_date, name"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    flow_type_id = fields.Many2one(
        "cash.planning.flow.type", required=True, ondelete="restrict", index=True
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Bank Journal",
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]",
    )
    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        store=True,
        readonly=True,
    )
    frequency = fields.Selection(
        [
            ("once", "Once"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("yearly", "Yearly"),
        ],
        required=True,
        default="monthly",
    )
    next_date = fields.Date(required=True)
    end_date = fields.Date()
    note = fields.Text()

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount < 0:
                raise ValidationError("Use a positive amount. The cash flow type determines the direction.")

    @api.constrains("next_date", "end_date")
    def _check_dates(self):
        for rec in self:
            if rec.end_date and rec.next_date and rec.end_date < rec.next_date:
                raise ValidationError("The end date cannot be before the next date.")
