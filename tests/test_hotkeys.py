"""The page-wide keys (hotkeys.py) are the ones the terminal binds, and
the desktop's Keys help lists them."""

from __future__ import annotations

from textual.binding import Binding

from ars_magica_manager import help_text as ht
from ars_magica_manager import hotkeys
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.workspace.base import WorkspaceBase

#: Textual's names for the table's keys.
_TEXTUAL = {
    "?": "question_mark",
    "F1": "f1",
    "Esc": "escape",
    "q": "q",
    "Ctrl+F": "ctrl+f",
}

#: The terminal's actions for each of the table's.
_ACTIONS = {
    hotkeys.HELP: {"help"},
    hotkeys.BACK: {"step_out"},
    hotkeys.QUIT: {"quit"},
    hotkeys.FIND: {"find"},
}


def _bound(bindings) -> dict[str, str]:
    keys = {}
    for binding in bindings:
        if isinstance(binding, Binding):
            keys[binding.key] = binding.action
        else:
            keys[binding[0]] = binding[1]
    return keys


def test_the_terminal_binds_the_same_keys():
    bound = _bound(WorkspaceBase.BINDINGS) | _bound(ArsMagicaManagerApp.BINDINGS)
    for hotkey in hotkeys.HOTKEYS:
        for key in hotkey.keys:
            assert bound.get(_TEXTUAL[key]) in _ACTIONS[hotkey.action], key


def test_the_desktop_keys_help_lists_every_key():
    text = ht.book(ht.GUI).topics["keys-always"].text
    for hotkey in hotkeys.HOTKEYS:
        for key in hotkey.keys:
            assert f"`{key}`" in text, key


def test_typed_keys_are_the_letters_and_signs():
    assert hotkeys.is_typed("?") and hotkeys.is_typed("q")
    assert not hotkeys.is_typed("Esc") and not hotkeys.is_typed("F1")
    assert hotkeys.keys_for(hotkeys.QUIT) == ("q",)
