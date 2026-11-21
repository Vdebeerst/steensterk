from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('account_id', 'partner_id', 'product_id', 'move_id', 'move_id.company_id')
    def _compute_analytic_distribution(self):
        super()._compute_analytic_distribution()
        for line in self:
            if line.account_id and not line.analytic_distribution:
                company = line.company_id or line.move_id.company_id or self.env.company
                distribution = line.account_id.with_company(company).wa_analytic_distribution
                if distribution:
                    line.analytic_distribution = dict(distribution)
