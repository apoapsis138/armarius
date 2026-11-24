"""Work on the laboratory itself, from its Planning tab, and
assisting in someone else's (planned on the assistant's sheet).

- Setting up a laboratory: two seasons, Magic Theory 3; after the first it
  works with the Basic Flaw (-3 General Quality), which the second removes.
  A magus with no laboratory yet plans the first season on the character
  sheet (a new laboratory in their covenant); the second is lab work in it.
- Refining it: +1 Refinement a season, if Magic Theory is at least the new
  Refinement + 3. Every such season rolls a stress die + Intelligence +
  Magic Theory: 12+ gains Highly Organized, 15+ also removes a Hidden
  Defect; a botch gains a Hidden Defect.
- Taking over another's laboratory (Covenants): a season rearranging it,
  rolled like refining; Refinement becomes at most the new owner's Magic
  Theory - 3. A Perception + Magic Theory roll against 3 x the old
  Refinement: failure adds Predecessor (a botch, Hidden Defect too). A
  laboratory with no owner is taken over from the magus's own sheet, and
  becomes theirs when the season is applied (their old one, if any, is
  left without an owner).
- Assisting: a season helping the magus whose lab work it is adds
  Intelligence + Magic Theory to his Lab Total (up to his Leadership in
  helpers) and gives the assistant Exposure in Magic Theory (DE pp. 264-265,
  376).
- Serving: a helper without The Gift and Magic Theory, such as a child
  apprentice before his training, serves instead (Apprentices p. 34): the
  lab counts the Servant Virtue for that season, read with his Intelligence
  (Covenants p. 116). He gains the same Exposure.
"""

from __future__ import annotations

import math
import random
from dataclasses import replace

from .. import catalog
from ..models import (
    Character,
    Laboratory,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
    new_instance_id,
)
from . import dice, lab
from .lab_stats import lab_characteristic_total, lab_free_virtues
from .lab_work import LabWork

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Setting Up a Laboratory, p. "
    "250"
)
REFINE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Refinement, p. 287"
)
TAKE_OVER_SOURCE = (
    "Covenants, Chapter Nine: Laboratories, Taking Over a Laboratory, p. 118"
)
ASSIST_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Help in the Laboratory, p. "
    "264"
)

BUILD = "set_up_lab"
#: Setting up a laboratory where there is none yet: planned on the
#: character sheet, it makes the laboratory (its first season).
NEW = "new_lab"
REFINE = "refine_lab"
TAKE_OVER = "take_over_lab"
ASSIST = "assist_lab"
SERVANT = "labvf_servant"
SERVANT_SOURCE = (
    "Apprentices, Chapter Four: Pueritia, p. 34; Covenants, Chapter Nine: "
    "Laboratories, Servant, p. 116"
)
MOVE = "move_lab"
ACTIVITIES: tuple[str, ...] = (BUILD, REFINE, TAKE_OVER, MOVE)
#: Seasons that roll the Highly Organized / Hidden Defect die (moving: only
#: by spell).
ROLLED: tuple[str, ...] = (REFINE, TAKE_OVER, MOVE)
#: Moving by mundane means: pack (a season), then reassemble (two).
MOVE_SEASONS = 3
DISORGANIZED = "labvf_disorganized"
MOVE_SOURCE = "Covenants, Chapter Nine: Laboratories, Moving a Laboratory, p. 119"

BASIC = "labvf_basic"
HIGHLY_ORGANIZED = "labvf_highly_organized"
HIDDEN_DEFECT = "labvf_hidden_defect"
SPOTLESS = "labvf_spotless"
#: A Refinement season's Tidy roll (or another fitting Personality Trait)
#: against 9 gains Spotless (DE p. 288).
TIDY_TRAITS = ("Tidy", "Neat", "Orderly", "Fastidious")
SPOTLESS_AT = 9
PREDECESSOR = "labvf_predecessor"
ORGANIZED_AT = 12
DEFECT_FOUND_AT = 15


def magic_theory(character: Character) -> int:
    score, bonus = lab.ability_score(character, "Magic Theory")
    return score + bonus


def has_vf(lab_: Laboratory, vf_id: str) -> bool:
    return any(vf.vf_id == vf_id for vf in lab_.virtues_flaws)


def add_vf(lab_: Laboratory, vf_id: str) -> None:
    """Give the lab the Virtue or Flaw: again if the book lets a lab have
    it more than once (Hidden Defect, DE p. 294), else only if it hasn't."""
    entry = catalog.load_lab_virtue_flaw_catalog_by_id().get(vf_id)
    if not has_vf(lab_, vf_id) or (entry is not None and entry.repeatable):
        lab_.virtues_flaws.append(VirtueFlawInstance(vf_id, id=new_instance_id()))


def remove_vf(lab_: Laboratory, vf_id: str) -> None:
    """Take one of the Virtue or Flaw away (one Hidden Defect found is one
    corrected)."""
    for i, vf in enumerate(lab_.virtues_flaws):
        if vf.vf_id == vf_id:
            del lab_.virtues_flaws[i]
            return


def new_lab_name(magus: Character, plan: SeasonPlan) -> str:
    """The new laboratory's name: the plan's, else the magus's own."""
    return plan.title.strip() or f"{magus.name}'s laboratory"


def new_lab_problems(saga: Saga, magus: Character, plan: SeasonPlan) -> list[str]:
    """Why `magus` can't set up a new laboratory this season."""
    found: list[str] = []
    theory = magic_theory(magus)
    if theory < 3:
        found.append(f"Setting up a laboratory needs Magic Theory 3 ({theory}).")
    if saga.covenant(magus.covenant_id) is None:
        found.append(
            f"{magus.name} has no covenant to set the laboratory up in "
            "(Covenant, on the character sheet)."
        )
    return found


def vacant(saga: Saga, lab_: Laboratory) -> bool:
    """Whether `lab_` has no owner in the saga, so a magus may take it over."""
    return saga.character(lab_.owner_id) is None


def can_take_over(saga: Saga, magus: Character) -> list[Laboratory]:
    """The laboratories `magus` could take over from their sheet: those with
    no owner, their covenant's first."""
    return sorted(
        (lab_ for lab_ in saga.laboratories if vacant(saga, lab_)),
        key=lambda lab_: (lab_.covenant_id != magus.covenant_id, lab_.name.lower()),
    )


def refinement(saga: Saga, lab_: Laboratory) -> int:
    return lab_characteristic_total(
        lab_, catalog.load_lab_virtue_flaw_catalog_by_id(), "refinement", saga
    )[3]


def work(
    saga: Saga, magus: Character, plan: SeasonPlan, lab_: Laboratory
) -> tuple[list[str], LabWork | None]:
    """The problems with a season of work on the laboratory, or what it
    does."""

    theory = magic_theory(magus)
    empty = lab.LabTotal(total=0, lines=[])
    if plan.activity == BUILD:
        if theory < 3:
            return [f"Setting up a laboratory needs Magic Theory 3 ({theory})."], None
        # The first season leaves it Basic; the second finishes it.
        second = has_vf(lab_, BASIC)
        return [], LabWork(None, empty, 0, finished=True, second_season=second)
    current = refinement(saga, lab_)
    if plan.activity == MOVE:
        if not plan.title.strip():
            return ["Say where the laboratory is moving to."], None
        result = LabWork(None, empty, 0, finished=True, refinement=current)
        if not plan.by_spell:
            done = lab_.move_seasons + 1
            result.finished = done >= MOVE_SEASONS
            result.notes.append(
                ("Packing the laboratory" if done == 1 else "Reassembling it")
                + f" (season {done} of {MOVE_SEASONS})."
            )
        return [], result
    if plan.activity == REFINE:
        raised = theory >= current + 1 + 3
        result = LabWork(None, empty, 0, finished=True, refinement=current + raised)
        if not raised:
            result.notes.append(
                f"No higher Refinement: {current + 1} needs Magic Theory "
                f"{current + 4} ({theory})."
            )
        if current > 0:
            result.notes.append(
                f"Refining needs familiarity: as a rule of thumb, {current} "
                f"year{'s' if current != 1 else ''} worked in this laboratory "
                "(DE p. 287)."
            )
        return [], result
    # Taking over.
    new = min(current, theory - 3)
    result = LabWork(
        None, empty, 0, finished=True, refinement=new, old_refinement=current
    )
    over = -(
        lab_free_virtues(lab_, catalog.load_lab_virtue_flaw_catalog_by_id())
        - (current - new)
    )
    if new < current and over > 0:
        result.notes.append(
            f"At Refinement {new} the laboratory has {over:g} point"
            f"{'s' if over != 1 else ''} of Virtues more than its Size and "
            "Refinement hold: Virtues are lost until it fits (Covenants p. 118)."
        )
    return [], result


def roll(
    work_: LabWork, magus: Character, plan: SeasonPlan, rng: random.Random, saga: Saga
) -> list[str]:
    """The season's stress die + Intelligence + Magic Theory (and for a
    take-over, the Perception + Magic Theory roll against 3 x the old
    Refinement). A die typed on the plan is used for the first roll."""
    if plan.activity == MOVE:
        if not plan.by_spell:
            return []
        return _move_by_spell(work_, magus, plan, rng, saga)
    base = magus.characteristics.intelligence + magic_theory(magus)
    if plan.die is not None:
        value, botched = plan.die, plan.die == 0
    else:
        die = dice.stress_die(rng, 1, saga=saga)
        value, botched = die.value, die.botched
    notes: list[str] = []
    if botched:
        work_.gains_vf.append(HIDDEN_DEFECT)
        notes.append("Botch: the laboratory gains a Hidden Defect.")
    else:
        total = base + value
        if total >= ORGANIZED_AT:
            work_.gains_vf.append(HIGHLY_ORGANIZED)
        if total >= DEFECT_FOUND_AT:
            work_.loses_vf.append(HIDDEN_DEFECT)
        notes.append(
            f"Intelligence + Magic Theory {base} + die {value} = {total}"
            + (": Highly Organized" if total >= ORGANIZED_AT else "")
            + ("; any Hidden Defect is found" if total >= DEFECT_FOUND_AT else "")
            + "."
        )
    if plan.activity == REFINE and not has_vf_id(work_, SPOTLESS):
        notes += _tidy_roll(work_, magus, rng, saga)
    if plan.activity == TAKE_OVER and work_.old_refinement > 0:
        against = 3 * work_.old_refinement
        check = dice.stress_die(rng, 1, saga=saga)
        per = magus.characteristics.perception + magic_theory(magus)
        if check.botched:
            work_.gains_vf += [PREDECESSOR, HIDDEN_DEFECT]
            notes.append(
                "The storyguide's roll botched: Predecessor and a Hidden Defect."
            )
        elif per + check.value < against:
            work_.gains_vf.append(PREDECESSOR)
            notes.append(
                f"Perception + Magic Theory {per} + {check.value} < {against}: "
                "the Predecessor's arrangements remain."
            )
    return notes


def has_vf_id(work_: LabWork, vf_id: str) -> bool:
    return vf_id in work_.gains_vf


def tidy_trait(magus: Character) -> tuple[str, int] | None:
    """The magus's best Personality Trait for keeping a laboratory clean
    (Tidy or the like), if any."""
    found = [
        (t.name, t.score)
        for t in magus.personality_traits
        if any(word.casefold() in t.name.casefold() for word in TIDY_TRAITS)
    ]
    return max(found, key=lambda f: f[1]) if found else None


def _tidy_roll(
    work_: LabWork, magus: Character, rng: random.Random, saga: Saga
) -> list[str]:
    """A Refinement season's optional Tidy roll against 9 for Spotless (DE
    p. 288): made when the magus has such a Personality Trait."""
    trait = tidy_trait(magus)
    if trait is None:
        return []
    name, score = trait
    die = dice.stress_die(rng, 1, saga=saga)
    total = score + die.value
    if die.botched or total < SPOTLESS_AT:
        return [f"{name} {score} + die {die.value} = {total}: not Spotless (needs 9)."]
    work_.gains_vf.append(SPOTLESS)
    return [f"{name} {score} + die {die.value} = {total}: the laboratory is Spotless."]


def _move_by_spell(
    work_: LabWork, magus: Character, plan: SeasonPlan, rng: random.Random, saga: Saga
):
    """Moving by spell: Perception + Finesse + stress die against 9 + 3 x
    Refinement (+3 if Highly Organized, -3 if Disorganized, + the room's
    difference typed as the plan's Other modifier). Failure: Disorganized, or
    Highly Organized lost; a botch: a Hidden Defect instead."""
    finesse = next((a.level for a in magus.abilities if a.name == "Finesse"), 0)
    base = magus.characteristics.perception + finesse
    ease = 9 + 3 * work_.refinement + plan.other_modifier
    if plan.die is not None:
        value, botched = plan.die, plan.die == 0
    else:
        die = dice.stress_die(rng, 1, saga=saga)
        value, botched = die.value, die.botched
    if botched:
        work_.gains_vf.append(HIDDEN_DEFECT)
        return ["Botch: the laboratory gains a Hidden Defect."]
    total = base + value
    if total >= ease:
        return [
            f"Perception + Finesse {base} + {value} = {total} against {ease}: moved."
        ]
    work_.loses_vf.append(HIGHLY_ORGANIZED)
    work_.gains_vf.append(DISORGANIZED)
    return [
        f"Perception + Finesse {base} + {value} = {total} against {ease}: it "
        "arrives Disorganized (and loses Highly Organized)."
    ]


def helpers(saga: Saga, magus: Character, plan: SeasonPlan) -> list[Character]:
    """Everyone planned to help `magus` this season: assistants and
    servants alike, all of them in the laboratory."""
    found = []
    for other in saga.season_plans:
        if (
            other.activity == ASSIST
            and other.teacher_id == magus.id
            and (other.season, other.year) == (plan.season, plan.year)
        ):
            helper = saga.character(other.character_id)
            if helper is not None:
                found.append(helper)
    return found


def assistants(saga: Saga, magus: Character, plan: SeasonPlan) -> list[Character]:
    """Those helping `magus` this season who add Intelligence + Magic
    Theory to his Lab Total."""
    return [c for c in helpers(saga, magus, plan) if can_assist(c)]


def servants(saga: Saga, magus: Character, plan: SeasonPlan) -> list[Character]:
    """Those helping `magus` this season as servants (`serves`)."""
    return [c for c in helpers(saga, magus, plan) if serves(c)]


def _gifted(character: Character) -> bool:
    return character.type == "magus" or any(
        vf.vf_id in catalog.GIFT_IDS for vf in character.virtues_flaws
    )


def can_assist(character: Character) -> bool:
    """Whether `character` could help in a laboratory: The Gift and Magic
    Theory."""
    return _gifted(character) and magic_theory(character) >= 1


def serves(character: Character) -> bool:
    """Whether `character` helps in a laboratory only as a servant: without
    The Gift and Magic Theory, as a child apprentice before his training
    (Apprentices p. 34)."""
    return not can_assist(character)


def servant_safety(servant: Character) -> int:
    """The Safety a servant adds: Intelligence / 2, rounded up, as the lab
    reads the Servant Virtue (effects.resolve_amount)."""
    return math.ceil(servant.characteristics.intelligence / 2)


def servant_instance(servant: Character) -> VirtueFlawInstance:
    """The lab's Servant Virtue for a season `servant` helps in it, read
    with their Intelligence: + Intelligence / 2 (rounded up) Safety, +1
    Aesthetics, +1 Mentem Specialization (Covenants p. 116)."""
    return VirtueFlawInstance(
        SERVANT,
        params={"intelligence": str(servant.characteristics.intelligence)},
        id=f"servant-{servant.id}",
    )


def with_servants(
    saga: Saga, magus: Character, plan: SeasonPlan, lab_: Laboratory
) -> Laboratory:
    """`lab_` as it is for the season of `plan`: with each servant helping
    `magus` as one more Servant Virtue. The laboratory itself is
    unchanged."""
    found = servants(saga, magus, plan)
    if not found:
        return lab_
    return replace(
        lab_,
        virtues_flaws=[*lab_.virtues_flaws, *(servant_instance(c) for c in found)],
    )


def assist_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    lead = saga.character(plan.teacher_id)
    if lead is None or lead is character:
        return ["Choose the magus to assist."]
    theirs = next(
        (
            p
            for p in saga.season_plans
            if p.character_id == lead.id
            and (p.season, p.year) == (plan.season, plan.year)
        ),
        None,
    )
    if theirs is None or not theirs.lab_id:
        return [f"{lead.name} has no lab work planned for {plan.season} {plan.year}."]
    return []
