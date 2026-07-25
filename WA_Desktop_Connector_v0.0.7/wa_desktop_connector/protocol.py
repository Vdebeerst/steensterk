from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, unquote, urlparse

from .constants import PROTOCOL_SCHEME


class ProtocolError(ValueError):
    pass


@dataclass(frozen=True)
class ProtocolRequest:
    raw_url: str
    action: str
    path: str
    parameters: dict[str, str | list[str]]


def parse_protocol_url(url: str) -> ProtocolRequest:
    parsed = urlparse(url)
    if parsed.scheme.lower() != PROTOCOL_SCHEME:
        raise ProtocolError(f"Expected '{PROTOCOL_SCHEME}://' URL, received: {url}")

    action = parsed.netloc.strip().lower()
    if not action:
        raise ProtocolError("The WA URL does not contain an action.")

    values = parse_qs(parsed.query, keep_blank_values=True)
    parameters: dict[str, str | list[str]] = {
        key: unquote(items[0]) if len(items) == 1 else [unquote(item) for item in items]
        for key, items in values.items()
    }

    return ProtocolRequest(
        raw_url=url,
        action=action,
        path=unquote(parsed.path.lstrip("/")),
        parameters=parameters,
    )
