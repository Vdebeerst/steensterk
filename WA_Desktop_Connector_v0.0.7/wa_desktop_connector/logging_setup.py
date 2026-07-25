from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import app_data_dir


def log_path() -> Path:
    path = app_data_dir() / "logs" / "wa-desktop-connector.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("wa_desktop_connector")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        log_path(), maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(handler)
    return logger
