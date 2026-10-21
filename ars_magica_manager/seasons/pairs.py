"""Paired plans: a season that takes another person's season too. Being
taught plans the teacher's Teach, being trained the master's season
working at the Ability, Teach with a student the student's Be taught, and
lab work naming an assistant that assistant's Assist. Clearing one side
clears the other.

What each activity's counterpart is, is a hook per activity (Strategy, as
a table): `PARTNERS`. A plan made this way remembers whose plan made it
(`SeasonPlan.partner_id`), so it can be replaced or cleared with it.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from ..models import Character, Saga, SeasonPlan, XpAllocation
from ..rules import activities as rules
from ..rules import laboratory_seasons as ls
from .plans import plan_for, plan_summary, set_plan

#: The Ability a teacher's season of teaching gives Exposure in.
TEACHING = "ability:Teaching"


@dataclass(frozen=True)
class Pair:
    """The other person's plan a plan takes, and whether the plan can't
    be carried out without it (a teacher must Teach; a master may be
    doing something else)."""

    plan: SeasonPlan
    required: bool = True


Partner = Callable[[Saga, Character, SeasonPlan], list[Pair]]


def _subject(plan: SeasonPlan) -> str:
    return next((a.subject for a in plan.allocations if a.subject), "")


def _other(saga: Saga, character: Character, other_id: str | None):
    other = saga.character(other_id)
    return None if other is None or other is character else other


def _teacher(saga: Saga, character: Character, plan: SeasonPlan) -> list[Pair]:
    teacher = _other(saga, character, plan.teacher_id)
    if teacher is None:
        return []
    teach = SeasonPlan(
        teacher.id,
        plan.year,
        plan.season,
        rules.TEACH,
        allocations=[XpAllocation(TEACHING, 0)],
        partner_id=character.id,
    )
    return [Pair(teach)]


def _master(saga: Saga, character: Character, plan: SeasonPlan) -> list[Pair]:
    """A master trains at their own work in the Ability, gaining Exposure
    in it."""
    master = _other(saga, character, plan.teacher_id)
    subject = _subject(plan)
    if master is None or not subject:
        return []
    work = SeasonPlan(
        master.id,
        plan.year,
        plan.season,
        rules.EXPOSURE,
        allocations=[XpAllocation(subject, 0)],
        details=f"Training {character.name}.",
        partner_id=character.id,
    )
    return [Pair(work, required=False)]


def _student(saga: Saga, character: Character, plan: SeasonPlan) -> list[Pair]:
    student = _other(saga, character, plan.subject_id)
    if student is None or not plan.student_subject:
        return []
    taught = SeasonPlan(
        student.id,
        plan.year,
        plan.season,
        rules.TAUGHT,
        allocations=[XpAllocation(plan.student_subject, 0)],
        teacher_id=character.id,
        partner_id=character.id,
    )
    return [Pair(taught)]


def _assistants(saga: Saga, character: Character, plan: SeasonPlan) -> list[Pair]:
    found = []
    for helper_id in plan.assistant_ids:
        helper = _other(saga, character, helper_id)
        if helper is not None:
            assist = SeasonPlan(
                helper.id,
                plan.year,
                plan.season,
                ls.ASSIST,
                teacher_id=character.id,
                partner_id=character.id,
            )
            found.append(Pair(assist))
    return found


#: The counterpart of each paired activity (Strategy); lab work's are its
#: assistants (`partners`).
PARTNERS: dict[str, Partner] = {
    rules.TAUGHT: _teacher,
    rules.TRAINED: _master,
    rules.TEACH: _student,
}


def partners(saga: Saga, character: Character, plan: SeasonPlan) -> list[Pair]:
    """The other people's plans `plan` takes."""
    if plan.lab_id:
        return _assistants(saga, character, plan)
    partner = PARTNERS.get(plan.activity)
    return [] if partner is None else partner(saga, character, plan)


def _serves(there: SeasonPlan, wanted: SeasonPlan) -> bool:
    """Whether the plan already there does what the pair needs: a teacher
    already teaching, a student already taught by this teacher, a helper
    already assisting this magus."""
    if there.activity != wanted.activity:
        return False
    if wanted.activity == rules.TEACH:
        return True
    return there.teacher_id == wanted.teacher_id


def _replaceable(there: SeasonPlan, character: Character) -> bool:
    return there.partner_id == character.id


def _needed(
    saga: Saga, character: Character, plan: SeasonPlan
) -> tuple[list[SeasonPlan], str | None]:
    """The partner plans to make for `plan`, or why it can't be paired: a
    required partner whose season is planned for something else."""
    made: list[SeasonPlan] = []
    for pair in partners(saga, character, plan):
        other = saga.character(pair.plan.character_id)
        if other is None:
            continue
        there = plan_for(saga, other, plan.season, plan.year)
        if there is not None and there is not plan and _serves(there, pair.plan):
            continue
        if there is None or _replaceable(there, character):
            made.append(pair.plan)
        elif pair.required:
            return [], (
                f"{other.name} already has {plan_summary(saga, other, there)} "
                f"planned for {plan.season} {plan.year}: change or clear that "
                "plan first."
            )
    return made, None


def to_make(saga: Saga, character: Character, plan: SeasonPlan) -> list[SeasonPlan]:
    """The other people's plans saving `plan` would make."""
    return _needed(saga, character, plan)[0]


def pair_problem(saga: Saga, character: Character, plan: SeasonPlan) -> str | None:
    """Why `plan` can't be saved with the other people's plans it takes."""
    return _needed(saga, character, plan)[1]


@contextmanager
def in_place(saga: Saga, character: Character, plan: SeasonPlan) -> Iterator[None]:
    """The saga as it would be with `plan`'s partner plans made, for
    checking or previewing `plan` before it is saved."""
    made, _why = _needed(saga, character, plan)
    taken = {(p.character_id, p.season, p.year) for p in saga.season_plans}
    added = [p for p in made if (p.character_id, p.season, p.year) not in taken]
    saga.season_plans.extend(added)
    try:
        yield
    finally:
        for each in added:
            if each in saga.season_plans:
                saga.season_plans.remove(each)


def _taught_by(saga: Saga, teach: SeasonPlan) -> list[SeasonPlan]:
    return [
        p
        for p in saga.season_plans
        if p.activity == rules.TAUGHT
        and p.teacher_id == teach.character_id
        and (p.season, p.year) == (teach.season, teach.year)
    ]


def _drop_made_by(saga: Saga, character_id: str, season: str, year: int) -> None:
    """Clear the plans `character_id`'s plan made in that season, but keep
    a Teach another student still needs."""
    for p in list(saga.season_plans):
        if p.partner_id != character_id or (p.season, p.year) != (season, year):
            continue
        if p.activity == rules.TEACH and any(
            t.character_id != character_id for t in _taught_by(saga, p)
        ):
            continue
        saga.season_plans.remove(p)


def make_pairs(saga: Saga, character: Character, plan: SeasonPlan) -> list[SeasonPlan]:
    """Plan the other people's seasons `plan` (already saved) takes,
    replacing those an earlier plan of the character's made that season.
    Returns the plans made."""
    _drop_made_by(saga, character.id, plan.season, plan.year)
    made, why = _needed(saga, character, plan)
    if why is not None:
        return []
    for each in made:
        set_plan(saga, each)
    return made


def drop_pairs(saga: Saga, plan: SeasonPlan) -> None:
    """Clear the plans `plan` made (it is changed or moved)."""
    _drop_made_by(saga, plan.character_id, plan.season, plan.year)


def linked(saga: Saga, plan: SeasonPlan) -> list[SeasonPlan]:
    """The other people's plans cleared with `plan`: those it made, the
    one that made it (an assistant's Assist only leaves the lab work), a
    teacher's students, and lab work's assistants. A Teach another student
    still needs stays."""
    found: list[SeasonPlan] = []
    for p in saga.season_plans:
        if p is plan or (p.season, p.year) != (plan.season, plan.year):
            continue
        if p.character_id == plan.character_id:
            continue
        made_it = plan.partner_id == p.character_id and plan.activity != ls.ASSIST
        made = p.partner_id == plan.character_id
        students = plan.activity == rules.TEACH and p in _taught_by(saga, plan)
        helpers = (
            bool(plan.lab_id)
            and p.activity == ls.ASSIST
            and p.teacher_id == plan.character_id
        )
        if made_it or made or students or helpers:
            found.append(p)
    return [
        p
        for p in found
        if not (
            p.activity == rules.TEACH
            and any(
                t is not plan and t not in found and t.character_id != p.character_id
                for t in _taught_by(saga, p)
            )
        )
    ]


def clear_with(saga: Saga, plans: list[SeasonPlan]) -> None:
    """Clear `plans`; an assistant's Assist leaves the lab work but takes
    the assistant off it."""
    for plan in plans:
        if plan.activity == ls.ASSIST:
            for lead in saga.season_plans:
                if (
                    lead.character_id == plan.teacher_id
                    and (lead.season, lead.year) == (plan.season, plan.year)
                    and plan.character_id in lead.assistant_ids
                ):
                    lead.assistant_ids.remove(plan.character_id)
        if plan in saga.season_plans:
            saga.season_plans.remove(plan)


def names(saga: Saga, plans: list[SeasonPlan]) -> str:
    """ "Tiberius and Bertram": whose plans these are."""
    people = list(
        dict.fromkeys(
            c.name for p in plans if (c := saga.character(p.character_id)) is not None
        )
    )
    if len(people) < 2:
        return "".join(people)
    return ", ".join(people[:-1]) + " and " + people[-1]
