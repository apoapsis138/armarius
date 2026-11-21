"""A Show's copy of a record (shows.py): its printed sheet in the Player
copy, as Markdown (markdown_sheet).

Pattern: Protection Proxy. The sheet is built while viewing reads as the
table (print_records.document), so it holds no unrevealed Secret and no
private note, and every record it names it names as the players know it
(viewing.name_of): the same copy Print to PDF and Export as Markdown
give."""

from __future__ import annotations

from typing import Any

from . import markdown_sheet, print_records, viewing
from .models import Saga


def player_copy(saga: Saga, record: Any) -> str:
    """`record`'s sheet as the players read it, as Markdown. KeyError for
    a record with no printed sheet (shows.SHOWABLE lists those that have)."""
    kind = print_records.kind_of(record)
    if kind is None:
        raise KeyError(type(record).__name__)
    doc = print_records.document(saga, kind, record, viewer=viewing.TABLE_VIEWER)
    return markdown_sheet.render(doc)
