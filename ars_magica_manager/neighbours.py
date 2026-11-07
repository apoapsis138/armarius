"""The saga's neighbours: the lords, towns, churches, universities,
factions and threats of the region, its places, and its customs and
lore, each a Neighbour record of one kind.

Pattern: Strategy, as a registry (KINDS), the way rules/activities.py
registers the seasonal activities and tribunal_packages the Tribunals'
customs. The core knows only the common record (name, summary, ruler,
liege, realm, attitude, favours, links); a kind names its book, the
group it is listed under in the Region, and what it adds. Adding a kind
is one entry here."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import (
    churches,
    customs,
    factions,
    lords,
    manors,
    marriages,
    place_events,
    places,
    references,
    sourcebooks,
    storage,
    story_chapters,
    threats,
    tombs,
    town_charter,
    town_court,
    town_guilds,
    towns,
    universities,
    viewing,
    world,
)
from .form_spec import DialogField
from .models import Covenant, Neighbour, Saga
from .neighbour_lists import KindTab
from .references import Fact
from .rules import sites
from .sections import (
    REGION_CHURCH_SECTION,
    REGION_CUSTOMS_SECTION,
    REGION_FACTIONS_SECTION,
    REGION_LORDS_SECTION,
    REGION_PLACES_SECTION,
    REGION_THREATS_SECTION,
    REGION_UNIVERSITIES_SECTION,
)


@dataclass(frozen=True)
class Group:
    """A list of the Region: its title and its section."""

    key: str
    title: str
    section_id: str


#: The Region's lists of neighbours, in the order shown.
GROUPS: tuple[Group, ...] = (
    Group("lords", "Lords and Towns", REGION_LORDS_SECTION),
    Group("church", "The Church", REGION_CHURCH_SECTION),
    Group("universities", "Universities", REGION_UNIVERSITIES_SECTION),
    Group("factions", "Factions", REGION_FACTIONS_SECTION),
    Group("threats", "Threats", REGION_THREATS_SECTION),
    Group("places", "Places", REGION_PLACES_SECTION),
    Group("customs", "Customs and Lore", REGION_CUSTOMS_SECTION),
)


@dataclass(frozen=True)
class NeighbourKind:
    """One kind of neighbour."""

    key: str
    name: str
    #: What it is, in a few words, for New Neighbour's list.
    blurb: str
    #: The group (GROUPS) it is listed under.
    group: str
    #: The sourcebook it needs in play; "" for the core rules.
    book: str = ""
    #: The fields it adds to New and Edit, kept in the neighbour's
    #: details under their keys, and what is wrong with what was entered.
    fields: Callable[[Saga, Neighbour | None], list[DialogField]] | None = None
    problem: Callable[[dict[str, Any]], str | None] | None = None
    #: What is worked out for one of its neighbours, shown on its tab.
    facts: Callable[[Saga, Neighbour], list[Fact]] | None = None
    #: The tab it adds to its neighbours' sheets (what it works out, then
    #: its lists), and any more tabs of lists after it.
    tab: KindTab | None = None
    more: tuple[KindTab, ...] = ()
    #: Whether it holds an attitude toward the troupe (a place doesn't),
    #: and which common fields it has no use for.
    attitude: bool = True
    hides: frozenset[str] = frozenset()


#: Every kind, in the order New Neighbour offers them.
KINDS: dict[str, NeighbourKind] = {}


def register(kind: NeighbourKind) -> None:
    KINDS[kind.key] = kind


for _kind in (
    NeighbourKind(
        "lord",
        "Lord",
        "a noble and his household",
        "lords",
        "LoM",
        lords.fields,
        lords.problem,
        lords.facts,
        lords.TAB,
        # A lord's Marriages tab comes after his Manors; his Roll Tables
        # sit beside his Diary, after Standing.
        (manors.LORD_TAB, marriages.TAB, lords.TABLES_TAB, lords.DIARY_TAB),
    ),
    NeighbourKind(
        "town",
        "Town",
        "a town, its council and its market",
        "lords",
        "C&G",
        towns.fields,
        towns.problem,
        towns.facts,
        towns.TAB,
        (town_charter.CHARTER_TAB, town_guilds.GUILDS_TAB, town_court.COURT_TAB),
    ),
    NeighbourKind(
        "church",
        "Church",
        "a bishop, an abbey, a parish",
        "church",
        "TC",
        churches.fields,
        churches.problem,
        churches.facts,
        churches.TAB,
    ),
    NeighbourKind(
        "university",
        "University",
        "a studium and its masters",
        "universities",
        "A&A",
        universities.fields,
        universities.problem,
        universities.facts,
        universities.TAB,
    ),
    NeighbourKind(
        "faction",
        "Faction",
        "a gild, a hedge coven, a family",
        "factions",
        "",
        factions.fields,
        factions.problem,
        factions.facts,
        factions.TAB,
        (place_events.TABLES_TAB, factions.DIARY_TAB),
    ),
    NeighbourKind(
        "threat",
        "Threat",
        "a story that grows if left alone",
        "threats",
        "",
        threats.fields,
        threats.problem,
        lambda saga, threat: (
            threats.facts(saga, threat) + story_chapters.threat_facts(saga, threat)
        ),
        threats.TAB,
        (place_events.TABLES_TAB, story_chapters.THREAT_DIARY_TAB),
    ),
    NeighbourKind(
        sites.PLACE,
        "Place",
        "a forest, a ruin, a regio",
        "places",
        "",
        # A place may be marked a tomb (Lands of the Nile): its Tomb tab
        # comes after Regio.
        lambda saga, place: (
            place_events.place_fields(saga, place) + tombs.mark_fields(saga, place)
        ),
        place_events.place_problem,
        place_events.place_facts,
        place_events.REGIO_TAB,
        (tombs.TOMB_TAB, place_events.TABLES_TAB, place_events.DIARY_TAB),
        attitude=False,
        hides=frozenset({"detail", "ruler", "answers_to"}),
    ),
    NeighbourKind(
        "custom",
        "Custom",
        "a land's way of life, its law or its lore",
        "customs",
        "",
        customs.fields,
        None,
        customs.facts,
        customs.TAB,
        attitude=False,
        hides=frozenset({"detail", "answers_to"}),
    ),
):
    register(_kind)

#: What a neighbour of a kind no longer known is taken for.
FALLBACK = "faction"


def kind_of(neighbour: Neighbour) -> NeighbourKind:
    return KINDS.get(neighbour.kind) or KINDS[FALLBACK]


def icon_concept(neighbour: Neighbour) -> str:
    """The artwork concept a neighbour's picture shows: its kind's, or a
    ruin for a ruined covenant's site."""
    return "ruin" if places.is_ruin(neighbour) else kind_of(neighbour).key


def group(key: str) -> Group:
    return next(g for g in GROUPS if g.key == key)


def in_play(saga: Saga, kind: NeighbourKind) -> bool:
    """Whether `kind`'s book is in play."""
    return not kind.book or sourcebooks.in_play(kind.book, sourcebooks.saga_books(saga))


def kinds_of(group_key: str) -> list[NeighbourKind]:
    """The kinds listed under the group `group_key`."""
    return [k for k in KINDS.values() if k.group == group_key]


def members(saga: Saga, group_key: str) -> list[Neighbour]:
    """The neighbours listed under the group `group_key`, as entered: those
    whoever is looking may read (viewing.shown)."""
    return [n for n in viewing.shown(saga.neighbours) if kind_of(n).group == group_key]


def groups_shown(saga: Saga) -> list[Group]:
    """The groups the Region shows: each that has a neighbour, or a kind
    whose book is in play."""
    return [
        g
        for g in GROUPS
        if members(saga, g.key) or any(in_play(saga, k) for k in kinds_of(g.key))
    ]


def add(saga: Saga, kind: str, name: str) -> Neighbour:
    """A new neighbour of `kind` called `name`, added to the saga."""
    neighbour = Neighbour(
        id=storage.generate_unique_id(name, [n.id for n in saga.neighbours]),
        name=name,
        kind=kind,
        # A faction's members are kept on its roster from the start, so
        # a faction answering to it later is its liege's, never taken for
        # a member by the move of older saves (models.saga).
        details={"roster": []} if kind == "faction" else {},
    )
    saga.neighbours.append(neighbour)
    return neighbour


def vassals(saga: Saga, neighbour: Neighbour) -> list[Neighbour]:
    """The neighbours that answer to `neighbour`."""
    return [n for n in saga.neighbours if n.answers_to == neighbour.id]


def deletion_consequences(saga: Saga, neighbour: Neighbour) -> list[str]:
    """What deleting `neighbour` does besides removing it."""
    found = []
    below = [n.name for n in vassals(saga, neighbour)]
    if below:
        found.append(f"{', '.join(below)} will answer to no one.")
    held = places.here(saga, neighbour)
    if held:
        found.append(f"{', '.join(held)} will be placed nowhere.")
    if found:
        found[-1] = found[-1].removesuffix(".") + "; nothing else changes."
    return found


def delete(saga: Saga, neighbour: Neighbour) -> None:
    for other in vassals(saga, neighbour):
        other.answers_to = None
    references.forget_ruler(saga, neighbour)
    saga.neighbours.remove(neighbour)
    places.sync(saga)


# -- attitude, as the Region shows it --


def home(saga: Saga) -> Covenant | None:
    """The player covenant the Region's attitudes are shown toward: the
    first the troupe plays."""
    played = world.player_covenants(saga)
    return played[0] if played else None


def score(saga: Saga, record: Neighbour | Covenant) -> int | None:
    """`record`'s attitude toward the home covenant; None with no player
    covenant (or when `record` is it)."""
    covenant = home(saga)
    if covenant is None or record is covenant:
        return None
    if isinstance(record, Neighbour) and not kind_of(record).attitude:
        return None
    return world.attitude_score(world.attitude_toward(record, covenant.id))
