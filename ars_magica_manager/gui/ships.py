"""The desktop covenant's Ships, the first section of its Possessions:
each ship ruled off on the page as a ledger entry (a § rubric, her name
in small capitals, what she is and her cargo, her damage as a badge, her
quality, crew and captain, and her note), with Add, Edit, Delete, Stress
Check and Ship Combat on the chosen one; the chosen ship shows in the
inspector. What it says comes from the core (ships.py, forms/ships.py),
as the terminal's Ships list does.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from .. import ships as ship_text
from ..forms import possession as possession_forms
from ..forms import ship_build
from ..forms import ships as ship_forms
from ..models import Covenant, Possession, Saga
from ..possessions import KIND_TITLES
from ..rules import ships as rules
from .character_sheet import TextBlock, section
from .editing import Chooser, RowVerb, Run, verb_buttons
from .ruled_entry import RuledEntry
from .themes import Palette
from .widgets import badge, edit_button, serif, text

#: Inspect: the inspector's title, the line under it, and its markup.
Inspect = Callable[[str, str, str], None]
SECTION_ID = "section-pos-ship"


def _quiet(block: TextBlock) -> TextBlock:
    """A text block that lets clicks through to the entry it sits in."""
    block.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    block.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    return block


class ShipEntry(RuledEntry):
    """One ship ruled off on the page."""

    def __init__(self, shown: ship_text.Card, p: Palette) -> None:
        super().__init__(p)
        row = self.ruled_row()
        rubric = text("§", p["heading"], serif(20, bold=True))
        rubric.setFixedWidth(28)
        rubric.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        row.addWidget(rubric, 0, Qt.AlignmentFlag.AlignTop)
        column = QVBoxLayout()
        column.setSpacing(3)
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(
            text(shown.title, p["heading"], serif(12.5, bold=True, caps=True))
        )
        top.addWidget(text(shown.meta, p["label"], serif(11, italic=True)))
        top.addStretch(1)
        top.addWidget(badge(shown.badge, p[shown.tone], p))
        column.addLayout(top)
        body = text(shown.body, p["foreground"], serif(13.5))
        body.setWordWrap(True)
        column.addWidget(body)
        if shown.note:
            note = _quiet(TextBlock(f"[i]{shown.note}[/]", p))
            note.setFont(serif(12, italic=True))
            column.addWidget(note)
        row.addLayout(column, 1)


def _chooses(entries: Sequence[ShipEntry], chooser: Chooser) -> None:
    """Clicking entry i chooses ship i; the chosen one is bracketed."""
    for index, entry in enumerate(entries):
        before = entry.clicked

        def clicked(index: int = index, before: Callable[[], None] = before) -> None:
            chooser.choose(index)
            before()

        entry.clicked = clicked

    def mark(chosen: int | None) -> None:
        for index, entry in enumerate(entries):
            entry.set_chosen(index == chosen)

    chooser.listeners.append(mark)


def ships_section(
    saga: Saga, covenant: Covenant, p: Palette, run: Run, inspect: Inspect
) -> QWidget:
    """The covenant's ships, with Add, Edit, Delete, Stress Check and
    Ship Combat on the chosen one."""
    chooser = Chooser()
    body = QWidget()
    stack = QVBoxLayout(body)
    stack.setContentsMargins(0, 0, 0, 0)
    stack.setSpacing(2)
    listed: list[Possession] = rules.ships_of(covenant)
    entries: list[ShipEntry] = []
    for record in listed:
        entry = ShipEntry(ship_text.card(record, saga), p)

        def show(record: Possession = record) -> None:
            # Her kind and size are the inspector's own line under her name.
            lines = ship_text.detail_lines(record, saga)[1:]
            if record.description.strip():
                lines += ["", f"[i]{record.description.strip()}[/]"]
            lines.append(ship_text.STRESS_NOTE)
            inspect(record.name, ship_text.subtitle(record), "\n".join(lines))

        entry.clicked = show
        entries.append(entry)
        stack.addWidget(entry)
    _chooses(entries, chooser)
    if not listed:
        stack.addWidget(text("None recorded.", p["dim"], serif(12.5, italic=True)))

    def whole(row: int) -> bool:
        ships = rules.ships_of(covenant)
        return row < len(ships) and not rules.lost(rules.ship_of(ships[row]))

    more: list[RowVerb] = [
        (
            "Stress Check",
            "threat",
            lambda row: ship_forms.stress_check(saga, covenant, row),
            whole,
        ),
        (
            "Ship Combat",
            "combat",
            lambda row: ship_forms.ship_combat(saga, covenant, row),
            whole,
        ),
        (
            "Sunk or Taken",
            "threat",
            lambda row: ship_forms.mark_fate(saga, covenant, row),
            lambda row: row < len(rules.ships_of(covenant)),
        ),
    ]
    widget = section(
        f"{KIND_TITLES['ship']} ({len(listed)})",
        p,
        body,
        buttons=[
            *verb_buttons(
                possession_forms.possession_ops(saga, covenant, "ship"),
                chooser,
                run,
                p,
                more=more,
            ),
            edit_button(
                ship_build.TITLE,
                p,
                lambda: run(ship_build.build_form(saga, covenant)),
                "new",
            ),
        ],
    )
    widget.setObjectName(SECTION_ID)
    return widget
