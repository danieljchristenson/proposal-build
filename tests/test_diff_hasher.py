"""Tests for skill_assets/proposal_build/diff/hasher.py."""
from __future__ import annotations

from proposal_build.diff.hasher import hash_string


def test_hash_string_is_sha256_with_prefix():
    h = hash_string("hello")
    assert h.startswith("sha256:")
    assert len(h) == len("sha256:") + 64  # hex sha256


def test_hash_string_is_deterministic():
    assert hash_string("hello") == hash_string("hello")


def test_hash_string_differs_for_different_input():
    assert hash_string("hello") != hash_string("world")
