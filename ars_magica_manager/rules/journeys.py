"""How long a journey takes, what passage costs, and what hurrying does
to the travellers: the Travel calculator's rules, without a front-end.

SOURCE: City & Guild, Chapter V: Travel -- the means of transport and
their costs against sea travel (p. 80), the comparison of travelling
speeds and costs (pp. 85-86), adding places to the trade map (p. 89) and
the Naval Trade Tables (pp. 89-90); Errata (Ars Magica 5th Edition)
p. 57, which swaps p. 89's river divisors (8 with the current, 6
against); Definitive Edition, Fatigue (pp. 403-404) and Travel (p. 408).

- **Speeds** (C&G p. 85), for a route's own length: barges 8 to 10 miles
  a day, faster downriver; road cargoes 15 to 25; mounted merchants with
  packhorses about 24; coaches 18 to 24; skilled couriers about 30;
  sailing ships 60 to 80; couriers breaking their horses, with remounts,
  up to 90. The book gives no walking speed: foot travel uses DE p. 408's
  20 miles a day.
- **Direct distance** (C&G p. 89, errata p. 57): divide the distance as
  the crow flies by 12 for road travel, 8 for river travel with the
  current or 6 against it, 60 for sea travel. The divisors include a 20%
  allowance for winding roads and rivers; a mixed route counts as all
  road or all river when it is mostly one, else its legs are summed.
- **The Naval Trade Tables** (C&G pp. 89-90) give a voyage's days
  between named ports directly, through the junctions that link Europe's
  six regions, inland travel to the named city included.
- **Cost** (C&G pp. 85-86): two magi and six grogs pay one pound to
  travel with a merchant for two weeks, in about a ton of space with a
  fortnight's food; hugging the coast, eight need only half a ton. River
  travel costs twice sea travel, road travel 8 to 20 times. Known magi
  may have to pay double for passage. Food, tools and lodging have no
  rate, so travelling on foot or on one's own horses has no figure.
- **Travelling quickly** (DE p. 408) costs one Long-Term Fatigue level a
  day while the characters travel; delays for terrain and weather don't
  reduce it, waiting on toll collectors does. A night's rest restores one
  Long-Term level (p. 404).

The Definitive Edition's figures (p. 408) are shown as a rough guide
beside City & Guild's, which is the fuller source: where they differ
(ships about 30 miles a day against C&G's 60 to 80) the calculator uses
City & Guild's and says what the Definitive Edition gives.

The app's readings, where the books leave a gap:
- the cost is a pound a ton of space a fortnight by sea, counted by the
  day, with eight travellers to the ton (sixteen hugging the coast) and
  cargo by its own tons;
- a known magus doubles the passengers' fare aboard a ship or a barge
  (p. 85 speaks of captains and crews), and changes nothing on the road;
- with the current a barge makes the top of p. 85's range, 10 miles a
  day, and against it the bottom, 8;
- a direct distance on foot or on horseback is lengthened by p. 89's 20%
  before the day's miles are applied (p. 89 gives divisors only for
  trade by road, river and sea);
- hurrying costs one level for each day on the road, and the nights of a
  forced march restore nothing: one level comes back for each night of
  rest without hurrying afterwards;
- a season is 13 weeks (91 days), so a journey that sets out this season
  arrives as many seasons later as it has whole seasons of days.

How far one character can push himself in a day (Grogs pp. 51-52, two
Long-Term levels a day on foot) is rules/travel.py's, read from his
Athletics, Ride and load on the character sheet; this calculator has no
character, so it keeps to the Definitive Edition's party-wide level a
day.

Pattern: the means of travel are a Strategy table (a dict from a key to
its figures), read by `journey`, which the Travel form's inspector shows.
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass

from ..models import FATIGUE_LEVELS as MODEL_FATIGUE_LEVELS
from ..models import next_season

SOURCE = (
    "City & Guild, Chapter V: Travel, pp. 80, 85-86, 89-90; Errata p. 57; "
    "Definitive Edition, Fatigue pp. 403-404, Travel p. 408"
)

CG = "C&G"

# -- how the distance was measured --

#: As the crow flies: p. 89's divisors.
DIRECT = "direct"
#: Along the road or river itself: p. 85's speeds.
ROUTE = "route"
#: Between two named ports: the Naval Trade Tables.
PORTS = "ports"

MEASURES: dict[str, str] = {
    DIRECT: "Direct distance, as the crow flies",
    ROUTE: "Route length, along the road or river",
    PORTS: "Between named ports (the Naval Trade Tables)",
}

#: p. 89's allowance for winding roads and rivers, inside its divisors.
MEANDER = 1.2

#: The divisors of a direct distance (C&G p. 89, with the errata's river
#: figures, p. 57).
ROAD_DIVISOR = 12
RIVER_WITH_CURRENT = 8
RIVER_AGAINST_CURRENT = 6
SEA_DIVISOR = 60

#: Days in the fortnight the passage fare is quoted for (C&G p. 85).
FORTNIGHT = 14
#: Travellers to a ton of space with a fortnight's food (C&G p. 85).
TRAVELLERS_PER_TON = 8
#: The fare by sea: a pound a ton of space a fortnight (C&G p. 85).
SEA_POUNDS_PER_TON_FORTNIGHT = 1
PENCE_PER_POUND = 240
#: What a known magus pays for passage, as a multiple (C&G p. 85).
KNOWN_MAGUS_FARE = 2

#: The Fatigue levels, least to most tired (DE p. 403), as named.
FATIGUE_LEVELS = tuple(level.capitalize() for level in MODEL_FATIGUE_LEVELS)

#: Days in a season, for the season a journey arrives in (the app's
#: reading: a quarter of a year, 13 weeks).
SEASON_DAYS = 91


def arrival(season: str, year: int, days: int) -> tuple[str, int]:
    """The season a journey of `days` that sets out in (season, year)
    arrives in: one season later for each whole season of days."""
    for _ in range(max(days, 0) // SEASON_DAYS):
        season, year = next_season(season, year)
    return season, year


# -- the kinds of travel --

FOOT, RIDER, ROAD, RIVER, SEA = "foot", "rider", "road", "river", "sea"


@dataclass(frozen=True)
class Means:
    """One way to travel: its speed along a route (miles a day, lowest to
    highest, and where from), its divisor of a direct distance (None: none
    in the book), the books' words, its cost against sea travel (None: no
    figure in the book) and the space eight travellers take, in tons."""

    label: str
    kind: str
    speed: tuple[int, int]
    speed_source: str
    divisor: int | None
    words: str
    #: DE p. 408's miles a day, as the rough guide (None: it has none).
    guide: int | None
    guide_words: str
    cost_times: tuple[int, int] | None
    space_for_eight: float = 1.0
    #: The miles a day when the traveller hurries (DE p. 408's urgent
    #: courier); None keeps the usual speed.
    quick_speed: int | None = None
    #: Always a forced march (riding remounts to death leaves no rest).
    hurried: bool = False

    @property
    def on_land(self) -> bool:
        """Whether the travellers walk or ride, and so can hurry."""
        return self.kind in (FOOT, RIDER, ROAD)


#: Every means of travel, by key (Strategy, as a table).
MEANS: dict[str, Means] = {
    "foot": Means(
        "On foot",
        FOOT,
        (20, 20),
        "DE p. 408",
        None,
        "no walking speed",
        20,
        "a peasant walks seven miles to market and home again in a day, "
        "twenty if he only travels",
        None,
    ),
    "horses": Means(
        "On your own horses",
        RIDER,
        (24, 24),
        f"{CG} p. 85",
        None,
        "mounted merchants with light loads travel perhaps 24 miles a day",
        30,
        "a mounted courier about 30 miles a day, 50 if urgent",
        None,
    ),
    "courier": Means(
        "A lone rider, as a courier",
        RIDER,
        (30, 30),
        f"{CG} p. 85",
        None,
        "skilled couriers, single riders, travel around 30 miles a day",
        30,
        "a mounted courier about 30 miles a day, 50 if urgent",
        None,
        quick_speed=50,
    ),
    "remounts": Means(
        "A rider breaking horses, with remounts",
        RIDER,
        (90, 90),
        f"{CG} p. 85",
        None,
        "couriers willing to break their horses, with a steady supply of "
        "remounts, have sometimes managed 90 miles a day",
        100,
        "up to 100 miles a day with lots of good horses, leaving the "
        "traveller no time to rest",
        None,
        hurried=True,
    ),
    "packhorse": Means(
        "With a merchant's packhorses",
        ROAD,
        (24, 24),
        f"{CG} p. 85",
        ROAD_DIVISOR,
        "mounted merchants with light loads, by packhorse, travel perhaps "
        "24 miles a day",
        None,
        "no figure for packhorses",
        (8, 20),
    ),
    "cart": Means(
        "With a merchant's carts",
        ROAD,
        (15, 25),
        f"{CG} p. 85",
        ROAD_DIVISOR,
        "most road cargoes travel 15 to 25 miles a day",
        20,
        "twenty miles a day with a cart is very good progress",
        (8, 20),
    ),
    "coach": Means(
        "By coach",
        ROAD,
        (18, 24),
        f"{CG} p. 85",
        ROAD_DIVISOR,
        "coaches carrying people travel 18 to 24 miles a day, the "
        "discomfort growing with the speed",
        None,
        "no figure for coaches",
        (8, 20),
    ),
    "barge_down": Means(
        "By barge, with the current",
        RIVER,
        (10, 10),
        f"{CG} p. 85",
        RIVER_WITH_CURRENT,
        "river barges travel 8 to 10 miles a day, faster downriver than "
        "upriver; a strong current widens the gap",
        None,
        "no river figure",
        (2, 2),
    ),
    "barge_up": Means(
        "By barge, against the current",
        RIVER,
        (8, 8),
        f"{CG} p. 85",
        RIVER_AGAINST_CURRENT,
        "river barges travel 8 to 10 miles a day, slower upriver than "
        "downriver; a strong current widens the gap",
        None,
        "no river figure",
        (2, 2),
    ),
    "ship": Means(
        "By sailing ship",
        SEA,
        (60, 80),
        f"{CG} p. 85",
        SEA_DIVISOR,
        "sailing vessels travel roughly 60 to 80 miles a day, and many "
        "ventures stall for weeks waiting for the weather; six pounds "
        "charters a small crewed ship for a season",
        30,
        "most ships about 30 miles a day, good ships with good wind three "
        "or four times that",
        (1, 1),
    ),
    "coast": Means(
        "By ship, hugging the coast",
        SEA,
        (60, 80),
        f"{CG} p. 85",
        SEA_DIVISOR,
        "sailing vessels travel roughly 60 to 80 miles a day; restocking "
        "along the coast, eight passengers need only half a ton of space",
        30,
        "most ships about 30 miles a day, good ships with good wind three "
        "or four times that",
        (1, 1),
        space_for_eight=0.5,
    ),
}


# -- the Naval Trade Tables (C&G pp. 89-90) --


@dataclass(frozen=True)
class NavalTable:
    """One region's table: its places, and the days from each (a row) to
    each (a column), as printed. A few pairs differ by direction in the
    book (Bordeaux to Seville 21, Seville to Bordeaux 19): each is kept
    as printed, read from the row's place to the column's."""

    places: tuple[str, ...]
    days: tuple[tuple[int, ...], ...]


NAVAL_TABLES: tuple[NavalTable, ...] = (
    NavalTable(
        (
            "Bruges",
            "Dublin",
            "Edinburgh (Leith)",
            "Hamburg",
            "London",
            "Paris",
            "Brittany Junction",
            "Skagarek Junction",
        ),
        (
            (0, 11, 8, 7, 4, 32, 8, 11),
            (11, 0, 12, 17, 12, 36, 7, 9),
            (8, 12, 0, 9, 9, 38, 13, 9),
            (7, 17, 9, 0, 9, 38, 10, 7),
            (3, 11, 8, 8, 1, 32, 5, 17),
            (27, 31, 33, 33, 5, 0, 35, 34),
            (7, 5, 13, 10, 9, 40, 0, 16),
            (9, 17, 9, 7, 12, 39, 16, 0),
        ),
    ),
    NavalTable(
        ("Danzig", "Lubeck", "Reval", "Riga", "Skagarek Junction"),
        (
            (0, 6, 8, 6, 8),
            (6, 0, 12, 10, 5),
            (8, 12, 0, 6, 13),
            (6, 10, 6, 0, 12),
            (8, 5, 13, 12, 0),
        ),
    ),
    NavalTable(
        (
            "Bilhorod",
            "Constanta",
            "Kaffa",
            "Trebizond",
            "Varna",
            "Constantinople Junction",
        ),
        (
            (0, 3, 2, 10, 5, 6),
            (3, 0, 6, 12, 1, 4),
            (2, 6, 0, 7, 7, 7),
            (10, 12, 7, 0, 15, 10),
            (5, 1, 7, 15, 0, 3),
            (6, 4, 7, 10, 3, 0),
        ),
    ),
    NavalTable(
        ("Bordeaux", "Lisbon", "Seville", "Brittany Junction", "Gibraltar Junction"),
        (
            (0, 14, 21, 6, 19),
            (14, 0, 7, 13, 5),
            (19, 5, 0, 18, 5),
            (6, 13, 20, 0, 18),
            (19, 5, 7, 18, 0),
        ),
    ),
    NavalTable(
        (
            "Algiers",
            "Barcelona",
            "Genoa",
            "Marseilles",
            "Naples",
            "Palermo",
            "Palma",
            "Pisa",
            "Rome",
            "Valencia",
            "Gibraltar Junction",
            "Messina Junction",
            "Syracuse Junction",
            "Tunis Junction",
        ),
        (
            (0, 5, 10, 8, 11, 10, 3, 10, 10, 4, 8, 12, 12, 8),
            (5, 0, 7, 4, 11, 11, 3, 7, 8, 3, 10, 13, 14, 9),
            (10, 7, 0, 4, 6, 8, 9, 1, 4, 10, 17, 9, 11, 9),
            (8, 4, 4, 0, 9, 9, 6, 4, 6, 7, 14, 11, 12, 9),
            (11, 11, 6, 9, 0, 3, 11, 5, 21, 13, 19, 3, 5, 6),
            (10, 11, 8, 9, 3, 0, 10, 7, 4, 13, 18, 2, 4, 4),
            (3, 3, 9, 6, 11, 10, 0, 9, 9, 3, 9, 12, 13, 8),
            (10, 7, 1, 4, 5, 7, 9, 0, 3, 10, 17, 8, 9, 8),
            (10, 8, 4, 6, 21, 4, 9, 3, 0, 11, 18, 5, 7, 6),
            (4, 3, 10, 7, 13, 13, 3, 10, 11, 0, 8, 15, 15, 11),
            (8, 10, 17, 14, 19, 18, 9, 17, 18, 8, 0, 20, 20, 16),
            (12, 13, 9, 11, 3, 2, 12, 8, 5, 15, 20, 0, 1, 6),
            (12, 14, 11, 12, 5, 4, 13, 9, 7, 15, 20, 1, 0, 5),
            (8, 9, 9, 9, 6, 4, 8, 8, 6, 11, 16, 6, 5, 0),
        ),
    ),
    NavalTable(
        (
            "Acre",
            "Alexandria",
            "Crete (Iraklion)",
            "Cyprus (Larnaca)",
            "Smyrna",
            "Split",
            "Venice",
            "Constantinople Junction",
            "Messina Junction",
            "Syracuse Junction",
            "Tunis Junction",
        ),
        (
            (0, 6, 22, 3, 12, 23, 26, 16, 19, 19, 24),
            (6, 0, 7, 6, 10, 20, 23, 14, 16, 16, 20),
            (22, 7, 0, 8, 5, 13, 17, 9, 10, 9, 5),
            (3, 6, 8, 0, 10, 22, 25, 15, 18, 18, 22),
            (12, 10, 5, 10, 0, 16, 19, 5, 12, 12, 17),
            (23, 20, 13, 22, 16, 0, 4, 19, 9, 9, 14),
            (26, 23, 17, 25, 19, 4, 0, 22, 12, 13, 18),
            (16, 14, 9, 15, 5, 19, 22, 0, 16, 15, 20),
            (19, 16, 10, 18, 12, 9, 12, 16, 0, 1, 6),
            (19, 16, 9, 18, 12, 9, 13, 15, 1, 0, 5),
            (24, 20, 5, 22, 17, 14, 18, 20, 6, 5, 0),
        ),
    ),
)


def _legs() -> dict[str, dict[str, int]]:
    """Every printed leg, from place to place: the quickest where two
    tables both give one (the junctions they share)."""
    legs: dict[str, dict[str, int]] = {}
    for table in NAVAL_TABLES:
        for i, start in enumerate(table.places):
            for j, end in enumerate(table.places):
                if i != j:
                    days = table.days[i][j]
                    known = legs.setdefault(start, {}).get(end)
                    legs[start][end] = days if known is None else min(known, days)
    return legs


NAVAL_LEGS = _legs()

#: The named ports a voyage can start or end at (not the junctions), in
#: alphabetical order.
PORTS_LISTED: tuple[str, ...] = tuple(
    sorted(place for place in NAVAL_LEGS if not place.endswith("Junction"))
)


@dataclass(frozen=True)
class Voyage:
    """The quickest voyage the tables give: its days and the places it
    passes, start and end included."""

    days: int
    path: tuple[str, ...]


def voyage(start: str, end: str) -> Voyage | None:
    """The quickest voyage from `start` to `end` by the Naval Trade
    Tables, adding the days to each junction and then to the port (C&G
    p. 89); None when either isn't in the tables."""
    if start not in NAVAL_LEGS or end not in NAVAL_LEGS:
        return None
    if start == end:
        return Voyage(0, (start,))
    best: dict[str, int] = {start: 0}
    came_from: dict[str, str] = {}
    queue: list[tuple[int, str]] = [(0, start)]
    while queue:
        days, place = heapq.heappop(queue)
        if place == end:
            break
        if days > best.get(place, days):
            continue
        for following, leg in NAVAL_LEGS[place].items():
            total = days + leg
            if total < best.get(following, total + 1):
                best[following] = total
                came_from[following] = place
                heapq.heappush(queue, (total, following))
    if end not in best:
        return None
    path = [end]
    while path[-1] != start:
        path.append(came_from[path[-1]])
    return Voyage(best[end], tuple(reversed(path)))


# -- a journey --


@dataclass(frozen=True)
class Fatigue:
    """A forced march: the days hurried, the Long-Term Fatigue levels lost
    (one a day, DE p. 408) and the level each day ends at, and the nights
    of unhurried rest that restore them (one a night, DE p. 404)."""

    days: int
    levels_lost: int
    #: (day, the level the travellers end it at), one per day lost, up to
    #: Unconscious.
    by_day: tuple[tuple[int, str], ...]
    nights_to_recover: int

    @property
    def level(self) -> str:
        return FATIGUE_LEVELS[self.levels_lost]

    @property
    def unconscious_on(self) -> int | None:
        """The day the travellers fall unconscious, if the march is that
        long."""
        last = len(FATIGUE_LEVELS) - 1
        return last if self.days >= last else None


def forced_march(days: int) -> Fatigue:
    """One Long-Term Fatigue level for each day of hurried travel (DE
    p. 408), down to Unconscious; one back for each night's rest without
    hurrying afterwards (p. 404, the app's reading)."""
    most = len(FATIGUE_LEVELS) - 1
    lost = min(max(days, 0), most)
    return Fatigue(
        days,
        lost,
        tuple((day, FATIGUE_LEVELS[day]) for day in range(1, lost + 1)),
        lost,
    )


@dataclass(frozen=True)
class Journey:
    """What a journey comes to: its days (fewest to most), how they were
    worked out, the rough guide's days, the space taken and the cost in
    pence (None: no figure in the book), and the Fatigue of hurrying."""

    measure: str
    means: Means | None
    days: tuple[int, int]
    #: How the days were worked out, with the page (plain text).
    working: str
    #: The miles travelled along the way (a direct distance with p. 89's
    #: 20% added), or None for a voyage by the tables.
    route_miles: float | None
    guide_days: int | None
    space_tons: float
    cost_pence: tuple[float, float] | None
    known_magus_doubled: bool
    fatigue: Fatigue | None
    voyage: Voyage | None = None

    @property
    def hurried(self) -> bool:
        return self.fatigue is not None


def _days(miles: float, speed: float) -> int:
    """Whole days to cover `miles` at `speed` a day: a part day counts."""
    return max(1, math.ceil(miles / speed - 1e-9)) if miles > 0 else 0


def travel_days(
    means: Means, miles: float, measure: str, quick: bool = False
) -> tuple[tuple[int, int], str, float]:
    """The days `means` takes over `miles` measured as `measure` (DIRECT
    or ROUTE), fewest to most; how they were worked out; and the miles
    actually travelled."""
    if measure == DIRECT:
        route = miles * MEANDER
        if means.divisor is not None:
            days = _days(miles, means.divisor)
            how = {
                ROAD: "for road travel",
                RIVER: "with the current"
                if means.divisor == RIVER_WITH_CURRENT
                else "against the current",
                SEA: "for sea travel",
            }[means.kind]
            page = f"{CG} p. 89" + (", errata p. 57" if means.kind == RIVER else "")
            return (
                (days, days),
                f"{_miles(miles)} miles / {means.divisor} {how}, winding "
                f"included ({page})",
                route,
            )
        lengthened = f"{_miles(miles)} miles + 20% for the winding way"
    else:
        route = miles
        lengthened = f"{_miles(miles)} miles"
    if quick and means.quick_speed is not None:
        days = _days(route, means.quick_speed)
        return (
            (days, days),
            f"{lengthened} at {means.quick_speed} a day, an urgent courier's "
            "pace (DE p. 408)",
            route,
        )
    low, high = means.speed
    fewest, most = _days(route, high), _days(route, low)
    pace = f"{low}" if low == high else f"{low} to {high}"
    return (
        (fewest, most),
        f"{lengthened} at {pace} a day ({means.speed_source})",
        route,
    )


def _miles(miles: float) -> str:
    return f"{miles:,.0f}" if miles == int(miles) else f"{miles:,.1f}"


def space(means: Means | None, travellers: int, cargo: float) -> float:
    """The tons of space the travellers (eight to the ton with their food,
    sixteen hugging the coast) and their cargo take (C&G p. 85)."""
    for_eight = means.space_for_eight if means is not None else 1.0
    return travellers / TRAVELLERS_PER_TON * for_eight + max(cargo, 0.0)


def cost(
    means: Means,
    days: tuple[int, int],
    travellers: int,
    cargo: float,
    known_magus: bool = False,
) -> tuple[float, float] | None:
    """What passage costs in pence, least to most: a pound a ton of space
    a fortnight by sea, counted by the day, twice that by river and 8 to
    20 times by road (C&G pp. 85-86); a known magus doubles the
    passengers' fare aboard (p. 85). None where the book has no figure
    (on foot, on one's own horses)."""
    if means.cost_times is None:
        return None
    people = space(means, travellers, 0.0)
    if known_magus and means.kind in (RIVER, SEA):
        people *= KNOWN_MAGUS_FARE
    tons = people + max(cargo, 0.0)
    rate = SEA_POUNDS_PER_TON_FORTNIGHT * PENCE_PER_POUND * tons / FORTNIGHT
    (fewest, most), (cheap, dear) = days, means.cost_times
    return (rate * fewest * cheap, rate * most * dear)


def guide_days(means: Means, route_miles: float) -> int | None:
    """The Definitive Edition's rough guide (p. 408): the days at its
    miles a day, or None where it gives none."""
    if means.guide is None:
        return None
    return _days(route_miles, means.guide)


def journey(
    means_key: str | None,
    miles: float | None,
    measure: str = ROUTE,
    *,
    travellers: int = 0,
    cargo: float = 0.0,
    known_magus: bool = False,
    quick: bool = False,
    start_port: str | None = None,
    end_port: str | None = None,
) -> Journey | None:
    """The journey by `means_key` over `miles` measured as `measure`, or
    between two named ports (PORTS) by the Naval Trade Tables; None while
    there isn't enough to work it out (no distance, no means, a port not
    chosen or no voyage between them)."""
    travellers, cargo = max(travellers, 0), max(cargo, 0.0)
    if measure == PORTS:
        found = voyage(start_port or "", end_port or "")
        if found is None:
            return None
        ship = MEANS["ship"]
        days = (found.days, found.days)
        return Journey(
            PORTS,
            None,
            days,
            f"the Naval Trade Tables, {' > '.join(found.path)} ({CG} pp. 89-90)",
            None,
            None,
            space(ship, travellers, cargo),
            cost(ship, days, travellers, cargo, known_magus),
            known_magus,
            None,
            found,
        )
    means = MEANS.get(means_key or "")
    if means is None or not miles or miles <= 0:
        return None
    hurrying = means.on_land and (quick or means.hurried)
    days, working, route = travel_days(means, miles, measure, hurrying)
    return Journey(
        measure,
        means,
        days,
        working,
        route,
        guide_days(means, route),
        space(means, travellers, cargo),
        cost(means, days, travellers, cargo, known_magus),
        known_magus and means.kind in (RIVER, SEA),
        forced_march(days[1]) if hurrying else None,
    )
