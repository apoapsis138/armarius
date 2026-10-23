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
  helpers) and gives the assistant Exposure in Magic Theory.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .. import catalog
from ..models import (
    Character,
    Laboratory,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
    new_instance_id,
)
from . import lab
from .lab_stats import lab_characteristic_total

if TYPE_CHECKING:
    from .lab_seasons import LabWork

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Setting Up a "
    "Laboratory (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Eight:_Laboratory#Setting_Up_a_Laboratory)"
)
REFINE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Refinement "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eight:"
    "_Laboratory#Refinement)"
)
TAKE_OVER_SOURCE = (
    "Covenants, Chapter Nine: Laboratories, Taking Over a Laboratory "
    "(https://www.redcap.org/page/Covenants_Chapter_Nine:_Laboratories"
    "#Taking_Over_a_Laboratory)"
)
ASSIST_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Help in the "
    "Laboratory (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Eight:_Laboratory#Help_in_the_Laboratory)"
)

BUILD = "set_up_lab"
#: Setting up a laboratory where there is none yet: planned on the
#: character sheet, it makes the laboratory (its first season).
NEW = "new_lab"
REFINE = "refine_lab"
TAKE_OVER = "take_over_lab"
ASSIST = "assist_lab"
MOVE = "move_lab"
ACTIVITIES: tuple[str, ...] = (BUILD, REFINE, TAKE_OVER, MOVE)
#: Seasons that roll the Highly Organized / Hidden Defect die (moving: only
#: by spell).
ROLLED: tuple[str, ...] = (REFINE, TAKE_OVER, MOVE)
#: Moving by mundane means: pack (a season), then reassemble (two).
MOVE_SEASONS = 3
DISORGANIZED = "labvf_disorganized"
MOVE_SOURCE = (
    "Covenants, Chapter Nine: Laboratories, Moving a Laboratory "
    "(https://www.redcap.org/page/Covenants_Chapter_Nine:_Laboratories"
    "#Moving_a_Laboratory)"
)

BASIC = "labvf_basic"
HIGHLY_ORGANIZED = "labvf_highly_organized"
HIDDEN_DEFECT = "labvf_hidden_defect"
PREDECESSOR = "labvf_predecessor"
ORGANIZED_AT = 12
DEFECT_FOUND_AT = 15


def magic_theory(character: Character) -> int:
    score, bonus = lab.ability_score(character, "Magic Theory")
    return score + bonus


def has_vf(lab_: Laboratory, vf_id: str) -> bool:
    return any(vf.vf_id == vf_id for vf in lab_.virtues_flaws)


def add_vf(lab_: Laboratory, vf_id: str) -> None:
    if not has_vf(lab_, vf_id):
        lab_.virtues_flaws.append(VirtueFlawInstance(vf_id, id=new_instance_id()))


def remove_vf(lab_: Laboratory, vf_id: str) -> None:
    lab_.virtues_flaws = [vf for vf in lab_.virtues_flaws if vf.vf_id != vf_id]


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


def refinement(lab_: Laboratory) -> int:
    return lab_characteristic_total(
        lab_, catalog.load_lab_virtue_flaw_catalog_by_id(), "refinement"
    )[3]


def work(
    saga: Saga, magus: Character, plan: SeasonPlan, lab_: Laboratory
) -> tuple[list[str], LabWork | None]:
    """The problems with a season of work on the laboratory, or what it
    does."""
    from .lab_seasons import LabWork

    theory = magic_theory(magus)
    empty = lab.LabTotal(total=0, lines=[])
    if plan.activity == BUILD:
        if theory < 3:
            return [f"Setting up a laboratory needs Magic Theory 3 ({theory})."], None
        # The first season leaves it Basic; the second finishes it.
        second = has_vf(lab_, BASIC)
        return [], LabWork(None, empty, 0, finished=True, second_season=second)
    current = refinement(lab_)
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
        return [], result
    # Taking over.
    new = min(current, theory - 3)
    return [], LabWork(
        None, empty, 0, finished=True, refinement=new, old_refinement=current
    )


def roll(
    work_: LabWork, magus: Character, plan: SeasonPlan, rng: random.Random, saga: Saga
) -> list[str]:
    """The season's stress die + Intelligence + Magic Theory (and for a
    take-over, the Perception + Magic Theory roll against 3 x the old
    Refinement). A die typed on the plan is used for the first roll."""
    from . import dice

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


def _move_by_spell(
    work_: LabWork, magus: Character, plan: SeasonPlan, rng: random.Random, saga: Saga
):
    """Moving by spell: Perception + Finesse + stress die against 9 + 3 x
    Refinement (+3 if Highly Organized, -3 if Disorganized, + the room's
    difference typed as the plan's Other modifier). Failure: Disorganized, or
    Highly Organized lost; a botch: a Hidden Defect instead."""
    from . import dice

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


def assistants(saga: Saga, magus: Character, plan: SeasonPlan) -> list[Character]:
    """Those planned to assist `magus` this season."""
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


def _gifted(character: Character) -> bool:
    return character.type == "magus" or any(
        vf.vf_id in catalog.GIFT_IDS for vf in character.virtues_flaws
    )


def can_assist(character: Character) -> bool:
    """Whether `character` could help in a laboratory: The Gift and Magic
    Theory."""
    return _gifted(character) and magic_theory(character) >= 1


def assist_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    lead = saga.character(plan.teacher_id)
    if lead is None or lead is character:
        return ["Choose the magus to assist."]
    if not _gifted(character):
        return [f"{character.name} needs The Gift to help in a laboratory."]
    if magic_theory(character) < 1:
        return [f"{character.name} needs Magic Theory to help in a laboratory."]
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
