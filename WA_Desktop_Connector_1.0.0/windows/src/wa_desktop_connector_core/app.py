import argparse, os, socket, subprocess, sys
from pathlib import Path
from .config import ensure
from .errors import ConnectorError
from .logging_setup import configure
from .protocol import parse
from .registry import install
from wa_desktop_connector_sync.client import Client
from wa_desktop_connector_cache.store import Store, State
from wa_desktop_connector_locking.manager import LockManager

def args():
    p=argparse.ArgumentParser();p.add_argument("--install-protocol",action="store_true");p.add_argument("--monitor");p.add_argument("url",nargs="?");return p.parse_args()
def detached(state):
    cmd=[sys.executable,"--monitor",str(state)] if getattr(sys,"frozen",False) else [sys.executable,"-m","wa_desktop_connector_core.app","--monitor",str(state)]
    flags=subprocess.CREATE_NO_WINDOW|subprocess.DETACHED_PROCESS|subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform=="win32" else 0
    subprocess.Popen(cmd,creationflags=flags,close_fds=True)
def main():
    ensure();log=configure();a=args()
    try:
        if a.install_protocol:install();return 0
        if a.monitor:
            from wa_desktop_connector_monitor.watcher import monitor
            monitor(Path(a.monitor));return 0
        if not a.url:return 0
        req=parse(a.url)
        if req.action!="open":raise ConnectorError("Unsupported action.")
        client=Client(req.values["server"],req.values["document_id"],req.values["access_token"])
        meta=client.metadata(); lock=LockManager(client).acquire(socket.gethostname())
        store=Store(req.values["document_id"]); target=store.target(meta["filename"]);client.download(meta["download_url"],target)
        state=State(client.server,client.document_id,client.token,str(target),meta["etag"],lock,meta)
        path=store.save(state);detached(path)
        if sys.platform=="win32":os.startfile(target)
        log.info("Opened document %s",client.document_id);return 0
    except Exception as exc:
        log.exception("Connector failure");
        try:
            from wa_desktop_connector_ui.notifications import error
            error(str(exc))
        except Exception:pass
        return 1
if __name__=="__main__":raise SystemExit(main())
