"""The Church's seasons: Good Works, Care of Souls, following a preacher,
pilgrimage (a progress record toward its Target Level) and penance."""

from __future__ import annotations

import random

from ...models import Character, Saga, SeasonPlan
from .. import activity_groups as groups
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
