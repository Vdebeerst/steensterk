# -*- coding: utf-8 -*-
from odoo import models
from odoo.fields import Domain


class AccountReport(models.Model):
    _inherit = 'account.report'

    def _get_options_domain(self, options, date_scope):
        domain = super()._get_options_domain(options, date_scope)
        if options.get('filter_ledger_accounts') and options.get('ledger_account_ids') and options.get('report_id') == self.env.ref('steensterk_analytic_ledger.analytic_ledger_report').id:
            domain = Domain(domain) & Domain([('account_id', 'in', [int(account_id) for account_id in options['ledger_account_ids']])])
        return domain
