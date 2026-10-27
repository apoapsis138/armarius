"""The saga's Conflicts, its battles, fights and sieges, as both front-ends show
them: the two lists' Add, Edit and Delete, and the More commands that act
on a chosen fight or siege, by action name.

Pattern: COMMANDS is a dict of command builders keyed by the More menu's
action names, so the terminal's handlers and the desktop's buttons look
up the same step (the Command pattern, reduced to a dict of functions).
"""

from __future__ import annotations

from collections.abc import Callable

from . import (
    battle_muster,
    battles,
    combat_options_form,
    fight_morale,
    fights,
    siege_actions,
    sieges,
)
from .commands import Command, Refuse, SectionOps
from .models import Saga
from .references import Fact
from .sections import CONFLICT_BATTLES_SECTION, FIGHTS_SECTION, SIEGES_SECTION

#: Each More command on a chosen fight (by its row) or siege.
COMMANDS: dict[str, Callable[[Saga, int], Command]] = {
    "conflict_battle_event": lambda saga, row: battles.event_form(
        saga, battles.battle_of(saga, row)
    ),
    "battle_muster": lambda saga, row: battle_muster.muster(
        saga, battles.battle_of(saga, row)
    ),
    "next_blow": lambda saga, row: fights.next_blow(saga, fights.fight_of(saga, row)),
    "next_round": lambda saga, row: fights.next_round(saga, fights.fight_of(saga, row)),
    "add_combatant": lambda saga, row: fights.add_combatant(
        saga, fights.fight_of(saga, row)
    ),
    "edit_combatant": lambda saga, row: fights.edit_combatant(
        saga, fights.fight_of(saga, row)
    ),
    "remove_combatant": lambda saga, row: fights.remove_combatant(
        saga, fights.fight_of(saga, row)
    ),
    "form_group": lambda saga, row: fights.form_group(saga, fights.fight_of(saga, row)),
    "break_group": lambda saga, row: fights.break_group(
        saga, fights.fight_of(saga, row)
    ),
    "restart_fight": lambda saga, row: fights.restart(saga, fights.fight_of(saga, row)),
    "fight_options": lambda saga, row: combat_options_form.options_form(
        saga, fights.fight_of(saga, row)
    ),
    "group_morale": lambda saga, row: fight_morale.check_form(
        saga, fights.fight_of(saga, row)
    ),
    "rally_group": lambda saga, row: fight_morale.rally_form(
        saga, fights.fight_of(saga, row)
    ),
    "next_siege_event": lambda saga, row: sieges.next_event(
        saga, sieges.siege_of(saga, row)
    ),
    "siege_actions": lambda saga, row: siege_actions.actions(
        saga, sieges.siege_of(saga, row)
    ),
}
#: The section each command's row is chosen in.
SECTION_OF = {
    action: SIEGES_SECTION
    if action in ("next_siege_event", "siege_actions")
    else CONFLICT_BATTLES_SECTION
    if action in ("conflict_battle_event", "battle_muster")
    else FIGHTS_SECTION
    for action in COMMANDS
}


def ops(saga: Saga) -> dict[str, SectionOps]:
    """Add, Edit and Delete on the Battles, Fights and Sieges lists."""
    return {
        CONFLICT_BATTLES_SECTION: battles.ops(saga),
        FIGHTS_SECTION: fights.ops(saga),
        SIEGES_SECTION: sieges.ops(saga),
    }


def command(saga: Saga, action: str, row: int | None) -> Command:
    """The More command `action` on the chosen row of its list."""
    if row is None:
        noun = {SIEGES_SECTION: "siege", CONFLICT_BATTLES_SECTION: "battle"}.get(
            SECTION_OF.get(action, ""), "fight"
        )
        return Refuse(action.replace("_", " ").title(), f"Choose a {noun} first.")
    return COMMANDS[action](saga, row)


def header_facts(saga: Saga) -> list[Fact]:
    """The Conflicts' figures: fights and sieges, and how many go on."""
    return [
        Fact("Battles", str(len(saga.battles))),
        Fact("Fights", str(len(saga.fights))),
        Fact("Fights going on", str(sum(1 for f in saga.fights if not f.over))),
        Fact("Sieges", str(len(saga.sieges))),
        Fact("Sieges going on", str(sum(1 for s in saga.sieges if not s.ended))),
    ]
