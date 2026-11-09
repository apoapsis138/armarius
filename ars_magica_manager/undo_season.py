"""Undo Last Season: the saga put back as it was before the last advance.

Every Advance Season, and every downtime run, backs the saga up first
(storage.backup_saga) and keeps a copy just after it ends
(storage.remember_after): a pair. Undo is offered when the newest pair's
after-copy has the saga's date, so the saga hasn't been moved since by
Set Date; it puts back the backup, whole (the date, Wealth, Diaries and
every result), one advance at a time, as far as the pairs go (up to
storage.BACKUPS_KEPT). A downtime run is one pair, so it undoes as one.

What anyone changed since the advance is lost too: the question lists the
records changed since (the after-copy against the saga now), by name. The
saga as it stood is kept first (storage.undone_path), so a mistaken undo
loses nothing.

Pattern: Memento. A backup is the saga's state before the advance, kept
outside it and restored whole; the after-copy is a second memento, read
only to say what changed since.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any, Protocol

from . import storage
from .commands import Command, Confirm, Refuse
from .markup import escape
from .models import Saga
from .saga_delta import saga_delta

TITLE = "Undo Last Season"
#: The saga's own fields that change with every save, not with play.
_BOOKKEEPING = frozenset({"saved_by", "app_version"})
#: How many changed records the question names before "and N more".
NAMED = 12


@dataclass(frozen=True)
class Undo:
    """An advance that can be undone: which pair (`age`), the season it
    goes back to, the season it is now, and the records changed since."""

    age: int
    back_to: str
    now: str
    lost: tuple[str, ...]


@dataclass(frozen=True)
class Undone:
    """What an undo ended with, for the front-end: the season the saga is
    back to (its dial turns back), and the line saying so. `remote`: done
    by the host, so the window reads the saga again to see it."""

    back_to: str
    message: str
    remote: bool = False


class HostUndo(Protocol):
    """A storyguide's Remote seat, whose host keeps the backups
    (remote/season_undo.py, through seat_session.SeatSession)."""

    def undo_offer(self) -> Undo | None: ...

    def undo_season(self, now: str) -> str: ...


#: Set while a storyguide's window has a Joined game open: Undo then asks
#: its host (as picture_files.use_host does for pictures).
_host: HostUndo | None = None


def use_host(host: HostUndo | None) -> None:
    global _host
    _host = host


def _read(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return None
    return data if isinstance(data, dict) else None


def _date(data: dict[str, Any]) -> str:
    return f"{data.get('current_season')} {data.get('current_year')}"


def offer(saga: Saga) -> Undo | None:
    """The newest advance that can be undone, or None: its backup and
    after-copy are both kept, and the after-copy is at the saga's date (an
    advance cancelled part-way left a backup with no after-copy, which is
    passed over)."""
    now = asdict(saga)
    for age in range(storage.BACKUPS_KEPT):
        after = _read(storage.after_path(saga.id, age))
        if after is None:
            continue
        before = _read(storage.backup_path(saga.id, age))
        if before is None or _date(after) != _date(now):
            return None
        return Undo(age, _date(before), _date(now), _changed_since(after, now))
    return None


def _changed_since(after: dict[str, Any], now: dict[str, Any]) -> tuple[str, ...]:
    """The records changed since the after-copy, by name; the saga's own
    settings as one."""
    was, is_ = saga_delta(after, now)
    names: list[str] = []
    for place in [*was, *(p for p in is_ if p not in was)]:
        key, _, rest = place.partition("[")
        if not rest:
            if key not in _BOOKKEEPING and "the saga's own settings" not in names:
                names.append("the saga's own settings")
            continue
        record = is_.get(place) or was.get(place) or {}
        name = str(record.get("name") or record.get("id") or key)
        if name not in names:
            names.append(name)
    return tuple(names)


def undo(saga: Saga, found: Undo) -> Undone:
    """Put `saga` back to the backup of `found`, in place (the caller saves
    it): the saga as it stood is kept first, and the pairs back to that one
    are used up, the older ones moving up. ValueError if the backup can't
    be read."""
    data = _read(storage.backup_path(saga.id, found.age))
    if data is None:
        raise ValueError("The backup can't be read.")
    restored = storage.saga_from_data(data)
    storage.undone_path(saga.id).parent.mkdir(parents=True, exist_ok=True)
    storage.undone_path(saga.id).write_text(
        json.dumps(asdict(saga), indent=2), encoding="utf-8"
    )
    for field in fields(Saga):
        if field.name not in _BOOKKEEPING:
            setattr(saga, field.name, getattr(restored, field.name))
    _use_up(saga.id, found.age)
    return Undone(
        found.back_to,
        f"Undone: the saga is back to {found.back_to}, as it was before "
        f"{found.now} was reached.",
    )


def _use_up(saga_id: str, age: int) -> None:
    """Drop the pairs up to `age`; the older ones move up to take their
    place."""
    for path_of in (storage.backup_path, storage.after_path):
        for gone in range(age + 1):
            path_of(saga_id, gone).unlink(missing_ok=True)
        for older in range(age + 1, storage.BACKUPS_KEPT):
            path = path_of(saga_id, older)
            if path.exists():
                path.replace(path_of(saga_id, older - age - 1))


def question(found: Undo) -> str:
    """What Undo asks first (markup)."""
    lost = ""
    if found.lost:
        shown = ", ".join(escape(n) for n in found.lost[:NAMED])
        more = len(found.lost) - NAMED
        lost = (
            f"\n\nChanges made since {escape(found.now)} are lost too: {shown}"
            + (f", and {more} more" if more > 0 else "")
            + "."
        )
    return (
        f"Put the whole saga back to {escape(found.back_to)}, as it was before "
        f"it reached {escape(found.now)}? The date, Wealth, Diaries and every "
        f"result of the season go back.{lost}\n\n[dim]The saga as it is now is "
        "kept in sagas/backups in your data folder first.[/]"
    )


def undo_command(saga: Saga) -> Command:
    """Undo Last Season: asked first, then done (the saga changed in place;
    the front-end saves it and turns the season's dial back). In a Joined
    game it is asked of the host, which keeps the backups."""
    host = _host
    if host is not None:
        return _from_host(host)
    found = offer(saga)
    if found is None:
        return Refuse(TITLE, NOTHING)
    return Confirm(
        question(found),
        lambda: undo(saga, found),
        yes_label="Undo",
        title=TITLE,
    )


UNREACHABLE = "The host can't be reached: try again once it answers."
NOTHING = (
    "There's no advance to undo: none is kept since the saga's date was last "
    "set, or the backups were cleared."
)


def _from_host(host: HostUndo) -> Command:
    try:
        found = host.undo_offer()
    except ConnectionError, TimeoutError:
        return Refuse(TITLE, UNREACHABLE)
    if found is None:
        return Refuse(TITLE, NOTHING)

    def apply() -> Undone | Refuse:
        try:
            said = host.undo_season(found.now)
        except ConnectionError, TimeoutError:
            return Refuse(TITLE, UNREACHABLE)
        if not said:
            return Refuse(TITLE, "The saga moved on meanwhile: nothing was undone.")
        return Undone(found.back_to, said, remote=True)

    return Confirm(
        question(found).replace(
            "kept in sagas/backups in your data folder", "kept on the host's computer"
        ),
        apply,
        yes_label="Undo",
        title=TITLE,
    )
