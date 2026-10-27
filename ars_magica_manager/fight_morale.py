"""More's Discipline or Morale and Rally a Group on a fight, under the
Morale and Discipline option (Lords of Men pp. 134-135; the rules are
rules.group_morale's): the leader's Presence + Leadership + stress die,
the group's state changed by the result, and the fight's chronicle.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from .commands import Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Fight, FightEntry, FightGroup, Saga
from .rules import combat_options as co
from .rules import dice, options
from .rules import fight as fight_rules
from .rules import group_morale as gm

CHECK_TITLE = "Discipline or Morale"
RALLY_TITLE = "Rally a Group"
HELP_ID = "group-morale"
OTHER = "Another cause (type its Ease Factor)"


def _groups(fight: Fight, *, rallying: bool = False) -> list[tuple[str, str]]:
    return [
        (
            escape(g.name or "A group")
            + (f" ({gm.state_of(g).label})" if g.state else ""),
            g.id,
        )
        for side in fight.sides
        for g in side.groups
        if not rallying or g.state
    ]


def _group(fight: Fight, group_id: Any) -> FightGroup | None:
    return next((g for s in fight.sides for g in s.groups if g.id == group_id), None)


def _unit(saga: Saga, fight: Fight, group: FightGroup) -> fight_rules.Unit | None:
    return fight_rules.units(saga, fight).get(group.id)


def _leader(unit: fight_rules.Unit) -> fight_rules.Fighter | None:
    group = unit.group
    found = next(
        (f for f in unit.fighters if group is not None and f.id == group.leader),
        None,
    )
    return found if found is not None and not found.down() else None


def leader_total(unit: fight_rules.Unit) -> int | None:
    """The leader's Presence + Leadership (None: no leader standing, so
    every check fails, p. 135)."""
    leader = _leader(unit)
    if leader is None:
        return None
    presence = (
        leader.character.characteristics.presence if leader.character is not None else 0
    )
    return presence + leader.figures().leadership


def trait_bonus(unit: fight_rules.Unit, trait: str) -> int:
    """The lowest positive Loyal (Discipline) or Brave (Morale) when every
    member has one (p. 134): none for a member with no sheet."""
    members = [f.character for f in unit.standing()]
    if not members or any(m is None for m in members):
        return 0
    return co.trait_bonus([m for m in members if m is not None], trait)


def _check_fields(fight: Fight) -> list[DialogField]:
    groups = _groups(fight)

    def is_check(kind: str) -> Callable[[dict[str, Any]], bool]:
        return lambda v: (v.get("check") or gm.MORALE) == kind

    return [
        DialogField(
            "group", "Group", "select", groups[0][1] if groups else None, options=groups
        ),
        DialogField(
            "check",
            "Check",
            "select",
            gm.MORALE,
            options=[("Morale", gm.MORALE), ("Discipline", gm.DISCIPLINE)],
        ),
        DialogField(
            "morale_cause",
            "Cause",
            "select",
            next(iter(gm.MORALE_EASE)),
            options=[(f"{c} ({e})", c) for c, e in gm.MORALE_EASE.items()]
            + [(OTHER, OTHER)],
            show_if=is_check(gm.MORALE),
        ),
        DialogField(
            "discipline_cause",
            "Cause",
            "select",
            next(iter(gm.DISCIPLINE_EASE)),
            options=[(f"{c} ({e})", c) for c, e in gm.DISCIPLINE_EASE.items()]
            + [(OTHER, OTHER)],
            show_if=is_check(gm.DISCIPLINE),
        ),
        DialogField(
            "ease",
            "Ease Factor",
            "int",
            6,
            show_if=lambda v: (
                OTHER in (v.get("morale_cause"), v.get("discipline_cause"))
            ),
        ),
        DialogField("die", "Stress die", "optint", None, hint="Blank: rolled."),
    ]


def _ease(values: dict[str, Any]) -> int:
    check = values.get("check") or gm.MORALE
    table = gm.MORALE_EASE if check == gm.MORALE else gm.DISCIPLINE_EASE
    cause = values.get(f"{check}_cause") or next(iter(table))
    return table.get(cause, values.get("ease") or 0)


def _roll(saga: Saga, rng: random.Random, typed: Any) -> tuple[int, bool]:
    if typed is not None:
        return int(typed), False
    die = dice.stress_die(rng, 1, saga=saga)
    return die.value, die.botched


def check_form(
    saga: Saga, fight: Fight | None, rng: random.Random | None = None
) -> Form | Refuse:
    """Discipline or Morale for one of the fight's groups (p. 134)."""
    if fight is None:
        return Refuse(CHECK_TITLE, "Choose a fight first.")
    if not options.is_on(saga, options.MORALE_DISCIPLINE):
        return Refuse(CHECK_TITLE, "Turn on Morale and Discipline in Edit Saga.")
    if not _groups(fight):
        return Refuse(CHECK_TITLE, "The fight has no group to check.")
    dice_ = rng or random.Random()

    def apply(values: dict[str, Any]) -> list[str]:
        group = _group(fight, values.get("group"))
        if group is None:
            return notes("That group is gone.")
        unit = _unit(saga, fight, group)
        check = values.get("check") or gm.MORALE
        ease = _ease(values)
        lead = leader_total(unit) if unit is not None else None
        word = "Morale" if check == gm.MORALE else "Discipline"
        if unit is None or lead is None:
            held, text = False, f"{group.name} has no leader: its {word} check fails"
        else:
            bonus = trait_bonus(unit, "Brave" if check == gm.MORALE else "Loyal")
            die, botched = _roll(saga, dice_, values.get("die"))
            total = lead + bonus + die
            held = not botched and total >= ease
            text = (
                f"{group.name}'s {word}: Presence + Leadership {lead}"
                + (f" + {bonus}" if bonus else "")
                + f" + die {die} = {total} against {ease}"
            )
        if held:
            text += ": it holds."
        else:
            group.state = gm.after_failure(group, check)
            text += f": it is {gm.state_of(group).label}."
        fight.log.append(FightEntry(fight.round, text))
        return notes(escape(text))

    return Form(
        CHECK_TITLE,
        lambda: _check_fields(fight),
        apply,
        save_label="Roll",
        help_id=HELP_ID,
    )


def _casualties(unit: fight_rules.Unit) -> int:
    """Members with a Medium Wound or worse, unconscious or out (p. 135)."""
    return sum(1 for f in unit.fighters if f.down() or f.wound_penalty() <= -3)


def rally_form(
    saga: Saga, fight: Fight | None, rng: random.Random | None = None
) -> Form | Refuse:
    """Rally a disordered or routed group, one step (p. 135)."""
    if fight is None:
        return Refuse(RALLY_TITLE, "Choose a fight first.")
    groups = _groups(fight, rallying=True)
    if not groups:
        return Refuse(RALLY_TITLE, "No group is disordered or routed.")
    dice_ = rng or random.Random()

    def apply(values: dict[str, Any]) -> list[str]:
        group = _group(fight, values.get("group"))
        if group is None:
            return notes("That group is gone.")
        unit = _unit(saga, fight, group)
        lead = leader_total(unit) if unit is not None else None
        if unit is None or lead is None:
            return notes(escape(f"{group.name} has no leader standing to rally it."))
        situation = values.get("situation") or next(iter(gm.RALLY_EASE))
        ease = gm.rally_ease(situation, _casualties(unit), len(unit.fighters))
        die, botched = _roll(saga, dice_, values.get("die"))
        total = lead + die
        text = f"Rallying {group.name}: {lead} + die {die} = {total} against {ease}"
        if not botched and total >= ease:
            group.state = gm.after_rally(group)
            text += f": it is {gm.state_of(group).label}."
        else:
            text += ": it doesn't rally."
        fight.log.append(FightEntry(fight.round, text))
        return notes(escape(text))

    return Form(
        RALLY_TITLE,
        lambda: [
            DialogField("group", "Group", "select", groups[0][1], options=groups),
            DialogField(
                "situation",
                "Its situation",
                "select",
                "Engaged in melee",
                options=[(f"{s} ({e})", s) for s, e in gm.RALLY_EASE.items()],
                hint="+1 with casualties, +3 at half or more (worked out).",
            ),
            DialogField("die", "Stress die", "optint", None, hint="Blank: rolled."),
        ],
        apply,
        save_label="Rally",
        help_id=HELP_ID,
    )


def disorder_army(fight: Fight, side: int, spirit: str) -> None:
    """A battle's army disordered or routed carries into its event's fight:
    each of its groups starts so (Lords of Men p. 106)."""
    state = gm.ROUTED if spirit == "routed" else gm.DISORDERED
    for group in fight.sides[side].groups:
        group.state = state
