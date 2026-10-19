"""The desktop's Ahead: what is coming, a season to a column and a card
to an entry (ahead.py works it out), with the storyguide's own calendar
entries added, edited and deleted here (forms/ahead.py). The saga's
Seasons page shows the whole saga, with a chip per kind of entry; a
covenant's Seasons chapter only what concerns it."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import ahead
from ..commands import Act
from ..forms import ahead as ahead_forms
from ..models import SEASONS, Covenant, Saga
from .character_sheet import section
from .editing import Chooser, Run, verb_buttons
from .themes import Palette
from .widgets import ClickableCard, serif, text

#: Seasons shown across: a year to a row.
ACROSS = len(SEASONS)

Inspect = Callable[[str, str, str], None]


def _chips(saga: Saga, p: Palette, run: Run) -> QWidget:
    """Show: a chip per kind of entry, the one shown lit."""
    row = QWidget()
    line = QHBoxLayout(row)
    line.setContentsMargins(0, 0, 0, 0)
    line.setSpacing(6)
    line.addWidget(text("Show", p["label"], serif(11, italic=True)))
    for show in ahead.SHOWS:
        chip = QPushButton(show)
        chip.setObjectName("chip")
        chip.setCheckable(True)
        chip.setChecked(show == saga.ahead_show)
        chip.setCursor(Qt.CursorShape.PointingHandCursor)
        colour = p["heading"] if show == saga.ahead_show else p["label"]
        chip.setStyleSheet(
            f"color:{colour}; border:1px solid {colour}; border-radius:9px;"
            " padding:1px 10px; background:transparent"
        )

        def pick(_checked: bool = False, show: str = show) -> None:
            def apply() -> None:
                saga.ahead_show = show

            run(Act(apply))

        chip.clicked.connect(pick)
        line.addWidget(chip)
    line.addStretch(1)
    return row


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
        now = ahead.order(year, season) == ahead.now(saga)
        cell_column.addWidget(
            text(
                ahead.season_text(saga, year, season),
                p["heading"] if now else p["label"],
                serif(12, bold=now),
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
    return section(
        ahead.title(saga, covenant),
        p,
        body,
        edits={"Looking ahead": lambda: run(ahead_forms.looking_form(saga))},
        buttons=buttons,
    )
