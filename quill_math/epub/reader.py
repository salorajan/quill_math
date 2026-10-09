"""Accessible EPUB reader with structured heading inference and math speech extraction."""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path

from quill_math.core.latex_bridge import latex_to_mathml
from quill_math.core.mathml import parse_mathml
from quill_math.core.navigator import _normalize
from quill_math.core.speech import speak

_HTML_HEADING_PATTERN = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
_BLOCK_PATTERN = re.compile(r"<(p|div)\b([^>]*)>(.*?)</\1>", re.IGNORECASE | re.DOTALL)
_CLASS_PATTERN = re.compile(r'class\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
_ALL_BOLD_PATTERN = re.compile(
    r"^\s*<(?:b|strong)\b[^>]*>(.*?)</(?:b|strong)>\s*$", re.IGNORECASE | re.DOTALL
)

_CLASS_LEVEL_HINTS: tuple[tuple[str, int], ...] = (
    ("h1", 1),
    ("h2", 2),
    ("h3", 3),
    ("h4", 4),
    ("h5", 5),
    ("h6", 6),
    ("chapter", 1),
    ("title", 1),
    ("subtitle", 2),
    ("section", 2),
    ("subhead", 3),
    ("heading", 2),
    ("head", 2),
)

_MAX_INFERRED_HEADING_WORDS = 14

_MATH_TAG_PATTERN = re.compile(r"<math\b[^>]*>.*?</math>", re.DOTALL | re.IGNORECASE)
_LATEX_TAG_PATTERN = re.compile(
    r"<(span|div)\b[^>]*\bclass\s*=\s*['\"][^'\"]*?\b(?:math|latex)\b[^'\"]*?['\"][^>]*>(.*?)</\1>",
    re.DOTALL | re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class EpubHeading:
    level: int
    title: str


@dataclass(frozen=True, slots=True)
class EpubChapter:
    title: str
    href: str
    text: str
    headings: tuple[EpubHeading, ...] = ()
    body: str = ""
    headings_inferred: bool = False


@dataclass(frozen=True, slots=True)
class EpubBook:
    title: str
    chapters: tuple[EpubChapter, ...]


def _strip_latex_delimiters(text: str) -> str:
    t = text.strip()
    if t.startswith("$$") and t.endswith("$$") and len(t) > 4:
        return t[2:-2].strip()
    if t.startswith(r"\(") and t.endswith(r"\)") and len(t) > 4:
        return t[2:-2].strip()
    if t.startswith(r"\[") and t.endswith(r"\]") and len(t) > 4:
        return t[2:-2].strip()
    if t.startswith("$") and t.endswith("$") and len(t) > 2:
        return t[1:-1].strip()
    return t


def _convert_mathml_to_speech(mathml_str: str) -> str:
    try:
        root = parse_mathml(mathml_str)
        if root.attrib.get("alttext"):
            return root.attrib["alttext"]
        if root.attrib.get("aria-label"):
            return root.attrib["aria-label"]
        normalized = _normalize(root)
        return speak(normalized)
    except Exception:
        try:
            root = parse_mathml(html.unescape(mathml_str))
            if root.attrib.get("alttext"):
                return root.attrib["alttext"]
            if root.attrib.get("aria-label"):
                return root.attrib["aria-label"]
            normalized = _normalize(root)
            return speak(normalized)
        except Exception:
            without_tags = re.sub(r"<[^>]+>", " ", mathml_str)
            decoded = html.unescape(without_tags)
            return " ".join(decoded.split())


def _convert_latex_to_speech(latex_str: str) -> str:
    try:
        clean = html.unescape(latex_str)
        mathml = latex_to_mathml(clean)
        return _convert_mathml_to_speech(mathml)
    except Exception:
        return latex_str


def _extract_math_placeholders(content: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}
    counter = 0

    def math_replacer(match: re.Match[str]) -> str:
        nonlocal counter
        mathml_str = match.group(0)
        placeholder = f"___MATH_EQ_PLACEHOLDER_{counter}___"
        spoken = _convert_mathml_to_speech(mathml_str)
        placeholders[placeholder] = f"[Math Equation: {spoken}]"
        counter += 1
        return f" {placeholder} "

    def latex_replacer(match: re.Match[str]) -> str:
        nonlocal counter
        latex_str = match.group(2).strip()
        placeholder = f"___MATH_EQ_PLACEHOLDER_{counter}___"
        clean_latex = _strip_latex_delimiters(latex_str)
        spoken = _convert_latex_to_speech(clean_latex)
        placeholders[placeholder] = f"[Math Equation: {spoken}]"
        counter += 1
        return f" {placeholder} "

    content = _MATH_TAG_PATTERN.sub(math_replacer, content)
    content = _LATEX_TAG_PATTERN.sub(latex_replacer, content)
    return content, placeholders


def _process_embedded_latex_delimiters(text: str) -> str:
    def replace_latex(match: re.Match[str]) -> str:
        latex_str = match.group(1).strip()
        spoken = _convert_latex_to_speech(latex_str)
        return f" [Math Equation: {spoken}] "

    text = re.sub(r"\$\$(.*?)\$\$", replace_latex, text, flags=re.DOTALL)
    text = re.sub(r"\\\[(.*?)\\\]", replace_latex, text, flags=re.DOTALL)
    text = re.sub(r"\\\((.*?)\\\)", replace_latex, text, flags=re.DOTALL)
    return text


def _extract_text(content: str) -> str:
    body_only = re.sub(r"<head\b[^>]*>.*?</head>", " ", content, flags=re.DOTALL | re.IGNORECASE)
    body_match = re.search(r"<body\b[^>]*>(.*?)</body>", body_only, flags=re.DOTALL | re.IGNORECASE)
    working_text = body_match.group(1) if body_match else body_only

    working_text, placeholders = _extract_math_placeholders(working_text)
    without_tags = re.sub(r"<[^>]+>", " ", working_text)
    for placeholder, math_repr in placeholders.items():
        without_tags = without_tags.replace(placeholder, math_repr)
    without_tags = _process_embedded_latex_delimiters(without_tags)
    decoded = html.unescape(without_tags)
    return " ".join(decoded.split())


def _clean_inline_text(raw: str) -> str:
    stripped = _HTML_TAG_PATTERN.sub("", raw)
    return " ".join(html.unescape(stripped).split())


def _true_heading_spans(content: str) -> list[tuple[int, int, int, str]]:
    spans: list[tuple[int, int, int, str]] = []
    for m in _HTML_HEADING_PATTERN.finditer(content):
        level = int(m.group(1))
        title = _clean_inline_text(m.group(2))
        if title:
            spans.append((m.start(), m.end(), level, title))
    return spans


def _infer_heading_spans(content: str) -> list[tuple[int, int, int, str]]:
    spans: list[tuple[int, int, int, str]] = []
    for m in _BLOCK_PATTERN.finditer(content):
        attrs, inner = m.group(2), m.group(3)
        class_match = _CLASS_PATTERN.search(attrs)
        class_name = class_match.group(1).lower() if class_match else ""
        level = None
        for keyword, candidate_level in _CLASS_LEVEL_HINTS:
            if keyword in class_name:
                level = candidate_level
                break
        if level is None and _ALL_BOLD_PATTERN.match(inner):
            level = 2
        if level is not None:
            title = _clean_inline_text(inner)
            if title and len(title.split()) <= _MAX_INFERRED_HEADING_WORDS:
                spans.append((m.start(), m.end(), level, title))
    return spans


def _render_chapter_body(content: str, spans: list[tuple[int, int, int, str]]) -> str:
    chunks: list[str] = []
    last_idx = 0
    for start, end, level, title in spans:
        prose_before = _extract_text(content[last_idx:start])
        if prose_before:
            chunks.append(prose_before)
        prefix = "#" * max(1, min(6, level + 2))
        chunks.append(f"{prefix} {title}")
        last_idx = end
    trailing = _extract_text(content[last_idx:])
    if trailing:
        chunks.append(trailing)
    return "\n\n".join(chunks)


def load_epub_book(path: Path) -> EpubBook:
    """Load an EPUB book file into an accessible EpubBook dataclass."""
    with zipfile.ZipFile(path, "r") as archive:
        chapter_files = _chapter_files(archive)
        toc = _read_toc(archive)
        title = _read_book_title(archive) or path.stem
        chapters: list[EpubChapter] = []
        ordered = toc if toc else [(Path(name).stem, name) for name in chapter_files]
        for label, href in ordered:
            matched = _resolve_href(chapter_files, href)
            if matched is None:
                continue
            raw_content = archive.read(matched).decode("utf-8", errors="ignore")
            body_match = re.search(r"<body\b[^>]*>(.*?)</body>", raw_content, flags=re.DOTALL | re.IGNORECASE)
            content = body_match.group(1) if body_match else re.sub(r"<head\b[^>]*>.*?</head>", " ", raw_content, flags=re.DOTALL | re.IGNORECASE)
            text = _extract_text(content)
            true_spans = _true_heading_spans(content)
            spans = true_spans
            inferred = False
            if not spans:
                spans = _infer_heading_spans(content)
                inferred = bool(spans)
            headings = tuple(
                EpubHeading(level=level, title=t) for _s, _e, level, t in spans
            )
            body = _render_chapter_body(content, spans) if spans else text
            chapters.append(
                EpubChapter(
                    title=label or Path(matched).stem,
                    href=matched,
                    text=text,
                    headings=headings,
                    body=body,
                    headings_inferred=inferred,
                )
            )
    return EpubBook(title=title, chapters=tuple(chapters))


def render_epub_book(book: EpubBook) -> str:
    """Render the full EPUB book to accessible markdown format."""
    lines = [f"# EPUB: {book.title}", ""]
    for index, chapter in enumerate(book.chapters, start=1):
        lines.append(f"## {index}. {chapter.title}")
        lines.append("")
        lines.append(chapter.body or chapter.text)
        lines.append("")
    return "\n".join(lines).strip()


def _chapter_files(archive: zipfile.ZipFile) -> list[str]:
    names = [name for name in archive.namelist() if name.lower().endswith((".xhtml", ".html", ".htm"))]
    return sorted(names)


def _resolve_href(chapter_files: list[str], href: str) -> str | None:
    target = href.split("#", 1)[0].replace("\\", "/")
    for name in chapter_files:
        if name == target or name.endswith(f"/{target}") or Path(name).name == Path(target).name:
            return name
    return None


def _read_spine(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    """Read reading order from OPF manifest & spine."""
    opf_files = [name for name in archive.namelist() if name.lower().endswith(".opf")]
    if not opf_files:
        return []
    try:
        opf_path = opf_files[0]
        base_dir = str(Path(opf_path).parent).replace("\\", "/")
        data = archive.read(opf_path).decode("utf-8", errors="ignore")
        root = ET.fromstring(data)

        # Build manifest map: id -> (href, properties)
        manifest: dict[str, tuple[str, str]] = {}
        for item in root.iter("{http://www.idpf.org/2007/opf}item"):
            item_id = item.attrib.get("id", "")
            href = item.attrib.get("href", "")
            props = item.attrib.get("properties", "")
            if item_id and href:
                full_href = f"{base_dir}/{href}" if base_dir and base_dir != "." else href
                manifest[item_id] = (full_href, props)

        # Read spine
        spine: list[tuple[str, str]] = []
        for itemref in root.iter("{http://www.idpf.org/2007/opf}itemref"):
            idref = itemref.attrib.get("idref", "")
            if idref in manifest:
                href, props = manifest[idref]
                if "nav" not in props:  # Skip nav doc from reading spine
                    spine.append((Path(href).stem, href))
        return spine
    except Exception:
        return []


def _read_toc(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    """Read TOC from NCX or EPUB 3 nav document."""
    # 1. Try NCX (EPUB 2 / EPUB 3 compatibility)
    ncx_files = [name for name in archive.namelist() if name.lower().endswith(".ncx")]
    if ncx_files:
        try:
            data = archive.read(ncx_files[0]).decode("utf-8", errors="ignore")
            root = ET.fromstring(data)
            toc: list[tuple[str, str]] = []
            for nav_point in root.iter("{http://www.daisy.org/z3986/2005/ncx/}navPoint"):
                text_el = nav_point.find("{http://www.daisy.org/z3986/2005/ncx/}navLabel/{http://www.daisy.org/z3986/2005/ncx/}text")
                content_el = nav_point.find("{http://www.daisy.org/z3986/2005/ncx/}content")
                label = (text_el.text or "").strip() if text_el is not None else ""
                src = content_el.attrib.get("src", "").strip() if content_el is not None else ""
                if src:
                    toc.append((label, src))
            if toc:
                return toc
        except Exception:
            pass

    # 2. Try EPUB 3 nav.xhtml
    for name in archive.namelist():
        if "nav" in name.lower() and name.lower().endswith((".xhtml", ".html")):
            try:
                data = archive.read(name).decode("utf-8", errors="ignore")
                root = ET.fromstring(data)
                toc: list[tuple[str, str]] = []
                base_dir = str(Path(name).parent).replace("\\", "/")

                # Find <nav epub:type="toc"> or <nav id="toc">
                toc_nav = None
                for nav in root.iter("{http://www.w3.org/1999/xhtml}nav"):
                    epub_type = (
                        nav.attrib.get("{http://www.idpf.org/2007/ops}type", "")
                        or nav.attrib.get("epub:type", "")
                    )
                    nav_id = nav.attrib.get("id", "")
                    if epub_type == "toc" or nav_id == "toc":
                        toc_nav = nav
                        break
                if toc_nav is None:
                    toc_nav = root.find(".//{http://www.w3.org/1999/xhtml}nav")

                search_root = toc_nav if toc_nav is not None else root
                for a in search_root.iter("{http://www.w3.org/1999/xhtml}a"):
                    href = a.attrib.get("href", "").strip()
                    label = "".join(a.itertext()).strip()
                    if href and not href.startswith("#"):
                        full_href = f"{base_dir}/{href}" if base_dir and base_dir != "." else href
                        toc.append((label, full_href))
                if toc:
                    return toc
            except Exception:
                pass

    # 3. Fallback to spine order
    return _read_spine(archive)


def _read_book_title(archive: zipfile.ZipFile) -> str | None:
    opf_files = [name for name in archive.namelist() if name.lower().endswith(".opf")]
    if not opf_files:
        return None
    try:
        data = archive.read(opf_files[0]).decode("utf-8", errors="ignore")
        root = ET.fromstring(data)
        title_el = root.find(".//{http://purl.org/dc/elements/1.1/}title")
        return (title_el.text or "").strip() if title_el is not None else None
    except Exception:
        return None

