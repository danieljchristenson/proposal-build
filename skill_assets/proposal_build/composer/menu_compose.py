"""Menu-mode compose orchestrator — assembles the slide list for a creative-menu
/ ROM pricing proposal.

Slide sequence (FIGat7th-locked structure for v1):
  1. cover                      (image_fullbleed)
  2. palette                    (image_fullbleed; skipped when no prebuilt_palette_image)
  3. creative_vision
  4..K. section content slides
       - single-item section (or section whose extra items are enhancements
         of the lead item) → 1 zone_solo with section header inlined on lead
       - multi-item section → 2 zone_2up_gallery slides (or 1 if exactly 2 items),
         alternate-banner derived from section.has_alternates
  K+1. rom_investment p1 (sections 1+2+3a)
  K+2. rom_investment p2 (section 3b + totals)
  K+3. sign_off

MenuProjectModel is frozen and does not carry the on-disk project directory.
The menu ctx builders read it from module-level state in
`composer.menu_ctx_builders` via `set_resolved_project_dir`. compose_menu
sets it before building ctxs and clears it after (try/finally).
"""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

from proposal_build.models import MenuProjectModel, SlidePlanItem, Section
from proposal_build.composer.menu_ctx_builders import (
    build_image_fullbleed_ctx,
    build_menu_creative_vision_ctx,
    build_menu_zone_solo_ctx,
    build_menu_zone_2up_gallery_ctx,
    build_menu_rom_investment_ctx,
    build_menu_sign_off_ctx,
)


REPO_ROOT_GUESS = Path(__file__).resolve().parents[3]
PROJECTS_DIR = REPO_ROOT_GUESS / "Projects"


def _find_project_dir_for_model(model: MenuProjectModel) -> Path:
    """Locate the on-disk project directory for a MenuProjectModel by scanning
    Projects/* and matching the Brief's client_company + menu mode."""
    import frontmatter
    if not PROJECTS_DIR.exists():
        raise ValueError(f"Projects directory not found: {PROJECTS_DIR}")
    for entry in sorted(PROJECTS_DIR.iterdir()):
        if not entry.is_dir() or entry.name.startswith("_"):
            continue
        brief = entry / "04 - Process & Notes" / "Project Brief.md"
        if not brief.exists():
            continue
        try:
            fm = frontmatter.load(str(brief)).metadata
        except Exception:
            continue
        if fm.get("client_company") == model.client_company and fm.get("mode") == "menu":
            return entry
    raise ValueError(
        f"Could not locate project directory for client_company={model.client_company!r}"
    )


def compose_menu(
    model: MenuProjectModel, project_dir: Path | None = None
) -> Tuple[list[SlidePlanItem], list]:
    """Returns (slides, []). The empty second tuple slot mirrors the tiered
    compose() signature (which returns itemized_pricing_docs); menu mode
    doesn't emit per-tier itemized PDFs for v1.

    project_dir: optional on-disk project directory used by ctx builders to
    resolve rendering filenames to file:// URIs. If None, walk Projects/* and
    match by client_company + mode.
    """
    from proposal_build.composer.menu_ctx_builders import set_resolved_project_dir

    if project_dir is None:
        project_dir = _find_project_dir_for_model(model)

    set_resolved_project_dir(project_dir)
    try:
        return _build_slides(model)
    finally:
        set_resolved_project_dir(None)


def _build_slides(model: MenuProjectModel) -> Tuple[list[SlidePlanItem], list]:
    """The actual slide assembly. Lifted from the plan's prescribed body."""
    layout_hints: list[tuple[str, dict]] = []

    # 1. Cover
    layout_hints.append(("image_fullbleed", {"kind": "cover"}))

    # 2. Palette (conditional)
    if model.prebuilt_palette_image:
        layout_hints.append(("image_fullbleed", {"kind": "palette"}))

    # 3. Creative Vision
    layout_hints.append(("creative_vision_menu", {}))

    # 4..K. Section content
    for section in model.sections:
        layout_hints.extend(_section_slides(section))

    # Sample of work (conditional)
    if model.sample_work:
        from proposal_build.composer import _load_past_work_entries
        entries = _load_past_work_entries(list(model.sample_work))
        layout_hints.append(("sample_of_work", {"past_work_entries": entries}))

    # Investment p1 + p2
    layout_hints.append(("rom_investment", {"page_part": 1}))
    layout_hints.append(("rom_investment", {"page_part": 2}))

    # Sign-off
    layout_hints.append(("sign_off_menu", {}))

    # Stamp page_num/page_total
    total = len(layout_hints)
    slides: list[SlidePlanItem] = []
    for i, (logical, hint) in enumerate(layout_hints, start=1):
        layout_name, ctx = _build_ctx(model, logical, i, total, hint)
        slides.append(SlidePlanItem(layout_name=layout_name, context=ctx))

    return slides, []


def _is_enhancement_only_section(section: Section) -> bool:
    """True when items[1:] are all enhancements of items[0] (codes like
    '10' + '10-enh'). Such sections render as a single zone_solo with the
    extras folded into bullets."""
    if len(section.items) <= 1:
        return False
    base = section.items[0].code.split("-")[0]
    for it in section.items[1:]:
        if it.code.split("-")[0] != base:
            return False
    return True


def _section_slides(section: Section) -> list[tuple[str, dict]]:
    """Emit one or two slides for a section."""
    if len(section.items) == 1 or _is_enhancement_only_section(section):
        return [("zone_solo_menu", {"section": section})]
    if len(section.items) <= 2:
        return [("zone_2up_gallery_menu", {
            "section": section, "items": tuple(section.items[:2]),
            "is_first_slide_of_section": True,
            "alternate_banner": _alt_banner_for(section),
        })]
    # Multi-item: 2 slides of 2 cells each. For >4 items, extend later; v1 caps at 4.
    return [
        ("zone_2up_gallery_menu", {
            "section": section, "items": tuple(section.items[:2]),
            "is_first_slide_of_section": True,
            "alternate_banner": _alt_banner_for(section),
        }),
        ("zone_2up_gallery_menu", {
            "section": section, "items": tuple(section.items[2:4]),
            "is_first_slide_of_section": False,
            "alternate_banner": _alt_banner_for(section),
        }),
    ]


def _alt_banner_for(section: Section) -> str:
    # Banner intentionally suppressed: per-section "Customer Choice — Pick One"
    # / "All Four Included" framing was confusing — sections are menus of
    # options, not forced picks or forced bundles. Empty string keeps the
    # template's existing `{% if alternate_banner %}` guard inert.
    return ""


def _build_ctx(model: MenuProjectModel, logical: str, page_num: int, page_total: int, hint: dict):
    """Dispatch logical-name → real layout template + ctx."""
    if logical == "image_fullbleed":
        return "image_fullbleed", build_image_fullbleed_ctx(model, page_num, page_total, kind=hint["kind"])
    if logical == "creative_vision_menu":
        return "creative_vision", build_menu_creative_vision_ctx(model, page_num, page_total)
    if logical == "zone_solo_menu":
        return "zone_solo", build_menu_zone_solo_ctx(model, hint["section"], page_num, page_total)
    if logical == "zone_2up_gallery_menu":
        return "zone_2up_gallery", build_menu_zone_2up_gallery_ctx(
            model, hint["section"], hint["items"],
            page_num, page_total,
            is_first_slide_of_section=hint["is_first_slide_of_section"],
            alternate_banner=hint["alternate_banner"],
        )
    if logical == "rom_investment":
        return "rom_investment", build_menu_rom_investment_ctx(
            model, page_num, page_total, page_part=hint["page_part"]
        )
    if logical == "sample_of_work":
        from proposal_build.composer.menu_ctx_builders import build_menu_sample_of_work_ctx
        return "sample_of_work", build_menu_sample_of_work_ctx(
            model, page_num, page_total, hint["past_work_entries"]
        )
    if logical == "sign_off_menu":
        return "sign_off", build_menu_sign_off_ctx(model, page_num, page_total)
    raise ValueError(f"Unknown logical layout: {logical}")
