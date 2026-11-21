from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AnalyticDistributionWizard(models.TransientModel):
    _name = 'wa.account.analytic.distribution.wizard'
    _description = 'Update Journal Item Analytic Distributions'

    account_id = fields.Many2one('account.account', required=True, readonly=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True)
    scope = fields.Selection([('all', 'All journal items'), ('missing', 'Only missing distributions')], required=True, default='all')
    update_method = fields.Selection([
        ('replace', 'Replace entire distribution'),
        ('merge', 'Update matching analytic plans and preserve other plans'),
    ], required=True, default='merge')
    line_count = fields.Integer(string='Journal Items to Update', compute='_compute_line_count')

    def _domain(self):
        self.ensure_one()
        domain = [('account_id', '=', self.account_id.id), ('company_id', '=', self.company_id.id)]
        if self.scope == 'missing':
            domain += ['|', ('analytic_distribution', '=', False), ('analytic_distribution', '=', {})]
        return domain

    @api.depends('account_id', 'company_id', 'scope')
    def _compute_line_count(self):
        for wizard in self:
            wizard.line_count = self.env['account.move.line'].search_count(wizard._domain()) if wizard.account_id and wizard.company_id else 0

    def _merge_plans(self, line, existing, incoming):
        """Use Odoo's own plan-aware distribution merge implementation."""
        ids = {int(i) for key in incoming for i in key.split(',')}
        accounts = self.env['account.analytic.account'].browse(list(ids)).exists()
        if len(accounts) != len(ids):
            raise ValidationError(_('One or more analytic accounts in the distribution no longer exist.'))
        columns = list({account.root_plan_id._column_name() for account in accounts})
        values = dict(incoming)
        values['__update__'] = columns
        return line._merge_distribution(dict(existing), values)

    def action_confirm(self):
        self.ensure_one()
        if self.company_id not in self.env.companies:
            raise UserError(_('The selected company is not among your allowed companies.'))
        distribution = self.account_id.with_company(self.company_id).wa_analytic_distribution or {}
        if not distribution:
            raise UserError(_('Configure an analytic distribution on this account for the selected company first.'))
        lines = self.env['account.move.line'].with_company(self.company_id).search(self._domain())
        for line in lines:
            values = dict(distribution) if self.update_method == 'replace' or not line.analytic_distribution else self._merge_plans(line, line.analytic_distribution, distribution)
            if values != (line.analytic_distribution or {}):
                line.write({'analytic_distribution': values})
        return {'type': 'ir.actions.act_window_close'}
