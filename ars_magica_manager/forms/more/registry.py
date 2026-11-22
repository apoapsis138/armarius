"""The registry: one MoreAction per More and New action (the area modules
beside this one hold them), and what the menus, the pages and the
front-ends read from it -- each action's menu line, the one section it is
offered in, where pages set it out, its first step, what it changes -- and
`available`, which asks the generic gates and then the action's own rule.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import replace
from types import MappingProxyType

from ... import action_books, deeds, viewing
from ...actions import CREATE_PLACES, ActionFacts, MenuItem, NodeKind
from ...commands import Command
from ..menu_refresh import Refresh
from ..menu_steps import interests_command
from ..page import Page
from . import (
    character,
    conflicts,
    covenant,
    familiar,
    laboratory,
    new,
    records,
    region,
    saga,
)
from .entry import MoreAction
from .rules import RECORD_RULES, SECTION_RULES, drafting

#: The order the menus and pages list the actions in (New first).
ORDER: tuple[str, ...] = (
    "create_covenant",
    "create_character",
    "create_laboratory",
    "create_familiar",
    "create_tribunal",
    "create_neighbour",
    "create_creature",
    "restore",
    "improve",
    "instill_effect",
    "use_charge",
    "use_effect",
    "perform_ritual",
    "share_spell",
    "boost_spell",
    "give",
    "give_silver",
    "lab_text_access",
    "edit_traditions",
    "disputatio",
    "hedge_cast",
    "galdor_conjure",
    "galdor_bargain",
    "galdor_bind",
    "edit_fatigue",
    "take_harm",
    "recovery_roll",
    "end_session",
    "what_changed",
    "open_session",
    "cast_glance",
    "begin_session",
    "close_session",
    "read_chronicle",
    "send_message",
    "set_scene",
    "end_scene",
    "show_at_session",
    "show_record",
    "my_handouts",
    "player_handouts",
    "withdraw_show",
    "open_show",
    "sheet_roll",
    "teaching_requests",
    "study_path",
    "tourney_season",
    "melee_event",
    "command_beast",
    "place_aging_points",
    "resolve_twilight",
    "disguise_roll",
    "trait_roll",
    "familiar_trait_roll",
    "edit_familiar_fatigue",
    "import_data",
    "research_bonuses",
    "export_record",
    "export_markdown",
    "edit_interests",
    "export_saga",
    "export_cult",
    "export_pack",
    "host_saga",
    "stop_hosting",
    "update_record",
    "toggle_mode",
    "promote",
    "demote",
    "creation_worksheet",
    "set_date",
    "undo_season",
    "downtime_run",
    "previously_on",
    "edit_arms",
    "withdraw_case",
    "war_end",
    "neutralize_shard",
    "tribunal_longevity",
    "roll_fair",
    "court_roll",
    "roll_table",
    "battle_event",
    "redeem_gratitude",
    "buy_manor",
    "assart",
    "winter_roll",
    "settle_inheritance",
    "conflict_battle_event",
    "battle_muster",
    "fight_options",
    "next_blow",
    "next_round",
    "add_combatant",
    "edit_combatant",
    "remove_combatant",
    "form_group",
    "break_group",
    "restart_fight",
    "group_morale",
    "rally_group",
    "next_siege_event",
    "siege_actions",
    "found_covenant",
    "begin_story",
    "delay_threat",
    "grow_story",
    "merge_doubles",
    "reveal",
    "conceal",
    "mark_unknown",
    "player_view",
    "assign_storyguide",
    "reveal_secret",
    "conceal_secret",
    "split_secret",
    "plan_goal",
    "take_up_tale",
    "take_up_story",
    "go_to",
    "impress_agent",
    "spend_agency_xp",
    "set_agent_task",
    "resolve_agent_task",
    "add_purity",
    "move_to_source",
    "plan_journey",
    "labor_story",
    "grog_story_xp",
    "suggest_story",
    "plan_copying",
    "clear_copying",
    "invest_labor",
    "discipline_grog",
    "grog_pension",
    "craft_by_magic",
    "seal_charter",
    "break_clause",
    "censure_clause",
    "charge_clause",
    "use_charter_template",
    "save_charter_template",
    "forget_charter_template",
    "end_membership",
    "pay_fee",
    "lend_vis",
    "repay_vis_loan",
    "rhine_mark",
    "rhine_challenge",
    "sell_goods",
    "make_ligature",
    "apothecary_store",
    "theban_letter",
    "invoke_oath",
    "make_greek_fire",
    "paint_icon",
    "venerate_icon",
    "mothers_curse",
    "indulge_sin",
    "infernal_influence",
    "ars_goetia",
    "hunt_on_manor",
    "area_lore_on_manor",
    "hunt_on_journey",
    "area_lore_on_journey",
    "turbulence",
    "gauntlet",
    "lose_the_gift",
    "learn_cantation",
    "artist_career",
    "scholar_career",
    "ars_fabulosa",
    "faerie_bargain",
    "faerie_offer",
    "cast_in_lacuna",
    "pilgrimage",
    "invoke_saint",
    "threaten_saint",
    "patron_saint",
    "devotion_points",
    "act_of_piety",
    "invoke_baraka",
    "hajj",
    "holy_influence",
    "mystic_path",
    "spiritual_path",
    "monistic_revelation",
    "gods_aid",
    "font_of_knowledge",
    "commanding_aura",
    "verditius_hubris",
    "spirits_and_names",
    "dream_working",
    "hermetic_sacrifice",
    "certamen_duel",
    "whereabouts",
    "guest_stay",
    "tmre_divination",
    "tmre_astrology",
    "house_acclaim",
    "reputation_roll",
    "philosophic_alchemy",
    "great_elixir",
    "change_virtues_flaws",
    "library_search",
    "overcome_trap",
    "overcome_ward",
    "cross_threshold",
    "ship_stress",
    "ship_combat",
    "ship_fate",
    "build_ship",
    "detach_ship",
    "rejoin_ship",
    "add_stop",
    "plan_route",
    "shape_land",
    "perform_exorcism",
    "experiment_script",
    "tower_stress",
    "tower_conjure",
    "show_project",
    "begin_project",
    "open_tunnel",
    "end_marriage",
    "tame_beast",
    "menagerie_award",
    "warning_bell",
    "gather_connection",
    "lower_aegis",
    "death_roll",
    "circulate_text",
    "draft_charter",
    "seek_loophole",
    "follow_avenue",
)


def _entries() -> dict[str, MoreAction]:
    found = {
        entry.key: entry
        for area in (
            records,
            saga,
            character,
            covenant,
            laboratory,
            familiar,
            region,
            conflicts,
            new,
        )
        for entry in area.ENTRIES
    }
    return {key: found[key] for key in ORDER}


_REGISTRY = _entries()

#: Every action's label, by its key.
LABELS: Mapping[str, str] = MappingProxyType(
    {key: entry.label for key, entry in _REGISTRY.items()}
)

# Edit Interests lists each interest's actions by label: its step is
# finished here, where every label is known.
_REGISTRY["edit_interests"] = replace(
    _REGISTRY["edit_interests"],
    step=lambda page: interests_command(page, LABELS),
)

#: Each action's entry, by its key, in menu order.
REGISTRY: Mapping[str, MoreAction] = MappingProxyType(_REGISTRY)

# -- what the menus and pages read --

MORE_MENU: tuple[MenuItem, ...] = tuple(
    entry.item for entry in REGISTRY.values() if entry.menu == "more"
)
NEW_MENU: tuple[MenuItem, ...] = tuple(
    entry.item for entry in REGISTRY.values() if entry.menu == "new"
)
#: The actions offered in one section only, by that section's id.
MORE_SECTIONS: Mapping[str, str] = MappingProxyType(
    {key: e.section for key, e in REGISTRY.items() if e.section is not None}
)
#: The actions no page offers in its More: a section's or row's own button.
NOT_ON_PAGES: frozenset[str] = frozenset(
    key for key, entry in REGISTRY.items() if not entry.on_page
)
#: Where a page sets each action out itself.
PLACES: Mapping[str, tuple[tuple[NodeKind, str], ...]] = MappingProxyType(
    {key: e.places for key, e in REGISTRY.items() if e.places is not None}
)
#: Each action's first step, for those the core runs.
STEPS: Mapping[str, Callable[[Page], Command]] = MappingProxyType(
    {key: e.step for key, e in REGISTRY.items() if e.step is not None}
)
#: What each action the core runs changes.
REFRESH: Mapping[str, Refresh] = MappingProxyType(
    {key: e.refresh for key, e in REGISTRY.items() if e.refresh is not None}
)


def available(action: str, facts: ActionFacts) -> bool:
    """Whether `action` can run where the user is: what enables add / edit /
    delete and decides what More and New offer."""
    if not facts.player_may(action):
        return False
    if not viewing.offers(action):
        return False
    if not action_books.book_allows(action, facts.saga):
        return False
    if action in deeds.DEEDS and drafting(facts):
        return False
    character = facts.selected_character
    if character is not None and deeds.hidden(deeds.interests_off(character), action):
        return False
    if action in CREATE_PLACES and facts.selected_kind not in CREATE_PLACES[action]:
        return False
    if action == "edit" and facts.selected_kind == NodeKind.SAGA:
        return True
    entry = REGISTRY.get(action)
    if entry is not None:
        return entry.offered(facts)
    rule = RECORD_RULES.get(action)
    if rule is not None:
        return rule(facts)
    in_section = SECTION_RULES.get(action)
    if in_section is None:
        return True
    return in_section(facts, facts.active_section() or "")
