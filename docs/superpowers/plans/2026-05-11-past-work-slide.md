# Past Work Slide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the `sample_of_work` slide — a 6-tile image grid of prior-season installations — to both tiered and menu proposal modes.

**Architecture:** A new `sample_of_work.html` layout renders a 3×2 grid from a Brief-supplied list of project IDs. Each ID resolves to a `{id}.md` + `{id}.jpg` pair in `skill_assets/past_work_library/` (which ships empty; Daniel curates). The composer skips the slide when `sample_work:` is absent. The inspector enforces "exactly 6 IDs, all resolvable" when present.

**Tech Stack:** Python 3.11+, Jinja2 + WeasyPrint, pytest, PyMuPDF (fitz), python-frontmatter.

**Spec:** `docs/superpowers/specs/2026-05-11-past-work-slide-design.md`

---

## File Structure

### New files

| Path | Responsibility |
|---|---|
| `skill_assets/layouts/sample_of_work.html` | The slide template (extends `base.html`, light theme + footer) |
| `tests/fixtures/past_work_library/fixture_a.md` … `fixture_f.md` | 6 synthetic frontmatter-only entries for tests |
| `tests/fixtures/past_work_library/fixture_a.jpg` … `fixture_f.jpg` | 6 tiny placeholder images |
| `tests/fixtures/past_work_library/__init__.py` | Empty — makes it importable for path resolution |

### Modified files

| Path | Change |
|---|---|
| `skill_assets/proposal_build/models.py` | Add `sample_work: Tuple[str, ...]` to `ProjectModel` and `MenuProjectModel` |
| `skill_assets/proposal_build/parser/__init__.py` | Read `sample_work` from Brief frontmatter into `ProjectModel` |
| `skill_assets/proposal_build/parser/menu_resolver.py` | Read `sample_work` for menu mode |
| `skill_assets/proposal_build/composer/__init__.py` | Load past-work entries; dispatch `sample_of_work` slide (tiered) |
| `skill_assets/proposal_build/composer/menu_compose.py` | Same dispatch for menu mode |
| `skill_assets/proposal_build/composer/ctx_builders.py` | New `build_sample_of_work_ctx` |
| `skill_assets/proposal_build/inspector/brief.py` | Three new findings (wrong count, unknown ID, missing image) |
| `skill_assets/AE_SOP.md` | Append "Past Work slide" section with curation rules |
| `tests/test_layouts.py` | Add `sample_of_work` render case |
| `tests/test_parser_brief.py` | Add `sample_work:` parsing tests |
| `tests/test_inspector_brief.py` | Add three inspector findings tests |
| `tests/fixtures/riverside.py` | Add `sample_of_work_ctx` for the layout render test |

---

## Task Sequence

Tasks are ordered so each one's tests pass on green commits. Run `pytest -q` after each task as a smoke check.

---

### Task 1: Synthetic past-work fixture library

**Files:**
- Create: `tests/fixtures/past_work_library/__init__.py`
- Create: `tests/fixtures/past_work_library/fixture_a.md` … `fixture_f.md`
- Create: `tests/fixtures/past_work_library/fixture_a.jpg` … `fixture_f.jpg`

These exist only in `tests/` — they never ship in the skill bundle and use obviously-synthetic names so no fictional customer ever lands in `skill_assets/`.

- [ ] **Step 1: Create the directory and `__init__.py`**

```bash
mkdir -p tests/fixtures/past_work_library
touch tests/fixtures/past_work_library/__init__.py
```

- [ ] **Step 2: Create the 6 frontmatter `.md` files**

Each file is frontmatter only — no body. Pattern: `Sample Project {letter}` / `Sample City, {AA}` / years 2022–2024.

`tests/fixtures/past_work_library/fixture_a.md`:
```yaml
---
id: fixture_a
name: "Sample Project A"
location: "Sample City, AA"
year: 2024
---
```

`tests/fixtures/past_work_library/fixture_b.md`:
```yaml
---
id: fixture_b
name: "Sample Project B"
location: "Sample City, BB"
year: 2024
---
```

`tests/fixtures/past_work_library/fixture_c.md`:
```yaml
---
id: fixture_c
name: "Sample Project C"
location: "Sample City, CC"
year: 2023
---
```

`tests/fixtures/past_work_library/fixture_d.md`:
```yaml
---
id: fixture_d
name: "Sample Project D"
location: "Sample City, DD"
year: 2023
---
```

`tests/fixtures/past_work_library/fixture_e.md`:
```yaml
---
id: fixture_e
name: "Sample Project E"
location: "Sample City, EE"
year: 2022
---
```

`tests/fixtures/past_work_library/fixture_f.md`:
```yaml
---
id: fixture_f
name: "Sample Project F"
location: "Sample City, FF"
year: 2022
---
```

- [ ] **Step 3: Create the 6 tiny placeholder images**

Generate 100×100 solid-color JPGs (any tool — PIL is already a dep transitively, or use ImageMagick). Each gets a distinct fill color so visual inspection of the rendered PDF shows 6 different tiles.

```bash
python3 - <<'PY'
from PIL import Image
from pathlib import Path
colors = [(43,74,111),(111,74,43),(43,111,74),(111,43,74),(74,43,111),(111,111,43)]
out = Path("tests/fixtures/past_work_library")
for letter, rgb in zip("abcdef", colors):
    Image.new("RGB", (100, 100), rgb).save(out / f"fixture_{letter}.jpg", "JPEG", quality=80)
PY
ls tests/fixtures/past_work_library/*.jpg
```

Expected output:
```
tests/fixtures/past_work_library/fixture_a.jpg
tests/fixtures/past_work_library/fixture_b.jpg
tests/fixtures/past_work_library/fixture_c.jpg
tests/fixtures/past_work_library/fixture_d.jpg
tests/fixtures/past_work_library/fixture_e.jpg
tests/fixtures/past_work_library/fixture_f.jpg
```

- [ ] **Step 4: Commit**

```bash
git add tests/fixtures/past_work_library/
git commit -m "$(cat <<'EOF'
test(plan-10): synthetic past_work_library fixture (6 entries, 6 jpgs)

All entries use 'Sample Project X / Sample City, XX' — no fictional
customer names ever land in tests/. Production skill_assets/past_work_library/
remains empty; Daniel curates that out-of-band.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Add `sample_work` field to `ProjectModel` and `MenuProjectModel`

**Files:**
- Modify: `skill_assets/proposal_build/models.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_models.py`:

```python
def test_project_model_has_sample_work_field():
    """ProjectModel exposes sample_work as an empty tuple by default."""
    from proposal_build.models import ProjectModel
    import dataclasses
    fields = {f.name for f in dataclasses.fields(ProjectModel)}
    assert "sample_work" in fields, (
        "ProjectModel missing sample_work field — see spec §5"
    )


def test_menu_project_model_has_sample_work_field():
    """MenuProjectModel exposes sample_work as an empty tuple by default."""
    from proposal_build.models import MenuProjectModel
    import dataclasses
    fields = {f.name for f in dataclasses.fields(MenuProjectModel)}
    assert "sample_work" in fields, (
        "MenuProjectModel missing sample_work field — see spec §5"
    )
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py::test_project_model_has_sample_work_field -v
pytest tests/test_models.py::test_menu_project_model_has_sample_work_field -v
```

Expected: both FAIL with `"sample_work" in fields` assertion failure.

- [ ] **Step 3: Add the field to both dataclasses**

In `skill_assets/proposal_build/models.py`, inside `ProjectModel`, add (place near the other optional `Tuple[str, ...]` fields like `greenery_references`):

```python
    # AE-supplied list of past_work_library project IDs. When non-empty, the
    # composer emits a sample_of_work slide. Must contain exactly 6 IDs at
    # generation time; inspector enforces. Empty tuple → slide skipped.
    sample_work: Tuple[str, ...] = ()
```

In the same file, inside `MenuProjectModel`, add at the end of the dataclass (after `what_youre_approving`):

```python
    # AE-supplied list of past_work_library project IDs. Same semantics as
    # ProjectModel.sample_work.
    sample_work: Tuple[str, ...] = ()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_models.py::test_project_model_has_sample_work_field tests/test_models.py::test_menu_project_model_has_sample_work_field -v
```

Expected: both PASS.

- [ ] **Step 5: Run the full models suite to confirm no regressions**

```bash
pytest tests/test_models.py tests/test_models_rom.py -v
```

Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/models.py tests/test_models.py
git commit -m "$(cat <<'EOF'
feat(plan-10): add sample_work field to ProjectModel + MenuProjectModel

Optional tuple of past_work_library IDs. Empty by default so existing
Briefs continue to render without the slide.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Parse `sample_work:` from Brief frontmatter (tiered mode)

**Files:**
- Modify: `skill_assets/proposal_build/parser/__init__.py`
- Test: `tests/test_parser_brief.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_parser_brief.py`:

```python
def test_brief_sample_work_absent_defaults_to_empty_tuple(tmp_path):
    """A Brief without sample_work: yields ProjectModel.sample_work == ()."""
    # Smallest path: use an existing project fixture and just confirm the field.
    # Riverside Brief doesn't list sample_work, so the parsed model's
    # sample_work should be ().
    from proposal_build.parser import build_project_model
    project_dir = (
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    model, _ = build_project_model(project_dir)
    assert model.sample_work == ()


def test_brief_sample_work_present_is_parsed_as_tuple(tmp_path, monkeypatch):
    """A Brief with sample_work: [a, b, c] yields a tuple of 3 strings."""
    # Patch a Brief on disk by copying Riverside's Brief and editing.
    import shutil
    from proposal_build.parser import build_project_model
    src = (
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    dst = tmp_path / "fake_project"
    shutil.copytree(src, dst)
    brief = dst / "04 - Process & Notes" / "Project Brief.md"
    txt = brief.read_text()
    # Inject after the first --- line of YAML
    new_yaml_line = "sample_work:\n  - fixture_a\n  - fixture_b\n  - fixture_c\n"
    # Insert before the closing --- of the frontmatter block
    parts = txt.split("---", 2)
    assert len(parts) >= 3, "Expected YAML frontmatter delimited by ---"
    parts[1] = parts[1].rstrip() + "\n" + new_yaml_line
    brief.write_text("---".join(parts))

    model, _ = build_project_model(dst)
    assert model.sample_work == ("fixture_a", "fixture_b", "fixture_c")
```

- [ ] **Step 2: Run test to verify failures**

```bash
pytest tests/test_parser_brief.py::test_brief_sample_work_absent_defaults_to_empty_tuple tests/test_parser_brief.py::test_brief_sample_work_present_is_parsed_as_tuple -v
```

Expected: first PASSES (default `()` already works from Task 2); second FAILS because the parser doesn't read the field yet.

- [ ] **Step 3: Wire the field through the parser**

In `skill_assets/proposal_build/parser/__init__.py`, inside `build_project_model`, find the `ProjectModel(` constructor call (around line 131). Add a new argument, grouped near the other `Tuple` fields:

```python
        sample_work=tuple(fm.get("sample_work") or ()),
```

Place it adjacent to `slide_plan_override=tuple(fm.get("slide_plan", ())),` so related list-from-frontmatter args stay together.

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_parser_brief.py -v -k sample_work
```

Expected: both PASS.

- [ ] **Step 5: Run the full parser suite to confirm no regressions**

```bash
pytest tests/test_parser_brief.py tests/test_parser_validate.py tests/test_parser_add_ons.py -v
```

Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/parser/__init__.py tests/test_parser_brief.py
git commit -m "$(cat <<'EOF'
feat(plan-10): parse sample_work: from Brief frontmatter (tiered)

ProjectModel.sample_work populated from the optional sample_work: list in
the Brief's YAML frontmatter. Absent or empty list → empty tuple, slide skipped.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Parse `sample_work:` for menu mode

**Files:**
- Modify: `skill_assets/proposal_build/parser/menu_resolver.py`
- Test: `tests/test_parser_brief_menu_mode.py`

- [ ] **Step 1: Read the existing menu_resolver to find the MenuProjectModel constructor**

```bash
grep -n "MenuProjectModel(" skill_assets/proposal_build/parser/menu_resolver.py
```

Note the line where the `MenuProjectModel(...)` call lives.

- [ ] **Step 2: Write the failing test**

Append to `tests/test_parser_brief_menu_mode.py`:

```python
def test_menu_brief_sample_work_absent_defaults_to_empty_tuple():
    """A menu Brief without sample_work: yields MenuProjectModel.sample_work == ()."""
    from proposal_build.parser import parse_project
    project_dir = (
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "Projects" / "FIGat7th DTLA"
    )
    model = parse_project(project_dir)
    assert model.sample_work == ()
```

- [ ] **Step 3: Run test to verify it fails**

```bash
pytest tests/test_parser_brief_menu_mode.py::test_menu_brief_sample_work_absent_defaults_to_empty_tuple -v
```

Expected: FAIL — `MenuProjectModel` got an unexpected keyword argument 'sample_work', OR the constructor call doesn't pass it. The exact failure depends on the existing resolver code path; either way the test confirms the field isn't wired.

(If the test passes because the field defaults to `()`, that's fine — proceed to Step 4 anyway so present-case parsing also works.)

- [ ] **Step 4: Wire the field into `MenuProjectModel(...)` construction**

In `skill_assets/proposal_build/parser/menu_resolver.py`, find the `MenuProjectModel(` call (Step 1 told you the line). Add this kwarg near the end of the call:

```python
        sample_work=tuple(brief.frontmatter.get("sample_work") or ()),
```

- [ ] **Step 5: Add a second test for the populated case**

Append to `tests/test_parser_brief_menu_mode.py`:

```python
def test_menu_brief_sample_work_present_is_parsed_as_tuple(tmp_path):
    """A menu Brief with sample_work: [a, b] yields a tuple of 2 strings."""
    import shutil
    from proposal_build.parser import parse_project
    src = (
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "Projects" / "FIGat7th DTLA"
    )
    dst = tmp_path / "fake_menu_project"
    shutil.copytree(src, dst)
    brief = dst / "04 - Process & Notes" / "Project Brief.md"
    txt = brief.read_text()
    parts = txt.split("---", 2)
    assert len(parts) >= 3
    parts[1] = parts[1].rstrip() + "\nsample_work:\n  - fixture_a\n  - fixture_b\n"
    brief.write_text("---".join(parts))

    model = parse_project(dst)
    assert model.sample_work == ("fixture_a", "fixture_b")
```

- [ ] **Step 6: Run the menu parser suite**

```bash
pytest tests/test_parser_brief_menu_mode.py tests/test_parser_menu_pipeline.py -v
```

Expected: all PASS.

- [ ] **Step 7: Commit**

```bash
git add skill_assets/proposal_build/parser/menu_resolver.py tests/test_parser_brief_menu_mode.py
git commit -m "$(cat <<'EOF'
feat(plan-10): parse sample_work: from Brief frontmatter (menu mode)

MenuProjectModel.sample_work populated from the same Brief field as tiered.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Past-work library loader

**Files:**
- Modify: `skill_assets/proposal_build/composer/__init__.py`
- Test: `tests/test_composer_past_work_loader.py` (NEW)

The loader resolves a list of IDs into a list of `{name, location, year, image_path}` dicts. It looks in `skill_assets/past_work_library/` by default but accepts a base-dir override so tests can point at `tests/fixtures/past_work_library/`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_composer_past_work_loader.py`:

```python
"""Tests for the composer's past_work_library loader.

The loader is exercised via a fixture library under tests/fixtures/past_work_library/.
Production skill_assets/past_work_library/ is curated by Daniel and ships empty.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_LIB = Path(__file__).resolve().parent / "fixtures" / "past_work_library"


def test_load_past_work_entries_returns_dicts_in_order():
    """Six IDs → six dicts in input order, each with name/location/year/image."""
    from proposal_build.composer import _load_past_work_entries
    ids = ["fixture_a", "fixture_b", "fixture_c", "fixture_d", "fixture_e", "fixture_f"]
    entries = _load_past_work_entries(ids, library_dir=FIXTURE_LIB)
    assert [e["name"] for e in entries] == [
        "Sample Project A", "Sample Project B", "Sample Project C",
        "Sample Project D", "Sample Project E", "Sample Project F",
    ]
    assert entries[0]["location"] == "Sample City, AA"
    assert entries[0]["year"] == 2024
    assert entries[0]["image"].endswith("fixture_a.jpg")
    # Image path is absolute (so WeasyPrint can resolve it regardless of base_url)
    assert Path(entries[0]["image"]).is_absolute()


def test_load_past_work_entries_raises_on_unknown_id(tmp_path):
    """Unknown ID → FileNotFoundError (inspector catches this earlier in practice)."""
    from proposal_build.composer import _load_past_work_entries
    with pytest.raises(FileNotFoundError):
        _load_past_work_entries(["nonexistent_id"], library_dir=FIXTURE_LIB)


def test_load_past_work_entries_uses_default_library_dir_when_omitted(tmp_path):
    """No library_dir kwarg → looks under skill_assets/past_work_library/.
    Production library is empty, so this should raise FileNotFoundError for any ID."""
    from proposal_build.composer import _load_past_work_entries
    with pytest.raises(FileNotFoundError):
        _load_past_work_entries(["fixture_a"])
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_composer_past_work_loader.py -v
```

Expected: all 3 FAIL — `_load_past_work_entries` doesn't exist yet.

- [ ] **Step 3: Implement the loader**

In `skill_assets/proposal_build/composer/__init__.py`, near the existing `CASE_STUDIES_DIR` constant (around line 23), add:

```python
PAST_WORK_LIBRARY_DIR = Path(__file__).resolve().parents[3] / "skill_assets" / "past_work_library"
```

Then add the loader function, near `_load_case_study` (around line 169):

```python
def _load_past_work_entries(ids: list[str], library_dir: Path | None = None) -> list[dict]:
    """Resolve a list of past_work_library IDs to display-ready dicts.

    Returns one dict per ID in input order:
        {"id": str, "name": str, "location": str, "year": int, "image": str}

    `image` is an absolute filesystem path to the corresponding .jpg.

    Raises FileNotFoundError if any ID lacks a matching .md file. The
    inspector catches this earlier in practice; the raise here is a
    belt-and-braces guard for unit tests that hit the loader directly.

    `library_dir` lets tests point at tests/fixtures/past_work_library/.
    Production callers omit it and use skill_assets/past_work_library/.
    """
    base = library_dir if library_dir is not None else PAST_WORK_LIBRARY_DIR
    entries: list[dict] = []
    for pid in ids:
        md_path = base / f"{pid}.md"
        if not md_path.exists():
            raise FileNotFoundError(
                f"past_work_library entry not found: {pid} (looked at {md_path})"
            )
        post = frontmatter.load(str(md_path))
        jpg_path = base / f"{pid}.jpg"
        entries.append({
            "id": pid,
            "name": post.metadata["name"],
            "location": post.metadata["location"],
            "year": int(post.metadata["year"]),
            "image": str(jpg_path.resolve()),
        })
    return entries
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_composer_past_work_loader.py -v
```

Expected: all 3 PASS.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/composer/__init__.py tests/test_composer_past_work_loader.py
git commit -m "$(cat <<'EOF'
feat(plan-10): _load_past_work_entries — resolve IDs to display dicts

Reads {id}.md frontmatter, returns name/location/year/image-path tuples
in input order. Library dir is overridable for tests; production uses
skill_assets/past_work_library/.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: `build_sample_of_work_ctx` context builder

**Files:**
- Modify: `skill_assets/proposal_build/composer/ctx_builders.py`
- Test: `tests/test_composer_past_work_loader.py` (append; same file is the natural home)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_composer_past_work_loader.py`:

```python
def test_build_sample_of_work_ctx_emits_six_tiles():
    """build_sample_of_work_ctx returns tiles in input order with full strings."""
    from proposal_build.composer.ctx_builders import build_sample_of_work_ctx
    from tests.fixtures.riverside import build_model

    model = build_model()  # Riverside ProjectModel; doesn't need to have sample_work set
    entries = [
        {"id": "fixture_a", "name": "Sample Project A",
         "location": "Sample City, AA", "year": 2024, "image": "/abs/path/a.jpg"},
        {"id": "fixture_b", "name": "Sample Project B",
         "location": "Sample City, BB", "year": 2024, "image": "/abs/path/b.jpg"},
    ]
    ctx = build_sample_of_work_ctx(model, page_num=10, page_total=14,
                                   past_work_entries=entries)
    assert ctx["page_eyebrow"] == "Sample of Our Work"
    assert ctx["page_title"] == "Recent installations"
    assert ctx["page_num"] == 10
    assert ctx["page_total"] == 14
    assert len(ctx["tiles"]) == 2
    assert ctx["tiles"][0] == {
        "name": "Sample Project A",
        "location_year": "Sample City, AA · 2024",
        "image": "/abs/path/a.jpg",
    }
```

Note this test imports `build_model` from `tests.fixtures.riverside`. Check whether that helper exists:

```bash
grep -n "^def build_model\|^build_model" tests/fixtures/riverside.py
```

If `build_model` doesn't exist, the test should instead build a minimal `ProjectModel` inline. **If `build_model` is absent, replace the import + setup lines with:**

```python
    from proposal_build.models import ProjectModel, Tier
    # Minimal model — only fields that build_sample_of_work_ctx touches need to be valid.
    model = ProjectModel(
        client_company="X", client_short="X", project_name="X", project_short="X",
        project_year=2026, project_subtitle="", proposal_type="Holiday Proposal",
        presenter_name="", presenter_title="", presenter_email="", presenter_phone="",
        proposal_date="", go_live="2026-11-15", season_end="2027-01-10",
        fabrication_lock="2026-08-22", signing_deadline="2026-10-25",
        voice="civic", recommended_tier=Tier.ENHANCED, design_phrase="",
        pricing_format="single", cover_image="", creative_vision_hero="",
        case_study="skip", case_study_hero="",
        zones=(), line_items=(),
        creative_direction="", customer_goals=(), customer_constraints=(),
        success_criteria=(), what_youre_approving="",
        pillars=(), phases=(), scope_includes=(), add_ons=(), term_panels={},
        after_approval_steps=(), company_facts=(), team=(), contact_strip="",
        partnership_discounts=(),
    )
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_composer_past_work_loader.py::test_build_sample_of_work_ctx_emits_six_tiles -v
```

Expected: FAIL — `build_sample_of_work_ctx` not defined.

- [ ] **Step 3: Implement the ctx builder**

In `skill_assets/proposal_build/composer/ctx_builders.py`, after `build_case_study_ctx` (around line 319), add:

```python
def build_sample_of_work_ctx(model, page_num: int, page_total: int,
                             past_work_entries: list[dict]) -> dict:
    """Build context for the sample_of_work slide.

    past_work_entries is the resolved output of _load_past_work_entries —
    a list of dicts with id/name/location/year/image keys.

    The template wants `tiles` shaped as {name, location_year, image}, where
    location_year is the pre-formatted "City, ST · YYYY" string the bottom-
    left overlay renders. Building that string here keeps Jinja simple.
    """
    return {
        **_project_base(model),
        "page_num": page_num, "page_total": page_total,
        "page_eyebrow": "Sample of Our Work",
        "page_title": "Recent installations",
        "tiles": [
            {
                "name": e["name"],
                "location_year": f"{e['location']} · {e['year']}",
                "image": e["image"],
            }
            for e in past_work_entries
        ],
    }
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_composer_past_work_loader.py::test_build_sample_of_work_ctx_emits_six_tiles -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/composer/ctx_builders.py tests/test_composer_past_work_loader.py
git commit -m "$(cat <<'EOF'
feat(plan-10): build_sample_of_work_ctx — tiles with formatted location_year

Pre-formats 'City, ST · YYYY' so the Jinja template stays trivial.
Eyebrow/title match spec §3.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: `sample_of_work.html` layout + render test

**Files:**
- Create: `skill_assets/layouts/sample_of_work.html`
- Modify: `tests/fixtures/riverside.py` (add `sample_of_work_ctx`)
- Modify: `tests/test_layouts.py` (add render case)

- [ ] **Step 1: Add the layout fixture ctx**

Append to `tests/fixtures/riverside.py`:

```python


# ===== Sample of Our Work =====
# Six synthetic entries. Images are loaded from tests/fixtures/past_work_library/
# so the rendered tile shows a real (synthetic) JPG.
_PAST_WORK_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "past_work_library"
sample_of_work_ctx = {
    **PROJECT,
    "page_num": 10,
    "page_total": 14,
    "page_eyebrow": "Sample of Our Work",
    "page_title": "Recent installations",
    "tiles": [
        {"name": "Sample Project A", "location_year": "Sample City, AA · 2024",
         "image": (_PAST_WORK_FIXTURE_DIR / "fixture_a.jpg").as_uri()},
        {"name": "Sample Project B", "location_year": "Sample City, BB · 2024",
         "image": (_PAST_WORK_FIXTURE_DIR / "fixture_b.jpg").as_uri()},
        {"name": "Sample Project C", "location_year": "Sample City, CC · 2023",
         "image": (_PAST_WORK_FIXTURE_DIR / "fixture_c.jpg").as_uri()},
        {"name": "Sample Project D", "location_year": "Sample City, DD · 2023",
         "image": (_PAST_WORK_FIXTURE_DIR / "fixture_d.jpg").as_uri()},
        {"name": "Sample Project E", "location_year": "Sample City, EE · 2022",
         "image": (_PAST_WORK_FIXTURE_DIR / "fixture_e.jpg").as_uri()},
        {"name": "Sample Project F", "location_year": "Sample City, FF · 2022",
         "image": (_PAST_WORK_FIXTURE_DIR / "fixture_f.jpg").as_uri()},
    ],
}
```

- [ ] **Step 2: Add the render case to `LAYOUT_CASES`**

In `tests/test_layouts.py`, append a new tuple to `LAYOUT_CASES` (place it after the `case_study_riverside` entry):

```python
    ("sample_of_work_riverside", "sample_of_work", "riverside", "sample_of_work_ctx", [
        "Sample of Our Work", "Recent installations",
        "Sample Project A", "Sample Project F",
        "Sample City, AA · 2024", "Sample City, FF · 2022",
    ]),
```

- [ ] **Step 3: Run the render test to verify it fails**

```bash
pytest tests/test_layouts.py -v -k sample_of_work
```

Expected: FAIL — `sample_of_work.html` template not found, or assertion fails because nothing renders the expected strings.

- [ ] **Step 4: Write the layout**

Create `skill_assets/layouts/sample_of_work.html`:

```html
<!-- layout-version: 2026-05-11 -->
{% extends "base.html" %}
{% block layout_version %}<!-- layout-version: 2026-05-11 -->{% endblock %}
{% block title %}{{ project_short }} — {{ page_eyebrow }}{% endblock %}
{% block extra_head %}
<style>
  /* Sample of Our Work — light page, footer present.
     Spec ref: docs/superpowers/specs/2026-05-11-past-work-slide-design.md §3.

     Top: eyebrow (red caps "SAMPLE OF OUR WORK") + page title
          ("Recent installations" — Poppins Black 50pt).
     Body: 3 × 2 equal grid of tiles. Each tile is a full-bleed photo
           with a dark gradient scrim and bottom-left name + location/year. */

  .sw-outer {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .sw-title-area {
    flex: 0 0 auto;
    margin-bottom: var(--space-5);
  }

  .sw-title-area .eyebrow {
    margin-bottom: var(--space-2);
  }

  .sw-title-area .page-title {
    margin-bottom: 0;
  }

  .sw-grid {
    flex: 1 1 0;
    min-height: 0;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(2, 1fr);
    gap: var(--space-3);
  }

  .sw-tile {
    position: relative;
    overflow: hidden;
    border-radius: 3pt;
    background: #2A2A2A;  /* dark placeholder behind images */
  }

  .sw-tile img {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    object-fit: cover;
  }

  .sw-tile-scrim {
    position: absolute;
    left: 0; right: 0; bottom: 0;
    height: 50%;
    background: linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 100%);
    pointer-events: none;
  }

  .sw-tile-caption {
    position: absolute;
    left: var(--space-3);
    right: var(--space-3);
    bottom: var(--space-3);
    color: #FFFFFF;
    font-family: var(--font-body);
  }

  .sw-tile-name {
    font-family: var(--font-heading);
    font-weight: 700;
    font-size: var(--text-base);
    line-height: 1.15;
    margin-bottom: 1pt;
  }

  .sw-tile-meta {
    font-size: var(--text-xs);
    opacity: 0.9;
  }
</style>
{% endblock %}
{% block content %}
<div class="sw-outer">

  <!-- Eyebrow + page title -->
  <div class="sw-title-area">
    <div class="eyebrow">{{ page_eyebrow }}</div>
    <h1 class="page-title">{{ page_title }}</h1>
  </div>

  <!-- 3 × 2 tile grid -->
  <div class="sw-grid">
    {% for tile in tiles %}
    <div class="sw-tile">
      {% if tile.image %}
      <img src="{{ tile.image }}" alt="{{ tile.name }}">
      {% endif %}
      <div class="sw-tile-scrim"></div>
      <div class="sw-tile-caption">
        <div class="sw-tile-name">{{ tile.name }}</div>
        <div class="sw-tile-meta">{{ tile.location_year }}</div>
      </div>
    </div>
    {% endfor %}
  </div>

</div>
{% endblock %}
```

- [ ] **Step 5: Run the render test to verify it passes**

```bash
pytest tests/test_layouts.py -v -k sample_of_work
```

Expected: PASS. The generated PDF lands at `tests/_output/sample_of_work_riverside.pdf` — eyeball it to confirm: red eyebrow, 50pt charcoal title, 3×2 grid of synthetic-colored tiles each with name + "Sample City, XX · YYYY".

- [ ] **Step 6: Run the full layouts suite**

```bash
pytest tests/test_layouts.py -v
```

Expected: all PASS (no regressions in other layouts).

- [ ] **Step 7: Commit**

```bash
git add skill_assets/layouts/sample_of_work.html tests/fixtures/riverside.py tests/test_layouts.py
git commit -m "$(cat <<'EOF'
feat(plan-10): sample_of_work.html layout — 3x2 past-work grid

Light page, red eyebrow, Poppins Black 50pt title, full-bleed tiles with
dark gradient scrim + bottom-left name/location/year overlay.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 8: Composer dispatch — tiered mode

**Files:**
- Modify: `skill_assets/proposal_build/composer/__init__.py`
- Test: `tests/test_composer_tier_coverage.py` (or a new test file if more natural)

The dispatch:
1. After `case_study` slide, before `investment`, append `("sample_of_work", {...})` when `model.sample_work` is non-empty.
2. `_build_ctx` learns to route `sample_of_work` to `build_sample_of_work_ctx`.

- [ ] **Step 1: Write the failing test**

Create or append to `tests/test_composer_past_work_dispatch.py`:

```python
"""Tests for composer wiring of the sample_of_work slide (tiered + menu)."""
from __future__ import annotations

from pathlib import Path
import shutil

import pytest


def _patch_brief(project_dir: Path, sample_work_ids: list[str]) -> None:
    """Inject sample_work: into the Brief's YAML frontmatter."""
    brief = project_dir / "04 - Process & Notes" / "Project Brief.md"
    txt = brief.read_text()
    yaml_lines = "sample_work:\n" + "".join(f"  - {pid}\n" for pid in sample_work_ids)
    parts = txt.split("---", 2)
    assert len(parts) >= 3, "Brief missing YAML frontmatter"
    parts[1] = parts[1].rstrip() + "\n" + yaml_lines
    brief.write_text("---".join(parts))


def _swap_library_to_fixture(monkeypatch):
    """Point composer at tests/fixtures/past_work_library/ for the run."""
    fixture_lib = (
        Path(__file__).resolve().parent / "fixtures" / "past_work_library"
    )
    from proposal_build import composer
    monkeypatch.setattr(composer, "PAST_WORK_LIBRARY_DIR", fixture_lib)


def test_tiered_composer_emits_sample_of_work_when_sample_work_present(
    tmp_path, monkeypatch,
):
    """sample_work: in Brief → composer emits sample_of_work between case_study and investment."""
    src = (
        Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    dst = tmp_path / "fake_riverside"
    shutil.copytree(src, dst)
    _patch_brief(dst, ["fixture_a", "fixture_b", "fixture_c",
                       "fixture_d", "fixture_e", "fixture_f"])
    _swap_library_to_fixture(monkeypatch)

    from proposal_build.parser import build_project_model
    from proposal_build.composer import compose

    model, _ = build_project_model(dst)
    slides, _ = compose(model)
    layouts = [s.layout_name for s in slides]

    assert "sample_of_work" in layouts, (
        f"Expected sample_of_work in slide deck; got: {layouts}"
    )
    # Placement: after case_study (when present), before investment.
    sow_idx = layouts.index("sample_of_work")
    inv_idx = layouts.index("investment")
    assert sow_idx < inv_idx, "sample_of_work must come before investment"
    if "case_study" in layouts:
        cs_idx = layouts.index("case_study")
        assert cs_idx < sow_idx, "sample_of_work must come after case_study"


def test_tiered_composer_skips_sample_of_work_when_sample_work_empty(tmp_path):
    """No sample_work: in Brief → no sample_of_work slide in deck."""
    project_dir = (
        Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    from proposal_build.parser import build_project_model
    from proposal_build.composer import compose

    model, _ = build_project_model(project_dir)
    slides, _ = compose(model)
    layouts = [s.layout_name for s in slides]
    assert "sample_of_work" not in layouts
```

- [ ] **Step 2: Run tests to verify failure**

```bash
pytest tests/test_composer_past_work_dispatch.py -v
```

Expected: `test_tiered_composer_skips_sample_of_work_when_sample_work_empty` PASSES (no slide emitted because no dispatch yet). `test_tiered_composer_emits_sample_of_work_when_sample_work_present` FAILS.

- [ ] **Step 3: Wire the dispatch**

In `skill_assets/proposal_build/composer/__init__.py`, find this block inside `_compose_tiered` (around line 80–83):

```python
    if model.case_study and model.case_study != "skip":
        cs = _load_case_study(model.case_study)
        slides_raw.append(("case_study", {"case_study_data": cs}))
    slides_raw.append(("investment", {"tier_totals": tier_totals,
```

Insert immediately before the `slides_raw.append(("investment", ...))` line:

```python
    if model.sample_work:
        entries = _load_past_work_entries(list(model.sample_work))
        slides_raw.append(("sample_of_work", {"past_work_entries": entries}))
```

Then in the same file, inside `_build_ctx` (around line 165, just before the final `raise ValueError`), add:

```python
    if layout == "sample_of_work":
        return build_sample_of_work_ctx(model, page_num, page_total,
                                         hint["past_work_entries"])
```

And add the import at the top of the file. Find the existing `from proposal_build.composer.ctx_builders import (` block (around line 8) and add `build_sample_of_work_ctx` to its name list.

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_composer_past_work_dispatch.py -v
```

Expected: both PASS.

- [ ] **Step 5: Run the full composer + e2e suites**

```bash
pytest tests/test_composer_tier_coverage.py tests/test_composer_slide_plan.py tests/test_renderer_outputs.py -v
```

Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/composer/__init__.py tests/test_composer_past_work_dispatch.py
git commit -m "$(cat <<'EOF'
feat(plan-10): composer dispatches sample_of_work in tiered mode

Inserted between case_study and investment when model.sample_work is
non-empty. Library entries loaded via _load_past_work_entries; ctx
routed through build_sample_of_work_ctx.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 9: Composer dispatch — menu mode

**Files:**
- Modify: `skill_assets/proposal_build/composer/menu_compose.py`
- Test: `tests/test_composer_past_work_dispatch.py` (append)

- [ ] **Step 1: Read `menu_compose.py` to find the slide-assembly block**

```bash
grep -n "slides_raw\|append\|investment\|rom_investment" skill_assets/proposal_build/composer/menu_compose.py | head -30
```

Note the line where the slide list is assembled and where the `rom_investment` (or equivalent investment) slide gets appended.

- [ ] **Step 2: Write the failing test**

Append to `tests/test_composer_past_work_dispatch.py`:

```python
def test_menu_composer_emits_sample_of_work_when_sample_work_present(
    tmp_path, monkeypatch,
):
    """sample_work: in a menu Brief → menu composer emits sample_of_work."""
    src = (
        Path(__file__).resolve().parent.parent
        / "Projects" / "FIGat7th DTLA"
    )
    dst = tmp_path / "fake_figat7th"
    shutil.copytree(src, dst)
    _patch_brief(dst, ["fixture_a", "fixture_b", "fixture_c",
                       "fixture_d", "fixture_e", "fixture_f"])
    _swap_library_to_fixture(monkeypatch)

    from proposal_build.parser import parse_project
    from proposal_build.composer import compose

    model = parse_project(dst)
    slides, _ = compose(model)
    layouts = [s.layout_name for s in slides]

    assert "sample_of_work" in layouts, (
        f"Expected sample_of_work in menu deck; got: {layouts}"
    )


def test_menu_composer_skips_sample_of_work_when_sample_work_empty():
    """A FIGat7th Brief without sample_work → no sample_of_work slide."""
    project_dir = (
        Path(__file__).resolve().parent.parent
        / "Projects" / "FIGat7th DTLA"
    )
    from proposal_build.parser import parse_project
    from proposal_build.composer import compose

    model = parse_project(project_dir)
    slides, _ = compose(model)
    layouts = [s.layout_name for s in slides]
    assert "sample_of_work" not in layouts
```

- [ ] **Step 3: Run tests to verify the present-case fails**

```bash
pytest tests/test_composer_past_work_dispatch.py -v -k menu
```

Expected: `..._skips_...` PASSES; `..._emits_...` FAILS.

- [ ] **Step 4: Wire the dispatch into `menu_compose.py`**

In `skill_assets/proposal_build/composer/menu_compose.py`, find the slide-assembly block (Step 1 told you the line). The exact code shape varies — locate the line where the `rom_investment` (or `investment`) slide is appended, then insert immediately before it:

```python
    if model.sample_work:
        from proposal_build.composer import _load_past_work_entries
        entries = _load_past_work_entries(list(model.sample_work))
        slides_raw.append(("sample_of_work", {"past_work_entries": entries}))
```

If `menu_compose.py` has its own `_build_ctx` dispatcher, add the same routing arm as in Task 8 Step 3. If it shares the tiered `_build_ctx` (check the imports), no second edit needed.

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_composer_past_work_dispatch.py -v -k menu
pytest tests/test_e2e_figat7th_menu_pipeline.py tests/test_figat7th_golden.py -v
```

Expected: dispatch tests PASS; menu e2e + golden tests PASS (no regression).

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/composer/menu_compose.py tests/test_composer_past_work_dispatch.py
git commit -m "$(cat <<'EOF'
feat(plan-10): composer dispatches sample_of_work in menu mode

Same trigger condition as tiered: model.sample_work non-empty. Inserted
before the rom_investment slide. Reuses _load_past_work_entries.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 10: Inspector — `sample_work_wrong_count`

**Files:**
- Modify: `skill_assets/proposal_build/inspector/brief.py`
- Test: `tests/test_inspector_brief.py`

- [ ] **Step 1: Read `inspector/brief.py` to see existing finding shapes**

```bash
grep -n "^def\|Finding(" skill_assets/proposal_build/inspector/brief.py | head -40
```

Note the `Finding` constructor pattern and how existing optional fields raise findings.

- [ ] **Step 2: Write the failing test**

Append to `tests/test_inspector_brief.py`:

```python
def test_inspector_flags_sample_work_with_wrong_count(tmp_path):
    """sample_work: with 5 IDs → sample_work_wrong_count blocker."""
    import shutil
    from proposal_build.inspector.brief import check
    src = (
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    dst = tmp_path / "fake_project"
    shutil.copytree(src, dst)
    brief = dst / "04 - Process & Notes" / "Project Brief.md"
    txt = brief.read_text()
    parts = txt.split("---", 2)
    parts[1] = parts[1].rstrip() + "\nsample_work:\n  - fixture_a\n  - fixture_b\n  - fixture_c\n  - fixture_d\n  - fixture_e\n"
    brief.write_text("---".join(parts))

    findings = check(dst)
    issues = {f.issue for f in findings}
    assert "sample_work_wrong_count" in issues, (
        f"Expected sample_work_wrong_count; got {issues}"
    )


def test_inspector_accepts_sample_work_absent():
    """No sample_work: → no sample_work_* findings (slide just gets skipped)."""
    from proposal_build.inspector.brief import check
    project_dir = (
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    findings = check(project_dir)
    sw_issues = {f.issue for f in findings if f.issue.startswith("sample_work_")}
    assert sw_issues == set()
```

- [ ] **Step 3: Run tests to verify the wrong-count test fails**

```bash
pytest tests/test_inspector_brief.py -v -k sample_work
```

Expected: `..._accepts_...` PASSES; `..._wrong_count` FAILS.

- [ ] **Step 4: Implement the inspector check**

In `skill_assets/proposal_build/inspector/brief.py`, locate the `def check(project_path)` function. After the existing tiered-mode checks (after the zones loop, before the function returns), add a helper call. Near the top of the file alongside other constants, add:

```python
PAST_WORK_LIBRARY_RELPATH = "skill_assets/past_work_library"
```

Then inside both `check()` (tiered branch — placed after the existing zone checks) and `_check_menu_mode()` (find the equivalent end-of-checks spot), append:

```python
    findings.extend(_check_sample_work(project_path, fm))
```

Add the new helper function at module scope (place it near the bottom):

```python
def _check_sample_work(project_path: Path, fm: dict) -> list[Finding]:
    """Three findings on the sample_work: field. Empty/absent → no findings."""
    findings: list[Finding] = []
    sample_work = fm.get("sample_work") or []
    if not sample_work:
        return findings

    if len(sample_work) != 6:
        findings.append(Finding(
            severity="blocker", category="brief",
            issue="sample_work_wrong_count",
            detail=(
                f"sample_work: lists {len(sample_work)} IDs; the past-work "
                "slide requires exactly 6."
            ),
            fix=(
                "Edit the Brief so `sample_work:` has exactly 6 project IDs "
                "from skill_assets/past_work_library/, or remove the field "
                "entirely to skip the slide."
            ),
            field="sample_work",
        ))
    return findings
```

(The unknown-ID and missing-image findings get added in Tasks 11 and 12 — leave room for them in the helper.)

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_inspector_brief.py -v -k sample_work
```

Expected: both PASS.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/inspector/brief.py tests/test_inspector_brief.py
git commit -m "$(cat <<'EOF'
feat(plan-10): inspector finding — sample_work_wrong_count

Blocker when sample_work: is present but doesn't have exactly 6 IDs.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 11: Inspector — `sample_work_unknown_id`

**Files:**
- Modify: `skill_assets/proposal_build/inspector/brief.py`
- Test: `tests/test_inspector_brief.py`

This finding requires the inspector to know where the past_work_library lives. The check looks at `skill_assets/past_work_library/{id}.md`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_inspector_brief.py`:

```python
def test_inspector_flags_sample_work_unknown_id(tmp_path, monkeypatch):
    """sample_work: with an ID not in the library → sample_work_unknown_id."""
    import shutil
    from pathlib import Path
    from proposal_build.inspector import brief as inspector_brief
    from proposal_build.inspector.brief import check

    # Point inspector at the test fixture library
    fixture_lib = Path(__file__).resolve().parent / "fixtures" / "past_work_library"
    monkeypatch.setattr(inspector_brief, "PAST_WORK_LIBRARY_DIR", fixture_lib)

    src = (
        Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    dst = tmp_path / "fake_project"
    shutil.copytree(src, dst)
    brief = dst / "04 - Process & Notes" / "Project Brief.md"
    txt = brief.read_text()
    parts = txt.split("---", 2)
    # 6 IDs, but 'not_in_library' doesn't exist
    parts[1] = parts[1].rstrip() + (
        "\nsample_work:\n  - fixture_a\n  - fixture_b\n  - fixture_c\n"
        "  - fixture_d\n  - fixture_e\n  - not_in_library\n"
    )
    brief.write_text("---".join(parts))

    findings = check(dst)
    issues = [f.issue for f in findings]
    assert "sample_work_unknown_id" in issues
    # And no wrong-count (we have exactly 6)
    assert "sample_work_wrong_count" not in issues
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_inspector_brief.py::test_inspector_flags_sample_work_unknown_id -v
```

Expected: FAIL — finding not raised.

- [ ] **Step 3: Promote `PAST_WORK_LIBRARY_RELPATH` to a `PAST_WORK_LIBRARY_DIR` Path**

In `skill_assets/proposal_build/inspector/brief.py`, replace the string constant from Task 10 with a Path constant (so tests can monkeypatch it):

```python
from pathlib import Path

PAST_WORK_LIBRARY_DIR = (
    Path(__file__).resolve().parents[3] / "skill_assets" / "past_work_library"
)
```

Then extend `_check_sample_work` to walk the IDs and verify each `.md` file exists:

```python
def _check_sample_work(project_path: Path, fm: dict) -> list[Finding]:
    """Findings on the sample_work: field. Empty/absent → no findings."""
    findings: list[Finding] = []
    sample_work = fm.get("sample_work") or []
    if not sample_work:
        return findings

    if len(sample_work) != 6:
        findings.append(Finding(
            severity="blocker", category="brief",
            issue="sample_work_wrong_count",
            detail=(
                f"sample_work: lists {len(sample_work)} IDs; the past-work "
                "slide requires exactly 6."
            ),
            fix=(
                "Edit the Brief so `sample_work:` has exactly 6 project IDs "
                "from skill_assets/past_work_library/, or remove the field "
                "entirely to skip the slide."
            ),
            field="sample_work",
        ))

    for pid in sample_work:
        md_path = PAST_WORK_LIBRARY_DIR / f"{pid}.md"
        if not md_path.exists():
            findings.append(Finding(
                severity="blocker", category="brief",
                issue="sample_work_unknown_id",
                detail=(
                    f"sample_work ID '{pid}' has no entry at "
                    f"{md_path.relative_to(PAST_WORK_LIBRARY_DIR.parents[1])}"
                ),
                fix=(
                    f"Either remove '{pid}' from sample_work: in the Brief, "
                    f"or add {pid}.md (and {pid}.jpg) to the past_work_library/."
                ),
                field="sample_work",
            ))

    return findings
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_inspector_brief.py -v -k sample_work
```

Expected: all PASS (Task 10's two tests + Task 11's new one).

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build/inspector/brief.py tests/test_inspector_brief.py
git commit -m "$(cat <<'EOF'
feat(plan-10): inspector finding — sample_work_unknown_id

Blocker when any sample_work ID has no matching .md in past_work_library/.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 12: Inspector — `sample_work_missing_image`

**Files:**
- Modify: `skill_assets/proposal_build/inspector/brief.py`
- Test: `tests/test_inspector_brief.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_inspector_brief.py`:

```python
def test_inspector_flags_sample_work_missing_image(tmp_path, monkeypatch):
    """sample_work: ID has .md but no .jpg → sample_work_missing_image."""
    import shutil
    from pathlib import Path
    from proposal_build.inspector import brief as inspector_brief
    from proposal_build.inspector.brief import check

    # Build a temporary library where fixture_g has an .md but no .jpg
    tmp_lib = tmp_path / "lib"
    tmp_lib.mkdir()
    (tmp_lib / "fixture_g.md").write_text(
        '---\nid: fixture_g\nname: "G"\nlocation: "City, GG"\nyear: 2023\n---\n'
    )
    monkeypatch.setattr(inspector_brief, "PAST_WORK_LIBRARY_DIR", tmp_lib)

    src = (
        Path(__file__).resolve().parent.parent
        / "Projects" / "Downtown Riverside Metro Link"
    )
    dst = tmp_path / "fake_project"
    shutil.copytree(src, dst)
    brief = dst / "04 - Process & Notes" / "Project Brief.md"
    txt = brief.read_text()
    parts = txt.split("---", 2)
    # 6 IDs, all with .md but fixture_g lacks .jpg
    for pid in ("fixture_g",) * 6:  # all the same intentionally — keeps test simple
        (tmp_lib / f"{pid}.md").write_text(
            f'---\nid: {pid}\nname: "G"\nlocation: "City, GG"\nyear: 2023\n---\n'
        )
    parts[1] = parts[1].rstrip() + (
        "\nsample_work:\n  - fixture_g\n  - fixture_g\n  - fixture_g\n"
        "  - fixture_g\n  - fixture_g\n  - fixture_g\n"
    )
    brief.write_text("---".join(parts))

    findings = check(dst)
    issues = [f.issue for f in findings]
    assert "sample_work_missing_image" in issues
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_inspector_brief.py::test_inspector_flags_sample_work_missing_image -v
```

Expected: FAIL — finding not raised.

- [ ] **Step 3: Extend `_check_sample_work` to check the `.jpg`**

In `skill_assets/proposal_build/inspector/brief.py`, inside the `for pid in sample_work:` loop in `_check_sample_work`, add a sibling check after the `.md` existence check:

```python
        jpg_path = PAST_WORK_LIBRARY_DIR / f"{pid}.jpg"
        if md_path.exists() and not jpg_path.exists():
            findings.append(Finding(
                severity="blocker", category="brief",
                issue="sample_work_missing_image",
                detail=(
                    f"sample_work ID '{pid}' has a .md entry but no "
                    f"matching {pid}.jpg in past_work_library/."
                ),
                fix=(
                    f"Add {pid}.jpg to skill_assets/past_work_library/ "
                    f"(recommended ~1200x800)."
                ),
                field="sample_work",
            ))
```

- [ ] **Step 4: Run tests to verify all pass**

```bash
pytest tests/test_inspector_brief.py -v -k sample_work
```

Expected: 4 tests PASS (Task 10's two + Task 11's one + Task 12's one).

- [ ] **Step 5: Run the full inspector suite**

```bash
pytest tests/test_inspector_brief.py tests/test_inspector_folder.py tests/test_inspector_renderings.py tests/test_inspector_worksheet.py tests/test_inspector_aggregate.py tests/test_inspector_report.py tests/test_inspector_menu_mode.py -v
```

Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build/inspector/brief.py tests/test_inspector_brief.py
git commit -m "$(cat <<'EOF'
feat(plan-10): inspector finding — sample_work_missing_image

Blocker when a sample_work ID has a .md but no matching .jpg in
skill_assets/past_work_library/.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 13: AE_SOP — past_work_library section

**Files:**
- Modify: `skill_assets/AE_SOP.md`

- [ ] **Step 1: Read the current AE_SOP to find the right insertion point**

```bash
grep -n "^##\|^# " skill_assets/AE_SOP.md
```

Note where existing "Brief fields" / "Slide-specific" sections live so the new section slots in alongside them, not at random.

- [ ] **Step 2: Append the new section**

Add this section to `skill_assets/AE_SOP.md` (place it adjacent to other slide-specific Brief sections):

```markdown
## Past Work slide (`sample_work:` in Brief)

The Past Work slide is a 6-tile image grid of prior-season installations.
To include it in a proposal, add a `sample_work:` list to the Brief naming
exactly 6 project IDs from `skill_assets/past_work_library/`.

```yaml
sample_work:
  - project_id_one
  - project_id_two
  - project_id_three
  - project_id_four
  - project_id_five
  - project_id_six
```

Rules:

- **Past work only.** Never include current-cycle prospects or any project
  still being pitched. The slide is social proof; an active deal on it reads
  as inflated track record.
- **Real customers only.** Every ID must correspond to a real installed
  project. No fictional, aspirational, or stand-in names.
- **Library is curated by Daniel.** New past-work entries (`.md` + `.jpg`)
  are added out-of-band. Do not auto-fill from the `Projects/` directory.

Omit `sample_work:` to skip the slide entirely. The inspector blocks
generation if `sample_work:` is present but lists ≠ 6 IDs, an unknown ID,
or an ID with a missing image.
```

- [ ] **Step 3: Verify the file still parses (Markdown lint-style sanity)**

```bash
head -1 skill_assets/AE_SOP.md   # confirm file still starts with a heading
wc -l skill_assets/AE_SOP.md     # confirm the addition landed
```

- [ ] **Step 4: Commit**

```bash
git add skill_assets/AE_SOP.md
git commit -m "$(cat <<'EOF'
docs(plan-10): AE_SOP — past_work_library curation rules

Documents sample_work: Brief field, the exact-6 rule, and the three
curation constraints (past-only, real-only, Daniel-curated).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 14: Final integration smoke + verification

**Files:** (none modified)

- [ ] **Step 1: Run the full test suite**

```bash
pytest -q
```

Expected: 0 failures. Test count should be +~10 over baseline (4 inspector, ~3 composer dispatch, 1 layout, ~2 parser, 2 models).

- [ ] **Step 2: Eyeball the rendered layout**

```bash
ls -la tests/_output/sample_of_work_riverside.pdf
open tests/_output/sample_of_work_riverside.pdf
```

Confirm visually:
- Red "SAMPLE OF OUR WORK" eyebrow at top-left.
- "Recent installations" page title (Poppins Black, 50pt, charcoal) underneath.
- 3 × 2 grid of tiles, equal sizes, small gap.
- Each tile shows the synthetic-color background JPG with white name + meta in the bottom-left over a dark gradient scrim.
- Footer present (page number, project subtitle — whatever `base.html` provides).
- Tile copy reads as "Sample Project A / Sample City, AA · 2024" through "Sample Project F / Sample City, FF · 2022".

- [ ] **Step 3: Run an end-to-end generation against a real project to confirm no regression**

```bash
python3 -m proposal_build "Projects/Downtown Riverside Metro Link" --output tests/_output/riverside_smoke
```

(Or whichever CLI invocation matches the project's conventions — check `python3 -m proposal_build --help` if unsure.)

Expected: Riverside deck still generates exactly as before. No `sample_of_work` slide (Riverside Brief has no `sample_work:`).

- [ ] **Step 4: No commit needed — verification only**

If anything fails, fix in a targeted commit. If all green, plan is complete.

---

## Self-Review Notes

Coverage check against spec sections:

- §3 Slide design → Tasks 6, 7
- §4 Data model (`past_work_library/`) → Task 1 (test fixture), production lib stays empty per spec
- §5 Brief integration → Tasks 3, 4
- §6 Composer wiring → Tasks 5, 6, 8, 9
- §7 Inspector validations → Tasks 10, 11, 12
- §8 Test plan → Tasks 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
- §9 AE_SOP additions → Task 13
- §10 File manifest → Spread across all tasks

No spec gaps. No placeholders in the plan. Function signatures consistent (`_load_past_work_entries`, `build_sample_of_work_ctx`, `_check_sample_work`, `PAST_WORK_LIBRARY_DIR`).
