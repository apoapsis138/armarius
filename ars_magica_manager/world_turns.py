"""The world turns: the yearly step. When Winter is played, Advance
Season asks one more question before the season is played out: what the
year brought beyond the covenants (a place's triggers and its aura, a
threat's stages, the towns' fairs, the loans the Tribunals are owed, and
the year's events with each neighbour), each line with a tick box. Only
the ticked lines are applied, and all of them go into one entry of the
saga's record (Saga.world_turns); deleting that entry undoes them.

Nothing is guessed: an attitude moves only by the change and reason the
storyguide gives, and the dice for an aura or a fair are rolled when the
question is asked, so what is shown is what is applied.

Each change is a small record (a dict, so it saves with the saga):
"set" a value at a path within a record, "append" an entry to a list
there, or give an attitude a "reason". Undoing one reverses it, unless
the value has been changed since, which is left alone and reported.

Pattern: Command, whose undo is its diary entry (each change keeps what
it replaced, a Memento of that one value)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from . import economics, neighbours, place_events, places, threats, towns, world
from .commands import Confirm, Form, SectionOps
from .form_spec import DialogField
from .grids import Grid
from .markup import escape
from .models import SEASONS, Attitude, Reason, Saga, WorldTurn, new_instance_id
from .rules import dice

#: The groups the review lists, in order.
PLACES, THREATS, NEIGHBOURS, TREASURY, ATTITUDES = (
    "Places",
    "Threats",
    "Neighbours",
    "Tribunal treasury",
    "Attitudes",
)
_GROUP_NOTES = {
    PLACES: "from each place's triggers and its aura",
    THREATS: "from each threat's dated stages",
    NEIGHBOURS: "each town's fairs: the income rolls",
    TREASURY: "loans the Tribunals are owed this year",
    ATTITUDES: "the year's events with each neighbour: you give the change "
    "and its reason",
}

#: An attitude's change, as the review offers it ("0": none).
CHANGES: tuple[str, ...] = ("0", "+1", "+2", "+3", "-1", "-2", "-3")


@dataclass
class Proposal:
    """One line of the review: what it says, the changes ticking it
    applies, and whether it starts ticked. An attitude line has no
    changes of its own: its change and reason are asked."""

    group: str
    text: str
    changes: list[dict[str, Any]] = field(default_factory=list)
    ticked: bool = True
    #: For an attitude line: the neighbour, the player covenant, and what
    #: happened between them this year.
    neighbour_id: str = ""
    covenant_id: str = ""
    events: list[str] = field(default_factory=list)


# -- changes --


def _record(saga: Saga, kind: str, record_id: str) -> Any:
    if kind == "neighbour":
        return saga.neighbour(record_id)
    if kind == "tribunal":
        return saga.tribunal(record_id)
    return None


def _step(target: Any, step: Any) -> Any:
    if isinstance(step, str) and step.startswith("#"):
        wanted = step[1:]
        return next(
            item
            for item in target
            if (item.get("id") if isinstance(item, dict) else item.id) == wanted
        )
    if isinstance(target, dict):
        return target[step]
    if isinstance(target, list):
        return target[int(step)]
    return getattr(target, step)


def _put(target: Any, step: Any, value: Any) -> None:
    if isinstance(target, (dict, list)):
        target[step] = value
    else:
        setattr(target, step, value)


def _get(target: Any, step: Any) -> Any:
    if isinstance(target, dict):
        return target.get(step)
    return _step(target, step)


def set_change(
    kind: str, record_id: str, path: list[Any], before: Any, after: Any
) -> dict[str, Any]:
    return {
        "op": "set",
        "record": kind,
        "id": record_id,
        "path": path,
        "before": before,
        "after": after,
    }


def append_change(
    kind: str, record_id: str, path: list[Any], value: Any
) -> dict[str, Any]:
    return {
        "op": "append",
        "record": kind,
        "id": record_id,
        "path": path,
        "value": value,
    }


def _parent(saga: Saga, change: dict[str, Any]) -> Any:
    target = _record(saga, change["record"], change["id"])
    if target is None:
        raise LookupError
    for step in change["path"][:-1]:
        target = _step(target, step)
    return target


def _list(saga: Saga, change: dict[str, Any]) -> list[Any]:
    parent = _parent(saga, change)
    last = change["path"][-1]
    found = _get(parent, last)
    if found is None:
        found = []
        _put(parent, last, found)
    return found


def apply_change(saga: Saga, change: dict[str, Any]) -> None:
    op = change["op"]
    if op == "set":
        parent = _parent(saga, change)
        last = change["path"][-1]
        # A key the record didn't have is taken out again on undo.
        if isinstance(parent, dict) and last not in parent:
            change["absent"] = True
        _put(parent, last, change["after"])
    elif op == "append":
        _list(saga, change).append(change["value"])
    elif op == "reason":
        record = _record(saga, change["record"], change["id"])
        attitude = world.attitude_toward(record, change["covenant_id"])
        if attitude is None:
            attitude = Attitude(change["covenant_id"])
            record.attitudes.append(attitude)
        attitude.reasons.append(Reason(**change["reason"]))


def undo_change(saga: Saga, change: dict[str, Any]) -> bool:
    """Reverse `change`; False (nothing done) when what it set has been
    changed or removed since."""
    try:
        op = change["op"]
        if op == "set":
            parent = _parent(saga, change)
            last = change["path"][-1]
            if _get(parent, last) != change["after"]:
                return False
            if change.get("absent") and isinstance(parent, dict):
                del parent[last]
            else:
                _put(parent, last, change["before"])
            return True
        if op == "append":
            entries = _list(saga, change)
            if change["value"] not in entries:
                return False
            entries.remove(change["value"])
            return True
        if op == "reason":
            record = _record(saga, change["record"], change["id"])
            attitude = world.attitude_toward(record, change["covenant_id"])
            wanted = change["reason"]["id"]
            if attitude is None or not any(r.id == wanted for r in attitude.reasons):
                return False
            attitude.reasons = [r for r in attitude.reasons if r.id != wanted]
            return True
    except LookupError, StopIteration, IndexError, KeyError, AttributeError:
        return False
    return False


# -- what the year brought --


def _diary_line(year: int, season: str, text: str) -> dict[str, Any]:
    return {"year": year, "season": season, "text": text}


def _places(saga: Saga, year: int, rng: random.Random) -> list[Proposal]:
    found = []
    for place in places.all_places(saga):
        for trigger in place_events.triggers(place):
            season = place_events.comes_in(trigger, year)
            if season is None:
                continue
            what = trigger.get("what") or trigger["name"]
            found.append(
                Proposal(
                    PLACES,
                    f"{place.name}: {trigger['name']}",
                    [
                        append_change(
                            "neighbour",
                            place.id,
                            ["details", "diary"],
                            _diary_line(year, season, what),
                        )
                    ],
                )
            )
        rolled = place_events.aura_roll(saga, place, rng)
        if rolled is not None:
            total, rises = rolled
            before = int(place.details.get("aura") or 0)
            if rises:
                text = (
                    f"The aura rose to Magic {before + 1} ({total} against "
                    f"{place_events.RAISE_EASE})."
                )
                found.append(
                    Proposal(
                        PLACES,
                        f"{place.name}: aura {before} → {before + 1} (rolled {total})",
                        [
                            set_change(
                                "neighbour",
                                place.id,
                                ["details", "aura"],
                                place.details.get("aura"),
                                before + 1,
                            ),
                            append_change(
                                "neighbour",
                                place.id,
                                ["details", "diary"],
                                _diary_line(year, SEASONS[-1], text),
                            ),
                        ],
                    )
                )
    return found


def _threats(saga: Saga, year: int) -> list[Proposal]:
    found = []
    end = year * len(SEASONS) + len(SEASONS) - 1
    for threat in saga.neighbours:
        if threat.kind != "threat" or not threats.by_date(threat):
            continue
        for index, stage in enumerate(threats.stages(threat)):
            if (stage.get("outcome") or threats.PENDING) != threats.PENDING:
                continue
            when = threats.stage_order(stage)
            if when is None or when > end:
                continue
            found.append(
                Proposal(
                    THREATS,
                    f"{threat.name}: {stage['title']} has come",
                    [
                        set_change(
                            "neighbour",
                            threat.id,
                            ["details", "stages", index, "outcome"],
                            stage.get("outcome"),
                            "Happened",
                        )
                    ],
                )
            )
    return found


def _fairs(saga: Saga, year: int, rng: random.Random) -> list[Proposal]:
    found = []
    for town in saga.neighbours:
        if town.kind != "town":
            continue
        for index, fair in enumerate(towns.fairs(town)):
            covenant = saga.covenant(fair.get("covenant_id"))
            if covenant is None:
                continue
            die = dice.stress_die(rng, saga=saga)
            effect = towns.effect_of(die)
            before = towns.fair_income(fair)
            after = economics.projected_income(before, effect)
            shown = "a botch" if die.botched else str(die.value)
            last = (
                f"{year}: {effect} {economics.income_multiplier_text(effect)}, "
                f"{before} to {after}"
            )
            found.append(
                Proposal(
                    NEIGHBOURS,
                    f"{town.name} fair: {covenant.name}'s income {before} → {after} "
                    f"(rolled {shown})",
                    [
                        set_change(
                            "neighbour",
                            town.id,
                            ["details", "fairs", index, "income"],
                            fair.get("income"),
                            after,
                        ),
                        set_change(
                            "neighbour",
                            town.id,
                            ["details", "fairs", index, "last"],
                            fair.get("last"),
                            last,
                        ),
                    ],
                )
            )
    return found


def _loans(saga: Saga, year: int) -> list[Proposal]:
    found = []
    for tribunal in saga.tribunals:
        for entry in tribunal.treasury:
            if entry.kind != "loan" or entry.paid or entry.due_year is None:
                continue
            if entry.due_year > year:
                continue
            found.append(
                Proposal(
                    TREASURY,
                    f"{tribunal.name}: the loan to {entry.who or 'someone'} "
                    f"({entry.amount:g}) was repaid",
                    [
                        set_change(
                            "tribunal",
                            tribunal.id,
                            ["treasury", f"#{entry.id}", "paid"],
                            False,
                            True,
                        )
                    ],
                    ticked=False,
                )
            )
    return found


def _events(saga: Saga, neighbour: Any, covenant: Any, year: int) -> list[str]:
    """What happened this year between `neighbour` and `covenant`: the
    favours begun or repaid, and the covenant's diary entries naming it."""
    found = []
    for favour in neighbour.favours:
        if favour.year == year:
            found.append(f"favour: {favour.what}")
        elif favour.repaid_year == year:
            found.append(f"favour repaid: {favour.what}")
    name = neighbour.name.lower()
    for entry in covenant.diary:
        if entry.year == year and name in f"{entry.name} {entry.details}".lower():
            found.append(entry.name or entry.details)
    return found


def _attitudes(saga: Saga, year: int) -> list[Proposal]:
    found = []
    for neighbour in saga.neighbours:
        if not neighbours.kind_of(neighbour).attitude:
            continue
        for covenant in world.player_covenants(saga):
            events = _events(saga, neighbour, covenant, year)
            if events:
                found.append(
                    Proposal(
                        ATTITUDES,
                        f"{neighbour.name}'s attitude to {covenant.name}",
                        ticked=False,
                        neighbour_id=neighbour.id,
                        covenant_id=covenant.id,
                        events=events,
                    )
                )
    return found


def proposals(saga: Saga, rng: random.Random) -> list[Proposal]:
    """Everything the year that is ending brought, to review."""
    year = saga.current_year
    return [
        *_places(saga, year, rng),
        *_threats(saga, year),
        *_fairs(saga, year, rng),
        *_loans(saga, year),
        *_attitudes(saga, year),
    ]


# -- the review --


def review_fields(found: list[Proposal]) -> list[DialogField]:
    fields: list[DialogField] = []
    group = ""
    for index, proposal in enumerate(found):
        if proposal.group != group:
            group = proposal.group
            fields.append(
                DialogField(
                    f"_group_{index}",
                    "",
                    "info",
                    f"{group.upper()}: {_GROUP_NOTES[group]}",
                )
            )
        if proposal.group == ATTITUDES:
            fields += [
                DialogField(
                    f"_events_{index}",
                    "",
                    "info",
                    f"{proposal.text}: this year, " + "; ".join(proposal.events),
                ),
                DialogField(
                    f"change_{index}",
                    "Change",
                    "select",
                    "0",
                    options=[("No change" if c == "0" else c, c) for c in CHANGES],
                    required=True,
                ),
                DialogField(
                    f"reason_{index}",
                    "Reason",
                    "text",
                    "",
                    show_if=lambda v, index=index: v.get(f"change_{index}") != "0",
                    placeholder="why it moved",
                ),
            ]
        else:
            fields += [
                DialogField(f"_line_{index}", "", "info", proposal.text),
                DialogField(f"tick_{index}", "Apply", "check", proposal.ticked),
            ]
    return fields


def _chosen(
    saga: Saga, found: list[Proposal], values: dict[str, Any]
) -> list[tuple[str, list[dict[str, Any]]]]:
    """The ticked lines (and the attitudes given a change), each with its
    changes."""
    year = saga.current_year
    chosen = []
    for index, proposal in enumerate(found):
        if proposal.group == ATTITUDES:
            change = int(values.get(f"change_{index}") or 0)
            if not change:
                continue
            reason = (values.get(f"reason_{index}") or "").strip()
            chosen.append(
                (
                    f"{proposal.text}: {change:+d}, {reason}",
                    [
                        {
                            "op": "reason",
                            "record": "neighbour",
                            "id": proposal.neighbour_id,
                            "covenant_id": proposal.covenant_id,
                            "reason": {
                                "what": reason,
                                "change": change,
                                "year": year,
                                "season": SEASONS[-1],
                                "id": new_instance_id(),
                            },
                        }
                    ],
                )
            )
        elif values.get(f"tick_{index}"):
            chosen.append((proposal.text, proposal.changes))
    return chosen


def _problem(found: list[Proposal], values: dict[str, Any]) -> str | None:
    for index, proposal in enumerate(found):
        if proposal.group != ATTITUDES or values.get(f"change_{index}") in (None, "0"):
            continue
        if not (values.get(f"reason_{index}") or "").strip():
            return f"Give the reason {proposal.text} changed: the app doesn't guess."
    return None


def title(year: int) -> str:
    return f"The World Turns: Winter {year}"


def entry_title(turn: WorldTurn) -> str:
    return f"The world turns, {turn.season} {turn.year}"


def review(saga: Saga, found: list[Proposal], then: Any) -> Form:
    """The review of `found`: Apply applies the ticked lines into one
    entry of the saga's record, then runs `then()` (the season played
    out)."""
    year = saga.current_year

    def live(values: dict[str, Any]) -> str:
        count = sum(len(changes) > 0 for _t, changes in _chosen(saga, found, values))
        return (
            f"[b]{count} change{'' if count == 1 else 's'}[/] go into the saga's "
            f"record as one entry, [i]The world turns, Winter {year}[/]. "
            "Delete that entry (Seasons) to undo them."
        )

    def apply(values: dict[str, Any]) -> Any:
        record(saga, _chosen(saga, found, values))
        return then()

    return Form(
        title(year),
        lambda: review_fields(found),
        apply,
        validate=lambda values: _problem(found, values),
        live=live,
        save_label="Apply",
        help_id="world-turns",
    )


def record(
    saga: Saga, chosen: list[tuple[str, list[dict[str, Any]]]]
) -> WorldTurn | None:
    """Apply the chosen lines and keep them as one entry (None: nothing
    chosen)."""
    if not chosen:
        return None
    turn = WorldTurn(saga.current_year, SEASONS[-1])
    for text, changes in chosen:
        for change in changes:
            apply_change(saga, change)
        turn.lines.append(text)
        turn.changes += changes
    saga.world_turns.append(turn)
    places.sync(saga)
    return turn


def undo(saga: Saga, turn: WorldTurn) -> list[str]:
    """Delete `turn`, undoing its changes (newest first); returns a note
    for each change left alone because it was changed since."""
    left = [
        change for change in reversed(turn.changes) if not undo_change(saga, change)
    ]
    saga.world_turns.remove(turn)
    places.sync(saga)
    if not left:
        return []
    return [
        f"{len(left)} change{'' if len(left) == 1 else 's'} had been changed "
        "since and were left as they are."
    ]


# -- the list on the Seasons sheet --


def turns_title(saga: Saga) -> str:
    return f"The World Turned ({len(saga.world_turns)})"


def turn_rows(saga: Saga) -> list[tuple[int | None, str]]:
    turns = list(reversed(saga.world_turns))
    if not turns:
        return [
            (
                None,
                "[$label]Nothing yet: each Winter, Advance Season asks what the "
                "year brought.[/]",
            )
        ]
    return [
        (
            index,
            f"{escape(entry_title(turn))}: {len(turn.lines)} "
            f"change{'' if len(turn.lines) == 1 else 's'}",
        )
        for index, turn in enumerate(turns)
    ]


def turns_grid(saga: Saga) -> Grid:
    """Each entry, newest first, with how many changes it made."""
    turns = list(reversed(saga.world_turns))
    return Grid(
        ["Entry", "Changes"],
        [[entry_title(t), str(len(t.lines))] for t in turns],
        list(range(len(turns))),
        "Nothing yet: each Winter, Advance Season asks what the year brought.",
    )


def turn_text(turn: WorldTurn) -> str:
    lines = [f"[b]{escape(entry_title(turn))}[/]"]
    lines += [f"  {escape(line)}" for line in turn.lines]
    lines.append("[$label]Delete it to undo these changes.[/]")
    return "\n".join(lines)


def turn_ops(saga: Saga) -> SectionOps:
    """Delete on The World Turned: undo the chosen entry (newest first)."""

    def remove(row: int) -> Confirm:
        turn = list(reversed(saga.world_turns))[row]
        return Confirm(
            f"Delete {escape(entry_title(turn))}? Its {len(turn.lines)} "
            f"change{'' if len(turn.lines) == 1 else 's'} are undone.",
            lambda: undo(saga, turn),
            yes_label="Delete and undo",
        )

    return SectionOps(
        remove=remove,
        rows=lambda: [entry_title(t) for t in reversed(saga.world_turns)],
    )
