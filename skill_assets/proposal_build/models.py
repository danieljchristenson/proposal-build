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
    # Customer-side primary contact — shown on Cover + Sign-off slides.
    # Optional (defaults to empty strings) so older Briefs still parse cleanly.
    client_contact_name: str = ""
    client_contact_title: str = ""
    client_contact_email: str = ""
    client_contact_phone: str = ""
    # Greenery / material reference images for the Creative Vision slide.
    # AE picks a curated subset in Brief frontmatter — these appear as a
    # thumbnail grid replacing the single hero image when non-empty.
    # Files live in the project's `Greenery references/` folder.
    greenery_references: Tuple[str, ...] = ()
    # Per-tier cards on the Investment slide. AE-authored in Brief frontmatter:
    #   tier_highlights:
    #     essential: { tagline: "...", items: [..., ..., ...] }
    #     enhanced:  { tagline: "...", items: [..., ..., ...] }
    #     signature: { tagline: "...", items: [..., ..., ...] }
    # When absent, the Investment slide falls back to empty-tagline / empty-list
    # cards (the V1 behavior). Map keys are tier names lowercased.
    tier_highlights: Mapping[str, dict] = field(default_factory=dict)
    # Optional Brief-authored override for the Understanding slide's
    # VENUE & CONTEXT panel. When non-empty, replaces the auto-generated
    # zone-summary one-liner.
    venue_context: str = ""
    # Optional Brief-authored override for the Greenery Mood Board copy
    # block. When non-empty, replaces the default tier-progression copy
    # in build_material_palette_ctx — useful for single-tier projects
    # where the base→Signature progression line doesn't apply.
    greenery_description: str = ""
    # AE-supplied list of past_work_library project IDs. When non-empty, the
    # composer emits a sample_of_work slide. Must contain exactly 6 IDs at
    # generation time; inspector enforces. Empty tuple → slide skipped.
    sample_work: Tuple[str, ...] = ()
    # Visual theme: "editorial" (default) or "classic" (opt-out via theme: classic in Brief).
    theme: str = "editorial"


@dataclass(frozen=True)
class ItemizedPricingDoc:
    """One per offered tier. Composer builds these; Renderer turns them into PDFs."""
    tier: Tier
    project: ProjectModel
    base_scope_lines: Tuple[LineItem, ...]
    enhancement_lines: Tuple[LineItem, ...]
    tier_total: float


class ProposalMode(str, Enum):
    """Selects which compose path the pipeline runs.

    TIERED: existing Essential/Enhanced/Signature path (Riverside, Sheraton, Pier 39).
    MENU:   creative-menu / ROM pricing path (FIGat7th).
    """
    TIERED = "tiered"
    MENU = "menu"


@dataclass(frozen=True)
class ROMLineItem:
    """Line item for ROM (Rough Order of Magnitude) pricing.

    Each item carries six numbers: rental low/high (all-inclusive annual fee),
    purchase one-time low/high, and purchase annual service low/high (install +
    removal + storage bundled).

    Point estimates (no range) are stored as low==high.

    Alternate groups: items sharing an `alternate_group` value are mutually
    exclusive options (customer picks one). Totals across the group are
    bookended by min(low) and max(high) of group members.
    """
    code: str            # e.g. "20", "10-enh", "30"
    section: str         # human-readable section key, e.g. "Arches"
    name: str
    description: str
    alternate_group: str
    rental_low: int
    rental_high: int
    purchase_ot_low: int
    purchase_ot_high: int
    purchase_svc_low: int
    purchase_svc_high: int
    customer_facing: str
    materials: str
    notes: str
    rendering_ref: str

    @property
    def is_alternate(self) -> bool:
        return bool(self.alternate_group)

    @property
    def is_point_estimate(self) -> bool:
        return (self.rental_low == self.rental_high
                and self.purchase_ot_low == self.purchase_ot_high
                and self.purchase_svc_low == self.purchase_svc_high)


@dataclass(frozen=True)
class Section:
    """A grouping of ROMLineItems on the proposal.

    key:      stable identifier ("1", "2", "3a", "3b" — used to order sections)
    label:    full table-row label ("Section 3a — Plaza Arches (customer picks one)")
    name:     short title for the section header strip on the lead slide
    is_lead:  if True, this section's first slide carries a section header block
    items:    tuple of ROMLineItems in display order
    """
    key: str
    label: str
    name: str
    is_lead: bool
    items: Tuple[ROMLineItem, ...]

    @property
    def has_alternates(self) -> bool:
        return any(it.is_alternate for it in self.items)


@dataclass(frozen=True)
class MenuProjectModel:
    """Fully-resolved project state for the creative-menu proposal mode.

    Parallel to ProjectModel, but with sections + ROMLineItems instead of
    zones + LineItems with tiers. The composer picks the right model based
    on Brief frontmatter `mode`.
    """
    client_company: str
    client_short: str
    project_name: str
    project_short: str
    project_year: int
    project_subtitle: str

    presenter_name: str
    presenter_title: str
    presenter_org: str
    proposal_date: str

    client_contact_name: str
    client_contact_title: str
    client_contact_email: str
    client_contact_phone: str

    design_phrase: str
    voice: str

    creative_direction: str
    customer_goals: Tuple[str, ...]
    creative_phases: Tuple[dict, ...]   # [{"label": "ARRIVE", "body": "..."}]

    prebuilt_cover_image: str           # filename in Base Scope/
    prebuilt_palette_image: str         # filename in Base Scope/ (or "" if no palette slide)
    creative_vision_hero: str           # filename for the creative-vision page hero

    sections: Tuple[Section, ...]
    what_youre_approving: str
    # AE-supplied list of past_work_library project IDs. Same semantics as
    # ProjectModel.sample_work.
    sample_work: Tuple[str, ...] = ()
    # AE-supplied tree-comparison block. When non-empty:
    #   {"trees": ["tree_30", "tree_40", "tree_50"], "recommended": "tree_50"}
    # → composer emits an Alternate Tree Options slide before sign_off.
    # Empty dict (default) → slide skipped silently.
    tree_comparison: Mapping[str, object] = field(default_factory=dict)
