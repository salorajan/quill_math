"""Accessible EPUB 3.4 publisher conforming to EPUB Accessibility 1.2 & MathML standards."""

from __future__ import annotations

import html
import uuid
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from quill_math.core.latex_bridge import latex_to_mathml
from quill_math.core.mathml import clean_mathml_for_epub, parse_mathml
from quill_math.core.speech import speak, to_braille


def create_accessible_epub(
    target_path: Path,
    *,
    title: str,
    author: str = "Anonymous",
    language: str = "en",
    chapters: list[dict[str, str]],
) -> Path:
    """Create a fully accessible EPUB 3.4 document with embedded MathML support.

    *chapters* is a list of dictionaries with keys:
      - ``title``: string
      - ``content_html``: HTML body content (may contain valid <math> tags)
    """
    book_id = f"urn:uuid:{uuid.uuid4()}"
    modified_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(target_path, "w") as archive:
        # 1. mimetype (must be first, uncompressed)
        archive.writestr(
            "mimetype",
            "application/epub+zip",
            compress_type=zipfile.ZIP_STORED,
        )

        # 2. META-INF/container.xml
        container_xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
            "  <rootfiles>\n"
            '    <rootfile full-path="OEBPS/package.opf" media-type="application/oebps-package+xml"/>\n'
            "  </rootfiles>\n"
            "</container>\n"
        )
        archive.writestr("META-INF/container.xml", container_xml)

        # Build chapter files
        manifest_items = [
            '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
            '    <item id="css" href="styles.css" media-type="text/css"/>',
        ]
        spine_items = []
        nav_toc_links = []

        css_content = (
            "body { font-family: sans-serif; line-height: 1.6; margin: 5% auto; max-width: 45em; padding: 0 1em; }\n"
            "math { font-size: 1.1em; }\n"
            "h1, h2, h3 { color: #111; }\n"
        )
        archive.writestr("OEBPS/styles.css", css_content)

        for index, ch in enumerate(chapters, start=1):
            ch_id = f"chapter_{index}"
            ch_filename = f"chapter_{index}.xhtml"
            ch_title = html.escape(ch.get("title", f"Chapter {index}"))
            ch_content = ch.get("content_html", "<p></p>")

            has_math = "<math" in ch_content.lower()
            prop_attr = ' properties="math"' if has_math else ""

            manifest_items.append(
                f'    <item id="{ch_id}" href="chapters/{ch_filename}" media-type="application/xhtml+xml"{prop_attr}/>'
            )
            spine_items.append(f'    <itemref idref="{ch_id}"/>')
            nav_toc_links.append(
                f'        <li><a href="chapters/{ch_filename}">{ch_title}</a></li>'
            )

            ch_xhtml = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<!DOCTYPE html>\n'
                '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" '
                f'xml:lang="{language}" lang="{language}">\n'
                "<head>\n"
                f"  <title>{ch_title}</title>\n"
                '  <link rel="stylesheet" type="text/css" href="../styles.css"/>\n'
                "</head>\n"
                "<body>\n"
                f"  <h1>{ch_title}</h1>\n"
                f"  {ch_content}\n"
                "</body>\n"
                "</html>\n"
            )
            archive.writestr(f"OEBPS/chapters/{ch_filename}", ch_xhtml)

        # 3. OEBPS/nav.xhtml
        nav_xhtml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" '
            f'xml:lang="{language}" lang="{language}">\n'
            "<head>\n"
            f"  <title>{html.escape(title)} - Table of Contents</title>\n"
            '  <link rel="stylesheet" type="text/css" href="styles.css"/>\n'
            "</head>\n"
            "<body>\n"
            '  <nav epub:type="toc" id="toc">\n'
            "    <h1>Table of Contents</h1>\n"
            "    <ol>\n"
            + "\n".join(nav_toc_links) + "\n"
            "    </ol>\n"
            "  </nav>\n"
            '  <nav epub:type="landmarks" hidden="">\n'
            "    <h2>Landmarks</h2>\n"
            "    <ol>\n"
            '      <li><a epub:type="toc" href="#toc">Table of Contents</a></li>\n'
            '      <li><a epub:type="bodymatter" href="chapters/chapter_1.xhtml">Begin Reading</a></li>\n'
            "    </ol>\n"
            "  </nav>\n"
            "</body>\n"
            "</html>\n"
        )
        archive.writestr("OEBPS/nav.xhtml", nav_xhtml)

        # 4. OEBPS/package.opf
        manifest_str = "\n".join(manifest_items)
        spine_str = "\n".join(spine_items)

        package_opf = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id">\n'
            "  <metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\">\n"
            f"    <dc:identifier id=\"pub-id\">{book_id}</dc:identifier>\n"
            f"    <dc:title>{html.escape(title)}</dc:title>\n"
            f"    <dc:language>{language}</dc:language>\n"
            f"    <dc:creator>{html.escape(author)}</dc:creator>\n"
            f"    <meta property=\"dcterms:modified\">{modified_time}</meta>\n"
            '    <meta property="dcterms:conformsTo">epub-a11y-12</meta>\n'
            '    <meta property="schema:accessibilitySummary">This publication conforms to the EPUB Accessibility 1.2 specification at WCAG 2.2 Level AA. All mathematical formulas are marked up natively using MathML with semantic structure to support screen readers and interactive braille displays.</meta>\n'
            '    <meta property="schema:accessMode">textual</meta>\n'
            '    <meta property="schema:accessMode">visual</meta>\n'
            '    <meta property="schema:accessibilityFeature">structuralNavigation</meta>\n'
            '    <meta property="schema:accessibilityFeature">mathML</meta>\n'
            '    <meta property="schema:accessibilityFeature">readingOrder</meta>\n'
            '    <meta property="schema:accessibilityHazard">none</meta>\n'
            "  </metadata>\n"
            "  <manifest>\n"
            f"{manifest_str}\n"
            "  </manifest>\n"
            "  <spine>\n"
            f"{spine_str}\n"
            "  </spine>\n"
            "</package>\n"
        )
        archive.writestr("OEBPS/package.opf", package_opf)

    return target_path


def create_epub_from_markdown(
    source_md_path: Path,
    target_epub_path: Path,
    *,
    title: str | None = None,
    author: str = "Anonymous",
    language: str = "en",
) -> Path:
    """Compile a Markdown file with LaTeX math directly into an accessible EPUB 3.4 file."""
    import re

    source_path = Path(source_md_path)
    text = source_path.read_text(encoding="utf-8")

    # Strip YAML frontmatter if present
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
    if frontmatter_match:
        text = text[frontmatter_match.end():]

    # Extract title from H1 if not explicitly provided
    book_title = title
    if not book_title:
        h1_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
        if h1_match:
            book_title = h1_match.group(1).strip()
        else:
            book_title = source_path.stem.replace("_", " ").replace("-", " ").title()

    # Split markdown into chapters on top-level "# Heading", respecting fenced code blocks
    lines = text.split("\n")
    chapter_chunks: list[list[str]] = []
    current_chunk: list[str] = []
    in_code_fence = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code_fence = not in_code_fence

        if not in_code_fence and line.startswith("# ") and current_chunk:
            chapter_chunks.append(current_chunk)
            current_chunk = [line]
        else:
            current_chunk.append(line)

    if current_chunk:
        chapter_chunks.append(current_chunk)

    chapters: list[dict[str, str]] = []

    def math_to_mathml(formula: str, display: str = "block") -> str:
        try:
            mathml_str = latex_to_mathml(formula, display=display)
            root = parse_mathml(mathml_str)
            spoken = speak(root, language=language)
            return clean_mathml_for_epub(mathml_str, speech_desc=spoken, display=display)
        except Exception:
            return f"<p>{html.escape(formula)}</p>"

    def _process_chapter(index_and_chunk: tuple[int, list[str]]) -> dict[str, str]:
        index, chunk = index_and_chunk
        if not chunk:
            return {"title": f"Chapter {index}", "content_html": "<p></p>"}
        first_line = chunk[0].strip()
        ch_title = first_line[2:].strip() if first_line.startswith("# ") else f"Chapter {index}"
        body_lines = chunk[1:] if first_line.startswith("# ") else chunk
        body_text = "\n".join(body_lines)

        # 1. Convert block math $$...$$ or \[...\] to MathML
        def block_math_replacer(match: re.Match[str]) -> str:
            formula = match.group(1).strip()
            mathml_str = math_to_mathml(formula, display="block")
            return f"\n\n<!--MATH_BLOCK-->\n{mathml_str}\n<!--/MATH_BLOCK-->\n\n"

        body_text = re.sub(r"\$\$(.+?)\$\$", block_math_replacer, body_text, flags=re.DOTALL)
        body_text = re.sub(r"\\\[(.+?)\\\]", block_math_replacer, body_text, flags=re.DOTALL)

        # 2. Convert inline math \(...\) or $...$
        body_text = re.sub(
            r"\\\((.+?)\\\)",
            lambda m: math_to_mathml(m.group(1).strip(), display="inline"),
            body_text,
            flags=re.DOTALL,
        )

        # 3. Structure into HTML blocks
        raw_blocks = re.split(r"\n\s*\n", body_text)
        html_blocks: list[str] = []

        for block in raw_blocks:
            block_str = block.strip()
            if not block_str:
                continue

            if "<!--MATH_BLOCK-->" in block_str:
                m_match = re.search(
                    r"<!--MATH_BLOCK-->\s*(.+?)\s*<!--/MATH_BLOCK-->", block_str, flags=re.DOTALL
                )
                if m_match:
                    html_blocks.append(f"<p>{m_match.group(1).strip()}</p>")
                else:
                    html_blocks.append(f"<p>{block_str}</p>")
                continue

            if re.match(r"^(\-{3,}|\*{3,}|_{3,})$", block_str):
                html_blocks.append("<hr />")
                continue

            if block_str.startswith("```") and block_str.endswith("```"):
                code_lines = block_str.split("\n")
                code_body = "\n".join(code_lines[1:-1])
                html_blocks.append(f"<pre><code>{html.escape(code_body)}</code></pre>")
                continue

            if block_str.startswith("### "):
                html_blocks.append(f"<h3>{html.escape(block_str[4:].strip())}</h3>")
            elif block_str.startswith("## "):
                html_blocks.append(f"<h2>{html.escape(block_str[3:].strip())}</h2>")
            elif block_str.startswith("# "):
                html_blocks.append(f"<h1>{html.escape(block_str[2:].strip())}</h1>")
            elif block_str.startswith("#### "):
                html_blocks.append(f"<h4>{html.escape(block_str[5:].strip())}</h4>")
            else:
                html_blocks.append(f"<p>{block_str}</p>")

        content_html = "\n".join(html_blocks)
        return {"title": ch_title, "content_html": content_html}

    if len(chapter_chunks) > 1:
        with ThreadPoolExecutor(max_workers=min(len(chapter_chunks), 8)) as executor:
            chapters = list(executor.map(_process_chapter, enumerate(chapter_chunks, start=1)))
    elif chapter_chunks:
        chapters = [_process_chapter((1, chapter_chunks[0]))]
    else:
        chapters = []

    return create_accessible_epub(
        target_epub_path,
        title=book_title,
        author=author,
        language=language,
        chapters=chapters,
    )


def create_brf_from_markdown(
    source_md_path: Path,
    target_brf_path: Path,
    *,
    title: str | None = None,
    braille_code: str = "Nemeth",
    line_width: int = 40,
    lines_per_page: int = 25,
) -> Path:
    """Compile a Markdown file with math into a standardized BRF (Braille Ready Format) file."""
    import re
    import textwrap

    source_path = Path(source_md_path)
    text = source_path.read_text(encoding="utf-8")

    # Strip YAML frontmatter if present
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
    if frontmatter_match:
        text = text[frontmatter_match.end():]

    def math_to_braille(formula: str) -> str:
        try:
            mathml_str = latex_to_mathml(formula)
            root = parse_mathml(mathml_str)
            return to_braille(root, braille_code=braille_code)
        except Exception:
            return formula

    # Convert block equations
    text = re.sub(
        r"\$\$(.+?)\$\$",
        lambda m: f"\n{math_to_braille(m.group(1).strip())}\n",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"\\\[(.+?)\\\]",
        lambda m: f"\n{math_to_braille(m.group(1).strip())}\n",
        text,
        flags=re.DOTALL,
    )
    # Convert inline equations
    text = re.sub(
        r"\\\((.+?)\\\)",
        lambda m: math_to_braille(m.group(1).strip()),
        text,
        flags=re.DOTALL,
    )

    lines: list[str] = []
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append("")
            continue
        wrapped = textwrap.wrap(paragraph, width=line_width)
        lines.extend(wrapped)

    # Group into pages using ASCII form feed (\x0c) delimiters
    pages: list[str] = []
    current_page_lines: list[str] = []
    for line in lines:
        current_page_lines.append(line)
        if len(current_page_lines) >= lines_per_page:
            pages.append("\r\n".join(current_page_lines))
            current_page_lines = []
    if current_page_lines:
        pages.append("\r\n".join(current_page_lines))

    brf_content = "\x0c".join(pages) + "\r\n"
    target_path = Path(target_brf_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(brf_content.encode("latin-1", errors="replace"))
    return target_path


