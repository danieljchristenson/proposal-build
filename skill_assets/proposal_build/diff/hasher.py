"""sha256 hashing utilities for Brief/Worksheet/rendering/output content."""
from __future__ import annotations

import hashlib


def hash_string(s: str) -> str:
    """Return sha256 hex of a UTF-8 string, prefixed with 'sha256:'."""
    digest = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"
