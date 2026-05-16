"""Tests for last_run.json read/write + schema handling."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from proposal_build.diff.snapshot import (
    write_snapshot, read_snapshot, SnapshotError, SUPPORTED_SCHEMA_VERSIONS,
)


def test_write_then_read_roundtrip(tmp_path: Path):
    payload = {
        "schema_version": 1,
        "generated_at": "2026-05-14T18:00:00Z",
        "revision": 2,
        "brief": {"design_phrase": "sha256:abc"},
        "worksheet": {"row.20.rental_low": "sha256:def"},
        "renderings": {},
        "slides_rendered": [{"layout": "cover", "page": 1}],
        "outputs": {"deck_pdf": "sha256:ghi"},
    }
    path = tmp_path / "last_run.json"
    write_snapshot(path, payload)

    loaded = read_snapshot(path)
    assert loaded["revision"] == 2
    assert loaded["brief"]["design_phrase"] == "sha256:abc"


def test_read_missing_returns_none(tmp_path: Path):
    assert read_snapshot(tmp_path / "missing.json") is None


def test_read_schema_version_mismatch(tmp_path: Path):
    path = tmp_path / "last_run.json"
    path.write_text(json.dumps({"schema_version": 99}))
    with pytest.raises(SnapshotError, match="schema_version"):
        read_snapshot(path)


def test_read_malformed_backs_up_and_returns_none(tmp_path: Path):
    path = tmp_path / "last_run.json"
    path.write_text("{ this is not valid json")
    result = read_snapshot(path)
    assert result is None
    # Backup file should exist alongside.
    backups = list(tmp_path.glob("last_run.json.broken-*"))
    assert len(backups) == 1


def test_supported_schema_versions_includes_1():
    assert 1 in SUPPORTED_SCHEMA_VERSIONS
