"""Finding and InspectionReport dataclasses for the inspector."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional


Severity = Literal["blocker", "warning", "info", "error"]
Category = Literal["folder", "brief", "worksheet", "renderings", "validator"]


@dataclass(frozen=True)
class Finding:
    severity: Severity
    category: Category
    issue: str
    detail: str
    fix: Optional[str] = None
    field: Optional[str] = None
    zone: Optional[str] = None


@dataclass(frozen=True)
class InspectionReport:
    project_path: Path
    ready_to_generate: bool
    findings: tuple[Finding, ...]
    summary: str
