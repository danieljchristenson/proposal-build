"""Assemble MenuProjectModel from parsed Brief + ROM Worksheet data."""
from __future__ import annotations

from typing import Mapping

from proposal_build.models import MenuProjectModel, ROMLineItem, Section
from proposal_build.parser.brief import BriefData
from proposal_build.parser.worksheet_rom import ROMWorksheetData


def resolve_menu_project(
    brief: BriefData, worksheet: ROMWorksheetData
) -> MenuProjectModel:
    """Combine BriefData (menu-mode) + ROMWorksheetData into a MenuProjectModel.

    Sections are built in Brief order; within each section, items appear in
    the Brief's item_codes order (NOT worksheet order — Brief is authoritative
    on customer-facing display sequence).
    """
    fm = brief.frontmatter
    items_by_code: Mapping[str, ROMLineItem] = {it.code: it for it in worksheet.line_items}

    sections = []
    for s in fm["sections"]:
        items = []
        for code in s["item_codes"]:
            if code not in items_by_code:
                raise ValueError(
                    f"Section {s['key']!r} references item code {code!r} "
                    f"not found in the worksheet"
                )
            items.append(items_by_code[code])
        sections.append(Section(
            key=s["key"],
            label=s["label"],
            name=s["name"],
            is_lead=bool(s["is_lead"]),
            items=tuple(items),
        ))

    return MenuProjectModel(
        client_company=fm["client_company"],
        client_short=fm.get("project_short", fm["client_company"]),
        project_name=fm["project_name"],
        project_short=fm.get("project_short", fm["project_name"]),
        project_year=int(fm["project_year"]),
        project_subtitle=fm.get("project_subtitle", ""),
        presenter_name=fm.get("presenter_name", ""),
        presenter_title=fm.get("presenter_title", ""),
        presenter_org=fm.get("presenter_org", ""),
        proposal_date=fm.get("proposal_date", ""),
        client_contact_name=fm.get("client_decision_maker", ""),
        client_contact_title=fm.get("client_decision_maker_title", ""),
        client_contact_email=fm.get("client_decision_maker_email", ""),
        client_contact_phone=fm.get("client_decision_maker_phone", ""),
        design_phrase=fm["design_phrase"],
        voice=fm["voice"],
        creative_direction=_section_text(brief, "Creative Direction"),
        customer_goals=tuple(_section_list(brief, "Customer Goals")),
        creative_phases=tuple(fm.get("creative_phases", ())),
        prebuilt_cover_image=fm["prebuilt_cover_image"],
        prebuilt_palette_image=fm.get("prebuilt_palette_image", ""),
        creative_vision_hero=fm["creative_vision_hero"],
        sections=tuple(sections),
        what_youre_approving=fm.get("what_youre_approving", ""),
    )


def _section_text(brief: BriefData, name: str) -> str:
    v = brief.sections.get(name, "")
    return v if isinstance(v, str) else ""


def _section_list(brief: BriefData, name: str) -> list[str]:
    v = brief.sections.get(name, [])
    return list(v) if isinstance(v, list) else []
