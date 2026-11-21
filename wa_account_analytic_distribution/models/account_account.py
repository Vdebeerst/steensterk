from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    wa_analytic_distribution = fields.Json(string='Default Analytic Distribution', default=dict)

    def _wa_open_distribution_wizard(self, scope):
        self.ensure_one()
        if not self.wa_analytic_distribution:
            raise UserError(_('Configure an analytic distribution on this account for the active company first.'))
        return {
            'type': 'ir.actions.act_window', 'name': _('Update Journal Item Analytic Distributions'),
            'res_model': 'wa.account.analytic.distribution.wizard', 'view_mode': 'form', 'target': 'new',
            'context': {'default_account_id': self.id, 'default_company_id': self.env.company.id,
                        'default_scope': scope, 'default_update_method': 'merge'},
        }

    def action_wa_update_all_distributions(self):
        return self._wa_open_distribution_wizard('all')

    def action_wa_fill_missing_distributions(self):
        return self._wa_open_distribution_wizard('missing')
