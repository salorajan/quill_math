"""Splicing Word (OMML) equations into docx paragraphs."""

from __future__ import annotations

import functools
import re
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from quill_math.core.mathml import _safe_xml_fromstring
from quill_math.io.pandoc_bridge import PandocConversionError, PandocUnavailableError, convert_file_with_pandoc

_MATH_OMML_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
_MATH_SPAN_RE = re.compile(r"\$\$(.+?)\$\$|\\\((.+?)\\\)", re.DOTALL)


@dataclass(frozen=True, slots=True)
class MathSegment:
    """One piece of text: plain, or a single LaTeX equation."""

    is_math: bool
    content: str
    display: bool = False


def split_math_segments(text: str) -> list[MathSegment]:
    """Split *text* into plain-text and math segments.

    Recognizes ``$$...$$`` (display) and ``\\(...\\)`` (inline).
    """
    segments: list[MathSegment] = []
    pos = 0
    for match in _MATH_SPAN_RE.finditer(text):
        if match.start() > pos:
            segments.append(MathSegment(is_math=False, content=text[pos : match.start()]))
        display_latex, inline_latex = match.group(1), match.group(2)
        if display_latex is not None:
            segments.append(MathSegment(is_math=True, content=display_latex, display=True))
        else:
            segments.append(MathSegment(is_math=True, content=inline_latex, display=False))
        pos = match.end()
    if pos < len(text):
        segments.append(MathSegment(is_math=False, content=text[pos:]))
    if not segments:
        segments.append(MathSegment(is_math=False, content=text))
    return segments


@functools.lru_cache(maxsize=256)
def omml_fragment_for_latex(latex: str, *, display: bool) -> str | None:
    """Return an ``<m:oMath>``/``<m:oMathPara>`` XML fragment for *latex*, or None."""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "eq.md"
            target = tmp / "eq.docx"
            wrapped = f"$${latex}$$" if display else f"${latex}$"
            source.write_text(wrapped, encoding="utf-8")
            convert_file_with_pandoc(source, target, from_format="gfm", to_format="docx")
            with zipfile.ZipFile(target) as archive:
                xml = archive.read("word/document.xml").decode("utf-8")
    except (PandocUnavailableError, PandocConversionError, OSError, KeyError):
        return None

    try:
        root = _safe_xml_fromstring(xml)
    except Exception:
        return None
    tag = f"{_MATH_OMML_NS}oMathPara" if display else f"{_MATH_OMML_NS}oMath"
    for element in root.iter(tag):
        return ET.tostring(element, encoding="unicode")
    return None


def batch_omml_fragments_for_latex(
    items: list[tuple[str, bool]],
    max_workers: int = 4,
) -> list[str | None]:
    """Parallel batch computation of OMML fragments for a list of (latex, display) pairs."""
    if not items:
        return []
    results: list[str | None] = [None] * len(items)
    with ThreadPoolExecutor(max_workers=min(max_workers, len(items))) as executor:
        future_to_idx = {
            executor.submit(omml_fragment_for_latex, latex, display=display): idx
            for idx, (latex, display) in enumerate(items)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception:
                results[idx] = None
    return results
