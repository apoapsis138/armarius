"""Signing in to a hosted copy, from a browser or over SSH.

A hosted copy asks for a name and a passcode before it opens a saga
(players.sign_in checks them). Two rules sit in front of that check here:

- **Wrong passcodes wait.** Each name typed has a count of wrong passcodes
  in a row, kept in a file in the host's data folder (outside the saga),
  shared by every copy under a lock, since each copy is a process of its
  own. The wait is the rule every sign-in shares (lockout.py). A name no
  player has is counted the same way, so the waits don't tell real names
  from made-up ones.
- **A passcode shorter than 14 characters signs in once more.** The
  player is then asked for a new one, and may put that off this one time;
  the next sign-in with the short one is refused until it is changed (by
  them, here, or by the storyguide). Which short passcode had its last
  sign-in is noted by its salt, so a new passcode, even another short one
  the storyguide set, starts afresh.

Pattern: `attempt` is the one gate both ways in (a browser tab, an SSH
session) pass through; the passcode rule is players.passcode_problem (a
Specification), the waits lockout's policy (a Strategy) over a file shared
the way the Remote seat files are (remote/folder.SharedFile).
"""

from __future__ import annotations

import json
import math
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import lockout, players, shapes, storage
from .files import write_atomic
from .models import Player, Saga
from .remote.folder import SharedFile, remote_file
from .remote.passcodes import RemotePasscodes, passcodes_path

#: What a wrong name or passcode is told: the same sentence for both.
REFUSED = "That name and passcode don't match a player of this saga."
#: What a short passcode whose last sign-in is spent is told.
SHORT_SPENT = (
    f"Your passcode is shorter than {players.MIN_PASSCODE} characters and "
    "has had its last sign-in. Ask the storyguide to set you a new one."
)


@dataclass
class Tries:
    """Wrong passcodes in a row for one name, and when it may try again."""

    failures: int = 0
    locked_until: float = 0.0


@dataclass
class SignInFile:
    """The file's shape, checked as it is read (shapes.build): tries by
    name, and each player's short passcode whose last sign-in is spent
    (by its salt)."""

    names: dict[str, Tries] = field(default_factory=dict[str, Tries])
    short_spent: dict[str, str] = field(default_factory=dict[str, str])


class SignInBook(SharedFile):
    """The tries of one hosted saga's sign-in dialog, shared by every copy."""

    def __init__(self, path: Path, clock: Callable[[], float] = time.time) -> None:
        self._path = path
        self._clock = clock
        self._book = SignInFile()
        self._load()

    def _load(self) -> None:
        self._book = SignInFile()
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            self._book = shapes.build(SignInFile, data)
        except (OSError, ValueError) as exc:
            raise ValueError(
                f"The sign-in file {self._path.name} cannot be read ({exc})."
            ) from exc

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        write_atomic(self._path, json.dumps(asdict(self._book), indent=1))

    def wait(self, name: str) -> int:
        """Whole seconds before `name` may try again; 0 if it may now."""
        with self._fresh():
            tries = self._book.names.get(_key(name))
            if tries is None:
                return 0
            return max(0, math.ceil(tries.locked_until - self._clock()))

    def failed(self, name: str) -> int:
        """Count a wrong passcode for `name`; the seconds it must now wait."""
        with self._fresh():
            tries = self._book.names.setdefault(_key(name), Tries())
            tries.failures += 1
            until = lockout.locked_until(tries.failures, self._clock())
            if until:
                tries.locked_until = until
            self._save()
            return self.wait(name)

    def signed_in(self, name: str) -> None:
        """A right passcode for `name`: its count starts again."""
        with self._fresh():
            if self._book.names.pop(_key(name), None) is not None:
                self._save()

    def short_spent(self, player: Player) -> bool:
        """Whether `player`'s short passcode has had its last sign-in."""
        with self._fresh():
            salt = _salt(player)
            return bool(salt) and self._book.short_spent.get(player.id) == salt

    def spend_short(self, player: Player) -> None:
        """Note that `player`'s short passcode has had its last sign-in."""
        with self._fresh():
            self._book.short_spent[player.id] = _salt(player)
            self._save()


def _key(name: str) -> str:
    return name.strip().casefold()


def _salt(player: Player) -> str:
    try:
        salt, _ = players.stored_parts(player.passcode_hash)
    except ValueError:
        return ""
    return salt.hex()


def book_path(saga_name: str) -> Path:
    """Where a saga's sign-in tries are kept, beside its Remote seat files."""
    return remote_file(saga_name, "signin.json")


@dataclass(frozen=True)
class Outcome:
    """What a sign-in came to: the `player` signed in, or why not
    (`refused`). `short`: their passcode is shorter than the rule allows,
    so they must be asked for a new one; `may_put_off`: they may say no
    this once."""

    player: Player | None = None
    refused: str = ""
    short: bool = False
    may_put_off: bool = False


def attempt(book: SignInBook, saga: Saga, name: str, passcode: str) -> Outcome:
    """Try to sign in to `saga` as `name` with `passcode`."""
    wait = book.wait(name)
    if wait:
        return Outcome(refused=lockout.wait_text(wait))
    player = players.sign_in(saga, name, passcode)
    if player is None:
        wait = book.failed(name)
        return Outcome(refused=lockout.wait_text(wait) if wait else REFUSED)
    book.signed_in(name)
    if players.passcode_problem(passcode) is None:
        return Outcome(player)
    if book.short_spent(player):
        return Outcome(refused=SHORT_SPENT)
    return Outcome(player, short=True, may_put_off=True)


def change_passcode(saga: Saga, player: Player, new: str) -> str | None:
    """Set `player`'s new passcode and save it, as `player`: why not, or
    None once saved. A long enough one may be used from a Remote seat too."""
    problem = players.passcode_problem(new)
    if problem is not None:
        return problem
    players.set_passcode(player, new)
    storage.save_saga(saga, storage.Saver(player.name))
    RemotePasscodes(passcodes_path(saga.name)).note(player, new)
    return None
