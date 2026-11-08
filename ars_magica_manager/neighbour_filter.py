"""What the Region's lists of neighbours are narrowed to: a Tribunal's
lands, a region (a place that sits inside no other, such as the Black
Forest) and a kind.

Pattern: Specification, as lab_texts.Filter is: one value says whether a
neighbour matches, whichever front-end's controls built it. The filter
is kept for each saga while the app runs, here in the core, so the
lists, their titles and the rows Edit and Delete act on always agree."""

from __future__ import annotations

from dataclasses import dataclass

from . import neighbours, places, viewing
from .models import Neighbour, Saga, Tribunal
from .rules import sites


@dataclass(frozen=True)
class Filter:
    """A region's place id, a kind's key and a Tribunal's id ("": any)."""

    region: str = ""
    kind: str = ""
    tribunal: str = ""

    @property
    def active(self) -> bool:
        return self != Filter()


#: Each saga's filter, by its id, while the app runs.
_CURRENT: dict[str, Filter] = {}


def regions(saga: Saga) -> list[Neighbour]:
    """The places a neighbour can be found in, at any depth: each place
    that sits inside no other and holds something."""
    held = {
        outer.id
        for record in viewing.shown(saga.neighbours)
        for outer in places.inside_of(saga, record)
    }
    return [p for p in sites.all_places(saga) if not p.place_id and p.id in held]


def tribunals(saga: Saga) -> list[Tribunal]:
    """The Tribunals some place names as whose lands it is."""
    named = {p.details.get(places.LANDS) for p in sites.all_places(saga)}
    return [t for t in saga.tribunals if t.id in named]


def kinds(saga: Saga) -> list[neighbours.NeighbourKind]:
    """The kinds the saga has neighbours of, in New Neighbour's order."""
    present = {neighbours.kind_of(n).key for n in viewing.shown(saga.neighbours)}
    return [k for k in neighbours.KINDS.values() if k.key in present]


def current(saga: Saga) -> Filter:
    """The saga's filter; a region since deleted no longer narrows it."""
    wanted = _CURRENT.get(saga.id, Filter())
    if wanted.region and sites.place(saga, wanted.region) is None:
        wanted = Filter(kind=wanted.kind, tribunal=wanted.tribunal)
    if wanted.tribunal and saga.tribunal(wanted.tribunal) is None:
        wanted = Filter(region=wanted.region, kind=wanted.kind)
    return wanted


def choose(saga: Saga, wanted: Filter) -> None:
    if wanted.active:
        _CURRENT[saga.id] = wanted
    else:
        _CURRENT.pop(saga.id, None)


def describe(saga: Saga, wanted: Filter) -> str:
    """ "Lord, in The Black Forest" ("" when nothing is set)."""
    parts = []
    kind = neighbours.KINDS.get(wanted.kind)
    if kind is not None:
        parts.append(kind.name)
    region = sites.place(saga, wanted.region) if wanted.region else None
    if region is not None:
        parts.append(f"in {region.name}")
    tribunal = saga.tribunal(wanted.tribunal) if wanted.tribunal else None
    if tribunal is not None:
        parts.append(f"in the lands of {tribunal.name}")
    return ", ".join(parts)


def matches(saga: Saga, neighbour: Neighbour, wanted: Filter) -> bool:
    """Whether `neighbour` is of the kind, in the Tribunal's lands, and in
    (or is) the region."""
    if wanted.kind and neighbours.kind_of(neighbour).key != wanted.kind:
        return False
    if wanted.tribunal:
        lands = places.lands_of(saga, neighbour)
        if lands is None or lands.id != wanted.tribunal:
            return False
    if not wanted.region or neighbour.id == wanted.region:
        return True
    return any(p.id == wanted.region for p in places.inside_of(saga, neighbour))


def shown(saga: Saga, group_key: str) -> list[Neighbour]:
    """The group's neighbours the saga's filter lets through, as entered."""
    wanted = current(saga)
    members = neighbours.members(saga, group_key)
    if not wanted.active:
        return members
    return [n for n in members if matches(saga, n, wanted)]
