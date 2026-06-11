"""Typo-guard: classic semantic token values must equal the legacy hex.
Catches wrong-token swaps introduced during the tokenization pass."""
import re
from pathlib import Path

CSS = Path("skill_assets/layouts/brand.css").read_text()


def _block(selector):
    # return the LAST occurrence of `selector { ... }` body
    blocks = re.findall(re.escape(selector) + r"\s*\{([^}]*)\}", CSS)
    return blocks[-1] if blocks else ""


def test_classic_dark_tokens_match_legacy():
    b = _block("body.page-dark")
    for tok, val in [("--surface-card", "#2a2a2a"), ("--surface-card-2", "#0d0d0d"),
                     ("--surface-hero", "#2a2a2a"), ("--surface-strip", "#1C1C1C"),
                     ("--ink", "#ECEFF1"), ("--accent", "#B31315")]:
        assert f"{tok}:{val}" in b.replace(" ", ""), f"{tok} drifted on classic dark"


def test_classic_light_tokens_match_legacy():
    b = _block("body.page-light")
    for tok, val in [("--ink", "#1C1C1C"), ("--ink-muted", "#555555"),
                     ("--surface-card", "#F2F2F2"), ("--rule", "#E0E0E0"),
                     ("--accent", "#B31315")]:
        assert f"{tok}:{val}" in b.replace(" ", ""), f"{tok} drifted on classic light"
