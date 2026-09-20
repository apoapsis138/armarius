import pytest
from textual.content import Content

from ars_magica_manager.screens import markdown_inline


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("plain text", "plain text"),
        ("a **bold** b", "a [b]bold[/b] b"),
        ("a *italic* b", "a [i]italic[/i] b"),
        ("***both***", "[b][i]both[/i][/b]"),
        ("**bold *and italic* bold**", "[b]bold [i]and italic[/i] bold[/b]"),
        ("*ital **bold** ital*", "[i]ital [b]bold[/b] ital[/i]"),
        ("two **a** and **b**", "two [b]a[/b] and [b]b[/b]"),
    ],
)
def test_emphasis_becomes_markup(text, expected):
    assert markdown_inline(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "5 * 3 * 2",  # space-flanked: multiplication, not emphasis
        "stray * star",
        "**oops",  # unmatched
        "oops**",
        "a ** b ** c",
        "****",  # four or more: literal
        "* bullet-looking line",
    ],
)
def test_asterisks_that_are_not_emphasis_stay_literal(text):
    assert markdown_inline(text) == text


def test_backslash_gives_a_literal_asterisk():
    assert markdown_inline(r"\*not italic\*") == "*not italic*"
    assert markdown_inline(r"a \ b") == r"a \ b"  # and an escaped backslash


def test_everything_else_is_escaped_so_brackets_cannot_become_markup():
    # Capitalised tags were the case Textual's own escape() missed.
    assert (
        markdown_inline("**[Tower]** of *[Iris]*")
        == r"[b]\[Tower][/b] of [i]\[Iris][/i]"
    )
    assert markdown_inline("[b]not bold[/b]") == r"\[b]not bold\[/b]"


def test_emphasis_never_spans_a_blank_line():
    # The stray * in paragraph one must not pair with the * in paragraph two.
    text = "para *one\n\nstill *literal*"
    assert markdown_inline(text) == "para *one\n\nstill [i]literal[/i]"


def test_multi_line_text_and_blank_lines_are_preserved():
    text = "Accessible Value: **250**\n\nLocation: sealed *Muto*\nContents: books"
    assert markdown_inline(text) == (
        "Accessible Value: [b]250[/b]\n\nLocation: sealed [i]Muto[/i]\nContents: books"
    )


def test_output_parses_into_the_expected_styled_spans():
    content = Content.from_markup(markdown_inline("a **bold** and *italic* [Tower]"))
    assert content.plain == "a bold and italic [Tower]"
    styled = {(content.plain[s.start : s.end], str(s.style)) for s in content.spans}
    assert styled == {("bold", "b"), ("italic", "i")}
