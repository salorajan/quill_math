# quill-math

Accessible MathML Tree Navigation, LaTeX Translation, and EPUB 3.4 Publishing Engine.

`quill-math` is an independent, lightweight, screen-reader-first STEM toolkit designed for technical authors, researchers, educators, and blind/low-vision STEM students.

---

## Key Capabilities

1. **Accessible MathML Structural Navigation:**
   - Step hierarchically through algebraic expressions, fractions (numerator / denominator), roots (radicand / index), superscripts, and subscripts.
   - Screen-reader-friendly semantic labeling and plain-English readings.

2. **Dual-Tier Mathematical Speech:**
   - MathCAT ctypes engine support for screen-reader-grade speech and Nemeth/UEB braille.
   - Robust, zero-dependency plain-English template engine fallback.

3. **Lossless LaTeX & MathML Interop:**
   - Converts LaTeX math to MathML using `latex2mathml`.
   - Embeds original LaTeX source in `<semantics><annotation encoding="application/x-tex">` for lossless round-trips.

4. **EPUB 3.4 & EPUB Accessibility 1.2:**
   - Reader: Parses EPUBs, infers heading hierarchies, and speaks embedded MathML/LaTeX equations inline.
   - Publisher: Generates EPUB 3.4 packages conforming to EPUB Accessibility 1.2 and WCAG 2.2 AAA with native accessible MathML.
   - Validator: Audits EPUB packages for accessibility violations and malformed equations.

5. **Document Interop:**
   - DOCX OMML formula segment splitting and Pandoc document bridges.

---

## Installation

```bash
pip install -e .
```

### Optional Dependencies
- `defusedxml`: For hardened XML parsing.

---

## CLI Usage

### 1. Spoken Math Reading
```bash
quill-math speak "x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"
# Output:
# x equals the fraction minus b plus or minus the square root of b squared minus 4 a c over 2 a
```

### 2. LaTeX to MathML Conversion
```bash
quill-math convert "E = mc^2" --display inline
```

### 3. Interactive Structural Exploration
```bash
quill-math explore "\frac{a + 1}{b - 2}"
```

### 4. Compile Markdown to Accessible HTML5 (Interactive Tree Navigation)
```bash
quill-math compile-html document.md -o output.html
```

### 5. Publish Markdown to Accessible EPUB 3.4
```bash
quill-math publish-epub document.md -o output.epub --title "STEM Textbook" --author "Author"
```

### 6. EPUB Validation & Reading
```bash
quill-math validate-epub output.epub
quill-math read-epub output.epub
```

---

## Python API Quickstart

```python
from quill_math.core import EquationNavigator, latex_to_mathml, parse_equation, speak

# Convert LaTeX to canonical MathML
mathml = latex_to_mathml(r"f(x) = \sqrt{x^2 + 1}")

# Get speech reading
root = parse_equation(mathml)
print(speak(root))
# -> "f open paren x close paren equals the square root of x squared plus 1"

# Step through equation structure
nav = EquationNavigator(root)
print("Root:", nav.label())  # Equation
for child in nav.child_options():
    print("Child:", child.label)
```

---

## Running Tests

```bash
pytest
```
