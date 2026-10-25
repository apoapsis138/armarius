"""Battles between two armies (Lords of Men, Chapter Eight: Massed Combat):
each side a lord, covenant or other power of the Region (or just a name)
in combat groups of five, with its commander's Deployment Total and its
baggage, and the battlefield events played so far. The rules are
rules.battle's; this is the record and its forms.

A battle is kept once, in the saga's Conflicts, and each lord's Fief tab
lists the battles that name him, on either side. Pattern: one record
shown in several places (a filtered view over saga.battles), so the two
lords of a battle never hold copies that could disagree.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from . import armies, diaries
from .commands import Command, Confirm, Form, Refuse, SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import SEASONS, Battle, BattleEvent, BattleSide, Neighbour, Saga
from .rules import battle
from .rules.lab import ability_score

#: What a side can be: a covenant, or one of the Region's powers.
ARMY_KINDS = ("lord", "town", "threat", "faction", "church")
COVENANT, NEIGHBOUR = "covenant:", "neighbour:"


def sides(entry: Battle) -> list[BattleSide]:
    """The battle's two sides, made when it has fewer."""
    while len(entry.sides) < 2:
        entry.sides.append(BattleSide())
    return entry.sides


def side_name(saga: Saga, entry: Battle, index: int) -> str:
    """A side's name, its linked record's when it has none of its own."""
    side = sides(entry)[index]
    if side.name:
        return side.name
    record = saga.neighbour(side.neighbour_id) or saga.covenant(side.covenant_id)
    if record is not None:
        return record.name
    return ("The first army", "The second army")[min(index, 1)]


def involving(saga: Saga, neighbour: Neighbour) -> list[Battle]:
    """The battles that name `neighbour` on either side."""
    return [
        b for b in saga.battles if any(s.neighbour_id == neighbour.id for s in sides(b))
    ]


def weight(entry: Battle, side: int = 0) -> int:
    """`side`'s Weight of Numbers against the other."""
    mine, theirs = sides(entry)[side], sides(entry)[1 - side]
    return battle.weight_of_numbers(mine.groups, theirs.groups)


def territorial(entry: Battle, side: int = 0) -> int:
    mine, theirs = sides(entry)[side], sides(entry)[1 - side]
    return battle.territorial_advantage(mine.deployment, theirs.deployment)


def baggage_short(entry: Battle, side: int = 0) -> int:
    """Baggage groups `side`'s army lacks for its size now."""
    mine = sides(entry)[side]
    return max(0, battle.baggage_needed(mine.groups) - mine.baggage)


def routed(entry: Battle) -> int | None:
    """The side whose army routed, which ends the battle (None: none has)."""
    for event in entry.events:
        if battle.morale_result(event.morale, event.rally) == battle.ROUTS:
            return 1 - event.side if event.won else event.side
    return None


def morale_text(event: BattleEvent) -> str:
    """The losing commander's Morale after an event ("" when not rolled)."""
    result = battle.morale_result(event.morale, event.rally)
    if not result:
        return ""
    words = {
        battle.HOLDS: f"Morale {event.morale} holds",
        battle.WAVERS: f"Morale {event.morale} fails: a rally at the next event "
        f"(against {battle.RALLY_EASE})",
        battle.RALLIES: f"Morale {event.morale} fails; rallied ({event.rally})",
        battle.ROUTS: f"Morale {event.morale} fails; the rally ({event.rally}) "
        "fails too: the army routs, and the battle is over",
    }
    return words[result]


def record_text(entry: Battle) -> str:
    """Events the first side won and lost ("2 won, 1 lost"; "none yet")."""
    if not entry.events:
        return "none yet"
    won = sum(1 for e in entry.events if e.won == (e.side == 0))
    return f"{won} won, {len(entry.events) - won} lost"


# -- the lists --


def title(saga: Saga, neighbour: Neighbour | None = None) -> str:
    listed = saga.battles if neighbour is None else involving(saga, neighbour)
    return f"Battles ({len(listed)})"


def grid(saga: Saga, neighbour: Neighbour | None = None) -> Grid:
    """The saga's battles, or those naming `neighbour`, from the first
    side's point of view."""
    listed = saga.battles if neighbour is None else involving(saga, neighbour)
    rows = [
        [
            b.name,
            f"{side_name(saga, b, 0)} v {side_name(saga, b, 1)}",
            f"{sides(b)[0].groups} v {sides(b)[1].groups}",
            f"{territorial(b):+d}",
            f"{weight(b):+d}",
            record_text(b),
        ]
        for b in listed
    ]
    return Grid(
        ["Battle", "Armies", "Groups", "Ground", "Numbers", "Events"],
        rows,
        list(range(len(rows))),
        "No battles fought: add one, then play its events with Battle Event.",
        caps=[20, 30, 9, 6, 7, 0],
        stretch=1,
    )


def _army_options(saga: Saga) -> list[tuple[str, str]]:
    return [
        ("None: just a name", ""),
        *((escape(c.name), COVENANT + c.id) for c in saga.covenants),
        *(
            (f"{escape(n.name)} ({n.kind})", NEIGHBOUR + n.id)
            for n in saga.neighbours
            if n.kind in ARMY_KINDS
        ),
    ]


def _linked(side: BattleSide) -> str:
    if side.neighbour_id:
        return NEIGHBOUR + side.neighbour_id
    return COVENANT + side.covenant_id if side.covenant_id else ""


def fields(
    saga: Saga, entry: Battle | None, first: Neighbour | None = None
) -> list[DialogField]:
    """A battle's form; `first` links a new one's first side to the lord
    whose page it is added on."""
    e = entry or Battle(
        "",
        year=saga.current_year,
        season=saga.current_season,
        sides=[BattleSide(neighbour_id=first.id if first else ""), BattleSide()],
    )
    found = [
        DialogField(
            "name",
            "Battle",
            "text",
            e.name,
            required=True,
            placeholder="e.g. The ford at Werl",
        ),
        DialogField("place", "Where", "text", e.place, placeholder="e.g. by the Lippe"),
        DialogField("season", "Season", "select", e.season, options=pairs(SEASONS)),
        DialogField("year", "Year", "int", e.year),
    ]
    for index, label in enumerate(("First army", "Second army")):
        side = sides(e)[index]
        found += [
            DialogField(
                f"army_{index}",
                label,
                "select",
                _linked(side),
                options=_army_options(saga),
                hint="A lord, town or other power of the Region, or a covenant: "
                "the battle shows on a lord's Fief tab and is written in each "
                "side's Diary.",
            ),
            DialogField(
                f"name_{index}",
                f"{label}'s name",
                "text",
                side.name,
                placeholder="Blank: the linked record's name",
            ),
            DialogField(
                f"home_{index}",
                f"{label} fights on its home ground",
                "check",
                side.at_home,
                hint="Only on home ground does a lord raise his levies (Lords "
                "of Men pp. 31, 102).",
            ),
            DialogField(
                f"groups_{index}",
                f"{label}'s combat groups",
                "optint",
                side.groups if entry is not None else None,
                hint="Groups of five men. Blank, a lord's title's army fills it "
                "in, his levies only at home; add his allies and mercenaries.",
            ),
            DialogField(
                f"deployment_{index}",
                f"{label}'s Deployment Total",
                "int",
                side.deployment,
                hint="Intelligence + Area Lore + stress die, the commander's (or "
                "a lieutenant's); + the magnitude of a spell that shapes the "
                "ground.",
            ),
            DialogField(
                f"baggage_{index}",
                f"{label}'s baggage groups",
                "optint",
                side.baggage if entry is not None else None,
                hint="A group for every ten combat groups (blank: as many as it "
                "needs); each one short is -1 to its Event Totals.",
            ),
        ]
    return found


def _write(saga: Saga, entry: Battle, values: dict[str, Any]) -> None:
    entry.name = values["name"]
    entry.place = values.get("place") or ""
    entry.season = values.get("season") or entry.season
    entry.year = int(values.get("year") or entry.year)
    for index in range(2):
        side = sides(entry)[index]
        linked = str(values.get(f"army_{index}") or "")
        side.neighbour_id = (
            linked.removeprefix(NEIGHBOUR) if linked.startswith(NEIGHBOUR) else ""
        )
        side.covenant_id = (
            linked.removeprefix(COVENANT) if linked.startswith(COVENANT) else ""
        )
        side.name = values.get(f"name_{index}") or ""
        side.at_home = bool(values.get(f"home_{index}"))
        groups = values.get(f"groups_{index}")
        if groups is None:
            lord = saga.neighbour(side.neighbour_id)
            groups = (
                armies.army_groups(lord, at_home=side.at_home)
                if lord and lord.kind == "lord"
                else 0
            )
        side.groups = int(groups)
        side.deployment = int(values.get(f"deployment_{index}") or 0)
        baggage = values.get(f"baggage_{index}")
        side.baggage = (
            battle.baggage_needed(side.groups) if baggage is None else int(baggage)
        )


def problem(values: dict[str, Any]) -> str | None:
    for index in range(2):
        for key in ("groups", "baggage"):
            if (values.get(f"{key}_{index}") or 0) < 0:
                return "Groups can't be fewer than none."
    if values.get("army_0") and values.get("army_0") == values.get("army_1"):
        return "An army can't fight itself."
    return None


def ops(saga: Saga, neighbour: Neighbour | None = None) -> SectionOps:
    """Add, Edit and Delete on the saga's battles, or (`neighbour`) on
    those naming him: Add there links the new battle's first side to
    him."""

    def listed() -> list[Battle]:
        return saga.battles if neighbour is None else involving(saga, neighbour)

    def form(index: int | None) -> Command:
        entry = None if index is None else listed()[index]

        def apply(values: dict[str, Any]) -> None:
            if entry is None:
                made = Battle(values["name"])
                _write(saga, made, values)
                saga.battles.append(made)
            else:
                _write(saga, entry, values)

        return Form(
            "Add a Battle" if entry is None else "Edit a Battle",
            lambda: fields(saga, entry, neighbour),
            apply,
            validate=problem,
            save_label="Add" if entry is None else "Save",
            help_id="section-nb-battles",
        )

    def remove(index: int) -> Command:
        entry = listed()[index]
        return Confirm(
            f"Delete the battle {escape(entry.name)}?",
            lambda: saga.battles.remove(entry),
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=remove,
        rows=lambda: [b.name for b in listed()],
    )


def info(saga: Saga, entry: Battle) -> str:
    """A battle in full: the armies, the ground and each event (markup)."""
    first, second = sides(entry)[:2]
    lines = [
        f"[b]{escape(entry.name)}[/]  [dim]{entry.season} {entry.year}"
        + (f", {escape(entry.place)}" if entry.place else "")
        + "[/]",
        f"{escape(side_name(saga, entry, 0))}: {first.groups} combat groups, "
        f"Deployment Total {first.deployment}, {first.baggage} baggage.",
        f"{escape(side_name(saga, entry, 1))}: {second.groups} combat groups, "
        f"Deployment Total {second.deployment}, {second.baggage} baggage.",
        f"For the first army: Weight of Numbers {weight(entry):+d}, Territorial "
        f"Advantage {territorial(entry):+d}.",
    ]
    for stage, event in enumerate(entry.events):
        who = saga.character(event.who)
        lines.append(
            f"{stage + 1}. {battle.stage_name(stage)} ({battle.ease_factor(stage)}): "
            f"{escape(who.name if who else '(gone)')} for "
            f"{escape(side_name(saga, entry, event.side))}, {event.maneuver} "
            f"{event.enemy} {event.size}, Event Total {event.total}: "
            f"{'won' if event.won else 'lost'}"
            + (f", {event.losses} groups lost" if event.losses else "")
            + (f"; {escape(morale_text(event))}" if morale_text(event) else "")
            + "."
        )
    lines.append(f"[dim]{battle.SOURCE}.[/]")
    return "\n".join(lines)


def info_for(saga: Saga, neighbour: Neighbour, index: int) -> str:
    """The `index`th battle naming the lord, in full."""
    listed = involving(saga, neighbour)
    return info(saga, listed[index]) if index < len(listed) else ""


# -- a battlefield event --


def event_of(saga: Saga, entry: Battle, values: dict[str, Any]) -> battle.Event | None:
    who = saga.character(values.get("who"))
    if who is None:
        return None
    side = int(values.get("side") or 0)
    return battle.Event(
        stamina=who.characteristics.stamina,
        leadership=sum(ability_score(who, "Leadership")),
        territorial=territorial(entry, side),
        weight=weight(entry, side),
        maneuver=values.get("maneuver") or "Defend",
        enemy=values.get("enemy") or "Inexpensive",
        size=values.get("size") or "Lesser",
        gave_up_initiative=bool(values.get("initiative")),
        baggage_short=baggage_short(entry, side),
    )


def event_live(saga: Saga, entry: Battle, values: dict[str, Any]) -> str:
    stage = len(entry.events)
    event = event_of(saga, entry, values)
    if event is None:
        return "Choose the character at the heart of the event."
    need = battle.ease_factor(stage)
    verdict = (
        "it can be won" if event.can_win(stage) else "it is played, but can't be won"
    )
    return (
        f"{battle.stage_name(stage)}, Ease Factor {need}: Event Total "
        f"{event.total} (Stamina {event.stamina:+d}, Leadership {event.leadership}, "
        f"Ground {event.territorial:+d}, Numbers {event.weight:+d}, Event Bonus "
        f"{event.bonus}"
        + (", +1 for the initiative" if event.gave_up_initiative else "")
        + (f", -{event.baggage_short} baggage short" if event.baggage_short else "")
        + f"): {verdict}."
    )


def _event_fields(saga: Saga, entry: Battle) -> list[DialogField]:
    return [
        DialogField(
            "who",
            "Leading the event",
            "select",
            saga.characters[0].id if saga.characters else None,
            options=[(escape(c.name), c.id) for c in saga.characters],
            required=True,
            hint="The player character at its heart: Stamina + Leadership.",
        ),
        DialogField(
            "side",
            "Fighting for",
            "select",
            "0",
            options=[(escape(side_name(saga, entry, i)), str(i)) for i in range(2)],
            required=True,
        ),
        DialogField(
            "maneuver",
            "Maneuver",
            "select",
            "Defend",
            options=[(f"{name} (+{n})", name) for name, n in battle.MANEUVERS.items()],
            required=True,
        ),
        DialogField(
            "enemy",
            "Enemy",
            "select",
            "Standard",
            options=[(f"{name} (+{n})", name) for name, n in battle.ENEMIES.items()],
            required=True,
        ),
        DialogField(
            "size",
            "Size",
            "select",
            "Even",
            options=[(f"{name} (+{n})", name) for name, n in battle.SIZES.items()],
            required=True,
        ),
        DialogField("initiative", "Give up the initiative (+1)", "check", False),
        DialogField(
            "result",
            "How it went",
            "select",
            "won",
            options=pairs(("won", "lost")),
            required=True,
            hint="Play the event out as a combat; then say who won it.",
        ),
        DialogField(
            "morale",
            "The losing commander's Morale",
            "optint",
            None,
            hint=f"Presence + Leadership + stress die, against "
            f"{battle.MORALE_EASE} (Lords of Men p. 106). Blank: not rolled.",
        ),
        DialogField(
            "rally",
            "His rally, if the Morale failed",
            "optint",
            None,
            hint=f"Presence + Leadership + stress die at the next event's "
            f"start, against {battle.RALLY_EASE}; failing it, the army routs "
            "and the battle ends.",
        ),
    ]


def event_form(saga: Saga, entry: Battle | None) -> Command:
    """Battle Event on a battle: the next event's focal character, the
    side they fight on, its Maneuver, Enemy and Size, its Event Total, and
    how it went; the losing side loses its groups, and the event is
    written in each side's Diary and the character's."""
    if entry is None:
        return Refuse("Battle Event", "Choose a battle first.")
    fled = routed(entry)
    if fled is not None:
        return Refuse(
            "Battle Event",
            f"{escape(side_name(saga, entry, fled))}'s army routed: the battle "
            "is over (Lords of Men p. 106).",
        )
    stage = len(entry.events)

    def apply(values: dict[str, Any]) -> None:
        event = event_of(saga, entry, values)
        assert event is not None
        side = int(values.get("side") or 0)
        won = values.get("result") == "won"
        mine = weight(entry, side)
        lost = battle.losses(event.size, mine if won else -mine)
        losing = 1 - side if won else side
        loser = sides(entry)[losing]
        loser.groups = max(0, loser.groups - lost)
        who = saga.character(values["who"])
        name = who.name if who else "someone"
        record = BattleEvent(
            values["who"],
            side,
            event.maneuver,
            event.enemy,
            event.size,
            event.gave_up_initiative,
            event.total,
            won,
            lost,
            values.get("morale"),
            values.get("rally"),
        )
        spirit = morale_text(record)
        diaries.write(
            saga.current_year,
            saga.current_season,
            entry.name or "Battle",
            f"{battle.stage_name(stage)}: {name} led {event.maneuver} for "
            f"{side_name(saga, entry, side)} against {event.enemy} ({event.size}), "
            f"Event Total {event.total}: {'won' if won else 'lost'}"
            + (
                f"; {lost} of {side_name(saga, entry, losing)}'s groups lost"
                if lost
                else ""
            )
            + (f"; {side_name(saga, entry, losing)}: {spirit}" if spirit else "")
            + ".",
            characters=[who] if who else [],
            neighbours=[
                n for s in sides(entry) if (n := saga.neighbour(s.neighbour_id))
            ],
            covenants=[c for s in sides(entry) if (c := saga.covenant(s.covenant_id))],
        )
        entry.events.append(record)

    return Form(
        f"Battle Event {stage + 1}: {escape(entry.name)}",
        lambda: _event_fields(saga, entry),
        apply,
        live=lambda values: event_live(saga, entry, values),
        save_label="Record",
        help_id="battle-event",
    )


def battle_of(saga: Saga, index: int) -> Battle | None:
    return saga.battles[index] if 0 <= index < len(saga.battles) else None


def event_for(saga: Saga, neighbour: Neighbour, index: int) -> Command:
    """Battle Event on the `index`th battle naming the lord."""
    listed = involving(saga, neighbour)
    return event_form(saga, listed[index] if index < len(listed) else None)


#: A lord's Fief tab lists the battles naming him through these, which
#: take (saga, neighbour) as a kind's lists do.
LORD_TITLE: Callable[[Saga, Neighbour], str] = title
LORD_GRID: Callable[[Saga, Neighbour], Grid] = grid
LORD_OPS: Callable[[Saga, Neighbour], SectionOps] = ops
