from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    wa_stock_source_line_id = fields.Many2one(
        'account.move.line', string='Stock Transfer Source Line',
        index=True, copy=False, readonly=True,
        help='Original expense journal item that generated this stock transfer line.',
    )

    def _wa_default_account_distribution(self, account, company):
        if not account or not company:
            return {}
        return dict(account.with_company(company).wa_analytic_distribution or {})

    def _wa_merge_account_distribution(self, existing, incoming):
        """Replace only plans present in the account default; preserve other plans."""
        if not incoming:
            return dict(existing or {})
        if not existing:
            return dict(incoming)
        analytic_ids = {
            int(account_id)
            for key in incoming
            if key != '__update__'
            for account_id in key.split(',')
        }
        accounts = self.env['account.analytic.account'].browse(list(analytic_ids)).exists()
        if len(accounts) != len(analytic_ids):
            raise ValidationError('The account default references a missing analytic account.')
        columns = list({account.root_plan_id._column_name() for account in accounts})
        updates = dict(incoming)
        updates['__update__'] = columns
        return self._merge_distribution(dict(existing), updates)

    def _wa_apply_account_default(self, account=None):
        for line in self:
            selected_account = account or line.account_id
            if not selected_account:
                continue
            company = line.move_id.company_id or line.company_id or self.env.company
            incoming = line._wa_default_account_distribution(selected_account, company)
            if incoming:
                line.analytic_distribution = line._wa_merge_account_distribution(
                    line.analytic_distribution, incoming,
                )

    @api.depends('account_id', 'partner_id', 'product_id', 'move_id', 'move_id.company_id')
    def _compute_analytic_distribution(self):
        super()._compute_analytic_distribution()
        for line in self:
            if line.account_id and not line.analytic_distribution:
                line._wa_apply_account_default()

    @api.onchange('account_id')
    def _wa_onchange_account_distribution(self):
        self._wa_apply_account_default()

    @api.model_create_multi
    def create(self, vals_list):
        prepared = [dict(vals) for vals in vals_list]
        account_ids = {v['account_id'] for v in prepared if v.get('account_id') and 'analytic_distribution' not in v}
        move_ids = {v['move_id'] for v in prepared if v.get('move_id') and 'analytic_distribution' not in v}
        accounts = {r.id: r for r in self.env['account.account'].browse(account_ids)}
        moves = {r.id: r for r in self.env['account.move'].browse(move_ids)}
        for vals in prepared:
            if not vals.get('account_id') or 'analytic_distribution' in vals:
                continue
            move = moves.get(vals.get('move_id'))
            company = move.company_id if move else (
                self.env['res.company'].browse(vals['company_id'])
                if vals.get('company_id') else self.env.company
            )
            incoming = self._wa_default_account_distribution(accounts[vals['account_id']], company)
            if incoming:
                vals['analytic_distribution'] = incoming
        return super().create(prepared)

    def write(self, vals):
        if 'account_id' not in vals or 'analytic_distribution' in vals or not vals.get('account_id'):
            return super().write(vals)
        account = self.env['account.account'].browse(vals['account_id'])
        for line in self:
            company = line.move_id.company_id or line.company_id or self.env.company
            incoming = line._wa_default_account_distribution(account, company)
            new_vals = dict(vals)
            if incoming:
                new_vals['analytic_distribution'] = line._wa_merge_account_distribution(
                    line.analytic_distribution, incoming,
                )
            super(AccountMoveLine, line).write(new_vals)
        return True

    def init(self):
        super().init()
        self.env.cr.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS wa_stock_source_line_unique_idx
            ON account_move_line (wa_stock_source_line_id)
            WHERE wa_stock_source_line_id IS NOT NULL
        """)
