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
import re
import secrets
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Protocol

from . import dice_text, paths, references, sessions, shapes, table_rules, viewing
from .files import held_lock
from .markup import escape
from .models import SUPERNATURAL_CATEGORIES, Character, Saga, Session
from .models.definitions import ROLL_CHARACTERISTICS
from .rules import creation_access, derived, dice, realms, scores

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


#: Who runs a Session; the rule lives with the Table's other rules.
storyguide_of = table_rules.storyguide_of


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
    """One line of a Chronicle. `for_you`: at a Remote seat, whether its
    host said the entry is for the seat's Player (ADR 0031); None in the
    host's own Chronicle, which works it out (for_whom), and never on file."""

    number: int
    time: str
    kind: str
    author: str
    audience: Audience
    body: dict[str, Any] = field(default_factory=dict)
    # Not part of what the entry is: a seat's copy equals the host's.
    for_you: bool | None = field(default=None, compare=False)


def _on_file(entry: Entry) -> dict[str, Any]:
    """`entry` as the Chronicle file keeps it."""
    kept = asdict(entry)
    del kept["for_you"]
    return kept


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
        problem = typed_problem(kind, body)
        if problem:
            raise ValueError(problem)
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
            out.write(json.dumps(_on_file(entry), ensure_ascii=False) + "\n")
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

PUBLIC = table_rules.PUBLIC
PRIVATE = table_rules.PRIVATE
BLIND = table_rules.BLIND

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
    #: The aura it is rolled in, for a supernatural Ability (scene_aura):
    #: its score and realm ("" for none), and whether in a regio.
    aura: int = 0
    aura_realm: str = ""
    in_regio: bool = False


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


why_not_act = table_rules.why_not_act


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
        aura = _aura_term(sheet)
        if aura is not None:
            terms.append(aura[0])
            extra += aura[1]
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


def supernatural(ability: str) -> bool:
    """Whether `ability` is a Supernatural Ability or a hedge Art, which an
    aura touches (DE p. 411)."""
    return bool(ability) and (
        creation_access.ability_category(ability) in SUPERNATURAL_CATEGORIES
    )


def _aura_term(sheet: SheetRoll) -> tuple[Term, int] | None:
    """The aura's term on a supernatural Ability, taken as Magic (most are,
    DE p. 411), and the botch dice a foreign realm's aura adds: one a point
    of the aura as it is, twice that in a regio (DE pp. 411, 422). None
    for a mundane Ability, or no aura."""
    if not sheet.aura_realm or not supernatural(sheet.ability):
        return None
    realm, score = sheet.aura_realm, sheet.aura
    modifier = realms.aura_modifier(realms.HERMETIC, realm, score)
    botch = realms.extra_botch_dice(
        realms.HERMETIC, realm, score, in_regio=sheet.in_regio
    )
    return (f"Aura, {realm} {score}", modifier), botch


def why_not_roll(
    saga: Saga, session: Session, request: RollRequest, who: str
) -> str | None:
    """Why `who` may not make `request` at `session`, or None when they may:
    a player rolls only for a character they play tonight, the Session's
    storyguide for any character or none; only the storyguide rolls Blind."""
    if request.botch_dice < 0:
        return "Botch dice can't be fewer than none."
    words = typed_problem(ROLL, {"for": request.for_what})
    if words:
        return words
    problem = table_rules.why_not_roll_for(
        saga, session, who, request.character_id, request.visibility
    )
    if problem:
        return problem
    try:
        sheet_terms(saga, request)
    except ValueError as problem:
        return str(problem)
    return None


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
        player = table_rules.player_of(session, character_id)
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
    """Why `who` may not make a Table roll from a form, or None: the same
    who-may rule as every roll (table_rules), and a character who can't act
    rolls nothing. A form for no one in particular (a roll on a table) is
    anyone's to roll."""
    problem = table_rules.why_not_roll_for(
        saga, session, who, character_id, visibility, for_no_one=True
    )
    if problem:
        return problem
    character = _character(saga, character_id) if character_id else None
    return table_rules.why_not_act(character) if character is not None else None


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
    whole_dice: list[dict[str, Any]] | None = None,
) -> Entry:
    """Write a Table roll made from a form: the form's name, the
    character, every face the host drew for it in order (and `whole_dice`, the
    same faces as whole dice, when they are known), and the form's own
    result lines, word for word. A form cancelled after drawing is
    written all the same, with no result, so nobody re-rolls by
    cancelling."""
    problem = why_not_form_roll(saga, session, character_id, visibility, by)
    if problem:
        raise ValueError(problem)
    body: dict[str, Any] = {
        "form": form,
        "character_id": character_id,
        "character_name": _character_name(saga, character_id),
        "faces": list(faces),
        **({"dice": [dict(d) for d in whole_dice]} if whole_dice is not None else {}),
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
    kept = body.get("dice")
    if isinstance(kept, list):
        shown = dice_text.dice_text(kept)
    else:  # written before whole dice were kept
        shown = "dice " + " ".join(str(face) for face in body["faces"])
    if body.get("cancelled"):
        return f"{body['form']}{who}: {shown}; drawn, then cancelled."
    said = " ".join(str(line) for line in body.get("lines", []))
    return f"{body['form']}{who}: {shown}; {said}".rstrip("; ")


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
    words = typed_problem(VOID, {"reason": reason})
    if words:
        raise ValueError(words)
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
    if who != storyguide_of(session, saga) and character.id not in table_rules.plays(
        session, who
    ):
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
    #: The aura each answer is rolled in, for a supernatural Ability: kept
    #: at the host, never sent a seat (the storyguide may keep it).
    aura: int = 0
    aura_realm: str = ""
    in_regio: bool = False


def answerer(saga: Saga, session: Session, character_id: str) -> str:
    """Who answers a Roll request for `character_id` tonight: whoever plays
    it, else (a character no Player is named on) its Steward, else the
    Session's storyguide."""
    player = table_rules.player_of(session, character_id)
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
    if call.visibility not in table_rules.VISIBILITIES:
        return "Choose who sees the rolls."
    words = typed_problem(REQUEST, {"for": call.for_what})
    if words:
        return words
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
    if call.aura_realm:
        body["aura"] = {
            "score": call.aura,
            "realm": call.aura_realm,
            "regio": call.in_regio,
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
    problem = why_not_answer(book, saga, session, number, character_id, by)
    if problem:
        raise ValueError(problem)
    request = _request(book, number)
    assert request is not None
    body = request.body
    kept = body.get("aura")
    aura: dict[str, Any] = kept if isinstance(kept, dict) else {}
    rolled = RollRequest(
        stress=bool(body.get("stress", True)),
        botch_dice=1 if body.get("stress", True) else 0,
        ease_factor=body.get("ease_factor"),
        for_what=str(body.get("for", "")),
        character_id=character_id,
        visibility=str(body["visibility"]),
        sheet=SheetRoll(
            str(body["characteristic"]),
            str(body["ability"]),
            specialty,
            aura=int(aura.get("score", 0)),
            aura_realm=str(aura.get("realm", "")),
            in_regio=aura.get("regio") is True,
        ),
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
    words = typed_problem(OUTCOME, {"text": text})
    if words:
        raise ValueError(words)
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


# -- Messages --

MESSAGE = "message"
#: The most characters a Message's words may hold.
MESSAGE_LIMIT = 2000
#: The most records one Message may link.
LINKS_LIMIT = 20
#: The longest body (as JSON text) a seat's event frame carries
#: (remote/events.MAX_BODY); a Message bigger than this is refused.
ENTRY_LIMIT = 8_000


def at_session(saga: Saga, session: Session) -> list[str]:
    """Who is at `session` to be sent a Message, each once: its
    storyguide, and every Player not Away (another storyguide of the
    troupe counts as a Player)."""
    away = set(session.away)
    return list(
        dict.fromkeys(
            [
                storyguide_of(session, saga),
                *(p.id for p in saga.players if p.id not in away),
            ]
        )
    )


def name_at(saga: Saga, session: Session, who: str) -> str:
    """`who` as a Message names them: the storyguide, or a Player's name."""
    if who == viewing.HOST:
        return "the storyguide"
    found = next((p.name for p in saga.players if p.id == who), "")
    return found or session.names.get(who, who)


def viewer_of(saga: Saga, who: str) -> viewing.Viewer:
    """The viewer a person at a Session reads as: the host's window as
    storyguide, a Player as themselves, anyone else as the table."""
    if who == viewing.HOST:
        return viewing.STORYGUIDE_VIEWER
    player = next((p for p in saga.players if p.id == who), None)
    if player is None:
        return viewing.TABLE_VIEWER
    return viewing.viewer_for(player, hosts=False)


def _named_at(words: str, name: str) -> int:
    """Where `name` is written in `words` as a whole word, or -1."""
    found = re.search(rf"(?<!\w){re.escape(name)}(?!\w)", words)
    return found.start() if found is not None else -1


def _link_problem(
    saga: Saga, words: str, links: tuple[references.Ref, ...], who: str
) -> str | None:
    if len(links) > LINKS_LIMIT:
        return f"A Message links at most {LINKS_LIMIT} records."
    if len({(link.kind, link.id) for link in links}) < len(links):
        return "Link each record once."
    looking = viewer_of(saga, who)
    for link in links:
        record = references.target(saga, link)
        if record is None or not viewing.readable(looking, record, saga):
            return "Link only records you may open."
        if _named_at(words, link.name) < 0:
            return "A linked record's name must be in the Message."
    return None


def why_not_message(
    saga: Saga,
    session: Session,
    words: str,
    to: tuple[str, ...],
    who: str,
    *,
    links: tuple[references.Ref, ...] = (),
) -> str | None:
    """Why `who` may not send `words` to `to` (none: the Table), or None:
    anyone at the Session sends one, to people at it, in plain words,
    linking only records they may open, by the names written."""
    here_now = at_session(saga, session)
    if who not in here_now:
        return "Only someone at the Session sends a Message."
    if not words.strip():
        return "Write the Message."
    if len(words) > MESSAGE_LIMIT:
        return f"A Message holds at most {MESSAGE_LIMIT} characters."
    problem = typed_problem(MESSAGE, {"words": words})
    if problem:
        return problem
    if any(t not in here_now for t in to):
        return "Whisper only to people at the Session."
    if to and set(to) == {who}:
        return "Whisper to someone besides yourself."
    problem = _link_problem(saga, words, links, who)
    if problem:
        return problem
    if len(json.dumps(_message_body(saga, session, words, to, links, who))) > (
        ENTRY_LIMIT
    ):
        return "This Message is too long to send to the seats."
    return None


def _message_body(
    saga: Saga,
    session: Session,
    words: str,
    to: tuple[str, ...],
    links: tuple[references.Ref, ...],
    by: str,
) -> dict[str, Any]:
    whispered = [t for t in dict.fromkeys(to) if t != by]
    return {
        "words": words,
        "author_name": name_at(saga, session, by),
        "to": whispered,
        "to_names": [name_at(saga, session, t) for t in whispered],
        "links": [[link.kind, link.id, link.name] for link in links],
    }


def message(
    book: Chronicle,
    saga: Saga,
    session: Session,
    words: str,
    *,
    to: tuple[str, ...] = (),
    links: tuple[references.Ref, ...] = (),
    by: str,
) -> Entry:
    """Write a Message from `by`: to the Table, or, naming `to`, a Whisper
    those people and the Session's storyguide see, with the records it
    links. It is written once and stays as sent."""
    problem = why_not_message(saga, session, words, to, by, links=links)
    if problem:
        raise ValueError(problem)
    audience = chosen(*dict.fromkeys(t for t in (by, *to))) if to else table()
    body = _message_body(saga, session, words, to, links, by)
    return book.add(MESSAGE, by, audience, body)


def _links_of(body: dict[str, Any]) -> tuple[references.Ref, ...]:
    return tuple(
        references.Ref(str(kind), str(record_id), str(name))
        for kind, record_id, name in body.get("links", [])
    )


def message_label(body: dict[str, Any]) -> str:
    """Who a Message is from, and for a Whisper to whom ("Ana, whispering
    to Ben")."""
    author = str(body["author_name"])
    author = author[:1].upper() + author[1:]
    to_names = [str(n) for n in body.get("to_names", [])]
    if not to_names:
        return author
    return f"{author}, whispering to {', '.join(to_names)}"


def message_fact(entry: Entry, saga: Saga, viewer: viewing.Viewer) -> references.Fact:
    """A Message as `viewer` reads it: who it is from and to, its words as
    written, and a link for each record named that they may open now (one
    they may not, or one gone, stays its name in plain words)."""
    body = entry.body
    words = str(body["words"])
    shown = sorted(
        (
            link
            for link in _links_of(body)
            if (record := references.target(saga, link)) is not None
            and viewing.readable(viewer, record, saga)
        ),
        key=lambda link: _named_at(words, link.name),
    )
    return references.Fact(message_label(body), words, tuple(shown))


# -- Shows --

SHOW = "show"


@dataclass(frozen=True)
class ShowCall:
    """A Show, as data (the glossary's): its title, what is shown (a
    record, or a picture already in the saga as its folder and file name),
    the Players shown (none: the Table) and the open story it belongs to,
    by id, if any. The host builds the one frozen copy (shows.py)."""

    title: str
    record: references.Ref | None = None
    picture: tuple[str, str] | None = None
    to: tuple[str, ...] = ()
    story_id: str = ""


def show_line(body: dict[str, Any]) -> str:
    """A Show's line: its title, and to whom for chosen Players."""
    line = f"The storyguide shows: {body['title']}"
    names = [str(n) for n in body.get("to_names", [])]
    return f"{line} (to {', '.join(names)})" if names else line


# -- Scenes --

SCENE_SET = "scene set"
SCENE_ENDED = "scene ended"


@dataclass(frozen=True)
class SceneCall:
    """Set a Scene, as data: which of the Session's uses of a Scene to
    play (by its id), and whether the table is told its aura. The host
    writes the banner from the saga (scene_play.py)."""

    use_id: str
    tell_aura: bool = False


def scene_set_line(body: dict[str, Any]) -> str:
    """A banner's line: the Scene's title and place, and its aura when the
    table was told it."""
    line = f"Scene: {body['title']}, at {body['place']}"
    return f"{line} (aura {body['aura']})" if "aura" in body else line


# -- words typed into the Chronicle --


def typed_problem(kind: str, body: dict[str, Any]) -> str | None:
    """Why an entry of `kind` may not keep `body`'s typed words (a text,
    or each of a list of texts), or None."""
    for key in TYPED.get(kind, ()):
        value = body.get(key)
        texts = value if isinstance(value, list) else [value]
        for text in texts:
            if isinstance(text, str) and (problem := shapes.why_not_words(text)):
                return problem
    return None


# -- as text --

UNKNOWN = "Something this version can't show; update Armarius."


def die_of(body: Mapping[str, Any]) -> dice.DieResult:
    """A roll entry's die, as `rules.dice` made it."""
    return dice.DieResult(
        value=int(body["die"]),
        faces=tuple(int(face) for face in body["faces"]),
        stress=bool(body["stress"]),
        botch_faces=tuple(int(face) for face in body["botch_faces"]),
    )


def terms_of(body: dict[str, Any]) -> list[Term]:
    """A roll's terms as its entry keeps them; a Free roll written before
    terms were kept has its modifier as its one term."""
    kept = body.get("terms")
    if not isinstance(kept, list):
        return [("Modifier", int(body["modifier"]))]
    return [(str(label), int(amount)) for label, amount in kept]


#: A roll's terms as a line (dice_text's, kept here for its callers).
terms_text = dice_text.terms_text


def _roll_line(body: dict[str, Any]) -> str:
    who = body["character_name"] or "Storyguide"
    what = f" ({body['for']})" if body["for"] else ""
    said = dice_text.dice_line(
        die_of(body), terms_of(body), int(body["total"]), body["ease_factor"]
    )
    return f"{who}{what}: {said}"


def _line(entry: Entry, struck: dict[int, str]) -> str:
    spec = KINDS.get(entry.kind)
    if spec is None:
        return UNKNOWN
    line = spec.line(entry.body)
    if spec.strikable:
        if entry.number in struck:
            line = f"STRUCK ({struck[entry.number]}): {line}"
        tag = visibility_tag(entry.audience)
        if tag:
            line += f" [{tag}]"
    return line


def _rolled_line(body: dict[str, Any]) -> str:
    who = body["character_name"] or "A character"
    what = f" ({body['for']})" if body["for"] else ""
    return f"{who}{what}: the storyguide rolled."


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


# -- the kinds of entry --

#: How an entry is drawn as a card (each front-end keeps its own look):
#: a note (its line alone), a roll, a form's roll, a Roll request with its
#: answers gathered, a Message, a Show (which opens its copy), a Scene's
#: banner, or nothing (it amends another's card).
(
    NOTE,
    ROLL_CARD,
    FORM_ROLL_CARD,
    REQUEST_CARD,
    MESSAGE_CARD,
    SHOW_CARD,
    SCENE_CARD,
    NO_CARD,
) = (
    "note",
    "roll",
    "form_roll",
    "request",
    "message",
    "show",
    "scene",
    "none",
)


def _never(_entry: Entry) -> bool:
    return False


def _always(_entry: Entry) -> bool:
    return True


#: Who an entry is meant for, enough to call a collapsed pane's attention:
#: one kind's rule (Strategy), given the entry, its Session and the saga.
ForWhom = Callable[[Entry, Session, "Saga | None"], frozenset[str]]

NO_ONE: frozenset[str] = frozenset()


def _no_one(_entry: Entry, _session: Session, _saga: Saga | None) -> frozenset[str]:
    return NO_ONE


def _blind_number(entry: Entry, session: Session, saga: Saga | None) -> frozenset[str]:
    """A Blind roll's number: for the Session's storyguide."""
    if entry.audience.to != STORYGUIDE:
        return NO_ONE
    return frozenset({storyguide_of(session, saga)})


def _rolled_for(entry: Entry, _session: Session, _saga: Saga | None) -> frozenset[str]:
    """The line that the storyguide rolled: for the player it is for."""
    if entry.audience.to != CHOSEN:
        return NO_ONE
    return frozenset(entry.audience.players)


def _whispered_to(
    entry: Entry, _session: Session, _saga: Saga | None
) -> frozenset[str]:
    """A Whisper or a Show: for each person it is to (one to the Table: no
    one, as for any Table entry)."""
    return frozenset(str(t) for t in entry.body.get("to", []))


def _offered_to(entry: Entry, session: Session, saga: Saga | None) -> frozenset[str]:
    """A Roll request: for whoever rolls each character offered it, but
    the Session's storyguide, who made it."""
    rollers = {str(c.get("roller", "")) for c in entry.body.get("characters", [])}
    return frozenset(rollers - {"", storyguide_of(session, saga)})


@dataclass(frozen=True)
class Kind:
    """One kind of entry, described once. `typed`: the keys of its body
    holding words someone typed, which Chronicle.add puts through the
    character rule (shapes.why_not_words). `line`: its line from its
    body. `strikable`: a roll a Strike may take from the count (its line
    then says so, and who saw it). `card`: how it is drawn. `amends`:
    whether it changes cards already drawn (a pane draws them again).
    `sounds`: a roll landing, which a pane may sound. `storyguide_skips`:
    the Session's storyguide doesn't read it (they have the roll itself).
    `for_whom`: who it is meant for, whose collapsed pane it calls; the
    host's own pane and the "for you" it tells each seat both ask it.
    Every kind names its rule, `_no_one` included, so a new kind can't
    leave it out by mistake. `held_back`: the keys of its body the host
    keeps and never sends a seat (a Whisper's recipients' Player ids);
    every kind names it too, `()` for one that sends its whole body."""

    name: str
    line: Callable[[dict[str, Any]], str]
    for_whom: ForWhom
    held_back: tuple[str, ...]
    typed: tuple[str, ...] = ()
    strikable: bool = False
    card: str = NOTE
    amends: Callable[[Entry], bool] = _never
    sounds: bool = False
    storyguide_skips: bool = False


#: Every kind of entry the Chronicle writes, by name.
KINDS: dict[str, Kind] = {
    spec.name: spec
    for spec in (
        Kind(BEGIN, lambda _body: "Session begun.", for_whom=_no_one, held_back=()),
        Kind(END, lambda _body: "Session ended.", for_whom=_no_one, held_back=()),
        Kind(
            ROLL,
            _roll_line,
            typed=("for",),
            strikable=True,
            card=ROLL_CARD,
            # An answer to a Roll request is gathered on the request's card.
            amends=lambda entry: "request" in entry.body,
            sounds=True,
            for_whom=_blind_number,
            held_back=(),
        ),
        Kind(
            FORM_ROLL,
            form_roll_line,
            # A form's name may come from a seat; its result lines are
            # checked where a seat sends them (remote/events), since the
            # host's own forms write theirs.
            typed=("form",),
            strikable=True,
            card=FORM_ROLL_CARD,
            sounds=True,
            for_whom=_blind_number,
            held_back=(),
        ),
        # Its "for" copies its roll's, already checked; kept typed all the same.
        Kind(
            ROLLED,
            _rolled_line,
            typed=("for",),
            sounds=True,
            storyguide_skips=True,
            for_whom=_rolled_for,
            held_back=(),
        ),
        Kind(
            VOID,
            lambda body: f"Roll {body['strikes']} is struck: {body['reason']}",
            typed=("reason",),
            card=NO_CARD,
            amends=_always,
            for_whom=_no_one,
            held_back=(),
        ),
        Kind(
            CONFIDENCE,
            confidence_line,
            amends=_always,
            for_whom=_no_one,
            held_back=(),
        ),
        Kind(
            REQUEST,
            request_line,
            typed=("for",),
            card=REQUEST_CARD,
            for_whom=_offered_to,
            # Each character's roller (a Player id) travels: a seat reads
            # it to know whether it answers (Reader.may_answer). The aura
            # the answers are rolled in stays here (the storyguide's).
            held_back=("aura",),
        ),
        Kind(
            REQUEST_EASE,
            lambda body: (
                f"Request {body['request']}'s Ease Factor, kept from its "
                f"players: {body['ease_factor']}"
            ),
            card=NO_CARD,
            amends=_always,
            for_whom=_no_one,
            held_back=(),
        ),
        Kind(
            OUTCOME,
            lambda body: f"Request {body['request']}: {body['text']}",
            typed=("text",),
            amends=_always,
            for_whom=_no_one,
            held_back=(),
        ),
        Kind(
            MESSAGE,
            lambda body: f"{message_label(body)}: {body['words']}",
            typed=("words",),
            card=MESSAGE_CARD,
            for_whom=_whispered_to,
            # A seat is told whether it is for them (for_you), and reads
            # the others' names; their ids stay here (ADR 0031).
            held_back=("to",),
        ),
        Kind(
            SHOW,
            show_line,
            # The story's name comes from the saga, a seat's copy of it.
            typed=("title", "story"),
            card=SHOW_CARD,
            for_whom=_whispered_to,
            # As a Whisper's: the Players shown by name only (ADR 0031).
            held_back=("to",),
        ),
        # A Scene's banner and its end: words from the saga, and the place
        # as the players know it (scene_play.py); for the Table, so no one.
        Kind(
            SCENE_SET,
            scene_set_line,
            card=SCENE_CARD,
            for_whom=_no_one,
            held_back=(),
        ),
        Kind(
            SCENE_ENDED,
            lambda body: f"Scene ended: {body['title']}",
            for_whom=_no_one,
            held_back=(),
        ),
    )
}

#: The keys of each kind's body that hold typed words (KINDS' `typed`).
TYPED: dict[str, tuple[str, ...]] = {k: s.typed for k, s in KINDS.items() if s.typed}
#: The kinds whose bodies hold no typed words: numbers and names from the saga.
UNTYPED = frozenset(k for k, s in KINDS.items() if not s.typed)
#: The kinds of entry a Strike may take from the count: rolls.
STRIKABLE = frozenset(k for k, s in KINDS.items() if s.strikable)


def kind_of(entry: Entry) -> Kind | None:
    """`entry`'s kind, or None for one this version doesn't know."""
    return KINDS.get(entry.kind)


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
        session.id,
        [
            stamped(e, who, session, saga)
            for e in book.since(since)
            if sees(e, who, session, saga)
        ],
    )


def stamped(entry: Entry, who: str, session: Session, saga: Saga | None) -> Entry:
    """`entry` as the host hands it to `who`'s seat, told whether it is for
    them, and without what its kind holds back (ADR 0031). The one place
    this is done, so live sending and catching up after a drop give the
    same pulses and send the same."""
    for_you = calls_attention(entry, who, session, saga)
    spec = kind_of(entry)
    body = entry.body
    if spec is not None and spec.held_back:
        body = {k: v for k, v in body.items() if k not in spec.held_back}
    return replace(entry, body=body, for_you=for_you)


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
    spec = KINDS.get(entry.kind)
    if (
        spec is not None
        and spec.storyguide_skips
        and who == storyguide_of(session, saga)
    ):
        return False
    return sees(entry, who, session, saga)


def line(entry: Entry, struck: dict[int, str]) -> str:
    """`entry`'s line, as the Chronicle reads (plain text, not markup);
    `struck` is `voided(book)`, worked out once for all the lines drawn."""
    return _line(entry, struck)


def for_whom(
    entry: Entry, session: Session, saga: Saga | None = None
) -> frozenset[str]:
    """Who `entry`, in the host's own Chronicle, is meant for: its kind's
    rule (Kind.for_whom); no one for a kind this version doesn't know."""
    spec = kind_of(entry)
    return spec.for_whom(entry, session, saga) if spec is not None else NO_ONE


def calls_attention(
    entry: Entry, who: str, session: Session, saga: Saga | None = None
) -> bool:
    """Whether `entry`, in the host's own Chronicle, calls `who`'s collapsed
    pane (Reader.calls_attention, for any book)."""
    return who in for_whom(entry, session, saga)


def visibility_tag(audience: Audience) -> str:
    """How a roll seen by `audience` is marked: "Blind" (the storyguide
    alone), "Private" (chosen Players), "" (the Table)."""
    if audience.to == TABLE:
        return ""
    return "Blind" if audience.to == STORYGUIDE else "Private"


@dataclass(frozen=True)
class Reader:
    """The Chronicle as one person reads it, the same whether `book` is
    the host's own or what a Remote seat was sent (which comes already
    filtered, without the Players chosen or what each kind holds back, so
    a Whisper there has no recipients' ids, and told which entries are for
    it): which entries they read, which call their attention, whether they
    may answer a Roll request, and a request's answer as they see it. At
    a seat, attention is the host's word (`for_you`), never the kind's
    rule, which needs what was held back.

    Pattern: an Adapter over two sources, the host's Chronicle and a
    seat's feed."""

    book: HasEntries
    who: str
    session: Session
    saga: Saga | None = None

    @property
    def at_seat(self) -> bool:
        return isinstance(self.book, SeatChronicle)

    @property
    def runs_the_session(self) -> bool:
        return self.who == storyguide_of(self.session, self.saga)

    def reads(self, entry: Entry) -> bool:
        """Whether this person reads `entry`: at the host, through the
        audience filter; at a seat, what the host sent, less the line
        telling a player a Blind roll was made, for the storyguide."""
        if not self.at_seat:
            return reads(entry, self.who, self.session, self.saga)
        spec = KINDS.get(entry.kind)
        return not (
            spec is not None and spec.storyguide_skips and self.runs_the_session
        )

    def entries(self) -> list[Entry]:
        """The entries this person reads, in order."""
        return [e for e in self.book.entries if self.reads(e)]

    def calls_attention(self, entry: Entry) -> bool:
        """Whether `entry` calls this person's collapsed pane: at the host,
        its kind's rule; at a seat, what the host said ("for you")."""
        if self.at_seat:
            return entry.for_you is True
        return calls_attention(entry, self.who, self.session, self.saga)

    def may_answer(self, request: Entry, character_id: str) -> bool:
        """Whether this person answers `request` for `character_id` now:
        at the host, as the host checks it; at a seat, the roller the
        request names who hasn't answered yet (the host checks again)."""
        if any(
            e.body.get("character_id") == character_id
            for e in answers(self.book, request.number)
        ):
            return False
        if not self.at_seat and self.saga is not None:
            why = why_not_answer(
                self.book,
                self.saga,
                self.session,
                request.number,
                character_id,
                self.who,
            )
            return why is None
        return self.who == roller_of(request, character_id)

    def kept_ease(self, request: Entry) -> int | None:
        """`request`'s Ease Factor kept from its players, for the Session's
        storyguide's eyes; None for anyone else or none kept."""
        if not self.runs_the_session:
            return None
        return hidden_ease(self.book, request.number)

    def answer_result(self, request: Entry, character_id: str) -> str:
        """`character_id`'s answer to `request` as this person sees it: its
        total and whether it succeeded (against the Ease Factor kept from
        the players, for the storyguide), "botch", "rolled" for one they
        may not see, or "…" for none yet."""
        made = [
            e
            for e in answers(self.book, request.number)
            if e.body.get("character_id") == character_id
        ]
        if not made:
            return "…"
        seen = next((e for e in made if self.reads(e)), None)
        if seen is None:
            return "rolled"
        body = seen.body
        if body.get("botches"):
            return "botch"
        result = str(body.get("total"))
        kept = self.kept_ease(request)
        if kept is not None:
            return result + (" ✓" if int(body["total"]) >= kept else " ✗")
        if body.get("succeeded") is not None:
            return result + (" ✓" if body["succeeded"] else " ✗")
        return result
