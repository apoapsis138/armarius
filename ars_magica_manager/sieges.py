"""The saga's sieges: the list, the form that sets one up and the command
that plays its next event (Lords of Men pp. 111-116). The rules are
rules.siege's; this is the record and its forms, for either front-end.

Pattern: each siege event is a Strategy, a small function kept in
rules.siege by its name, which Next Siege Event picks from.
"""

from __future__ import annotations

import random
from typing import Any

from . import armies, diaries, medallions
from .commands import Command, Confirm, Form, Refuse, SectionOps, notes
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import SEASONS, WALLS, Neighbour, Saga, Siege, SiegeEvent
from .rules import battle
from .rules import siege as rules

SOURCE = rules.SOURCE
ENDINGS = ("Raised", "Surrendered", "Breached", "Taken by storm")


def siege_of(saga: Saga, index: int) -> Siege | None:
    return saga.sieges[index] if 0 <= index < len(saga.sieges) else None


def time_text(days: int) -> str:
    """How long a siege has run, in the largest whole units ("3 weeks",
    "1 season and 2 months", "2 years")."""
    if days <= 0:
        return "just begun"
    years, rest = divmod(days, rules.DAYS_PER_YEAR)
    seasons, rest = divmod(rest, rules.DAYS_PER_SEASON)
    months, rest = divmod(rest, rules.INTERVAL_DAYS["Month"])
    weeks, rest = divmod(rest, rules.INTERVAL_DAYS["Week"])
    parts = [
        f"{n} {unit}{'s' if n > 1 else ''}"
        for n, unit in (
            (years, "year"),
            (seasons, "season"),
            (months, "month"),
            (weeks, "week"),
            (rest, "day"),
        )
        if n
    ]
    return " and ".join(parts[:2])


def state_text(siege: Siege) -> str:
    return siege.ended or f"{time_text(siege.days)}"


def garrison_step(groups: int) -> str:
    """The Garrison's step by its combat groups, with its Weight of
    Numbers ("Week, +2")."""
    interval, weight = rules.garrison(groups)
    return f"{interval}, Weight of Numbers +{weight}"


# -- the list --


def castle_name(saga: Saga, siege: Siege) -> str:
    """The castle's name, or the linked record's when none is typed."""
    linked = saga.neighbour(siege.castle_id)
    return siege.castle or (linked.name if linked else "")


def besieger_name(saga: Saga, siege: Siege) -> str:
    """The besieger's name, or the linked lord's when none is typed."""
    linked = saga.neighbour(siege.besieger_id)
    return siege.besieger or (linked.name if linked else "")


def involving(saga: Saga, neighbour: Neighbour) -> list[Siege]:
    """The sieges a lord (or town, or place) holds out in or lays."""
    return [s for s in saga.sieges if neighbour.id in (s.castle_id, s.besieger_id)]


def _listed(saga: Saga, neighbour: Neighbour | None) -> list[Siege]:
    return saga.sieges if neighbour is None else involving(saga, neighbour)


def title(saga: Saga, neighbour: Neighbour | None = None) -> str:
    return f"Sieges ({len(_listed(saga, neighbour))})"


def grid(saga: Saga, neighbour: Neighbour | None = None) -> Grid:
    rows = [
        [
            s.name,
            castle_name(saga, s),
            besieger_name(saga, s),
            f"{s.garrison} groups",
            s.defenses,
            s.supplies,
            state_text(s),
        ]
        for s in _listed(saga, neighbour)
    ]
    return Grid(
        ["Siege", "Castle", "Besieger", "Garrison", "Defenses", "Supplies", "State"],
        rows,
        list(range(len(rows))),
        "No sieges yet: add one, then play it with Next Siege Event.",
        caps=[18, 14, 14, 9, 8, 8, 0],
        stretch=1,
    )


def _walls_fields(
    key: str, label: str, values: list[int], hint: str
) -> list[DialogField]:
    return [
        DialogField(
            f"{key}_{i}",
            f"{label}: {wall}",
            "int",
            values[i],
            hint=hint if i == 0 else "",
        )
        for i, wall in enumerate(WALLS)
    ]


def fields(
    saga: Saga, siege: Siege | None, besieger: Neighbour | None = None
) -> list[DialogField]:
    """A siege's form; `besieger` links a new one's besieging lord to the
    lord whose page it is added on."""
    s = siege or Siege(
        "",
        year=saga.current_year,
        season=saga.current_season,
        besieger_id=besieger.id if besieger else "",
    )
    found = [
        DialogField(
            "name",
            "Siege",
            "text",
            s.name,
            required=True,
            placeholder="e.g. The Siege of Burg Falkenstein",
        ),
        DialogField(
            "castle", "Castle", "text", s.castle, placeholder="e.g. Burg Falkenstein"
        ),
        DialogField(
            "holder",
            "Held by",
            "text",
            s.holder,
            placeholder="e.g. Sir Konrad, for the covenant",
        ),
        DialogField(
            "besieger",
            "Besieged by",
            "text",
            s.besieger,
            placeholder="e.g. the Baron of Urach",
        ),
        DialogField("season", "Begun in", "select", s.season, options=pairs(SEASONS)),
        DialogField("year", "Year", "int", s.year),
        DialogField(
            "size",
            "Castle's Size",
            "int",
            s.size,
            hint="+5 to +8 a house, tower or shell keep (walls of Defense Bonus x "
            "3 damage levels); +9 and larger a castle, town or city (x 4).",
        ),
        DialogField(
            "garrison",
            "Garrison (combat groups)",
            "optint",
            s.garrison if siege is not None else None,
            hint="10 or fewer a Day, +1 Weight of Numbers; 11-20 a Week, +2; "
            "21-40 a Month, +3; 41 or more a Season, +4. Blank: the army of the "
            "lord holding the castle (linked below), else 10.",
        ),
        DialogField(
            "defenses",
            "Defenses",
            "select",
            s.defenses,
            options=pairs(rules.QUALITIES),
            hint="Shoddy a Day, +1; Standard a Week, +2; Superior a Month, +3; "
            "Excellent a Season, +4.",
        ),
        DialogField(
            "supplies",
            "Supplies",
            "select",
            s.supplies,
            options=pairs(rules.QUALITIES),
            hint="Shoddy a Week, +1; Standard a Month, +3; Superior a Season, +5; "
            "Excellent a Year, +7 (the Siege Conditions Bonus).",
        ),
        DialogField(
            "enchanted", "Permanent defensive enchantments (+1)", "check", s.enchanted
        ),
        DialogField(
            "moat", "A moat (Defenses a step higher against mines)", "check", s.moat
        ),
        DialogField("miners", "Besiegers' units of miners", "int", s.miners),
        *(
            DialogField(
                f"engine_{kind}",
                f"Besiegers' {kind.lower()}s",
                "int",
                s.engines.get(kind, 0),
            )
            for kind in rules.ENGINES
        ),
        DialogField(
            "soldiers",
            "Besiegers' combat groups of soldiers",
            "optint",
            s.soldiers if siege is not None else None,
            hint="Blank: the besieging lord's army (linked below), else none.",
        ),
        *_walls_fields(
            "besieger_walls",
            "Besiegers at",
            s.besieger_walls,
            "Combat groups at each wall: at three walls or more the castle is in "
            "stockade and makes supplies rolls.",
        ),
        *_walls_fields(
            "garrison_walls",
            "Garrison at",
            s.garrison_walls,
            "The garrison's groups at each wall.",
        ),
        DialogField(
            "sapper",
            "Besiegers' sapper",
            "int",
            s.sapper,
            hint="Intelligence + Profession: Sapper.",
        ),
        DialogField(
            "gunner",
            "Besiegers' engine master",
            "int",
            s.gunner,
            hint="Intelligence + Siege Weapon.",
        ),
        DialogField(
            "counter_sapper",
            "Castle's counter-miner",
            "int",
            s.counter_sapper,
            hint="Intelligence + Profession: Sapper.",
        ),
        DialogField(
            "engineer",
            "Castle's engineer",
            "int",
            s.engineer,
            hint="Intelligence + Profession: Siege Engineer.",
        ),
    ]
    lords = [n for n in saga.neighbours if n.kind == "lord"]
    holders = [n for n in saga.neighbours if n.kind in ("lord", "place", "town")]
    none = [("None", "")]
    found += [
        DialogField(
            "covenant_id",
            "Covenant it concerns",
            "select",
            s.covenant_id,
            options=[*none, *((escape(c.name), c.id) for c in saga.covenants)],
            hint="Its Diary is written when the siege ends.",
        ),
        DialogField(
            "castle_id",
            "The castle in the Region",
            "select",
            s.castle_id,
            options=[*none, *((escape(n.name), n.id) for n in holders)],
            hint="A lord, town or place whose Diary its ending is written in.",
        ),
        DialogField(
            "besieger_id",
            "The besieging lord",
            "select",
            s.besieger_id,
            options=[*none, *((escape(n.name), n.id) for n in lords)],
            hint="The siege shows on his Fief tab, and on the castle's lord's.",
        ),
    ]
    if siege is not None:
        found += _walls_fields(
            "walls",
            "Damage levels left",
            rules.walls(siege),
            f"A whole wall has {rules.full_wall(siege)}.",
        )
        found.append(
            DialogField(
                "ended",
                "Ended",
                "select",
                siege.ended,
                options=[("No: it goes on", ""), *pairs(ENDINGS)],
            )
        )
    return found


def _four(values: dict[str, Any], key: str) -> list[int]:
    return [max(0, int(values.get(f"{key}_{i}") or 0)) for i in range(len(WALLS))]


def _army(saga: Saga, neighbour_id: str) -> int | None:
    """The combat groups a linked lord's title raises (None: no lord)."""
    lord = saga.neighbour(neighbour_id)
    return (
        armies.army_groups(lord) if lord is not None and lord.kind == "lord" else None
    )


def _write(saga: Saga, siege: Siege, values: dict[str, Any]) -> None:
    for key in (
        "name",
        "castle",
        "holder",
        "besieger",
        "season",
        "defenses",
        "supplies",
    ):
        setattr(siege, key, values.get(key) or getattr(siege, key))
    for key in (
        "year",
        "size",
        "miners",
        "sapper",
        "gunner",
        "counter_sapper",
        "engineer",
    ):
        setattr(siege, key, int(values.get(key) or 0))
    siege.enchanted, siege.moat = (
        bool(values.get("enchanted")),
        bool(values.get("moat")),
    )
    siege.engines = {
        kind: n
        for kind in rules.ENGINES
        if (n := int(values.get(f"engine_{kind}") or 0)) > 0
    }
    siege.besieger_walls = _four(values, "besieger_walls")
    siege.garrison_walls = _four(values, "garrison_walls")
    if "walls_0" in values:
        # No wall holds more than it had when the siege began.
        whole = rules.full_wall(siege)
        siege.walls = [min(whole, n) for n in _four(values, "walls")]
    for key in ("covenant_id", "castle_id", "besieger_id"):
        setattr(siege, key, values.get(key) or "")
    garrison, soldiers = values.get("garrison"), values.get("soldiers")
    if garrison is None:
        garrison = _army(saga, siege.castle_id) or 10
    if soldiers is None:
        soldiers = _army(saga, siege.besieger_id) or 0
    siege.garrison, siege.soldiers = int(garrison), int(soldiers)
    if "ended" in values:
        siege.ended = values.get("ended") or ""


def problem(values: dict[str, Any]) -> str | None:
    if (values.get("garrison") or 0) < 0 or (values.get("soldiers") or 0) < 0:
        return "A garrison can't be fewer than no groups."
    return None


def ops(saga: Saga, neighbour: Neighbour | None = None) -> SectionOps:
    """Add, Edit and Delete on the Sieges list, or (`neighbour`) on the
    sieges a lord holds out in or lays: Add there makes him the
    besieger."""

    def form(index: int | None) -> Command:
        siege = None if index is None else _listed(saga, neighbour)[index]

        def apply(values: dict[str, Any]) -> None:
            if siege is None:
                made = Siege(values["name"])
                _write(saga, made, values)
                saga.sieges.append(made)
            else:
                was = siege.ended
                _write(saga, siege, values)
                if siege.ended and not was:
                    record_ending(saga, siege)

        return Form(
            "Add a Siege" if siege is None else "Edit a Siege",
            lambda: fields(saga, siege, neighbour),
            apply,
            validate=problem,
            save_label="Add" if siege is None else "Save",
            help_id="sieges",
        )

    def remove(index: int) -> Command:
        listed = _listed(saga, neighbour)
        siege = listed[index] if 0 <= index < len(listed) else None
        if siege is None:
            return Refuse("Delete Siege", "Choose a siege first.")
        return Confirm(
            f"Delete the siege {escape(siege.name)}?", lambda: saga.sieges.remove(siege)
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=remove,
        rows=lambda: [s.name for s in _listed(saga, neighbour)],
    )


# -- the next event --


def _needs_wall(values: dict[str, Any]) -> bool:
    return values.get("event") in (
        rules.UNDERMINE,
        rules.ARTILLERY,
        rules.ESCALADE,
        rules.SEAL,
    )


def event_fields(siege: Siege) -> list[DialogField]:
    return [
        DialogField(
            "event",
            "Event",
            "select",
            rules.ARTILLERY if rules.engine_groups(siege) else rules.WAIT,
            options=pairs(rules.EVENTS),
            required=True,
        ),
        DialogField(
            "wall",
            "At the wall",
            "select",
            "0",
            options=[(w, str(i)) for i, w in enumerate(WALLS)],
            show_if=_needs_wall,
        ),
        DialogField(
            "target",
            "Against the besiegers'",
            "select",
            "Miners",
            options=pairs(rules.SALLY_TARGETS),
            show_if=lambda v: v.get("event") == rules.SALLY,
        ),
        DialogField(
            "units",
            "Groups of soldiers struck",
            "int",
            1,
            show_if=lambda v: (
                v.get("event") == rules.SALLY and v.get("target") == "Soldiers"
            ),
            hint="A won sally removes the units it targets (p. 115): as many "
            "as the troupe says.",
        ),
        DialogField(
            "result",
            "How the battlefield event went",
            "select",
            "won",
            options=[("The besiegers won", "won"), ("The garrison won", "lost")],
            show_if=lambda v: v.get("event") in (rules.ESCALADE, rules.SALLY),
            hint="Play it out as a battlefield event (Battles), then say who won it.",
        ),
    ]


def event_live(siege: Siege, values: dict[str, Any]) -> str:
    event = values.get("event")
    castle = rules.castle_of(siege)
    wall = int(values.get("wall") or 0)
    when = (
        f"Every {castle.interval().lower()}: the next event comes on day "
        f"{siege.days + rules.interval_days(siege)}."
    )
    if event == rules.UNDERMINE:
        bonus = rules.wall_bonus(siege, wall, against_mines=True)
        return (
            f"{when} Mine Attack {siege.sapper} + stress die against the castle's "
            f"{siege.counter_sapper} + Defense Bonus {bonus} + stress die."
        )
    if event == rules.ARTILLERY:
        groups = rules.engine_groups(siege)
        bonus = rules.wall_bonus(siege, wall)
        return (
            f"{when} {len(groups)} group(s) of engines, each {siege.gunner} + the "
            f"engine's Attack + stress die against {siege.engineer} + Defense Bonus "
            f"{bonus} + stress die."
        )
    if event == rules.ESCALADE:
        weight = rules.garrison(siege.garrison)[1]
        bonus = rules.wall_bonus(siege, wall)
        return (
            f"{when} A battlefield event at Ease Factor {battle.ease_factor(0)}+: the "
            f"garrison's Weight of Numbers (+{weight}) and the Defense Bonus (+{bonus}) "
            "stand in for numbers and ground (on the besiegers' side, as penalties)."
        )
    if event == rules.SALLY:
        return (
            f"{when} A battlefield event at Battle Ease Factor {rules.SALLY_EASE}, "
            "with neither ground nor numbers."
        )
    if event == rules.SEAL:
        left, whole = rules.walls(siege)[wall], rules.full_wall(siege)
        return (
            f"{when} Seal the Breach (CrTe 20 ritual) restores up to "
            f"{rules.SEAL_THE_BREACH} damage levels: the {WALLS[wall]} wall has "
            f"{left} of {whole}."
        )
    return f"{when} The stockade holds" + (
        "; supplies rolls come due as they fall." if rules.stockaded(siege) else "."
    )


def play_event(
    siege: Siege, values: dict[str, Any], rng: random.Random
) -> rules.Played:
    """The chosen event, played (each a Strategy of rules.siege)."""
    event = values.get("event") or rules.WAIT
    wall = int(values.get("wall") or 0)
    won = values.get("result") == "won"
    rules.begin(siege)
    plays = {
        rules.UNDERMINE: lambda: rules.undermine(siege, wall, rng),
        rules.ARTILLERY: lambda: rules.bombard(siege, wall, rng),
        rules.ESCALADE: lambda: rules.escalade(siege, wall, won),
        rules.SALLY: lambda: rules.sally(
            siege,
            values.get("target") or "Miners",
            not won,
            units=max(1, values.get("units") or 1),
        ),
        rules.SEAL: lambda: rules.seal_breach(siege, wall),
        rules.WAIT: lambda: rules.Played("The stockade holds."),
    }
    return plays[event]()


def next_event(
    saga: Saga, siege: Siege | None, rng: random.Random | None = None
) -> Command:
    """More's Next Siege Event: the besiegers' (or the garrison's) move at
    the castle's interval, then the supplies rolls the time brings."""
    if siege is None:
        return Refuse("Next Siege Event", "Choose a siege first.")
    if siege.ended:
        return Refuse(
            "Next Siege Event", f"The siege has ended: {escape(siege.ended)}."
        )
    dice = rng or random.Random()

    def apply(values: dict[str, Any]) -> list[str]:
        played = play_event(siege, values, dice)
        supplies = [] if siege.ended else rules.pass_interval(siege, dice, saga)
        siege.events.append(
            SiegeEvent(
                siege.days,
                values.get("event") or rules.WAIT,
                played.text,
                played.lines + supplies,
            )
        )
        return notes(played.text, *played.lines, *supplies, *record_ending(saga, siege))

    return Form(
        f"Next Siege Event: {escape(siege.name)}",
        lambda: event_fields(siege),
        apply,
        live=lambda v: event_live(siege, v),
        save_label="Play",
        help_id="sieges",
    )


def ended_when(siege: Siege) -> tuple[str, int]:
    """The season the siege has reached: its start, plus the full seasons
    it has run."""
    season, year = medallions.seasons_between(
        siege.season, siege.year, rules.seasons_run(siege) + 1, last=1
    )[0]
    return season, year


def record_ending(saga: Saga, siege: Siege) -> list[str]:
    """Once a siege has ended, a line in the Diary of its covenant, of the
    castle as a neighbour and of the besieging lord (each linked on the
    siege). Returns a note when it writes."""
    if not siege.ended or siege.recorded:
        return []
    siege.recorded = True
    covenant = saga.covenant(siege.covenant_id)
    linked = [
        n for i in (siege.castle_id, siege.besieger_id) if (n := saga.neighbour(i))
    ]
    season, year = ended_when(siege)
    count = diaries.write(
        year,
        season,
        siege.name,
        f"{siege.ended} after {time_text(siege.days)}: {castle_name(saga, siege) or 'the castle'}, "
        f"held by {siege.holder or 'its garrison'} against "
        f"{besieger_name(saga, siege) or 'the besiegers'}.",
        covenants=[covenant] if covenant else [],
        neighbours=linked,
    )
    return [f"Written in {count} Diar{'y' if count == 1 else 'ies'}."] if count else []


# -- what a siege shows --


def _count(n: int, noun: str) -> str:
    return f"{n} {noun}{'' if n == 1 else 's'}"


def info(saga: Saga, siege: Siege) -> str:
    """A siege in full, as markup."""
    castle = rules.castle_of(siege)
    left = rules.walls(siege)
    engines = ", ".join(
        f"{n} {k.lower()}{'s' if n > 1 else ''}" for k, n in siege.engines.items() if n
    )
    lines = [
        f"[b]{escape(siege.name)}[/]  [dim]begun {siege.season} {siege.year}[/]  "
        f"{escape(state_text(siege))}",
        f"[$label]Castle:[/] {escape(castle_name(saga, siege) or '(unnamed)')}, held by "
        f"{escape(siege.holder or '(nobody named)')}; Size {siege.size:+d}. Events "
        f"every {castle.interval().lower()}.",
        f"[$label]Garrison:[/] {siege.garrison} combat groups ({garrison_step(siege.garrison)})",
        f"[$label]Defenses:[/] {siege.defenses}, Defense Bonus +{castle.defense_bonus()}"
        + (" (a moat)" if siege.moat else ""),
        f"[$label]Supplies:[/] {siege.supplies}, Siege Conditions Bonus "
        f"+{castle.supplies_bonus()}; "
        + (
            f"in stockade, rolls against {castle.supplies_ease(rules.years_run(siege))}"
            if rules.stockaded(siege)
            else "not in stockade"
        ),
        "[$label]Walls:[/] "
        + ", ".join(
            f"{w} {n}/{rules.full_wall(siege)}"
            for w, n in zip(WALLS, left, strict=True)
        ),
        f"[$label]Besiegers:[/] {escape(besieger_name(saga, siege) or '(unnamed)')}: "
        f"{_count(siege.miners, 'unit')} of miners, {engines or 'no engines'}, "
        f"{_count(siege.soldiers, 'group')} of soldiers",
    ]
    if siege.events:
        hidden = len(siege.events) - 10
        lines.append(
            "[$label]Chronicle:[/]"
            + (
                f" [dim]({_count(hidden, 'earlier event')} not shown)[/]"
                if hidden > 0
                else ""
            )
        )
        lines += [
            f"  Day {e.day}: {escape(e.text)}"
            + "".join(f"\n    [dim]{escape(x)}[/]" for x in e.lines)
            for e in siege.events[-10:]
        ]
    lines.append(
        f"[dim]{SOURCE}. Living under siege: -2 Living Conditions for each year "
        "with a season of it.[/]"
    )
    return "\n".join(lines)


def info_for(saga: Saga, neighbour: Neighbour, index: int) -> str:
    """The `index`th siege a lord holds out in or lays, in full."""
    listed = involving(saga, neighbour)
    return info(saga, listed[index]) if index < len(listed) else ""
