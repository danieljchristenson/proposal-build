"""Tests for skill_assets/proposal_build/diff/hasher.py."""
from __future__ import annotations

from proposal_build.diff.hasher import hash_string, flatten_brief, hash_brief
from proposal_build.parser.brief import BriefData


def test_hash_string_is_sha256_with_prefix():
    h = hash_string("hello")
    assert h.startswith("sha256:")
    assert len(h) == len("sha256:") + 64  # hex sha256


def test_hash_string_is_deterministic():
    assert hash_string("hello") == hash_string("hello")


def test_hash_string_differs_for_different_input():
    assert hash_string("hello") != hash_string("world")


def test_flatten_brief_top_level():
    bd = BriefData(
        frontmatter={"client_name": "Acme", "project_year": 2026},
        sections={},
    )
    flat = flatten_brief(bd)
    assert flat["client_name"] == "Acme"
    assert flat["project_year"] == 2026


def test_flatten_brief_nested_dict():
    bd = BriefData(
        frontmatter={"tree_comparison": {"trees": ["a", "b"], "recommended": "b"}},
        sections={},
    )
    flat = flatten_brief(bd)
    assert flat["tree_comparison.recommended"] == "b"
    assert flat["tree_comparison.trees.0"] == "a"
    assert flat["tree_comparison.trees.1"] == "b"


def test_flatten_brief_list_of_dicts():
    bd = BriefData(
        frontmatter={"creative_phases": [
            {"label": "ARRIVE", "body": "x"},
            {"label": "GATHER", "body": "y"},
        ]},
        sections={},
    )
    flat = flatten_brief(bd)
    assert flat["creative_phases.0.label"] == "ARRIVE"
    assert flat["creative_phases.0.body"] == "x"
    assert flat["creative_phases.1.body"] == "y"


def test_flatten_brief_includes_sections():
    bd = BriefData(
        frontmatter={"client_name": "Acme"},
        sections={"Creative Direction": "An ornament canopy..."},
    )
    flat = flatten_brief(bd)
    assert flat["sections.Creative Direction"] == "An ornament canopy..."


def test_hash_brief_returns_path_to_hash_map():
    bd = BriefData(
        frontmatter={"client_name": "Acme"},
        sections={"Creative Direction": "x"},
    )
    hashes = hash_brief(bd)
    assert hashes["client_name"].startswith("sha256:")
    assert hashes["sections.Creative Direction"].startswith("sha256:")


def test_hash_brief_deterministic():
    bd1 = BriefData(frontmatter={"a": 1, "b": 2}, sections={})
    bd2 = BriefData(frontmatter={"b": 2, "a": 1}, sections={})  # key order differs
    assert hash_brief(bd1) == hash_brief(bd2)


from pathlib import Path

from proposal_build.diff.hasher import hash_worksheet_rows, hash_file


def test_hash_worksheet_rows_keys_by_item_code():
    rows = [
        {"item_code": "20", "rental_low": 1000, "rental_high": 1200},
        {"item_code": "10-enh", "rental_low": 500, "rental_high": 600},
    ]
    h = hash_worksheet_rows(rows)
    assert "row.20.rental_low" in h
    assert "row.20.rental_high" in h
    assert "row.10-enh.rental_low" in h
    assert h["row.20.rental_low"].startswith("sha256:")


def test_hash_worksheet_rows_handles_hyphen_in_item_code():
    rows = [{"item_code": "10-enh", "rental_low": 500}]
    h = hash_worksheet_rows(rows)
    assert "row.10-enh.rental_low" in h


def test_hash_file_returns_sha256(tmp_path: Path):
    f = tmp_path / "x.txt"
    f.write_bytes(b"hello")
    h = hash_file(f)
    assert h == "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_hash_file_missing_returns_none(tmp_path: Path):
    h = hash_file(tmp_path / "does_not_exist.txt")
    assert h is None
