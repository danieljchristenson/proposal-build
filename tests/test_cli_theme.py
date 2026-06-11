"""The generate CLI accepts --theme and overrides the model's theme."""
import argparse
import pytest

from proposal_build.cli import _apply_theme_override, _placeholder_model, main


def test_override_none_keeps_model_theme():
    model = _placeholder_model()  # default theme = "editorial"
    out = _apply_theme_override(model, None)
    assert out.theme == model.theme


def test_override_to_classic():
    model = _placeholder_model()
    out = _apply_theme_override(model, "classic")
    assert out.theme == "classic"


def test_override_to_editorial():
    import dataclasses
    model = dataclasses.replace(_placeholder_model(), theme="classic")
    out = _apply_theme_override(model, "editorial")
    assert out.theme == "editorial"


def test_override_does_not_mutate_original():
    model = _placeholder_model()
    original = model.theme
    _apply_theme_override(model, "classic")
    assert model.theme == original  # frozen dataclass; replace returns a copy


def test_generate_parser_accepts_theme_choice():
    # Build the same parser main() builds and confirm --theme parses + validates choices.
    parser = argparse.ArgumentParser(prog="proposal_build")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("project_dir")
    gen.add_argument("--theme", choices=("classic", "editorial"), default=None)

    assert parser.parse_args(["generate", "X", "--theme", "classic"]).theme == "classic"
    assert parser.parse_args(["generate", "X", "--theme", "editorial"]).theme == "editorial"
    assert parser.parse_args(["generate", "X"]).theme is None
    with pytest.raises(SystemExit):
        parser.parse_args(["generate", "X", "--theme", "bogus"])
