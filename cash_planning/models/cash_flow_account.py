from odoo import fields, models


class CashPlanningAccountLine(models.Model):
    _name = "cash.planning.account.line"
    _description = "Cash Planning Account Mapping"
    _order = "company_id, flow_type_id, account_id"

    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    flow_type_id = fields.Many2one(
        "cash.planning.flow.type",
        required=True,
        ondelete="cascade",
        index=True,
    )
    account_id = fields.Many2one(
        "account.account",
        required=True,
        ondelete="cascade",
        domain="[('company_ids', 'in', company_id)]",
        index=True,
    )
    direction = fields.Selection(related="flow_type_id.direction", store=True, readonly=True)
    note = fields.Char()

    _sql_constraints = [
        (
            "company_account_type_unique",
            "unique(company_id, account_id, flow_type_id)",
            "This account is already mapped to this cash planning type for this company.",
        ),
    ]
