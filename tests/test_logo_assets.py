from pathlib import Path
from PIL import Image
from proposal_build.renderer.pdf import _enrich_ctx

BRANDING = Path("skill_assets/Branding")

def test_white_logo_exists_and_has_alpha():
    p = BRANDING / "ST NICKS LOGO WHITE.png"
    assert p.is_file()
    im = Image.open(p).convert("RGBA")
    px = [im.getpixel((x, y)) for x in range(0, im.width, max(1, im.width//20))
          for y in range(0, im.height, max(1, im.height//20))]
    opaque = [q for q in px if q[3] > 200]
    assert opaque, "logo has no opaque pixels"
    assert all(c > 200 for q in opaque for c in q[:3]), "opaque pixels are not white"

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
