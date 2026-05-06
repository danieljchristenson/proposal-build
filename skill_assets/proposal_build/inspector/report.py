"""Finding and InspectionReport dataclasses for the inspector."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


Severity = Literal["blocker", "warning", "info", "error"]
Category = Literal["folder", "brief", "worksheet", "renderings", "validator"]


@dataclass(frozen=True)
class Finding:
    severity: Severity
    category: Category
    issue: str
    detail: str
    fix: str | None = None
    field: str | None = None
    zone: str | None = None


@dataclass(frozen=True)
class InspectionReport:
    project_path: Path
    ready_to_generate: bool
    findings: tuple[Finding, ...]
    summary: str
