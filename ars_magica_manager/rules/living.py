"""A character's Living Conditions Modifier, which aging rolls and, with
Art & Academe's medicine, disease rolls and prognosis use.

The covenant's Living Conditions (the magi's for a magus, the mundanes'
for anyone else), half the Health of a magus's laboratory, rounded down
(negative Health too: -3 gives -2) (DE p. 289), what the place he lives
in adds, and a physician's regimen (rules.medicine).
"""

from __future__ import annotations

from .. import catalog
from ..models import Character, Saga
from . import effects, medicine, sites
from .lab_stats import lab_characteristic_total
from .rounding import round_down

SOURCE = "Ars Magica Definitive Edition, Laboratory Health, p. 289"

#: A laboratory's Health / LAB_HEALTH_DIVISOR, rounded down, adds to its
#: magus's Living Conditions.
LAB_HEALTH_DIVISOR = 2


def living_conditions(saga: Saga, character: Character) -> int:
    covenant = saga.covenant(character.covenant_id)
    living = 0
    if covenant is not None:
        living = (
            covenant.living_conditions_magi
            if character.type == "magus"
            else covenant.living_conditions_mundane
        )
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
