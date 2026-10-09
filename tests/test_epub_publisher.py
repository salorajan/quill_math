"""Unit tests for accessible EPUB 3.4 publisher and validator."""

from pathlib import Path

from quill_math.epub.publisher import create_accessible_epub
from quill_math.epub.reader import load_epub_book
from quill_math.epub.validator import validate_epub


def test_create_and_validate_accessible_epub(tmp_path: Path) -> None:
    epub_file = tmp_path / "calculus.epub"
    chapters = [
        {
            "title": "Limits and Derivatives",
            "content_html": (
                "<p>Definition of derivative: "
                '<math xmlns="http://www.w3.org/1998/Math/MathML">'
                "<mrow><msup><mi>f</mi><mo>′</mo></msup><mo stretchy=\"false\">(</mo><mi>x</mi><mo stretchy=\"false\">)</mo>"
                "<mo>=</mo><munder><mo movablelimits=\"true\">lim</mo><mrow><mi>h</mi><mo>→</mo><mn>0</mn></mrow></munder>"
                "<mfrac><mrow><mi>f</mi><mo stretchy=\"false\">(</mo><mi>x</mi><mo>+</mo><mi>h</mi><mo stretchy=\"false\">)</mo>"
                "<mo>−</mo><mi>f</mi><mo stretchy=\"false\">(</mo><mi>x</mi><mo stretchy=\"false\">)</mo></mrow><mi>h</mi></mfrac></mrow>"
                "</math></p>"
            ),
        }
    ]

    out = create_accessible_epub(
        epub_file,
        title="Accessible Calculus",
        author="Prof. Euler",
        language="en",
        chapters=chapters,
    )
    assert out.is_file()

    # Validate accessibility
    report = validate_epub(out)
    assert report.is_valid is True
    assert len(report.errors) == 0

    # Load and verify reading
    book = load_epub_book(out)
    assert book.title == "Accessible Calculus"
    assert len(book.chapters) == 1
    assert "Limits and Derivatives" in book.chapters[0].title


def test_create_epub_from_markdown_clean_math(tmp_path: Path) -> None:
    from quill_math.epub.publisher import create_epub_from_markdown
    md_file = tmp_path / "test.md"
    md_file.write_text(
        "# Math Benchmark\n\n"
        "Here is the quadratic formula:\n\n"
        "$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$\n\n"
        "Done.",
        encoding="utf-8",
    )
    epub_file = tmp_path / "test.epub"
    out = create_epub_from_markdown(md_file, epub_file)
    assert out.is_file()

    report = validate_epub(out)
    assert report.is_valid is True

    book = load_epub_book(out)
    assert book.title == "Math Benchmark"
    text = book.chapters[0].body
    assert text.count("Math Benchmark") == 1
    assert "x equals fraction with numerator minus b plus or minus" in text
    assert "annotation" not in text
    assert "\\frac" not in text
