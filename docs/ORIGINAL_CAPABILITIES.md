# Baseline Documentation: Original QUILL Community Math Capabilities

**Project Origin:** Extracted from `Community-Access/quill` (`quill/core/math/`, `quill/core/epub.py`, `quill/io/docx_math.py`, `quill/quillins_bundled/math-equations/`)  
**Package:** `quill_math`  
**Date:** October 2026  

---

## 1. Executive Summary of Inherited Capabilities

The original Community QUILL project provided initial modules for handling mathematical content within a screen-reader-first desktop word processor. The capabilities centered around:
1. **Canonical MathML Model & TeX Annotation Embedding**
2. **LaTeX to MathML Conversion (via `latex2mathml`)**
3. **DAISY Consortium MathCAT C-API Integration**
4. **Lightweight Plain-English AST Tree Navigator**
5. **EPUB MathML/LaTeX Spoken Extraction**
6. **DOCX OMML Math Splicing**

---

## 2. Detailed Technical Breakdown of Original Modules

### 2.1. Canonical MathML Model (`quill.core.math.mathml`)
- **Philosophy:** MathML is the canonical in-memory representation shared across features (screen readers, exporters, MathCAT).
- **Round-Trip Source Preservation:** To avoid losing the author's editable LaTeX text, formulas are wrapped with:
  ```xml
  <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
    <semantics>
      <mrow>...</mrow>
      <annotation encoding="application/x-tex">LaTeX Source Here</annotation>
    </semantics>
  </math>
  ```
- **Parsing:** Uses hardened XML parsing to guard against entity-expansion attacks (`<!DOCTYPE>`, `<!ENTITY>`).

### 2.2. LaTeX Translation Bridge (`quill.core.math.latex_bridge`)
- **Engine:** Built upon the `latex2mathml` Python library.
- **Direction:** Unidirectional LaTeX $\rightarrow$ MathML conversion.
- **Reverse Lookup:** Recovers LaTeX strictly by reading the `<annotation encoding="application/x-tex">` tag.

### 2.3. The DAISY Consortium MathCAT Engine (`quill.core.math.mathcat_engine`)
- **Method:** Native `ctypes` binding to `libmathcat_c.dll` (from DAISY's `MathCATForC` library) and its associated `Rules` folder.
- **Target:** Produces natural spoken language and Nemeth / UEB braille.
- **Memory Management:** Uses `ctypes.c_void_p` and explicitly frees Rust-allocated pointers with `dll.FreeMathCATString` under a thread lock to avoid heap corruption.
- **Availability:** Optional; degraded gracefully to the template navigator when the DLL or Rules folder is absent.

### 2.4. Python Structural Navigator & Template Speech (`quill.core.math.navigator`, `quill.core.math.speech`)
- **Purpose:** In-memory Python AST traversal of MathML elements.
- **Role Tagging:**
  - `<mfrac>` $\rightarrow$ `Numerator`, `Denominator`
  - `<mroot>` $\rightarrow$ `Radicand`, `Root index`
  - `<msup>` $\rightarrow$ `Base`, `Exponent`
  - `<msub>` $\rightarrow$ `Base`, `Subscript`
  - `<msubsup>` $\rightarrow$ `Base`, `Subscript`, `Exponent`
- **Template Linear Speech:** Converts mathematical symbols (`=`, `+`, `\pm`, `\times`, `\le`, `\ge`, exponents like `squared`/`cubed`) into plain-English string representations.

### 2.5. EPUB Book Reader Math Extraction (`quill.core.epub`)
- Scans EPUB chapter files for `<math>`, `<span class="math">`, and `$$...$$` / `\(...\)` delimiters.
- Replaces math elements with placeholder tokens (`___MATH_EQ_PLACEHOLDER_N___`).
- Evaluates placeholders through the speech engine and outputs `[Math Equation: {spoken_text}]` into readable Markdown text.

### 2.6. Word DOCX OMML Math Splicing (`quill.io.docx_math`)
- Identifies math segments in paragraph text.
- Leverages Pandoc to convert LaTeX fragments into OpenXML Math (`<m:oMath>` / `<m:oMathPara>`) and splices them into DOCX runs.

---

## 3. Limitations of the Original Monorepo Implementation

While the core math logic in Python was functional, it had key gaps for standalone publication:
1. **No Interactive HTML Document Pipeline:** It could extract math *out* of an EPUB to plain text, but had no pipeline to compile Markdown/LaTeX *into* interactive, accessible HTML web pages or textbooks with client-side tree navigation.
2. **Desktop UI Dependency in Monorepo:** The interactive formula explorer was tied to the desktop `wxPython` GUI Quillin (`math-equations/extension.py`) rather than being an exportable HTML/EPUB widget usable in any browser or reader.
3. **Screen Reader Virtual Cursor Friction:** The original design had no browser runtime implementing `role="application"` focus switches or in-place navigation drawers for web readers using NVDA or JAWS.

---

## 4. Next Step: Building the Autonomous Pipeline

We will now build the **Accessible HTML & EPUB Equation Creator Pipeline** directly in `quill_math`, enabling standalone conversion of Markdown documents into self-contained, fully accessible HTML5 textbooks with client-side interactive sub-expression exploration.
