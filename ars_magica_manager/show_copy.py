"""A Show's copy of a record (shows.py): its printed sheet in the Player
copy, as Markdown (markdown_sheet), with the Secrets the storyguide ticked.

Pattern: Protection Proxy. The sheet is built while viewing reads as the
table (print_records.document), so it holds no unrevealed Secret and no
private note, and every record it names it names as the players know it
(viewing.name_of): the same copy Print to PDF and Export as Markdown
give. The ticked Secrets reach it as if revealed this season, on a copy of
the record; the record itself is left as it is."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from . import markdown_sheet, print_records, viewing
from .models import Saga


def player_copy(saga: Saga, record: Any, ticked: tuple[int, ...] = ()) -> str:
    """`record`'s sheet as the players read it, with its Secrets at the
    places `ticked`, as Markdown. KeyError for a record with no printed
    sheet (shows.SHOWABLE lists those that have)."""
    kind = print_records.kind_of(record)
    if kind is None:
        raise KeyError(type(record).__name__)
    shown = _with_ticked(saga, record, set(ticked)) if ticked else record
    doc = print_records.document(saga, kind, shown, viewer=viewing.TABLE_VIEWER)
    return markdown_sheet.render(doc)


def _with_ticked(saga: Saga, record: Any, ticked: set[int]) -> Any:
    """A copy of `record` whose ticked Secrets read as revealed now."""
    return replace(
        record,
        secrets=[
            replace(
                secret,
                revealed_year=saga.current_year,
                revealed_season=saga.current_season,
            )
            if row in ticked and not secret.revealed
            else secret
            for row, secret in enumerate(record.secrets)
        ],
    )
