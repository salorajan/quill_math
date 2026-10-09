"""Compiler turning Markdown documents with LaTeX math into accessible HTML5 web pages."""

from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
from pathlib import Path

from quill_math.core.latex_bridge import latex_to_mathml
from quill_math.core.speech import speak
from quill_math.html.assets import NAV_CSS, NAV_JS
from quill_math.html.builder import build_inline_equation_html, build_interactive_equation_html


def _clean_latex_for_transpiler(latex: str) -> str:
    """Sanitize and standardize LaTeX strings for transpilation."""
    s = latex.strip()
    s = s.replace(r"\LaTeX", r"\text{LaTeX}")
    s = re.sub(r"\\quad|\\qquad|\\,|\\;|\\!|\\:", " ", s)
    return s.strip()


def compile_markdown_to_accessible_html(
    markdown_text: str,
    *,
    title: str | None = None,
    language: str = "en",
    include_runtime: bool = True,
) -> str:
    """Compile *markdown_text* containing math expressions into fully accessible HTML5."""
    # 1. Strip YAML frontmatter if present
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", markdown_text, flags=re.DOTALL)
    if frontmatter_match:
        markdown_text = markdown_text[frontmatter_match.end():]

    # 2. Detect title from H1 if not explicitly given
    doc_title = title
    if not doc_title:
        h1_match = re.search(r"^#\s+(.+)$", markdown_text, flags=re.MULTILINE)
        if h1_match:
            doc_title = h1_match.group(1).strip()
        else:
            doc_title = "Accessible Mathematical Document"

    # 3. Collect block equations and substitute with placeholders
    block_equations: list[dict] = []

    def block_replacer(match: re.Match) -> str:
        formula = match.group(1).strip()
        eq_idx = len(block_equations) + 1

        start_pos = match.start()
        prefix = markdown_text[:start_pos]
        heading_matches = list(re.finditer(r"(?:^|\n)#{1,6}\s+([^\n]+)", prefix))
        if heading_matches:
            raw_heading = heading_matches[-1].group(1).strip()
            clean_heading = re.sub(r"^\d+(\.\d+)*\s*", "", raw_heading)
            desc = clean_heading or raw_heading
        else:
            desc = f"Equation {eq_idx}"

        clean_latex = _clean_latex_for_transpiler(formula)
        wrapper = build_interactive_equation_html(
            clean_latex,
            eq_id=f"eq-{eq_idx}",
            description=desc,
            language=language
        )
        block_equations.append({"idx": eq_idx, "wrapper": wrapper})
        return f"\n\n<!--ACCESSIBLE_BLOCK_EQ_{eq_idx}-->\n\n"

    processed_md = re.sub(r"\$\$(.+?)\$\$", block_replacer, markdown_text, flags=re.DOTALL)
    processed_md = re.sub(r"\\\[(.+?)\\\]", block_replacer, processed_md, flags=re.DOTALL)

    # 4. Process inline math equations
    def inline_replacer(match: re.Match) -> str:
        formula = match.group(1).strip()
        clean_latex = _clean_latex_for_transpiler(formula)
        try:
            return build_inline_equation_html(
                clean_latex,
                description=f"Math: {formula}",
                language=language
            )
        except Exception:
            return f"\\({formula}\\)"

    processed_md = re.sub(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", inline_replacer, processed_md)
    processed_md = re.sub(r"\\\((.+?)\\\)", inline_replacer, processed_md)

    # 5. Convert markdown structure to HTML
    body_html = ""
    pandoc_exe = shutil.which("pandoc")
    if pandoc_exe:
        try:
            res = subprocess.run(
                [
                    pandoc_exe,
                    "-f", "gfm",
                    "-t", "html5",
                    "--wrap=none",
                ],
                input=processed_md,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True
            )
            body_html = res.stdout
        except Exception:
            body_html = ""

    if not body_html:
        raw_blocks = re.split(r"\n\s*\n", processed_md)
        html_blocks: list[str] = []
        for block in raw_blocks:
            b = block.strip()
            if not b:
                continue
            if re.match(r"^<!--ACCESSIBLE_BLOCK_EQ_\d+-->$", b):
                html_blocks.append(b)
            elif re.match(r"^(\-{3,}|\*{3,}|_{3,})$", b):
                html_blocks.append("<hr />")
            elif b.startswith("### "):
                html_blocks.append(f"<h3>{html.escape(b[4:].strip())}</h3>")
            elif b.startswith("## "):
                html_blocks.append(f"<h2>{html.escape(b[3:].strip())}</h2>")
            elif b.startswith("# "):
                html_blocks.append(f"<h1>{html.escape(b[2:].strip())}</h1>")
            elif b.startswith("#### "):
                html_blocks.append(f"<h4>{html.escape(b[5:].strip())}</h4>")
            elif b.startswith("> "):
                html_blocks.append(f"<blockquote><p>{html.escape(b[2:].strip())}</p></blockquote>")
            elif b.startswith("```"):
                code_lines = b.splitlines()[1:-1]
                html_blocks.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
            else:
                html_blocks.append(f"<p>{b}</p>")
        body_html = "\n".join(html_blocks)

    # 6. Replace block equation placeholders
    for item in block_equations:
        idx = item["idx"]
        wrapper = item["wrapper"]
        placeholder = f"<!--ACCESSIBLE_BLOCK_EQ_{idx}-->"
        body_html = re.sub(
            rf"<p>\s*{placeholder}\s*</p>",
            lambda m, w=wrapper: f"\n{w}\n",
            body_html
        )
        body_html = body_html.replace(placeholder, wrapper)

    # 7. Assemble page
    css_block = NAV_CSS if include_runtime else ""
    js_block = NAV_JS if include_runtime else ""

    return f"""<!DOCTYPE html>
<html lang="{language}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(doc_title)}</title>
  <style>
    :root {{
      --bg-primary: #ffffff;
      --bg-secondary: #f8fafc;
      --text-main: #0f172a;
      --text-muted: #475569;
      --accent: #0284c7;
      --accent-hover: #0369a1;
      --border-color: #e2e8f0;
      --code-bg: #f1f5f9;
      --code-border: #cbd5e1;
      --table-header: #f1f5f9;
      --table-row-alt: #f8fafc;
      --blockquote-border: #0284c7;
      --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
    }}

    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
        --accent: #38bdf8;
        --accent-hover: #7dd3fc;
        --border-color: #334155;
        --code-bg: #1e293b;
        --code-border: #475569;
        --table-header: #1e293b;
        --table-row-alt: #172554;
        --blockquote-border: #38bdf8;
        --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
      }}
    }}

    *, *::before, *::after {{
      box-sizing: border-box;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      line-height: 1.68;
      color: var(--text-main);
      background-color: var(--bg-primary);
      margin: 0;
      padding: 0;
    }}

    .container {{
      max-width: 960px;
      margin: 0 auto;
      padding: 40px 24px 80px 24px;
    }}

    h1, h2, h3, h4, h5, h6 {{
      color: var(--text-main);
      font-weight: 700;
      line-height: 1.3;
      margin-top: 1.8em;
      margin-bottom: 0.6em;
    }}

    h1 {{
      font-size: 2.2rem;
      border-bottom: 2px solid var(--border-color);
      padding-bottom: 0.4em;
      margin-top: 0;
    }}

    h2 {{
      font-size: 1.6rem;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 0.3em;
    }}

    h3 {{
      font-size: 1.3rem;
    }}

    p {{
      margin: 1em 0;
    }}

    blockquote {{
      margin: 1.5em 0;
      padding: 16px 20px;
      background-color: var(--bg-secondary);
      border-left: 4px solid var(--blockquote-border);
      border-radius: 0 8px 8px 0;
      color: var(--text-muted);
    }}

    blockquote p {{
      margin: 0.4em 0;
    }}

    pre {{
      background-color: var(--code-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 16px;
      overflow-x: auto;
      font-family: ui-monospace, "Cascadia Code", "Source Code Pro", Menlo, Monaco, Consolas, monospace;
      font-size: 0.92rem;
      line-height: 1.5;
    }}

    code {{
      font-family: ui-monospace, "Cascadia Code", "Source Code Pro", Menlo, Monaco, Consolas, monospace;
      font-size: 0.9em;
      background-color: var(--code-bg);
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid var(--border-color);
    }}

    pre code {{
      background-color: transparent;
      padding: 0;
      border: none;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1.8em 0;
      font-size: 0.95rem;
      background-color: var(--bg-primary);
      box-shadow: var(--card-shadow);
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid var(--border-color);
    }}

    th, td {{
      padding: 12px 16px;
      text-align: left;
      border-bottom: 1px solid var(--border-color);
      vertical-align: top;
    }}

    th {{
      background-color: var(--table-header);
      font-weight: 600;
      color: var(--text-main);
    }}

    tr:nth-child(even) {{
      background-color: var(--table-row-alt);
    }}

    tr:last-child td {{
      border-bottom: none;
    }}

    ul, ol {{
      padding-left: 1.6em;
      margin: 1em 0;
    }}

    li {{
      margin: 0.5em 0;
    }}

    hr {{
      border: none;
      border-top: 1px solid var(--border-color);
      margin: 2.5em 0;
    }}

    .inline-math-wrapper {{
      display: inline-flex;
      align-items: center;
      padding: 0 4px;
      border-radius: 4px;
      cursor: default;
      transition: background-color 0.2s;
    }}

    .inline-math-wrapper:focus {{
      outline: 2px solid var(--accent);
      background-color: rgba(2, 132, 199, 0.1);
    }}

    .interactive-equation-wrapper {{
      margin: 24px 0;
    }}
  </style>
  {css_block}
</head>
<body>
  <main class="container">
{body_html}
  </main>

  {js_block}
</body>
</html>
"""


def compile_file(
    source_path: str | Path,
    output_path: str | Path | None = None,
    *,
    title: str | None = None,
    language: str = "en",
) -> Path:
    """Read markdown from *source_path* and compile it to *output_path*."""
    src = Path(source_path)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")

    dst = Path(output_path) if output_path else src.with_suffix(".html")
    content = src.read_text(encoding="utf-8")

    doc_title = title or src.stem.replace("_", " ").replace("-", " ").title()
    html_doc = compile_markdown_to_accessible_html(content, title=doc_title, language=language)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(html_doc, encoding="utf-8")
    return dst
