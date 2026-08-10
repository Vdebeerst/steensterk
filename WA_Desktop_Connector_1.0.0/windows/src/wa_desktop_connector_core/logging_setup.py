import logging
from logging.handlers import RotatingFileHandler
from .config import LOGS, ensure
def configure():
    ensure(); log=logging.getLogger("wa_desktop_connector"); log.setLevel(logging.INFO)
    if not log.handlers:
        h=RotatingFileHandler(LOGS/"connector.log",maxBytes=2_000_000,backupCount=5,encoding="utf-8")
        h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")); log.addHandler(h)
    return log
