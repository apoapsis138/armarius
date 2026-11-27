"""A catalog entry read in full: when an entry is too long for a details
panel or an inspector, and the page it is read on instead.

A long entry's panel shows its summary; Read in full opens the whole of it
in the reading window a shown Handout opens in (handout_layout.Reading),
its text read into blocks by the one parser (handout_markup.blocks), so a
paragraph, a bold heading line and a list are drawn as each front-end
draws a Handout's.

Pattern: Interpreter, reused: the Handout's block parser reads the entry's
text, and each front-end's reading window draws it (the Bridge of
handout_layout). The long rule is a plain function and a constant."""

from __future__ import annotations

from dataclasses import replace

from . import handout_layout as layout
from . import handout_markup as markup
from .markup import escape
from .models import VELLUM

#: An entry whose description is longer than this, in characters, is long:
#: its panel shows the summary, and Read in full shows the rest.
LONG = 750

#: The line a long entry's panel ends its summary with (markup); a
#: front-end can give its own, naming its key or button.
READ_HINT = "[dim]A long entry: Read in full shows all of it.[/]"

#: Read in full's title, its help page, and what it says with no long
#: entry chosen.
READ_TITLE = "Read in full"
READ_HELP = "read-in-full"
READ_REFUSED = "Choose a long entry in its list first."


def is_long(description: str) -> bool:
    """Whether an entry with `description` is too long for a panel: past
    LONG characters, or holding a table, which only the reading page has
    room for."""
    if len(description) > LONG:
        return True
    return "|" in description and any(
        block.kind == markup.TABLE for block in markup.blocks(description, tables=True)
    )


def whole_text(description: str) -> str:
    """An entry's whole text (markup) where there is no reading page to
    open: each table's rows as lines of words, its cells set apart by a
    dot, the header first."""
    parts: list[str] = []
    for block in markup.blocks(description, tables=True):
        if block.kind == markup.TABLE:
            parts.append("\n".join(" · ".join(row) for row in block.rows))
        else:
            parts.append(block.text)
    return "\n\n".join(parts)


def panel_text(description: str, summary: str) -> str:
    """What a long entry's panel shows of it (markup): its summary, or with
    none its text without its tables, which only the reading page draws."""
    if summary.strip():
        return escape(" ".join(summary.split()))
    return "\n\n".join(
        block.text
        for block in markup.blocks(description, tables=True)
        if block.kind != markup.TABLE
    )


def short_view(description: str, summary: str) -> str:
    """What a panel or a picker's preview shows of an entry's text
    (markup): a long one's panel_text, a short one's whole_text."""
    if is_long(description):
        return panel_text(description, summary)
    return whole_text(description)


def _line(words: str, tag: str = "") -> str:
    """`words` on one line in italics, under a Handout tag if given (so a
    line with no tag never opens on one); "" for none."""
    words = " ".join(words.split())
    if not words:
        return ""
    return f"[{tag}] *{words}*" if tag else f"*{words}*"


def reading(
    title: str,
    kind: str,
    category: str,
    summary: str,
    description: str,
    source: str,
    help_id: str = "",
) -> layout.Reading:
    """The entry titled `title` laid out to read in full: on vellum named
    for its `kind` (Minor Virtue), its `category` centred under the title,
    its `summary` in italics as the lead, then its `description`, and its
    `source` at the foot; F1 opens `help_id`. Brackets are shown as
    written; the description may lay itself out as a Handout's text does
    (paragraphs, **bold**, lists, a Handout's tags), and hold pipe tables."""
    parts = [
        _line(category, "centre"),
        _line(summary),
        description,
        _line(f"Source: {source}" if source.strip() else "", "right"),
    ]
    text = "\n\n".join(part for part in parts if part.strip())
    laid = layout.lay_out(title, VELLUM, text, tables=True)
    page = replace(laid.stationery, name="catalog-entry", label=kind)
    return layout.Reading(replace(laid, stationery=page), help_id=help_id)
