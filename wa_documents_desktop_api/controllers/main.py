from __future__ import annotations
import base64, hashlib, hmac, json, time
from urllib.parse import quote
from odoo import http
from odoo.http import request
from ..models.documents_document import TOKEN_SECRET_PARAM

class TokenError(ValueError): pass

def decode(value): return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

class WADesktopAPI(http.Controller):
    def json(self, payload, status=200):
        return request.make_json_response(payload, status=status, headers=[("Cache-Control","no-store")])

    def authenticate(self, document_id, write=False):
        try:
            scheme, sep, token = request.httprequest.headers.get("Authorization", "").partition(" ")
            if not sep or scheme.lower() != "bearer": raise TokenError("Missing Bearer token.")
            encoded, signature = token.strip().split(".", 1)
            payload = json.loads(decode(encoded).decode())
            secret = request.env["ir.config_parameter"].sudo().get_param(TOKEN_SECRET_PARAM)
            expected = hmac.new(secret.encode(), encoded.encode("ascii"), hashlib.sha256).digest()
            if not hmac.compare_digest(decode(signature), expected): raise TokenError("Invalid signature.")
            if payload.get("v") != 3 or int(payload.get("document_id",0)) != document_id: raise TokenError("Wrong document.")
            if int(payload.get("exp",0)) < int(time.time()): raise TokenError("Expired token.")
            if write and payload.get("scope") != "read_write": raise TokenError("Read-only token.")
        except Exception as exc:
            return None, self.json({"error":"invalid_token","message":str(exc)},401)
        request.update_env(user=int(payload["uid"]))
        document = request.env["documents.document"].browse(document_id).exists()
        if not document: return None, self.json({"error":"not_found"},404)
        try:
            document.check_access("write" if write else "read")
            document.attachment_id.check_access("write" if write else "read")
        except Exception:
            return None, self.json({"error":"not_found"},404)
        return document, None

    @staticmethod
    def etag(attachment):
        stamp = attachment.write_date.isoformat() if attachment.write_date else ""
        return hashlib.sha256(f"{attachment.id}:{attachment.checksum or ''}:{stamp}".encode()).hexdigest()

    def metadata_payload(self, document):
        a=document.attachment_id; prefix=f"/wa_documents_desktop/api/document/{document.id}"
        return {"document_id":document.id,"attachment_id":a.id,"filename":a.name or document.name,
                "mime_type":a.mimetype or "application/octet-stream","size":a.file_size or 0,
                "etag":self.etag(a),"modified":a.write_date.isoformat() if a.write_date else None,
                "download_url":prefix+"/download","upload_url":prefix+"/upload",
                "lock_url":prefix+"/lock","heartbeat_url":prefix+"/heartbeat","unlock_url":prefix+"/unlock"}

    @http.route("/wa_documents_desktop/api/document/<int:document_id>", type="http", auth="public", methods=["GET"], csrf=False, save_session=False)
    def metadata(self, document_id, **kw):
        document,error=self.authenticate(document_id)
        if error:return error
        if not document.attachment_id:return self.json({"error":"no_attachment"},409)
        return self.json(self.metadata_payload(document))

    @http.route("/wa_documents_desktop/api/document/<int:document_id>/download", type="http", auth="public", methods=["GET"], csrf=False, save_session=False)
    def download(self, document_id, **kw):
        document,error=self.authenticate(document_id)
        if error:return error
        a=document.attachment_id; content=a.raw or b""; filename=a.name or document.name
        return request.make_response(content, headers=[("Content-Type",a.mimetype or "application/octet-stream"),
            ("Content-Length",str(len(content))),("Content-Disposition",f"attachment; filename*=UTF-8''{quote(filename)}"),
            ("ETag",self.etag(a)),("Cache-Control","private, no-store"),("X-Content-Type-Options","nosniff")])
