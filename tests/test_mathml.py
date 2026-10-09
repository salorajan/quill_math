"""Unit tests for MathML parsing, safety, and annotation embedding."""

import pytest
from quill_math.core.mathml import (
    Equation,
    MathMLError,
    extract_tex_annotation,
    is_valid_mathml,
    parse_mathml,
    wrap_with_tex_annotation,
)

_SIMPLE = '<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline"><mi>x</mi></math>'
_MULTI = (
    '<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">'
    "<mi>x</mi><mo>+</mo><mn>1</mn></math>"
)


def test_parse_mathml_valid() -> None:
    root = parse_mathml(_SIMPLE)
    assert root.tag.endswith("math")


def test_parse_mathml_rejects_non_math() -> None:
    with pytest.raises(MathMLError):
        parse_mathml("<mrow><mi>x</mi></mrow>")


def test_parse_mathml_rejects_malformed() -> None:
    with pytest.raises(MathMLError):
        parse_mathml("<math><mi>x</mi>")


def test_is_valid_mathml() -> None:
    assert is_valid_mathml(_SIMPLE) is True
    assert is_valid_mathml("not xml") is False


def test_wrap_and_extract_roundtrip_single() -> None:
    wrapped = wrap_with_tex_annotation(_SIMPLE, "x")
    assert extract_tex_annotation(wrapped) == "x"
    assert is_valid_mathml(wrapped)


def test_wrap_and_extract_roundtrip_multiple() -> None:
    wrapped = wrap_with_tex_annotation(_MULTI, "x+1")
    assert extract_tex_annotation(wrapped) == "x+1"
    assert is_valid_mathml(wrapped)


def test_extract_tex_annotation_none_when_absent() -> None:
    assert extract_tex_annotation(_SIMPLE) is None


def test_wrap_preserves_display() -> None:
    wrapped = wrap_with_tex_annotation(_SIMPLE, "x")
    root = parse_mathml(wrapped)
    assert root.get("display") == "inline"


def test_equation_dataclass() -> None:
    eq = Equation(mathml=_SIMPLE, latex="x")
    assert eq.mathml == _SIMPLE
    assert eq.latex == "x"


def test_clean_mathml_for_epub() -> None:
    from quill_math.core.mathml import clean_mathml_for_epub
    wrapped = wrap_with_tex_annotation(_MULTI, "x+1")
    cleaned = clean_mathml_for_epub(wrapped, display="block")
    assert "annotation" not in cleaned
    assert "semantics" not in cleaned
    assert "display=\"block\"" in cleaned
    assert "<mi>x</mi><mo>+</mo><mn>1</mn>" in cleaned
