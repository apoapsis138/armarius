"""Any Handout a player holds laid out for paper (print_layout's blocks):
a written Handout on its Stationery, a record's copy as it was shown, a
picture on a page of its own. The desktop draws them (gui.handout_print);
the terminal doesn't print.

A written Handout's words reach the page only through the one tag parser
(handout_layout.reading, handout_markup.blocks), as on screen. A record's
copy was frozen as the Markdown of its printed sheet (show_copy), so it is
read back into that sheet's blocks: its title, headings, tables, facts,
Virtues and Flaws and paragraphs. A picture is printed under its Show's
title, never its copy's file name.

Pattern: Builder, as print_records: each builder fills a Document with
blocks that one renderer draws, and LAYOUTS picks the builder by what the
Handout holds (Strategy). Unlike print_records' builders these need no
Protection Proxy in front of them: a Handout's copy was frozen when it
was shown and holds only what its reader was shown."""

from __future__ import annotations

import re
from collections.abc import Callable

from . import handout_layout as hl
from . import handout_markup as hm
from .handout_list import PICTURE, RECORD, WRITTEN
from .print_layout import (
    Block,
    Cell,
    Column,
    Document,
    Entry,
    Facts,
    Flourish,
    Heading,
    Paragraph,
    Passage,
    Picture,
    Table,
    Title,
)
from .shows import Shown

#: The line under a picture Handout's title, and under a record copy's
#: whose Markdown has none of its own.
PICTURE_SUBTITLE = "A picture shown"
RECORD_SUBTITLE = "As it was shown"

#: Where each kind of a written Handout's block stands on paper.
_ALIGN = {hl.LEFT: "l", hl.CENTRE: "c", hl.RIGHT: "r"}


def kind_of(shown: Shown) -> str:
    """What a Handout's copy holds: a written Handout, a picture or a
    record (handout_list's kinds)."""
    if shown.written:
        return WRITTEN
    return PICTURE if shown.picture is not None else RECORD


# ---------------------------------------------------------------- written


def _placed(block: hl.Placed, pictures: tuple[bytes | None, ...]) -> Block:
    if block.kind == hm.FLOURISH:
        return Flourish()
    if block.kind == hm.PICTURE:
        data = pictures[block.picture - 1] if block.picture <= len(pictures) else None
        return Picture(data, block.caption, number=block.picture)
    return Passage(
        block.text,
        _ALIGN.get(block.align, "l"),
        heading=block.kind == hm.HEADING,
        initial=block.initial,
    )


def written_document(shown: Shown) -> Document:
    """A written Handout's copy on its Stationery: its title, then its
    blocks as the tag parser reads them, each placed picture with the
    bytes shown with it."""
    laid = hl.reading(shown.title, shown.stationery, shown.text, shown.pictures).laid
    label = laid.stationery.label
    blocks: list[Block] = [Title(laid.title, label)]
    blocks += [_placed(block, shown.pictures) for block in laid.blocks]
    return Document(laid.title, label, blocks, stationery=laid.stationery.name)


# ---------------------------------------------------------------- picture


def picture_document(shown: Shown) -> Document:
    """A picture's copy: its title, then the picture filling the page."""
    title = shown.title.strip() or "(untitled)"
    return Document(
        title,
        PICTURE_SUBTITLE,
        [Title(title, PICTURE_SUBTITLE), Picture(shown.picture, title, page=True)],
    )


# ---------------------------------------------------------------- record

#: The marks markdown_sheet sets a styled cell or paragraph in, longest
#: first, so bold is never read as italic.
_STYLES = (("**", "bold"), ("~~", "struck"), ("*", "italic"))
#: A table's cell bars, those escaped in its words left alone.
_BAR = re.compile(r"(?<!\\)\|")
#: A Virtue or Flaw: its name, its tier and category, its summary.
_ENTRY = re.compile(r"^- \*\*(.+?)\*\*(?: \((.*?)\))?(?:: (.*))?$")


#: Marks inside words, which paper sets plain: bold, struck, then italic.
_INNER = (
    re.compile(r"\*\*(.+?)\*\*"),
    re.compile(r"~~(.+?)~~"),
    re.compile(r"\*(.+?)\*"),
)


def _unmarked(words: str) -> str:
    """Words with the marks inside them taken off."""
    for marks in _INNER:
        words = marks.sub(r"\1", words)
    return words


def _styled(words: str) -> tuple[str, str]:
    """Words and the style their marks set them all in ("" for none, or
    for words only partly marked: those come out plain)."""
    for mark, style in _STYLES:
        size = len(mark)
        inner = words[size:-size]
        if (
            len(words) > 2 * size
            and words.startswith(mark)
            and words.endswith(mark)
            and mark[0] not in inner
        ):
            return inner, style
    return _unmarked(words), ""


#: The narrowest share of a table's width a column of a record copy gets.
NARROWEST = 0.08


def _widths(header: list[str], rows: list[list[str]]) -> list[float]:
    """Each column's share of the width, by the longest words in it (the
    copy keeps no widths), none narrower than NARROWEST."""
    longest = [
        max([len(header[c]), *(len(row[c]) for row in rows if c < len(row))], default=1)
        or 1
        for c in range(len(header))
    ]
    shares = [max(NARROWEST, n / sum(longest)) for n in longest]
    return [share / sum(shares) for share in shares]


def _cells(line: str) -> list[str]:
    inside = line.strip().removeprefix("|").removesuffix("|")
    return [cell.strip().replace("\\|", "|") for cell in _BAR.split(inside)]


def _table(lines: list[str]) -> Block:
    """A GitHub table read back: a header of blanks over bold labels is a
    sheet's facts; a row of a bold name and blanks names the group of the
    rows under it."""
    header, rows = _cells(lines[0]), [_cells(line) for line in lines[2:]]
    if not any(header) and len(header) == 2:
        pairs = [(_styled(label)[0], value) for label, value in rows]
        return Facts(tuple(pairs))
    groups: list[tuple[int, str]] = []
    kept: list[tuple[Cell, ...]] = []
    for row in rows:
        first, style = _styled(row[0])
        if len(row) > 1 and style == "bold" and not any(row[1:]):
            groups.append((len(kept), first))
            continue
        kept.append(tuple(Cell(*_styled(cell)) for cell in row))
    widths = _widths(header, rows)
    return Table(
        tuple(Column(t, w) for t, w in zip(header, widths, strict=True)),
        tuple(kept),
        tuple(groups),
    )


def _entries(lines: list[str]) -> list[Block]:
    found: list[Block] = []
    for line in lines:
        match = _ENTRY.match(line)
        if match is None:
            found.append(Paragraph(_unmarked(line.removeprefix("- "))))
            continue
        name, note, summary = match.groups()
        found.append(Entry(name, note or "", summary or "", run_in=True))
    return found


def _part(part: str) -> list[Block]:
    """One part of the Markdown (the words between blank lines) as blocks."""
    lines = part.split("\n")
    if all(line.startswith("|") for line in lines) and len(lines) >= 2:
        return [_table(lines)]
    if all(line.startswith("- ") for line in lines):
        return _entries(lines)
    heading = re.match(r"^(#{2,6}) (.*)$", part)
    if heading is not None:
        return [Heading(heading.group(2), 1 if len(heading.group(1)) == 2 else 2)]
    return [Paragraph(*_styled(part))]


def record_document(shown: Shown) -> Document:
    """A record's copy, read back from the Markdown it was frozen as: its
    own title and the line under it (the Show's title when it has none),
    then each part as the block it was written from. An italic line
    straight under the title is read as that line: Markdown writes both
    alike, and every record's sheet has one."""
    parts = [p.strip() for p in shown.text.split("\n\n") if p.strip()]
    title = Title(shown.title.strip() or "(untitled)", RECORD_SUBTITLE)
    if parts and parts[0].startswith("# "):
        name = parts.pop(0).removeprefix("# ").strip()
        subtitle = ""
        if parts and _styled(parts[0])[1] == "italic":
            subtitle = _styled(parts.pop(0))[0]
        title = Title(name, subtitle)
    blocks: list[Block] = [title]
    for part in parts:
        blocks += _part(part)
    return Document(
        shown.title.strip() or title.name, title.subtitle or RECORD_SUBTITLE, blocks
    )


# ---------------------------------------------------------------- registry

#: Each kind of Handout's printed pages, by what its copy holds.
LAYOUTS: dict[str, Callable[[Shown], Document]] = {
    WRITTEN: written_document,
    RECORD: record_document,
    PICTURE: picture_document,
}


def document(shown: Shown) -> Document:
    """The printed pages of the Handout whose copy is `shown`."""
    return LAYOUTS[kind_of(shown)](shown)
