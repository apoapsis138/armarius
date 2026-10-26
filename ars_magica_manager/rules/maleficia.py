"""The maleficia: an infernalist's Methods and Powers (Realms of Power: The
Infernal, Chapter Ten, pp. 102-112; Errata p. 56).

- A maleficium pairs a Method with a Power: a stress die + the Method's
  Characteristic + Method + Power + the aura against its level, from the
  Powers' guidelines (catalog data, data/power_guidelines.json, each
  labelled with its Method) and the Hermetic Ranges, Durations and
  Targets, with four of Hell's own (p. 103): Crossroads (as Voice),
  Cursed (Condition) (as Sun, plus the triggered effect's Duration),
  Forsaken (as Year; repentance ends it) and Passion (as Group). It is a
  Vim effect against Magic Resistance (p. 102).
- Falling short (p. 102): a botch and a Warping Point for each 10 levels
  or fraction short, Vituperation at 2 Warping Points or more; Hierarchy
  x 10 may stand in for the total, for the failure only. A total of 18
  against level 30 is two; with Hierarchy 3 none, with 2 one. An actual
  botch: a soul for Hell within a season, or the Devil takes him.
  Used selflessly, a maleficium works as with Vengeful Powers.
- Debauchery (Stamina, p. 103): a long-term Fatigue level (about two
  minutes) or a Light Wound (as fast as a spell); the rite may be
  extended, spending Confidence again with a botch die more each time,
  or held for a season, adding Infernal Lore and rolling no die (p. 104).
- Incantation (Communication, p. 104): a Confidence Point, or a Warping
  Point for a fitting sin, not counted against the Confidence he may
  spend; vis +2 a pawn, at most Incantation + the Power pawns; Magic or
  Faerie vis doubles the botch dice at least, Divine vis serves only
  profaned.
- An Infernal aura adds no botch dice to a maleficium, being of its own
  realm (Errata p. 56, on p. 103's example).

Pattern: plain functions over a tradition's effect, as rules.holy_powers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..models import Character, TraditionDef, TraditionEffect
from . import infernalists
from .rounding import round_up
from .scores import ability_level

SOURCE = "Realms of Power: The Infernal, Chapter Ten: The Maleficia, pp. 102-112; Errata p. 56"

INFERNAL = "Infernal"
DEBAUCHERY, INCANTATION = "Debauchery", "Incantation"
#: Each Method and the Characteristic it adds (pp. 103-104).
METHODS: dict[str, str] = {DEBAUCHERY: "Stamina", INCANTATION: "Communication"}
#: The six unholy Powers (pp. 105-112).
POWERS = (
    "Consumption",
    "Diablerie",
    "Effusion",
    "Malediction",
    "Phantasm",
    "Psychomachia",
)
LEVELS_PER_BOTCH = 10
HIERARCHY_STANDS_IN = 10
VITUPERATION_AT = infernalists.VITUPERATION_AT
VIS_BONUS = 2


@dataclass(frozen=True)
class Failure:
    """What falling short of a maleficium brings: the botches, as many
    Warping Points, and whether Vituperation must be rolled."""

    botches: int
    warping: int

    @property
    def vituperation(self) -> bool:
        return self.warping >= VITUPERATION_AT


def failure(total: int, level: int, hierarchy: int = 0) -> Failure:
    """A botch and a Warping Point for each 10 levels or fraction short,
    Hierarchy x 10 standing in for the total when higher (p. 102)."""
    short = level - max(total, HIERARCHY_STANDS_IN * max(0, hierarchy))
    count = round_up(short / LEVELS_PER_BOTCH) if short > 0 else 0
    return Failure(count, count)


def vis_cap(incantation: int, power: int) -> int:
    """The most pawns of vis Incantation may use: Incantation + the Power
    (p. 104)."""
    return max(0, incantation) + max(0, power)


_LABELLED = re.compile(r"\((Debauchery|Incantation)\)\s*$")


def guideline_method(effect_guideline: str) -> str:
    found = _LABELLED.search(effect_guideline)
    return found.group(1) if found else ""


def is_maleficium(tradition: TraditionDef, effect: TraditionEffect) -> bool:
    return tradition.realm == INFERNAL and any(u in POWERS for u in effect.uses)


def effect_notes(
    character: Character, tradition: TraditionDef, effect: TraditionEffect
) -> list[str]:
    """What a maleficium asks beyond its level: its Method's cost, its
    guideline's own Method, and what a shortfall brings (advice)."""
    if not is_maleficium(tradition, effect):
        return []
    power = next(u for u in effect.uses if u in POWERS)
    method = next((u for u in effect.uses if u in METHODS), "")
    found: list[str] = []
    wanted = guideline_method(effect.guideline)
    if method and wanted and method != wanted:
        found.append(f"its guideline is for {wanted} (RoP: Infernal pp. 105-112)")
    if method == DEBAUCHERY:
        found.append(
            "a long-term Fatigue level (two minutes) or a Light Wound; extended, "
            "a botch die more each time; a season's rite adds Infernal Lore, no "
            "die (pp. 103-104)"
        )
    elif method == INCANTATION:
        cap = vis_cap(
            ability_level(character, INCANTATION), ability_level(character, power)
        )
        found.append(
            f"a Confidence Point, or a Warping Point for a fitting sin; vis +{VIS_BONUS} "
            f"a pawn, up to {cap}, Infernal vis only (p. 104)"
        )
    hierarchy = infernalists.hierarchy(character)
    line = "each 10 levels short, a botch and a Warping Point (Vituperation at 2)"
    if hierarchy:
        line += f"; his Hierarchy stands in as {HIERARCHY_STANDS_IN * hierarchy}"
    found.append(line + "; a true botch: a soul for Hell within a season (p. 102)")
    return found
