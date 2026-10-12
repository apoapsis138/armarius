"""The Textual front-end has a handler for everything actions.py says can be
done: every More and New menu entry, and every verb of every sheet
section. Menu handlers are looked up by name, so a renamed method would
only fail when someone picked the entry; and a section whose verbs and
handlers disagreed would offer a key that does nothing, or hide one that
works."""

import pytest

from ars_magica_manager import actions
from ars_magica_manager.models import Saga
from ars_magica_manager.screens.workspace import base
from ars_magica_manager.screens.workspace.screen import WorkspaceScreen


def _handler_name(item: actions.MenuItem) -> str:
    return base._MENU_HANDLERS.get(item.action, f"action_{item.action}")


@pytest.mark.parametrize(
    "item",
    actions.MORE_MENU + actions.NEW_MENU,
    ids=lambda item: f"{item.action}-{_handler_name(item)}",
)
def test_every_menu_item_has_its_handler(item):
    handler = getattr(WorkspaceScreen, _handler_name(item), None)
    assert callable(handler)


def test_menu_handlers_name_only_menu_actions():
    menu_actions = {item.action for item in actions.MORE_MENU + actions.NEW_MENU}
    assert set(base._MENU_HANDLERS) <= menu_actions


def test_section_handlers_match_the_section_verbs():
    screen = WorkspaceScreen(Saga(id="saga1", name="Test"))
    handled = {
        section: frozenset(
            verb for verb in actions.VERBS if getattr(ops, verb) is not None
        )
        for section, ops in screen._section_ops.items()
    }
    assert handled == actions.SECTION_VERBS
