from odoo import fields, models


class CashPlanningDashboardCompatibility(models.TransientModel):
    """Compatibility stub for earlier experimental versions.

    Some test databases may still contain ir.model metadata for
    cash.planning.dashboard. Keeping this transient model prevents autovacuum
    from crashing while the old module state is cleaned up by a normal upgrade.
    """

    _name = "cash.planning.dashboard"
    _description = "Cash Planning Dashboard Compatibility"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    start_date = fields.Date(default=fields.Date.context_today)
    weeks_ahead = fields.Integer(default=8)
