"""Discipline and Morale for combat groups (Lords of Men pp. 134-135), the
Morale and Discipline saga option: a group tempted to break formation
makes a Discipline roll, one when bad things happen a Morale roll, both
the leader's Presence + Leadership + stress die, + the lowest Loyal (for
Discipline) or Brave (Morale) when every member has a positive one.

Failing either disorders the group. A trained group disordered fights as
an untrained one; failing a second Discipline check it fights as a
disordered untrained group, only half its attacks hitting (rounded up).
An untrained group disordered is that already. Only a Morale failure
routs a disordered group, which then tries to disengage and flee. The
leader rallies a group as an action (Presence + Leadership + stress die):
a routed group becomes disordered, a disordered one steady, one step at
a time. A group with no leader fails every check.

Pattern: State: each of the four states says how the group attacks (a
dict of the states' rules).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import FightGroup
from . import combat_options as co

SOURCE = "Lords of Men, Morale and Discipline, pp. 134-135"

STEADY, DISORDERED, BROKEN, ROUTED = "", "disordered", "disordered_untrained", "routed"


@dataclass(frozen=True)
class State:
    """How a group in this state fights: as a trained group still, with
    half its attacks hitting, or not at all (it flees)."""

    label: str
    trained_counts: bool
    half_hits: bool
    flees: bool


STATES: dict[str, State] = {
    STEADY: State("steady", True, False, False),
    DISORDERED: State("disordered", False, False, False),
    BROKEN: State("disordered, as an untrained group", False, True, False),
    ROUTED: State("routed", False, False, True),
}

DISCIPLINE, MORALE = "discipline", "morale"

#: The Ease Factors are Combat Options' tables (rules.combat_options).
DISCIPLINE_EASE = co.DISCIPLINE
MORALE_EASE = co.MORALE
RALLY_EASE = co.RALLY
rally_ease = co.rally_ease
#: The two Morale checks the fight can see coming (p. 134).
LEADER_DOWN_EASE = co.MORALE["Vanguard or leader down"]
ALL_WOUNDED_EASE = co.MORALE["Every member at -3 or worse"]


def state_of(group: FightGroup) -> State:
    return STATES.get(group.state, STATES[STEADY])


def after_failure(group: FightGroup, check: str) -> str:
    """The state a failed check leaves the group in (p. 134-135)."""
    if group.state == STEADY:
        return DISORDERED
    if check == MORALE:
        return ROUTED
    # A second Discipline failure: a trained group now fights as a
    # disordered untrained one; an untrained one is that already.
    if group.state == DISORDERED and group.trained:
        return BROKEN
    return group.state


def after_rally(group: FightGroup) -> str:
    """One step up: routed to disordered, disordered to steady (p. 135)."""
    return DISORDERED if group.state == ROUTED else STEADY


def hits(group: FightGroup | None, attackers: int) -> int:
    """How many of a group's attacks can hit: half (rounded up) for one
    fighting as a disordered untrained group (p. 135)."""
    if group is None:
        return attackers
    state = state_of(group)
    if state.half_hits or (group.state == DISORDERED and not group.trained):
        return -(-attackers // 2)
    return attackers
