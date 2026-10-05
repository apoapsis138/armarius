"""Every More and New menu entry runs a method that exists (STORY-1125):
MenuItem.run looks its handler up by name, so a renamed method would only
fail when someone picked the entry."""

import pytest

from ars_magica_manager.screens.workspace import base
from ars_magica_manager.screens.workspace.screen import WorkspaceScreen


@pytest.mark.parametrize(
    "item",
    base._MORE_MENU + base._NEW_MENU,
    ids=lambda item: f"{item.action}-{item.handler or 'action'}",
)
def test_every_menu_item_has_its_handler(item):
    handler = getattr(WorkspaceScreen, item.handler or f"action_{item.action}", None)
    assert callable(handler)
