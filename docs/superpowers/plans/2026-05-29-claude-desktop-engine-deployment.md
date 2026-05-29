# Claude Desktop Engine Deployment — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let AEs generate proposals conversationally from Claude Desktop on their own machines, by wrapping the existing engine in a local MCP server and providing IT-run per-OS install scripts.

**Architecture:** A local stdio MCP server calls a new thin internal API (`proposal_build.api`) that both the CLI and the server share. Claude Desktop launches the server per the user's `claude_desktop_config.json`; the server reads/writes projects in the locally-synced Creative Deliverables SharePoint folder. Managed native install (Python + WeasyPrint/GTK), piloted on one Windows machine, Docker held as fallback.

**Tech Stack:** Python 3.11+, the `mcp` SDK (FastMCP), WeasyPrint, pytest, PowerShell (Windows install), bash (macOS install).

**Spec:** `docs/superpowers/specs/2026-05-29-claude-desktop-engine-deployment-design.md`

---

## File Structure

**New:**
- `skill_assets/proposal_build/api.py` — shared internal API: `inspect_project()`, `generate_proposal()` returning structured results (no printing).
- `skill_assets/proposal_build_mcp/__init__.py` — MCP server package.
- `skill_assets/proposal_build_mcp/config.py` — resolves the projects base path from env/config.
- `skill_assets/proposal_build_mcp/formatting.py` — translates validator blockers/warnings to plain language.
- `skill_assets/proposal_build_mcp/server.py` — FastMCP server exposing the tools.
- `scripts/install/claude_desktop_config.py` — idempotently writes the MCP entry into `claude_desktop_config.json` (cross-platform).
- `scripts/install/selftest.py` — generates the Riverside fixture as install verification.
- `scripts/install/install-macos.sh` — macOS setup.
- `scripts/install/install-windows.ps1` — Windows setup.
- `scripts/install/update.sh` / `update.ps1` — pull + reinstall.
- `scripts/install/README.md` — IT install/runbook + pilot checklist.
- `tests/test_api.py`, `tests/test_mcp_server.py`, `tests/test_mcp_formatting.py`, `tests/test_claude_desktop_config.py` — tests.

**Modify:**
- `skill_assets/proposal_build/cli.py` — route `_do_inspect`/`_do_generate` through `api.py` (DRY).
- `pyproject.toml` — add `mcp` dependency and `proposal-build-mcp` entry point.

---

## Task 1: Add the `mcp` dependency and entry point

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add dependency and console script**

In `pyproject.toml`, add `"mcp>=1.2.0"` to `[project].dependencies`, and under `[project.scripts]` add:

```toml
proposal-build-mcp = "proposal_build_mcp.server:main"
```

- [ ] **Step 2: Install and verify import**

Run: `pip install -e ".[dev]" && python -c "import mcp; print(mcp.__version__)"`
Expected: prints a version ≥ 1.2.0, no error.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "build: add mcp dependency + proposal-build-mcp entry point"
```

---

## Task 2: Extract a shared internal API (`api.py`)

Both the CLI and the MCP server must call the same logic. Extract pure functions that return data instead of printing.

**Files:**
- Create: `skill_assets/proposal_build/api.py`
- Test: `tests/test_api.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_api.py
from pathlib import Path
from proposal_build import api

RIVERSIDE = Path("Projects/Downtown Riverside Metro Link")

def test_inspect_returns_structured_result():
    res = api.inspect_project(RIVERSIDE)
    assert isinstance(res.blockers, list)
    assert isinstance(res.warnings, list)
    assert res.ready == (len(res.blockers) == 0)

def test_generate_returns_output_paths(tmp_path):
    res = api.generate_proposal(RIVERSIDE, compress=False)
    assert res.ready is True
    assert any(p.suffix == ".pdf" for p in res.outputs)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_api.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'proposal_build.api'`.

- [ ] **Step 3: Implement `api.py`**

```python
# skill_assets/proposal_build/api.py
"""Shared internal API used by both the CLI and the MCP server.

These functions return structured results and never print. The CLI formats
them for humans; the MCP server formats them for Claude Desktop.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from proposal_build.parser import build_project_model, ProjectLoadError
from proposal_build.inspector import inspect_project as _inspect
from proposal_build.renderer import render


@dataclass
class InspectResult:
    ready: bool
    blockers: list[tuple[str, str]] = field(default_factory=list)
    warnings: list[tuple[str, str]] = field(default_factory=list)
    error: str | None = None


@dataclass
class GenerateResult:
    ready: bool
    outputs: list[Path] = field(default_factory=list)
    blockers: list[tuple[str, str]] = field(default_factory=list)
    error: str | None = None


def inspect_project(project_dir: Path) -> InspectResult:
    try:
        result = _inspect(project_dir)
    except ProjectLoadError as e:
        return InspectResult(ready=False, blockers=[("project_load", str(e))])
    return InspectResult(
        ready=not result.blockers,
        blockers=list(result.blockers),
        warnings=list(result.warnings),
    )


def generate_proposal(project_dir: Path, compress: bool = True,
                      no_snapshot: bool = False) -> GenerateResult:
    try:
        model, artifacts = build_project_model(project_dir)
    except ProjectLoadError as e:
        return GenerateResult(ready=False, blockers=[("project_load", str(e))])
    insp = _inspect(project_dir)
    if insp.blockers:
        return GenerateResult(ready=False, blockers=list(insp.blockers))
    outcome = render(project_dir, model, compress=compress, no_snapshot=no_snapshot)
    return GenerateResult(ready=True, outputs=list(outcome.output_paths))
```

> NOTE for implementer: confirm the real signatures of `inspect_project`,
> `build_project_model`, and `render` in the current code and adapt the calls
> (names/return shapes) to match. The structure above is the contract; wire it
> to the actual functions. Do not change engine behavior.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_api.py -v`
Expected: PASS (Riverside fixture is "ready" and generates PDFs).

- [ ] **Step 5: Route the CLI through the API (DRY)**

Modify `skill_assets/proposal_build/cli.py` so `_do_inspect` and `_do_generate` call `api.inspect_project` / `api.generate_proposal` and then handle printing. Keep CLI output identical.

- [ ] **Step 6: Run the full suite**

Run: `pytest -q`
Expected: PASS (no regressions in existing CLI tests).

- [ ] **Step 7: Commit**

```bash
git add skill_assets/proposal_build/api.py skill_assets/proposal_build/cli.py tests/test_api.py
git commit -m "refactor: extract shared proposal_build.api used by CLI (and soon MCP)"
```

---

## Task 3: Projects-path config for the MCP server

**Files:**
- Create: `skill_assets/proposal_build_mcp/__init__.py` (empty)
- Create: `skill_assets/proposal_build_mcp/config.py`
- Test: `tests/test_mcp_server.py` (config portion)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_mcp_server.py
import os
from pathlib import Path
import pytest
from proposal_build_mcp import config

def test_projects_root_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("PROPOSAL_BUILD_PROJECTS_ROOT", str(tmp_path))
    assert config.projects_root() == tmp_path

def test_projects_root_missing_raises(monkeypatch):
    monkeypatch.delenv("PROPOSAL_BUILD_PROJECTS_ROOT", raising=False)
    with pytest.raises(config.ConfigError):
        config.projects_root()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_mcp_server.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'proposal_build_mcp'`.

- [ ] **Step 3: Implement `config.py`**

```python
# skill_assets/proposal_build_mcp/config.py
"""Resolve where the AE's projects live (the locally-synced Creative
Deliverables folder). Set by the installer per machine."""
from __future__ import annotations
import os
from pathlib import Path

ENV_VAR = "PROPOSAL_BUILD_PROJECTS_ROOT"

class ConfigError(Exception):
    pass

def projects_root() -> Path:
    raw = os.environ.get(ENV_VAR)
    if not raw:
        raise ConfigError(
            f"{ENV_VAR} is not set. The installer should point this at the "
            "synced 'Creative Deliverables/Projects' folder."
        )
    p = Path(raw).expanduser()
    if not p.is_dir():
        raise ConfigError(f"{ENV_VAR} points at a missing folder: {p}")
    return p
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_mcp_server.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build_mcp/__init__.py skill_assets/proposal_build_mcp/config.py tests/test_mcp_server.py
git commit -m "feat(mcp): projects-root config resolution"
```

---

## Task 4: Plain-language formatting of inspect results

**Files:**
- Create: `skill_assets/proposal_build_mcp/formatting.py`
- Test: `tests/test_mcp_formatting.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_mcp_formatting.py
from proposal_build.api import InspectResult
from proposal_build_mcp import formatting

def test_ready_message():
    txt = formatting.readiness_text("Morongo", InspectResult(ready=True))
    assert "ready to generate" in txt.lower()

def test_blockers_are_humanized():
    res = InspectResult(ready=False,
        blockers=[("brief/missing-field", "Brief is missing required frontmatter field: client_company")])
    txt = formatting.readiness_text("Morongo", res)
    assert "client_company" in txt
    assert "brief/missing-field" not in txt  # raw codes hidden
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_mcp_formatting.py -v`
Expected: FAIL with import error.

- [ ] **Step 3: Implement `formatting.py`**

```python
# skill_assets/proposal_build_mcp/formatting.py
"""Turn engine results into plain language for an AE in Claude Desktop.
Never leak raw validator codes or stack traces."""
from __future__ import annotations
from proposal_build.api import InspectResult, GenerateResult

def readiness_text(project: str, res: InspectResult) -> str:
    if res.error:
        return f"Couldn't read {project!r}: {res.error}"
    if res.ready:
        n = len(res.warnings)
        tail = f" ({n} minor warning{'s' if n != 1 else ''})" if n else ""
        return f"{project} is ready to generate{tail}."
    lines = [f"{project} isn't ready yet. Needs:"]
    for _code, msg in res.blockers:
        lines.append(f"  - {msg}")
    return "\n".join(lines)

def generate_text(project: str, res: GenerateResult) -> str:
    if res.error:
        return f"Generation failed for {project!r}: {res.error}"
    if not res.ready:
        lines = [f"Can't generate {project} yet. Resolve first:"]
        lines += [f"  - {msg}" for _c, msg in res.blockers]
        return "\n".join(lines)
    files = "\n".join(f"  - {p.name}" for p in res.outputs)
    return f"Generated {project}:\n{files}\nThey're in the project's 03 - Scope & Pricing folder."
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_mcp_formatting.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skill_assets/proposal_build_mcp/formatting.py tests/test_mcp_formatting.py
git commit -m "feat(mcp): plain-language formatting of engine results"
```

---

## Task 5: MCP server with `list_projects`, `inspect_project`, `generate_proposal`

**Files:**
- Create: `skill_assets/proposal_build_mcp/server.py`
- Test: `tests/test_mcp_server.py` (extend)

- [ ] **Step 1: Write the failing tests (test the tool functions directly)**

```python
# tests/test_mcp_server.py  (append)
from pathlib import Path
from proposal_build_mcp import server

def test_list_projects(monkeypatch, tmp_path):
    (tmp_path / "Alpha").mkdir()
    (tmp_path / "Beta").mkdir()
    monkeypatch.setenv("PROPOSAL_BUILD_PROJECTS_ROOT", str(tmp_path))
    out = server._list_projects_impl()
    assert "Alpha" in out and "Beta" in out

def test_generate_blocks_when_not_ready(monkeypatch, tmp_path):
    monkeypatch.setenv("PROPOSAL_BUILD_PROJECTS_ROOT", str(tmp_path))
    (tmp_path / "Empty").mkdir()
    out = server._generate_impl("Empty")
    assert "isn't ready" in out or "Can't generate" in out
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest tests/test_mcp_server.py -v`
Expected: FAIL (`server` has no `_list_projects_impl`).

- [ ] **Step 3: Implement `server.py`**

```python
# skill_assets/proposal_build_mcp/server.py
"""Local MCP server exposing the proposal builder to Claude Desktop.

Tool functions have plain `_impl` counterparts so they're unit-testable
without the MCP transport. Tools never raise to the client — they catch and
return a friendly message."""
from __future__ import annotations
from pathlib import Path
from mcp.server.fastmcp import FastMCP

from proposal_build import api
from proposal_build_mcp import config, formatting

mcp = FastMCP("proposal-builder")

def _resolve(project: str) -> Path:
    return config.projects_root() / project

def _list_projects_impl() -> str:
    try:
        root = config.projects_root()
    except config.ConfigError as e:
        return f"Configuration problem — contact IT/Daniel: {e}"
    names = sorted(p.name for p in root.iterdir()
                   if p.is_dir() and not p.name.startswith(("_", ".")))
    if not names:
        return "No projects found in the Creative Deliverables folder."
    return "Projects:\n" + "\n".join(f"  - {n}" for n in names)

def _inspect_impl(project: str) -> str:
    try:
        res = api.inspect_project(_resolve(project))
    except config.ConfigError as e:
        return f"Configuration problem — contact IT/Daniel: {e}"
    except Exception as e:  # never leak a stack trace
        return f"Couldn't inspect {project!r} — contact IT/Daniel. ({type(e).__name__})"
    return formatting.readiness_text(project, res)

def _generate_impl(project: str, compress: bool = True) -> str:
    try:
        res = api.generate_proposal(_resolve(project), compress=compress)
    except config.ConfigError as e:
        return f"Configuration problem — contact IT/Daniel: {e}"
    except Exception as e:
        return f"Generation failed for {project!r} — contact IT/Daniel. ({type(e).__name__})"
    return formatting.generate_text(project, res)

@mcp.tool()
def list_projects() -> str:
    """List proposal projects available to generate."""
    return _list_projects_impl()

@mcp.tool()
def inspect_project(project: str) -> str:
    """Check whether a project is ready to generate and what's missing."""
    return _inspect_impl(project)

@mcp.tool()
def generate_proposal(project: str, compress: bool = True) -> str:
    """Generate the proposal deck + per-tier pricing PDFs for a project."""
    return _generate_impl(project, compress=compress)

def main() -> None:
    mcp.run()

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run to verify it passes**

Run: `pytest tests/test_mcp_server.py -v`
Expected: PASS.

- [ ] **Step 5: Manual smoke (stdio server starts)**

Run: `PROPOSAL_BUILD_PROJECTS_ROOT="Projects" timeout 3 proposal-build-mcp` (it should start and wait on stdio without crashing; Ctrl-C / timeout to exit).

- [ ] **Step 6: Commit**

```bash
git add skill_assets/proposal_build_mcp/server.py tests/test_mcp_server.py
git commit -m "feat(mcp): server with list/inspect/generate tools"
```

---

## Task 6: Idempotent Claude Desktop config wiring

**Files:**
- Create: `scripts/install/claude_desktop_config.py`
- Test: `tests/test_claude_desktop_config.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_claude_desktop_config.py
import json
from pathlib import Path
import importlib.util

MOD = Path("scripts/install/claude_desktop_config.py")
spec = importlib.util.spec_from_file_location("cdc", MOD)
cdc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cdc)

def test_adds_server_entry(tmp_path):
    cfg = tmp_path / "claude_desktop_config.json"
    cdc.ensure_server(cfg, command="proposal-build-mcp",
                      projects_root="/x/Projects")
    data = json.loads(cfg.read_text())
    assert data["mcpServers"]["proposal-builder"]["command"] == "proposal-build-mcp"
    assert data["mcpServers"]["proposal-builder"]["env"]["PROPOSAL_BUILD_PROJECTS_ROOT"] == "/x/Projects"

def test_idempotent_and_preserves_others(tmp_path):
    cfg = tmp_path / "claude_desktop_config.json"
    cfg.write_text(json.dumps({"mcpServers": {"other": {"command": "x"}}}))
    cdc.ensure_server(cfg, command="proposal-build-mcp", projects_root="/x")
    cdc.ensure_server(cfg, command="proposal-build-mcp", projects_root="/x")
    data = json.loads(cfg.read_text())
    assert "other" in data["mcpServers"]
    assert list(data["mcpServers"]).count("proposal-builder") == 1
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest tests/test_claude_desktop_config.py -v`
Expected: FAIL (module/function missing).

- [ ] **Step 3: Implement `claude_desktop_config.py`**

```python
# scripts/install/claude_desktop_config.py
"""Idempotently register the proposal-builder MCP server in a user's
Claude Desktop config, preserving any existing servers."""
from __future__ import annotations
import json, sys
from pathlib import Path

SERVER_KEY = "proposal-builder"

def ensure_server(config_path: Path, command: str, projects_root: str) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if config_path.exists() and config_path.read_text().strip():
        data = json.loads(config_path.read_text())
    servers = data.setdefault("mcpServers", {})
    servers[SERVER_KEY] = {
        "command": command,
        "env": {"PROPOSAL_BUILD_PROJECTS_ROOT": projects_root},
    }
    config_path.write_text(json.dumps(data, indent=2))

def default_config_path() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    if sys.platform.startswith("win"):
        import os
        return Path(os.environ["APPDATA"]) / "Claude/claude_desktop_config.json"
    raise SystemExit("Unsupported OS for Claude Desktop config.")

if __name__ == "__main__":
    # args: <command> <projects_root>
    ensure_server(default_config_path(), sys.argv[1], sys.argv[2])
    print(f"Registered {SERVER_KEY} in {default_config_path()}")
```

- [ ] **Step 4: Run to verify it passes**

Run: `pytest tests/test_claude_desktop_config.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/install/claude_desktop_config.py tests/test_claude_desktop_config.py
git commit -m "feat(install): idempotent Claude Desktop MCP config wiring"
```

---

## Task 7: Install self-test

**Files:**
- Create: `scripts/install/selftest.py`

- [ ] **Step 1: Implement the self-test**

```python
# scripts/install/selftest.py
"""Install verification: generate the Riverside fixture. Exits non-zero on
any failure so the installer aborts loudly before an AE relies on it."""
from __future__ import annotations
import sys
from pathlib import Path
from proposal_build import api

def main() -> int:
    fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Projects/Downtown Riverside Metro Link")
    if not fixture.is_dir():
        print(f"SELF-TEST FAIL: fixture not found at {fixture}"); return 2
    res = api.generate_proposal(fixture, compress=False, no_snapshot=True)
    if not res.ready or not res.outputs:
        print("SELF-TEST FAIL: generation did not produce outputs.")
        for _c, m in res.blockers: print("  -", m)
        return 1
    print("SELF-TEST PASS: WeasyPrint rendered", len(res.outputs), "PDFs.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run it on the dev machine**

Run: `python scripts/install/selftest.py`
Expected: `SELF-TEST PASS: WeasyPrint rendered 4 PDFs.`

- [ ] **Step 3: Commit**

```bash
git add scripts/install/selftest.py
git commit -m "feat(install): WeasyPrint self-test (generates Riverside fixture)"
```

---

## Task 8: macOS install script

**Files:**
- Create: `scripts/install/install-macos.sh`

- [ ] **Step 1: Write the script**

```bash
#!/usr/bin/env bash
# macOS install for the proposal-builder MCP server.
# Usage: install-macos.sh <repo_dir> <projects_root>
set -euo pipefail
REPO="${1:?repo dir}"; PROJECTS="${2:?projects root}"

command -v brew >/dev/null || { echo "Install Homebrew first: https://brew.sh"; exit 1; }
brew list pango >/dev/null 2>&1 || brew install pango
PYBIN="$(command -v python3.11 || command -v python3)"
"$PYBIN" -m venv "$REPO/.venv"
"$REPO/.venv/bin/pip" install -e "$REPO/skill_assets"  # installs engine + mcp deps

# Wire Claude Desktop to launch the server from this venv.
MCP_CMD="$REPO/.venv/bin/proposal-build-mcp"
"$REPO/.venv/bin/python" "$REPO/scripts/install/claude_desktop_config.py" "$MCP_CMD" "$PROJECTS"

# Verify.
PROPOSAL_BUILD_PROJECTS_ROOT="$PROJECTS" "$REPO/.venv/bin/python" "$REPO/scripts/install/selftest.py" "$REPO/Projects/Downtown Riverside Metro Link"
echo "macOS install complete. Restart Claude Desktop."
```

> NOTE: confirm `pip install -e skill_assets` is the correct install target
> (the package lives under `skill_assets/`). If `pyproject.toml` is at repo
> root, install the repo root instead. Adapt to the actual packaging.

- [ ] **Step 2: Test on the dev Mac (dry idempotent run)**

Run against a scratch repo copy + a test projects dir; confirm it ends with `SELF-TEST PASS` and writes the Claude config entry.

- [ ] **Step 3: Commit**

```bash
git add scripts/install/install-macos.sh
git commit -m "feat(install): macOS setup script"
```

---

## Task 9: Windows install script (PowerShell)

**Files:**
- Create: `scripts/install/install-windows.ps1`

- [ ] **Step 1: Write the script**

```powershell
# install-windows.ps1  — proposal-builder MCP server install (Windows)
# Usage: .\install-windows.ps1 -Repo <repo_dir> -Projects <projects_root>
param([Parameter(Mandatory)] [string]$Repo,
      [Parameter(Mandatory)] [string]$Projects)
$ErrorActionPreference = "Stop"

# 1. Python (assumes Python 3.11+ already installed via winget/IT image).
$py = (Get-Command python).Source

# 2. GTK runtime — REQUIRED by WeasyPrint. IT installs the GTK3 runtime
#    (e.g. the tschoonj GTK3 runtime installer) BEFORE running this script.
#    Verify it loads; fail loudly if not.
& $py -c "import ctypes.util,sys; sys.exit(0 if ctypes.util.find_library('libgobject-2.0-0') or ctypes.util.find_library('gobject-2.0') else 3)"
if ($LASTEXITCODE -ne 0) { throw "GTK runtime not found. Install the GTK3 runtime, then re-run." }

# 3. venv + engine + mcp deps
& $py -m venv "$Repo\.venv"
& "$Repo\.venv\Scripts\pip.exe" install -e "$Repo\skill_assets"

# 4. Wire Claude Desktop
$mcpCmd = "$Repo\.venv\Scripts\proposal-build-mcp.exe"
& "$Repo\.venv\Scripts\python.exe" "$Repo\scripts\install\claude_desktop_config.py" "$mcpCmd" "$Projects"

# 5. Self-test
$env:PROPOSAL_BUILD_PROJECTS_ROOT = $Projects
& "$Repo\.venv\Scripts\python.exe" "$Repo\scripts\install\selftest.py" "$Repo\Projects\Downtown Riverside Metro Link"
if ($LASTEXITCODE -ne 0) { throw "Self-test failed — do not roll out. See output above." }
Write-Host "Windows install complete. Restart Claude Desktop."
```

- [ ] **Step 2: (Pilot machine) run it; capture output**

This is exercised in the pilot (Task 12), not on the dev Mac. The GTK check at step 2 is the make-or-break gate.

- [ ] **Step 3: Commit**

```bash
git add scripts/install/install-windows.ps1
git commit -m "feat(install): Windows (PowerShell) setup script with GTK gate"
```

---

## Task 10: Update scripts

**Files:**
- Create: `scripts/install/update.sh`, `scripts/install/update.ps1`

- [ ] **Step 1: Write `update.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail
REPO="${1:?repo dir}"
git -C "$REPO" pull --ff-only
"$REPO/.venv/bin/pip" install -e "$REPO/skill_assets"
echo "Updated. Restart Claude Desktop."
```

- [ ] **Step 2: Write `update.ps1`**

```powershell
param([Parameter(Mandatory)] [string]$Repo)
$ErrorActionPreference = "Stop"
git -C $Repo pull --ff-only
& "$Repo\.venv\Scripts\pip.exe" install -e "$Repo\skill_assets"
Write-Host "Updated. Restart Claude Desktop."
```

- [ ] **Step 3: Commit**

```bash
git add scripts/install/update.sh scripts/install/update.ps1
git commit -m "feat(install): update scripts (git pull + reinstall)"
```

---

## Task 11: Install runbook + pilot checklist (docs)

**Files:**
- Create: `scripts/install/README.md`

- [ ] **Step 1: Write the runbook**

Include: prerequisites (Python 3.11+, GTK3 runtime on Windows / Homebrew on Mac, Creative Deliverables synced + "Always keep on this device"), the exact install command per OS, how to find the projects-root path, how to restart Claude Desktop, the update procedure, and the troubleshooting table (GTK missing, sync missing, worksheet open, config not picked up). Then the **pilot acceptance checklist** (Task 12).

- [ ] **Step 2: Commit**

```bash
git add scripts/install/README.md
git commit -m "docs(install): IT runbook + pilot checklist"
```

---

## Task 12: Windows pilot (manual acceptance — decision gate)

Not code. Performed with IT on one Windows machine. Record results in the PR/issue.

- [ ] Install GTK3 runtime; confirm `python -c "import weasyprint"` succeeds.
- [ ] Confirm Creative Deliverables is synced + "Always keep on this device."
- [ ] Run `install-windows.ps1`; confirm it ends with `SELF-TEST PASS`.
- [ ] Restart Claude Desktop; confirm the `proposal-builder` tools appear.
- [ ] In Claude Desktop: "list projects" → returns the Creative Deliverables projects.
- [ ] "inspect Morongo" → returns a plain-language readiness report.
- [ ] On a ready project: "generate it" → PDFs appear in `03 - Scope & Pricing` and sync.
- [ ] **Gate:** if the GTK install/render is unreliable → invoke the Docker fallback (separate plan) for Windows; Macs stay native.

---

## Task 13: (Gated) Conversational Brief completion

**Depends on:** creative-team sign-off that the Phase-1/Phase-2 split can collapse (spec "Brief completion" section). Do NOT build until confirmed.

**Files:**
- Modify: `skill_assets/proposal_build_mcp/server.py` (add `update_brief` tool)
- Test: `tests/test_mcp_server.py` (extend)

- [ ] **Step 1: Write the failing test**

```python
def test_update_brief_writes_fields(monkeypatch, tmp_path):
    monkeypatch.setenv("PROPOSAL_BUILD_PROJECTS_ROOT", str(tmp_path))
    proj = tmp_path / "Demo" / "04 - Process & Notes"; proj.mkdir(parents=True)
    (proj / "Project Brief.md").write_text('---\nclient_company: ""\n---\n')
    from proposal_build_mcp import server
    out = server._update_brief_impl("Demo", {"client_company": "Morongo"})
    assert "client_company" in (tmp_path / "Demo" / "04 - Process & Notes" / "Project Brief.md").read_text()
    assert "Morongo" in (tmp_path / "Demo" / "04 - Process & Notes" / "Project Brief.md").read_text()
```

- [ ] **Step 2: Run to verify it fails**, then implement `_update_brief_impl` + `@mcp.tool() update_brief(project, fields)` that safely merges YAML frontmatter fields into the Brief (preserve comments where feasible; never blank existing values it wasn't asked to change). **Step 3:** run to pass. **Step 4:** commit `feat(mcp): conversational Brief field completion`.

---

## Self-Review

- **Spec coverage:** MCP server (T3–5), list/inspect/generate (T5), install scripts Win+Mac (T8–9), Claude Desktop wiring (T6), self-test (T7), data-path config (T3), updates (T10), error handling (T4–5 friendly messages + try/except), testing (T2–6), pilot + Docker gate (T12), Brief-completion decision (T13, gated). All spec sections map to a task.
- **Placeholder scan:** Two implementer NOTEs (api signatures; pip install target) are explicit "confirm against real code" instructions, not lazy placeholders — they exist because exact internal signatures must be read from the current engine. Acceptable and called out.
- **Type consistency:** `InspectResult`/`GenerateResult` defined in T2 are used consistently in T4/T5/T7. Tool `_impl` names match between T5 and tests. `ensure_server` signature matches between T6 impl and tests.

---

## Execution note

Execution is **blocked on externals**, not just code: a Windows pilot machine, IT/CircleCap, and (for Task 13) creative-team sign-off. Tasks 1–7 are pure dev and can be done anytime on the Mac; Tasks 8–12 need the pilot machine.
