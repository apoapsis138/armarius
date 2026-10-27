"""A character's Living Conditions Modifier, which aging rolls and, with
Art & Academe's medicine, disease rolls and prognosis use.

The covenant's Living Conditions (the magi's for a magus or a noble, the
mundanes' for anyone else: DE p. 190's table puts them in one row), half the Health of a magus's laboratory, rounded down
(negative Health too: -3 gives -2) (DE p. 289), what the place he lives
in adds, and a physician's regimen (rules.medicine).
"""

from __future__ import annotations

from .. import catalog
from ..models import Character, Covenant, Saga
from . import effects, medicine, sites
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
    )
