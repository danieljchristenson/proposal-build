"""Tests for menu-mode (creative-menu / ROM) Brief parsing.

The existing tiered-mode parse continues to work unchanged; this test
focuses on the new mode-detection and validation path.
"""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from proposal_build.parser.brief import parse_brief, BriefParseError


def _write_brief(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "Project Brief.md"
    p.write_text(dedent(content).lstrip("\n"))
    return p


MENU_BRIEF_VALID = """
---
status: ready
mode: menu

client_company: "FIGat7th"
client_decision_maker: "Alexandra Castro"
client_decision_maker_title: "Property Manager, Athena PM"
client_decision_maker_email: "acastro@athenapm.com"

project_name: "FIGat7th DTLA — 2026 Holiday Program"
project_short: "FIGat7th DTLA"
project_year: 2026

design_phrase: "Modern Magic"
voice: "destination-retail"

prebuilt_cover_image: "01_cover-slide-cityscape.png"
prebuilt_palette_image: "02_palette-board-mood.png"
creative_vision_hero: "10_tree-A-studio-blackbg.png"

sections:
  - { key: "1",  label: "Section 1 — Main Entrance Overhead",   name: "Main Entrance Overhead", is_lead: true,  item_codes: ["20"] }
  - { key: "2",  label: "Section 2 — Holiday Tree + Photo Op",  name: "The FIGat7th Tree",      is_lead: true,  item_codes: ["10", "10-enh"] }
  - { key: "3a", label: "Section 3a — Plaza Arches",            name: "Plaza Photo-Ops",        is_lead: true,  item_codes: ["33", "32", "30", "31"] }
  - { key: "3b", label: "Section 3b — Plaza Photo-Ops",         name: "Plaza Photo-Ops",        is_lead: false, item_codes: ["40", "41", "42", "43"] }
---

## Creative Direction

FIGat7th becomes Downtown LA's most photographed holiday destination.

## Customer Goals

- Drive incremental foot traffic.
- Generate Instagram-worthy moments.
- Athena's first-year statement.

## Showcase Sections

1. **Main Entrance Overhead** — An ornament canopy that turns the courtyard ceiling into a winter night sky.
2. **The FIGat7th Tree** — The centerpiece every shopper poses with.
3. **Plaza Photo-Ops** — A menu of arches, frames, and selfie moments.
"""


def test_menu_mode_parses(tmp_path):
    """Menu-mode briefs parse without requiring tier-related fields."""
    path = _write_brief(tmp_path, MENU_BRIEF_VALID)
    brief = parse_brief(path)
    assert brief.frontmatter["mode"] == "menu"
    assert brief.frontmatter["design_phrase"] == "Modern Magic"
    assert len(brief.frontmatter["sections"]) == 4


def test_menu_mode_rejects_when_sections_missing(tmp_path):
    """Brief with mode: menu but no sections list is rejected."""
    # Strip the entire `sections:` block (sections + its 4 indented list items)
    # so the YAML stays valid but the field is absent.
    lines = MENU_BRIEF_VALID.splitlines(keepends=True)
    bad_lines: list[str] = []
    skipping = False
    for line in lines:
        if line.startswith("sections:"):
            skipping = True
            continue
        if skipping:
            # Continue skipping indented list items belonging to `sections:`
            if line.startswith("  -") or line.startswith("  "):
                continue
            skipping = False
        bad_lines.append(line)
    bad = "".join(bad_lines)
    path = _write_brief(tmp_path, bad)
    with pytest.raises(BriefParseError, match="sections"):
        parse_brief(path)


def test_menu_mode_rejects_tiered_fields(tmp_path):
    """Brief with mode: menu must not carry recommended_tier or zones."""
    bad = MENU_BRIEF_VALID.replace(
        "mode: menu",
        'mode: menu\nrecommended_tier: "essential"',
    )
    path = _write_brief(tmp_path, bad)
    with pytest.raises(BriefParseError, match="recommended_tier"):
        parse_brief(path)


def test_tiered_mode_unchanged(tmp_path):
    """An existing tiered-mode Brief (no `mode` field, defaults to tiered) still parses."""
    tiered = """
        ---
        status: ready
        client_company: "RCTC"
        project_name: "Riverside MetroLink"
        project_year: 2026
        presenter_name: "Jonathan Yang"
        voice: "civic"
        recommended_tier: "enhanced"
        pricing_format: "three"
        cover_image: "tree.png"
        zones:
          - { name: "Downtown", subtitle: "flagship", flags: [flagship] }
        ---

        ## Creative Direction
        Civic-scale program.
    """
    path = _write_brief(tmp_path, tiered)
    brief = parse_brief(path)
    # mode field absent → tiered default behavior is preserved
    assert brief.frontmatter.get("mode", "tiered") == "tiered"
