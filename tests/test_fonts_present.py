"""Asserts the 5 required font files exist in skill_assets/fonts/.

Per parent spec §3 / Plan 2 design §5, fonts MUST be embedded in the
skill bundle and never loaded from the system. This test catches
accidental deletion or wrong filename.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FONTS = REPO_ROOT / "skill_assets" / "fonts"

REQUIRED_FONTS = [
    "Roboto-Bold.ttf",
    "Roboto-Regular.ttf",
    "Poppins-Light.ttf",
    "Poppins-Regular.ttf",
    "Poppins-Medium.ttf",
]


def test_required_fonts_present():
    missing = [f for f in REQUIRED_FONTS if not (FONTS / f).is_file()]
    assert not missing, f"Missing fonts: {missing}"


def test_fonts_are_nonempty():
    for f in REQUIRED_FONTS:
        path = FONTS / f
        assert path.stat().st_size > 1000, f"{f} suspiciously small ({path.stat().st_size} bytes)"
