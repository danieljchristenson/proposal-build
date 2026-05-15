"""Tests for revisions/v<n>/ archival."""
from __future__ import annotations

from pathlib import Path

from proposal_build.diff.revisions import copy_to_revision, next_revision_number


def _make_artifacts(tmp: Path) -> dict[str, Path]:
    notes = tmp / "04 - Process & Notes"
    output = tmp / "05 - Output"
    pricing = tmp / "03 - Scope & Pricing"
    notes.mkdir(parents=True)
    output.mkdir(parents=True)
    pricing.mkdir(parents=True)
    deck = output / "deck.pdf"
    deck.write_bytes(b"deck content")
    itemized = pricing / "itemized.pdf"
    itemized.write_bytes(b"itemized content")
    workbook = pricing / "workbook.xlsx"
    workbook.write_bytes(b"workbook content")
    summary = output / "change_summary.md"
    summary.write_text("# summary\n")
    last_run = notes / "last_run.json"
    last_run.write_text('{"schema_version": 1}')
    return {
        "notes_dir": notes,
        "deck": deck, "itemized": itemized, "workbook": workbook,
        "summary": summary, "last_run": last_run,
    }


def test_next_revision_number_when_no_revisions_dir(tmp_path: Path):
    notes = tmp_path / "04 - Process & Notes"
    notes.mkdir()
    assert next_revision_number(notes) == 1


def test_next_revision_number_with_existing_revisions(tmp_path: Path):
    notes = tmp_path / "04 - Process & Notes"
    (notes / "revisions" / "v1").mkdir(parents=True)
    (notes / "revisions" / "v3").mkdir(parents=True)
    (notes / "revisions" / "v2").mkdir(parents=True)
    assert next_revision_number(notes) == 4


def test_copy_to_revision_creates_v1_folder(tmp_path: Path):
    a = _make_artifacts(tmp_path)
    copy_to_revision(
        notes_dir=a["notes_dir"], revision=1,
        deck=a["deck"], itemized=a["itemized"],
        workbook=a["workbook"], change_summary=a["summary"],
        last_run_json=a["last_run"],
    )
    v1 = a["notes_dir"] / "revisions" / "v1"
    assert (v1 / "deck.pdf").read_bytes() == b"deck content"
    assert (v1 / "itemized.pdf").read_bytes() == b"itemized content"
    assert (v1 / "workbook.xlsx").read_bytes() == b"workbook content"
    assert (v1 / "change_summary.md").exists()
    assert (v1 / "last_run.json").exists()


def test_copy_to_revision_overwrites_existing(tmp_path: Path):
    a = _make_artifacts(tmp_path)
    v2 = a["notes_dir"] / "revisions" / "v2"
    v2.mkdir(parents=True)
    (v2 / "deck.pdf").write_bytes(b"stale")
    copy_to_revision(
        notes_dir=a["notes_dir"], revision=2,
        deck=a["deck"], itemized=a["itemized"],
        workbook=a["workbook"], change_summary=a["summary"],
        last_run_json=a["last_run"],
    )
    assert (v2 / "deck.pdf").read_bytes() == b"deck content"
