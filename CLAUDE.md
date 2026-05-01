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

- Python 3.11+, pyproject.toml, pytest.
- Local dev: `python3.11 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`.
- WeasyPrint is the PDF rendering engine (chosen over python-pptx; spec §3).
- Fonts (Roboto + Poppins) are embedded in `skill_assets/fonts/` (Plan 2). Never load from system.

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
