"""Hermetic Viresculture: Hérisson's cultivation of vis (Legends of
Hermes pp. 72-76).

- The breakthroughs (rules.integrations): Hermetic Viresculture itself, a
  Major Breakthrough giving the Supernatural Ability of that name (only
  for those Opened to the Hermetic Arts), and a Minor one letting living
  Lesser Enchantment Vis be made a Stirps (pp. 72-73).
- Vitalization (pp. 72-73): a lab season making a living source of vis
  (Magic Might 0 or more, able to reproduce) a Stirps. Its Level is the
  Might (or a Lesser Enchantment Vis's effect level); the Vitalization
  Total is a Creo Vim Lab Total with Hermetic Viresculture in place of
  Magic Theory, and each season adds what the Total exceeds the Level by,
  until the points reach the Level. One pawn of Vim vis per ten levels
  or fraction, paid from the stores with its first season.
- Several Stirpes in one season (p. 75's example, under Multiple
  Laboratory Activities, ArM5 p. 102, DE p. 264): the Total is applied to
  the sum of their Levels, so they must all be finished that season
  (Total less the sum at least the sum); Invigorating several shares the
  Invigoration Total among them, rounded up (43 for two roosters gives
  each 22). They are one Technique and Form, so Invigorated Stirpes
  share a Form.
- Invigoration (pp. 73-74): one season, Creo + the Stirps' Form (Vim
  requisite) + Viresculture: a breeding season that yields vis for every
  ten points or fraction. Each breeding season's litter or crop holds a
  fifth (rounded up) of the Might or level in pawns of the Stirps' Form;
  each pawn has a one in ten chance of being a new, uninvigorated Stirps.
- Tending (p. 75): a magus oversees at most his Viresculture score in
  Stirpes; each needs 12 Labor Points a year; every 6 Labor Points (or
  fraction) lacking, and every month left unattended, costs a pawn.
- An aura harvested (p. 76): with Aura Variation, the yearly aura
  modifier falls by a fifth (rounded up) of the pawns grown in it.

Pattern: the rules are plain functions; the two lab seasons go through
the season registry (season_work/viresculture.py), each a Strategy, and
keep their progress in Progress records.
"""

from __future__ import annotations

import random

from ..models import Character, Saga
from . import dice, lab, realms
from . import hybrid_magic as hybrid
from .breakdown import Line
from .rounding import round_up

SOURCE = (
    "Legends of Hermes, Hérisson, Viresculture, pp. 72-76; Ars Magica "
    "Definitive Edition, Multiple Laboratory Activities (p. 264)"
)

ABILITY = "Hermetic Viresculture"
#: The breakthroughs (rules.integrations' names).
BREAKTHROUGH = "Hermetic Viresculture"
LESSER_ENCHANTMENT = "Viresculture of Lesser Enchantment Vis"

#: The season activities.
VITALIZE = "vitalize_stirps"
INVIGORATE = "invigorate_stirps"
#: Their Progress records' kinds: a Stirps being Vitalized (points toward
#: its Level), and an Invigorated Stirps (its breeding seasons left).
VITALIZING = "vitalization"
INVIGORATED = "invigorated stirps"

LEVELS_PER_VIM_PAWN = 10
INVIGORATION_PER_SEASON = 10
MIGHT_PER_PAWN = 5
LABOR_PER_STIRPS = 12
LABOR_PER_PAWN = 6
PAWNS_PER_AURA_POINT = 5


def score(character: Character) -> int:
    """The magus's Hermetic Viresculture, with any Puissant bonus."""
    value, bonus = lab.ability_score(character, ABILITY)
    return value + bonus


def can_practise(character: Character) -> bool:
    """Only one Opened to the Hermetic Arts, with a score, practises it."""
    return character.type == "magus" and score(character) > 0


def _total(saga: Saga, magus: Character, form: str) -> lab.LabTotal:
    """Intelligence + Creo + `form` + Hermetic Viresculture + the aura: the
    magus's laboratory's Creo Lab Total with Viresculture for Magic Theory,
    or, with no laboratory, the bare sum in his covenant's aura."""
    vires = Line(ABILITY, amount=score(magus), source=SOURCE)
    own = saga.laboratory(magus.assigned_lab_id)
    if own is not None:
        total = lab.lab_total(saga, magus, "Creo", form, own)
        label, theory = hybrid.theory(magus)
        return lab.with_lines(
            total,
            [Line(f"{label}: not used", amount=-theory, source=SOURCE), vires],
        )
    aura, realm = realms.home_aura(saga, magus)
    aura_label, aura_amount = hybrid.aura_label(magus, realm, aura)
    lines = [
        Line("Creo", amount=sum(lab.art_score(magus, "Creo")), source=SOURCE),
        Line(form, amount=sum(lab.art_score(magus, form)), source=SOURCE),
        Line("Intelligence", amount=magus.characteristics.intelligence, source=SOURCE),
        vires,
        Line(aura_label, amount=aura_amount, source=realms.SOURCE),
    ]
    amount = sum(line.amount or 0 for line in lines)
    return lab.LabTotal(total=amount, lines=lines, flat=amount)


def vitalization_total(saga: Saga, magus: Character) -> lab.LabTotal:
    """Intelligence + Creo + Vim + Hermetic Viresculture + aura."""
    return _total(saga, magus, "Vim")


def requisite_form(magus: Character, form: str) -> str:
    """The Art an Invigoration Total counts for its Form: the Form, or Vim
    (its requisite) when Vim is lower: a requisite counts the lesser
    score (DE p. 312)."""
    if form == "Vim":
        return form
    return (
        "Vim"
        if sum(lab.art_score(magus, "Vim")) < sum(lab.art_score(magus, form))
        else form
    )


def invigoration_total(saga: Saga, magus: Character, form: str) -> lab.LabTotal:
    """Intelligence + Creo + the Stirps' Form (Vim requisite) + Hermetic
    Viresculture + aura."""
    return _total(saga, magus, requisite_form(magus, form))


def vitalization_level(might: int) -> int:
    """The Level a Stirps is Vitalized against: its Magic Might, or its
    Lesser Enchantment Vis's effect level (never below 0)."""
    return max(0, might)


def vitalization_points(total: int, level: int) -> int:
    """A season's points toward the Stirps: what the Total exceeds the
    Level by."""
    return max(0, total - level)


def vitalization_vis(level: int) -> int:
    """Pawns of Vim vis: one per ten levels or fraction."""
    return round_up(max(0, level) / LEVELS_PER_VIM_PAWN)


def vitalized_together(total: int, levels: list[int]) -> bool:
    """Whether one season Vitalizes all of several Stirpes: the Total less
    the sum of their Levels reaches that sum (Multiple Laboratory
    Activities)."""
    together = sum(max(0, level) for level in levels)
    return vitalization_points(total, together) >= max(1, together)


def vitalization_vis_for(levels: list[int]) -> int:
    """Pawns of Vim vis for Vitalizing Stirpes of `levels`: each one's own
    pawn per ten levels or fraction (two Mights of 10 cost two)."""
    return sum(vitalization_vis(level) for level in levels)


def shared_total(total: int, stirpes: int) -> int:
    """Each Stirps' share of an Invigoration Total split among `stirpes`
    of them, rounded up."""
    return round_up(max(0, total) / max(1, stirpes))


def breeding_seasons(total: int) -> int:
    """An Invigoration's breeding seasons: one per ten points or fraction."""
    return round_up(max(0, total) / INVIGORATION_PER_SEASON)


#: A Stirps' breeding season: the spring for animals, the autumn for
#: plants (Legends of Hermes p. 75).
PLANT_FORM = "Herbam"


def breeding_season(form: str) -> str:
    """The season a Stirps of `form` breeds in."""
    return "Autumn" if form.casefold() == PLANT_FORM.casefold() else "Spring"


def pawns_per_breeding(level: int) -> int:
    """The pawns of vis in each litter or crop: a fifth of the Might (or
    effect level), rounded up."""
    return round_up(max(0, level) / MIGHT_PER_PAWN)


def roll_stirpes(rng: random.Random, pawns: int) -> int:
    """How many of a harvest's `pawns` are new, uninvigorated Stirpes: each
    has a one in ten chance (a simple die of 1)."""
    return sum(1 for _ in range(max(0, pawns)) if dice.simple_die(rng) == 1)


def labor_needed(stirpes: int) -> int:
    """The Labor Points a year to care for `stirpes` Stirpes."""
    return LABOR_PER_STIRPS * max(0, stirpes)


def harvest(expected: int, stirpes: int, labor: int, neglected_months: int = 0) -> int:
    """A year's pawns from `stirpes` Stirpes: the `expected` yield, less a
    pawn per 6 Labor Points (or fraction) short of their care and a pawn
    per month left unattended."""
    lacking = max(0, labor_needed(stirpes) - labor)
    short = round_up(lacking / LABOR_PER_PAWN)
    return max(0, expected - short - max(0, neglected_months))


def tended(character: Character, stirpes: int) -> int:
    """How many of `stirpes` breed: at most the magus's Viresculture."""
    return min(max(0, stirpes), score(character))


def aura_drain(pawns: int) -> int:
    """What a year's Viresculture takes off the aura's yearly modifier,
    with the Aura Variation rules: a fifth of the pawns, rounded up."""
    return round_up(max(0, pawns) / PAWNS_PER_AURA_POINT)
