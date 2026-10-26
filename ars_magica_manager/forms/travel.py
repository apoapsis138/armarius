"""The Travel calculator, independent of how it is drawn: a form of the
route, the means and the party, with an inspector, The Journey, that
works out the days, the cost and the Fatigue of hurrying as the user
types. It ends two ways: Close leaves it as a what-if, recording nothing;
Set Out makes the journey, in one click, for those who go: a line in each
traveller's Diary, the forced march's Long-Term Fatigue on each (with
Travel quickly), and the arrival in the saga's calendar, for Ahead.

The figures and their pages are rules/journeys.py's; this module words
them.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import diaries
from .. import goods as gd
from ..commands import Choice, Choose, Form, Picked, notes
from ..form_spec import DialogField, ListEditor
from ..markup import escape
from ..models import CalendarEntry, Character, Covenant, Saga
from ..rules import harm
from ..rules import journeys as tr

CG = tr.CG
#: The form's own help page.
HELP_ID = "travel"


def places(saga: Saga) -> list[tuple[str, str]]:
    """What From and To offer: the saga's covenants, then its towns and
    places, each by name."""
    covenants = sorted((c.name, c.id) for c in saga.covenants if c.name)
    others = sorted(
        (n.name, n.id)
        for n in saga.neighbours
        if n.kind in ("town", "place") and n.name
    )
    return [(escape(name), value) for name, value in (*covenants, *others)]


def _place_name(saga: Saga, value: str | None) -> str:
    if not value:
        return ""
    covenant = saga.covenant(value)
    if covenant is not None:
        return covenant.name
    neighbour = saga.neighbour(value)
    return neighbour.name if neighbour is not None else ""


def _measure(values: dict[str, Any]) -> str:
    return values.get("measure") or tr.DIRECT


def _by_distance(values: dict[str, Any]) -> bool:
    return _measure(values) != tr.PORTS


def _can_hurry(values: dict[str, Any]) -> bool:
    means = tr.MEANS.get(values.get("means") or "")
    return _by_distance(values) and means is not None and means.on_land


def _character_name(saga: Saga, character_id: str) -> str:
    character = saga.character(character_id)
    return character.name if character is not None else "(gone)"


def traveller_name(saga: Saga) -> Callable[[str], str]:
    """A traveller's name from their id, as Who goes lists them."""
    return lambda character_id: _character_name(saga, character_id)


def choose_traveller(saga: Saga, title: str = "Who Goes") -> Callable[[Any], Choose]:
    """Who goes's chooser (and The Hunt's): one of the saga's characters."""

    def choose(_current: Any = None) -> Choose:
        return Choose(
            title,
            lambda: [
                Choice(escape(c.name), c.id)
                for c in sorted(saga.characters, key=lambda c: c.name)
                if c.name
            ],
            Picked,
            empty="The saga has no characters.",
        )

    return choose


def _follows_who(start: int = 0) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Travellers follows Who goes: each one named or taken off counts one
    more or one fewer, and the count never falls below those named, so
    unnamed others can still be counted."""
    named = [start]

    def fills(values: dict[str, Any]) -> dict[str, Any]:
        now = len(values.get("who") or [])
        counted = (values.get("travellers") or 0) + now - named[0]
        named[0] = now
        return {"travellers": max(counted, now)}

    return fills


def travel_fields(saga: Saga, start: str | None = None) -> list[DialogField]:
    """The form: where from and to, how the distance is measured, the
    miles and the means (or two named ports), who goes, the party and its
    cargo."""
    offered = places(saga)
    ports = [(escape(port), port) for port in tr.PORTS_LISTED]
    name = traveller_name(saga)
    return [
        DialogField(
            "start", "From", "select", start, options=offered, allow_blank=True
        ),
        DialogField("end", "To", "select", None, options=offered, allow_blank=True),
        DialogField(
            "measure",
            "Measured",
            "select",
            tr.DIRECT,
            options=[(label, key) for key, label in tr.MEASURES.items()],
        ),
        DialogField(
            "miles",
            "Miles",
            "optint",
            None,
            hint="The saga keeps no distances: measure them on the troupe's map.",
            show_if=_by_distance,
        ),
        DialogField(
            "means",
            "By",
            "select",
            "foot",
            options=[(m.label, key) for key, m in tr.MEANS.items()],
            show_if=_by_distance,
        ),
        DialogField(
            "start_port",
            "Port of departure",
            "select",
            None,
            options=ports,
            allow_blank=True,
            show_if=lambda values: not _by_distance(values),
        ),
        DialogField(
            "end_port",
            "Port of arrival",
            "select",
            None,
            options=ports,
            allow_blank=True,
            show_if=lambda values: not _by_distance(values),
        ),
        DialogField(
            "who",
            "Who goes",
            "picker",
            [],
            display=lambda chosen: (
                "; ".join(name(c) for c in chosen) or "(no one named)"
            ),
            items=ListEditor(name, choose_traveller(saga), "Who Goes"),
            fills=_follows_who(),
            hint="The saga's characters who set out; Travellers counts them.",
        ),
        DialogField(
            "travellers",
            "Travellers",
            "int",
            0,
            hint="Those named and any others. Eight take about a ton of a ship's "
            f"space with their food ({CG} p. 85).",
        ),
        DialogField("cargo", "Cargo, in tons", "optfloat", None),
        DialogField(
            "known_magus",
            "A known magus travels",
            "check",
            False,
            hint=f"Sailors think a wizard aboard bad luck: known magi pay double "
            f"({CG} p. 85).",
        ),
        DialogField(
            "quick",
            "Travel quickly",
            "check",
            False,
            hint="A forced march: Long-Term Fatigue each day (DE p. 408).",
            show_if=_can_hurry,
        ),
    ]


def journey_of(values: dict[str, Any]) -> tr.Journey | None:
    """The journey the form's values describe, as rules/journeys.py works
    it out; None while there isn't enough to go on."""
    return tr.journey(
        values.get("means"),
        values.get("miles"),
        _measure(values),
        travellers=values.get("travellers") or 0,
        cargo=values.get("cargo") or 0.0,
        known_magus=bool(values.get("known_magus")),
        quick=bool(values.get("quick")) and _can_hurry(values),
        start_port=values.get("start_port"),
        end_port=values.get("end_port"),
    )


def _span(days: tuple[int, int]) -> str:
    fewest, most = days
    return f"{fewest}" if fewest == most else f"{fewest} to {most}"


def _tons(tons: float) -> str:
    """A weight in tons: "1 ton", "3 tons", "0.25 tons"."""
    shown = f"{tons:,.0f}" if tons >= 10 or tons == int(tons) else f"{tons:.2g}"
    return f"{shown} ton" if shown == "1" else f"{shown} tons"


def money(pence: float) -> str:
    """A sum of pence as the app writes money in full, to the penny."""
    if pence < 1:
        return "less than a penny"
    return gd.pounds_shillings_pence(round(pence))


def _cost_lines(journey: tr.Journey, travellers: int, cargo: float) -> list[str]:
    means = journey.means
    if journey.cost_pence is None:
        return [
            "Cost: [b]no figure in the book[/] [dim]for travelling on foot or on "
            f"your own horses: food, tools and lodging have no rate ({CG} p. 86)[/]"
        ]
    low, high = journey.cost_pence
    sums = money(low) if money(low) == money(high) else f"{money(low)} to {money(high)}"
    kind = means.kind if means is not None else tr.SEA
    basis = {
        tr.SEA: "sea travel, a pound a ton of space a fortnight",
        tr.RIVER: "river travel costs twice sea travel",
    }.get(kind, "road travel costs 8 to 20 times sea travel")
    to_the_ton = (
        "16 to the ton hugging the coast"
        if means is not None and means.space_for_eight < 1
        else "8 to the ton with their food"
    )
    party = f"{travellers} traveller{'s' if travellers != 1 else ''}, {to_the_ton}"
    if cargo:
        party += f", + {_tons(cargo)} of cargo"
    lines = [
        f"Cost: about [b]{sums}[/] [dim]for {_tons(journey.space_tons)} of space "
        f"({party}) over {_span(journey.days)} days; {basis} ({CG} pp. 85-86)[/]"
    ]
    if journey.known_magus_doubled:
        lines.append(
            "[dim]A known magus pays double for passage, and only a captain "
            f"desperate enough to risk his ship will take him ({CG} p. 85).[/]"
        )
    return lines


def _fatigue_lines(journey: tr.Journey) -> list[str]:
    fatigue = journey.fatigue
    means = journey.means
    if fatigue is None:
        if means is not None and means.on_land:
            return [
                "[dim]Travelling quickly would cost one Long-Term Fatigue level "
                "a day (DE p. 408).[/]"
            ]
        return []
    day, level = fatigue.by_day[-1]
    reached = (
        f"Unconscious on day {fatigue.unconscious_on}"
        if fatigue.unconscious_on is not None
        else f"{level} by day {day}"
    )
    return [
        "[$text-error]Forced march: one Long-Term Fatigue level a day on the road, "
        f"{fatigue.days} in all: {reached}[/] [dim](DE p. 408)[/]",
        f"[dim]The app's reading: each night's rest without hurrying restores one "
        f"level, so {fatigue.nights_to_recover} nights to be Fresh again (DE "
        "p. 404). Delays for terrain or weather still cost the level; waiting on "
        "toll collectors doesn't.[/]",
    ]


def travel_live(saga: Saga) -> Callable[[dict[str, Any]], str]:
    """The Journey: the days, how they were worked out, the books' words,
    the rough guide, the cost and the Fatigue of hurrying."""

    def live(values: dict[str, Any]) -> str:
        start = _place_name(saga, values.get("start"))
        end = _place_name(saga, values.get("end"))
        by_distance = _by_distance(values)
        means = tr.MEANS.get(values.get("means") or "") if by_distance else None
        how = means.label if means is not None else "By sea, by the Naval Trade Tables"
        lines = []
        if start or end:
            lines.append(
                f"[b]{escape(start or '?')} to {escape(end or '?')}[/]  [$label]{how}[/]"
            )
        else:
            lines.append(f"[b]{how}[/]")
        journey = journey_of(values)
        if journey is None:
            if not by_distance:
                lines.append(
                    "[$text-error]Choose two ports in the Naval Trade Tables "
                    f"({CG} pp. 89-90).[/]"
                )
            else:
                lines.append(
                    "[$text-error]Give the distance in miles to work out the days.[/]"
                )
            return "\n".join(lines)
        lines.append(
            f"Days: [b]{_span(journey.days)}[/] [dim]= {escape(journey.working)}[/]"
        )
        if means is not None:
            lines.append(f"[i]{CG}: {escape(means.words)}.[/]")
            if journey.guide_days is not None and means.speed_source != "DE p. 408":
                guide = f"about {journey.guide_days} days ({means.guide_words})"
            else:
                guide = means.guide_words
            lines.append(f"[dim]Rough guide, DE p. 408: {escape(guide)}.[/]")
        else:
            lines.append(
                f"[i]{CG}: the tables' days include the journey inland from the port "
                "to the named city.[/]"
            )
        travellers = max(values.get("travellers") or 0, 0)
        cargo = max(values.get("cargo") or 0.0, 0.0)
        lines.extend(_cost_lines(journey, travellers, cargo))
        lines.extend(_fatigue_lines(journey))
        season, year = tr.arrival(
            saga.current_season, saga.current_year, journey.days[1]
        )
        who = [_character_name(saga, c) for c in values.get("who") or []]
        setting_out = escape(", ".join(who)) if who else "name who goes first"
        lines.append(f"[dim]Set Out: {setting_out}; arriving {season} {year}.[/]")
        return "\n".join(lines)

    return live


def travel_problem(values: dict[str, Any]) -> str | None:
    """Why Set Out refuses: a figure below nothing, no one named, or not
    enough to work the journey out. (Close never refuses.)"""
    if _by_distance(values) and (values.get("miles") or 0) < 0:
        return "Miles can't be below 0."
    if (values.get("travellers") or 0) < 0:
        return "Travellers can't be below 0."
    if (values.get("cargo") or 0) < 0:
        return "Cargo can't be below 0 tons."
    if not values.get("who"):
        return "Name who goes to set out, or Close to leave it as a what-if."
    if journey_of(values) is None:
        if _by_distance(values):
            return "Give the distance in miles to set out."
        return "Choose two ports the Naval Trade Tables join to set out."
    return None


def _ends(saga: Saga, values: dict[str, Any]) -> tuple[str, str]:
    """Where the journey starts and ends, by name ("" for neither)."""
    start = _place_name(saga, values.get("start")) or values.get("start_port") or ""
    end = _place_name(saga, values.get("end")) or values.get("end_port") or ""
    return start, end


def _cost_text(journey: tr.Journey) -> str:
    if journey.cost_pence is None:
        return ""
    low, high = journey.cost_pence
    return money(low) if money(low) == money(high) else f"{money(low)} to {money(high)}"


def journey_text(saga: Saga, values: dict[str, Any], journey: tr.Journey) -> str:
    """The Diary's line for the journey: where, how, how long, the cost."""
    start, end = _ends(saga, values)
    how = journey.means.label if journey.means is not None else "By sea"
    text = (
        f"From {start or 'home'} to {end or 'their destination'}, "
        f"{how[0].lower()}{how[1:]}: {_span(journey.days)} days"
    )
    cost = _cost_text(journey)
    if cost:
        text += f", about {cost} for passage"
    if journey.fatigue is not None:
        lost = journey.fatigue.levels_lost
        text += f"; a forced march, {lost} Long-Term Fatigue level{'s' if lost != 1 else ''} lost"
    return text + "."


def set_out(
    saga: Saga, values: dict[str, Any], covenant: Covenant | None = None
) -> list[str]:
    """Make the journey: a line in each traveller's Diary, the forced
    march's Long-Term Fatigue on each (one level a day, DE p. 408), and
    the arrival in the saga's calendar, where Ahead shows it."""
    journey = journey_of(values)
    if journey is None:
        return notes("Not enough to set out on: nothing was recorded.")
    travellers: list[Character] = [
        c for c in (saga.character(i) for i in values.get("who") or []) if c is not None
    ]
    text = journey_text(saga, values, journey)
    season, year = saga.current_season, saga.current_year
    diaries.write(year, season, "Travel", text, characters=travellers)
    if journey.fatigue is not None:
        for traveller in travellers:
            for _ in range(journey.fatigue.levels_lost):
                if harm.lose_fatigue(traveller, long_term=True):
                    break
    _start, end = _ends(saga, values)
    at, when = tr.arrival(season, year, journey.days[1])
    names = ", ".join(c.name for c in travellers)
    one = len(travellers) == 1
    saga.calendar.append(
        CalendarEntry(
            f"{names} arrive{'s' if one else ''}" + (f" at {end}" if end else ""),
            when,
            at,
            note=text,
            covenant_id=covenant.id if covenant is not None else None,
        )
    )
    return notes(
        f"{escape(names)} set{'s' if one else ''} out. {escape(text)}",
        f"Arriving {at} {when}: on Ahead.",
    )


def travel(saga: Saga, covenant: Covenant | None = None) -> Form:
    """The Travel calculator, From the covenant on show if any: Close
    leaves it as a what-if, Set Out makes the journey."""
    return Form(
        "Travel",
        lambda: travel_fields(saga, covenant.id if covenant is not None else None),
        lambda values: set_out(saga, values, covenant),
        validate=travel_problem,
        live=travel_live(saga),
        save_label="Set Out",
        cancel_label="Close",
        help_id=HELP_ID,
        inspector="The Journey",
    )
