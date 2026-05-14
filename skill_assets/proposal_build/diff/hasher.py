"""sha256 hashing utilities for Brief/Worksheet/rendering/output content."""
from __future__ import annotations

import hashlib
from typing import Any

from proposal_build.parser.brief import BriefData


def hash_string(s: str) -> str:
    """Return sha256 hex of a UTF-8 string, prefixed with 'sha256:'."""
    digest = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def flatten_brief(brief: BriefData) -> dict[str, Any]:
    """Flatten a BriefData (frontmatter + sections) to JSON-path keyed dict.

    Lists are indexed (creative_phases.0.body). Dicts use dotted keys.
    Sections are prefixed with 'sections.'.
    """
    out: dict[str, Any] = {}
    _walk("", brief.frontmatter, out)
    _walk("sections", brief.sections, out)
    return out


def _walk(prefix: str, value: Any, out: dict[str, Any]) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            _walk(key, v, out)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            _walk(f"{prefix}.{i}", item, out)
    else:
        out[prefix] = value


def hash_brief(brief: BriefData) -> dict[str, str]:
    """Hash each flattened Brief path value. Returns {path: 'sha256:...'}."""
    flat = flatten_brief(brief)
    return {path: hash_string(repr(value)) for path, value in flat.items()}


def hash_worksheet_rows(rows: list[dict]) -> dict[str, str]:
    """Hash each worksheet cell. Keys: row.<item_code>.<column_name>.

    Each row dict must include an 'item_code' key. All other keys are
    treated as columns.
    """
    out: dict[str, str] = {}
    for row in rows:
        item_code = row.get("item_code")
        if item_code is None:
            continue
        for col, val in row.items():
            if col == "item_code":
                continue
            key = f"row.{item_code}.{col}"
            out[key] = hash_string(repr(val))
    return out


from pathlib import Path


def hash_file(path: Path, chunk_size: int = 65536) -> str | None:
    """Return sha256 of file contents, or None if file does not exist."""
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"
