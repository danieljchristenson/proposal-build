"""Plan 4: build_project_model must expose brief_data + worksheet_rows in
the artifacts dict so the diff module can compute snapshots without
re-parsing the project."""
from __future__ import annotations

from pathlib import Path

from proposal_build.parser import build_project_model
from proposal_build.parser.brief import BriefData


RIVERSIDE = (
    Path(__file__).resolve().parent.parent
    / "Projects" / "Downtown Riverside Metro Link"
)


def test_artifacts_includes_brief_data():
    model, artifacts = build_project_model(RIVERSIDE)
    assert isinstance(artifacts["brief_data"], BriefData)
    # Sanity: BriefData has both frontmatter and sections
    assert isinstance(artifacts["brief_data"].frontmatter, dict)
    assert isinstance(artifacts["brief_data"].sections, dict)


def test_artifacts_includes_worksheet_rows():
    model, artifacts = build_project_model(RIVERSIDE)
    rows = artifacts["worksheet_rows"]
    assert isinstance(rows, list)
    assert len(rows) > 0
    assert all("item_code" in r for r in rows)
    # Spot-check that other columns are present.
    first = rows[0]
    assert "price" in first
    assert "tier" in first
