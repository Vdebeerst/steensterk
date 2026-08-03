from odoo import fields, models


class CashPlanningFlowRule(models.Model):
    _name = "cash.planning.flow.rule"
    _description = "Cash Planning Flow Rule"
    _order = "sequence, id"

    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        index=True,
        help="Leave empty to make this rule available for all companies.",
    )
    flow_type_id = fields.Many2one(
        "cash.planning.flow.type", required=True, ondelete="cascade", index=True
    )
    match_type = fields.Selection(
        [
            ("code_prefix", "Account Code Prefix"),
            ("account_type", "Account Type"),
            ("exact_code", "Exact Account Code"),
        ],
        required=True,
        default="code_prefix",
    )
    account_code = fields.Char(
        help="Used for exact account code or prefix matching, depending on the match type."
    )
    account_type = fields.Selection(
        selection=[
            ("asset_receivable", "Receivable"),
            ("liability_payable", "Payable"),
            ("asset_cash", "Bank and Cash"),
            ("asset_current", "Current Assets"),
            ("liability_current", "Current Liabilities"),
            ("income", "Income"),
            ("expense", "Expenses"),
        ],
        help="Technical account type to match. Extend later if needed.",
    )
    auto_create_mapping = fields.Boolean(
        default=True,
        help="Later phases can use this to create account mappings automatically.",
    )
