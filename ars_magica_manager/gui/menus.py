"""The desktop's equivalent of the terminal's n and m keys: each New and
More action the core offers on a page (menu_forms, and so
actions.available), set out where menu_forms.PLACES puts it, as a button
in a chapter or section or a New card at the end of the cards it adds to
(a Placer draws them). A record's page offers the rest itself
(menu_forms.ON_THE_PAGE: its Manage chapter, with Delete, and its mode
toggle). Choosing one runs its steps through the window, which then shows
where the change leaves the reader: a new record's page, or the same page
again.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtWidgets import QPushButton

from .. import menu_forms
from ..actions import MenuItem
from ..commands import Command
from ..menu_forms import Page
from ..models import Saga
from .markup_html import plain
from .themes import Palette
from .widgets import NewCard, edit_button

#: Runs a command, then (once its last step is answered) `then` instead
#: of drawing the page again.
RunThen = Callable[[Command, Callable[[], None] | None], None]

#: Where a New entry's record is listed, to find the one it made.
_MADE: dict[str, Callable[[Saga], list[str]]] = {
    "create_covenant": lambda saga: [c.id for c in saga.covenants],
    "found_covenant": lambda saga: [c.id for c in saga.covenants],
    "create_tribunal": lambda saga: [t.id for t in saga.tribunals],
    "create_neighbour": lambda saga: [n.id for n in saga.neighbours],
    "create_character": lambda saga: [c.id for c in saga.characters],
    "create_laboratory": lambda saga: [lab.id for lab in saga.laboratories],
    "create_familiar": lambda saga: [f.id for f in saga.familiars],
}


def _choose(
    page: Page,
    action: str,
    run: RunThen,
    show: Callable[[str, str], None],
    command: Command | None = None,
) -> Callable[[], None]:
    """What choosing `action` on `page` does: run its steps (`command`, or
    the action's own), then show the record a New entry made (or the page
    again)."""

    def steps() -> Command:
        return command if command is not None else menu_forms.command(page, action)

    listed = _MADE.get(action)
    if listed is None:
        return lambda: run(steps(), None)
    saga = page.saga

    def made() -> None:
        before = set(listed(saga))

        def then() -> None:
            fresh = [i for i in listed(saga) if i not in before]
            if fresh:
                show(action, fresh[-1])

        run(steps(), then)

    return made


#: The icon of each action a page sets out as a button.
ICONS: dict[str, str] = {
    "create_familiar": "familiar",
    "edit_saga": "edit",
    "import_data": "update",
    "set_date": "season",
    "lab_text_access": "lab_text",
    "perform_ritual": "magic",
    "research_bonuses": "library",
    "export_saga": "export",
    "export_pack": "export",
    "give_silver": "silver",
}

#: What each New card makes, as artwork.ICON_NAMES has it.
NEW_ICONS: dict[str, str] = {
    "create_covenant": "covenant",
    "create_tribunal": "tribunal",
    "create_neighbour": "region",
    "create_character": "character",
    "create_laboratory": "laboratory",
    "create_familiar": "familiar",
}


@dataclass(frozen=True)
class Placer:
    """The window's side of what a page sets out itself (menu_forms.
    PLACES): its buttons in a chapter or section, and the New card at the
    end of the cards a New action adds to."""

    page: Page | None
    p: Palette
    run: RunThen
    show: Callable[[str, str], None]

    def items(self, spot: str) -> list[MenuItem]:
        return [] if self.page is None else menu_forms.placed(self.page, spot)

    def placed_buttons(self, spot: str) -> list[tuple[MenuItem, QPushButton]]:
        """The actions at `spot`, each as a section button."""
        page = self.page
        if page is None:
            return []
        return [
            (
                item,
                edit_button(
                    plain(item.label),
                    self.p,
                    _choose(page, item.action, self.run, self.show),
                    ICONS.get(item.action, "edit"),
                ),
            )
            for item in self.items(spot)
        ]

    def buttons(self, spot: str) -> list[QPushButton]:
        return [button for _, button in self.placed_buttons(spot)]

    def new_card(
        self,
        spot: str,
        words: str | None = None,
        command: Command | None = None,
        hint: str = "",
    ) -> NewCard | None:
        """The New card at `spot` (its New action's own words and steps,
        or `words` and `command`), or None if nothing is made there."""
        page = self.page
        if page is None:
            return None
        item = next(
            (i for i in self.items(spot) if i.action in NEW_ICONS),
            None,
        )
        if item is None:
            return None
        return NewCard(
            words or plain(item.label),
            NEW_ICONS[item.action],
            self.p,
            _choose(page, item.action, self.run, self.show, command),
            hint,
        )
