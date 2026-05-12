# Tree Comparison Slide — `tree_comparison.html`

**Date:** 2026-05-12
**Status:** Approved, ready for plan (next session)
**Author:** Daniel + Claude (brainstorming session)

---

## 1. Goal

Add an opt-in "Alternate Tree Options" slide to menu-mode proposals. Three
tree-size cards side-by-side (e.g. 30 ft / 40 ft / 50 ft) acting as a
value-engineering supplement to the main pitch. Placed near the end of
the deck, just before the sign-off slide.

The slide does **not** modify the main program pricing — it presents
alternates so a customer who balks at the headline tree price has a
downgrade path without St. Nick's pulling out a new proposal.

Originating use case: FIGat7th DTLA 2026 program pitches a 50 ft tree
in Section 2. The 30/40 ft options preserve the program if budget needs
flexibility.

---

## 2. Scope

**In scope**

- New layout `skill_assets/layouts/tree_comparison.html`.
- New tree catalog `skill_assets/tree_library/` (ships empty; Daniel
  seeds from spec sheet).
- New Brief field `tree_comparison:` (optional; menu-mode only for V1).
- Parser + context builder + composer dispatch for menu mode.
- Inspector validations for the new field.
- Test fixtures using synthetic tree IDs.
- AE_SOP section explaining the field and curation rules.

**Out of scope (V1)**

- Tiered-mode integration. Riverside / Sheraton / Pier 39 don't get this
  slide. Wire it in a follow-up if a tiered project ever needs it.
- A "Recommended" tree algorithm. The Brief explicitly names the
  recommended ID; no derivation.
- Variable tree counts (2 or 4 trees per slide). V1 is fixed at exactly 3.
- Cross-project tree quoting (e.g. "use FIGat7th's tree on this property").
  Out of scope — Daniel curates the catalog.
- Replacing or modifying Section 2's pricing. The main pitch is untouched.

---

## 3. Slide design

**Layout name:** `tree_comparison.html`
**Aspect:** Same 11×8.5 landscape page as other layouts.
**Theme:** Light page, footer present.

### Visual structure

The layout reuses the `investment.html` 3-up tier-card pattern. Differences:

- Each card carries a small tree photo at the top (investment cards don't).
- Card content is spec-oriented (height / topper / footprint / ornaments)
  rather than tier-feature lists.
- The "★ RECOMMENDED ★" red banner above one card is identical to investment.

```
┌──────────────────────────────────────────────────────────────────────┐
│  ALTERNATE TREE OPTIONS                  (red eyebrow, caps)          │
│  Three scale options for the program                                  │
│  (Standfirst — short explanatory line about value-engineering)        │
│                                                                        │
│  ┌──────────┐ ┌──────────────┐ ┌──────────┐                           │
│  │          │ │ ★ RECOMMENDED│ │          │                           │
│  │ ┌──────┐ │ │ ┌──────────┐ │ │ ┌──────┐ │                           │
│  │ │photo │ │ │ │  photo   │ │ │ │photo │ │                           │
│  │ └──────┘ │ │ └──────────┘ │ │ └──────┘ │                           │
│  │ 30 ft    │ │ 40 ft        │ │ 50 ft    │                           │
│  │ name     │ │ name         │ │ name     │                           │
│  │ tagline  │ │ tagline      │ │ tagline  │                           │
│  │ ─────    │ │ ─────        │ │ ─────    │                           │
│  │ • bullet │ │ • bullet     │ │ • bullet │                           │
│  │ • bullet │ │ • bullet     │ │ • bullet │                           │
│  │ • bullet │ │ • bullet     │ │ • bullet │                           │
│  │ $price   │ │ $price       │ │ $price   │                           │
│  └──────────┘ └──────────────┘ └──────────┘                           │
│                                                                        │
│  Footnote: "Alternates to the program tree in Section 2 ..."          │
└──────────────────────────────────────────────────────────────────────┘
```

### Card content

Each card pulls from the tree's `.md` frontmatter:

- **Top:** small hero image (`{id}.jpg`)
- **Height label:** `height_display` field (e.g. "30 ft")
- **Name:** `name` field (e.g. "30 ft Commercial Tree")
- **Tagline:** `tagline` field — short positioning line (red caps style,
  matches investment.html)
- **Thin rule** (color varies per card, e.g. gray/red/navy like investment)
- **Bullets:** 3–4 spec items from the `bullets` array in the `.md`
- **Price line:** display TBD per spec sheet — likely rental headline
  with purchase info in a smaller line or footnote. Final shape locked
  in the implementation plan once the spec sheet is in hand.

### Copy

- **Eyebrow:** "ALTERNATE TREE OPTIONS" — red, uppercase, 0.10em
  letter-spacing (matches eyebrow convention from past_work + case_study).
- **Page title:** "Three scale options for the program" (working title;
  may revise in implementation when seen rendered).
- **Standfirst:** Short explanation that these are alternates to the
  Section 2 tree, sized for budget flexibility. Final wording deferred.
- **Footnote:** Reinforces that these are options, not adds. Working
  text: *"These are scale alternatives to the program tree in Section 2.
  Selecting one of these replaces the Section 2 tree pricing; the
  enhancement package (lit reindeer, gift boxes, branded arch) carries
  over to whichever tree the customer picks."*

---

## 4. Data model — `tree_library/`

### Directory

```
skill_assets/tree_library/
├── .gitkeep                      ← ships empty
├── {tree_id}.md                  ← Daniel adds out-of-band
└── {tree_id}.jpg                 ← Daniel adds out-of-band
```

### `.md` shape (working set; final fields confirmed against spec sheet)

Frontmatter only — no body. All numeric pricing axes present so the card
can choose what to display.

```yaml
---
id: tree_30
height_display: "30 ft"
name: "30 ft Commercial Tree"
tagline: "Compact landmark presence."

# Spec axes
topper: "6 ft LED topper (option)"
footprint: "8 ft base diameter"
ornament_package: "Champagne gold / sapphire teal / jewel teal / ivory white"

# Pricing axes (same shape as ROMLineItem)
rental_low: 90000
rental_high: 95000
purchase_ot_low: 120000
purchase_ot_high: 130000
purchase_svc_low: 45000
purchase_svc_high: 50000

# Display bullets (3–4 items)
bullets:
  - "30 ft commercial PVC, engineered steel-frame base"
  - "Fully decorated in the FIGat7th ornament package"
  - "6 ft LED topper (cool-white or gold sparkler)"
  - "Storage and re-deploy ready"
---
```

### `.jpg` shape

- Single tree photo per `.md`.
- Recommended ~1200×800; landscape preferred (matches the card's photo aspect).
- Filename must match `{id}.jpg` exactly.

### Curation rules (same vibe as past_work_library)

1. **Real configurations only.** No fictional or aspirational tree builds.
   Each entry must reflect a tree St. Nick's can actually deliver.
2. **Pricing must be confirmed.** No placeholder dollars. The catalog is
   a sales reference; quoted figures need to be defensible.
3. **Daniel curates.** Entries added out-of-band from the spec sheet.

---

## 5. Brief integration

### New Brief field

```yaml
tree_comparison:
  trees: [tree_30, tree_40, tree_50]
  recommended: tree_50
```

- **Optional.** Absent → slide is skipped silently.
- **Exactly 3 IDs in `trees`** when the field is present (matches the
  fixed 3-card layout).
- **`recommended`** must be one of the IDs in `trees`.
- Each ID must resolve to a `.md` + `.jpg` in `tree_library/`.

### Parser

The menu parser (`parser/menu_resolver.py`) reads `tree_comparison` from
Brief frontmatter into `MenuProjectModel.tree_comparison`. The model
field is typed `Mapping[str, object]` with `field(default_factory=dict)`
— matches the existing pattern used by `tier_highlights` on
`ProjectModel`. Keys: `"trees"` (list of IDs) and `"recommended"`
(single ID). Empty dict → field absent → slide skipped.

Tiered-mode parser leaves the field absent for V1.

### Inspector validations

Five new findings in `inspector/brief.py`, all blockers:

| Finding ID | Trigger |
|---|---|
| `tree_comparison_wrong_count` | `trees:` present and `len != 3` |
| `tree_comparison_unknown_id` | A `trees:` ID has no matching `.md` in `tree_library/` |
| `tree_comparison_missing_image` | An ID has `.md` but no `.jpg` |
| `tree_comparison_recommended_not_in_trees` | `recommended:` is not one of the IDs in `trees:` |
| `tree_comparison_recommended_missing` | `tree_comparison:` present but `recommended:` absent or empty |

Per past_work_library lessons: `wrong_count` short-circuits the per-ID
checks to avoid spurious unknown-ID noise when the count is wrong.

---

## 6. Composer wiring

### Menu-mode dispatch

In `composer/menu_compose.py`, after the `rom_investment` slides and
before `sign_off_menu`, insert `tree_comparison` if
`model.tree_comparison` is non-empty:

```python
if model.tree_comparison:
    entries = _load_tree_entries(model.tree_comparison["trees"])
    layout_hints.append((
        "tree_comparison",
        {
            "tree_entries": entries,
            "recommended_id": model.tree_comparison["recommended"],
        },
    ))
```

### Loader

`_load_tree_entries` lives in `composer/__init__.py` (alongside
`_load_past_work_entries`) and follows the same pattern:

- Reads `{id}.md` frontmatter from `skill_assets/tree_library/` (or a
  test-supplied `library_dir`).
- Returns one dict per ID with all spec + pricing fields, plus an
  absolute path for the `.jpg`.
- Raises `FileNotFoundError` if an `.md` is missing (inspector catches
  earlier in normal flow).

### Context builder

`build_tree_comparison_ctx` in `composer/menu_ctx_builders.py` returns:

```python
{
    **_project_dict(model),
    "page_num": page_num,
    "page_total": page_total,
    "page_eyebrow": "Alternate Tree Options",
    "page_title": "Three scale options for the program",
    "standfirst": "<finalized in implementation>",
    "footnote": "<finalized in implementation>",
    "cards": [
        {
            "rule_color": "gray",        # alternates per card position
            "image": entry["image"],
            "height_display": entry["height_display"],
            "name": entry["name"],
            "tagline": entry["tagline"],
            "bullets": entry["bullets"],
            "price_display": <formatted from rental/purchase axes>,
            "is_recommended": entry["id"] == recommended_id,
        }
        for entry in tree_entries
    ],
}
```

### Tiered-mode (deferred)

`tree_comparison` is **not** wired into `composer/__init__.py`
`_compose_tiered` for V1. If a tiered project ever needs it, follow the
same pattern: dispatch before sign_off, share the loader, share the
ctx builder shape.

---

## 7. Layout — new `tree_comparison.html`

Extends `base.html`. Reuses heavy CSS from `investment.html`'s tier-card
pattern. Key differences:

- Each card has a photo area at the top (~30% of card height).
- Bullet list density tuned for spec items (3–4 short lines).
- Card price line shows the display string built by the ctx builder.
- Recommended banner identical to investment.html (`★ RECOMMENDED ★`).

### Shared CSS opportunity (small refactor)

The recommended banner + tier-card frame currently live inline in
`investment.html`. Moving these classes to `brand.css` (e.g.
`.tier-card`, `.recommended-banner`, `.banner-spacer`) lets both layouts
share them without copy-paste. Mark as a small inline refactor in the
implementation plan; don't expand scope beyond what's needed.

If the refactor adds non-trivial risk (other layouts breaking, golden
test deltas), defer it and inline the CSS in tree_comparison.html
instead — duplication is acceptable for V1.

---

## 8. Test plan

### Render test

`tests/test_layouts.py::test_layout_renders` gains a `tree_comparison`
case. Fixture provides 3 synthetic tree entries (`fixture_tree_a/b/c`)
with obviously-synthetic names ("Sample Tree A — 30 ft"). The recommended
one is `fixture_tree_b`. Assertion: each card's name + height + tagline
appears in the rendered PDF; the recommended banner text "RECOMMENDED"
appears exactly once.

### Parser test

A new test in `tests/test_parser_brief_menu_mode.py`:
- `tree_comparison:` absent → `model.tree_comparison` is `{}` or `None`.
- `tree_comparison:` present with `trees:` and `recommended:` → both
  populated correctly.

### Inspector tests

Five new cases in `tests/test_inspector_brief.py`:
- Wrong count (2 or 4 IDs) → `tree_comparison_wrong_count`.
- Unknown ID → `tree_comparison_unknown_id`.
- Missing image → `tree_comparison_missing_image`.
- `recommended` not in `trees` → `tree_comparison_recommended_not_in_trees`.
- `recommended` absent → `tree_comparison_recommended_missing`.

`wrong_count` test asserts the per-ID checks short-circuit (no spurious
`unknown_id` findings when count is wrong).

### Composer dispatch test

New file `tests/test_composer_tree_comparison_dispatch.py` (mirrors
`test_composer_past_work_dispatch.py`):

- Menu Brief with `tree_comparison:` populated → slide emitted between
  rom_investment p2 and sign_off.
- Menu Brief without `tree_comparison:` → slide skipped silently.

### Integration test

The FIGat7th fixture Brief **does** add `tree_comparison:` once the
real tree catalog is seeded (Daniel's spec sheet content). Until then,
the test asserts the field is absent and FIGat7th renders without the
slide. Once seeded, the golden test for FIGat7th gains the new slide
in the layout sequence.

### Fixture library

`tests/fixtures/tree_library/` mirrors production:
```
fixture_tree_a.md  (height_display: "30 ft", recommended: false)
fixture_tree_a.jpg
fixture_tree_b.md  (height_display: "40 ft", recommended: true)
fixture_tree_b.jpg
fixture_tree_c.md  (height_display: "50 ft", recommended: false)
fixture_tree_c.jpg
```

Synthetic data only; never ships in the skill bundle.

---

## 9. AE_SOP additions

Append a short section to `skill_assets/AE_SOP.md` (alongside the
"Past Work slide" section):

> **Tree Comparison slide (`tree_comparison:` in Brief, menu mode)**
>
> The Tree Comparison slide shows three tree-size alternatives near the
> end of a menu-mode deck. Useful when the main pitch carries a flagship
> tree that may be larger than the customer's budget. The slide does NOT
> modify Section 2's pricing — it presents scale-down options as a
> conversation tool.
>
> To include it, add a `tree_comparison:` block to the Brief naming
> exactly 3 tree IDs from `skill_assets/tree_library/` plus a
> `recommended:` ID (must be one of the three):
>
> ```yaml
> tree_comparison:
>   trees: [tree_30, tree_40, tree_50]
>   recommended: tree_50
> ```
>
> Rules:
> - **Real configurations only.** Every ID must correspond to a tree
>   St. Nick's can actually deliver.
> - **Pricing must be confirmed.** Catalog dollar figures need to be
>   defensible — they appear on a customer-facing slide.
> - **Library is curated by Daniel.** New tree entries (`.md` + `.jpg`)
>   are added out-of-band from confirmed spec sheets.
>
> Omit `tree_comparison:` to skip the slide entirely.

---

## 10. File manifest

### Created

| Path | Purpose |
|---|---|
| `skill_assets/layouts/tree_comparison.html` | New layout |
| `skill_assets/tree_library/.gitkeep` | Empty library marker |
| `tests/fixtures/tree_library/fixture_tree_{a,b,c}.md` | Synthetic test fixtures |
| `tests/fixtures/tree_library/fixture_tree_{a,b,c}.jpg` | Tiny placeholder images |
| `tests/test_composer_tree_comparison_dispatch.py` (or extension) | Dispatch test |

### Modified

| Path | Change |
|---|---|
| `skill_assets/proposal_build/models.py` | Add `tree_comparison: Mapping[str, object] = field(default_factory=dict)` to `MenuProjectModel` |
| `skill_assets/proposal_build/parser/menu_resolver.py` | Parse `tree_comparison:` from Brief |
| `skill_assets/proposal_build/composer/__init__.py` | Add `_load_tree_entries` loader + `TREE_LIBRARY_DIR` constant |
| `skill_assets/proposal_build/composer/menu_compose.py` | Dispatch `tree_comparison` slide before sign_off |
| `skill_assets/proposal_build/composer/menu_ctx_builders.py` | New `build_tree_comparison_ctx` |
| `skill_assets/proposal_build/inspector/brief.py` | Five new findings |
| `skill_assets/AE_SOP.md` | New section on tree_comparison Brief field |
| `skill_assets/layouts/brand.css` | (Optional) shared tier-card classes |
| `skill_assets/layouts/investment.html` | (Optional) use shared brand.css classes if extracted |
| `tests/test_layouts.py` | `tree_comparison` render case |
| `tests/test_parser_brief_menu_mode.py` | `tree_comparison:` parser test |
| `tests/test_inspector_brief.py` | Five new inspector cases |
| `tests/fixtures/figat7th.py` (or equivalent) | Wire `sample_of_work_ctx`-style fixture for the render test |

---

## 11. Open items deferred to implementation

These get firmed up when Daniel uploads the spec sheet + pricing reference:

- Final field list per tree `.md` (matched to spec sheet content).
- Final card content layout — which fields are above-the-fold on the
  card, which become bullets, which sit in footnote/legend space.
- Whether cards show rental headline only, purchase headline only, or
  both. Likely rental-headline + purchase line beneath; lock at
  implementation time.
- Slide title, standfirst, and footnote final wording.
- Brand.css refactor for shared tier-card classes — go or no-go based
  on risk to existing investment.html render.
- Exact "Recommended" badge color/treatment if it should differ from
  the investment.html badge.

---

## 12. Out of scope (revisit later)

- Tiered-mode (Riverside / Sheraton) integration.
- Variable tree counts on the slide (2 or 4+ trees).
- Auto-derivation of recommended tree based on budget hints.
- Cross-project tree quoting (pull from another project's pricing).
- A "Configure Your Tree" interactive variant (sizes + ornament packages
  as independent axes).
- Integration with the customer-facing scope workbook (separate Plan).
