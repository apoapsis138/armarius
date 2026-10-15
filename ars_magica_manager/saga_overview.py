"""What the saga, covenant and season pages show, independent of how they
are drawn: a saga's covenants, a covenant's people and laboratories as
cards, and the seasons each character spent or plans as a timeline.

Plain values rather than markup, so a front-end gives each its own type.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from . import catalog, places, tribunals
from . import character_sheet as cs
from . import laboratories as labs
from .models import (
    COMPANION_TYPES,
    SEASONS,
    Character,
    Covenant,
    Laboratory,
    Saga,
    character_age,
)
from .rules.activities import ACTIVITIES

#: The groups a covenant's people are shown in, in order, by type.
PEOPLE = (
    ("Magi", ("magus",)),
    ("Companions", COMPANION_TYPES),
    ("Grogs", ("grog",)),
)

#: What a new person made from each group is (its first type), and what
#: making one is called.
NEW_PERSON: dict[str, tuple[str, str]] = {
    title: (types[0], f"New {types[0].title()}") for title, types in PEOPLE
}


@dataclass(frozen=True)
class SagaCard:
    id: str
    name: str
    subtitle: str
    covenants: int
    characters: int


def saga_card(saga: Saga) -> SagaCard:
    storyguide = f"Storyguide {saga.storyguide}  ·  " if saga.storyguide else ""
    return SagaCard(
        saga.id,
        saga.name,
        f"{storyguide}{saga.current_season} {saga.current_year}",
        len(saga.covenants),
        len(saga.characters),
    )


@dataclass(frozen=True)
class CovenantCard:
    """A covenant at a glance; `id` None stands for the characters who
    belong to no covenant."""

    id: str | None
    name: str
    subtitle: str
    facts: tuple[cs.Fact, ...]


def covenant_subtitle(saga: Saga, covenant: Covenant) -> str:
    parts = [f"{covenant.covenant_season} covenant"]
    tribunal = tribunals.title_of(saga, covenant)
    if tribunal:
        parts.insert(0, tribunal)
    if covenant.year_founded is not None:
        parts.append(f"founded {covenant.year_founded}")
    return "  ·  ".join(parts)


def covenant_cards(saga: Saga) -> list[CovenantCard]:
    """Each covenant with its aura and how many people and laboratories
    it has."""
    cards = []
    for covenant in saga.covenants:
        people = members(saga, covenant.id)
        labs = [lab for lab in saga.laboratories if lab.covenant_id == covenant.id]
        facts = [
            cs.Fact("Aura", f"{covenant.aura_realm} {covenant.aura}"),
            *(
                cs.Fact(group, str(sum(c.type in types for c in people)))
                for group, types in PEOPLE
            ),
            cs.Fact("Laboratories", str(len(labs))),
        ]
        cards.append(
            CovenantCard(
                covenant.id,
                covenant.name,
                covenant_subtitle(saga, covenant),
                tuple(facts),
            )
        )
    return cards


def members(saga: Saga, covenant_id: str | None) -> list[Character]:
    return [c for c in saga.characters if c.covenant_id == covenant_id]


@dataclass(frozen=True)
class PersonCard:
    id: str
    name: str
    house: str | None  # a House's catalog id, for its symbol
    subtitle: str
    detail: str


def person_card(saga: Saga, character: Character) -> PersonCard:
    house = cs.house_name(character)
    kind = f"Magus of House {house}" if house else character.type.title()
    age = character_age(character.background.year_born, saga.current_year)
    detail = [f"Age {age}"] if age is not None else []
    if character.type == "magus":
        lab = saga.laboratory(character.assigned_lab_id)
        if lab:
            detail.append(lab.name)
    elif character.background.title_profession:
        detail.append(character.background.title_profession)
    return PersonCard(
        character.id,
        character.name or "(unnamed)",
        character.hermetic.house if character.type == "magus" else None,
        kind,
        "  ·  ".join(detail),
    )


def people_groups(
    saga: Saga, covenant_id: str | None, *, every: bool = False
) -> list[tuple[str, list[Character]]]:
    """A covenant's people by group (Magi, Companions, Grogs): each group
    that has anyone, or with `every` each group, so it can be added to."""
    people = members(saga, covenant_id)
    groups = [
        (title, [c for c in people if c.type in types]) for title, types in PEOPLE
    ]
    return [(title, group) for title, group in groups if every or group]


@dataclass(frozen=True)
class LabCard:
    id: str
    name: str
    subtitle: str
    facts: tuple[cs.Fact, ...]


def lab_cards(saga: Saga, covenant_id: str | None) -> list[LabCard]:
    return [
        _lab_card(saga, lab)
        for lab in saga.laboratories
        if lab.covenant_id == covenant_id
    ]


def _lab_card(saga: Saga, lab: Laboratory) -> LabCard:
    owner = saga.character(lab.owner_id)
    covenant = saga.covenant(lab.covenant_id)
    own = places.lab_aura(saga, lab)
    aura = labs.lab_aura_total(
        lab, own[0] if own is not None else covenant.aura if covenant else 0
    )
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()

    def total(name: str) -> str:
        return f"{labs.lab_characteristic_total(lab, by_id, name)[3]:+d}"

    return LabCard(
        lab.id,
        lab.name,
        f"The sanctum of {owner.name}" if owner else "No one's sanctum",
        (
            cs.Fact("Aura", str(aura)),
            cs.Fact("Size", total("size")),
            cs.Fact("Quality", total("general_quality")),
            cs.Fact("Safety", total("safety")),
        ),
    )


# The season timeline


#: The kinds of season a timeline colours apart, in the order its legend
#: lists them.
LAB, STUDY, WRITING, WORK, ADVENTURE, REST, OTHER = (
    "Laboratory",
    "Study",
    "Teaching & Writing",
    "Work",
    "Adventure & Travel",
    "Recovery",
    "Other",
)
KINDS = (LAB, STUDY, WRITING, WORK, ADVENTURE, REST, OTHER)

_KIND_OF: dict[str, str] = {
    **dict.fromkeys(
        (
            "practice",
            "read",
            "taught",
            "trained",
            "vis_study",
            "study_significato",
            "study_realia",
            "read_commentary",
            "library_research",
            "attend_university",
            "vernacular_literature",
            "research_formula",
            "study_artwork",
            "integrate_insight",
            "undergo_initiation",
            "search_lacuna",
        ),
        STUDY,
    ),
    **dict.fromkeys(
        (
            "teach",
            "write_summa",
            "write_tractatus",
            "copy_book",
            "translate_book",
            "rewrite_lab_texts",
            "copy_lab_texts",
            "edit_florilegium",
            "write_casting_tablet",
            "teach_abbreviations",
            "teach_hermetic_virtue",
            "open_arts",
            "search_apprentice",
            "record_lectures",
            "inspeximus",
            "bind_catalog",
            "mystagogue",
            "train_group",
        ),
        WRITING,
    ),
    **dict.fromkeys(("adventure", "travel", "pilgrimage", "tournament"), ADVENTURE),
    **dict.fromkeys(("aging", "convalesce", "longevity_subject"), REST),
    "other": OTHER,
}


def activity_kind(key: str) -> str:
    """The kind of season an activity is (LAB, STUDY...): laboratory work
    by the registry's own flag, the rest by the table above, anything
    else (a working season, a sourcebook's trade) Work."""
    activity = ACTIVITIES.get(key)
    if activity is None:
        return OTHER
    if activity.lab:
        return LAB
    return _KIND_OF.get(key, WORK)


_KEY_BY_LABEL = {a.label: key for key, a in ACTIVITIES.items()}


@dataclass(frozen=True)
class Season:
    """One character's season on the timeline: what they did (from their
    Diary) or will do (a locked-in plan)."""

    kind: str
    label: str
    detail: str
    planned: bool


def _when(season: str, year: int) -> int:
    return year * len(SEASONS) + SEASONS.index(season)


def _at(index: int) -> tuple[str, int]:
    return SEASONS[index % len(SEASONS)], index // len(SEASONS)


def character_seasons(saga: Saga, character: Character) -> dict[int, Season]:
    """A character's seasons by when (year x 4 + season): each Diary
    entry, then each locked-in plan for a season not yet written up."""
    seasons: dict[int, Season] = {}
    for entry in character.diary:
        if entry.season not in SEASONS:
            continue
        key = _KEY_BY_LABEL.get(entry.activity, "")
        label = entry.activity or entry.name or "Diary entry"
        kind = activity_kind(key) if key else OTHER
        if not key and "twilight" in entry.name.lower():
            kind = REST
        name = entry.name if entry.name != label else ""
        detail = "\n".join(part for part in (name, entry.details) if part)
        seasons[_when(entry.season, entry.year)] = Season(kind, label, detail, False)
    for plan in saga.season_plans:
        if plan.character_id != character.id or plan.season not in SEASONS:
            continue
        when = _when(plan.season, plan.year)
        activity = ACTIVITIES.get(plan.activity)
        seasons.setdefault(
            when,
            Season(
                activity_kind(plan.activity),
                activity.label if activity else plan.activity,
                plan.details,
                True,
            ),
        )
    return seasons


@dataclass(frozen=True)
class Timeline:
    """Seasons across, people down: `columns` are (season, year) from the
    first season anyone recorded (at most `BACK` before now) to `AHEAD`
    after now; `rows` each person's name and their seasons by column."""

    columns: list[tuple[str, int]]
    current: int  # the column of the saga's current season
    rows: list[tuple[str, str, dict[int, Season]]]  # (id, name, seasons)


#: How far back and ahead of the current season a timeline reaches.
BACK, AHEAD = 39, 4


def timeline(saga: Saga, characters: Sequence[Character]) -> Timeline:
    now = _when(saga.current_season, saga.current_year)
    every = {c.id: character_seasons(saga, c) for c in characters}
    known = [when for seasons in every.values() for when in seasons]
    first = max(min([*known, now - 3]), now - BACK)
    last = max([*known, now + AHEAD]) if known else now + AHEAD
    last = min(last, now + AHEAD + 8)
    columns = [_at(i) for i in range(first, last + 1)]
    rows = [
        (
            c.id,
            c.name or "(unnamed)",
            {
                when - first: season
                for when, season in every[c.id].items()
                if first <= when <= last
            },
        )
        for c in characters
    ]
    return Timeline(columns, now - first, rows)


def calendar(saga: Saga, character: Character) -> list[tuple[int, list[Season | None]]]:
    """One character's seasons as a calendar: a row per year, newest
    first, from their first recorded season (or this year) to the last
    planned, each with its four seasons."""
    return calendar_rows(saga, character_seasons(saga, character))


def lab_seasons(saga: Saga, lab: Laboratory) -> dict[int, Season]:
    """A laboratory's seasons by when: each entry of its Diary, then each
    locked-in plan made in it for a season not yet written up."""
    seasons: dict[int, Season] = {}
    for entry in lab.diary:
        if entry.season in SEASONS:
            label = entry.activity or entry.name or "Diary entry"
            name = entry.name if entry.name != label else ""
            detail = "\n".join(part for part in (name, entry.details) if part)
            seasons[_when(entry.season, entry.year)] = Season(LAB, label, detail, False)
    for plan in saga.season_plans:
        if plan.lab_id != lab.id or plan.season not in SEASONS:
            continue
        activity = ACTIVITIES.get(plan.activity)
        who = saga.character(plan.character_id)
        seasons.setdefault(
            _when(plan.season, plan.year),
            Season(
                activity_kind(plan.activity),
                activity.label if activity else plan.activity,
                who.name if who else "",
                True,
            ),
        )
    return seasons


def calendar_rows(
    saga: Saga, seasons: dict[int, Season]
) -> list[tuple[int, list[Season | None]]]:
    """Seasons by when as a calendar: a row per year, newest first, from
    the first (or this year) to the last, each with its four seasons."""
    now = _when(saga.current_season, saga.current_year)
    years = [when // len(SEASONS) for when in seasons] or [saga.current_year]
    first, last = min(*years, now // len(SEASONS)), max(*years, now // len(SEASONS))
    return [
        (
            year,
            [seasons.get(year * len(SEASONS) + i) for i in range(len(SEASONS))],
        )
        for year in range(last, first - 1, -1)
    ]
