"""The More and New menus and deleting a record, for a front-end that
shows one record's page at a time (the desktop), independent of how they
are drawn.

A `Page` is actions.ActionFacts for such a front-end: the record on show,
and no focused section. Its menus offer what actions.available offers
anywhere on the page: each More command is asked about with the page's
sections (PAGE_SECTIONS) one by one, and kept if any offers it. Every
command acts on the record on show, so the page counts as being "on the
record" (Delete, Export, In Creation / In Play); a command that would act
on a chosen row asks which first (a commands.Choose).

`command(page, action)` builds the first step of a menu entry, or of
Delete (`DELETE_RECORD`), as commands.py steps: mutating the saga only in
the last step's apply, so cancelling any step changes nothing.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import NamedTuple

from .. import (
    deeds,
    giving,
    viewing,
)
from ..actions import (
    MORE_MENU,
    MORE_SECTIONS,
    NEW_MENU,
    RECORD_SECTION,
    MenuItem,
    NodeKind,
    available,
    silver_purse,
)
from ..commands import Command, Refuse
from ..markup import escape
from ..rules import covenfolk
from ..sections import FAITH_SECTION, LAB_TEXTS_SECTION
from . import hosting as hosting_forms
from .menu_steps import _COMMANDS as _STEPS
from .menu_steps import delete_record, familiar_binder
from .page import (
    Page,
    Record,
)

#: Delete's action: the record on show, after a confirmation that says
#: what happens to what it owns.
DELETE_RECORD = "delete_record"

#: The More commands a page offers nowhere: the desktop shows them as the
#: section's own button (Fatigue beside Wounds in Health; Instill, Use a
#: Charge and Use an Effect beside Enchanted Devices). The Creation
#: Worksheet is offered, but opens a page rather than running a command.
NOT_ON_PAGES = frozenset(
    {
        # The desktop's eye in the title bar.
        "player_view",
        # Saga Content's Sessions draws them as row buttons.
        "cast_glance",
        "begin_session",
        "close_session",
        "read_chronicle",
        # The Chronicle pane's own Message button.
        "send_message",
        # The Secrets list's own row buttons.
        "reveal_secret",
        "conceal_secret",
        "split_secret",
        # Notes & Goals' own row button.
        "plan_goal",
        "edit_arms",
        "edit_fatigue",
        "edit_familiar_fatigue",
        # The familiar's page draws Roll as its Personality Traits' button.
        "familiar_trait_roll",
        "instill_effect",
        "use_charge",
        "use_effect",
        "give",
        "withdraw_case",
        "war_end",
        "neutralize_shard",
        "tribunal_longevity",
        "roll_fair",
        "court_roll",
        "roll_table",
        # The desktop draws it as the Open Stories' own button.
        "grow_story",
        # The desktop draws it as a button on the Diary, Open Stories and
        # Needs You.
        "take_up_story",
        # The desktop's Whereabouts draws it as its Add.
        "add_stop",
        "battle_event",
        "redeem_gratitude",
        "buy_manor",
        "assart",
        "winter_roll",
        "settle_inheritance",
        "conflict_battle_event",
        "battle_muster",
        "next_blow",
        "next_round",
        "add_combatant",
        "edit_combatant",
        "remove_combatant",
        "form_group",
        "break_group",
        "restart_fight",
        "fight_options",
        "group_morale",
        "rally_group",
        "next_siege_event",
        "siege_actions",
        # The desktop draws them as the Agents list's own buttons.
        "impress_agent",
        "spend_agency_xp",
        "set_agent_task",
        "resolve_agent_task",
        # The desktop draws it as the Goods list's own button.
        "add_purity",
        # The desktop draws it as House Rules' own button.
        "move_to_source",
        # The desktop draws it as Ahead's own button.
        "plan_journey",
        # The desktop draws them as the Charter's and Clauses' own buttons.
        "seal_charter",
        "break_clause",
        "censure_clause",
        "charge_clause",
        "use_charter_template",
        "save_charter_template",
        "forget_charter_template",
        "end_membership",
        # The desktop draws it as the Guests list's own button.
        "pay_fee",
        # The desktop draws the names a page holds as links instead.
        "go_to",
        # The Theban treasury's loans: the Tokens list's own buttons.
        "lend_vis",
        "repay_vis_loan",
        # The Rhine's ranks: the Gilds list's own buttons.
        "rhine_mark",
        "rhine_challenge",
        # The hunt and Area Lore: the Manors list's and Ahead's own buttons.
        "hunt_on_manor",
        "area_lore_on_manor",
        "hunt_on_journey",
        "area_lore_on_journey",
        # The Great Library: the rule of access's own button.
        "library_search",
        # A tomb's trap springs: the Traps list's own button.
        "overcome_trap",
        "overcome_ward",
        "cross_threshold",
        # A covenant's ships: the Ships list's own buttons.
        "ship_stress",
        "ship_combat",
        "ship_fate",
        "build_ship",
        "detach_ship",
        "rejoin_ship",
        # The desktop draws it as Whereabouts' own button.
        "plan_route",
        # A cleric's career: Holy Orders' own button.
        "perform_exorcism",
        # A covenant's Hermetic Projects: the tower's and the projects
        # list's own buttons, and Begin Project on the Overview chapter.
        "tower_stress",
        "tower_conjure",
        "show_project",
        "begin_project",
        # A lord's marriages: the Marriages list's own button.
        "end_marriage",
        # A covenant's Menagerie: the Beasts list's own button.
        "tame_beast",
        "menagerie_award",
        # A covenant's staged project: its block's own buttons.
        "warning_bell",
        "gather_connection",
        "lower_aegis",
        "death_roll",
        # Polemic and Charter Strength: the Texts list's and the charter
        # lords' own buttons.
        "circulate_text",
        "draft_charter",
        "seek_loophole",
        # A Criamon magus's path: its own Follow an Avenue button.
        "follow_avenue",
    }
)

#: Per page, the sections whose More commands its menu offers (None: the
#: page itself, with no section).
PAGE_SECTIONS: dict[NodeKind, tuple[str | None, ...]] = {
    NodeKind.SAGA: (None,),
    NodeKind.CHARACTER: (
        RECORD_SECTION[NodeKind.CHARACTER],
        "section-hermetic-background",
        "section-known-spells",
        "section-raw-vis-hermetic",
        "section-raw-vis-inventory",
        "section-inventory",
    ),
    NodeKind.FAMILIAR: (RECORD_SECTION[NodeKind.FAMILIAR],),
    NodeKind.TRIBUNAL: (RECORD_SECTION[NodeKind.TRIBUNAL],),
    NodeKind.NEIGHBOUR: (RECORD_SECTION[NodeKind.NEIGHBOUR],),
    NodeKind.CREATURE: (RECORD_SECTION[NodeKind.CREATURE],),
    NodeKind.LABORATORY: (
        RECORD_SECTION[NodeKind.LABORATORY],
        "section-lab-raw-vis",
        LAB_TEXTS_SECTION,
    ),
    NodeKind.COVENANT: (
        RECORD_SECTION[NodeKind.COVENANT],
        *(f"section-inh-{kind}" for kind in covenfolk.AUTO_KINDS),
        "section-eco-income",
        "section-eco-wealth",
        "section-pos-vis_store",
        "section-lib-books",
    ),
}


#: The sections only a magus's sheet has.
_MAGUS_SECTIONS = frozenset(
    {"section-hermetic-background", "section-known-spells", "section-raw-vis-hermetic"}
)


def page_sections(page: Page) -> tuple[str | None, ...]:
    """The sections of PAGE_SECTIONS the page shows."""
    sections = PAGE_SECTIONS.get(page.kind, ()) if page.kind else ()
    if page.kind == NodeKind.CHARACTER and (
        page.character is None or page.character.type != "magus"
    ):
        sections = tuple(s for s in sections if s not in _MAGUS_SECTIONS)
    return sections


def _anything(_page: Page) -> bool:
    return True


#: More commands the page's menu leaves out while they have nothing to act
#: on (the terminal offers them in their section and then says so).
_PAGE_CHECKS: dict[str, Callable[[Page], bool]] = {
    "improve": lambda page: bool(
        page.covenant is not None and page.covenant.economics.income_sources
    ),
    # Philosophic Alchemy's digestions.
    "philosophic_alchemy": lambda page: available(
        "philosophic_alchemy", replace(page, section="section-char-season")
    ),
}


def more_items(page: Page) -> list[MenuItem]:
    """What More offers on the page, in the menu's order."""
    sections = page_sections(page)
    return [
        item
        for item in MORE_MENU
        if item.action not in NOT_ON_PAGES
        and _PAGE_CHECKS.get(item.action, _anything)(page)
        and any(
            available(item.action, replace(page, section=section))
            for section in sections
        )
    ]


def section_of(page: Page, action: str) -> str | None:
    """The first of the page's sections that offers `action`."""
    for section in page_sections(page):
        if available(action, replace(page, section=section)):
            return section
    return None


class ManageItem(NamedTuple):
    """One entry of a record's Manage chapter: its action (a More
    command's, or DELETE_RECORD), its label and a line on what it does."""

    action: str
    label: str
    detail: str


#: A record's Manage chapter: what manages it as a file rather than as
#: part of the saga, each with what it does; Delete is last.
MANAGE: dict[str, str] = {
    "export_record": "Write it to a file that another saga, or this saga on "
    "another computer, can import.",
    "export_markdown": "Write its sheet as a Markdown file, for notes, a wiki "
    "or a message: the same copy and sheet as Print to PDF.",
    "update_record": "Read an export of it over it, for example after working "
    "on it elsewhere: shows what would change first, and keeps its place in "
    "this saga.",
    "edit_interests": "Tick the kinds of deed this character takes up: an "
    "interest left unticked (Knightly for a magus, Scholarly for a "
    "blacksmith) takes its actions off the Deeds chapter, A Season's Work "
    "and More.",
    "promote": "Write more of it down: a line becomes a sketch with a "
    "statblock, and a sketch a full record, In Creation, keeping everything "
    "it had.",
    "demote": "Keep less of it: a full record becomes a sketch, left out "
    "of seasons, ageing and upkeep, and a sketch a line. Nothing is deleted; the "
    "chapters it no longer shows keep what they hold.",
    "found_covenant": "Raise a new covenant on this ruin, as Winter Ruins "
    "does: it starts In Creation, sited here, and the ruin becomes its claim.",
    "begin_story": "Start this dormant story: its stages begin to come, the "
    "first due next season at the soonest.",
    "merge_doubles": "Make one record of each faction that shares its name "
    "with a character or creature: its attitudes, favours, links, words and "
    "memberships move to the character or creature.",
    "grow_story": "Make the chosen open story a threat of the Region, from "
    "its words; the story is marked Grown, naming the threat.",
    "take_up_tale": "Write a chapter of the threat's tale: what the troupe "
    "did, met or avoided, in its Diary and the troupe's covenants'.",
    "reveal": "Tell the players of it: they see it in lists, Find and the "
    "Atlas, and its name where a page names it. A dated line goes in the "
    "troupe's covenants' Diary.",
    "conceal": "Take it back: it is left out of everything the players read "
    "until you reveal it again, and the line its reveal wrote goes.",
    "assign_storyguide": "Take it as your story while it has no storyguide, "
    "or release or hand on one of yours: its storyguide alone reads its "
    "Secrets, and any other storyguide reads it as a player would.",
    "delay_threat": "Push the threat later or bring it sooner: its dated stages "
    "still to come move together, or it moves back or on along its track; "
    "the reason goes in its Diary.",
    DELETE_RECORD: "Remove it from the saga, after saying what happens to "
    "what it holds.",
}

#: The More commands a record's own page offers instead: in its Manage
#: chapter, or as its In Creation / In Play toggle and the Creation
#: Worksheet beside it.
ON_THE_PAGE = frozenset({*MANAGE, "toggle_mode", "creation_worksheet"})


def _managed(page: Page, action: str, detail: str) -> str:
    """A Manage entry's line, with Its Storyguide saying whose it is now."""
    if action != "assign_storyguide":
        return detail
    record = page.record_to_delete()
    who = viewing.storyguide_name(page.saga, viewing.storyguide_of(record, page.saga))
    return f"{detail} Now: {escape(who)}."


def manage_items(page: Page) -> list[ManageItem]:
    """What the page's Manage chapter offers, in order."""
    labels = {item.action: item.label for item in MORE_MENU}
    items = [
        ManageItem(action, labels[action], _managed(page, action, detail))
        for action, detail in MANAGE.items()
        if action != DELETE_RECORD and available(action, page)
    ]
    record = deletes(page)
    if record is not None:
        items.append(
            ManageItem(
                DELETE_RECORD,
                f"Delete {escape(record.name or '(unnamed)')}",
                MANAGE[DELETE_RECORD],
            )
        )
    return items


#: Edit Saga: in the saga page's Saga Settings, where the terminal's e
#: edits it.
EDIT_SAGA = MenuItem("e", "edit_saga", "Edit Saga")

#: Where a front-end that shows one page at a time (the desktop), and so
#: has no New or More menu, offers each New and More action: in one of the
#: page's chapters or sections, by its name. A New action there is a New
#: card at the end of the cards it adds to. An action is offered only
#: where it is listed (Restore nowhere: Add on the Magi and Companions
#: lists brings someone back); every New and More action is listed, or
#: is one a record's page offers itself (ON_THE_PAGE) or a section's own
#: button (NOT_ON_PAGES).
PLACES: dict[str, tuple[tuple[NodeKind, str], ...]] = {
    "edit_saga": ((NodeKind.SAGA, "Saga Settings"),),
    # On a covenant, books straight into its library.
    "import_data": ((NodeKind.SAGA, "Saga Management"), (NodeKind.COVENANT, "Library")),
    "export_saga": ((NodeKind.SAGA, "Saga Management"),),
    "export_cult": ((NodeKind.SAGA, "Saga Management"),),
    "export_pack": ((NodeKind.SAGA, "Saga Management"),),
    "merge_doubles": ((NodeKind.SAGA, "The Region"),),
    "mark_unknown": ((NodeKind.SAGA, "The Region"),),
    "host_saga": ((NodeKind.SAGA, "Saga Management"),),
    "stop_hosting": ((NodeKind.SAGA, "Saga Management"),),
    "set_date": ((NodeKind.SAGA, "Seasons"),),
    "undo_season": ((NodeKind.SAGA, "Seasons"),),
    "downtime_run": ((NodeKind.SAGA, "Seasons"),),
    "previously_on": ((NodeKind.SAGA, "Seasons"),),
    "create_covenant": ((NodeKind.SAGA, "Covenants"),),
    "create_tribunal": ((NodeKind.SAGA, "Tribunals"),),
    "create_neighbour": ((NodeKind.SAGA, "Neighbours"),),
    "create_creature": ((NodeKind.SAGA, "Creatures"), (NodeKind.BESTIARY, "Creatures")),
    "create_character": (
        (NodeKind.SAGA, "Unassigned Characters"),
        # A player's own characters, on The Troupe.
        (NodeKind.SAGA, "Your Characters"),
        (NodeKind.COVENANT, "People"),
        (NodeKind.CHARACTER_GROUP, "People"),
    ),
    "create_laboratory": (
        (NodeKind.SAGA, "Unassigned Laboratories"),
        (NodeKind.COVENANT, "Laboratories"),
    ),
    "create_familiar": (
        (NodeKind.CHARACTER, "Familiar"),
        (NodeKind.LABORATORY, deeds.SEASON_WORK),
    ),
    "restore": (),
    # On each source of income's row.
    "improve": ((NodeKind.COVENANT, "Income"),),
    "lab_text_access": (
        (NodeKind.CHARACTER, "Hermetic Background"),
        (NodeKind.LABORATORY, "Lab Texts"),
    ),
    # Beside the Abilities chapter's own buttons.
    "edit_traditions": ((NodeKind.CHARACTER, "Abilities"),),
    "disputatio": ((NodeKind.CHARACTER, deeds.SCHOLARLY),),
    "hedge_cast": ((NodeKind.CHARACTER, "Abilities"),),
    "galdor_conjure": ((NodeKind.CHARACTER, "Abilities"),),
    "galdor_bargain": ((NodeKind.CHARACTER, "Abilities"),),
    "galdor_bind": ((NodeKind.CHARACTER, "Abilities"),),
    # Beside Health's Edit buttons.
    "take_harm": ((NodeKind.CHARACTER, "Health"),),
    "recovery_roll": ((NodeKind.CHARACTER, "Health"),),
    # The Deeds chapter's headers (deeds.INTERESTS), and This Season for
    # the season-long ones.
    "end_session": ((NodeKind.CHARACTER, deeds.SESSION),),
    "what_changed": ((NodeKind.CHARACTER, deeds.SESSION),),
    "teaching_requests": ((NodeKind.CHARACTER, "This Season"),),
    "study_path": ((NodeKind.CHARACTER, "This Season"),),
    "tourney_season": ((NodeKind.CHARACTER, deeds.SEASON_WORK),),
    "melee_event": ((NodeKind.CHARACTER, deeds.KNIGHTLY),),
    # Beside This Season's Plan, Edit and Clear.
    "labor_story": ((NodeKind.CHARACTER, deeds.SEASON_WORK),),
    "grog_story_xp": ((NodeKind.CHARACTER, deeds.SEASON_WORK),),
    "plan_copying": ((NodeKind.CHARACTER, "This Season"),),
    "clear_copying": ((NodeKind.CHARACTER, "This Season"),),
    "invest_labor": ((NodeKind.CHARACTER, deeds.SEASON_WORK),),
    "command_beast": ((NodeKind.CHARACTER, "Personality Traits"),),
    "discipline_grog": ((NodeKind.CHARACTER, deeds.COVENFOLK),),
    "grog_pension": ((NodeKind.CHARACTER, deeds.COVENFOLK),),
    "craft_by_magic": ((NodeKind.CHARACTER, "Magic Outside the Lab"),),
    "place_aging_points": ((NodeKind.CHARACTER, "Aging"),),
    "resolve_twilight": ((NodeKind.CHARACTER, "Aging"),),
    "disguise_roll": ((NodeKind.CHARACTER, "Covers"),),
    # At the top of Hermetic Magic, under where the character is now.
    "whereabouts": ((NodeKind.CHARACTER, "Current Location"),),
    "guest_stay": ((NodeKind.CHARACTER, "Current Location"),),
    # On the Hooks' points line, not their title's, where it would wrap.
    "suggest_story": ((NodeKind.COVENANT, "Hooks"),),
    "trait_roll": ((NodeKind.CHARACTER, "Personality Traits"),),
    "sheet_roll": (
        (NodeKind.CHARACTER, "Abilities"),
        (NodeKind.CHARACTER, "Characteristics"),
    ),
    # The Shared tick in a known spell's form.
    "share_spell": ((NodeKind.CHARACTER, "Known Spells"),),
    "boost_spell": ((NodeKind.CHARACTER, "Known Spells"),),
    "perform_ritual": ((NodeKind.LABORATORY, deeds.SEASON_WORK),),
    "give_silver": (
        (NodeKind.CHARACTER, "Personal Gear"),
        (NodeKind.COVENANT, "Wealth"),
    ),
    "research_bonuses": ((NodeKind.COVENANT, "Library"),),
    # A craftsman's sale of his finished goods, beside This Season's Plan.
    "sell_goods": ((NodeKind.CHARACTER, deeds.SEASON_WORK),),
    # Art & Academe: a ligature beside Disputatio, the apothecary's
    # store beside This Season's Plan.
    "make_ligature": ((NodeKind.CHARACTER, deeds.SCHOLARLY),),
    "apothecary_store": ((NodeKind.CHARACTER, deeds.SEASON_WORK),),
    # The Theban Tribunal's Byzantine customs: letters and oaths among the
    # Deeds, Greek Fire's season on This Season, the icons and a mother's
    # curse in Faith.
    "theban_letter": ((NodeKind.CHARACTER, deeds.TRIBUNAL),),
    "invoke_oath": ((NodeKind.CHARACTER, deeds.TRIBUNAL),),
    "make_greek_fire": ((NodeKind.CHARACTER, deeds.SEASON_WORK),),
    "paint_icon": ((NodeKind.CHARACTER, "Faith"),),
    "venerate_icon": ((NodeKind.CHARACTER, "Faith"),),
    "mothers_curse": ((NodeKind.CHARACTER, "Faith"),),
    # Sin, tarnish and the Goetic Arts (RoP: The Infernal): beside the
    # Personality Traits' buttons, and the Abilities chapter's.
    "indulge_sin": ((NodeKind.CHARACTER, deeds.INFERNAL),),
    "infernal_influence": ((NodeKind.CHARACTER, deeds.INFERNAL),),
    "ars_goetia": ((NodeKind.CHARACTER, deeds.INFERNAL),),
    # A Mystagogue's experiment on a Script (TMRE p. 18).
    "experiment_script": ((NodeKind.CHARACTER, deeds.MYSTERY_CULTS),),
    # An apprentice's magic and the Gauntlet (Apprentices): beside the
    # Abilities chapter's buttons, This Season's, and Known Spells'.
    "turbulence": (
        (NodeKind.CHARACTER, deeds.APPRENTICESHIP),
        (NodeKind.CHARACTER, deeds.SEASON_WORK),
    ),
    "gauntlet": ((NodeKind.CHARACTER, deeds.APPRENTICESHIP),),
    "lose_the_gift": ((NodeKind.CHARACTER, deeds.APPRENTICESHIP),),
    "learn_cantation": ((NodeKind.CHARACTER, "Known Spells"),),
    # Art & Academe's artists and scholars, beside Disputatio.
    "artist_career": ((NodeKind.CHARACTER, deeds.SEASON_WORK),),
    "scholar_career": ((NodeKind.CHARACTER, deeds.SEASON_WORK),),
    # Dealing with faeries (RoP: Faerie), beside the Abilities chapter's.
    "ars_fabulosa": ((NodeKind.CHARACTER, deeds.FAERIE),),
    "faerie_bargain": ((NodeKind.CHARACTER, deeds.FAERIE),),
    "faerie_offer": ((NodeKind.CHARACTER, deeds.FAERIE),),
    # The lacuna and the pilgrim (HoH:S, The Church): in Magic Outside
    # the Lab, and beside This Season's buttons.
    "cast_in_lacuna": ((NodeKind.CHARACTER, "Magic Outside the Lab"),),
    "pilgrimage": ((NodeKind.CHARACTER, deeds.SEASON_WORK),),
    # Devotion and the saints, holy influence, the mystic paths and God's
    # aid (The Church, RoP: The Divine): in the Religion chapter's Faith
    # section, each where his faith offers it (rules.faiths). The Font
    # beside the Abilities' buttons, the Commanding Aura beside Health's
    # (its Soak).
    "invoke_saint": ((NodeKind.CHARACTER, "Faith"),),
    "threaten_saint": ((NodeKind.CHARACTER, "Faith"),),
    "patron_saint": ((NodeKind.CHARACTER, "Faith"),),
    "devotion_points": ((NodeKind.CHARACTER, "Faith"),),
    "act_of_piety": ((NodeKind.CHARACTER, "Faith"),),
    "invoke_baraka": ((NodeKind.CHARACTER, "Faith"),),
    "hajj": ((NodeKind.CHARACTER, "Faith"),),
    "holy_influence": ((NodeKind.CHARACTER, "Faith"),),
    "mystic_path": ((NodeKind.CHARACTER, "Faith"),),
    "spiritual_path": ((NodeKind.CHARACTER, "Faith"),),
    "monistic_revelation": ((NodeKind.CHARACTER, "Faith"),),
    "gods_aid": ((NodeKind.CHARACTER, "Faith"),),
    "font_of_knowledge": ((NodeKind.CHARACTER, deeds.INSIGHT),),
    "commanding_aura": ((NodeKind.CHARACTER, "Health"),),
    # House Verditius's Hubris beside the Personality Traits' buttons.
    "verditius_hubris": ((NodeKind.CHARACTER, "Personality Traits"),),
    # Hermetic spirit magic and theurgy, dream magic, Hermetic sacrifice
    # and certamen in Magic Outside the Lab, under Raw Vis.
    "spirits_and_names": ((NodeKind.CHARACTER, "Magic Outside the Lab"),),
    "dream_working": ((NodeKind.CHARACTER, "Magic Outside the Lab"),),
    "hermetic_sacrifice": ((NodeKind.CHARACTER, "Magic Outside the Lab"),),
    "certamen_duel": ((NodeKind.CHARACTER, "Magic Outside the Lab"),),
    # Divination and Hermetic astrology beside the Abilities' buttons.
    "tmre_divination": ((NodeKind.CHARACTER, deeds.INSIGHT),),
    "tmre_astrology": ((NodeKind.CHARACTER, deeds.INSIGHT),),
    # House Acclaim and Reputation rolls beside the Reputations' buttons.
    "house_acclaim": ((NodeKind.CHARACTER, deeds.SESSION),),
    "reputation_roll": ((NodeKind.CHARACTER, deeds.SESSION),),
    # Philosophic Alchemy's digestions.
    "philosophic_alchemy": ((NodeKind.CHARACTER, deeds.SEASON_WORK),),
    # The Great Elixir's test.
    "great_elixir": ((NodeKind.CHARACTER, "Aging"),),
    # Gaining and losing Virtues and Flaws in play, beside their buttons.
    "change_virtues_flaws": ((NodeKind.CHARACTER, "Virtues & Flaws"),),
    # Shaping the land by magic, beside Improve Income.
    "shape_land": ((NodeKind.COVENANT, "Income"),),
    # Wizard's War's tunnel (Hermetic Projects), in Magic Outside the Lab.
    "open_tunnel": ((NodeKind.CHARACTER, "Magic Outside the Lab"),),
}

#: The saga page's Saga Management: each entry with what it does.
SAGA_MANAGEMENT: dict[str, str] = {
    "import_data": "Bring books, spells or records in from a file, such as "
    "another saga's export or a list of books.",
    "export_cult": "Write one of the saga's own Mystery Cults, its degrees "
    "and Scripts, to a file another saga can import.",
    "export_saga": "Write the whole saga, every record and what it holds, to "
    "one file that another saga, or this one on another computer, can import.",
    "export_pack": "Write chosen Tribunals, covenants, places and neighbours, "
    "with what goes with them, to a content pack another saga can import or "
    "start from.",
    "host_saga": "Let the players open the saga in a web browser on their own "
    "computers, over your private network, each signing in as one of Saga "
    "Content's Players.",
}


def management_note(action: str) -> str:
    """What Saga Management says beside `action` (plain text)."""
    if action == "stop_hosting":
        return hosting_forms.hosting_note()
    return SAGA_MANAGEMENT.get(action, "")


def lives_at(action: str, kind: NodeKind, spot: str) -> bool:
    """Whether PLACES puts `action` at `spot` on a `kind` page."""
    return (kind, spot) in PLACES.get(action, ())


#: Whether the page offers a placed action where `available`, which
#: answers for the terminal's New and More, doesn't say.
_PLACED_CHECKS: dict[str, Callable[[Page], bool]] = {
    "edit_saga": lambda page: page.kind == NodeKind.SAGA,
    "create_familiar": lambda page: familiar_binder(page) is not None,
    # The page's sections (PAGE_SECTIONS) leave This Season out.
    "labor_story": lambda page: available(
        "labor_story", replace(page, section="section-char-season")
    ),
    "invest_labor": lambda page: available(
        "invest_labor", replace(page, section="section-char-season")
    ),
    "grog_story_xp": lambda page: available(
        "grog_story_xp", replace(page, section="section-char-season")
    ),
    "plan_copying": lambda page: available(
        "plan_copying", replace(page, section="section-char-season")
    ),
    "clear_copying": lambda page: available(
        "clear_copying", replace(page, section="section-char-season")
    ),
    # A craftsman's sale of his finished goods.
    "sell_goods": lambda page: available(
        "sell_goods", replace(page, section="section-char-season")
    ),
    # An apothecary's searching and preserving.
    "apothecary_store": lambda page: available(
        "apothecary_store", replace(page, section="section-char-season")
    ),
    # The pilgrim's road (The Church).
    "pilgrimage": lambda page: available(
        "pilgrimage", replace(page, section="section-char-season")
    ),
    # Gaining and losing Virtues and Flaws in play: the page's sections
    # leave the Virtues & Flaws lists out.
    "change_virtues_flaws": lambda page: available(
        "change_virtues_flaws", replace(page, section="section-vf-virtues")
    ),
}


#: The section a placed spot stands for, for the checks that ask which
#: section focus is in: a desktop page has none focused.
SPOT_SECTIONS: dict[str, str] = {
    "Faith": FAITH_SECTION,
    "Reputations": "section-reputations",
    # The Deeds chapter's Reputation actions answer as on Reputations.
    deeds.SESSION: "section-reputations",
    "Health": "section-char-health",
    "Aging": "section-aging",
}


def _offered_at(page: Page, spot: str, action: str, offered: set[str]) -> bool:
    """Whether `action` is offered at `spot`: as the page offers it, or as
    it would be with focus in the section the spot stands for (its More
    section, or the spot's own)."""
    if action in offered:
        return True
    section = MORE_SECTIONS.get(action) or SPOT_SECTIONS.get(spot)
    return section is not None and available(action, replace(page, section=section))


def placed(page: Page, spot: str) -> list[MenuItem]:
    """The actions the page offers at `spot` (a chapter's or section's
    name, or "New" / "More"), in PLACES's order."""
    items = {item.action: item for item in (EDIT_SAGA, *NEW_MENU, *MORE_MENU)}
    offered = {i.action for i in (*new_items(page), *more_items(page))}
    return [
        items[action]
        for action, places in PLACES.items()
        if (page.kind, spot) in places
        and (
            # A check of its own still answers to who sits here.
            (
                viewing.offers(action)
                and page.player_may(action)
                and _PLACED_CHECKS[action](page)
            )
            if action in _PLACED_CHECKS
            else _offered_at(page, spot, action, offered)
        )
    ]


def new_items(page: Page) -> list[MenuItem]:
    """What New can make from the page."""
    return [item for item in NEW_MENU if available(item.action, page)]


def deletes(page: Page) -> Record | None:
    """The record Delete deletes on the page, if any."""
    if page.kind is None or not available(DELETE_RECORD, page):
        return None
    return page.record_to_delete()


def command(page: Page, action: str) -> Command:
    """The first step of the menu entry `action` on the page."""
    saga = page.saga
    if action == DELETE_RECORD:
        record = deletes(page)
        if record is None:
            return Refuse("Delete", "Nothing here to delete.")
        return delete_record(saga, record)
    builder = _COMMANDS.get(action)
    if builder is None:
        return Refuse("More", "That isn't available here.")
    return builder(page)


# Give Silver gives from the purse of the section that offers it, which
# the page's placement finds.


def _silver_command(page: Page) -> Command:
    section = section_of(page, "give_silver")
    purse = silver_purse(replace(page, section=section))
    if purse is None:
        return Refuse("Give Silver", "No silver to give here.")
    return giving.give(page.saga, giving.SILVER, purse)


#: Each More action's first step (menu_steps), with Give Silver's.
_COMMANDS: dict[str, Callable[[Page], Command]] = {
    **_STEPS,
    "give_silver": _silver_command,
}
