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
