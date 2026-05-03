# Plan 2 Iteration 1 — Abstract-Driven Layouts (archived)

**Status:** Superseded 2026-05-03 by Plan 2-prime (master-driven layouts).

This directory contains the 18 layouts shipped by Plan 2 (May 1–2, 2026) along
with their rendered PDFs. They are kept here for reference: side-by-side visual
comparison with the master deck and Plan 2-prime's output, and as a worked
example of what *not* to ship.

## Why archived

The original Plan 2 spec (decision 6) called the master pptx an "informal
directional reference only" and produced a fresh modern redesign. The output was
technically clean but bland and structurally wrong:

- Abstract layouts (`showcase_2up`, `showcase_3up`) instead of zone-driven slides
  customers can map to physical parts of their property.
- St. Nick's branding hidden — only on the cover and About page, not as
  persistent header/footer.
- Pricing reserved — tier numbers and add-on costs were set small or absent.
- Tone was civic-procurement reserved, not the confident sales tone of the
  master.

Daniel rejected the output on 2026-05-03. Plan 2-prime uses the master pptx as
the literal reference instead.

## What's here

- `*.html` — the 18 Jinja2 layouts (page chrome + design tokens via `brand.css`)
- `*.pdf` — rendered output as of the final Plan 2 commit. Eyeball these
  alongside the new layouts to see the gap.

## Original specs + plans

- Spec: `docs/superpowers/specs/2026-05-01-plan-2-brand-layout-design.md`
- Plan: `docs/superpowers/plans/2026-05-01-02-brand-layout-system.md`
- Replacement spec: `docs/superpowers/specs/2026-05-03-plan-2-prime-master-driven-design.md`
- Replacement plan: `docs/superpowers/plans/2026-05-03-plan-2-prime-master-driven-layouts.md`

A typographic-fallback addendum (cover_typographic.html, showcase_typographic.html)
was scoped on 2026-05-03 morning but never executed; its spec/plan are also
marked superseded.
