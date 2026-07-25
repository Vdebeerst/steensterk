from __future__ import annotations

import sys
from pathlib import Path

from .constants import REGISTRY_KEY


def _winreg():
    if sys.platform != "win32":
        raise RuntimeError("Windows protocol registration is only available on Windows.")
    import winreg
    return winreg


def command_value() -> str:
    main_file = Path(__file__).resolve().parent.parent / "main.py"
    return f'"{Path(sys.executable)}" "{main_file}" "%1"'


def install_protocol() -> str:
    winreg = _winreg()
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "URL:WA Protocol")
        winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")

    command = command_value()
    with winreg.CreateKey(
        winreg.HKEY_CURRENT_USER, REGISTRY_KEY + r"\shell\open\command"
    ) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
    return command


def protocol_status() -> str | None:
    winreg = _winreg()
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REGISTRY_KEY + r"\shell\open\command"
        ) as key:
            return winreg.QueryValueEx(key, "")[0]
    except FileNotFoundError:
        return None
