from odoo import fields, models
class DocumentsDocument(models.Model):
    _inherit="documents.document"
    wa_desktop_lock_uid=fields.Many2one("res.users",copy=False,readonly=True)
    wa_desktop_lock_date=fields.Datetime(copy=False,readonly=True)
    wa_desktop_lock_token=fields.Char(copy=False,readonly=True)
    wa_desktop_lock_machine=fields.Char(copy=False,readonly=True)
