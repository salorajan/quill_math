"""Canonical MathML equation model — the in-memory form every math feature shares.

MathML is the canonical representation for math structures, screen readers,
and MathML-aware exporters. The original LaTeX source is preserved by embedding
it as a ``semantics``/``annotation`` pair.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import cast

MATHML_NS = "http://www.w3.org/1998/Math/MathML"
TEX_ANNOTATION_ENCODING = "application/x-tex"

ET.register_namespace("", MATHML_NS)

_DTD_OR_ENTITY = re.compile(rb"<!(?:DOCTYPE|ENTITY)\b", re.IGNORECASE)

try:
    from defusedxml.common import DefusedXmlException
    from defusedxml.ElementTree import fromstring as _defused_fromstring

    _HAVE_DEFUSED = True
except ImportError:
    _defused_fromstring = None
    DefusedXmlException = ()  # type: ignore[assignment]
    _HAVE_DEFUSED = False


class MathMLError(Exception):
    """Raised when a string is not well-formed MathML or violates safety checks."""


@dataclass(frozen=True, slots=True)
class Equation:
    """A canonical math equation: MathML plus its LaTeX source, when known."""

    mathml: str
    latex: str | None = None


def _safe_xml_fromstring(text: str | bytes) -> ET.Element:
    """Parse untrusted XML with entity-expansion defenses."""
    if _HAVE_DEFUSED and _defused_fromstring is not None:
        try:
            return cast(ET.Element, _defused_fromstring(text))
        except DefusedXmlException as exc:
            raise MathMLError(f"Refused untrusted XML: {exc}") from exc

    raw_bytes = text if isinstance(text, bytes) else text.encode("utf-8", errors="ignore")
    if _DTD_OR_ENTITY.search(raw_bytes):
        raise MathMLError("Refused to parse XML containing a DTD or entity declaration.")
    return ET.fromstring(text)


def parse_mathml(text: str) -> ET.Element:
    """Parse *text* as MathML, raising :class:`MathMLError` on malformed input."""
    try:
        root = _safe_xml_fromstring(text)
    except Exception as exc:
        raise MathMLError(str(exc) or type(exc).__name__) from exc
    if root.tag not in (f"{{{MATHML_NS}}}math", "math"):
        raise MathMLError(f"root element is not <math>: {root.tag}")
    return root


def is_valid_mathml(text: str) -> bool:
    """Return True when *text* parses as well-formed MathML with a <math> root."""
    try:
        parse_mathml(text)
    except MathMLError:
        return False
    return True


def wrap_with_tex_annotation(mathml: str, latex: str) -> str:
    """Return *mathml* rewritten with *latex* embedded as a semantics/annotation."""
    root = parse_mathml(mathml)
    children = list(root)
    content = children[0] if len(children) == 1 else _wrap_in_mrow(children)

    semantics = ET.Element(f"{{{MATHML_NS}}}semantics")
    semantics.append(content)
    annotation = ET.SubElement(
        semantics,
        f"{{{MATHML_NS}}}annotation",
        {"encoding": TEX_ANNOTATION_ENCODING, "aria-hidden": "true"},
    )
    annotation.text = latex

    new_root = ET.Element(f"{{{MATHML_NS}}}math", dict(root.attrib))
    new_root.append(semantics)
    return ET.tostring(new_root, encoding="unicode")


def extract_tex_annotation(mathml: str) -> str | None:
    """Return the LaTeX source embedded in *mathml*'s annotation, or None."""
    root = parse_mathml(mathml)
    for annotation in root.iter(f"{{{MATHML_NS}}}annotation"):
        if annotation.get("encoding") == TEX_ANNOTATION_ENCODING:
            return annotation.text or ""
    return None


def clean_mathml_for_epub(
    mathml: str,
    *,
    speech_desc: str | None = None,
    display: str | None = None,
) -> str:
    """Return clean presentation MathML stripped of annotations, with optional natural speech_desc.

    Injects alttext when speech_desc is provided to ensure e-reader Text-to-Speech
    (Thorium Reader, Apple Books, VoiceOver, Edge) announces formulas with natural clarity,
    avoiding redundant aria-label attributes that trigger double-speaking in complex equations.
    """
    root = parse_mathml(mathml)

    if speech_desc:
        root.attrib["alttext"] = speech_desc
        root.attrib.pop("aria-label", None)
    else:
        root.attrib.pop("alttext", None)
        root.attrib.pop("aria-label", None)

    if display:
        root.attrib["display"] = display

    def _strip_annotations(el: ET.Element) -> ET.Element:
        tag = el.tag.split("}", 1)[1] if "}" in el.tag else el.tag
        if tag == "semantics":
            children = [
                c
                for c in el
                if (c.tag.split("}", 1)[1] if "}" in c.tag else c.tag) != "annotation"
            ]
            if len(children) == 1:
                return _strip_annotations(children[0])
            mrow = ET.Element(f"{{{MATHML_NS}}}mrow")
            mrow.extend([_strip_annotations(c) for c in children])
            return mrow
        new_el = ET.Element(el.tag, dict(el.attrib))
        new_el.text = el.text
        new_el.tail = el.tail
        for c in el:
            c_tag = c.tag.split("}", 1)[1] if "}" in c.tag else c.tag
            if c_tag != "annotation":
                new_el.append(_strip_annotations(c))
        return new_el

    cleaned_children = [_strip_annotations(child) for child in list(root)]
    new_root = ET.Element(f"{{{MATHML_NS}}}math", dict(root.attrib))
    new_root.extend(cleaned_children)
    return ET.tostring(new_root, encoding="unicode")


def _wrap_in_mrow(children: list[ET.Element]) -> ET.Element:
    mrow = ET.Element(f"{{{MATHML_NS}}}mrow")
    mrow.extend(children)
    return mrow
