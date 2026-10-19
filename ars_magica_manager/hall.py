"""The grand hall: a Tribunal's meeting as the desktop draws it, a
hemicycle of seats, one for each vote in the hall, in blocks by
covenant, each seat its magus's House and the side its vote went; the
covenants' pennants round it; and the opening card shown once as a
meeting opens. Only what is drawn is worked out here, from the meeting
as it stands: nothing new is kept."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from . import arms, meeting, tribunals, world
from .arms import Arms
from .models import Case, Covenant, Saga, Tribunal
from .tribunal_packages import Envoy


@dataclass(frozen=True)
class Seat:
    """One vote in the hall: whose (a named magus's, an unnamed one's or a
    proxy's), their House (None when it isn't known), and the side it
    voted (meeting.FOR, AGAINST or UNDECIDED)."""

    who: str
    house_id: str | None
    side: str
    proxy: bool = False


@dataclass(frozen=True)
class Bench:
    """A covenant's seats (or an envoy's one), and its arms for the
    pennant over them; `called` is False until the Praeco has called it."""

    covenant: Covenant | Envoy
    seats: tuple[Seat, ...]
    arms: Arms | None
    called: bool = True


def _members(
    saga: Saga, tribunal: Tribunal, meeting_: dict[str, Any], covenant: Covenant
):
    """Who sits for `covenant`: its named magi, then its unnamed ones,
    less those absent, then the proxies it carries."""
    magi, proxies = meeting.present(saga, tribunal, meeting_, covenant)
    named = [(m.name, m.hermetic.house) for m in world.covenant_magi(saga, covenant)]
    unnamed = [(f"A magus of {covenant.name}", None)] * covenant.unnamed_magi
    seats = (named + unnamed)[:magi]
    return seats + [(f"A proxy carried by {covenant.name}", None)] * proxies, magi


def benches(
    saga: Saga,
    tribunal: Tribunal,
    meeting_: dict[str, Any],
    case: Case | None,
    called: int | None = None,
) -> list[Bench]:
    """The hall, covenant by covenant in the order of the roll: each
    seat's side as the vote on `case` goes (every seat undecided with no
    case). With `called`, only the first `called` covenants have been
    called; the others' seats are not yet decided."""
    found: list[Bench] = []
    calls = (
        list(meeting.call_the_vote(saga, tribunal, meeting_, case))
        if case is not None
        else []
    )
    for index, covenant in enumerate(meeting.voters(saga, tribunal, meeting_)):
        if isinstance(covenant, Envoy):
            who = covenant.name
            if covenant.speaks_for:
                who += f", for {covenant.speaks_for}"
            members = [(who, None)]
            magi = 1
        else:
            members, magi = _members(saga, tribunal, meeting_, covenant)
        shown = called is None or index < called
        sides: list[str] = []
        if shown and index < len(calls):
            vote = calls[index]
            sides = [meeting.FOR] * vote.yes + [meeting.AGAINST] * vote.no
        sides += [meeting.UNDECIDED] * (len(members) - len(sides))
        seats = tuple(
            Seat(who, house, side, i >= magi)
            for i, ((who, house), side) in enumerate(zip(members, sides))
        )
        shield = None if isinstance(covenant, Envoy) else arms.arms_of(covenant)
        found.append(Bench(covenant, seats, shield, shown))
    return found


def tally_so_far(benches_: list[Bench]) -> tuple[int, int, int]:
    """For, against and undecided among the seats shown."""
    counts = {meeting.FOR: 0, meeting.AGAINST: 0, meeting.UNDECIDED: 0}
    for bench in benches_:
        for seat in bench.seats:
            counts[seat.side] += 1
    return counts[meeting.FOR], counts[meeting.AGAINST], counts[meeting.UNDECIDED]


# -- where each seat sits --

#: The hemicycle's rows, innermost first, as fractions of its radius.
INNER, OUTER = 0.42, 0.94


def rows_for(count: int) -> int:
    """How many rows the hall needs for `count` seats."""
    return max(1, min(7, math.ceil(math.sqrt(count / 3))))


def seat_places(count: int) -> list[tuple[float, float]]:
    """Where each of `count` seats sits, from the left of the hemicycle
    round to its right, as (angle, radius): the angle from pi (the left)
    to 0 (the right), the radius a fraction of the hall's. The seats fill
    the rows column by column, so a covenant's seats sit together in a
    wedge; each row has seats in proportion to its length."""
    if count <= 0:
        return []
    rows = rows_for(count)
    radii = [
        INNER + (OUTER - INNER) * (r / (rows - 1) if rows > 1 else 1.0)
        for r in range(rows)
    ]
    total = sum(radii)
    per_row = [max(1, round(count * r / total)) for r in radii]
    per_row[-1] += count - sum(per_row)
    places: list[tuple[float, float]] = []
    for radius, n in zip(radii, per_row):
        for i in range(n):
            angle = math.pi - math.pi * (i + 0.5) / n
            places.append((angle, radius))
    # Left to right across every row at once: covenants sit in wedges.
    places.sort(key=lambda p: (-round(p[0], 6), p[1]))
    return places


# -- the opening card --


def roman(number: int) -> str:
    """ "MCCXXVIII"."""
    numerals = (
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    )
    words = ""
    for value, letters in numerals:
        while number >= value:
            words += letters
            number -= value
    return words


@dataclass(frozen=True)
class OpeningCard:
    """What the card says as a meeting opens."""

    anno: str
    title: str
    opened: str
    arms: list[tuple[str, Arms]] = field(default_factory=list)
    numbers: str = ""


def opening_card(saga: Saga, tribunal: Tribunal) -> OpeningCard:
    record = meeting.record(saga, tribunal)
    year = int(record.get("year") or saga.current_year)
    place = record.get("place") or ""
    members = tribunals.covenants_of(saga, tribunal)
    votes, _proxies = meeting.hall(saga, tribunal, record)
    cases = meeting.business(tribunal)
    motions = sum(1 for c in cases if c.kind == "motion")
    heard = len(cases) - motions
    numbers = [
        f"{len(members)} covenant{'' if len(members) == 1 else 's'}",
        f"{votes} vote{'' if votes == 1 else 's'}",
        f"{heard} case{'' if heard == 1 else 's'}",
        f"{motions} motion{'' if motions == 1 else 's'}",
    ]
    praeco = saga.character(tribunal.praeco_id)
    if praeco is not None:
        numbers.append(f"{praeco.name} presiding")
    name = tribunals.title(tribunal)
    return OpeningCard(
        f"Anno Domini {roman(year)}",
        f"The {name}",
        f"is opened at {place}" if place else "is opened",
        [(c.name, found) for c in members if (found := arms.arms_of(c)) is not None],
        " · ".join(numbers),
    )
