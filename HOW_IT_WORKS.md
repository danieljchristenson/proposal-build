# How the Proposal Builder Works

A plain-language overview of how proposals get built day to day: who does
what, where everything lives, and how the engine, the AEs, and the creative
renderings fit together.

For the AE step-by-step, see `skill_assets/AE_SOP.md`.
For the technical/deployment detail, see `CLAUDE.md`.

---

## The mental model: 3 pieces that stay separate

```
   PEOPLE                 DATA                          ENGINE
   (AEs + operator)       (SharePoint team site)        (the build machine)
   prep + review    →     Creative Deliverables    ←    proposal_build
                          /Projects/<project>/          (Python + WeasyPrint)
                          ▲ renderings, Brief,          points at a project,
                          │ worksheet, output PDFs      reads it, writes the
                          └─ syncs to the Mac ──────────┘ deck back into it
```

- **The engine** is software (Python + WeasyPrint). It lives in the **git repo
  on the build machine (Daniel's Mac)**, with GitHub as backup. That is the
  *only* place it runs — not on AE machines, not on SharePoint. A shared drive
  is storage; it cannot run software.
- **The data** — every project — lives in the **Creative Deliverables
  SharePoint team site**. The build machine sees it locally through a OneDrive
  shortcut, and it syncs both directions automatically.
- **The people** never touch the engine. AEs prepare inputs; the operator runs
  generation.

---

## Where everything lives

| Thing | Home |
|---|---|
| The engine (code) | Git repo on the build machine + GitHub. **Never** on SharePoint. |
| Active projects | `Creative Deliverables/Projects/<project>/` (SharePoint team site) |
| Renderings | Inside each project: `02 - Renderings/` |
| Brief | Inside each project: `04 - Process & Notes/Project Brief.md` |
| Worksheet | Inside each project: `03 - Scope & Pricing/<project> - Scope Worksheet.xlsx` |
| Generated decks + pricing PDFs | Inside each project: `03 - Scope & Pricing/` |
| Test fixtures (e.g. Riverside) | Git repo only |

SharePoint site root:
`https://uniconfin.sharepoint.com/sites/BrendaSteph/Shared Documents/Creative Deliverables/`

---

## The process (who does what)

**1. Creative team** drops renderings into a project's `02 - Renderings/_inbox/`
(with their `Revise → Approved → Curated Finals` review flow). The project
folder already exists with the standard `01–05` structure.

**2. The AE** — their whole job is files in SharePoint, no software:
- Fills the **Brief** (`Project Brief.md`, the Phase-1 intake template) and
  flips `status: ready`.
- Fills the **Worksheet** (scope + tier pricing).
- **Curates renderings**: moves the *final* shots from `_inbox` into
  `Base Scope/` (and `Enhancements/`), and names a `cover_image`.
- Pings the operator: "X is ready."

**3. The operator (Daniel)** — on the build machine:
- Appends the **Phase-2** Brief fields (presenter, voice, schedule,
  `cover_image`, pricing format) — the part the intake template expects the
  builder to add.
- Runs the engine against the project's path.
- The **deck + per-tier pricing PDFs** write straight back into
  `03 - Scope & Pricing/` and sync to everyone (use `--compress` for an
  emailable file size).

**4. The AE** reviews the PDFs in their folder, optionally polishes in
**Canva** (manual upload → tweak → export), and sends.

```
AE preps in SharePoint → auto-syncs to the Mac → operator runs the engine →
deck auto-syncs back to SharePoint → AE reviews / polishes / sends
```

---

## How the renderings flow ties in

The creative team and the proposal builder share **one home** (the Creative
Deliverables site), so renderings are never copied around. They originate in
`_inbox`, get reviewed there, and the AE promotes the finals into
`Base Scope`/`Enhancements` — which is exactly where the engine reads them.
That curation step (which images make the pitch) is deliberately the AE's call,
not automatic.

---

## Why the engine runs centrally (and not on each PC)

WeasyPrint (the PDF renderer) needs native system libraries (Pango/Cairo/GTK)
installed on whatever machine runs it. Getting that working on every Windows
PC is fragile and high-maintenance, and Claude Desktop's skill sandbox can't
run local software either. So generation is **centralized** on one machine that
has the libraries set up. AEs get a finished deck without installing anything.

---

## What's running today vs. later

- **Today — operator-driven:** AE preps a project, flips `status: ready`, and
  the operator runs the engine. Works now, zero extra infrastructure.
- **Later — self-serve watcher (optional):** a watcher on the build machine
  detects a project flipped to "ready" and auto-generates, removing the operator
  step. Worth adding only when the manual step becomes a bottleneck. A dedicated
  always-on build machine (e.g. a Mac mini) would make this fully hands-off.

---

## One-line summary

**AEs prepare projects in SharePoint, the operator presses go on the build
machine, and finished decks come back to SharePoint.**
