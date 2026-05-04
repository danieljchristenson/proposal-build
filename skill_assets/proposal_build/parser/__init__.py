"""Top-level Parser orchestrator: build_project_model(project_dir) → ProjectModel.

Composes brief + worksheet + renderings + voice + boilerplate into a fully-
resolved ProjectModel. Blocking errors raise; warnings are returned alongside.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from proposal_build.models import ProjectModel, Zone, Tier
from proposal_build.parser.brief import parse_brief, BriefParseError
from proposal_build.parser.worksheet import parse_worksheet, WorksheetParseError
from proposal_build.parser.renderings import (
    walk_renderings, list_all_renderings, resolve_filename, RenderingsResolutionError,
)
from proposal_build.parser.voice import load_voice, VoiceLoadError
from proposal_build.parser.boilerplate import load_boilerplate, substitute_placeholders


class ProjectLoadError(Exception):
    """Top-level error during project loading. Contains a descriptive message."""


def build_project_model(project_dir: Path) -> tuple[ProjectModel, dict]:
    """Returns (model, parse_artifacts) where parse_artifacts has eligible_renderings, scenarios, etc.

    Raises ProjectLoadError on any blocking issue.
    """
    project_dir = Path(project_dir)

    # 1. Brief
    brief_path = project_dir / "04 - Process & Notes" / "Project Brief.md"
    try:
        brief = parse_brief(brief_path)
    except BriefParseError as e:
        raise ProjectLoadError(f"Brief: {e}") from e

    # 2. Worksheet
    fm = brief.frontmatter
    worksheet_name = f"{fm['project_name']} - Scope Worksheet.xlsx"
    worksheet_path = project_dir / "03 - Scope & Pricing" / worksheet_name
    try:
        ws = parse_worksheet(worksheet_path)
    except WorksheetParseError as e:
        raise ProjectLoadError(f"Worksheet: {e}") from e

    # 3. Renderings
    try:
        eligible = walk_renderings(project_dir)
    except RenderingsResolutionError as e:
        raise ProjectLoadError(f"Renderings: {e}") from e
    all_renderings = list_all_renderings(project_dir)

    # 4. Verify all image references resolve
    referenced_filenames = []
    image_fields = ["cover_image", "creative_vision_hero", "case_study_hero"]
    for f in image_fields:
        name = fm.get(f, "")
        if name:
            try:
                resolve_filename(name, eligible)
                referenced_filenames.append(name)
            except RenderingsResolutionError as e:
                raise ProjectLoadError(f"{f}: {e}") from e
    for z in fm["zones"]:
        name = z.get("hero_image", "")
        if name:
            try:
                resolve_filename(name, eligible)
                referenced_filenames.append(name)
            except RenderingsResolutionError as e:
                raise ProjectLoadError(f"zone {z['name']!r} hero_image: {e}") from e

    # 5. Auto-derive blank dates
    go_live = fm["go_live"]
    fab_lock = fm.get("fabrication_lock") or _date_offset(go_live, days=-90)
    sign = fm.get("signing_deadline") or _date_offset(go_live, days=-21)

    # 6. Load voice + boilerplate
    try:
        voice = load_voice(fm["voice"])
    except VoiceLoadError as e:
        raise ProjectLoadError(str(e)) from e
    bp = load_boilerplate()

    # 7. Build placeholder values for substitution
    placeholders = _build_placeholders(fm, fab_lock, sign, brief)

    # 8. Resolve voice/boilerplate fills (Brief overrides win)
    pillars = _fill_pillars(brief, voice, placeholders)
    phases = _fill_phases(brief, voice, placeholders)
    scope_includes = _fill_scope_includes(brief, bp, placeholders)
    add_ons = _fill_add_ons(brief, placeholders)
    term_panels = _fill_term_panels(brief, bp, placeholders)
    after_steps = _fill_after_approval_steps(brief, voice, placeholders)
    company_facts = _fill_company_facts(brief, bp, placeholders)
    team = _fill_team(brief, bp, placeholders)
    contact_strip = substitute_placeholders(bp.contact_strip, placeholders)
    partnership_discounts = tuple((d["term"], d["label"]) for d in bp.partnership_discounts)

    # 9. Build Zones tuple
    zones = tuple(
        Zone(
            num=z["num"], name=z["name"], subtitle=z.get("subtitle", ""),
            flags=tuple(z.get("flags") or ()),
            hero_image=z.get("hero_image", ""),
            bullets=tuple(z.get("bullets") or ()),
            layout_override=z.get("layout"),
        )
        for z in fm["zones"]
    )

    model = ProjectModel(
        client_company=fm["client_company"], client_short=fm.get("client_short", ""),
        project_name=fm["project_name"], project_short=fm.get("project_short", ""),
        project_year=int(fm["project_year"]),
        project_subtitle=fm.get("project_subtitle", ""),
        proposal_type=fm.get("proposal_type", "Holiday Proposal"),
        presenter_name=fm["presenter_name"], presenter_title=fm.get("presenter_title", ""),
        presenter_email=fm.get("presenter_email", ""), presenter_phone=fm.get("presenter_phone", ""),
        proposal_date=fm.get("proposal_date", ""),
        go_live=go_live, season_end=fm.get("season_end", ""),
        fabrication_lock=fab_lock, signing_deadline=sign,
        voice=fm["voice"], recommended_tier=Tier.from_string(fm["recommended_tier"]),
        design_phrase=fm.get("design_phrase", ""), pricing_format=fm["pricing_format"],
        cover_image=fm["cover_image"], creative_vision_hero=fm.get("creative_vision_hero", ""),
        case_study=fm.get("case_study", "skip"), case_study_hero=fm.get("case_study_hero", ""),
        zones=zones, line_items=ws.line_items,
        creative_direction=brief.sections.get("Creative Direction", ""),
        customer_goals=tuple(brief.sections.get("Customer Goals", []) or ()),
        customer_constraints=tuple(brief.sections.get("Customer Constraints", []) or ()),
        success_criteria=tuple(brief.sections.get("Success Criteria", []) or ()),
        what_youre_approving=brief.sections.get("What You're Approving", ""),
        pillars=pillars, phases=phases, scope_includes=scope_includes, add_ons=add_ons,
        term_panels=term_panels, after_approval_steps=after_steps,
        company_facts=company_facts, team=team, contact_strip=contact_strip,
        partnership_discounts=partnership_discounts,
        slide_plan_override=tuple(fm.get("slide_plan", ())),
        resolved_renderings={n: str(eligible[n].resolve()) for n in eligible},
    )

    artifacts = {
        "eligible_renderings": eligible,
        "all_renderings": all_renderings,
        "referenced_filenames": referenced_filenames,
        "scenarios": ws.scenarios,
        "per_line_sums": ws.tier_sums_per_line(),
    }
    return model, artifacts


# === Helpers ===

def _date_offset(iso: str, days: int) -> str:
    d = datetime.fromisoformat(iso).date()
    return (d + timedelta(days=days)).isoformat()


def _date_long(iso: str) -> str:
    if not iso:
        return ""
    d = datetime.fromisoformat(iso).date()
    return d.strftime("%b %d, %Y")


def _build_placeholders(fm: dict, fab_lock: str, sign: str, brief) -> dict:
    """All known {placeholder} keys for voice/boilerplate substitution."""
    fab_minus_60 = _date_offset(fab_lock, days=-60) if fab_lock else ""
    return {
        "project_name": fm["project_name"],
        "project_short": fm.get("project_short", ""),
        "project_year": int(fm["project_year"]),
        "next_year": int(fm["project_year"]) + 1,
        "client_short": fm.get("client_short", ""),
        "proposal_type": fm.get("proposal_type", "Holiday Proposal"),
        "go_live": fm.get("go_live", ""),
        "season_end": fm.get("season_end", ""),
        "fabrication_lock": fab_lock,
        "signing_deadline": sign,
        "proposal_date": fm.get("proposal_date", ""),
        "go_live_long": _date_long(fm.get("go_live", "")),
        "season_end_long": _date_long(fm.get("season_end", "")),
        "fabrication_lock_long": _date_long(fab_lock),
        "signing_deadline_long": _date_long(sign),
        "proposal_date_long": _date_long(fm.get("proposal_date", "")),
        "fabrication_lock_minus_60d": _date_long(fab_minus_60) if fab_minus_60 else "",
        "zone_summary": _build_zone_summary(fm["zones"]),
    }


def _build_zone_summary(zones: list) -> str:
    """e.g. 'six stations from Downtown Riverside through Perris-Downtown'."""
    if not zones:
        return ""
    if len(zones) == 1:
        return zones[0]["name"]
    counts = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
              6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    n_word = counts.get(len(zones), str(len(zones)))
    return f"{n_word} zones from {zones[0]['name']} through {zones[-1]['name']}"


def _fill_pillars(brief, voice, ph):
    # V1: Brief-level Pillars override is not supported — voice preset always wins.
    # If an AE writes a `## Pillars` section, raise rather than silently ignore it.
    if "Pillars" in brief.sections:
        raise ProjectLoadError(
            "Brief 'Pillars' section is not supported in V1; "
            "remove the section to use the voice preset's pillars."
        )
    return tuple(
        {"title": p["title"], "body": substitute_placeholders(p["body"], ph)}
        for p in voice.default_pillars
    )


def _fill_phases(brief, voice, ph):
    return tuple(
        {"label": p["label"], "body": substitute_placeholders(p["body"], ph)}
        for p in voice.default_phases
    )


def _fill_scope_includes(brief, bp, ph):
    if include := brief.sections.get("Scope Includes"):
        return tuple(include) if isinstance(include, list) else (include,)
    return tuple(bp.scope_inclusions_default)


def _fill_add_ons(brief, ph):
    add_ons_raw = brief.sections.get("Add-Ons", [])
    if not add_ons_raw:
        return ()
    if isinstance(add_ons_raw, str):
        add_ons_raw = add_ons_raw.splitlines()
    out = []
    for line in add_ons_raw:
        if isinstance(line, str) and ":" in line:
            text, price = line.rsplit(":", 1)
            out.append((text.strip(), price.strip()))
    return tuple(out)


def _fill_term_panels(brief, bp, ph):
    """4 term panels: payment_schedule, insurance_permits, change_orders, validity.
    Brief frontmatter `term_panel_overrides` can override per-panel."""
    overrides = brief.frontmatter.get("term_panel_overrides", {}) or {}
    panels = {}
    for key in ("payment_schedule", "insurance_permits", "change_orders", "validity"):
        if key in overrides:
            panels[key] = substitute_placeholders(overrides[key], ph)
        else:
            default = bp.term_panels.get(f"default_{key}", "")
            panels[key] = substitute_placeholders(default, ph)
    return panels


def _fill_after_approval_steps(brief, voice, ph):
    return tuple(
        substitute_placeholders(step, ph) for step in voice.default_after_approval_steps
    )


def _fill_company_facts(brief, bp, ph):
    return tuple(bp.company_facts_default_bullets)


def _fill_team(brief, bp, ph):
    return tuple(bp.team_roster)
