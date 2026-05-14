# Plan 4 — Diff-Mode Regeneration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `last_run.json` snapshot + `dependency_map.yaml`-driven differ to the existing `python -m proposal_build generate` pipeline so each regen produces a change report (terminal), a customer-pasteable `change_summary.md`, and an automatic `04 - Process & Notes/revisions/v<n>/` archive.

**Architecture:** Pure pre-render and post-render hooks around the existing renderer. New `skill_assets/proposal_build/diff/` package owns hashing, snapshot I/O, dep-map resolution, change-summary text generation, and revision-folder copying. CLI grows two flags (`--no-snapshot`, `--diff-only`) but the default `generate` path stays compatible. The existing `layout_pin.json` infrastructure (Plan 3 ratification) handles layout-version locking and is untouched.

**Tech Stack:** Python 3.11+, hashlib (sha256), pyyaml (already in deps), shutil, pathlib. No new dependencies.

**Reference:** Approved spec at `docs/superpowers/specs/2026-05-14-04-diff-mode-regeneration-design.md`.

---

## File Structure

**New package `skill_assets/proposal_build/diff/`:**

| File | Responsibility |
|---|---|
| `__init__.py` | Public API surface (re-exports) |
| `hasher.py` | sha256 utilities + Brief/Worksheet/rendering flatteners |
| `dep_map.py` | Load + validate + resolve `dependency_map.yaml` |
| `differ.py` | Compare two snapshot dicts; compute affected slides |
| `snapshot.py` | Read/write `last_run.json` with schema_version handling |
| `summary.py` | Render `change_summary.md` text from differ output |
| `revisions.py` | Copy outputs to `04 - Process & Notes/revisions/v<n>/` |

**New skill-bundled file:** `skill_assets/dependency_map.yaml`

**Modified files:**
- `skill_assets/proposal_build/cli.py:18-44` — add `--no-snapshot`, `--diff-only` flags + plumbing
- `skill_assets/proposal_build/cli.py:47-83` — `_do_generate` calls the diff hooks
- `.gitignore` — add `revisions/` pattern
- `skill_assets/AE_SOP.md` — append a "Revision tracking" section

**New tests:**

| File | What it covers |
|---|---|
| `tests/test_diff_hasher.py` | Determinism, JSON-path flattening, file hashing |
| `tests/test_diff_dep_map.py` | YAML load, schema validation, static/glob/follow resolution |
| `tests/test_diff_differ.py` | Add/remove/modify detection, affected-slides computation |
| `tests/test_diff_snapshot.py` | Write, read, schema_version mismatch, corrupt-file recovery |
| `tests/test_diff_summary.py` | Bullet generation, human_label substitution + fallback |
| `tests/test_diff_revisions.py` | Folder creation, file copy, counter logic |
| `tests/test_diff_cli.py` | `--no-snapshot` and `--diff-only` behavior |
| `tests/test_diff_integration.py` | Full pipeline twice on a fixture project |

Target: 251 → ~280 tests.

---

## Task 1: Set up `diff/` package skeleton + first hasher test

**Files:**
- Create: `skill_assets/proposal_build/diff/__init__.py`
- Create: `skill_assets/proposal_build/diff/hasher.py`
- Create: `tests/test_diff_hasher.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_diff_hasher.py
"""Tests for skill_assets/proposal_build/diff/hasher.py."""
from __future__ import annotations

from proposal_build.diff.hasher import hash_string


def test_hash_string_is_sha256_with_prefix():
    h = hash_string("hello")
    assert h.startswith("sha256:")
    assert len(h) == len("sha256:") + 64  # hex sha256


def test_hash_string_is_deterministic():
    assert hash_string("hello") == hash_string("hello")


def test_hash_string_differs_for_different_input():
    assert hash_string("hello") != hash_string("world")
```

- [ ] **Step 2: Run test to verify it fails**

```
source .venv/bin/activate
python -m pytest tests/test_diff_hasher.py -v -p no:warnings
```

Expected: ImportError / ModuleNotFoundError for `proposal_build.diff.hasher`.

- [ ] **Step 3: Create the package files with minimal implementation**

```python
# skill_assets/proposal_build/diff/__init__.py
"""Diff-mode regeneration support: snapshot, differ, change report, revision archival."""
```

```python
# skill_assets/proposal_build/diff/hasher.py
"""sha256 hashing utilities for Brief/Worksheet/rendering/output content."""
from __future__ import annotations

import hashlib


def hash_string(s: str) -> str:
    """Return sha256 hex of a UTF-8 string, prefixed with 'sha256:'."""
    digest = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"
```

- [ ] **Step 4: Run test to verify it passes**

```
python -m pytest tests/test_diff_hasher.py -v -p no:warnings
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/diff/__init__.py skill_assets/proposal_build/diff/hasher.py tests/test_diff_hasher.py
git commit -m "feat(plan-4): diff/ package skeleton + string hashing"
```

---

## Task 2: Brief flattening + Brief hashing

**Files:**
- Modify: `skill_assets/proposal_build/diff/hasher.py`
- Modify: `tests/test_diff_hasher.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_diff_hasher.py`:

```python
from proposal_build.diff.hasher import flatten_brief, hash_brief
from proposal_build.parser.brief import BriefData


def test_flatten_brief_top_level():
    bd = BriefData(
        frontmatter={"client_name": "Acme", "project_year": 2026},
        sections={},
    )
    flat = flatten_brief(bd)
    assert flat["client_name"] == "Acme"
    assert flat["project_year"] == 2026


def test_flatten_brief_nested_dict():
    bd = BriefData(
        frontmatter={"tree_comparison": {"trees": ["a", "b"], "recommended": "b"}},
        sections={},
    )
    flat = flatten_brief(bd)
    assert flat["tree_comparison.recommended"] == "b"
    assert flat["tree_comparison.trees.0"] == "a"
    assert flat["tree_comparison.trees.1"] == "b"


def test_flatten_brief_list_of_dicts():
    bd = BriefData(
        frontmatter={"creative_phases": [
            {"label": "ARRIVE", "body": "x"},
            {"label": "GATHER", "body": "y"},
        ]},
        sections={},
    )
    flat = flatten_brief(bd)
    assert flat["creative_phases.0.label"] == "ARRIVE"
    assert flat["creative_phases.0.body"] == "x"
    assert flat["creative_phases.1.body"] == "y"


def test_flatten_brief_includes_sections():
    bd = BriefData(
        frontmatter={"client_name": "Acme"},
        sections={"Creative Direction": "An ornament canopy..."},
    )
    flat = flatten_brief(bd)
    assert flat["sections.Creative Direction"] == "An ornament canopy..."


def test_hash_brief_returns_path_to_hash_map():
    bd = BriefData(
        frontmatter={"client_name": "Acme"},
        sections={"Creative Direction": "x"},
    )
    hashes = hash_brief(bd)
    assert hashes["client_name"].startswith("sha256:")
    assert hashes["sections.Creative Direction"].startswith("sha256:")


def test_hash_brief_deterministic():
    bd1 = BriefData(frontmatter={"a": 1, "b": 2}, sections={})
    bd2 = BriefData(frontmatter={"b": 2, "a": 1}, sections={})  # key order differs
    assert hash_brief(bd1) == hash_brief(bd2)
```

- [ ] **Step 2: Run test to verify it fails**

```
python -m pytest tests/test_diff_hasher.py -v -p no:warnings
```

Expected: ImportError for `flatten_brief` and `hash_brief`.

- [ ] **Step 3: Implement**

Append to `skill_assets/proposal_build/diff/hasher.py`:

```python
from typing import Any

from proposal_build.parser.brief import BriefData


def flatten_brief(brief: BriefData) -> dict[str, Any]:
    """Flatten a BriefData (frontmatter + sections) to JSON-path keyed dict.

    Lists are indexed (creative_phases.0.body). Dicts use dotted keys.
    Sections are prefixed with 'sections.'.
    """
    out: dict[str, Any] = {}
    _walk("", brief.frontmatter, out)
    _walk("sections", brief.sections, out)
    return out


def _walk(prefix: str, value: Any, out: dict[str, Any]) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            _walk(key, v, out)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            _walk(f"{prefix}.{i}", item, out)
    else:
        out[prefix] = value


def hash_brief(brief: BriefData) -> dict[str, str]:
    """Hash each flattened Brief path value. Returns {path: 'sha256:...'}."""
    flat = flatten_brief(brief)
    return {path: hash_string(repr(value)) for path, value in flat.items()}
```

- [ ] **Step 4: Run test to verify it passes**

```
python -m pytest tests/test_diff_hasher.py -v -p no:warnings
```

Expected: 9 passed (3 from Task 1 + 6 new).

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/diff/hasher.py tests/test_diff_hasher.py
git commit -m "feat(plan-4): Brief flattening to JSON-path map + per-path hashing"
```

---

## Task 3: Worksheet + rendering + output file hashing

**Files:**
- Modify: `skill_assets/proposal_build/diff/hasher.py`
- Modify: `tests/test_diff_hasher.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_diff_hasher.py`:

```python
from pathlib import Path

import pytest

from proposal_build.diff.hasher import hash_worksheet_rows, hash_file


def test_hash_worksheet_rows_keys_by_item_code():
    rows = [
        {"item_code": "20", "rental_low": 1000, "rental_high": 1200},
        {"item_code": "10-enh", "rental_low": 500, "rental_high": 600},
    ]
    h = hash_worksheet_rows(rows)
    assert "row.20.rental_low" in h
    assert "row.20.rental_high" in h
    assert "row.10-enh.rental_low" in h
    assert h["row.20.rental_low"].startswith("sha256:")


def test_hash_worksheet_rows_handles_hyphen_in_item_code():
    rows = [{"item_code": "10-enh", "rental_low": 500}]
    h = hash_worksheet_rows(rows)
    assert "row.10-enh.rental_low" in h


def test_hash_file_returns_sha256(tmp_path: Path):
    f = tmp_path / "x.txt"
    f.write_bytes(b"hello")
    h = hash_file(f)
    assert h == "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_hash_file_missing_returns_none(tmp_path: Path):
    h = hash_file(tmp_path / "does_not_exist.txt")
    assert h is None
```

- [ ] **Step 2: Run test to verify it fails**

```
python -m pytest tests/test_diff_hasher.py -v -p no:warnings
```

Expected: ImportError for `hash_worksheet_rows` and `hash_file`.

- [ ] **Step 3: Implement**

Append to `skill_assets/proposal_build/diff/hasher.py`:

```python
from pathlib import Path


def hash_worksheet_rows(rows: list[dict]) -> dict[str, str]:
    """Hash each worksheet cell. Keys: row.<item_code>.<column_name>.

    Each row dict must include an 'item_code' key. All other keys are
    treated as columns.
    """
    out: dict[str, str] = {}
    for row in rows:
        item_code = row.get("item_code")
        if item_code is None:
            continue
        for col, val in row.items():
            if col == "item_code":
                continue
            key = f"row.{item_code}.{col}"
            out[key] = hash_string(repr(val))
    return out


def hash_file(path: Path, chunk_size: int = 65536) -> str | None:
    """Return sha256 of file contents, or None if file does not exist."""
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"
```

- [ ] **Step 4: Run test to verify it passes**

```
python -m pytest tests/test_diff_hasher.py -v -p no:warnings
```

Expected: 13 passed (9 prior + 4 new).

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/diff/hasher.py tests/test_diff_hasher.py
git commit -m "feat(plan-4): worksheet-row and file hashing"
```

---

## Task 4: Author `dependency_map.yaml` + loader/validator

**Files:**
- Create: `skill_assets/dependency_map.yaml`
- Create: `skill_assets/proposal_build/diff/dep_map.py`
- Create: `tests/test_diff_dep_map.py`

- [ ] **Step 1: Author the dependency map**

Create `skill_assets/dependency_map.yaml`. Cover every layout currently in `skill_assets/layouts/`. To get the list of current layouts run `ls skill_assets/layouts/*.html` first.

```yaml
schema_version: 1

slides:
  cover:
    brief:
      - path: client_name
        human_label: "Client name"
      - path: project_name
        human_label: "Project name"
      - path: project_year
        human_label: "Project year"
      - path: cover_image
        human_label: "Cover image"
    worksheet: []
    renderings:
      - glob: "Base Scope/01_*"

  creative_vision:
    brief:
      - path: design_phrase
        human_label: "Design phrase"
      - path: creative_vision_hero
        human_label: "Creative vision hero image"
      - path: creative_phases
        human_label: "Creative phases (ARRIVE/GATHER/EXPLORE bodies)"
    worksheet: []

  zone_solo:
    brief:
      - path: zones
        human_label: "Zone scope and copy"
    worksheet: []

  zone_solo_gallery:
    brief:
      - path: zones
        human_label: "Zone scope and copy"
    worksheet: []

  zone_solo_fullbleed:
    brief:
      - path: zones
        human_label: "Zone scope and copy"
    worksheet: []

  zone_feature:
    brief:
      - path: zones
        human_label: "Zone scope and copy"
    worksheet: []

  zone_2up_gallery:
    brief:
      - path: sections
        human_label: "Section structure"
    worksheet: []

  rom_investment:
    brief:
      - path: sections
        human_label: "Section / scope structure"
    worksheet:
      - pattern: "row.*.rental_low"
        human_label: "Annual rental low"
      - pattern: "row.*.rental_high"
        human_label: "Annual rental high"
      - pattern: "row.*.purchase_ot_low"
        human_label: "One-time purchase low"
      - pattern: "row.*.purchase_ot_high"
        human_label: "One-time purchase high"
      - pattern: "row.*.purchase_svc_low"
        human_label: "Annual service low"
      - pattern: "row.*.purchase_svc_high"
        human_label: "Annual service high"

  investment:
    brief:
      - path: tier_highlights
        human_label: "Tier highlights"
      - path: recommended_tier
        human_label: "Recommended tier"
    worksheet:
      - pattern: "row.*.tier"
        human_label: "Line-item tier assignment"
      - pattern: "row.*.price"
        human_label: "Line-item price"

  a_la_carte:
    brief:
      - path: add_ons
        human_label: "Add-on items"
    worksheet: []

  material_palette:
    brief:
      - path: greenery_references
        human_label: "Greenery references"
      - path: greenery_description
        human_label: "Greenery description"
    worksheet: []

  tree_comparison:
    brief:
      - path: tree_comparison.trees
        human_label: "Tree comparison — sizes shown"
      - path: tree_comparison.recommended
        human_label: "Tree comparison — recommended size"
    worksheet: []
    follow:
      - resolve_from: tree_comparison.trees
        to_assets:
          - "skill_assets/tree_library/{id}.md"
          - "skill_assets/tree_library/{id}.jpg"

  sample_of_work:
    brief:
      - path: sample_work
        human_label: "Past-work selection"
    worksheet: []
    follow:
      - resolve_from: sample_work
        to_assets:
          - "skill_assets/past_work_library/{id}.md"
          - "skill_assets/past_work_library/{id}.jpg"

  about:
    brief:
      - path: company_facts
        human_label: "Company facts"
      - path: team
        human_label: "Team roster"
    worksheet: []

  sign_off:
    brief:
      - path: presenter_name
        human_label: "Presenter name"
      - path: presenter_email
        human_label: "Presenter email"
      - path: proposal_date
        human_label: "Proposal date"
      - path: signing_deadline
        human_label: "Signing deadline"
    worksheet: []

  sign_off_menu:
    brief:
      - path: presenter_name
        human_label: "Presenter name"
      - path: presenter_email
        human_label: "Presenter email"
      - path: proposal_date
        human_label: "Proposal date"
    worksheet: []

  image_fullbleed:
    brief:
      - path: zones
        human_label: "Zone scope and copy"
    worksheet: []

  section_divider:
    brief:
      - path: sections
        human_label: "Section structure"
    worksheet: []

itemized_pricing_pdf:
  brief:
    - path: client_name
      human_label: "Client name"
    - path: sections
      human_label: "Section / scope structure"
  worksheet:
    - pattern: "row.*"
      human_label: "Pricing line items"

customer_workbook_xlsx:
  brief:
    - path: client_name
      human_label: "Client name"
    - path: project_name
      human_label: "Project name"
  worksheet:
    - pattern: "row.*"
      human_label: "Worksheet line items"
```

> Note: if a layout in `skill_assets/layouts/` is missing from this map, the implementer should add it before continuing. Run `ls skill_assets/layouts/*.html | xargs -n1 basename | sed 's/\.html$//'` and cross-check.

- [ ] **Step 2: Write the failing tests**

```python
# tests/test_diff_dep_map.py
"""Tests for dependency map loading + validation."""
from __future__ import annotations

from pathlib import Path

import pytest

from proposal_build.diff.dep_map import (
    load_dep_map, DepMapError, DepMap,
)


SKILL_DEP_MAP = Path(__file__).resolve().parent.parent / "skill_assets" / "dependency_map.yaml"


def test_load_skill_dep_map():
    dm = load_dep_map(SKILL_DEP_MAP)
    assert isinstance(dm, DepMap)
    assert dm.schema_version == 1
    assert "cover" in dm.slides
    assert "tree_comparison" in dm.slides


def test_load_dep_map_missing_schema_version(tmp_path: Path):
    f = tmp_path / "dm.yaml"
    f.write_text("slides:\n  cover:\n    brief: []\n    worksheet: []\n")
    with pytest.raises(DepMapError, match="schema_version"):
        load_dep_map(f)


def test_load_dep_map_unknown_schema_version(tmp_path: Path):
    f = tmp_path / "dm.yaml"
    f.write_text("schema_version: 99\nslides: {}\n")
    with pytest.raises(DepMapError, match="schema_version"):
        load_dep_map(f)


def test_load_dep_map_file_missing(tmp_path: Path):
    with pytest.raises(DepMapError, match="not found"):
        load_dep_map(tmp_path / "missing.yaml")


def test_load_dep_map_brief_entries_have_human_labels():
    """Every brief path should have a human_label (otherwise change-report falls back)."""
    dm = load_dep_map(SKILL_DEP_MAP)
    missing = []
    for slide_name, entry in dm.slides.items():
        for brief_entry in entry.brief:
            if not brief_entry.human_label:
                missing.append(f"{slide_name}/{brief_entry.path}")
    assert missing == [], f"Brief paths without human_label: {missing}"
```

- [ ] **Step 3: Run test to verify it fails**

```
python -m pytest tests/test_diff_dep_map.py -v -p no:warnings
```

Expected: ImportError for `proposal_build.diff.dep_map`.

- [ ] **Step 4: Implement**

Create `skill_assets/proposal_build/diff/dep_map.py`:

```python
"""Load + validate + resolve dependency_map.yaml."""
from __future__ import annotations

from dataclasses import dataclass, field
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
    renderings = tuple(r["glob"] for r in (body.get("renderings") or []) if "glob" in r)
    follow = tuple(
        FollowEntry(
            resolve_from=f["resolve_from"],
            to_assets=tuple(f.get("to_assets") or []),
        )
        for f in (body.get("follow") or [])
    )
    return SlideEntry(brief=brief, worksheet=worksheet, renderings=renderings, follow=follow)
```

- [ ] **Step 5: Run test to verify it passes**

```
python -m pytest tests/test_diff_dep_map.py -v -p no:warnings
```

Expected: 5 passed. If `test_load_dep_map_brief_entries_have_human_labels` fails, it means the YAML authored in Step 1 has missing labels — fix those in the YAML, not the test.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/dependency_map.yaml skill_assets/proposal_build/diff/dep_map.py tests/test_diff_dep_map.py
git commit -m "feat(plan-4): dependency_map.yaml + loader"
```

---

## Task 5: Dep-map resolver (static + glob + follow chains)

**Files:**
- Modify: `skill_assets/proposal_build/diff/dep_map.py`
- Modify: `tests/test_diff_dep_map.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_diff_dep_map.py`:

```python
from proposal_build.diff.dep_map import resolve_slide_deps, ResolvedDeps


def _slide(brief_paths=(), worksheet_patterns=(), follow_chains=()):
    return SlideEntry(
        brief=tuple(BriefEntry(p, p) for p in brief_paths),
        worksheet=tuple(WorksheetEntry(p, p) for p in worksheet_patterns),
        renderings=(),
        follow=tuple(
            FollowEntry(resolve_from=src, to_assets=tuple(targets))
            for src, targets in follow_chains
        ),
    )


def test_resolve_static_brief_paths():
    slide = _slide(brief_paths=("client_name", "project_name"))
    deps = resolve_slide_deps(
        slide,
        brief_flat={"client_name": "Acme", "project_name": "Holiday", "extra": "x"},
        worksheet_hashes={},
    )
    assert "client_name" in deps.brief
    assert "project_name" in deps.brief
    assert "extra" not in deps.brief


def test_resolve_worksheet_glob():
    slide = _slide(worksheet_patterns=("row.*.rental_low", "row.*.rental_high"))
    deps = resolve_slide_deps(
        slide,
        brief_flat={},
        worksheet_hashes={
            "row.20.rental_low": "sha256:a",
            "row.20.rental_high": "sha256:b",
            "row.20.purchase_ot_low": "sha256:c",
        },
    )
    assert "row.20.rental_low" in deps.worksheet
    assert "row.20.rental_high" in deps.worksheet
    assert "row.20.purchase_ot_low" not in deps.worksheet


def test_resolve_follow_chain():
    slide = _slide(
        brief_paths=("tree_comparison.trees",),
        follow_chains=(("tree_comparison.trees", ("skill_assets/tree_library/{id}.md",)),),
    )
    deps = resolve_slide_deps(
        slide,
        brief_flat={
            "tree_comparison.trees.0": "tree_30",
            "tree_comparison.trees.1": "tree_50",
        },
        worksheet_hashes={},
    )
    assert "skill_assets/tree_library/tree_30.md" in deps.assets
    assert "skill_assets/tree_library/tree_50.md" in deps.assets


def test_resolve_follow_chain_missing_source_yields_no_assets():
    slide = _slide(
        follow_chains=(("missing_field", ("skill_assets/x/{id}.md",)),),
    )
    deps = resolve_slide_deps(
        slide, brief_flat={}, worksheet_hashes={},
    )
    assert deps.assets == set()
```

- [ ] **Step 2: Run test to verify it fails**

```
python -m pytest tests/test_diff_dep_map.py -v -p no:warnings
```

Expected: ImportError for `resolve_slide_deps`.

- [ ] **Step 3: Implement**

Append to `skill_assets/proposal_build/diff/dep_map.py`:

```python
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
    # Brief: direct path matches.
    brief = {b.path for b in slide.brief if b.path in brief_flat}

    # Brief: also include nested children (a brief entry of 'tree_comparison.trees'
    # should match all 'tree_comparison.trees.*' flat keys).
    for b in slide.brief:
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
    return list elements. If scalar, return [value]. Missing → []."""
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
```

- [ ] **Step 4: Run test to verify it passes**

```
python -m pytest tests/test_diff_dep_map.py -v -p no:warnings
```

Expected: 9 passed (5 prior + 4 new).

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/diff/dep_map.py tests/test_diff_dep_map.py
git commit -m "feat(plan-4): dep_map resolver (static + glob + follow chains)"
```

---

## Task 6: Differ — diff two snapshot dicts

**Files:**
- Create: `skill_assets/proposal_build/diff/differ.py`
- Create: `tests/test_diff_differ.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_diff_differ.py
"""Tests for snapshot diffing."""
from __future__ import annotations

from proposal_build.diff.differ import diff_snapshots, ChangeReport


def _snap(brief=None, worksheet=None, renderings=None, slides_rendered=None):
    return {
        "schema_version": 1,
        "generated_at": "2026-05-13T00:00:00Z",
        "revision": 1,
        "brief": brief or {},
        "worksheet": worksheet or {},
        "renderings": renderings or {},
        "slides_rendered": slides_rendered or [],
        "outputs": {},
    }


def test_diff_no_changes():
    snap = _snap(brief={"a": "sha256:1"}, worksheet={"row.1.x": "sha256:2"})
    cr = diff_snapshots(prior=snap, current=snap)
    assert isinstance(cr, ChangeReport)
    assert cr.has_changes is False
    assert cr.brief == {}
    assert cr.worksheet == {}


def test_diff_brief_field_modified():
    prior = _snap(brief={"design_phrase": "sha256:OLD"})
    current = _snap(brief={"design_phrase": "sha256:NEW"})
    cr = diff_snapshots(prior=prior, current=current)
    assert cr.has_changes
    assert cr.brief == {"design_phrase": ("modified",)}


def test_diff_brief_field_added():
    prior = _snap(brief={"design_phrase": "sha256:A"})
    current = _snap(brief={"design_phrase": "sha256:A", "tree_comparison.recommended": "sha256:B"})
    cr = diff_snapshots(prior=prior, current=current)
    assert "tree_comparison.recommended" in cr.brief
    assert cr.brief["tree_comparison.recommended"] == ("added",)


def test_diff_brief_field_removed():
    prior = _snap(brief={"x": "sha256:1", "y": "sha256:2"})
    current = _snap(brief={"x": "sha256:1"})
    cr = diff_snapshots(prior=prior, current=current)
    assert cr.brief["y"] == ("removed",)


def test_diff_worksheet_cell_modified():
    prior = _snap(worksheet={"row.30.rental_high": "sha256:OLD"})
    current = _snap(worksheet={"row.30.rental_high": "sha256:NEW"})
    cr = diff_snapshots(prior=prior, current=current)
    assert cr.worksheet["row.30.rental_high"] == ("modified",)


def test_diff_rendering_added():
    prior = _snap(renderings={})
    current = _snap(renderings={"Base Scope/22_new.png": "sha256:N"})
    cr = diff_snapshots(prior=prior, current=current)
    assert cr.renderings["Base Scope/22_new.png"] == ("added",)


def test_diff_slide_added_to_render_list():
    prior = _snap(slides_rendered=[{"layout": "cover", "page": 1}])
    current = _snap(slides_rendered=[
        {"layout": "cover", "page": 1},
        {"layout": "tree_comparison", "page": 12},
    ])
    cr = diff_snapshots(prior=prior, current=current)
    assert "tree_comparison" in cr.slides_added
```

- [ ] **Step 2: Run test to verify it fails**

```
python -m pytest tests/test_diff_differ.py -v -p no:warnings
```

Expected: ImportError.

- [ ] **Step 3: Implement**

```python
# skill_assets/proposal_build/diff/differ.py
"""Compare two last_run.json snapshots and compute the change report."""
from __future__ import annotations

from dataclasses import dataclass, field
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
        worksheet=_diff_hash_dict(prior.get("worksheet", {}), current.get("worksheet", {})),
        renderings=_diff_hash_dict(prior.get("renderings", {}), current.get("renderings", {})),
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
```

- [ ] **Step 4: Run test to verify it passes**

```
python -m pytest tests/test_diff_differ.py -v -p no:warnings
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/diff/differ.py tests/test_diff_differ.py
git commit -m "feat(plan-4): differ — compare two snapshots, classify add/remove/modify"
```

---

## Task 7: Affected-slides computation

**Files:**
- Modify: `skill_assets/proposal_build/diff/differ.py`
- Modify: `tests/test_diff_differ.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_diff_differ.py`:

```python
from proposal_build.diff.dep_map import (
    DepMap, SlideEntry, BriefEntry, WorksheetEntry, FollowEntry,
)
from proposal_build.diff.differ import compute_affected_slides


def _slide_entry(brief_paths=(), worksheet_patterns=()):
    return SlideEntry(
        brief=tuple(BriefEntry(p, p) for p in brief_paths),
        worksheet=tuple(WorksheetEntry(p, p) for p in worksheet_patterns),
        renderings=(), follow=(),
    )


def test_affected_slides_brief_path_change():
    dep_map = DepMap(
        schema_version=1,
        slides={
            "cover": _slide_entry(brief_paths=("client_name",)),
            "tree_comparison": _slide_entry(brief_paths=("tree_comparison.recommended",)),
        },
        itemized_pricing_pdf=None,
        customer_workbook_xlsx=None,
    )
    cr = ChangeReport(
        brief={"client_name": ("modified",)},
        worksheet={}, renderings={},
        slides_added=frozenset(), slides_removed=frozenset(),
    )
    affected = compute_affected_slides(
        cr, dep_map,
        brief_flat={"client_name": "Acme", "tree_comparison.recommended": "tree_50"},
        worksheet_hashes={},
        rendered_slides=("cover", "tree_comparison"),
    )
    assert "cover" in affected
    assert "tree_comparison" not in affected


def test_affected_slides_worksheet_pattern_match():
    dep_map = DepMap(
        schema_version=1,
        slides={
            "rom_investment": _slide_entry(worksheet_patterns=("row.*.rental_high",)),
            "cover": _slide_entry(brief_paths=("client_name",)),
        },
        itemized_pricing_pdf=None,
        customer_workbook_xlsx=None,
    )
    cr = ChangeReport(
        brief={}, worksheet={"row.30.rental_high": ("modified",)},
        renderings={}, slides_added=frozenset(), slides_removed=frozenset(),
    )
    affected = compute_affected_slides(
        cr, dep_map,
        brief_flat={"client_name": "Acme"},
        worksheet_hashes={"row.30.rental_high": "sha256:x"},
        rendered_slides=("cover", "rom_investment"),
    )
    assert "rom_investment" in affected
    assert "cover" not in affected


def test_affected_slides_only_includes_rendered():
    """Slides not in this run's slides_rendered list shouldn't appear."""
    dep_map = DepMap(
        schema_version=1,
        slides={
            "tree_comparison": _slide_entry(brief_paths=("tree_comparison.recommended",)),
        },
        itemized_pricing_pdf=None, customer_workbook_xlsx=None,
    )
    cr = ChangeReport(
        brief={"tree_comparison.recommended": ("modified",)},
        worksheet={}, renderings={},
        slides_added=frozenset(), slides_removed=frozenset(),
    )
    affected = compute_affected_slides(
        cr, dep_map, brief_flat={"tree_comparison.recommended": "tree_50"},
        worksheet_hashes={},
        rendered_slides=(),  # nothing rendered this run
    )
    assert affected == set()
```

- [ ] **Step 2: Run test to verify it fails**

```
python -m pytest tests/test_diff_differ.py -v -p no:warnings
```

Expected: ImportError for `compute_affected_slides`.

- [ ] **Step 3: Implement**

Append to `skill_assets/proposal_build/diff/differ.py`:

```python
from proposal_build.diff.dep_map import DepMap, resolve_slide_deps


def compute_affected_slides(
    change_report: ChangeReport,
    dep_map: DepMap,
    brief_flat: dict,
    worksheet_hashes: dict[str, str],
    rendered_slides: tuple[str, ...],
) -> set[str]:
    """Cross-reference change_report against dep_map to produce the set of
    rendered-slide names whose inputs changed."""
    changed_brief_paths = set(change_report.brief)
    changed_worksheet_keys = set(change_report.worksheet)

    affected: set[str] = set()
    for slide_name in rendered_slides:
        entry = dep_map.slides.get(slide_name)
        if entry is None:
            continue
        deps = resolve_slide_deps(entry, brief_flat, worksheet_hashes)
        if deps.brief & changed_brief_paths:
            affected.add(slide_name)
            continue
        if deps.worksheet & changed_worksheet_keys:
            affected.add(slide_name)
            continue
    return affected
```

- [ ] **Step 4: Run test to verify it passes**

```
python -m pytest tests/test_diff_differ.py -v -p no:warnings
```

Expected: 10 passed (7 prior + 3 new).

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/diff/differ.py tests/test_diff_differ.py
git commit -m "feat(plan-4): compute_affected_slides — cross-ref diff with dep_map"
```

---

## Task 8: Snapshot writer + reader with schema_version handling

**Files:**
- Create: `skill_assets/proposal_build/diff/snapshot.py`
- Create: `tests/test_diff_snapshot.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_diff_snapshot.py
"""Tests for last_run.json read/write + schema handling."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from proposal_build.diff.snapshot import (
    write_snapshot, read_snapshot, SnapshotError, SUPPORTED_SCHEMA_VERSIONS,
)


def test_write_then_read_roundtrip(tmp_path: Path):
    payload = {
        "schema_version": 1,
        "generated_at": "2026-05-14T18:00:00Z",
        "revision": 2,
        "brief": {"design_phrase": "sha256:abc"},
        "worksheet": {"row.20.rental_low": "sha256:def"},
        "renderings": {},
        "slides_rendered": [{"layout": "cover", "page": 1}],
        "outputs": {"deck_pdf": "sha256:ghi"},
    }
    path = tmp_path / "last_run.json"
    write_snapshot(path, payload)

    loaded = read_snapshot(path)
    assert loaded["revision"] == 2
    assert loaded["brief"]["design_phrase"] == "sha256:abc"


def test_read_missing_returns_none(tmp_path: Path):
    assert read_snapshot(tmp_path / "missing.json") is None


def test_read_schema_version_mismatch(tmp_path: Path):
    path = tmp_path / "last_run.json"
    path.write_text(json.dumps({"schema_version": 99}))
    with pytest.raises(SnapshotError, match="schema_version"):
        read_snapshot(path)


def test_read_malformed_backs_up_and_returns_none(tmp_path: Path):
    path = tmp_path / "last_run.json"
    path.write_text("{ this is not valid json")
    result = read_snapshot(path)
    assert result is None
    # Backup file should exist alongside.
    backups = list(tmp_path.glob("last_run.json.broken-*"))
    assert len(backups) == 1


def test_supported_schema_versions_includes_1():
    assert 1 in SUPPORTED_SCHEMA_VERSIONS
```

- [ ] **Step 2: Run test to verify it fails**

```
python -m pytest tests/test_diff_snapshot.py -v -p no:warnings
```

Expected: ImportError.

- [ ] **Step 3: Implement**

```python
# skill_assets/proposal_build/diff/snapshot.py
"""Read + write last_run.json. Handles schema_version + corruption."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


SUPPORTED_SCHEMA_VERSIONS = {1}


class SnapshotError(Exception):
    """Raised on schema_version mismatch or other unrecoverable problems."""


def write_snapshot(path: Path, payload: dict) -> None:
    """Atomically write a snapshot JSON to path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def read_snapshot(path: Path) -> dict | None:
    """Read last_run.json. Returns None if file is missing OR malformed (after
    backing up the malformed file). Raises SnapshotError on schema_version
    mismatch (recoverable schema mismatches are intentionally surfaced rather
    than swallowed)."""
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
    except (OSError, json.JSONDecodeError):
        # Back up the unreadable file, return None (caller treats as first run).
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = path.with_suffix(path.suffix + f".broken-{ts}")
        try:
            path.rename(backup)
        except OSError:
            pass
        return None

    version = data.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise SnapshotError(
            f"last_run.json schema_version={version!r} not supported "
            f"(supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)}). "
            f"Delete the file to regenerate from scratch, or run a migration."
        )
    return data
```

- [ ] **Step 4: Run test to verify it passes**

```
python -m pytest tests/test_diff_snapshot.py -v -p no:warnings
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/diff/snapshot.py tests/test_diff_snapshot.py
git commit -m "feat(plan-4): snapshot read/write with schema_version + corruption handling"
```

---

## Task 9: Change-summary text generator

**Files:**
- Create: `skill_assets/proposal_build/diff/summary.py`
- Create: `tests/test_diff_summary.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_diff_summary.py
"""Tests for change_summary.md generation."""
from __future__ import annotations

from proposal_build.diff.dep_map import (
    DepMap, SlideEntry, BriefEntry, WorksheetEntry,
)
from proposal_build.diff.differ import ChangeReport
from proposal_build.diff.summary import (
    render_change_summary, render_initial_summary,
)


def _dep_map_with_labels():
    return DepMap(
        schema_version=1,
        slides={
            "tree_comparison": SlideEntry(
                brief=(
                    BriefEntry(path="tree_comparison.recommended",
                               human_label="Recommended tree size"),
                ),
                worksheet=(), renderings=(), follow=(),
            ),
            "rom_investment": SlideEntry(
                brief=(),
                worksheet=(WorksheetEntry(pattern="row.*.rental_high",
                                          human_label="Annual rental high"),),
                renderings=(), follow=(),
            ),
        },
        itemized_pricing_pdf=None, customer_workbook_xlsx=None,
    )


def test_render_initial_summary():
    text = render_initial_summary(
        client_name="FIGat7th DTLA",
        revision=1,
        generated_at="2026-05-14",
    )
    assert "Revision 1" in text
    assert "FIGat7th DTLA" in text
    assert "Initial revision" in text


def test_render_change_summary_includes_brief_bullet():
    cr = ChangeReport(
        brief={"tree_comparison.recommended": ("modified",)},
        worksheet={}, renderings={},
        slides_added=frozenset(), slides_removed=frozenset(),
    )
    text = render_change_summary(
        client_name="FIGat7th DTLA",
        revision=2,
        prior_revision=1,
        prior_generated_at="2026-05-13",
        current_generated_at="2026-05-14",
        change_report=cr,
        affected_slides={"tree_comparison"},
        dep_map=_dep_map_with_labels(),
    )
    assert "Revision 2" in text
    assert "Recommended tree size" in text


def test_render_change_summary_falls_back_to_path_when_label_missing():
    cr = ChangeReport(
        brief={"unknown_field": ("modified",)},
        worksheet={}, renderings={},
        slides_added=frozenset(), slides_removed=frozenset(),
    )
    text = render_change_summary(
        client_name="X", revision=2, prior_revision=1,
        prior_generated_at="2026-05-13", current_generated_at="2026-05-14",
        change_report=cr, affected_slides=set(),
        dep_map=_dep_map_with_labels(),
    )
    assert "unknown_field" in text  # bare path fallback


def test_render_change_summary_no_em_dashes():
    """Customer-facing copy must not contain em dashes (per feedback)."""
    cr = ChangeReport(
        brief={"tree_comparison.recommended": ("modified",)},
        worksheet={}, renderings={},
        slides_added=frozenset(), slides_removed=frozenset(),
    )
    text = render_change_summary(
        client_name="X", revision=2, prior_revision=1,
        prior_generated_at="2026-05-13", current_generated_at="2026-05-14",
        change_report=cr, affected_slides={"tree_comparison"},
        dep_map=_dep_map_with_labels(),
    )
    # Section above the "---" separator is customer-facing; below is internal.
    customer_section = text.split("---")[1] if "---" in text else text
    assert "—" not in customer_section, "em dash found in customer-facing section"
```

- [ ] **Step 2: Run test to verify it fails**

```
python -m pytest tests/test_diff_summary.py -v -p no:warnings
```

Expected: ImportError.

- [ ] **Step 3: Implement**

```python
# skill_assets/proposal_build/diff/summary.py
"""Generate change_summary.md text from a ChangeReport."""
from __future__ import annotations

import logging

from proposal_build.diff.dep_map import DepMap
from proposal_build.diff.differ import ChangeReport


logger = logging.getLogger(__name__)


def render_initial_summary(client_name: str, revision: int, generated_at: str) -> str:
    """Render the change_summary.md text for a first run (no prior to compare)."""
    return (
        f"# {client_name} Revision {revision} Change Summary\n"
        f"\n"
        f"**Generated:** {generated_at}\n"
        f"\n"
        f"---\n"
        f"\n"
        f"## Initial revision\n"
        f"\n"
        f"This is the first version generated for this proposal. No prior\n"
        f"revision exists to compare against.\n"
    )


def render_change_summary(
    *,
    client_name: str,
    revision: int,
    prior_revision: int,
    prior_generated_at: str,
    current_generated_at: str,
    change_report: ChangeReport,
    affected_slides: set[str],
    dep_map: DepMap,
) -> str:
    """Render the change_summary.md body for a subsequent run."""
    label_index = _build_label_index(dep_map)
    bullets = _bullets_for(change_report, label_index)

    affected_list = ", ".join(sorted(affected_slides)) or "none"

    return (
        f"# {client_name} Revision {revision} Change Summary\n"
        f"\n"
        f"**Generated:** {current_generated_at}\n"
        f"**Previous revision:** v{prior_revision} ({prior_generated_at})\n"
        f"\n"
        f"> Copy the section below into your customer email body.\n"
        f"\n"
        f"---\n"
        f"\n"
        f"## Changes since revision {prior_revision}\n"
        f"\n"
        + ("\n".join(bullets) if bullets else "_No customer-visible changes._\n")
        + "\n"
        f"\n"
        f"---\n"
        f"\n"
        f"*Internal: affected slides this round: {affected_list}.*\n"
    )


def _build_label_index(dep_map: DepMap) -> dict[str, str]:
    """Flatten all brief/worksheet entries from the dep_map into a single
    {path_or_pattern -> human_label} index."""
    out: dict[str, str] = {}
    for entry in dep_map.slides.values():
        for b in entry.brief:
            if b.human_label and b.path not in out:
                out[b.path] = b.human_label
        for w in entry.worksheet:
            if w.human_label and w.pattern not in out:
                out[w.pattern] = w.human_label
    return out


def _bullets_for(cr: ChangeReport, labels: dict[str, str]) -> list[str]:
    bullets: list[str] = []
    for path, (kind,) in sorted(cr.brief.items()):
        label = _label_for_path(path, labels)
        if label is None:
            logger.warning("No human_label for brief path %r in dependency_map.yaml", path)
            label = path
        bullets.append(f"- **{label}:** {kind}")
    for key, (kind,) in sorted(cr.worksheet.items()):
        label = _label_for_path(key, labels)
        if label is None:
            label = key
        bullets.append(f"- **{label}:** {kind} ({key})")
    for path, (kind,) in sorted(cr.renderings.items()):
        bullets.append(f"- **Rendering {kind}:** {path}")
    return bullets


def _label_for_path(path: str, labels: dict[str, str]) -> str | None:
    """Resolve a label by exact match or by matching a glob pattern key."""
    import fnmatch
    if path in labels:
        return labels[path]
    for pattern, label in labels.items():
        if "*" in pattern and fnmatch.fnmatch(path, pattern):
            return label
    return None
```

- [ ] **Step 4: Run test to verify it passes**

```
python -m pytest tests/test_diff_summary.py -v -p no:warnings
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/diff/summary.py tests/test_diff_summary.py
git commit -m "feat(plan-4): change_summary.md text generation with human_label support"
```

---

## Task 10: Revisions folder copier + counter

**Files:**
- Create: `skill_assets/proposal_build/diff/revisions.py`
- Create: `tests/test_diff_revisions.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_diff_revisions.py
"""Tests for revisions/v<n>/ archival."""
from __future__ import annotations

from pathlib import Path

from proposal_build.diff.revisions import copy_to_revision, next_revision_number


def _make_artifacts(tmp: Path) -> dict[str, Path]:
    notes = tmp / "04 - Process & Notes"
    output = tmp / "05 - Output"
    pricing = tmp / "03 - Scope & Pricing"
    notes.mkdir(parents=True)
    output.mkdir(parents=True)
    pricing.mkdir(parents=True)
    deck = output / "deck.pdf"
    deck.write_bytes(b"deck content")
    itemized = pricing / "itemized.pdf"
    itemized.write_bytes(b"itemized content")
    workbook = pricing / "workbook.xlsx"
    workbook.write_bytes(b"workbook content")
    summary = output / "change_summary.md"
    summary.write_text("# summary\n")
    last_run = notes / "last_run.json"
    last_run.write_text('{"schema_version": 1}')
    return {
        "notes_dir": notes,
        "deck": deck, "itemized": itemized, "workbook": workbook,
        "summary": summary, "last_run": last_run,
    }


def test_next_revision_number_when_no_revisions_dir(tmp_path: Path):
    notes = tmp_path / "04 - Process & Notes"
    notes.mkdir()
    assert next_revision_number(notes) == 1


def test_next_revision_number_with_existing_revisions(tmp_path: Path):
    notes = tmp_path / "04 - Process & Notes"
    (notes / "revisions" / "v1").mkdir(parents=True)
    (notes / "revisions" / "v3").mkdir(parents=True)
    (notes / "revisions" / "v2").mkdir(parents=True)
    assert next_revision_number(notes) == 4


def test_copy_to_revision_creates_v1_folder(tmp_path: Path):
    a = _make_artifacts(tmp_path)
    copy_to_revision(
        notes_dir=a["notes_dir"], revision=1,
        deck=a["deck"], itemized=a["itemized"],
        workbook=a["workbook"], change_summary=a["summary"],
        last_run_json=a["last_run"],
    )
    v1 = a["notes_dir"] / "revisions" / "v1"
    assert (v1 / "deck.pdf").read_bytes() == b"deck content"
    assert (v1 / "itemized.pdf").read_bytes() == b"itemized content"
    assert (v1 / "workbook.xlsx").read_bytes() == b"workbook content"
    assert (v1 / "change_summary.md").exists()
    assert (v1 / "last_run.json").exists()


def test_copy_to_revision_overwrites_existing(tmp_path: Path):
    a = _make_artifacts(tmp_path)
    v2 = a["notes_dir"] / "revisions" / "v2"
    v2.mkdir(parents=True)
    (v2 / "deck.pdf").write_bytes(b"stale")
    copy_to_revision(
        notes_dir=a["notes_dir"], revision=2,
        deck=a["deck"], itemized=a["itemized"],
        workbook=a["workbook"], change_summary=a["summary"],
        last_run_json=a["last_run"],
    )
    assert (v2 / "deck.pdf").read_bytes() == b"deck content"
```

- [ ] **Step 2: Run test to verify it fails**

```
python -m pytest tests/test_diff_revisions.py -v -p no:warnings
```

Expected: ImportError.

- [ ] **Step 3: Implement**

```python
# skill_assets/proposal_build/diff/revisions.py
"""Copy outputs into 04 - Process & Notes/revisions/v<n>/ after each render."""
from __future__ import annotations

import re
import shutil
from pathlib import Path


REVISION_DIR_NAME = "revisions"
REVISION_FOLDER_PATTERN = re.compile(r"^v(\d+)$")


def next_revision_number(notes_dir: Path) -> int:
    """Return the next integer N such that revisions/v<N> does not yet exist.

    If revisions/ doesn't exist, returns 1.
    """
    revisions_dir = notes_dir / REVISION_DIR_NAME
    if not revisions_dir.exists():
        return 1
    used = []
    for child in revisions_dir.iterdir():
        if child.is_dir():
            m = REVISION_FOLDER_PATTERN.match(child.name)
            if m:
                used.append(int(m.group(1)))
    return (max(used) + 1) if used else 1


def copy_to_revision(
    *,
    notes_dir: Path,
    revision: int,
    deck: Path | None,
    itemized: Path | None,
    workbook: Path | None,
    change_summary: Path | None,
    last_run_json: Path | None,
) -> Path:
    """Copy the listed outputs into notes_dir/revisions/v<revision>/.

    Existing files at the destination are overwritten. Missing source files
    are silently skipped (intentional — some outputs are optional per mode).
    Returns the path to the revision folder.
    """
    dest = notes_dir / REVISION_DIR_NAME / f"v{revision}"
    dest.mkdir(parents=True, exist_ok=True)
    for src, name in [
        (deck, "deck.pdf"),
        (itemized, "itemized.pdf"),
        (workbook, "workbook.xlsx"),
        (change_summary, "change_summary.md"),
        (last_run_json, "last_run.json"),
    ]:
        if src is not None and src.exists():
            shutil.copy2(src, dest / name)
    return dest
```

- [ ] **Step 4: Run test to verify it passes**

```
python -m pytest tests/test_diff_revisions.py -v -p no:warnings
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/diff/revisions.py tests/test_diff_revisions.py
git commit -m "feat(plan-4): revisions/v<n>/ folder copier + counter"
```

---

## Task 11: Public API surface in `diff/__init__.py`

**Files:**
- Modify: `skill_assets/proposal_build/diff/__init__.py`

- [ ] **Step 1: Re-export the public API**

Replace the contents of `skill_assets/proposal_build/diff/__init__.py`:

```python
"""Diff-mode regeneration: snapshot, dep-map, differ, change summary, revisions."""
from proposal_build.diff.hasher import (
    hash_string, hash_brief, hash_worksheet_rows, hash_file, flatten_brief,
)
from proposal_build.diff.dep_map import (
    load_dep_map, resolve_slide_deps, DepMap, DepMapError, ResolvedDeps,
    SlideEntry, BriefEntry, WorksheetEntry, FollowEntry,
)
from proposal_build.diff.differ import (
    diff_snapshots, compute_affected_slides, ChangeReport,
)
from proposal_build.diff.snapshot import (
    write_snapshot, read_snapshot, SnapshotError, SUPPORTED_SCHEMA_VERSIONS,
)
from proposal_build.diff.summary import (
    render_change_summary, render_initial_summary,
)
from proposal_build.diff.revisions import (
    copy_to_revision, next_revision_number,
)

__all__ = [
    "hash_string", "hash_brief", "hash_worksheet_rows", "hash_file", "flatten_brief",
    "load_dep_map", "resolve_slide_deps", "DepMap", "DepMapError", "ResolvedDeps",
    "SlideEntry", "BriefEntry", "WorksheetEntry", "FollowEntry",
    "diff_snapshots", "compute_affected_slides", "ChangeReport",
    "write_snapshot", "read_snapshot", "SnapshotError", "SUPPORTED_SCHEMA_VERSIONS",
    "render_change_summary", "render_initial_summary",
    "copy_to_revision", "next_revision_number",
]
```

- [ ] **Step 2: Verify all imports resolve**

```
python -c "import proposal_build.diff; print('OK')"
```

Expected: `OK`.

- [ ] **Step 3: Run full diff test suite**

```
python -m pytest tests/test_diff_*.py -v -p no:warnings
```

Expected: All previous diff tests still pass.

- [ ] **Step 4: Commit**

```bash
git add skill_assets/proposal_build/diff/__init__.py
git commit -m "feat(plan-4): public API surface for proposal_build.diff"
```

---

## Task 12: CLI plumbing — wire differ into `_do_generate`

**Files:**
- Modify: `skill_assets/proposal_build/cli.py`
- Create: `tests/test_diff_cli.py`

**Context:** The current `_do_generate` (cli.py lines 47-83) calls `build_project_model → run_validation → compose → render`. We add pre-render and post-render hooks:

- **Pre-render:** load prior `last_run.json` if exists, compute current snapshot from inputs, compute diff, print report.
- **Post-render:** if `outcome["status"] != "blocked"`, write new `last_run.json`, copy outputs to `revisions/v<n>/`, write `change_summary.md`.

The diff module needs access to the BriefData (for `hash_brief`) and a list of worksheet rows (for `hash_worksheet_rows`). The parser already produces both — see `parse_brief()` in `parser/brief.py` and `build_project_model()` in `parser/__init__.py`. The implementer may need to thread these through if not already exposed.

- [ ] **Step 1: Find the brief + worksheet handles in the existing pipeline**

Run:
```
grep -n "parse_brief\|BriefData\|read_worksheet\|read_rom_worksheet" skill_assets/proposal_build/parser/*.py | head -20
```

Make notes on where the `BriefData` and worksheet rows are created. If they're consumed inside `build_project_model` but not returned to the caller, you'll need to either:
- Add a second return value to `build_project_model` (e.g., add `raw_inputs` to the artifacts dict), or
- Call `parse_brief` directly in `_do_generate` alongside `build_project_model`.

Pick the lower-impact option — re-parsing the Brief in `_do_generate` is wasteful but isolates the change to cli.py. **Recommended:** thread it through artifacts.

- [ ] **Step 2: Write the failing test**

```python
# tests/test_diff_cli.py
"""Integration tests for the CLI's diff hooks."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from proposal_build.cli import main


FIXTURE_PROJECT = Path(__file__).resolve().parent / "fixtures" / "diff_smoke_project"
# Use the existing Riverside or a small fixture. Implementer: pick the
# cheapest one that actually exercises the full pipeline. If no such fixture
# exists yet, create a minimal copy here and check it in.


def test_first_run_writes_snapshot_and_revisions(tmp_path: Path):
    """Smoke: first generate run on a fresh project creates last_run.json + revisions/v1/."""
    project = tmp_path / "test_project"
    shutil.copytree(FIXTURE_PROJECT, project)
    rc = main(["generate", str(project)])
    assert rc == 0
    assert (project / "04 - Process & Notes" / "last_run.json").exists()
    assert (project / "04 - Process & Notes" / "revisions" / "v1" / "deck.pdf").exists()
    assert (project / "05 - Output" / "change_summary.md").exists()


def test_no_snapshot_flag_skips_snapshot(tmp_path: Path):
    project = tmp_path / "test_project"
    shutil.copytree(FIXTURE_PROJECT, project)
    rc = main(["generate", str(project), "--no-snapshot"])
    assert rc == 0
    assert not (project / "04 - Process & Notes" / "last_run.json").exists()
    assert not (project / "04 - Process & Notes" / "revisions").exists()


def test_diff_only_with_no_prior_snapshot(tmp_path: Path, capsys):
    project = tmp_path / "test_project"
    shutil.copytree(FIXTURE_PROJECT, project)
    rc = main(["generate", str(project), "--diff-only"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "no prior run" in captured.out.lower()
```

- [ ] **Step 3: Run test to verify it fails**

```
python -m pytest tests/test_diff_cli.py -v -p no:warnings
```

Expected: FAIL — fixture doesn't exist OR flags not parsed OR no snapshot writing.

- [ ] **Step 4: Create the fixture project**

Make a minimal copy of an existing test project. Easiest path: copy the menu-mode fixture data (FIGat7th's data files but stripped to ~3 slides for speed). The implementer should pick the smallest renderable fixture that exists. Goal: full pipeline runs in under 5 seconds.

```bash
mkdir -p tests/fixtures/diff_smoke_project
# Copy minimal Brief, worksheet, and renderings here.
# Use the simplest existing fixture (e.g., the synthetic menu fixture in tests/fixtures/) as a template.
```

The implementer should verify the fixture renders before continuing — run `python -m proposal_build generate tests/fixtures/diff_smoke_project` once manually.

- [ ] **Step 5: Update `cli.py` — add flags**

In `skill_assets/proposal_build/cli.py`, modify the `generate` subparser definition (around lines 21-26):

```python
    gen = sub.add_parser("generate", help="Generate a proposal for a project folder")
    gen.add_argument("project_dir", help="Path to the project folder")
    gen.add_argument("--use-latest-layouts", action="store_true",
                     help="Refresh the layout_pin.json to current versions")
    gen.add_argument("--compress", action="store_true",
                     help="Run ghostscript /ebook on output PDFs (smaller send-size).")
    gen.add_argument("--no-snapshot", action="store_true",
                     help="Skip writing last_run.json and revisions/ archive.")
    gen.add_argument("--diff-only", action="store_true",
                     help="Run differ + write change_summary.md, skip render and snapshot.")
```

And update the dispatch in `main()`:

```python
    if args.command == "generate":
        return _do_generate(
            Path(args.project_dir),
            args.use_latest_layouts,
            args.compress,
            no_snapshot=args.no_snapshot,
            diff_only=args.diff_only,
        )
```

And update `_do_generate` signature + body to accept the new flags. Implementation:

```python
def _do_generate(
    project_dir: Path,
    use_latest: bool,
    compress: bool,
    *,
    no_snapshot: bool = False,
    diff_only: bool = False,
) -> int:
    from datetime import datetime, timezone
    from proposal_build.diff import (
        load_dep_map, hash_brief, hash_worksheet_rows, hash_file,
        diff_snapshots, compute_affected_slides, flatten_brief,
        write_snapshot, read_snapshot, render_change_summary, render_initial_summary,
        copy_to_revision, next_revision_number,
    )

    try:
        model, artifacts = build_project_model(project_dir)
    except ProjectLoadError as e:
        result = ValidationResult(blockers=[("project_load", str(e))], warnings=[])
        outcome = render(project_dir, _placeholder_model(), [], [], {}, result, use_latest)
        print(f"❌ BLOCKED — {e}", file=sys.stderr)
        print(f"   See: {outcome['report']}", file=sys.stderr)
        return 1

    result = run_validation(
        model,
        eligible_renderings=artifacts["eligible_renderings"],
        referenced_filenames=artifacts["referenced_filenames"],
        per_line_sums=artifacts["per_line_sums"],
        scenarios=artifacts["scenarios"],
    )

    slides, pricing_docs = compose(model)

    # === DIFF: pre-render snapshot + change report ===
    notes_dir = project_dir / "04 - Process & Notes"
    snapshot_path = notes_dir / "last_run.json"
    prior = read_snapshot(snapshot_path)

    brief_data = artifacts.get("brief_data")  # see Step 1 — add this to artifacts
    worksheet_rows = artifacts.get("worksheet_rows", [])
    rendering_files = artifacts.get("eligible_renderings", [])

    current_brief_hashes = hash_brief(brief_data) if brief_data else {}
    current_worksheet_hashes = hash_worksheet_rows(worksheet_rows)
    current_rendering_hashes = {
        str(p.relative_to(project_dir / "02 - Renderings")): hash_file(p)
        for p in rendering_files if p.exists()
    }
    current_brief_flat = flatten_brief(brief_data) if brief_data else {}

    skill_dep_map_path = Path(__file__).resolve().parent.parent / "dependency_map.yaml"
    dep_map = load_dep_map(skill_dep_map_path)

    rendered_layout_names = tuple(s[0] for s in slides)
    rendered_slide_records = [
        {"layout": layout, "page": i + 1}
        for i, (layout, _ctx) in enumerate(slides)
    ]

    change_report = None
    affected_slides: set[str] = set()
    if prior is not None:
        current_snapshot_preview = {
            "brief": current_brief_hashes,
            "worksheet": current_worksheet_hashes,
            "renderings": current_rendering_hashes,
            "slides_rendered": rendered_slide_records,
        }
        change_report = diff_snapshots(prior=prior, current=current_snapshot_preview)
        affected_slides = compute_affected_slides(
            change_report, dep_map,
            brief_flat=current_brief_flat,
            worksheet_hashes=current_worksheet_hashes,
            rendered_slides=rendered_layout_names,
        )
        _print_change_report(change_report, affected_slides, prior)
    else:
        print("[diff] first run — no prior snapshot to compare against.")

    # === --diff-only: stop here, write summary only if prior existed ===
    if diff_only:
        if prior is None:
            print("[diff-only] no prior run to diff against; exiting.")
            return 0
        client_name = getattr(model, "client_company", None) or getattr(model, "client_short", "") or "Project"
        text = render_change_summary(
            client_name=client_name,
            revision=prior.get("revision", 0) + 1,
            prior_revision=prior.get("revision", 0),
            prior_generated_at=prior.get("generated_at", "(unknown)"),
            current_generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            change_report=change_report,
            affected_slides=affected_slides,
            dep_map=dep_map,
        )
        (project_dir / "05 - Output" / "change_summary.md").write_text(text, encoding="utf-8")
        print(f"[diff-only] wrote change_summary.md (no render performed).")
        return 0

    # === Render (unchanged from before) ===
    outcome = render(project_dir, model, slides, pricing_docs, artifacts, result,
                     use_latest, compress=compress)

    if outcome["status"] == "blocked":
        print(f"❌ BLOCKED. See: {outcome['report']}", file=sys.stderr)
        return 1

    # === Post-render: snapshot, summary, revisions ===
    if not no_snapshot:
        client_name = getattr(model, "client_company", None) or getattr(model, "client_short", "") or "Project"
        deck_pdf = next((p for p in outcome.get("pdfs", []) if "deck" in p.name.lower() or p.suffix == ".pdf"), None)
        itemized_pdf = next((p for p in outcome.get("pdfs", []) if "itemized" in p.name.lower()), None)
        workbook_xlsx = outcome.get("workbook")
        change_summary_path = project_dir / "05 - Output" / "change_summary.md"

        output_hashes = {
            "deck_pdf": hash_file(deck_pdf) if deck_pdf else None,
            "itemized_pdf": hash_file(itemized_pdf) if itemized_pdf else None,
            "workbook_xlsx": hash_file(workbook_xlsx) if workbook_xlsx else None,
        }

        revision = (prior.get("revision", 0) + 1) if prior else 1

        payload = {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "revision": revision,
            "brief": current_brief_hashes,
            "worksheet": current_worksheet_hashes,
            "renderings": current_rendering_hashes,
            "slides_rendered": rendered_slide_records,
            "outputs": output_hashes,
        }
        write_snapshot(snapshot_path, payload)

        if prior is None:
            text = render_initial_summary(
                client_name=client_name,
                revision=revision,
                generated_at=payload["generated_at"][:10],
            )
        else:
            text = render_change_summary(
                client_name=client_name,
                revision=revision,
                prior_revision=prior.get("revision", 0),
                prior_generated_at=prior.get("generated_at", "(unknown)"),
                current_generated_at=payload["generated_at"][:10],
                change_report=change_report,
                affected_slides=affected_slides,
                dep_map=dep_map,
            )
        change_summary_path.write_text(text, encoding="utf-8")

        copy_to_revision(
            notes_dir=notes_dir,
            revision=revision,
            deck=deck_pdf,
            itemized=itemized_pdf,
            workbook=workbook_xlsx,
            change_summary=change_summary_path,
            last_run_json=snapshot_path,
        )
        print(f"[snapshot] wrote last_run.json (revision {revision})")
        print(f"[snapshot] copied outputs to 04 - Process & Notes/revisions/v{revision}/")
        print(f"[summary]  wrote change_summary.md")

    print("✅ Generation complete.")
    print(f"   Coverage Report: {outcome['report']}")
    print("   Outputs:")
    for p in outcome.get("pdfs", []):
        print(f"     • {p.name}")
    return 0


def _print_change_report(cr, affected_slides, prior) -> None:
    rev = prior.get("revision", 0)
    when = prior.get("generated_at", "(unknown)")[:10]
    print(f"[diff] CHANGES SINCE LAST RUN (rev {rev}, {when}):")
    if cr.brief:
        print("       Brief:")
        for path, (kind,) in sorted(cr.brief.items()):
            print(f"         - {path}: {kind}")
    if cr.worksheet:
        print("       Worksheet:")
        for key, (kind,) in sorted(cr.worksheet.items()):
            print(f"         - {key}: {kind}")
    if cr.renderings:
        print("       Renderings:")
        for path, (kind,) in sorted(cr.renderings.items()):
            print(f"         - {path}: {kind}")
    if not (cr.brief or cr.worksheet or cr.renderings):
        print("       no input changes detected.")
    if affected_slides:
        print(f"       Affected slides ({len(affected_slides)}): {', '.join(sorted(affected_slides))}")
```

- [ ] **Step 6: Update the parser to expose brief_data + worksheet_rows in artifacts**

If `build_project_model` doesn't currently return these in artifacts, add them. Open `skill_assets/proposal_build/parser/__init__.py` and ensure the artifacts dict returned includes:

```python
artifacts["brief_data"] = brief_data   # the BriefData instance
artifacts["worksheet_rows"] = worksheet_rows  # list[dict], each with at least item_code
```

If the parser doesn't currently retain these for the caller, walk back through the parsing path and capture them. Add a test in `tests/test_parser_returns_brief_data_in_artifacts.py` covering the new contract:

```python
def test_artifacts_includes_brief_data_and_worksheet_rows():
    model, artifacts = build_project_model(FIGAT7TH_FIXTURE_PROJECT_DIR)
    from proposal_build.parser.brief import BriefData
    assert isinstance(artifacts["brief_data"], BriefData)
    assert isinstance(artifacts["worksheet_rows"], list)
    assert all("item_code" in r for r in artifacts["worksheet_rows"])
```

- [ ] **Step 7: Run all tests**

```
python -m pytest -p no:warnings 2>&1 | tail -3
```

Expected: All previous tests still pass + new CLI tests pass. Target ~275+ total.

- [ ] **Step 8: Commit**

```bash
git add skill_assets/proposal_build/cli.py skill_assets/proposal_build/parser/__init__.py tests/test_diff_cli.py tests/fixtures/diff_smoke_project/ tests/test_parser_returns_brief_data_in_artifacts.py
git commit -m "feat(plan-4): wire diff hooks into generate CLI + --no-snapshot/--diff-only flags"
```

---

## Task 13: Gitignore + AE_SOP update

**Files:**
- Modify: `.gitignore`
- Modify: `skill_assets/AE_SOP.md`

- [ ] **Step 1: Update `.gitignore`**

Append to `.gitignore`:

```
# Plan 4 — revision history archives (binary blobs, regenerated from inputs)
Projects/**/04 - Process & Notes/revisions/
```

- [ ] **Step 2: Update `AE_SOP.md`**

Find an appropriate section (probably near the existing "Coverage Report" / "Outputs" section) and append:

```markdown
## Revision Tracking (Plan 4)

After each successful `python -m proposal_build generate` run, the skill
writes three new artifacts:

- `04 - Process & Notes/last_run.json` — internal snapshot of all inputs +
  outputs, drives the next regen's change report. Do not edit by hand.
- `04 - Process & Notes/revisions/v<n>/` — automatic archive of the deck,
  itemized PDF, workbook, last_run.json, and change_summary.md at the time
  of revision N. **Gitignored** — local-only. Open in Finder to recover
  prior versions.
- `05 - Output/change_summary.md` — paste into the customer email body.
  The section above the second `---` is customer-facing; the section
  below is internal.

### Re-generating after a Brief or Worksheet edit

Just run `python -m proposal_build generate <project>` again. The terminal
will print a CHANGES SINCE LAST RUN block listing exactly what changed and
which slides are affected. Inspect it before sending to the customer.

### Flags

- `--no-snapshot` — skip writing last_run.json + revisions/. Use for
  test/throwaway renders.
- `--diff-only` — run inspector + composer + differ, write
  change_summary.md, skip render and snapshot. Use to preview what would
  change without rebuilding.

### Schema mismatch

If a future skill version bumps the snapshot schema, an old `last_run.json`
will error with instructions. Delete the file to start fresh (you lose
revision counter but no actual data).
```

- [ ] **Step 3: Verify .gitignore catches the right paths**

```bash
git check-ignore -v "Projects/Fig at 7th - 2026 - Multi-Rendering Project/04 - Process & Notes/revisions/v1/deck.pdf"
```

Expected: `.gitignore:<line>:Projects/**/04 - Process & Notes/revisions/    Projects/Fig at 7th - 2026 - Multi-Rendering Project/04 - Process & Notes/revisions/v1/deck.pdf`

- [ ] **Step 4: Commit**

```bash
git add .gitignore skill_assets/AE_SOP.md
git commit -m "docs(plan-4): gitignore revisions/ + AE_SOP revision tracking section"
```

---

## Task 14: End-to-end integration test

**Files:**
- Create: `tests/test_diff_integration.py`

- [ ] **Step 1: Write the integration test**

```python
# tests/test_diff_integration.py
"""End-to-end: run generate twice on a fixture project, assert diff behavior."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from proposal_build.cli import main


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "diff_smoke_project"


def test_run_twice_with_brief_edit_in_between(tmp_path: Path, capsys):
    project = tmp_path / "p"
    shutil.copytree(FIXTURE, project)

    # First run: no prior snapshot, creates v1.
    rc = main(["generate", str(project)])
    assert rc == 0
    last_run_path = project / "04 - Process & Notes" / "last_run.json"
    assert last_run_path.exists()
    v1 = project / "04 - Process & Notes" / "revisions" / "v1"
    assert v1.exists()
    first = json.loads(last_run_path.read_text())
    assert first["revision"] == 1

    # Modify the brief — change design_phrase or whatever field the fixture has.
    brief_path = next((project / "04 - Process & Notes").glob("*Project Brief*.md"), None)
    if brief_path is None:
        # Fixture may put Brief elsewhere — adapt if needed.
        brief_path = next(project.rglob("Project Brief.md"), None)
    assert brief_path is not None, "couldn't find Project Brief.md in fixture"
    text = brief_path.read_text()
    text = text.replace("Modern Magic", "Modern Magic — Refined")  # any field tweak
    brief_path.write_text(text)

    # Second run: should detect the change and write v2.
    rc = main(["generate", str(project)])
    assert rc == 0
    second = json.loads(last_run_path.read_text())
    assert second["revision"] == 2

    v2 = project / "04 - Process & Notes" / "revisions" / "v2"
    assert v2.exists()
    assert (v2 / "change_summary.md").exists()
    summary_text = (project / "05 - Output" / "change_summary.md").read_text()
    assert "Revision 2" in summary_text


def test_run_twice_with_no_changes_does_not_bump_revision(tmp_path: Path):
    project = tmp_path / "p"
    shutil.copytree(FIXTURE, project)

    main(["generate", str(project)])
    first_text = (project / "04 - Process & Notes" / "last_run.json").read_text()
    first_revision = json.loads(first_text)["revision"]

    main(["generate", str(project)])
    second_revision = json.loads(
        (project / "04 - Process & Notes" / "last_run.json").read_text()
    )["revision"]

    # Per spec §7 no-changes case: revision counter does NOT increment.
    assert second_revision == first_revision
    # And v<first_revision+1> should NOT exist.
    assert not (project / "04 - Process & Notes" / "revisions" / f"v{first_revision + 1}").exists()
```

- [ ] **Step 2: Run the test**

```
python -m pytest tests/test_diff_integration.py -v -p no:warnings
```

Expected: both pass.

If `test_run_twice_with_no_changes_does_not_bump_revision` fails, the CLI logic from Task 12 needs adjustment: when `prior is not None` and the differ produces no changes, do NOT bump the revision counter and do NOT create a new revisions folder. Add that branch to `_do_generate`:

```python
    if prior is not None and change_report is not None and not change_report.has_changes:
        # No-changes case per spec §7. Update generated_at only; skip everything else.
        no_change_payload = {**prior, "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        if not no_snapshot:
            write_snapshot(snapshot_path, no_change_payload)
            (project_dir / "05 - Output" / "change_summary.md").write_text(
                f"# {client_name} — no changes since revision {prior.get('revision')}\n",
                encoding="utf-8",
            )
            print(f"[snapshot] no input changes since rev {prior.get('revision')}; revision counter not bumped.")
        # Skip render? No — caller asked for a regen; rebuild outputs but no snapshot bump.
        # (Continue to render below.)
```

Place this branch just before the existing render call, after the change_report is computed.

- [ ] **Step 3: Commit**

```bash
git add tests/test_diff_integration.py skill_assets/proposal_build/cli.py
git commit -m "test(plan-4): end-to-end integration test (run twice, brief edit, no-change case)"
```

---

## Task 15: Final verification + plan-4 status note

**Files:**
- Modify: `docs/superpowers/plans/2026-05-14-04-diff-mode-regeneration.md` (this file — mark complete)

- [ ] **Step 1: Run the full test suite**

```
python -m pytest -p no:warnings 2>&1 | tail -3
```

Expected: 280+ passed, 0 failed. (Baseline before Plan 4 was 251.)

- [ ] **Step 2: Smoke test against a real project**

Pick FIGat7th (largest exercise). Run:

```bash
python -m proposal_build generate "Projects/Fig at 7th - 2026 - Multi-Rendering Project"
```

Expected output:
- `[diff] first run — no prior snapshot to compare against.`
- ✅ Generation complete.
- `[snapshot] wrote last_run.json (revision 1)`
- `[snapshot] copied outputs to 04 - Process & Notes/revisions/v1/`

Verify by hand:
- `04 - Process & Notes/last_run.json` exists, has schema_version=1
- `04 - Process & Notes/revisions/v1/` contains deck.pdf + itemized.pdf + workbook.xlsx + change_summary.md + last_run.json
- `05 - Output/change_summary.md` says "Initial revision"

Then run it again with no changes:

```bash
python -m proposal_build generate "Projects/Fig at 7th - 2026 - Multi-Rendering Project"
```

Expected: `[snapshot] no input changes since rev 1; revision counter not bumped.`

Then modify any Brief field (e.g., proposal_date) and run again:

```bash
python -m proposal_build generate "Projects/Fig at 7th - 2026 - Multi-Rendering Project"
```

Expected: terminal shows CHANGES SINCE LAST RUN block listing the modified field, `revisions/v2/` is created, `change_summary.md` has a bullet.

- [ ] **Step 3: Verify gitignore**

```bash
git status -s | grep "revisions/" || echo "revisions/ correctly gitignored"
```

Expected: `revisions/ correctly gitignored`.

- [ ] **Step 4: Commit final smoke note**

```bash
git commit --allow-empty -m "chore(plan-4): plan-4 verification — diff-mode regeneration shipped

End-to-end smoke verified on FIGat7th:
- First run wrote last_run.json + revisions/v1/
- No-change re-run did not bump revision counter
- Brief edit triggered change report + revisions/v2/
- Full suite 280+ tests passing
- revisions/ correctly gitignored

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## After execution

Once all tasks are checked off:

1. Run `superpowers:finishing-a-development-branch` to choose how to merge.
2. Update memory:
   - `project_proposal_builder.md` — mark Plan 4 shipped
   - Update `MEMORY.md` index line for Plan 4
3. Consider opening a PR for review, or merge directly to main per past pattern.
