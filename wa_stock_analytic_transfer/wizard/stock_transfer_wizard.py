import calendar
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockTransferWizard(models.TransientModel):
    _name = 'wa.stock.transfer.wizard'
    _description = 'Create Monthly Stock Transfer'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    month = fields.Date(string='Month', required=True, default=lambda self: fields.Date.context_today(self).replace(day=1))
    journal_id = fields.Many2one('account.journal', string='Miscellaneous Journal', required=True,
                                 domain="[('type', '=', 'general'), ('company_id', '=', company_id)]")
    counterpart_account_id = fields.Many2one('account.account', string='Stock Variation Account (609500)', required=True)
    line_count = fields.Integer(compute='_compute_preview', string='Source Lines')
    total_amount = fields.Monetary(compute='_compute_preview', currency_field='currency_id', string='Net Amount')
    currency_id = fields.Many2one(related='company_id.currency_id')

    @api.onchange('company_id')
    def _onchange_company_id(self):
        self.journal_id = False
        self.counterpart_account_id = False

    def _period(self):
        self.ensure_one()
        first = self.month.replace(day=1)
        last = date(first.year, first.month, calendar.monthrange(first.year, first.month)[1])
        return first, last

    def _source_lines(self):
        self.ensure_one()
        first, last = self._period()
        return self.env['account.move.line'].with_company(self.company_id).search([
            ('company_id', '=', self.company_id.id),
            ('date', '>=', first), ('date', '<=', last),
            ('move_id.state', '=', 'posted'),
            ('wa_stock_source_line_id', '=', False),
            ('balance', '!=', 0),
        ], order='date, id').filtered(
            lambda line: bool(line.account_id.with_company(self.company_id).wa_stock_account_id)
        ).filtered(lambda line: not self.env['account.move.line'].search_count([
            ('wa_stock_source_line_id', '=', line.id)
        ]))

    @api.depends('company_id', 'month')
    def _compute_preview(self):
        for wizard in self:
            if not wizard.company_id or not wizard.month:
                wizard.line_count = 0
                wizard.total_amount = 0
                continue
            lines = wizard._source_lines()
            wizard.line_count = len(lines)
            wizard.total_amount = sum(lines.mapped('balance'))

    def action_create_move(self):
        self.ensure_one()
        if self.company_id not in self.env.companies:
            raise UserError(_('The selected company is not among your allowed companies.'))
        if self.journal_id.company_id != self.company_id or self.journal_id.type != 'general':
            raise ValidationError(_('Select a miscellaneous journal of the selected company.'))
        if self.counterpart_account_id.company_ids and self.company_id not in self.counterpart_account_id.company_ids:
            raise ValidationError(_('The stock variation account is not available for the selected company.'))
        if self.counterpart_account_id.deprecated:
            raise ValidationError(_('The stock variation account is deprecated.'))
        first, last = self._period()
        lines = self._source_lines()
        if not lines:
            raise UserError(_('There are no unprocessed posted expense lines for this month.'))
        move_lines = []
        for source in lines:
            stock_account = source.account_id.with_company(self.company_id).wa_stock_account_id
            if stock_account and stock_account.company_ids and self.company_id not in stock_account.company_ids:
                raise ValidationError(_('Stock account is not available for the selected company: %s.') % stock_account.display_name)
            if not stock_account or stock_account == self.counterpart_account_id:
                raise ValidationError(_('Invalid stock account mapping for %s.') % source.account_id.display_name)
            if source.account_id == self.counterpart_account_id:
                raise ValidationError(_('The stock variation account cannot be a source account.'))
            amount = source.balance
            distribution = dict(source.analytic_distribution or {})
            common = {'name': source.name or source.account_id.display_name,
                      'analytic_distribution': distribution,
                      'partner_id': source.partner_id.id or False}
            move_lines.append((0, 0, {
                **common, 'account_id': stock_account.id,
                'debit': max(amount, 0), 'credit': max(-amount, 0),
                'wa_stock_source_line_id': source.id,
            }))
            move_lines.append((0, 0, {
                **common, 'account_id': self.counterpart_account_id.id,
                'debit': max(-amount, 0), 'credit': max(amount, 0),
            }))
        move = self.env['account.move'].with_company(self.company_id).create({
            'move_type': 'entry', 'company_id': self.company_id.id,
            'journal_id': self.journal_id.id, 'date': last,
            'ref': _('Monthly stock transfer %s') % first.strftime('%Y-%m'),
            'line_ids': move_lines,
        })
        return {
            'type': 'ir.actions.act_window', 'res_model': 'account.move',
            'res_id': move.id, 'view_mode': 'form', 'target': 'current',
        }
