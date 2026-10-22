"""The desktop's drawing of the saga's world pieces every record shares:
a section of rows with the core's Add, Edit and Delete, and a record's
Attitude, Favours and Links (world_forms)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from PySide6.QtWidgets import QWidget

from ..commands import SectionOps
from ..forms import go_to as go_to_forms
from ..forms import world as world_forms
from ..models import Saga
from ..tables import Table
from .character_sheet import section
from .editing import Chooser, RowVerb, Run, verb_buttons
from .themes import Palette
from .widgets import serif, table_view, text


def table_section(
    title: str,
    table: Table,
    ops: SectionOps,
    p: Palette,
    run: Run,
    *,
    empty: str = "None yet.",
    on_choose: Callable[[int], None] | None = None,
    more: Sequence[RowVerb] = (),
) -> QWidget:
    """`table` under `title`, with the core's Add, Edit and Delete (and
    `more`) acting on the row chosen."""
    chooser = Chooser()

    def choose(row: int) -> None:
        chooser.choose(row)
        if on_choose is not None:
            on_choose(row)

    body = (
        table_view(table, p, choose)
        if table.rows
        else text(empty, p["dim"], serif(12.5, italic=True))
    )
    return section(
        title, p, body, buttons=verb_buttons(ops, chooser, run, p, more=more)
    )


def relations(
    saga: Saga, record: Any, p: Palette, run: Run, *, attitude: bool = True
) -> list[QWidget]:
    """A world record's Attitude toward each player covenant, the favours
    owed and its links."""
    ops = world_forms.record_ops(saga, record)
    parts: list[QWidget] = []
    if attitude:
        parts.append(
            table_section(
                "Attitude",
                world_forms.attitude_table(saga, record),
                ops[world_forms.ATTITUDE_SECTION],
                p,
                run,
                empty="There is no player covenant to have an attitude toward.",
            )
        )
    parts += [
        table_section(
            f"Favours ({len(record.favours)})",
            world_forms.favour_table(record),
            ops[world_forms.FAVOURS_SECTION],
            p,
            run,
            empty="None owed.",
        ),
        table_section(
            f"Links ({len(record.links)})",
            world_forms.link_table(saga, record),
            ops[world_forms.LINKS_SECTION],
            p,
            run,
            empty="No links.",
            more=[
                (
                    "Open",
                    "open",
                    lambda row: go_to_forms.open_link(saga, record, row),
                    lambda row: go_to_forms.opens(saga, record, row),
                )
            ],
        ),
    ]
    return parts
