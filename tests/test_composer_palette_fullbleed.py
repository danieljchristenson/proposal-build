"""Tests for the tiered full-bleed palette slide + Scope accent passthrough.

A pre-designed palette/mood board image (Brief `prebuilt_palette_image`) should
render as a chrome-less full-bleed `image_fullbleed` slide in tiered mode,
taking precedence over the generated `material_palette` (Greenery) slide. The
Scope slide's "includes" card accent is driven by Brief `scope_accent`.
"""
from __future__ import annotations

from pathlib import Path
import glob
import shutil

RIVERSIDE = (
    Path(__file__).resolve().parent.parent / "Projects" / "Downtown Riverside Metro Link"
)


def _first_base_scope_png(project_dir: Path) -> str:
    pngs = sorted(glob.glob(str(project_dir / "02 - Renderings" / "Base Scope" / "*.png")))
    assert pngs, "fixture project has no Base Scope PNG to use as a palette image"
    return Path(pngs[0]).name


def _append_frontmatter(project_dir: Path, yaml_block: str) -> None:
    brief = project_dir / "04 - Process & Notes" / "Project Brief.md"
    txt = brief.read_text()
    parts = txt.split("---", 2)
    assert len(parts) >= 3, "Brief missing YAML frontmatter"
    parts[1] = parts[1].rstrip() + "\n" + yaml_block + "\n"
    brief.write_text("---".join(parts))


def test_prebuilt_palette_image_emits_fullbleed_slide(tmp_path):
    """`prebuilt_palette_image:` → an image_fullbleed palette slide after creative_vision."""
    dst = tmp_path / "fake_riverside"
    shutil.copytree(RIVERSIDE, dst)
    palette = _first_base_scope_png(dst)
    _append_frontmatter(dst, f'prebuilt_palette_image: "{palette}"')

    from proposal_build.parser import build_project_model
    from proposal_build.composer import compose

    model, _ = build_project_model(dst)
    slides, _ = compose(model)
    layouts = [s.layout_name for s in slides]

    assert "image_fullbleed" in layouts, f"expected palette full-bleed slide; got {layouts}"
    # It rides directly after creative_vision and replaces the greenery slide.
    assert layouts.index("image_fullbleed") == layouts.index("creative_vision") + 1
    assert "material_palette" not in layouts


def test_no_palette_image_keeps_default_behavior(tmp_path):
    """Without `prebuilt_palette_image:`, no image_fullbleed slide is added."""
    from proposal_build.parser import build_project_model
    from proposal_build.composer import compose

    model, _ = build_project_model(RIVERSIDE)
    slides, _ = compose(model)
    layouts = [s.layout_name for s in slides]
    assert "image_fullbleed" not in layouts


def test_palette_fullbleed_ctx_uses_contain_fit(tmp_path):
    """The palette slide ctx resolves the image and requests contain-fit."""
    dst = tmp_path / "fake_riverside2"
    shutil.copytree(RIVERSIDE, dst)
    palette = _first_base_scope_png(dst)
    _append_frontmatter(dst, f'prebuilt_palette_image: "{palette}"')

    from proposal_build.parser import build_project_model
    from proposal_build.composer.ctx_builders import build_palette_fullbleed_ctx

    model, _ = build_project_model(dst)
    ctx = build_palette_fullbleed_ctx(model, 3, 16)
    assert ctx["fit"] == "contain"
    assert ctx["hero_image"]  # resolved to a path, not empty


def test_scope_accent_passthrough(tmp_path):
    """Brief `scope_accent:` flows to the Scope slide ctx; defaults to green."""
    from proposal_build.parser import build_project_model
    from proposal_build.composer.ctx_builders import build_scope_ctx

    # Default (no scope_accent in Riverside Brief) → green.
    model, _ = build_project_model(RIVERSIDE)
    assert build_scope_ctx(model, 1, 16)["includes_accent"] == "green"

    # Explicit red.
    dst = tmp_path / "fake_riverside3"
    shutil.copytree(RIVERSIDE, dst)
    _append_frontmatter(dst, 'scope_accent: "red"')
    model2, _ = build_project_model(dst)
    assert build_scope_ctx(model2, 1, 16)["includes_accent"] == "red"
