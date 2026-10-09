"""Unit tests for equation tree navigation and structural inspection."""

import pytest
from quill_math.core.navigator import (
    EquationNavigator,
    MathNavigatorError,
    node_kind_label,
    parse_equation,
    read_aloud,
)


def test_parse_equation_latex() -> None:
    root = parse_equation("a^2 + b^2 = c^2")
    assert root.tag.endswith("math")


def test_parse_equation_mathml() -> None:
    mathml = '<math xmlns="http://www.w3.org/1998/Math/MathML"><mi>x</mi></math>'
    root = parse_equation(mathml)
    assert root.tag.endswith("math")


def test_parse_equation_invalid() -> None:
    with pytest.raises(MathNavigatorError):
        parse_equation("")


def test_read_aloud_pythagorean() -> None:
    root = parse_equation("a^2 + b^2 = c^2")
    assert read_aloud(root) == "a squared plus b squared equals c squared"


def test_read_aloud_quadratic() -> None:
    root = parse_equation(r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}")
    reading = read_aloud(root)
    assert "fraction" in reading
    assert "square root" in reading
    assert "plus or minus" in reading


def test_read_aloud_powers() -> None:
    assert read_aloud(parse_equation("x^3")) == "x cubed"
    assert "power" in read_aloud(parse_equation("x^4"))


def test_navigator_tree_walking() -> None:
    root = parse_equation(r"x = \frac{a + 1}{b}")
    nav = EquationNavigator(root)
    assert nav.at_root()
    assert "fraction" in nav.reading()

    # Find the fraction child
    options = nav.child_options()
    frac_idx = next(i for i, opt in enumerate(options) if "Fraction" in opt.label)
    nav.descend(frac_idx)
    assert not nav.at_root()
    assert nav.label() == "Fraction"

    # Check child roles
    children = nav.child_options()
    assert [c.role for c in children] == ["Numerator", "Denominator"]

    # Descend into numerator
    nav.descend(0)
    assert not nav.at_root()
    assert "a plus 1" in nav.reading()

    # Ascend back to fraction
    nav.ascend()
    assert nav.label() == "Fraction"

    # Reset to root
    nav.reset()
    assert nav.at_root()


def test_node_kind_label() -> None:
    import xml.etree.ElementTree as ET

    el = ET.fromstring("<mo>+</mo>")
    assert node_kind_label(el) == "plus"
    assert node_kind_label(el, language="es") == "más"


def test_read_aloud_spanish() -> None:
    root = parse_equation("a^2 + b^2 = c^2")
    assert read_aloud(root, language="es") == "a al cuadrado más b al cuadrado igual a c al cuadrado"

    quad = parse_equation(r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}")
    quad_read = read_aloud(quad, language="es")
    assert "fracción con numerador" in quad_read
    assert "raíz cuadrada de" in quad_read
    assert "más o menos" in quad_read

    cube = parse_equation("x^3")
    assert read_aloud(cube, language="es") == "x al cubo"


def test_navigator_tree_walking_spanish() -> None:
    root = parse_equation(r"x = \frac{a + 1}{b}")
    nav = EquationNavigator(root, language="es")
    assert nav.at_root()
    assert "fracción" in nav.reading()

    options = nav.child_options()
    frac_idx = next(i for i, opt in enumerate(options) if "Fracción" in opt.label)
    nav.descend(frac_idx)
    assert nav.label() == "Fracción"

    children = nav.child_options()
    assert [c.role for c in children] == ["Numerador", "Denominador"]

    nav.descend(0)
    assert "a más 1" in nav.reading()

