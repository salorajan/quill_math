"""Structural equation tree navigator for step-by-step mathematical exploration.

Allows screen-reader and keyboard users to step through a mathematical formula's
hierarchy (numerator/denominator, base/exponent, root/radicand) with semantic
role labeling and plain-English readings.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

from quill_math.core.latex_bridge import (
    LatexBridgeUnavailable,
    LatexConversionError,
    latex_to_mathml,
)
from quill_math.core.mathml import MATHML_NS, MathMLError, parse_mathml

_TAG = f"{{{MATHML_NS}}}"

_ROLE_LABELS_EN: dict[str, tuple[str, ...]] = {
    "mfrac": ("Numerator", "Denominator"),
    "mroot": ("Radicand", "Root index"),
    "msup": ("Base", "Exponent"),
    "msub": ("Base", "Subscript"),
    "msubsup": ("Base", "Subscript", "Exponent"),
}

_ROLE_LABELS_ES: dict[str, tuple[str, ...]] = {
    "mfrac": ("Numerador", "Denominador"),
    "mroot": ("Radicando", "Índice de la raíz"),
    "msup": ("Base", "Exponente"),
    "msub": ("Base", "Subíndice"),
    "msubsup": ("Base", "Subíndice", "Exponente"),
}

_ROLE_LABELS = _ROLE_LABELS_EN

_SYMBOL_WORDS_EN: dict[str, str] = {
    "=": "equals",
    "+": "plus",
    "−": "minus",
    "-": "minus",
    "±": "plus or minus",
    "∓": "minus or plus",
    "×": "times",
    "⋅": "times",
    "·": "times",
    "*": "times",
    "/": "divided by",
    "÷": "divided by",
    "<": "is less than",
    ">": "is greater than",
    "≤": "is less than or equal to",
    "≥": "is greater than or equal to",
    "≠": "is not equal to",
    "≈": "is approximately equal to",
    "≡": "is equivalent to",
    "≅": "is isomorphic to",
    "∝": "is proportional to",
    "∼": "is distributed as",
    "~": "is distributed as",
    "≪": "is much less than",
    "≫": "is much greater than",
    "∈": "is in",
    "∉": "is not in",
    "⊂": "is a proper subset of",
    "⊆": "is a subset of",
    "⊃": "is a superset of",
    "⊇": "is a superset of or equal to",
    "∩": "intersection",
    "∪": "union",
    "∅": "empty set",
    "⇒": "implies",
    "⇔": "if and only if",
    "→": "approaches",
    "\\to": "approaches",
    "\\rightarrow": "approaches",
    "\\longrightarrow": "approaches",
    "\\rightleftharpoons": "in equilibrium with",
    "\\longleftrightarrow": "in equilibrium with",
    "⇌": "in equilibrium with",
    "⇄": "in equilibrium with",
    "∞": "infinity",
    "∑": "sum",
    "∏": "product",
    "∫": "integral",
    "∮": "contour integral",
    "∂": "partial derivative",
    "∇": "del",
    "√": "square root",
    "⊕": "direct sum",
    "⊗": "tensor product",
    "⊙": "element-wise product",
    "⊖": "symmetric difference",
    "⊘": "element-wise division",
    "‖": "norm of",
    "|": "vertical bar",
    "∣": "given",
    "(": "open paren",
    ")": "close paren",
    "[": "open bracket",
    "]": "close bracket",
    "{": "open brace",
    "}": "close brace",
    "′": "prime",
    "'": "prime",
    # Greek lowercase
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon",
    "ϵ": "epsilon", "ζ": "zeta", "η": "eta", "θ": "theta", "ϑ": "theta",
    "ι": "iota", "κ": "kappa", "λ": "lambda", "μ": "mu", "ν": "nu",
    "ξ": "xi", "π": "pi", "ϖ": "pi", "ρ": "rho", "ϱ": "rho",
    "σ": "sigma", "ς": "sigma", "τ": "tau", "υ": "upsilon", "φ": "phi",
    "ϕ": "phi", "χ": "chi", "ψ": "psi", "ω": "omega",
    # Greek uppercase
    "Γ": "Gamma", "Δ": "Delta", "Θ": "Theta", "Λ": "Lambda", "Ξ": "Xi",
    "Π": "Pi", "Σ": "Sigma", "Υ": "Upsilon", "Φ": "Phi", "Ψ": "Psi", "Ω": "Omega",
    # Script / Calligraphic uppercase
    "𝒜": "script A", "ℬ": "script B", "𝒞": "script C", "𝒟": "script D",
    "ℰ": "script E", "ℱ": "script F", "𝒢": "script G", "ℋ": "script H",
    "ℐ": "script I", "𝒥": "script J", "𝒦": "script K", "ℒ": "script L",
    "ℳ": "script M", "𝒩": "script N", "𝒪": "script O", "𝒫": "script P",
    "𝒬": "script Q", "ℛ": "script R", "𝒮": "script S", "𝒯": "script T",
    "𝒰": "script U", "𝒱": "script V", "𝒲": "script W", "𝒳": "script X",
    "𝒴": "script Y", "𝒵": "script Z",
    # Blackboard Bold
    "ℝ": "real numbers", "ℂ": "complex numbers", "ℕ": "natural numbers",
    "ℚ": "rational numbers", "ℤ": "integers", "ℙ": "probability space",
    "𝔼": "expectation", "𝔽": "field", "ℍ": "quaternions",
}

_SYMBOL_WORDS_ES: dict[str, str] = {
    "=": "igual a",
    "+": "más",
    "−": "menos",
    "-": "menos",
    "±": "más o menos",
    "∓": "menos o más",
    "×": "por",
    "⋅": "por",
    "·": "por",
    "*": "por",
    "/": "dividido por",
    "÷": "dividido por",
    "<": "menor que",
    ">": "mayor que",
    "≤": "menor o igual que",
    "≥": "mayor o igual que",
    "≠": "no es igual a",
    "≈": "aproximadamente igual a",
    "≡": "equivalente a",
    "≅": "isomorfo a",
    "∝": "proporcional a",
    "∼": "distribuido como",
    "~": "distribuido como",
    "≪": "mucho menor que",
    "≫": "mucho mayor que",
    "∈": "pertenece a",
    "∉": "no pertenece a",
    "⊂": "subconjunto propio de",
    "⊆": "subconjunto de",
    "⊃": "superconjunto de",
    "⊇": "superconjunto de o igual a",
    "∩": "intersección",
    "∪": "unión",
    "∅": "conjunto vacío",
    "⇒": "implica",
    "⇔": "si y solo si",
    "→": "tiende a",
    "\\to": "tiende a",
    "\\rightarrow": "tiende a",
    "\\longrightarrow": "tiende a",
    "\\rightleftharpoons": "en equilibrio con",
    "\\longleftrightarrow": "en equilibrio con",
    "⇌": "en equilibrio con",
    "⇄": "en equilibrio con",
    "∞": "infinito",
    "∑": "sumatoria",
    "∏": "producto",
    "∫": "integral",
    "∮": "integral de contorno",
    "∂": "derivada parcial",
    "∇": "nabla",
    "√": "raíz cuadrada",
    "⊕": "suma directa",
    "⊗": "producto tensorial",
    "⊙": "producto de Hadamard",
    "⊖": "diferencia simétrica",
    "⊘": "división elemento a elemento",
    "‖": "norma de",
    "|": "barra vertical",
    "∣": "dado",
    "(": "abrir paréntesis",
    ")": "cerrar paréntesis",
    "[": "abrir corchete",
    "]": "cerrar corchete",
    "{": "abrir llave",
    "}": "cerrar llave",
    "′": "prima",
    "'": "prima",
    # Greek lowercase
    "α": "alfa", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "épsilon",
    "ϵ": "épsilon", "ζ": "zeta", "η": "eta", "θ": "theta", "ϑ": "theta",
    "ι": "iota", "κ": "kappa", "λ": "lambda", "μ": "mu", "ν": "nu",
    "ξ": "xi", "π": "pi", "ϖ": "pi", "ρ": "rho", "ϱ": "rho",
    "σ": "sigma", "ς": "sigma", "τ": "tau", "υ": "ípsilon", "φ": "phi",
    "ϕ": "phi", "χ": "chi", "ψ": "psi", "ω": "omega",
    # Greek uppercase
    "Γ": "Gamma", "Δ": "Delta", "Θ": "Theta", "Λ": "Lambda", "Ξ": "Xi",
    "Π": "Pi", "Σ": "Sigma", "Υ": "Ípsilon", "Φ": "Phi", "Ψ": "Psi", "Ω": "Omega",
    # Script / Calligraphic uppercase
    "𝒜": "A caligráfica", "ℬ": "B caligráfica", "𝒞": "C caligráfica", "𝒟": "D caligráfica",
    "ℰ": "E caligráfica", "ℱ": "F caligráfica", "𝒢": "G caligráfica", "ℋ": "H caligráfica",
    "ℐ": "I caligráfica", "𝒥": "J caligráfica", "𝒦": "K caligráfica", "ℒ": "L caligráfica",
    "ℳ": "M caligráfica", "𝒩": "N caligráfica", "𝒪": "O caligráfica", "𝒫": "P caligráfica",
    "𝒬": "Q caligráfica", "ℛ": "R caligráfica", "𝒮": "S caligráfica", "𝒯": "T caligráfica",
    "𝒰": "U caligráfica", "𝒱": "V caligráfica", "𝒲": "W caligráfica", "𝒳": "X caligráfica",
    "𝒴": "Y caligráfica", "𝒵": "Z caligráfica",
    # Blackboard Bold
    "ℝ": "números reales", "ℂ": "números complejos", "ℕ": "números naturales",
    "ℚ": "números racionales", "ℤ": "enteros", "ℙ": "espacio de probabilidad",
    "𝔼": "esperanza matemática", "𝔽": "cuerpo", "ℍ": "cuaterniones",
}

_EXPONENT_WORDS_EN: dict[str, str] = {"2": "squared", "3": "cubed"}
_EXPONENT_WORDS_ES: dict[str, str] = {"2": "al cuadrado", "3": "al cubo"}


class MathNavigatorError(Exception):
    """Raised when an equation cannot be parsed as LaTeX or MathML."""


def _local_tag(element: ET.Element) -> str:
    tag = element.tag
    return tag[len(_TAG) :] if tag.startswith(_TAG) else tag


def _children(element: ET.Element) -> list[ET.Element]:
    return list(element)


def _text_of(element: ET.Element) -> str:
    return (element.text or "").strip()


def _symbol_reading(text: str, language: str = "en") -> str:
    if language.startswith("es"):
        return _SYMBOL_WORDS_ES.get(text, text)
    return _SYMBOL_WORDS_EN.get(text, text)


def parse_equation(text: str) -> ET.Element:
    """Parse *text* (LaTeX or MathML string) into a MathML root element."""
    stripped = text.strip()
    if stripped.startswith("<math"):
        try:
            return parse_mathml(stripped)
        except MathMLError as exc:
            raise MathNavigatorError(str(exc)) from exc
    try:
        mathml = latex_to_mathml(stripped)
    except (LatexConversionError, LatexBridgeUnavailable) as exc:
        raise MathNavigatorError(str(exc)) from exc
    return parse_mathml(mathml)


def node_kind_label(element: ET.Element, language: str = "en") -> str:
    """Return a descriptive label for *element* itself."""
    tag = _local_tag(element)
    is_es = language.startswith("es")
    if tag == "mfrac":
        return "Fracción" if is_es else "Fraction"
    if tag == "msqrt":
        return "Raíz cuadrada" if is_es else "Square root"
    if tag == "mroot":
        return "Raíz" if is_es else "Root"
    if tag in ("msup", "msub", "msubsup"):
        return read_aloud(element, language=language)
    if tag == "mrow":
        return "Grupo" if is_es else "Group"
    if tag in ("mi", "mn", "mtext"):
        return _symbol_reading(_text_of(element), language=language) or tag
    if tag == "mo":
        return _symbol_reading(_text_of(element), language=language)
    if tag in ("math", "semantics"):
        return "Ecuación" if is_es else "Equation"
    return tag


def _read_children(children: list[ET.Element], language: str = "en") -> list[str]:
    chunks: list[str] = []
    i = 0
    is_es = language.startswith("es")
    
    # Spanish function name mappings
    _FUNC_NAMES_ES = {
        "sin": "seno",
        "cos": "coseno",
        "tan": "tangente",
        "ln": "logaritmo natural",
        "exp": "exponencial",
        "log": "logaritmo",
    }

    while i < len(children):
        c = children[i]
        tag = _local_tag(c)
        text = _text_of(c)

        # 1. Check for function call: mi/msup/msub followed by ( ... )
        # e.g. f(x), f'(x), u(x), v(x), f(t), f(x + h), log_b(x)
        is_func = False
        func_speech = ""
        if tag == "mi" and text in ("f", "g", "h", "u", "v", "p", "q", "sin", "cos", "tan", "ln", "exp", "log"):
            is_func = True
            if is_es and text in _FUNC_NAMES_ES:
                func_speech = _FUNC_NAMES_ES[text]
            else:
                func_speech = _symbol_reading(text, language=language)
        elif tag == "msup":
            msup_children = _children(c)
            if len(msup_children) >= 2:
                base, exp = msup_children[0], msup_children[1]
                if _local_tag(base) == "mi" and _text_of(exp) in ("′", "'", "prime", "\u2032"):
                    is_func = True
                    prime_str = "prima" if is_es else "prime"
                    func_speech = f"{read_aloud(base, language=language)} {prime_str}"
        elif tag == "msub":
            msub_children = _children(c)
            if len(msub_children) >= 2:
                base, sub = msub_children[0], msub_children[1]
                if _text_of(base) in ("log", "logarithm"):
                    is_func = True
                    log_prefix = "logaritmo en base" if is_es else "log base"
                    func_speech = f"{log_prefix} {read_aloud(sub, language=language)}"

        if is_func and i + 1 < len(children):
            # Check if next token is '('
            next_c = children[i + 1]
            if _local_tag(next_c) == "mo" and _text_of(next_c) == "(":
                # Collect tokens until matching ')'
                depth = 0
                arg_els = []
                j = i + 1
                while j < len(children):
                    cj = children[j]
                    tj = _text_of(cj)
                    if tj == "(":
                        depth += 1
                        if depth > 1:
                            arg_els.append(cj)
                    elif tj == ")":
                        depth -= 1
                        if depth == 0:
                            j += 1
                            break
                        else:
                            arg_els.append(cj)
                    else:
                        arg_els.append(cj)
                    j += 1
                arg_speech = " ".join(_read_children(arg_els, language=language))
                chunks.append(f"{func_speech} de {arg_speech}" if is_es else f"{func_speech} of {arg_speech}")
                i = j
                continue
            elif _local_tag(next_c) == "mrow":
                mrow_children = _children(next_c)
                if len(mrow_children) >= 2 and _text_of(mrow_children[0]) == "(" and _text_of(mrow_children[-1]) == ")":
                    arg_speech = " ".join(_read_children(mrow_children[1:-1], language=language))
                    chunks.append(f"{func_speech} de {arg_speech}" if is_es else f"{func_speech} of {arg_speech}")
                    i += 2
                    continue

        # 2. Check for limit notation in msub: <msub><mo>lim</mo><mrow>h -> 0</mrow></msub>
        if tag == "msub":
            msub_children = _children(c)
            if len(msub_children) >= 2:
                base, sub = msub_children[0], msub_children[1]
                if _text_of(base) in ("lim", "limit"):
                    sub_read = read_aloud(sub, language=language)
                    if is_es:
                        chunks.append(f"límite cuando {sub_read} de")
                    else:
                        if "approaches" in sub_read:
                            chunks.append(f"limit as {sub_read} of")
                        else:
                            chunks.append(f"limit under {sub_read} of")
                    i += 1
                    continue

        # 3. Check for reaction arrow in chemical context
        if tag == "mo" and text in ("→", "\\to", "\\rightarrow", "\\longrightarrow"):
            all_texts = [_text_of(ch) for ch in children]
            has_lim = any("lim" in t.lower() for t in all_texts)
            from quill_math.core.chemistry import ELEMENTS
            has_chem = any(t in ELEMENTS for t in all_texts if len(t) <= 2)
            if has_chem and not has_lim:
                chunks.append("reacciona para formar" if is_es else "reacts to form")
                i += 1
                continue

        chunks.append(read_aloud(c, language=language))
        i += 1

    return chunks


def read_aloud(element: ET.Element, language: str = "en") -> str:
    """Return a linear plain-language reading of *element* and its subtrees."""
    tag = _local_tag(element)
    is_es = language.startswith("es")
    
    if tag in ("math", "semantics"):
        children = [c for c in _children(element) if _local_tag(c) != "annotation"]
        res = " ".join(_read_children(children, language=language))
        return " ".join(res.split())
    if tag == "mrow":
        res = " ".join(_read_children(_children(element), language=language))
        return " ".join(res.split())
    if tag in ("mi", "mn", "mtext"):
        return _symbol_reading(_text_of(element), language=language)
    if tag == "mo":
        text = _text_of(element)
        if text in ("′", "'", "\u2032"):
            return "prima" if is_es else "prime"
        return _symbol_reading(text, language=language)
    if tag == "mfrac":
        children = _children(element)
        if len(children) >= 2:
            num, den = children[0], children[1]
            num_read = read_aloud(num, language=language)
            den_read = read_aloud(den, language=language)
            # Check for derivative notation d / dx or d / dt
            if num_read.strip() == "d" and (den_read.startswith("d ") or den_read.startswith("d")):
                var = den_read.replace("d ", "").replace("d", "").strip() or "x"
                return f"derivada respecto a {var} de" if is_es else f"derivative with respect to {var} of"
            if is_es:
                return f"fracción con numerador {num_read} sobre denominador {den_read}"
            return f"fraction with numerator {num_read} over denominator {den_read}"
        return "fracción" if is_es else "fraction"
    if tag == "msqrt":
        inner = " ".join(_read_children(_children(element), language=language))
        return f"raíz cuadrada de {inner}" if is_es else f"square root of {inner}"
    if tag == "mroot":
        children = _children(element)
        if len(children) >= 2:
            radicand, index = children[0], children[1]
            idx_text = read_aloud(index, language=language)
            if idx_text == "3":
                return f"raíz cúbica de {read_aloud(radicand, language=language)}" if is_es else f"cube root of {read_aloud(radicand, language=language)}"
            return f"raíz {idx_text} de {read_aloud(radicand, language=language)}" if is_es else f"{idx_text}-root of {read_aloud(radicand, language=language)}"
        return "raíz" if is_es else "root"
    if tag == "msup":
        children = _children(element)
        if len(children) >= 2:
            base, exponent = children[0], children[1]
            exp_text = _text_of(exponent)
            if exp_text in ("′", "'", "prime", "\u2032"):
                prime_str = "prima" if is_es else "prime"
                return f"{read_aloud(base, language=language)} {prime_str}"
            if is_es:
                if exp_text in _EXPONENT_WORDS_ES:
                    return f"{read_aloud(base, language=language)} {_EXPONENT_WORDS_ES[exp_text]}"
                exp_read = read_aloud(exponent, language=language)
                if exp_read in ("2", "dos", "al cuadrado"):
                    return f"{read_aloud(base, language=language)} al cuadrado"
                if exp_read in ("3", "tres", "al cubo"):
                    return f"{read_aloud(base, language=language)} al cubo"
                return f"{read_aloud(base, language=language)} elevado a {exp_read}"
            else:
                if exp_text in _EXPONENT_WORDS_EN:
                    return f"{read_aloud(base, language=language)} {_EXPONENT_WORDS_EN[exp_text]}"
                exp_read = read_aloud(exponent, language=language)
                if exp_read in ("2", "squared"):
                    return f"{read_aloud(base, language=language)} squared"
                if exp_read in ("3", "cubed"):
                    return f"{read_aloud(base, language=language)} cubed"
                return f"{read_aloud(base, language=language)} to the power of {exp_read}"
        return "superíndice" if is_es else "superscript"
    if tag == "msub":
        children = _children(element)
        if len(children) >= 2:
            base, sub = children[0], children[1]
            base_text = _text_of(base)
            if base_text in ("log", "logarithm"):
                log_pfx = "logaritmo en base" if is_es else "log base"
                of_str = "de" if is_es else "of"
                return f"{log_pfx} {read_aloud(sub, language=language)} {of_str}"
            if base_text in ("lim", "limit"):
                sub_read = read_aloud(sub, language=language)
                if is_es:
                    return f"límite cuando {sub_read} de"
                if "approaches" in sub_read:
                    return f"limit as {sub_read} of"
                return f"limit under {sub_read} of"
            sub_raw = "".join(sub.itertext()).strip().lower().replace(" ", "")
            if sub_raw in ("(aq)", "aq", "aqueous", "acuoso"):
                return f"{read_aloud(base, language=language)} {'acuoso' if is_es else 'aqueous'}"
            if sub_raw in ("(s)", "s", "solid", "sólido", "solido"):
                return f"{read_aloud(base, language=language)} {'sólido' if is_es else 'solid'}"
            if sub_raw in ("(l)", "l", "liquid", "líquido", "liquido"):
                return f"{read_aloud(base, language=language)} {'líquido' if is_es else 'liquid'}"
            if sub_raw in ("(g)", "g", "gas"):
                return f"{read_aloud(base, language=language)} gas"
            return f"{read_aloud(base, language=language)} sub {read_aloud(sub, language=language)}"
        return "subíndice" if is_es else "subscript"
    if tag in ("msubsup", "munderover"):
        children = _children(element)
        if len(children) >= 3:
            base, sub, exp = children[0], children[1], children[2]
            base_text = _text_of(base)
            if base_text in ("∫", "integral", "\u222b"):
                if is_es:
                    return f"integral definida de {read_aloud(sub, language=language)} a {read_aloud(exp, language=language)} de"
                return f"definite integral from {read_aloud(sub, language=language)} to {read_aloud(exp, language=language)} of"
            if is_es:
                return f"{read_aloud(base, language=language)} sub {read_aloud(sub, language=language)} elevado a {read_aloud(exp, language=language)}"
            return f"{read_aloud(base, language=language)} sub {read_aloud(sub, language=language)} to the power of {read_aloud(exp, language=language)}"
        return "subíndice y superíndice" if is_es else "subscript and superscript"
    if tag in ("munder", "mover"):
        children = _children(element)
        if len(children) >= 2:
            base, under = children[0], children[1]
            base_text = _text_of(base)
            if base_text in ("lim", "limit"):
                under_read = read_aloud(under, language=language)
                if is_es:
                    return f"límite cuando {under_read} de"
                if "approaches" in under_read:
                    return f"limit as {under_read} of"
                return f"limit under {under_read} of"
            under_str = "debajo de" if is_es else "under"
            return f"{read_aloud(base, language=language)} {under_str} {read_aloud(under, language=language)}"
        return "elemento inferior" if is_es else "under element"
    res = " ".join(_read_children(_children(element), language=language))
    return " ".join(res.split())


def _normalize(node: ET.Element) -> ET.Element:
    """Collapse transparent outer wrappers (math, semantics, lone mrow) to content."""
    while True:
        tag = _local_tag(node)
        if tag in ("math", "semantics"):
            children = [c for c in _children(node) if _local_tag(c) != "annotation"]
        elif tag == "mrow":
            children = _children(node)
        else:
            return node
        if len(children) != 1:
            return node
        node = children[0]


@dataclass(frozen=True, slots=True)
class ChildOption:
    """One navigable child option of the current node."""

    index: int
    role: str
    label: str


class EquationNavigator:
    """Steps through an equation's hierarchical structure node by node."""

    def __init__(self, root: ET.Element, language: str = "en") -> None:
        self._path: list[ET.Element] = [_normalize(root)]
        self.language: str = language

    @property
    def current(self) -> ET.Element:
        return self._path[-1]

    def at_root(self) -> bool:
        return len(self._path) == 1

    def is_leaf(self) -> bool:
        return len(_children(self.current)) == 0

    def label(self) -> str:
        """A short role/kind label for the current node."""
        return node_kind_label(self.current, language=self.language)

    def reading(self) -> str:
        """The full plain-language reading of the current subtree."""
        return read_aloud(self.current, language=self.language)

    def child_options(self) -> list[ChildOption]:
        """List navigable children of the current node with role titles."""
        current = self.current
        tag = _local_tag(current)
        children = _children(current)
        if tag in ("math", "semantics"):
            children = [c for c in children if _local_tag(c) != "annotation"]
        roles_dict = _ROLE_LABELS_ES if self.language.startswith("es") else _ROLE_LABELS_EN
        roles = roles_dict.get(tag)
        options: list[ChildOption] = []
        for index, child in enumerate(children):
            role = roles[index] if roles and index < len(roles) else ""
            child_label = node_kind_label(child, language=self.language)
            label = f"{role}: {child_label}" if role else child_label
            options.append(ChildOption(index=index, role=role, label=label))
        return options

    def descend(self, index: int) -> None:
        """Descend into child at *index*."""
        current = self.current
        tag = _local_tag(current)
        children = _children(current)
        if tag in ("math", "semantics"):
            children = [c for c in children if _local_tag(c) != "annotation"]
        self._path.append(_normalize(children[index]))

    def ascend(self) -> None:
        """Ascend back to the parent node. No-op at the root."""
        if len(self._path) > 1:
            self._path.pop()

    def reset(self) -> None:
        """Jump back to the root equation node."""
        del self._path[1:]
