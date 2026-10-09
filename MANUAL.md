# `quill_math` User Manual & Verification Guide

**Project:** `quill_math` (Accessible STEM & EPUB 3.4 Publishing Toolkit)  
**Location:** `c:\salo\quill_light\quill_math`  
**Version:** 0.1.0  

---

## 1. Introduction

`quill_math` is an independent, lightweight, accessible mathematics and EPUB 3.4 publishing toolkit. It provides:
1. **Plain-English Math Speech:** Linear spoken readings of algebraic formulas, calculus expressions, inequalities, and exponents.
2. **Structural Equation Navigation:** Hierarchical tree navigation designed for keyboard and screen-reader users to step into fractions, roots, powers, and sub-expressions.
3. **Lossless LaTeX & MathML Interop:** Conversion between LaTeX and canonical MathML with `<semantics><annotation encoding="application/x-tex">` source embedding.
4. **Accessible EPUB 3.4 Publishing & Reading:** Full compliance with EPUB Accessibility 1.2 and WCAG 2.2 AAA recommendations, embedding native MathML.
5. **EPUB Accessibility Auditing:** Automated verification of metadata, navigation landmarks, and MathML syntax.

---

## 2. Quick Setup & Installation

Navigate to the project folder in your command terminal (with your virtual environment active):

```powershell
cd C:\salo\quill_light\quill_math
python -m pip install -e .
```

Verify that the CLI is installed and responsive:

```powershell
quill-math --help
```

---

## 3. Command-Line Interface (CLI) Manual & Examples

### 3.1. Generating Spoken Readings (`quill-math speak`)

Translates mathematical expressions into plain-English speech suitable for screen readers.

#### Example 1: Basic Algebra
```powershell
quill-math speak "a^2 + b^2 = c^2"
```
**Expected Output:**
```
Spoken reading:
a squared plus b squared equals c squared
```

#### Example 2: Quadratic Formula (Fractions, Roots, Plus-Minus)
```powershell
quill-math speak "x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"
```
**Expected Output:**
```
Spoken reading:
x equals the fraction minus b plus or minus the square root of b squared minus 4 a c over 2 a
```

#### Example 3: Greek Letters & Higher Exponents
```powershell
quill-math speak "\alpha x^5 + \beta x^3 + \gamma = 0"
```
**Expected Output:**
```
Spoken reading:
α x to the power 5 plus β x cubed plus γ equals 0
```

---

### 3.2. Lossless LaTeX <-> MathML Conversion (`quill-math convert`)

Converts LaTeX into valid W3C MathML and embeds the LaTeX source inside `<annotation encoding="application/x-tex">` for round-trip fidelity.

#### Example 1: Inline LaTeX to MathML
```powershell
quill-math convert "E = mc^2" --display inline
```
**Expected Output:**
```xml
MathML:
<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline"><semantics><mrow><mi>E</mi><mo>=</mo><mi>m</mi><msup><mi>c</mi><mn>2</mn></msup></mrow><annotation encoding="application/x-tex">E = mc^2</annotation></semantics></math>
```

#### Example 2: Block Display MathML
```powershell
quill-math convert "\int_0^\infty e^{-x} dx = 1" --display block
```

#### Example 3: Recovering Original LaTeX from MathML
```powershell
quill-math convert "<math xmlns='http://www.w3.org/1998/Math/MathML'><semantics><mrow><mi>x</mi></mrow><annotation encoding='application/x-tex'>x = 42</annotation></semantics></math>"
```
**Expected Output:**
```
LaTeX:
x = 42
```

---

### 3.3. Interactive Structural Navigation (`quill-math explore`)

Allows a user to step into nested mathematical nodes step-by-step.

#### Example Walkthrough:
Run the interactive explorer with a rational formula:

```powershell
quill-math explore "x = \frac{a + 1}{b - 2}"
```

**Interactive Session:**
```
=== Equation Structural Explorer ===
Full formula: x equals the fraction a plus 1 over b minus 2

Current node: Equation
Node reading: x equals the fraction a plus 1 over b minus 2

Children:
  [1] x
  [2] equals
  [3] Fraction

Commands: (1-N) descend, (u) up/parent, (r) root, (q) quit
> 3
----------------------------------------
Current node: Fraction
Node reading: the fraction a plus 1 over b minus 2

Children:
  [1] Numerator: a plus 1
  [2] Denominator: b minus 2

Commands: (1-N) descend, (u) up/parent, (r) root, (q) quit
> 1
----------------------------------------
Current node: Group
Node reading: a plus 1

Children:
  [1] a
  [2] plus
  [3] 1

Commands: (1-N) descend, (u) up/parent, (r) root, (q) quit
> u
----------------------------------------
Current node: Fraction
Node reading: the fraction a plus 1 over b minus 2

Commands: (1-N) descend, (u) up/parent, (r) root, (q) quit
> q
```

---

### 3.4. EPUB 3.4 Validation & Accessibility Check (`quill-math validate-epub`)

Audits EPUB files for EPUB Accessibility 1.2 compliance, metadata completeness, and MathML syntax validity.

#### Example:
```powershell
quill-math validate-epub my_book.epub
```

**Expected Output (Passing EPUB):**
```
SUCCESS: 'my_book.epub' conforms to EPUB & MathML accessibility checks.
```

---

### 3.5. Reading EPUB with Inline Math Speech (`quill-math read-epub`)

Extracts chapters in true reading order, speaking embedded MathML formulas inline.

```powershell
quill-math read-epub my_book.epub
```

**Expected Output:**
```markdown
# EPUB: Accessible Calculus

## 1. Chapter 1: Introduction

Definition: [Math Equation: f open paren x close paren equals x squared] is continuous.
```

---

## 4. Python API Manual & Verification Scripts

You can also verify all features directly in Python.

### 4.1. Converting Formulas & Reading Aloud

Create a test script or run in the Python REPL:

```python
from quill_math.core import (
    EquationNavigator,
    latex_to_mathml,
    mathml_to_latex,
    parse_equation,
    speak,
)

# 1. LaTeX to MathML
latex_input = r"f(x) = \sqrt{x^2 + 1}"
mathml = latex_to_mathml(latex_input)
print("Generated MathML:", mathml)

# 2. Extract LaTeX back out
recovered = mathml_to_latex(mathml)
assert recovered == latex_input
print("Recovered LaTeX:", recovered)

# 3. Spoken Reading
root = parse_equation(mathml)
print("Speech:", speak(root))
# Output: "f open paren x close paren equals the square root of x squared plus 1"
```

---

### 4.2. Creating an Accessible EPUB 3.4 Document

```python
from pathlib import Path
from quill_math.epub import create_accessible_epub, load_epub_book, render_epub_book, validate_epub

output_path = Path("sample_textbook.epub")

chapters = [
    {
        "title": "Kinematics",
        "content_html": """
            <p>The displacement equation is:</p>
            <math xmlns="http://www.w3.org/1998/Math/MathML">
              <mrow>
                <mi>s</mi>
                <mo>=</mo>
                <msub><mi>v</mi><mn>0</mn></msub><mi>t</mi>
                <mo>+</mo>
                <mfrac>
                  <mrow><mn>1</mn></mrow>
                  <mrow><mn>2</mn></mrow>
                </mfrac>
                <mi>a</mi><msup><mi>t</mi><mn>2</mn></msup>
              </mrow>
            </math>
        """,
    }
]

# Build EPUB 3.4
epub_file = create_accessible_epub(
    output_path,
    title="Physics for STEM",
    author="Galileo Galilei",
    language="en",
    chapters=chapters,
)

print("Created EPUB:", epub_file)

# Validate Accessibility
report = validate_epub(epub_file)
print("Is Valid:", report.is_valid)
print("Errors:", len(report.errors))

# Read Back with Spoken Math
book = load_epub_book(epub_file)
print("\nRendered Markdown:")
print(render_epub_book(book))
```

---

### 4.3. Document Segment Splitting (`split_math_segments`)

```python
from quill_math.io import split_math_segments

text = r"Here is inline \(x + y = z\) and display $$E=mc^2$$ in text."
segments = split_math_segments(text)

for seg in segments:
    print(f"is_math={seg.is_math}, display={seg.display}, content={seg.content!r}")
```

---

## 5. Automated Test Suite Execution

Run the complete test suite to verify all units:

```powershell
cd C:\salo\quill_light\quill_math
pytest -v
```

**Expected Result:**
```
============================= test session starts =============================
collected 32 items

tests/test_docx_math.py::test_split_math_segments_plain PASSED           [  3%]
tests/test_docx_math.py::test_split_math_segments_inline PASSED          [  6%]
tests/test_docx_math.py::test_split_math_segments_block PASSED           [  9%]
tests/test_epub_publisher.py::test_create_and_validate_accessible_epub PASSED [ 12%]
tests/test_epub_reader.py::test_load_epub_basic PASSED                   [ 15%]
tests/test_epub_reader.py::test_load_epub_with_mathml PASSED             [ 18%]
tests/test_epub_reader.py::test_load_epub_with_xml_entities PASSED       [ 21%]
tests/test_epub_reader.py::test_render_epub_markdown PASSED              [ 25%]
tests/test_latex_bridge.py::test_latex_to_mathml_valid PASSED           [ 28%]
tests/test_latex_bridge.py::test_latex_to_mathml_roundtrip PASSED       [ 31%]
tests/test_latex_bridge.py::test_latex_to_mathml_greek PASSED           [ 34%]
tests/test_latex_bridge.py::test_latex_to_mathml_display_block PASSED   [ 37%]
tests/test_latex_bridge.py::test_latex_to_mathml_error_on_invalid PASSED [ 40%]
tests/test_mathml.py::test_parse_mathml_valid PASSED                     [ 43%]
tests/test_mathml.py::test_parse_mathml_rejects_non_math PASSED          [ 46%]
tests/test_mathml.py::test_parse_mathml_rejects_malformed PASSED         [ 50%]
tests/test_mathml.py::test_is_valid_mathml PASSED                        [ 53%]
tests/test_mathml.py::test_wrap_and_extract_roundtrip_single PASSED      [ 56%]
tests/test_mathml.py::test_wrap_and_extract_roundtrip_multiple PASSED    [ 59%]
tests/test_mathml.py::test_extract_tex_annotation_none_when_absent PASSED [ 62%]
tests/test_mathml.py::test_wrap_preserves_display PASSED                 [ 65%]
tests/test_mathml.py::test_equation_dataclass PASSED                     [ 68%]
tests/test_navigator.py::test_parse_equation_latex PASSED                [ 71%]
tests/test_navigator.py::test_parse_equation_mathml PASSED               [ 75%]
tests/test_navigator.py::test_parse_equation_invalid PASSED              [ 78%]
tests/test_navigator.py::test_read_aloud_pythagorean PASSED              [ 81%]
tests/test_navigator.py::test_read_aloud_quadratic PASSED                [ 84%]
tests/test_navigator.py::test_read_aloud_powers PASSED                   [ 87%]
tests/test_navigator.py::test_navigator_tree_walking PASSED             [ 90%]
tests/test_navigator.py::test_node_kind_label PASSED                     [ 93%]
tests/test_speech.py::test_speech_fallback_to_template PASSED           [ 96%]
tests/test_speech.py::test_speech_never_raises_on_invalid_engine PASSED  [100%]

============================= 32 passed in 0.19s ==============================
```

---

## 6. Architecture & File Structure Reference

| Path | Purpose |
| :--- | :--- |
| [`pyproject.toml`](file:///C:/salo/quill_light/quill_math/pyproject.toml) | Modern packaging configuration (Hatchling backend, Python `>=3.12`) |
| [`plan_math.md`](file:///C:/salo/quill_light/quill_math/plan_math.md) | Full architectural blueprint & roadmap |
| [`MANUAL.md`](file:///C:/salo/quill_light/quill_math/MANUAL.md) | This user manual and verification guide |
| [`quill_math/cli.py`](file:///C:/salo/quill_light/quill_math/quill_math/cli.py) | Command-line interface entry points |
| [`quill_math/core/mathml.py`](file:///C:/salo/quill_light/quill_math/quill_math/core/mathml.py) | Canonical MathML model, safe XML parser, TeX annotation wrapping |
| [`quill_math/core/latex_bridge.py`](file:///C:/salo/quill_light/quill_math/quill_math/core/latex_bridge.py) | LaTeX to MathML translation & source recovery |
| [`quill_math/core/navigator.py`](file:///C:/salo/quill_light/quill_math/quill_math/core/navigator.py) | AST tree navigation & plain-English operator readings |
| [`quill_math/core/speech.py`](file:///C:/salo/quill_light/quill_math/quill_math/core/speech.py) | Math speech synthesizer (MathCAT + template fallback) |
| [`quill_math/epub/publisher.py`](file:///C:/salo/quill_light/quill_math/quill_math/epub/publisher.py) | Accessible EPUB 3.4 compiler conforming to EPUB A11y 1.2 |
| [`quill_math/epub/reader.py`](file:///C:/salo/quill_light/quill_math/quill_math/epub/reader.py) | EPUB parser with heading inference and inline math extraction |
| [`quill_math/epub/validator.py`](file:///C:/salo/quill_light/quill_math/quill_math/epub/validator.py) | Automated accessibility and MathML auditor |
| [`quill_math/io/docx_math.py`](file:///C:/salo/quill_light/quill_math/quill_math/io/docx_math.py) | Document math segment splitting & Pandoc bridge |
