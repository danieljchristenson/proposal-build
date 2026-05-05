"""Tests for the Brief inspector."""
from pathlib import Path

from proposal_build.inspector.brief import check


def _write_brief(path: Path, frontmatter: dict, body: str = "") -> None:
    import yaml
    text = "---\n" + yaml.safe_dump(frontmatter) + "---\n" + body
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_missing_brief_file_reports_blocker(tmp_path):
    proj = tmp_path / "P"
    (proj / "04 - Process & Notes").mkdir(parents=True)
    findings = check(proj)
    blockers = [f for f in findings if f.severity == "blocker"
                                       and f.issue == "missing-brief"]
    assert len(blockers) == 1


def test_missing_required_frontmatter_field_reports_blocker(tmp_path):
    proj = tmp_path / "P"
    brief = proj / "04 - Process & Notes" / "Project Brief.md"
    _write_brief(brief, frontmatter={
        "project_name": "Test", "project_short": "T",
    })
    findings = check(proj)
    issues = [(f.issue, f.field) for f in findings
              if f.issue == "missing-field"]
    assert ("missing-field", "client_company") in issues


def test_zone_without_hero_image_reports_warning(tmp_path):
    proj = tmp_path / "P"
    brief = proj / "04 - Process & Notes" / "Project Brief.md"
    _write_brief(brief, frontmatter={
        "client_company": "X", "client_short": "X",
        "project_name": "Y", "project_short": "Y",
        "project_year": 2026, "proposal_type": "Holiday Proposal",
        "presenter_name": "P", "presenter_title": "T",
        "presenter_email": "p@x.com", "presenter_phone": "555-0100",
        "proposal_date": "2026-05-05", "go_live": "2026-11-14",
        "voice": "civic", "recommended_tier": "Enhanced",
        "design_phrase": "Test", "pricing_format": "tiered",
        "cover_image": "cover.png",
        "zones": [
            {"num": 1, "name": "Zone One", "subtitle": "x"},
        ],
    })
    findings = check(proj)
    no_hero = [f for f in findings if f.issue == "no-hero-image"]
    assert len(no_hero) == 1
    assert no_hero[0].zone == "Zone One"
    assert no_hero[0].severity == "warning"


def test_malformed_yaml_reports_error_finding(tmp_path):
    proj = tmp_path / "P"
    brief = proj / "04 - Process & Notes" / "Project Brief.md"
    brief.parent.mkdir(parents=True)
    brief.write_text("---\nclient: [ broken yaml\n---\n")
    findings = check(proj)
    errors = [f for f in findings if f.severity == "error"
                                     and f.issue == "brief-yaml-parse-error"]
    assert len(errors) == 1
