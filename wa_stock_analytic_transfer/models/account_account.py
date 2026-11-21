from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    wa_stock_account_id = fields.Many2one(
        'account.account', string='Stock Transfer Account', company_dependent=True,
        help='Stock account used when transferring this expense account to inventory for the active company.',
    )
