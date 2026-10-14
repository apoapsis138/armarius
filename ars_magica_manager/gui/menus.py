"""The window's New and More menus, beside the trail: the desktop's
equivalent of the terminal's n and m keys, and of d on the record itself.

Each page offers what menu_forms (and so actions.available) offers there:
New what can be made from it, More the commands that apply anywhere on the
page, except those a record's page offers itself (menu_forms.ON_THE_PAGE:
its Manage chapter, with Delete, and its mode toggle) and those
menu_forms.PLACES sets out on the page itself: the saga page's row of
gilt buttons, and New Character and New Laboratory at the head of a
covenant's People and Laboratories. A menu with nothing in it isn't
shown. Choosing an entry runs its steps through the window,
which then shows where the change leaves the reader: a new record's page,
the page above a deleted one, or the same page again.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QMenu, QPushButton, QWidget

from .. import menu_forms
from ..commands import Command
from ..menu_forms import Page
from ..models import Saga
from . import pictures
from .markup_html import plain
from .themes import Palette
from .widgets import GiltButton

#: Runs a command, then (once its last step is answered) `then` instead
#: of drawing the page again.
RunThen = Callable[[Command, Callable[[], None] | None], None]

#: A page's own buttons at a spot on it (menu_forms.PAGE, or a
#: chapter's name), from the window (placed_buttons).
ButtonsAt = Callable[[str], list[QPushButton]]

#: Where a New entry's record is listed, to find the one it made.
_MADE: dict[str, Callable[[Saga], list[str]]] = {
    "create_covenant": lambda saga: [c.id for c in saga.covenants],
    "create_character": lambda saga: [c.id for c in saga.characters],
    "create_laboratory": lambda saga: [lab.id for lab in saga.laboratories],
    "create_familiar": lambda saga: [f.id for f in saga.familiars],
}


def menu_button(words: str, concept: str, p: Palette) -> QPushButton:
    button = QPushButton(pictures.icon(concept, p["label"]), f" {words}")
    button.setObjectName("menu")
    button.setFlat(True)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    return button


def _choose(
    page: Page, action: str, run: RunThen, show: Callable[[str, str], None]
) -> Callable[[], None]:
    """What choosing `action` on `page` does: run its steps, then show
    the record a New entry made (or the page again)."""
    listed = _MADE.get(action)
    if listed is None:
        return lambda: run(menu_forms.command(page, action), None)
    saga = page.saga

    def made() -> None:
        before = set(listed(saga))

        def then() -> None:
            fresh = [i for i in listed(saga) if i not in before]
            if fresh:
                show(action, fresh[-1])

        run(menu_forms.command(page, action), then)

    return made


def placed_buttons(
    page: Page | None,
    spot: str,
    p: Palette,
    run: RunThen,
    show: Callable[[str, str], None],
) -> list[QPushButton]:
    """The page's own buttons at `spot` (menu_forms.PAGE, or a chapter's
    name), as menu_forms.PLACES sets them out."""
    if page is None:
        return []
    return [
        GiltButton(plain(item.label), p, _choose(page, item.action, run, show))
        for item in menu_forms.placed(page, spot)
    ]


def button_row(buttons: list[QPushButton]) -> QWidget | None:
    """`buttons` side by side from the left, or None for none."""
    if not buttons:
        return None
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 4, 0, 4)
    row.setSpacing(10)
    for button in buttons:
        row.addWidget(button)
    row.addStretch(1)
    return box


def menu_buttons(
    page: Page | None,
    p: Palette,
    run: RunThen,
    show: Callable[[str, str], None],
) -> list[QPushButton]:
    """The New and More buttons for `page` (none for no page, or a menu
    with nothing in it): what the page offers that it doesn't set out
    itself (menu_forms.PLACES, ON_THE_PAGE). `show(action, id)` opens
    what a New entry made."""
    if page is None:
        return []
    buttons: list[QPushButton] = []
    for words, concept, items in (
        ("New", "new", menu_forms.new_items(page)),
        ("More", "more", menu_forms.more_items(page)),
    ):
        entries = [
            item
            for item in items
            if item.action not in menu_forms.ON_THE_PAGE
            and menu_forms.in_menu(page, item, words)
        ]
        if not entries:
            continue
        button = menu_button(words, concept, p)
        menu = QMenu(button)
        for item in entries:
            action = menu.addAction(plain(item.label))
            action.setData(item.action)
            go = _choose(page, item.action, run, show)
            action.triggered.connect(lambda _checked=False, go=go: go())
        button.setMenu(menu)
        buttons.append(button)
    return buttons
