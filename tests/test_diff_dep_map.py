"""Tests for dependency map loading + validation."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.diff.dep_map import (
    load_dep_map, DepMapError, DepMap,
)


SKILL_DEP_MAP = (
    Path(__file__).resolve().parent.parent
    / "skill_assets" / "dependency_map.yaml"
)


def test_load_skill_dep_map():
    dm = load_dep_map(SKILL_DEP_MAP)
    assert isinstance(dm, DepMap)
    assert dm.schema_version == 1
    assert "cover" in dm.slides
    assert "tree_comparison" in dm.slides


def test_load_dep_map_missing_schema_version(tmp_path: Path):
    f = tmp_path / "dm.yaml"
    f.write_text("slides:\n  cover:\n    brief: []\n    worksheet: []\n")
    with pytest.raises(DepMapError, match="schema_version"):
        load_dep_map(f)


def test_load_dep_map_unknown_schema_version(tmp_path: Path):
    f = tmp_path / "dm.yaml"
    f.write_text("schema_version: 99\nslides: {}\n")
    with pytest.raises(DepMapError, match="schema_version"):
        load_dep_map(f)


def test_load_dep_map_file_missing(tmp_path: Path):
    with pytest.raises(DepMapError, match="not found"):
        load_dep_map(tmp_path / "missing.yaml")


def test_load_dep_map_brief_entries_have_human_labels():
    """Every brief path should have a human_label (otherwise change-report falls back)."""
    dm = load_dep_map(SKILL_DEP_MAP)
    missing = []
    for slide_name, entry in dm.slides.items():
        for brief_entry in entry.brief:
            if not brief_entry.human_label:
                missing.append(f"{slide_name}/{brief_entry.path}")
    assert missing == [], f"Brief paths without human_label: {missing}"
