"""A section's Add, Edit and Delete buttons on the desktop, and which
row Edit and Delete act on.

The buttons run a commands.SectionOps' steps through the window. The row
is the one last clicked in the section (a `Chooser`); with none clicked
yet, the only row there is. Edit and Delete stay greyed out until there
is a row to act on, as the terminal says "choose a row first".

Every step (a form, a list to choose from, a question) opens as a window
over the page, one after another when a button asks several things.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QModelIndex, QSortFilterProxyModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import giving
from ..commands import Act, Command, Go, SectionOps
from ..models import Saga
from ..references import Ref
from .themes import Palette
from .widgets import ClickableCard, edit_button

Run = Callable[[Command], None]

#: A further button acting on the chosen row: its words, its icon's
#: concept, its first step (for the row) and whether it can act on the
#: row (Instill an Effect only on a device with room for one).
RowVerb = tuple[str, str, Callable[[int], Command], Callable[[int], bool]]


def follower(run: Run) -> Callable[[Ref], None]:
    """What a link to a record does: open it, through the window's steps
    (a commands.Go)."""
    return lambda found: run(Act(lambda: Go(found)))


def give_verb(
    saga: Saga,
    kind: str,
    shown: giving.Holder,
    things: Callable[[], Sequence[object]],
) -> RowVerb:
    """Give: the chosen row's thing (row `i` is `things()[i]`, of
    giving's `kind`) to another record, offered while it can be given."""

    def gift(row: int) -> giving.Gift | None:
        listed = things()
        return (
            giving.gift(saga, kind, shown, listed[row]) if row < len(listed) else None
        )

    def can(row: int) -> bool:
        found = gift(row)
        return found is not None and giving.blocked(saga, *found) is None

    return ("Give", "give", lambda row: giving.give_gift(saga, gift(row)), can)


class Chooser:
    """The row of a section that Edit and Delete act on."""

    def __init__(self) -> None:
        self.index: int | None = None
        self.listeners: list[Callable[[int | None], None]] = []

    def choose(self, index: int | None) -> None:
        self.index = index
        for listener in self.listeners:
            listener(index)

    def row(self, count: int) -> int | None:
        """The chosen row, or the only one there is; None with nothing to
        act on."""
        if self.index is not None and self.index < count:
            return self.index
        return 0 if count == 1 else None


def verb_buttons(
    ops: SectionOps,
    chooser: Chooser,
    run: Run,
    p: Palette,
    *,
    nouns: tuple[str, str, str] = ("Add", "Edit", "Delete"),
    more: Sequence[RowVerb] = (),
) -> list[QPushButton]:
    """The section's buttons, for character_sheet.section(buttons=...):
    one per verb `ops` has, named `nouns` (Add, Edit, Delete), then the
    `more` that act on the chosen row. A verb with no row it could act on
    (an empty list, or Give with nobody to take any of it) isn't shown;
    one whose row isn't chosen yet is greyed out."""
    add, edit, remove = nouns
    buttons: list[QPushButton] = []
    if ops.add is not None:
        start = ops.add
        buttons.append(edit_button(add, p, lambda: run(start()), "add"))
    per_row: list[tuple[QPushButton, Callable[[int], bool]]] = []
    verbs: list[RowVerb] = [
        (words, concept, step, lambda _row: True)
        for words, concept, step in (
            (edit, "edit", ops.edit),
            (remove, "delete", ops.remove),
        )
        if step is not None
    ]
    for words, concept, step, allowed in [*verbs, *more]:

        def act(step: Callable[[int], Command] = step) -> None:
            row = chooser.row(len(ops.rows()))
            if row is not None:
                run(step(row))

        button = edit_button(words, p, act, concept)
        per_row.append((button, allowed))
        buttons.append(button)

    def refresh(_index: int | None = None) -> None:
        rows = ops.rows()
        row = chooser.row(len(rows))
        for button, allowed in per_row:
            verb = button.text().strip()
            # Nothing listed it could act on: not offered at all (a filter
            # that empties the list hides it until the filter changes).
            if not any(allowed(index) for index in range(len(rows))):
                button.setEnabled(False)
                button.hide()
                continue
            if button.isHidden() and button.parentWidget() is not None:
                button.show()
            if row is None:
                button.setEnabled(False)
                button.setToolTip("Choose a row first.")
            elif not allowed(row):
                button.setEnabled(False)
                button.setToolTip(f"Not for {rows[row]}.")
            else:
                button.setEnabled(True)
                button.setToolTip(f"{verb} {rows[row]}")

    chooser.listeners.append(refresh)
    refresh()
    return buttons


def choose_cards(cards: Sequence[ClickableCard], chooser: Chooser) -> None:
    """Clicking a card chooses its row (as well as what it did), and the
    chosen card is outlined."""
    for index, card in enumerate(cards):
        before = card.clicked

        def clicked(index: int = index, before: Callable[[], None] = before) -> None:
            chooser.choose(index)
            before()

        card.clicked = clicked

    def outline(chosen: int | None) -> None:
        for index, card in enumerate(cards):
            card.set_chosen(index == chosen)

    chooser.listeners.append(outline)


def choose_rows(
    view: QAbstractItemView,
    chooser: Chooser,
    to_row: Callable[[int], int | None] | None = None,
) -> None:
    """Choosing a row of a table or list view chooses it for the section;
    `to_row` maps the view's row to the section's (a sorted proxy's
    source row, or None for a heading row). A view with a
    QSortFilterProxyModel is mapped through it."""
    model = view.model()

    def current(index: QModelIndex, _previous: QModelIndex) -> None:
        if not index.isValid():
            chooser.choose(None)
            return
        row = index.row()
        if isinstance(model, QSortFilterProxyModel):
            row = model.mapToSource(index).row()
        chooser.choose(to_row(row) if to_row is not None else row)

    selection = view.selectionModel()
    if selection is not None:
        selection.currentChanged.connect(current)


class Section(QWidget):
    """A titled part of a chapter (character_sheet.section): its title row,
    then its body."""

    def __init__(self) -> None:
        super().__init__()
        self.column = QVBoxLayout(self)
        # Room above the title, so it sits apart from the section above.
        self.column.setContentsMargins(0, 10, 0, 0)
        self.column.setSpacing(6)
