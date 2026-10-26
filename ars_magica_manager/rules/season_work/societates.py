"""Houses of Hermes: Societates' seasons: House work, Tribunal or Redcap
duties, and searching for a lacuna (Intelligence + Area Lore against 9;
rules.lacunae, HoH:S p. 57): the first success records the city's
lacunae found, and later seasons there are Area Lore practice."""

from __future__ import annotations

import random

from ...models import Character, Saga, SeasonPlan
from .. import activity_groups as groups
from .. import dice, lacunae
from .base import (
    CH,
    MAGI,
    SimpleActivity,
    SupplementWork,
    experience_only,
    register,
    source,
    subject_ability,
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
    lore, score = lacunae.search_lore(character, subject_ability(plan))
    area = lacunae.area_of(lore) if lore else ""
    known = (
        f" He knows {lacunae.known_count(score)} small lacunae there "
        f"({lacunae.PER_LORE} per level of {lore})."
        if area
        else ""
    )
    if area and lacunae.found_record(character, area) is not None:
        # Seasons after the first search are Area Lore practice (p. 57).
        result.notes.append(
            f"{area}'s obvious lacunae are already found: the season is Area "
            "Lore practice, and the Area Lore's specialty may become lacunae." + known
        )
        return
    if plan.die is not None:
        die = plan.die
    elif rng is not None:
        die = dice.stress_die(rng, 1, saga=saga).value
    else:
        result.notes.append("The search is rolled when the season is played.")
        return
    total = lacunae.search_base(character, score) + die
    if total < lacunae.SEARCH_EASE:
        result.notes.append(
            f"Int + Area Lore + die = {total} against {lacunae.SEARCH_EASE}: "
            "none found."
        )
        return
    result.notes.append(
        f"Int + Area Lore + die = {total} against {lacunae.SEARCH_EASE}: the "
        "obvious lacunae are found." + known
    )
    if area:
        result.progress.append(
            (lacunae.KIND, lacunae.record_name(area), lacunae.SEARCH_EASE, total)
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
