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


def plural(count: int, noun: str) -> str:
    """ "1 pound", "3 pounds": `count` and `noun`, an s added unless it is
    one."""
    return f"{count} {noun}{'' if count == 1 else 's'}"


def aligned(rows: Sequence[tuple[str, object]]) -> str:
    """`label: value` lines with the values lined up in one column. The
    labels are in the theme's $label colour, so the values stand out."""
    width = max(len(label) for label, _ in rows)
    return "\n".join(
        f"[$label]{label + ':':<{width + 1}}[/] {value}" for label, value in rows
    )


def inherited(text: str) -> str:
    """Markup for a value that's derived or inherited (from the saga, a Boon...) and
    isn't edited where it's shown: italic, in the $label colour, so it reads apart from
    both labels and edited values. `text` must already be escaped."""
    return f"[i $label]{text}[/]"


#: Marks a problem: something is wrong.
PROBLEM_GLYPH = "✘"
#: Marks a to-do: something still to do or worth noticing -- the manicule,
#: the pointing hand scribes drew in a margin.
TODO_GLYPH = "☞"


def problem(text: str) -> str:
    """Markup for a message saying something is wrong: led by ✘, in the theme's error
    colour, so it stands out by shape as well as colour. `text` must already be escaped.
    A number coloured by whether it's in range (a deficit, "5 of 4") stays a plain
    coloured value instead."""
    return f"[$text-error]{PROBLEM_GLYPH} {text}[/]"


def todo(text: str) -> str:
    """Markup for a message about something still to do or worth noticing
    (a point to allocate, nothing planned, a file to be replaced): led by
    ☞, in the theme's warning colour. `text` must already be
    escaped."""
    return f"[$text-warning]{TODO_GLYPH} {text}[/]"


def escape(text: str) -> str:
    """Make user text safe to embed in Textual markup. textual.markup.escape
    only protects lowercase [tags]; a capitalised one like "[Tower]" would be
    swallowed as markup, so escape every opening bracket."""
    return text.replace("[", "\\[")


_EMPHASIS_OPEN = {"*": "[i]", "**": "[b]", "~~": "[s]"}
_EMPHASIS_CLOSE = {"*": "[/i]", "**": "[/b]", "~~": "[/s]"}

#: The glyph a bulleted line is drawn with; a front-end hangs a wrapped
#: line's continuation under the words after it.
BULLET = "•"

#: A bulleted line as written ("- ", "* " or "+ ", perhaps indented).
_BULLET_LINE = re.compile(r"^([ \t]*)[-*+][ \t]+(?=\S)")
#: A numbered line as written ("1. " or "1) ", perhaps indented).
_NUMBERED_LINE = re.compile(r"^([ \t]*)(\d{1,3})[.)][ \t]+(?=\S)")
#: A list line as markdown_text draws it, for a front-end's hanging indent.
LIST_LINE = re.compile(rf"^([ \t]*)({BULLET}|\d{{1,3}}\.) ")


def markdown_text(text: str) -> str:
    """Turn user-written text with a little Markdown into safe Textual
    markup: `**bold**`, `*italic*`, `***both***` and `~~struck through~~`
    (nesting works), and lines starting `- ` (or `* `, `+ `) as bullets
    and `1. ` (or `1) `) as numbered items; all other text is escaped, so
    brackets can't be read as markup.

    An emphasis marker only opens when the character after it isn't
    whitespace and only closes when the character before it isn't, so
    "5 * 3" stays literal; unmatched markers and runs of four or more
    asterisks stay literal too; `\\*` and `\\~` are literal. Emphasis never
    spans a blank line or runs from one list item into the next, so a
    stray `*` can't italicise half the page. Deliberately small: no
    headings, tables or links."""
    parts = re.split(r"(\n[ \t]*\n)", text)  # paragraphs, keeping the separators
    return "".join(
        part if index % 2 else _paragraph(part) for index, part in enumerate(parts)
    )


def _paragraph(text: str) -> str:
    """One paragraph. Each list item (with any lines run on from it) is its
    own run of emphasis, as are the plain lines before the first."""
    runs: list[tuple[str, list[str]]] = []  # (list marker drawn, lines)
    for line in text.split("\n"):
        bullet = _BULLET_LINE.match(line)
        numbered = None if bullet else _NUMBERED_LINE.match(line)
        if bullet:
            runs.append((f"{bullet.group(1)}{BULLET} ", [line[bullet.end() :]]))
        elif numbered:
            marker = f"{numbered.group(1)}{numbered.group(2)}. "
            runs.append((marker, [line[numbered.end() :]]))
        elif runs:
            runs[-1][1].append(line)
        else:
            runs.append(("", [line]))
    return "\n".join(marker + _emphasis("\n".join(lines)) for marker, lines in runs)


#: A piece of a run of text: escaped text, or a run of one marker
#: character as (the character, its length, can open, can close).
_Piece = str | tuple[str, int, bool, bool]


def _emphasis(text: str) -> str:
    return _pair(_pieces(text))


def _pieces(text: str) -> list[_Piece]:
    """Pass 1: `text` split into escaped text pieces and marker runs."""
    pieces: list[_Piece] = []
    buffer: list[str] = []
    i = 0
    while i < len(text):
        char = text[i]
        if char == "\\" and i + 1 < len(text) and text[i + 1] in "*~\\":
            buffer.append(text[i + 1])  # an escaped marker (or backslash)
            i += 2
        elif char in "*~":
            j = i
            while j < len(text) and text[j] == char:
                j += 1
            if buffer:
                pieces.append(escape("".join(buffer)))
                buffer = []
            before = text[i - 1] if i else ""
            after = text[j] if j < len(text) else ""
            pieces.append(
                (
                    char,
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
    return pieces


def _pair(pieces: list[_Piece]) -> str:
    """Pass 2: pair up openers and closers. Every marker starts out literal
    and is only rewritten into a tag once it finds its partner."""
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
        char, length, can_open, can_close = piece
        if char == "~":
            if length == 2:
                handle("~~", can_open, can_close)
            else:
                output.append("~" * length)
        elif length == 1:
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
