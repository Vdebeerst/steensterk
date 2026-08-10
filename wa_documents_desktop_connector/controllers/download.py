from pathlib import Path

from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound


class WADesktopConnectorDownload(http.Controller):

    @http.route(
        "/wa_desktop_connector/download/installer",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def download_installer(self, **kwargs):
        filename = "WA Desktop Connector Setup.exe"
        module_root = Path(__file__).resolve().parents[1]
        path = module_root / "static" / "installer" / filename

        if not path.is_file():
            raise NotFound(
                "The WA Desktop Connector installer has not yet been added to this release."
            )

        content = path.read_bytes()
        return request.make_response(
            content,
            headers=[
                ("Content-Type", "application/vnd.microsoft.portable-executable"),
                ("Content-Disposition", f'attachment; filename="{filename}"'),
                ("Content-Length", str(len(content))),
                ("Cache-Control", "no-store"),
                ("X-Content-Type-Options", "nosniff"),
            ],
        )
