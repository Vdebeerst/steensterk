import json, os
from pathlib import Path
APP=Path(os.getenv("APPDATA",Path.home()/"AppData/Roaming"))/"WA"/"DesktopConnector"
CONFIG=APP/"config.json"; LOGS=APP/"logs"; CACHE=APP/"cache"
def ensure():
    for p in (APP,LOGS,CACHE):p.mkdir(parents=True,exist_ok=True)
    if not CONFIG.exists():CONFIG.write_text(json.dumps({"settle_seconds":3,"heartbeat_seconds":300,"close_idle_seconds":30},indent=2))
    return json.loads(CONFIG.read_text())
