"""The Church's season of personal devotion: a season of prayer and
meditation at a saint's shrine earns 5 Devotion Points toward him, and
only exposure experience, in Church Lore, Dominion Lore or the like (The
Church p. 14). The saint is the plan's name; the points go to his
Devotion (rules.devotion), begun if new."""

from __future__ import annotations

import random

from ...models import Character, Saga, SeasonPlan
from .. import activity_groups as groups
from .. import devotion as dv
from .base import (
    ANYONE,
    CH,
    SimpleActivity,
    SupplementWork,
    needs_name,
    register,
    source,
)

DEVOTION_SEASON = 5
CHURCH = source("The Church " + CH.format("The_Church"), "TC")


def _devotion(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    held = dv.devotion(character, plan.title)
    name = held.name if held is not None else plan.title.strip()
    result.progress.append((dv.DEVOTION, name, 0, DEVOTION_SEASON))
    result.notes.append(f"+{DEVOTION_SEASON} Devotion Points toward {name}.")


register(
    SimpleActivity(
        "personal_devotion",
        "Personal devotion",
        "A season of prayer at a saint's shrine: 5 Devotion Points toward "
        "him (name the saint). Exposure 2 in Church or Dominion Lore.",
        CHURCH,
        "FAITH-1",
        who=ANYONE,
        group=groups.FAITH,
    ),
    _devotion,
    needs_name,
)
