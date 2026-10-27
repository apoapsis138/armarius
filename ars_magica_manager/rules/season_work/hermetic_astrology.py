"""The Mysteries Revised Edition's season of Hermetic Astrology: making a
precision armillary sphere (pp. 51-53). The astrologer designs it
(Int + Artes Liberales (Astronomy) against 12) and crafts it (Dex + Craft:
Mechanisms or Clocks against 12; Blacksmith at -3 with three more botch
dice), testing and reworking it through the season. A sphere designed for
another to make, or copied from a precise one, is the troupe's: its Ease
Factors are in rules.tmre_divination."""

from __future__ import annotations

import random

from ...models import Character, Saga, SeasonPlan
from .. import activity_groups as groups
from .. import dice
from .. import tmre_divination as td
from .base import MAGI, SimpleActivity, SupplementWork, register, source

SPHERE = source(
    "The Mysteries Revised Edition, Making an Armillary Sphere, p. 52", "TMRE"
)


def _make_sphere(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """The design and craft rolls, each made as the season is played."""
    design = td.astronomy_total(character)
    craft, score, extra = td.best_craft(character)
    hand = character.characteristics.dexterity + score
    if rng is None:
        result.notes.append(
            f"Design: stress die {design:+d} against {td.design_ease()}; craft "
            f"({craft}): stress die {hand:+d} against {td.craft_ease()}"
            + (f", {1 + extra} botch dice" if extra else "")
            + ", both rolled when the season is played."
        )
        return
    designed = dice.roll(rng, design, ease_factor=td.design_ease(), saga=saga)
    made = dice.roll(
        rng, hand, ease_factor=td.craft_ease(), botch_dice=1 + extra, saga=saga
    )
    name = plan.title.strip() or "the armillary sphere"
    result.notes += [
        f"Designing {name}: {td.sphere_outcome(designed, 'design')}",
        f"Crafting it ({craft}): {td.sphere_outcome(made, 'mechanism')}",
    ]
    if designed.succeeded and made.succeeded:
        result.notes.append(
            f"A precise armillary sphere, ready to open as an invested device "
            f"({td.OPENING_PAWNS['base metal']} pawns in base metal, "
            f"{td.OPENING_PAWNS['silver']} in silver, {td.OPENING_PAWNS['gold']} "
            "in gold) for Know the Heavens and Track the Heavens (TMRE p. 53)."
        )


def _sphere_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    if not td.best_craft(character)[0]:
        return [
            f"{character.name} has no Craft: Mechanisms, Clocks or Blacksmith to "
            "build the sphere with."
        ]
    return []


register(
    SimpleActivity(
        "make_armillary_sphere",
        "Make an armillary sphere",
        "A season designing and building a precision armillary sphere, "
        "testing it against the heavens (no experience).",
        SPHERE,
        "TMRE-2",
        who=MAGI,
        no_xp=True,
        group=groups.WORK,
    ),
    _make_sphere,
    _sphere_problems,
)
