"""The window's New and More menus, beside the trail: the desktop's
equivalent of the terminal's n and m keys, and of d on the record itself.

Each page offers what menu_forms (and so actions.available) offers there:
New what can be made from it, More the commands that apply anywhere on the
page, except those a record's page offers itself (menu_forms.ON_THE_PAGE:
its Manage chapter, with Delete, and its mode toggle). A menu with nothing
in it isn't shown. Choosing an entry runs its steps through the window,
which then shows where the change leaves the reader: a new record's page,
the page above a deleted one, or the same page again.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu, QPushButton

from .. import menu_forms
from ..actions import NodeKind
from ..commands import Command
from ..menu_forms import Page
from ..models import Saga
from . import pictures
from .markup_html import plain
from .themes import Palette

#: Runs a command, then (once its last step is answered) `then` instead
#: of drawing the page again.
RunThen = Callable[[Command, Callable[[], None] | None], None]

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


def menu_buttons(
    page: Page | None,
    p: Palette,
    run: RunThen,
    show: Callable[[str, str], None],
) -> list[QPushButton]:
    """The New and More buttons for `page` (none for no page, or a menu
    with nothing in it). `show(action, id)` opens what a New entry made."""
    if page is None:
        return []
    saga = page.saga
    buttons: list[QPushButton] = []

    new = menu_forms.new_items(page)
    if new:
        button = menu_button("New", "new", p)
        menu = QMenu(button)
        for item in new:
            action = menu.addAction(plain(item.label))
            action.setData(item.action)

            def made(name: str = item.action) -> None:
                listed = _MADE[name]
                before = set(listed(saga))

                def then() -> None:
                    fresh = [i for i in listed(saga) if i not in before]
                    if fresh:
                        show(name, fresh[-1])

                run(menu_forms.command(page, name), then)

            action.triggered.connect(lambda _checked=False, go=made: go())
        button.setMenu(menu)
        buttons.append(button)

    more: list[tuple[str, str, Callable[[], None]]] = []
    if page.kind == NodeKind.SAGA:
        more.append(
            (
                "Edit Saga",
                "edit_saga",
                lambda: run(menu_forms.creation_forms.edit_saga_form(saga), None),
            )
        )
    for item in menu_forms.more_items(page):
        if item.action in menu_forms.ON_THE_PAGE:
            continue
        more.append(
            (
                item.label,
                item.action,
                lambda name=item.action: run(menu_forms.command(page, name), None),
            )
        )
    if more:
        button = menu_button("More", "more", p)
        menu = QMenu(button)
        for label, name, go in more:
            action = menu.addAction(plain(label))
            action.setData(name)
            action.triggered.connect(lambda _checked=False, go=go: go())
        button.setMenu(menu)
        buttons.append(button)
    return buttons
