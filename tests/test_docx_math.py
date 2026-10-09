"""Unit tests for docx math segment splitting."""

from quill_math.io.docx_math import MathSegment, split_math_segments


def test_split_math_segments_plain() -> None:
    segments = split_math_segments("Just plain text with a $5 bill.")
    assert len(segments) == 1
    assert segments[0].is_math is False
    assert segments[0].content == "Just plain text with a $5 bill."


def test_split_math_segments_inline() -> None:
    segments = split_math_segments(r"The formula \(E=mc^2\) is iconic.")
    assert len(segments) == 3
    assert segments[0] == MathSegment(is_math=False, content="The formula ")
    assert segments[1] == MathSegment(is_math=True, content="E=mc^2", display=False)
    assert segments[2] == MathSegment(is_math=False, content=" is iconic.")


def test_split_math_segments_block() -> None:
    segments = split_math_segments("$$x = y + 1$$")
    assert len(segments) == 1
    assert segments[0] == MathSegment(is_math=True, content="x = y + 1", display=True)


def test_batch_omml_fragments_for_latex() -> None:
    from quill_math.io.docx_math import batch_omml_fragments_for_latex

    items = [("x^2", False), ("y^2", True)]
    # Even if Pandoc is not installed or returns None, the batch executor safely completes
    results = batch_omml_fragments_for_latex(items)
    assert len(results) == 2
    assert batch_omml_fragments_for_latex([]) == []
