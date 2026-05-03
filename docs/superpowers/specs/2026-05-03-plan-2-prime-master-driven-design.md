# Plan 2-prime — Master-Driven Layout System: Design

**Status:** Approved 2026-05-03 (brainstorming session, Daniel + Claude)
**Parent spec:** `docs/superpowers/specs/2026-05-01-proposal-builder-skill-design.md`
**Supersedes:**
- `docs/superpowers/specs/2026-05-01-plan-2-brand-layout-design.md` (Plan 2, decision 6 was wrong — see §1 below)
- `docs/superpowers/specs/2026-05-03-typographic-fallback-layouts-design.md` (the typographic-fallback addendum from earlier today; never executed and the direction is off-brand — Playfair Display violates the Branding Board's "avoid decorative or script fonts" rule)
**Successor:** Plan 3 — Phase 2 generation core (parsers + AE workflow + render pipeline)

---

## 1. Goal

Rebuild Plan 2's layout system using `Master Proposal Reference/StNicks_Proposal_v2_Master.pdf` as the **literal visual + structural reference**. Plan 2's decision 6 ("master is informal directional reference only") was the load-bearing error: the actual master is a far stronger proposal than the ground-up redesign produced, and Daniel wants the shipped output to look like the master with a small set of explicit modifications.

After Plan 2-prime: 15 master-derived layouts ship, the Branding Board fonts and colors are honored exactly, and projects with varying zone counts have layout variants that scale gracefully.

## 2. Why this exists (what went wrong with Plan 2)

Plan 2 produced 18 working layouts that all render correctly, pass tests, and are technically clean. They are also bland, generic, and structurally wrong:

- **Abstraction-driven, not zone-driven.** Customers think "Embarcadero Arrival, Pier Promenade, Bay Terrace" — physical zones of their property. Plan 2 produced abstract layouts (`showcase_2up`, `showcase_3up`) that don't map to how customers experience the proposal.
- **Branding hidden.** The St. Nick's wordmark only appeared on the cover and About page. The master places it in a persistent header on every slide, plus a footer with proposal title and page number.
- **Pricing reserved.** The master shows tier prices ($225K / $345K / $485K) prominently with a `★ RECOMMENDED ★` banner, inline add-on prices (`+$12K`), and a multi-year partnership discount table. Plan 2's investment layouts hid most of the numbers.
- **Tone civic-procurement.** Plan 2 read like a transit-agency RFP response. The master reads like a confident sales document.
- **Vague About content.** Plan 2's About page shipped with stat strings ("17 years", "120+ programs") that don't match real St. Nick's. The master has the actual data — license #, insurance limits, founding year, named team roles.

The pivot is preserved-foundation, replaced-layouts: WeasyPrint pipeline, Jinja2 + base.html, brand.css colors, embedded fonts, test infrastructure all stay. The 18 layout files and the abstract Riverside fixture get archived (see §10) and replaced with master-derived layouts and a destination-style fixture.

## 3. Decisions (locked)

These were the decisions made in the 2026-05-03 brainstorming session.

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | Visual reference | Master pptx is **literal** — not "directional" | Plan 2's "fresh modern redesign from spec" produced output Daniel rejected as bland. The master proves a stronger proposal already exists. |
| 2 | Audience tags | **Drop** the `OWNER / GM` / `MARKETING` / `FINANCE` audience pills | Daniel: "I don't necessarily like the notes that say marketing or GM/Owner those can be scrapped." |
| 3 | Zone schema | **Keep** zone-based structure (Embarcadero / Promenade / Bay Terrace pattern). Ship 5 zone-layout variants to handle varying zone counts. | Daniel: "I like the zone notes I think that helps it flow really well." Real projects have anywhere from 1 to 10+ zones; one layout pattern doesn't scale. |
| 4 | Brand fonts | **Roboto + Poppins, no others.** Add Poppins-Black for heavy display headlines. | Branding Board page 2 specifies Roboto (primary) + Poppins (secondary), explicitly rules out decorative/script fonts. The master's massive headlines (~50pt cover, ~36pt section titles) want Poppins Black, which we don't yet ship. |
| 5 | Brand colors | **Existing 5 verbatim** — no changes | Branding Board page 1 specifies exactly the 5 hex values already in `brand.css`: `#B31315 #12355B #555555 #1C1C1C #ECEFF1`. No additions. |
| 6 | Test fixtures | **Two fixtures** — destination-style (Pier 39, 3 zones) + zone-heavy (repurposed Riverside MetroLink as multi-station, 5+ zones) | The master is built on Pier 39 — reuse its content for the destination case. A second fixture proves the zone-grouped layouts work at scale. |
| 7 | Plan 2 archive | Move 18 layouts + 18 PDFs to `archive/iteration-1-abstract-layouts/` with README | Daniel: "archive them as an iteration. Just for reference later and kinda what not to do and compare later." |

## 4. Visual language (master-derived)

These are the consistent treatments across every slide in the master. The new layouts must hit all of them.

**Page chrome (every slide):**
- **Header (top-left):** `ST. NICK'S` in bold sans-serif tracked + `CHRISTMAS LIGHTING & DÉCOR` in smaller tracked caps below. White on dark pages, charcoal on light pages.
- **Footer (every slide except the cover):** left side `ST. NICK'S  ·  2026 HOLIDAY PROPOSAL  ·  PIER 39 SAN FRANCISCO`, right side `N / 13` (page count). Set in tracked caps, gray.
- **No audience tags** (the colored pills in the master's top-right are dropped).

**Page background pattern (master-defined):**
- **Dark pages** (charcoal `#1C1C1C` background, white text): cover, creative vision, zone-fullbleed (signature zone), about. These are the "feature" pages.
- **Light pages** (white background, charcoal text): exec summary, our understanding, zone-solo, zone-2up, zone-3up, zone-index, scope, case study, investment, terms, sign-off. These are the "content" pages.

**Type system:**
- **Page-title hero** (`Executive Summary`, `Our Understanding`, `Investment`, etc.): Poppins Black at ~50pt, charcoal on light / white on dark.
- **Italic standfirst** below page title: Poppins Light Italic at ~16pt, gray. (E.g. *"Our 2026 holiday program for Pier 39, at a glance."*)
- **Section labels** (`VENUE & CONTEXT`, `INCLUDED ELEMENTS`, `AT A GLANCE`): Roboto Bold caps, brand red `#B31315`, ~11pt with 0.06em tracking.
- **Eyebrows / zone numbers** (`ZONE 01`, `CASE STUDY`): Roboto Bold caps, brand red, ~10pt with 0.10em tracking.
- **Body copy:** Poppins Regular at 11–12pt, charcoal, 1.5 line-height.
- **Captions / metadata:** Poppins Light at 9–10pt, gray.
- **All-caps labels for key-value blocks** (`PROJECT`, `ZONES`, `RECOMMENDED TIER` in the AT A GLANCE panel): Roboto Bold caps gray, value below in Poppins Bold black.

**Color usage rules:**
- Brand red `#B31315` is reserved for: section labels, eyebrows, the recommended-tier banner, deadline labels (FABRICATION LOCK, SIGNING DEADLINE), the dark-bg "Terms" date banner, and very small accent rules. Never used for block fills except: the date banner on Terms (full-width red bar), the OPTIONAL ADD-ONS top header, the RECOMMENDED banner on Investment, and the about-page bottom contact strip.
- Light gray `#F2F2F2` is the panel/card background. **New token:** `--color-panel: #F2F2F2`. (Distinct from `--color-light: #ECEFF1`, which stays for type on dark backgrounds.)
- Cards have a subtle drop-shadow (~2pt soft) and a colored top header bar (red for warning/add-ons, green for inclusions, gray/red/navy for tier rules).
- Green for "YOUR PROGRAM INCLUDES" header in Scope. **New token:** `--color-green: #1B7A3F`. Used on the Scope page only.

**Card pattern (used on Understanding, Scope, Terms, Sign-off):**
- Background: `--color-panel`
- Top: colored header bar (full width of card, ~36pt tall) with white tracked-caps title centered or left-aligned
- Body: padded interior (~`var(--space-4)` all sides), bullet lists or paragraphs
- Optional: red left-edge rule (Understanding pattern) instead of top header bar (Scope pattern)
- Subtle shadow underneath

## 5. Slide catalog (15 layouts)

Each row maps a master pptx slide to a layout file. The `# zones` column governs which zone-layout variant Plan 3 picks at render time.

| # | Master slide | Layout file | Bg | Notes |
|---|---|---|---|---|
| 1 | 1 — Cover | `cover.html` | dark | Two-zone split: text-left, hero-image-right. Project name in Poppins Black ~80pt. Eyebrow `2026 HOLIDAY SEASON` in red. Bottom-left: `PREPARED BY` block. |
| 2 | 2 — Executive Summary | `exec_summary.html` | light | Big page title + standfirst. Body left, AT A GLANCE side panel right. 3 pillar cards across bottom. |
| 3 | 3 — Our Understanding | `understanding.html` | light | 2×2 cards with red left-edge rules. Sections: Venue & Context, Goals, Constraints, Success. |
| 4 | 4 — Creative Vision | `creative_vision.html` | dark | Title + standfirst. Design direction phrase as hero ("Bayside Twilight."). Hero image right. 3 phase cards bottom. |
| 5 | 5 — Zone (solo, light) | `zone_solo.html` | light | Single zone — `ZONE 0N` red eyebrow + zone name + standfirst. Bullet list left, hero image right. Used for non-signature zones. |
| 6 | 7 — Zone (solo, full-bleed) | `zone_solo_fullbleed.html` | dark | Single "signature" zone. Hero image top half (full-bleed). Dark text panel bottom: `ZONE 0N` + name + standfirst + 2-column bullets. |
| 7 | (new — for zone-heavy) | `zone_2up.html` | light | Two zones share a slide. Each zone gets its `ZONE 0N` red eyebrow + name + standfirst + bullet list, side-by-side. Page title (top of slide): `Program Zones`. |
| 8 | (new — for zone-heavy) | `zone_3up.html` | light | Three zones per slide. Used when total zone count is high (7+). Page title `Program Zones`. |
| 9 | (new — for zone-heavy) | `zone_index.html` | light | Overview slide listing all zones at a glance before drilling into them. Used when total zone count ≥ 5. Page title `The Program at a Glance`. |
| 10 | 8 — Scope of Work | `scope.html` | light | Two cards: green-headed `YOUR PROGRAM INCLUDES` (left) + red-headed `OPTIONAL ADD-ONS` (right). Inline `+$NK` prices on add-ons. |
| 11 | 9 — Case Study | `case_study.html` | light | Page title + standfirst. Hero image left, three stacked sections right: `THE CHALLENGE`, `OUR APPROACH`, `THE OUTCOME` — each with red caps label. |
| 12 | 10 — Investment | `investment.html` | light | Three tier cards (Essential gray-rule / Enhanced red-banner-recommended / Signature navy-rule), big prices, MULTI-YEAR PARTNERSHIP discount strip in dark bg below. Footer note about pricing validity. |
| 13 | 11 — Terms & Next Steps | `terms.html` | light | Full-width brand-red date banner showing 2 critical dates (Signing Deadline + Fabrication Lock). 2×2 cards below: Payment, Insurance, Change Orders, Validity. Dark bottom strip with "AFTER APPROVAL →" workflow. |
| 14 | 12 — Sign-off | `sign_off.html` | light | "Let's Make It Happen" page title (dropped the more reserved "Acceptance / Authorization"). What-you're-approving recap above two side-by-side signature blocks. Footnote about Canva digital signing. |
| 15 | 13 — About St. Nick's | `about.html` | dark | Page title + standfirst. Two-column body: THE COMPANY (license #s, insurance limits, founding year) + YOUR TEAM (real team with roles). Bottom: brand-red contact strip with phone + address + copyright. |

## 6. Brand system additions (`skill_assets/layouts/brand.css`)

**Existing tokens (locked from Plan 2 and remain unchanged):**
- All 5 colors (`--color-red`, `--color-charcoal`, `--color-gray`, `--color-navy`, `--color-light`).
- All type scale tokens (`--text-xs` through `--text-3xl`).
- All space tokens (`--space-1` through `--space-8`).
- Page geometry (13.333" × 7.5" landscape).
- `--font-heading: "Roboto", sans-serif`, `--font-body: "Poppins", sans-serif`.

**New tokens:**
- `--color-panel: #F2F2F2;` — light gray card background. Distinct from `--color-light: #ECEFF1` which stays for type on dark backgrounds.
- `--color-green: #1B7A3F;` — Scope page "YOUR PROGRAM INCLUDES" green header. Only used there.
- `--font-display: "Poppins", sans-serif;` — declared so layouts can opt in to the heavy display weight via `font-family: var(--font-display); font-weight: 900;`. Same family as `--font-body`, but the token signals intent.

**New `@font-face`:**
- `Poppins-Black.ttf` (weight 900, normal). Sourced from fontsource CDN — same source as the other Poppins weights.

## 7. Test fixtures (two of them)

**Fixture 1: `tests/fixtures/pier_39.py`** — destination-style, 3 zones.

Built directly from the master pptx content — Pier 39, San Francisco, 3 zones (Embarcadero Arrival / Pier Promenade / Bay Terrace), Bayside Twilight design direction, $225K / $345K / $485K tier pricing. Drives `cover`, `exec_summary`, `understanding`, `creative_vision`, `zone_solo` (×2 for zones 1+2), `zone_solo_fullbleed` (×1 for signature zone 3), `scope`, `case_study`, `investment`, `terms`, `sign_off`, `about`.

This fixture stays close to master content — no fabrication. It's the canonical "destination-style" reference.

**Fixture 2: `tests/fixtures/riverside.py`** (repurposed) — zone-heavy, multi-station civic.

Reshape the existing Riverside data to match the new layout schema. Change "showcase categories" (Pole Decor, Platform & Plaza, etc.) into proper named zones: 5–6 zones representing 5–6 stations on the MetroLink line (Downtown Riverside, La Sierra, Pedley, Riverside-Hunter Park, Moreno Valley, etc.). Drives the `zone_2up` / `zone_3up` / `zone_index` layouts with realistic content.

This fixture proves the layout variants work when zone count is high. It also serves as the "zone-heavy path" Daniel asked about — Plan 3's parser will pick layouts based on zone count.

**Tests:**
- `tests/test_layouts.py::LAYOUT_CASES` gets 15 entries (one per layout). Each entry references one of the two fixtures. Fixtures are imported once at the top of the test module and switched per-case via the existing `ctx_attr` mechanism.
- The `test_all_layouts_rendered` gate (already generalized — see Plan 2's commit `0dc8fa2` history) continues to enforce that every PDF named in `LAYOUT_CASES` exists on disk.
- Per-layout font assertion stays at the existing pattern: every PDF must embed Roboto + Poppins. Layouts that use Poppins Black must also embed it (since WeasyPrint subsets fonts to only what's used) — checked via `_assert_font_family_present(doc, "Poppins")` which substring-matches all Poppins variants.

## 8. Tone modifications (vs the master)

Daniel said "with some modifications." Captured here:

- **Audience tags removed** (decision 2 above).
- **No other content changes confirmed yet.** The master's tone — "Lock in rates and save", "Sign by Nov 14 to guarantee install", `★ RECOMMENDED ★` — stays. If Daniel surfaces other tone tweaks during the eyeball pass, they're handled as inline plan edits, not spec revisions.

## 9. Out of scope (deferred to Plan 3)

- **AE workflow** for choosing which zone layout (`zone_solo` vs `zone_2up` etc.) gets used per project. Plan 2-prime ships all 5 zone variants; Plan 3 picks based on zone count from the scope worksheet.
- **AE workflow** for picking cover hero image and zone hero images. Existing project memory ("AE chooses cover/hero images, system never picks defaults") still applies.
- **Real St. Nick's logo file.** Until one lands, the brand wordmark is set typographically in Roboto Bold + Roboto Regular small caps tag. Replaceable later when an SVG/PNG logo asset exists.
- **Real past-work photo library** for the Case Study slide. Until one exists, the test fixture references a placeholder rendering from the project's own folder.
- **Real St. Nick's data** (license #, insurance limits, team roster) for the About slide. The Pier 39 fixture uses the master's authored content; the Riverside fixture should use the same St. Nick's company data (it's the same company, regardless of project).

## 10. Archive plan

**Move (not delete) Plan 2's iteration-1 work to `archive/iteration-1-abstract-layouts/` at repo root:**

Files moved (from `skill_assets/layouts/`):
- All 18 `.html` files (cover, exec_summary, understanding, creative_vision, showcase_hero, showcase_2up, showcase_3up, showcase_4up, showcase_fullbleed, scope, sample_of_work, case_study, investment_tiered, investment_single, add_ons, terms, sign_block, about).

Files copied (from `tests/_output/`, since `_output/` is gitignored):
- All 18 rendered `.pdf` files. Filenames kept identical (`cover.pdf`, `exec_summary.pdf`, etc.) so they pair 1:1 with the HTML files in the same archive folder.

Files added:
- `archive/iteration-1-abstract-layouts/README.md` — explains: this was Plan 2 (May 1 spec, May 1–2 implementation), abstract showcase-driven layouts, superseded May 3 by master-driven design. Kept for visual comparison and "what not to do." Includes a one-paragraph postmortem with links to both spec files.

Files preserved in `skill_assets/layouts/`:
- `brand.css` (with Plan 2-prime additions per §6)
- `base.html` (unchanged Jinja2 shell)
- All 15 new layout files (added during Plan 2-prime execution).

Files preserved in `skill_assets/fonts/`:
- All 5 existing fonts (Roboto Bold/Regular, Poppins Light/Regular/Medium).
- New: Poppins-Black.ttf.

Files removed from tree:
- `skill_assets/layouts/cover_typographic.html` and `showcase_typographic.html` — never existed in tree (the addendum spec was committed but not implemented). Just don't create them.

Spec files preserved in `docs/superpowers/specs/`:
- The original 2026-05-01 Plan 2 spec stays in tree with a status banner added: `**Status: SUPERSEDED 2026-05-03 — see plan-2-prime spec.**` at the top. Same for the 2026-05-03 typographic-fallback spec.
- Both prior plan documents in `docs/superpowers/plans/` get the same banner.

## 11. Files added / modified

**Added:**
- `skill_assets/fonts/Poppins-Black.ttf`
- `skill_assets/layouts/cover.html` (overwrites old)
- `skill_assets/layouts/exec_summary.html` (overwrites old)
- `skill_assets/layouts/understanding.html` (overwrites old)
- `skill_assets/layouts/creative_vision.html` (overwrites old)
- `skill_assets/layouts/zone_solo.html` (new pattern)
- `skill_assets/layouts/zone_solo_fullbleed.html` (new pattern, replaces showcase_fullbleed)
- `skill_assets/layouts/zone_2up.html` (new)
- `skill_assets/layouts/zone_3up.html` (new)
- `skill_assets/layouts/zone_index.html` (new)
- `skill_assets/layouts/scope.html` (overwrites old; note: old version had no add-ons inline pricing or green/red headers)
- `skill_assets/layouts/case_study.html` (overwrites old)
- `skill_assets/layouts/investment.html` (overwrites old; replaces both investment_tiered and investment_single — single layout per master)
- `skill_assets/layouts/terms.html` (overwrites old)
- `skill_assets/layouts/sign_off.html` (replaces sign_block; renamed to match master's "Sign-off" terminology)
- `skill_assets/layouts/about.html` (overwrites old)
- `tests/fixtures/pier_39.py`
- `archive/iteration-1-abstract-layouts/` directory + 18 HTML + 18 PDF + README.md

**Modified:**
- `skill_assets/layouts/brand.css` — add Poppins-Black `@font-face`; add `--color-panel`, `--color-green`, `--font-display` tokens.
- `tests/test_fonts_present.py` — add Poppins-Black to `REQUIRED_FONTS`.
- `tests/test_brand_css.py` — assert new tokens + new `@font-face` url present.
- `tests/fixtures/riverside.py` — reshape from showcase-categories to multi-station zones (~5–6 zones).
- `tests/test_layouts.py` — replace `LAYOUT_CASES` with 15 new entries (one per layout from §5).

**Removed from `skill_assets/layouts/` (moved to archive):**
- All 18 layout files leave the active tree. Of those:
  - **10 have no successor** in Plan 2-prime and are removed entirely from `skill_assets/layouts/`: `showcase_hero`, `showcase_2up`, `showcase_3up`, `showcase_4up`, `showcase_fullbleed`, `sample_of_work`, `investment_tiered`, `investment_single`, `add_ons`, `sign_block`. Their HTML lives only in `archive/`.
  - **8 have a same-named successor** with new content (`cover`, `exec_summary`, `understanding`, `creative_vision`, `scope`, `case_study`, `terms`, `about`). For these: the original is copied to `archive/` first, then the file at `skill_assets/layouts/<name>.html` is overwritten with the new Plan 2-prime version.
- All 18 corresponding PDFs from `tests/_output/` are copied to `archive/iteration-1-abstract-layouts/` (one per HTML, same base filename).

## 12. Verification

Plan 2-prime is done when:
- All 15 layouts render to PDF via the existing `render_layout` test helper.
- `pytest -v` passes (test count: existing baseline + 15 layout cases + 1 generalized gate test + new font-presence + new brand-css token tests).
- Manual eyeball pass: each rendered PDF compared visually against the corresponding master pptx page. No layout should feel "blander" than the master — that was the failure mode of Plan 2.
- Brand standards confirmed: every PDF embeds Roboto + Poppins (no other families), uses only the 5 brand colors plus `--color-panel` (`#F2F2F2`) and `--color-green` (`#1B7A3F`), respects the type scale tokens.
- Archive folder exists with 18 HTMLs + 18 PDFs + README; old spec files have superseded banners.
