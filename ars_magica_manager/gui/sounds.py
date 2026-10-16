"""The desktop version's few sounds, kept for the moments that mean
something: a page turned for a chapter (a longer one for a record), a
quill when a form is saved, coins for the Treasury, a chest for the
Inventory, a wax seal for Advance Season and a dull knock when an entry
is refused. Plain button presses stay silent.

`play(cue)` is the one way in. It plays through Windows' own `winsound`,
so nothing new is installed; on any other system, while the Sounds
setting is off, and whenever ARMARIUS_SOUNDS is "off" (the tests) the
player is a silent one that does nothing, so no caller checks.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Protocol

from .. import artwork, settings

#: Turns every sound off whatever the setting says (the tests set it).
ENV_VAR = "ARMARIUS_SOUNDS"


class Player(Protocol):
    def play(self, path: Path) -> None: ...


class Silent:
    """A player that plays nothing."""

    def play(self, path: Path) -> None:
        pass


class Windows:
    """Plays a sound without waiting for it, cutting off one still
    playing (winsound plays one at a time)."""

    def play(self, path: Path) -> None:
        if sys.platform == "win32":
            import winsound

            winsound.PlaySound(
                str(path),
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
            )


_player: Player | None = None


def enabled() -> bool:
    """Whether the Sounds setting is on (it is unless turned off)."""
    return settings.load_settings().get("sounds", True) is not False


def set_enabled(on: bool) -> None:
    """Turn the sounds on or off, and remember it."""
    global _player
    settings.update_settings(sounds=on)
    _player = None


def _chosen() -> Player:
    if os.environ.get(ENV_VAR) == "off" or not enabled():
        return Silent()
    return Windows() if sys.platform == "win32" else Silent()


def play(cue: str) -> None:
    """Play the sound for `cue` (artwork.SOUNDS); KeyError for one the
    registry lacks."""
    global _player
    path = artwork.SOUNDS[cue]
    if _player is None:
        _player = _chosen()
    _player.play(path)
