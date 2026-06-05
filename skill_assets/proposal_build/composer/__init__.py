"""Composer top-level: ProjectModel → list of (layout_name, ctx) tuples + ItemizedPricingDocs."""
from __future__ import annotations

from pathlib import Path

import frontmatter

from proposal_build.composer.ctx_builders import (
    build_cover_ctx, build_exec_summary_ctx, build_understanding_ctx,
    build_creative_vision_ctx, build_material_palette_ctx,
    build_zone_index_ctx, build_zone_solo_ctx,
    build_zone_solo_fullbleed_ctx, build_zone_solo_gallery_ctx,
    build_zone_feature_ctx, build_palette_fullbleed_ctx,
    build_zone_2up_ctx, build_zone_3up_ctx,
    build_scope_ctx, build_a_la_carte_ctx, build_case_study_ctx, build_investment_ctx,
    build_terms_ctx, build_sign_off_ctx, build_about_ctx,
    build_sample_of_work_ctx,
)
from proposal_build.composer.slide_plan import auto_arrange_zones, SlidePlanError
from proposal_build.composer.pricing import build_itemized_pricing_docs
from proposal_build.models import ProjectModel, SlidePlanItem, Tier, MenuProjectModel


CASE_STUDIES_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "case_studies"
PAST_WORK_LIBRARY_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "past_work_library"
TREE_LIBRARY_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "tree_library"


def compose(model) -> tuple[list[SlidePlanItem], list]:
    """Top-level compose dispatcher.

    Routes to the tiered or menu compose path based on the model type.
    Returns (slides, pricing_docs). For menu-mode, pricing_docs is empty
    (no per-tier itemized PDFs).
    """
    if isinstance(model, MenuProjectModel):
        from proposal_build.composer.menu_compose import compose_menu
        return compose_menu(model)
    return _compose_tiered(model)


def _compose_tiered(model: ProjectModel) -> tuple[list[SlidePlanItem], list]:
    """Returns (slides, itemized_pricing_docs).

    slides is an ordered list of SlidePlanItem (layout_name, ctx). itemized_pricing_docs
    is a list of ItemizedPricingDoc (1 or 3 depending on pricing_format).
    """
    pricing_docs = build_itemized_pricing_docs(model)
    tier_totals = {d.tier: d.tier_total for d in pricing_docs}
    if model.pricing_format == "single":
        # Synthesize per-line sums for any tier not emitted as a pricing doc, so
        # the Investment slide's tier-card display still works when only one
        # pricing PDF was emitted. Tiers with zero line items are still skipped.
        for t in [Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE]:
            if t not in tier_totals:
                synthetic = sum(li.line_total for li in model.line_items if t in li.tiers)
                if synthetic > 0:
                    tier_totals[t] = synthetic

    # Headline range spans the active (non-empty) tiers in canonical order.
    _ordered_active = [t for t in (Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE) if t in tier_totals]
    if len(_ordered_active) >= 2:
        investment_range = (f"${tier_totals[_ordered_active[0]]/1000:.0f}K – "
                            f"${tier_totals[_ordered_active[-1]]/1000:.0f}K")
    else:
        investment_range = f"${tier_totals[_ordered_active[0]]/1000:.0f}K"

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
    # Palette slide: a pre-designed full-bleed palette/mood board takes
    # precedence over the generated Greenery Mood Board when present.
    if model.prebuilt_palette_image:
        slides_raw.append(("image_fullbleed", {"kind": "palette"}))
    elif model.greenery_references:
        slides_raw.append(("material_palette", {}))
    slides_raw.extend(zone_block)
    if model.case_study and model.case_study != "skip":
        cs = _load_case_study(model.case_study)
        slides_raw.append(("case_study", {"case_study_data": cs}))
    if model.sample_work:
        entries = _load_past_work_entries(list(model.sample_work))
        slides_raw.append(("sample_of_work", {"past_work_entries": entries}))
    slides_raw.append(("investment", {"tier_totals": tier_totals,
                                       "partnership_discounts": _format_partnership_for_slide(model.partnership_discounts)}))
    slides_raw.append(("scope", {}))
    if model.add_ons:
        slides_raw.append(("a_la_carte", {}))
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
            if layout in ("zone_solo", "zone_solo_fullbleed", "zone_solo_gallery", "zone_feature"):
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
    if layout == "material_palette":
        return build_material_palette_ctx(model, page_num, page_total)
    if layout == "image_fullbleed":
        return build_palette_fullbleed_ctx(model, page_num, page_total)
    if layout == "zone_index":
        return build_zone_index_ctx(model, page_num, page_total)
    if layout == "zone_solo":
        return build_zone_solo_ctx(model, page_num, page_total, hint["zone"])
    if layout == "zone_solo_fullbleed":
        return build_zone_solo_fullbleed_ctx(model, page_num, page_total, hint["zone"])
    if layout == "zone_solo_gallery":
        return build_zone_solo_gallery_ctx(model, page_num, page_total, hint["zone"])
    if layout == "zone_feature":
        return build_zone_feature_ctx(model, page_num, page_total, hint["zone"])
    if layout == "zone_2up":
        return build_zone_2up_ctx(model, page_num, page_total, hint["zones"])
    if layout == "zone_3up":
        return build_zone_3up_ctx(model, page_num, page_total, hint["zones"])
    if layout == "scope":
        return build_scope_ctx(model, page_num, page_total)
    if layout == "a_la_carte":
        return build_a_la_carte_ctx(model, page_num, page_total)
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
    if layout == "sample_of_work":
        return build_sample_of_work_ctx(model, page_num, page_total,
                                         hint["past_work_entries"])
    raise ValueError(f"Unknown layout: {layout}")


def _load_past_work_entries(ids: list[str], library_dir: Path | None = None) -> list[dict]:
    """Resolve a list of past_work_library IDs to display-ready dicts.

    Returns one dict per ID in input order:
        {"id": str, "name": str, "location": str, "year": int, "image": str}

    `image` is an absolute filesystem path to the corresponding .jpg.

    Raises FileNotFoundError if any ID lacks a matching .md file. The
    inspector catches this earlier in practice; the raise here is a
    belt-and-braces guard for unit tests that hit the loader directly.

    `library_dir` lets tests point at tests/fixtures/past_work_library/.
    Production callers omit it and use skill_assets/past_work_library/.
    """
    base = library_dir if library_dir is not None else PAST_WORK_LIBRARY_DIR
    entries: list[dict] = []
    for pid in ids:
        md_path = base / f"{pid}.md"
        if not md_path.exists():
            raise FileNotFoundError(
                f"past_work_library entry not found: {pid} (looked at {md_path})"
            )
        post = frontmatter.load(str(md_path))
        jpg_path = base / f"{pid}.jpg"
        entries.append({
            "id": pid,
            "name": post.metadata["name"],
            "location": post.metadata["location"],
            "year": int(post.metadata["year"]),
            "image": str(jpg_path.resolve()),
        })
    return entries


def _load_tree_entries(ids: list[str], library_dir: Path | None = None) -> list[dict]:
    """Resolve a list of tree_library IDs to display-ready dicts.

    Returns one dict per ID in input order with keys:
        id, letter_code, factory_part_no,
        height_display, height_eyebrow, name, tagline,
        light_count, ornament_count_heavy, ornament_count_light,
        ornaments_per_branch_heavy, branch_count,
        canopy_diameter_display, price_display, bullets, image

    `image` is an absolute filesystem path to {id}.jpg.

    Raises FileNotFoundError if any ID lacks a matching .md file. The
    inspector catches this earlier in normal flow; the raise here is a
    belt-and-braces guard for unit tests that hit the loader directly.

    `library_dir` lets tests point at tests/fixtures/tree_library/.
    Production callers omit it and use skill_assets/tree_library/.
    """
    base = library_dir if library_dir is not None else TREE_LIBRARY_DIR
    entries: list[dict] = []
    for tid in ids:
        md_path = base / f"{tid}.md"
        if not md_path.exists():
            raise FileNotFoundError(
                f"tree_library entry not found: {tid} (looked at {md_path})"
            )
        post = frontmatter.load(str(md_path))
        meta = post.metadata
        jpg_path = base / f"{tid}.jpg"
        entries.append({
            "id": tid,
            "letter_code": meta.get("letter_code", ""),
            "factory_part_no": meta.get("factory_part_no", ""),
            "height_display": meta["height_display"],
            "height_eyebrow": meta["height_eyebrow"],
            "name": meta["name"],
            "tagline": meta["tagline"],
            "light_count": int(meta["light_count"]),
            "ornament_count_heavy": int(meta["ornament_count_heavy"]),
            "ornament_count_light": int(meta["ornament_count_light"]),
            "ornaments_per_branch_heavy": int(meta["ornaments_per_branch_heavy"]),
            "branch_count": int(meta["branch_count"]),
            "canopy_diameter_display": meta["canopy_diameter_display"],
            "price_display": meta["price_display"],
            "bullets": list(meta["bullets"]),
            "image": str(jpg_path.resolve()),
        })
    return entries


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
