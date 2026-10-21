"""Seasons ahead worked out from the character as they will be by then: a
copy of the saga is played forward, season by season, with the functions
Advance Season uses (`resolve`, then `apply`), so a plan two seasons out
counts the Arts, Abilities, books read, vis spent and lab work of the
plans before it. The real saga is never touched.

Nothing is rolled: a season whose die isn't rolled yet (vis study, an
experiment) counts as gaining nothing from it, and the seasons after it
say so. The year's end (aging, a grog's year, the covenants' seasons) is
left out; only the planned seasons are played.

Prototype: the copy is the saga cloned and played on. In Python that is
no class hierarchy, just a copy (pickling, several times quicker than
`copy.deepcopy`) and the functions Advance already has. The copy is kept
while the saga is unchanged, so a sheet that asks about several seasons
plays them once.
"""

from __future__ import annotations

import pickle
from dataclasses import dataclass, field

from ..models import SEASONS, Character, Saga, next_season
from ..rules import activities as rules
from ..rules import lab_seasons

#: How many seasons ahead a projection reaches at most (the Planning tab's
#: horizon).
LONGEST = 40

Key = tuple[str, str, int]  # (character id, season, year)


def _when(season: str, year: int) -> int:
    return year * len(SEASONS) + SEASONS.index(season)


@dataclass
class Projection:
    """The saga played forward from its current season: each season's
    outcomes, worked out from the copy as it stood at that season."""

    copy: Saga
    #: The saga as it stood (pickled), to start again from.
    state: bytes
    outcomes: dict[Key, rules.Outcome] = field(default_factory=dict)
    lab_work: dict[Key, tuple[list[str], lab_seasons.LabWork | None]] = field(
        default_factory=dict
    )
    played: int = 0

    def _reached(self) -> int:
        return _when(self.copy.current_season, self.copy.current_year)

    def _play_through(self, season: str, year: int) -> None:
        target = _when(season, year)
        while self._reached() <= target and self.played < LONGEST:
            self._play_one()

    def at(self, season: str, year: int) -> Saga:
        """A copy of the saga as it will stand when that season begins (its
        own plans not yet played), free to change."""
        target = _when(season, year)
        played = self
        if self._reached() > target:
            played = Projection(pickle.loads(self.state), self.state)
        while played._reached() < target and played.played < LONGEST:
            played._play_one()
        return pickle.loads(pickle.dumps(played.copy, pickle.HIGHEST_PROTOCOL))

    def _play_one(self) -> None:
        # Imported here: advance's own imports reach the sheets' text,
        # which reads projections.
        from .advance import apply, resolve

        saga = self.copy
        when = (saga.current_season, saga.current_year)
        worked = resolve(saga)
        for outcome in worked:
            key = (outcome.character_id, *when)
            self.outcomes[key] = outcome
            character = saga.character(outcome.character_id)
            if outcome.plan.lab_id and character is not None:
                self.lab_work[key] = lab_seasons.work(saga, character, outcome.plan)
        apply(saga, worked)
        saga.current_season, saga.current_year = next_season(*when)
        self.played += 1

    def outcome(
        self, character_id: str, season: str, year: int
    ) -> rules.Outcome | None:
        """What the character's plan for that season gives, worked out from
        them as the seasons planned before it leave them."""
        self._play_through(season, year)
        return self.outcomes.get((character_id, season, year))

    def work(
        self, character_id: str, season: str, year: int
    ) -> tuple[list[str], lab_seasons.LabWork | None] | None:
        """lab_seasons.work for the character's lab plan that season, from
        the laboratory and magus as they will be then."""
        self._play_through(season, year)
        return self.lab_work.get((character_id, season, year))

    def unrolled_before(
        self, character_id: str, season: str, year: int
    ) -> list[tuple[str, int, str]]:
        """The character's seasons before this one whose die isn't rolled
        yet, counted as gaining nothing: (season, year, activity label)."""
        self._play_through(season, year)
        target = _when(season, year)
        return [
            (s, y, o.activity.label if o.activity else o.plan.activity)
            for (who, s, y), o in self.outcomes.items()
            if who == character_id and _when(s, y) < target and o.pending_roll
        ]


_kept: tuple[int, bytes, Projection] | None = None


def projection(saga: Saga) -> Projection:
    """`saga` played forward (lazily, as far as it is asked). The same
    projection is returned while the saga is unchanged."""
    global _kept
    state = pickle.dumps(saga, protocol=pickle.HIGHEST_PROTOCOL)
    if _kept is not None and _kept[0] == id(saga) and _kept[1] == state:
        return _kept[2]
    made = Projection(pickle.loads(state), state)
    _kept = (id(saga), state, made)
    return made


def unrolled_text(saga: Saga, character_id: str, season: str, year: int) -> str:
    """ "Counts nothing from Vis study (Spring 1221): its die isn't rolled
    yet.", or ""."""
    found = projection(saga).unrolled_before(character_id, season, year)
    if not found:
        return ""
    each = ", ".join(f"{label} ({s} {y})" for s, y, label in found)
    return f"Counts nothing gained from {each}: the die isn't rolled yet."


def as_then(
    saga: Saga, character: Character, season: str, year: int
) -> tuple[Saga, Character]:
    """The saga and `character` as they will stand when that season
    begins: the real ones for the current season, else a projection's copy
    (to work out a plan for a season ahead)."""
    if _when(season, year) <= _when(saga.current_season, saga.current_year):
        return saga, character
    then = projection(saga).at(season, year)
    return then, then.character(character.id) or character
