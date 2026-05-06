"""Smoke test: skill bundle has the structure Claude Desktop and AEs expect."""
from __future__ import annotations

from pathlib import Path

import frontmatter


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_BUNDLE = REPO_ROOT / "skill_assets"


def test_skill_md_exists_and_parses():
    p = SKILL_BUNDLE / "skill.md"
    assert p.is_file(), "skill_assets/skill.md missing"
    post = frontmatter.load(str(p))
    assert post.metadata.get("name"), "skill.md missing `name`"
    desc = post.metadata.get("description", "")
    assert isinstance(desc, str) and len(desc) > 30, \
        "skill.md `description` must be a substantive string"
    # Activation phrases the skill claims to handle
    for phrase in ("build a proposal", "generate"):
        assert phrase.lower() in desc.lower(), \
            f"skill.md description should mention activation phrase: {phrase}"


def test_skill_md_body_has_required_steps():
    body = frontmatter.load(str(SKILL_BUNDLE / "skill.md")).content
    for header in ("## Step 1", "## Step 2", "## Step 3", "## Step 4",
                   "## Step 5", "## Step 6", "## Beta safety rail"):
        assert header in body, f"skill.md body missing section: {header}"


def test_ae_sop_exists_and_has_required_sections():
    p = SKILL_BUNDLE / "AE_SOP.md"
    assert p.is_file(), "skill_assets/AE_SOP.md missing"
    body = p.read_text()
    for section in ("## Setup (one-time)", "## Daily workflow", "## Reference"):
        assert section in body, f"AE_SOP.md missing section: {section}"
    assert len(body) > 1000, "AE_SOP.md suspiciously short"
