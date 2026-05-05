# Riverside v3 polish — session handoff (2026-05-05)

**Status:** All v3 polish work landed on branch `riverside-v3-polish`. 124/124 tests
passing, Riverside regenerates cleanly, both Essential and Enhanced itemized
pricing PDFs ship in the new Zoho-style template, and the About slide is a
light-theme Company Profile page modeled on the Tachi Christmas reference.

## What landed

### Itemized pricing PDFs — Zoho-style redesign

Source files: `skill_assets/layouts/itemized_pricing.html` (layout-version
`2026-05-05`), `skill_assets/proposal_build/renderer/pricing_pdf.py`.

- Removed the heavy dark "ITEMIZED COST BREAKDOWN" hero band and the gray
  6-cell meta panel from page 1. Page-1 chrome now takes ~1.5in instead
  of ~3in.
- New compact header: small St. Nick's logo + company address top-left,
  "Proposal Pricing" + "{Tier} Tier" red eyebrow top-right.
- New Bill To strip: client_company + client contact (name, title, email,
  phone) on the left; Quote Date / Project / Valid (60 days) right-aligned,
  `white-space: nowrap` so values never wrap.
- Table rebuilt as 6 columns: `# / Item & Description / Qty / Unit / Rate /
  Amount`. Body 8pt with 2.5pt vertical padding for density. Group headers
  (Base Scope / Optional Enhancements) are bold black-on-white with a
  charcoal underline (no fill).
- Replaced the dark `TOTAL — {TIER} TIER` band with a single right-aligned
  `Total: $XX,XXX` row (1.5pt charcoal top rule).
- Page 2 (Payment Terms & Savings) layout kept; tightened spacing so the
  footer no longer orphans onto a 4th page. Phone number wrapped in
  `nowrap` spans so `(562)` and `438-0017` stay on the same line.

**Page count outcomes:**
- Essential: 2 pages ✅ (page 1 = 12 line items + Total, page 2 = Payment
  Terms & Savings).
- Enhanced: 3 pages — page 1 holds 15 of 17 items, items 16-17 + Total spill
  to page 2, Payment Terms is page 3. Daniel accepted this rather than
  truncate item 16's long description ("12 ft wide custom-fabricated
  illuminated 'Happy Holidays' overhead marquee with skyline silhouette,
  PVC mesh, warm-white channel-letter LED + rope light, span-mounted
  between columns") or shrink fonts further.
- Signature still generates but isn't part of the customer-facing bundle
  per Daniel.

### Zone-feature slides — small white panel bottom-left

Source: `skill_assets/layouts/zone_feature.html` (layout-version `2026-05-05`).

- Removed the dark gradient scrim that overlaid white text on the image —
  Daniel: "tough to read, blended into the photo."
- New: a compact white panel anchored bottom-left (max-width 4.2in,
  ~0.20in padding, light box-shadow). Eyebrow red, zone name + subtitle +
  bullets all charcoal-on-white. Sized so the panel doesn't crowd the
  subject in either the Bell Display or Gift Box Tower hero shots.

### About slide — Company Profile light layout

Sources: `skill_assets/layouts/about.html` (layout-version `2026-05-05`),
`skill_assets/proposal_build/composer/ctx_builders.py` (`build_about_ctx`).

- Switched from dark theme to light/white background. Inspired by the Zoho
  RFP-compliance sample at
  `Master Proposal Reference/Reference company profile/RFP Ontario Airport - Summer Activations 2026 169.png`.
- "COMPANY PROFILE" big black uppercase title top-left (Poppins-Heavy ~38pt).
- 2-column body grid: team list on the left (name regular + role bold
  Roboto, both 14pt), company facts as red-bulleted list on the right (13pt).
- Big St. Nick's Santa logo in the bottom-right (1.5in wide, absolute
  positioned).
- Removed the red contact-strip footer.
- Removed the "25 years…" standfirst (now 29 years; Daniel chose to drop
  the tagline rather than update it).
- Tried adding a wreath hero strip image cropped from the Zoho sample,
  then removed it on Daniel's call so the type fills the page.

### Boilerplate + canonical facts updates

- `skill_assets/boilerplate/team.md`: Tyler Norwood removed entirely.
  Carlos Vasquez and Alonso Salazar split into separate "Sr. Installer &
  Project Manager" entries (was combined). 7 names total.
- `skill_assets/boilerplate/company_facts.md`: replaced the 6-bullet sales
  pitch with a 12-bullet RFP-compliance roster — Tax ID #68-0636192, T&G
  Global LLC (CA), LSBE Vendor #16942501, address, phone, fax, website,
  plus the kept-from-current insurance line and the "200+ commercial
  venues across North America" sales differentiator. Employee count
  updated to 27 year-round + 70 off-season per Daniel.
- `00_Company_Context/about_st_nicks.md`: years-in-business 28 → 29;
  Sales count 5 → 4 (Tyler removed from summary line).
- `00_Company_Context/org_chart.md`: Tyler Norwood row removed.

### Tests

- `tests/test_layouts.py`: about-slide expected text updated from
  `"About St. Nick's"` + `"ST-NICKS.COM"` to `"Company Profile"` (since
  the red contact strip is gone).
- All 124 tests pass.

## What did NOT change

- Cover and Creative Vision layouts: untouched. Daniel reported missing
  content there based on reading the v2 FINAL PDF (which shipped with
  empty WELCOME/JOURNEY/ARRIVAL cards and no Prepared For/By blocks).
  The v3 generation already has all that content. Confirmed by re-reading
  the regenerated `Riverside MetroLink - 2026 Holiday Proposal.pdf`.
- Em-dash linter and validator hardening from plan-3-ratification: still
  passing on Riverside.

## Workflow note for future sessions

Daniel uses Canva to fine-tune the generated PDF before sending to the
customer. **Canva re-flows text on PDF import** — word spacing, kerning,
and sometimes line breaks change. This is a Canva-side limitation
(Canva's PDF parser doesn't honor embedded font metrics). Two paths
worth exploring later:
1. Outline text glyphs before final export (loses Canva-side text
   editability but preserves layout exactly).
2. Test alternate font embedding strategies (e.g. embed-all vs subset).

Tabled as a workflow concern — not blocking ship.

## Suggested next focus — Plan 8

Plan 8 scope (per spec §13 of `2026-05-03-plan-3-phase-2-generation-design.md`
and the markers left in `2026-05-01-01-repo-restructure-skill-scaffolding.md`):
finalize the deployable Claude Desktop skill bundle —
`skill_assets/AE_SOP.md` (the AE-facing standard operating procedure)
and `skill_assets/skill.md` (the skill manifest Claude reads when the
skill is invoked). No plan file written yet for this; brainstorm scope
with Daniel before writing one and executing.

## Verify locally

```bash
git checkout main
git pull
source .venv/bin/activate
pytest                                                    # 124 passing
python -m proposal_build generate "Projects/Downtown Riverside Metro Link" --use-latest-layouts
python -m proposal_build generate "Projects/Downtown Riverside Metro Link" --use-latest-layouts --compress
```

Check the regenerated PDFs in `Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/`:
- `Riverside MetroLink - 2026 Holiday Proposal.pdf` — proposal deck (21 slides;
  cover with Prepared For/By blocks, filled Creative Vision cards, Bell +
  Gift Box bottom-left white panels, light-theme Company Profile slide).
- `Riverside MetroLink - 2026 Itemized Pricing - Essential.pdf` — 2 pages.
- `Riverside MetroLink - 2026 Itemized Pricing - Enhanced.pdf` — 3 pages
  (Daniel accepted this rather than truncate item 16).
