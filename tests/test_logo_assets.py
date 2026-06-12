from pathlib import Path
from PIL import Image
from proposal_build.renderer.pdf import _enrich_ctx

BRANDING = Path("skill_assets/Branding")

def test_white_logo_exists_and_is_two_tone():
    """Dark-page logo: ivory wordmark + the colored Santa kept, transparent bg."""
    p = BRANDING / "ST NICKS LOGO WHITE.png"
    assert p.is_file()
    im = Image.open(p).convert("RGBA")
    px = list(im.getdata())
    opaque = [q for q in px if q[3] > 200]
    assert opaque, "logo has no opaque pixels"
    # The wordmark must include near-ivory pixels (so text reads on dark)...
    ivory = [q for q in opaque if all(c > 200 for c in q[:3])]
    assert ivory, "logo has no ivory wordmark pixels"
    # ...and the Santa must keep some color (not flattened to white).
    colored = [q for q in opaque if (max(q[:3]) - min(q[:3])) > 55]
    assert colored, "logo has no colored Santa pixels (flattened to white?)"


def test_white_logo_is_a_knockout_not_a_solid_box():
    """Regression guard: the white logo must be a transparent knockout of the
    wordmark, not a solid filled rectangle (the bug from recoloring an opaque
    white-background source). The background should be mostly transparent."""
    im = Image.open(BRANDING / "ST NICKS LOGO WHITE.png").convert("RGBA")
    px = list(im.getdata())
    transparent = sum(1 for q in px if q[3] < 16)
    opaque = sum(1 for q in px if q[3] > 200)
    frac_transparent = transparent / len(px)
    assert frac_transparent > 0.4, (
        f"white logo is {frac_transparent:.0%} transparent — looks like a solid box, "
        "not a knockout of the wordmark")
    assert opaque > 0, "white logo has no opaque wordmark pixels"

def test_enrich_white_logo_on_editorial_dark():
    out = _enrich_ctx({"logo_path": "/x/black.png", "logo_path_dark": "/x/white.png"},
                      theme="editorial", layout="cover")
    assert out["header_logo"] == "/x/white.png"

def test_enrich_black_logo_on_editorial_light_page():
    out = _enrich_ctx({"logo_path": "/x/black.png", "logo_path_dark": "/x/white.png"},
                      theme="editorial", layout="about")  # about is light
    assert out["header_logo"] == "/x/black.png"

def test_enrich_classic_always_black_logo():
    # classic must be byte-stable: header_logo == logo_path on every layout
    for layout in ("cover", "about", "exec_summary"):
        out = _enrich_ctx({"logo_path": "/x/black.png", "logo_path_dark": "/x/white.png"},
                          theme="classic", layout=layout)
        assert out["header_logo"] == "/x/black.png"
