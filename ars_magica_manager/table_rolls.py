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

from . import chronicle
from .commands import Form, notes
from .form_spec import DialogField
from .markup import plain
from .models import Saga, Session

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


class RecordingDice(DrawnDice):
    """A source of chance that keeps every face it gives out, in order:
    `source`'s own (the host's `secrets.SystemRandom` unless given). A die
    (`randrange`, `randint`) is kept as its face; any other draw (a choice,
    a shuffle) goes through `randrange` too, so it is kept the same way."""

    def __init__(self, source: random.Random | None = None) -> None:
        super().__init__()
        self._source = source if source is not None else secrets.SystemRandom()
        self.faces: list[int] = []

    def randrange(self, start: int, stop: int | None = None, step: int = 1) -> int:
        face = self._source.randrange(start, stop, step)
        self.faces.append(face)
        return face

    def randint(self, a: int, b: int) -> int:
        face = self._source.randint(a, b)
        self.faces.append(face)
        return face


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


class _TableDice(DrawnDice):
    """What a Table roll form takes instead of `random.Random()`: while a
    form roll is being saved under a Session, each draw comes from that
    roll's dice; otherwise from a source of its own, as before."""

    def __init__(self) -> None:
        super().__init__()
        self._own: random.Random | None = None

    def _source(self) -> random.Random:
        if _drawing is not None:
            return _drawing
        if self._own is None:
            self._own = plain_source()
        return self._own

    def randrange(self, start: int, stop: int | None = None, step: int = 1) -> int:
        return self._source().randrange(start, stop, step)

    def randint(self, a: int, b: int) -> int:
        return self._source().randint(a, b)


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
        self.dice = dice
        self.lines: list[str] = []
        #: Why the roll couldn't be written to the Chronicle, if it couldn't.
        self.refused: str | None = None


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
    drawn.refused = roll.finish([plain(line) for line in drawn.lines])


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
    text; nothing for a further step."""
    if isinstance(result, list) and all(isinstance(line, str) for line in result):
        lines: list[str] = result
        return [plain(line) for line in lines]
    return []


def form(
    inner: Form,
    saga: Saga,
    *,
    character_id: str = "",
    typed: Sequence[str] = (),
) -> Form:
    """`inner`, a Table roll form, as the table rolls it: unchanged outside
    a Session; while one is Under way, with who sees the roll, its
    typed-die fields (the keys `typed`) hidden, and its roll written to
    the Chronicle when it is saved."""
    session = chronicle.under_way(saga)
    if session is None:
        return inner
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
            return inner.apply(rest)
        try:
            roll = _open(saga, session, Opening(name, character_id, visibility), who)
        except ValueError as problem:
            return notes(str(problem))
        _drawing = roll.dice
        try:
            result = inner.apply(rest)
        except DiceUnavailable as problem:
            roll.cancel()
            return notes(f"Nothing was rolled: {problem}")
        except BaseException:
            roll.cancel()
            raise
        finally:
            _drawing = None
        refused = roll.finish(result_lines(result))
        if refused and isinstance(result, list):
            shown: list[str] = result
            return [*shown, f"The roll isn't in the Chronicle: {refused}"]
        return result

    return dataclasses.replace(inner, fields=fields, apply=apply)
