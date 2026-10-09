import pytest
import xml.etree.ElementTree as ET
from quill_math.core.chemistry import (
    is_chemical_formula,
    transpile_mhchem,
    chem_to_speech,
    ELEMENTS,
)
from quill_math.core.latex_bridge import latex_to_mathml
from quill_math.core.navigator import parse_equation, read_aloud
from quill_math.core.speech import speak


def test_chemistry_detection():
    assert is_chemical_formula("H2O") is True
    assert is_chemical_formula("CO2") is True
    assert is_chemical_formula(r"\ce{2H2 + O2 -> 2H2O}") is True
    assert is_chemical_formula("a^2 + b^2 = c^2") is False


def test_mhchem_transpile_and_bridge():
    mathml = latex_to_mathml(r"\ce{H2O}")
    assert "math" in mathml
    assert "H" in mathml


def test_reaction_arrows_speech():
    root = parse_equation(r"\ce{2H2 + O2 -> 2H2O}")
    speech_out = read_aloud(root)
    assert "reacts to form" in speech_out


def test_equilibrium_speech():
    root = parse_equation(r"\ce{N2 + 3H2 <=> 2NH3}")
    speech_out = read_aloud(root)
    assert "in equilibrium with" in speech_out


def test_chem_speech_util():
    assert chem_to_speech("H2O") == "H 2 O"
    assert "reacts to form" in chem_to_speech(r"2H2 + O2 -> 2H2O")
