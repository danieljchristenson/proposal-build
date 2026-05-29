# Design: Conversational Proposal Generation in Claude Desktop (Per-Machine Engine)

**Date:** 2026-05-29
**Status:** Draft — pending user review

## Background

Today the proposal builder runs in a **centralized** model: the engine
(Python + WeasyPrint) lives in the git repo on Daniel's Mac, AEs prep projects
in the Creative Deliverables SharePoint team site, and Daniel (the operator)
runs generation. See `HOW_IT_WORKS.md`.

The goal of this work is to let the **sales team self-serve**: an AE types
*"build the Morongo proposal"* into **Claude Desktop on their own machine** and
gets the deck generated locally, with no operator step.

## Why this is non-trivial

- The engine is a Bash/CLI orchestrator that shells out to WeasyPrint, which
  needs native system libraries (Pango/Cairo/GTK). Those must be installed on
  whatever machine runs it.
- Claude Desktop's **built-in Skills run in a cloud sandbox** with no local
  filesystem and no native libraries — that is why an earlier Skills install
  failed (`ModuleNotFoundError`, no Pango, no data access).
- The supported way for Claude Desktop to run **local** software is a **local
  MCP server**. That is the linchpin of this design.

## Goal & success criteria

A pilot Windows machine, set up by IT, where an AE can open Claude Desktop and:
1. Ask to list/inspect projects in the Creative Deliverables site and get a
   plain-language readiness report.
2. Ask to generate a proposal and receive the deck + per-tier pricing PDFs
   written back into that project's SharePoint folder (synced).
3. Never see a raw stack trace or a fabricated deck on failure.

Then the same install repeats on the remaining Windows + Mac machines.

## Constraints

- **Fleet:** mostly Windows, a few Macs (~3–6 machines total).
- **Setup:** IT / CircleCap performs per-machine install (standardized script
  acceptable; no polished one-click product required).
- **Data home unchanged:** projects stay in the Creative Deliverables SharePoint
  site, synced locally on each machine. This work does not move data.
- **Engine core unchanged where possible:** wrap, don't rewrite.

## Chosen approach: Managed native install + MCP server (pilot first)

Considered three packaging strategies:
1. **Managed native install** — IT script installs Python + GTK/Pango + engine
   + MCP server and wires Claude Desktop. *(Chosen.)*
2. **Containerized (Docker)** — engine in a Linux container per machine. Held as
   the **fallback** if the Windows GTK install proves too fragile in the pilot.
3. **Bundled one-click installer** — embedded Python + WeasyPrint + GTK.
   Rejected as overkill for this scale.

Rationale: lowest build effort, leverages IT support, standard tooling. The one
real risk (Windows GTK) is contained by piloting on a single machine before
rollout, with Docker as a pre-agreed fallback.

## Architecture

```
AE in Claude Desktop                Their machine (Windows / Mac)
"build the Morongo proposal" ─▶  ┌──────────────────────────────┐
                                 │  MCP server (NEW)             │
                                 │   tools: list / inspect /     │
                                 │          generate             │
                                 │        │ calls internal API   │
                                 │        ▼                      │
                                 │  proposal_build engine        │
                                 │  (Python + WeasyPrint + GTK)  │
                                 └────────────┬─────────────────┘
                                              │ reads/writes
                       Creative Deliverables (SharePoint, synced locally)
                                              │ deck syncs back ▶ team
```

### Component 1 — MCP server (the only substantial new code)

A local stdio MCP server (Python, built on the MCP Python SDK) packaged inside
the repo (e.g. `skill_assets/proposal_build_mcp/`). It calls the **same internal
functions the CLI already uses** (`build_project_model`, `inspect_project`,
`render`) — a wrapper layer, not a rewrite.

Tools exposed to Claude Desktop:
- `list_projects()` → projects in the synced Creative Deliverables folder, each
  with a one-line readiness state.
- `inspect_project(project_name)` → readiness check; returns blockers/warnings
  translated to plain language (not raw validator codes).
- `generate_proposal(project_name, compress=True)` → runs the engine; returns
  the output PDF paths and a short summary. Compressed output by default
  (send-ready size).

Configuration: the server reads the **projects base path** (the local
Creative Deliverables sync location) from an env var / config file written at
install time, since that path differs per machine/user.

### Component 2 — Per-OS setup scripts

A `scripts/install/` set, one per OS:
- **Windows** (`install-windows.ps1`): install Python 3.11+, the GTK3 runtime,
  `pip install` the engine + MCP server, write the Claude Desktop MCP config
  entry, detect the Creative Deliverables sync path, run the self-test.
- **macOS** (`install-macos.sh`): ensure Python, `brew install pango`, pip
  install, write the config, detect the sync path, run the self-test.

Each script ends with a **self-test**: generate the bundled Riverside fixture.
If WeasyPrint can't render, the install fails loudly here — before the AE ever
relies on it.

### Component 3 — Claude Desktop wiring

The setup script registers the server in the per-user Claude Desktop config:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

It adds (idempotently) an `mcpServers` entry launching the local server. After a
Claude Desktop restart, the tools are available conversationally.

### Component 4 — Data access

Each machine must have the **Creative Deliverables site synced** (the OneDrive
shortcut), set to "Always keep on this device" so renderings are real files.
The setup script verifies the sync path exists and points the server at it.

## Brief completion in a self-serve world (design decision to confirm)

In the centralized model, the operator appended "Phase-2" Brief fields
(presenter, voice, schedule, `cover_image`, `pricing_format`) at build time. In
the self-serve model there is no operator, so those fields must be filled
another way. **Recommended resolution:** the generate flow conversationally
completes the Brief — Claude Desktop (via the MCP `inspect`/prompts) asks the AE
for any missing required fields and writes them into `Project Brief.md` before
generating. This turns the old operator step into a natural Claude Desktop
conversation and removes the Phase-1/Phase-2 split. *This touches the creative
team's intake convention and should be confirmed with them.*

## Rollout plan

1. Build the MCP server + setup scripts (dev on Daniel's Mac).
2. **Pilot on one Windows machine** (with IT): run setup → self-test passes →
   exercise list/inspect/generate conversationally in Claude Desktop end-to-end.
3. Pilot passes → IT rolls out to remaining Windows + Mac machines.
4. **Decision gate:** if the Windows GTK install proves too fragile, switch
   Windows machines to the Docker fallback (engine in a Linux container, MCP
   server forwards to it). Mac machines stay native.

## Updates & maintenance

Engine changes land in git as usual. An `update` script (git pull + reinstall)
that IT runs per machine keeps machines current — acceptable at this scale, no
auto-updater. The MCP server reports its version so we can see who is on what.

## Error handling

Every MCP tool catches failures and returns plain-language, actionable messages,
never a stack trace and never a fabricated deck:
- Worksheet open in Excel → "Close Excel and retry."
- Renderings not curated into Base Scope → name the missing/needed files.
- Brief incomplete → list the missing fields (and offer to collect them).
- Runtime/GTK failure or missing sync → "Environment problem — contact IT/Daniel."

## Testing

- **Unit tests** for the MCP tool wrappers (mock the engine; assert friendly
  error translation).
- **Install self-test**: Riverside fixture generation as the per-machine
  acceptance gate.
- **Pilot acceptance**: a real end-to-end conversational generate from Claude
  Desktop on a Windows machine.

## Out of scope (YAGNI)

- No auto-updater, no polished/one-click installer.
- No new engine or proposal features.
- No change to the data model — projects stay in SharePoint; AEs still fill the
  Brief/worksheet and curate renderings as in `HOW_IT_WORKS.md`.
- This work *only* adds local, conversational generation from Claude Desktop.

## Risks

- **Primary:** WeasyPrint GTK install reliability on Windows. Mitigated by the
  one-machine pilot + Docker fallback.
- **Secondary:** Claude Desktop MCP config format / behavior changes across app
  versions. Mitigated by keeping the config entry minimal and version-checking.
- **Sync timing:** generated PDFs depend on OneDrive sync to reach others;
  acceptable, but note in AE guidance.
