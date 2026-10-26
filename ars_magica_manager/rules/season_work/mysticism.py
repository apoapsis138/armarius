"""The Church's seasons on a contemplative's Spiritual Path (The Church p.
22): each is a Quest Component toward the Revelation the plan names. A
season serving the poor or the Church +1; of personal devotion +1, with
one Devotion Point toward the saint the plan's details name (his patron
saint if none) and only exposure, in Dominion Lore; preaching the Gospel
+3, once on a path; preaching to heretics, pagans or infidels at the risk
of martyrdom +9, a story. The other components are kept with More's
Spiritual Path (rules.mysticism)."""

from __future__ import annotations

import random

from ...models import Character, Saga, SeasonPlan
from .. import activity_groups as groups
from .. import devotion as dv
from .. import mysticism as my
from .base import ANYONE, CH, SimpleActivity, SupplementWork, register, source

CHURCH = source("The Church " + CH.format("The_Church") + " (mysticism)", "TC")
STORY = "FAITH-2"
#: Personal devotion on a path: one Devotion Point (p. 22), not p. 14's 5.
DEVOTION_POINT = 1
PREACHING = "Spiritual path: preaching"


def _path(character: Character, plan: SeasonPlan):
    return my.find_path(character, plan.title.strip())


def _outcome(key: str):
    def outcome(
        saga: Saga,
        character: Character,
        plan: SeasonPlan,
        rng: random.Random | None,
        result: SupplementWork,
    ) -> None:
        record = _path(character, plan)
        if record is None:
            return
        component = my.COMPONENTS[key]
        result.progress.append((my.SPIRITUAL_PATH, record.name, 0, component.value))
        reached = record.points + component.value
        claim = (
            " (reached: claim it with More's Spiritual Path)."
            if reached >= record.target
            else "."
        )
        result.notes.append(
            f"Quest Component +{component.value} {my.counted_line(record.name)} "
            f"{reached} of {record.target}{claim}"
        )
        if key == "devotion":
            saint = plan.details.strip() or dv.patron(character)
            if saint:
                held = dv.devotion(character, saint)
                name = held.name if held is not None else saint
                result.progress.append((dv.DEVOTION, name, 0, DEVOTION_POINT))
                result.notes.append(f"+{DEVOTION_POINT} Devotion Point toward {name}.")

    return outcome


def _check(key: str):
    def check(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
        if my.path(character) != my.CONTEMPLATIVE:
            return ["Only a contemplative mystic walks a Spiritual Path (TC p. 22)."]
        record = _path(character, plan)
        if record is None:
            return ["Name the Spiritual Path (the Revelation sought), begun with More."]
        problem = my.component_problem(character, record, key)
        if (
            problem is None
            and my.COMPONENTS[key].once
            and preached(character, record.name)
        ):
            problem = "Preaching the Gospel counts once on a path (TC p. 22)."
        return [problem] if problem else []

    return check


def preached(character: Character, record_name: str) -> bool:
    """Whether a season of preaching has counted on this path already: its
    Diary entry says so."""
    marker = my.counted_line(record_name)
    return any(
        entry.activity == PREACHING and marker in entry.details
        for entry in character.diary
    )


_SEASONS = (
    (
        "service",
        "path_service",
        "Spiritual path: service",
        "A season serving the poor or the Church, tending the sick: +1 toward "
        "the Revelation named.",
        "",
    ),
    (
        "devotion",
        "path_devotion",
        "Spiritual path: devotion",
        "A season of personal devotion: +1 toward the Revelation named, and a "
        "Devotion Point toward the saint in its details (his patron if none). "
        "Only exposure, in Dominion Lore.",
        "Dominion Lore only.",
    ),
    (
        "preaching",
        "path_preaching",
        PREACHING,
        "A season preaching the Gospel: +3 toward the Revelation named, once on "
        "a path.",
        "",
    ),
    (
        "infidels",
        "path_mission",
        "Spiritual path: mission",
        "A season preaching to heretics, pagans or infidels at the risk of "
        "martyrdom, a story: +9 toward the Revelation named.",
        "",
    ),
)

for _key, _activity, _label, _summary, _hint in _SEASONS:
    register(
        SimpleActivity(
            _activity,
            _label,
            _summary,
            CHURCH,
            STORY,
            hint=_hint,
            who=ANYONE,
            group=groups.FAITH,
        ),
        _outcome(_key),
        _check(_key),
    )
