"""Tests for change_summary.md generation."""
from __future__ import annotations

from proposal_build.diff.dep_map import (
    DepMap, SlideEntry, BriefEntry, WorksheetEntry,
)
from proposal_build.diff.differ import ChangeReport
from proposal_build.diff.summary import (
    render_change_summary, render_initial_summary,
)


def _dep_map_with_labels():
    return DepMap(
        schema_version=1,
        slides={
            "tree_comparison": SlideEntry(
                brief=(
                    BriefEntry(path="tree_comparison.recommended",
                               human_label="Recommended tree size"),
                ),
                worksheet=(), renderings=(), follow=(),
            ),
            "rom_investment": SlideEntry(
                brief=(),
                worksheet=(WorksheetEntry(pattern="row.*.rental_high",
                                          human_label="Annual rental high"),),
                renderings=(), follow=(),
            ),
        },
        itemized_pricing_pdf=None, customer_workbook_xlsx=None,
    )


def test_render_initial_summary():
    text = render_initial_summary(
        client_name="FIGat7th DTLA",
        revision=1,
        generated_at="2026-05-14",
    )
    assert "Revision 1" in text
    assert "FIGat7th DTLA" in text
    assert "Initial revision" in text


def test_render_change_summary_includes_brief_bullet():
    cr = ChangeReport(
        brief={"tree_comparison.recommended": ("modified",)},
        worksheet={}, renderings={},
        slides_added=frozenset(), slides_removed=frozenset(),
    )
    text = render_change_summary(
        client_name="FIGat7th DTLA",
        revision=2,
        prior_revision=1,
        prior_generated_at="2026-05-13",
        current_generated_at="2026-05-14",
        change_report=cr,
        affected_slides={"tree_comparison"},
        dep_map=_dep_map_with_labels(),
    )
    assert "Revision 2" in text
    assert "Recommended tree size" in text


def test_render_change_summary_falls_back_to_path_when_label_missing():
    cr = ChangeReport(
        brief={"unknown_field": ("modified",)},
        worksheet={}, renderings={},
        slides_added=frozenset(), slides_removed=frozenset(),
    )
    text = render_change_summary(
        client_name="X", revision=2, prior_revision=1,
        prior_generated_at="2026-05-13", current_generated_at="2026-05-14",
        change_report=cr, affected_slides=set(),
        dep_map=_dep_map_with_labels(),
    )
    assert "unknown_field" in text  # bare path fallback


def test_render_change_summary_no_em_dashes():
    """Customer-facing copy must not contain em dashes (per feedback)."""
    cr = ChangeReport(
        brief={"tree_comparison.recommended": ("modified",)},
        worksheet={}, renderings={},
        slides_added=frozenset(), slides_removed=frozenset(),
    )
    text = render_change_summary(
        client_name="X", revision=2, prior_revision=1,
        prior_generated_at="2026-05-13", current_generated_at="2026-05-14",
        change_report=cr, affected_slides={"tree_comparison"},
        dep_map=_dep_map_with_labels(),
    )
    # Section between first and second '---' is customer-facing; below is internal.
    parts = text.split("---")
    # parts[0] = header, parts[1] = customer-facing, parts[2] = internal footer.
    customer_section = parts[1] if len(parts) >= 2 else text
    assert "—" not in customer_section, "em dash found in customer-facing section"
