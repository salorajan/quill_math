"""Spoken mathematical rendering bridge (MathCAT primary, template fallback)."""

from __future__ import annotations

import functools
import xml.etree.ElementTree as ET

from quill_math.core.mathml import MATHML_NS
from quill_math.core.navigator import read_aloud as _template_read_aloud


def mathcat_available() -> bool:
    """Return True if the MathCAT engine pack is installed."""
    try:
        from quill_math.core import mathcat_engine

        return mathcat_engine.is_available()
    except Exception:
        return False


@functools.lru_cache(maxsize=4096)
def _cached_speak_mathml(mathml_str: str, language: str = "en") -> str:
    """Cached speech generator for normalized MathML strings."""
    if mathcat_available():
        try:
            from quill_math.core import mathcat_engine

            if language != "en":
                try:
                    mathcat_engine.set_preference("Language", language)
                except Exception:
                    pass
            return mathcat_engine.mathml_to_speech(mathml_str)
        except Exception:
            pass
    from quill_math.core.mathml import parse_mathml

    root = parse_mathml(mathml_str)
    return _template_read_aloud(root, language=language)


def speak(element: ET.Element, language: str = "en") -> str:
    """Return the best available spoken reading for *element* (never raises)."""
    try:
        tag = element.tag.split("}", 1)[1] if "}" in element.tag else element.tag
        if tag == "math":
            raw_inner = "".join(ET.tostring(c, encoding="unicode") for c in element)
            mathml_str = f'<math xmlns="{MATHML_NS}">{raw_inner}</math>'
        else:
            mathml_str = f'<math xmlns="{MATHML_NS}">{ET.tostring(element, encoding="unicode")}</math>'
        return _cached_speak_mathml(mathml_str, language=language)
    except Exception:
        return _template_read_aloud(element, language=language)


def batch_speak(elements: list[ET.Element], language: str = "en") -> list[str]:
    """Return spoken readings for a list of MathML elements in batch."""
    return [speak(el, language=language) for el in elements]


def to_braille(element: ET.Element, braille_code: str = "Nemeth") -> str:
    """Return Braille representation for *element* using MathCAT if available."""
    if mathcat_available():
        try:
            from quill_math.core import mathcat_engine

            mathcat_engine.set_preference("BrailleCode", braille_code)
            tag = element.tag.split("}", 1)[1] if "}" in element.tag else element.tag
            if tag == "math":
                raw_inner = "".join(ET.tostring(c, encoding="unicode") for c in element)
                mathml_str = f'<math xmlns="{MATHML_NS}">{raw_inner}</math>'
            else:
                mathml_str = f'<math xmlns="{MATHML_NS}">{ET.tostring(element, encoding="unicode")}</math>'
            return mathcat_engine.mathml_to_braille(mathml_str)
        except Exception:
            pass
    # Fallback to spoken reading if Braille engine is not active
    return speak(element)
