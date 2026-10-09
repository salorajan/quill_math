"""Unit tests for LaTeX <-> MathML bridge."""

import pytest
from quill_math.core.latex_bridge import (
    LatexConversionError,
    latex_to_mathml,
    mathml_to_latex,
)
from quill_math.core.mathml import is_valid_mathml


def test_latex_to_mathml_valid() -> None:
    mathml = latex_to_mathml(r"x^2 + 1")
    assert is_valid_mathml(mathml)
    assert "<msup>" in mathml
    assert "<mn>2</mn>" in mathml


def test_latex_to_mathml_roundtrip() -> None:
    source = r"\frac{1}{y}"
    mathml = latex_to_mathml(source)
    assert mathml_to_latex(mathml) == source


def test_latex_to_mathml_greek() -> None:
    mathml = latex_to_mathml(r"\alpha + \beta")
    assert "α" in mathml
    assert "β" in mathml


def test_latex_to_mathml_display_block() -> None:
    mathml = latex_to_mathml(r"x = y", display="block")
    assert 'display="block"' in mathml


def test_latex_to_mathml_error_on_invalid() -> None:
    with pytest.raises(LatexConversionError):
        latex_to_mathml("")
