"""The Church's seasons: Good Works, Care of Souls, following a preacher,
pilgrimage (a progress record toward its Target Level) and penance."""

from __future__ import annotations

import random

from ...models import Character, Saga, SeasonPlan
from .. import activity_groups as groups
from .. import clergy
from .base import (
    ANYONE,
    CH,
    COMPANIONS,
    SimpleActivity,
    SupplementWork,
    experience_only,
    needs_name,
    register,
    source,
)

CHURCH = source("The Church " + CH.format("The_Church"), "TC")
#: A pilgrimage season's progress toward its Target Level.
PILGRIMAGE_SEASON = 3


def _pilgrimage(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    name = plan.title.strip()
    target = plan.book_level if plan.book_level in (18, 30) else 18
    gained = PILGRIMAGE_SEASON + max(0, plan.other_modifier)
    result.progress.append(("pilgrimage", name, target, gained))
    result.notes.append(
        f"+{PILGRIMAGE_SEASON} for the season"
        + (
            f", +{plan.other_modifier} for elements overcome"
            if plan.other_modifier
            else ""
        )
        + f" toward Target Level {target}."
    )


def _care_of_souls(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    name = plan.title.strip()
    theme = name or "the sermons' theme"
    result.notes.append(
        f"For the following year, willing congregants get +1 to activities "
        f"fitting {theme}."
    )


register(
    SimpleActivity(
        "good_works",
        "Good Works",
        "Source Quality 2, and 1 Faith Point.",
        CHURCH,
        "921",
        # Any Christian, a magus too; a cleric's may be a working season
        # (The Church p. 27).
        who=ANYONE,
        faith=1,
        group=groups.FAITH,
    ),
    experience_only,
)
register(
    SimpleActivity(
        "care_of_souls",
        "Care of Souls",
        "A priest's season: Source Quality 2; a congregation bonus next year.",
        CHURCH,
        "921",
        who=COMPANIONS,
        group=groups.FAITH,
    ),
    _care_of_souls,
)
register(
    SimpleActivity(
        "follow_preacher",
        "Follow a preacher",
        "Source Quality = the sermons' Aesthetic Quality.",
        CHURCH,
        "921",
        None,
        "the sermons' Aesthetic Quality",
        # Any character's free season (The Church p. 130).
        ANYONE,
        group=groups.FAITH,
    ),
    experience_only,
)
register(
    SimpleActivity(
        "pilgrimage",
        "Pilgrimage",
        "A season on pilgrimage toward its Target Level (18 minor, 30 "
        "major). Exposure 2.",
        CHURCH,
        "921",
        # Any pilgrim, magi and grogs included (The Church p. 16).
        who=ANYONE,
        group=groups.ADVENTURE,
    ),
    _pilgrimage,
    needs_name,
)
register(
    SimpleActivity(
        "penance",
        "Visitation, petition or penance",
        "Exposure 2; the penance served.",
        CHURCH,
        "921",
        # Any penitent (The Church pp. 12, 16).
        who=ANYONE,
        group=groups.FAITH,
    ),
    experience_only,
)


# -- Ordination (The Church pp. 33-35) --


def ordination_grade(character: Character, plan: SeasonPlan) -> clergy.Grade | None:
    """The grade the season's examination is for: the one the plan names,
    or his next."""
    named = clergy.BY_NAME.get(plan.title.strip())
    return named if named is not None else clergy.next_grade(character.church)


def _ordination(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    grade = ordination_grade(character, plan)
    if grade is None:
        return
    terms = clergy.exam_terms(character, grade)
    sum_words = (
        f"Intelligence {terms.intelligence:+d} + {grade.ability} {terms.score} "
        f"+ stress die against {grade.ease}"
    )
    if rng is None and plan.die is None:
        result.notes.append(f"Examination for {grade.name}: {sum_words}.")
        return
    if plan.die is not None:
        record = clergy.examine_with(
            character, grade, plan.die, season=plan.season, year=plan.year
        )
    else:
        assert rng is not None
        record = clergy.examine(
            saga, character, grade, rng, season=plan.season, year=plan.year
        )
    record.examiner = plan.examiner
    record.elsewhere = plan.ordained_elsewhere
    result.ordination = record
    die = "a botch" if record.botched else str(record.die)
    result.notes.append(
        f"Examination for {grade.name}: {sum_words}; the die shows {die}, total "
        f"{record.total}: {clergy.result_label(record.result).lower()}."
    )


def _ordination_check(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    career = character.church
    if career.barred:
        return [
            "His last examination botched: a petition must let him sit again "
            "(Petition the Church, EF 9; The Church p. 34)."
        ]
    grade = ordination_grade(character, plan)
    if grade is None:
        return ["He holds every grade an examination gives: a bishop is elected."]
    if clergy.rank(grade.name) <= clergy.rank(career.grade):
        return [f"He is already ordained {career.grade}."]
    return []


register(
    SimpleActivity(
        "ordination",
        "Ordination",
        "A season's examination for the next grade of holy orders; Source "
        "Quality 2 in Church Lore or Civil and Canon Law.",
        CHURCH,
        "217",
        # Any man may be ordained; a magus too (The Church p. 33).
        who=ANYONE,
        group=groups.FAITH,
    ),
    _ordination,
    _ordination_check,
)
