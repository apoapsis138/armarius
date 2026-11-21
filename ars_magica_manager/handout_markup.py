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


@dataclass(frozen=True)
class Block:
    """One block of a Handout: what it is, its words as safe markup (for
    text, a heading, a centred or right line, or an initial's paragraph),
    or the number of the picture it places (1 for the first)."""

    kind: str
    text: str = ""
    picture: int = 0


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


def blocks(text: str, pictures: int = 0) -> list[Block]:
    """`text` read into blocks, in order; `pictures` is how many pictures
    the Handout has (a `[picture n]` beyond them is text)."""
    found: list[Block] = []
    words: list[str] = []
    opening = TEXT

    def close() -> None:
        nonlocal opening
        if words:
            found.append(Block(opening, markdown_text("\n".join(words))))
            words.clear()
        opening = TEXT

    for line in text.splitlines():
        if not line.strip():
            close()
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
