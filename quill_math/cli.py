"""Command-line interface for quill_math."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from quill_math.core.latex_bridge import latex_to_mathml, mathml_to_latex
from quill_math.core.navigator import EquationNavigator, parse_equation
from quill_math.core.speech import speak
from quill_math.epub.publisher import create_epub_from_markdown
from quill_math.epub.reader import load_epub_book, render_epub_book
from quill_math.epub.validator import validate_epub
from quill_math.html.compiler import compile_file


def cmd_speak(args: argparse.Namespace) -> None:
    try:
        root = parse_equation(args.equation)
        reading = speak(root, language=getattr(args, "lang", "en"))
        print(f"Spoken reading:\n{reading}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_convert(args: argparse.Namespace) -> None:
    try:
        if args.equation.strip().startswith("<math"):
            tex = mathml_to_latex(args.equation)
            if tex:
                print(f"LaTeX:\n{tex}")
            else:
                print("No LaTeX annotation embedded in MathML.")
        else:
            mathml = latex_to_mathml(args.equation, display=args.display)
            print(f"MathML:\n{mathml}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_explore(args: argparse.Namespace) -> None:
    try:
        root = parse_equation(args.equation)
    except Exception as exc:
        print(f"Error parsing equation: {exc}", file=sys.stderr)
        sys.exit(1)

    nav = EquationNavigator(root)
    print("=== Equation Structural Explorer ===")
    print(f"Full formula: {nav.reading()}\n")

    while True:
        print(f"Current node: {nav.label()}")
        print(f"Node reading: {nav.reading()}")
        options = nav.child_options()
        if options:
            print("\nChildren:")
            for opt in options:
                print(f"  [{opt.index + 1}] {opt.label}")
        print("\nCommands: (1-N) descend, (u) up/parent, (r) root, (q) quit")

        choice = input("> ").strip().lower()
        if choice in ("q", "quit", "exit"):
            break
        elif choice in ("u", "up", "b", "back"):
            nav.ascend()
        elif choice in ("r", "reset", "root"):
            nav.reset()
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                nav.descend(idx)
            else:
                print("Invalid child index.")
        else:
            print("Unrecognized command.")
        print("-" * 40)


def cmd_validate_epub(args: argparse.Namespace) -> None:
    report = validate_epub(Path(args.epub_path))
    if report.is_valid:
        print(f"SUCCESS: '{args.epub_path}' conforms to EPUB & MathML accessibility checks.")
    else:
        print(f"FAIL: Found {len(report.errors)} error(s) in '{args.epub_path}':")
    for issue in report.issues:
        loc = f" ({issue.location})" if issue.location else ""
        print(f"  [{issue.severity.upper()}]{loc} {issue.message}")
    if not report.is_valid:
        sys.exit(1)


def cmd_read_epub(args: argparse.Namespace) -> None:
    try:
        book = load_epub_book(Path(args.epub_path))
        rendered = render_epub_book(book)
        print(rendered)
    except Exception as exc:
        print(f"Error reading EPUB: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_compile_html(args: argparse.Namespace) -> None:
    try:
        source = Path(args.input)
        target = Path(args.output) if args.output else source.with_suffix(".html")
        out = compile_file(source, target, title=args.title, language=args.lang)
        print(f"SUCCESS: Compiled '{source}' -> '{out}'")
    except Exception as exc:
        print(f"Error compiling HTML: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_publish_epub(args: argparse.Namespace) -> None:
    try:
        source = Path(args.input)
        target = Path(args.output) if args.output else source.with_suffix(".epub")
        out = create_epub_from_markdown(
            source,
            target,
            title=args.title,
            author=args.author,
            language=args.lang,
        )
        print(f"SUCCESS: Published EPUB 3.4 '{source}' -> '{out}'")
    except Exception as exc:
        print(f"Error publishing EPUB: {exc}", file=sys.stderr)
        sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    args_list = argv if argv is not None else sys.argv[1:]

    # Direct document compilation shortcut: if first arg is a markdown file
    if args_list and args_list[0].endswith(".md") and not args_list[0].startswith("-"):
        parser = argparse.ArgumentParser(
            prog="quill-math",
            description="Compile Markdown document with math into an accessible HTML5 page.",
        )
        parser.add_argument("input", help="Source markdown file (.md)")
        parser.add_argument("output", nargs="?", default=None, help="Target output HTML file (.html)")
        parser.add_argument("--title", "-t", default=None, help="Document title")
        parser.add_argument("--lang", "-l", default="en", help="Language code (default: en)")
        args = parser.parse_args(args_list)
        try:
            src = Path(args.input)
            dst = Path(args.output) if args.output else src.with_suffix(".html")
            compile_file(src, dst, title=args.title, language=args.lang)
            print(f"SUCCESS: Compiled '{src}' -> '{dst}'")
            return
        except Exception as exc:
            print(f"Error compiling HTML: {exc}", file=sys.stderr)
            sys.exit(1)

    parser = argparse.ArgumentParser(
        prog="quill-math",
        description="Accessible MathML, LaTeX, and EPUB 3.4 publishing toolkit",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # speak
    p_speak = subparsers.add_parser("speak", help="Get plain-English speech reading of an equation")
    p_speak.add_argument("equation", help="LaTeX formula or MathML string")
    p_speak.add_argument("--lang", "-l", default="en", help="Language code (default: en)")
    p_speak.set_defaults(func=cmd_speak)

    # convert
    p_convert = subparsers.add_parser("convert", help="Convert LaTeX to MathML or recover LaTeX")
    p_convert.add_argument("equation", help="LaTeX formula or MathML string")
    p_convert.add_argument("--display", choices=["inline", "block"], default="inline")
    p_convert.set_defaults(func=cmd_convert)

    # explore
    p_explore = subparsers.add_parser("explore", help="Interactively explore equation tree hierarchy")
    p_explore.add_argument("equation", help="LaTeX formula or MathML string")
    p_explore.set_defaults(func=cmd_explore)

    # validate-epub
    p_val = subparsers.add_parser("validate-epub", help="Validate EPUB package for accessibility and MathML")
    p_val.add_argument("epub_path", help="Path to .epub file")
    p_val.set_defaults(func=cmd_validate_epub)

    # read-epub
    p_read = subparsers.add_parser("read-epub", help="Extract and read EPUB content with math speech inline")
    p_read.add_argument("epub_path", help="Path to .epub file")
    p_read.set_defaults(func=cmd_read_epub)

    # compile-html
    p_html = subparsers.add_parser(
        "compile-html",
        help="Compile Markdown document with math into an accessible HTML5 page with interactive tree navigation",
    )
    p_html.add_argument("input", help="Source markdown file (.md)")
    p_html.add_argument("-o", "--output", help="Target output HTML file (.html)")
    p_html.add_argument("--title", help="Document title")
    p_html.add_argument("--lang", default="en", help="Language code (default: en)")
    p_html.set_defaults(func=cmd_compile_html)

    # publish-epub
    p_epub = subparsers.add_parser(
        "publish-epub",
        help="Publish Markdown document with math into an accessible EPUB 3.4 digital textbook",
    )
    p_epub.add_argument("input", help="Source markdown file (.md)")
    p_epub.add_argument("-o", "--output", help="Target output EPUB file (.epub)")
    p_epub.add_argument("--title", help="Book title")
    p_epub.add_argument("--author", default="Anonymous", help="Author name")
    p_epub.add_argument("--lang", default="en", help="Language code (default: en)")
    p_epub.set_defaults(func=cmd_publish_epub)

    args = parser.parse_args(args_list)
    args.func(args)


if __name__ == "__main__":
    main()
