from __future__ import annotations

import argparse
import json
import sys

from .commands import execute_command
from .config import ensure_config
from .exceptions import ConnectorError
from .logging_setup import configure_logging, log_path
from .protocol import ProtocolError, parse_protocol_url
from .registry import install_protocol, protocol_status
from .version import VERSION


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WA Desktop Connector")
    parser.add_argument("--install-protocol", action="store_true")
    parser.add_argument("--protocol-status", action="store_true")
    parser.add_argument("--show-log", action="store_true")
    parser.add_argument(
        "--download-only",
        action="store_true",
        help="Download a document without opening it in its Windows application.",
    )
    parser.add_argument("url", nargs="?")
    return parser


def _sanitized_result(result: dict) -> dict:
    parameters = result.get("parameters")
    if isinstance(parameters, dict) and "access_token" in parameters:
        result = dict(result)
        result["parameters"] = dict(parameters)
        result["parameters"]["access_token"] = "***"
    return result


def main() -> int:
    ensure_config()
    logger = configure_logging()
    args = build_parser().parse_args()

    try:
        if args.install_protocol:
            command = install_protocol()
            logger.info("WA protocol installed: %s", command)
            print("Protocol installed.")
            print(command)
            return 0

        if args.protocol_status:
            command = protocol_status()
            if command:
                print("Registered:")
                print(command)
                return 0
            print("Protocol not installed.")
            return 1

        if args.show_log:
            print(log_path())
            return 0

        if args.url:
            request = parse_protocol_url(args.url)
            result = execute_command(request, open_file=not args.download_only)
            safe_result = _sanitized_result(result)
            logger.info("Protocol command completed: %s", json.dumps(safe_result, ensure_ascii=False))
            print(json.dumps(safe_result, indent=2, ensure_ascii=False))
            return 0

        print(f"WA Desktop Connector {VERSION}")
        print("Run with --install-protocol to register wa:// in Windows.")
        return 0

    except (ProtocolError, ConnectorError, RuntimeError, OSError) as exc:
        logger.error("Connector error: %s", exc, exc_info=True)
        print(f"Error: {exc}", file=sys.stderr)
        return 1
