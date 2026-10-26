"""Houses of Hermes: Societates' seasons: House work, Tribunal or Redcap
duties, and searching for a lacuna (Intelligence + Area Lore against 9)."""

from __future__ import annotations

import random

from ...models import Character, Saga, SeasonPlan
from .. import activity_groups as groups
from .. import dice
from .base import (
    CH,
    MAGI,
    SimpleActivity,
    SupplementWork,
    experience_only,
    register,
    source,
)

SOCIETATES = source(
    "Houses of Hermes: Societates " + CH.format("Houses_of_Hermes:_Societates"),
    "HoH:S",
)


def _search_lacuna(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    if plan.die is not None:
        die = plan.die
    elif rng is not None:
        die = dice.stress_die(rng, 1, saga=saga).value
    else:
        result.notes.append("The search is rolled when the season is played.")
        return
    lore = max(
        (a.level for a in character.abilities if a.name.startswith("Area Lore")),
        default=0,
    )
    total = character.characteristics.intelligence + lore + die
    result.notes.append(
        f"Int + Area Lore + die = {total} against 9: "
        + ("the obvious lacunae are found." if total >= 9 else "none found.")
    )


register(
    SimpleActivity(
        "house_work",
        "House seasonal work",
        "House-specific work (Fenicil rituals, Criamon Path stations, Bjornaer "
        "heartbeast...): the storyguide's Source Quality.",
        SOCIETATES,
        "918",
        None,
        "as the House's rule gives (Exposure 2 if nothing else)",
        MAGI,
        group=groups.ORDER,
    ),
    experience_only,
)
register(
    SimpleActivity(
        "tribunal_duties",
        "Tribunal or Redcap duties",
        "A season of Order business or Redcap rounds: Exposure 2.",
        SOCIETATES,
        "918",
        group=groups.ORDER,
    ),
    experience_only,
)
register(
    SimpleActivity(
        "search_lacuna",
        "Search for a lacuna",
        "Intelligence + Area Lore against 9; later seasons are practice.",
        SOCIETATES,
        "923",
        4,
        group=groups.STUDY,
    ),
    _search_lacuna,
)
