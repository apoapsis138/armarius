"""A written Handout's text read into blocks (ADR 0021): the only way its
text reaches a drawing, on either front-end.

The text is the app's own markup (markup.markdown_text: **bold**, *italic*,
bullets) plus six handout tags, each starting a line:

- `[heading] A Proclamation`: a heading;
- `[centre] By order of the Count` (or `[center]`): a centred line;
- `[right] Given at Cologne`: a right-aligned line;
- `[initial] Know all men...`: a paragraph opening on an illuminated
  initial, running on to the next blank line;
- `[flourish]`, alone on its line: a flourish;
- `[picture 2]`, alone on its line: the Handout's second picture, placed.

A catalog entry read in full (entry_reading) is read the same way, and
may also hold pipe tables (`| Rune | Tree |`, a rule of dashes, then its
rows); a Handout's text has none.

Nothing else is a tag. Any other bracket, a tag mid-line, a tag with
nothing after it, or a picture the Handout hasn't got comes out as text,
escaped; a block never holds a file name or an address, only a picture's
number among the Handout's own.

Pattern: Interpreter, small: one function over a fixed table of tags, not
a class per tag. Each front-end draws the blocks in its own look (ADR
0008)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .markup import markdown_text
from .markup import plain as plain_markup

#: What a block is.
TEXT = "text"
HEADING = "heading"
CENTRED = "centred"
RIGHT = "right"
INITIAL = "initial"
FLOURISH = "flourish"
PICTURE = "picture"

#: The tags that lead a line of words, by the word written, and the
#: flourish, which stands alone. The placed picture is the sixth tag.
TAGS: dict[str, str] = {
    "heading": HEADING,
    "centre": CENTRED,
    "center": CENTRED,
    "right": RIGHT,
    "initial": INITIAL,
    "flourish": FLOURISH,
}

#: The most pictures a Handout has, so the most a `[picture n]` can name.
MOST_PICTURES = 4

#: A line led by a tag: the tag's word (and a picture's number), then the
#: rest of the line.
_TAGGED = re.compile(r"^\[([A-Za-z]+)(?: ([0-9]+))?\](.*)$")


#: A pipe table: its first row the header, each cell safe markup.
TABLE = "table"

#: The most rows (header included) a table holds, the rest read as text
#: after it; and the most columns, a wider one read as text.
MOST_TABLE_ROWS = 60
MOST_TABLE_COLUMNS = 8

#: A table row: a line opening and closing with a bar; and the line under
#: a table's header, its cells dashes (with an optional colon each side).
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
_TABLE_RULE = re.compile(r"^\s*\|(\s*:?-+:?\s*\|)+\s*$")
#: A bar between cells: one not written `\|`.
_CELL_BAR = re.compile(r"(?<!\\)\|")


@dataclass(frozen=True)
class Block:
    """One block of a Handout: what it is, its words as safe markup (for
    text, a heading, a centred or right line, or an initial's paragraph),
    the number of the picture it places (1 for the first), or a table's
    rows, the header first, each cell safe markup."""

    kind: str
    text: str = ""
    picture: int = 0
    rows: tuple[tuple[str, ...], ...] = ()


def table_cells(line: str) -> list[str]:
    """A pipe table row's cells, as written between its bars (`\\|` is a
    bar in a cell's words). The one reading of a row, for the reading page
    and a printed record's copy alike."""
    inner = line.strip().removeprefix("|").removesuffix("|")
    return [cell.strip().replace("\\|", "|") for cell in _CELL_BAR.split(inner)]


def _table(lines: list[str], at: int) -> tuple[Block, int] | None:
    """The pipe table starting at line `at` (a header row, a rule of
    dashes, then its rows) and the line after it; None when the lines there
    aren't one, or it is wider than a table may be. It ends at the first
    line that isn't a row of the header's width, or at its last row."""
    if at + 1 >= len(lines) or not _TABLE_ROW.match(lines[at]):
        return None
    if not _TABLE_RULE.match(lines[at + 1]):
        return None
    header = table_cells(lines[at])
    rule = table_cells(lines[at + 1])
    if len(rule) != len(header) or len(header) > MOST_TABLE_COLUMNS:
        return None
    rows = [header]
    end = at + 2
    while (
        end < len(lines)
        and len(rows) < MOST_TABLE_ROWS
        and _TABLE_ROW.match(lines[end])
        and len(table_cells(lines[end])) == len(header)
    ):
        rows.append(table_cells(lines[end]))
        end += 1
    cells = tuple(tuple(markdown_text(cell) for cell in row) for row in rows)
    return Block(TABLE, rows=cells), end


def _tag(line: str, pictures: int) -> Block | None:
    """The block a tagged `line` opens, or None when it isn't one."""
    found = _TAGGED.match(line.strip())
    if found is None:
        return None
    word, number, rest = found.group(1).lower(), found.group(2), found.group(3)
    if word == PICTURE:
        if number is None or rest.strip():
            return None
        index = int(number)
        return Block(PICTURE, picture=index) if 1 <= index <= pictures else None
    kind = TAGS.get(word)
    if kind is None or number is not None:
        return None
    if kind == FLOURISH:
        return None if rest.strip() else Block(FLOURISH)
    words = rest.strip()
    if not words or not rest.startswith(" "):
        return None
    return Block(kind, words)


def blocks(text: str, pictures: int = 0, *, tables: bool = False) -> list[Block]:
    """`text` read into blocks, in order; `pictures` is how many pictures
    the Handout has (a `[picture n]` beyond them is text). With `tables`
    (a catalog entry's text, not a Handout's), a pipe table is a table
    block."""
    found: list[Block] = []
    words: list[str] = []
    opening = TEXT

    def close() -> None:
        nonlocal opening
        if words:
            found.append(Block(opening, markdown_text("\n".join(words))))
            words.clear()
        opening = TEXT

    lines = text.splitlines()
    at = 0
    while at < len(lines):
        line = lines[at]
        at += 1
        if not line.strip():
            close()
            continue
        table = _table(lines, at - 1) if tables else None
        if table is not None:
            close()
            found.append(table[0])
            at = table[1]
            continue
        tagged = _tag(line, pictures)
        if tagged is None:
            words.append(line)
            continue
        close()
        if tagged.kind == INITIAL:
            opening = INITIAL
            words.append(tagged.text)
        elif tagged.kind in (HEADING, CENTRED, RIGHT):
            found.append(Block(tagged.kind, markdown_text(tagged.text)))
        else:
            found.append(tagged)
    close()
    return found


def plain(text: str, pictures: int = 0) -> str:
    """`text` without its tags or markup, a line or paragraph a block: what
    the terminal shows and a list row quotes. A flourish is a blank line,
    a picture "(picture 2)"."""
    lines: list[str] = []
    for block in blocks(text, pictures):
        if block.kind == FLOURISH:
            lines.append("")
        elif block.kind == PICTURE:
            lines.append(f"(picture {block.picture})")
        else:
            lines.append(plain_markup(block.text))
    return "\n".join(lines)
