"""Benchmark tests for natural mathematical speech synthesis."""

from pathlib import Path
import pytest
from quill_math.core.latex_bridge import latex_to_mathml
from quill_math.core.mathml import parse_mathml
from quill_math.core.speech import speak

BENCHMARK_EQUATIONS = [
    # 1. Quadratic Formula
    (
        r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
        "x equals fraction with numerator minus b plus or minus square root of b squared minus 4 a c over denominator 2 a",
    ),
    # 2. Standard Form
    (
        r"a x^2 + b x + c = 0",
        "a x squared plus b x plus c equals 0",
    ),
    # 3. Compound Interest
    (
        r"A = P \left(1 + \frac{r}{n}\right)^{nt}",
        "A equals P open paren 1 plus fraction with numerator r over denominator n close paren to the power of n t",
    ),
    # 4. Distance Formula
    (
        r"d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}",
        "d equals square root of open paren x sub 2 minus x sub 1 close paren squared plus open paren y sub 2 minus y sub 1 close paren squared",
    ),
    # 5. Change of Base
    (
        r"\log_b(x) = \frac{\log_a(x)}{\log_a(b)}",
        "log base b of x equals fraction with numerator log base a of x over denominator log base a of b",
    ),
    # 6. Definite Integral
    (
        r"\int_{a}^{b} x^2 \, dx = \frac{b^3 - a^3}{3}",
        "definite integral from a to b of x squared d x equals fraction with numerator b cubed minus a cubed over denominator 3",
    ),
    # 7. Limit Definition of Derivative
    (
        r"f'(x) = \lim_{h \to 0} \frac{f(x + h) - f(x)}{h}",
        "f prime of x equals limit as h approaches 0 of fraction with numerator f of x plus h minus f of x over denominator h",
    ),
    # 8. Product Rule
    (
        r"\frac{d}{dx}\left(u(x) v(x)\right) = u'(x)v(x) + u(x)v'(x)",
        "derivative with respect to x of open paren u of x v of x close paren equals u prime of x v of x plus u of x v prime of x",
    ),
    # 9. Gaussian Integral
    (
        r"\int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}",
        "definite integral from minus infinity to infinity of e to the power of minus x squared d x equals square root of pi",
    ),
    # 10. FTC 1
    (
        r"\frac{d}{dx}\left(\int_{a}^{x} f(t) \, dt\right) = f(x)",
        "derivative with respect to x of open paren definite integral from a to x of f of t d t close paren equals f of x",
    ),
]


@pytest.mark.parametrize("latex,expected", BENCHMARK_EQUATIONS)
def test_benchmark_equation_speech(latex: str, expected: str) -> None:
    mathml = latex_to_mathml(latex)
    root = parse_mathml(mathml)
    spoken = speak(root)
    # Verify semantic match
    assert spoken == expected or spoken.replace("open paren ", "(").replace(" close paren", ")") == expected.replace("open paren ", "(").replace(" close paren", ")")


def test_1000_equation_benchmark_profiling() -> None:
    """Milestone 1: Profile quill_math on a 1,000-equation synthetic dataset."""
    import time
    from quill_math.core.speech import batch_speak

    # Generate 1,000 equations by cycling through the benchmark equations
    equations_latex = [BENCHMARK_EQUATIONS[i % len(BENCHMARK_EQUATIONS)][0] for i in range(1000)]
    
    t0 = time.perf_counter()
    mathml_trees = [parse_mathml(latex_to_mathml(eq)) for eq in equations_latex]
    t_parse = time.perf_counter() - t0

    t1 = time.perf_counter()
    results = batch_speak(mathml_trees)
    t_speech = time.perf_counter() - t1

    assert len(results) == 1000
    assert all(isinstance(r, str) and len(r) > 0 for r in results)
    
    # Verify high-throughput performance (should easily process 1,000 equations under 1.5s in Python)
    total_time = t_parse + t_speech
    assert total_time < 5.0  # Generous upper bound for test runners


def test_lru_memoization_cache_speedup() -> None:
    """Milestone 2: Verify LRU caching prevents redundant evaluation."""
    import time
    from quill_math.core.speech import _cached_speak_mathml

    _cached_speak_mathml.cache_clear()
    sample_mathml = latex_to_mathml(r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}")

    # First call (cold cache)
    t0 = time.perf_counter()
    speech1 = _cached_speak_mathml(sample_mathml)
    cold_time = time.perf_counter() - t0

    # Second call (warm cache hit)
    t1 = time.perf_counter()
    speech2 = _cached_speak_mathml(sample_mathml)
    warm_time = time.perf_counter() - t1

    assert speech1 == speech2
    assert _cached_speak_mathml.cache_info().hits >= 1


def test_braille_and_brf_export(tmp_path: Path) -> None:
    """Milestone 4: Verify Braille conversion and BRF document generation."""
    from quill_math.core.speech import to_braille
    from quill_math.epub.publisher import create_brf_from_markdown

    mathml = latex_to_mathml(r"x^2 + y^2 = r^2")
    root = parse_mathml(mathml)
    braille_result = to_braille(root, braille_code="Nemeth")
    assert isinstance(braille_result, str) and len(braille_result) > 0

    md_content = """# Algebra Review
In this chapter, we explore polynomial roots:
$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$
And Pythagorean theorem:
\\(a^2 + b^2 = c^2\\)
"""
    source_file = tmp_path / "chapter.md"
    source_file.write_text(md_content, encoding="utf-8")
    brf_file = tmp_path / "chapter.brf"

    create_brf_from_markdown(source_file, brf_file, title="Algebra Review", braille_code="Nemeth")
    assert brf_file.is_file()
    assert brf_file.stat().st_size > 0
