from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CashPlanningFlowType(models.Model):
    _name = "cash.planning.flow.type"
    _description = "Cash Planning Flow Type"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    direction = fields.Selection(
        [
            ("balance", "Balance"),
            ("in", "Cash In"),
            ("out", "Cash Out"),
            ("both", "Cash In / Out"),
        ],
        required=True,
        default="out",
    )
    include_in_opening_balance = fields.Boolean(
        string="Opening Balance",
        help="Use this type when calculating the opening cash position.",
    )
    sign = fields.Selection(
        [("positive", "Positive"), ("negative", "Negative")],
        required=True,
        default="positive",
        help="Default sign when forecast lines are generated.",
    )
    account_line_ids = fields.One2many(
        "cash.planning.account.line", "flow_type_id", string="Accounts"
    )
    rule_ids = fields.One2many(
        "cash.planning.flow.rule", "flow_type_id", string="Rules"
    )

    _sql_constraints = [
        ("code_unique", "unique(code)", "The cash planning type code must be unique."),
    ]

    @api.constrains("code")
    def _check_code_upper(self):
        for rec in self:
            if rec.code and rec.code != rec.code.upper():
                raise ValidationError("Use uppercase codes for cash planning flow types.")
