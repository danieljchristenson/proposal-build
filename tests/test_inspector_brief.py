"""Tests for the Brief inspector."""
from __future__ import annotations

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


def test_missing_required_section_reports_blocker(tmp_path):
    """Brief missing required prose sections should emit one blocker per missing section."""
    from proposal_build.inspector.brief import (
        REQUIRED_BULLET_SECTIONS, REQUIRED_PROSE_SECTIONS,
    )
    proj = tmp_path / "P"
    brief = proj / "04 - Process & Notes" / "Project Brief.md"
    _write_brief(brief, frontmatter={
        "client_company": "X", "project_name": "Y", "project_year": 2026,
        "presenter_name": "P", "voice": "civic", "recommended_tier": "Enhanced",
        "pricing_format": "tiered", "cover_image": "cover.png",
        "zones": [{"num": 1, "name": "Z1", "hero_image": "img.png"}],
    })  # body intentionally empty — no section headers
    findings = check(proj)
    blockers = [f for f in findings if f.issue == "missing-section"]
    expected = len(REQUIRED_BULLET_SECTIONS) + len(REQUIRED_PROSE_SECTIONS)
    assert len(blockers) == expected


def test_inspector_flags_sample_work_with_wrong_count(tmp_path):
    """sample_work: with 5 IDs → sample_work_wrong_count blocker."""
    import shutil
    from proposal_build.inspector.brief import check
    src = (
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    dst = tmp_path / "fake_project"
    shutil.copytree(src, dst)
    brief = dst / "04 - Process & Notes" / "Project Brief.md"
    txt = brief.read_text()
    parts = txt.split("---", 2)
    parts[1] = parts[1].rstrip() + "\nsample_work:\n  - fixture_a\n  - fixture_b\n  - fixture_c\n  - fixture_d\n  - fixture_e\n"
    brief.write_text("---".join(parts))

    findings = check(dst)
    issues = {f.issue for f in findings}
    assert "sample_work_wrong_count" in issues, (
        f"Expected sample_work_wrong_count; got {issues}"
    )


def test_inspector_accepts_sample_work_absent():
    """No sample_work: → no sample_work_* findings (slide just gets skipped)."""
    from proposal_build.inspector.brief import check
    project_dir = (
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    findings = check(project_dir)
    sw_issues = {f.issue for f in findings if f.issue.startswith("sample_work_")}
    assert sw_issues == set()


def test_inspector_flags_sample_work_unknown_id(tmp_path, monkeypatch):
    """sample_work: with an ID not in the library → sample_work_unknown_id."""
    import shutil
    from pathlib import Path
    from proposal_build.inspector import brief as inspector_brief
    from proposal_build.inspector.brief import check

    # Point inspector at the test fixture library
    fixture_lib = Path(__file__).resolve().parent / "fixtures" / "past_work_library"
    monkeypatch.setattr(inspector_brief, "PAST_WORK_LIBRARY_DIR", fixture_lib)

    src = (
        Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    dst = tmp_path / "fake_project"
    shutil.copytree(src, dst)
    brief = dst / "04 - Process & Notes" / "Project Brief.md"
    txt = brief.read_text()
    parts = txt.split("---", 2)
    # 6 IDs, but 'not_in_library' doesn't exist
    parts[1] = parts[1].rstrip() + (
        "\nsample_work:\n  - fixture_a\n  - fixture_b\n  - fixture_c\n"
        "  - fixture_d\n  - fixture_e\n  - not_in_library\n"
    )
    brief.write_text("---".join(parts))

    findings = check(dst)
    issues = [f.issue for f in findings]
    assert "sample_work_unknown_id" in issues
    # And no wrong-count (we have exactly 6)
    assert "sample_work_wrong_count" not in issues
