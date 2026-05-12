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


def test_build_sample_of_work_ctx_emits_six_tiles():
    """build_sample_of_work_ctx returns tiles with formatted location_year."""
    from proposal_build.composer.ctx_builders import build_sample_of_work_ctx
    from proposal_build.models import ProjectModel, Tier
    # Minimal model — only fields that build_sample_of_work_ctx touches need to be valid.
    model = ProjectModel(
        client_company="X", client_short="X", project_name="X", project_short="X",
        project_year=2026, project_subtitle="", proposal_type="Holiday Proposal",
        presenter_name="", presenter_title="", presenter_email="", presenter_phone="",
        proposal_date="", go_live="2026-11-15", season_end="2027-01-10",
        fabrication_lock="2026-08-22", signing_deadline="2026-10-25",
        voice="civic", recommended_tier=Tier.ENHANCED, design_phrase="",
        pricing_format="single", cover_image="", creative_vision_hero="",
        case_study="skip", case_study_hero="",
        zones=(), line_items=(),
        creative_direction="", customer_goals=(), customer_constraints=(),
        success_criteria=(), what_youre_approving="",
        pillars=(), phases=(), scope_includes=(), add_ons=(), term_panels={},
        after_approval_steps=(), company_facts=(), team=(), contact_strip="",
        partnership_discounts=(),
    )
    entries = [
        {"id": "fixture_a", "name": "Sample Project A",
         "location": "Sample City, AA", "year": 2024, "image": "/abs/path/a.jpg"},
        {"id": "fixture_b", "name": "Sample Project B",
         "location": "Sample City, BB", "year": 2024, "image": "/abs/path/b.jpg"},
    ]
    ctx = build_sample_of_work_ctx(model, page_num=10, page_total=14,
                                   past_work_entries=entries)
    assert ctx["page_eyebrow"] == "Sample of Our Work"
    assert ctx["page_title"] == "Recent installations"
    assert ctx["page_num"] == 10
    assert ctx["page_total"] == 14
    assert len(ctx["tiles"]) == 2
    assert ctx["tiles"][0] == {
        "name": "Sample Project A",
        "location_year": "Sample City, AA · 2024",
        "image": "/abs/path/a.jpg",
    }
