"""Read + write last_run.json. Handles schema_version + corruption."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


SUPPORTED_SCHEMA_VERSIONS = {1}


class SnapshotError(Exception):
    """Raised on schema_version mismatch or other unrecoverable problems."""


def write_snapshot(path: Path, payload: dict) -> None:
    """Atomically write a snapshot JSON to path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def read_snapshot(path: Path) -> dict | None:
    """Read last_run.json. Returns None if file is missing OR malformed (after
    backing up the malformed file). Raises SnapshotError on schema_version
    mismatch (recoverable schema mismatches are intentionally surfaced rather
    than swallowed)."""
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
    except (OSError, json.JSONDecodeError):
        # Back up the unreadable file, return None (caller treats as first run).
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = path.with_suffix(path.suffix + f".broken-{ts}")
        try:
            path.rename(backup)
        except OSError:
            pass
        return None

    version = data.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise SnapshotError(
            f"last_run.json schema_version={version!r} not supported "
            f"(supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)}). "
            f"Delete the file to regenerate from scratch, or run a migration."
        )
    return data
