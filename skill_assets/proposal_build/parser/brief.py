"""Parse Project Brief.md — YAML frontmatter + markdown body sections.

Returns BriefData (raw). Voice/boilerplate fill, date auto-derivation, and image
filename resolution happen downstream in the orchestrator (parser/__init__.py).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import frontmatter


REQUIRED_FIELDS = (
    "client_company", "project_name", "project_year", "presenter_name",
    "voice", "recommended_tier", "pricing_format", "cover_image",
)

PROSE_SECTIONS = (
    "Creative Direction", "Customer Goals", "Customer Constraints",
    "Success Criteria", "What You're Approving",
)
# Sections that are bullet lists vs free prose. Bullet sections become tuples; prose stays a string.
BULLET_SECTIONS = {"Customer Goals", "Customer Constraints", "Success Criteria"}


class BriefParseError(Exception):
    """Raised on a blocking Brief problem (missing field, bad structure, etc.)."""


@dataclass
class BriefData:
    frontmatter: dict
    sections: dict   # {section_name: str OR list[str]}


def parse_brief(path: Path) -> BriefData:
    """Parse a Brief.md file into BriefData. Raises BriefParseError on hard issues."""
    if not path.exists():
        raise BriefParseError(f"Brief not found at {path}")

    post = frontmatter.load(str(path))
    fm = dict(post.metadata)

    # Required-field check
    missing = [f for f in REQUIRED_FIELDS if not fm.get(f)]
    if missing:
        raise BriefParseError(f"Brief missing required fields: {', '.join(missing)}")
    if not fm.get("zones"):
        raise BriefParseError("Brief missing required field: zones (must be non-empty list)")

    # Signature-count check
    sigs = [z for z in fm["zones"] if "signature" in (z.get("flags") or [])]
    if len(sigs) > 1:
        names = ", ".join(z["name"] for z in sigs)
        raise BriefParseError(f"At most one zone may carry the 'signature' flag; found: {names}")

    # Parse markdown body into sections
    sections = _split_sections(post.content)

    return BriefData(frontmatter=fm, sections=sections)


def _split_sections(body: str) -> dict[str, Any]:
    """Split markdown body into {heading: content} pairs. Bullet sections → list[str]; prose → str."""
    sections: dict[str, Any] = {}
    current_name = None
    current_lines: list[str] = []

    for line in body.splitlines():
        if line.startswith("## "):
            if current_name is not None:
                sections[current_name] = _coerce_section(current_name, current_lines)
            current_name = line[3:].strip()
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)

    if current_name is not None:
        sections[current_name] = _coerce_section(current_name, current_lines)

    return sections


def _coerce_section(name: str, lines: list[str]) -> Any:
    """Bullet sections → list of bullet text; prose sections → joined string."""
    if name in BULLET_SECTIONS:
        return [ln[2:].strip() for ln in lines if ln.startswith("- ")]
    return "\n".join(lines).strip()
