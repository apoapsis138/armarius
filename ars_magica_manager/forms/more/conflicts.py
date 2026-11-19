"""More in Conflicts: battles, fights and sieges."""

from __future__ import annotations

from ...sections import FIGHTS_SECTION
from .entry import MoreAction
from .rules import with_morale_rules

#: This area's actions, in the order More lists them.
ENTRIES: tuple[MoreAction, ...] = (
    MoreAction(
        "conflict_battle_event",
        "b",
        "Battle Event",
        section="section-conflict-battles",
        on_page=False,
    ),
    MoreAction(
        "battle_muster",
        "u",
        "Muster and Aftermath",
        section="section-conflict-battles",
        on_page=False,
    ),
    MoreAction(
        "fight_options", "o", "Combat Options", section=FIGHTS_SECTION, on_page=False
    ),
    MoreAction("next_blow", "n", "Next Blow", section=FIGHTS_SECTION, on_page=False),
    MoreAction("next_round", "r", "Next Round", section=FIGHTS_SECTION, on_page=False),
    MoreAction(
        "add_combatant", "a", "Add Combatant", section=FIGHTS_SECTION, on_page=False
    ),
    MoreAction(
        "edit_combatant", "e", "Edit Combatant", section=FIGHTS_SECTION, on_page=False
    ),
    MoreAction(
        "remove_combatant",
        "v",
        "Remove Combatant",
        section=FIGHTS_SECTION,
        on_page=False,
    ),
    MoreAction(
        "form_group", "g", "Form a Group", section=FIGHTS_SECTION, on_page=False
    ),
    MoreAction(
        "break_group", "u", "Break up a Group", section=FIGHTS_SECTION, on_page=False
    ),
    MoreAction(
        "restart_fight",
        "t",
        "Restart the Fight",
        section=FIGHTS_SECTION,
        on_page=False,
    ),
    MoreAction(
        "group_morale",
        "m",
        "Discipline or Morale",
        section=FIGHTS_SECTION,
        on_page=False,
        in_section=with_morale_rules(FIGHTS_SECTION),
    ),
    MoreAction(
        "rally_group",
        "l",
        "Rally a Group",
        section=FIGHTS_SECTION,
        on_page=False,
        in_section=with_morale_rules(FIGHTS_SECTION),
    ),
    MoreAction(
        "next_siege_event",
        "n",
        "Next Siege Event",
        section="section-sieges",
        on_page=False,
    ),
    MoreAction(
        "siege_actions", "a", "Siege Actions", section="section-sieges", on_page=False
    ),
)
