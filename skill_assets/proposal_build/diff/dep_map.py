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


import fnmatch
import re


@dataclass(frozen=True)
class ResolvedDeps:
    """Concrete dependency keys for one slide, resolved against current inputs."""
    brief: frozenset[str]      # brief flat paths
    worksheet: frozenset[str]  # worksheet flat keys
    assets: frozenset[str]     # filesystem paths (from follow chains + rendering globs)


def resolve_slide_deps(
    slide: SlideEntry,
    brief_flat: dict[str, Any],
    worksheet_hashes: dict[str, str],
) -> ResolvedDeps:
    """Expand a SlideEntry's patterns + follow chains against current inputs."""
    # Brief: direct path matches AND any nested children
    # (a brief entry of 'tree_comparison.trees' should also match
    # 'tree_comparison.trees.0', 'tree_comparison.trees.1', etc.)
    brief: set[str] = set()
    for b in slide.brief:
        if b.path in brief_flat:
            brief.add(b.path)
        for key in brief_flat:
            if key == b.path or key.startswith(b.path + "."):
                brief.add(key)

    # Worksheet: fnmatch each pattern against actual cell keys.
    worksheet: set[str] = set()
    for w in slide.worksheet:
        regex = _glob_to_regex(w.pattern)
        for key in worksheet_hashes:
            if regex.fullmatch(key):
                worksheet.add(key)

    # Follow chains: read brief values, substitute {id}, collect paths.
    assets: set[str] = set()
    for chain in slide.follow:
        ids = _collect_follow_ids(chain.resolve_from, brief_flat)
        for asset_template in chain.to_assets:
            for ident in ids:
                assets.add(asset_template.format(id=ident))

    return ResolvedDeps(
        brief=frozenset(brief),
        worksheet=frozenset(worksheet),
        assets=frozenset(assets),
    )


def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    """fnmatch-style glob to compiled regex."""
    return re.compile(fnmatch.translate(pattern))


def _collect_follow_ids(source_path: str, brief_flat: dict[str, Any]) -> list[str]:
    """Read the brief value at source_path. If it's a list (tree_comparison.trees),
    return list elements. If scalar, return [value]. Missing -> []."""
    # Scalar case: source_path is directly in brief_flat
    if source_path in brief_flat:
        val = brief_flat[source_path]
        if isinstance(val, list):
            return [str(v) for v in val]
        return [str(val)]
    # List case: brief_flat has source_path.0, source_path.1, ...
    prefix = source_path + "."
    indexed = [(k, v) for k, v in brief_flat.items() if k.startswith(prefix)]
    if not indexed:
        return []
    indexed.sort(key=lambda kv: kv[0])
    return [str(v) for _, v in indexed]
