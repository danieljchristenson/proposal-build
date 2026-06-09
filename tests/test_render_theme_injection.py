from proposal_build.renderer import pdf as pdfmod
from tests.fixtures import riverside as rv


def test_enrich_adds_theme_surface_and_layout_name():
    ctx = {"hello": "world"}
    out = pdfmod._enrich_ctx(ctx, theme="editorial", layout="cover")
    assert out["theme"] == "editorial"
    assert out["layout_name"] == "cover"
    assert out["body_surface"] == "dark"          # cover is dark under editorial
    assert out["hello"] == "world"                # original keys preserved
    assert ctx == {"hello": "world"}              # original dict not mutated


def test_enrich_classic_about_is_light():
    out = pdfmod._enrich_ctx({}, theme="classic", layout="about")
    assert out["body_surface"] == "light"
    assert out["theme"] == "classic"


def test_render_proposal_pdf_defaults_to_classic(tmp_path):
    # Use the real riverside cover ctx so WeasyPrint can render without errors.
    slides = [("cover", rv.cover_ctx)]
    out = tmp_path / "smoke.pdf"
    # Should not raise; theme defaults to classic.
    pdfmod.render_proposal_pdf(slides, out)
    assert out.exists()
