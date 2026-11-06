"""Vis sources at their places: the sources a covenant holds name the
Place (and level) they are gathered at, and a place can hold sources no
covenant has claimed yet.

The Definitive Edition (p. 422): a vis source is a place where a certain
number of pawns can be taken each year, most often in a supernatural
aura, and vis gathered in an aura not of Magic may be tainted by its
realm (Faerie vis mostly safe, Divine vis risking the Church's anger,
Infernal vis corrupting). Finding one is a story's treasure (p. 520).

A held source is one of its covenant's possessions (models.Possession,
kind "vis_source") with `place_id` and `place_level`. A source not yet
held is kept on its place, in Neighbour.details["vis_sources"], each an
UnclaimedSource; claiming one makes it the claiming covenant's
possession and takes it off the place.

Pattern: the derived reverse index connections.py keeps: a place's list
is worked out from the sources that name it, never stored twice; places
in places (Composite) give a region its total."""

from __future__ import annotations

from typing import Any, TypedDict, cast

from . import storage
from .arts import ARTS
from .commands import SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import SEASONS, Covenant, Neighbour, Possession, Saga, details_list
from .neighbour_lists import KindList, list_ops
from .places import inside_of, level_name
from .rules.sites import aura_at, levels, place
from .sections import VIS_SITES_SECTION

#: An unclaimed source's list in its place's details.
UNCLAIMED = "vis_sources"


class UnclaimedSource(TypedDict, total=False):
    """A source on a place that no covenant holds: its name, Art, pawns a
    year, the season it is gathered, the level it is on (0 the surface),
    its physical form; and, in the form only, the covenant claiming it."""

    name: str
    art: str
    pawns: int
    season: str
    level: int
    physical_form: str
    claim: str


def _level(entry: UnclaimedSource) -> int:
    """Its level as a number (the form gives the choice as words)."""
    value = str(entry.get("level") or 0)
    return int(value) if value.isdigit() else 0


def unclaimed(found: Neighbour) -> list[UnclaimedSource]:
    return cast(list[UnclaimedSource], details_list(found, UNCLAIMED))


def held_at(saga: Saga, found: Neighbour) -> list[tuple[Covenant, Possession]]:
    """The sources covenants hold at `found`, each with its covenant."""
    return [
        (covenant, record)
        for covenant in saga.covenants
        for record in covenant.possessions
        if record.kind == "vis_source" and record.place_id == found.id
    ]


def taint(saga: Saga, place_id: str | None, level: int = 0) -> str:
    """ "Faerie vis" when the aura it is gathered in is not Magic's (DE
    p. 422); "" in a Magic aura or nowhere entered."""
    found = place(saga, place_id)
    if found is None:
        return ""
    _aura, realm = aura_at(found, level)
    return f"{realm} vis" if realm and realm != "Magic" else ""


def _level_text(found: Neighbour, level: int) -> str:
    return level_name(found, level) if level > 0 else ""


def vis_title(saga: Saga, found: Neighbour) -> str:
    count = len(held_at(saga, found)) + len(unclaimed(found))
    return f"Vis Sources ({count})"


def vis_grid(saga: Saga, found: Neighbour) -> Grid:
    """The sources gathered here: those held, by their covenant (chosen
    and changed on its Possessions), then those no covenant holds yet,
    which this list edits."""
    rows: list[list[str]] = []
    keys: list[int | None] = []
    for covenant, record in held_at(saga, found):
        rows.append(
            [
                record.name,
                record.art,
                str(record.pawns),
                record.season,
                covenant.name,
                ", ".join(
                    t
                    for t in (
                        _level_text(found, record.place_level),
                        taint(saga, found.id, record.place_level),
                    )
                    if t
                ),
            ]
        )
        keys.append(None)
    for index, entry in enumerate(unclaimed(found)):
        level = _level(entry)
        rows.append(
            [
                entry.get("name", ""),
                entry.get("art", ""),
                str(entry.get("pawns") or 0),
                entry.get("season", ""),
                "(unclaimed)",
                ", ".join(
                    t
                    for t in (_level_text(found, level), taint(saga, found.id, level))
                    if t
                ),
            ]
        )
        keys.append(index)
    return Grid(
        ["Source", "Art", "Pawns", "Season", "Held by", "Where, taint"],
        rows,
        keys,
        "No vis sources here: add one no covenant holds yet, or name this "
        "place on a covenant's vis source.",
        caps=[26, 10, 5, 7, 22, 0],
    )


def _fields(
    saga: Saga, found: Neighbour, entry: UnclaimedSource | None
) -> list[DialogField]:
    e = entry or {}
    shown = levels(found)
    return [
        DialogField("name", "Name", "text", e.get("name", ""), required=True),
        DialogField(
            "art",
            "Art",
            "select",
            e.get("art") or None,
            options=pairs(ARTS),
            required=True,
            allow_blank=True,
            placeholder="(choose an Art)",
        ),
        DialogField("pawns", "Pawns", "int", e.get("pawns") or 1),
        DialogField(
            "season",
            "Season gathered",
            "select",
            e.get("season") or None,
            options=pairs(SEASONS),
            required=True,
            allow_blank=True,
            placeholder="(choose a Season)",
        ),
        *(
            [
                DialogField(
                    "level",
                    "Level",
                    "select",
                    str(int(e.get("level") or 0)),
                    options=[
                        ("The surface", "0"),
                        *(
                            (escape(level_name(found, i)), str(i))
                            for i in range(1, len(shown) + 1)
                        ),
                    ],
                )
            ]
            if shown
            else []
        ),
        DialogField(
            "physical_form", "Physical form", "text", e.get("physical_form", "")
        ),
        DialogField(
            "claim",
            "Claimed by",
            "select",
            None,
            options=[(escape(c.name), c.id) for c in saga.covenants],
            allow_blank=True,
            placeholder="(no one yet)",
            hint="Choose a covenant to give it the source: it moves to that "
            "covenant's Vis Sources, gathered here.",
        ),
    ]


def _problem(values: dict[str, Any]) -> str | None:
    if (values.get("pawns") or 0) < 1:
        return "Pawns must be at least 1."
    return None


def claim(
    saga: Saga, found: Neighbour, entry: UnclaimedSource, covenant: Covenant
) -> Possession:
    """Make `entry` a source `covenant` holds, gathered at `found`, and
    take it off the place."""
    record = Possession(
        id=storage.generate_unique_id(
            entry.get("name") or "vis_source", [r.id for r in covenant.possessions]
        ),
        kind="vis_source",
        name=entry.get("name", ""),
        art=entry.get("art", ""),
        pawns=int(entry.get("pawns") or 1),
        season=entry.get("season", ""),
        physical_form=entry.get("physical_form", ""),
        location=found.name,
        place_id=found.id,
        place_level=_level(entry),
    )
    covenant.possessions.append(record)
    unclaimed(found).remove(entry)
    return record


def _claim_chosen(saga: Saga, found: Neighbour) -> None:
    """After Add or Edit: each source given a covenant goes to it."""
    for entry in list(unclaimed(found)):
        chosen = saga.covenant(entry.pop("claim", None) or None)
        if chosen is not None:
            claim(saga, found, entry, chosen)


def vis_ops(saga: Saga, found: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        found,
        UNCLAIMED,
        "Vis Source",
        _fields,
        lambda e: e.get("name", ""),
        validate=_problem,
        after=lambda: _claim_chosen(saga, found),
    )


VIS_SITES = KindList(VIS_SITES_SECTION, vis_title, vis_grid, vis_ops)


# -- what a place, and what is inside it, gives --


def _pawns_by_art(saga: Saga, found: Neighbour) -> dict[str, int]:
    totals: dict[str, int] = {}
    for _covenant, record in held_at(saga, found):
        totals[record.art] = totals.get(record.art, 0) + record.pawns
    for entry in unclaimed(found):
        art = entry.get("art", "")
        totals[art] = totals.get(art, 0) + int(entry.get("pawns") or 0)
    return totals


def vis_text(saga: Saga, found: Neighbour) -> str:
    """ "9 pawns a year (Herbam 5, Vim 4); 3 more in the places inside":
    what the place's sources give, and those of the places inside it,
    however deep; "" when none."""
    here = _pawns_by_art(saga, found)
    inside = sum(
        sum(_pawns_by_art(saga, p).values())
        for p in saga.neighbours
        if p.kind == "place" and found in inside_of(saga, p)
    )
    parts = []
    if here:
        arts = ", ".join(f"{a} {n}" for a, n in sorted(here.items()))
        parts.append(f"{sum(here.values())} pawns a year ({arts})")
    if inside:
        parts.append(f"{inside} {'more ' if here else ''}in the places inside")
    return "; ".join(parts)


def where_text(saga: Saga, record: Possession) -> str:
    """A held source's place, its level and taint: "The Whispering Well,
    Faerie vis"; "" when it names no place."""
    found = place(saga, record.place_id)
    if found is None:
        return ""
    words = [found.name]
    if record.place_level > 0:
        words.append(level_name(found, record.place_level))
    taint_words = taint(saga, found.id, record.place_level)
    if taint_words:
        words.append(taint_words)
    return ", ".join(words)
