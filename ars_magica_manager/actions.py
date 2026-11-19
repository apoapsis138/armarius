"""What the user can do where they are, independent of how it is shown.

Each sheet section supports some of the four verbs (add, remove, edit,
restore), and the More and New menus offer commands only where they
apply. This module declares all of that and decides it; a front-end binds
each verb or command to its own handler (a key, a button, a menu entry) and
asks `available` whether to offer it.

The front-end answers the questions `available` needs through the
ActionFacts protocol: what is selected, where focus is, and the few facts
only it knows (which device row is chosen, whether files can be sent)."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, NamedTuple, Protocol

from . import (
    giving,
    merges,
    seasons,
    storyguides,
    traditions,
)
from .models import (
    INHABITANT_KINDS,
    POSSESSION_KINDS,
    Character,
    Covenant,
    Creature,
    Familiar,
    Laboratory,
    Neighbour,
    Saga,
    Tribunal,
)
from .rules import (
    covenfolk,
)
from .sections import (
    ARGUMENT_TEXTS_SECTION,
    BATTLES_SECTION,
    BOOK_SECTIONS,
    BOOKS_SECTION,
    CASES_SECTION,
    CATALOGS_SECTION,
    CHAR_AHEAD_SECTION,
    CHARTER_SECTION,
    CONFLICT_BATTLES_SECTION,
    CORE_SECTIONS,
    COURT_CASES_SECTION,
    CREATURE_INFO_SECTION,
    DEVICE_SECTIONS,
    ESTABLISHMENTS_SECTION,
    FAIRS_SECTION,
    FIGHTS_SECTION,
    GILDS_SECTION,
    GRATITUDE_SECTION,
    HIDDEN_SECTION,
    HOUSE_RULES_SECTION,
    HOUSEHOLD_SECTION,
    LAB_VF_SECTIONS,
    LIBRARY_RULES_SECTION,
    MANORS_SECTION,
    NEIGHBOUR_INFO_SECTION,
    ORDERS_SECTION,
    PLAYERS_SECTION,
    REGION_STORIES_SECTION,
    SESSIONS_SECTION,
    SIEGES_SECTION,
    SILVER_SECTIONS,
    SOURCES_SECTION,
    SPELL_SECTION,
    TABLES_SECTION,
    TOKENS_SECTION,
    TRADITIONS_SECTION,
    TRAIT_SECTIONS,
    TRIBUNAL_INFO_SECTION,
    WHEREABOUTS_SECTION,
)

if TYPE_CHECKING:
    from .transfer import Record


class NodeKind(StrEnum):
    """What the selected item of the saga's navigation stands for (in the
    Textual front-end, a nav-tree node)."""

    SAGA = "saga"
    COVENANT = "covenant"
    CHARACTER_GROUP = "character_group"
    CHARACTER = "character"
    FAMILIAR = "familiar"
    LABORATORY_GROUP = "laboratory_group"
    LABORATORY = "laboratory"
    SAGA_CONTENT = "saga_content"
    SEASONS = "seasons"
    #: The saga's stores (stores.py): every book, every enchanted device.
    ARMARIUM = "armarium"
    CUSTODIA = "custodia"
    REGION = "region"
    TRIBUNAL = "tribunal"
    NEIGHBOUR_GROUP = "neighbour_group"
    NEIGHBOUR = "neighbour"
    BESTIARY = "bestiary"
    CREATURE = "creature"
    CONFLICTS = "conflicts"


# -- the section verbs: a / d / e, and More's Restore --

#: The four things a section can let the user do to its rows.
VERBS: tuple[str, ...] = ("add", "remove", "edit", "restore")

_EDIT = frozenset({"edit"})
_ALL3 = frozenset({"add", "remove", "edit"})
_ADD_REMOVE = frozenset({"add", "remove"})


def _section_verbs() -> dict[str, frozenset[str]]:
    verbs: dict[str, frozenset[str]] = {
        SPELL_SECTION: _ALL3,
        HOUSE_RULES_SECTION: _ALL3,
        PLAYERS_SECTION: _ALL3,
        SESSIONS_SECTION: _ALL3,
        BOOKS_SECTION: _EDIT,
        TRADITIONS_SECTION: _EDIT,
        SOURCES_SECTION: _ALL3,
        CATALOGS_SECTION: _EDIT,
        HIDDEN_SECTION: _ADD_REMOVE,
        # Character sheet
        "section-char-info": _EDIT,
        "section-char-characteristics": _EDIT,
        "section-char-biographical": _EDIT,
        "tab-abilities": _ALL3,
        "section-aging": _EDIT,
        # Health has two dialogs (Wounds and Fatigue); Edit opens Wounds,
        # Fatigue is in More.
        "section-char-health": _EDIT,
        "section-arts": _EDIT,
        "section-hermetic-background": _EDIT,
        "section-known-spells": _ALL3,
        "section-research-goals": _ALL3,
        "section-inventory": _ALL3,
        "section-raw-vis-hermetic": _ALL3,
        "section-raw-vis-inventory": _ALL3,
        "section-char-season": _ALL3,
        CHAR_AHEAD_SECTION: _ALL3,
        "tab-diary": _ALL3,
        # Familiar sheet
        "section-fam-info": _EDIT,
        "section-fam-binding": _EDIT,
        "section-fam-characteristics": _EDIT,
        "section-fam-health": _EDIT,
        "section-fam-natural-weapons": _ALL3,
        "tab-fam-abilities": _ALL3,
        "tab-fam-powers": _ALL3,
        # Laboratory sheet
        "section-lab-identity": _EDIT,
        "section-lab-characteristics": _EDIT,
        "section-lab-specialties": _ALL3,
        "section-lab-features": _ALL3,
        "section-lab-raw-vis": _ALL3,
        "tab-lab-planning": _ALL3,
        "tab-lab-diary": _ALL3,
        "section-lab-connections": _ALL3,
        "section-lab-rooms": _ALL3,
        "section-lab-items": _ALL3,
        # Covenant sheet
        "section-cov-info": _EDIT,
        "section-cov-description": _EDIT,
        "section-cov-boons": _ALL3,
        "section-cov-hooks": _ALL3,
        "section-eco-wealth": _EDIT,
        "section-eco-income": _ALL3,
        "section-eco-expenditure": _EDIT,
        "section-eco-savings": _EDIT,
        "section-inh-loyalty": _EDIT,
        "section-inh-population": _EDIT,
        "section-inh-misc": _EDIT,
        "tab-cov-diary": _ALL3,
        **CORE_SECTIONS,
    }
    for section in TRAIT_SECTIONS:
        verbs[section] = _ALL3
    # Editing a Virtue or Flaw changes only what it names (Puissant's
    # Ability); which Virtue it is stays.
    for section in (
        "section-vf-virtues",
        "section-vf-flaws",
        "section-fam-vf-virtues",
        "section-fam-vf-flaws",
        *LAB_VF_SECTIONS,
    ):
        verbs[section] = _ALL3
    for section in BOOK_SECTIONS:
        # The Library summary lists no books of its own: only Add.
        verbs[section] = (
            frozenset({"add"}) if section == "section-lib-summary" else _ALL3
        )
    for kind in INHABITANT_KINDS:
        # Only Magi and Companions can be departed, and so restored.
        verbs[f"section-inh-{kind}"] = (
            _ALL3 | {"restore"} if kind in covenfolk.AUTO_KINDS else _ALL3
        )
    for kind, _ in seasons.SEASON_KINDS:
        verbs[f"section-cov-seasons-{kind}"] = _ALL3
    for section in DEVICE_SECTIONS:
        verbs[section] = _ALL3
    for kind in POSSESSION_KINDS:
        verbs[f"section-pos-{kind}"] = _ALL3
    for tradition in traditions.all_traditions():
        verbs[traditions.tradition_section(tradition.id)] = _ALL3
        verbs[traditions.effects_section(tradition.id)] = _ALL3
        verbs[traditions.bonds_section(tradition.id)] = _ALL3
        verbs[traditions.pools_section(tradition.id)] = _EDIT
    return verbs


#: What each sheet section lets the user do to its rows, by section id. A
#: front-end offers a verb in a section only if it is listed here, and must
#: have a handler for every verb listed.
SECTION_VERBS: dict[str, frozenset[str]] = _section_verbs()


# -- the More and New menus --


class MenuItem(NamedTuple):
    """One entry of the More or New menu: the letter that picks it, the
    action `available` is asked about, and its label."""

    letter: str
    action: str
    label: str


#: New: what can be made, each offered only where it belongs (see
#: CREATE_PLACES).
NEW_MENU: tuple[MenuItem, ...] = (
    MenuItem("v", "create_covenant", "New Covenant"),
    MenuItem("c", "create_character", "New Character"),
    MenuItem("l", "create_laboratory", "New Laboratory"),
    MenuItem("f", "create_familiar", "Bind Familiar"),
    MenuItem("t", "create_tribunal", "New Tribunal"),
    MenuItem("b", "create_neighbour", "New Neighbour"),
    MenuItem("r", "create_creature", "New Creature"),
)

#: More: what only a few sections, or the record itself, can do. Each
#: is offered only where `available` says it applies.
MORE_MENU: tuple[MenuItem, ...] = (
    MenuItem("r", "restore", "Restore"),
    MenuItem("i", "improve", "Improve Income"),
    MenuItem("i", "instill_effect", "Instill an Effect"),
    MenuItem("c", "use_charge", "Use a Charge"),
    MenuItem("u", "use_effect", "Use an Effect"),
    MenuItem("p", "perform_ritual", "Perform Ritual"),
    MenuItem("s", "share_spell", "Share Spell"),
    MenuItem("b", "boost_spell", "Boost a Spell"),
    MenuItem("g", "give", "Give"),
    MenuItem("s", "give_silver", "Give Silver"),
    MenuItem("l", "lab_text_access", "Lab Texts Read"),
    MenuItem("t", "edit_traditions", "Traditions"),
    MenuItem("d", "disputatio", "Disputatio"),
    MenuItem("c", "hedge_cast", "Cast a Power"),
    MenuItem("j", "galdor_conjure", "Conjure a Spirit"),
    MenuItem("q", "galdor_bargain", "Bargain with a Lord"),
    MenuItem("z", "galdor_bind", "Bind an Item"),
    MenuItem("f", "edit_fatigue", "Edit Fatigue"),
    MenuItem("h", "take_harm", "Take Harm"),
    MenuItem("y", "recovery_roll", "Recovery Roll"),
    MenuItem("e", "end_session", "End of Session"),
    MenuItem("w", "what_changed", "What Changed Since the Last Session"),
    MenuItem("g", "cast_glance", "Cast at a Glance"),
    # The Virtual Tabletop (Preview): a Session's Chronicle (chronicle.py).
    MenuItem("b", "begin_session", "Begin Session"),
    MenuItem("n", "close_session", "End Session"),
    MenuItem("r", "read_chronicle", "Chronicle"),
    # A Message or Whisper at the Session Under way (forms/message.py).
    MenuItem("s", "send_message", "Message"),
    # Roll from the sheet, at the Session Under way (forms/sheet_roll.py).
    MenuItem("o", "sheet_roll", "Roll"),
    MenuItem("q", "teaching_requests", "Teaching Requests"),
    MenuItem("y", "study_path", "Study Path"),
    MenuItem("t", "tourney_season", "Tournament"),
    MenuItem("v", "melee_event", "Melee Event"),
    MenuItem("c", "command_beast", "Command the Beast"),
    MenuItem("a", "place_aging_points", "Place Aging Points"),
    MenuItem("w", "resolve_twilight", "Resolve Twilight"),
    MenuItem("g", "disguise_roll", "Disguise Roll"),
    MenuItem("o", "trait_roll", "Roll"),
    MenuItem("o", "familiar_trait_roll", "Roll"),
    MenuItem("f", "edit_familiar_fatigue", "Edit Fatigue"),
    MenuItem("i", "import_data", "Import"),
    MenuItem("b", "research_bonuses", "Set Up Research Library"),
    MenuItem("x", "export_record", "Export"),
    # The record's sheet as a Markdown file (markdown_sheet).
    MenuItem("j", "export_markdown", "Export as Markdown"),
    # Which interests' deeds a character's sheet offers (deeds).
    MenuItem("w", "edit_interests", "Interests"),
    MenuItem("x", "export_saga", "Export Saga"),
    MenuItem("y", "export_cult", "Export a Cult"),
    MenuItem("k", "export_pack", "Export Pack"),
    MenuItem("h", "host_saga", "Host for Players"),
    MenuItem("h", "stop_hosting", "Stop Hosting"),
    MenuItem("u", "update_record", "Update from a File"),
    MenuItem("m", "toggle_mode", "In Creation / In Play"),
    MenuItem("p", "promote", "Promote"),
    MenuItem("o", "demote", "Demote"),
    MenuItem("w", "creation_worksheet", "Creation Worksheet"),
    MenuItem("t", "set_date", "Set Date"),
    MenuItem("z", "undo_season", "Undo Last Season"),
    MenuItem("o", "downtime_run", "Run Downtime"),
    MenuItem("u", "previously_on", "Previously On"),
    MenuItem("a", "edit_arms", "Arms"),
    MenuItem("w", "withdraw_case", "Withdraw"),
    MenuItem("e", "war_end", "War's End"),
    MenuItem("n", "neutralize_shard", "Neutralize a Shard"),
    MenuItem("l", "tribunal_longevity", "The Tribunal's Longevity Ritual"),
    MenuItem("r", "roll_fair", "Roll Income"),
    MenuItem("r", "court_roll", "Court Roll"),
    MenuItem("r", "roll_table", "Roll"),
    MenuItem("b", "battle_event", "Battle Event"),
    MenuItem("r", "redeem_gratitude", "Redeem Gratitude"),
    MenuItem("b", "buy_manor", "Buy a Manor"),
    MenuItem("s", "assart", "Assart"),
    MenuItem("w", "winter_roll", "Winter Roll"),
    MenuItem("i", "settle_inheritance", "Settle an Inheritance"),
    MenuItem("b", "conflict_battle_event", "Battle Event"),
    MenuItem("u", "battle_muster", "Muster and Aftermath"),
    MenuItem("o", "fight_options", "Combat Options"),
    MenuItem("n", "next_blow", "Next Blow"),
    MenuItem("r", "next_round", "Next Round"),
    MenuItem("a", "add_combatant", "Add Combatant"),
    MenuItem("e", "edit_combatant", "Edit Combatant"),
    MenuItem("v", "remove_combatant", "Remove Combatant"),
    MenuItem("g", "form_group", "Form a Group"),
    MenuItem("u", "break_group", "Break up a Group"),
    MenuItem("t", "restart_fight", "Restart the Fight"),
    MenuItem("m", "group_morale", "Discipline or Morale"),
    MenuItem("l", "rally_group", "Rally a Group"),
    MenuItem("n", "next_siege_event", "Next Siege Event"),
    MenuItem("a", "siege_actions", "Siege Actions"),
    MenuItem("f", "found_covenant", "Found a Covenant Here"),
    MenuItem("b", "begin_story", "Begin This Story"),
    MenuItem("h", "delay_threat", "Delay or Hasten"),
    MenuItem("g", "grow_story", "Grow into a Threat"),
    MenuItem("q", "merge_doubles", merges.TITLE),
    # Who may read what (viewing.py): telling the players of a record, or
    # taking it back; many at once on the Region; and the storyguide's
    # own window seen as the players see it.
    MenuItem("k", "reveal", "Reveal to the Players"),
    MenuItem("k", "conceal", "Hide from the Players"),
    MenuItem("k", "mark_unknown", "Hide from the Players"),
    MenuItem("v", "player_view", "Player View"),
    # A record's own storyguide, with more than one (storyguides.py).
    MenuItem("y", "assign_storyguide", storyguides.TITLE),
    # One secret of a record's Secrets list, revealed or taken back, or
    # split into a secret for each paragraph.
    MenuItem("k", "reveal_secret", "Reveal the Secret"),
    MenuItem("k", "conceal_secret", "Hide the Secret Again"),
    MenuItem("s", "split_secret", "Split by Paragraph"),
    # A player's goal of a score to reach (forms/notes_goals.py).
    MenuItem("p", "plan_goal", "Plan the Study Path"),
    # A chapter of what the troupe did: on a threat, or a chosen open story.
    MenuItem("t", "take_up_tale", "Take Up the Tale"),
    MenuItem("t", "take_up_story", "Take Up the Tale"),
    MenuItem("g", "go_to", "Go To"),
    MenuItem("i", "impress_agent", "Impress"),
    MenuItem("x", "spend_agency_xp", "Spend Agency Experience"),
    MenuItem("t", "set_agent_task", "Set a Task"),
    MenuItem("r", "resolve_agent_task", "Resolve the Task"),
    MenuItem("p", "add_purity", "Add a Purity"),
    MenuItem("s", "move_to_source", "Move to Source"),
    MenuItem("j", "plan_journey", "Travel"),
    MenuItem("l", "labor_story", "Labor Points from a Story"),
    # A grog's story experience, counted against the yearly update.
    MenuItem("s", "grog_story_xp", "Story Experience"),
    # A covenant's Hook proposes a story to accept.
    MenuItem("y", "suggest_story", "Suggest a Story"),
    # A grog's season of copying, planned like anyone's (DE p. 380).
    MenuItem("c", "plan_copying", "Plan Copying"),
    MenuItem("x", "clear_copying", "Clear Copying"),
    MenuItem("v", "invest_labor", "Invest Time or Money"),
    MenuItem("r", "discipline_grog", "Reward or Punish"),
    MenuItem("n", "grog_pension", "Pension"),
    MenuItem("f", "craft_by_magic", "Craft by Magic"),
    MenuItem("s", "seal_charter", "Seal the Charter"),
    MenuItem("b", "break_clause", "Break a Clause"),
    MenuItem("c", "censure_clause", "Censure"),
    MenuItem("g", "charge_clause", "Charge at Tribunal"),
    # A covenant's charter: its templates and its expelled members.
    MenuItem("u", "use_charter_template", "Use a Template"),
    MenuItem("t", "save_charter_template", "Save as Template"),
    MenuItem("f", "forget_charter_template", "Forget a Template"),
    MenuItem("x", "end_membership", "End Membership"),
    # A guest's yearly fee for his hospitality, on the host's Guests.
    MenuItem("p", "pay_fee", "Pay the Fee"),
    # The Theban treasury's loans of vis.
    MenuItem("v", "lend_vis", "Lend Vis from the Treasury"),
    MenuItem("p", "repay_vis_loan", "Repay a Loan of Vis"),
    # The Rhine's ranks: masters' marks and archmagi's challenges.
    MenuItem("k", "rhine_mark", "Mark of Approval"),
    MenuItem("c", "rhine_challenge", "Archmage's Challenge"),
    # A craftsman's sale of his finished goods (City & Guild).
    MenuItem("s", "sell_goods", "Sell Finished Goods"),
    # Art & Academe's ligatures and the apothecary's store.
    MenuItem("l", "make_ligature", "Make a Ligature"),
    MenuItem("o", "apothecary_store", "Apothecary's Store"),
    # The Theban Tribunal's Byzantine customs (The Sundered Eagle).
    MenuItem("e", "theban_letter", "Hermetic Letter"),
    MenuItem("s", "invoke_oath", "Invoke a Broken Oath"),
    MenuItem("f", "make_greek_fire", "Make Greek Fire"),
    MenuItem("i", "paint_icon", "Paint an Icon"),
    MenuItem("v", "venerate_icon", "Venerate an Icon"),
    MenuItem("a", "mothers_curse", "A Mother's Curse"),
    # Sin, tarnish and the Goetic Arts (RoP: The Infernal).
    MenuItem("n", "indulge_sin", "Confidence through Sin"),
    MenuItem("u", "infernal_influence", "Infernal Influence"),
    MenuItem("g", "ars_goetia", "Ars Goetia"),
    # The hunt and Area Lore, on a manor and on the road (LoM, C&G).
    MenuItem("h", "hunt_on_manor", "The Hunt"),
    MenuItem("l", "area_lore_on_manor", "Area Lore"),
    MenuItem("h", "hunt_on_journey", "The Hunt"),
    MenuItem("l", "area_lore_on_journey", "Area Lore"),
    # An apprentice's magic and the Gauntlet (Apprentices).
    MenuItem("b", "turbulence", "Turbulence"),
    MenuItem("u", "gauntlet", "The Gauntlet"),
    MenuItem("z", "lose_the_gift", "Lose the Gift"),
    MenuItem("c", "learn_cantation", "Learn a Cantation"),
    # Art & Academe's artists and scholars, between their seasons.
    MenuItem("t", "artist_career", "An Artist's Career"),
    MenuItem("k", "scholar_career", "A Scholar's Career"),
    # Dealing with faeries: the Ars Fabulosa, bargains and offers (RoP: Faerie).
    MenuItem("y", "ars_fabulosa", "Ars Fabulosa"),
    MenuItem("q", "faerie_bargain", "A Faerie Bargain"),
    MenuItem("o", "faerie_offer", "An Offer to Faerie"),
    # The lacuna and the pilgrim (HoH:S, The Church).
    MenuItem("m", "cast_in_lacuna", "Cast in a Lacuna"),
    MenuItem("j", "pilgrimage", "Pilgrimage"),
    # Devotion and the saints (The Church, RoP: The Divine).
    MenuItem("w", "invoke_saint", "Invoke a Saint"),
    MenuItem("x", "threaten_saint", "Threaten a Saint"),
    MenuItem("p", "patron_saint", "Patron Saint"),
    MenuItem("d", "devotion_points", "Devotion Points"),
    MenuItem("g", "act_of_piety", "Indulgence, Vigil or Fast"),
    # A Muslim's baraka and the Hajj (RoP: The Divine).
    MenuItem("b", "invoke_baraka", "Invoke Baraka"),
    MenuItem("j", "hajj", "The Hajj"),
    # Holy influence and tempers (RoP: The Divine).
    MenuItem("h", "holy_influence", "Holy Influence"),
    # Mystic paths, God's aid, the Font and the Commanding Aura (The
    # Church, RoP: The Divine, DE).
    MenuItem("k", "mystic_path", "Mystic Path"),
    MenuItem("q", "spiritual_path", "Spiritual Path"),
    MenuItem("z", "monistic_revelation", "Monistic Revelation"),
    MenuItem("i", "gods_aid", "Invoke God's Aid"),
    MenuItem("o", "font_of_knowledge", "Font of Knowledge"),
    MenuItem("c", "commanding_aura", "Commanding Aura"),
    # House Verditius's Hubris and vendettas (HoH:MC, DE).
    MenuItem("b", "verditius_hubris", "Hubris"),
    # Hermetic spirit magic and theurgy (The Mysteries Revised Edition).
    MenuItem("y", "spirits_and_names", "Spirits and Names"),
    # Dream magic and Hermetic sacrifice (The Mysteries Revised Edition).
    MenuItem("v", "dream_working", "Dream Working"),
    MenuItem("a", "hermetic_sacrifice", "Hermetic Sacrifice"),
    # A certamen duel with another magus (DE pp. 231-233).
    MenuItem("z", "certamen_duel", "Certamen"),
    # Where a character is now: the aura his casting counts.
    MenuItem("h", "whereabouts", "Current Location"),
    # A stay as a guest at another covenant (DE pp. 381, 518).
    MenuItem("u", "guest_stay", "Stay as Guest"),
    # Divination and Hermetic astrology (The Mysteries Revised Edition).
    MenuItem("n", "tmre_divination", "Divination"),
    MenuItem("s", "tmre_astrology", "Astrology"),
    # House Acclaim and Reputation rolls (HoH:TL, HoH:S, LoH, DE).
    MenuItem("h", "house_acclaim", "House Acclaim"),
    MenuItem("r", "reputation_roll", "Reputation Roll"),
    # Philosophic Alchemy's digestions (The Mysteries Revised Edition).
    MenuItem("q", "philosophic_alchemy", "Philosophic Alchemy"),
    # The Great Elixir's test (The Mysteries Revised Edition).
    MenuItem("x", "great_elixir", "Test the Great Elixir"),
    # Gaining and losing Virtues and Flaws in play (Grogs pp. 61-64).
    MenuItem("g", "change_virtues_flaws", "Gain or Lose in Play"),
    # The Rhine's Great Library at Durenmar (Guardians of the Forests).
    MenuItem("s", "library_search", "Search the Great Library"),
    # A tomb's trap springs (Lands of the Nile).
    MenuItem("o", "overcome_trap", "Overcome It"),
    MenuItem("o", "overcome_ward", "Overcome It"),
    # A place with a Faerie aura: crossing into the Faerie Realm.
    MenuItem("t", "cross_threshold", "Cross the Threshold"),
    # A covenant's ships (Hermetic Projects; City & Guild).
    MenuItem("s", "ship_stress", "Stress Check"),
    MenuItem("c", "ship_combat", "Ship Combat"),
    MenuItem("f", "ship_fate", "Sunk or Taken"),
    MenuItem("b", "build_ship", "Build a Ship"),
    MenuItem("x", "detach_ship", "Detach"),
    MenuItem("j", "rejoin_ship", "Rejoin"),
    # Where a covenant is: a mobile covenant logs its stops; its route is
    # planned on Whereabouts.
    MenuItem("o", "add_stop", "Add a Stop"),
    MenuItem("t", "plan_route", "Plan Route"),
    # Shaping the land by magic (Transforming Mythic Europe).
    MenuItem("l", "shape_land", "Shape the Land"),
    # A cleric's career (The Church).
    MenuItem("x", "perform_exorcism", "Perform an Exorcism"),
    # Saga Content's Mystery Cults.
    MenuItem("y", "experiment_script", "Experiment on a Script"),
    # A covenant's Hermetic Projects: the tower's stress check and rituals,
    # the project shown, beginning one; a magus's Wizard's War tunnel.
    MenuItem("s", "tower_stress", "Stress Check"),
    MenuItem("c", "tower_conjure", "Conjure Levels"),
    MenuItem("w", "show_project", "Show Project"),
    MenuItem("b", "begin_project", "Begin Project"),
    MenuItem("o", "open_tunnel", "Open a Tunnel"),
    # A lord's marriages: the chosen one ends (LoM p. 11; DE pp. 148, 513).
    MenuItem("x", "end_marriage", "End a Marriage"),
    # A covenant's Menagerie (Hermetic Projects): taming the chosen beast.
    MenuItem("t", "tame_beast", "Tame a Beast"),
    MenuItem("w", "menagerie_award", "Reputation Award"),
    # A covenant's staged Hermetic Project: a Burning City's warning bell,
    # an Intangible Assassin's connections and Aegis, a Living Corpse's
    # death roll.
    MenuItem("b", "warning_bell", "Warning Bell"),
    MenuItem("g", "gather_connection", "Gather a Connection"),
    MenuItem("a", "lower_aegis", "Lower an Aegis"),
    MenuItem("r", "death_roll", "Death Roll"),
    # Polemic and Charter Strength (Transforming Mythic Europe pp. 27-36).
    MenuItem("c", "circulate_text", "Circulate a Text"),
    MenuItem("d", "draft_charter", "Draft the Charter"),
    MenuItem("o", "seek_loophole", "Seek a Loophole"),
    # A Criamon magus's path: plan the next avenue (HoH:MC pp. 58-73).
    MenuItem("v", "follow_avenue", "Follow an Avenue"),
)

#: The More commands offered in one section only, by that section's id.
MORE_SECTIONS: dict[str, str] = {
    "lab_text_access": "section-hermetic-background",
    "edit_fatigue": "section-char-health",
    "take_harm": "section-char-health",
    "recovery_roll": "section-char-health",
    "end_session": "section-reputations",
    "what_changed": "section-reputations",
    "cast_glance": SESSIONS_SECTION,
    "begin_session": SESSIONS_SECTION,
    "close_session": SESSIONS_SECTION,
    "read_chronicle": SESSIONS_SECTION,
    "send_message": SESSIONS_SECTION,
    "teaching_requests": "section-char-season",
    "study_path": "section-char-season",
    "tourney_season": "section-reputations",
    "melee_event": "section-reputations",
    "command_beast": "section-personality-traits",
    "place_aging_points": "section-aging",
    "resolve_twilight": "section-aging",
    "disguise_roll": "section-char-covers",
    "whereabouts": "section-casting",
    "guest_stay": "section-casting",
    "suggest_story": "section-cov-hooks",
    "grow_story": REGION_STORIES_SECTION,
    "trait_roll": "section-personality-traits",
    "familiar_trait_roll": "section-fam-personality-traits",
    "edit_familiar_fatigue": "section-fam-health",
    "withdraw_case": CASES_SECTION,
    "war_end": CASES_SECTION,
    "neutralize_shard": TOKENS_SECTION,
    "tribunal_longevity": TOKENS_SECTION,
    "roll_fair": FAIRS_SECTION,
    "court_roll": COURT_CASES_SECTION,
    "roll_table": TABLES_SECTION,
    "battle_event": BATTLES_SECTION,
    "redeem_gratitude": GRATITUDE_SECTION,
    "buy_manor": MANORS_SECTION,
    "assart": MANORS_SECTION,
    "winter_roll": ESTABLISHMENTS_SECTION,
    "settle_inheritance": HOUSEHOLD_SECTION,
    "conflict_battle_event": CONFLICT_BATTLES_SECTION,
    "battle_muster": CONFLICT_BATTLES_SECTION,
    "fight_options": FIGHTS_SECTION,
    "next_blow": FIGHTS_SECTION,
    "next_round": FIGHTS_SECTION,
    "add_combatant": FIGHTS_SECTION,
    "edit_combatant": FIGHTS_SECTION,
    "remove_combatant": FIGHTS_SECTION,
    "form_group": FIGHTS_SECTION,
    "break_group": FIGHTS_SECTION,
    "restart_fight": FIGHTS_SECTION,
    "group_morale": FIGHTS_SECTION,
    "rally_group": FIGHTS_SECTION,
    "next_siege_event": SIEGES_SECTION,
    "siege_actions": SIEGES_SECTION,
    "craft_by_magic": "section-known-spells",
    "seal_charter": CHARTER_SECTION,
    "use_charter_template": CHARTER_SECTION,
    "save_charter_template": CHARTER_SECTION,
    # The Theban treasury's loans of vis.
    "lend_vis": TOKENS_SECTION,
    "repay_vis_loan": TOKENS_SECTION,
    # The Rhine's ranks: masters' marks and archmagi's challenges.
    "rhine_mark": GILDS_SECTION,
    "rhine_challenge": GILDS_SECTION,
    # The hunt and Area Lore on the chosen manor.
    "hunt_on_manor": MANORS_SECTION,
    "area_lore_on_manor": MANORS_SECTION,
    # The Rhine's Great Library at Durenmar (Guardians of the Forests).
    "library_search": LIBRARY_RULES_SECTION,
    # A tomb's trap springs (Lands of the Nile).
    "overcome_trap": "section-nb-tomb-traps",
    "overcome_ward": "section-nb-tomb-wards",
    # A covenant's ships: the chosen ship's stress check and combat.
    "ship_stress": "section-pos-ship",
    "ship_combat": "section-pos-ship",
    "ship_fate": "section-pos-ship",
    "build_ship": "section-pos-ship",
    "plan_route": WHEREABOUTS_SECTION,
    # A cleric's career: the exorcism on Holy Orders.
    "perform_exorcism": ORDERS_SECTION,
    # Saga Content's Mystery Cults.
    # A covenant's Hermetic Projects: the tower's, and the projects list's.
    "tower_stress": "section-cov-tower",
    "tower_conjure": "section-cov-tower",
    "show_project": "section-cov-projects",
    # A lord's marriages: End a Marriage on the chosen one.
    "end_marriage": "section-nb-marriages",
    # A covenant's Menagerie: Tame a Beast on the chosen beast.
    "tame_beast": "section-cov-menagerie-beasts",
    "menagerie_award": "section-cov-menagerie-beasts",
    # Polemic: Circulate a Text on an argument's chosen text.
    "circulate_text": ARGUMENT_TEXTS_SECTION,
    # A Criamon magus's path: Follow an Avenue.
    "follow_avenue": "section-char-criamon-path",
}

#: Where in the navigation each record can be created: the saga, and
#: the covenant, group or record it would sit beside. A new character or
#: laboratory defaults to the covenant on show. Binding a Familiar also
#: needs a magus without one (and, on a character, that character to be a
#: magus).
CREATE_PLACES: dict[str, frozenset[NodeKind]] = {
    "create_covenant": frozenset({NodeKind.SAGA}),
    "create_tribunal": frozenset({NodeKind.SAGA, NodeKind.REGION, NodeKind.TRIBUNAL}),
    "create_neighbour": frozenset(
        {NodeKind.SAGA, NodeKind.REGION, NodeKind.NEIGHBOUR_GROUP, NodeKind.NEIGHBOUR}
    ),
    "create_creature": frozenset({NodeKind.SAGA, NodeKind.BESTIARY, NodeKind.CREATURE}),
    "create_character": frozenset(
        {NodeKind.SAGA, NodeKind.COVENANT, NodeKind.CHARACTER_GROUP, NodeKind.CHARACTER}
    ),
    "create_laboratory": frozenset(
        {
            NodeKind.SAGA,
            NodeKind.COVENANT,
            NodeKind.LABORATORY_GROUP,
            NodeKind.LABORATORY,
        }
    ),
    "create_familiar": frozenset(
        {NodeKind.SAGA, NodeKind.COVENANT, NodeKind.CHARACTER_GROUP, NodeKind.CHARACTER}
    ),
}

#: Each record sheet's own section: the top panel that names the record.
#: With focus there (or on the record in the navigation), Delete and More
#: act on the record itself.
RECORD_SECTION: dict[NodeKind, str] = {
    NodeKind.CHARACTER: "section-char-info",
    NodeKind.COVENANT: "section-cov-info",
    NodeKind.LABORATORY: "section-lab-identity",
    NodeKind.FAMILIAR: "section-fam-info",
    NodeKind.TRIBUNAL: TRIBUNAL_INFO_SECTION,
    NodeKind.NEIGHBOUR: NEIGHBOUR_INFO_SECTION,
    NodeKind.CREATURE: CREATURE_INFO_SECTION,
}


# -- deciding what is available --


class ActionFacts(Protocol):
    """What `available` asks the front-end about where the user is."""

    @property
    def saga(self) -> Saga: ...

    @property
    def selected_kind(self) -> NodeKind | None: ...

    @property
    def selected_covenant(self) -> Covenant | None: ...

    @property
    def selected_character(self) -> Character | None: ...

    @property
    def selected_laboratory(self) -> Laboratory | None: ...

    def active_section(self) -> str | None:
        """The id of the section focus is in, if any."""
        ...

    def player_may(self, action: str) -> bool:
        """Whether whoever is using the app may run `action` here."""
        ...

    def on_record(self) -> bool:
        """Whether focus is on the record itself rather than one of its
        sections."""
        ...

    def creation_record(self) -> Character | Covenant | Laboratory | None:
        """The record on show that has an In Creation / In Play mode."""
        ...

    def device_action_enabled(self, action: str) -> bool:
        """Whether Instill an Effect or Use a Charge can act on the chosen
        device."""
        ...

    def to_give(self) -> giving.Gift | None:
        """What Give would give: the chosen row of the section focus is
        in, if that section lists things that can be given away."""
        ...

    def record_to_export(self) -> Record | None: ...

    def record_to_delete(
        self,
    ) -> (
        Covenant
        | Character
        | Laboratory
        | Familiar
        | Tribunal
        | Neighbour
        | Creature
        | None
    ): ...

    def can_send_files(self) -> bool:
        """Whether an exported file has somewhere to go (not over SSH)."""
        ...

    def chosen_row(self, section: str) -> int | None:
        """The row chosen in `section`'s list (its index in the list the
        section shows), or None with none chosen or no such list."""
        ...


def silver_purse(facts: ActionFacts) -> giving.Holder | None:
    """Whose silver Give Silver gives in the section focus is in: the
    character's on Personal Gear, the covenant's on Wealth."""
    whose = SILVER_SECTIONS.get(facts.active_section() or "")
    if whose == "character":
        return facts.selected_character
    if whose == "covenant":
        return facts.selected_covenant
    return None
