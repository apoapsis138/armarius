"""A Session's Chronicle: everything rolled while it is Under way, kept by
the host in a file of its own beside the saga (ADRs 0018 and 0020).

Begin Session opens it and End Session closes it; only the Session's
storyguide does either, and at most one Session of a saga is Under way.
Every entry has the same envelope (its number within the Session, time,
kind, author, Audience, and a body by kind) and nothing is ever changed or
removed: a Strike (stored as kind `void`) is a new entry naming the roll
it takes from the count, and a Confidence spend a new entry naming the
roll it raises.

Pattern: Command. A RollRequest is what to roll, as data (for a roll from
the sheet, the Characteristic, the Ability and whether a Specialty
applies, never a number); `free_roll` carries it out once, at the host,
with the host's own source of chance, working a sheet roll's terms out
from the saga as it stands, and the Chronicle is the list of the commands
carried out. Asking again makes a second roll, never a replacement.

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
from typing import Any, Protocol

from . import paths, sessions, shapes, viewing
from .files import held_lock
from .markup import escape
from .models import Character, Saga, Session
from .models.definitions import ROLL_CHARACTERISTICS
from .rules import creation_access, derived, dice, scores

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


#: An entry to write: its kind, author, Audience and body.
Written = tuple[str, str, "Audience", dict[str, Any]]


class HasEntries(Protocol):
    """A Chronicle as a reader holds it: the host's file-backed Chronicle,
    or what a Remote seat was sent (SeatChronicle)."""

    @property
    def entries(self) -> list[Entry]: ...


class Chronicle:
    """A Session's Chronicle: its entries in order, and its file."""

    def __init__(self, path: Path, entries: list[Entry]) -> None:
        self.path = path
        self.entries = entries
        self._listeners: list[Callable[[Entry], None]] = []
        #: The file's size when last read (-1: not read here yet).
        self._read_size = -1

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
        self,
        kind: str,
        author: str,
        audience: Audience,
        body: dict[str, Any],
        then: Callable[[Entry], Written | None] | None = None,
    ) -> Entry:
        """Write a new entry at the end, flushed to the file before it
        counts: under the file's lock, after what another process wrote
        since, numbered from the file. `then` gives an entry that belongs
        with it (a Blind roll's line for its player), written in the same
        hold of the lock, so the two are on file before anyone is told."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with held_lock(_lock_of(self.path)):
            caught_up = self._catch_up(mend=True)
            if self.closed:
                self._tell(caught_up)
                raise ValueError("This Session has ended: its Chronicle is closed.")
            entry = self._write(kind, author, audience, body)
            written = [entry]
            follows = then(entry) if then is not None else None
            if follows is not None:
                written.append(self._write(*follows))
        # Subscribers are told once the lock is let go and all of it is on
        # file, so a slow or failing one never holds up the other process,
        # nor stops what belongs with the entry from being written.
        self._tell([*caught_up, *written])
        return entry

    def _write(
        self, kind: str, author: str, audience: Audience, body: dict[str, Any]
    ) -> Entry:
        """Append one entry (the file's lock held)."""
        entry = Entry(len(self.entries) + 1, clock(), kind, author, audience, body)
        with self.path.open("a", encoding="utf-8", newline="\n") as out:
            out.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
            out.flush()
            os.fsync(out.fileno())
        self.entries.append(entry)
        return entry

    def refresh(self) -> list[Entry]:
        """Catch up with what another process wrote since (Observer: each
        subscriber is told of every entry new here). A file no bigger than
        last read has nothing new, and isn't read again."""
        try:
            size = self.path.stat().st_size
        except FileNotFoundError:
            return []
        if size == self._read_size:
            return []
        fresh = self._catch_up()
        self._tell(fresh)
        return fresh

    def _catch_up(self, *, mend: bool = False) -> list[Entry]:
        """Read what is new in the file; `mend` (only with the file's lock
        held) cuts a half-written last line first."""
        found = _load(self.path, mend=mend)
        try:
            self._read_size = self.path.stat().st_size
        except FileNotFoundError:
            self._read_size = 0
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
    spend_at_end(saga, book)
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
#: A Strike: the storyguide takes a roll from the count. Stored as "void",
#: the word it was first written under, so every Chronicle file reads back.
VOID = "void"
CONFIDENCE = "confidence"

#: Extra botch dice for an Ability used with no score in it (DE p. 157).
UNTRAINED_BOTCH_DICE = 3
#: What one Confidence Point adds to a roll's total (DE p. 29).
CONFIDENCE_BONUS = 3


@dataclass(frozen=True)
class SheetRoll:
    """What a roll from the sheet asks for: a Characteristic (as the book
    names it, "Dexterity"), an Ability or none, and whether a Specialty of
    that Ability applies. The scores come from the saga at the host."""

    characteristic: str
    ability: str = ""
    specialty: bool = False


@dataclass(frozen=True)
class RollRequest:
    """A roll, as data: a stress or simple die, the modifier the roller
    typed (for a roll from the sheet, anything beyond the sheet), the
    botch dice, an optional Ease Factor, what it is for, the character it
    is for (none: the storyguide's own), who may see it (PUBLIC, PRIVATE or
    BLIND) and, for a roll from the sheet, what on the sheet it rolls."""

    stress: bool = True
    modifier: int = 0
    botch_dice: int = 1
    ease_factor: int | None = None
    for_what: str = ""
    character_id: str = ""
    visibility: str = PUBLIC
    sheet: SheetRoll | None = None


#: One part of a roll's modifier, as the roll shows it: its label and
#: its amount.
Term = tuple[str, int]


def _character(saga: Saga, character_id: str) -> Character | None:
    return next((c for c in saga.characters if c.id == character_id), None)


def why_not_act(character: Character) -> str | None:
    """Why `character` can take no action now (DE p. 404: Incapacitated;
    an Unconscious or dead character neither), or None."""
    if character.wounds.dead:
        return f"{character.name} is dead."
    if character.wounds.incapacitated:
        return f"{character.name} is Incapacitated: no actions."
    if character.fatigue_level == "unconscious":
        return f"{character.name} is Unconscious."
    return None


def sheet_terms(saga: Saga, request: RollRequest) -> tuple[list[Term], int]:
    """A roll's terms, and the botch dice it adds. For a roll from the
    sheet: the Characteristic, the Ability (+1 with its Specialty, and any
    fixed bonus such as Puissant), the wound and Fatigue penalties as the
    character's Virtues and Flaws adjust them (DE pp. 403-404), and
    anything typed beyond; an Ability with no score is rolled at 0 with
    three extra botch dice (DE p. 157). A Free roll's one term is its
    modifier. ValueError says why the sheet can't be rolled."""
    sheet = request.sheet
    if sheet is None:
        return [("Modifier", request.modifier)], 0
    character = _character(saga, request.character_id)
    if character is None:
        raise ValueError("Roll from a character's sheet.")
    if sheet.characteristic not in ROLL_CHARACTERISTICS:
        raise ValueError("Choose a Characteristic.")
    problem = why_not_act(character)
    if problem:
        raise ValueError(problem)
    value = getattr(character.characteristics, sheet.characteristic.lower())
    terms: list[Term] = [(sheet.characteristic, value)]
    extra = 0
    if sheet.ability:
        held = next((a for a in character.abilities if a.name == sheet.ability), None)
        if held is None and creation_access.needs_experience(sheet.ability):
            raise ValueError(f"{sheet.ability} can't be used without experience in it.")
        if held is None:
            terms.append((f"{sheet.ability} (no score)", 0))
            extra = UNTRAINED_BOTCH_DICE
        else:
            level, bonus = scores.ability_score(character, sheet.ability)
            terms.append((sheet.ability, level))
            if bonus:
                terms.append((f"{sheet.ability} bonus", bonus))
        if sheet.specialty:
            specialty = held.specialty if held is not None else None
            if not specialty:
                raise ValueError(
                    f"{character.name} has no Specialty in {sheet.ability}."
                )
            terms.append((f"Specialty ({specialty})", 1))
    elif sheet.specialty:
        raise ValueError("A Specialty belongs to an Ability.")
    wounds = derived.wound_penalty(character.wounds, character.virtues_flaws)
    if wounds:
        terms.append(("Wounds", wounds))
    fatigue = derived.fatigue_penalty(character.fatigue_level, character.virtues_flaws)
    if fatigue:
        terms.append(("Fatigue", fatigue))
    if request.modifier:
        terms.append(("Modifier", request.modifier))
    return terms, extra


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
    try:
        sheet_terms(saga, request)
    except ValueError as problem:
        return str(problem)
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


def _body(
    saga: Saga, request: RollRequest, result: dice.Roll, terms: list[Term]
) -> dict[str, Any]:
    """Everything the roll was, how its modifier was made, and every die
    face it showed."""
    die = result.die
    return {
        "terms": [list(term) for term in terms],
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
    return _carry_out(
        book, saga, session, request, by=by, rng=rng, player=None, links={}
    )


def _carry_out(
    book: Chronicle,
    saga: Saga,
    session: Session,
    request: RollRequest,
    *,
    by: str,
    rng: random.Random | None,
    player: str | None,
    links: dict[str, Any],
) -> Entry:
    """Roll `request` once (already checked) and write it: a Private roll
    seen by its roller, a Blind one's line told to `player` (None: whoever
    plays the character tonight). `links` join the roll's body (the Roll
    request it answers)."""
    terms, extra = sheet_terms(saga, request)
    result = dice.roll(
        rng or secrets.SystemRandom(),
        sum(amount for _label, amount in terms),
        ease_factor=request.ease_factor,
        stress=request.stress,
        botch_dice=request.botch_dice + extra if request.stress else 0,
        saga=saga,
    )
    body = _body(saga, request, result, terms) | links
    return _write_roll(
        book,
        saga,
        session,
        ROLL,
        body,
        visibility=request.visibility,
        character_id=request.character_id,
        for_what=request.for_what,
        by=by,
        player=player,
    )


def _write_roll(
    book: Chronicle,
    saga: Saga,
    session: Session,
    kind: str,
    body: dict[str, Any],
    *,
    visibility: str,
    character_id: str,
    for_what: str,
    by: str,
    player: str | None,
) -> Entry:
    """Write a roll of `kind` seen as `visibility` says: a Private roll by
    its roller, a Blind one by the storyguide alone, with a line told to
    `player` (None: whoever plays the character tonight) that it was
    rolled."""
    if player is None:
        player = _player_of(session, character_id)
        roller = by if by != storyguide_of(session, saga) else ""
    else:
        roller = player
    audience = {
        PUBLIC: table(),
        PRIVATE: chosen(roller) if roller else chosen(),
        BLIND: storyguide_only(),
    }[visibility]
    # Worked out before anything is written, so nothing can fail between
    # the roll and its line.
    name = _character_name(saga, character_id)
    blind = visibility == BLIND and bool(player)

    def rolled(roll: Entry) -> Written | None:
        if not blind:
            return None
        told = {"roll": roll.number, "for": for_what, "character_name": name}
        return (ROLLED, by, chosen(player), told)

    return book.add(kind, by, audience, body, then=rolled)


# -- Table rolls made from a form --

#: A Table roll made from one of the app's rolling forms (table_rolls.py).
FORM_ROLL = "form_roll"


def why_not_form_roll(
    saga: Saga, session: Session, character_id: str, visibility: str, who: str
) -> str | None:
    """Why `who` may not make a Table roll from a form, or None: only the
    Session's storyguide rolls Blind."""
    if visibility not in (PUBLIC, PRIVATE, BLIND):
        return "Choose who sees the roll."
    if character_id and _character(saga, character_id) is None:
        return "That character isn't in the saga."
    if visibility == BLIND and who != storyguide_of(session, saga):
        return "Only the Session's storyguide rolls Blind."
    return None


def form_roll(
    book: Chronicle,
    saga: Saga,
    session: Session,
    *,
    form: str,
    character_id: str,
    visibility: str,
    faces: list[int],
    lines: list[str],
    by: str,
    cancelled: bool = False,
) -> Entry:
    """Write a Table roll made from a form: the form's name, the
    character, every face the host drew for it in order, and the form's
    own result lines, word for word. A form cancelled after drawing is
    written all the same, with no result, so nobody re-rolls by
    cancelling."""
    if book.closed:
        raise ValueError("This Session has ended: its Chronicle is closed.")
    problem = why_not_form_roll(saga, session, character_id, visibility, by)
    if problem:
        raise ValueError(problem)
    body: dict[str, Any] = {
        "form": form,
        "character_id": character_id,
        "character_name": _character_name(saga, character_id),
        "faces": list(faces),
        "lines": [] if cancelled else list(lines),
        "cancelled": cancelled,
    }
    return _write_roll(
        book,
        saga,
        session,
        FORM_ROLL,
        body,
        visibility=visibility,
        character_id=character_id,
        for_what=form,
        by=by,
        player=None,
    )


def form_roll_line(body: dict[str, Any]) -> str:
    """A form's Table roll as a line: the form, the character, the dice
    and the form's own result."""
    who = f", {body['character_name']}" if body.get("character_name") else ""
    shown = " ".join(str(face) for face in body["faces"])
    if body.get("cancelled"):
        return f"{body['form']}{who}: dice {shown}; drawn, then cancelled."
    said = " ".join(str(line) for line in body.get("lines", []))
    return f"{body['form']}{who}: dice {shown}; {said}".rstrip("; ")


#: The kinds of entry a Strike may take from the count: rolls.
STRIKABLE = frozenset({ROLL, FORM_ROLL})


def strike(
    book: Chronicle,
    session: Session,
    number: int,
    reason: str,
    *,
    by: str,
    saga: Saga | None = None,
) -> Entry:
    """Strike roll `number` from the count, with a reason; the roll stays.
    The Strike is seen by whoever saw the roll."""
    if by != storyguide_of(session, saga):
        raise ValueError("Only the Session's storyguide strikes a roll.")
    if not reason.strip():
        raise ValueError("Say why the roll doesn't count.")
    target = next((e for e in book.entries if e.number == number), None)
    if target is None or target.kind not in STRIKABLE:
        raise ValueError("There is no such roll.")
    if number in voided(book):
        raise ValueError("That roll is already struck.")
    return book.add(
        VOID, by, target.audience, {"strikes": number, "reason": reason.strip()}
    )


def voided(book: HasEntries) -> dict[int, str]:
    """The rolls struck, by number, with the reason."""
    return {e.body["strikes"]: e.body["reason"] for e in book.entries if e.kind == VOID}


# -- Confidence --


def confidence_spent(book: HasEntries, character_id: str, on: int | None = None) -> int:
    """The Confidence Points spent for `character_id` in this Chronicle
    (on roll `on` alone, when given)."""
    return sum(
        int(e.body["points"])
        for e in book.entries
        if e.kind == CONFIDENCE
        and e.body.get("character_id") == character_id
        and (on is None or e.body.get("roll") == on)
    )


def confidence_left(book: HasEntries, character: Character) -> int:
    """The Confidence Points `character` has left this Session: the
    record's, less what this Chronicle has spent (the record falls at End
    Session)."""
    return max(
        0, character.background.confidence_points - confidence_spent(book, character.id)
    )


def why_not_spend(
    book: HasEntries,
    saga: Saga,
    session: Session,
    number: int,
    points: int,
    who: str,
) -> str | None:
    """Why `who` may not spend `points` Confidence on roll `number`, or
    None when they may (DE p. 29): after the roll, on one that didn't
    botch and isn't struck, up to the character's Confidence Score on any
    one roll, out of the points left; by one who may roll for the
    character and sees the roll's number."""
    target = next((e for e in book.entries if e.number == number), None)
    if target is None or target.kind != ROLL:
        return "There is no such roll."
    if number in voided(book):
        return "That roll is struck."
    if target.body.get("botches"):
        return "Confidence can't be spent on a botch."
    character = _character(saga, str(target.body.get("character_id") or ""))
    if character is None:
        return "Only a character's roll takes Confidence."
    if not sees(target, who, session, saga):
        return "Only someone who sees the roll's number spends Confidence on it."
    plays = {c.character_id for c in session.castings if c.player_id == who}
    if who != storyguide_of(session, saga) and character.id not in plays:
        return "Spend Confidence for a character you play tonight."
    if points < 1:
        return "Spend at least one point."
    on_this = confidence_spent(book, character.id, number)
    if on_this + points > character.background.confidence_score:
        return (
            f"At most {character.background.confidence_score} on one roll "
            "(the Confidence Score)."
        )
    left = confidence_left(book, character)
    if points > left:
        return f"{character.name} has {left} Confidence left."
    return None


def spend_confidence(
    book: Chronicle,
    saga: Saga,
    session: Session,
    number: int,
    points: int,
    *,
    by: str,
) -> Entry:
    """Spend `points` Confidence on roll `number`: a new entry naming the
    roll, +3 a point (DE p. 29), seen by whoever saw the roll."""
    problem = why_not_spend(book, saga, session, number, points, by)
    if problem:
        raise ValueError(problem)
    target = next(e for e in book.entries if e.number == number)
    character_id = str(target.body["character_id"])
    raised = confidence_spent(book, character_id, number) + points
    total = int(target.body["total"]) + CONFIDENCE_BONUS * raised
    ease = target.body.get("ease_factor")
    body: dict[str, Any] = {
        "roll": number,
        "character_id": character_id,
        "character_name": target.body.get("character_name", ""),
        "points": points,
        "total": total,
        "ease_factor": ease,
        "succeeded": total >= ease if isinstance(ease, int) else None,
        "margin": total - ease if isinstance(ease, int) else None,
    }
    return book.add(CONFIDENCE, by, target.audience, body)


# -- Roll requests --

REQUEST = "request"
#: The Ease Factor a Roll request keeps from its players: the storyguide's
#: alone, written beside the request.
REQUEST_EASE = "request_ease"
OUTCOME = "outcome"


@dataclass(frozen=True)
class RollCall:
    """A Roll request (the glossary's): the storyguide's call for chosen
    characters to roll a Characteristic, with an Ability or none, what it
    is for, who sees each answer, and an Ease Factor the storyguide may
    keep to themselves. `rollers` names, for this request only, who rolls
    a character in place of whoever would (a shared grog handed over)."""

    characters: tuple[str, ...]
    characteristic: str
    ability: str = ""
    ease_factor: int | None = None
    hide_ease: bool = False
    visibility: str = BLIND
    for_what: str = ""
    stress: bool = True
    rollers: dict[str, str] = field(default_factory=dict)


def answerer(saga: Saga, session: Session, character_id: str) -> str:
    """Who answers a Roll request for `character_id` tonight: whoever plays
    it, else (a character no Player is named on) its Steward, else the
    Session's storyguide."""
    player = _player_of(session, character_id)
    if player:
        return player
    character = _character(saga, character_id)
    keeper = sessions.steward(saga, character) if character is not None else None
    if keeper is not None:
        return keeper.id
    return storyguide_of(session, saga)


def _rollers(saga: Saga, session: Session, call: RollCall) -> dict[str, str]:
    """Each character of `call` and who answers it."""
    return {
        c: call.rollers.get(c) or answerer(saga, session, c) for c in call.characters
    }


def why_not_call(saga: Saga, session: Session, call: RollCall, who: str) -> str | None:
    """Why `who` may not make Roll request `call`, or None when they may."""
    if who != storyguide_of(session, saga):
        return "Only the Session's storyguide makes a Roll request."
    if not call.characters:
        return "Choose who rolls."
    if call.characteristic not in ROLL_CHARACTERISTICS:
        return "Choose a Characteristic."
    if call.visibility not in (PUBLIC, PRIVATE, BLIND):
        return "Choose who sees the rolls."
    known = {c.id for c in saga.characters}
    if any(c not in known for c in call.characters):
        return "That character isn't in the saga."
    players = {p.id for p in saga.players} | {storyguide_of(session, saga)}
    if any(p not in players for p in call.rollers.values()):
        return "That Player isn't in the saga."
    return None


def request_rolls(
    book: Chronicle, saga: Saga, session: Session, call: RollCall, *, by: str
) -> Entry:
    """Make Roll request `call` (a Macro Command: each character's answer
    is a roll of its own, pointing back at it). The request is seen by
    whoever sees its rolls; a hidden Ease Factor is written beside it for
    the storyguide alone."""
    if book.closed:
        raise ValueError("This Session has ended: its Chronicle is closed.")
    problem = why_not_call(saga, session, call, by)
    if problem:
        raise ValueError(problem)
    rollers = _rollers(saga, session, call)
    shown = sorted({p for p in rollers.values() if p != storyguide_of(session, saga)})
    audience = table() if call.visibility == PUBLIC else chosen(*shown)
    body: dict[str, Any] = {
        "characters": [
            {"id": c, "name": _character_name(saga, c), "roller": rollers[c]}
            for c in call.characters
        ],
        "characteristic": call.characteristic,
        "ability": call.ability,
        "ease_factor": None if call.hide_ease else call.ease_factor,
        "visibility": call.visibility,
        "for": call.for_what,
        "stress": call.stress,
    }
    hidden = call.hide_ease and call.ease_factor is not None

    def ease(entry: Entry) -> Written | None:
        if not hidden:
            return None
        return (
            REQUEST_EASE,
            by,
            storyguide_only(),
            {"request": entry.number, "ease_factor": call.ease_factor},
        )

    return book.add(REQUEST, by, audience, body, then=ease)


def _request(book: HasEntries, number: int) -> Entry | None:
    found = next((e for e in book.entries if e.number == number), None)
    return found if found is not None and found.kind == REQUEST else None


def hidden_ease(book: HasEntries, number: int) -> int | None:
    """Roll request `number`'s Ease Factor kept from its players (for the
    storyguide's eyes), or None."""
    return next(
        (
            int(e.body["ease_factor"])
            for e in book.entries
            if e.kind == REQUEST_EASE and e.body.get("request") == number
        ),
        None,
    )


def answers(book: HasEntries, number: int) -> list[Entry]:
    """The rolls that answer Roll request `number`, in order."""
    return [
        e for e in book.entries if e.kind == ROLL and e.body.get("request") == number
    ]


def roller_of(request: Entry, character_id: str) -> str:
    """Who answers `request` for `character_id`, as the request says."""
    return next(
        (
            str(c["roller"])
            for c in request.body.get("characters", [])
            if c.get("id") == character_id
        ),
        "",
    )


def why_not_answer(
    book: HasEntries,
    saga: Saga,
    session: Session,
    number: int,
    character_id: str,
    who: str,
) -> str | None:
    """Why `who` may not answer Roll request `number` for `character_id`."""
    request = _request(book, number)
    if request is None:
        return "There is no such Roll request."
    if not any(c.get("id") == character_id for c in request.body["characters"]):
        return "That character isn't asked to roll."
    if any(e.body.get("character_id") == character_id for e in answers(book, number)):
        return "That character has answered already."
    if who not in (roller_of(request, character_id), storyguide_of(session, saga)):
        return "Another Player rolls for that character."
    character = _character(saga, character_id)
    if character is None:
        return "That character isn't in the saga."
    return why_not_act(character)


def answer(
    book: Chronicle,
    saga: Saga,
    session: Session,
    number: int,
    character_id: str,
    *,
    by: str,
    specialty: bool = False,
    rng: random.Random | None = None,
) -> Entry:
    """Answer Roll request `number` for `character_id`: one roll from the
    sheet, at the host, seen as the request says (a Blind one's line told
    to whoever answers), pointing back at the request. A hidden Ease
    Factor isn't in the roll: the storyguide reads it beside the request."""
    if book.closed:
        raise ValueError("This Session has ended: its Chronicle is closed.")
    problem = why_not_answer(book, saga, session, number, character_id, by)
    if problem:
        raise ValueError(problem)
    request = _request(book, number)
    assert request is not None
    body = request.body
    rolled = RollRequest(
        stress=bool(body.get("stress", True)),
        botch_dice=1 if body.get("stress", True) else 0,
        ease_factor=body.get("ease_factor"),
        for_what=str(body.get("for", "")),
        character_id=character_id,
        visibility=str(body["visibility"]),
        sheet=SheetRoll(str(body["characteristic"]), str(body["ability"]), specialty),
    )
    sheet_terms(saga, rolled)  # a Specialty the character lacks says so
    roller = roller_of(request, character_id)
    player = "" if roller == storyguide_of(session, saga) else roller
    return _carry_out(
        book,
        saga,
        session,
        rolled,
        by=by,
        rng=rng,
        player=player,
        links={"request": number},
    )


def note_outcome(
    book: Chronicle,
    session: Session,
    number: int,
    text: str,
    *,
    by: str,
    saga: Saga | None = None,
) -> Entry:
    """The storyguide's note of what came of Roll request `number`, seen
    by whoever saw the request."""
    if by != storyguide_of(session, saga):
        raise ValueError("Only the Session's storyguide notes an outcome.")
    request = _request(book, number)
    if request is None:
        raise ValueError("There is no such Roll request.")
    if not text.strip():
        raise ValueError("Say what came of it.")
    return book.add(
        OUTCOME, by, request.audience, {"request": number, "text": text.strip()}
    )


def request_line(body: dict[str, Any]) -> str:
    """A Roll request's line."""
    what = body["characteristic"]
    if body.get("ability"):
        what += f" + {body['ability']}"
    who = ", ".join(str(c["name"]) for c in body["characters"])
    line = f"Roll request: {what} for {who}"
    if body.get("for"):
        line += f" ({body['for']})"
    if body.get("ease_factor") is not None:
        line += f", against {body['ease_factor']}"
    return line


def spend_at_end(saga: Saga, book: HasEntries) -> None:
    """Take what the evening spent off each character's Confidence Points."""
    for character in saga.characters:
        spent = confidence_spent(book, character.id)
        if spent:
            character.background.confidence_points = max(
                0, character.background.confidence_points - spent
            )


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


def _signed(amount: int) -> str:
    return f"+{amount}" if amount >= 0 else f"−{abs(amount)}"


def terms_of(body: dict[str, Any]) -> list[Term]:
    """A roll's terms as its entry keeps them; a Free roll written before
    terms were kept has its modifier as its one term."""
    kept = body.get("terms")
    if not isinstance(kept, list):
        return [("Modifier", int(body["modifier"]))]
    return [(str(label), int(amount)) for label, amount in kept]


def terms_text(terms: list[Term]) -> str:
    """A sheet roll's terms as a line ("Dexterity +2, Athletics +3,
    Wounds −1"); a Free roll's modifier alone ("+3")."""
    if len(terms) == 1 and terms[0][0] == "Modifier":
        return _signed(terms[0][1])
    return ", ".join(f"{label} {_signed(amount)}" for label, amount in terms)


def _roll_line(body: dict[str, Any]) -> str:
    who = body["character_name"] or "Storyguide"
    what = f" ({body['for']})" if body["for"] else ""
    line = (
        f"{who}{what}: {_faces(body)}, {terms_text(terms_of(body))} = {body['total']}"
    )
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
    if entry.kind in STRIKABLE:
        line = (
            _roll_line(entry.body) if entry.kind == ROLL else form_roll_line(entry.body)
        )
        if entry.number in struck:
            line = f"STRUCK ({struck[entry.number]}): {line}"
        if entry.audience.to != TABLE:
            line += " [Blind]" if entry.audience.to == STORYGUIDE else " [Private]"
        return line
    if entry.kind == ROLLED:
        who = entry.body["character_name"] or "A character"
        what = f" ({entry.body['for']})" if entry.body["for"] else ""
        return f"{who}{what}: the storyguide rolled."
    if entry.kind == VOID:
        return f"Roll {entry.body['strikes']} is struck: {entry.body['reason']}"
    if entry.kind == CONFIDENCE:
        return confidence_line(entry.body)
    if entry.kind == REQUEST:
        return request_line(entry.body)
    if entry.kind == REQUEST_EASE:
        return (
            f"Request {entry.body['request']}'s Ease Factor, kept from its "
            f"players: {entry.body['ease_factor']}"
        )
    if entry.kind == OUTCOME:
        return f"Request {entry.body['request']}: {entry.body['text']}"
    return UNKNOWN


def confidence_line(body: dict[str, Any]) -> str:
    """A Confidence spend's line."""
    who = body["character_name"] or "A character"
    points = int(body["points"])
    line = (
        f"{who} spends {points} Confidence on roll {body['roll']}: "
        f"+{CONFIDENCE_BONUS * points}, now {body['total']}"
    )
    if body.get("ease_factor") is not None:
        verdict = "succeeds" if body["succeeded"] else "fails"
        line += f", {verdict}, margin {body['margin']}"
    return line


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
        self._cleared: list[Callable[[], None]] = []

    def clear(self, session_id: str = "") -> None:
        """Hold nothing (a new Session's start): subscribers are told by
        `cleared`, so a pane draws itself again."""
        self.session_id, self.entries = session_id, []
        for listener in list(self._cleared):
            listener()

    def when_cleared(self, listener: Callable[[], None]) -> Callable[[], None]:
        self._cleared.append(listener)

        def stop() -> None:
            if listener in self._cleared:
                self._cleared.remove(listener)

        return stop

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
            self.clear(session_id)
        if entry.number <= self.last:
            return
        self.entries.append(entry)
        for listener in list(self._listeners):
            listener(entry)


def for_reader(
    book: HasEntries, who: str, session: Session, saga: Saga | None = None
) -> list[Entry]:
    """The entries `who` reads, in order: those they may see, less the
    line telling a player a Blind roll was made, for the Session's
    storyguide, who has the roll itself."""
    return [e for e in book.entries if reads(e, who, session, saga)]


def reads(entry: Entry, who: str, session: Session, saga: Saga | None = None) -> bool:
    """Whether `who` reads `entry` (for_reader, one entry at a time)."""
    if entry.kind == ROLLED and who == storyguide_of(session, saga):
        return False
    return sees(entry, who, session, saga)


def line(entry: Entry, struck: dict[int, str]) -> str:
    """`entry`'s line, as the Chronicle reads (plain text, not markup);
    `struck` is `voided(book)`, worked out once for all the lines drawn."""
    return _line(entry, struck)


def calls_attention(
    entry: Entry, who: str, session: Session, saga: Saga | None = None
) -> bool:
    """Whether `entry` is meant for `who` alone enough to call a collapsed
    pane's attention: a Blind roll's number for the Session's storyguide,
    or the line telling a player one was rolled for their character."""
    if entry.kind in STRIKABLE and entry.audience.to == STORYGUIDE:
        return who == storyguide_of(session, saga)
    if entry.kind == ROLLED:
        return who in entry.audience.players
    return False
