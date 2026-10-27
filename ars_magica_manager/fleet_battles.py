"""A Battle fought at sea, between fleets (Tales of Power pp. 106-110):
the fields the Battle and Battle Event forms gain at sea, what their
inspectors say, and the lines a fleet battle adds to its page. No UI in
here; the rules are rules.fleet_battle's, the battle itself battles'.

Each side's ships are the covenant's ship Possessions (rules.ships) it
picks, plus a count of others kept on no covenant's Possessions. Weight
of Numbers counts ships: all of them for the battle, only those engaged
for an event.

Pattern: the same Battle record and forms, with fields shown only at sea
(each DialogField's show_if), so a fleet battle is a Battle, not a second
kind of record beside it.
"""

from __future__ import annotations

from typing import Any

from .form_spec import DialogField
from .markup import escape
from .models import Battle, BattleEvent, BattleSide, Character, Possession, Saga
from .rules import battle, fleet_battle
from .rules import ships as ship_rules

#: How a battle's form names the record a side is linked to.
COVENANT, NEIGHBOUR = "covenant:", "neighbour:"
LAND, SEA = "land", "sea"
SIDE_LABELS = ("First army", "Second army")


def _at_sea(values: dict[str, Any]) -> bool:
    return values.get("fought") == SEA


# -- a side's ships --


def ship_records(saga: Saga, side: BattleSide) -> list[Possession]:
    """The side's ships from its covenant's Possessions, in their order
    there (a ship since removed is left out)."""
    covenant = saga.covenant(side.covenant_id)
    if covenant is None:
        return []
    return [p for p in ship_rules.ships_of(covenant) if p.id in side.ships]


def afloat(saga: Saga, side: BattleSide) -> list[Possession]:
    """Its ships not wrecked."""
    return [
        p
        for p in ship_records(saga, side)
        if not ship_rules.wrecked(ship_rules.ship_of(p))
    ]


def ship_count(saga: Saga, side: BattleSide) -> int:
    return len(afloat(saga, side)) + side.other_ships


def men(records: list[Possession]) -> int:
    """The crews and fighting men of these ships."""
    return sum(
        ship_rules.crew(ship_rules.ship_of(p))
        + ship_rules.fighting_men(ship_rules.ship_of(p))
        for p in records
    )


def weight(saga: Saga, sides: list[BattleSide], side: int) -> int:
    """`side`'s Weight of Numbers by every ship of both fleets."""
    return battle.weight_of_numbers(
        ship_count(saga, sides[side]), ship_count(saga, sides[1 - side])
    )


def pilot_words(character: Character | None) -> str:
    """ "Int +1, Profession: Sailor 6": what the pilot brings."""
    if character is None:
        return "no pilot named"
    name, score = ship_rules.profession(character)
    return f"Int {character.characteristics.intelligence:+d}, {name} {score}"


def pilot_base(character: Character | None) -> int:
    if character is None:
        return 0
    _name, score = ship_rules.profession(character)
    return fleet_battle.deployment_base(character.characteristics.intelligence, score)


def _seafarers(saga: Saga) -> list[Character]:
    """Characters with a seafaring Profession, who can pilot."""
    return [
        c
        for c in saga.characters
        if ship_rules.profession(c) != (ship_rules.DEFAULT_PROFESSION, 0)
    ]


def _ship_label(record: Possession) -> str:
    ship = ship_rules.ship_of(record)
    crew = ship_rules.crew(ship) + ship_rules.fighting_men(ship)
    kind = (ship.kind_name or "ship").lower()
    return f"{record.name or '(unnamed)'}, {kind}, {crew} men"


def _ship_key(index: int, record: Possession) -> str:
    return f"ship_{index}_{record.id}"


# -- the battle's form --


def fought_field(entry: Battle) -> DialogField:
    return DialogField(
        "fought",
        "Fought",
        "select",
        SEA if entry.at_sea else LAND,
        options=[("On land", LAND), ("At sea: a fleet battle", SEA)],
        required=True,
        hint="At sea, Weight of Numbers counts ships and a pilot sets the "
        "Deployment (Tales of Power p. 106).",
    )


def side_fields(saga: Saga, side: BattleSide, index: int) -> list[DialogField]:
    """A side's fleet: each ship its covenant keeps (shown when that
    covenant is the side), its other ships, its pilot and its bearding."""
    label = SIDE_LABELS[index]
    army_key = f"army_{index}"
    found: list[DialogField] = []
    for covenant, record in ship_rules.saga_ships(saga):

        def shown(values: dict[str, Any], cid: str = covenant.id) -> bool:
            return _at_sea(values) and values.get(army_key) == COVENANT + cid

        found.append(
            DialogField(
                _ship_key(index, record),
                _ship_label(record),
                "check",
                record.id in side.ships
                if side.ships
                else not ship_rules.wrecked(ship_rules.ship_of(record)),
                show_if=shown,
            )
        )
    pilots = _seafarers(saga)
    current = saga.character(side.pilot_id)
    if current is not None and current not in pilots:
        pilots.append(current)
    found += [
        DialogField(
            f"other_ships_{index}",
            f"{label}'s other ships",
            "int",
            side.other_ships,
            hint="Ships kept on no covenant's Possessions: an enemy's fleet, "
            "or ships hired.",
            show_if=_at_sea,
        ),
        DialogField(
            f"pilot_{index}",
            f"{label}'s pilot",
            "select",
            side.pilot_id,
            options=[
                ("(none)", ""),
                *((escape(f"{c.name}: {pilot_words(c)}"), c.id) for c in pilots),
            ],
            hint="Intelligence + his seafaring Profession + stress die is the "
            "Deployment Total: the pilot's Ability in place of Area Lore (Tales "
            "of Power p. 106).",
            show_if=_at_sea,
        ),
        DialogField(
            f"bearded_{index}",
            f"{label}'s ships bearded",
            "check",
            side.bearded,
            hint="Iron plates on the bows: slower, but armoured, more "
            "resistant to damage, and better at ramming and taking collisions; "
            "the storyguide sets the bonus (Tales of Power pp. 106, 110).",
            show_if=_at_sea,
        ),
    ]
    return found


def picked(saga: Saga, values: dict[str, Any], index: int) -> list[Possession]:
    """The ships the form has ticked for side `index`: only those of the
    covenant the side is linked to count."""
    linked = values.get(f"army_{index}")
    return [
        record
        for covenant, record in ship_rules.saga_ships(saga)
        if linked == COVENANT + covenant.id and values.get(_ship_key(index, record))
    ]


def write(
    saga: Saga, entry: Battle, sides: list[BattleSide], values: dict[str, Any]
) -> None:
    """The fleet fields into the battle (after battles' own); at sea, a
    side whose combat groups were left blank gets its crews'."""
    entry.at_sea = _at_sea(values)
    for index in range(2):
        side = sides[index]
        if not entry.at_sea:
            continue
        records = picked(saga, values, index)
        side.ships = [p.id for p in records]
        side.other_ships = int(values.get(f"other_ships_{index}") or 0)
        side.pilot_id = str(values.get(f"pilot_{index}") or "")
        side.bearded = bool(values.get(f"bearded_{index}"))
        if values.get(f"groups_{index}") is None and records:
            side.groups = fleet_battle.crew_groups(men(records))
            if values.get(f"baggage_{index}") is None:
                side.baggage = battle.baggage_needed(side.groups)


def problem(saga: Saga, values: dict[str, Any]) -> str | None:
    if not _at_sea(values):
        return None
    for index in range(2):
        other = values.get(f"other_ships_{index}") or 0
        if other < 0:
            return "Ships can't be fewer than none."
        if len(picked(saga, values, index)) + other == 0:
            return (
                f"A fleet battle needs ships on both sides: the {SIDE_LABELS[index].lower()} "
                "has none."
            )
    return None


def _ships(count: int) -> str:
    return f"{count} ship" + ("" if count == 1 else "s")


def _count(saga: Saga, values: dict[str, Any], index: int) -> int:
    return len(picked(saga, values, index)) + int(
        values.get(f"other_ships_{index}") or 0
    )


def battle_live(saga: Saga, values: dict[str, Any]) -> str:
    """The Edit Battle inspector: at sea, the Weight of Numbers by ships,
    the crews as combat groups, the pilots' Deployment, the bearding."""
    if not _at_sea(values):
        first, second = values.get("groups_0"), values.get("groups_1")
        if first is None or second is None:
            return (
                "On land: Weight of Numbers by the armies' combat groups; a "
                "lord's left blank are his title's army (Lords of Men p. 105)."
            )
        return (
            f"On land: {first} combat groups against {second}, Weight of "
            f"Numbers {battle.weight_of_numbers(first, second):+d} for the first "
            "army (Lords of Men p. 105)."
        )
    ours, theirs = _count(saga, values, 0), _count(saga, values, 1)
    lines = [
        f"[b]{_ships(ours)} against {theirs}[/]: Weight of Numbers "
        f"{battle.weight_of_numbers(ours, theirs):+d} for the first army while "
        "all are in the fight; later only the ships engaged count (ToP p. 106).",
    ]
    for index in range(2):
        records = picked(saga, values, index)
        crews = men(records)
        if records:
            lines.append(
                f"{SIDE_LABELS[index]}'s crews: {crews} men, "
                f"{fleet_battle.crew_groups(crews)} combat groups"
                + (
                    " (the groups left blank are filled in from them)."
                    if values.get(f"groups_{index}") is None
                    else "."
                )
            )
        pilot = saga.character(values.get(f"pilot_{index}"))
        if pilot is not None:
            name, score = ship_rules.profession(pilot)
            lines.append(
                f"[b]{SIDE_LABELS[index]}'s Deployment:[/] Int "
                f"{pilot.characteristics.intelligence:+d} + {escape(name)} {score} "
                f"= {pilot_base(pilot)} + stress die."
            )
    if values.get("bearded_0") or values.get("bearded_1"):
        lines.append(fleet_battle.BEARDED_NOTE)
    lines.append(f"[dim]{fleet_battle.BOARDING_NOTE}[/]")
    return "\n".join(lines)


# -- an event at sea --


def _previous(entry: Battle) -> BattleEvent | None:
    return next((e for e in reversed(entry.events) if e.deed), None)


def event_fields(
    saga: Saga, entry: Battle, sides: list[BattleSide]
) -> list[DialogField]:
    """What the event was at sea, the ships engaged in it (at first every
    ship; later those engaged last time), and naptha."""
    last = _previous(entry)
    found = [
        DialogField(
            "deed",
            "Event",
            "select",
            fleet_battle.FLEET_EVENT_DEFAULT,
            options=[(words, key) for key, words in fleet_battle.FLEET_EVENTS.items()],
            required=True,
            hint="Played as on land, told at sea (Tales of Power p. 106).",
        )
    ]
    for index in range(2):
        side = sides[index]
        for record in afloat(saga, side):
            found.append(
                DialogField(
                    f"eng_{record.id}",
                    f"Engaged: {record.name or '(unnamed)'}",
                    "check",
                    record.id in last.engaged_ships if last else True,
                )
            )
        if side.other_ships:
            found.append(
                DialogField(
                    f"eng_other_{index}",
                    f"Engaged: {SIDE_LABELS[index]}'s others",
                    "int",
                    last.engaged_other[index] if last else side.other_ships,
                    hint=f"Of its {side.other_ships} other ships.",
                )
            )
    found.append(
        DialogField(
            "naptha",
            "They throw naptha bombs",
            "check",
            False,
            hint="+5 damage, and the ship is set alight (Tales of Power p. 110).",
        )
    )
    return found


def engaged_ids(
    saga: Saga, sides: list[BattleSide], values: dict[str, Any]
) -> list[str]:
    return [
        record.id
        for side in sides[:2]
        for record in afloat(saga, side)
        if values.get(f"eng_{record.id}")
    ]


def engaged_other(sides: list[BattleSide], values: dict[str, Any]) -> list[int]:
    return [
        int(values.get(f"eng_other_{index}") or 0) if sides[index].other_ships else 0
        for index in range(2)
    ]


def engaged_counts(
    saga: Saga, sides: list[BattleSide], values: dict[str, Any]
) -> tuple[int, int]:
    """Ships engaged on each side (first, second)."""
    ids = set(engaged_ids(saga, sides, values))
    other = engaged_other(sides, values)
    first, second = (
        sum(1 for p in afloat(saga, sides[i]) if p.id in ids) + other[i]
        for i in range(2)
    )
    return first, second


def event_weight(
    saga: Saga, sides: list[BattleSide], values: dict[str, Any], side: int
) -> int:
    """`side`'s Weight of Numbers in this event: its engaged ships against
    the other's."""
    counts = engaged_counts(saga, sides, values)
    return battle.weight_of_numbers(counts[side], counts[1 - side])


def event_problem(sides: list[BattleSide], values: dict[str, Any]) -> str | None:
    for index in range(2):
        value = values.get(f"eng_other_{index}") or 0
        if value < 0 or value > sides[index].other_ships:
            return (
                f"The {SIDE_LABELS[index].lower()} has "
                f"{sides[index].other_ships} other ships to engage."
            )
    return None


def event_live(saga: Saga, sides: list[BattleSide], values: dict[str, Any]) -> str:
    """The lines an event at sea puts above the Event Total."""
    side = int(values.get("side") or 0)
    counts = engaged_counts(saga, sides, values)
    lines = [
        f"Engaged: {counts[side]} against {counts[1 - side]}: Weight of Numbers "
        f"[b]{event_weight(saga, sides, values, side):+d}[/] for this event (ToP p. 106)."
    ]
    if values.get("naptha"):
        lines.append(fleet_battle.NAPTHA_NOTE)
    return "\n".join(lines)


def event_words(event: BattleEvent) -> str:
    """ "Board their flagship, 2 ships against 1": an event at sea, for
    its line on the page and in the Diary ("" on land)."""
    if not event.deed:
        return ""
    words = fleet_battle.FLEET_EVENTS.get(event.deed, event.deed)
    return words + (", with naptha bombs" if event.naptha else "")


# -- the battle's page --


def side_line(saga: Saga, side: BattleSide) -> str:
    """ "Ships: Nebelkönigin, Seehund and 2 others (82 men); pilot Bjorn
    (Int +1, Profession: Sailor 6); bearded." (markup)."""
    records = ship_records(saga, side)
    names = [
        escape(p.name or "(unnamed)")
        + (" (wrecked)" if ship_rules.wrecked(ship_rules.ship_of(p)) else "")
        for p in records
    ]
    if side.other_ships:
        names.append(f"{side.other_ships} other{'s' if side.other_ships > 1 else ''}")
    listed = ", ".join(names) if names else "none"
    crews = men(afloat(saga, side))
    pilot = saga.character(side.pilot_id)
    return (
        f"  Ships: {listed}"
        + (f" ({crews} men)" if crews else "")
        + (
            f"; pilot {escape(pilot.name)} ({escape(pilot_words(pilot))})"
            if pilot is not None
            else ""
        )
        + ("; bearded" if side.bearded else "")
        + "."
    )
