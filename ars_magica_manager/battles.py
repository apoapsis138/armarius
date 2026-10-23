"""A lord's battles (Lords of Men, Chapter Eight: Massed Combat): each
battle his army fights, with both armies in combat groups of five, the
commanders' Deployment Totals, and the battlefield events played so far.
The rules are rules.battle's; this is the record and its forms.

Kept in Neighbour.details["battles"], each {"name", "enemy", "ours",
"theirs" (combat groups now), "our_deployment", "their_deployment",
"baggage", "events"}; an event is {"who" (a character's id), "maneuver", "enemy",
"size", "initiative" (given up), "total", "won", "losses"}."""

from __future__ import annotations

from typing import Any, Required, TypedDict, cast

from .commands import Command, Form, Refuse, SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import Character, Neighbour, Saga, details_list
from .neighbour_lists import list_ops
from .rules import battle
from .rules.lab import ability_score


class BattleEvent(TypedDict):
    """A battlefield event played: who led it (a character's id), the
    maneuver, the enemy unit and its size, whether the initiative was
    given up, its Event Total, whether it was won, and the combat groups
    lost."""

    who: str
    maneuver: str
    enemy: str
    size: str
    initiative: bool
    total: int
    won: bool
    losses: int


class Battle(TypedDict, total=False):
    """A battle the lord's army fights: the enemy, both armies in combat
    groups now, the commanders' Deployment Totals, the baggage train, and
    the events played."""

    name: Required[str]
    enemy: str
    ours: int
    theirs: int
    our_deployment: int
    their_deployment: int
    baggage: int
    events: list[BattleEvent]


def battles(neighbour: Neighbour) -> list[Battle]:
    return cast(list[Battle], details_list(neighbour, "battles"))


def army_groups(neighbour: Neighbour) -> int:
    """The combat groups of five the lord's title raises (his levies
    included)."""
    from . import lords  # lords' Fief tab lists the battles

    army = lords.army_of(lords.title(neighbour), lords.wealth(neighbour))
    men = army.knights + army.serjeants + army.infantry + army.levies
    return men // battle.GROUP_SIZE


def territorial(entry: Battle) -> int:
    return battle.territorial_advantage(
        int(entry.get("our_deployment") or 0), int(entry.get("their_deployment") or 0)
    )


def weight(entry: Battle) -> int:
    return battle.weight_of_numbers(
        int(entry.get("ours") or 0), int(entry.get("theirs") or 0)
    )


def events(entry: Battle) -> list[BattleEvent]:
    found = entry.setdefault("events", [])
    if not isinstance(found, list):
        raise ValueError(f"A battle's events should be a list, not {found!r}.")
    return found


def record_text(entry: Battle) -> str:
    """Events won and lost ("2 won, 1 lost"; "none yet")."""
    played = events(entry)
    if not played:
        return "none yet"
    won = sum(1 for e in played if e.get("won"))
    return f"{won} won, {len(played) - won} lost"


# -- the list --


def title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Battles ({len(battles(neighbour))})"


def grid(_saga: Saga, neighbour: Neighbour) -> Grid:
    rows = [
        [
            b.get("name", ""),
            b.get("enemy", ""),
            f"{b.get('ours', 0)} v {b.get('theirs', 0)}",
            f"{territorial(b):+d}",
            f"{weight(b):+d}",
            record_text(b),
        ]
        for b in battles(neighbour)
    ]
    return Grid(
        ["Battle", "Against", "Groups", "Ground", "Numbers", "Events"],
        rows,
        list(range(len(rows))),
        "No battles fought: add one, then play its events with Battle Event.",
        caps=[22, 18, 9, 6, 7, 0],
        stretch=1,
    )


def fields(
    _saga: Saga, neighbour: Neighbour, entry: Battle | None
) -> list[DialogField]:
    e = entry or {}
    return [
        DialogField(
            "name",
            "Battle",
            "text",
            e.get("name", ""),
            required=True,
            placeholder="e.g. The ford at Werl",
        ),
        DialogField(
            "enemy",
            "Against",
            "text",
            e.get("enemy", ""),
            placeholder="e.g. the Count of Mark",
        ),
        DialogField(
            "ours",
            "His combat groups",
            "int",
            e.get("ours", army_groups(neighbour)),
            hint="Groups of five men: his title's army, with allies and "
            "mercenaries added.",
        ),
        DialogField("theirs", "The enemy's combat groups", "int", e.get("theirs", 0)),
        DialogField(
            "our_deployment",
            "His Deployment Total",
            "int",
            e.get("our_deployment", 0),
            hint="Intelligence + Area Lore + stress die, his commander's (or "
            "lieutenant's); + the magnitude of a spell that shapes the ground.",
        ),
        DialogField(
            "their_deployment",
            "The enemy's Deployment Total",
            "int",
            e.get("their_deployment", 0),
        ),
        DialogField(
            "baggage",
            "His baggage groups",
            "int",
            e.get("baggage", battle.baggage_needed(army_groups(neighbour))),
            hint="A group for every ten combat groups; each one short is -1 "
            "to his Event Totals.",
        ),
    ]


def baggage_short(entry: Battle) -> int:
    """Baggage groups the lord's army lacks for its size now."""
    needed = battle.baggage_needed(int(entry.get("ours") or 0))
    return max(0, needed - int(entry.get("baggage") or 0))


def problem(values: dict[str, Any]) -> str | None:
    if any((values.get(key) or 0) < 0 for key in ("ours", "theirs", "baggage")):
        return "Groups can't be fewer than none."
    return None


def ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        neighbour,
        "battles",
        "Battle",
        fields,
        lambda b: b["name"],
        validate=problem,
    )


def info(saga: Saga, neighbour: Neighbour, index: int) -> str:
    """A battle in full: the armies, the ground and each event (markup)."""
    entry = battles(neighbour)[index]
    lines = [
        f"[b]{escape(entry.get('name', ''))}[/] against "
        f"{escape(entry.get('enemy', '') or 'the enemy')}",
        f"Combat groups: {entry.get('ours', 0)} against {entry.get('theirs', 0)}; "
        f"Weight of Numbers {weight(entry):+d}.",
        f"Territorial Advantage {territorial(entry):+d} (Deployment Totals "
        f"{entry.get('our_deployment', 0)} and {entry.get('their_deployment', 0)}).",
    ]
    for stage, event in enumerate(events(entry)):
        who = saga.character(event.get("who"))
        lines.append(
            f"{stage + 1}. {battle.stage_name(stage)} ({battle.ease_factor(stage)}): "
            f"{escape(who.name if who else '(gone)')}, {event['maneuver']} "
            f"{event['enemy']} {event['size']}, Event Total {event['total']}: "
            f"{'won' if event.get('won') else 'lost'}"
            + (
                f", {event['losses']} enemy groups lost"
                if event.get("won") and event.get("losses")
                else f", {event['losses']} of his groups lost"
                if event.get("losses")
                else ""
            )
            + "."
        )
    lines.append(f"[dim]{battle.SOURCE}.[/]")
    return "\n".join(lines)


# -- a battlefield event --


def event_of(saga: Saga, entry: Battle, values: dict[str, Any]) -> battle.Event | None:
    who: Character | None = saga.character(values.get("who"))
    if who is None:
        return None
    return battle.Event(
        stamina=who.characteristics.stamina,
        leadership=sum(ability_score(who, "Leadership")),
        territorial=territorial(entry),
        weight=weight(entry),
        maneuver=values.get("maneuver") or "Defend",
        enemy=values.get("enemy") or "Inexpensive",
        size=values.get("size") or "Lesser",
        gave_up_initiative=bool(values.get("initiative")),
        baggage_short=baggage_short(entry),
    )


def event_live(saga: Saga, entry: Battle, values: dict[str, Any]) -> str:
    stage = len(events(entry))
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


def event_form(saga: Saga, neighbour: Neighbour, index: int) -> Command:
    """More's Battle Event on the chosen battle: the next event's focal
    character and its Maneuver, Enemy and Size, its Event Total, and how
    it went; the losing side loses its groups."""
    listed = battles(neighbour)
    if index >= len(listed):
        return Refuse("Battle Event", "Choose a battle first.")
    entry = listed[index]
    stage = len(events(entry))

    def form_fields() -> list[DialogField]:
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
                "maneuver",
                "Maneuver",
                "select",
                "Defend",
                options=[
                    (f"{name} (+{n})", name) for name, n in battle.MANEUVERS.items()
                ],
                required=True,
            ),
            DialogField(
                "enemy",
                "Enemy",
                "select",
                "Standard",
                options=[
                    (f"{name} (+{n})", name) for name, n in battle.ENEMIES.items()
                ],
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
            DialogField(
                "initiative",
                "Give up the initiative (+1)",
                "check",
                False,
            ),
            DialogField(
                "result",
                "How it went",
                "select",
                "won",
                options=pairs(("won", "lost")),
                required=True,
                hint="Play the event out as a combat; then say who won it.",
            ),
        ]

    def apply(values: dict[str, Any]) -> None:
        event = event_of(saga, entry, values)
        assert event is not None
        won = values.get("result") == "won"
        ours = weight(entry)
        lost = battle.losses(event.size, ours if won else -ours)
        side = "theirs" if won else "ours"
        entry[side] = max(0, int(entry.get(side) or 0) - lost)
        events(entry).append(
            {
                "who": values["who"],
                "maneuver": event.maneuver,
                "enemy": event.enemy,
                "size": event.size,
                "initiative": event.gave_up_initiative,
                "total": event.total,
                "won": won,
                "losses": lost,
            }
        )

    return Form(
        f"Battle Event {stage + 1}: {escape(entry.get('name', ''))}",
        form_fields,
        apply,
        live=lambda values: event_live(saga, entry, values),
        save_label="Record",
        help_id="battle-event",
    )
