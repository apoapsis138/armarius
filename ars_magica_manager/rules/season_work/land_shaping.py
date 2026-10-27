"""Transforming Mythic Europe's shaping of the land as a season: a magus
casts the Rituals of one of his covenant's land projects (its wall, fill,
surface life and wards), in order. The rules are rules.land_shaping's.

The plan names the project (its title) and the pool its vis comes from
(vis_from). Each Ritual takes fifteen minutes a magnitude and a pawn of vis
a magnitude, of its Form first and then its Technique, at most the magus's
score in each (DE p. 213); its long-term Fatigue comes back with a night's
sleep, so a season casts every Ritual left that the vis allows. The
Casting Total is the Ritual's (Casting Score + Artes Liberales +
Philosophiae + stress die, in the covenant's aura); a botch or a failure
spends the vis and ends the season's casting, for the troupe to resolve.
Each Ritual cast is a point of the magus's Progress record toward the
project (LAND_KIND, named for it), its target the project's Rituals.
"""

from __future__ import annotations

import random

from ... import vis
from ...models import LAND_KIND, Character, Saga, SeasonPlan
from .. import activity_groups as groups
from .. import casting, dice, realms
from .. import land_shaping as ls
from ..casting_virtues import ritual_vis
from ..lab import art_score
from .base import MAGI, SimpleActivity, SupplementWork, register, source

SHAPING = source(
    "Transforming Mythic Europe, Chapter Three: The Island of the "
    "Magicians, pp. 54-77; Ars Magica Definitive Edition p. 213",
    "TME",
)
STORY = "933-B"

SHAPE_LAND = "shape_land"
#: The seasons that pay vis, from the pool the plan's vis_from names.
PAYS_VIS = (SHAPE_LAND,)


def _score(magus: Character, art: str) -> int:
    score, bonus = art_score(magus, art)
    return score + bonus


def _draw(
    magus: Character, work: ls.Work, pool: dict[str, int]
) -> dict[str, int] | None:
    """The vis one Ritual takes from what is left of the pool, Form first
    (Art -> pawns), or None when the pool or the magus's Arts fall short."""
    pawns = ritual_vis(magus, work.pawns)
    if pawns is None:
        return None
    taken: dict[str, int] = {}
    for art in (work.form, work.technique):
        have = pool.get(art.lower(), 0)
        part = min(pawns, have, _score(magus, art))
        if part > 0:
            taken[art] = part
            pawns -= part
    return taken if pawns <= 0 else None


def _spend(pool: dict[str, int], taken: dict[str, int], cost: dict[str, int]) -> None:
    for art, pawns in taken.items():
        pool[art.lower()] = pool.get(art.lower(), 0) - pawns
        cost[art] = cost.get(art, 0) + pawns


def _paid(taken: dict[str, int]) -> str:
    return ", ".join(f"{n} {art}" for art, n in taken.items())


def _shape_land(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    found = ls.find_project(saga, plan.title)
    if found is None:
        return
    _, project = found
    total = len(ls.works(project))
    left = ls.remaining(saga, project)
    pool = dict(vis.season_pool(saga, character, plan))
    aura, realm = realms.home_aura(saga, character)
    cast = 0
    for work in left:
        taken = _draw(character, work, pool)
        if taken is None:
            result.notes.append(
                f"{work.name} ({work.arts} {work.level}) needs {work.pawns} pawn(s) "
                f"of {work.form} or {work.technique} vis, at most the magus's score "
                f"in each, from {vis.payer(character, plan)} vis: the season's "
                "casting stops there."
            )
            break
        score = int(
            casting.casting_score(
                character,
                work.technique,
                work.form,
                aura=aura,
                aura_realm=realm,
                ritual=True,
            ).total
        )
        if rng is None:
            _spend(pool, taken, result.vis_cost)
            cast += 1
            result.notes.append(
                f"{work.name} ({work.arts} {work.level}, {work.minutes} minutes, "
                f"{_paid(taken)} vis): {score} + stress die; {work.level}+ casts it "
                f"for a long-term Fatigue level, down to {work.level - 10} for two "
                "or three (DE p. 213)."
            )
            continue
        roll = dice.roll(
            rng,
            score,
            botch_dice=casting.botch_dice(
                vis_pawns=sum(taken.values()), aura_realm=realm, aura=aura, saga=saga
            ),
            saga=saga,
        )
        _spend(pool, taken, result.vis_cost)
        if roll.die.botched:
            result.notes.append(
                f"{work.name} botched ({roll.die.botches} zero(es)): its "
                f"{_paid(taken)} vis is spent, and the troupe decides what the "
                "Ritual did instead."
            )
            break
        outcome = casting.ritual_outcome(roll.total, work.level)
        if not outcome.cast:
            result.notes.append(
                f"{work.name} fails: {roll.total} against level {work.level}; "
                f"{outcome.fatigue} long-term Fatigue level(s) lost and its "
                f"{_paid(taken)} vis spent."
            )
            break
        cast += 1
        result.notes.append(
            f"{work.name} ({work.arts} {work.level}): {roll.total}, cast, "
            f"{outcome.fatigue} long-term Fatigue level(s) lost (back after a "
            f"night's sleep), {_paid(taken)} vis spent."
        )
    if cast:
        result.progress.append((LAND_KIND, project.name, total, cast))


def _problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    found = ls.find_project(saga, plan.title)
    if found is None:
        return ["Choose the land project the season works on."]
    _, project = found
    if not ls.remaining(saga, project):
        return [f"Every Ritual of {project.name} is cast."]
    if ritual_vis(character, 1) is None:
        return ["A magus who can't cast Rituals can't shape the land."]
    return []


register(
    SimpleActivity(
        SHAPE_LAND,
        "Shape the land (cast a land project's Rituals)",
        "A season casting a covenant land project's Rituals in order (its "
        "wall, fill, surface life and wards), each a pawn of vis a magnitude.",
        SHAPING,
        STORY,
        hint="Exposure (2 xp), e.g. in Creo or Terram.",
        who=MAGI,
        group=groups.ORDER,
    ),
    _shape_land,
    _problems,
)
