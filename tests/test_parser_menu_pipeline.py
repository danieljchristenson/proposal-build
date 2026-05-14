"""Full menu-mode pipeline test: Brief + ROM Worksheet → MenuProjectModel."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.parser import parse_project
from proposal_build.models import MenuProjectModel, ROMLineItem, Section


REPO_ROOT = Path(__file__).resolve().parent.parent
FIGAT7TH = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"


def test_parse_figat7th_yields_menu_model():
    model = parse_project(FIGAT7TH)
    assert isinstance(model, MenuProjectModel)
    assert model.client_company == "FIGat7th"
    assert model.design_phrase == "Modern Magic"


def test_figat7th_sections_match_brief_order():
    model = parse_project(FIGAT7TH)
    keys = [s.key for s in model.sections]
    assert keys == ["1", "2", "3a", "3b"]


def test_figat7th_section_3a_items_in_brief_order():
    """Arches section emits items in the order specified by the Brief's
    item_codes (D=33, C=32, A=30, B=31) — same order the customer sees on the deck."""
    model = parse_project(FIGAT7TH)
    arches = next(s for s in model.sections if s.key == "3a")
    codes = [it.code for it in arches.items]
    assert codes == ["33", "32", "30", "31"]


def test_figat7th_line_item_count():
    """11 priced items, distributed across 4 sections."""
    model = parse_project(FIGAT7TH)
    total = sum(len(s.items) for s in model.sections)
    assert total == 11
