"""A Session's Chronicle: everything rolled while it is Under way, kept by
the host in a file of its own beside the saga (ADRs 0018 and 0020).

Begin Session opens it and End Session closes it; only the Session's
storyguide does either, and at most one Session of a saga is Under way.
Every entry has the same envelope (its number within the Session, time,
kind, author, Audience, and a body by kind) and nothing is ever changed or
removed: a Void is a new entry naming the roll it strikes.

Pattern: Command. A RollRequest is what to roll, as data; `free_roll`
carries it out once, at the host, with the host's own source of chance,
and the Chronicle is the list of the commands carried out. Asking again
makes a second roll, never a replacement.

Who may see an entry is decided here, once: `sees` is the one audience
filter every reader goes through (the host's own window now; seats and
the desktop pane later). The host's computer keeps the whole file,
whatever each entry's Audience, and the help says so.

The file is JSON Lines at `chronicles/<saga id>/<session id>.jsonl` in the
save folder, flushed per entry; a last line left half-written (the app
stopped mid-write) is dropped when it is read back.

Two processes write it: the Storyguide's window, and the Remote seat
listener (remote/serve.py), which runs apart from the window. The file is
the one Chronicle: each writer holds its lock, reads what the other wrote
since, and numbers the new entry from the file, never from its own copy;
each catches up with `refresh`, telling its subscribers of every entry new
to it.
"""

from __future__ import annotations

import datetime
import json
import os
import random
import secrets
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from . import paths, shapes, viewing
from .files import held_lock
from .markup import escape
from .models import Saga, Session
from .rules import dice

# -- Audience --

TABLE = "table"
STORYGUIDE = "storyguide"
CHOSEN = "chosen"


@dataclass(frozen=True)
class Audience:
    """Who may see an entry: the Table (everyone at the Session), the
    Session's storyguide alone, or chosen Players (the Session's storyguide
    always sees those too)."""

    to: str
    players: list[str] = field(default_factory=list)


def table() -> Audience:
    return Audience(TABLE)


def storyguide_only() -> Audience:
    return Audience(STORYGUIDE)


def chosen(*players: str) -> Audience:
    return Audience(CHOSEN, list(players))


def storyguide_of(session: Session, saga: Saga | None = None) -> str:
    """Who runs `session`, as a person at it: the Player named as its
    storyguide, else the host (the saga's own storyguide). Given the saga,
    a storyguide no longer among its Players counts as none, so a Session
    never waits on someone who can't end it."""
    named = session.storyguide_id
    if named and saga is not None and named not in {p.id for p in saga.players}:
        named = ""
    return named or viewing.HOST


def here() -> str:
    """Who is using this copy of the app, as a person at a Session."""
    return person(viewing.current())


def person(viewer: viewing.Viewer) -> str:
    """Who `viewer` is at a Session: a signed-in Player's id, HOST for the
    host's own window as storyguide, "" for anyone else (the table)."""
    if viewer.player is not None:
        return viewer.player.id
    return viewing.HOST if viewer.hosts and viewer.is_storyguide else ""


# -- entries --


@dataclass(frozen=True)
class Entry:
    """One line of a Chronicle."""

    number: int
    time: str
    kind: str
    author: str
    audience: Audience
    body: dict[str, Any] = field(default_factory=dict)


def sees(entry: Entry, who: str, session: Session, saga: Saga | None = None) -> bool:
    """Whether `who` may see `entry`: the audience filter."""
    if entry.audience.to == TABLE:
        return True
    if who == storyguide_of(session, saga):
        return True
    return entry.audience.to == CHOSEN and who in entry.audience.players


#: The clock entries are stamped with (UTC).
def _now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")


clock: Callable[[], str] = _now


class Chronicle:
    """A Session's Chronicle: its entries in order, and its file."""

    def __init__(self, path: Path, entries: list[Entry]) -> None:
        self.path = path
        self.entries = entries
        self._listeners: list[Callable[[Entry], None]] = []

    def subscribe(self, listener: Callable[[Entry], None]) -> Callable[[], None]:
        """Tell `listener` of each entry added from now on (Observer: a
        seat's event connection, the desktop pane). Returns the call that
        stops it."""
        self._listeners.append(listener)

        def stop() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return stop

    @property
    def closed(self) -> bool:
        """Ended: nothing more is written to it."""
        return bool(self.entries) and self.entries[-1].kind == END

    def since(self, number: int) -> list[Entry]:
        """The entries after `number` (0: all of them)."""
        return [e for e in self.entries if e.number > number]

    def seen_by(
        self, who: str, session: Session, saga: Saga | None = None
    ) -> list[Entry]:
        """The entries `who` may see, in order."""
        return [e for e in self.entries if sees(e, who, session, saga)]

    def add(
        self, kind: str, author: str, audience: Audience, body: dict[str, Any]
    ) -> Entry:
        """Write a new entry at the end, flushed to the file before it
        counts: under the file's lock, after what another process wrote
        since, numbered from the file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with held_lock(_lock_of(self.path)):
            caught_up = self._catch_up(mend=True)
            if self.closed:
                self._tell(caught_up)
                raise ValueError("This Session has ended: its Chronicle is closed.")
            entry = Entry(len(self.entries) + 1, clock(), kind, author, audience, body)
            with self.path.open("a", encoding="utf-8", newline="\n") as out:
                out.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
                out.flush()
                os.fsync(out.fileno())
            self.entries.append(entry)
        # Subscribers are told once the lock is let go, so a slow or failing
        # one never holds up the other process.
        self._tell([*caught_up, entry])
        return entry

    def refresh(self) -> list[Entry]:
        """Catch up with what another process wrote since (Observer: each
        subscriber is told of every entry new here)."""
        fresh = self._catch_up()
        self._tell(fresh)
        return fresh

    def _catch_up(self, *, mend: bool = False) -> list[Entry]:
        """Read what is new in the file; `mend` (only with the file's lock
        held) cuts a half-written last line first."""
        found = _load(self.path, mend=mend)
        fresh = found[len(self.entries) :]
        self.entries.extend(fresh)
        return fresh

    def _tell(self, entries: list[Entry]) -> None:
        for entry in entries:
            for listener in list(self._listeners):
                listener(entry)


def _lock_of(path: Path) -> Path:
    """The lock every writer of the Chronicle file `path` holds."""
    return path.with_name(f".{path.name}.lock")


def _safe(value: str, what: str) -> str:
    if not shapes.is_plain_id(value):
        raise ValueError(f"A {what} id can't name a Chronicle file: {value!r}")
    return value


def path_of(saga: Saga, session: Session) -> Path:
    """Where `session`'s Chronicle is kept."""
    return (
        paths.data_dir()
        / paths.CHRONICLES
        / _safe(saga.id, "saga")
        / f"{_safe(session.id, 'Session')}.jsonl"
    )


def files_of(saga_id: str) -> list[Path]:
    """Every Chronicle file of the saga `saga_id`, for its backups: none
    for an id no Chronicle file could be named by."""
    if not shapes.is_plain_id(saga_id):
        return []
    folder = paths.data_dir() / paths.CHRONICLES / saga_id
    return sorted(folder.glob("*.jsonl")) if folder.is_dir() else []


def _load(path: Path, *, mend: bool = False) -> list[Entry]:
    """The entries in `path`; a last line left half-written is dropped, a
    damaged line before it refused (ValueError). With `mend`, before more
    is written, the dropped half line is cut from the file too, so the next
    entry starts a line of its own."""
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return []
    lines = raw.split(b"\n")
    entries: list[Entry] = []
    whole = 0
    for index, line in enumerate(lines):
        if index == len(lines) - 1:
            break  # after the last newline: empty, or a half-written entry
        try:
            data = json.loads(line)
        except ValueError:
            raise ValueError(
                f"{path.name}, line {index + 1}: not a Chronicle entry"
            ) from None
        entries.append(shapes.build(Entry, data))
        whole += len(line) + 1
    if mend and whole < len(raw):
        with path.open("r+b") as out:
            out.truncate(whole)
    return entries


#: The Chronicles open in this copy of the app, by their file.
_open: dict[Path, Chronicle] = {}


def forget_open() -> None:
    """Forget the Chronicles open here, as a restart of the app does: each
    is read back from its file when next asked for."""
    _open.clear()


def read(saga: Saga, session: Session) -> Chronicle:
    """`session`'s Chronicle: the one open here, else read back from its
    file (after a restart while it is Under way, or once it has ended)."""
    path = path_of(saga, session)
    found = _open.get(path)
    if found is None:
        found = Chronicle(path, _load(path))
        if session.under_way:
            _open[path] = found
    return found


def has_chronicle(saga: Saga, session: Session) -> bool:
    """Whether `session` was ever begun, so has a Chronicle to read."""
    if session.under_way:
        return True
    try:
        return path_of(saga, session).is_file()
    except ValueError:
        return False


# -- Begin and End Session --

BEGIN = "begin"
END = "end"


def under_way(saga: Saga) -> Session | None:
    """The saga's Session that is Under way, if any."""
    return next((s for s in saga.sessions if s.under_way), None)


def why_not_begin(saga: Saga, session: Session, who: str) -> str | None:
    """Why `who` may not Begin `session`, or None when they may."""
    if who != storyguide_of(session, saga):
        return "Only the Session's storyguide begins it."
    if session.played:
        return "This Session has been played."
    if session.under_way:
        return "This Session is already under way."
    if under_way(saga) is not None:
        return "Another Session is under way: end it first."
    try:
        path = path_of(saga, session)
    except ValueError as problem:
        return str(problem)
    if path.is_file() and Chronicle(path, _load(path)).closed:
        return "This Session has ended: its Chronicle is closed."
    return None


def why_not_end(session: Session, who: str, saga: Saga | None = None) -> str | None:
    """Why `who` may not End `session`, or None when they may."""
    if not session.under_way:
        return "This Session isn't under way."
    if who != storyguide_of(session, saga):
        return "Only the Session's storyguide ends it."
    return None


def begin(saga: Saga, session: Session, *, by: str) -> Chronicle:
    """Begin `session`: it is Under way, and its Chronicle opens."""
    problem = why_not_begin(saga, session, by)
    if problem:
        raise ValueError(problem)
    path = path_of(saga, session)
    book = Chronicle(path, _load(path))
    book.add(BEGIN, by, table(), {})
    session.under_way = True
    _open[path] = book
    return book


def end(saga: Saga, session: Session, *, by: str) -> Chronicle:
    """End `session`: it is Played, and its Chronicle closes, kept beside
    the saga to read."""
    problem = why_not_end(session, by, saga)
    if problem:
        raise ValueError(problem)
    book = read(saga, session)
    book.add(END, by, table(), {})
    session.under_way = False
    session.played = True
    _open.pop(book.path, None)
    return book


# -- rolling --

PUBLIC = "public"
PRIVATE = "private"
BLIND = "blind"

ROLL = "roll"
ROLLED = "rolled"
VOID = "void"


@dataclass(frozen=True)
class RollRequest:
    """A Free roll, as data: a stress or simple die, the modifier the
    roller typed, the botch dice, an optional Ease Factor, what it is for,
    the character it is for (none: the storyguide's own), and who may see
    it (PUBLIC, PRIVATE or BLIND)."""

    stress: bool = True
    modifier: int = 0
    botch_dice: int = 1
    ease_factor: int | None = None
    for_what: str = ""
    character_id: str = ""
    visibility: str = PUBLIC


def why_not_roll(
    saga: Saga, session: Session, request: RollRequest, who: str
) -> str | None:
    """Why `who` may not make `request` at `session`, or None when they may:
    a player rolls only for a character they play tonight, the Session's
    storyguide for any character or none; only the storyguide rolls Blind."""
    if request.visibility not in (PUBLIC, PRIVATE, BLIND):
        return "Choose who sees the roll."
    if request.botch_dice < 0:
        return "Botch dice can't be fewer than none."
    storyguide = who == storyguide_of(session, saga)
    known = {c.id for c in saga.characters}
    if request.character_id and request.character_id not in known:
        return "That character isn't in the saga."
    if storyguide:
        return None
    if request.visibility == BLIND:
        return "Only the Session's storyguide rolls Blind."
    plays = {c.character_id for c in session.castings if c.player_id == who}
    if request.character_id not in plays:
        return "Roll for a character you play tonight."
    return None


def _player_of(session: Session, character_id: str) -> str:
    """Who plays `character_id` tonight, or "" for no one."""
    return next(
        (c.player_id for c in session.castings if c.character_id == character_id), ""
    )


def _character_name(saga: Saga, character_id: str) -> str:
    return next((c.name for c in saga.characters if c.id == character_id), "")


def _body(saga: Saga, request: RollRequest, result: dice.Roll) -> dict[str, Any]:
    """Everything the roll was and every die face it showed."""
    die = result.die
    return {
        "stress": die.stress,
        "faces": list(die.faces),
        "botch_faces": list(die.botch_faces),
        "die": die.value,
        "modifier": result.modifiers,
        "total": result.total,
        "botches": die.botches,
        "ease_factor": result.ease_factor,
        "succeeded": result.succeeded,
        "margin": result.margin,
        "for": request.for_what,
        "character_id": request.character_id,
        "character_name": _character_name(saga, request.character_id),
    }


def free_roll(
    book: Chronicle,
    saga: Saga,
    session: Session,
    request: RollRequest,
    *,
    by: str,
    rng: random.Random | None = None,
) -> Entry:
    """Carry out `request` once at the host and write it to the Chronicle.
    A Blind roll's number goes to the Session's storyguide alone, with a
    line for the character's player saying only that it was rolled."""
    if book.closed:
        raise ValueError("This Session has ended: its Chronicle is closed.")
    problem = why_not_roll(saga, session, request, by)
    if problem:
        raise ValueError(problem)
    result = dice.roll(
        rng or secrets.SystemRandom(),
        request.modifier,
        ease_factor=request.ease_factor,
        stress=request.stress,
        botch_dice=request.botch_dice,
        saga=saga,
    )
    audience = {
        PUBLIC: table(),
        PRIVATE: chosen(by) if by != storyguide_of(session, saga) else chosen(),
        BLIND: storyguide_only(),
    }[request.visibility]
    entry = book.add(ROLL, by, audience, _body(saga, request, result))
    player = _player_of(session, request.character_id)
    if request.visibility == BLIND and player:
        book.add(
            ROLLED,
            by,
            chosen(player),
            {
                "roll": entry.number,
                "for": request.for_what,
                "character_name": _character_name(saga, request.character_id),
            },
        )
    return entry


def void(
    book: Chronicle, session: Session, number: int, reason: str, *, by: str
) -> Entry:
    """Strike roll `number` from the count, with a reason; the roll stays.
    The Void is seen by whoever saw the roll."""
    if by != storyguide_of(session):
        raise ValueError("Only the Session's storyguide voids a roll.")
    if not reason.strip():
        raise ValueError("Say why the roll doesn't count.")
    target = next((e for e in book.entries if e.number == number), None)
    if target is None or target.kind != ROLL:
        raise ValueError("There is no such roll.")
    if number in voided(book):
        raise ValueError("That roll is already void.")
    return book.add(
        VOID, by, target.audience, {"strikes": number, "reason": reason.strip()}
    )


def voided(book: Chronicle) -> dict[int, str]:
    """The rolls struck, by number, with the reason."""
    return {e.body["strikes"]: e.body["reason"] for e in book.entries if e.kind == VOID}


# -- as text --

UNKNOWN = "Something this version can't show; update Armarius."


def _faces(body: dict[str, Any]) -> str:
    if not body["stress"]:
        return f"simple die {body['die']}"
    faces: list[int] = body["faces"]
    shown = " → ".join(str(f if i == 0 or f else 10) for i, f in enumerate(faces))
    if body["botch_faces"]:
        shown += f"; botch dice {' '.join(str(f) for f in body['botch_faces'])}"
    return f"stress die {shown}"


def _roll_line(body: dict[str, Any]) -> str:
    who = body["character_name"] or "Storyguide"
    what = f" ({body['for']})" if body["for"] else ""
    modifier = body["modifier"]
    sign = "+" if modifier >= 0 else "−"
    line = f"{who}{what}: {_faces(body)}, {sign}{abs(modifier)} = {body['total']}"
    if body["botches"]:
        line += f", botch ({body['botches']} zero{'s' if body['botches'] > 1 else ''})"
    if body["ease_factor"] is not None:
        verdict = "succeeds" if body["succeeded"] else "fails"
        line += f" against {body['ease_factor']}: {verdict}, margin {body['margin']}"
    return line


def _line(entry: Entry, struck: dict[int, str]) -> str:
    if entry.kind == BEGIN:
        return "Session begun."
    if entry.kind == END:
        return "Session ended."
    if entry.kind == ROLL:
        line = _roll_line(entry.body)
        if entry.number in struck:
            line = f"VOID ({struck[entry.number]}): {line}"
        if entry.audience.to != TABLE:
            line += " [Blind]" if entry.audience.to == STORYGUIDE else " [Private]"
        return line
    if entry.kind == ROLLED:
        who = entry.body["character_name"] or "A character"
        what = f" ({entry.body['for']})" if entry.body["for"] else ""
        return f"{who}{what}: the storyguide rolled."
    if entry.kind == VOID:
        return f"Roll {entry.body['strikes']} is void: {entry.body['reason']}"
    return UNKNOWN


def text(entries: list[Entry], book: Chronicle) -> str:
    """`entries` (as one reader sees them), a line each, as markup."""
    if not entries:
        return "Nothing yet."
    struck = voided(book)
    return "\n".join(
        escape(f"{e.number}. {e.time[11:16]}  {_line(e, struck)}")
        for e in entries
        if e.kind != VOID
    )


# -- Remote seats --


@dataclass(frozen=True)
class Feed:
    """What a seat is sent: the Session under way, and the entries after
    the one it holds that its Player may see."""

    session_id: str
    entries: list[Entry]


def feed(saga: Saga, who: str, session_id: str, since: int) -> Feed | None:
    """The entries `who` may see after `since` in Session `session_id`'s
    Chronicle, read from the file as it stands. The numbers are that
    Session's: another Session under way now is fed from its start. A
    Session ended since is fed to its end (End Session included); None
    with nothing to feed."""
    session = under_way(saga)
    if session is None or session.id != session_id:
        ended = next((s for s in saga.sessions if s.id == session_id), None)
        if ended is not None and not ended.under_way and has_chronicle(saga, ended):
            session = ended
        elif session is None:
            return None
        else:
            since = 0
    path = path_of(saga, session)
    book = Chronicle(path, _load(path))
    return Feed(
        session.id, [e for e in book.since(since) if sees(e, who, session, saga)]
    )


class SeatChronicle:
    """The Chronicle as a Remote seat holds it: what its host sent, in
    memory only (a restart asks again from the start), told to subscribers
    as it comes (Observer)."""

    def __init__(self) -> None:
        self.session_id = ""
        self.entries: list[Entry] = []
        self._listeners: list[Callable[[Entry], None]] = []

    @property
    def last(self) -> int:
        """The number of the last entry held: what to ask for after."""
        return self.entries[-1].number if self.entries else 0

    def subscribe(self, listener: Callable[[Entry], None]) -> Callable[[], None]:
        self._listeners.append(listener)

        def stop() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return stop

    def take(self, session_id: str, entry: Entry) -> None:
        """An entry the host sent; one already held is passed over, and a
        new Session's entries start afresh."""
        if session_id != self.session_id:
            self.session_id, self.entries = session_id, []
        if entry.number <= self.last:
            return
        self.entries.append(entry)
        for listener in list(self._listeners):
            listener(entry)
