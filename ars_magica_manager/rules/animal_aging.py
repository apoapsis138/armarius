"""Animal Aging: how an animal grog's kind ages (Grogs, Chapter 7, Horses
& Hounds, Animal Aging).

- A human's average lifespan is 50 years: aging starts at 35, adds 1 to
  the aging roll for every 10 years, one roll a year; a character is
  grown at 5.
- Each kind of beast has its own figures, the book's table:

    kind               lifespan  grown  aging from  +1 per    rolls
    Clawed Beasts          9       1         6       2 years   5 a year
    Hoofed Beasts         27       3        20       5 years   2 a year
    Birds                 81       8        55      15 years   1 per 2 years
    Fish and Serpents    243      24       170      50 years   1 per 5 years

- A species the storyguide gives its own average lifespan scales the
  human figures by 50 / lifespan: aging from 35 / that, +1 per 10 / that
  years, that many rolls a year (the book's example: 10 years gives 5,
  so aging from 7, +1 per 2 years, 5 rolls a year). Each figure rounds
  to the nearest whole number (no fewer than 1 year a point, or a
  roll every whole number of years), since the book's table rounds
  both ways.
- Several rolls a year are spread evenly over the four seasons, any left
  over in Winter (5 a year: one each season, two in Winter; 2 a year:
  Summer and Winter). Fewer than one a year are made in Winter, every
  so many years from the age aging starts.

The roll itself is the ordinary one (rules.aging), with the kind's
modifier for age in place of age / 10.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from ..models import SEASONS, Character
from .rounding import round_up

SOURCE = (
    "Grogs, Chapter 7: Grog Templates, Horses & Hounds, Animal Aging "
    "(https://www.redcap.org/page/Grogs_Chapter_Seven:_Grog_Templates"
    "#Animal_Aging)"
)


@dataclass(frozen=True)
class AgingFigures:
    """A kind's aging: its average lifespan, the age it is grown (the end
    of its 120 xp of pre-adult life), the age its aging rolls start, the
    years each +1 to the roll takes, and its rolls a year."""

    lifespan: int
    grown: int
    aging_from: int
    years_a_point: int
    rolls_a_year: Fraction


HUMAN = AgingFigures(50, 5, 35, 10, Fraction(1))

#: The book's table, by rules.animal_grogs kind.
TABLE: dict[str, AgingFigures] = {
    "clawed": AgingFigures(9, 1, 6, 2, Fraction(5)),
    "hoofed": AgingFigures(27, 3, 20, 5, Fraction(2)),
    "bird": AgingFigures(81, 8, 55, 15, Fraction(1, 2)),
    "fish": AgingFigures(243, 24, 170, 50, Fraction(1, 5)),
}


def _nearest(value: Fraction) -> int:
    """The nearest whole number, a half rounding up."""
    return int(value + Fraction(1, 2)) if value >= 0 else -int(-value + Fraction(1, 2))


def scaled(lifespan: int) -> AgingFigures:
    """The figures for an average lifespan of `lifespan` years: the human
    ones divided by 50 / lifespan."""
    lifespan = max(1, lifespan)
    factor = Fraction(HUMAN.lifespan, lifespan)
    if factor >= 1:
        rolls = Fraction(max(1, _nearest(factor)))
    else:
        rolls = Fraction(1, max(1, _nearest(1 / factor)))
    return AgingFigures(
        lifespan,
        max(1, _nearest(HUMAN.grown / factor)),
        max(1, _nearest(HUMAN.aging_from / factor)),
        max(1, _nearest(HUMAN.years_a_point / factor)),
        rolls,
    )


def kind_figures(kind: str, lifespan: int | None = None) -> AgingFigures:
    """A kind's figures: the book's table, or scaled from `lifespan` when
    a species has its own."""
    own = TABLE.get(kind, HUMAN)
    if lifespan is None or lifespan == own.lifespan:
        return own
    return scaled(lifespan)


def figures(character: Character) -> AgingFigures | None:
    """An animal grog's aging figures; None for a person."""
    animal = character.animal
    if animal is None:
        return None
    return kind_figures(animal.kind, animal.lifespan)


def start_age(character: Character) -> int | None:
    """The age an animal's aging rolls start at; None for a person."""
    found = figures(character)
    return found.aging_from if found is not None else None


def age_modifier(character: Character, age: int) -> int:
    """What age adds to the aging roll: age / 10 rounded up for a person,
    age / the kind's years a point for an animal."""
    found = figures(character) or HUMAN
    return round_up(age / found.years_a_point)


def rolls_in_season(character: Character, age: int, season: str) -> int:
    """How many aging rolls an animal of `age` makes in `season`, its age
    past the start (or a Longevity Ritual) assumed; 0 for a person."""
    found = figures(character)
    if found is None or season not in SEASONS:
        return 0
    rolls = found.rolls_a_year
    winter = season == SEASONS[-1]
    if rolls < 1:
        every = int(1 / rolls)
        return int(winter and (age - found.aging_from) % every == 0)
    whole = int(rolls)
    each, left = divmod(whole, len(SEASONS))
    index = SEASONS.index(season)
    # The ones left over go evenly back from Winter (2: Summer and Winter).
    step = len(SEASONS) // left if left else 0
    extra = sum(1 for n in range(left) if len(SEASONS) - 1 - n * step == index)
    return each + extra


def rolls_in_year(character: Character, age: int) -> int:
    """An animal's aging rolls in the year it is `age`."""
    return sum(rolls_in_season(character, age, season) for season in SEASONS)


def rolls_between(character: Character, first: int, last: int) -> int:
    """An animal's aging rolls from age `first` up to (not including)
    `last`."""
    return sum(rolls_in_year(character, age) for age in range(first, last))


def schedule_text(character: Character) -> str:
    """ "From 6, +1 per 2 years, 5 rolls a year (2 in Winter)"."""
    found = figures(character)
    if found is None:
        return ""
    rolls = found.rolls_a_year
    if rolls < 1:
        every = int(1 / rolls)
        how = f"a roll every {every} years in Winter"
    else:
        count = int(rolls)
        winter = rolls_in_season(character, found.aging_from, SEASONS[-1])
        how = f"{count} roll{'s' if count != 1 else ''} a year"
        if count > 1:
            how += f" ({winter} in Winter)"
    return (
        f"aging from {found.aging_from}, +1 per {found.years_a_point} "
        f"year{'s' if found.years_a_point != 1 else ''}, {how}"
    )
