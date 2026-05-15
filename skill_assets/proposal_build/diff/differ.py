"""Compare two last_run.json snapshots and compute the change report."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ChangeKind = Literal["added", "removed", "modified"]


@dataclass(frozen=True)
class ChangeReport:
    brief: dict[str, tuple[ChangeKind]]
    worksheet: dict[str, tuple[ChangeKind]]
    renderings: dict[str, tuple[ChangeKind]]
    slides_added: frozenset[str]
    slides_removed: frozenset[str]

    @property
    def has_changes(self) -> bool:
        return bool(
            self.brief or self.worksheet or self.renderings
            or self.slides_added or self.slides_removed
        )


def diff_snapshots(prior: dict, current: dict) -> ChangeReport:
    return ChangeReport(
        brief=_diff_hash_dict(prior.get("brief", {}), current.get("brief", {})),
        worksheet=_diff_hash_dict(
            prior.get("worksheet", {}), current.get("worksheet", {})
        ),
        renderings=_diff_hash_dict(
            prior.get("renderings", {}), current.get("renderings", {})
        ),
        slides_added=_slide_layouts(current) - _slide_layouts(prior),
        slides_removed=_slide_layouts(prior) - _slide_layouts(current),
    )


def _diff_hash_dict(prior: dict[str, str], current: dict[str, str]) -> dict[str, tuple[ChangeKind]]:
    out: dict[str, tuple[ChangeKind]] = {}
    prior_keys = set(prior)
    current_keys = set(current)
    for k in current_keys - prior_keys:
        out[k] = ("added",)
    for k in prior_keys - current_keys:
        out[k] = ("removed",)
    for k in current_keys & prior_keys:
        if prior[k] != current[k]:
            out[k] = ("modified",)
    return out


def _slide_layouts(snap: dict) -> frozenset[str]:
    return frozenset(s.get("layout", "") for s in snap.get("slides_rendered", []))
