"""The Textual front-end has a handler for everything actions.py says can be
done: every More and New menu entry, and every verb of every sheet
section. Menu handlers are looked up by name, so a renamed method would
only fail when someone picked the entry; and a section whose verbs and
handlers disagreed would offer a key that does nothing, or hide one that
works."""

import pytest

from ars_magica_manager import actions
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import menu_refresh
from ars_magica_manager.models import Saga
from ars_magica_manager.tui.screens.workspace import base
from ars_magica_manager.tui.screens.workspace.screen import WorkspaceScreen


def _handler_name(item: actions.MenuItem) -> str:
    return base._MENU_HANDLERS.get(item.action, f"action_{item.action}")


@pytest.mark.parametrize(
    "item",
    actions.MORE_MENU + actions.NEW_MENU,
    ids=lambda item: f"{item.action}-{_handler_name(item)}",
)
def test_every_menu_item_has_its_handler(item):
    """A handler of the terminal's own, or the core's first step for it and
    what it changes (menu_refresh), which the terminal runs itself."""
    handler = getattr(WorkspaceScreen, _handler_name(item), None)
    assert callable(handler) or (
        item.action in menu_refresh.REFRESH and item.action in menu_forms._COMMANDS
    )


def test_an_action_with_a_handler_of_its_own_is_not_also_in_the_registry():
    """One way to run an action: a handler, or the registry's entry."""
    both = [
        item.action
        for item in actions.MORE_MENU + actions.NEW_MENU
        if item.action in menu_refresh.REFRESH
        and callable(getattr(WorkspaceScreen, _handler_name(item), None))
    ]
    assert not both, both


def test_the_registry_names_only_actions_the_core_can_run():
    assert set(menu_refresh.REFRESH) <= set(menu_forms._COMMANDS)
    on_menus = {item.action for item in actions.MORE_MENU + actions.NEW_MENU}
    assert set(menu_refresh.REFRESH) <= on_menus


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
