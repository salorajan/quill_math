"""Unit tests for math speech synthesis and fallback."""

from quill_math.core.navigator import EquationNavigator, parse_equation
from quill_math.core.speech import mathcat_available, speak


def test_speech_fallback_to_template(monkeypatch) -> None:
    from quill_math.core import speech

    monkeypatch.setattr(speech, "mathcat_available", lambda: False)
    root = parse_equation("a^2 + b^2 = c^2")
    nav = EquationNavigator(root)
    assert speak(nav.current) == "a squared plus b squared equals c squared"


def test_speech_never_raises_on_invalid_engine(monkeypatch) -> None:
    import sys

    monkeypatch.setitem(sys.modules, "quill_math.core.mathcat_engine", None)
    root = parse_equation("x + y")
    nav = EquationNavigator(root)
    assert speak(nav.current) == "x plus y"
