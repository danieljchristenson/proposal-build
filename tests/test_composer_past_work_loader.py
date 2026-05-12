"""Tests for the composer's past_work_library loader.

The loader is exercised via a fixture library under tests/fixtures/past_work_library/.
Production skill_assets/past_work_library/ is curated by Daniel and ships empty.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_LIB = Path(__file__).resolve().parent / "fixtures" / "past_work_library"


def test_load_past_work_entries_returns_dicts_in_order():
    """Six IDs → six dicts in input order, each with name/location/year/image."""
    from proposal_build.composer import _load_past_work_entries
    ids = ["fixture_a", "fixture_b", "fixture_c", "fixture_d", "fixture_e", "fixture_f"]
    entries = _load_past_work_entries(ids, library_dir=FIXTURE_LIB)
    assert [e["name"] for e in entries] == [
        "Sample Project A", "Sample Project B", "Sample Project C",
        "Sample Project D", "Sample Project E", "Sample Project F",
    ]
    assert entries[0]["location"] == "Sample City, AA"
    assert entries[0]["year"] == 2024
    assert entries[0]["image"].endswith("fixture_a.jpg")
    assert Path(entries[0]["image"]).is_absolute()


def test_load_past_work_entries_raises_on_unknown_id(tmp_path):
    """Unknown ID → FileNotFoundError (inspector catches this earlier in practice)."""
    from proposal_build.composer import _load_past_work_entries
    with pytest.raises(FileNotFoundError):
        _load_past_work_entries(["nonexistent_id"], library_dir=FIXTURE_LIB)


def test_load_past_work_entries_uses_default_library_dir_when_omitted(tmp_path):
    """No library_dir kwarg → looks under skill_assets/past_work_library/.
    Production library is empty, so this should raise FileNotFoundError for any ID."""
    from proposal_build.composer import _load_past_work_entries
    with pytest.raises(FileNotFoundError):
        _load_past_work_entries(["fixture_a"])
