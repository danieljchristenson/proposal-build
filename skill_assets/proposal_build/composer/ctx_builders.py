"""One context-dict builder per layout.

Each builder takes ProjectModel + (optional) per-slide hint and returns the
dict that gets passed to Jinja2 as the rendering context. Dict shape MUST
match what tests/fixtures/{pier_39,riverside}.py hand-author — those fixtures
are the gold standard.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from proposal_build.models import ProjectModel, Tier, Zone


# Absolute path to the brand logo, embedded in every page header via base.html.
_LOGO_PATH = (Path(__file__).resolve().parents[3] / "skill_assets" / "Branding" / "ST NICKS LOGO.png").as_posix()


def _project_base(model: ProjectModel) -> dict:
    """Common project-wide values merged into every slide ctx."""
    return {
        "client_company": model.client_company,
        "client_short": model.client_short,
        "project_name": model.project_name,
        "project_short": model.project_short,
        "project_year": model.project_year,
        "project_subtitle": model.project_subtitle,
        "presenter_name": model.presenter_name,
        "presenter_title": model.presenter_title,
        "presenter_org": "St. Nick's Christmas Lighting & Décor",
        "proposal_date": _date_long(model.proposal_date),
        "logo_path": _LOGO_PATH,
    }


def _date_long(iso: str) -> str:
    if not iso:
        return ""
    return datetime.fromisoformat(iso).date().strftime("%B %d, %Y")


def _zone_tier_coverage(model: ProjectModel, zone: Zone) -> str:
    """Tier-coverage label for a zone, e.g. 'ESSENTIAL + ENHANCED' or 'ENHANCED ONLY'.

    Returns an empty string when no priced line items reference this zone (and
    no wildcard rows apply), so the layout can omit the badge. Also suppressed
    entirely when the project is single-tier — there's no tier choice to
    communicate.
    """
    if model.pricing_format == "single":
        return ""
    tiers: set[Tier] = set()
    for li in model.line_items:
        if li.zone == zone.name or li.zone == "*":
            tiers.update(li.tiers)
    if not tiers:
        return ""
    ordered = [t for t in (Tier.ESSENTIAL, Tier.ENHANCED, Tier.SIGNATURE) if t in tiers]
    names = [t.value.upper() for t in ordered]
    if len(names) == 1:
        return f"{names[0]} ONLY"
    return " + ".join(names)


def build_cover_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num,
        "page_total": page_total,
        "season_label": f"{model.project_year} HOLIDAY SEASON",
        "hero_image": model.resolved_renderings.get(model.cover_image, model.cover_image),
        "prepared_by_org": "St. Nick's Christmas Lighting & Décor",
        "client_contact_name": model.client_contact_name,
        "client_contact_title": model.client_contact_title,
        "client_contact_email": model.client_contact_email,
        "client_contact_phone": model.client_contact_phone,
    }


def build_exec_summary_ctx(model: ProjectModel, page_num: int, page_total: int,
                           investment_range: str) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Executive Summary",
        "standfirst": _exec_standfirst(model),
        "body_paragraphs": [_exec_body_para_1(model), _exec_body_para_2(model)],
        "at_a_glance": [r for r in [
            ("PROJECT", f"{model.project_year} {model.proposal_type}", False),
            ("ZONES", _zone_summary_short(model), False),
            # RECOMMENDED TIER row suppressed when single-tier (no tier choice exists)
            None if model.pricing_format == "single"
                else ("RECOMMENDED TIER", model.recommended_tier.value, False),
            ("INVESTMENT", investment_range, False),
            ("GO LIVE", _date_month(model.go_live), False),
            ("SIGNING DEADLINE", _date_short(model.signing_deadline), True),
        ] if r is not None],
        "pillars": list(model.pillars),
    }


def _exec_standfirst(model: ProjectModel) -> str:
    n = len(model.zones)
    if n == 1:
        return f"Our {model.project_year} {model.proposal_type.lower()} for {model.project_name}, at a glance."
    article = "An" if _n_word(n)[0] in "aeiou" else "A"
    return f"{article} {_n_word(n)}-zone {model.proposal_type.lower()} for the {model.project_name}, at a glance."


def _exec_body_para_1(model: ProjectModel) -> str:
    n = len(model.zones)
    return (f"St. Nick's is proposing a coordinated holiday décor program across "
            f"{_n_word(n)} {'zones' if n != 1 else 'zone'} of {model.project_name}, "
            f"a single visual identity that builds on what works in your space.")


def _exec_body_para_2(model: ProjectModel) -> str:
    return ("Our approach builds on operational discipline, repeatable seasonal investment, "
            "and a design language that scales across the program from end to end.")


def _zone_summary_short(model: ProjectModel) -> str:
    if len(model.zones) <= 3:
        return " · ".join(z.name for z in model.zones)
    return f"{_n_word(len(model.zones)).capitalize()} ({model.zones[0].name} → {model.zones[-1].name})"


def _n_word(n: int) -> str:
    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
             6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    return words.get(n, str(n))


def _date_short(iso: str) -> str:
    if not iso:
        return ""
    d = datetime.fromisoformat(iso).date()
    weekday = d.strftime("%a")
    return f"{weekday}, {d.strftime('%b %-d, %Y')}"


def _date_month(iso: str) -> str:
    """Month + year only (e.g., 'November 2026'). Used for go-live where the
    exact day isn't customer-relevant."""
    if not iso:
        return ""
    return datetime.fromisoformat(iso).date().strftime("%B %Y")


def _join_clauses(items) -> str:
    """Join list items into one semicolon-separated line. Brief items are often
    authored as full sentences ending in a period; strip that trailing period
    before joining so we don't render "...season.; Replace..." (period then
    semicolon), then close the whole line with a single period."""
    parts = [s.strip().rstrip(".").strip() for s in items if s and s.strip()]
    return "; ".join(parts) + "." if parts else ""


def build_understanding_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Our Understanding",
        "standfirst": "Playback of discovery, so we're all working from the same page.",
        "panels": [
            {"title": "VENUE & CONTEXT",
             "body": _understanding_venue(model)},
            {"title": "GOALS FOR " + str(model.project_year),
             "body": _join_clauses(model.customer_goals)},
            {"title": "KEY CONSTRAINTS",
             "body": _join_clauses(model.customer_constraints) if model.customer_constraints else "None identified at this stage."},
            {"title": "WHAT SUCCESS LOOKS LIKE",
             "body": _join_clauses(model.success_criteria)},
        ],
    }


def _understanding_venue(model: ProjectModel) -> str:
    if model.venue_context:
        return model.venue_context
    return (f"{model.project_name}: a {len(model.zones)}-zone program "
            f"covering {_zone_summary_short(model)}.")


def build_creative_vision_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Creative Vision",
        "standfirst": f"The design direction for the {model.project_year} {model.project_short} program",
        "design_phrase": model.design_phrase,
        "design_direction_body": model.creative_direction,
        "phases": list(model.phases),
        "hero_image": model.resolved_renderings.get(model.creative_vision_hero, model.creative_vision_hero),
        # Pass through the creative_vision_hero_fit Brief field so AEs can opt
        # in to contain-fit when a hero image gets cropped at the top/bottom
        # (e.g. a 40-foot tree rendering whose top extends past the frame).
        "hero_fit": getattr(model, "creative_vision_hero_fit", "") or "cover",
    }


def build_material_palette_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    """Greenery Mood Board — descriptive copy block + image gallery.
    Default copy describes our build standards; AE can override via Brief
    frontmatter `greenery_description`."""
    default_copy = (
        "Realistic PVC green tips form the base of every wreath, garland, and tree, "
        "with warm-white LED lighting that reads warm against the architecture. "
        "Garlands present cleanly undecorated at the base tier and step up to red, "
        "gold, and green-gold ornament clusters and floral accents at the Signature "
        "tier, a consistent decorating language applied across the property."
    )
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Greenery Mood Board",
        "standfirst": "What the wreaths, garlands, and trees actually look like in real materials.",
        "copy": model.greenery_description or default_copy,
        "items": [{"src": path} for path in model.greenery_references],
    }


def build_zone_index_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "The Program at a Glance",
        "standfirst": f"{_n_word(len(model.zones)).capitalize()} zones, one design language. "
                       f"Here's how the program reads from end to end.",
        "zones": [
            {"num": z.num, "name": z.name, "subtitle": z.subtitle,
             "included_elements": list(z.bullets)}
            for z in model.zones
        ],
    }


def build_zone_solo_ctx(model: ProjectModel, page_num: int, page_total: int, zone: Zone) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "zone_num": zone.num, "zone_name": zone.name, "zone_subtitle": zone.subtitle,
        "tier_coverage": _zone_tier_coverage(model, zone),
        "included_elements": list(zone.bullets),
        "hero_image": model.resolved_renderings.get(zone.hero_image, zone.hero_image),
        "hero_fit": zone.hero_fit,
    }


def build_zone_solo_fullbleed_ctx(model: ProjectModel, page_num: int, page_total: int, zone: Zone) -> dict:
    return build_zone_solo_ctx(model, page_num, page_total, zone)


def build_zone_feature_ctx(model: ProjectModel, page_num: int, page_total: int, zone: Zone) -> dict:
    return build_zone_solo_ctx(model, page_num, page_total, zone)


def build_zone_solo_gallery_ctx(model: ProjectModel, page_num: int, page_total: int, zone: Zone) -> dict:
    """Multi-image variant of zone_solo. Resolves zone.gallery_images to absolute paths."""
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "zone_num": zone.num, "zone_name": zone.name, "zone_subtitle": zone.subtitle,
        "tier_coverage": _zone_tier_coverage(model, zone),
        "included_elements": list(zone.bullets),
        "hero_images": [
            model.resolved_renderings.get(img, img)
            for img in zone.gallery_images
        ],
        "gallery_fit": zone.gallery_fit,
        "gallery_orientation": zone.gallery_orientation,
        "gallery_emphasis": zone.gallery_emphasis,
    }


def build_zone_2up_ctx(model: ProjectModel, page_num: int, page_total: int, zones: list[Zone]) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Program Zones",
        "standfirst": f"Zones {zones[0].num} and {zones[1].num}.",
        "zones": [_zone_dict(model, z) for z in zones],
    }


def build_zone_3up_ctx(model: ProjectModel, page_num: int, page_total: int, zones: list[Zone]) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Program Zones",
        "standfirst": f"Zones {', '.join(z.num for z in zones[:-1])}, and {zones[-1].num}.",
        "zones": [_zone_dict(model, z) for z in zones],
    }


def _zone_dict(model: ProjectModel, z: Zone) -> dict:
    return {
        "num": z.num, "name": z.name, "subtitle": z.subtitle,
        "included_elements": list(z.bullets),
        "hero_image": model.resolved_renderings.get(z.hero_image, z.hero_image),
    }


def build_palette_fullbleed_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    """Chrome-less full-bleed slide for a pre-designed palette / mood board image.
    Uses the image_fullbleed layout. The board arrives already designed as a
    full PNG, so it renders edge-to-edge with no header/footer. Contain-fit
    letterboxes a portrait board cleanly on the dark page rather than cropping."""
    image = model.prebuilt_palette_image
    alt = f"{model.project_name} — Selected Palette"
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": alt,
        "hero_image": model.resolved_renderings.get(image, image),
        "alt_text": alt,
        "fit": "contain",
    }


def build_scope_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    single = model.pricing_format == "single"
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Scope of Work",
        "standfirst": "What your program includes." if single
                      else "What your selected tier includes.",
        "includes": list(model.scope_includes),
        "includes_accent": model.scope_accent,
        "service_note": model.scope_service_note,
        "add_ons": list(model.add_ons),
    }


def build_a_la_carte_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "À La Carte Enhancements",
        "standfirst": "Customize beyond your selected tier with any of the options below.",
        "add_ons": list(model.add_ons),
    }


def build_case_study_ctx(model: ProjectModel, page_num: int, page_total: int,
                         case_study_data: dict) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_eyebrow": "CASE STUDY",
        "page_title": case_study_data["name"],
        "standfirst": case_study_data["standfirst"],
        "challenge": case_study_data["challenge"],
        "approach": case_study_data["approach"],
        "outcome": case_study_data["outcome"],
        "hero_image": model.resolved_renderings.get(model.case_study_hero, model.case_study_hero),
    }


def build_sample_of_work_ctx(model: ProjectModel, page_num: int, page_total: int,
                             past_work_entries: list[dict]) -> dict:
    """Build context for the sample_of_work slide.

    past_work_entries is the resolved output of _load_past_work_entries —
    a list of dicts with id/name/location/year/image keys.

    The template wants `tiles` shaped as {name, location_year, image}, where
    location_year is the pre-formatted "City, ST · YYYY" string the bottom-
    left overlay renders. Building that string here keeps Jinja simple.
    """
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_eyebrow": "Sample of Our Work",
        "page_title": "Recent installations",
        "tiles": [
            {
                "name": e["name"],
                "location_year": f"{e['location']} · {e['year']}",
                "image": e["image"],
            }
            for e in past_work_entries
        ],
    }


def build_investment_ctx(model: ProjectModel, page_num: int, page_total: int,
                         tier_totals: dict, partnership_discounts: list) -> dict:
    th = model.tier_highlights or {}
    _card_specs = [
        (Tier.ESSENTIAL, "ESSENTIAL", "gray", "essential"),
        (Tier.ENHANCED, "ENHANCED", "red", "enhanced"),
        (Tier.SIGNATURE, "SIGNATURE", "navy", "signature"),
    ]
    tiers = [
        _tier_card(name, color, tier_totals[t],
                   model.recommended_tier == t, th.get(key, {}))
        for t, name, color, key in _card_specs if t in tier_totals
    ]
    standfirst_by_count = {
        1: "One program, fully scoped. Pick the add-ons that fit your season.",
        2: "Two levels of program. Pick what fits your season.",
        3: "Three levels of program. Pick what fits your season.",
    }

    # Zone breakdown: aggregate base-scope (non-enhancement) line totals by zone.
    # Used by the zone-itemized investment layout when pricing_format == "single".
    zone_order = []
    zone_totals_map: dict[str, float] = {}
    for li in model.line_items:
        if li.is_enhancement:
            continue
        z = li.zone or "Other"
        if z not in zone_totals_map:
            zone_order.append(z)
            zone_totals_map[z] = 0.0
        zone_totals_map[z] += li.line_total
    zone_breakdown = [{"name": z, "total": zone_totals_map[z]} for z in zone_order]
    grand_total = sum(zone_totals_map.values())

    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Investment",
        "standfirst": standfirst_by_count.get(len(tiers), "Pick the program that fits your season."),
        "tiers": tiers,
        "tier_count": len(tiers),
        "zone_breakdown": zone_breakdown,
        "grand_total": grand_total,
        "partnership_discounts": [],  # disabled — partnership savings removed from all output
        "footer_note": (f"Pricing valid 30 days from proposal date. Fabrication must be locked "
                        f"by {_date_long(model.fabrication_lock)}."),
    }


def _tier_card(name: str, rule_color: str, price: float, is_recommended: bool, highlights_data: dict) -> dict:
    return {
        "name": name,
        "rule_color": rule_color,
        "tagline": highlights_data.get("tagline", ""),
        "highlights": list(highlights_data.get("items", []) or []),
        "price": f"${price:,.0f}",
        "is_recommended": is_recommended,
    }


def build_terms_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    panels = model.term_panels
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Terms & Next Steps",
        "standfirst": f"The critical dates and terms for the {model.project_year} program.",
        "critical_dates": [
            (_date_long(model.signing_deadline), "Execute by this date to guarantee the install schedule."),
            (_date_long(model.fabrication_lock), "All custom fabrication must be approved by this date."),
        ],
        "term_panels": [
            ("PAYMENT SCHEDULE", panels.get("payment_schedule", "")),
            ("INSURANCE & PERMITS", panels.get("insurance_permits", "")),
            ("CHANGE ORDERS", panels.get("change_orders", "")),
            ("PROPOSAL VALIDITY", panels.get("validity", "")),
        ],
        "after_approval_steps": list(model.after_approval_steps),
    }


def build_sign_off_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Let's Make It Happen",
        "standfirst": f"Sign below to launch the {model.project_year} {model.project_short} program.",
        "what_youre_approving": model.what_youre_approving,
        "client_party_label": f"{model.client_short} AUTHORIZATION",
        "stnicks_party_label": "ST. NICK'S AUTHORIZED SIGNATURE",
        "digital_signing_note": ("Prefer to sign digitally? Use the Canva e-signature link in your "
                                  "email. Questions? Reply directly and we'll respond within 24 hours."),
        "client_contact_name": model.client_contact_name,
        "client_contact_title": model.client_contact_title,
        "client_contact_email": model.client_contact_email,
        "client_contact_phone": model.client_contact_phone,
    }


def build_about_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Company Profile",
        "company_facts": list(model.company_facts),
        "team": list(model.team),
    }
