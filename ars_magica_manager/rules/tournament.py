"""Tournaments (Lords of Men, The Tournament, pp. 64-69).

- A patron should spend 10 pounds a point of his Prudhomme Reputation to
  hold one (p. 66); a sponsor pays about 4 pounds a season for each knight
  he retains (p. 66); a prize is worth about a pound a point of the
  winner's Prudhomme Reputation (p. 69).
- A season of tourneying earns the highest of: riding at the head of a
  company, ransoming a well-matched opponent, a feat of daring or one of
  unquestionable honour, 1 experience point each; ransoming a stronger
  opponent, or a prize, 2 (p. 68). Not paying a ransom is an experience
  point toward a fitting bad Reputation (p. 67).
- Hosting one or more tournaments in a season is 1 point toward the
  patron's Prudhomme, 2 if lavish, and 1 more for an artist's record of
  aesthetic quality at least his Prudhomme; patrons hosting together share
  the points equally (p. 69).
- The grand charge as random encounters: a stress roll + Prudhomme on the
  Melee Events Table, with 1 botch die + 1 for each event already rolled;
  each opponent past the first event has a Light Wound more (p. 68).
- As income, a season on the circuit makes (Dexterity + Single or Great
  Weapon) x the Wealth Multiplier (Poor 2, average 3, Wealthy 6) Labor
  Points, and an errant knight needs 36 a year (p. 69, from City & Guild's
  Labor Points).
"""

from __future__ import annotations

from collections.abc import Iterable

from ..models import Character
from . import scores
from .rounding import round_down, round_up
from .supplement_work import WEALTH_MULTIPLIER, wealth

SOURCE = "Lords of Men, The Tournament, pp. 64-69"

#: Pounds a patron spends a point of his Prudhomme Reputation (p. 66).
PATRON_POUNDS = 10
#: Pounds a season for each knight a sponsor retains (p. 66).
SPONSOR_POUNDS = 4
#: A prize's value a point of the winner's Prudhomme Reputation (p. 69).
PRIZE_POUNDS = 1
#: Labor Points an errant knight needs a year (p. 69).
LIVING_LABOR = 36
#: Experience toward a fitting bad Reputation for each ransom not paid
#: (p. 67).
UNPAID_RANSOM_XP = 1

#: A knight's season at the tourney: what he did, and its experience
#: points toward his Prudhomme Reputation (p. 68). Only the highest counts.
KNIGHT_DEEDS: dict[str, tuple[str, int]] = {
    "company": ("Rode at the head of a company", 1),
    "matched": ("Took ransom from a well-matched opponent", 1),
    "daring": ("A feat of daring", 1),
    "honour": ("A feat of unquestionable honour", 1),
    "stronger": ("Took ransom from a stronger opponent", 2),
    "prize": ("Was awarded a prize", 2),
}

#: Hosting: none, one or more tournaments in the season, or a lavish one
#: (p. 69).
HOSTING: dict[str, tuple[str, int]] = {
    "": ("Hosted none", 0),
    "hosted": ("Hosted one or more", 1),
    "lavish": ("Hosted a lavish one", 2),
}

#: The Melee Events Table (p. 68): the lowest roll each line needs.
MELEE_EVENTS: tuple[tuple[int, str], ...] = (
    (0, "An inexperienced knight presents himself as a target."),
    (3, "A lone Poor knight presents himself as a target."),
    (5, "A lone average knight presents himself as a target."),
    (7, "A Poor knight guarded by a company presents himself as a target."),
    (9, "An average knight guarded by a company presents himself as a target."),
    (11, "A Wealthy knight guarded by a company presents himself as a target."),
    (13, "A group of equal size targets the character's company."),
    (15, "A large company of two combat groups targets the character's company."),
    (17, "A large company of three combat groups targets the character's company."),
)


#: The ransom it is reasonable to take, by the beaten knight's means (p.
#: 67): never service or an oath.
RANSOMS: dict[str, str] = {
    "Wealthy": "his horse and his armor",
    "average": "his horse or his armor",
    "Poor": "perhaps his weapons",
    "inexperienced": "little: it is poor manners to take much from a young knight",
}


def ransom_due(line: str) -> str:
    """What a fair ransom is from the knight a Melee Events line presents
    (a company's opponents are judged one by one)."""
    for means in ("Wealthy", "average", "Poor", "inexperienced"):
        if means.casefold() in line.casefold():
            return RANSOMS[means]
    return "as each knight's means allow"


def knight_xp(done: Iterable[str]) -> int:
    """The season's experience points toward Prudhomme: the highest of what
    he did, not their sum."""
    return max((KNIGHT_DEEDS[k][1] for k in done if k in KNIGHT_DEEDS), default=0)


def patron_xp(hosting: str, artist_quality: int | None, prudhomme: int) -> int:
    """A season's experience points toward a patron's Prudhomme, before they
    are shared: the hosting's, and 1 for an artist's record whose aesthetic
    quality is at least his Prudhomme (none without hosting)."""
    base = HOSTING.get(hosting, HOSTING[""])[1]
    if base == 0:
        return 0
    artist = 1 if artist_quality is not None and artist_quality >= prudhomme else 0
    return base + artist


def share(xp: int, patrons: int) -> int:
    """Each patron's share when `patrons` host together, rounded down."""
    return round_down(xp / max(1, patrons))


def patron_spend(prudhomme: int) -> int:
    """What befits a patron to spend on a tournament, in pounds."""
    return PATRON_POUNDS * max(0, prudhomme)


def prize_value(prudhomme: int) -> int:
    """A prize's baseline value for its winner, in pounds."""
    return PRIZE_POUNDS * max(0, prudhomme)


def sponsor_cost(knights: int, seasons: int = 1) -> int:
    """Retaining `knights` for the tourney for `seasons`, in pounds."""
    return SPONSOR_POUNDS * max(0, knights) * max(0, seasons)


def melee_event(total: int) -> str:
    """The Melee Events Table's line for a roll + Prudhomme of `total`."""
    found = MELEE_EVENTS[0][1]
    for need, text in MELEE_EVENTS:
        if total >= need:
            found = text
    return found


def melee_botch_dice(events_rolled: int) -> int:
    """Botch dice on the next Melee Events roll: 1 + one per event so far."""
    return 1 + max(0, events_rolled)


def opponent_light_wounds(event: int) -> int:
    """The short-term Light Wounds the opponents of the `event`th event
    (counting from 1) already carry."""
    return max(0, event - 1)


def weapon_score(character: Character) -> int:
    """The better of his Single Weapon and Great Weapon."""
    return max(
        scores.ability_level(character, "Single Weapon"),
        scores.ability_level(character, "Great Weapon"),
    )


def labor_per_season(character: Character) -> int:
    """Labor Points from a season on the circuit: (Dexterity + Single or
    Great Weapon) x the Wealth Multiplier, never below 0."""
    base = character.characteristics.dexterity + weapon_score(character)
    return max(0, base) * WEALTH_MULTIPLIER[wealth(character)]


def seasons_to_live(character: Character) -> int | None:
    """The seasons a year an errant knight must tourney to meet his 36
    Labor Points; None when tourneying earns him none."""
    per_season = labor_per_season(character)
    if per_season <= 0:
        return None
    return round_up(LIVING_LABOR / per_season)
