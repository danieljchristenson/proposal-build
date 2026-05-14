"""Tests for composer wiring of the sample_of_work slide (tiered + menu)."""
from __future__ import annotations

from pathlib import Path
import shutil

import pytest


def _patch_brief(project_dir: Path, sample_work_ids: list[str]) -> None:
    """Inject sample_work: into the Brief's YAML frontmatter."""
    brief = project_dir / "04 - Process & Notes" / "Project Brief.md"
    txt = brief.read_text()
    yaml_lines = "sample_work:\n" + "".join(f"  - {pid}\n" for pid in sample_work_ids)
    parts = txt.split("---", 2)
    assert len(parts) >= 3, "Brief missing YAML frontmatter"
    parts[1] = parts[1].rstrip() + "\n" + yaml_lines
    brief.write_text("---".join(parts))


def _swap_library_to_fixture(monkeypatch):
    """Point composer at tests/fixtures/past_work_library/ for the run."""
    fixture_lib = (
        Path(__file__).resolve().parent / "fixtures" / "past_work_library"
    )
    from proposal_build import composer
    monkeypatch.setattr(composer, "PAST_WORK_LIBRARY_DIR", fixture_lib)


def test_tiered_composer_emits_sample_of_work_when_sample_work_present(
    tmp_path, monkeypatch,
):
    """sample_work: in Brief → composer emits sample_of_work between case_study and investment."""
    src = (
        Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    dst = tmp_path / "fake_riverside"
    shutil.copytree(src, dst)
    _patch_brief(dst, ["fixture_a", "fixture_b", "fixture_c",
                       "fixture_d", "fixture_e", "fixture_f"])
    _swap_library_to_fixture(monkeypatch)

    from proposal_build.parser import build_project_model
    from proposal_build.composer import compose

    model, _ = build_project_model(dst)
    slides, _ = compose(model)
    layouts = [s.layout_name for s in slides]

    assert "sample_of_work" in layouts, (
        f"Expected sample_of_work in slide deck; got: {layouts}"
    )
    # Placement: after case_study (when present), before investment.
    sow_idx = layouts.index("sample_of_work")
    inv_idx = layouts.index("investment")
    assert sow_idx < inv_idx, "sample_of_work must come before investment"
    if "case_study" in layouts:
        cs_idx = layouts.index("case_study")
        assert cs_idx < sow_idx, "sample_of_work must come after case_study"


def test_tiered_composer_skips_sample_of_work_when_sample_work_empty(tmp_path):
    """No sample_work: in Brief → no sample_of_work slide in deck."""
    project_dir = (
        Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    from proposal_build.parser import build_project_model
    from proposal_build.composer import compose

    model, _ = build_project_model(project_dir)
    slides, _ = compose(model)
    layouts = [s.layout_name for s in slides]
    assert "sample_of_work" not in layouts


def test_menu_composer_emits_sample_of_work_when_sample_work_present(
    tmp_path, monkeypatch,
):
    """sample_work: in a menu Brief → menu composer emits sample_of_work."""
    src = (
        Path(__file__).resolve().parent.parent
        / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"
    )
    dst = tmp_path / "fake_figat7th"
    shutil.copytree(src, dst)
    _patch_brief(dst, ["fixture_a", "fixture_b", "fixture_c",
                       "fixture_d", "fixture_e", "fixture_f"])
    _swap_library_to_fixture(monkeypatch)

    from proposal_build.parser import parse_project
    from proposal_build.composer import compose

    model = parse_project(dst)
    slides, _ = compose(model)
    layouts = [s.layout_name for s in slides]

    assert "sample_of_work" in layouts, (
        f"Expected sample_of_work in menu deck; got: {layouts}"
    )


def test_menu_composer_skips_sample_of_work_when_sample_work_empty():
    """A FIGat7th Brief without sample_work → no sample_of_work slide."""
    project_dir = (
        Path(__file__).resolve().parent.parent
        / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"
    )
    from proposal_build.parser import parse_project
    from proposal_build.composer import compose

    model = parse_project(project_dir)
    slides, _ = compose(model)
    layouts = [s.layout_name for s in slides]
    assert "sample_of_work" not in layouts
