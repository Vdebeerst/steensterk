import hashlib
import time
from pathlib import Path

from wa_desktop_connector_cache.store import load, save
from wa_desktop_connector_core.config import ensure
from wa_desktop_connector_core.logging_setup import configure
from wa_desktop_connector_sync.client import Client
from wa_desktop_connector_locking.manager import LockManager
from wa_desktop_connector_ui.notifications import error


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def readable_digest(path, log, document_id, attempts=12, delay=0.25):
    """Read a file hash, tolerating the short exclusive locks used by Office.

    A temporary PermissionError must never terminate the monitor. Excel can keep
    the workbook locked briefly while completing Ctrl+S.
    """
    last_exc = None
    for attempt in range(1, attempts + 1):
        try:
            return digest(path)
        except (PermissionError, OSError) as exc:
            last_exc = exc
            log.info(
                "File temporarily unavailable document=%s file=%s attempt=%s/%s error=%s",
                document_id, Path(path).name, attempt, attempts, exc,
            )
            time.sleep(delay)
    raise last_exc


def stable(path, seconds):
    first = (path.stat().st_size, path.stat().st_mtime_ns)
    time.sleep(seconds)
    return first == (path.stat().st_size, path.stat().st_mtime_ns)


def wait_until_stable(path, log, document_id, settle_seconds, attempts=8):
    for attempt in range(1, attempts + 1):
        try:
            if stable(path, settle_seconds):
                # Also prove that the completed Office file is readable before upload.
                readable_digest(path, log, document_id)
                return True
        except (PermissionError, OSError) as exc:
            log.info(
                "Waiting for Office save document=%s file=%s attempt=%s/%s error=%s",
                document_id, Path(path).name, attempt, attempts, exc,
            )
        time.sleep(0.25)
    return False


def monitor(state_path):
    cfg = ensure()
    log = configure()
    state = load(state_path)
    path = Path(state.path)
    client = Client(state.server, state.document_id, state.token)
    locks = LockManager(client)
    last = readable_digest(path, log, state.document_id)
    heartbeat = time.monotonic()
    log.info(
        "Monitor started document=%s file=%s baseline=%s",
        state.document_id, path, last,
    )
    try:
        while True:
            time.sleep(1)

            # A transient heartbeat/network problem must not kill the file watcher.
            if time.monotonic() - heartbeat >= cfg["heartbeat_seconds"]:
                try:
                    locks.heartbeat(state.metadata["heartbeat_url"], state.lock_token)
                    log.info("Heartbeat document=%s", state.document_id)
                except Exception:
                    log.exception("Heartbeat failed document=%s; monitor continues", state.document_id)
                finally:
                    heartbeat = time.monotonic()

            try:
                current = readable_digest(path, log, state.document_id)
            except (PermissionError, OSError):
                log.exception(
                    "File still unavailable after retries document=%s file=%s; monitor continues",
                    state.document_id, path.name,
                )
                continue

            if current == last:
                continue

            log.info(
                "Change detected document=%s file=%s old=%s new=%s",
                state.document_id, path.name, last, current,
            )

            if not wait_until_stable(
                path, log, state.document_id, cfg["settle_seconds"]
            ):
                log.warning(
                    "File did not become stable document=%s file=%s; monitor continues",
                    state.document_id, path.name,
                )
                continue

            try:
                upload_hash = readable_digest(path, log, state.document_id)
                log.info(
                    "Upload started document=%s file=%s etag=%s hash=%s",
                    state.document_id, path.name, state.etag, upload_hash,
                )
                result = client.upload(
                    state.metadata["upload_url"], path, state.etag, state.lock_token
                )
                state.etag = result.get("etag", state.etag)
                state.metadata = {**state.metadata, **result}
                save(state_path, state)

                # The local workbook is the working copy. Never replace/delete it
                # after upload while Excel has it open; only advance our baseline.
                last = upload_hash
                log.info(
                    "Upload successful document=%s file=%s etag=%s baseline=%s",
                    state.document_id, path.name, state.etag, last,
                )
            except (PermissionError, OSError) as exc:
                # Office may briefly lock the workbook even after a change event.
                # Keep the old baseline so the same change is retried next loop.
                log.warning(
                    "Upload deferred document=%s file=%s error=%s; monitor continues",
                    state.document_id, path.name, exc,
                )
            except Exception as exc:
                error(f"Synchronization failed for {path.name}: {exc}")
                log.exception(
                    "Upload failed document=%s file=%s; monitor continues",
                    state.document_id, path.name,
                )
    finally:
        try:
            locks.release(state.metadata["unlock_url"], state.lock_token)
            log.info("Lock released document=%s", state.document_id)
        except Exception:
            log.exception("Unlock failed document=%s", state.document_id)
