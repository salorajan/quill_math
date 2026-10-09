"""Unit tests for EPUB reader and math placeholder decoding."""

import zipfile
from pathlib import Path

from quill_math.epub.reader import load_epub_book, render_epub_book


def test_load_epub_basic(tmp_path: Path) -> None:
    target = tmp_path / "simple.epub"
    chapter = "<html><body><h1>Introduction</h1><p>Hello STEM world.</p></body></html>"
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("chapters/ch1.xhtml", chapter)

    book = load_epub_book(target)
    assert len(book.chapters) == 1
    assert "Hello STEM world." in book.chapters[0].text
    assert book.chapters[0].headings[0].title == "Introduction"


def test_load_epub_with_mathml(tmp_path: Path) -> None:
    target = tmp_path / "math.epub"
    chapter = (
        '<html><body><p>Quadratic formula: <math xmlns="http://www.w3.org/1998/Math/MathML">'
        "<mi>x</mi><mo>=</mo><mfrac><mrow><mo>-</mo><mi>b</mi></mrow><mrow><mn>2</mn><mi>a</mi></mrow></mfrac>"
        "</math> in body.</p></body></html>"
    )
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("chapters/ch1.xhtml", chapter)

    book = load_epub_book(target)
    text = book.chapters[0].text
    assert "[Math Equation:" in text
    assert "fraction" in text or "over" in text
    assert "in body." in text


def test_load_epub_with_xml_entities(tmp_path: Path) -> None:
    target = tmp_path / "entities.epub"
    chapter = (
        '<html><body><p>Inequality: <math xmlns="http://www.w3.org/1998/Math/MathML">'
        "<mi>x</mi><mo>&lt;</mo><mi>y</mi></math>.</p></body></html>"
    )
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("chapters/ch1.xhtml", chapter)

    book = load_epub_book(target)
    assert "[Math Equation:" in book.chapters[0].text
    assert "less than" in book.chapters[0].text or "<" in book.chapters[0].text


def test_render_epub_markdown(tmp_path: Path) -> None:
    target = tmp_path / "book.epub"
    chapter = "<html><body><h1>Title</h1><p>Content</p></body></html>"
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("chapters/ch1.xhtml", chapter)

    book = load_epub_book(target)
    rendered = render_epub_book(book)
    assert "# EPUB:" in rendered
    assert "## 1." in rendered
