from __future__ import annotations

import configparser
import os
from pathlib import Path

from .constants import APP_NAME


def app_data_dir() -> Path:
    base = os.environ.get("APPDATA")
    if base:
        return Path(base) / "WA"
    return Path.home() / ".wa-desktop-connector"


def config_path() -> Path:
    return app_data_dir() / "config.ini"


def ensure_config() -> Path:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        config = configparser.ConfigParser()
        config["application"] = {
            "name": APP_NAME,
            "log_level": "INFO",
        }
        with path.open("w", encoding="utf-8") as stream:
            config.write(stream)
    return path
