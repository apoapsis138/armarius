"""Where a front-end loads and saves the saga it shows (ADR 0011).

Two kinds, the same three calls, so the pages never know which they have
(Remote Proxy):

- `LocalStore`: the saga file in the data folder (storage.py), as always,
  merging with other copies' saves (ADR 0005).
- `RemoteStore`: a Joined game. It loads the Player's Seat view from the
  host, and on save works out which records changed since that snapshot
  and sends each as one change (ADR 0010). Nothing is written on the
  Player's computer.

`refresh` brings what another copy saved: the local file's changes, or a
new snapshot from the host.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol

from . import storage
from .models import Saga
from .saga_delta import HOST_ONLY, saga_delta
from .seat_changes import CHANGEABLE, record_key


class NotSaved(Exception):
    """The host refused one change (not the Player's to make)."""


@dataclass(frozen=True)
class Refreshed:
    """What another copy saved: the saga as it now is (the same object for
    a local file, a fresh one from a host) and the records that changed,
    as (list, id) pairs."""

    saga: Saga
    changed: list[tuple[str, str]]


@dataclass(frozen=True)
class Saved:
    """What a save sent back: where it overlapped another's change (kept
    as this save has it), and what the host refused."""

    overlaps: list[str]
    refused: list[str]


class SagaStore(Protocol):
    """Load, save and keep up to date one saga."""

    remote: bool

    def save(self, saga: Saga) -> Saved: ...

    def refresh(self, saga: Saga) -> Refreshed | None: ...


class LocalStore:
    """The saga's file in the data folder."""

    remote = False

    def save(self, saga: Saga) -> Saved:
        found = storage.save_saga(saga)
        return Saved(found.conflicts, [])

    def refresh(self, saga: Saga) -> Refreshed | None:
        """Raises ValueError when the file can't be read (storage.reload_into)."""
        changed = storage.reload_into(saga)
        return Refreshed(saga, changed) if changed else None


class RemoteSeat(Protocol):
    """What RemoteStore needs of a Remote seat (seat_session.SeatSession)."""

    def read(self, since: str = "") -> tuple[str, Saga | None]: ...

    def send_change(
        self,
        kind: str,
        key: str,
        before: dict[str, Any] | None,
        after: dict[str, Any] | None,
    ) -> list[str]: ...

    def send_saga(self, before: dict[str, Any], after: dict[str, Any]) -> list[str]: ...


class RemoteStore:
    """A Joined game's saga, read from and saved to its host. A player's
    seat sends each record changed (ADR 0010); a storyguide's (`whole`)
    sends what changed in the whole saga (saga_delta.py, ADR 0014)."""

    remote = True

    def __init__(self, seat: RemoteSeat, *, whole: bool = False) -> None:
        self.seat = seat
        self.whole = whole
        self.revision = ""
        self._base: dict[str, Any] = {}

    def load(self) -> Saga:
        revision, saga = self.seat.read()
        if saga is None:
            raise ValueError("The host sent no saga.")
        self._took(revision, saga)
        return saga

    def _took(self, revision: str, saga: Saga) -> None:
        self.revision = revision
        self._base = asdict(saga)

    def save(self, saga: Saga) -> Saved:
        """Send each record changed since the last snapshot. A change the
        host refuses is listed; the rest are kept."""
        return self.send(asdict(saga))

    def send(self, now: dict[str, Any]) -> Saved:
        """As save, for the saga as plain data (`asdict`, taken on the
        window's thread, so this can run on another)."""
        if self.whole:
            return self._send_whole(now)
        overlaps: list[str] = []
        refused: list[str] = []
        for kind in sorted(CHANGEABLE):
            for key, before, after in changed_records(
                kind, self._base.get(kind, []), now.get(kind, [])
            ):
                try:
                    overlaps += self.seat.send_change(kind, key, before, after)
                except NotSaved:
                    refused.append(f"{kind}:{key}")
        self._base = now
        return Saved(overlaps, refused)

    def _send_whole(self, now: dict[str, Any]) -> Saved:
        """A storyguide's save: what changed since the last snapshot, sent
        at once. Changes to what only the host changes are left out and
        listed as refused. AlreadyAdvanced (from the seat) is passed on."""
        before, after = saga_delta(self._base, now)
        held = [p for p in {*before, *after} if p.split("[", 1)[0] in HOST_ONLY]
        for place in held:
            before.pop(place, None)
            after.pop(place, None)
        overlaps: list[str] = []
        refused = sorted(held)
        if before or after:
            try:
                overlaps = self.seat.send_saga(before, after)
            except NotSaved:
                refused.append("saga")
        self._base = now
        return Saved(overlaps, refused)

    def start_again(self) -> None:
        """Drop what wasn't taken (another storyguide advanced first): the
        next read brings the host's whole saga, which replaces this copy."""
        self.revision = ""

    def refresh(self, saga: Saga) -> Refreshed | None:
        """A new snapshot, if the host's saga changed in what this seat may
        see."""
        return self.take(*self.seat.read(self.revision))

    def take(self, revision: str, fresh: Saga | None) -> Refreshed | None:
        """What `seat.read` brought (it may have been read on another
        thread): the new snapshot and what changed in it, or None."""
        if fresh is None:
            return None
        changed = [
            (kind, key)
            for kind in sorted(CHANGEABLE)
            for key, _before, _after in changed_records(
                kind, self._base.get(kind, []), asdict(fresh).get(kind, [])
            )
        ]
        self._took(revision, fresh)
        return Refreshed(fresh, changed or [("saga", "")])


def changed_records(
    kind: str, before: list[dict[str, Any]], after: list[dict[str, Any]]
) -> list[tuple[str, dict[str, Any] | None, dict[str, Any] | None]]:
    """Each record of the list `kind` added, changed or deleted between
    `before` and `after`: its key, and it before and after (None: not
    there)."""
    old = {record_key(kind, r): r for r in before}
    new = {record_key(kind, r): r for r in after}
    found = []
    for key in [*old, *(k for k in new if k not in old)]:
        was, now = old.get(key), new.get(key)
        if was != now:
            found.append((key, was, now))
    return found
