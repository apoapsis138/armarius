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

from . import armies, diaries, fight_morale
from . import battle_fights as bf
from . import fleet_battles as fleet
from .commands import Command, Confirm, Form, Refuse, SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import SEASONS, Battle, BattleEvent, BattleSide, Fight, Neighbour, Saga
from .rules import battle, confidence
from .rules import fleet_battle as fleet_rules
from .rules import options as rule_options
from .rules import siege as siege_rules
from .rules.lab import ability_score

#: What a side can be: a covenant, or one of the Region's powers.
ARMY_KINDS = ("lord", "town", "threat", "faction", "church")
COVENANT, NEIGHBOUR = fleet.COVENANT, fleet.NEIGHBOUR


#: The bad Reputation a character attacking the baggage earns toward.
BAGGAGE_REPUTATION = "Attacked the baggage"

#: The kinds of group an army keeps, and the Enemy whose losses fall on
#: each (p. 106: the units lost match the Enemy).
KINDS: tuple[str, ...] = ("knights", "serjeants", "infantry", "archers", "levies")
#: Groups a lord's allies bring (Raise Allies): lost after the side's own.
ALLIES = "allies"
ENEMY_KINDS: dict[str, tuple[str, ...]] = {
    "Inexpensive": ("levies",),
    "Standard": ("infantry", "archers"),
    "Expensive": ("knights", "serjeants"),
}


def add_groups(side: BattleSide, kind: str, count: int) -> None:
    """Add `count` groups of `kind` to the side, counted in its total."""
    if count <= 0:
        return
    side.mix[kind] = side.mix.get(kind, 0) + count
    side.groups += count


def take_losses(side: BattleSide, enemy: str, lost: int) -> list[str]:
    """Take an event's losses from the kinds its Enemy names first (p.
    106), then from the side's other groups, its allies last; the total
    falls by `lost`."""
    lost = min(lost, side.groups)
    left = lost
    taken: list[str] = []
    for kind in (*ENEMY_KINDS.get(enemy, ()), *KINDS, ALLIES):
        have = side.mix.get(kind, 0)
        if not left or not have:
            continue
        out = min(have, left)
        side.mix[kind] = have - out
        left -= out
        taken.append(f"{out} of {kind}")
    side.groups -= lost
    return taken


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


def weight(entry: Battle, side: int = 0, saga: Saga | None = None) -> int:
    """`side`'s Weight of Numbers against the other: by combat groups, or
    at sea (with the `saga` that holds the ships) by ships."""
    if entry.at_sea and saga is not None:
        return fleet.weight(saga, sides(entry), side)
    if entry.siege_id:
        # An escalade: the garrison's Garrison row, for it, against the
        # besiegers (Lords of Men p. 115).
        return entry.siege_weight if side == 1 else -entry.siege_weight
    mine, theirs = sides(entry)[side], sides(entry)[1 - side]
    return battle.weight_of_numbers(mine.groups, theirs.groups)


def territorial(entry: Battle, side: int = 0) -> int:
    if entry.siege_id:
        # The castle's Defense Bonus stands for Territorial Advantage, the
        # garrison's (p. 115).
        return entry.siege_defense if side == 1 else -entry.siege_defense
    mine, theirs = sides(entry)[side], sides(entry)[1 - side]
    return battle.territorial_advantage(mine.deployment, theirs.deployment)


def baggage_short(entry: Battle, side: int = 0) -> int:
    """Baggage groups `side`'s army lacks for its size now."""
    mine = sides(entry)[side]
    return max(0, battle.baggage_needed(mine.groups) - mine.baggage)


#: An army's spirit: steady, disordered by a first failed rally, routed by
#: a second (Lords of Men pp. 106, 134-135).
STEADY, DISORDERED, ROUTED = "steady", "disordered", "routed"
_SPIRIT = (STEADY, DISORDERED, ROUTED)
#: A player character's rally: Presence + Leadership + stress die (p. 135).
PC_RALLY_EASE = 9


def rally_held(event: BattleEvent) -> bool:
    """Whether a player character's rally at the event succeeded."""
    if not event.rally_by:
        return False
    if event.rally_story:
        return event.rally_story == "won"
    return event.rally_roll is not None and event.rally_roll >= PC_RALLY_EASE


def spirits(entry: Battle) -> list[str]:
    """Each army's spirit after the events so far: a failed rally of its
    commander steps it down (steady to disordered, disordered to routed),
    a player character's rally steps it up, one step at a time (pp. 106,
    135)."""
    found = [0, 0]
    for event in entry.events:
        if event.rally_by and rally_held(event):
            side = event.rally_side
            found[side] = max(0, found[side] - 1)
        if battle.morale_result(event.morale, event.rally) == battle.ROUTS:
            losing = 1 - event.side if event.won else event.side
            found[losing] = min(2, found[losing] + 1)
    return [_SPIRIT[n] for n in found]


def routed(entry: Battle) -> int | None:
    """The side whose army routed, which ends the battle (None: none has):
    a first failed rally only disorders it (p. 106)."""
    for side, spirit in enumerate(spirits(entry)):
        if spirit == ROUTED:
            return side
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
        "fails too: the army is disordered, or routs if it was already",
    }
    return words[result]


def ships_text(saga: Saga, entry: Battle) -> str:
    """ "3 v 2": each fleet's ships afloat ("" for a battle on land)."""
    if not entry.at_sea:
        return ""
    first, second = (fleet.ship_count(saga, side) for side in sides(entry)[:2])
    return f"{first} v {second}"


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
            f"{weight(b, saga=saga):+d}",
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
        fleet.fought_field(e),
        DialogField("place", "Where", "text", e.place, placeholder="e.g. by the Lippe"),
        DialogField("season", "Season", "select", e.season, options=pairs(SEASONS)),
        DialogField("year", "Year", "int", e.year),
        DialogField(
            "chevauchee_on",
            "Chevauchee on",
            "select",
            e.chevauchee_on or None,
            options=[(escape(c.name), c.id) for c in saga.covenants],
            allow_blank=True,
            placeholder="(no covenant's land)",
            hint="The covenant whose land an army ravaged: those who return "
            "to it from the campaign take -2 on their next Aging roll; in "
            "extreme cases the land may take an Infernal aura, the "
            "storyguide's (Lords of Men p. 103).",
        ),
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
            *fleet.side_fields(saga, side, index),
        ]
    return found


def _write(saga: Saga, entry: Battle, values: dict[str, Any]) -> None:
    entry.name = values["name"]
    entry.place = values.get("place") or ""
    entry.season = values.get("season") or entry.season
    entry.year = int(values.get("year") or entry.year)
    entry.chevauchee_on = values.get("chevauchee_on") or ""
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
    fleet.write(saga, entry, sides(entry), values)


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
            validate=lambda values: problem(values) or fleet.problem(saga, values),
            live=lambda values: fleet.battle_live(saga, values),
            save_label="Add" if entry is None else "Save",
            help_id="section-nb-battles",
            inspector="The Fleets"
            if entry is not None and entry.at_sea
            else "The Armies",
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
        + (", at sea" if entry.at_sea else "")
        + "[/]",
        f"{escape(side_name(saga, entry, 0))}: {first.groups} combat groups, "
        f"Deployment Total {first.deployment}, {first.baggage} baggage.",
    ]
    if entry.at_sea:
        lines.append(fleet.side_line(saga, first))
    lines.append(
        f"{escape(side_name(saga, entry, 1))}: {second.groups} combat groups, "
        f"Deployment Total {second.deployment}, {second.baggage} baggage."
    )
    if entry.at_sea:
        lines.append(fleet.side_line(saga, second))
    lines.append(
        f"For the first army: Weight of Numbers {weight(entry, saga=saga):+d}"
        + (" by ships" if entry.at_sea else "")
        + f", Territorial Advantage {territorial(entry):+d}."
    )
    for stage, event in enumerate(entry.events):
        who = saga.character(event.who)
        lines.append(
            f"{stage + 1}. {battle.stage_name(stage)} ({battle.ease_factor(stage)}): "
            f"{escape(who.name if who else '(gone)')} for "
            f"{escape(side_name(saga, entry, event.side))}, "
            + (f"{escape(fleet.event_words(event))}: " if event.deed else "")
            + f"{event.maneuver} "
            f"{event.enemy} {event.size}, Event Total {event.total}: "
            f"{'won' if event.won else 'lost'}"
            + (f", {event.losses} groups lost" if event.losses else "")
            + (f"; {escape(morale_text(event))}" if morale_text(event) else "")
            + (
                f"; rallied by {escape(_name(saga, event.rally_by))}"
                + ("" if rally_held(event) else ", in vain")
                if event.rally_by
                else ""
            )
            + "."
        )
    for side, spirit in enumerate(spirits(entry)):
        if spirit != STEADY:
            lines.append(
                f"{escape(side_name(saga, entry, side))}'s army is {spirit}"
                + (
                    ": a player character may rally it at the next event."
                    if spirit == DISORDERED
                    else ": the battle is over."
                )
            )
    lines.append(
        f"[dim]{battle.SOURCE}"
        + (f"; at sea, {fleet_rules.SOURCE}" if entry.at_sea else "")
        + ".[/]"
    )
    return "\n".join(lines)


def _name(saga: Saga, character_id: str) -> str:
    who = saga.character(character_id)
    return who.name if who else "(gone)"


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
        weight=fleet.event_weight(saga, sides(entry), values, side)
        if entry.at_sea
        else weight(entry, side),
        maneuver=values.get("maneuver") or "Defend",
        enemy=values.get("enemy") or "Inexpensive",
        size=values.get("size") or "Lesser",
        gave_up_initiative=bool(values.get("initiative")),
        baggage_short=baggage_short(entry, side),
    )


def event_live(saga: Saga, entry: Battle, values: dict[str, Any]) -> str:
    """The Event Total so far; at sea, the ships engaged first; with a
    fight played for it, what the fight says."""
    total = _event_total_live(saga, entry, values)
    if entry.at_sea:
        return fleet.event_live(saga, sides(entry), values) + "\n" + total
    playing = bf.pending(saga, entry)
    if playing is not None:
        return total + "\n" + escape(bf.proposal_text(saga, playing))
    return total


def _event_total_live(saga: Saga, entry: Battle, values: dict[str, Any]) -> str:
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
    at_sea = fleet.event_fields(saga, entry, sides(entry)) if entry.at_sea else []
    playing = bf.pending(saga, entry)
    kept = dict(playing.battle_event) if playing is not None else {}

    def was(key: str, default: Any) -> Any:
        return kept.get(key, default)

    won = bf.proposal(saga, playing).won if playing is not None else None
    on_land = [] if entry.at_sea else _fight_fields(playing, won)
    return at_sea + [
        DialogField(
            "who",
            "Leading the event",
            "select",
            was("who", saga.characters[0].id if saga.characters else None),
            options=[(escape(c.name), c.id) for c in saga.characters],
            required=True,
            hint="The player character at its heart: Stamina + Leadership.",
        ),
        DialogField(
            "side",
            "Fighting for",
            "select",
            was("side", "0"),
            options=[(escape(side_name(saga, entry, i)), str(i)) for i in range(2)],
            required=True,
        ),
        DialogField(
            "maneuver",
            "Maneuver",
            "select",
            was("maneuver", "Defend"),
            options=[(f"{name} (+{n})", name) for name, n in battle.MANEUVERS.items()],
            required=True,
        ),
        DialogField(
            "enemy",
            "Enemy",
            "select",
            was("enemy", "Standard"),
            options=[(f"{name} (+{n})", name) for name, n in battle.ENEMIES.items()],
            required=True,
        ),
        DialogField(
            "size",
            "Size",
            "select",
            was("size", "Even"),
            options=[(f"{name} (+{n})", name) for name, n in battle.SIZES.items()],
            required=True,
        ),
        DialogField(
            "initiative",
            "Give up the initiative (+1)",
            "check",
            bool(was("initiative", False)),
        ),
        *on_land,
        *_rally_fields(saga, entry),
        DialogField(
            "result",
            "How it went",
            "select",
            "won" if won is not False else "lost",
            options=pairs(("won", "lost")),
            required=True,
            show_if=lambda _v: entry.at_sea,
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


def _rally_fields(saga: Saga, entry: Battle) -> list[DialogField]:
    """A player character's rally of a disordered army, offered while one
    is (Lords of Men pp. 106, 135)."""
    failing = [i for i, s in enumerate(spirits(entry)) if s == DISORDERED]
    if not failing:
        return []

    def rallied(values: dict[str, Any]) -> bool:
        return bool(values.get("rally_by"))

    return [
        DialogField(
            "rally_by",
            "A rally by",
            "select",
            None,
            options=[(escape(c.name), c.id) for c in saga.characters],
            allow_blank=True,
            placeholder="(no one)",
            hint="A player character takes command of the disordered army: "
            f"{escape(side_name(saga, entry, failing[0]))}'s.",
        ),
        DialogField(
            "rally_way",
            "The rally is",
            "select",
            "roll",
            options=[
                ("A roll: Presence + Leadership + stress die against 9", "roll"),
                ("A story event played for it", "story"),
            ],
            show_if=rallied,
        ),
        DialogField(
            "rally_roll",
            "His roll",
            "optint",
            None,
            show_if=lambda v: rallied(v) and v.get("rally_way") != "story",
        ),
        DialogField(
            "rally_story",
            "The story",
            "select",
            "won",
            options=pairs(("won", "lost")),
            show_if=lambda v: rallied(v) and v.get("rally_way") == "story",
        ),
    ]


def condition_key(maneuver: str) -> str:
    """The form's key for a Maneuver's "How it went" ("condition_Run_the_
    Gauntlet"): a field's key becomes a widget id, which takes no spaces."""
    return "condition_" + "".join(c if c.isalnum() else "_" for c in maneuver)


def _fight_fields(playing: Fight | None, won: bool | None) -> list[DialogField]:
    """Playing the event out as a fight (battle_fights): the leader's own
    group and the enemy's troops, and each Maneuver's ways to win."""
    found: list[DialogField] = []
    if playing is None:
        found += [
            DialogField(
                "play_fight",
                "Play it out as a fight",
                "check",
                False,
                hint="Makes a fight on Conflicts from the Maneuver, Enemy and "
                "Size: the leader and his group against the enemy's groups "
                "from the Standard Combat Groups (Lords of Men pp. 105-108). "
                "Play it, then come back to record the event.",
            ),
            DialogField(
                "company",
                "His company is one group",
                "check",
                False,
                show_if=lambda v: bool(v.get("play_fight")),
                hint="A Knight Banneret's or Mercenary Captain's company stays "
                "one group whatever the Weight of Numbers (Lords of Men p. "
                "104); ticked for him by the Virtue.",
            ),
            DialogField(
                "own_troop",
                "His group",
                "select",
                bf.own_troop_options()[4][1],
                options=bf.own_troop_options(),
                show_if=lambda v: bool(v.get("play_fight")),
            ),
        ]
        for enemy in battle.ENEMIES:
            options = bf.enemy_troop_options(enemy)
            if not options:
                continue
            found.append(
                DialogField(
                    f"enemy_troop_{enemy}",
                    "Their troops",
                    "select",
                    options[0][1],
                    options=options,
                    show_if=lambda v, enemy=enemy: (
                        bool(v.get("play_fight")) and v.get("enemy") == enemy
                    ),
                )
            )
    for maneuver, conditions in bf.WIN_CONDITIONS.items():
        # A finished fight proposes the Maneuver's first win, or first loss.
        first = next(
            (key for key, _w, wins in conditions if won is None or wins == won),
            conditions[0][0],
        )
        found.append(
            DialogField(
                condition_key(maneuver),
                "How it went",
                "select",
                first,
                options=[(words, key) for key, words, _won in conditions],
                show_if=lambda v, maneuver=maneuver: (
                    not v.get("play_fight") and v.get("maneuver") == maneuver
                ),
                hint="How the Maneuver is won or lost (Lords of Men pp. 106-108).",
            )
        )
    return found


def _make_fight(
    saga: Saga, entry: Battle, values: dict[str, Any], event: battle.Event
) -> list[str]:
    """The event's fight, made and left on Conflicts to play."""
    side = int(values.get("side") or 0)
    who = saga.character(values.get("who"))
    weapon = next(
        (i.id for i in (who.inventory if who else []) if i.kind == "weapon"), ""
    )
    enemy_row = values.get(f"enemy_troop_{event.enemy}")
    made = bf.Template(
        who=values.get("who") or "",
        weapon_id=weapon,
        side_name=side_name(saga, entry, side),
        enemy_name=side_name(saga, entry, 1 - side),
        enemy=event.enemy,
        size=event.size,
        weight=event.weight,
        own_row=int(values.get("own_troop") or 0),
        enemy_row=int(enemy_row) if enemy_row is not None else None,
        company=bool(values.get("company"))
        or bf.leads_a_company(saga, values.get("who") or ""),
    )
    fight = bf.fight_for(saga, entry, len(entry.events), made)
    fight.battle_event = bf.template_values(values)
    if rule_options.is_on(saga, rule_options.MORALE_DISCIPLINE):
        # An army disordered or routed fights its event so (p. 106).
        spirit = spirits(entry)
        for fight_side, army in ((0, side), (1, 1 - side)):
            if spirit[army] != STEADY:
                fight_morale.disorder_army(fight, fight_side, spirit[army])
    saga.fights.append(fight)
    special = (
        " A Special enemy is the storyguide's: add it with Add Combatant."
        if event.enemy == "Special"
        else ""
    )
    return [
        f"The fight {fight.name} is on Conflicts: play it (five rounds, unless "
        f"the event says otherwise), then Battle Event again records it.{special}"
    ]


def _escalade_problem(entry: Battle, values: dict[str, Any]) -> str | None:
    if entry.siege_id and values.get("enemy") == "Baggage":
        return "In an escalade the besiegers can't strike the baggage (p. 115)."
    return None


def _escalade_won(saga: Saga, entry: Battle, besiegers_won: bool) -> list[str]:
    """An escalade battle's event: a besiegers' win takes the Garrison a
    step down from the next siege event (p. 115)."""
    siege = next((s for s in saga.sieges if s.id == entry.siege_id), None)
    if siege is None or not besiegers_won:
        return []
    siege.garrison = siege_rules.step_down(siege.garrison)
    return [f"The garrison falls to {siege.garrison} combat groups."]


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
    if entry.ended:
        return Refuse("Battle Event", f"The battle is over: {escape(entry.ended)}")
    stage = len(entry.events)

    def apply(values: dict[str, Any]) -> list[str] | None:
        event = event_of(saga, entry, values)
        assert event is not None
        if values.get("play_fight") and not entry.at_sea:
            return _make_fight(saga, entry, values, event)
        side = int(values.get("side") or 0)
        condition = str(values.get(condition_key(event.maneuver)) or "")
        by_condition = bf.condition_won(event.maneuver, condition)
        won = (
            by_condition
            if by_condition is not None and not entry.at_sea
            else values.get("result") == "won"
        )
        mine = event.weight
        # Attrition: the event's Size times the winner's Weight of Numbers
        # (p. 106), on top of the groups the fight itself cost.
        lost = battle.losses(event.size, mine if won else -mine)
        playing = bf.pending(saga, entry)
        if playing is not None:
            found = bf.proposal(saga, playing)
            lost += found.lost_theirs if won else found.lost_ours
        losing = 1 - side if won else side
        loser = sides(entry)[losing]
        take_losses(loser, event.enemy, lost)
        if entry.siege_id:
            _escalade_won(saga, entry, losing == 1)
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
        record.win_condition = condition
        if playing is not None:
            record.fight_id = playing.id
        if values.get("rally_by"):
            failing = [i for i, s in enumerate(spirits(entry)) if s == DISORDERED]
            record.rally_by = str(values["rally_by"])
            record.rally_side = failing[0] if failing else side
            if values.get("rally_way") == "story":
                record.rally_story = str(values.get("rally_story") or "won")
            else:
                record.rally_roll = values.get("rally_roll")
        if entry.at_sea:
            record.deed = str(values.get("deed") or fleet_rules.FLEET_EVENT_DEFAULT)
            record.engaged_ships = fleet.engaged_ids(saga, sides(entry), values)
            record.engaged_other = fleet.engaged_other(sides(entry), values)
            record.naptha = bool(values.get("naptha"))
        at_sea = fleet.event_words(record)
        spirit = morale_text(record)
        diaries.write(
            saga.current_year,
            saga.current_season,
            entry.name or "Battle",
            f"{battle.stage_name(stage)}"
            + (f" at sea ({at_sea})" if at_sea else "")
            + f": {name} led {event.maneuver} for "
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
        if event.enemy == "Baggage" and who is not None:
            # Attacking the baggage earns 1 xp toward a bad Reputation (p. 106).
            confidence.deed_toward(who, BAGGAGE_REPUTATION, 1, bad=True)
        return None

    return Form(
        f"Battle Event {stage + 1}"
        + (" at sea" if entry.at_sea else "")
        + f": {escape(entry.name)}",
        lambda: _event_fields(saga, entry),
        apply,
        validate=(lambda values: fleet.event_problem(sides(entry), values))
        if entry.at_sea
        else (lambda values: _escalade_problem(entry, values))
        if entry.siege_id
        else None,
        live=lambda values: event_live(saga, entry, values),
        save_label="Record",
        help_id="battle-event",
        inspector="The Event" if entry.at_sea else "",
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
