"""Familiars as lab work: binding (or strengthening) the bond and
empowering it with bond powers. The familiar is the magus's own, recorded
on his sheet (its Might and Size) before the season.

- Binding: any appropriate Technique + Form Lab Total (Familiar
  Specialization) must reach 25 + Might + 5 x Size; one season. The Lab
  Total buys the three cords (0, 5, 15, 30, 50, 75 points for 0-5). Vis:
  Lab Total / 5 pawns (rounded up), each of the Technique or Form in any
  mix, less what an earlier binding spent when strengthening it.
- A bond power is instilled like an effect in an invested device: Lab
  Total above its modified level (worked out from its uses per day,
  Penetration and modifications, or typed), Lab Total - level points a
  season, its vis (level / 10, of its Technique or Form in any mix) in the
  first season.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from ..models import (
    CORD_SCORE_COSTS,
    BondPower,
    Character,
    Familiar,
    Laboratory,
    Saga,
    SeasonPlan,
)
from . import enchantment, lab
from .breakdown import Line
from .rounding import round_up

if TYPE_CHECKING:
    from .lab_seasons import LabWork

SOURCE = "Ars Magica Definitive Edition, Chapter 8: Laboratory, Familiars, pp. 265-268"
BIND_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, The Initial Bond, pp. "
    "266-267"
)
EMPOWER_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Empowering the Bond, pp. "
    "267-268"
)

BIND = "bind_familiar"
EMPOWER = "empower_bond"
ACTIVITIES: tuple[str, ...] = (BIND, EMPOWER)
BASE_LEVEL = 25


#: Bjornaer magi cannot bind familiars (DE p. 234).
HEARTBEAST = "vf_heartbeast"


#: The book's Suggested Familiars by Art: animals that suit each Art
#: (DE p. 266). The bond's Arts must suit the animal or its powers, so
#: this is advice: a troupe may find another fitting reason.
SUGGESTED_FAMILIARS: dict[str, tuple[str, ...]] = {
    "Creo": ("beaver", "eagle", "lizard", "pelican", "weasel", "any that rejuvenates"),
    "Intellego": (
        "cat (tortoiseshell)",
        "crow",
        "goat",
        "raven",
        "woodpecker",
        "toad",
        "any with keen senses",
        "any thought to foretell",
    ),
    "Muto": (
        "cat (white or tortoiseshell)",
        "fox",
        "hare",
        "moth",
        "butterfly",
        "toad",
        "amphibians",
    ),
    "Perdo": ("asp", "hedgehog", "salamander", "shrew", "weasel", "any venomous"),
    "Rego": (
        "badger",
        "cat (black)",
        "cockerel",
        "dog",
        "lion",
        "owl",
        "wolf",
        "any pack leader",
    ),
    "Animal": ("any animal",),
    "Aquam": (
        "coot",
        "duck",
        "frog",
        "kingfisher",
        "otter",
        "swan",
        "any semi-aquatic",
    ),
    "Auram": ("crow", "kingfisher", "spider", "any bird", "bat"),
    "Corpus": ("caladrius", "cat", "dog", "goose"),
    "Herbam": ("beaver", "monkey", "squirrel", "woodpecker"),
    "Ignem": ("eagle", "hercinia", "salamander", "scitalis", "very small dragons"),
    "Imaginem": ("chameleon", "cricket", "magpie", "partridge", "peacock", "scitalis"),
    "Mentem": (
        "ape",
        "cat (black or tortoiseshell)",
        "fox",
        "owl",
        "wolf",
        "any with Intelligence",
    ),
    "Terram": ("badger", "hedgehog", "ferret", "frog", "fox", "mole", "mouse"),
    "Vim": ("hoopoe", "any magical animal"),
}
SUGGESTED_SOURCE = "Ars Magica Definitive Edition, Suggested Familiars by Art, p. 266"


def suits(art: str, species: str) -> bool:
    """Whether the book's list for `art` names `species` (a word of it:
    "falcon" doesn't match, "barn owl" matches owl)."""
    words = set(species.casefold().replace(",", " ").split())
    return any(
        animal.split(" (")[0] in words for animal in SUGGESTED_FAMILIARS.get(art, ())
    )


def fitting_note(familiar: Familiar, technique: str, form: str) -> str:
    """What the book suggests for the bond's two Arts, and whether it names
    the familiar's kind: advice beside the choice (DE p. 266)."""
    lines = [
        f"{art}: {', '.join(SUGGESTED_FAMILIARS[art])}"
        for art in (technique, form)
        if art in SUGGESTED_FAMILIARS
    ]
    if not lines:
        return ""
    kind = familiar.species or familiar.name
    named = [art for art in (technique, form) if kind and suits(art, kind)]
    verdict = (
        f"The list names a {kind} for {' and '.join(named)}."
        if named
        else f"Neither list names a {kind} by name: the Arts must suit the "
        "animal or its powers (a bird suits Auram), as the troupe decides."
        if kind
        else ""
    )
    return (
        "Suggested familiars (DE p. 266): "
        + "; ".join(lines)
        + (f". {verdict}" if verdict else ".")
    )


def binding_level(familiar: Familiar) -> int:
    """25 + Magic Might + 5 x Size."""
    return BASE_LEVEL + familiar.magic_might + 5 * familiar.size


def cords_of(plan: SeasonPlan) -> tuple[int, int, int]:
    return plan.golden_cord, plan.silver_cord, plan.bronze_cord


def power_of(familiar: Familiar, plan: SeasonPlan) -> BondPower | None:
    return next((p for p in familiar.bond_powers if p.id == plan.effect_id), None)


def work(
    saga: Saga,
    magus: Character,
    plan: SeasonPlan,
    lab_: Laboratory,
    options: lab.LabOptions,
) -> tuple[list[str], LabWork | None]:
    """The problems with a season of familiar work, or what it does."""
    from .lab_seasons import LabWork, vis_pool, whose_vis

    familiar = saga.familiar_of(magus.id)
    if familiar is None:
        return [
            f"{magus.name} has no familiar: add it (with its Might and Size) "
            "on the magus's sheet first."
        ], None
    if lab.distraction_penalty(max(0, plan.days_away)) is None:
        return [
            f"{plan.days_away} days away from the laboratory: no lab work is "
            "possible this season (more than 20)."
        ], None
    pool = vis_pool(saga, magus, plan)

    if plan.activity == BIND:
        if any(vf.vf_id == HEARTBEAST for vf in magus.virtues_flaws):
            return ["Bjornaer magi cannot bind familiars (DE p. 234)."], None
        if not plan.technique or not plan.form:
            return ["Choose the Technique and Form the bond is made with."], None
        bound = (familiar.binding_technique, familiar.binding_form)
        if (
            familiar.year_bound is not None
            and all(bound)
            and (plan.technique, plan.form) != bound
        ):
            return [
                f"Strengthening the bond uses the Arts it was made with: "
                f"{bound[0]} {bound[1]} (DE p. 267)."
            ], None
        total = lab.lab_total(
            saga,
            magus,
            plan.technique,
            plan.form,
            lab_,
            activity="bind_familiar",
            days_missed=max(0, plan.days_away),
            experimenting=plan.experimenting,
        )
        total = options(magus, plan, plan.technique, plan.form, total)
        lab_total = int(total.total)
        level = binding_level(familiar)
        if lab_total < level:
            return [
                f"Lab Total {lab_total} is below the binding level {level} "
                f"(25 + Might {familiar.magic_might} + 5 x Size {familiar.size})."
            ], None
        cords = cords_of(plan)
        if any(not 0 <= c <= 5 for c in cords):
            return ["Each cord is 0 to 5."], None
        cord_points = sum(cord_cost(c) for c in cords)
        if cord_points > lab_total:
            return [
                f"The cords cost {cord_points} points; the Lab Total is {lab_total}."
            ], None
        pawns = max(0, round_up(lab_total / 5) - familiar.vis_spent_binding)
        short, split = _payment(
            magus,
            plan,
            (plan.technique, plan.form),
            pawns,
            pool,
            whose_vis(magus, plan),
            what="The bond takes",
        )
        if short:
            return [short], None
        return [], LabWork(
            None,
            total,
            level,
            finished=True,
            vis_cost=split,
            familiar=familiar,
        )

    # Empowering the bond with a power.
    power = power_of(familiar, plan)
    if power is None:
        return [
            f"Choose the bond power (add it on {familiar.name}'s sheet, with "
            "Instilling 0)."
        ], None
    if power.instilling_progress is None:
        return [f"{power.name} is already instilled."], None
    if not power.technique or not power.form or power.level <= 0:
        return [f"Give {power.name} its Technique, Form and level."], None
    level = enchantment.bond_power_level(power)
    total = lab.lab_total(
        saga,
        magus,
        power.technique,
        power.form,
        lab_,
        activity="bind_familiar",
        days_missed=max(0, plan.days_away),
        experimenting=plan.experimenting,
        similar_spell_level=lab.similar_spell_level(saga, magus, plan.similar_spell_id),
    )
    # Sharing the Arts the bond was made with: +5 for one, +10 for both
    # (DE pp. 267-268), in place of an invested device's shared-Arts bonus.
    shared = (power.technique == familiar.binding_technique) + (
        power.form == familiar.binding_form
    )
    if shared:
        total = lab.with_lines(
            total,
            [
                Line(
                    "Shares the binding's "
                    + ("Technique and Form" if shared == 2 else "Technique or Form"),
                    amount=5 * shared,
                    source=EMPOWER_SOURCE,
                )
            ],
        )
    total = options(magus, plan, power.technique, power.form, total)
    lab_total = int(total.total)
    if lab_total <= level:
        return [
            f"Lab Total {lab_total} isn't above {power.name}'s level "
            f"{level}: it can't be instilled yet."
        ], None
    cost: dict[str, int] = {}
    if power.instilling_progress == 0:
        short, cost = _payment(
            magus,
            plan,
            (power.technique, power.form),
            round_up(level / 10),
            pool,
            whose_vis(magus, plan),
            what="It takes",
        )
        if short:
            return [short], None
    gained = lab.points_per_season(lab_total, level)
    before = power.instilling_progress
    return [], LabWork(
        None,
        total,
        level,
        points_before=before,
        points_gained=gained,
        finished=before + gained >= level,
        vis_cost=cost,
        familiar=familiar,
        power=power,
    )


def _payment(
    magus: Character,
    plan: SeasonPlan,
    arts: tuple[str, str],
    pawns: int,
    pool: Mapping[str, int],
    whose: str,
    *,
    what: str,
) -> tuple[str, dict[str, int]]:
    """What's wrong with paying `pawns` of vis for the work (or ""), and
    the pawns of each Art paid: of the plan's chosen Art, with its pawns of
    the other Art, at most twice Magic Theory, from `pool`."""
    art = plan.vis_art if plan.vis_art in arts else ""
    if pawns and not art:
        return f"Choose the vis to pay with: {arts[0]} or {arts[1]}.", {}
    limit = lab.vis_limit(magus)
    if pawns > limit:
        return (
            f"{what} {pawns} pawns of vis; {magus.name} can handle {limit} in a "
            "season (twice Magic Theory).",
            {},
        )
    split = enchantment.split_vis(arts, art, plan.other_vis, pawns) if art else {}
    return enchantment.vis_shortfall(split, pool, whose), split


def cord_cost(score: int) -> int:
    """The point cost of a Cord score (0-5), from the fixed table."""
    return CORD_SCORE_COSTS[score]
