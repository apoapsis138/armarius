"""What Help opens on, kept apart from the help screen so a dialog can name
it without importing the screen that is built on dialogs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class HelpContext:
    """What Help opens on: the topic ids for where focus is (most specific
    first), where that is in words, and the keys that work there; and, from
    a screen with places to go to, what opens one (Go there): it takes a
    tab's or section's id, opens it once Help has closed, and says whether
    the screen has it."""

    ids: list[str] = field(default_factory=list)
    where: str = ""
    keys: list[str] = field(default_factory=list)
    go_to: Callable[[str], bool] | None = None
