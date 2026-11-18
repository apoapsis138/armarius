"""Table rolls: while a Session is Under way, a rolling form whose roll
the story calls for in the moment takes its dice from the host and is
written to the Chronicle (ADR 0018, as amended; the glossary's Table
roll). Outside a Session, and for the rolls a season, a year or a project
calls for, nothing changes.

A Table roll form makes two small changes and no other: it takes its
source of chance from `dice()` instead of building `random.Random()`, and
it hands its Form to `form`, naming its typed-die fields. While a Session
is Under way `form` adds who sees the roll (Public, Private, or Blind for
the storyguide alone; the storyguide starts at Blind, a player at
Public), hides the typed-die fields (the host rolls), and on Save draws
the form's dice for it:

- On the host's own copy, from a `RecordingDice` over the host's
  `secrets.SystemRandom`, keeping every face, then writes the roll.
- At a Remote seat, through the opener the window sets (`use_seat`): each
  die is drawn from the host one at a time, the host keeps the faces, and
  the seat sends back only the form's result line. The form still works
  its rule at the seat; it can't choose its dice or quietly roll again.

A form that fails after drawing (its Save refused, the seat cut off)
leaves its dice in the Chronicle as "drawn, then cancelled".

Which modules roll at the table is kept here, by module (`TABLE`,
`NOT_TABLE`, `FIGHTS`); a test checks every module that rolls is in
exactly one.

Pattern: Decorator, twice. `RecordingDice` wraps a source of chance and
adds recording, so every rule that takes an `rng` takes it unchanged;
`form` wraps a Form and adds the visibility pick and the Chronicle entry,
so no form's rule changes. At a seat the die source is a Remote Proxy for
the host's. The roll itself is a Command kept in the Chronicle, struck
like any other.
"""

from __future__ import annotations

import dataclasses
import random
import secrets
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Protocol

from . import chronicle, dice_text
from .commands import Confirm, Form, notes
from .form_spec import DialogField
from .markup import plain
from .models import Saga, Session
from .rules import dice as dice_rules

# -- which rolls are Table rolls --

#: Modules whose rolls the story calls for in the moment, for a character
#: acting in a scene: they post while a Session is Under way.
TABLE: frozenset[str] = frozenset(
    {
        "baraka",
        "devotion",
        "disputations",
        "forms.acclaim",
        "forms.agents",
        "forms.beast",
        "forms.church",
        "forms.covers",
        "forms.craft_magic",
        "forms.faerie_dealings",
        "forms.galdor",
        "forms.goetic",
        "forms.hedge_cast",
        "forms.holy_influence",
        "forms.hubris",
        "forms.hunting",
        "forms.lacuna",
        "forms.polemic",
        "forms.ships",
        "forms.sin",
        "forms.tmre_divination",
        "forms.tmre_dreams",
        "forms.tmre_spirits",
        "forms.trait_roll",
        "forms.tunnel",
        "forms.turbulence",
        "health",
        "meeting",
        "melee_events",
        "mystic_paths",
        "place_events",
        "selling",
        "theban_customs",
        "town_court",
    }
)

#: Modules whose rolls a season, a year or a project calls for, or that
#: build a record rather than act in a scene: they never post.
NOT_TABLE: frozenset[str] = frozenset(
    {
        "book_packs.generated",
        "forms.apothecary",
        "forms.careers",
        "forms.character",
        "forms.charter_strength",
        "forms.constant_effect",
        "forms.gauntlet",
        "forms.ship_build",
        "forms.tmre_alchemy",
        "forms.worksheet",
        "hermetic_projects",
        "hibernia_meeting",
        "manors",
        "menagerie",
        "rules.activities",
        "seasons.advance",
        "seasons.experiment_results",
        "seasons.lab_apply",
        "staged_projects",
        "tombs",
        "towns",
        "tribunal_packages.rhine_library",
    }
)

#: Fights, battles, sieges and certamen: their own story, not yet sorted.
FIGHTS: frozenset[str] = frozenset(
    {
        "battle_muster",
        "fight_morale",
        "fights",
        "forms.certamen_duel",
        "siege_actions",
        "sieges",
    }
)

# -- the recording die source --

#: The most bits one draw asks for: a larger draw is made of several.
_CHUNK = 30


class DrawnDice(random.Random):
    """A source of chance whose every draw is a `randrange`: a choice, a
    shuffle or a float is made of dice too, so a source that records or
    fetches its dice (the host's, a seat's) sees all of them."""

    def random(self) -> float:
        return self.getrandbits(_CHUNK) / (1 << _CHUNK)

    def getrandbits(self, k: int, /) -> int:
        bits = 0
        while k > 0:
            take = min(k, _CHUNK)
            bits = (bits << take) | self.randrange(1 << take)
            k -= take
        return bits


#: A die as a form roll's entry keeps it: a whole die
#: (`{"stress", "faces", "botch_faces"}`, as `rules.dice.DieResult` has
#: them) or a face drawn outside the die helpers (`{"face"}`).
Die = dict[str, Any]


class RecordingDice(DrawnDice):
    """A source of chance that keeps every face it gives out, in order:
    `source`'s own (the host's `secrets.SystemRandom` unless given). A die
    (`randrange`, `randint`) is kept as its face; any other draw (a choice,
    a shuffle) goes through `randrange` too, so it is kept the same way.

    `dice` keeps the same faces grouped: each whole die `rules.dice`
    makes (it tells the source through `die_made`) with its doublings and
    botch dice, and each face drawn some other way on its own."""

    def __init__(self, source: random.Random | None = None) -> None:
        super().__init__()
        self._source = source if source is not None else secrets.SystemRandom()
        self.faces: list[int] = []
        #: How many of `faces` are already in a whole die of `_whole`.
        self._grouped = 0
        self._whole: list[Die] = []

    def randrange(self, start: int, stop: int | None = None, step: int = 1) -> int:
        face = self._source.randrange(start, stop, step)
        self.faces.append(face)
        return face

    def randint(self, a: int, b: int) -> int:
        face = self._source.randint(a, b)
        self.faces.append(face)
        return face

    def note(self, face: int) -> None:
        """Keep a face drawn from some other source (a watch's)."""
        self.faces.append(face)

    def die_made(self, die: dice_rules.DieResult) -> None:
        """`die`, just made from the last of the loose faces: kept whole
        (loose faces before it stay loose). A die whose faces aren't the
        last ones drawn is left as loose faces."""
        listener = getattr(self._source, "die_made", None)
        if callable(listener):  # a recording source under this one
            listener(die)
        thrown = [*die.faces, *die.botch_faces]
        loose = self.faces[self._grouped :]
        if not thrown or loose[len(loose) - len(thrown) :] != thrown:
            return
        before = len(self.faces) - len(thrown)
        self._whole.extend({"face": f} for f in self.faces[self._grouped : before])
        self._whole.append(
            {
                "stress": die.stress,
                "faces": list(die.faces),
                "botch_faces": list(die.botch_faces),
            }
        )
        self._grouped = len(self.faces)

    @property
    def dice(self) -> list[Die]:
        """Every face drawn, as whole dice and loose faces, in order."""
        return [*self._whole, *({"face": f} for f in self.faces[self._grouped :])]


def system_source() -> random.Random:
    """The host's source of chance."""
    return secrets.SystemRandom()


#: Where the host's dice come from (tests give a d10 of chosen faces).
host_source: Callable[[], random.Random] = system_source
#: Where a form's dice come from outside a Session, as before.
plain_source: Callable[[], random.Random] = random.Random

# -- the source a Table roll form takes --

#: The dice of the form roll being saved here, if any.
_drawing: random.Random | None = None
#: Every face a Table roll form hands out while it is being saved, from
#: whichever source, kept whole for its dice line.
_watching: RecordingDice | None = None


class _TableDice(DrawnDice):
    """What a Table roll form takes instead of `random.Random()`: while a
    form roll is being saved under a Session, each draw comes from that
    roll's dice; otherwise from a source of its own, as before. Either
    way, while the form is being saved each face is also kept by the
    watch, so its result can show its dice."""

    def __init__(self) -> None:
        super().__init__()
        self._own: random.Random | None = None

    def _source(self) -> random.Random:
        if _drawing is not None:
            return _drawing
        if self._own is None:
            self._own = plain_source()
        return self._own

    def _watched(self, face: int) -> int:
        if _watching is not None:
            _watching.note(face)
        return face

    def randrange(self, start: int, stop: int | None = None, step: int = 1) -> int:
        return self._watched(self._source().randrange(start, stop, step))

    def randint(self, a: int, b: int) -> int:
        return self._watched(self._source().randint(a, b))

    def die_made(self, die: dice_rules.DieResult) -> None:
        """Pass a whole die on to the source it came from, if it listens,
        and to the watch."""
        listener = getattr(self._source(), "die_made", None)
        if callable(listener):
            listener(die)
        if _watching is not None:
            _watching.die_made(die)


def dice() -> random.Random:
    """The source of chance a Table roll form takes."""
    return _TableDice()


# -- a form roll, at the host or from a seat --


@dataclass(frozen=True)
class Opening:
    """What a form roll is, as the host is told before its first die: the
    form's name, the character (none: the storyguide's own) and who sees
    it."""

    form: str
    character_id: str
    visibility: str


class DiceUnavailable(Exception):
    """A seat's dice couldn't be drawn from the host; the reason, to show."""


class FormRoll(Protocol):
    """One form roll being saved: where its dice come from, and how it
    ends. `finish` writes it with the form's result lines (the reason it
    couldn't be, or None); `cancel` writes the dice drawn so far as
    cancelled."""

    @property
    def dice(self) -> random.Random: ...

    def finish(self, lines: list[str]) -> str | None: ...

    def cancel(self) -> None: ...


#: Opens a form roll at a Remote seat (the window sets it while the
#: seat's Chronicle pane is attached).
Opener = Callable[[Opening], FormRoll]

_seat: Opener | None = None


def use_seat(opener: Opener | None) -> None:
    """Draw form rolls' dice from the host through `opener` (a Remote
    seat), or here (None: the host's own copy)."""
    global _seat
    _seat = opener


class HostRoll:
    """A form roll at the host: its dice from the host's source, recorded,
    and written to the Session's Chronicle by `by` (the host's own window,
    or a seat's Player through the host's listener)."""

    def __init__(
        self,
        saga: Saga,
        session: Session,
        opening: Opening,
        *,
        by: str,
        source: random.Random | None = None,
        book: chronicle.Chronicle | None = None,
    ) -> None:
        problem = chronicle.why_not_form_roll(
            saga, session, opening.character_id, opening.visibility, by
        )
        if problem:
            raise ValueError(problem)
        self.saga, self.session, self.opening, self.by = saga, session, opening, by
        self._book = book
        self._dice = RecordingDice(source if source is not None else host_source())
        self.ended = False
        #: The number of the entry written (0: none yet).
        self.number = 0

    @property
    def dice(self) -> random.Random:
        return self._dice

    @property
    def faces(self) -> list[int]:
        return self._dice.faces

    def _write(self, lines: list[str], *, cancelled: bool) -> None:
        self.ended = True
        if not self._dice.faces:
            return
        book = self._book or chronicle.read(self.saga, self.session)
        entry = chronicle.form_roll(
            book,
            self.saga,
            self.session,
            form=self.opening.form,
            character_id=self.opening.character_id,
            visibility=self.opening.visibility,
            faces=self._dice.faces,
            whole_dice=self._dice.dice,
            lines=lines,
            by=self.by,
            cancelled=cancelled,
        )
        self.number = entry.number

    def finish(self, lines: list[str]) -> str | None:
        try:
            self._write(lines, cancelled=False)
        except ValueError as problem:
            return str(problem)
        except OSError:
            return "The Chronicle couldn't be saved."
        return None

    def cancel(self) -> None:
        if self.ended:
            return
        try:
            self._write([], cancelled=True)
        except OSError, ValueError:
            pass  # the form's own failure is what the user is told


def _open(saga: Saga, session: Session, opening: Opening, who: str) -> FormRoll:
    """A form roll opened here: through the seat's opener at a Remote
    seat, else at the host (ValueError says why it can't be made)."""
    if _seat is not None:
        return _seat(opening)
    return HostRoll(saga, session, opening, by=who)


def default_visibility(saga: Saga, session: Session, who: str) -> str:
    """Who sees a Table roll unless the roller says: the storyguide's are
    Blind, a player's Public."""
    if who == chronicle.storyguide_of(session, saga):
        return chronicle.BLIND
    return chronicle.PUBLIC


class Drawing:
    """A Table roll made outside a form (a roll on a table, a debate, a
    question answered Yes): its dice, and the lines that say what came of
    it, filled in before the roll ends."""

    def __init__(self, dice: random.Random) -> None:
        self._recorded = RecordingDice(dice)
        self.dice: random.Random = self._recorded
        self.lines: list[str] = []
        #: Why the roll couldn't be written to the Chronicle, if it couldn't.
        self.refused: str | None = None

    @property
    def said(self) -> str:
        """The whole dice drawn so far, as the dice line says them ("" for
        none): for the roll's own result to show."""
        return dice_said(self._recorded.dice)


@contextmanager
def drawing(
    saga: Saga,
    name: str,
    *,
    character_id: str = "",
    own: random.Random | None = None,
) -> Iterator[Drawing]:
    """Roll `name` (markup) with the Session's dice when one is Under way:
    seen as `default_visibility` says, and written to the Chronicle with
    its faces and the lines given when the block ends; drawn, then
    cancelled, if the block fails. Outside a Session, `own` (a source of
    its own unless given). ValueError or DiceUnavailable when the dice
    can't be drawn."""
    session = chronicle.under_way(saga)
    if session is None:
        yield Drawing(own if own is not None else plain_source())
        return
    who = chronicle.here()
    opening = Opening(plain(name), character_id, default_visibility(saga, session, who))
    roll = _open(saga, session, opening, who)
    drawn = Drawing(roll.dice)
    try:
        yield drawn
    except BaseException:
        roll.cancel()
        raise
    lines = [plain(line) for line in drawn.lines]
    if drawn.said and not isinstance(roll, HostRoll):
        lines.append(drawn.said)  # the host can't group a seat's dice: say them
    drawn.refused = roll.finish(lines)


# -- the form decorator --

#: The field `form` adds: who sees the roll.
VISIBILITY = "table_visibility"


def visibility_options(storyguide: bool) -> list[tuple[str, str]]:
    shown = [
        ("Public: everyone at the Session", chronicle.PUBLIC),
        ("Private: you and the storyguide", chronicle.PRIVATE),
    ]
    if storyguide:
        shown.append(("Blind: the number is yours alone", chronicle.BLIND))
    return shown


def _never(_values: dict[str, Any]) -> bool:
    return False


def result_lines(result: Any) -> list[str]:
    """A form's result as the Chronicle keeps it: its notes, as plain
    text; a Keep question's (Health, Disputations) the roll's result it
    asks about, line by line; nothing for any other further step."""
    if isinstance(result, Confirm):
        return [plain(line) for line in result.question.splitlines() if line.strip()]
    if isinstance(result, list) and all(isinstance(line, str) for line in result):
        lines: list[str] = result
        return [plain(line) for line in lines]
    return []


def dice_said(kept: Sequence[Die]) -> str:
    """The whole dice a form drew, as its result's last line says them
    (faces drawn outside the die helpers left to the form's own words);
    "" when it drew none."""
    wholes = [die for die in kept if "face" not in die]
    return dice_text.dice_text(wholes) if wholes else ""


def with_dice(result: Any, said: str) -> Any:
    """A form's result with its dice line last: under its notes, or under
    a Keep question's result; any other further step unchanged."""
    if not said:
        return result
    if isinstance(result, Confirm):
        return dataclasses.replace(result, question=f"{result.question}\n\n{said}")
    if isinstance(result, list) and all(isinstance(line, str) for line in result):
        lines: list[str] = result
        return [*lines, said]
    return result


def _watched(inner: Form, values: dict[str, Any]) -> tuple[Any, str]:
    """`inner` saved with `values`, every face it draws watched: its
    result and its dice line."""
    global _watching
    watch = RecordingDice(random.Random(0))  # only noted, never drawn from
    _watching = watch
    try:
        result = inner.apply(values)
    finally:
        _watching = None
    return result, dice_said(watch.dice)


def _shown(inner: Form, values: dict[str, Any]) -> Any:
    """`inner` saved outside a Session: its result, with its dice."""
    result, said = _watched(inner, values)
    return with_dice(result, said)


def form(
    inner: Form,
    saga: Saga,
    *,
    character_id: str = "",
    typed: Sequence[str] = (),
) -> Form:
    """`inner`, a Table roll form, as the table rolls it: outside a
    Session, unchanged but for its dice line under its result (`with_dice`);
    while one is Under way, with that line, who sees the roll, its
    typed-die fields (the keys `typed`) hidden, and its roll written to
    the Chronicle when it is saved."""
    session = chronicle.under_way(saga)
    if session is None:
        return dataclasses.replace(inner, apply=lambda values: _shown(inner, values))
    who = chronicle.here()
    storyguide = who == chronicle.storyguide_of(session, saga)
    name = plain(inner.title)

    def fields() -> list[DialogField]:
        found = [
            dataclasses.replace(f, show_if=_never) if f.key in typed else f
            for f in inner.fields()
        ]
        return [
            *found,
            DialogField(
                VISIBILITY,
                "Who sees the roll",
                "select",
                default_visibility(saga, session, who),
                options=visibility_options(storyguide),
                hint="The host rolls the dice and keeps them in the Chronicle.",
            ),
        ]

    def apply(values: dict[str, Any]) -> Any:
        global _drawing
        visibility = str(values.get(VISIBILITY) or chronicle.PUBLIC)
        rest = {k: v for k, v in values.items() if k != VISIBILITY}
        if not session.under_way:  # ended while the form was open
            return _shown(inner, rest)
        try:
            roll = _open(saga, session, Opening(name, character_id, visibility), who)
        except ValueError as problem:
            return notes(str(problem))
        _drawing = roll.dice
        try:
            result, said = _watched(inner, rest)
        except DiceUnavailable as problem:
            roll.cancel()
            return notes(f"Nothing was rolled: {problem}")
        except BaseException:
            roll.cancel()
            raise
        finally:
            _drawing = None
        lines = result_lines(result)
        if said and not isinstance(roll, HostRoll):
            lines.append(said)  # the host can't group a seat's dice: say them
        refused = roll.finish(lines)
        result = with_dice(result, said)
        if refused and isinstance(result, list):
            shown: list[str] = result
            return [*shown, f"The roll isn't in the Chronicle: {refused}"]
        return result

    return dataclasses.replace(inner, fields=fields, apply=apply)
