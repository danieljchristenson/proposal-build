"""Inspector accepts menu-mode projects without spurious 'missing tier' findings."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.inspector import inspect_project


REPO_ROOT = Path(__file__).resolve().parent.parent
FIGAT7TH = REPO_ROOT / "Projects" / "Fig at 7th - 2026 - Multi-Rendering Project"


def _blockers(report):
    return [f for f in report.findings if f.severity == "blocker"]


def test_figat7th_inspector_passes_or_only_warns():
    """Menu-mode FIGat7th project should not produce tier-related blockers."""
    report = inspect_project(FIGAT7TH)
    tier_blockers = [
        f for f in _blockers(report)
        if "recommended_tier" in str(f) or "pricing_format" in str(f)
        or "zones" in str(f) or "cover_image" in str(f)
    ]
    assert tier_blockers == [], (
        f"Tier-related blockers leaked into menu mode: "
        f"{[(b.issue, b.detail) for b in tier_blockers]}"
    )


def test_figat7th_inspector_no_parser_crashes():
    """The validator pass must not crash on a menu-mode project."""
    report = inspect_project(FIGAT7TH)
    crashes = [f for f in report.findings if f.issue in ("check-crashed", "parser-crashed")]
    assert crashes == [], (
        f"Inspector crashed on menu-mode project: "
        f"{[(c.category, c.detail) for c in crashes]}"
    )


def test_figat7th_inspector_validates_section_items_resolve():
    """If the Brief's sections reference an item code missing from the
    worksheet, the inspector returns a clear blocker. The locked FIGat7th
    project's section/item codes all resolve cleanly."""
    report = inspect_project(FIGAT7TH)
    item_blockers = [
        f for f in _blockers(report)
        if "item_codes" in str(f) or "item code" in str(f).lower()
    ]
    assert item_blockers == [], (
        f"Section/item-code blockers on locked FIGat7th: "
        f"{[(b.issue, b.detail) for b in item_blockers]}"
    )
