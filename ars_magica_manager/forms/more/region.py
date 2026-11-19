"""More in the Region: Tribunals, neighbours and places, threats, manors and creatures."""

from __future__ import annotations

from ...models import Neighbour
from ...sections import CASES_SECTION, DIARY_SECTION, NEIGHBOUR_INFO_SECTION
from .. import threshold as threshold_forms
from ..menu_refresh import changes
from ..menu_steps import needs, neighbour
from .entry import MoreAction
from .rules import on_charter_lord

#: This area's actions, in the order More lists them.
ENTRIES: tuple[MoreAction, ...] = (
    MoreAction(
        "withdraw_case", "w", "Withdraw", section="section-trib-cases", on_page=False
    ),
    MoreAction(
        "war_end",
        "e",
        "War's End",
        section="section-trib-cases",
        on_page=False,
        in_section=lambda facts, section: (
            section == CASES_SECTION and facts.chosen_row(section) is not None
        ),
    ),
    MoreAction(
        "neutralize_shard",
        "n",
        "Neutralize a Shard",
        section="section-trib-tokens",
        on_page=False,
    ),
    MoreAction(
        "tribunal_longevity",
        "l",
        "The Tribunal's Longevity Ritual",
        section="section-trib-tokens",
        on_page=False,
    ),
    MoreAction(
        "roll_fair", "r", "Roll Income", section="section-nb-fairs", on_page=False
    ),
    MoreAction(
        "court_roll", "r", "Court Roll", section="section-nb-court-cases", on_page=False
    ),
    MoreAction("roll_table", "r", "Roll", section="section-nb-tables", on_page=False),
    MoreAction(
        "battle_event", "b", "Battle Event", section="section-nb-battles", on_page=False
    ),
    MoreAction(
        "redeem_gratitude",
        "r",
        "Redeem Gratitude",
        section="section-nb-gratitude",
        on_page=False,
    ),
    MoreAction(
        "buy_manor", "b", "Buy a Manor", section="section-manors", on_page=False
    ),
    MoreAction("assart", "s", "Assart", section="section-manors", on_page=False),
    MoreAction(
        "winter_roll",
        "w",
        "Winter Roll",
        section="section-establishments",
        on_page=False,
    ),
    MoreAction(
        "settle_inheritance",
        "i",
        "Settle an Inheritance",
        section="section-household",
        on_page=False,
    ),
    MoreAction(
        "grow_story",
        "g",
        "Grow into a Threat",
        section="section-region-stories",
        on_page=False,
    ),
    # The Theban treasury's loans of vis.
    MoreAction(
        "lend_vis",
        "v",
        "Lend Vis from the Treasury",
        section="section-trib-tokens",
        on_page=False,
    ),
    MoreAction(
        "repay_vis_loan",
        "p",
        "Repay a Loan of Vis",
        section="section-trib-tokens",
        on_page=False,
    ),
    # The Rhine's ranks: masters' marks and archmagi's challenges.
    MoreAction(
        "rhine_mark",
        "k",
        "Mark of Approval",
        section="section-trib-gilds",
        on_page=False,
    ),
    MoreAction(
        "rhine_challenge",
        "c",
        "Archmage's Challenge",
        section="section-trib-gilds",
        on_page=False,
    ),
    # The hunt and Area Lore, on a manor and on the road (LoM, C&G).
    MoreAction(
        "hunt_on_manor", "h", "The Hunt", section="section-manors", on_page=False
    ),
    MoreAction(
        "area_lore_on_manor", "l", "Area Lore", section="section-manors", on_page=False
    ),
    # The Rhine's Great Library at Durenmar (Guardians of the Forests).
    MoreAction(
        "library_search",
        "s",
        "Search the Great Library",
        section="section-trib-library",
        on_page=False,
    ),
    # A tomb's trap springs (Lands of the Nile).
    MoreAction(
        "overcome_trap",
        "o",
        "Overcome It",
        section="section-nb-tomb-traps",
        on_page=False,
    ),
    MoreAction(
        "overcome_ward",
        "o",
        "Overcome It",
        section="section-nb-tomb-wards",
        on_page=False,
    ),
    # A place with a Faerie aura: crossing into the Faerie Realm.
    MoreAction(
        "cross_threshold",
        "t",
        "Cross the Threshold",
        step=needs(neighbour, threshold_forms.threshold_form),
        refresh=changes(NEIGHBOUR_INFO_SECTION, DIARY_SECTION),
        on_page=False,
        in_section=lambda facts, section: (
            section == NEIGHBOUR_INFO_SECTION
            and isinstance(record := facts.record_to_export(), Neighbour)
            and threshold_forms.offers(facts.saga, record)
        ),
    ),
    # A lord's marriages: the chosen one ends (LoM p. 11; DE pp. 148, 513).
    MoreAction(
        "end_marriage",
        "x",
        "End a Marriage",
        section="section-nb-marriages",
        on_page=False,
    ),
    # Polemic and Charter Strength (Transforming Mythic Europe pp. 27-36).
    MoreAction(
        "circulate_text",
        "c",
        "Circulate a Text",
        section="section-trib-argument-texts",
        on_page=False,
    ),
    MoreAction(
        "draft_charter",
        "d",
        "Draft the Charter",
        on_page=False,
        in_section=on_charter_lord,
    ),
    MoreAction(
        "seek_loophole",
        "o",
        "Seek a Loophole",
        on_page=False,
        in_section=on_charter_lord,
    ),
)
