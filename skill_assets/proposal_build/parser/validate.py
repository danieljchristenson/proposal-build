"""Validation pass — blocking errors + warnings (sniff test, coverage gaps).

This module exposes individual check functions (used by tests) AND a top-level
run_validation(model) orchestrator that's called by the CLI.
"""
from __future__ import annotations

import re
from typing import Iterable, Mapping

from proposal_build.models import LineItem, ProjectModel, ValidationResult


# --- Sniff test regexes (W5/W6/W7) ---

# W6 markers: dimensions like 14", units mid-sentence (1024 LF), TBD, formula × style, anchoring talk.
_DIMENSION_RE = re.compile(r'\d+"\s')
_UNITS_MID_RE = re.compile(r'\b\d+\s*(LF|ea|LS|sq ft|SF)\b', re.IGNORECASE)
_FORMULA_RE = re.compile(r'\d+\s*[×x]\s*\d+')
_TBD_RE = re.compile(r'\bTBD\b', re.IGNORECASE)
_ANCHORING_RE = re.compile(r'\banchoring\b', re.IGNORECASE)


def check_cfd_sniff(line_items: Iterable[LineItem]) -> list[tuple[str, str]]:
    """Run W5/W6/W7 on Customer-Facing Descriptions. Returns [(code, message), ...]."""
    warnings = []
    for li in line_items:
        cfd = li.customer_facing.strip()
        if not cfd:
            continue   # blocking error 5 handled elsewhere

        # W5 — identical to internal description
        if cfd == li.description.strip():
            warnings.append(("W5",
                f"Row #{li.line_num}: Customer-Facing Description matches internal description verbatim "
                f"— likely copy-pasted, run polish chat."))

        # W6 — internal-jargon markers
        if (_DIMENSION_RE.search(cfd) or _UNITS_MID_RE.search(cfd) or _FORMULA_RE.search(cfd)
                or _TBD_RE.search(cfd) or _ANCHORING_RE.search(cfd)):
            warnings.append(("W6",
                f"Row #{li.line_num}: Customer-Facing Description contains internal markers "
                f"({cfd[:60]!r}) — consider polishing."))

        # W7 — fewer than 4 words
        word_count = len(cfd.split())
        if word_count < 4:
            warnings.append(("W7",
                f"Row #{li.line_num}: Customer-Facing Description is {word_count} words "
                f"({cfd!r}) — consider rewriting."))

    return warnings


def check_zone_coverage(
    line_items: Iterable[LineItem],
    zone_names: Iterable[str],
    brief_bullets: Mapping[str, list[str]],
) -> list[tuple[str, str]]:
    """W2: zone with no priced items.  W3: zone with priced items but bullet count diverges by >2."""
    warnings = []
    items = list(line_items)
    has_wildcard = any(li.zone == "*" for li in items)

    for zone_name in zone_names:
        direct = [li for li in items if li.zone == zone_name]
        bullets = brief_bullets.get(zone_name, [])

        # W2 — no priced items at all (no direct, no wildcard)
        if not direct and not has_wildcard and bullets:
            warnings.append(("W2",
                f"Zone {zone_name!r} has {len(bullets)} bullets in Brief but no priced line items "
                f"in worksheet — confirm intentional."))

        # W3 — direct items present but bullet count diverges by >2
        if direct and bullets:
            divergence = abs(len(direct) - len(bullets))
            if divergence > 2:
                warnings.append(("W3",
                    f"Zone {zone_name!r} has {len(direct)} priced items but {len(bullets)} bullets "
                    f"— confirm intentional."))

    return warnings


def check_unused_renderings(
    eligible: Mapping[str, object],
    referenced_filenames: Iterable[str],
) -> list[tuple[str, str]]:
    """W1: files in Base Scope/ or Enhancements/ that no field references."""
    referenced = set(referenced_filenames)
    warnings = []
    for filename in eligible.keys():
        if filename not in referenced:
            warnings.append(("W1",
                f"Unused rendering: {filename!r}. If intentional, move to "
                f"02 - Renderings/Unused Renderings/ to silence this warning."))
    return warnings


def check_tier_scenarios_drift(per_line_sums: dict, scenarios: tuple | None) -> list[tuple[str, str]]:
    """W4: per-line tier sums vs the worksheet's TIER SCENARIOS block."""
    if not scenarios:
        return []

    # Match scenarios by string-prefix to tier names
    warnings = []
    for label, scenario_total in scenarios:
        upper = label.upper()
        for tier_name, line_total in per_line_sums.items():
            if tier_name.value.upper() in upper:
                drift = scenario_total - line_total
                if drift == 0:
                    continue
                pct = abs(drift) / max(line_total, 1) * 100
                level = "drift > 5%" if pct > 5 else "within tolerance"
                warnings.append(("W4",
                    f"{tier_name.value} per-line sum ${line_total:,.0f} vs scenario block "
                    f"${scenario_total:,.0f} — {pct:.1f}% drift ({level})."))
                break
    return warnings


def run_validation(model: ProjectModel, eligible_renderings: dict, referenced_filenames: list[str],
                   per_line_sums: dict, scenarios: tuple | None) -> ValidationResult:
    """Top-level: run all warning checks. Blocking errors are raised earlier in Parser."""
    warnings = []
    warnings.extend(check_cfd_sniff(model.line_items))
    warnings.extend(check_zone_coverage(
        model.line_items,
        [z.name for z in model.zones],
        {z.name: list(z.bullets) for z in model.zones},
    ))
    warnings.extend(check_unused_renderings(eligible_renderings, referenced_filenames))
    warnings.extend(check_tier_scenarios_drift(per_line_sums, scenarios))

    return ValidationResult(blockers=[], warnings=warnings)
