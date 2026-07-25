from __future__ import annotations

import json
import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urljoin, urlparse
from urllib.request import Request, urlopen

from .config import app_data_dir
from .exceptions import DownloadError, OdooClientError
from .version import VERSION

_SAFE_FILENAME = re.compile(r"[^A-Za-z0-9._() -]+")
_DEFAULT_METADATA_PATH = "/wa_desktop_connector/api/document/{document_id}"


@dataclass(frozen=True)
class DocumentMetadata:
    document_id: str
    filename: str
    download_url: str
    mime_type: str | None = None
    etag: str | None = None
    modified: str | None = None


def download_dir() -> Path:
    path = app_data_dir() / "downloads"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _safe_filename(value: str) -> str:
    name = Path(unquote(value)).name.strip() or "document"
    name = _SAFE_FILENAME.sub("_", name)
    return name[:180] or "document"


def _validate_https_url(url: str, description: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https":
        raise OdooClientError(f"For safety, {description} requires an https:// URL.")
    if not parsed.hostname:
        raise OdooClientError(f"The {description} URL does not contain a valid host.")


def _request_headers(bearer_token: str | None = None) -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "User-Agent": f"WA-Desktop-Connector/{VERSION}",
    }
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    return headers


def build_metadata_url(
    server: str,
    document_id: str,
    *,
    metadata_path: str | None = None,
) -> str:
    _validate_https_url(server, "Odoo server")
    document_id = str(document_id).strip()
    if not document_id:
        raise OdooClientError("document_id is required.")

    template = metadata_path or _DEFAULT_METADATA_PATH
    if "{document_id}" in template:
        path = template.format(document_id=quote(document_id, safe=""))
    else:
        path = template.rstrip("/") + "/" + quote(document_id, safe="")
    return urljoin(server.rstrip("/") + "/", path.lstrip("/"))


def fetch_document_metadata(
    *,
    server: str,
    document_id: str,
    bearer_token: str | None = None,
    metadata_url: str | None = None,
    metadata_path: str | None = None,
    timeout: int = 30,
) -> DocumentMetadata:
    url = metadata_url or build_metadata_url(
        server, document_id, metadata_path=metadata_path
    )
    _validate_https_url(url, "metadata request")

    request = Request(url, headers=_request_headers(bearer_token), method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            payload = json.loads(response.read().decode(charset))
    except HTTPError as exc:
        raise OdooClientError(
            f"Odoo metadata request failed with HTTP status {exc.code}."
        ) from exc
    except URLError as exc:
        raise OdooClientError(f"Could not reach the Odoo server: {exc.reason}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OdooClientError("Odoo returned invalid JSON document metadata.") from exc

    if not isinstance(payload, dict):
        raise OdooClientError("Odoo metadata must be a JSON object.")

    # Accept a direct object and the common Odoo JSON-RPC {result: {...}} wrapper.
    if isinstance(payload.get("result"), dict):
        payload = payload["result"]

    filename = str(payload.get("filename") or "").strip()
    download_url = str(payload.get("download_url") or "").strip()
    if not filename:
        raise OdooClientError("Odoo metadata does not contain 'filename'.")
    if not download_url:
        raise OdooClientError("Odoo metadata does not contain 'download_url'.")

    download_url = urljoin(server.rstrip("/") + "/", download_url)
    _validate_https_url(download_url, "document download")

    server_host = urlparse(server).hostname
    download_host = urlparse(download_url).hostname
    if server_host and download_host and server_host.lower() != download_host.lower():
        allow_external = bool(payload.get("allow_external_download"))
        if not allow_external:
            raise OdooClientError(
                "Odoo returned a download URL on another host without explicit permission."
            )

    return DocumentMetadata(
        document_id=str(payload.get("document_id") or document_id),
        filename=_safe_filename(filename),
        download_url=download_url,
        mime_type=_optional_string(payload, "mime_type"),
        etag=_optional_string(payload, "etag"),
        modified=_optional_string(payload, "modified"),
    )


def _optional_string(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    result = str(value).strip()
    return result or None


def _filename_from_headers(headers, fallback_url: str, requested: str | None) -> str:
    if requested:
        return _safe_filename(requested)

    disposition = headers.get("Content-Disposition", "")
    match = re.search(r"filename\*?=(?:UTF-8''|\")?([^\";]+)", disposition, re.I)
    if match:
        return _safe_filename(match.group(1))

    url_name = Path(urlparse(fallback_url).path).name
    if url_name:
        return _safe_filename(url_name)

    content_type = headers.get_content_type() if hasattr(headers, "get_content_type") else ""
    extension = mimetypes.guess_extension(content_type or "") or ""
    return f"document{extension}"


def download_document(
    url: str,
    *,
    filename: str | None = None,
    bearer_token: str | None = None,
    timeout: int = 60,
) -> Path:
    try:
        _validate_https_url(url, "document download")
    except OdooClientError as exc:
        raise DownloadError(str(exc)) from exc

    headers = {
        "Accept": "*/*",
        "User-Agent": f"WA-Desktop-Connector/{VERSION}",
    }
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            target_name = _filename_from_headers(response.headers, url, filename)
            target = download_dir() / target_name
            temporary = target.with_suffix(target.suffix + ".part")
            with temporary.open("wb") as stream:
                while chunk := response.read(1024 * 1024):
                    stream.write(chunk)
            temporary.replace(target)
            return target
    except HTTPError as exc:
        raise DownloadError(f"Download failed with HTTP status {exc.code}.") from exc
    except URLError as exc:
        raise DownloadError(f"Could not reach the document server: {exc.reason}") from exc
    except OSError as exc:
        raise DownloadError(f"Could not save the downloaded document: {exc}") from exc
