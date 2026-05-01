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
