"""The keys that work on every page, in both front-ends: Help, Back and
Quit.

Each is a command (its action) with the keys that give it, written as
they are printed on the keyboard. A front-end binds each key to its own
handler for the action: the terminal's screens bind them as Textual
bindings, the desktop window as shortcuts (gui/window.py). Tests check
both front-ends and their Keys help against this table, so they can't
drift apart.

A typed key (a letter or a sign, not Esc or F1) never acts while the
user is typing in a field, or while a form or question is open: there it
is part of what is typed.
"""

from __future__ import annotations

from typing import NamedTuple

HELP, BACK, QUIT = "help", "back", "quit"


class Hotkey(NamedTuple):
    """One page-wide command: its action, the keys that give it, and what
    it does, for the help pages."""

    action: str
    keys: tuple[str, ...]
    does: str


HOTKEYS: tuple[Hotkey, ...] = (
    Hotkey(HELP, ("?", "F1"), "Help on the page you are on"),
    Hotkey(
        BACK,
        ("Esc",),
        "Cancel the form or question that is open, else go back a page",
    ),
    Hotkey(QUIT, ("q",), "Quit Armarius"),
)


def keys_for(action: str) -> tuple[str, ...]:
    """The keys that give `action`."""
    return next(hotkey.keys for hotkey in HOTKEYS if hotkey.action == action)


def is_typed(key: str) -> bool:
    """Whether `key` is one that types a character (a letter or a sign),
    so never acts while a field or form is being filled in."""
    return len(key) == 1
