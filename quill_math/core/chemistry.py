"""Chemical formula and equation recognition, transpilation, and speech engine for quill_math.

Provides seamless support for mhchem \\ce{...} syntax, chemical formula parsing,
reaction arrow semantics, state of matter indicators, and element lookups.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

# Periodic Table of Elements (Atomic numbers 1 to 118)
ELEMENTS: dict[str, str] = {
    "H": "Hydrogen", "He": "Helium", "Li": "Lithium", "Be": "Beryllium",
    "B": "Boron", "C": "Carbon", "N": "Nitrogen", "O": "Oxygen",
    "F": "Fluorine", "Ne": "Neon", "Na": "Sodium", "Mg": "Magnesium",
    "Al": "Aluminum", "Si": "Silicon", "P": "Phosphorus", "S": "Sulfur",
    "Cl": "Chlorine", "Ar": "Argon", "K": "Potassium", "Ca": "Calcium",
    "Sc": "Scandium", "Ti": "Titanium", "V": "Vanadium", "Cr": "Chromium",
    "Mn": "Manganese", "Fe": "Iron", "Co": "Cobalt", "Ni": "Nickel",
    "Cu": "Copper", "Zn": "Zinc", "Ga": "Gallium", "Ge": "Germanium",
    "As": "Arsenic", "Se": "Selenium", "Br": "Bromine", "Kr": "Krypton",
    "Rb": "Rubidium", "Sr": "Strontium", "Y": "Yttrium", "Zr": "Zirconium",
    "Nb": "Niobium", "Mo": "Molybdenum", "Tc": "Technetium", "Ru": "Ruthenium",
    "Rh": "Rhodium", "Pd": "Palladium", "Ag": "Silver", "Cd": "Cadmium",
    "In": "Indium", "Sn": "Tin", "Sb": "Antimony", "Te": "Tellurium",
    "I": "Iodine", "Xe": "Xenon", "Cs": "Cesium", "Ba": "Barium",
    "La": "Lanthanum", "Ce": "Cerium", "Pr": "Praseodymium", "Nd": "Neodymium",
    "Pm": "Promethium", "Sm": "Samarium", "Eu": "Europium", "Gd": "Gadolinium",
    "Tb": "Terbium", "Dy": "Dysprosium", "Ho": "Holmium", "Er": "Erbium",
    "Tm": "Thulium", "Yb": "Ytterbium", "Lu": "Lutetium", "Hf": "Hafnium",
    "Ta": "Tantalum", "W": "Tungsten", "Re": "Rhenium", "Os": "Osmium",
    "Ir": "Iridium", "Pt": "Platinum", "Au": "Gold", "Hg": "Mercury",
    "Tl": "Thallium", "Pb": "Lead", "Bi": "Bismuth", "Po": "Polonium",
    "At": "Astatine", "Rn": "Radon", "Fr": "Francium", "Ra": "Radium",
    "Ac": "Actinium", "Th": "Thorium", "Pa": "Protactinium", "U": "Uranium",
    "Np": "Neptunium", "Pu": "Plutonium", "Am": "Americium", "Cm": "Curium",
    "Bk": "Berkelium", "Cf": "Californium", "Es": "Einsteinium", "Fm": "Fermium",
    "Md": "Mendelevium", "No": "Nobelium", "Lr": "Lawrencium", "Rf": "Rutherfordium",
    "Db": "Dubnium", "Sg": "Seaborgium", "Bh": "Bohrium", "Hs": "Hassium",
    "Mt": "Meitnerium", "Ds": "Darmstadtium", "Rg": "Roentgenium", "Cn": "Copernicium",
    "Nh": "Nihonium", "Fl": "Flerovium", "Mc": "Moscovium", "Lv": "Livermorium",
    "Ts": "Tennessine", "Og": "Oganesson"
}

STATE_OF_MATTER: dict[str, str] = {
    "(aq)": "aqueous",
    "(s)": "solid",
    "(l)": "liquid",
    "(g)": "gas",
    "aq": "aqueous",
    "s": "solid",
    "l": "liquid",
    "g": "gas"
}

REACTION_ARROWS: dict[str, str] = {
    "->": "reacts to form",
    "-->": "reacts to form",
    "\\rightarrow": "reacts to form",
    "\\longrightarrow": "reacts to form",
    "\\to": "reacts to form",
    "→": "reacts to form",
    "\\rightleftharpoons": "in equilibrium with",
    "\\longleftrightarrow": "in equilibrium with",
    "<=>": "in equilibrium with",
    "<->": "in equilibrium with",
    "⇌": "in equilibrium with",
    "⇄": "in equilibrium with",
    "<-": "formed from",
    "\\leftarrow": "formed from",
    "←": "formed from",
}


def is_chemical_symbol(token: str) -> bool:
    """Return True if *token* is a standard chemical element symbol."""
    return token in ELEMENTS


def is_chemical_formula(text: str) -> bool:
    """Heuristic check whether text represents a chemical formula or equation."""
    if not text or not text.strip():
        return False
    stripped = text.strip()
    if "\\ce{" in stripped or "\\ce {" in stripped:
        return True
    if any(k in stripped for k in ("->", "<=>", "\\rightleftharpoons", "⇌", "⇄", "(aq)")):
        return True
    
    tokens = re.findall(r"[A-Z][a-z]?", stripped)
    if tokens and all(t in ELEMENTS for t in tokens):
        if len(tokens) >= 1 and re.search(r"\d", stripped):
            return True
        if len(tokens) >= 2:
            return True
    return False


def transpile_mhchem(latex: str) -> str:
    """
    Transpiles LaTeX containing \\ce{...} (mhchem syntax) into canonical LaTeX math.
    """
    if "\\ce{" not in latex and "\\ce {" not in latex:
        return latex

    def _convert_ce_body(body: str) -> str:
        body = body.strip()
        body = re.sub(r"<=>|<->", r" \\rightleftharpoons ", body)
        body = re.sub(r"->|-->", r" \\rightarrow ", body)
        body = re.sub(r"<-|<--", r" \\leftarrow ", body)
        body = re.sub(r"\((aq|s|l|g)\)", r"_{(\1)}", body, flags=re.IGNORECASE)
        body = re.sub(r"\^?([0-9]*[\+\-])(?=[\s\+_]|$)", r"^{\1}", body)

        def _sub_digits(m: re.Match) -> str:
            elem = m.group(1)
            digits = m.group(2)
            return f"{elem}_{{{digits}}}"

        body = re.sub(r"([A-Z][a-z]?)(\d+)", _sub_digits, body)
        return body

    pattern = re.compile(r"\\ce\{([^}]+)\}")
    return pattern.sub(lambda m: _convert_ce_body(m.group(1)), latex)


def chem_to_speech(text: str) -> str:
    """Return natural spoken reading for chemical text / LaTeX."""
    if not text:
        return ""
    
    for arrow, spoken in REACTION_ARROWS.items():
        if arrow in text:
            parts = text.split(arrow)
            spoken_parts = [chem_to_speech(p.strip()) for p in parts]
            return f" {spoken} ".join(spoken_parts)

    for state, spoken_state in STATE_OF_MATTER.items():
        if f"({state})" in text or f"_{{({state})}}" in text:
            text = text.replace(f"_{{({state})}}", f" {spoken_state}")
            text = text.replace(f"({state})", f" {spoken_state}")

    if "+" in text and not re.search(r"\^\+?|\d\+", text):
        terms = text.split("+")
        return " plus ".join(chem_to_speech(t.strip()) for t in terms)

    cleaned = re.sub(r"\\text\{([^}]+)\}", r"\1", text)
    cleaned = re.sub(r"\\ce\{([^}]+)\}", r"\1", cleaned)
    cleaned = cleaned.replace("{", "").replace("}", "").replace("_", "").replace("^", " ")

    words: list[str] = []
    tokens = re.findall(r"[A-Z][a-z]?|\d+|\+|\-|\(|\)", cleaned)
    for tok in tokens:
        if tok in ELEMENTS:
            if len(tok) == 2:
                words.append(f"{tok[0]} {tok[1]}")
            else:
                words.append(tok)
        elif tok == "+":
            words.append("plus")
        elif tok == "-":
            words.append("minus")
        elif tok == "(":
            words.append("open paren")
        elif tok == ")":
            words.append("close paren")
        else:
            words.append(tok)

    return " ".join(words)
