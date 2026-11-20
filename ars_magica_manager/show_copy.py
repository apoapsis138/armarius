"""A Show's copy of a record (shows.py): its printed sheet in the Player
copy, as Markdown (markdown_sheet), with the name of every record the
players don't know of taken out, as a page leaves them off.

Pattern: Protection Proxy. The sheet is built while viewing reads as the
table (print_records.document), so it holds no unrevealed Secret and no
private note; the names its facts write as plain words (a character's
covenant) are taken out here."""

from __future__ import annotations

import re
from typing import Any

from . import markdown_sheet, print_records, viewing
from .models import Saga

#: What stands where an unknown record's name was.
UNKNOWN = "(unknown)"


def player_copy(saga: Saga, record: Any) -> str:
    """`record`'s sheet as the players read it, as Markdown. KeyError for
    a record with no printed sheet (shows.SHOWABLE lists those that have)."""
    kind = print_records.kind_of(record)
    if kind is None:
        raise KeyError(type(record).__name__)
    doc = print_records.document(saga, kind, record, viewer=viewing.TABLE_VIEWER)
    return scrubbed(
        markdown_sheet.render(doc), viewing.unknown_names(saga) - {record.name}
    )


def scrubbed(text: str, names: set[str]) -> str:
    """`text` with each of `names` written as a whole word taken out,
    longest first, so a name inside another goes with it."""
    for name in sorted((n for n in names if n), key=len, reverse=True):
        text = re.sub(rf"(?<!\w){re.escape(name)}(?!\w)", UNKNOWN, text)
    return text
