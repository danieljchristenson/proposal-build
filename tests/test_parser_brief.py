"""Tests for parser/brief.py — Brief.md frontmatter + section parsing."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser.brief import parse_brief, BriefParseError

FIXTURES = Path(__file__).parent / "fixtures" / "briefs"


def test_minimal_valid_parses():
    data = parse_brief(FIXTURES / "minimal_valid.md")
    assert data.frontmatter["voice"] == "civic"
    assert data.frontmatter["project_name"] == "Test Project"
    assert len(data.frontmatter["zones"]) == 1
    assert data.frontmatter["zones"][0]["name"] == "Zone One"
    assert data.sections["Creative Direction"].strip() == "Test direction."
    assert data.sections["Customer Goals"] == ["Goal A", "Goal B"]
    assert data.sections["What You're Approving"].strip().startswith("The test approval")


def test_missing_voice_raises():
    with pytest.raises(BriefParseError) as exc:
        parse_brief(FIXTURES / "missing_voice.md")
    assert "voice" in str(exc.value).lower()


def test_two_signatures_raises():
    with pytest.raises(BriefParseError) as exc:
        parse_brief(FIXTURES / "two_signatures.md")
    assert "signature" in str(exc.value).lower()


def test_auto_dates_blank_passes_through():
    """parse_brief returns the raw frontmatter with blank dates;
    auto-derivation happens in the orchestrator, not the parser."""
    data = parse_brief(FIXTURES / "auto_dates.md")
    assert data.frontmatter["fabrication_lock"] == ""
    assert data.frontmatter["signing_deadline"] == ""
