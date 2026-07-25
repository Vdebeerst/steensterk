from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from .exceptions import CommandError
from .odoo_client import download_document, fetch_document_metadata
from .protocol import ProtocolRequest


def _string_parameter(request: ProtocolRequest, name: str) -> str | None:
    value = request.parameters.get(name)
    if value is None:
        return None
    if isinstance(value, list):
        if len(value) != 1:
            raise CommandError(f"Parameter '{name}' may only occur once.")
        value = value[0]
    value = str(value).strip()
    return value or None


def _open_local_file(path: Path) -> None:
    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]
        return
    raise CommandError("Opening downloaded files is currently supported only on Windows.")


def execute_command(request: ProtocolRequest, *, open_file: bool = True) -> dict[str, Any]:
    if request.action != "open":
        raise CommandError(f"Unsupported WA action: {request.action}")

    token = _string_parameter(request, "access_token")
    direct_download_url = _string_parameter(request, "download_url")
    server = _string_parameter(request, "server")
    document_id = _string_parameter(request, "document_id")

    metadata = None
    if direct_download_url:
        download_url = direct_download_url
        filename = _string_parameter(request, "filename")
    elif server and document_id:
        metadata = fetch_document_metadata(
            server=server,
            document_id=document_id,
            bearer_token=token,
            metadata_url=_string_parameter(request, "metadata_url"),
            metadata_path=_string_parameter(request, "metadata_path"),
        )
        download_url = metadata.download_url
        filename = metadata.filename
    else:
        # Backwards-compatible preview mode used while testing Odoo URL generation.
        return {
            "status": "parsed",
            "action": request.action,
            "path": request.path,
            "parameters": request.parameters,
            "message": (
                "Request parsed. Supply either download_url, or both server and "
                "document_id, to retrieve a document."
            ),
        }

    target = download_document(
        download_url,
        filename=filename,
        bearer_token=token,
    )
    if open_file:
        _open_local_file(target)

    result: dict[str, Any] = {
        "status": "opened" if open_file else "downloaded",
        "action": request.action,
        "file": str(target),
    }
    if metadata:
        result["document"] = {
            "document_id": metadata.document_id,
            "filename": metadata.filename,
            "mime_type": metadata.mime_type,
            "etag": metadata.etag,
            "modified": metadata.modified,
        }
    return result
