"""Markup helpers shared by the UI and the pure-logic modules.

User text goes into Textual markup in many places (list rows, details panels,
confirm messages); these keep it safe and let descriptions use inline emphasis.
"""

from __future__ import annotations

import re
from collections.abc import Sequence


def fit(text: str, width: int) -> str:
    """`text` on one line, cut to `width` with an ellipsis if it's longer and
    padded to `width` if it's shorter -- one fixed-width table column."""
    text = text.replace("\n", " ")
    if len(text) > width:
        text = text[: width - 1] + "…"
    return text.ljust(width)


def aligned(rows: Sequence[tuple[str, object]]) -> str:
    """`label: value` lines with the values lined up in one column. The
    labels are in the theme's $label colour, so the values stand out
    (STORY-1012)."""
    width = max(len(label) for label, _ in rows)
    return "\n".join(
        f"[$label]{label + ':':<{width + 1}}[/] {value}" for label, value in rows
    )


def inherited(text: str) -> str:
    """Markup for a value that's derived or inherited (from the saga, a
    Boon...) and isn't edited where it's shown: italic, in the $label
    colour, so it reads apart from both labels and edited values
    (STORY-1012). `text` must already be escaped."""
    return f"[i $label]{text}[/]"


#: Marks a problem: something is wrong (STORY-1015).
PROBLEM_GLYPH = "✘"
#: Marks a to-do: something still to do or worth noticing -- the manicule,
#: the pointing hand scribes drew in a margin (STORY-1015).
TODO_GLYPH = "☞"


def problem(text: str) -> str:
    """Markup for a message saying something is wrong: led by ✘, in the
    theme's error colour, so it stands out by shape as well as colour
    (STORY-1015). `text` must already be escaped. A number coloured by
    whether it's in range (a deficit, "5 of 4") stays a plain coloured
    value instead."""
    return f"[$text-error]{PROBLEM_GLYPH} {text}[/]"


def todo(text: str) -> str:
    """Markup for a message about something still to do or worth noticing
    (a point to allocate, nothing planned, a file to be replaced): led by
    ☞, in the theme's warning colour (STORY-1015). `text` must already be
    escaped."""
    return f"[$text-warning]{TODO_GLYPH} {text}[/]"


def escape(text: str) -> str:
    """Make user text safe to embed in Textual markup. textual.markup.escape
    only protects lowercase [tags]; a capitalised one like "[Tower]" would be
    swallowed as markup, so escape every opening bracket."""
    return text.replace("[", "\\[")


_EMPHASIS_OPEN = {"*": "[i]", "**": "[b]"}
_EMPHASIS_CLOSE = {"*": "[/i]", "**": "[/b]"}


def markdown_inline(text: str) -> str:
    """Turn user-written text with inline Markdown emphasis into safe Textual
    markup: `**bold**`, `*italic*` and `***both***` (nesting works); all other
    text is escaped, so brackets can't be read as markup.

    An asterisk run only opens emphasis when the character after it isn't
    whitespace and only closes when the character before it isn't, so "5 * 3"
    stays literal; unmatched runs and runs of four or more stay literal too;
    `\\*` is a literal asterisk. Emphasis never spans a blank line, so a stray
    `*` can't italicise half the page. Deliberately just emphasis -- no
    headings, lists or links."""
    parts = re.split(r"(\n[ \t]*\n)", text)  # paragraphs, keeping the separators
    return "".join(
        part if index % 2 else _emphasis_paragraph(part)
        for index, part in enumerate(parts)
    )


def _emphasis_paragraph(text: str) -> str:
    # Pass 1: split into escaped text pieces and asterisk runs.
    pieces: list[
        str | tuple[int, bool, bool]
    ] = []  # text, or (run length, can open, can close)
    buffer: list[str] = []
    i = 0
    while i < len(text):
        char = text[i]
        if char == "\\" and i + 1 < len(text) and text[i + 1] in "*\\":
            buffer.append(text[i + 1])  # an escaped asterisk (or backslash)
            i += 2
        elif char == "*":
            j = i
            while j < len(text) and text[j] == "*":
                j += 1
            if buffer:
                pieces.append(escape("".join(buffer)))
                buffer = []
            before = text[i - 1] if i else ""
            after = text[j] if j < len(text) else ""
            pieces.append(
                (
                    j - i,
                    bool(after) and not after.isspace(),
                    bool(before) and not before.isspace(),
                )
            )
            i = j
        else:
            buffer.append(char)
            i += 1
    if buffer:
        pieces.append(escape("".join(buffer)))

    # Pass 2: pair up openers and closers. Every marker starts out literal
    # and is only rewritten into a tag once it finds its partner.
    output: list[str] = []
    stack: list[tuple[str, int]] = []  # (marker, slot in `output`)

    def handle(marker: str, can_open: bool, can_close: bool) -> None:
        slot = len(output)
        output.append(marker)  # literal unless paired below
        if can_close and stack and stack[-1][0] == marker:
            _, open_slot = stack.pop()
            output[open_slot] = _EMPHASIS_OPEN[marker]
            output[slot] = _EMPHASIS_CLOSE[marker]
        elif can_open:
            stack.append((marker, slot))

    for piece in pieces:
        if isinstance(piece, str):
            output.append(piece)
            continue
        length, can_open, can_close = piece
        if length == 1:
            handle("*", can_open, can_close)
        elif length == 2:
            handle("**", can_open, can_close)
        elif length == 3:
            # ***x***: bold outside italic when opening, italic closes first.
            closing = can_close and bool(stack)
            for marker in ("*", "**") if closing else ("**", "*"):
                handle(marker, can_open, can_close)
        else:
            output.append("*" * length)
    return "".join(output)
