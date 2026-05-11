"""Tests for the ROM (Rough Order of Magnitude) pricing data model
used by the creative-menu proposal mode."""
from __future__ import annotations

import pytest

from proposal_build.models import (
    ProposalMode, ROMLineItem, Section, MenuProjectModel,
)


def test_proposal_mode_values():
    assert ProposalMode.TIERED.value == "tiered"
    assert ProposalMode.MENU.value == "menu"


def test_rom_line_item_basic():
    item = ROMLineItem(
        code="20",
        section="Overhead",
        name="Mixed Ornament Canopy",
        description="16 oversized 6-foot overhead ornaments forming a layered canopy.",
        alternate_group="",
        rental_low=22400,
        rental_high=22400,
        purchase_ot_low=19200,
        purchase_ot_high=19200,
        purchase_svc_low=18600,
        purchase_svc_high=18600,
        customer_facing="An ornament canopy that turns the FIGat7th courtyard ceiling into a winter night sky.",
        materials="Steel/metal frames; warm-white and cool-white LED lights; tinsel; rope light.",
        notes="",
        rendering_ref="20_overhead-mixed-canopy.png",
    )
    assert item.is_alternate is False
    assert item.is_point_estimate is True


def test_rom_line_item_range_and_alternate():
    item = ROMLineItem(
        code="43", section="Standalones", name="Gift Box Trio",
        description="", alternate_group="",
        rental_low=4000, rental_high=6000,
        purchase_ot_low=6000, purchase_ot_high=8000,
        purchase_svc_low=4000, purchase_svc_high=7000,
        customer_facing="", materials="", notes="",
        rendering_ref="43_gift-box-trio.png",
    )
    assert item.is_point_estimate is False
    arch = ROMLineItem(
        code="30", section="Arches", name="Letter Arch",
        description="", alternate_group="arch_alternates",
        rental_low=9500, rental_high=9500,
        purchase_ot_low=9000, purchase_ot_high=9000,
        purchase_svc_low=2000, purchase_svc_high=2000,
        customer_facing="", materials="", notes="",
        rendering_ref="30_arch-letters-happy-holidays.png",
    )
    assert arch.is_alternate is True


def test_section_holds_ordered_items():
    item_a = ROMLineItem(
        code="30", section="Arches", name="Letter Arch", description="",
        alternate_group="arch_alternates",
        rental_low=9500, rental_high=9500,
        purchase_ot_low=9000, purchase_ot_high=9000,
        purchase_svc_low=2000, purchase_svc_high=2000,
        customer_facing="", materials="", notes="", rendering_ref="",
    )
    item_b = ROMLineItem(
        code="31", section="Arches", name="Bauble Arch", description="",
        alternate_group="arch_alternates",
        rental_low=9000, rental_high=9000,
        purchase_ot_low=8900, purchase_ot_high=8900,
        purchase_svc_low=2000, purchase_svc_high=2000,
        customer_facing="", materials="", notes="", rendering_ref="",
    )
    section = Section(
        key="3a",
        label="Section 3a — Plaza Arches (customer picks one)",
        name="Plaza Arches",
        is_lead=True,
        items=(item_a, item_b),
    )
    assert section.has_alternates is True
    assert len(section.items) == 2


def test_menu_project_model_smoke():
    model = MenuProjectModel(
        client_company="FIGat7th",
        client_short="FIGat7th DTLA",
        project_name="FIGat7th DTLA — 2026 Holiday Program",
        project_short="FIGat7th DTLA",
        project_year=2026,
        project_subtitle="First-Pass Creative Menu",
        presenter_name="Daniel Christenson",
        presenter_title="Director of Sales",
        presenter_org="St. Nick's Christmas Lighting & Décor",
        proposal_date="May 9, 2026",
        client_contact_name="Alexandra Castro",
        client_contact_title="Property Manager, Athena Property Management",
        client_contact_email="acastro@athenapm.com",
        client_contact_phone="",
        design_phrase="Modern Magic",
        voice="destination-retail",
        creative_direction="FIGat7th becomes Downtown LA's most photographed holiday destination.",
        customer_goals=("Drive foot traffic.", "Generate Instagram moments.", "Athena's first-year statement."),
        creative_phases=(
            {"label": "ARRIVE", "body": "An ornament canopy turns the courtyard into a winter night sky."},
            {"label": "GATHER", "body": "The centerpiece tree anchors the plaza."},
            {"label": "EXPLORE", "body": "A menu of arches, frames, and selfie moments."},
        ),
        prebuilt_cover_image="01_cover-slide-cityscape.png",
        prebuilt_palette_image="02_palette-board-mood.png",
        creative_vision_hero="10_tree-A-studio-blackbg.png",
        sections=(),
        what_youre_approving="Approve this first-pass creative menu and ROM pricing as the basis for site walk.",
    )
    assert model.client_company == "FIGat7th"
    assert model.design_phrase == "Modern Magic"
