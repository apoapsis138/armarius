"""Ancient Magic's seasons: learning to measure the array of fixed stars,
the first stage of integrating Ptolemy's coordinates (The Hesperides,
p. 90). An apprentice of a master who knows it learns it in training."""

from __future__ import annotations

import random

from ...models import Character, Saga, SeasonPlan
from .. import activity_groups as groups
from .. import ancient_integrations as am
from .base import MAGI, SimpleActivity, SupplementWork, register, source

HESPERIDES = source("Ancient Magic, The Hesperides, p. 90", "AM")


def _measure_stars(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """The method learned from the corrupt copies of The Geography; the
    system still needs calibrating at its origin."""
    result.progress.append((am.MEASURING_KIND, am.MEASURING, 1, 1))
    result.notes.append(
        "Learned to measure the array of fixed stars. To derive coordinates "
        "the system must still be calibrated at its origin (the Zero "
        "Longitude, in the Purple Islands); then an Intelligence + Artes "
        f"Liberales roll against {am.observation_ease()} gives where one stands."
    )


def _measure_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    if am.knows_stellar_measurement(character):
        return [f"{character.name} already knows how to measure the fixed stars."]
    return []


register(
    SimpleActivity(
        "measure_fixed_stars",
        "Learn to measure the fixed stars",
        "A season learning Ptolemy's measure of the array of fixed stars, the "
        "first stage of his coordinates (no experience).",
        HESPERIDES,
        "AM-2",
        who=MAGI,
        no_xp=True,
        group=groups.STUDY,
    ),
    _measure_stars,
    _measure_problems,
)
