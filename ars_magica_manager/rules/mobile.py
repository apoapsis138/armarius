"""A covenant that moves: which of its dated stops is in force, its route,
and what the Waters of a Place mean for a fleet.

The books give a mobile covenant no mechanics of its own: Constantly
Mobile and Erratically Mobile are story Hooks (Covenants pp. 9-10). What
they show is how little travels: people, ships and laboratories go (a
lab with the Mobile Virtue, DE p. 293), while an aura comes from where
the covenant is (Through the Aegis pp. 11, 23-24), and where two realms
have influence only the stronger holds sway (DE p. 410). An Aegis is a
Boundary effect and stays behind when what it surrounds moves (Legends
of Hermes p. 123). The errata touch none of this.

A stop in force decides where a covenant is; with no stop it is where
its own place puts it, so a covenant that never moves is unchanged. That
no ship holds an Aegis unless docked at a Port all season, and that a
Place travelling with a covenant takes the stronger of its own aura and
its surroundings', are the troupe's rulings, not printed rules; a tie
keeps its own.

Pattern: Temporal Property, a dated list and one function, as GuestStay
is; a circuit is a Circular Iterator, which here is (i + 1) % len(route).
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from ..models import (
    Covenant,
    CovenantStop,
    RouteStop,
    season_order,
)

SOURCE = (
    "Covenants pp. 9-10 (Constantly and Erratically Mobile), 26-27; Through "
    "the Aegis pp. 11, 23-25, 118-120; Legends of Hermes p. 123; The Sundered "
    "Eagle p. 84; Definitive Edition p. 410"
)

#: The two Mobile Hooks of the covenant catalog (Covenants pp. 9-10).
MOBILE_HOOKS: tuple[str, ...] = (
    "covbh_hook_major_constantly_mobile",
    "covbh_hook_minor_erratically_mobile",
)
#: How a sketch covenant's What Matters names the same Hooks.
_MOBILE_WORDS = re.compile(r"\b(?:Constantly|Erratically) Mobile\b")

#: What a Place offers ships (a Place's Waters).
OPEN_WATER, ANCHORAGE, PORT = "Open water", "Anchorage", "Port"
WATERS: tuple[str, ...] = (OPEN_WATER, ANCHORAGE, PORT)


def stop_in_force(
    stops: Sequence[CovenantStop], year: int, season: str
) -> CovenantStop | None:
    """The latest stop not after `season` of `year` (the later entered,
    of two for one season); None before the first. Stops still to come
    aren't in force until the date reaches them."""
    now = season_order(season=season, year=year)
    found: CovenantStop | None = None
    for stop in stops:
        when = season_order(season=stop.season, year=stop.year)
        if when <= now and (
            found is None or when >= season_order(season=found.season, year=found.year)
        ):
            found = stop
    return found


def date_order(stops: list[CovenantStop]) -> None:
    """Sort `stops` by date, in place, oldest first."""
    stops.sort(key=lambda s: season_order(season=s.season, year=s.year))


def has_mobile_hook(covenant: Covenant) -> bool:
    """Whether it has a Mobile Hook: attached, or named in What Matters."""
    return any(held.vf_id in MOBILE_HOOKS for held in covenant.boons_hooks) or bool(
        _MOBILE_WORDS.search(covenant.what_matters)
    )


def next_leg(covenant: Covenant) -> RouteStop | None:
    """The leg of its route it goes to next; None with no route, or at
    the end of one that isn't a circuit."""
    route = covenant.route
    if not route:
        return None
    if covenant.route_at < len(route):
        return route[covenant.route_at]
    return route[0] if covenant.circuit else None


def _is_at(leg: RouteStop, place_id: str | None, level: int) -> bool:
    return (leg.place_id, leg.level) == (place_id, level)


def next_leg_from(
    covenant: Covenant, place_id: str | None, level: int = 0
) -> RouteStop | None:
    """The next leg that isn't where it is now, since a leg it is already
    at is no move; None with nowhere else to go."""
    route = covenant.route
    if not route:
        return None
    ahead = len(route) if covenant.circuit else len(route) - covenant.route_at
    for offset in range(ahead):
        leg = route[(covenant.route_at + offset) % len(route)]
        if not _is_at(leg, place_id, level):
            return leg
    return None


def step_past_here(covenant: Covenant, place_id: str | None, level: int = 0) -> None:
    """Move past the legs it is already at."""
    for _ in covenant.route:
        leg = next_leg(covenant)
        if leg is None or not _is_at(leg, place_id, level):
            return
        step_route(covenant)


def step_route(covenant: Covenant) -> None:
    """Move past the next leg: round to the first on a circuit."""
    if not covenant.route:
        covenant.route_at = 0
    elif covenant.circuit:
        covenant.route_at = (covenant.route_at + 1) % len(covenant.route)
    else:
        covenant.route_at = min(covenant.route_at + 1, len(covenant.route))


def planned_stay(covenant: Covenant) -> int:
    """The seasons planned at the leg it came to last (1 before any)."""
    route = covenant.route
    if not route or (covenant.route_at == 0 and not covenant.circuit):
        return 1
    return route[(covenant.route_at - 1) % len(route)].seasons


def seasons_here(stops: Sequence[CovenantStop], stop: CovenantStop) -> int:
    """How many seasons running the stops have it at `stop`'s place, up to
    and including `stop`."""
    ordered = sorted(stops, key=lambda s: season_order(season=s.season, year=s.year))
    count = 0
    for entry in reversed(ordered[: ordered.index(stop) + 1]):
        if (entry.place_id, entry.level) != (stop.place_id, stop.level):
            break
        count += 1
    return count
