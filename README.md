# St. Nick's Proposal Builder

Claude Desktop skill that turns RFP materials, a structured project brief, a scope worksheet, and renderings into polished, on-brand customer proposals.

## Where to start

- **Design spec:** [`docs/superpowers/specs/2026-05-01-proposal-builder-skill-design.md`](docs/superpowers/specs/2026-05-01-proposal-builder-skill-design.md)
- **Implementation plans:** [`docs/superpowers/plans/`](docs/superpowers/plans/) — sequenced 01–09
- **Repo guide for Claude Code sessions:** [`CLAUDE.md`](CLAUDE.md)

## Local development

Requires Python 3.11+.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

WeasyPrint (declared in `pyproject.toml`) requires system-level cairo, pango, and gdk-pixbuf libraries on macOS — install via `brew install cairo pango gdk-pixbuf` if `pip install` errors on it.
