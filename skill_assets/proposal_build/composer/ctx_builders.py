"""One context-dict builder per layout.

Each builder takes ProjectModel + (optional) per-slide hint and returns the
dict that gets passed to Jinja2 as the rendering context. Dict shape MUST
match what tests/fixtures/{pier_39,riverside}.py hand-author — those fixtures
are the gold standard.
"""
from __future__ import annotations

from datetime import datetime

from proposal_build.models import ProjectModel, Tier, Zone


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
    }


def _date_long(iso: str) -> str:
    if not iso:
        return ""
    return datetime.fromisoformat(iso).date().strftime("%B %d, %Y")


def build_cover_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num,
        "page_total": page_total,
        "season_label": f"{model.project_year} HOLIDAY SEASON",
        "hero_image": model.resolved_renderings.get(model.cover_image, model.cover_image),
        "prepared_by_org": "St. Nick's Christmas Lighting & Décor",
    }


def build_exec_summary_ctx(model: ProjectModel, page_num: int, page_total: int,
                           investment_range: str) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Executive Summary",
        "standfirst": _exec_standfirst(model),
        "body_paragraphs": [_exec_body_para_1(model), _exec_body_para_2(model)],
        "at_a_glance": [
            ("PROJECT", f"{model.project_year} {model.proposal_type}", False),
            ("ZONES", _zone_summary_short(model), False),
            ("RECOMMENDED TIER", model.recommended_tier.value, False),
            ("INVESTMENT RANGE", investment_range, False),
            ("GO LIVE", _date_short(model.go_live), False),
            ("FABRICATION LOCK", _date_short(model.fabrication_lock), True),
            ("SIGNING DEADLINE", _date_short(model.signing_deadline), True),
        ],
        "pillars": list(model.pillars),
    }


def _exec_standfirst(model: ProjectModel) -> str:
    n = len(model.zones)
    if n == 1:
        return f"Our {model.project_year} {model.proposal_type.lower()} for {model.project_name}, at a glance."
    return f"A {_n_word(n)}-zone {model.proposal_type.lower()} for the {model.project_name}, at a glance."


def _exec_body_para_1(model: ProjectModel) -> str:
    n = len(model.zones)
    return (f"St. Nick's is proposing a coordinated holiday décor program across "
            f"{_n_word(n)} {'zones' if n != 1 else 'zone'} of {model.project_name} — "
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


def build_understanding_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Our Understanding",
        "standfirst": "Playback of discovery — so we're all working from the same page.",
        "panels": [
            {"title": "VENUE & CONTEXT",
             "body": _understanding_venue(model)},
            {"title": "GOALS FOR " + str(model.project_year),
             "body": "; ".join(model.customer_goals)},
            {"title": "KEY CONSTRAINTS",
             "body": "; ".join(model.customer_constraints) if model.customer_constraints else "None identified at this stage."},
            {"title": "WHAT SUCCESS LOOKS LIKE",
             "body": "; ".join(model.success_criteria)},
        ],
    }


def _understanding_venue(model: ProjectModel) -> str:
    return (f"{model.project_name} — a {len(model.zones)}-zone program "
            f"covering {_zone_summary_short(model)}.")


def build_creative_vision_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Creative Vision",
        "standfirst": f"The design direction for the {model.project_year} {model.project_short} program.",
        "design_phrase": model.design_phrase,
        "design_direction_body": model.creative_direction,
        "phases": list(model.phases),
        "hero_image": model.resolved_renderings.get(model.creative_vision_hero, model.creative_vision_hero),
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
        "included_elements": list(zone.bullets),
        "hero_image": model.resolved_renderings.get(zone.hero_image, zone.hero_image),
        "hero_fit": zone.hero_fit,
    }


def build_zone_solo_fullbleed_ctx(model: ProjectModel, page_num: int, page_total: int, zone: Zone) -> dict:
    return build_zone_solo_ctx(model, page_num, page_total, zone)


def build_zone_solo_gallery_ctx(model: ProjectModel, page_num: int, page_total: int, zone: Zone) -> dict:
    """Multi-image variant of zone_solo. Resolves zone.gallery_images to absolute paths."""
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "zone_num": zone.num, "zone_name": zone.name, "zone_subtitle": zone.subtitle,
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


def build_scope_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Scope of Work",
        "standfirst": "What your investment includes, and what you can add on.",
        "includes": list(model.scope_includes),
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


def build_investment_ctx(model: ProjectModel, page_num: int, page_total: int,
                         tier_totals: dict, partnership_discounts: list) -> dict:
    tiers = [
        _tier_card("ESSENTIAL", "gray", tier_totals[Tier.ESSENTIAL],
                   model.recommended_tier == Tier.ESSENTIAL),
        _tier_card("ENHANCED", "red", tier_totals[Tier.ENHANCED],
                   model.recommended_tier == Tier.ENHANCED),
        _tier_card("SIGNATURE", "navy", tier_totals[Tier.SIGNATURE],
                   model.recommended_tier == Tier.SIGNATURE),
    ]
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "Investment",
        "standfirst": "Three levels of program. Pick what fits your season.",
        "tiers": tiers,
        "partnership_discounts": partnership_discounts,
        "footer_note": (f"Pricing valid 30 days from proposal date. Fabrication must be locked "
                        f"by {_date_long(model.fabrication_lock)}."),
    }


def _tier_card(name: str, rule_color: str, price: float, is_recommended: bool) -> dict:
    return {
        "name": name, "rule_color": rule_color, "tagline": "",
        "highlights": [],   # populated by ctx_builders if needed; minimal for V1
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
                                  "email. Questions? Reply directly — we'll respond within 24 hours."),
    }


def build_about_ctx(model: ProjectModel, page_num: int, page_total: int) -> dict:
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_title": "About St. Nick's",
        "standfirst": "25 years of large-scale holiday design, installation, and service.",
        "company_facts": list(model.company_facts),
        "team": list(model.team),
        "contact_strip": model.contact_strip,
    }
