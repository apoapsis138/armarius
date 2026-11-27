"""A More action is registered in several places; this names, in one
failure, every place a new action is still missing, so adding one is one
test run rather than one per registry.

Where a More action lives (each also checked on its own elsewhere):

* its entry in the More registry (forms/more, ADR 0030): its letter and
  label, where it shows and when it is offered, and how it runs -- a
  terminal handler (`WorkspaceScreen.action_<name>`, or
  `base._MENU_HANDLERS`), else the entry's first step and what it
  redraws (its `Refresh`);
* where the desktop shows it: its places, `ON_THE_PAGE`, or not on pages;
* on a character's page: its book in `action_books.ACTION_BOOKS` or
  `NO_BOOK`;
* its form's dialog contract: an opener in `tests/dialog_openers.py`
  (checked by its own test below, a ratchet over the gaps it began with),
  or a reason in `NO_CONTRACT`;
* who may run it, when not every storyguide action: viewing's
  `LOOKING_ACTIONS` (players too), `STORYGUIDE_ONLY_ACTIONS` or
  `HOST_ONLY_ACTIONS`. Not required, so not checked here."""

import test_dialog_contracts_character as character
import test_dialog_contracts_covenant as covenant
import test_dialog_contracts_laboratory as laboratory
import test_dialog_contracts_library as library
import test_dialog_contracts_saga as saga
import test_dialog_contracts_tribunal as tribunal
from dialog_openers import OPENERS

from ars_magica_manager import action_books, actions
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import more
from ars_magica_manager.tui.screens.workspace import base
from ars_magica_manager.tui.screens.workspace.screen import WorkspaceScreen


def _missing(item: actions.MenuItem) -> list[str]:
    action = item.action
    found: list[str] = []
    handler = base._MENU_HANDLERS.get(action, f"action_{action}")
    if not callable(getattr(WorkspaceScreen, handler, None)):
        if action not in menu_forms._COMMANDS:
            found.append("forms/menu._COMMANDS")
        if action not in more.REFRESH:
            found.append("forms/more.REFRESH")
    placed = (
        action in menu_forms.PLACES
        or action in menu_forms.ON_THE_PAGE
        or action in menu_forms.NOT_ON_PAGES
    )
    if not placed:
        found.append("forms/menu.PLACES (or ON_THE_PAGE / NOT_ON_PAGES)")
    on_character = any(
        kind == NodeKind.CHARACTER for kind, _ in menu_forms.PLACES.get(action, ())
    )
    booked = action in action_books.ACTION_BOOKS or action in action_books.NO_BOOK
    if on_character and not booked:
        found.append("action_books.ACTION_BOOKS (or NO_BOOK)")
    return found


#: More actions with no dialog contract yet, when this check came in
#: (2026-11-18). A ratchet: this list only shrinks. Give a new action an
#: opener in tests/dialog_openers.py (named for it, "trait roll" for
#: trait_roll, or reaching it with `_run_more`), or name it in NO_CONTRACT
#: with why.
UNCONTRACTED_BEFORE: frozenset[str] = frozenset(
    {
        "apothecary_store",
        "area_lore_on_journey",
        "area_lore_on_manor",
        "artist_career",
        "assign_storyguide",
        "battle_muster",
        "begin_session",
        "begin_story",
        "boost_spell",
        "break_group",
        "build_ship",
        "cast_glance",
        "certamen_duel",
        "clear_copying",
        "close_session",
        "command_beast",
        "conceal",
        "conceal_secret",
        "conflict_battle_event",
        "creation_worksheet",
        "cross_threshold",
        "demote",
        "discipline_grog",
        "disputatio",
        "downtime_run",
        "edit_arms",
        "edit_combatant",
        "end_membership",
        "end_session",
        "experiment_script",
        "export_cult",
        "export_markdown",
        "export_pack",
        "export_record",
        "export_saga",
        "faerie_bargain",
        "faerie_offer",
        "familiar_trait_roll",
        "fight_options",
        "forget_charter_template",
        "form_group",
        "galdor_bargain",
        "galdor_bind",
        "galdor_conjure",
        "gather_connection",
        "gauntlet",
        "give",
        "give_silver",
        "go_to",
        "gods_aid",
        "grog_pension",
        "grog_story_xp",
        "group_morale",
        "guest_stay",
        "host_saga",
        "hunt_on_journey",
        "hunt_on_manor",
        "import_data",
        "impress_agent",
        "improve",
        "indulge_sin",
        "invoke_oath",
        "lab_text_access",
        "learn_cantation",
        "library_search",
        "lower_aegis",
        "make_ligature",
        "mark_unknown",
        "menagerie_award",
        "merge_doubles",
        "mothers_curse",
        "neutralize_shard",
        "next_round",
        "paint_icon",
        "pay_fee",
        "place_aging_points",
        "plan_copying",
        "plan_goal",
        "plan_journey",
        "player_view",
        "previously_on",
        "promote",
        "rally_group",
        "read_chronicle",
        "recovery_roll",
        "redeem_gratitude",
        "rejoin_ship",
        "remove_combatant",
        "repay_vis_loan",
        "restart_fight",
        "restore",
        "reveal",
        "reveal_secret",
        "rhine_challenge",
        "rhine_mark",
        "roll_fair",
        "roll_table",
        "scholar_career",
        "share_spell",
        "ship_fate",
        "ship_stress",
        "show_project",
        "siege_actions",
        "split_secret",
        "stop_hosting",
        "study_path",
        "suggest_story",
        "take_harm",
        "take_up_tale",
        "tame_beast",
        "teaching_requests",
        "theban_letter",
        "tmre_astrology",
        "tmre_divination",
        "toggle_mode",
        "tourney_season",
        "tower_conjure",
        "tower_stress",
        "tribunal_longevity",
        "undo_season",
        "update_record",
        "use_charge",
        "use_effect",
        "venerate_icon",
        "war_end",
        "what_changed",
        "whereabouts",
        "withdraw_case",
    }
)

#: More actions that open no form to contract, with why.
NO_CONTRACT: dict[str, str] = {
    "end_scene": "A yes-or-no question with nothing to fill "
    "(test_scene_forms.py drives it).",
    "open_show": "It only reads: a list of the Session's Shows, then one's copy "
    "with nothing to change (test_show_forms.py drives it).",
    "withdraw_show": "A list of the Session's Shows, then a yes-or-no question "
    "with nothing to fill (test_show_forms.py drives it).",
    "my_handouts": "It only reads: a list of Handouts, then one's copy with "
    "nothing to change (test_handout_list.py drives it).",
    "player_handouts": "It only reads: a Player's Handouts, then one's copy "
    "with nothing to change (test_handout_list.py drives it).",
    "preview_handout": "It only reads: the chosen Handout on its Stationery, "
    "with nothing to fill (test_preview_handout.py, test_gui_preview_handout.py "
    "and test_tui_shown_handout.py drive it).",
    "read_in_full": "It only reads: a long entry on a reading page, with "
    "nothing to fill (test_read_in_full.py drives it in the core and both "
    "front-ends).",
    "open_session": "opens the Session's page, not a dialog "
    "(test_session_page.py, test_tui_session_page.py)",
}


def _contracted() -> set[str]:
    """The More actions with a dialog contract: those an opener says it
    opens (Opener.action) whose name has a Contract in one of the
    test_dialog_contracts_<area> files."""
    contracts = {
        name
        for area in (character, covenant, laboratory, library, saga, tribunal)
        for name in area.CONTRACTS
    }
    return {
        opener.action
        for name, opener in OPENERS.items()
        if opener.action and name in contracts
    }


def test_every_more_action_has_a_dialog_contract_or_says_why_not():
    contracted = _contracted()
    gaps = sorted(
        item.action
        for item in more.MORE_MENU
        if item.action not in contracted
        and item.action not in UNCONTRACTED_BEFORE
        and item.action not in NO_CONTRACT
    )
    assert not gaps, (
        "Give each an opener in tests/dialog_openers.py and a contract, or "
        "name it in NO_CONTRACT with why: " + ", ".join(gaps)
    )


def test_the_list_of_old_gaps_only_shrinks():
    """An action given a contract leaves UNCONTRACTED_BEFORE, and one no
    longer on the menu does too."""
    on_menu = {item.action for item in more.MORE_MENU}
    contracted = _contracted()
    stale = sorted(
        a for a in UNCONTRACTED_BEFORE if a in contracted or a not in on_menu
    )
    assert not stale, "Take these off UNCONTRACTED_BEFORE: " + ", ".join(stale)


def test_each_reason_for_no_contract_still_holds():
    """An action in NO_CONTRACT is on the menu, has no contract after all,
    and isn't also counted among the old gaps."""
    on_menu = {item.action for item in more.MORE_MENU}
    contracted = _contracted()
    stale = sorted(
        a
        for a in NO_CONTRACT
        if a not in on_menu or a in contracted or a in UNCONTRACTED_BEFORE
    )
    assert not stale, "Take these off NO_CONTRACT: " + ", ".join(stale)
    assert all(why.strip() for why in NO_CONTRACT.values())


def test_every_more_action_is_registered_everywhere_it_must_be():
    gaps = {
        item.action: missing for item in more.MORE_MENU if (missing := _missing(item))
    }
    assert not gaps, "\n".join(
        f"{action}: add to {', '.join(where)}" for action, where in gaps.items()
    )
