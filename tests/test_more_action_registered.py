"""A More action is registered in several places; this names, in one
failure, every place a new action is still missing, so adding one is one
test run rather than one per registry.

Where a More action lives (each also checked on its own elsewhere):

* `actions.MORE_MENU`: its letter and label (the list this walks);
* how it runs: a terminal handler (`WorkspaceScreen.action_<name>`, or
  `base._MENU_HANDLERS`), else the core's first step in
  `forms/menu._COMMANDS` and what it redraws in `forms/menu_refresh.REFRESH`;
* where the desktop shows it: `forms/menu.PLACES`, `ON_THE_PAGE` or
  `NOT_ON_PAGES`;
* on a character's page: its book in `action_books.ACTION_BOOKS` or
  `NO_BOOK`;
* who may run it, when not every storyguide action: viewing's
  `LOOKING_ACTIONS` (players too), `STORYGUIDE_ONLY_ACTIONS` or
  `HOST_ONLY_ACTIONS`; and where it is offered: `actions.MORE_SECTIONS`,
  `_RECORD_RULES` or `_SECTION_RULES`. Neither is required, so neither is
  checked here."""

from ars_magica_manager import action_books, actions
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import menu_refresh
from ars_magica_manager.tui.screens.workspace import base
from ars_magica_manager.tui.screens.workspace.screen import WorkspaceScreen


def _missing(item: actions.MenuItem) -> list[str]:
    action = item.action
    found: list[str] = []
    handler = base._MENU_HANDLERS.get(action, f"action_{action}")
    if not callable(getattr(WorkspaceScreen, handler, None)):
        if action not in menu_forms._COMMANDS:
            found.append("forms/menu._COMMANDS")
        if action not in menu_refresh.REFRESH:
            found.append("forms/menu_refresh.REFRESH")
    placed = (
        action in menu_forms.PLACES
        or action in menu_forms.ON_THE_PAGE
        or action in menu_forms.NOT_ON_PAGES
    )
    if not placed:
        found.append("forms/menu.PLACES (or ON_THE_PAGE / NOT_ON_PAGES)")
    on_character = any(
        kind == NodeKind.CHARACTER for kind, _ in menu_forms.PLACES.get(action, ())
    )
    booked = action in action_books.ACTION_BOOKS or action in action_books.NO_BOOK
    if on_character and not booked:
        found.append("action_books.ACTION_BOOKS (or NO_BOOK)")
    return found


def test_every_more_action_is_registered_everywhere_it_must_be():
    gaps = {
        item.action: missing
        for item in actions.MORE_MENU
        if (missing := _missing(item))
    }
    assert not gaps, "\n".join(
        f"{action}: add to {', '.join(where)}" for action, where in gaps.items()
    )
