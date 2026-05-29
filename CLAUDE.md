# Proposal Builder — Repo Guide

This repo is a multi-session build of a Claude Desktop skill that turns
RFP + Brief + Worksheet + renderings into polished customer proposals.

## Read first

1. **Design spec:** `docs/superpowers/specs/2026-05-01-proposal-builder-skill-design.md`
2. **Active plans:** `docs/superpowers/plans/` — numbered `2026-05-01-NN-<name>.md`,
   one per subsystem. Execute in order. Plan 1 is the repo scaffolding;
   later plans build on top.

## Repo layout (locked by Plan 1)

- `00_Company_Context/` — always-on context (about, glossary, org chart).
- `Branding Board/` — brand assets, mood board, colors, typography.
- `Projects/`
  - `_master_templates/` — reference-only originals (master pptx, itemized pricing pdf).
  - `_template_project/` — blank duplicate-me-per-project skeleton.
  - `Downtown Riverside Metro Link/` — real test-fixture project (drives Plan 3+ end-to-end tests).
- `skill_assets/` — the deployable Claude Desktop skill bundle (populated by Plans 2–9).
- `docs/superpowers/{specs,plans}/` — design + execution artefacts.
- `tests/` — pytest. Start with `pytest tests/test_repo_structure.py`.
- `pyproject.toml` — runtime + dev dependencies.

## Toolchain

- Python 3.11+ (this machine runs 3.14 from python.org), pyproject.toml, pytest.
- Local dev: `python3.14 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`.
- WeasyPrint is the PDF rendering engine (chosen over python-pptx; spec §3).
- Fonts (Roboto + Poppins) are embedded in `skill_assets/fonts/` (Plan 2). Never load from system.

### Local macOS dev requirements (Plan 2 setup)

WeasyPrint depends on Pango/Cairo system libraries from Homebrew, not pip:

1. Homebrew installed at `/opt/homebrew/` (Apple Silicon path).
2. `brew install pango` — pulls in cairo, glib, harfbuzz, fribidi, etc.
3. `~/.zshenv` exports `DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_FALLBACK_LIBRARY_PATH"`
   so cffi's `dlopen` finds the libs at import time. Without this every
   WeasyPrint command fails with `cannot load library 'libgobject-2.0-0'`.

### Deployment: centralized generation (NOT a sandbox skill)

The skill (`skill_assets/skill.md`) is a **Bash orchestrator** — it shells out
to `python -m proposal_build inspect|generate "<project_dir>"`. It does NOT run
inside Claude's sandbox; it requires a machine with this repo installed (`pip
install -e .`) and WeasyPrint/Pango present. An earlier note here claimed "the
deployed skill bundle runs in Claude's sandbox where these libs are available"
— that was never true (a Claude Desktop Skills install of it failed with
`ModuleNotFoundError: proposal_build`, no Pango, no data access).

How it actually runs (decided 2026-05-29):

- **Generation is centralized** on a build machine that has the engine working
  (Daniel's Mac). The CLI accepts any path, so it reads/writes a project folder
  that lives on OneDrive.
- **AEs (on PCs)** prepare inputs and review/polish outputs via OneDrive; they
  do not run the engine. See `skill_assets/AE_SOP.md`.
- **OneDrive** is the source of truth for active customer projects; this git
  repo holds the engine + the Riverside fixture only.
- `scripts/export_to_onedrive.py` mirrors the AE-facing files to OneDrive
  (drops `.git`/`.venv`/`runs`/`_archive`; keeps `_inbox` + `Unused Renderings`,
  which the engine requires).

The Homebrew/Pango steps above remain required on the build machine.

## Working with plans

- Each plan is bite-sized: discrete tasks, exact file paths, complete code per step.
- Use `superpowers:executing-plans` or `superpowers:subagent-driven-development`
  to execute. Mark checkboxes done as you go.
- Don't start the next plan until the current one's tests pass and is committed.

## Common pitfalls

- Folder names contain spaces (`Branding Board`, `Downtown Riverside Metro Link`,
  `02 - Renderings`, `Base Scope`, etc.). Quote paths in shell commands.
- `.DS_Store` files are gitignored — ignore them when they appear on disk.
- The Riverside MetroLink project is the canonical test fixture for the
  spec; treat changes to its contents carefully.
