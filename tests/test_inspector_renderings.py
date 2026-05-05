"""Tests for the Renderings inspector."""
from __future__ import annotations

from proposal_build.inspector.renderings import check


def _setup_renderings(proj: Path) -> Path:
    rd = proj / "02 - Renderings"
    for sub in ("Base Scope", "Enhancements", "Greenery references", "_inbox"):
        (rd / sub).mkdir(parents=True)
    return rd


def _write_brief(proj: Path, fm: dict) -> None:
    import yaml
    bp = proj / "04 - Process & Notes" / "Project Brief.md"
    bp.parent.mkdir(parents=True, exist_ok=True)
    bp.write_text("---\n" + yaml.safe_dump(fm) + "---\n")


def test_no_renderings_reports_warning(tmp_path):
    proj = tmp_path / "P"
    _setup_renderings(proj)
    findings = check(proj)
    assert any(f.issue == "no-renderings-present" and f.severity == "warning"
               for f in findings)


def test_files_in_inbox_reports_info(tmp_path):
    proj = tmp_path / "P"
    rd = _setup_renderings(proj)
    (rd / "_inbox" / "unsorted.png").write_bytes(b"x")
    findings = check(proj)
    assert any(f.issue == "files-in-inbox" and f.severity == "warning"
               for f in findings)


def test_hero_image_unresolved_reports_blocker(tmp_path):
    proj = tmp_path / "P"
    _setup_renderings(proj)
    _write_brief(proj, {
        "zones": [{"num": 1, "name": "Z1", "hero_image": "missing.png"}]
    })
    findings = check(proj)
    assert any(f.issue == "hero-image-unresolved" and f.severity == "blocker"
               for f in findings)


def test_hero_image_resolved_no_finding(tmp_path):
    proj = tmp_path / "P"
    rd = _setup_renderings(proj)
    (rd / "Base Scope" / "wreath.png").write_bytes(b"x")
    _write_brief(proj, {
        "zones": [{"num": 1, "name": "Z1", "hero_image": "wreath.png"}]
    })
    findings = check(proj)
    assert not any(f.issue == "hero-image-unresolved" for f in findings)


def test_hero_images_plural_unresolved_reports_blocker(tmp_path):
    proj = tmp_path / "P"
    _setup_renderings(proj)
    _write_brief(proj, {
        "zones": [{
            "num": 1, "name": "Z1",
            "hero_images": ["a.png", "b.png"],
        }]
    })
    findings = check(proj)
    unresolved = [f for f in findings if f.issue == "hero-image-unresolved"]
    assert len(unresolved) == 2
