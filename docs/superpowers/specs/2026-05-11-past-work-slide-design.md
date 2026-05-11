# Past Work Slide — `sample_of_work.html`

**Date:** 2026-05-11
**Status:** Approved, ready for plan
**Author:** Daniel + Claude (brainstorming session)

---

## 1. Goal

Add a single-page "Sample of Our Work" slide to the proposal deck — a 6-tile
image grid of prior-season installations. The slide serves as compact social
proof: photo-led, scannable, no narrative.

This slide was specified in the original Plan 2 design (Task 18:
`sample_of_work.html`) but never built. Only the single-project
`case_study.html` deep-dive layout was implemented. This document fills the
gap.

---

## 2. Scope

**In scope**

- A new layout `skill_assets/layouts/sample_of_work.html`.
- A new content directory `skill_assets/past_work_library/`, shipping empty
  (no fictional placeholders committed).
- A new Brief field `sample_work:` (optional, exactly 6 IDs when present).
- Parser + context builder + composer dispatch for both `tiered` and `menu`
  model types.
- Inspector validations for the new field.
- Test fixtures using synthetic IDs (`fixture_a` … `fixture_f`).
- AE_SOP note clarifying curation rules.

**Out of scope**

- Auditing or replacing the existing `skill_assets/case_studies/` entries
  (`long_beach_transit.md`, `oregon_zoo.md`, `pier_39.md`) — separate pass.
- Auto-suggesting past_work entries by `voice:` tag — AE picks manually.
- A "logo wall" or "by-the-numbers" variant of the slide.
- Sourcing real project photos — Daniel curates the roster out-of-band.

---

## 3. Slide design

**Layout name:** `sample_of_work.html`
**Aspect:** Same 11×8.5 portrait-of-landscape page as other layouts.
**Theme:** Light page, footer present (consistent with about / case_study).

### Visual structure

```
┌────────────────────────────────────────────────────────────┐
│  SAMPLE OF OUR WORK              (red eyebrow, caps)        │
│  Recent installations            (Poppins Black 50pt)       │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                     │
│  │  photo   │ │  photo   │ │  photo   │   3 × 2 grid        │
│  │          │ │          │ │          │   equal weight      │
│  │ name     │ │ name     │ │ name     │   per tile          │
│  │ city·yr  │ │ city·yr  │ │ city·yr  │                     │
│  └──────────┘ └──────────┘ └──────────┘                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                     │
│  │  photo   │ │  photo   │ │  photo   │                     │
│  │          │ │          │ │          │                     │
│  │ name     │ │ name     │ │ name     │                     │
│  │ city·yr  │ │ city·yr  │ │ city·yr  │                     │
│  └──────────┘ └──────────┘ └──────────┘                     │
└────────────────────────────────────────────────────────────┘
```

### Per-tile composition

- Photo: object-fit cover, fills tile.
- Bottom-left overlay: project name + "Location · Year".
- Dark linear-gradient scrim from bottom (rgba(0,0,0,0.6) → 0) so white text
  reads on any photo.
- Border-radius 3–4pt, matching other gallery layouts.

### Copy

- **Eyebrow:** "SAMPLE OF OUR WORK" — red, uppercase, 0.10em letter-spacing.
- **Page title:** "Recent installations" — Poppins Black 50pt, charcoal.
- **No standfirst** (different from case_study; the photos carry the message).

### Style references

- Type system: existing `brand.css` tokens (no new tokens).
- Tile styling: pattern lifted from Plan 2 Task 18 spec (`sw-tile`,
  `sw-tile-overlay`, etc.) but using current spacing tokens.
- Eyebrow + title: same treatment as `case_study.html` / `scope.html`.

---

## 4. Data model — `past_work_library/`

### Directory

```
skill_assets/past_work_library/
├── .gitkeep                      ← ships empty
├── {project_id}.md               ← (Daniel adds out-of-band)
└── {project_id}.jpg              ← (Daniel adds out-of-band)
```

### `.md` shape

Frontmatter only — no body. Past-work tiles do not carry narrative; that is
what `case_studies/` is for.

```yaml
---
id: example_id
name: "Example Project Name"
location: "City, State"
year: 2024
---
```

### `.jpg` shape

- Single hero image per project.
- Recommended ~1200×800 (matches the original spec; tiles render at smaller
  size but headroom keeps them sharp).
- Filename must match `{id}.jpg` exactly.

### Curation rules

**Hard rules (codified in `AE_SOP.md` + inspector docs):**

1. **No current-cycle proposals.** Past Work means prior-season delivered
   work. Active prospects never appear here — it reads as inflated track
   record.
2. **No fictional or aspirational customers.** Every entry must be a real
   project actually installed by St. Nick's.
3. **Daniel curates the roster.** Library entries are never auto-generated
   from `Projects/` directory contents.

These rules are enforced by convention + docs, not by code (the skill cannot
distinguish real from fictional entries).

---

## 5. Brief integration

### New Brief field

```yaml
sample_work:
  - example_a
  - example_b
  - example_c
  - example_d
  - example_e
  - example_f
```

- **Optional.** Absent → slide is skipped (same pattern as `case_study: skip`).
- **Exactly 6 IDs when present.** Inspector errors on any other count.
- **Each ID must resolve to a file** in `skill_assets/past_work_library/`.

### Parser

`parser/__init__.py` reads `sample_work` as a `list[str]` (default `[]`).
Stored on `ProjectModel` as `sample_work: list[str]`.

---

## 6. Composer wiring

### Dispatch

Both `tiered` and `menu` model types support the slide via the same code path:

```python
if model.sample_work:
    sw = _load_sample_work(model.sample_work)   # list of dicts
    slides_raw.append(("sample_of_work", {"sample_work_data": sw}))
```

Insertion point: after `case_study`, before `investment` / `rom_investment`.
This matches the original Plan 2 spec placement and the existing
case_study → investment narrative arc.

### Context builder

`composer/ctx_builders.py` gains `build_sample_of_work_ctx`. Returns:

```python
{
    **PROJECT_BASE,
    "page_eyebrow": "Sample of Our Work",
    "page_title": "Recent installations",
    "tiles": [
        {
            "name": entry["name"],
            "location": entry["location"],
            "year": entry["year"],
            "image": model.resolved_renderings.get(f"{id}.jpg", absolute_path),
        }
        for id, entry in zip(model.sample_work, loaded_entries)
    ],
}
```

Tile images resolve through the existing `resolved_renderings` map (same
guard pattern used by `case_study_hero`, `cover_image`, etc.).

---

## 7. Inspector validations

`inspector/` gains three findings tied to `sample_work:`:

| Finding ID                          | Severity | Trigger                                                  |
|-------------------------------------|----------|----------------------------------------------------------|
| `sample_work_wrong_count`           | error    | `sample_work:` present and `len != 6`                    |
| `sample_work_unknown_id`            | error    | An ID in `sample_work:` has no matching `.md` in library |
| `sample_work_missing_image`         | error    | An ID has `.md` but no `.jpg` in library                 |

All three block generation. No warnings — past-work tiles must be either
complete or absent.

Briefs that omit `sample_work:` entirely produce no findings (slide is
skipped silently).

---

## 8. Test plan

### Render test

`tests/test_layouts.py::test_layout_renders` gains a `sample_of_work` case.
Fixture provides 6 synthetic entries (`fixture_a` … `fixture_f`) with
obviously-synthetic names ("Sample Project A", "Sample City, ST", 2023).
Assertion: each tile's name appears in the rendered HTML.

### Parser test

`tests/test_parser.py` (or equivalent) gains a case verifying:
- `sample_work:` absent → empty list on `ProjectModel`.
- `sample_work:` present → list of strings on `ProjectModel`.

### Inspector tests

Three new cases in `tests/test_inspector.py`:
- Wrong count (5 or 7 IDs) → `sample_work_wrong_count` finding.
- Unknown ID → `sample_work_unknown_id` finding.
- Missing image → `sample_work_missing_image` finding.

### Integration test

The Riverside / Sheraton / FIGat7th fixture Briefs **do not** add
`sample_work:` (per the no-current-cycle rule). They continue to render
without the slide. Test coverage for "slide is skipped silently" comes from
the existing fixture suite.

### Fixture library

`tests/fixtures/past_work_library/` mirrors the production directory shape
with 6 synthetic entries:

```
tests/fixtures/past_work_library/
├── fixture_a.md  (name: "Sample Project A", location: "Sample City, AA", year: 2023)
├── fixture_a.jpg (tiny solid-color placeholder, ~100×100)
├── fixture_b.md
├── fixture_b.jpg
└── ... fixture_c..f
```

These never ship in the skill bundle — they exist only in `tests/`.

---

## 9. AE_SOP additions

Add a short section to `skill_assets/AE_SOP.md`:

> **Past Work slide (`sample_work:` in Brief)**
>
> The Past Work slide shows 6 prior-season installations. To include it,
> add a `sample_work:` list to the Brief naming exactly 6 project IDs from
> `skill_assets/past_work_library/`.
>
> Rules:
> - **Past work only.** Never include current-cycle prospects or any project
>   still being pitched.
> - **Real customers only.** Every ID must correspond to a real installed
>   project.
> - **Library is curated by Daniel.** New past-work entries (`.md` + `.jpg`)
>   are added out-of-band; do not auto-fill from `Projects/`.
>
> Omit `sample_work:` to skip the slide entirely.

---

## 10. File manifest

### Created

| Path                                                | Purpose                                    |
|-----------------------------------------------------|--------------------------------------------|
| `skill_assets/layouts/sample_of_work.html`          | New layout                                 |
| `skill_assets/past_work_library/.gitkeep`           | Empty library marker (already exists)      |
| `tests/fixtures/past_work_library/fixture_{a–f}.md` | Synthetic test fixtures                    |
| `tests/fixtures/past_work_library/fixture_{a–f}.jpg`| Tiny placeholder images                    |

### Modified

| Path                                                | Change                                     |
|-----------------------------------------------------|--------------------------------------------|
| `skill_assets/proposal_build/models.py`             | Add `sample_work: list[str]` field         |
| `skill_assets/proposal_build/parser/__init__.py`    | Parse `sample_work:`                       |
| `skill_assets/proposal_build/composer/__init__.py`  | Dispatch `sample_of_work` slide            |
| `skill_assets/proposal_build/composer/ctx_builders.py` | `build_sample_of_work_ctx`              |
| `skill_assets/proposal_build/inspector/...`         | Three new findings                         |
| `skill_assets/AE_SOP.md`                            | New section on past_work_library rules     |
| `tests/test_layouts.py`                             | `sample_of_work` render test               |
| `tests/test_parser.py`                              | `sample_work:` parser test                 |
| `tests/test_inspector.py`                           | Three new inspector cases                  |
| `tests/fixtures/<project>.py`                       | One fixture exercises sample_work happy path |

---

## 11. Open items deferred to implementation

- Final tile background color when an entry is missing an image (probably
  match the case_study placeholder treatment: dark charcoal + italic gray
  "[name — photo]" centered).
- Exact gap / spacing values for the grid — tune during layout-render review.
- Whether the slide gets a footer page-number entry — assume yes, default
  base.html behavior.

---

## 12. Out of scope (revisit later)

- Cleaning up the existing `skill_assets/case_studies/` files
  (`long_beach_transit.md`, `oregon_zoo.md`, `pier_39.md`) which share the
  same fictional-customer-name issue. Daniel said leave for now.
- A 2-tile or 8-tile variant of the slide.
- Auto-filtering past-work entries by `voice:` tag.
- A "logo wall" or "by-the-numbers" alternate slide format.
