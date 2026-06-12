from pathlib import Path
from PIL import Image
from proposal_build.renderer.pdf import _enrich_ctx

BRANDING = Path("skill_assets/Branding")


def test_on_dark_logo_exists_and_is_hires_color():
    """Dark pages use the full-color logo (shown on a CSS light chip). It must be
    the hi-res artwork (not the old low-res file) and keep its color."""
    p = BRANDING / "ST NICKS LOGO ON-DARK.png"
    assert p.is_file()
    im = Image.open(p).convert("RGBA")
    assert im.width >= 800, f"on-dark logo is low-res ({im.size}) — use the hi-res file"
    px = list(im.getdata())
    colored = sum(1 for q in px if q[3] > 200 and (max(q[:3]) - min(q[:3])) > 55)
    assert colored > 0, "on-dark logo has no colored pixels (Santa missing?)"


def test_enrich_dark_logo_on_editorial_dark():
    out = _enrich_ctx({"logo_path": "/x/black.png", "logo_path_dark": "/x/dark.png"},
                      theme="editorial", layout="cover")
    assert out["header_logo"] == "/x/dark.png"


def test_enrich_black_logo_on_editorial_light_page():
    out = _enrich_ctx({"logo_path": "/x/black.png", "logo_path_dark": "/x/dark.png"},
                      theme="editorial", layout="about")  # about is light
    assert out["header_logo"] == "/x/black.png"


def test_enrich_classic_always_black_logo():
    # classic must be byte-stable: header_logo == logo_path on every layout
    for layout in ("cover", "about", "exec_summary"):
        out = _enrich_ctx({"logo_path": "/x/black.png", "logo_path_dark": "/x/dark.png"},
                          theme="classic", layout=layout)
        assert out["header_logo"] == "/x/black.png"
