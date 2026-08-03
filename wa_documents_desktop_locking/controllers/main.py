from datetime import timedelta
import hmac, secrets
from odoo import fields, http
from odoo.http import request
from odoo.addons.wa_documents_desktop_api.controllers.main import WADesktopAPI

class WADesktopLocking(WADesktopAPI):
    def timeout(self):
        return int(request.env["ir.config_parameter"].sudo().get_param("wa_documents_desktop.lock_minutes",30))
    def supplied(self): return request.httprequest.headers.get("X-WA-Lock-Token","")
    def owns(self, doc):
        return doc.wa_desktop_lock_uid == request.env.user and self.supplied() and hmac.compare_digest(self.supplied(),doc.wa_desktop_lock_token or "")

    @http.route("/wa_documents_desktop/api/document/<int:document_id>/lock",type="http",auth="public",methods=["POST"],csrf=False,save_session=False)
    def lock(self,document_id,**kw):
        doc,error=self.authenticate(document_id,write=True)
        if error:return error
        expiry=fields.Datetime.now()-timedelta(minutes=self.timeout())
        if doc.wa_desktop_lock_uid and doc.wa_desktop_lock_uid != request.env.user and doc.wa_desktop_lock_date and doc.wa_desktop_lock_date > expiry:
            return self.json({"error":"locked","message":f"Locked by {doc.wa_desktop_lock_uid.display_name}."},423)
        token=secrets.token_urlsafe(32)
        doc.sudo().write({"wa_desktop_lock_uid":request.env.user.id,"wa_desktop_lock_date":fields.Datetime.now(),
                          "wa_desktop_lock_token":token,"wa_desktop_lock_machine":request.httprequest.headers.get("X-WA-Machine","")[:128]})
        return self.json({"status":"locked","lock_token":token,"expires_in_minutes":self.timeout()})

    @http.route("/wa_documents_desktop/api/document/<int:document_id>/heartbeat",type="http",auth="public",methods=["POST"],csrf=False,save_session=False)
    def heartbeat(self,document_id,**kw):
        doc,error=self.authenticate(document_id,write=True)
        if error:return error
        if not self.owns(doc):return self.json({"error":"lock_mismatch"},423)
        doc.sudo().write({"wa_desktop_lock_date":fields.Datetime.now()})
        return self.json({"status":"alive"})

    @http.route("/wa_documents_desktop/api/document/<int:document_id>/unlock",type="http",auth="public",methods=["POST"],csrf=False,save_session=False)
    def unlock(self,document_id,**kw):
        doc,error=self.authenticate(document_id,write=True)
        if error:return error
        if self.owns(doc):doc.sudo().write({"wa_desktop_lock_uid":False,"wa_desktop_lock_date":False,"wa_desktop_lock_token":False,"wa_desktop_lock_machine":False})
        return self.json({"status":"unlocked"})
