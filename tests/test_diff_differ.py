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
