# Premium Print/PDF Design-System Specs — Findings Brief

**Date:** 2026-06-09
**For:** St. Nick's Christmas Lighting & Décor — proposal-generation system redesign
**Render target:** 16:9 PDF decks via WeasyPrint (HTML/CSS → PDF), embedded TTF fonts
**Current tokens:** Roboto (headings) + Poppins (body); red #B31315, charcoal #1C1C1C, gray #555, navy #12355B, light #ECEFF1
**Leading direction:** dark-theme-forward (charcoal grounds, red accent, bold caps headlines, stat call-outs, color-coded zones, refined data viz)

---

## Executive summary

- **Roboto + Poppins is the single biggest "generic" tell.** Both are ubiquitous Google defaults with no editorial voice. The fastest, highest-impact upgrade is swapping in a high-contrast display serif for headlines and a refined grotesque for body. Premium = *contrast of voice* (one expressive face + one quiet workhorse), not more fonts.
- **Strongest pairing recommendation: Fraunces (display serif, headlines) + Inter or Archivo (body/UI/data).** Fraunces is open-source (Google Fonts / SIL OFL), variable, with an optical-size axis that adapts letterforms between display and text — it reads warm, editorial, and "crafted" rather than corporate, which fits a holiday-décor luxury brand. Inter/Archivo give razor-clean, neutral support with excellent tabular numerals for pricing.
- **Go warm-charcoal, not true black.** A layered surface system (e.g. #14110F base → #1C1A17 → #24211D) reads more premium and prints/screens better than #000. True black is harsh; warm near-blacks feel deliberate and expensive (the Tom Ford / Saint Laurent move is #0A0A0A near-black, never pure #000).
- **Add a restrained metallic accent (warm gold ~#C69B3C, not web-gold #FFD700).** Used at <5% coverage — hairlines, eyebrow labels, the "recommended tier" marker, rule dividers — gold against warm charcoal signals premium far more than more red would. Keep red #B31315 as the *brand* accent (CTAs, key stat); gold as the *luxe* accent.
- **Tabular lining figures are mandatory for all pricing/stat call-outs.** Use `font-variant-numeric: tabular-nums lining-nums` (WeasyPrint supports `font-variant-numeric`) so dollar columns align vertically. This is a craft signal reviewers feel even if they can't name it.
- **Whitespace and a real grid do more for "premium" than any single graphic.** A 12-column grid with generous, asymmetric margins (≈6–8% outer margin on a 1280×720 frame) and disciplined alignment is what separates editorial decks from template decks. Luxury = restraint and breathing room.
- **WeasyPrint feasibility constraint to design around: `box-shadow` and `text-shadow` are NOT supported, and flexbox/grid are only partially supported.** Lean flat: use hairline borders, layered background surfaces, and gradient scrims instead of shadows. Gradients, border-radius, opacity, 2D transforms, `object-fit`, and `font-feature-settings` ARE supported — so duotone/scrim photo treatment and OpenType numerals are all feasible.
- **Color-coded zones should share fixed saturation + lightness across hues.** Pick 5–7 hues evenly spaced on the wheel at one muted S/L (think Carbon/IBM categorical palettes), not random bright colors. On a dark ground, slightly desaturated mid-tones keep the system tasteful instead of carnival.
- **Three highest-impact specific changes:** (1) Replace Roboto+Poppins with **Fraunces + Inter** (or Archivo). (2) Replace single charcoal #1C1C1C with a **3-step warm-charcoal surface scale + warm gold accent**. (3) Adopt **tabular lining numerals + a stat-call-out pattern** (oversized number, small caps eyebrow label, hairline rule) for every price and metric.

---

## Typography spec

### The problem with the current pairing
Roboto and Poppins are two of the most-used Google Fonts on the web. Poppins (geometric, perfectly circular o's) reads friendly-startup; Roboto reads Android-system. Neither carries editorial gravity. Premium editorial design in 2025–26 is driven by a **serif revival** — high-contrast display serifs that create visual drama for headlines, paired with a clean neutral sans for body. The recipe: **two distinct voices** — an expressive display voice that "stops the scroll," and a quiet body voice that sustains comfortable reading.

### Recommended families (all embeddable, open-source / SIL OFL via Google Fonts)

**Display / headline serif — pick one:**

| Font | Character | Why for St. Nick's | Caution |
|---|---|---|---|
| **Fraunces** *(top pick)* | Soft "old-style" display serif; variable with weight, **optical-size (opsz)**, SOFT (rounding), WONK (irregularity) axes. Inspired by Windsor/Cooper/Souvenir. | Warm, characterful, "crafted/handmade" feeling that suits premium holiday décor; opsz means big headlines get dramatic contrast while smaller text stays legible. Reads festive-elegant, not corporate. | Dial WONK low for a refined (not quirky) feel. |
| **Newsreader** | Screen-optimized editorial serif; reads like a premium digital magazine. | Calmer, more "publication" than Fraunces; great if you want restrained editorial over warmth. | Less distinctive personality. |
| **Cormorant** / Cormorant Garamond | High-contrast Garamond revival, dramatic thick/thin, fashion-editorial at 24px+. | Very luxe at large display sizes. | Too delicate for small sizes; only for big headlines. Hairlines can thin out in print. |
| **Playfair Display** | Classic high-contrast display serif. | Safe, elegant. | **Overused to the point of feeling like a default** — avoid if differentiation matters. |

**Body / UI / data sans — pick one:**

| Font | Character | Why |
|---|---|---|
| **Inter** *(top pick for data)* | Neutral grotesque designed for screens; huge weight range; excellent tabular figures; 147 languages. | Disappears in service of content; rock-solid pricing tables; pairs cleanly under an expressive serif. |
| **Archivo** | Grotesque optimized for highly legible body + dashboards; more "editorial" personality than Inter. | Good if you want the sans to carry slightly more character (headlines could even use Archivo Expanded/Black for all-caps eyebrows). |
| **Manrope** | Semi-geometric, softer terminals, great numerics. | Warmer than Inter; good middle ground. |
| **Space Grotesk** | Mono-inspired, squared terminals, distinctive numerals. | Only if you want a techy edge — likely *off-brand* for holiday décor. |

### Recommended pairing (primary)
- **Headlines / display:** **Fraunces** — weights 600–900, optical size tuned to the size, italics for pull-quotes/zone names. Set bold caps headlines in Fraunces Black or use Inter/Archivo for the caps eyebrows (see below).
- **Body / captions / tables / stats:** **Inter** (or **Archivo**) — 400 body, 500–600 labels, 700 for emphasis.
- This is a textbook premium recipe: *expressive high-contrast serif headline + clean minimal sans body.* Look for contrast in shape and tone but balance overall.

**Alternative all-sans direction (if a serif feels wrong for the brand):** Archivo (display/expanded, caps) + Inter (body). Less editorial but very modern; keeps a single-family discipline.

### Numerals (critical for pricing)
- **Pricing tables, totals, stat call-outs:** **tabular + lining** figures so columns align: `font-variant-numeric: tabular-nums lining-nums;` (WeasyPrint supports `font-variant-numeric` and `font-feature-settings`). Inter, Archivo, Manrope all ship tabular figures.
- **Lining figures** (cap-height, uniform) are correct for **all-caps headlines and big number call-outs**.
- **Oldstyle / proportional figures** are calmer in running body prose — optional nicety, but **never** use them in a price column.
- Big-dollar call-outs: tabular lining, tightened tracking, with the `$` and `,` styled in the accent or a lighter weight for hierarchy.

### Type scale
- Use a **modular scale**. For a deck (few sizes, want clear jumps): **Perfect Fourth (1.333)** for drama, or **Major Third (1.25)** for a tighter, calmer hierarchy. Recommend **1.25 for body/label steps, 1.333+ for the display jump** (decks benefit from one big leap to the headline).
- Suggested scale (base 16px body on a 1280×720 frame; scale up proportionally if you render at a larger pixel canvas):
  - Eyebrow/kicker: 11–12px caps
  - Body: 15–16px
  - Lead/standfirst: 19–21px
  - Subhead (H3): 24–28px
  - Section head (H2): 36–44px
  - Slide headline (H1/display): 64–96px+ (Fraunces, opsz high)
  - Hero stat number: 96–160px
- **Line-height:** headlines tight (1.0–1.1); body comfortable (1.45–1.6); caps eyebrows 1.2.
- **Optical sizing:** Fraunces' opsz axis — set high opsz for big headlines (more contrast/drama), lower opsz for sub-display text.

### Caps eyebrows / kickers / labels
- All-caps labels **must** get positive tracking: **0.08em–0.12em** (≈ +80 to +120 in print units). Default-spaced caps look cramped because caps were drawn expecting lowercase neighbors.
- Spec: `text-transform: uppercase; font-weight: 600; letter-spacing: 0.1em; font-size: 11–12px;` — optionally in gold or gray for the eyebrow, above a Fraunces headline.
- Small caps (`font-variant-caps: small-caps`, supported) are an elegant alternative for labels/footers.

---

## Grid & whitespace spec

- **Canvas:** design to a fixed 16:9 frame. Pick one and lock it — e.g. **1280×720** (or 1920×1080 if you want more resolution headroom; ratios below are unit-independent).
- **Columns:** **12-column grid** is the workhorse for 16:9 (cleanly supports 2/3/4/6-up layouts and side-by-side comparisons the wide canvas invites). A simpler **6-column** works for sparse luxury layouts.
- **Margins:** generous and consistent. ~**6–8% outer margin** (≈ 80–100px left/right on 1280, ≈ 48–60px top/bottom). Snap *every* element to the same left/right/top margins — this single discipline is what makes a deck look uniform and intentional. Premium decks often run **asymmetric** margins (bigger left margin, content hung off a strong vertical axis) rather than dead-centered.
- **Gutters:** consistent (~16–24px). Keep a small set of spacing tokens (4/8/12/16/24/32/48/64) and use only those.
- **Baseline grid:** establish a vertical rhythm unit (e.g. 8px) and align type/blocks to it for cross-slide consistency (Müller-Brockmann grid discipline). Even loose adherence reads as craft.
- **Whitespace = the premium signal.** Negative space is not wasted; it's what makes content breathe and reads as confidence/value. Luxury communicates through restraint — fewer elements, more air. One hero idea per slide. Resist filling the frame.

---

## Color system spec

### Direction: warm dark grounds, not true black
True black (#000) is harsh and "dominates"; warm near-blacks feel refined and let adjacent gold/cream feel deliberate and expensive. Build a **layered surface scale** where each elevation step gets *lighter* (5–8% luminance), never shadowed (and recall: WeasyPrint has no box-shadow, so layered surfaces ARE your depth system).

### Proposed dark palette (hex)

**Surfaces (warm charcoal scale):**
- `--surface-0` base ground: **#14110F** (warm near-black; alt cooler #14161A if you want navy-leaning)
- `--surface-1` panel: **#1C1A17** (≈ today's #1C1C1C but warmed)
- `--surface-2` card/elevated: **#24211D**
- `--surface-3` hover/highest: **#2E2A25**

**Text on dark:**
- Primary: **#F4EADE** (warm ivory — softer than pure white, premium)
- Secondary: **#B8B0A6** (warm gray)
- Muted/captions: **#8A837B**

**Accents:**
- **Brand red:** **#B31315** (keep — CTAs, one key stat per slide, tier marker). On dark, consider a slightly brighter tint for legibility, e.g. **#D8232A**, reserving #B31315 for fills.
- **Metallic gold (luxe accent):** **#C69B3C** (warm, prints/foils clean; avoid #FFD700 web-gold which reads neon/cheap). Range #C69B3C–#D4AF37. Use for hairlines, eyebrow labels, "recommended" tier, dividers — **<5% coverage.**
- **Cream/champagne neutral:** **#EBDAB0** for subtle warm fills behind light moments.

**Light-theme pages (About / pricing PDF / compliance):** keep a light system for RFP-compliance pages — ivory **#F4EADE**/off-white ground, charcoal text, with the same gold + red accents so the two themes feel like one family.

### Color-coded zone system (tasteful multi-hue)
- Pick **5–7 hues evenly spaced on the wheel at ONE fixed saturation + lightness** (e.g. all at S≈45%, L≈55% on the dark ground). This is the Carbon/IBM categorical approach — consistency of S/L is what keeps many hues from looking like a carnival.
- Suggested muted set on warm charcoal (tune to brand): teal #4A9B8E, slate-blue #5B7FB5, plum #9A6BA0, amber #C9974A, sage #7FA45C, terracotta #B5715A, dusty-rose #B57A86. Each gets a tint/shade for fills vs. labels.
- Use the zone color as a **thin left rule / eyebrow color / small chip**, not as a full background flood — accents, not floods.

### Contrast / accessibility
- Body text on dark should hit **≥ 4.5:1** (#F4EADE on #14110F passes comfortably). Gold #C69B3C on #14110F is ~6:1 — fine for labels/large text; verify if used for small body.
- Red #B31315 on #14110F is low-contrast for small text — use brand red as a **fill behind ivory text** or as large elements, not small body copy.

---

## Photography treatment spec

Holiday-décor renderings are the emotional core; a consistent treatment is what turns a folder of renders into a "campaign."

- **Consistent duotone / scrim system.** Two routes, both WeasyPrint-feasible (gradients + opacity supported; blend modes are NOT, so do duotone in the asset pipeline if you want true duotone):
  - *Gradient scrim (CSS, no preprocessing):* layer a `linear-gradient` from `surface-0` (opaque at the text edge) to transparent over the photo so headline/caption text always sits on a controlled dark field. This is the reliable, automatable approach in WeasyPrint and guarantees legibility regardless of the underlying image.
  - *Duotone (preprocessed):* map image luminance to two brand tones (warm-charcoal shadows → ivory/gold highlights) in the asset pipeline for full-bleed mood/section dividers. Reserve full duotone for atmospheric moments, not money-shot renders (clients want to see real color on the actual décor).
- **Money-shot renders stay full color** with only a subtle bottom/edge scrim for text — don't recolor the product the client is buying.
- **Framing discipline:** pick one of {full-bleed} or {contained with consistent inset + corner radius} per slide *type* and never mix within a type. Full-bleed for hero/section dividers; contained (e.g. 8px radius, hairline gold/ivory border) for grid/gallery slides.
- **Consistent corner radius** across all contained images and cards (pick one: 0px for editorial-sharp, or 6–8px for soft-premium; recommend **a single small radius like 6px**, or 0 for a sharper editorial feel — be consistent).
- **Existing project rule honored:** zone full-bleed feature slides use a bottom-left white/ivory text card (black-on-light), not a dark scrim over the subject — keep that; it's already a good craft call.

---

## Data viz & pricing spec

### Stat call-out pattern (signature element)
A repeatable "stat block" is one of the cheapest ways to read premium:
```
EYEBROW LABEL          ← caps, 11px, 0.1em tracking, gold or gray
1,200                  ← Fraunces/Inter, 96–140px, tabular lining figures
linear feet of garland ← Inter 14px, secondary gray
─────                  ← hairline gold rule under or beside
```
- Numbers in **tabular lining** figures; unit/label small and quiet; one hairline rule. Let whitespace carry it.

### Pricing tables
- **Hairline-driven, not boxy.** Use 1px rules (`border`) in a muted gray/gold at low opacity; avoid heavy gridlines and avoid shadows (unsupported anyway). Generous row padding (12–16px vertical).
- **Right-align all currency**, tabular lining figures, consistent decimal handling. Single emphasized **Total** row (heavier weight or a thin gold rule above).
- Matches the existing Zoho-style itemized PDF intent (compact RFP header, 6-col table, single Total row, no dark hero band) — keep that template's restraint.

### Tier-comparison cards
- **Card per tier**, separated by hairline borders or a subtle surface step (`surface-1` vs `surface-2`) rather than shadows.
- **Plan name + price bold and large** (the first thing the eye hits); feature list smaller/lighter with check/dot markers.
- **"Recommended" tier:** differentiate with the **gold accent** (top border, eyebrow chip, or slightly elevated surface) — *not* a louder color. Restraint reads as confidence.
- Keep features as a tidy bulleted/checkmarked list; align across cards so rows compare cleanly.

### Charts
- Flat, few colors, lots of air. Use the categorical zone palette (fixed S/L) for series; label directly on the chart rather than relying on a legend where possible. Muted, not saturated. Hairline axes, no chartjunk, no 3D, no shadows.

---

## Micro-detail checklist (the craft signals)

- [ ] **Hairline rules** (1px, muted gray or gold at ~40–60% opacity) as dividers — never heavy lines. (No shadows available; hairlines do the separating.)
- [ ] **One consistent corner radius** everywhere (recommend 6px, or 0 for editorial-sharp). No mix.
- [ ] **Flat, layered depth** (surface scale) instead of drop shadows — forced by WeasyPrint, also more premium.
- [ ] **Caps eyebrow labels** with 0.08–0.12em tracking above headlines.
- [ ] **Tabular lining numerals** on every number that lives in a column or stat.
- [ ] **Gold accent kept under ~5% coverage** — hairlines, eyebrows, recommended-tier marker, key rule.
- [ ] **Consistent footer system:** small caps or tracked-caps page numbers + project name; gold or muted-gray hairline above footer. Tabular page numbers.
- [ ] **Eyebrow + headline + standfirst rhythm** repeated on every content slide for predictability.
- [ ] **Pull-quotes** in Fraunces italic, oversized, with a gold leading rule.
- [ ] **Spacing tokens only** (4/8/12/16/24/32/48/64) — no arbitrary margins.
- [ ] **Warm ivory text (#F4EADE), never pure #FFF**, on dark grounds.
- [ ] **Verify zone teal/jewel colors against the brand board** before shipping (jewel teal often reads green — known project pitfall).
- [ ] **No em dashes in customer copy** (existing rule) — applies to generated headlines too.

---

## Direct recommended token set for our system (concrete values)

```css
:root {
  /* Type families (embed TTFs in skill_assets/fonts/) */
  --font-display: "Fraunces", Georgia, serif;          /* headlines, pull-quotes, hero stats */
  --font-sans:    "Inter", "Archivo", Helvetica, sans-serif; /* body, labels, tables */
  /* (Optional: --font-display-alt: "Archivo" for all-sans direction) */

  /* Type scale (px on a 1280x720 frame; scale proportionally for larger canvas) */
  --fs-eyebrow: 11px;
  --fs-body:    16px;
  --fs-lead:    20px;
  --fs-h3:      26px;
  --fs-h2:      40px;
  --fs-h1:      80px;     /* slide headline, Fraunces, high opsz */
  --fs-stat:    128px;    /* hero stat number */
  --ratio: 1.25;          /* major third for steps; ~1.333 for the display jump */

  /* Line height */
  --lh-tight: 1.05;       /* headlines */
  --lh-eyebrow: 1.2;
  --lh-body: 1.55;

  /* Tracking */
  --track-caps: 0.1em;    /* eyebrows/labels: 0.08–0.12em */
  --track-stat: -0.01em;  /* slight tighten on big numbers */

  /* Numerals */
  --num-table: "tnum" 1, "lnum" 1;   /* font-feature-settings for tables/stats */

  /* Surfaces (warm charcoal scale) */
  --surface-0: #14110F;   /* base ground */
  --surface-1: #1C1A17;   /* panel */
  --surface-2: #24211D;   /* card / elevated */
  --surface-3: #2E2A25;   /* highest */

  /* Text on dark */
  --text-primary:   #F4EADE;   /* warm ivory, NOT #FFF */
  --text-secondary: #B8B0A6;
  --text-muted:     #8A837B;

  /* Accents */
  --brand-red:   #B31315;      /* fills, CTAs, one key stat */
  --brand-red-bright: #D8232A; /* red text/lines on dark for legibility */
  --gold:        #C69B3C;      /* metallic accent, <5% coverage */
  --champagne:   #EBDAB0;      /* warm light fill */

  /* Light-theme pages (About / pricing PDF / RFP compliance) */
  --light-ground: #F4EADE;
  --light-text:   #1C1A17;

  /* Zone categorical palette (fixed S~45% / L~55%; tune to brand board) */
  --zone-1: #4A9B8E;  /* teal */
  --zone-2: #5B7FB5;  /* slate blue */
  --zone-3: #9A6BA0;  /* plum */
  --zone-4: #C9974A;  /* amber */
  --zone-5: #7FA45C;  /* sage */
  --zone-6: #B5715A;  /* terracotta */
  --zone-7: #B57A86;  /* dusty rose */

  /* Geometry */
  --margin-outer: 7%;          /* ~88px on 1280 */
  --gutter: 20px;
  --radius: 6px;               /* one radius everywhere (or 0 for editorial-sharp) */
  --hairline: 1px solid rgba(198,155,60,0.5);  /* gold hairline */
  --space: 4 8 12 16 24 32 48 64;  /* spacing token set */
}
```

### WeasyPrint feasibility notes (design around these)
- **NOT supported — do not rely on:** `box-shadow`, `text-shadow`, `mix-blend-mode`/blend modes, CSS `filter`. → Use layered surfaces + hairlines for depth; preprocess any true duotone/blend in the asset pipeline.
- **Partial — keep simple, avoid page-breaks inside them:** `flexbox`, CSS `grid`. Simple single-page flex/grid layouts work; complex grids and flex items that must break across pages misbehave. For multi-row tables prefer real `<table>` markup.
- **Supported — safe to use:** `@font-face` with embedded/subset TTFs (Pango ≥1.38), `linear-gradient`/`radial-gradient` (your scrims + subtle surface gradients), `border-radius`, `opacity`, 2D `transform`, `object-fit`/`object-position` (image framing), `font-variant-numeric` / `font-feature-settings` (tabular lining figures), `font-variant-caps` (small caps), `font-kerning`, `font-variant-ligatures`.
- Net: the dark-theme, scrim-photo, tabular-numeral, hairline, layered-surface direction is **fully achievable** in WeasyPrint. The only thing the engine forces you away from — shadows — is the thing premium design avoids anyway.

---

## Sources

- Pangram Pangram Foundry — Best Sans/Serif Font Pairings 2025: https://pangrampangram.com/blogs/journal/best-font-pairings-2025
- Pangram Pangram — Type Pairings with Editorial New: https://pangrampangram.com/blogs/journal/pairings-editorial-new
- Soleil Sundays — Sophisticated Google font pairings for premium brand 2025: https://soleilsundays.com/blogs/theblog/5-sophisticated-google-font-pairings-to-build-a-premium-brand-in-2025
- Ink Narrates — Best Fonts and Colors for Pitch Decks: https://www.inknarrates.com/post/best-fonts-and-colors-for-pitch-deck
- Typewolf — The 40 Best Google Fonts: https://www.typewolf.com/google-fonts
- Typewolf — Space Grotesk combinations: https://www.typewolf.com/space-grotesk
- Google Fonts — Fraunces specimen: https://fonts.google.com/specimen/Fraunces
- Adobe Fonts — Fraunces Variable: https://fonts.adobe.com/fonts/fraunces-variable
- Typogram — How to Use Fraunces: https://typogram.co/font-discovery/how-to-use-fraunces-font
- Madegood Designs — Best Google Fonts: https://madegooddesigns.com/best-google-fonts/
- BonFX — What fonts go with Inter: https://bonfx.com/what-fonts-go-with-inter/
- Untitled UI — Best free fonts for modern UI 2026: https://www.untitledui.com/blog/best-free-fonts
- TotallyType — Lining Figures: https://totallytype.com/figures.php
- CreativePro — TypeTalk: Know Your Figures: https://creativepro.com/typetalk-know-your-figures/
- Fonts.com — Proportional vs. Tabular Figures: https://www.myfonts.com/pages/fontscom-learning-fontology-level-3-numbers-proportional-vs-tabular-figures
- Butterick's Practical Typography — Alternate figures: https://practicaltypography.com/alternate-figures.html
- CalculateY — Type Scale Calculator / ratios: https://calculatey.com/type-scale-calculator/
- Cieden — Types of typographic scales: https://cieden.com/book/sub-atomic/typography/different-type-scale-types
- Pimp my Type — Tracking & kerning for all caps: https://pimpmytype.com/spacing-all-caps/
- Techstacker — Uppercase letterspacing/tracking: https://techstacker.com/typography-uppercase-letterspacing-tracking/
- Stephen Kelman — 16:9 Presentation Grid System (InDesign): https://stephenkelman.co.uk/slide-deck-grid-system-for-adobe-indesign
- Katopis Designs — Müller-Brockmann grid systems & presentation design: https://katopisdesigns.com/blog/mullerbrockmann-gridsystems
- Deckary — PowerPoint design guide (layout/color/type): https://deckary.com/blog/pillar-powerpoint-design-guide
- Made Good Designs — Charcoal vs Black: https://madegooddesigns.com/charcoal-vs-black/
- Muzli — Dark Mode Design Systems (patterns/tokens/hierarchy): https://muz.li/blog/dark-mode-design-systems-a-complete-guide-to-patterns-tokens-and-hierarchy/
- EightShapes (Nathan Curtis) — Light & Dark color modes: https://medium.com/eightshapes-llc/light-dark-9f8ea42c9081
- Material Design — Dark theme / elevation: https://m2.material.io/design/color/dark-theme.html
- Toptal — Principles of Dark UI Design: https://www.toptal.com/designers/ui/dark-ui-design
- Zoviz — Luxury brand colors & palettes (hex), 2026 guide: https://zoviz.com/blog/luxury-brand-colors-meanings
- Design Work Life — Luxury color palettes 2026: https://designworklife.com/luxury-color-palettes/
- Figma — Metallic gold color/hex: https://www.figma.com/colors/metallic-gold/
- The New Drop — Metallic gold hex code guide: https://www.thenewdrop.co.uk/metallic-gold-hex-code/
- 99designs — The duotone effect: https://99designs.com/blog/trends/duotone-design/
- Adobe — Make a duotone effect: https://www.adobe.com/creativecloud/photography/discover/duotone-effect.html
- Carbon Design System — Data-viz color palettes: https://carbondesignsystem.com/data-visualization/color-palettes/
- data.europa.eu — Colour for categories: https://data.europa.eu/apps/data-visualisation-guide/colour-for-categories
- Cloudscape — Data visualization colors: https://cloudscape.design/foundation/visual-foundation/data-vis-colors/
- DiviFlash — Pricing table examples: https://diviflash.com/pricing-table-examples/
- WeasyPrint — Features / supported CSS (stable docs): https://doc.courtbouillon.org/weasyprint/stable/features.html
- WeasyPrint v62 release (Grid support): https://www.courtbouillon.org/blog/00051-weasyprint-62/
- WeasyPrint Issue #324 — Flexbox support/limitations: https://github.com/Kozea/WeasyPrint/issues/324
- WeasyPrint Issue #2076 — Page-breaks on grid/flex items: https://github.com/Kozea/WeasyPrint/issues/2076
