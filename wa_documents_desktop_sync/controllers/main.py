import base64, hmac
from odoo import fields, http
from odoo.http import request
from odoo.addons.wa_documents_desktop_locking.controllers.main import WADesktopLocking

class WADesktopSync(WADesktopLocking):
    @http.route("/wa_documents_desktop/api/document/<int:document_id>/upload",type="http",auth="public",methods=["PUT","POST"],csrf=False,save_session=False)
    def upload(self,document_id,**kw):
        doc,error=self.authenticate(document_id,write=True)
        if error:return error
        a=doc.attachment_id
        if not a:return self.json({"error":"no_attachment"},409)
        if not self.owns(doc):return self.json({"error":"lock_mismatch"},423)
        before=self.etag(a); base=request.httprequest.headers.get("If-Match","").strip('"')
        Log=request.env["wa.desktop.sync.log"].sudo()
        if base and base != before:
            Log.create({"document_id":doc.id,"user_id":request.env.user.id,"status":"conflict","etag_before":base,"etag_after":before,"message":"Remote document changed."})
            return self.json({"error":"conflict","message":"The Odoo document changed after it was opened.","current_etag":before},409)
        content=request.httprequest.get_data(cache=False)
        if not content:return self.json({"error":"empty_upload"},400)
        filename=request.httprequest.headers.get("X-WA-Filename") or a.name
        a.write({"datas":base64.b64encode(content),"name":filename})
        doc.sudo().write({"wa_desktop_lock_date":fields.Datetime.now()})
        after=self.etag(a)
        Log.create({"document_id":doc.id,"user_id":request.env.user.id,"status":"uploaded","etag_before":before,"etag_after":after,"filename":filename,"size":len(content)})
        return self.json({"status":"uploaded",**self.metadata_payload(doc)})
