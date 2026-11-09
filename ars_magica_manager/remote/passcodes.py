"""Which players' passcodes are long enough to sign in from a Remote seat.

Only the length of a passcode decides it, and the length is known only at
the moment the passcode is set (the saga keeps just its scrypt hash). So
when a passcode is set, the host notes it here: player id to the salt of
that hash. A player may sign in remotely while the salt noted matches the
salt the saga holds now. A passcode changed by any other road (an older
saga, an edit made on another computer) has a fresh salt, so it falls back
to "not allowed" until it is set again here, never to a stale "allowed".

The file lives in the host's data folder, not the saga, so it never
travels with the saga or an export of it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .. import players, shapes
from ..files import write_atomic
from ..models import Player
from .folder import SharedFile, remote_file


@dataclass
class PasscodesFile:
    """The passcodes file's shape, checked as it is read (shapes.build):
    player id to the salt noted."""

    salts: dict[str, str]


class RemotePasscodes(SharedFile):
    """The long-enough passcodes of one hosted saga, kept in one file that
    the Storyguide's window writes and the listener reads."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._salts: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        self._salts = {}
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            self._salts = shapes.build(PasscodesFile, data).salts
        except (OSError, ValueError) as exc:
            raise ValueError(
                f"The passcodes file {self._path.name} cannot be read ({exc})."
            ) from exc

    def _save(self) -> None:
        write_atomic(self._path, json.dumps({"salts": self._salts}, indent=1))

    def note(self, player: Player, passcode: str) -> None:
        """Note the passcode just set for `player` (`player.passcode_hash`
        already holds it): allowed if long enough, else not."""
        salt = _salt(player)
        with self._fresh():
            if salt and players.passcode_problem(passcode) is None:
                self._salts[player.id] = salt
            else:
                self._salts.pop(player.id, None)
            self._save()

    def allow(self, player: Player) -> None:
        """Allow `player`'s passcode as it is now, which they set themselves
        from their seat: their app checked its length, since the host only
        ever sees its scrambled form (ADR 0013)."""
        salt = _salt(player)
        if not salt:
            raise ValueError("The player has no passcode.")
        with self._fresh():
            self._salts[player.id] = salt
            self._save()

    def forget(self, player_id: str) -> None:
        """A player was deleted."""
        with self._fresh():
            if self._salts.pop(player_id, None) is not None:
                self._save()

    def allows(self, player: Player) -> bool:
        """Whether `player`'s current passcode may be used from a Remote seat."""
        salt = _salt(player)
        with self._fresh():
            return bool(salt) and self._salts.get(player.id) == salt


def _salt(player: Player) -> str:
    try:
        salt, _ = players.stored_parts(player.passcode_hash)
    except ValueError:
        return ""
    return salt.hex()


def passcodes_path(saga_name: str) -> Path:
    """Where a saga's note of long-enough passcodes lives."""
    return remote_file(saga_name, "passcodes.json")
