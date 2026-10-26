"""The Normandy Tribunal's customs (The Lion and the Lily: The Normandy
Tribunal): under the Perthean Compact every vis source is held by a
covenant on one of five tenures, and after each meeting the covenants'
teams contest the Hermetic Tourney, whose ranks win prize pawns.

Kept in the package's data: "tenures", each {"source", "holder_id" (a
covenant, or None for the Tribunal), "tenure", "until", "notes"}, and
"tourney", each team's result {"year", "team", "points", "events"}
("points" its own tally, "events" {event key: placing}). A Tourney's
ranks and prize pawns are worked out from its total points. The Library
of the Tribunal keeps "leases" and "gifts" (see leases() and gifts())."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .. import tribunals
from ..commands import Command, Confirm, Form, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..markup import escape
from ..models import Book, Covenant, Saga, Tribunal
from ..rules import library
from ..rules.rounding import round_up
from ..sections import TENURE_SECTION, TOURNEY_SECTION
from . import PackageList, PackageTab, TribunalPackage, entries, register

KEY = "normandy"

#: The Perthean Compact's tenures, and what each means.
TENURES: dict[str, str] = {
    "seisin": "Within a day's return march: held while it qualifies",
    "legacy": "Granted by vote for 7 years; renewal needs a vote",
    "tropaeum": "The Tribunal's, leased for 7 years as a Tourney prize",
    "luctatio": "The Tribunal's, harvested by any magus who dares",
    "interim": "Reported, held by its finders until the next meeting",
}

#: The prize pawns each rank of the Tourney wins (21st keeps 6 and gives
#: 6 to the teams below it); a rank past 21st wins none.
PRIZE_PAWNS: dict[int, int] = {
    1: 31,
    2: 24,
    3: 18,
    4: 15,
    5: 13,
    6: 11,
    7: 17,
    8: 8,
    9: 7,
    10: 6,
    11: 6,
    12: 5,
    13: 0,
    14: 11,
    15: 3,
    16: 5,
    17: 4,
    18: 3,
    19: 5,
    20: 1,
    21: 6,
}

ENTERED = "entered"


#: The Tourney's six events (The Lion and the Lily p. 31): each placing's
#: points, and the point every team that enters gains besides (none in
#: the melee).
@dataclass(frozen=True)
class TourneyEvent:
    label: str
    placings: dict[str, int]
    entering: int = 1


TOURNEY_EVENTS: dict[str, TourneyEvent] = {
    "hastiludium": TourneyEvent(
        "The hastiludium", {"winner": 20, "finalist": 10, "semifinalist": 5}
    ),
    "certamen": TourneyEvent(
        "The certamen tournament", {"winner": 25, "finalist": 15, "semifinalist": 8}
    ),
    "dimicatio": TourneyEvent(
        "The dimicatio", {"winner": 23, "finalist": 12, "semifinalist": 6}
    ),
    "melee": TourneyEvent(
        "The melee",
        {"first": 6, "second to fourth": 2, "fifth": 1},
        entering=0,
    ),
    "host": TourneyEvent(
        "The hosting covenant's choice",
        {"first": 12, "second": 8, "third or fourth": 3},
    ),
    "joust": TourneyEvent(
        "The joust", {"first": 20, "second": 8, "third or fourth": 3}
    ),
}


def event_points(event: str, placing: str) -> int:
    """What a team's placing in one event earns: the placing's points and
    the point for entering ("" did not enter; ENTERED placed nowhere)."""
    found = TOURNEY_EVENTS.get(event)
    if found is None or not placing:
        return 0
    return found.placings.get(placing, 0) + found.entering


def total_points(result: dict[str, Any]) -> int:
    """A team's tally: its own points (its starting tally, the number of
    its covenant's members, and any the book's events don't give) and
    each event's."""
    events = result.get("events") or {}
    return int(result.get("points", 0)) + sum(
        event_points(event, placing) for event, placing in events.items()
    )


#: The named ranks, each a Hermetic Reputation of 2 for seven years.
SIEGES: dict[int, str] = {
    1: "Siege of Normandy",
    2: "Siege of Valor",
    7: "Siege of Notatus",
    13: "Siege of Shame",
    21: "Siege of Alms",
}


def tenures(tribunal: Tribunal) -> list[dict[str, Any]]:
    """The vis sources whose tenure is recorded, in the order entered."""
    return entries(tribunal, KEY, "tenures")


def tourney(tribunal: Tribunal) -> list[dict[str, Any]]:
    """Each team's result at each Tourney, in the order entered."""
    return entries(tribunal, KEY, "tourney")


def _holder(saga: Saga, holder_id: str | None) -> str:
    if not holder_id:
        return "the Tribunal"
    covenant = saga.covenant(holder_id)
    return covenant.name if covenant is not None else "(gone)"


# -- vis tenure --


def lapsed(saga: Saga, entry: dict[str, Any]) -> bool:
    """Whether the tenure's term has run out by this year."""
    until = entry.get("until")
    return until is not None and until <= saga.current_year


def tenure_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"Vis Tenure ({len(tenures(tribunal))})"


def tenure_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each source: who holds it, on what tenure, until when."""
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, entry in enumerate(tenures(tribunal)):
        until = entry.get("until")
        if lapsed(saga, entry):
            styles[(index, 3)] = "$text-warning"
        rows.append(
            [
                entry["source"],
                _holder(saga, entry.get("holder_id")),
                entry.get("tenure", "").capitalize(),
                str(until) if until is not None else "",
                entry.get("notes", ""),
            ]
        )
    return Grid(
        ["Source", "Held by", "Tenure", "Until", "Notes"],
        rows,
        list(range(len(rows))),
        "No vis tenure recorded: under the Perthean Compact each source is "
        "a seisin, legacy, tropaeum, luctatio or interim lease.",
        styles,
        caps=[24, 18, 9, 5, 0],
        stretch=4,
    )


def tenure_fields(
    saga: Saga, tribunal: Tribunal, entry: dict[str, Any] | None
) -> list[DialogField]:
    e = entry or {}
    return [
        DialogField(
            "source",
            "Vis source",
            "text",
            e.get("source", ""),
            required=True,
            placeholder="e.g. The Weeping Oak (3 Herbam)",
        ),
        DialogField(
            "holder_id",
            "Held by",
            "select",
            e.get("holder_id"),
            options=[
                (escape(c.name), c.id) for c in tribunals.covenants_of(saga, tribunal)
            ],
            allow_blank=True,
            placeholder="(the Tribunal)",
            hint="A covenant of the Tribunal; blank for a tropaeum or "
            "luctatio the Tribunal keeps.",
        ),
        DialogField(
            "tenure",
            "Tenure",
            "select",
            e.get("tenure", "seisin"),
            options=[(f"{k.capitalize()}: {v}", k) for k, v in TENURES.items()],
            required=True,
        ),
        DialogField(
            "until",
            "Until (year)",
            "optint",
            e.get("until"),
            hint="When a legacy, tropaeum or interim lease runs out.",
        ),
        DialogField("notes", "Notes", "text", e.get("notes", "")),
    ]


def tenure_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    def form(entry: dict[str, Any] | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = entry if entry is not None else {}
            target.update(values)
            target["holder_id"] = values.get("holder_id") or None
            if entry is None:
                tenures(tribunal).append(target)

        return Form(
            "Add a Vis Tenure" if entry is None else "Edit a Vis Tenure",
            lambda: tenure_fields(saga, tribunal, entry),
            apply,
            save_label="Add" if entry is None else "Save",
        )

    def remove(index: int) -> Command:
        entry = tenures(tribunal)[index]

        def apply() -> None:
            tenures(tribunal).remove(entry)

        return Confirm(f"Delete the tenure of {escape(entry['source'])}?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(tenures(tribunal)[index]),
        remove=remove,
        rows=lambda: [e["source"] for e in tenures(tribunal)],
    )


# -- the Tourney --


def ranked(tribunal: Tribunal) -> list[tuple[int, int]]:
    """(index, rank) of each result: the latest Tourney first, each by
    points, highest first. Teams level on points keep the order they
    were entered, as the book breaks ties by seniority."""
    results = tourney(tribunal)
    order = sorted(
        range(len(results)),
        key=lambda i: (-results[i].get("year", 0), -total_points(results[i]), i),
    )
    out: list[tuple[int, int]] = []
    rank, year = 0, None
    for index in order:
        if results[index].get("year") != year:
            rank, year = 0, results[index].get("year")
        rank += 1
        out.append((index, rank))
    return out


def prize(rank: int) -> str:
    """The prize pawns `rank` wins: "31", or "6, and 6 to give" for 21st."""
    pawns = PRIZE_PAWNS.get(rank, 0)
    return f"{pawns}, and 6 to give" if rank == 21 else str(pawns)


def tourney_title(_saga: Saga, tribunal: Tribunal) -> str:
    years = {r.get("year") for r in tourney(tribunal)}
    count = len(years)
    return f"The Tourney ({count} held)" if count else "The Tourney"


def tourney_grid(_saga: Saga, tribunal: Tribunal) -> Grid:
    """Each team at each Tourney, the latest first: its rank, points,
    prize pawns and any named rank."""
    results = tourney(tribunal)
    rows = []
    keys = []
    styles: dict[tuple[int, int], str] = {}
    for row, (index, rank) in enumerate(ranked(tribunal)):
        result = results[index]
        if rank in SIEGES:
            styles[(row, 5)] = "b"
        rows.append(
            [
                str(result.get("year", "")),
                str(rank),
                result["team"],
                str(total_points(result)),
                prize(rank),
                SIEGES.get(rank, ""),
            ]
        )
        keys.append(index)
    return Grid(
        ["Year", "Rank", "Team", "Points", "Pawns", "Named rank"],
        rows,
        keys,
        "No Tourney recorded: enter each team's points after a meeting, and "
        "its rank and prize pawns are worked out.",
        styles,
        caps=[5, 4, 24, 6, 16, 0],
    )


def tourney_fields(
    saga: Saga, tribunal: Tribunal, result: dict[str, Any] | None
) -> list[DialogField]:
    r = result or {}
    year = r.get("year", tribunal.next_year or saga.current_year)
    return [
        DialogField("year", "Year", "int", year, required=True),
        DialogField(
            "team",
            "Team",
            "text",
            r.get("team", ""),
            required=True,
            placeholder="e.g. Fengheld",
            hint="Its covenant, or a visiting team's name.",
        ),
        DialogField(
            "points",
            "Points",
            "int",
            r.get("points", 0),
            hint="Its starting tally (a point for each member of its covenant, "
            "one for a visiting team or a coenobium's member) and any points "
            "the events below don't give (The Lion and the Lily p. 31).",
        ),
    ] + [
        DialogField(
            f"event_{key}",
            event.label,
            "select",
            (r.get("events") or {}).get(key) or None,
            options=[
                (f"Entered, unplaced (+{event.entering})", ENTERED),
                *[
                    (f"{placing.capitalize()} (+{points + event.entering})", placing)
                    for placing, points in event.placings.items()
                ],
            ],
            allow_blank=True,
            placeholder="(did not enter)",
        )
        for key, event in TOURNEY_EVENTS.items()
    ]


def _tourney_live(values: dict[str, Any]) -> str:
    events = {
        key.removeprefix("event_"): value
        for key, value in values.items()
        if key.startswith("event_") and value
    }
    total = total_points({"points": values.get("points") or 0, "events": events})
    return f"Tally: {total} points." if events else ""


def _tourney_problem(values: dict[str, Any]) -> str | None:
    if (values.get("points") or 0) < 0:
        return "Points can't be fewer than none."
    return None


def tourney_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    def form(result: dict[str, Any] | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = result if result is not None else {}
            events = {
                key.removeprefix("event_"): value
                for key, value in values.items()
                if key.startswith("event_") and value
            }
            target.update(
                {k: v for k, v in values.items() if not k.startswith("event_")}
            )
            if events:
                target["events"] = events
            else:
                target.pop("events", None)
            if result is None:
                tourney(tribunal).append(target)

        return Form(
            "Add a Tourney Result" if result is None else "Edit a Tourney Result",
            lambda: tourney_fields(saga, tribunal, result),
            apply,
            validate=_tourney_problem,
            live=_tourney_live,
            save_label="Add" if result is None else "Save",
        )

    def remove(index: int) -> Command:
        result = tourney(tribunal)[index]

        def apply() -> None:
            tourney(tribunal).remove(result)

        return Confirm(
            f"Delete {escape(result['team'])}'s result at the Tourney of "
            f"{result.get('year', '')}?",
            apply,
        )

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(tourney(tribunal)[index]),
        remove=remove,
        rows=lambda: [r["team"] for r in tourney(tribunal)],
    )


# -- the Library of the Tribunal (The Lion and the Lily pp. 22-23) --

#: How a book the Tribunal owns in common opens its description (the
#: book pack writes it on each it records at Confluensis).
LIBRARY_HELD = "Held for the Tribunal at Confluensis, as a Tourney prize"

#: How long a book won from the Library is leased: seven years, and back
#: before the next meeting.
LEASE_YEARS = 7

#: How a lease was won: a contributor's automatic prize, or a Tourney prize.
BY_GIFT, BY_TOURNEY = "gift", "tourney"


def book(saga: Saga, book_id: str | None) -> Book | None:
    """The saga's book with that id, if it is still there."""
    return next((b for b in saga.books if book_id and b.id == book_id), None)


def leases(tribunal: Tribunal) -> list[dict[str, Any]]:
    """Each lease of a Library book: {"book_id", "covenant_id", "magus_id",
    "year", "until", "how", "returned" (the year, or None), "held_at" (the
    meeting that granted it)}."""
    return entries(tribunal, KEY, "leases")


def gifts(tribunal: Tribunal) -> list[dict[str, Any]]:
    """Each original book given to the Library: {"book_id", "magus_id",
    "year", "held_at"}."""
    return entries(tribunal, KEY, "gifts")


def given_ids(tribunal: Tribunal) -> list[str]:
    """The books given to the Library, which it now holds."""
    return [g["book_id"] for g in gifts(tribunal) if g.get("book_id")]


def library_books(saga: Saga, tribunal: Tribunal) -> list[Book]:
    """The books the Tribunal owns in common: those its pack records as
    held for it at Confluensis, and those given to it since."""
    given = set(given_ids(tribunal))
    return [
        b
        for b in saga.books
        if b.id in given
        or (b.type != "Other" and b.description.startswith(LIBRARY_HELD))
    ]


def keeper(saga: Saga, tribunal: Tribunal) -> Covenant | None:
    """The covenant that keeps the Library: the one owning its books."""
    for book in library_books(saga, tribunal):
        if book.owner_kind == "covenant" and book.id not in given_ids(tribunal):
            found = saga.covenant(book.owner_id)
            if found is not None:
                return found
    return None


def open_leases(tribunal: Tribunal) -> list[tuple[int, dict[str, Any]]]:
    """(index, lease) of each lease not yet returned."""
    return [(i, e) for i, e in enumerate(leases(tribunal)) if e.get("returned") is None]


def available(saga: Saga, tribunal: Tribunal) -> list[Book]:
    """The Library's books not out on lease."""
    out = {e.get("book_id") for _i, e in open_leases(tribunal)}
    return [b for b in library_books(saga, tribunal) if b.id not in out]


def worth(saga: Saga, book: Book) -> int:
    """A book's worth in Build Points, which a contributor's prize may
    not exceed."""
    return library.cost(book, saga)


#: A Library book costs a Tourney team a prize pawn for each 5 Build
#: Points of its worth (The Lion and the Lily p. 33).
BUILD_POINTS_PER_PAWN = 5


def book_pawns(saga: Saga, book: Book) -> int:
    """The prize pawns a book costs at the Tourney: one per 5 Build Points,
    a fraction counting as a pawn (at least one)."""
    return max(1, round_up(worth(saga, book) / BUILD_POINTS_PER_PAWN))


def team_pawns(tribunal: Tribunal, year: int, name: str) -> int | None:
    """The prize pawns the team called `name` won at `year`'s Tourney, by
    its rank (the p. 33 table); None when it has no result that year."""
    results = tourney(tribunal)
    key = name.strip().lower()
    for index, rank in ranked(tribunal):
        result = results[index]
        if result.get("year") == year and result.get("team", "").strip().lower() == key:
            return PRIZE_PAWNS.get(rank, 0)
    return None


def due(tribunal: Tribunal, year: int) -> list[tuple[int, dict[str, Any]]]:
    """The open leases whose seven years are up by `year`'s meeting."""
    return [
        (i, e) for i, e in open_leases(tribunal) if int(e.get("until") or 0) <= year
    ]


#: What the Code asks of a covenant founded in the Tribunal.
FOUNDING = (
    "Normandy's Code: a new covenant must hold exclusive vis sources "
    "yielding at least a pawn a year for each of its magi (four at the "
    "least), and a council chamber, to be recognised."
)


def covenant_fields(
    _saga: Saga, _tribunal: Tribunal, covenant: Covenant | None
) -> list[DialogField]:
    """A covenant being founded here is told the vis it must hold."""
    if covenant is not None:
        return []
    return [DialogField("founding", "", "info", FOUNDING)]


NORMANDY = TribunalPackage(
    KEY,
    "Normandy",
    customs="Vis tenure",
    book="L&L",
    tabs=(
        PackageTab(
            "Tenure",
            "tab-trib-tenure",
            (PackageList(TENURE_SECTION, tenure_title, tenure_grid, tenure_ops),),
        ),
        PackageTab(
            "Tourney",
            "tab-trib-tourney",
            (PackageList(TOURNEY_SECTION, tourney_title, tourney_grid, tourney_ops),),
        ),
    ),
    # The Library's step is in normandy_meeting.py.
    meeting_steps=("succession", "library", "tourney", "host_by_lot"),
    covenant_fields=covenant_fields,
    about="Every vis source is held on a tenure of the Perthean Compact, and "
    "the covenants' teams contest the Hermetic Tourney after each meeting "
    "for prize pawns. The eldest magus is Praeco, and the next host is drawn "
    "by lot.",
)

register(NORMANDY)
