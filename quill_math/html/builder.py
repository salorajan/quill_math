"""Builder for accessible interactive equation card HTML wrappers."""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from typing import Any

from quill_math.core.latex_bridge import latex_to_mathml
from quill_math.core.mathml import MATHML_NS, parse_mathml
from quill_math.core.navigator import (
    _ROLE_LABELS,
    _children,
    _local_tag,
    _normalize,
    node_kind_label,
    read_aloud,
)
from quill_math.core.speech import speak


def build_node_tree(node: ET.Element, role: str = "") -> dict[str, Any]:
    """Recursively convert a normalized MathML XML element into a navigable JSON node tree."""
    normalized = _normalize(node)
    tag = _local_tag(normalized)
    label = node_kind_label(normalized)
    reading = read_aloud(normalized)

    children_els = _children(normalized)
    if tag in ("math", "semantics"):
        children_els = [c for c in children_els if _local_tag(c) != "annotation"]

    roles = _ROLE_LABELS.get(tag)
    child_trees: list[dict[str, Any]] = []

    for idx, child in enumerate(children_els):
        child_role = roles[idx] if roles and idx < len(roles) else ""
        child_trees.append(build_node_tree(child, role=child_role))

    return {
        "tag": tag,
        "role": role,
        "label": label,
        "reading": reading,
        "children": child_trees,
    }


def build_interactive_equation_html(
    equation_input: str,
    *,
    eq_id: str = "eq-1",
    description: str = "Mathematical equation",
    language: str = "en",
    speech: str | None = None,
    svg_str: str = "",
) -> str:
    """Build the accessible interactive equation wrapper HTML string for *equation_input*."""
    stripped = equation_input.strip()
    is_es = language.startswith("es")

    # Parse to MathML element
    if stripped.startswith("<math"):
        root = parse_mathml(stripped)
        clean_ml = stripped
        latex_str = ""
    else:
        latex_str = stripped
        clean_ml = latex_to_mathml(stripped, display="block")
        root = parse_mathml(clean_ml)

    # Clean display attribute if needed
    if 'xmlns="http://www.w3.org/1998/Math/MathML"' not in clean_ml:
        clean_ml = clean_ml.replace("<math", '<math xmlns="http://www.w3.org/1998/Math/MathML"', 1)
    if 'display="block"' not in clean_ml:
        clean_ml = clean_ml.replace("<math", '<math display="block"', 1)

    raw_spoken = speech if speech else speak(root, language=language)
    spoken_summary = re.sub(r"\s+([,.:;])", r"\1", raw_spoken).strip()
    escaped_description = html.escape(description)
    escaped_speech = html.escape(spoken_summary)
    escaped_mathml = html.escape(clean_ml)
    escaped_latex = html.escape(latex_str) if latex_str else ""

    latex_attr = f' data-latex="{escaped_latex}"' if escaped_latex else ""

    drawer_aria_label = "Navegador de subexpresiones matemáticas" if is_es else "Math Sub-expression Navigator"
    level_badge_text = "Nivel 0: Ecuación completa" if is_es else "Level 0: Whole Equation"
    term_list_aria_label = "Subexpresiones de la ecuación" if is_es else "Equation Sub-expressions"

    shortcuts_html = """            <span><kbd>←</kbd> / <kbd>→</kbd> Hermanos</span>
            <span><kbd>↓</kbd> / <kbd>Enter</kbd> Profundizar</span>
            <span><kbd>↑</kbd> / <kbd>Esc</kbd> Subir</span>
            <span><kbd>Backspace</kbd> Salir</span>""" if is_es else """            <span><kbd>←</kbd> / <kbd>→</kbd> Siblings</span>
            <span><kbd>↓</kbd> / <kbd>Enter</kbd> Drill Down</span>
            <span><kbd>↑</kbd> / <kbd>Esc</kbd> Go Up</span>
            <span><kbd>Backspace</kbd> Exit</span>"""

    nav_toggle_label = "Navegar ecuación en el lugar" if is_es else "Navigate equation in-place"
    nav_toggle_text = "Navegar en el lugar" if is_es else "Navigate In-Place"
    speak_label = "Escuchar ecuación en voz alta" if is_es else "Speak equation aloud"
    speak_text = "Escuchar" if is_es else "Speak"
    code_label = "Mostrar código y detalles de la ecuación" if is_es else "Show equation code and details"
    code_text = "Código y detalles" if is_es else "Code & Details"

    visual_content = ""
    if svg_str:
        visual_content = f'<div class="math-svg-container" aria-hidden="true">{svg_str}</div>'

    return f"""<div class="interactive-equation-wrapper" 
     id="wrapper-{eq_id}"
     tabindex="0"
     role="region"
     data-eq-id="{eq_id}"
     data-description="{escaped_description}" 
     data-speech="{escaped_speech}"
     data-mathml="{escaped_mathml}"{latex_attr}
     aria-label="{escaped_description}">
    <div class="equation-container">
        {visual_content}
        {clean_ml}
    </div>
    
    <!-- In-Place MathJax SRE Style Navigation Drawer -->
    <div class="in-place-nav-drawer" role="application" aria-label="{drawer_aria_label}" style="display: none;" aria-hidden="true">
        <div class="in-place-nav-header">
            <span class="in-place-level-badge">{level_badge_text}</span>
            <span class="in-place-speech-text">{escaped_speech}</span>
        </div>
        <div class="in-place-term-list" role="group" aria-label="{term_list_aria_label}"></div>
        <div class="in-place-shortcuts" aria-hidden="true">
{shortcuts_html}
        </div>
    </div>
    
    <div class="eq-actions-overlay">
        <button type="button" class="eq-action-btn nav-toggle-btn" aria-label="{nav_toggle_label}"><span class="icon" aria-hidden="true">🎯</span> {nav_toggle_text}</button>
        <button type="button" class="eq-action-btn speak-btn" aria-label="{speak_label}"><span class="icon" aria-hidden="true">🔊</span> {speak_text}</button>
        <button type="button" class="eq-action-btn focus-btn" aria-label="{code_label}"><span class="icon" aria-hidden="true">📋</span> {code_text}</button>
    </div>
</div>"""


def build_inline_equation_html(
    equation_input: str,
    *,
    description: str = "Mathematical expression",
    language: str = "en",
    speech: str | None = None,
    svg_str: str = "",
) -> str:
    """Build the accessible inline math span wrapper."""
    stripped = equation_input.strip()

    if stripped.startswith("<math"):
        root = parse_mathml(stripped)
        clean_ml = stripped
        latex_str = ""
    else:
        latex_str = stripped
        clean_ml = latex_to_mathml(stripped, display="inline")
        root = parse_mathml(clean_ml)

    raw_spoken = speech if speech else speak(root, language=language)
    spoken_summary = re.sub(r"\s+([,.:;])", r"\1", raw_spoken).strip()
    escaped_description = html.escape(description)
    escaped_speech = html.escape(spoken_summary)
    escaped_mathml = html.escape(clean_ml)
    escaped_latex = html.escape(latex_str) if latex_str else ""
    latex_attr = f' data-latex="{escaped_latex}"' if escaped_latex else ""

    visual_content = ""
    if svg_str:
        visual_content = f'<span class="inline-math-svg" aria-hidden="true">{svg_str}</span>'

    clean_ml_inline = clean_ml.replace("\n", " ").strip()
    return f'<span class="inline-math-wrapper" tabindex="0" role="region" data-description="{escaped_description}" data-speech="{escaped_speech}" data-mathml="{escaped_mathml}"{latex_attr} aria-label="{escaped_description}">{visual_content}{clean_ml_inline}</span>'
