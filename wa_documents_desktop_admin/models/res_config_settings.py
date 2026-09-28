from odoo import fields, models
class ResConfigSettings(models.TransientModel):
    _inherit="res.config.settings"
    wa_desktop_token_lifetime=fields.Integer(string="Desktop token lifetime (seconds)",config_parameter="wa_documents_desktop_api.token_lifetime_seconds",default=28800)
    wa_desktop_lock_minutes=fields.Integer(string="Desktop lock timeout (minutes)",config_parameter="wa_documents_desktop.lock_minutes",default=30)
