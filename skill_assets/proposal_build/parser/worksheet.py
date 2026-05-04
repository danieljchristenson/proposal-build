"""Parse Scope Worksheet.xlsx — find data tables in the mixed-content sheet.

Returns WorksheetData with parsed line items and the optional tier scenarios block.
Validation against tier scenarios (W4) is in validate.py, not here.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import openpyxl

from proposal_build.models import LineItem, Tier


REQUIRED_HEADERS = (
    "Customer-Facing Description", "Zone", "Tiers",
)

# Worksheet header column names → field name on LineItem
HEADER_MAP = {
    "#": "line_num",
    "Item": "item",
    "Description / Location": "description",
    "Qty": "qty",
    "Unit": "unit",
    "Price\nper Unit": "price_per_unit",
    "Line Total": "line_total",
    "Rendering Reference": "rendering_ref",
    "Customer-Facing Description": "customer_facing",
    "Zone": "zone",
    "Tiers": "tiers",
}


class WorksheetParseError(Exception):
    """Raised on a blocking Worksheet problem."""


@dataclass
class WorksheetData:
    line_items: tuple
    scenarios: tuple | None  # ((label, total), ...) or None if block absent

    def tier_sums_per_line(self) -> dict:
        """Sum line_total per tier across line_items. Used by Investment + W4."""
        sums = {Tier.ESSENTIAL: 0.0, Tier.ENHANCED: 0.0, Tier.SIGNATURE: 0.0}
        for li in self.line_items:
            for t in li.tiers:
                sums[t] += li.line_total
        return sums


def parse_worksheet(path: Path) -> WorksheetData:
    if not path.exists():
        raise WorksheetParseError(f"Worksheet not found at {path}")

    wb = openpyxl.load_workbook(str(path), data_only=True)
    ws = wb.active   # Only one sheet expected

    rows = list(ws.iter_rows(values_only=True))

    # Find the first header row that contains all REQUIRED_HEADERS
    header_row_idx = _find_header_row(rows)
    if header_row_idx is None:
        raise WorksheetParseError(
            f"Worksheet missing required column(s): {', '.join(REQUIRED_HEADERS)}"
        )
    headers = [_norm(c) for c in rows[header_row_idx]]
    _verify_headers(headers)

    # Walk rows after the header, parsing data rows until we hit a blank row or summary row.
    line_items = []
    i = header_row_idx + 1
    while i < len(rows):
        row = rows[i]
        if _is_data_row(row):
            line_items.append(_parse_row(row, headers))
        elif _is_section_or_summary_row(row):
            # Try to find another header row (the Enhancements table)
            next_header = _find_header_row(rows, start=i + 1)
            if next_header is not None and next_header < len(rows):
                i = next_header  # jump to next header; loop will skip past it
                # Verify the next header has the same shape
                next_headers = [_norm(c) for c in rows[next_header]]
                if next_headers != headers:
                    raise WorksheetParseError(
                        "Second data table has different columns than the first."
                    )
        i += 1

    # Find the TIER SCENARIOS block
    scenarios = _parse_scenarios(rows)

    return WorksheetData(line_items=tuple(line_items), scenarios=scenarios)


def _norm(cell) -> str:
    if cell is None:
        return ""
    return str(cell).strip()


def _find_header_row(rows: list, start: int = 0) -> int | None:
    for i in range(start, len(rows)):
        normed = [_norm(c) for c in rows[i]]
        if all(h in normed for h in REQUIRED_HEADERS):
            return i
    return None


def _verify_headers(headers: list[str]) -> None:
    missing = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing:
        raise WorksheetParseError(
            f"Worksheet missing required column(s): {', '.join(missing)}"
        )


_LINE_NUM_RE = re.compile(r"^(?:\d+|E\d+)$")


def _is_data_row(row: tuple) -> bool:
    """A data row has a line_num like '1' or 'E6' in column 1."""
    if not row or row[0] is None:
        return False
    return bool(_LINE_NUM_RE.match(str(row[0]).strip()))


def _is_section_or_summary_row(row: tuple) -> bool:
    """Returns True for header-like rows that aren't data rows (e.g., 'OPTIONAL ENHANCEMENTS')."""
    return any(c is not None for c in row)


def _parse_row(row: tuple, headers: list[str]) -> LineItem:
    by_header = {}
    for col, h in enumerate(headers):
        if col >= len(row):
            break
        by_header[h] = row[col]

    tiers_raw = _norm(by_header.get("Tiers", ""))
    tiers = tuple(Tier.from_string(t) for t in tiers_raw.split(",") if t.strip())

    return LineItem(
        line_num=_norm(by_header.get("#", "")),
        item=_norm(by_header.get("Item", "")),
        description=_norm(by_header.get("Description / Location", "")),
        qty=float(by_header.get("Qty") or 0),
        unit=_norm(by_header.get("Unit", "")),
        price_per_unit=float(by_header.get("Price\nper Unit") or 0),
        line_total=float(by_header.get("Line Total") or 0),
        rendering_ref=_norm(by_header.get("Rendering Reference", "")),
        customer_facing=_norm(by_header.get("Customer-Facing Description", "")),
        zone=_norm(by_header.get("Zone", "")),
        tiers=tiers,
    )


def _parse_scenarios(rows: list) -> tuple | None:
    """Find the TIER SCENARIOS block and return ((label, total), ...) or None."""
    for i, row in enumerate(rows):
        cell = _norm(row[0]) if row else ""
        if cell.upper() == "TIER SCENARIOS":
            scenarios = []
            j = i + 1
            while j < len(rows):
                r = rows[j]
                label = _norm(r[1]) if len(r) > 1 else ""
                total = r[6] if len(r) > 6 else None
                if not label or total is None:
                    break
                scenarios.append((label, float(total)))
                j += 1
            return tuple(scenarios) if scenarios else None
    return None
