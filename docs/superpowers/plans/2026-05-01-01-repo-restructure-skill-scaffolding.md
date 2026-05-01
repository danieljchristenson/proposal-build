# Plan 1 — Repo Restructure + Skill Scaffolding

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the directory layout from §9 of the design spec — restructure existing content into `Projects/`, populate `Projects/_master_templates/` and `Projects/_template_project/`, scaffold an empty `skill_assets/` tree, and bootstrap a Python project (deps + test harness) — so subsequent plans build inside a fixed skeleton.

**Architecture:** Filesystem-first. `git mv` for renames so history follows. `.gitkeep` for empty buckets so git tracks the structure. A `pyproject.toml` declaring runtime + dev dependencies. One repo-structure smoke test that locks the layout.

**Tech Stack:** Python 3.11+, PEP 621 `pyproject.toml`, pytest, git.

**Spec reference:** `docs/superpowers/specs/2026-05-01-proposal-builder-skill-design.md` §9 (Repo Structure) and §10 (Deliverables).

**Out of scope for this plan (deferred to later plans):**
- The blank `[Client] - Scope Worksheet.xlsx` template (deferred to Plan 3, where openpyxl is wired in).
- `AE_SOP.md` content (deferred to Plan 8).
- `skill.md` manifest content (deferred to Plan 8).
- Any actual layout HTML, brand CSS, font embedding, Python logic. Plan 1 only places `.gitkeep` markers in those folders.

---

## File Structure

Files **created** by this plan:

| Path | Purpose |
|------|---------|
| `.gitignore` | Excludes `.DS_Store`, Python build artefacts, virtualenvs, IDE files. |
| `pyproject.toml` | PEP 621 project metadata; declares runtime + dev deps; configures pytest. |
| `CLAUDE.md` | Repo-level guidance for Claude Code sessions (toolchain, plan-execution model, where the spec + active plan live). |
| `tests/__init__.py` | Empty — marks `tests/` as a package. |
| `tests/test_repo_structure.py` | Smoke test asserting the directory layout exists. |
| `Projects/_master_templates/` | (rename target) Reference-only originals. |
| `Projects/_template_project/01 - RFP/.gitkeep` | Empty RFP bucket in template. |
| `Projects/_template_project/02 - Renderings/_inbox/.gitkeep` | Inbox bucket. |
| `Projects/_template_project/02 - Renderings/Base Scope/.gitkeep` | Sorted-renderings bucket. |
| `Projects/_template_project/02 - Renderings/Enhancements/.gitkeep` | Enhancement renderings bucket. |
| `Projects/_template_project/02 - Renderings/Unused Renderings/.gitkeep` | Skipped-with-reason bucket. |
| `Projects/_template_project/03 - Scope & Pricing/README.md` | Notes which file goes here (worksheet template deferred to Plan 3). |
| `Projects/_template_project/04 - Process & Notes/Project Brief.md` | Blank Brief template — full schema from spec §4.1. |
| `Projects/Downtown Riverside Metro Link/02 - Renderings/_inbox/` | New `_inbox/` for the existing project (with the two stray drop files moved into it). |
| `skill_assets/fonts/.gitkeep` | Embedded fonts go here in Plan 2. |
| `skill_assets/layouts/.gitkeep` | HTML/CSS layouts in Plan 2. |
| `skill_assets/boilerplate/.gitkeep` | Reusable text blocks in Plan 3. |
| `skill_assets/voice_presets/.gitkeep` | Voice preset .md files in Plan 3. |
| `skill_assets/past_work_library/.gitkeep` | Past work library in Plan 9. |
| `skill_assets/case_studies/.gitkeep` | Case study .md files in Plan 3/9. |
| `skill_assets/rfp_taxonomy/.gitkeep` | `elements.yaml` in Plan 5/6. |

Files **moved** by this plan (history preserved via `git mv`):

| From | To |
|------|----|
| `Sample Proposal/` (whole tree) | `Projects/` (entire rename) |
| `Projects/StNicks_Proposal_v2_Master.pptx` | `Projects/_master_templates/StNicks_Proposal_v2_Master.pptx` |
| `Projects/StNicks_Supplemental_Itemized_Pricing.pdf` | `Projects/_master_templates/StNicks_Supplemental_Itemized_Pricing.pdf` |
| `Projects/Downtown Riverside Metro Link/02 - Renderings/ChatGPT Image Apr 30, 2026, 02_33_45 PM copy.jpg` | `…/02 - Renderings/_inbox/ChatGPT Image Apr 30, 2026, 02_33_45 PM copy.jpg` |
| `Projects/Downtown Riverside Metro Link/02 - Renderings/revised 1ChatGPT Image Apr 30, 2026, 02_33_45 PM copy.png` | `…/02 - Renderings/_inbox/revised 1ChatGPT Image Apr 30, 2026, 02_33_45 PM copy.png` |

---

## Tasks

### Task 1: Add `.gitignore` and lock the existing untracked content as a baseline commit

**Why first:** `00_Company_Context/`, `Branding Board/`, and `Sample Proposal/` are currently on disk but untracked. Before we `git mv` anything we need them in git so `git mv` preserves history. We also need `.gitignore` first so we don't accidentally commit `.DS_Store` files scattered through the tree.

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Create `.gitignore` at repo root**

```gitignore
# macOS
.DS_Store

# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Virtualenvs
.venv/
venv/
env/

# Build / dist
build/
dist/

# IDE
.vscode/
.idea/

# Local test outputs
tests/_output/
```

- [ ] **Step 2: Verify `.gitignore` is recognised — `.DS_Store` should disappear from `git status`**

Run: `git status --short`
Expected: lines for `.gitignore`, `00_Company_Context/`, `Branding Board/`, `Sample Proposal/`, `docs/` (if any new) — but **no `.DS_Store` entries**.

- [ ] **Step 3: Stage existing untracked content (named adds — no `git add .`)**

Run:

```bash
git add .gitignore
git add 00_Company_Context
git add "Branding Board"
git add "Sample Proposal"
```

- [ ] **Step 4: Commit baseline**

Run:

```bash
git commit -m "$(cat <<'EOF'
chore: lock baseline content under git before restructure

Adds .gitignore (excludes .DS_Store, Python build artefacts, virtualenvs)
and commits the existing untracked folders so subsequent git mv operations
preserve history.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: commit succeeds; `git status` clean.

---

### Task 2: Rename `Sample Proposal/` → `Projects/`

**Files:**
- Move (rename): `Sample Proposal/` → `Projects/`

- [ ] **Step 1: Rename via `git mv`**

Run:

```bash
git mv "Sample Proposal" Projects
```

- [ ] **Step 2: Verify rename**

Run: `git status --short`
Expected: lines like `R  Sample Proposal/... -> Projects/...` for every file in the tree.

- [ ] **Step 3: Commit**

Run:

```bash
git commit -m "$(cat <<'EOF'
refactor: rename Sample Proposal/ to Projects/

Per design spec §9 — the directory will hold both _master_templates/,
_template_project/, and live customer projects, so "Sample Proposal" is
the wrong name once it's the home of all proposal work.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Create `Projects/_master_templates/` and move the two master files into it

**Files:**
- Create: `Projects/_master_templates/`
- Move: `Projects/StNicks_Proposal_v2_Master.pptx` → `Projects/_master_templates/StNicks_Proposal_v2_Master.pptx`
- Move: `Projects/StNicks_Supplemental_Itemized_Pricing.pdf` → `Projects/_master_templates/StNicks_Supplemental_Itemized_Pricing.pdf`

- [ ] **Step 1: Create the destination directory**

Run:

```bash
mkdir -p Projects/_master_templates
```

- [ ] **Step 2: Move both master files via `git mv`**

Run:

```bash
git mv "Projects/StNicks_Proposal_v2_Master.pptx" Projects/_master_templates/
git mv "Projects/StNicks_Supplemental_Itemized_Pricing.pdf" Projects/_master_templates/
```

- [ ] **Step 3: Verify**

Run: `ls Projects/_master_templates/`
Expected:
```
StNicks_Proposal_v2_Master.pptx
StNicks_Supplemental_Itemized_Pricing.pdf
```

Run: `ls Projects/`
Expected: no longer shows the two master files at the top level.

- [ ] **Step 4: Commit**

Run:

```bash
git add Projects/_master_templates
git commit -m "$(cat <<'EOF'
refactor: move master templates into Projects/_master_templates/

Reference-only originals (master pptx + itemized pricing pdf) live in a
dedicated subdir so the Projects/ root only contains real customer
projects + the blank _template_project/.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Create `Projects/_template_project/` skeleton with blank Brief and folder placeholders

**Files:**
- Create: `Projects/_template_project/01 - RFP/.gitkeep`
- Create: `Projects/_template_project/02 - Renderings/_inbox/.gitkeep`
- Create: `Projects/_template_project/02 - Renderings/Base Scope/.gitkeep`
- Create: `Projects/_template_project/02 - Renderings/Enhancements/.gitkeep`
- Create: `Projects/_template_project/02 - Renderings/Unused Renderings/.gitkeep`
- Create: `Projects/_template_project/03 - Scope & Pricing/README.md`
- Create: `Projects/_template_project/04 - Process & Notes/Project Brief.md`

- [ ] **Step 1: Create the directory tree**

Run:

```bash
mkdir -p "Projects/_template_project/01 - RFP"
mkdir -p "Projects/_template_project/02 - Renderings/_inbox"
mkdir -p "Projects/_template_project/02 - Renderings/Base Scope"
mkdir -p "Projects/_template_project/02 - Renderings/Enhancements"
mkdir -p "Projects/_template_project/02 - Renderings/Unused Renderings"
mkdir -p "Projects/_template_project/03 - Scope & Pricing"
mkdir -p "Projects/_template_project/04 - Process & Notes"
```

- [ ] **Step 2: Write `.gitkeep` markers in every empty folder**

Use the Write tool to create each of the following with empty content (zero bytes is fine — `.gitkeep` is a convention, content is irrelevant):

- `Projects/_template_project/01 - RFP/.gitkeep`
- `Projects/_template_project/02 - Renderings/_inbox/.gitkeep`
- `Projects/_template_project/02 - Renderings/Base Scope/.gitkeep`
- `Projects/_template_project/02 - Renderings/Enhancements/.gitkeep`
- `Projects/_template_project/02 - Renderings/Unused Renderings/.gitkeep`

- [ ] **Step 3: Write `Projects/_template_project/03 - Scope & Pricing/README.md`**

Content:

```markdown
# Scope & Pricing

Drop the AE-built Scope Worksheet into this folder, named:

    [Client] - Scope Worksheet.xlsx

(Replace `[Client]` with the customer's short name, e.g.
`Riverside MetroLink - Scope Worksheet.xlsx`.)

Worksheet column schema is locked in
`docs/superpowers/specs/2026-05-01-proposal-builder-skill-design.md` §4.2.

A blank worksheet template (Plan 3 deliverable) will eventually live in
this folder under the same filename, with all required columns
pre-populated and tier-totals formulas wired up.
```

- [ ] **Step 4: Write `Projects/_template_project/04 - Process & Notes/Project Brief.md`**

Content (verbatim — this is the canonical blank Brief, derived from spec §4.1):

```markdown
---
# Client
client_company: ""
client_decision_maker: ""
client_decision_maker_title: ""
client_decision_maker_email: ""
client_address: ""              # optional

# Project
project_name: ""
project_short: ""               # used in footers
project_year:

# Presenter
presenter_name: ""
presenter_email: ""
presenter_phone: ""

# Schedule (only go_live is required; rest auto-derive if blank)
go_live: ""
season_end: ""
fabrication_lock: ""            # default: go_live − 90 days
signing_deadline: ""            # default: go_live − 21 days

# Tone & creative
voice: ""                       # civic | destination-retail | corporate | hospitality
recommended_tier: ""            # essential | enhanced | signature
design_phrase: ""

# Assets
cover_image: ""
case_study: ""                  # filename (sans .md) or "skip"

# Slide control (defaults shown — only set to override)
include_case_study: true
include_add_ons: true
pricing_format: "tiered"        # tiered | single
mode: "one-shot"                # one-shot | checkpoint

# Sample of Our Work — array of past_work IDs (optional; default = best-of for voice)
sample_work: []
---

## Creative Direction

(2–3 sentences. Sets the visual narrative for slide 4.)

## Customer Goals
-
-

## Customer Success Criteria
-
-

## Constraints
- (bullet — or "none" to omit the box on slide 3)

## Showcase Sections
1. **Section Name** — one-line subtitle
2. **Section Name** — one-line subtitle
3. **Section Name** — one-line subtitle
```

- [ ] **Step 5: Verify the tree**

Run: `find Projects/_template_project -type f | sort`
Expected (exactly these 7 lines, in this order):
```
Projects/_template_project/01 - RFP/.gitkeep
Projects/_template_project/02 - Renderings/Base Scope/.gitkeep
Projects/_template_project/02 - Renderings/Enhancements/.gitkeep
Projects/_template_project/02 - Renderings/Unused Renderings/.gitkeep
Projects/_template_project/02 - Renderings/_inbox/.gitkeep
Projects/_template_project/03 - Scope & Pricing/README.md
Projects/_template_project/04 - Process & Notes/Project Brief.md
```

- [ ] **Step 6: Commit**

Run:

```bash
git add Projects/_template_project
git commit -m "$(cat <<'EOF'
feat: scaffold Projects/_template_project/ skeleton

Blank duplicate-me-for-each-new-project tree:
- 01 - RFP/, 02 - Renderings/{_inbox,Base Scope,Enhancements,Unused
  Renderings}/, 03 - Scope & Pricing/, 04 - Process & Notes/
- Project Brief.md prefilled with the locked schema from spec §4.1
- README in Scope & Pricing notes the worksheet filename convention;
  the actual .xlsx template is a Plan 3 deliverable

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Add `_inbox/` to existing Riverside project and move stray drop files into it

**Why:** The Riverside project predates the Phase-1 ingestion design. Two raw rendering drops sit at the root of `02 - Renderings/`. They belong in `_inbox/` per spec §4.3 — that's exactly the state Phase 1 will scan.

**Files:**
- Create: `Projects/Downtown Riverside Metro Link/02 - Renderings/_inbox/`
- Move: two files (see paths below)

- [ ] **Step 1: Create `_inbox/`**

Run:

```bash
mkdir -p "Projects/Downtown Riverside Metro Link/02 - Renderings/_inbox"
```

- [ ] **Step 2: Move the two stray drops via `git mv`**

Run:

```bash
git mv "Projects/Downtown Riverside Metro Link/02 - Renderings/ChatGPT Image Apr 30, 2026, 02_33_45 PM copy.jpg" \
       "Projects/Downtown Riverside Metro Link/02 - Renderings/_inbox/"

git mv "Projects/Downtown Riverside Metro Link/02 - Renderings/revised 1ChatGPT Image Apr 30, 2026, 02_33_45 PM copy.png" \
       "Projects/Downtown Riverside Metro Link/02 - Renderings/_inbox/"
```

- [ ] **Step 3: Verify**

Run: `ls "Projects/Downtown Riverside Metro Link/02 - Renderings/_inbox/"`
Expected:
```
ChatGPT Image Apr 30, 2026, 02_33_45 PM copy.jpg
revised 1ChatGPT Image Apr 30, 2026, 02_33_45 PM copy.png
```

Run: `ls "Projects/Downtown Riverside Metro Link/02 - Renderings/"`
Expected (no stray jpg/png at this level):
```
Base Scope
Enhancements
Unused Renderings
_inbox
```
(`.DS_Store` should be absent because of the gitignore — but it may still exist on disk; that's fine, it just won't be tracked.)

- [ ] **Step 4: Commit**

Run:

```bash
git commit -m "$(cat <<'EOF'
refactor: move Riverside stray drops into 02 - Renderings/_inbox/

Per spec §4.3, raw rendering drops live in _inbox/ until Phase 1 sorts
them. The two ChatGPT-named PNG/JPG files were sitting at the
02 - Renderings/ root; relocating them sets the project up to be a real
test fixture for Phase 1 ingestion.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Scaffold the empty `skill_assets/` tree

**Files:**
- Create: `skill_assets/fonts/.gitkeep`
- Create: `skill_assets/layouts/.gitkeep`
- Create: `skill_assets/boilerplate/.gitkeep`
- Create: `skill_assets/voice_presets/.gitkeep`
- Create: `skill_assets/past_work_library/.gitkeep`
- Create: `skill_assets/case_studies/.gitkeep`
- Create: `skill_assets/rfp_taxonomy/.gitkeep`

- [ ] **Step 1: Create directories**

Run:

```bash
mkdir -p skill_assets/fonts
mkdir -p skill_assets/layouts
mkdir -p skill_assets/boilerplate
mkdir -p skill_assets/voice_presets
mkdir -p skill_assets/past_work_library
mkdir -p skill_assets/case_studies
mkdir -p skill_assets/rfp_taxonomy
```

- [ ] **Step 2: Add `.gitkeep` to each (empty content via Write tool)**

Use Write to create each of the seven `.gitkeep` files listed above with empty content.

- [ ] **Step 3: Verify**

Run: `find skill_assets -type f | sort`
Expected:
```
skill_assets/boilerplate/.gitkeep
skill_assets/case_studies/.gitkeep
skill_assets/fonts/.gitkeep
skill_assets/layouts/.gitkeep
skill_assets/past_work_library/.gitkeep
skill_assets/rfp_taxonomy/.gitkeep
skill_assets/voice_presets/.gitkeep
```

- [ ] **Step 4: Commit**

Run:

```bash
git add skill_assets
git commit -m "$(cat <<'EOF'
feat: scaffold empty skill_assets/ tree

Locks the directory layout for the skill bundle (fonts, layouts,
boilerplate, voice_presets, past_work_library, case_studies,
rfp_taxonomy). Each subdir holds .gitkeep until later plans populate
it. Per design spec §9.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Add `pyproject.toml` declaring runtime + dev dependencies

**Why:** Plans 2+ assume `pip install -e ".[dev]"` (or `uv sync`) bootstraps a working environment. We declare every dep we know we'll need so future plans don't fight a dep-pinning game.

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Write `pyproject.toml`**

Content:

```toml
[project]
name = "stnicks-proposal-builder"
version = "0.0.1"
description = "St. Nick's proposal builder — Claude Desktop skill that generates customer proposals from Brief + Worksheet + renderings."
readme = "README.md"
requires-python = ">=3.11"
authors = [
    { name = "Daniel Christenson", email = "daniel@st-nicks.com" },
]
license = { text = "Proprietary" }

# Runtime dependencies — what the skill code imports.
dependencies = [
    "weasyprint>=62.0",          # HTML/CSS → PDF rendering pipeline (spec §3)
    "openpyxl>=3.1",             # Scope Worksheet .xlsx parsing (spec §4.2)
    "pillow>=10.0",              # Image handling (cover, renderings)
    "pyyaml>=6.0",               # elements.yaml, dependency_map.yaml, Brief frontmatter
    "python-frontmatter>=1.1",   # Brief.md YAML frontmatter parsing
    "jinja2>=3.1",               # Layout templating
    "pymupdf>=1.24",             # PDF text extraction during Phase 0 RFP intake
    "python-pptx>=1.0",          # PPTX text extraction during Phase 0
    "anthropic>=0.40",           # Vision calls in Phase 0 / Phase 1
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.6",
]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
# We do not currently distribute as a wheel — this section keeps
# `pip install -e .` happy by declaring the package layout explicitly.
packages = []

[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = "-ra -q"

[tool.ruff]
line-length = 100
target-version = "py311"
```

- [ ] **Step 2: Verify the file parses**

Run: `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"`
Expected: no output, exit 0. If it raises, fix the syntax before continuing.

- [ ] **Step 3: Stage + commit**

Run:

```bash
git add pyproject.toml
git commit -m "$(cat <<'EOF'
feat: bootstrap Python project via pyproject.toml

Declares the full runtime dep set the skill code will import (weasyprint,
openpyxl, pillow, pyyaml, python-frontmatter, jinja2, pymupdf,
python-pptx, anthropic) plus dev deps (pytest, pytest-cov, ruff).
Pinning floors-only — exact versions get locked once Plan 2 builds the
WeasyPrint pipeline against real layouts.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 8: Add the repo-structure smoke test

**Why:** Locks the layout — if a future task accidentally moves or removes a required directory, the test fails immediately. This is the only test in Plan 1; it's the harness that future plans plug into.

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_repo_structure.py`

- [ ] **Step 1: Write the failing test first**

Create `tests/__init__.py` with empty content.

Create `tests/test_repo_structure.py` with:

```python
"""Smoke test: locks the on-disk repo layout for the skill bundle.

If a future change accidentally moves or removes one of these paths,
this test fails before downstream plans break in confusing ways.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _exists(*parts: str) -> bool:
    return REPO_ROOT.joinpath(*parts).exists()


def test_top_level_layout():
    assert _exists("00_Company_Context")
    assert _exists("Branding Board")
    assert _exists("Projects")
    assert _exists("skill_assets")
    assert _exists("docs", "superpowers", "specs")
    assert _exists("docs", "superpowers", "plans")
    assert _exists("pyproject.toml")
    assert _exists(".gitignore")


def test_projects_layout():
    assert _exists("Projects", "_master_templates")
    assert _exists("Projects", "_master_templates", "StNicks_Proposal_v2_Master.pptx")
    assert _exists("Projects", "_master_templates", "StNicks_Supplemental_Itemized_Pricing.pdf")
    assert _exists("Projects", "_template_project")


def test_template_project_subfolders():
    base = ("Projects", "_template_project")
    assert _exists(*base, "01 - RFP")
    assert _exists(*base, "02 - Renderings", "_inbox")
    assert _exists(*base, "02 - Renderings", "Base Scope")
    assert _exists(*base, "02 - Renderings", "Enhancements")
    assert _exists(*base, "02 - Renderings", "Unused Renderings")
    assert _exists(*base, "03 - Scope & Pricing", "README.md")
    assert _exists(*base, "04 - Process & Notes", "Project Brief.md")


def test_riverside_project_has_inbox():
    base = ("Projects", "Downtown Riverside Metro Link", "02 - Renderings")
    assert _exists(*base, "_inbox")
    assert _exists(*base, "Base Scope")
    assert _exists(*base, "Enhancements")
    assert _exists(*base, "Unused Renderings")


def test_skill_assets_subfolders():
    base = ("skill_assets",)
    assert _exists(*base, "fonts")
    assert _exists(*base, "layouts")
    assert _exists(*base, "boilerplate")
    assert _exists(*base, "voice_presets")
    assert _exists(*base, "past_work_library")
    assert _exists(*base, "case_studies")
    assert _exists(*base, "rfp_taxonomy")
```

- [ ] **Step 2: Bootstrap a virtualenv and install dev deps**

Run (from repo root):

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

Expected: clean install. If `weasyprint` install errors, document the system dependency (cairo, pango, gdk-pixbuf) in a follow-up — but Plan 1's test does not import weasyprint, so a transient install error here doesn't block the test from running. If the install fails mid-way, retry with just `pip install pytest` and proceed; full env setup can be revisited in Plan 2 when the pipeline first actually runs.

- [ ] **Step 3: Run the test — expect PASS**

Run: `pytest tests/test_repo_structure.py -v`

Expected: all 5 tests pass. If any fails, diagnose which directory or file is missing and fix before continuing — that's the test catching exactly what it's designed to catch.

- [ ] **Step 4: Commit**

Run:

```bash
git add tests/__init__.py tests/test_repo_structure.py
git commit -m "$(cat <<'EOF'
test: add repo-structure smoke test

Five test functions assert the directory layout established by Plan 1
(top-level, Projects/, _template_project/ subfolders, Riverside _inbox/,
skill_assets/ subfolders). Future plans can extend this file to lock
their own additions.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 9: Add `CLAUDE.md` at repo root for codebase-specific Claude Code guidance

**Why:** Future Claude Code sessions land in this repo, see one commit, and don't know which plan is active or where the spec lives. `CLAUDE.md` auto-loads into Claude Code's context and points the next session at the right artefacts.

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Write `CLAUDE.md`**

Content:

```markdown
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
```

- [ ] **Step 2: Stage + commit**

Run:

```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs: add CLAUDE.md repo guide

Onboards future Claude Code sessions: points at the design spec,
explains the plans/ workflow, documents the locked layout, lists the
toolchain, flags space-in-path quoting and other common pitfalls.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Plan Completion Check

Before declaring Plan 1 done, confirm all of the following:

- [ ] `git status` is clean (no uncommitted changes).
- [ ] `git log --oneline` shows the expected commits from Tasks 1–9 (~9 commits beyond the initial spec commit).
- [ ] `pytest tests/test_repo_structure.py -v` reports 5/5 passing.
- [ ] `find Projects/_template_project skill_assets -type f | sort` matches the expected file list above.
- [ ] `ls Projects/_master_templates/` shows both master files.
- [ ] `ls "Projects/Downtown Riverside Metro Link/02 - Renderings/_inbox/"` shows the two ChatGPT-named drop files.
- [ ] `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"` exits 0.

If all green, Plan 1 is complete. Plan 2 (Brand + layout system) starts fresh against this skeleton.
