---
# Client
client_company: ""
client_decision_maker: ""
client_decision_maker_title: ""
client_decision_maker_email: ""
client_address: ""              # optional

# Project
project_name: ""
project_short: ""               # used in footers
project_year:

# Presenter
presenter_name: ""
presenter_email: ""
presenter_phone: ""

# Schedule (only go_live is required; rest auto-derive if blank)
go_live: ""
season_end: ""
fabrication_lock: ""            # default: go_live − 90 days
signing_deadline: ""            # default: go_live − 21 days

# Tone & creative
voice: ""                       # civic | destination-retail | corporate | hospitality
recommended_tier: ""            # essential | enhanced | signature
design_phrase: ""               # short title-style phrase, no trailing period

# Understanding slide
venue_context: ""               # optional. Replaces the auto-generated
                                # "X is a Y-zone program covering ..." one-liner
                                # on the Understanding slide. Use this for richer
                                # venue descriptions: scale, attendance, foot
                                # traffic, atmosphere. Falls back to auto-generated
                                # when empty.

# Assets
cover_image: ""
case_study: ""                  # filename (sans .md) or "skip"

# Greenery / mood-board references (optional)
# A curated list of image filenames shown as a 4-up grid on the Greenery
# Mood Board slide. The resolver searches THREE folders in priority order:
#   1. Greenery references/         (project-level greenery library)
#   2. 02 - Renderings/Base Scope/  (your project renderings)
#   3. 02 - Renderings/Enhancements/
# Pull project renderings (e.g. an undecorated swag shot) into the mood
# board without duplicating the file.
greenery_references: []
greenery_description: ""        # optional override for the Greenery Mood Board
                                # copy block. Empty = use the default tier-
                                # progression copy. Set this when the default
                                # doesn't apply (e.g. single-tier projects).

# Slide control (defaults shown, only set to override)
include_case_study: true
include_add_ons: true
pricing_format: "tiered"        # tiered | single
mode: "one-shot"                # one-shot | checkpoint

# Sample of Our Work, array of past_work IDs (optional; default = best-of for voice)
sample_work: []
---

## Creative Direction

(2–3 sentences. Sets the visual narrative for slide 4.)

## Customer Goals
-
-

## Customer Success Criteria
-
-

## Constraints
- (bullet, or "none" to omit the box on slide 3)

## Showcase Sections
1. **Section Name**, one-line subtitle
2. **Section Name**, one-line subtitle
3. **Section Name**, one-line subtitle

## Zone Bullet Starters

Reference patterns to copy into a zone's `bullets:` list when applicable.

**Pole banner zones** (any zone whose name contains "Pole Banner"):
- "Custom artwork option: we can design any pole banner from scratch or adapt your existing style guide"

(Add more starters here as patterns recur across projects.)
