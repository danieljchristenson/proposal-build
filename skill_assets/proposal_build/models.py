"""ProjectModel and supporting dataclasses — the contract between Parser and Composer.

ProjectModel is intentionally shaped to match what the existing layout test
fixtures (tests/fixtures/pier_39.py, riverside.py) produce by hand. Composer
emits context dicts of the same shape; Renderer never reads anything else.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Tuple


class Tier(str, Enum):
    ESSENTIAL = "Essential"
    ENHANCED = "Enhanced"
    SIGNATURE = "Signature"

    @classmethod
    def from_string(cls, s: str) -> "Tier":
        s = s.strip()
        for t in cls:
            if t.value.lower() == s.lower():
                return t
        raise ValueError(f"Unknown tier: {s!r}")


@dataclass(frozen=True)
class Zone:
    num: str
    name: str
    subtitle: str
    flags: Tuple[str, ...]
    hero_image: str
    bullets: Tuple[str, ...]
    layout_override: str | None = None
    # Optional list of additional images for the zone_solo_gallery layout.
    # When zone_solo_gallery is used, the gallery shows hero_images if non-empty,
    # otherwise falls back to (hero_image,). Other layouts ignore this field.
    hero_images: Tuple[str, ...] = ()
    # Gallery presentation hints (zone_solo_gallery layout only):
    #   gallery_fit: 'cover' (default) crops to fill; 'contain' shows full image
    #     with letterboxing — use for banner artwork or anything where the
    #     full design must be visible.
    #   gallery_orientation: 'stacked' (default) places images vertically;
    #     'horizontal' places them side-by-side — best for 2 portrait images
    #     (e.g., a pair of pole-banner artworks).
    gallery_fit: str = "cover"
    gallery_orientation: str = "stacked"
    # gallery_emphasis: 'equal' (default) gives every image the same width;
    # 'feature_first' makes the first image 2x wider than the rest — use when
    # one image is the marquee shot and others are supporting context.
    gallery_emphasis: str = "equal"
    # Hero image fit hint (zone_solo / zone_solo_fullbleed layouts):
    #   hero_fit: 'cover' (default) | 'contain'  — same semantics as gallery_fit
    #   but applied to the single hero_image. Use 'contain' when the rendering
    #   is shot at a perspective angle that captures the full space and
    #   shouldn't be cropped.
    hero_fit: str = "cover"

    @property
    def is_flagship(self) -> bool:
        return "flagship" in self.flags

    @property
    def is_signature(self) -> bool:
        return "signature" in self.flags

    @property
    def gallery_images(self) -> Tuple[str, ...]:
        """Resolved image list for gallery layouts: prefer hero_images, fall back to hero_image."""
        if self.hero_images:
            return self.hero_images
        return (self.hero_image,) if self.hero_image else ()


@dataclass(frozen=True)
class LineItem:
    line_num: str
    item: str
    description: str
    qty: float
    unit: str
    price_per_unit: float
    line_total: float
    rendering_ref: str
    customer_facing: str
    zone: str
    tiers: Tuple[Tier, ...]

    @property
    def is_enhancement(self) -> bool:
        return self.line_num.startswith("E")


@dataclass(frozen=True)
class SlidePlanItem:
    layout_name: str
    context: dict

    def __iter__(self):
        yield self.layout_name
        yield self.context


@dataclass
class ValidationResult:
    blockers: list
    warnings: list
    fills_log: list = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.blockers) == 0

    @property
    def status(self) -> str:
        return "PASSED" if self.passed else "BLOCKED"


@dataclass(frozen=True)
class ProjectModel:
    """Fully-resolved project state ready for Composer."""
    client_company: str
    client_short: str
    project_name: str
    project_short: str
    project_year: int
    project_subtitle: str
    proposal_type: str

    presenter_name: str
    presenter_title: str
    presenter_email: str
    presenter_phone: str
    proposal_date: str

    go_live: str
    season_end: str
    fabrication_lock: str
    signing_deadline: str

    voice: str
    recommended_tier: Tier
    design_phrase: str
    pricing_format: str

    cover_image: str
    creative_vision_hero: str
    case_study: str
    case_study_hero: str

    zones: Tuple[Zone, ...]
    line_items: Tuple[LineItem, ...]

    creative_direction: str
    customer_goals: Tuple[str, ...]
    customer_constraints: Tuple[str, ...]
    success_criteria: Tuple[str, ...]
    what_youre_approving: str

    pillars: Tuple[dict, ...]
    phases: Tuple[dict, ...]
    scope_includes: Tuple[str, ...]
    add_ons: Tuple[Tuple[str, str], ...]
    term_panels: Mapping[str, str]
    after_approval_steps: Tuple[str, ...]

    company_facts: Tuple[str, ...]
    team: Tuple[dict, ...]
    contact_strip: str
    partnership_discounts: Tuple[Tuple[str, str], ...]

    slide_plan_override: Tuple[dict, ...] = ()
    resolved_renderings: Mapping[str, str] = field(default_factory=dict)
    # Per-tier cards on the Investment slide. AE-authored in Brief frontmatter:
    #   tier_highlights:
    #     essential: { tagline: "...", items: [..., ..., ...] }
    #     enhanced:  { tagline: "...", items: [..., ..., ...] }
    #     signature: { tagline: "...", items: [..., ..., ...] }
    # When absent, the Investment slide falls back to empty-tagline / empty-list
    # cards (the V1 behavior). Map keys are tier names lowercased.
    tier_highlights: Mapping[str, dict] = field(default_factory=dict)


@dataclass(frozen=True)
class ItemizedPricingDoc:
    """One per offered tier. Composer builds these; Renderer turns them into PDFs."""
    tier: Tier
    project: ProjectModel
    base_scope_lines: Tuple[LineItem, ...]
    enhancement_lines: Tuple[LineItem, ...]
    tier_total: float
