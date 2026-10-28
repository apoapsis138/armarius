"""The desktop's Ahead: what is coming, a season to a column and a card
to an entry (ahead.py works it out), with the storyguide's own calendar
entries added, edited and deleted here (forms/ahead.py). The saga's
Seasons page shows the whole saga, with a chip per kind of entry; a
covenant's Seasons chapter only what concerns it."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QGridLayout,
    QVBoxLayout,
    QWidget,
)

from .. import ahead
from ..commands import Act
from ..forms import ahead as ahead_forms
from ..forms import hunting as hunting_forms
from ..forms import travel as travel_forms
from ..models import SEASONS, Covenant, Saga, season_order
from .character_sheet import section
from .editing import Chooser, Run, verb_buttons
from .medallions import Medallion, beside
from .themes import Palette
from .widgets import ClickableCard, chip_row, edit_button, serif, text

#: Seasons shown across: a year to a row.
ACROSS = len(SEASONS)

Inspect = Callable[[str, str, str], None]


def _chips(saga: Saga, p: Palette, run: Run) -> QWidget:
    """Show: a chip per kind of entry, the one shown lit."""

    def pick(show: str) -> Callable[[], None]:
        def apply() -> None:
            saga.ahead_show = show

        return lambda: run(Act(apply))

    return chip_row(
        "Show",
        [(show, show == saga.ahead_show, pick(show)) for show in ahead.SHOWS],
        p,
    )


def _edge(p: Palette, entry: ahead.Entry) -> str | None:
    if entry.show == ahead.THREATS:
        return p["text-warning"]
    if entry.show in (ahead.TRIBUNAL, ahead.EVERYTHING):
        return p["heading"]
    return None


def ahead_section(
    saga: Saga,
    p: Palette,
    run: Run,
    inspect: Inspect,
    covenant: Covenant | None = None,
) -> QWidget:
    """Ahead (for `covenant`, or the whole saga with its chips): each
    season's entries as cards, Add, Edit and Delete for the storyguide's
    own, and the span."""
    found = ahead.shown(saga, covenant)
    chooser = Chooser()
    cards: list[ClickableCard] = []
    body = QWidget()
    column = QVBoxLayout(body)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(8)
    if covenant is None:
        column.addWidget(_chips(saga, p, run))
    grid_box = QWidget()
    grid = QGridLayout(grid_box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(14)
    grid.setVerticalSpacing(12)
    row_index = 0
    first_year = saga.current_year
    for year, season, entries in ahead.by_season(found):
        cell = QWidget()
        cell_column = QVBoxLayout(cell)
        cell_column.setContentsMargins(0, 0, 0, 0)
        cell_column.setSpacing(6)
        now = season_order(season=season, year=year) == ahead.now(saga)
        cell_column.addWidget(
            beside(
                Medallion(saga, season, year, p, radius=16, now=now),
                text(
                    ahead.season_text(saga, year, season),
                    p["heading"] if now else p["label"],
                    serif(12, bold=now),
                ),
                gap=4,
            )
        )
        for entry in entries:
            card = ClickableCard(p, pad=8, edge=_edge(p, entry))
            card.column.addWidget(
                text(entry.title, p["foreground"], serif(12.5), wrap=True)
            )
            index = row_index
            row_index += 1

            def clicked(entry: ahead.Entry = entry, index: int = index) -> None:
                chooser.choose(index)
                inspect(
                    entry.title,
                    f"{entry.season} {entry.year} · {entry.show}",
                    ahead.detail_text(saga, entry),
                )

            card.clicked = clicked
            cards.append(card)
            cell_column.addWidget(card)
        cell_column.addStretch(1)
        # A year to a row and a season to a column, as a calendar.
        grid.addWidget(cell, year - first_year, SEASONS.index(season))
    for column_index in range(ACROSS):
        grid.setColumnStretch(column_index, 1)

    def outline(chosen: int | None) -> None:
        for index, card in enumerate(cards):
            card.set_chosen(index == chosen)

    chooser.listeners.append(outline)
    if found:
        column.addWidget(grid_box)
    else:
        column.addWidget(
            text(
                "Nothing coming in this span: add your own.",
                p["dim"],
                serif(12.5, italic=True),
            )
        )
    buttons = verb_buttons(ahead_forms.ahead_ops(saga, covenant), chooser, run, p)
    # Travel, the calculator: it records nothing.
    buttons.append(
        edit_button(
            "Travel", p, lambda: run(travel_forms.travel(saga, covenant)), "more"
        )
    )
    # The hunt and Area Lore on the road.
    buttons += [
        edit_button(
            hunting_forms.HUNT_TITLE,
            p,
            lambda: run(hunting_forms.hunt_on_journey(saga, covenant)),
            "more",
        ),
        edit_button(
            hunting_forms.AREA_LORE_TITLE,
            p,
            lambda: run(hunting_forms.area_lore_on_journey(saga, covenant)),
            "more",
        ),
    ]
    return section(
        ahead.title(saga, covenant),
        p,
        body,
        edits={"Looking ahead": lambda: run(ahead_forms.looking_form(saga))},
        buttons=buttons,
    )
