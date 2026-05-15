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


from proposal_build.diff.dep_map import (
    resolve_slide_deps, ResolvedDeps, SlideEntry, BriefEntry, WorksheetEntry, FollowEntry,
)


def _slide(brief_paths=(), worksheet_patterns=(), follow_chains=()):
    return SlideEntry(
        brief=tuple(BriefEntry(p, p) for p in brief_paths),
        worksheet=tuple(WorksheetEntry(p, p) for p in worksheet_patterns),
        renderings=(),
        follow=tuple(
            FollowEntry(resolve_from=src, to_assets=tuple(targets))
            for src, targets in follow_chains
        ),
    )


def test_resolve_static_brief_paths():
    slide = _slide(brief_paths=("client_name", "project_name"))
    deps = resolve_slide_deps(
        slide,
        brief_flat={"client_name": "Acme", "project_name": "Holiday", "extra": "x"},
        worksheet_hashes={},
    )
    assert "client_name" in deps.brief
    assert "project_name" in deps.brief
    assert "extra" not in deps.brief


def test_resolve_worksheet_glob():
    slide = _slide(worksheet_patterns=("row.*.rental_low", "row.*.rental_high"))
    deps = resolve_slide_deps(
        slide,
        brief_flat={},
        worksheet_hashes={
            "row.20.rental_low": "sha256:a",
            "row.20.rental_high": "sha256:b",
            "row.20.purchase_ot_low": "sha256:c",
        },
    )
    assert "row.20.rental_low" in deps.worksheet
    assert "row.20.rental_high" in deps.worksheet
    assert "row.20.purchase_ot_low" not in deps.worksheet


def test_resolve_follow_chain():
    slide = _slide(
        brief_paths=("tree_comparison.trees",),
        follow_chains=(("tree_comparison.trees", ("skill_assets/tree_library/{id}.md",)),),
    )
    deps = resolve_slide_deps(
        slide,
        brief_flat={
            "tree_comparison.trees.0": "tree_30",
            "tree_comparison.trees.1": "tree_50",
        },
        worksheet_hashes={},
    )
    assert "skill_assets/tree_library/tree_30.md" in deps.assets
    assert "skill_assets/tree_library/tree_50.md" in deps.assets


def test_resolve_follow_chain_missing_source_yields_no_assets():
    slide = _slide(
        follow_chains=(("missing_field", ("skill_assets/x/{id}.md",)),),
    )
    deps = resolve_slide_deps(
        slide, brief_flat={}, worksheet_hashes={},
    )
    assert deps.assets == set() or deps.assets == frozenset()
