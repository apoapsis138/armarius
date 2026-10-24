"""Familiars as lab work: binding (or strengthening) the bond and
empowering it with bond powers. The familiar is the magus's own, recorded
on his sheet (its Might and Size) before the season.

- Binding: any appropriate Technique + Form Lab Total (Familiar
  Specialization) must reach 25 + Might + 5 x Size; one season. The Lab
  Total buys the three cords (0, 5, 15, 30, 50, 75 points for 0-5). Vis:
  Lab Total / 5 pawns (rounded up) of the Technique or Form, less what an
  earlier binding spent when strengthening it.
- A bond power is instilled like an effect in an invested device: Lab
  Total above its level, Lab Total - level points a season, its vis
  (level / 10) in the first season.
"""

from __future__ import annotations

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
from . import lab
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
    limit = lab.vis_limit(magus)
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
        art = plan.vis_art if plan.vis_art in (plan.technique, plan.form) else ""
        if pawns and not art:
            return [
                f"Choose the vis to pay with: {plan.technique} or {plan.form}."
            ], None
        if pawns > limit:
            return [
                f"The bond takes {pawns} pawns of vis; {magus.name} can handle "
                f"{limit} in a season (twice Magic Theory)."
            ], None
        held = pool.get(art.lower(), 0) if art else 0
        if held < pawns:
            return [
                f"The bond takes {pawns} pawns of {art} vis; "
                f"{whose_vis(magus, plan)} raw vis has {held}."
            ], None
        return [], LabWork(
            None,
            total,
            level,
            finished=True,
            vis_cost={art: pawns} if pawns else {},
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
    if lab_total <= power.level:
        return [
            f"Lab Total {lab_total} isn't above {power.name}'s level "
            f"{power.level}: it can't be instilled yet."
        ], None
    cost: dict[str, int] = {}
    if power.instilling_progress == 0:
        pawns = round_up(power.level / 10)
        art = plan.vis_art if plan.vis_art in (power.technique, power.form) else ""
        if not art:
            return [
                f"Choose the vis to pay with: {power.technique} or {power.form}."
            ], None
        if pawns > limit:
            return [
                f"It takes {pawns} pawns of vis; {magus.name} can handle {limit} "
                "in a season (twice Magic Theory)."
            ], None
        held = pool.get(art.lower(), 0)
        if held < pawns:
            return [
                f"It takes {pawns} pawns of {art} vis; {whose_vis(magus, plan)} "
                f"raw vis has {held}."
            ], None
        cost = {art: pawns}
    gained = lab.points_per_season(lab_total, power.level)
    before = power.instilling_progress
    return [], LabWork(
        None,
        total,
        power.level,
        points_before=before,
        points_gained=gained,
        finished=before + gained >= power.level,
        vis_cost=cost,
        familiar=familiar,
        power=power,
    )


def cord_cost(score: int) -> int:
    """The point cost of a Cord score (0-5), from the fixed table."""
    return CORD_SCORE_COSTS[score]
