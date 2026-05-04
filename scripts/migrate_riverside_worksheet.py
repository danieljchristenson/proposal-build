"""One-shot migration of Riverside MetroLink - Scope Worksheet.xlsx.

Two operations in a single pass:

1. Adds Customer-Facing Description, Zone, Tiers columns to all 25 line items.
   Zone names match the 8-zone structure in Project Brief.md.

2. Restructures the TIER SCENARIOS block + tier-model legend bullet to reflect
   the consistent-garland-treatment principle: garland decoration is uniform
   within each tier (never mixed undecorated/decorated within the same tier).
   - ESSENTIAL: $88,906 — base only, all garland undecorated
   - ENHANCED:  $124,292 — base + 5 visual-interest add-ons (E1, E2, E7, E11, E12); garland still all undecorated
   - SIGNATURE: $200,249 — enhanced + Bell Display + Spiral LED Tree (replaces
                          Traditional) + ALL four garland sections decorated

Idempotent: running twice produces the same result. Kept in repo for
reproducibility — future projects can model after it.
"""
from __future__ import annotations

from pathlib import Path

import openpyxl

REPO = Path(__file__).resolve().parent.parent
WORKSHEET = REPO / "Projects" / "Downtown Riverside Metro Link" / "03 - Scope & Pricing" / "Riverside MetroLink - Scope Worksheet.xlsx"

# (line_num, customer_facing, zone, tiers)
RIVERSIDE_MIGRATION = {
    "1":  ("Branded 'Holiday Express' pole banners — one-time purchase; customer-owned, designed in-house.",
           "Pole Banner Program", "Essential, Enhanced, Signature"),
    "2":  ("Powder-coated steel pole banner brackets — one-time purchase; customer-owned, reusable indefinitely.",
           "Pole Banner Program", "Essential, Enhanced, Signature"),
    "3":  ("Annual install of pole banner program at season open; removal at season close. Storage between seasons included.",
           "Pole Banner Program", "Essential, Enhanced, Signature"),
    "4":  ("Warm-white string lighting on the eaves of all 16 platform canopies — 1,024 lineal feet of evening glow across the platforms.",
           "Canopy & Platform Lighting", "Essential, Enhanced, Signature"),
    "5":  ("Warm-white string lighting on the bus stop waiting canopies — additional warm-white evening accent at the perimeter.",
           "Canopy & Platform Lighting", "Essential, Enhanced, Signature"),
    "6":  ("Lit evergreen garland swagged across the perimeter fence — 621 lineal feet of warm-white glow framing the property edge.",
           "Perimeter & Driveway Garlands", "Essential, Enhanced, Signature"),
    "7":  ("Lit evergreen garland on the building eave — warm-white evening accent that reads from the platforms.",
           "Perimeter & Driveway Garlands", "Essential, Enhanced, Signature"),
    "8":  ("Lit evergreen garland on the center driveway gates — the welcome gesture as guests enter the station.",
           "Perimeter & Driveway Garlands", "Essential, Enhanced, Signature"),
    "9":  ("Custom-fabricated 5 ft lighted wreaths between the four entrance brick columns — the threshold gesture of the program.",
           "Station Entrance Wreaths", "Essential, Enhanced, Signature"),
    "10": ("Oversized 10 ft lighted wreath on the stair tower — a feature element visible from a block away.",
           "Stair Tower Feature", "Essential, Enhanced, Signature"),
    "11": ("18 ft traditional Christmas tree at the centerpiece location — pre-lit warm white with red, green, and gold ornaments.",
           "Plaza Centerpiece", "Essential, Enhanced"),
    "12": ("Walk-through warm-white lighted ornament archway at the bus loading island — a photo moment and the visual anchor of the program.",
           "Walk-Through Photo Moments", "Essential, Enhanced, Signature"),
    "E1": ("Lighted snowflakes along the bridge and platform railings — additional warm-white evening accents.",
           "Signature Add-Ons", "Enhanced, Signature"),
    "E2": ("Walk-through lighted gift box archway with red bow — additional photo moment and high social-media value installation.",
           "Walk-Through Photo Moments", "Enhanced, Signature"),
    "E3": ("Custom 'City of Riverside' lighted bell display — Mission Inn-style, branded for the City. One-time custom fabrication, customer-owned.",
           "Signature Add-Ons", "Signature"),
    "E4": ("Annual install and removal of the City of Riverside Bell Display each season.",
           "Signature Add-Ons", "Signature"),
    "E5": ("Off-season climate-controlled storage of the customer-owned Bell Display.",
           "Signature Add-Ons", "Signature"),
    "E6": ("21 ft red-and-green LED spiral tree with gold star topper — the Signature-tier alternative to the Traditional centerpiece tree.",
           "Plaza Centerpiece", "Signature"),
    "E7": ("Stacked oversized lighted gift box pyramid — 12 ft tall, additional photo moment at a separate plaza location.",
           "Signature Add-Ons", "Enhanced, Signature"),
    "E8":  ("Decorated garland upgrade — adds red, green & gold ornament clusters and bows to the perimeter fence garland.",
            "Perimeter & Driveway Garlands", "Signature"),
    "E9":  ("Decorated garland upgrade — adds red, green & gold ornament clusters and bows to the building eave garland.",
            "Perimeter & Driveway Garlands", "Signature"),
    "E10": ("Decorated garland upgrade — adds red, green & gold ornament clusters and bows to the center driveway gate garland.",
            "Perimeter & Driveway Garlands", "Signature"),
    "E11": ("Illuminated 'Happy Holidays' overhead marquee with skyline silhouette — custom-fabricated signage element.",
            "Plaza Centerpiece", "Enhanced, Signature"),
    "E12": ("Lit evergreen garland on the staircase tower and railing — warm-white evening accent on the vertical stair-tower feature.",
            "Stair Tower Feature", "Enhanced, Signature"),
    "E13": ("Decorated garland upgrade — adds red, green & gold ornament clusters and bows to the staircase tower garland.",
            "Stair Tower Feature", "Signature"),
}

# Tier-scenarios block + legend updates (operation 2 — see module docstring).
# Row positions: R43 = Enhanced; R44 = Signature; R57 = tier-model legend bullet.
TIER_SCENARIOS = {
    43: (
        "ENHANCED ⭐ — Base + Snowflakes + Walk-Through Gift Box + Gift Box Tower + Happy Holidays Sign + Staircase Garland (Undecorated)",
        124292,
    ),
    44: (
        "SIGNATURE — Enhanced + Bell Display + Spiral LED Tree (replaces Traditional) + All Garlands Decorated",
        200249,
    ),
}
TIER_MODEL_BULLET = (
    "• Tier model: garland decoration treatment is uniform within each tier — never mixed. "
    "ESSENTIAL = base scope, all garland undecorated. "
    "ENHANCED = base + Snowflakes + Walk-Through Gift Box + Gift Box Tower (new location) + Happy Holidays Sign + Staircase Garland (still undecorated). "
    "SIGNATURE = Enhanced + Bell Display + Spiral LED Tree (replaces Traditional) + ALL four garland sections upgraded to decorated."
)
TIER_MODEL_BULLET_ROW = 57


def main() -> None:
    if not WORKSHEET.exists():
        raise SystemExit(f"Worksheet not found: {WORKSHEET}")

    # openpyxl strips formula caches on save, breaking parser's data_only reads.
    # Workaround: snapshot all cached values up front, then write them back as
    # static values for any cell that currently holds a formula. Tradeoff —
    # the worksheet's formulas (Line Total, TIER SCENARIOS sums, etc.) become
    # hardcoded numbers. Editing Qty/Price/Unit in Excel afterwards will not
    # auto-update Line Total; AE must update Line Total manually if quantities
    # change. Customer-facing description edits (the polish workflow) are
    # unaffected.
    wb_values = openpyxl.load_workbook(str(WORKSHEET), data_only=True)
    ws_values = wb_values.active
    cached: dict[tuple[int, int], object] = {}
    for row in ws_values.iter_rows():
        for cell in row:
            if cell.value is not None:
                cached[(cell.row, cell.column)] = cell.value

    wb = openpyxl.load_workbook(str(WORKSHEET))
    ws = wb.active

    # Convert all formula cells to their cached static values
    formulas_replaced = 0
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith("="):
                cached_val = cached.get((cell.row, cell.column))
                if cached_val is not None:
                    cell.value = cached_val
                    formulas_replaced += 1
    print(f"Converted {formulas_replaced} formulas to static values.")

    # Find header row(s). The Riverside file has TWO header rows
    # (one for Base Scope, one for Enhancements) — both must get the new columns.
    rows = list(ws.iter_rows(values_only=False))
    header_indices = []
    for i, row in enumerate(rows):
        if row[0].value == "#" and row[1].value == "Item":
            header_indices.append(i + 1)   # openpyxl is 1-indexed
    print(f"Found {len(header_indices)} header rows at: {header_indices}")

    # Add the 3 new column headers after the existing 10
    NEW_HEADERS = ("Customer-Facing Description", "Zone", "Tiers")
    for hi in header_indices:
        for offset, name in enumerate(NEW_HEADERS, start=11):
            ws.cell(row=hi, column=offset, value=name)

    # Walk all data rows; fill in the 3 new columns from RIVERSIDE_MIGRATION
    filled = 0
    for row in ws.iter_rows():
        line_num = row[0].value
        if line_num is None:
            continue
        line_str = str(line_num).strip()
        if line_str in RIVERSIDE_MIGRATION:
            cf, zone, tiers = RIVERSIDE_MIGRATION[line_str]
            row[10].value = cf
            row[11].value = zone
            row[12].value = tiers
            filled += 1
    print(f"Filled {filled} data rows with the 3 new columns.")

    # Operation 2: tier-scenarios block + tier-model legend bullet
    for row_idx, (label, total) in TIER_SCENARIOS.items():
        ws.cell(row=row_idx, column=2, value=label)
        ws.cell(row=row_idx, column=7, value=total)
    ws.cell(row=TIER_MODEL_BULLET_ROW, column=1, value=TIER_MODEL_BULLET)
    print(f"Updated {len(TIER_SCENARIOS)} tier-scenarios rows + 1 legend bullet.")

    wb.save(str(WORKSHEET))
    print(f"Saved: {WORKSHEET}")


if __name__ == "__main__":
    main()
