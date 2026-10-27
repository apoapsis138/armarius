"""A character's Living Conditions Modifier, which aging rolls and, with
Art & Academe's medicine, disease rolls and prognosis use.

The covenant's Living Conditions (the magi's for a magus or a noble, the
mundanes' for anyone else: DE p. 190's table puts them in one row), half the Health of a magus's laboratory, rounded down
(negative Health too: -3 gives -2) (DE p. 289), what the place he lives
in adds, and a physician's regimen (rules.medicine).
"""

from __future__ import annotations

from .. import catalog
from ..models import SEASONS, Character, Covenant, Saga
from . import effects, medicine, sites
from . import siege as siege_rules
from .lab_stats import lab_characteristic_total
from .rounding import round_down

SOURCE = "Ars Magica Definitive Edition, Laboratory Health, p. 289"
SEASON_SOURCE = (
    "Ars Magica Definitive Edition, Points for Inhabitants of a Typical "
    "Covenant, p. 190"
)

#: The Living Conditions Modifier a covenant's season gives, as (a magus
#: or noble, anyone else): companions, specialists, craftsmen and other
#: covenfolk alike (DE p. 190).
SEASON_LIVING: dict[str, tuple[int, int]] = {
    "Spring": (1, 0),
    "Winter": (1, 0),
    "Summer": (2, 1),
    "Autumn": (2, 1),
}


def season_living(covenant: Covenant, *, magi: bool) -> int:
    """What the covenant's season gives a magus (`magi`) or anyone else."""
    pair = SEASON_LIVING.get(covenant.covenant_season, (0, 0))
    return pair[0] if magi else pair[1]


def covenant_living(covenant: Covenant, *, magi: bool) -> int:
    """The covenant's Living Conditions for its magi or everyone else: the
    typed value, else what its season gives."""
    typed = (
        covenant.living_conditions_magi if magi else covenant.living_conditions_mundane
    )
    return typed if typed is not None else season_living(covenant, magi=magi)


def living_text(covenant: Covenant, *, magi: bool) -> str:
    """ "+2" typed, "+2 (Summer)" from the season."""
    value = covenant_living(covenant, magi=magi)
    typed = (
        covenant.living_conditions_magi if magi else covenant.living_conditions_mundane
    )
    return (
        f"{value:+d}"
        if typed is not None
        else f"{value:+d} ({covenant.covenant_season})"
    )


#: The Social Status Virtues of a noble, who lives as a magus does (DE p.
#: 190's "Magus, Noble" row).
NOBLE_VIRTUES = frozenset({"vf_landed_noble", "vf_knight", "vf_gentleman_woman"})


def lives_as_magus(character: Character) -> bool:
    """Whether the covenant's magi's Living Conditions are this character's:
    a magus's, or a noble's (DE p. 190)."""
    return character.type == "magus" or any(
        vf.vf_id in NOBLE_VIRTUES for vf in character.virtues_flaws
    )


#: A laboratory's Health / LAB_HEALTH_DIVISOR, rounded down, adds to its
#: magus's Living Conditions.
LAB_HEALTH_DIVISOR = 2


def living_conditions(saga: Saga, character: Character) -> int:
    covenant = saga.covenant(character.covenant_id)
    living = 0
    if covenant is not None:
        living = covenant_living(covenant, magi=lives_as_magus(character))
    lab = saga.laboratory(character.assigned_lab_id)
    if lab is not None and character.type == "magus":
        health = lab_characteristic_total(
            lab, catalog.load_lab_virtue_flaw_catalog_by_id(), "health", saga
        )[3]
        living += round_down(health / LAB_HEALTH_DIVISOR)
    here = sites.character_effects(saga, character, "living_conditions")
    return (
        living
        + int(effects.amount_total(here))
        + medicine.regimen_bonus(saga, character)
        + campaign_living(saga, character)
        + siege_living(saga, character)
    )


#: A year with a season under siege (Lords of Men p. 112).
SIEGE_LIVING = siege_rules.LIVING_UNDER_SIEGE


def siege_days_in(start_season: str, start_year: int, days: int, year: int) -> int:
    """How many of a siege's days fall in `year`, the siege begun at the
    start of `start_season` of `start_year` and run `days` days (a season
    91 days, a year 364, as the siege's own intervals count them)."""
    season = siege_rules.INTERVAL_DAYS["Season"]
    begun = (start_year * 4 + SEASONS.index(start_season)) * season
    first, last = year * 4 * season, (year + 1) * 4 * season
    return max(0, min(begun + days, last) - max(begun, first))


def siege_living(saga: Saga, character: Character) -> int:
    """-2 for a year in which the character spent at least a season (91
    days) inside a besieged castle (Lords of Men p. 112), counted from the
    siege's start and the days it has run."""
    season = siege_rules.INTERVAL_DAYS["Season"]
    besieged = any(
        character.id in s.inside
        and siege_days_in(s.season, s.year, s.days, saga.current_year) >= season
        for s in saga.sieges
    )
    return SIEGE_LIVING if besieged else 0


#: A year with a season in a campaigning army (Lords of Men p. 102).
CAMPAIGN_LIVING = -1
#: A whole year of it brings a Disease Avoidance roll (p. 102).
CAMPAIGN_YEAR = 4
#: Coming back to land put to chevauchee: -2 on the next Aging roll
#: (Lords of Men p. 103).
CHEVAUCHEE_AGING = -2


def campaign_seasons(character: Character, year: int) -> int:
    return sum(1 for s in character.campaign_seasons if s.startswith(f"{year} "))


def campaign_living(saga: Saga, character: Character) -> int:
    """-1 for a year with a season campaigning (Lords of Men p. 102)."""
    return CAMPAIGN_LIVING if campaign_seasons(character, saga.current_year) else 0


def chevauchee_aging(saga: Saga, character: Character) -> int:
    """-2 on the Aging roll for those of land put to chevauchee this year,
    returning to it (Lords of Men p. 103): everyone of the ravaged
    covenant."""
    ravaged = any(
        b.chevauchee_on
        and b.chevauchee_on == character.covenant_id
        and b.year == saga.current_year
        for b in saga.battles
    )
    return CHEVAUCHEE_AGING if ravaged else 0
