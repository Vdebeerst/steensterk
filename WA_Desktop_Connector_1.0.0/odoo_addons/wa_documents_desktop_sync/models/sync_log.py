from odoo import fields, models
class WADesktopSyncLog(models.Model):
    _name="wa.desktop.sync.log"; _description="WA Desktop synchronization log"; _order="create_date desc"
    document_id=fields.Many2one("documents.document",required=True,ondelete="cascade",index=True)
    user_id=fields.Many2one("res.users",required=True,default=lambda self:self.env.user)
    status=fields.Selection([("uploaded","Uploaded"),("conflict","Conflict"),("error","Error")],required=True)
    etag_before=fields.Char(); etag_after=fields.Char(); filename=fields.Char(); size=fields.Integer(); message=fields.Text()
