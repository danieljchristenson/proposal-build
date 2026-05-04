"""Load boilerplate library from skill_assets/boilerplate/."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import frontmatter


BOILERPLATE_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "boilerplate"


@dataclass(frozen=True)
class Boilerplate:
    company_facts: dict
    company_facts_default_bullets: tuple
    team_roster: tuple
    contact_strip: str
    term_panels: dict   # {default_payment_schedule, default_insurance_permits, ...}
    scope_inclusions_default: tuple
    partnership_discounts: tuple
    non_multi_year_renewal_increase: float
    non_multi_year_renewal_note: str


def load_boilerplate() -> Boilerplate:
    company = frontmatter.load(str(BOILERPLATE_DIR / "company_facts.md")).metadata
    team_md = frontmatter.load(str(BOILERPLATE_DIR / "team.md")).metadata
    contact_md = frontmatter.load(str(BOILERPLATE_DIR / "contact_strip.md")).metadata
    terms_md = frontmatter.load(str(BOILERPLATE_DIR / "terms_panels.md")).metadata
    scope_md = frontmatter.load(str(BOILERPLATE_DIR / "scope_inclusions.md")).metadata
    partner_md = frontmatter.load(str(BOILERPLATE_DIR / "partnership_discounts.md")).metadata

    return Boilerplate(
        company_facts={k: v for k, v in company.items() if k != "default_bullets"},
        company_facts_default_bullets=tuple(company["default_bullets"]),
        team_roster=tuple(team_md["roster"]),
        contact_strip=contact_md["text"],
        term_panels={k: v.strip() for k, v in terms_md.items()},
        scope_inclusions_default=tuple(scope_md["default_inclusions"]),
        partnership_discounts=tuple(partner_md["discounts"]),
        non_multi_year_renewal_increase=float(partner_md.get("non_multi_year_renewal_increase", 0.05)),
        non_multi_year_renewal_note=partner_md.get("non_multi_year_renewal_note", ""),
    )


_PLACEHOLDER_RE = re.compile(r"\{([a-z_]+(?:_long|_minus_60d)?)\}")


def substitute_placeholders(text: str, values: dict) -> str:
    """Replace {key} with values[key]. Raises KeyError on unknown placeholder."""
    def _replace(m):
        key = m.group(1)
        if key not in values:
            raise KeyError(f"Unknown placeholder {{{key}}} in text")
        return str(values[key])

    return _PLACEHOLDER_RE.sub(_replace, text)
