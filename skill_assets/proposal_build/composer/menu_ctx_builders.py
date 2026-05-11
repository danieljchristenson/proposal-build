"""Ctx builders for menu-mode (creative-menu / ROM) layouts.

Each builder takes the MenuProjectModel + page coordinates + any needed
section/items, and returns a dict ready for renderer/pdf.py.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from proposal_build.models import MenuProjectModel, ROMLineItem, Section


# Word-form section labels for the deck header strip ("Section One", "Section Two", ...).
_SECTION_WORDS = {
    "1": "Section One",
    "2": "Section Two",
    "3": "Section Three",
    "3a": "Section Three",
    "3b": "Section Three",
}


# MenuProjectModel is frozen; the project dir for image URI resolution is
# communicated via module-level state set by composer.menu_compose before
# building ctxs and reset afterward.
_RESOLVED_PROJECT_DIR: Path | None = None


def set_resolved_project_dir(p: Path | None) -> None:
    """Set the active project directory used to resolve rendering filenames
    into absolute file URIs. Called by menu_compose.compose_menu before
    building ctxs; pass None to reset when compose completes.

    NOT thread-safe: this is a module-level global. Concurrent compose_menu
    calls would clobber each other's state mid-build, silently producing
    relative file URIs. Serialise compose calls if a multi-threaded caller
    is ever introduced (or refactor to thread project_dir through every
    builder signature)."""
    global _RESOLVED_PROJECT_DIR
    _RESOLVED_PROJECT_DIR = p


def _project_dir_from_model(model: MenuProjectModel) -> Path:
    return _RESOLVED_PROJECT_DIR or Path(".")


def _resolve_image_uri(model: MenuProjectModel, filename: str) -> str:
    if not filename:
        return ""
    project_dir = _project_dir_from_model(model)
    return (project_dir / "02 - Renderings" / "Base Scope" / filename).as_uri()


def _project_dict(model: MenuProjectModel) -> dict:
    """The shared project block every slide includes (matches the base.html footer needs)."""
    return {
        "client_company": model.client_company,
        "client_short": model.client_short,
        "project_name": model.project_name,
        "project_short": model.project_short,
        "project_year": model.project_year,
        "project_subtitle": model.project_subtitle,
        "presenter_name": model.presenter_name,
        "presenter_title": model.presenter_title,
        "presenter_org": model.presenter_org,
        "proposal_date": model.proposal_date,
    }


def build_image_fullbleed_ctx(
    model: MenuProjectModel, page_num: int, page_total: int, *, kind: str
) -> dict:
    """kind: 'cover' or 'palette'. Picks the right pre-built image."""
    if kind == "cover":
        image = model.prebuilt_cover_image
        alt = f"{model.project_name} — Cover"
    elif kind == "palette":
        image = model.prebuilt_palette_image
        alt = f"{model.project_name} — Selected Ornament Palette"
    else:
        raise ValueError(f"image_fullbleed kind must be 'cover' or 'palette', got {kind!r}")
    return {
        **_project_dict(model),
        "page_num": page_num,
        "page_total": page_total,
        "page_title": alt,
        "hero_image": _resolve_image_uri(model, image),
        "alt_text": alt,
    }


def build_menu_creative_vision_ctx(
    model: MenuProjectModel, page_num: int, page_total: int
) -> dict:
    return {
        **_project_dict(model),
        "page_num": page_num,
        "page_total": page_total,
        "page_title": "Creative Vision",
        "standfirst": f"The design direction for {model.client_short}'s {model.project_year} holiday program.",
        "design_phrase": model.design_phrase + ".",
        "design_direction_body": model.creative_direction,
        "phases": list(model.creative_phases),
        "hero_image": _resolve_image_uri(model, model.creative_vision_hero),
        "hero_fit": "contain",
    }


def build_menu_zone_solo_ctx(
    model: MenuProjectModel, section: Section, page_num: int, page_total: int
) -> dict:
    """Single-item section (canopy, tree). Inlines section header on the slide."""
    item = section.items[0]
    bullets = _bullets_for_item(item, extras=(section.items[1:] if len(section.items) > 1 else ()))
    return {
        **_project_dict(model),
        "page_num": page_num,
        "page_total": page_total,
        "section_label": _SECTION_WORDS.get(section.key, section.label),
        "section_name": section.name,
        "zone_num": _two_digit_code(item.code),
        "zone_name": item.name,
        "zone_subtitle": item.customer_facing,
        "included_elements": bullets,
        "hero_image": _resolve_image_uri(model, item.rendering_ref),
        "hero_fit": "contain",
    }


def _bullets_for_item(item: ROMLineItem, *, extras: Iterable[ROMLineItem] = ()) -> list[str]:
    """Build the bullet list for a zone_solo cell from materials + extras' names."""
    bullets = []
    if item.materials:
        # Split materials field at semicolons; one bullet per clause.
        bullets.extend(b.strip() for b in item.materials.split(";") if b.strip())
    for x in extras:
        bullets.append(x.customer_facing or x.name)
    return bullets


def _two_digit_code(code: str) -> str:
    """Drop suffixes like '-enh' so the eyebrow reads ZONE 01 / ZONE 10.
    3-digit codes (ZONE 100+) pass through with their natural width."""
    base = code.split("-")[0]
    if base.isdigit():
        return base.zfill(2)
    return code


def build_menu_zone_2up_gallery_ctx(
    model: MenuProjectModel, section: Section,
    items: tuple[ROMLineItem, ROMLineItem],
    page_num: int, page_total: int,
    *, is_first_slide_of_section: bool, alternate_banner: str = "",
) -> dict:
    """Two-cell image gallery. First slide of section carries section header."""
    eyebrow_offsets = {0: "OPTION A", 1: "OPTION B"} if is_first_slide_of_section \
                      else {0: "OPTION C", 1: "OPTION D"}
    # Standalone sections don't use OPTION letters; they use MOMENT NN counted from 01.
    # The caller signals this via the alternate_banner: "All ... Included" → MOMENT.
    use_moment_labels = "All" in alternate_banner and "Included" in alternate_banner
    if use_moment_labels:
        base = 1 if is_first_slide_of_section else 3
        eyebrow_offsets = {
            0: f"MOMENT {str(base).zfill(2)}",
            1: f"MOMENT {str(base + 1).zfill(2)}",
        }

    cells = []
    for i, item in enumerate(items):
        cells.append({
            "eyebrow": eyebrow_offsets[i],
            "name": item.name,
            "hero_image": _resolve_image_uri(model, item.rendering_ref),
        })

    ctx = {
        **_project_dict(model),
        "page_num": page_num,
        "page_total": page_total,
        "page_title": ("Plaza Arches" if section.has_alternates else "Plaza Moments")
                      + ("" if is_first_slide_of_section else " (continued)"),
        "standfirst": _gallery_standfirst(section, is_first_slide_of_section),
        "alternate_banner": alternate_banner,
        "cells": cells,
    }
    if is_first_slide_of_section and section.is_lead:
        ctx["section_label"] = _SECTION_WORDS.get(section.key, section.label)
        ctx["section_name"] = section.name
    return ctx


def _gallery_standfirst(section: Section, is_first: bool) -> str:
    if section.has_alternates:
        return ("Four walk-through arch directions. Each can stand alone as the moment. "
                "Options A and B follow; Options C and D on the next page.") if is_first else \
               "Options C and D — the final two arch directions for customer choice."
    return ("Four standalone photo-ops scattered through the plaza. "
            "Moments 01 and 02 below; Moments 03 and 04 on the next page.") if is_first else \
           "Moments 03 and 04 round out the standalone plaza photo-op program."


def build_menu_rom_investment_ctx(
    model: MenuProjectModel, page_num: int, page_total: int, *, page_part: int
) -> dict:
    """page_part: 1 = sections 1+2+3a (no totals/footnote); 2 = section 3b + totals + footnote."""
    from proposal_build.composer.rom_pricing import compute_rom_totals, format_money_range

    if page_part == 1:
        sections_data = _investment_sections(model, keys=("1", "2", "3a"))
        return {
            **_project_dict(model),
            "page_num": page_num,
            "page_total": page_total,
            "page_title": "Investment",
            "standfirst": "Rough order of magnitude pricing — Sections 1, 2, and 3a (continued on next page).",
            "sections": sections_data,
            "show_totals": False,
            "total_rental": "",
            "total_purchase_ot": "",
            "total_purchase_svc": "",
            "footnote": "",
        }

    # page_part == 2
    totals = compute_rom_totals(model.sections)
    sections_data = _investment_sections(model, keys=("3b",))
    return {
        **_project_dict(model),
        "page_num": page_num,
        "page_total": page_total,
        "page_title": "Investment (continued)",
        "standfirst": "Section 3b plus program total. Customer can mix and match rental and purchase per item.",
        "sections": sections_data,
        "show_totals": True,
        "total_rental": format_money_range(totals["rental_low"], totals["rental_high"]),
        "total_purchase_ot": format_money_range(totals["purchase_ot_low"], totals["purchase_ot_high"]),
        "total_purchase_svc": format_money_range(totals["purchase_svc_low"], totals["purchase_svc_high"]),
        "footnote": _rom_footnote(),
    }


def _investment_sections(model: MenuProjectModel, *, keys) -> list[dict]:
    from proposal_build.composer.rom_pricing import format_money_range
    out = []
    for section in model.sections:
        if section.key not in keys:
            continue
        rows = []
        for it in section.items:
            rows.append({
                "name": it.name,
                "description": "",
                "is_alternate": it.is_alternate,
                "rental_price": format_money_range(it.rental_low, it.rental_high),
                "purchase_ot_price": format_money_range(it.purchase_ot_low, it.purchase_ot_high),
                "purchase_svc_price": format_money_range(it.purchase_svc_low, it.purchase_svc_high),
            })
        out.append({"label": section.label, "rows": rows})
    return out


def _rom_footnote() -> str:
    return (
        "<strong>Rental</strong> is an annual all-inclusive fee covering item, install, removal, and storage. "
        "<strong>Purchase</strong> is a one-time price plus a separate annual service fee for install, removal, and storage. "
        "Plaza arches are mutually exclusive — Program ROM Total is bookended by the cheapest-pick (low) and "
        "most-expensive-pick (high) configurations. All figures are rough order of magnitude for first-pass scoping; "
        "final numbers will follow site walk and scope refinement."
    )


def build_menu_sign_off_ctx(
    model: MenuProjectModel, page_num: int, page_total: int
) -> dict:
    return {
        **_project_dict(model),
        "page_num": page_num,
        "page_total": page_total,
        "page_title": "Let's Make It Happen",
        "standfirst": f"Next steps to lock the {model.client_short} {model.project_year} program.",
        "what_youre_approving": model.what_youre_approving,
        "client_party_label": f"{model.client_short} — {model.client_contact_title.split(',')[-1].strip() if ',' in model.client_contact_title else 'Client'}",
        "client_contact_name": model.client_contact_name,
        "client_contact_title": model.client_contact_title,
        "client_contact_email": model.client_contact_email,
        "client_contact_phone": model.client_contact_phone,
        "stnicks_party_label": "St. Nick's Christmas Lighting & Décor",
        "digital_signing_note": "This proposal may be approved digitally — a countersigned PDF is sufficient to proceed.",
    }
