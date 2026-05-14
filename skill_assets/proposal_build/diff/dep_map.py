"""Load + validate + resolve dependency_map.yaml."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


SUPPORTED_SCHEMA_VERSIONS = {1}


class DepMapError(Exception):
    """Raised on dep_map load/validate problems."""


@dataclass(frozen=True)
class BriefEntry:
    path: str
    human_label: str


@dataclass(frozen=True)
class WorksheetEntry:
    pattern: str
    human_label: str


@dataclass(frozen=True)
class FollowEntry:
    resolve_from: str
    to_assets: tuple[str, ...]


@dataclass(frozen=True)
class SlideEntry:
    brief: tuple[BriefEntry, ...]
    worksheet: tuple[WorksheetEntry, ...]
    renderings: tuple[str, ...] = ()      # glob strings
    follow: tuple[FollowEntry, ...] = ()


@dataclass(frozen=True)
class DepMap:
    schema_version: int
    slides: dict[str, SlideEntry]
    itemized_pricing_pdf: SlideEntry | None
    customer_workbook_xlsx: SlideEntry | None


def load_dep_map(path: Path) -> DepMap:
    """Load a dependency_map.yaml. Raises DepMapError on schema problems."""
    if not path.exists():
        raise DepMapError(f"dependency_map.yaml not found at {path}")

    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    version = raw.get("schema_version")
    if version is None:
        raise DepMapError("dependency_map.yaml missing schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise DepMapError(
            f"dependency_map.yaml schema_version={version!r} not supported "
            f"(supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)})"
        )

    slides: dict[str, SlideEntry] = {}
    for name, body in (raw.get("slides") or {}).items():
        slides[name] = _parse_slide_entry(body)

    itemized = raw.get("itemized_pricing_pdf")
    workbook = raw.get("customer_workbook_xlsx")

    return DepMap(
        schema_version=version,
        slides=slides,
        itemized_pricing_pdf=_parse_slide_entry(itemized) if itemized else None,
        customer_workbook_xlsx=_parse_slide_entry(workbook) if workbook else None,
    )


def _parse_slide_entry(body: dict[str, Any]) -> SlideEntry:
    body = body or {}
    brief = tuple(
        BriefEntry(path=b["path"], human_label=b.get("human_label", ""))
        for b in (body.get("brief") or [])
    )
    worksheet = tuple(
        WorksheetEntry(pattern=w["pattern"], human_label=w.get("human_label", ""))
        for w in (body.get("worksheet") or [])
    )
    renderings = tuple(
        r["glob"] for r in (body.get("renderings") or []) if "glob" in r
    )
    follow = tuple(
        FollowEntry(
            resolve_from=f["resolve_from"],
            to_assets=tuple(f.get("to_assets") or []),
        )
        for f in (body.get("follow") or [])
    )
    return SlideEntry(
        brief=brief, worksheet=worksheet, renderings=renderings, follow=follow,
    )
