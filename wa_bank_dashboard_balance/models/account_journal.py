from odoo import models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def _fill_bank_cash_dashboard_data(self, dashboard_data):
        super()._fill_bank_cash_dashboard_data(dashboard_data)
        for journal in self.filtered(lambda j: j.type == 'bank'):
            data = dashboard_data.get(journal.id)
            if not data:
                continue
            currency = journal.currency_id or journal.company_id.sudo().currency_id
            # Odoo already computed the miscellaneous total, but only exposes its
            # formatted value. Keep the original statement balance untouched.
            # A formatted string must never be parsed to perform arithmetic.
            date_limit = journal.last_statement_id.date or journal.company_id.fiscalyear_lock_date
            domain = [
                ('account_id', '=', journal.default_account_id.id),
                ('statement_line_id', '=', False),
                ('parent_state', '=', 'posted'),
                ('payment_id', '=', False),
            ]
            if date_limit:
                domain.append(('date', '>', date_limit))
            lines = self.env['account.move.line'].search(domain)
            if lines and any(line.currency_id != currency for line in lines):
                # Preserve the standard display when amounts cannot be added safely.
                data['wa_combined_balance'] = False
                continue
            misc_amount = sum(lines.mapped('amount_currency'))
            # Reuse the formatted base balance only for display elsewhere; derive
            # the numeric base exactly as Odoo does, including direct payments.
            direct_payment_balances = journal._get_direct_bank_payments()
            _, direct_payments_balance = direct_payment_balances[journal.id]
            data['wa_combined_balance'] = currency.format(
                journal.current_statement_balance + direct_payments_balance + misc_amount
            )
