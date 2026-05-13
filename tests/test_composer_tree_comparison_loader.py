"""Tests for the composer's tree_library loader.

Mirrors test_composer_past_work_loader.py — uses tests/fixtures/tree_library/
for synthetic entries so production skill_assets/tree_library/ stays curated
(and ships empty for this PR).
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_LIB = Path(__file__).resolve().parent / "fixtures" / "tree_library"


def test_load_tree_entries_returns_dicts_in_order():
    """3 IDs → 3 dicts in input order; each carries spec + price + image path."""
    from proposal_build.composer import _load_tree_entries
    ids = ["fixture_tree_a", "fixture_tree_b", "fixture_tree_c"]
    entries = _load_tree_entries(ids, library_dir=FIXTURE_LIB)
    assert [e["id"] for e in entries] == ids
    assert entries[0]["name"] == "Sample Tree A — 30 ft"
    assert entries[0]["height_eyebrow"] == "30 FT"
    assert entries[0]["tagline"] == "Compact landmark presence."
    assert entries[0]["price_display"] == "$60,153"
    assert entries[0]["bullets"][0].startswith("18,700")
    assert entries[0]["image"].endswith("fixture_tree_a.jpg")
    assert Path(entries[0]["image"]).is_absolute()
    # Recommended-eligible fields make it through
    assert entries[1]["height_eyebrow"] == "40 FT"
    assert entries[1]["price_display"] == "$131,778"


def test_load_tree_entries_raises_on_unknown_id():
    """Unknown ID → FileNotFoundError (inspector catches earlier in practice)."""
    from proposal_build.composer import _load_tree_entries
    with pytest.raises(FileNotFoundError):
        _load_tree_entries(["does_not_exist"], library_dir=FIXTURE_LIB)


def test_load_tree_entries_default_library_dir_is_production():
    """No library_dir kwarg → composer.TREE_LIBRARY_DIR (production, ships empty)."""
    from proposal_build.composer import _load_tree_entries
    with pytest.raises(FileNotFoundError):
        _load_tree_entries(["fixture_tree_a"])  # production lib has no fixtures
