"""Composer top-level: ProjectModel → list of (layout_name, ctx) tuples + ItemizedPricingDocs."""
from __future__ import annotations

from pathlib import Path

import frontmatter

from proposal_build.composer.ctx_builders import (
    build_cover_ctx, build_exec_summary_ctx, build_understanding_ctx,
    build_creative_vision_ctx, build_zone_index_ctx, build_zone_solo_ctx,
    build_zone_solo_fullbleed_ctx, build_zone_solo_gallery_ctx,
    build_zone_2up_ctx, build_zone_3up_ctx,
    build_scope_ctx, build_case_study_ctx, build_investment_ctx,
    build_terms_ctx, build_sign_off_ctx, build_about_ctx,
)
from proposal_build.composer.slide_plan import auto_arrange_zones, SlidePlanError
from proposal_build.composer.pricing import build_itemized_pricing_docs
from proposal_build.models import ProjectModel, SlidePlanItem, Tier


CASE_STUDIES_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "case_studies"


def compose(model: ProjectModel) -> tuple[list[SlidePlanItem], list]:
    """Returns (slides, itemized_pricing_docs).

    slides is an ordered list of SlidePlanItem (layout_name, ctx). itemized_pricing_docs
    is a list of ItemizedPricingDoc (1 or 3 depending on pricing_format).
    """
    pricing_docs = build_itemized_pricing_docs(model)
    tier_totals = {d.tier: d.tier_total for d in pricing_docs}
    if model.pricing_format == "single":
        # Synthesize the absent tier totals from per-line sums so the Investment
        # slide's 3-tier display still works when only one pricing PDF was emitted.
        for t in [Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE]:
            if t not in tier_totals:
                tier_totals[t] = sum(li.line_total for li in model.line_items if t in li.tiers)

    investment_range = f"${tier_totals[Tier.ESSENTIAL]/1000:.0f}K — ${tier_totals[Tier.SIGNATURE]/1000:.0f}K"

    # Note: per-tier partnership savings rows (4%/6%/9% applied to tier total) are
    # rendered on page 2 of each Itemized Pricing supplement, not on the Investment
    # slide. That computation lives in renderer/pricing_pdf.py — not duplicated here.

    # Build the zone-block slide list
    zone_block = _resolve_zone_block(model)

    slides_raw: list[tuple[str, dict]] = []
    slides_raw.append(("cover", {}))
    slides_raw.append(("exec_summary", {"investment_range": investment_range}))
    slides_raw.append(("understanding", {}))
    slides_raw.append(("creative_vision", {}))
    slides_raw.extend(zone_block)
    slides_raw.append(("scope", {}))
    if model.case_study and model.case_study != "skip":
        cs = _load_case_study(model.case_study)
        slides_raw.append(("case_study", {"case_study_data": cs}))
    slides_raw.append(("investment", {"tier_totals": tier_totals,
                                       "partnership_discounts": _format_partnership_for_slide(model.partnership_discounts)}))
    slides_raw.append(("terms", {}))
    slides_raw.append(("sign_off", {}))
    slides_raw.append(("about", {}))

    page_total = len(slides_raw)
    slides = []
    for i, (layout, hint) in enumerate(slides_raw, start=1):
        ctx = _build_ctx(model, layout, i, page_total, hint)
        slides.append(SlidePlanItem(layout_name=layout, context=ctx))

    return slides, pricing_docs


def _resolve_zone_block(model: ProjectModel) -> list[tuple[str, dict]]:
    """Apply slide_plan_override if present, else auto-arrange."""
    if model.slide_plan_override:
        # Build slides from the override list. Each entry: {layout: ..., zones: [name, ...]}
        zone_by_name = {z.name: z for z in model.zones}
        result = []
        for entry in model.slide_plan_override:
            layout = entry["layout"]
            zone_names = entry["zones"]
            if layout in ("zone_solo", "zone_solo_fullbleed", "zone_solo_gallery"):
                if len(zone_names) != 1:
                    raise SlidePlanError(f"{layout} requires exactly 1 zone, got {len(zone_names)}")
                result.append((layout, {"zone": zone_by_name[zone_names[0]]}))
            elif layout == "zone_index":
                result.append((layout, {"zones": [zone_by_name[n] for n in zone_names]}))
            else:
                expected = int(layout.split("_")[1].rstrip("up"))
                if len(zone_names) != expected:
                    raise SlidePlanError(f"{layout} requires exactly {expected} zones")
                result.append((layout, {"zones": [zone_by_name[n] for n in zone_names]}))
        return result
    return auto_arrange_zones(list(model.zones))


def _build_ctx(model: ProjectModel, layout: str, page_num: int, page_total: int, hint: dict) -> dict:
    """Dispatch to the appropriate ctx_builder."""
    if layout == "cover":
        return build_cover_ctx(model, page_num, page_total)
    if layout == "exec_summary":
        return build_exec_summary_ctx(model, page_num, page_total, hint["investment_range"])
    if layout == "understanding":
        return build_understanding_ctx(model, page_num, page_total)
    if layout == "creative_vision":
        return build_creative_vision_ctx(model, page_num, page_total)
    if layout == "zone_index":
        return build_zone_index_ctx(model, page_num, page_total)
    if layout == "zone_solo":
        return build_zone_solo_ctx(model, page_num, page_total, hint["zone"])
    if layout == "zone_solo_fullbleed":
        return build_zone_solo_fullbleed_ctx(model, page_num, page_total, hint["zone"])
    if layout == "zone_solo_gallery":
        return build_zone_solo_gallery_ctx(model, page_num, page_total, hint["zone"])
    if layout == "zone_2up":
        return build_zone_2up_ctx(model, page_num, page_total, hint["zones"])
    if layout == "zone_3up":
        return build_zone_3up_ctx(model, page_num, page_total, hint["zones"])
    if layout == "scope":
        return build_scope_ctx(model, page_num, page_total)
    if layout == "case_study":
        return build_case_study_ctx(model, page_num, page_total, hint["case_study_data"])
    if layout == "investment":
        return build_investment_ctx(model, page_num, page_total,
                                     hint["tier_totals"], hint["partnership_discounts"])
    if layout == "terms":
        return build_terms_ctx(model, page_num, page_total)
    if layout == "sign_off":
        return build_sign_off_ctx(model, page_num, page_total)
    if layout == "about":
        return build_about_ctx(model, page_num, page_total)
    raise ValueError(f"Unknown layout: {layout}")


def _load_case_study(case_id: str) -> dict:
    path = CASE_STUDIES_DIR / f"{case_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"Case study not found: {case_id} (looked at {path})")
    post = frontmatter.load(str(path))
    sections = _split_md_sections(post.content)
    return {
        "name": post.metadata["name"],
        "year": post.metadata["year"],
        "voice_tag": post.metadata.get("voice_tag", ""),
        "standfirst": post.metadata["standfirst"],
        "challenge": sections.get("Challenge", ""),
        "approach": sections.get("Approach", ""),
        "outcome": sections.get("Outcome", ""),
    }


def _split_md_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = None
    lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(lines).strip()
            current = line[3:].strip()
            lines = []
        elif current is not None:
            lines.append(line)
    if current is not None:
        sections[current] = "\n".join(lines).strip()
    return sections


def _load_discount_pcts() -> dict[str, float]:
    """Load percentages from the partnership_discounts boilerplate."""
    bp_path = Path(__file__).resolve().parents[3] / "skill_assets" / "boilerplate" / "partnership_discounts.md"
    bp = frontmatter.load(str(bp_path)).metadata
    return {d["term"]: d["discount"] for d in bp["discounts"]}


def _format_partnership_for_slide(discounts: tuple) -> list:
    """Pass-through. Slide expects (term, label) tuples — e.g. ('2-YEAR', '4% OFF')
    — which is exactly the shape parser/__init__.py builds in model.partnership_discounts."""
    return list(discounts)
