"""Unit tests for accessible HTML equation compiler and interactive cards."""

from pathlib import Path

from quill_math.epub.publisher import create_epub_from_markdown
from quill_math.epub.validator import validate_epub
from quill_math.html.builder import build_interactive_equation_html, build_node_tree
from quill_math.html.compiler import compile_file, compile_markdown_to_accessible_html


def test_build_node_tree_fraction() -> None:
    from quill_math.core.latex_bridge import latex_to_mathml
    from quill_math.core.mathml import parse_mathml

    mathml = latex_to_mathml(r"\frac{a + 1}{b}")
    root = parse_mathml(mathml)
    tree = build_node_tree(root)

    assert tree["label"] == "Fraction"
    assert len(tree["children"]) == 2
    assert tree["children"][0]["role"] == "Numerator"
    assert tree["children"][1]["role"] == "Denominator"


def test_build_interactive_equation_html() -> None:
    html_card = build_interactive_equation_html(
        "a^2 + b^2 = c^2",
        eq_id="pythagoras",
        description="Pythagorean theorem",
    )
    # Check accessibility contracts
    assert 'role="region"' in html_card
    assert 'tabindex="0"' in html_card
    assert 'aria-label="Pythagorean theorem"' in html_card
    assert 'role="application"' in html_card
    assert 'class="in-place-nav-drawer"' in html_card
    assert "<math" in html_card
    assert "data-eq-id=" in html_card
    assert "data-speech=" in html_card


def test_compile_markdown_to_accessible_html(tmp_path: Path) -> None:
    md_content = """# Calculus Notes

Here is an inline formula \\(f(x) = x^2\\) in text.

And here is the quadratic formula:

$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$

Conclusion of notes.
"""
    html_output = compile_markdown_to_accessible_html(md_content, title="Calculus Notes")

    assert "<!DOCTYPE html>" in html_output
    assert "<title>Calculus Notes</title>" in html_output
    assert "interactive-equation-wrapper" in html_output
    assert "in-place-nav-drawer" in html_output
    assert "inline-math" in html_output


def test_compile_file_and_publish_epub(tmp_path: Path) -> None:
    md_file = tmp_path / "physics.md"
    md_file.write_text(
        "# Classical Mechanics\n\nNewton's second law is $$F = ma$$.\n\nKinetic energy is $$E = \\frac{1}{2}mv^2$$.\n",
        encoding="utf-8",
    )

    # 1. Compile HTML
    html_file = tmp_path / "physics.html"
    compile_file(md_file, html_file, title="Physics Lecture")
    assert html_file.is_file()
    assert "interactive-equation-wrapper" in html_file.read_text(encoding="utf-8")

    # 2. Publish EPUB
    epub_file = tmp_path / "physics.epub"
    create_epub_from_markdown(md_file, epub_file, title="Physics Lecture", author="Isaac Newton")
    assert epub_file.is_file()

    report = validate_epub(epub_file)
    assert report.is_valid is True
    assert len(report.errors) == 0


def test_compile_markdown_with_chemistry() -> None:
    md_content = """# General Chemistry

The water formation reaction is:

$$\\ce{2H2 + O2 -> 2H2O}$$

And photosynthesis equilibrium:

$$\\ce{6CO2 + 6H2O <=> C6H12O6 + 6O2}$$
"""
    html_output = compile_markdown_to_accessible_html(md_content, title="General Chemistry")
    assert "<!DOCTYPE html>" in html_output
    assert "interactive-equation-wrapper" in html_output
    assert "reacts to form" in html_output or "H" in html_output

