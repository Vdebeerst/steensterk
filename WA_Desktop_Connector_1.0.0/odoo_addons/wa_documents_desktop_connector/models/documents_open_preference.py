from odoo import fields, models


class DocumentsOpenPreference(models.Model):
    _name = "documents.open.preference"
    _description = "Documents Desktop Open Preference"

    user_id = fields.Many2one(
        "res.users",
        required=True,
        default=lambda self: self.env.user,
        ondelete="cascade",
    )
    preference = fields.Selection(
        [
            ("ask", "Ask every time"),
            ("odoo", "Always open in Odoo"),
            ("desktop", "Always open in desktop app"),
        ],
        default="ask",
        required=True,
    )
