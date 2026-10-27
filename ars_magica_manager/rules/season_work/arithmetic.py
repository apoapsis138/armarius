"""The Mysteries Revised Edition's arithmetic magic as seasons: inventing
Rotes (Hermetic Numerology, pp. 92-93) and binding an enchanted structure
(Hermetic Architecture, pp. 97-99). The rules are rules.tmre_numerology's.

- Inventing Rotes: the plan names the Technique and Form (technique,
  form) and the Rotes ("Name: level; Name: level (text)", its title). The
  magus's laboratory gives the Rote Lab Total, which must cover each Rote
  (twice its level, its level from a Lab Text); each one invented is a
  finished Progress record ("rote", "Name (CrIg 10)").
- Binding an enchanted structure: the plan names the structure (title),
  its highest component effect's level (book_level) and its Size
  multiplier (effect_params["size"]). The season places the components
  (Intelligence + Artes Liberales against 6 + Size; each failure costs the
  plan's days of recomputing and reworking, effect_params["rework_days"],
  a day to a month, and he tries again while the season's days last) and
  casts Bind the Mystical Structure, paying its Vim vis from the pool the
  plan's vis_from names. A bound structure is a finished Progress record
  ("enchanted structure").
"""

from __future__ import annotations

import random

from ... import vis
from ...arts import FORMS, TECHNIQUES
from ...models import Character, Saga, SeasonPlan
from .. import activity_groups as groups
from .. import casting, dice
from .. import tmre_numerology as tn
from ..journeys import SEASON_DAYS
from .base import MAGI, SimpleActivity, SupplementWork, register, source

ROTES = source(tn.ROTE_SOURCE, "TMRE")
BINDING = source(
    "The Mysteries Revised Edition, Hermetic Architecture: Completing and "
    "Binding the Enchantment, pp. 98-99",
    "TMRE",
)
STORY = "TMRE-5"

INVENT_ROTES = "invent_rotes"
BIND_STRUCTURE = "bind_mystical_structure"
#: A bound structure's Progress record.
STRUCTURE_KIND = "enchanted structure"


def _rotes(plan: SeasonPlan) -> list[tn.Rote] | None:
    return tn.parse_rotes(plan.title, plan.technique, plan.form)


def _rote_total(saga: Saga, character: Character, plan: SeasonPlan) -> int | None:
    own = saga.laboratory(character.assigned_lab_id)
    if own is None:
        return None
    return int(
        tn.rote_lab_total(
            saga,
            character,
            plan.technique,
            plan.form,
            own,
            days_missed=max(0, plan.days_away),
        ).total
    )


def _invent_rotes(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """Each Rote invented: a finished record of it."""
    rotes = _rotes(plan) or []
    total = _rote_total(saga, character, plan) or 0
    spent = sum(tn.rote_points(r) for r in rotes)
    for rote in rotes:
        result.progress.append((tn.ROTE_KIND, rote.record_name, rote.level, rote.level))
    names = ", ".join(r.record_name for r in rotes)
    result.notes.append(
        f"Rote Lab Total {total} (Rotes up to level {tn.max_rote_level(total)}): "
        f"{spent} point(s) invent {names}. Each is cast with no die or Fatigue, "
        "at half its Rote Casting Score (TMRE pp. 92-93)."
    )


def _rote_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    if not tn.lab_virtues.has(character, tn.NUMEROLOGY):
        return [f"{character.name} needs Hermetic Numerology to invent Rotes."]
    if plan.technique not in TECHNIQUES or plan.form not in FORMS:
        return ["Choose the Rotes' Technique and Form."]
    rotes = _rotes(plan)
    if rotes is None:
        return ['Type each Rote as Name: level, "(text)" after one from a Lab Text.']
    total = _rote_total(saga, character, plan)
    if total is None:
        return [f"{character.name} needs a laboratory to invent Rotes."]
    why = tn.rotes_problem(total, rotes)
    return [why] if why else []


def _size(plan: SeasonPlan) -> int | None:
    text = (plan.effect_params.get("size") or "").strip()
    return int(text) if text.isdigit() and int(text) in tn.SIZES else None


def _rework_days(plan: SeasonPlan) -> int | None:
    """The days each recomputing of the components' places takes (a month
    when the plan doesn't say; None when what it says isn't a day to a
    month)."""
    text = (plan.effect_params.get("rework_days") or "").strip()
    if not text:
        return tn.REWORK_DAYS_DEFAULT
    if not text.isdigit():
        return None
    days = int(text)
    return days if tn.REWORK_DAYS_LEAST <= days <= tn.REWORK_DAYS_MOST else None


def _bind(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """Placing the components, then the binding ritual."""
    size = _size(plan) or 7  # a Structure; _bind_problems asks for it
    name = plan.title.strip()
    level = tn.bind_level(plan.book_level or 0, size)
    pawns = tn.bind_vis(character, level) or 0
    ease = tn.placement_ease(size)
    placing = character.characteristics.intelligence + tn.roll_bonus(
        character, tn.GEOMETRY_SPECIALTY
    )
    score = int(tn.bind_casting_score(saga, character).total)
    result.vis_cost["Vim"] = pawns
    rework = _rework_days(plan) or tn.REWORK_DAYS_DEFAULT
    if rng is None:
        result.notes.append(
            f"Placing {tn.components_needed(size)} components: {placing} + stress "
            f"die against {ease}, each miss costing {rework} day(s) of reworking "
            "and tried again while the season lasts; then Bind the Mystical Structure (ReVi Ritual, "
            f"level {level}, {pawns} pawn(s) of Vim): {score} + stress die."
        )
        return
    # No limit on the tries but time: each failure costs the days of
    # recomputing and reworking, and he tries again while the season lasts
    # (TMRE p. 98).
    days = misses = 0
    while True:
        roll = dice.roll(rng, placing, ease_factor=ease, saga=saga)
        if roll.die.botched:
            result.notes.append(
                _misses_text(misses, rework)
                + f"Placing the components botched ({roll.die.botches} zero(es)) "
                f"on day {days + 1}: the error goes unnoticed until too late, and "
                "some disaster befalls (TMRE p. 98)."
            )
            result.vis_cost.clear()
            return
        if roll.succeeded:
            result.notes.append(
                _misses_text(misses, rework)
                + f"The components of {name} are placed on day {days + 1}: "
                f"{roll.total} against {ease}."
            )
            break
        misses += 1
        days += rework
        if days >= SEASON_DAYS:
            result.notes.append(
                _misses_text(misses, rework)
                + "The season ends before the components are placed."
            )
            result.vis_cost.clear()
            return
    roll = dice.roll(
        rng, score, botch_dice=casting.botch_dice(vis_pawns=pawns), saga=saga
    )
    outcome = casting.ritual_outcome(roll.total, level)
    if roll.die.botched:
        result.notes.append(
            f"Bind the Mystical Structure botched ({roll.die.botches} zero(es)); "
            f"its {pawns} pawn(s) of Vim are spent."
        )
        return
    lost = f"{outcome.fatigue} long-term Fatigue level(s)"
    if not outcome.cast:
        result.notes.append(
            f"Bind the Mystical Structure fails: {roll.total} against level "
            f"{level}; {lost} lost and its {pawns} pawn(s) of Vim spent."
        )
        return
    result.progress.append((STRUCTURE_KIND, name, 1, 1))
    result.notes.append(
        f"Bind the Mystical Structure (level {level}): {roll.total}, {lost} lost, "
        f"{pawns} pawn(s) of Vim spent. {name}'s enchantment works while every "
        "component is in its place (TMRE pp. 98-99)."
    )


def _misses_text(misses: int, rework: int) -> str:
    """The failed placements before the last roll, and the days they cost."""
    if not misses:
        return ""
    return (
        f"Placing the components failed {misses} time(s), each costing "
        f"{rework} day(s) recomputing and reworking their places "
        f"({misses * rework} day(s) in all). "
    )


def _bind_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    if not tn.lab_virtues.has(character, tn.ARCHITECTURE):
        return [f"{character.name} needs Hermetic Architecture to bind a structure."]
    if not plan.title.strip():
        return ["Name the structure enchanted."]
    if plan.book_level is None or plan.book_level < 0:
        return ["Type the level of its highest component effect."]
    size = _size(plan)
    if size is None:
        return ["Choose its Size multiplier (5 to 10)."]
    if _rework_days(plan) is None:
        return [
            "Type the days recomputing the components' places takes: "
            f"{tn.REWORK_DAYS_LEAST} (posts in a field) to "
            f"{tn.REWORK_DAYS_MOST} (niches in a building) (TMRE p. 98)."
        ]
    level = tn.bind_level(plan.book_level, size)
    pawns = tn.bind_vis(character, level)
    if pawns is None:
        return [f"{character.name} can't cast Rituals (Rigid Magic)."]
    too_many = casting.vis_limit_problem(character, "Vim", pawns)
    if too_many:
        return [too_many]
    held = vis.season_pool(saga, character, plan).get("vim", 0)
    if held < pawns:
        return [
            f"Bind the Mystical Structure (level {level}) takes {pawns} pawn(s) "
            f"of Vim vis; {vis.payer(character, plan)} raw vis has {held}."
        ]
    return []


register(
    SimpleActivity(
        INVENT_ROTES,
        "Invent Rotes (Hermetic Numerology)",
        "A season in the laboratory inventing Rotes of one Technique and "
        "Form: each costs twice its level of the Rote Lab Total (its level "
        "from a Lab Text), none above a fifth of it.",
        ROTES,
        STORY,
        hint="Exposure (2 xp), as other lab work, in Magic Theory.",
        who=MAGI,
        group=groups.MYSTERIES,
    ),
    _invent_rotes,
    _rote_problems,
)
register(
    SimpleActivity(
        BIND_STRUCTURE,
        "Bind an enchanted structure (Hermetic Architecture)",
        "A season placing a structure's enchanted components (Intelligence + "
        "Artes Liberales against 6 + Size) and casting Bind the Mystical "
        "Structure over them.",
        BINDING,
        STORY,
        hint="Exposure (2 xp), e.g. in Artes Liberales.",
        who=MAGI,
        group=groups.MYSTERIES,
    ),
    _bind,
    _bind_problems,
)
