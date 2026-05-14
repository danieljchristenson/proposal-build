"""Render the FIGat7th DTLA itemized pricing PDF (menu-mode ROM).

One-off script — menu mode doesn't auto-emit per-tier itemized PDFs the way
the tiered pipeline does, so this builds a single flat ROM-itemized supplement
to ship alongside the proposal deck.

Usage:
    python scripts/render_figat7th_itemized_pricing.py
"""
from __future__ import annotations

from pathlib import Path

from proposal_build.parser import parse_project
from proposal_build.composer.menu_ctx_builders import build_menu_rom_investment_ctx
from proposal_build.renderer.pdf import render_proposal_pdf


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJ = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"
OUT = PROJ / "03 - Scope & Pricing" / "FIGat7th DTLA - 2026 Itemized Pricing.pdf"
LOGO = REPO_ROOT / "skill_assets" / "Branding" / "ST NICKS LOGO.png"


def _fmt_range(low: int, high: int) -> str:
    if low == high:
        return f"${low:,}"
    return f"${low:,} – ${high:,}"


def _section_note(section_key: str) -> str:
    if section_key == "3a":
        return "customer picks one (alternate group — see deck section 3)"
    return ""


def _item_tag(li, section_key: str) -> str:
    if section_key == "3a":
        return "ALTERNATE"
    if section_key == "2" and li.code == "10-enh":
        return "ENHANCEMENT"
    return ""


def main() -> None:
    model = parse_project(PROJ)

    sections_ctx = []
    for section in model.sections:
        lines_ctx = []
        for li in section.items:
            lines_ctx.append({
                "name": li.name,
                "customer_facing": li.customer_facing or li.description,
                "rental_display": _fmt_range(li.rental_low, li.rental_high),
                "purchase_ot_display": _fmt_range(li.purchase_ot_low, li.purchase_ot_high),
                "purchase_svc_display": _fmt_range(li.purchase_svc_low, li.purchase_svc_high),
                "tag": _item_tag(li, section.key),
            })
        sections_ctx.append({
            "label": section.label,
            "note": _section_note(section.key),
            "lines": lines_ctx,
        })

    rom_ctx = build_menu_rom_investment_ctx(
        model, page_num=1, page_total=1, page_part=2,
    )

    proposal_date = model.proposal_date
    date_long = proposal_date if isinstance(proposal_date, str) else proposal_date.strftime("%B %d, %Y")

    ctx = {
        "logo_path": str(LOGO.resolve()),
        "project_name": model.project_name,
        "project_short": model.project_short,
        "project_year": model.project_year,
        "proposal_type": "Holiday Proposal",
        "proposal_date_long": date_long,
        "client_company": model.client_company,
        "client_contact_name": getattr(model, "client_contact_name", ""),
        "client_contact_title": getattr(model, "client_contact_title", ""),
        "client_contact_email": getattr(model, "client_contact_email", ""),
        "client_contact_phone": getattr(model, "client_contact_phone", ""),
        "sections": sections_ctx,
        "total_rental": rom_ctx["total_rental"],
        "total_purchase_ot": rom_ctx["total_purchase_ot"],
        "total_purchase_svc": rom_ctx["total_purchase_svc"],
        "pricing_caveats": (
            "Section 3a items are mutually exclusive — totals span the lowest- to "
            "highest-priced arch option. ROM ranges are budgetary; final fixed pricing "
            "is set when scope is locked."
        ),
        "page_num": 1,
        "page_total": 1,
    }

    render_proposal_pdf([("itemized_pricing_rom", ctx)], OUT)
    print(f"Rendered: {OUT}")
    print(f"Size: {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
