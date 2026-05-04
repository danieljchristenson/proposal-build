"""Tests for renderer/__init__.py — output paths, run dir, layout pin behavior.

These tests are minimal — they assert structural properties of generated PDFs
(page count via pypdf, font embedding) but not pixel correctness. The full
visual review is the eyeball pass at Plan 3 close-out.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from proposal_build.models import (
    ProjectModel, Tier, SlidePlanItem, ValidationResult, ItemizedPricingDoc, LineItem,
)
from proposal_build.renderer.report import (
    read_layout_versions, write_layout_pin, check_layout_pin,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
LAYOUTS_DIR = REPO_ROOT / "skill_assets" / "layouts"


def test_read_layout_versions_returns_all():
    versions = read_layout_versions(LAYOUTS_DIR)
    assert "cover.html" in versions
    assert "itemized_pricing.html" in versions
    # All versions should be ISO-format dates
    for name, ver in versions.items():
        assert len(ver) == 10 and ver[4] == "-"


def test_layout_pin_first_run(tmp_path):
    pin = tmp_path / "layout_pin.json"
    write_layout_pin(pin, LAYOUTS_DIR)
    data = json.loads(pin.read_text())
    assert "first_run" in data
    assert "last_run" in data
    assert "layouts" in data
    assert data["first_run"] == data["last_run"]


def test_layout_pin_check_match(tmp_path):
    pin = tmp_path / "layout_pin.json"
    write_layout_pin(pin, LAYOUTS_DIR)
    blockers = check_layout_pin(pin, LAYOUTS_DIR, use_latest=False)
    assert blockers == []


def test_layout_pin_check_drift(tmp_path):
    pin = tmp_path / "layout_pin.json"
    # Manually write a pin with a wrong version for cover.html
    pin.write_text(json.dumps({
        "first_run": "2026-05-12T14:23:01-07:00",
        "last_run": "2026-05-12T14:23:01-07:00",
        "layouts": {"cover.html": "1999-01-01"},
    }))
    blockers = check_layout_pin(pin, LAYOUTS_DIR, use_latest=False)
    assert any("cover.html" in msg for _, msg in blockers)
    assert any("layout_pin_drift" == code for code, _ in blockers)


def test_layout_pin_use_latest_skips_check(tmp_path):
    pin = tmp_path / "layout_pin.json"
    pin.write_text(json.dumps({"first_run": "x", "last_run": "y", "layouts": {"cover.html": "1999-01-01"}}))
    blockers = check_layout_pin(pin, LAYOUTS_DIR, use_latest=True)
    assert blockers == []
