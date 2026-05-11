"""Parse the ROM (Rough Order of Magnitude) Scope Worksheet for menu-mode proposals.

The ROM worksheet's column shape differs from the tiered worksheet
(see parser/worksheet.py):

  # | Section | Item Name | Description / Build Notes | Alternate Group
    | Rental Low | Rental High | Purchase OT Low | Purchase OT High
    | Purchase Svc Low | Purchase Svc High | Customer-Facing Description
    | Materials / Build | Notes / Assumptions | Rendering Reference

The sheet also contains section divider rows (single label cell in column A,
the rest empty) interspersed between item groups. Those are skipped here;
the `section` field on each ROMLineItem captures the grouping.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import openpyxl

from proposal_build.models import ROMLineItem


REQUIRED_HEADERS = (
    "#", "Section", "Item Name", "Alternate Group",
    "Rental Low", "Rental High",
    "Purchase OT Low", "Purchase OT High",
    "Purchase Svc Low", "Purchase Svc High",
    "Customer-Facing Description", "Rendering Reference",
)


class ROMWorksheetParseError(Exception):
    """Raised on a blocking ROM-worksheet problem."""


@dataclass(frozen=True)
class ROMWorksheetData:
    line_items: Tuple[ROMLineItem, ...]


def parse_rom_worksheet(path: Path) -> ROMWorksheetData:
    if not path.exists():
        raise ROMWorksheetParseError(f"Worksheet not found at {path}")

    wb = openpyxl.load_workbook(str(path), data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    header_idx = _find_header_row(rows)
    if header_idx is None:
        raise ROMWorksheetParseError(
            f"Worksheet missing required columns: {', '.join(REQUIRED_HEADERS)}"
        )
    headers = [_norm(c) for c in rows[header_idx]]
    col = {h: i for i, h in enumerate(headers)}

    items = []
    for row in rows[header_idx + 1:]:
        if _is_section_divider(row):
            continue
        if not _is_data_row(row, col):
            # Skip non-data rows (blank lines, trailing summary/footer text, etc.)
            continue
        items.append(_parse_row(row, col))

    return ROMWorksheetData(line_items=tuple(items))


def _find_header_row(rows) -> int | None:
    needed = set(REQUIRED_HEADERS)
    for i, row in enumerate(rows):
        cells = {_norm(c) for c in row}
        if needed.issubset(cells):
            return i
    return None


def _norm(cell) -> str:
    if cell is None:
        return ""
    return str(cell).strip()


def _is_section_divider(row) -> bool:
    """A divider row has a single label cell in column A starting with 'Section '."""
    if not row or row[0] is None:
        return False
    first = _norm(row[0])
    rest_empty = all(_norm(c) == "" for c in row[1:])
    return first.lower().startswith("section ") and rest_empty


def _is_data_row(row, col: dict) -> bool:
    """A data row has a non-empty `#` and `Item Name`."""
    code = _norm(row[col["#"]]) if col["#"] < len(row) else ""
    name = _norm(row[col["Item Name"]]) if col["Item Name"] < len(row) else ""
    return bool(code) and bool(name)


def _int_or_zero(v) -> int:
    if v is None or v == "":
        return 0
    return int(v)


def _parse_row(row, col: dict) -> ROMLineItem:
    def cell(name: str) -> str:
        i = col.get(name)
        if i is None or i >= len(row):
            return ""
        return _norm(row[i])
    def cell_int(name: str) -> int:
        i = col.get(name)
        if i is None or i >= len(row):
            return 0
        return _int_or_zero(row[i])

    return ROMLineItem(
        code=cell("#"),
        section=cell("Section"),
        name=cell("Item Name"),
        description=cell("Description / Build Notes"),
        alternate_group=cell("Alternate Group"),
        rental_low=cell_int("Rental Low"),
        rental_high=cell_int("Rental High"),
        purchase_ot_low=cell_int("Purchase OT Low"),
        purchase_ot_high=cell_int("Purchase OT High"),
        purchase_svc_low=cell_int("Purchase Svc Low"),
        purchase_svc_high=cell_int("Purchase Svc High"),
        customer_facing=cell("Customer-Facing Description"),
        materials=cell("Materials / Build"),
        notes=cell("Notes / Assumptions"),
        rendering_ref=cell("Rendering Reference"),
    )
