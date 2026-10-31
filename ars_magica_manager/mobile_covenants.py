"""A covenant on the move, independent of how it is drawn: the Whereabouts
section (its stops, Add a Stop, Plan Route), what Advance Season asks of
it, the Aegis it leaves behind, and a ship that leaves the fleet (Detach
and Rejoin).

Where it is now is rules.sites' (the stop in force); this writes the
stops. Stops are the log, the route is the plan: moving on logs a stop
and steps the route, so the route never rewrites what happened. A ship
apart is still of the covenant: being a covenant rests on the charter,
not on being together (Guardians of the Forests p. 70; the Northern
Seas's charter, Through the Aegis p. 25).

Pattern: Temporal Property for the stops, a commands.Form over the
covenant or ship for each step, and SectionOps for the list.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import diaries, places, storage
from .commands import Command, Confirm, Form, Refuse, SectionOps, notes
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import (
    SEASONS,
    Character,
    Covenant,
    CovenantDiaryEntry,
    CovenantStop,
    Neighbour,
    Possession,
    RouteStop,
    Saga,
    next_season,
    season_order,
)
from .models.ships import Ship
from .rules import mobile, realms, sites
from .rules import ships as ship_rules
from .sections import WHEREABOUTS_SECTION

TITLE = "Whereabouts"
ADD_TITLE = "Add a Stop"
ROUTE_TITLE = "Plan Route"
DETACH_TITLE = "Detach"
REJOIN_TITLE = "Rejoin"
ASK_TITLE = "Where Next?"
HELP_ID = WHEREABOUTS_SECTION
DEFENCE = "Defence & Magic"
#: The legs a Plan Route form has beyond those planned.
SPARE_LEGS = 3
MOST_FEW_LEGS = 6

#: Advance Season's answers.
MOVE_ON, STAY, ELSEWHERE = "move", "stay", "elsewhere"

ANCHOR_WORDS = (
    "A ship at anchor isn't stationary enough to hold an Aegis of the Hearth."
)


def _when(year: int, season: str) -> str:
    return f"{season} {year}"


def shows(covenant: Covenant) -> bool:
    """Whether its sheet shows Whereabouts: it has a stop, a route or a
    Mobile Hook."""
    return bool(covenant.stops or covenant.route or mobile.has_mobile_hook(covenant))


def _at(saga: Saga, covenant: Covenant) -> tuple[str | None, int]:
    """Which Place and level it is at: its stop in force's, else its own."""
    stop = sites.covenant_stop(saga, covenant)
    if stop is not None:
        return stop.place_id, stop.level
    return covenant.place_id, covenant.place_level


def fleet_afloat(covenant: Covenant) -> bool:
    """Whether it has a ship still sailing."""
    return any(
        not ship_rules.lost(ship_rules.ship_of(record))
        for record in ship_rules.ships_of(covenant)
    )


# -- what the sheet says --


def title(covenant: Covenant) -> str:
    return f"{TITLE} ({len(covenant.stops)})"


def where_now(saga: Saga, covenant: Covenant) -> str:
    """ "The Northern Seas, Magic 0": where it is now and the aura holding
    sway (plain words); "" for nowhere."""
    where = sites.covenant_place(saga, covenant)
    if where is None:
        return ""
    aura, realm = sites.aura_here(saga, *where)
    place_id, level = _at(saga, covenant)
    named = places.where_text(saga, place_id, level)
    return f"{named or where[0].name}, {realm} {realms.with_boons(covenant, aura)}"


def route_text(saga: Saga, covenant: Covenant) -> str:
    """The route in words, the next leg marked; "" for none."""
    if not covenant.route:
        return ""
    upcoming = mobile.next_leg_from(covenant, *_at(saga, covenant))
    legs = []
    for leg in covenant.route:
        words = places.where_text(saga, leg.place_id, leg.level)
        if leg.seasons > 1:
            words += f" ({leg.seasons} seasons)"
        legs.append(f"[b]{escape(words)}[/]" if leg is upcoming else escape(words))
    joined = " > ".join(legs)
    return f"{joined} > round again" if covenant.circuit else joined


def vis_this_season(saga: Saga, covenant: Covenant) -> str:
    """The vis sources harvested this season and where they lie (markup);
    "" for none. It doesn't check the covenant gets there."""
    found = [
        record.name + (f" ({record.location})" if record.location else "")
        for record in covenant.possessions
        if record.kind == "vis_source" and record.season == saga.current_season
    ]
    return escape("; ".join(found))


def summary_text(saga: Saga, covenant: Covenant) -> str:
    """The section's lines above its stops (markup): where it is now, its
    home, its route and this season's vis."""
    now = where_now(saga, covenant)
    home = sites.place(saga, covenant.place_id)
    lines = [f"[$label]Here now:[/] {escape(now) if now else 'nowhere entered'}"]
    stop = sites.covenant_stop(saga, covenant)
    if stop is not None and home is not None and not sites.travels(home):
        lines.append(f"[$label]Home:[/] {escape(home.name)}")
    route = route_text(saga, covenant)
    if route:
        lines.append(f"[$label]Route:[/] {route}")
    vis = vis_this_season(saga, covenant)
    if vis:
        lines.append(f"[$label]Vis this season:[/] {vis}")
    return "\n".join(lines)


def _newest_first(covenant: Covenant) -> list[CovenantStop]:
    return list(reversed(covenant.stops))


def grid(saga: Saga, covenant: Covenant) -> Grid:
    """The stops, newest first; the one in force is marked, and one still
    to come says so."""
    now = season_order(season=saga.current_season, year=saga.current_year)
    in_force = sites.covenant_stop(saga, covenant)
    rows: list[list[str]] = []
    for stop in _newest_first(covenant):
        found = sites.place(saga, stop.place_id)
        aura = realms.aura_at_stop(saga, covenant, stop)
        state = (
            "Here now"
            if stop is in_force
            else "Planned"
            if season_order(season=stop.season, year=stop.year) > now
            else ""
        )
        rows.append(
            [
                _when(stop.year, stop.season),
                places.where_text(saga, stop.place_id, stop.level),
                f"{aura[1]} {aura[0]}",
                sites.waters_of(found) if found is not None else "",
                state,
                stop.note,
            ]
        )
    return Grid(
        ["When", "Where", "Aura", "Waters", "", "Note"],
        rows,
        list(range(len(rows))),
        "No stops yet: Add a Stop logs where it is.",
        caps=[12, 34, 10, 10, 8, 0],
        stretch=5,
    )


# -- the Aegis --


def _aegis_lost(covenant: Covenant, year: int, season: str, why: str) -> list[str]:
    """Drop its Aegis to nothing, saying so in the Diary; nothing to say
    without one."""
    level = covenant.aegis_of_the_hearth
    if not level:
        return []
    covenant.aegis_of_the_hearth = 0
    covenant.aegis_penetration = 0
    text = f"Its Aegis of the Hearth, level {level}, is gone: {why}"
    covenant.diary.append(
        CovenantDiaryEntry(
            year, season, "The Aegis of the Hearth", text, category=DEFENCE
        )
    )
    return notes(f"{escape(covenant.name)}: {escape(text)}")


def aegis_refused(saga: Saga, covenant: Covenant) -> str:
    """Why a ship covenant can't hold an Aegis where it is now; "" where
    it can. It holds one only docked at a Port all season: moving on drops
    it, so a Port is all this needs to ask (Legends of Hermes p. 123; the
    Port is the troupe's ruling)."""
    if sites.covenant_stop(saga, covenant) is None or not fleet_afloat(covenant):
        return ""
    place = sites.place(saga, _at(saga, covenant)[0])
    if place is None:
        return ""
    waters = sites.waters_of(place)
    if waters == mobile.PORT:
        return ""
    if waters == mobile.ANCHORAGE:
        return ANCHOR_WORDS
    return "A ship covenant holds an Aegis only docked at a Port all season."


def aegis_problem(saga: Saga, covenant: Covenant, values: dict[str, Any]) -> str | None:
    """A higher Aegis typed where a ship covenant can't hold one."""
    level = values.get("aegis_of_the_hearth") or 0
    if level <= covenant.aegis_of_the_hearth:
        return None
    return aegis_refused(saga, covenant) or None


def _log_stop(saga: Saga, covenant: Covenant, stop: CovenantStop) -> list[str]:
    """Log `stop`, in date order: when that moves the covenant, the Aegis
    stays behind (a Boundary effect, Legends of Hermes p. 123)."""
    before = _at(saga, covenant)
    covenant.stops.append(stop)
    mobile.date_order(covenant.stops)
    places.sync(saga)
    if _at(saga, covenant) == before:
        return []
    return _aegis_lost(
        covenant,
        stop.year,
        stop.season,
        f"left behind when the covenant moved to "
        f"{places.where_text(saga, stop.place_id, stop.level)}.",
    )


# -- the stop form --


def _choices(
    saga: Saga, covenant: Covenant, leave_out: tuple[str, ...] = ()
) -> list[tuple[str, str]]:
    """Each Place and level a stop can name, but those travelling with the
    covenant: for a fleet, the Places marked with Waters first."""
    own = {p.id for p in sites.travelling_places(saga, covenant)}
    options = places.where_options(saga, {*own, *leave_out})
    if not fleet_afloat(covenant):
        return options

    def marked(option: tuple[str, str]) -> bool:
        found = sites.place(saga, places.split(option[1])[0])
        return found is None or not sites.waters_of(found)

    return sorted(options, key=marked)


def _carries_aura(covenant: Covenant) -> bool:
    """Whether its typed aura might be one that travels: no place yet and
    no stops."""
    return covenant.place_id is None and covenant.aura > 0 and not covenant.stops


def stop_fields(
    saga: Saga, covenant: Covenant, stop: CovenantStop | None
) -> list[DialogField]:
    year = stop.year if stop is not None else saga.current_year
    season = stop.season if stop is not None else saga.current_season
    fields = [
        DialogField("year", "Year", "int", year),
        DialogField("season", "Season", "select", season, options=pairs(SEASONS)),
        DialogField(
            "where",
            "Place",
            "select",
            places.where_value(stop.place_id, stop.level) if stop else None,
            options=_choices(saga, covenant),
            required=True,
            allow_blank=True,
            placeholder="(choose a Place from The Region)",
            hint="Open water is a Place too: a sea Place with no aura.",
        ),
        DialogField("note", "Note", "text", stop.note if stop else ""),
    ]
    if stop is None and _carries_aura(covenant):
        fields.append(
            DialogField(
                "carries",
                "Its aura travels with it",
                "check",
                False,
                hint="A ship's own aura, say: the aura typed on it becomes a "
                "Place that moves with it, and the stronger aura holds sway "
                "(DE p. 410). Leave it off and the aura stays behind.",
            )
        )
    return fields


def stop_live(saga: Saga, covenant: Covenant) -> Callable[[dict[str, Any]], str]:
    """What the Place chosen gives, and what it warns of."""

    def live(values: dict[str, Any]) -> str:
        place_id, level = places.split(values.get("where"))
        found = sites.place(saga, place_id)
        if found is None:
            return ""
        aura, realm = realms.aura_at_stop(
            saga, covenant, CovenantStop(saga.current_year, "", found.id, level)
        )
        lines = [f"[b]Aura there:[/] {realm} {aura}"]
        if fleet_afloat(covenant) and not sites.waters_of(found):
            lines.append(
                "[$text-warning]This Place isn't marked with Waters: ships "
                "may not be able to stop here.[/]"
            )
        moved = (place_id, level) != _at(saga, covenant)
        if moved and covenant.aegis_of_the_hearth:
            lines.append(
                "[$text-warning]The covenant's Aegis stays behind and drops to 0.[/]"
            )
        return "\n".join(lines)

    return live


def stop_problem(
    stops: list[CovenantStop], stop: CovenantStop | None
) -> Callable[[dict[str, Any]], str | None]:
    def problem(values: dict[str, Any]) -> str | None:
        if not values.get("where"):
            return "Choose the Place it stopped at."
        year, season = values.get("year"), values.get("season")
        taken = any(
            other is not stop and (other.year, other.season) == (year, season)
            for other in stops
        )
        if taken:
            return f"A stop is already logged for {season} {year}: edit that one."
        return None

    return problem


def _own_aura_place(saga: Saga, covenant: Covenant) -> None:
    """Make its typed aura a Place travelling with it, and put it there."""
    record = Neighbour(
        storage.generate_unique_id(covenant.name, [n.id for n in saga.neighbours]),
        covenant.name,
        kind=sites.PLACE,
        realm=covenant.aura_realm,
        details={"aura": covenant.aura, sites.TRAVELS_WITH: covenant.id},
    )
    saga.neighbours.append(record)
    covenant.place_id, covenant.place_level = record.id, 0


def add_stop(saga: Saga, covenant: Covenant) -> Form:
    """More's Add a Stop, for any covenant; a on Whereabouts."""

    def apply(values: dict[str, Any]) -> list[str]:
        if values.get("carries"):
            _own_aura_place(saga, covenant)
        place_id, level = places.split(values.get("where"))
        assert place_id is not None
        stop = CovenantStop(
            int(values["year"]),
            values["season"],
            place_id,
            level,
            (values.get("note") or "").strip(),
        )
        return notes(
            f"{escape(covenant.name)} is logged at "
            f"{escape(places.where_text(saga, place_id, level))}.",
            *_log_stop(saga, covenant, stop),
        )

    return Form(
        f"{ADD_TITLE}: {escape(covenant.name)}",
        lambda: stop_fields(saga, covenant, None),
        apply,
        validate=stop_problem(covenant.stops, None),
        live=stop_live(saga, covenant),
        help_id=HELP_ID,
        inspector="What It Means",
    )


def _edit_stop(saga: Saga, covenant: Covenant, row: int) -> Command:
    stop = _newest_first(covenant)[row]

    def apply(values: dict[str, Any]) -> None:
        stop.year, stop.season = int(values["year"]), values["season"]
        place_id, stop.level = places.split(values.get("where"))
        assert place_id is not None
        stop.place_id = place_id
        stop.note = (values.get("note") or "").strip()
        mobile.date_order(covenant.stops)
        places.sync(saga)

    return Form(
        f"Edit Stop: {escape(_when(stop.year, stop.season))}",
        lambda: stop_fields(saga, covenant, stop),
        apply,
        validate=stop_problem(covenant.stops, stop),
        live=stop_live(saga, covenant),
        help_id=HELP_ID,
        inspector="What It Means",
    )


def _remove_stop(saga: Saga, covenant: Covenant, row: int) -> Command:
    stop = _newest_first(covenant)[row]

    def apply() -> None:
        covenant.stops.remove(stop)
        places.sync(saga)

    return Confirm(
        f"Delete the stop of {escape(_when(stop.year, stop.season))}?", apply
    )


def ops(saga: Saga, covenant: Covenant) -> SectionOps:
    return SectionOps(
        add=lambda: add_stop(saga, covenant),
        edit=lambda row: _edit_stop(saga, covenant, row),
        remove=lambda row: _remove_stop(saga, covenant, row),
        rows=lambda: [
            places.where_text(saga, s.place_id, s.level)
            for s in _newest_first(covenant)
        ],
    )


def section_ops(saga: Saga, covenant: Covenant) -> dict[str, SectionOps]:
    return {WHEREABOUTS_SECTION: ops(saga, covenant)}


# -- Plan Route --


def _legs_shown(covenant: Covenant) -> int:
    return max(MOST_FEW_LEGS, len(covenant.route) + SPARE_LEGS)


def _leg_on(index: int) -> Callable[[dict[str, Any]], bool]:
    return lambda values: bool(values.get(f"leg_{index}"))


def route_fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    options = _choices(saga, covenant)
    fields = [
        DialogField(
            "_how",
            "",
            "info",
            "Each leg in order, with the seasons to stay there. Advance "
            "Season offers the next one; what really happens is logged as a "
            "stop, so this plan never changes the log.",
        ),
        DialogField(
            "circuit",
            "Circuit",
            "check",
            covenant.circuit,
            hint="After the last leg it goes back to the first.",
        ),
    ]
    for index in range(_legs_shown(covenant)):
        leg = covenant.route[index] if index < len(covenant.route) else None
        fields += [
            DialogField(
                f"leg_{index}",
                f"Leg {index + 1}",
                "select",
                places.where_value(leg.place_id, leg.level) if leg else None,
                options=options,
                allow_blank=True,
                placeholder="(none)",
            ),
            DialogField(
                f"seasons_{index}",
                f"Seasons at leg {index + 1}",
                "int",
                leg.seasons if leg else 1,
                show_if=_leg_on(index),
            ),
        ]
    return fields


def route_problem(covenant: Covenant) -> Callable[[dict[str, Any]], str | None]:
    def problem(values: dict[str, Any]) -> str | None:
        for index in range(_legs_shown(covenant)):
            if values.get(f"leg_{index}") and (values.get(f"seasons_{index}") or 0) < 1:
                return f"Leg {index + 1} needs a season at least."
        return None

    return problem


def plan_route(saga: Saga, covenant: Covenant) -> Form:
    """More's Plan Route on Whereabouts."""

    def apply(values: dict[str, Any]) -> list[str]:
        route: list[RouteStop] = []
        for index in range(_legs_shown(covenant)):
            place_id, level = places.split(values.get(f"leg_{index}"))
            if place_id is not None:
                route.append(
                    RouteStop(place_id, level, int(values.get(f"seasons_{index}") or 1))
                )
        if route != covenant.route:
            covenant.route_at = 0
        covenant.route = route
        covenant.circuit = bool(values.get("circuit"))
        if not route:
            return notes(f"{escape(covenant.name)} has no route now.")
        return notes(f"Route: {route_text(saga, covenant)}")

    return Form(
        f"{ROUTE_TITLE}: {escape(covenant.name)}",
        lambda: route_fields(saga, covenant),
        apply,
        validate=route_problem(covenant),
        help_id=HELP_ID,
    )


# -- what Advance Season asks --


@dataclass(frozen=True)
class Asked:
    """What Advance Season asks about: a covenant, or one of its ships
    apart from the fleet (`record`)."""

    covenant: Covenant
    record: Possession | None = None

    @property
    def stops(self) -> list[CovenantStop]:
        ship = self.record.ship if self.record is not None else None
        return ship.stops if ship is not None else self.covenant.stops

    @property
    def name(self) -> str:
        if self.record is not None:
            return f"{self.record.name} of {self.covenant.name}"
        return self.covenant.name


def apart(covenant: Covenant) -> list[Possession]:
    """Its ships apart from the fleet."""
    return [r for r in ship_rules.ships_of(covenant) if ship_rules.ship_of(r).stops]


def _next_date(saga: Saga) -> tuple[str, int]:
    return next_season(saga.current_season, saga.current_year)


def asked(saga: Saga) -> list[Asked]:
    """Each player covenant on the move and each of its ships apart, but
    those with a stop already logged for the coming season."""
    season, year = _next_date(saga)

    def open_to(stops: list[CovenantStop]) -> bool:
        return not any((s.year, s.season) == (year, season) for s in stops)

    found: list[Asked] = []
    for covenant in saga.covenants:
        if not covenant.played:
            continue
        if shows(covenant) and open_to(covenant.stops):
            found.append(Asked(covenant))
        found += [
            Asked(covenant, record)
            for record in apart(covenant)
            if open_to(ship_rules.ship_of(record).stops)
        ]
    return found


def _here(saga: Saga, entry: Asked) -> tuple[str | None, int]:
    if entry.record is None:
        return _at(saga, entry.covenant)
    stop = mobile.stop_in_force(entry.stops, saga.current_year, saga.current_season)
    return (stop.place_id, stop.level) if stop is not None else (None, 0)


def _answers(saga: Saga, entry: Asked) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    place_id, level = _here(saga, entry)
    if entry.record is None:
        leg = mobile.next_leg_from(entry.covenant, place_id, level)
        if leg is not None:
            words = places.where_text(saga, leg.place_id, leg.level)
            found.append((f"Move on to {escape(words)}", MOVE_ON))
    here = places.where_text(saga, place_id, level)
    if here:
        found.append((f"Stay at {escape(here)}", STAY))
    if sites.all_places(saga):
        found.append(("Go somewhere else", ELSEWHERE))
    return found


def _due_to_move(saga: Saga, covenant: Covenant) -> bool:
    """Whether it has stayed as long as its route planned."""
    stop = sites.covenant_stop(saga, covenant)
    if stop is None:
        return True
    leg = mobile.next_leg(covenant)
    at_leg = leg is not None and (leg.place_id, leg.level) == _at(saga, covenant)
    planned = (
        leg.seasons if leg is not None and at_leg else mobile.planned_stay(covenant)
    )
    return mobile.seasons_here(covenant.stops, stop) >= planned


def _default(saga: Saga, entry: Asked, answers: list[tuple[str, str]]) -> str:
    values = [value for _, value in answers]
    if MOVE_ON in values and _due_to_move(saga, entry.covenant):
        return MOVE_ON
    return STAY if STAY in values else values[0]


def _ask_fields(
    saga: Saga, found: list[tuple[Asked, list[tuple[str, str]]]]
) -> list[DialogField]:
    fields: list[DialogField] = [
        DialogField(
            "_why",
            "",
            "info",
            "Where does each go for the coming season? The answer is logged as a stop.",
        )
    ]
    for index, (entry, answers) in enumerate(found):
        fields.append(
            DialogField(
                f"what_{index}",
                escape(entry.name),
                "select",
                _default(saga, entry, answers),
                options=answers,
            )
        )

        def elsewhere(values: dict[str, Any], index: int = index) -> bool:
            return values.get(f"what_{index}") == ELSEWHERE

        fields.append(
            DialogField(
                f"where_{index}",
                f"Where {escape(entry.name)} goes",
                "select",
                None,
                options=_choices(saga, entry.covenant),
                allow_blank=True,
                placeholder="(choose a Place from The Region)",
                show_if=elsewhere,
            )
        )
    return fields


#: What Advance Season keeps of the answers, to log once the date moves.
Moves = tuple[tuple[Asked, str, str | None], ...]


def season_step(saga: Saga, then: Callable[[Moves], Any]) -> Any:
    """Ask where each goes next, then `then(answers)`; they are logged
    once the season has been played (log_moves)."""
    found = [
        (entry, answers) for entry in asked(saga) if (answers := _answers(saga, entry))
    ]
    if not found:
        return then(())

    def problem(values: dict[str, Any]) -> str | None:
        for index, (entry, _answers_) in enumerate(found):
            wanted = values.get(f"what_{index}") == ELSEWHERE
            if wanted and not values.get(f"where_{index}"):
                return f"Choose where {entry.name} goes."
        return None

    def apply(values: dict[str, Any]) -> Any:
        return then(
            tuple(
                (entry, values.get(f"what_{i}") or STAY, values.get(f"where_{i}"))
                for i, (entry, _answers_) in enumerate(found)
            )
        )

    return Form(
        ASK_TITLE,
        lambda: _ask_fields(saga, found),
        apply,
        validate=problem,
        save_label="Continue",
        help_id=HELP_ID,
    )


def _log_covenant(saga: Saga, entry: Asked, what: str, where: str | None) -> list[str]:
    covenant = entry.covenant
    year, season = saga.current_year, saga.current_season
    if what == MOVE_ON:
        here = _at(saga, covenant)
        leg = mobile.next_leg_from(covenant, *here)
        if leg is None:
            return []
        mobile.step_past_here(covenant, *here)
        mobile.step_route(covenant)
        return _log_stop(
            saga, covenant, CovenantStop(year, season, leg.place_id, leg.level)
        )
    if what == ELSEWHERE:
        place_id, level = places.split(where)
        if place_id is None:
            return []
        return _log_stop(saga, covenant, CovenantStop(year, season, place_id, level))
    previous = mobile.stop_in_force(covenant.stops, year, season)
    if previous is not None:
        _log_stop(
            saga,
            covenant,
            CovenantStop(year, season, previous.place_id, previous.level),
        )
    refused = aegis_refused(saga, covenant)
    return _aegis_lost(covenant, year, season, refused) if refused else []


def _log_ship(saga: Saga, ship: Ship, what: str, where: str | None) -> None:
    year, season = saga.current_year, saga.current_season
    if what == ELSEWHERE:
        place_id, level = places.split(where)
        if place_id is not None:
            ship.stops.append(CovenantStop(year, season, place_id, level))
    else:
        previous = mobile.stop_in_force(ship.stops, year, season)
        if previous is not None:
            ship.stops.append(
                CovenantStop(year, season, previous.place_id, previous.level)
            )
    mobile.date_order(ship.stops)


def log_moves(saga: Saga, moves: Moves) -> list[str]:
    """Log Advance Season's answers, dated the new season; then make every
    aura right for the new date, stops already planned for it included."""
    lines: list[str] = []
    for entry, what, where in moves:
        if entry.record is None:
            lines += _log_covenant(saga, entry, what, where)
        else:
            _log_ship(saga, ship_rules.ship_of(entry.record), what, where)
    places.sync(saga)
    return lines


# -- a ship leaving the fleet --


def _chosen(covenant: Covenant, index: int | None) -> Possession | None:
    listed = ship_rules.ships_of(covenant)
    return listed[index] if index is not None and 0 <= index < len(listed) else None


def can_detach(covenant: Covenant, index: int | None) -> bool:
    record = _chosen(covenant, index)
    if record is None:
        return False
    ship = ship_rules.ship_of(record)
    return not ship.stops and not ship_rules.lost(ship)


def can_rejoin(covenant: Covenant, index: int | None) -> bool:
    record = _chosen(covenant, index)
    return record is not None and bool(ship_rules.ship_of(record).stops)


def magi_aboard(saga: Saga, covenant: Covenant, record: Possession) -> list[Character]:
    """Who works in the ship's laboratory: the magi her Detach asks about."""
    if record.lab_id is None:
        return []
    return [
        c
        for c in saga.characters
        if c.covenant_id == covenant.id and c.assigned_lab_id == record.lab_id
    ]


def detach_fields(
    saga: Saga, covenant: Covenant, record: Possession
) -> list[DialogField]:
    fields = [
        DialogField(
            "where",
            "She goes to",
            "select",
            None,
            options=_choices(saga, covenant),
            required=True,
            allow_blank=True,
            placeholder="(choose a Place from The Region)",
        ),
        DialogField("note", "Note", "text", ""),
    ]
    for magus in magi_aboard(saga, covenant, record):
        fields.append(
            DialogField(
                f"goes_{magus.id}",
                f"{escape(magus.name)} travels with this ship",
                "check",
                True,
                hint="Untick to stay with the fleet: his laboratory goes without him.",
            )
        )
    return fields


def detach_form(saga: Saga, covenant: Covenant, index: int | None) -> Command:
    """More's Detach on the chosen ship: she sails on her own, still of
    the covenant; her laboratory and those who go with her take their
    aura from her stops."""
    record = _chosen(covenant, index)
    if record is None:
        return Refuse(DETACH_TITLE, "Choose a ship first.")
    if not can_detach(covenant, index):
        return Refuse(DETACH_TITLE, f"{escape(record.name)} can't leave the fleet now.")
    ship = ship_rules.ship_of(record)

    def apply(values: dict[str, Any]) -> list[str]:
        place_id, level = places.split(values.get("where"))
        assert place_id is not None
        year, season = saga.current_year, saga.current_season
        ship.stops = [
            CovenantStop(
                year, season, place_id, level, (values.get("note") or "").strip()
            )
        ]
        ship.aboard = [
            m.id
            for m in magi_aboard(saga, covenant, record)
            if values.get(f"goes_{m.id}")
        ]
        record.ship = ship
        where = places.where_text(saga, place_id, level)
        diaries.write(
            year,
            season,
            f"{DETACH_TITLE}: {record.name}",
            f"{record.name} left the fleet for {where}.",
            covenants=[covenant],
        )
        return notes(f"{escape(record.name)} left the fleet for {escape(where)}.")

    def problem(values: dict[str, Any]) -> str | None:
        return None if values.get("where") else "Choose where she goes."

    return Form(
        f"{DETACH_TITLE}: {escape(record.name)}",
        lambda: detach_fields(saga, covenant, record),
        apply,
        validate=problem,
        save_label=DETACH_TITLE,
        help_id=HELP_ID,
    )


def rejoin_form(saga: Saga, covenant: Covenant, index: int | None) -> Command:
    """More's Rejoin on the chosen ship apart from the fleet."""
    record = _chosen(covenant, index)
    if record is None:
        return Refuse(REJOIN_TITLE, "Choose a ship first.")
    if not can_rejoin(covenant, index):
        return Refuse(
            REJOIN_TITLE, f"{escape(record.name)} sails with the fleet already."
        )
    ship = ship_rules.ship_of(record)

    def apply() -> list[str]:
        ship.stops, ship.aboard = [], []
        record.ship = ship
        diaries.write(
            saga.current_year,
            saga.current_season,
            f"{REJOIN_TITLE}: {record.name}",
            f"{record.name} rejoined the fleet.",
            covenants=[covenant],
        )
        return notes(f"{escape(record.name)} rejoined the fleet.")

    return Confirm(
        f"Bring {escape(record.name)} back to the fleet?",
        apply,
        yes_label=REJOIN_TITLE,
        title=REJOIN_TITLE,
    )
