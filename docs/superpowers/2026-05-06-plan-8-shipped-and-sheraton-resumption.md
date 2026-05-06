# Plan 8 shipped + Sheraton San Diego resumption note (2026-05-06 evening)

## Plan 8 — DONE

Merged to `main` at commit `7acb2e6` and pushed to `origin/main`. The
deployable Claude Desktop skill bundle is live. 158/158 tests pass.

**Key files for tomorrow's reference:**
- `skill_assets/skill.md` — the Claude Desktop skill manifest, now with
  hardened CRITICAL preamble + Brand reference. Imperative MUST/MUST NOT
  rules prevent renderer-bypass.
- `skill_assets/AE_SOP.md` — operator-facing SOP for AEs.
- `skill_assets/proposal_build/` — the Python module (inspector,
  scaffold, CLI, parser, composer, renderer).
- `skill_assets/layouts/brand.css` — locked brand standards (red
  `#B31315`, charcoal, light, panel, Roboto + Poppins). Source of truth.

## Bugs fixed today (separate from Plan 8 task list)

**1. Ghostscript `/ebook` compression dropping body text** (`b97663f`).
Pre-existing bug from before Plan 8 — every `--compress` run silently
lost any text element styled with `opacity: N`. Symptom: Riverside's
Creative Vision page rendered with empty body bullets in the compressed
1.9MB PDF; uncompressed 99MB version had them. Fix: replaced every
text-level `opacity:` with `rgba()` colors across `brand.css`,
`cover.html`, `creative_vision.html`, `investment.html`, `terms.html`,
`zone_feature.html`. Verified compressed deck now preserves all bodies.

**2. Skill.md hardened against renderer-bypass** (`364b7f6`). T13
smoke surfaced two Desktop runs (Riverside dark-green-serif, Sheraton
navy-gold) where Claude improvised a custom proposal instead of running
`python -m proposal_build generate`. Root cause: descriptive manifest
wording. Fix: added imperative CRITICAL preamble at the top of
`skill.md` with explicit MUST/MUST NOT rules. Validated: Cowork-Claude
twice refused to bypass after the fix landed.

## T13 status

T13 was "manual smoke test in Claude Desktop + merge to main." We
shipped the merge but T13 wasn't fully validated in Desktop's local
runtime — see "Desktop UX gap" below. The skill code itself was
validated end-to-end via local regen (`b97663f` verification).

## The Desktop UX gap (CRITICAL — read before any AE smoke test)

**Claude Desktop the Mac app contains TWO different runtimes that look
identical in the chat UI:**

| Runtime | Where bash runs | Skill works? |
|---|---|---|
| **Local chat** | On the user's Mac, real filesystem, real venv | YES |
| **Cowork** (a feature *inside* Desktop) | Cloud Linux sandbox, no path to Mac | NO |

Daniel was in Cowork all day today thinking he was in local Desktop.
Every error (`/usr/bin/python`, broken venv symlinks, `Linux x86_64`)
was the Cowork runtime. The filesystem MCP we configured (`~/Library/
Application Support/Claude/claude_desktop_config.json`) only attaches
to **local** chats.

**Definitive test for runtime, paste in any chat:**
> *"Run `pwd && uname -a` in bash."*

- `/Users/Daniel-Admin/...` + Darwin → local, skill works.
- `/`, `/home/`, `/workspace/` + Linux → Cowork, skill won't work.

**To start a local chat in Desktop:** UI varies by version. Look for a
"+ New chat" without "Cowork" in the name. If everything routes through
Cowork by default, check Settings → Developer / Tools / Privacy for a
"Code Dispatch" or "Cowork as default" toggle to disable. The user's
config has `dispatchCodeTasksPermissionMode: "default"` — that may be
what auto-routes code-running chats to Cowork on Pro/Max plans.

If Daniel can't find the local-chat option, fastest workaround is to
run the skill from this Claude Code CLI session (the terminal one),
which is always local.

## Sheraton San Diego Resort — paused mid-work

**Status:** brief + worksheet + renderings are on disk in
`Projects/Sheraton San Diego Resort/`. Generation NOT attempted.
Daniel chose path A (ship Plan 8 tonight, do Sheraton tomorrow) after
realizing the actual scope was larger than the 30-min estimate I gave.

**Why Sheraton needs more work than a regenerate:**

1. **Brief schema mismatch.** Cowork-Claude wrote
   `Projects/Sheraton San Diego Resort/04 - Process & Notes/Project
   Brief.md` in a completely different schema than our parser expects.
   It has fields like `client_contact`, `ae_owner`, `tiers: [list]`,
   `install_year`, `program_type` — none of which our parser reads.
   It's missing required fields: `client_short`, `project_short`,
   `project_year`, `voice`, `recommended_tier`, `pricing_format`,
   `cover_image`, `design_phrase`, plus all `presenter_*` and
   `client_contact_*` (note: presenter is the AE, not the client).
   It has prose sections "Property Overview", "Scope Summary",
   "Logistics & Schedule", "Investment Summary", "Notes", "Open Items"
   — none of which match our required prose sections (Creative
   Direction, Customer Goals, Customer Constraints, Success Criteria,
   What You're Approving). Compare against the canonical Riverside
   brief at `Projects/Downtown Riverside Metro Link/04 - Process &
   Notes/Project Brief.md` for the right format.

2. **Worksheet 2-tier vs 3-tier mismatch.** Cowork-Claude wrote
   `Worksheet - Sheraton San Diego.xlsx` (note: filename should be
   `Sheraton San Diego Resort - Scope Worksheet.xlsx` to match parser
   conventions) with 2 tiers (Tier 1 — Base, Tier 2 — Premium). Our
   parser only accepts the literal strings `Essential`, `Enhanced`,
   `Signature` (case-insensitive) in the Tiers column. Daniel chose
   to add a synthetic 3rd Signature tier rather than do a single-tier
   proposal.

3. **Folder layout divergence.** The Sheraton folder has `01 - Brief`
   (canonical: `01 - RFP`), missing `02 - Renderings/Enhancements/`
   and `02 - Renderings/Unused Renderings/`, and a stray
   `Renderings/` plus `02 - Renderings/_archive/`. Inspector will
   flag these as `folder / missing-subdir` blockers.

**What's already good:**

- 15 zone renderings in `02 - Renderings/Base Scope/` are properly
  named (zone-numbered, descriptive). Re-usable as-is.
- Daniel's prose content (creative direction, scope philosophy,
  logistics dates) is correct AE work — just needs translating to our
  schema.
- The Brief's zone descriptions are detailed and good.

**Estimated work for tomorrow (~1.5–2h focused):**

1. Translate Brief schema (~30 min). Keep the prose; rewrite frontmatter
   keys and add missing required fields. Daniel makes these decisions:
   - `voice`: `hospitality` (hotel)
   - `recommended_tier`: Essential / Enhanced / Signature
   - `cover_image`: pick from the 15 base-scope renderings
   - `creative_vision_hero`: pick a different one for page 4
   - `design_phrase`: short evocative phrase (e.g., "Coastal Holiday")
   - `pricing_format`: `tiered` (since he wants 3 tiers)
   - `client_contact_name/title/email/phone`: Mackenzie O'Toole, Director
     of Rooms, Mackenzie.O'Toole@sheratonsandiegohotel.com (no phone in
     current brief — confirm)
   - `client_short`: probably "Sheraton San Diego"
   - `project_short`: probably "Sheraton SD"
   - `project_year`: 2026
   - `proposal_date`: tomorrow's actual date
   - `go_live`, `season_end`, `signing_deadline`, `fabrication_lock`:
     Sheraton's brief has "Design approval deadline: June 20, 2026",
     "Holiday installation: November 1–15, 2026", "Lights on:
     November 15, 2026", "Removal: January 5–20, 2027" — translate.
   - 4 missing prose sections (Customer Goals, Customer Constraints,
     Success Criteria, What You're Approving): Daniel writes these.

2. Worksheet edits (~10 min mechanical + 30+ min creative):
   - Rename file to `Sheraton San Diego Resort - Scope Worksheet.xlsx`.
   - Bulk-replace Tiers column: `1` → `Essential`, `2` → `Enhanced`,
     `1,2` → `Essential,Enhanced`.
   - Define what the new Signature tier *adds* over Premium and price
     each new line item. Possible additions: full multi-color sphere
     mix (not A/B), expanded twinkle ceiling, Sheraton-branded gift
     tags throughout, annual whale-fountain refurb included. **Daniel's
     creative scoping decision.**

3. Folder cleanup (~5 min):
   - Rename `01 - Brief` → `01 - RFP`.
   - Create empty `02 - Renderings/Enhancements/` and `02 - Renderings/
     Unused Renderings/`.
   - Decide what to do with stray `Renderings/` and `02 - Renderings/
     _archive/` (probably move out of the project folder).

4. Run `inspect`, fix any remaining gaps (~20 min).

5. Run `generate`, verify output (~10 min).

**Non-negotiable visual outcome:** the Sheraton proposal must use
**St. Nick's brand** — red `#B31315`, Roboto + Poppins, St. Nick's logo
top-left of every page. NOT Sheraton's navy + gold. The renderer
enforces this; the only way it goes wrong is if Claude bypasses the
renderer (which the hardened manifest now prevents).

## Untracked / unstaged work-in-progress (carried over)

These exist on disk but are NOT in the merged Plan 8:

- `Projects/Sheraton San Diego Resort/` — entire folder (Brief,
  Worksheet, renderings, etc.). Daniel's pending work.
- `Projects/Downtown Riverside Metro Link/smoke test output/` — 2
  failed test attempts (Cowork's dark-green-serif Riverside, plus
  the rebuild test). Includes a 112MB `.pptx`. Should be deleted or
  moved out of Projects/ before any future commit.
- `Projects/Downtown Riverside Metro Link/03 - Scope & Pricing/
  Riverside MetroLink - Scope Worksheet - prebackup.xlsx` —
  Daniel's manual backup; keep it.
- `Master Proposal Reference/StNicks_Proposal_v2_Master.pdf` —
  carried over from before; not Plan 8 scope.
- `skill_assets/Branding/about_hero_strip.jpg` — carried over leftover
  from v3-polish.
- `git stash@{0}` — `desktop-session-bulk-stage-2026-05-06`. Contains
  the smoke-test-output bulk-stage from Desktop's stale-lock incident
  earlier today. Includes the 112MB `.pptx`. **Drop this stash before
  doing real work tomorrow** (`git stash drop`) — it was just a
  workaround for an index-lock collision. The files it stashed are
  either still on disk or no longer needed.

## How to resume in tomorrow's session

1. Open Claude Code (terminal CLI, not Claude.ai web, not Claude Desktop
   Cowork) at `/Users/Daniel-Admin/Documents/Claude/Projects/proposal-build/`.

2. Confirm baseline:
   ```bash
   git checkout main
   git pull origin main
   git log --oneline -1     # expect 7acb2e6 (Plan 8 merge)
   source .venv/bin/activate && pytest -q --tb=no | tail -2  # expect 158 passed
   ```

3. Drop the stash from today's git-lock workaround:
   ```bash
   git stash drop
   ```

4. Tell Claude: *"Resume the Sheraton San Diego Resort proposal from
   the resumption note `docs/superpowers/2026-05-06-plan-8-shipped-and-
   sheraton-resumption.md`. Drive the skill end-to-end from this CLI
   session. Start by translating the Brief schema in
   `Projects/Sheraton San Diego Resort/04 - Process & Notes/Project
   Brief.md` to match the canonical Riverside format, then move on
   to the worksheet."*

5. Before starting Sheraton work, Daniel should also have a separate
   short conversation about what to add as the Signature tier. That's
   the creative scoping question the AE owns.

6. After Sheraton ships, file Plan 9 (decouple skill from local repo
   so AEs can run it without cloning + brew + venv setup). Spec
   discussion is in this conversation's history near the end of the
   day.

## Plan 9 spec (preview)

The skill currently requires each AE to clone the repo, run
`brew install pango`, set up a `.venv` with Python 3.11+, pip install
the package editably, and mount the repo root in Desktop. That's a
high friction floor for non-developer AEs.

Plan 9 should investigate:
- Packaging `proposal_build` as a pip-installable wheel (with bundled
  layouts/fonts/branding so the skill is fully self-contained).
- Whether WeasyPrint + Pango/Cairo can ship in a way that doesn't
  require `brew install` per AE.
- Whether the skill can be made Cowork-compatible (Linux sandbox-
  friendly Python + system libs), or whether Local Desktop is the
  permanent runtime requirement.
- Storing project folders outside the repo (OneDrive / Box / Drive)
  so AEs aren't dependent on git.

Decision deferred until Plan 8 has been used in production for a few
proposals and we know what AE friction is real vs theoretical.
