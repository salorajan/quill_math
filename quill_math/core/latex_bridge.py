"""LaTeX <-> MathML conversion bridge.

Converts LaTeX math expressions into canonical MathML with embedded LaTeX
source annotations for lossless round-tripping.
"""

from __future__ import annotations

from quill_math.core.mathml import extract_tex_annotation, wrap_with_tex_annotation

try:
    import latex2mathml.converter as _converter
except ImportError:
    _converter = None


class LatexConversionError(Exception):
    """Raised when LaTeX math cannot be parsed or converted to MathML."""


class LatexBridgeUnavailable(Exception):
    """Raised when the optional latex2mathml package is missing."""


def latex_to_mathml(latex: str, *, display: str = "inline") -> str:
    """Convert *latex* to canonical MathML with the source embedded for round-trip."""
    if _converter is None:
        raise LatexBridgeUnavailable("latex2mathml is not installed; install latex2mathml")
    original_latex = latex
    if "\\ce{" in latex or "\\ce {" in latex:
        from quill_math.core.chemistry import transpile_mhchem
        latex = transpile_mhchem(latex)
    try:
        raw = _converter.convert(latex, display=display)
    except Exception as exc:
        raise LatexConversionError(str(exc) or type(exc).__name__) from exc
    return wrap_with_tex_annotation(raw, original_latex)


def mathml_to_latex(mathml: str) -> str | None:
    """Return the LaTeX source embedded in *mathml*, or None if not present."""
    return extract_tex_annotation(mathml)
