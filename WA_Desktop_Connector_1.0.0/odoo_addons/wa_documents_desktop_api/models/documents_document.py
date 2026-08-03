from __future__ import annotations
import base64, hashlib, hmac, json, secrets, time
from urllib.parse import quote, urlencode
from odoo import _, models
from odoo.exceptions import UserError

TOKEN_SECRET_PARAM = "wa_documents_desktop_api.token_secret"
TOKEN_LIFETIME_PARAM = "wa_documents_desktop_api.token_lifetime_seconds"
DEFAULT_TOKEN_LIFETIME = 8 * 60 * 60

def b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")

class DocumentsDocument(models.Model):
    _inherit = "documents.document"

    def _wa_token_secret(self):
        params = self.env["ir.config_parameter"].sudo()
        secret = params.get_param(TOKEN_SECRET_PARAM)
        if not secret:
            secret = secrets.token_urlsafe(48)
            params.set_param(TOKEN_SECRET_PARAM, secret)
        return secret

    def _wa_access_token(self, scope="read_write"):
        self.ensure_one()
        params = self.env["ir.config_parameter"].sudo()
        lifetime = int(params.get_param(TOKEN_LIFETIME_PARAM, DEFAULT_TOKEN_LIFETIME))
        payload = {"v": 3, "uid": self.env.user.id, "document_id": self.id,
                   "scope": scope, "exp": int(time.time()) + lifetime,
                   "nonce": secrets.token_urlsafe(12)}
        encoded = b64url(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
        sig = hmac.new(self._wa_token_secret().encode(), encoded.encode("ascii"), hashlib.sha256).digest()
        return f"{encoded}.{b64url(sig)}"

    def _wa_protocol_url(self):
        self.ensure_one()
        if not self.attachment_id:
            raise UserError(_("This Documents record has no file."))
        self.check_access("read"); self.attachment_id.check_access("read")
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        if not base_url:
            raise UserError(_("The Odoo web base URL is not configured."))
        params = {"server": base_url.rstrip("/"), "document_id": str(self.id),
                  "database": self.env.cr.dbname, "access_token": self._wa_access_token()}
        return f"wa://open?{urlencode(params, quote_via=quote)}"

    def action_wa_prepare_desktop_open(self):
        self.ensure_one()
        return {"url": self._wa_protocol_url()}
