"""Top-level Parser orchestrator: build_project_model(project_dir) → ProjectModel.

Composes brief + worksheet + renderings + voice + boilerplate into a fully-
resolved ProjectModel. Blocking errors raise; warnings are returned alongside.
"""
from __future__ import annotations

import re
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
        for gallery_name in z.get("hero_images") or ():
            try:
                resolve_filename(gallery_name, eligible)
                referenced_filenames.append(gallery_name)
            except RenderingsResolutionError as e:
                raise ProjectLoadError(f"zone {z['name']!r} hero_images: {e}") from e
    # greenery_references may resolve outside Base Scope/Enhancements; add the
    # raw filenames so W1 doesn't flag the ones that DO live in eligible folders.
    for greenery_name in fm.get("greenery_references") or ():
        if greenery_name:
            referenced_filenames.append(greenery_name)
    # A prebuilt palette / mood board image is referenced by the full-bleed
    # palette slide; mark it so W1 doesn't flag it as unused.
    if fm.get("prebuilt_palette_image"):
        referenced_filenames.append(fm["prebuilt_palette_image"])

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
            hero_images=tuple(z.get("hero_images") or ()),
            gallery_fit=z.get("gallery_fit", "cover"),
            gallery_orientation=z.get("gallery_orientation", "stacked"),
            gallery_emphasis=z.get("gallery_emphasis", "equal"),
            hero_fit=z.get("hero_fit", "cover"),
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
        client_contact_name=fm.get("client_contact_name", ""),
        client_contact_title=fm.get("client_contact_title", ""),
        client_contact_email=fm.get("client_contact_email", ""),
        client_contact_phone=fm.get("client_contact_phone", ""),
        proposal_date=fm.get("proposal_date", ""),
        go_live=go_live, season_end=fm.get("season_end", ""),
        fabrication_lock=fab_lock, signing_deadline=sign,
        voice=fm["voice"], recommended_tier=Tier.from_string(fm["recommended_tier"]),
        design_phrase=fm.get("design_phrase", ""), pricing_format=fm["pricing_format"],
        cover_image=fm["cover_image"], creative_vision_hero=fm.get("creative_vision_hero", ""),
        creative_vision_hero_fit=fm.get("creative_vision_hero_fit", "cover"),
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
        sample_work=tuple(fm.get("sample_work") or ()),
        resolved_renderings={n: str(eligible[n].resolve()) for n in eligible},
        tier_highlights=fm.get("tier_highlights") or {},
        greenery_references=_resolve_greenery_refs(project_dir, fm.get("greenery_references", [])),
        venue_context=fm.get("venue_context", "") or "",
        greenery_description=fm.get("greenery_description", "") or "",
        prebuilt_palette_image=fm.get("prebuilt_palette_image", "") or "",
        scope_accent=fm.get("scope_accent", "green") or "green",
    )

    # worksheet_rows: per-line dicts keyed by item_code for diff hashing
    worksheet_rows = [
        {
            "item_code": li.line_num,
            "item": li.item,
            "description": li.description,
            "qty": li.qty,
            "unit": li.unit,
            "price": li.price_per_unit,
            "line_total": li.line_total,
            "customer_facing": li.customer_facing,
            "zone": li.zone,
            "tier": ",".join(t.value for t in li.tiers),
            "rendering_ref": li.rendering_ref,
        }
        for li in ws.line_items
    ]

    artifacts = {
        "eligible_renderings": eligible,
        "all_renderings": all_renderings,
        "referenced_filenames": referenced_filenames,
        "scenarios": ws.scenarios,
        "per_line_sums": ws.tier_sums_per_line(),
        "brief_data": brief,            # for diff hashing (Plan 4)
        "worksheet_rows": worksheet_rows,  # for diff hashing (Plan 4)
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
    # Honor Brief-level `pillars:` frontmatter override when present;
    # fall back to the voice preset's default_pillars otherwise.
    if "Pillars" in brief.sections:
        raise ProjectLoadError(
            "Brief 'Pillars' section is not supported; use the `pillars:` "
            "frontmatter key with a list of {title, body} dicts instead."
        )
    source = brief.frontmatter.get("pillars") or voice.default_pillars
    return tuple(
        {"title": p["title"], "body": substitute_placeholders(p["body"], ph)}
        for p in source
    )


def _fill_phases(brief, voice, ph):
    # Honor Brief-level `phases:` frontmatter override when present;
    # fall back to the voice preset's default_phases otherwise.
    source = brief.frontmatter.get("phases") or voice.default_phases
    return tuple(
        {"label": p["label"], "body": substitute_placeholders(p["body"], ph)}
        for p in source
    )


def _resolve_greenery_refs(project_dir: Path, filenames: list) -> tuple[str, ...]:
    """Resolve greenery-reference filenames to absolute paths.

    Searches Greenery references/ first, then falls back to the project's
    rendering subfolders so the AE can pull project-specific renderings
    (e.g. an undecorated swag shot from Base Scope) into the mood board
    without duplicating the file. Silently drops files that don't exist."""
    if not filenames:
        return ()
    search_dirs = [
        project_dir / "Greenery references",
        project_dir / "02 - Renderings" / "Base Scope",
        project_dir / "02 - Renderings" / "Enhancements",
    ]
    out = []
    for name in filenames:
        for folder in search_dirs:
            p = folder / name
            if p.exists():
                out.append(str(p.resolve()))
                break
    return tuple(out)


def _fill_scope_includes(brief, bp, ph):
    if include := brief.sections.get("Scope Includes"):
        return tuple(include) if isinstance(include, list) else (include,)
    return tuple(bp.scope_inclusions_default)


_ADD_ON_PRICE_RE = re.compile(r"\$\s?[\d][\d,]*(?:\.\d{2})?")


def _fill_add_ons(brief, ph):
    """Parse the Add-Ons section into ((description, price), ...) tuples.

    Each line looks like 'Description (qualifier): $1,234' OR
    'Description: $1,234 (qualifier)'. The price is whatever matches
    `$N,NNN` — not 'everything after the last colon'. The à-la-carte
    layout's Price column has nowrap and a fixed 1.6in width, so a stray
    parenthetical mistakenly captured into the price column overflows
    and gets visually truncated. (See the twinkle line bug, fixed
    2026-05-06: '$17,324 (net of snowflake removal)' lost the
    parenthetical at render time.)
    """
    add_ons_raw = brief.sections.get("Add-Ons", [])
    if not add_ons_raw:
        return ()
    if isinstance(add_ons_raw, str):
        add_ons_raw = add_ons_raw.splitlines()
    out = []
    for line in add_ons_raw:
        if not isinstance(line, str):
            continue
        price_match = _ADD_ON_PRICE_RE.search(line)
        if price_match is None:
            # Fall back to legacy rsplit behavior so an oddly-formatted line
            # still parses without dropping silently. Trade-off: rare lines
            # without a $ pattern get the old behavior.
            if ":" in line:
                text, price = line.rsplit(":", 1)
                out.append((text.strip(), price.strip()))
            continue
        price = price_match.group(0).strip()
        # Strip the price match out of the line, plus the trailing colon
        # before it (`Description: $1,234` → `Description`). Anything
        # remaining (e.g. a parenthetical after the price) is folded back
        # into the description in source order.
        before = line[:price_match.start()].rstrip().rstrip(":").rstrip()
        after = line[price_match.end():].strip()
        if after:
            description = f"{before} {after}".strip()
        else:
            description = before
        out.append((description, price))
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


def parse_project(project_dir):
    """Top-level entry: route to tiered or menu pipeline based on Brief's mode.

    Returns just the model (ProjectModel for tiered, MenuProjectModel for menu).
    Use build_project_model() if you need the artifacts dict alongside the model.
    """
    project_dir = Path(project_dir)
    brief_path = project_dir / "04 - Process & Notes" / "Project Brief.md"
    try:
        brief = parse_brief(brief_path)
    except BriefParseError as e:
        raise ProjectLoadError(f"Brief: {e}") from e

    mode = brief.frontmatter.get("mode", "tiered")
    if mode == "menu":
        from proposal_build.parser.worksheet_rom import parse_rom_worksheet, ROMWorksheetParseError
        from proposal_build.parser.menu_resolver import resolve_menu_project
        worksheet_path = _find_menu_worksheet(project_dir, brief.frontmatter)
        try:
            ws = parse_rom_worksheet(worksheet_path)
        except ROMWorksheetParseError as e:
            raise ProjectLoadError(f"ROM Worksheet: {e}") from e
        return resolve_menu_project(brief, ws)

    # Tiered path — re-use the existing orchestrator and drop the artifacts.
    model, _artifacts = build_project_model(project_dir)
    return model


def _find_menu_worksheet(project_dir: Path, fm: dict) -> Path:
    """Locate the ROM worksheet for a menu-mode project.

    Try `{project_short} - Scope Worksheet.xlsx` first; fall back to a single
    `*Scope Worksheet*.xlsx` in `03 - Scope & Pricing/`, then to a single
    `*.xlsx` if no name convention matched.
    """
    scope_dir = project_dir / "03 - Scope & Pricing"
    short = fm.get("project_short") or fm["project_name"]
    candidate = scope_dir / f"{short} - Scope Worksheet.xlsx"
    if candidate.exists():
        return candidate
    matches = list(scope_dir.glob("*Scope Worksheet*.xlsx"))
    if not matches:
        matches = list(scope_dir.glob("*.xlsx"))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ProjectLoadError(f"No ROM worksheet found in {scope_dir}")
    raise ProjectLoadError(
        f"Multiple worksheets in {scope_dir}; can't pick one: {[p.name for p in matches]}"
    )
