"""Tests for voice preset + boilerplate loading and layered fill."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser.voice import load_voice, VoiceLoadError
from proposal_build.parser.boilerplate import load_boilerplate, substitute_placeholders


def test_load_civic_voice():
    v = load_voice("civic")
    assert v.name == "Civic"
    assert v.default_case_study == "long_beach_transit"
    assert len(v.default_pillars) == 3
    assert v.default_pillars[0]["title"] == "Civic Pride"
    assert len(v.default_phases) == 3


def test_load_unknown_voice_raises():
    with pytest.raises(VoiceLoadError):
        load_voice("nonexistent")


def test_load_boilerplate():
    bp = load_boilerplate()
    assert "Founded 1998" in bp.company_facts_default_bullets[0]
    assert any("Daniel Christenson" in m["name"] for m in bp.team_roster)
    assert "ST-NICKS.COM" in bp.contact_strip
    assert "default_payment_schedule" in bp.term_panels  # snake_case key
    assert any(d["term"] == "2-YEAR" for d in bp.partnership_discounts)


def test_substitute_placeholders_known_keys():
    text = "Hello {project_name}, year {project_year}."
    result = substitute_placeholders(text, {"project_name": "MetroLink", "project_year": 2026})
    assert result == "Hello MetroLink, year 2026."


def test_substitute_placeholders_unknown_raises():
    text = "Hello {bogus}."
    with pytest.raises(KeyError):
        substitute_placeholders(text, {"project_name": "X"})


def test_pillars_template_substitution():
    v = load_voice("civic")
    pillar0 = v.default_pillars[0]
    body_with_subs = substitute_placeholders(
        pillar0["body"],
        {"project_name": "Riverside MetroLink", "project_year": 2026, "next_year": 2027},
    )
    assert "Riverside MetroLink" in body_with_subs
