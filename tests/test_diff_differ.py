"""Tests for snapshot diffing."""
from __future__ import annotations

from proposal_build.diff.differ import diff_snapshots, ChangeReport


def _snap(brief=None, worksheet=None, renderings=None, slides_rendered=None):
    return {
        "schema_version": 1,
        "generated_at": "2026-05-13T00:00:00Z",
        "revision": 1,
        "brief": brief or {},
        "worksheet": worksheet or {},
        "renderings": renderings or {},
        "slides_rendered": slides_rendered or [],
        "outputs": {},
    }


def test_diff_no_changes():
    snap = _snap(brief={"a": "sha256:1"}, worksheet={"row.1.x": "sha256:2"})
    cr = diff_snapshots(prior=snap, current=snap)
    assert isinstance(cr, ChangeReport)
    assert cr.has_changes is False
    assert cr.brief == {}
    assert cr.worksheet == {}


def test_diff_brief_field_modified():
    prior = _snap(brief={"design_phrase": "sha256:OLD"})
    current = _snap(brief={"design_phrase": "sha256:NEW"})
    cr = diff_snapshots(prior=prior, current=current)
    assert cr.has_changes
    assert cr.brief == {"design_phrase": ("modified",)}


def test_diff_brief_field_added():
    prior = _snap(brief={"design_phrase": "sha256:A"})
    current = _snap(brief={"design_phrase": "sha256:A", "tree_comparison.recommended": "sha256:B"})
    cr = diff_snapshots(prior=prior, current=current)
    assert "tree_comparison.recommended" in cr.brief
    assert cr.brief["tree_comparison.recommended"] == ("added",)


def test_diff_brief_field_removed():
    prior = _snap(brief={"x": "sha256:1", "y": "sha256:2"})
    current = _snap(brief={"x": "sha256:1"})
    cr = diff_snapshots(prior=prior, current=current)
    assert cr.brief["y"] == ("removed",)


def test_diff_worksheet_cell_modified():
    prior = _snap(worksheet={"row.30.rental_high": "sha256:OLD"})
    current = _snap(worksheet={"row.30.rental_high": "sha256:NEW"})
    cr = diff_snapshots(prior=prior, current=current)
    assert cr.worksheet["row.30.rental_high"] == ("modified",)


def test_diff_rendering_added():
    prior = _snap(renderings={})
    current = _snap(renderings={"Base Scope/22_new.png": "sha256:N"})
    cr = diff_snapshots(prior=prior, current=current)
    assert cr.renderings["Base Scope/22_new.png"] == ("added",)


def test_diff_slide_added_to_render_list():
    prior = _snap(slides_rendered=[{"layout": "cover", "page": 1}])
    current = _snap(slides_rendered=[
        {"layout": "cover", "page": 1},
        {"layout": "tree_comparison", "page": 12},
    ])
    cr = diff_snapshots(prior=prior, current=current)
    assert "tree_comparison" in cr.slides_added


from proposal_build.diff.dep_map import (
    DepMap, SlideEntry, BriefEntry, WorksheetEntry,
)
from proposal_build.diff.differ import compute_affected_slides


def _slide_entry(brief_paths=(), worksheet_patterns=()):
    return SlideEntry(
        brief=tuple(BriefEntry(p, p) for p in brief_paths),
        worksheet=tuple(WorksheetEntry(p, p) for p in worksheet_patterns),
        renderings=(), follow=(),
    )


def test_affected_slides_brief_path_change():
    dep_map = DepMap(
        schema_version=1,
        slides={
            "cover": _slide_entry(brief_paths=("client_name",)),
            "tree_comparison": _slide_entry(brief_paths=("tree_comparison.recommended",)),
        },
        itemized_pricing_pdf=None,
        customer_workbook_xlsx=None,
    )
    cr = ChangeReport(
        brief={"client_name": ("modified",)},
        worksheet={}, renderings={},
        slides_added=frozenset(), slides_removed=frozenset(),
    )
    affected = compute_affected_slides(
        cr, dep_map,
        brief_flat={"client_name": "Acme", "tree_comparison.recommended": "tree_50"},
        worksheet_hashes={},
        rendered_slides=("cover", "tree_comparison"),
    )
    assert "cover" in affected
    assert "tree_comparison" not in affected


def test_affected_slides_worksheet_pattern_match():
    dep_map = DepMap(
        schema_version=1,
        slides={
            "rom_investment": _slide_entry(worksheet_patterns=("row.*.rental_high",)),
            "cover": _slide_entry(brief_paths=("client_name",)),
        },
        itemized_pricing_pdf=None,
        customer_workbook_xlsx=None,
    )
    cr = ChangeReport(
        brief={}, worksheet={"row.30.rental_high": ("modified",)},
        renderings={}, slides_added=frozenset(), slides_removed=frozenset(),
    )
    affected = compute_affected_slides(
        cr, dep_map,
        brief_flat={"client_name": "Acme"},
        worksheet_hashes={"row.30.rental_high": "sha256:x"},
        rendered_slides=("cover", "rom_investment"),
    )
    assert "rom_investment" in affected
    assert "cover" not in affected


def test_affected_slides_only_includes_rendered():
    """Slides not in this run's slides_rendered list shouldn't appear."""
    dep_map = DepMap(
        schema_version=1,
        slides={
            "tree_comparison": _slide_entry(brief_paths=("tree_comparison.recommended",)),
        },
        itemized_pricing_pdf=None, customer_workbook_xlsx=None,
    )
    cr = ChangeReport(
        brief={"tree_comparison.recommended": ("modified",)},
        worksheet={}, renderings={},
        slides_added=frozenset(), slides_removed=frozenset(),
    )
    affected = compute_affected_slides(
        cr, dep_map, brief_flat={"tree_comparison.recommended": "tree_50"},
        worksheet_hashes={},
        rendered_slides=(),  # nothing rendered this run
    )
    assert affected == set()
