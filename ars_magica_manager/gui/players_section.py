"""The Players section of the saga page's Saga Management: everyone who
may sign in, their role, whom they play and whether they can join from a
Remote seat, with Add, Edit and Delete (the core's SectionOps) and Issue
Invite on the chosen row (it opens Host for Players to show the Invite).
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QWidget

from .. import players as pl
from .. import section_verbs
from ..models import Saga
from ..sections import PLAYERS_SECTION
from ..sheets import saga_content as scs
from .character_sheet import section
from .editing import Chooser, Run, choose_rows, verb_buttons
from .themes import Palette
from .widgets import cells_table, edit_button, serif, text

Inspect = Callable[[str, str, str], None]


def players_section(
    saga: Saga,
    p: Palette,
    run: Run,
    inspect: Inspect,
    invite: Callable[[str], None],
) -> QWidget:
    """The Players list and its buttons; choosing a row shows them in the
    inspector. `invite` issues an Invite to the player of that id."""
    chooser = Chooser()
    table = scs.players_table(saga, seats=True)
    rows = cells_table(
        table.columns,
        table.rows,
        p,
        lambda row: inspect(
            saga.players[row].name,
            pl.ROLE_LABELS.get(saga.players[row].role, ""),
            pl.detail_text(saga, saga.players[row]),
        ),
    )
    choose_rows(rows, chooser)

    def issue() -> None:
        row = chooser.row(len(saga.players))
        if row is not None:
            invite(saga.players[row].id)

    buttons = verb_buttons(
        section_verbs.ops_of(saga, saga)[PLAYERS_SECTION], chooser, run, p
    )
    if buttons and saga.players:  # not on a copy that may not change them
        buttons.append(edit_button("Issue Invite", p, issue, "players"))
    return section(
        f"Players ({len(saga.players)})",
        p,
        rows if saga.players else text("None yet.", p["dim"], serif(12.5, italic=True)),
        buttons=buttons,
    )
