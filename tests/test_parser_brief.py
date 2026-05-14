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


def test_brief_sample_work_absent_defaults_to_empty_tuple(tmp_path):
    """A Brief without sample_work: yields ProjectModel.sample_work == ()."""
    from proposal_build.parser import build_project_model
    project_dir = (
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    model, _ = build_project_model(project_dir)
    assert model.sample_work == ()


def test_brief_sample_work_present_is_parsed_as_tuple(tmp_path, monkeypatch):
    """A Brief with sample_work: [a, b, c] yields a tuple of 3 strings."""
    import shutil
    from proposal_build.parser import build_project_model
    src = (
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    dst = tmp_path / "fake_project"
    shutil.copytree(src, dst)
    brief = dst / "04 - Process & Notes" / "Project Brief.md"
    txt = brief.read_text()
    new_yaml_line = "sample_work:\n  - fixture_a\n  - fixture_b\n  - fixture_c\n"
    parts = txt.split("---", 2)
    assert len(parts) >= 3, "Expected YAML frontmatter delimited by ---"
    parts[1] = parts[1].rstrip() + "\n" + new_yaml_line
    brief.write_text("---".join(parts))

    model, _ = build_project_model(dst)
    assert model.sample_work == ("fixture_a", "fixture_b", "fixture_c")
