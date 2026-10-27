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

from collections.abc import Callable
from enum import StrEnum
from functools import partial
from typing import TYPE_CHECKING, NamedTuple, Protocol

from . import (
    arms,
    giving,
    hosting,
    places,
    seasons,
    selling,
    sourcebooks,
    theban_customs,
    threats,
    traditions,
    world,
)
from . import book_value as bv
from . import devotion as devotion_forms
from . import familiars as fam
from . import goods as gd
from . import inhabitants as inh
from . import lab_texts as lt
from . import mystery_cults as cults_core
from . import mystic_paths as mystic_forms
from . import spells as spl
from .forms import acclaim as acclaim_forms
from .forms import careers
from .forms import charter as charter_forms
from .forms import hubris as hubris_forms
from .forms import tmre_divination as tmre_divination_forms
from .forms import tmre_dreams as tmre_dream_forms
from .forms import tmre_spirits as tmre_spirit_forms
from .forms import tunnel as tunnel_forms
from .models import (
    FULL,
    INHABITANT_KINDS,
    LINE,
    POSSESSION_KINDS,
    TEXT_LONGEVITY,
    Agent,
    Character,
    Covenant,
    Creature,
    Familiar,
    Laboratory,
    Neighbour,
    Saga,
    Tribunal,
)
from .rules import agents as agent_rules
from .rules import apothecary, covenfolk, merchants, options, philosophy
from .rules import clergy as clergy_rules
from .rules import faerie_dealings as faerie_dealing_rules
from .rules import gauntlet as gauntlet_rules
from .rules import goetic as goetic_rules
from .rules import holy_influence as holy_influence_rules
from .rules import sin as sin_rules
from .rules import theban_customs as byzantine
from .rules import tmre_alchemy as tmre_alchemy_rules
from .sections import (
    AGENTS_SECTION,
    AHEAD_SECTION,
    ARGUMENT_TEXTS_SECTION,
    BATTLES_SECTION,
    BOOK_SECTIONS,
    BOOKS_SECTION,
    CASES_SECTION,
    CATALOGS_SECTION,
    CHAR_AHEAD_SECTION,
    CHARTER_LORDS_SECTION,
    CHARTER_SECTION,
    CLAUSES_SECTION,
    CONFLICT_BATTLES_SECTION,
    CONNECTIONS_SECTION,
    CORE_SECTIONS,
    COURT_CASES_SECTION,
    COV_AHEAD_SECTION,
    COV_CHARTER_LORDS_SECTION,
    CREATURE_INFO_SECTION,
    CULT_DEGREES_SECTION,
    CULTS_SECTION,
    DEVICE_SECTIONS,
    ESTABLISHMENTS_SECTION,
    FAIRS_SECTION,
    FIGHTS_SECTION,
    GILDS_SECTION,
    GOODS_SECTION,
    GRATITUDE_SECTION,
    HIDDEN_SECTION,
    HOUSE_RULES_SECTION,
    HOUSEHOLD_SECTION,
    LAB_TEXTS_SECTION,
    LAB_VF_SECTIONS,
    LIBRARY_RULES_SECTION,
    LIBRARY_SECTIONS,
    MANORS_SECTION,
    NEIGHBOUR_INFO_SECTION,
    ORDERS_SECTION,
    PLAYERS_SECTION,
    SIEGES_SECTION,
    SILVER_SECTIONS,
    SOURCES_SECTION,
    SPELL_SECTION,
    TABLES_SECTION,
    TOKENS_SECTION,
    TRADITIONS_SECTION,
    TRAIT_SECTIONS,
    TRIBUNAL_INFO_SECTION,
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
    BOOK_GROUP = "book_group"
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
    MenuItem("g", "give", "Give"),
    MenuItem("s", "give_silver", "Give Silver"),
    MenuItem("l", "lab_text_access", "Lab Texts Read"),
    MenuItem("t", "edit_traditions", "Traditions"),
    MenuItem("d", "disputatio", "Disputatio"),
    MenuItem("f", "edit_fatigue", "Edit Fatigue"),
    MenuItem("h", "take_harm", "Take Harm"),
    MenuItem("y", "recovery_roll", "Recovery Roll"),
    MenuItem("e", "end_session", "End of Session"),
    MenuItem("t", "tourney_season", "Tournament"),
    MenuItem("c", "command_beast", "Command the Beast"),
    MenuItem("a", "place_aging_points", "Place Aging Points"),
    MenuItem("f", "edit_familiar_fatigue", "Edit Fatigue"),
    MenuItem("i", "import_data", "Import"),
    MenuItem("b", "research_bonuses", "Set Up Research Library"),
    MenuItem("x", "export_record", "Export"),
    MenuItem("x", "export_saga", "Export Saga"),
    MenuItem("k", "export_pack", "Export Pack"),
    MenuItem("h", "host_saga", "Host for Players"),
    MenuItem("h", "stop_hosting", "Stop Hosting"),
    MenuItem("u", "update_record", "Update from a File"),
    MenuItem("m", "toggle_mode", "In Creation / In Play"),
    MenuItem("p", "promote", "Promote"),
    MenuItem("o", "demote", "Demote"),
    MenuItem("w", "creation_worksheet", "Creation Worksheet"),
    MenuItem("t", "set_date", "Set Date"),
    MenuItem("a", "edit_arms", "Arms"),
    MenuItem("w", "withdraw_case", "Withdraw"),
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
    MenuItem("n", "next_blow", "Next Blow"),
    MenuItem("r", "next_round", "Next Round"),
    MenuItem("a", "add_combatant", "Add Combatant"),
    MenuItem("e", "edit_combatant", "Edit Combatant"),
    MenuItem("v", "remove_combatant", "Remove Combatant"),
    MenuItem("g", "form_group", "Form a Group"),
    MenuItem("u", "break_group", "Break up a Group"),
    MenuItem("t", "restart_fight", "Restart the Fight"),
    MenuItem("n", "next_siege_event", "Next Siege Event"),
    MenuItem("f", "found_covenant", "Found a Covenant Here"),
    MenuItem("b", "begin_story", "Begin This Story"),
    MenuItem("g", "go_to", "Go To"),
    MenuItem("i", "impress_agent", "Impress"),
    MenuItem("x", "spend_agency_xp", "Spend Agency Experience"),
    MenuItem("t", "set_agent_task", "Set a Task"),
    MenuItem("r", "resolve_agent_task", "Resolve the Task"),
    MenuItem("p", "add_purity", "Add a Purity"),
    MenuItem("j", "plan_journey", "Travel"),
    MenuItem("l", "labor_story", "Labor Points from a Story"),
    MenuItem("v", "invest_labor", "Invest Time or Money"),
    MenuItem("r", "discipline_grog", "Reward or Punish"),
    MenuItem("n", "grog_pension", "Pension"),
    MenuItem("f", "craft_by_magic", "Craft by Magic"),
    MenuItem("s", "seal_charter", "Seal the Charter"),
    MenuItem("b", "break_clause", "Break a Clause"),
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
    MenuItem("d", "devotion_points", "Devotion Points"),
    MenuItem("g", "act_of_piety", "Indulgence, Vigil or Fast"),
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
    # A covenant's ships (Hermetic Projects; City & Guild).
    MenuItem("s", "ship_stress", "Stress Check"),
    MenuItem("c", "ship_combat", "Ship Combat"),
    # Shaping the land by magic (Transforming Mythic Europe).
    MenuItem("l", "shape_land", "Shape the Land"),
    # A cleric's career (The Church).
    MenuItem("p", "petition_church", "Petition the Church"),
    MenuItem("j", "canon_case", "Add Canon Case"),
    MenuItem("o", "holy_orders", "Holy Orders"),
    MenuItem("x", "perform_exorcism", "Perform an Exorcism"),
    # Saga Content's Mystery Cults.
    MenuItem("x", "experiment_script", "Experiment on a Script"),
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
    "tourney_season": "section-reputations",
    "command_beast": "section-personality-traits",
    "place_aging_points": "section-aging",
    "edit_familiar_fatigue": "section-fam-health",
    "withdraw_case": CASES_SECTION,
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
    "next_blow": FIGHTS_SECTION,
    "next_round": FIGHTS_SECTION,
    "add_combatant": FIGHTS_SECTION,
    "edit_combatant": FIGHTS_SECTION,
    "remove_combatant": FIGHTS_SECTION,
    "form_group": FIGHTS_SECTION,
    "break_group": FIGHTS_SECTION,
    "restart_fight": FIGHTS_SECTION,
    "next_siege_event": SIEGES_SECTION,
    "craft_by_magic": "section-known-spells",
    "seal_charter": CHARTER_SECTION,
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
    # A covenant's ships: the chosen ship's stress check and combat.
    "ship_stress": "section-pos-ship",
    "ship_combat": "section-pos-ship",
    # A cleric's career: the exorcism on Holy Orders.
    "perform_exorcism": ORDERS_SECTION,
    # Saga Content's Mystery Cults.
    "experiment_script": CULT_DEGREES_SECTION,
    # A covenant's Hermetic Projects: the tower's, and the projects list's.
    "tower_stress": "section-cov-tower",
    "tower_conjure": "section-cov-tower",
    "show_project": "section-cov-projects",
    # A lord's marriages: End a Marriage on the chosen one.
    "end_marriage": "section-nb-marriages",
    # A covenant's Menagerie: Tame a Beast on the chosen beast.
    "tame_beast": "section-cov-menagerie-beasts",
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


def available(action: str, facts: ActionFacts) -> bool:
    """Whether `action` can run where the user is: what enables add / edit /
    delete and decides what More and New offer."""
    if not facts.player_may(action):
        return False
    if action in CREATE_PLACES and facts.selected_kind not in CREATE_PLACES[action]:
        return False
    if action == "edit" and facts.selected_kind == NodeKind.SAGA:
        return True
    rule = _RECORD_RULES.get(action)
    if rule is not None:
        return rule(facts)
    in_section = _SECTION_RULES.get(action)
    if in_section is None:
        return True
    return in_section(facts, facts.active_section() or "")


# -- the actions that depend on the record on show --


def _on_saga(facts: ActionFacts) -> bool:
    return facts.selected_kind == NodeKind.SAGA


def _exports_saga(facts: ActionFacts) -> bool:
    return _on_saga(facts) and facts.can_send_files()


def _hosts(facts: ActionFacts) -> bool:
    """Host for Players: on the saga, in the storyguide's own window, while
    it isn't hosting yet."""
    return _on_saga(facts) and not hosting.is_hosted_copy() and not hosting.HOST.running


def _stops_hosting(facts: ActionFacts) -> bool:
    return _on_saga(facts) and hosting.HOST.running


def _in_full_creation(facts: ActionFacts, *, worksheet: bool) -> bool:
    """Toggle Mode, or (`worksheet`) the creation worksheet: on a full
    record with an In Creation / In Play mode, the worksheet only while it
    is In Creation."""
    record = facts.creation_record()
    return (
        record is not None
        and facts.on_record()
        and getattr(record, "detail", FULL) == FULL
        and (not worksheet or record.in_creation)
    )


def _changes_detail(facts: ActionFacts, *, up: bool) -> bool:
    """Promote (`up`) or Demote: a character or covenant whose level of
    detail has a step that way."""
    record = facts.creation_record()
    if not isinstance(record, (Character, Covenant)) or not facts.on_record():
        return False
    step = world.promoted if up else world.demoted
    return step(record.detail) is not None


def _on_covenfolk(facts: ActionFacts) -> bool:
    """Reward or Punish and Pension: on a grog who serves a covenant, from
    his record or his Personality Traits."""
    record = facts.creation_record()
    return (
        isinstance(record, Character)
        and record.type == "grog"
        and record.animal is None
        and facts.saga.covenant(record.covenant_id) is not None
        and facts.active_section()
        in (None, RECORD_SECTION[NodeKind.CHARACTER], "section-personality-traits")
    )


def _commands_beast(facts: ActionFacts) -> bool:
    """Command the Beast: on a tamed animal's Personality Traits."""
    record = facts.creation_record()
    return (
        isinstance(record, Character)
        and record.animal is not None
        and facts.active_section() in (None, "section-personality-traits")
    )


def _gives(facts: ActionFacts) -> bool:
    found = facts.to_give()
    return found is not None and giving.blocked(facts.saga, *found) is None


def _gives_silver(facts: ActionFacts) -> bool:
    purse = silver_purse(facts)
    return (
        purse is not None and giving.blocked(facts.saga, giving.SILVER, purse) is None
    )


def _exports_record(facts: ActionFacts) -> bool:
    return (
        facts.can_send_files()
        and facts.record_to_export() is not None
        and facts.on_record()
    )


def _updates_record(facts: ActionFacts) -> bool:
    return facts.record_to_export() is not None and facts.on_record()


def _binds_familiar(facts: ActionFacts) -> bool:
    """A magus without a familiar exists, and on a character, it is one."""
    character = facts.selected_character
    if facts.selected_kind == NodeKind.CHARACTER and (
        character is None or character.type != "magus"
    ):
        return False
    return bool(fam.unbonded_magi(facts.saga))


def _disputes(facts: ActionFacts) -> bool:
    """A character, with another to dispute with, when Art & Academe is in
    play."""
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and facts.selected_character is not None
        and len(facts.saga.characters) > 1
        and sourcebooks.in_play("A&A", sourcebooks.saga_books(facts.saga))
    )


def _makes_ligature(facts: ActionFacts) -> bool:
    """A character with Artes Liberales, Philosophiae or Medicine, when Art
    & Academe is in play."""
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and character is not None
        and bool(philosophy.ligature_abilities(character))
        and sourcebooks.in_play("A&A", sourcebooks.saga_books(facts.saga))
    )


def _keeps_byzantine_custom(
    test: Callable[[Saga, Character], bool],
) -> Callable[[ActionFacts], bool]:
    """A Byzantine custom's More command: on a person's record (not an
    animal's), with The Sundered Eagle in play, when `test` allows it."""

    def rule(facts: ActionFacts) -> bool:
        character = facts.selected_character
        return (
            facts.selected_kind == NodeKind.CHARACTER
            and facts.on_record()
            and character is not None
            and character.animal is None
            and theban_customs.in_play(facts.saga)
            and test(facts.saga, character)
        )

    return rule


def _joins_traditions(facts: ActionFacts) -> bool:
    """A full or sketched character, with a tradition the saga offers or
    one they belong to."""
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and facts.on_record()
        and character is not None
        and character.detail != LINE
        and bool(traditions.offered(facts.saga) or character.traditions)
    )


def _deletes_record(facts: ActionFacts) -> bool:
    return facts.record_to_delete() is not None


def _bears_arms(facts: ActionFacts) -> bool:
    record = facts.record_to_delete()
    return facts.on_record() and record is not None and arms.bears_arms(record)


def _on_ruin(facts: ActionFacts) -> bool:
    return facts.on_record() and places.is_ruin(facts.record_to_delete())


def _on_dormant_threat(facts: ActionFacts) -> bool:
    return facts.on_record() and threats.is_dormant(facts.record_to_delete())


def _goes_to(facts: ActionFacts) -> bool:
    """Go To: on a record whose page names another record. On a
    character, covenant or laboratory, whose sections have More items of
    their own, only on the record itself or its Connections."""
    from . import connections
    from .forms import go_to

    record = facts.record_to_delete()
    if record is None or not go_to.has_targets(facts.saga, record):
        return False
    if isinstance(record, connections.SHOWN_ON):
        return facts.on_record() or facts.active_section() == CONNECTIONS_SECTION
    return True


#: When each action that acts on the record on show (or the saga) is
#: offered, one rule per action (Strategy, as a table).

# Sin, tarnish and the Goetic Arts (RoP: The Infernal).


def _on_traits(facts: ActionFacts) -> Character | None:
    """The character on show, from his record or his Personality Traits."""
    character = facts.selected_character
    if (
        facts.selected_kind != NodeKind.CHARACTER
        or character is None
        or facts.active_section()
        not in (None, RECORD_SECTION[NodeKind.CHARACTER], "section-personality-traits")
    ):
        return None
    return character


def _sins(facts: ActionFacts) -> bool:
    """Confidence through Sin: a trait or Flaw with a penchant for a sin."""
    character = _on_traits(facts)
    return character is not None and bool(sin_rules.sinful_traits(character))


def _influences(facts: ActionFacts) -> bool:
    """Infernal Influence: a sinner, or one who knows Infernal Lore."""
    character = _on_traits(facts)
    return character is not None and (
        bool(sin_rules.sinful_traits(character))
        or any(a.name == "Infernal Lore" for a in character.abilities)
    )


def _works_goetia(facts: ActionFacts) -> bool:
    """Ars Goetia: one who holds a Goetic Art, from his record or a
    tradition's chapter."""
    character = facts.selected_character
    section = facts.active_section() or ""
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and character is not None
        and goetic_rules.holds_goetic_art(character)
        and (
            section in ("", RECORD_SECTION[NodeKind.CHARACTER])
            or section.startswith(traditions.SECTION_PREFIX)
        )
    )


# An apprentice's magic and the Gauntlet (Apprentices).


def _apprentices_character(facts: ActionFacts, *sections: str) -> Character | None:
    """The character on show, from his record or one of `sections`,
    while Apprentices is in play."""
    character = facts.selected_character
    section = facts.active_section() or ""
    if (
        facts.selected_kind != NodeKind.CHARACTER
        or character is None
        or not gauntlet_rules.in_play(facts.saga)
        or section not in ("", RECORD_SECTION[NodeKind.CHARACTER], *sections)
    ):
        return None
    return character


def _turbulent(facts: ActionFacts) -> bool:
    """Turbulence: a Gifted character, from his record or This Season."""
    character = _apprentices_character(facts, "section-char-season")
    return character is not None and gauntlet_rules.gifted(character)


def _faces_gauntlet(facts: ActionFacts) -> bool:
    """The Gauntlet: an apprentice (the Social Status)."""
    character = _apprentices_character(facts)
    return character is not None and gauntlet_rules.apprentice(character)


def _may_lose_gift(facts: ActionFacts) -> bool:
    """Lose the Gift: a Gifted apprentice."""
    character = _apprentices_character(facts)
    return (
        character is not None
        and gauntlet_rules.apprentice(character)
        and gauntlet_rules.gifted(character)
    )


def _learns_cantation(facts: ActionFacts) -> bool:
    """Learn a Cantation: on Known Spells, with the saga option on."""
    character = _apprentices_character(facts, "section-known-spells")
    return (
        character is not None
        and facts.active_section() == "section-known-spells"
        and gauntlet_rules.cantations_in_play(facts.saga)
    )


# Art & Academe's artists and scholars.


def _academe_person(facts: ActionFacts) -> Character | None:
    """A person's record (not an animal's), with Art & Academe in play."""
    character = facts.selected_character
    if (
        facts.selected_kind != NodeKind.CHARACTER
        or not facts.on_record()
        or character is None
        or character.animal is not None
        or not sourcebooks.in_play("A&A", sourcebooks.saga_books(facts.saga))
    ):
        return None
    return character


def _makes_art(facts: ActionFacts) -> bool:
    """An Artist's Career: someone with a Craft or Profession."""
    character = _academe_person(facts)
    return character is not None and bool(careers.artist_crafts(character))


def _studies(facts: ActionFacts) -> bool:
    """A Scholar's Career: anyone."""
    return _academe_person(facts) is not None


# Dealing with faeries (RoP: Faerie).


def _faerie_dealer(facts: ActionFacts) -> Character | None:
    """A person on show, from his record or a tradition's chapter, with
    Realms of Power: Faerie in play."""
    character = facts.selected_character
    section = facts.active_section() or ""
    if (
        facts.selected_kind != NodeKind.CHARACTER
        or character is None
        or character.animal is not None
        or not sourcebooks.in_play("RoP:F", sourcebooks.saga_books(facts.saga))
        or not (
            section in ("", RECORD_SECTION[NodeKind.CHARACTER])
            or section.startswith(traditions.SECTION_PREFIX)
        )
    ):
        return None
    return character


def _bargains_with_faeries(facts: ActionFacts) -> bool:
    """Ars Fabulosa and A Faerie Bargain: one who holds a bargaining
    power."""
    character = _faerie_dealer(facts)
    return character is not None and faerie_dealing_rules.bargains(character)


def _offers_to_faerie(facts: ActionFacts) -> bool:
    """An Offer to Faerie: any person."""
    return _faerie_dealer(facts) is not None


# The lacuna and the pilgrim (HoH:S, The Church).


def _goes_on_pilgrimage(facts: ActionFacts, section: str) -> bool:
    """Pilgrimage: on a person's This Season, with The Church in play
    (any pilgrim, grogs too: The Church p. 16)."""
    character = facts.selected_character
    return (
        section == "section-char-season"
        and character is not None
        and character.animal is None
        and sourcebooks.in_play("TC", sourcebooks.saga_books(facts.saga))
    )


def _casts_in_lacuna(facts: ActionFacts, section: str) -> bool:
    """Cast in a Lacuna: on a magus's Known Spells, with Houses of Hermes:
    Societates in play."""
    character = facts.selected_character
    return (
        section == "section-known-spells"
        and character is not None
        and character.type == "magus"
        and sourcebooks.in_play("HoH:S", sourcebooks.saga_books(facts.saga))
    )


def _keeps_devotion(test: Callable[[Saga], bool]) -> Callable[[ActionFacts], bool]:
    """Devotion and the saints' More commands: on a person's record (not
    an animal's), when `test` finds the saga's books allow it."""

    def rule(facts: ActionFacts) -> bool:
        character = facts.selected_character
        return (
            facts.selected_kind == NodeKind.CHARACTER
            and facts.on_record()
            and character is not None
            and character.animal is None
            and test(facts.saga)
        )

    return rule


# Holy influence and tempers (RoP: The Divine).


def _influences_holily(facts: ActionFacts) -> bool:
    """Holy Influence: a person of holy standing (clergy, True Faith,
    Dominion Lore...) on his Personality Traits, with Realms of Power: The
    Divine in play."""
    character = _on_traits(facts)
    return (
        character is not None
        and character.animal is None
        and holy_influence_rules.has_standing(character)
        and sourcebooks.in_play("RoP:D", sourcebooks.saga_books(facts.saga))
    )


# Mystic paths, God's aid, the Font and the Commanding Aura.


def _walks_in_faith(
    test: Callable[[Saga, Character], bool],
) -> Callable[[ActionFacts], bool]:
    """A holy life's More commands: on a person's record or Personality
    Traits, when `test` finds the saga and the character allow it."""

    def rule(facts: ActionFacts) -> bool:
        character = _on_traits(facts)
        return (
            character is not None
            and character.animal is None
            and test(facts.saga, character)
        )

    return rule


# House Verditius's Hubris and vendettas.


def _is_proud(facts: ActionFacts) -> bool:
    """Hubris: a Verditius with the Flaw or the trait, on his Personality
    Traits."""
    character = _on_traits(facts)
    return character is not None and hubris_forms.offers(facts.saga, character)


# Hermetic spirit magic and theurgy (The Mysteries Revised Edition).


def _works_with_spirits(facts: ActionFacts) -> bool:
    """Spirits and Names: a magus with one of the Mysteries, from his
    record or his Known Spells."""
    character = facts.selected_character
    return (
        facts.selected_kind == NodeKind.CHARACTER
        and character is not None
        and facts.active_section()
        in (None, RECORD_SECTION[NodeKind.CHARACTER], "section-known-spells")
        and tmre_spirit_forms.offers(character)
    )


# Dream magic and Hermetic sacrifice (The Mysteries Revised Edition).


def _on_known_spells(
    offers: Callable[[Saga, Character], bool],
) -> Callable[[ActionFacts], bool]:
    """A Mystery's More command: on the character's record or his Known
    Spells, when `offers` allows it."""

    def rule(facts: ActionFacts) -> bool:
        character = facts.selected_character
        return (
            facts.selected_kind == NodeKind.CHARACTER
            and character is not None
            and facts.active_section()
            in (None, RECORD_SECTION[NodeKind.CHARACTER], "section-known-spells")
            and offers(facts.saga, character)
        )

    return rule


# Divination and Hermetic astrology (The Mysteries Revised Edition).


def _reads_signs(
    offers: Callable[[Saga, Character], bool],
) -> Callable[[ActionFacts], bool]:
    """Divination and Astrology: on a person's record, when `offers`
    allows it."""

    def rule(facts: ActionFacts) -> bool:
        character = facts.selected_character
        return (
            facts.selected_kind == NodeKind.CHARACTER
            and character is not None
            and character.animal is None
            and facts.active_section() in (None, RECORD_SECTION[NodeKind.CHARACTER])
            and offers(facts.saga, character)
        )

    return rule


# House Acclaim and Reputation rolls (HoH:TL, HoH:S, LoH, DE).


def _on_reputations(facts: ActionFacts) -> Character | None:
    """The character on show, from his Reputations."""
    character = facts.selected_character
    if (
        facts.selected_kind != NodeKind.CHARACTER
        or character is None
        or facts.active_section() != "section-reputations"
    ):
        return None
    return character


def _keeps_acclaim(facts: ActionFacts) -> bool:
    """House Acclaim: a magus of Bonisagus or Flambeau, or one holding it."""
    character = _on_reputations(facts)
    return character is not None and acclaim_forms.offers(facts.saga, character)


def _has_reputation(facts: ActionFacts) -> bool:
    """Reputation Roll: anyone with a Reputation."""
    character = _on_reputations(facts)
    return character is not None and bool(character.reputations)


def _churchgoer(*, without_tab: bool = False) -> Callable[[ActionFacts], bool]:
    """A cleric's career's More commands: on a person's record (not an
    animal's) while The Church is in play; Holy Orders (`without_tab`)
    only while the sheet has no Church tab, where e edits them."""

    def rule(facts: ActionFacts) -> bool:
        character = facts.selected_character
        return (
            facts.selected_kind == NodeKind.CHARACTER
            and facts.on_record()
            and character is not None
            and character.animal is None
            and devotion_forms.the_church(facts.saga)
            and not (without_tab and clergy_rules.has_church_tab(character))
        )

    return rule


# A covenant's Hermetic Projects (Hermetic Projects).

#: Where Begin Project is offered: the covenant's record and the
#: sections of its Attributes tab.
BEGIN_PROJECT_SECTIONS = (
    None,
    RECORD_SECTION[NodeKind.COVENANT],
    "section-cov-description",
    "section-cov-reputations",
    "section-cov-boons",
    "section-cov-hooks",
)


def _begins_project(facts: ActionFacts) -> bool:
    """Begin Project: on a full covenant's record or Attributes tab."""
    covenant = facts.selected_covenant
    return (
        facts.selected_kind == NodeKind.COVENANT
        and covenant is not None
        and covenant.detail == FULL
        and facts.active_section() in BEGIN_PROJECT_SECTIONS
    )


_RECORD_RULES: dict[str, Callable[[ActionFacts], bool]] = {
    "set_date": _on_saga,
    "export_saga": _exports_saga,
    "export_pack": _exports_saga,
    "host_saga": _hosts,
    "stop_hosting": _stops_hosting,
    "toggle_mode": partial(_in_full_creation, worksheet=False),
    "creation_worksheet": partial(_in_full_creation, worksheet=True),
    "promote": partial(_changes_detail, up=True),
    "demote": partial(_changes_detail, up=False),
    "give": _gives,
    "command_beast": _commands_beast,
    "discipline_grog": _on_covenfolk,
    "grog_pension": _on_covenfolk,
    "edit_traditions": _joins_traditions,
    "disputatio": _disputes,
    "give_silver": _gives_silver,
    "export_record": _exports_record,
    "update_record": _updates_record,
    "create_familiar": _binds_familiar,
    "delete_record": _deletes_record,
    "edit_arms": _bears_arms,
    "found_covenant": _on_ruin,
    "begin_story": _on_dormant_threat,
    "go_to": _goes_to,
    # A scholar's ligature (Art & Academe).
    "make_ligature": _makes_ligature,
    # The Theban Tribunal's Byzantine customs (The Sundered Eagle).
    "theban_letter": _keeps_byzantine_custom(lambda _s, _c: True),
    "invoke_oath": _keeps_byzantine_custom(lambda _s, _c: True),
    "make_greek_fire": _keeps_byzantine_custom(lambda _s, _c: True),
    "paint_icon": _keeps_byzantine_custom(
        lambda saga, c: (
            byzantine.icon_problem(c) is None and bool(theban_customs.church_list(saga))
        )
    ),
    "venerate_icon": _keeps_byzantine_custom(
        lambda saga, _c: bool(theban_customs.icon_choices(saga))
    ),
    "mothers_curse": _keeps_byzantine_custom(lambda _s, _c: True),
    # Sin, tarnish and the Goetic Arts (RoP: The Infernal).
    "indulge_sin": _sins,
    "infernal_influence": _influences,
    "ars_goetia": _works_goetia,
    # An apprentice's magic and the Gauntlet (Apprentices).
    "turbulence": _turbulent,
    "gauntlet": _faces_gauntlet,
    "lose_the_gift": _may_lose_gift,
    "learn_cantation": _learns_cantation,
    # Art & Academe's artists and scholars.
    "artist_career": _makes_art,
    "scholar_career": _studies,
    # Dealing with faeries (RoP: Faerie).
    "ars_fabulosa": _bargains_with_faeries,
    "faerie_bargain": _bargains_with_faeries,
    "faerie_offer": _offers_to_faerie,
    # Devotion and the saints (The Church, RoP: The Divine).
    "invoke_saint": _keeps_devotion(devotion_forms.invokes),
    "threaten_saint": _keeps_devotion(devotion_forms.threatens),
    "devotion_points": _keeps_devotion(devotion_forms.the_church),
    "act_of_piety": _keeps_devotion(devotion_forms.the_church),
    # Holy influence and tempers (RoP: The Divine).
    "holy_influence": _influences_holily,
    # Mystic paths, God's aid, the Font and the Commanding Aura.
    "mystic_path": _walks_in_faith(mystic_forms.offers_path),
    "spiritual_path": _walks_in_faith(mystic_forms.offers_spiritual),
    "monistic_revelation": _walks_in_faith(mystic_forms.offers_revelation),
    "gods_aid": _walks_in_faith(mystic_forms.offers_aid),
    "font_of_knowledge": _walks_in_faith(mystic_forms.offers_font),
    "commanding_aura": _walks_in_faith(mystic_forms.offers_aura),
    # House Verditius's Hubris and vendettas.
    "verditius_hubris": _is_proud,
    # Hermetic spirit magic and theurgy (The Mysteries Revised Edition).
    "spirits_and_names": _works_with_spirits,
    # Dream magic and Hermetic sacrifice (The Mysteries Revised Edition).
    "dream_working": _on_known_spells(tmre_dream_forms.offers_dreams),
    "hermetic_sacrifice": _on_known_spells(tmre_dream_forms.offers_sacrifice),
    # Divination and Hermetic astrology (The Mysteries Revised Edition).
    "tmre_divination": _reads_signs(tmre_divination_forms.offers_divination),
    "tmre_astrology": _reads_signs(tmre_divination_forms.offers_astrology),
    # House Acclaim and Reputation rolls (HoH:TL, HoH:S, LoH, DE).
    "house_acclaim": _keeps_acclaim,
    "reputation_roll": _has_reputation,
    # A cleric's career (The Church).
    "petition_church": _churchgoer(),
    "canon_case": _churchgoer(),
    "holy_orders": _churchgoer(without_tab=True),
    # A covenant's Hermetic Projects: Begin Project on its record and its
    # Attributes; a magus's tunnel on his Known Spells.
    "begin_project": _begins_project,
    "open_tunnel": _on_known_spells(tunnel_forms.offers),
}


# -- the actions that depend on the section focus is in --


def _has_verb(action: str) -> Callable[[ActionFacts, str], bool]:
    def rule(_facts: ActionFacts, section: str) -> bool:
        return action in SECTION_VERBS.get(section, ())

    return rule


def _restores(facts: ActionFacts, section: str) -> bool:
    """Offered only while someone has departed (Magi, Companions)."""
    covenant = facts.selected_covenant
    return (
        "restore" in SECTION_VERBS.get(section, ())
        and covenant is not None
        and bool(
            inh.departed_entries_for_kind(
                facts.saga, covenant, section.removeprefix("section-inh-")
            )
        )
    )


def _in_more_section(action: str) -> Callable[[ActionFacts, str], bool]:
    def rule(_facts: ActionFacts, section: str) -> bool:
        return section == MORE_SECTIONS[action]

    return rule


def _improves(_facts: ActionFacts, section: str) -> bool:
    return section == "section-eco-income"


def _acts_on_device(action: str) -> Callable[[ActionFacts, str], bool]:
    def rule(facts: ActionFacts, section: str) -> bool:
        return section in DEVICE_SECTIONS and facts.device_action_enabled(action)

    return rule


def _shares_spell(facts: ActionFacts, section: str) -> bool:
    character = facts.selected_character
    return (
        section == "section-known-spells"
        and character is not None
        and bool(spl.shareable_spells(character))
    )


def _filters_lab_texts(_facts: ActionFacts, section: str) -> bool:
    return section == LAB_TEXTS_SECTION


def _performs_ritual(facts: ActionFacts, section: str) -> bool:
    lab = facts.selected_laboratory
    return (
        section == LAB_TEXTS_SECTION
        and lab is not None
        and any(
            lt.kind(b) == TEXT_LONGEVITY
            for b in lt.texts_of(facts.saga, "laboratory", lab.id)
        )
    )


def _research_bonuses(facts: ActionFacts, section: str) -> bool:
    """Library research values are Covenants'."""
    covenant = facts.selected_covenant
    return (
        sourcebooks.in_play(bv.SOURCE_BOOK, sourcebooks.saga_books(facts.saga))
        and facts.selected_kind == NodeKind.COVENANT
        and section in LIBRARY_SECTIONS
        and covenant is not None
        and bool(bv.library_subjects(facts.saga, covenant))
    )


def _acts_on_agent(
    test: Callable[[Character, Agent], bool],
) -> Callable[[ActionFacts, str], bool]:
    """A More command on the Agents list, offered only for a chosen agent
    it can act on (Impress only one not yet impressed)."""

    def rule(facts: ActionFacts, section: str) -> bool:
        character = facts.selected_character
        if section != AGENTS_SECTION or character is None:
            return False
        row = facts.chosen_row(section)
        return (
            row is not None
            and 0 <= row < len(character.agents)
            and test(character, character.agents[row])
        )

    return rule


def _adds_purity(facts: ActionFacts, section: str) -> bool:
    """Add a Purity, offered on the Goods list for a chosen good priced by
    purity that has a pure price."""
    if section != GOODS_SECTION:
        return False
    row = facts.chosen_row(section)
    listed = gd.listed(facts.saga)
    return row is not None and 0 <= row < len(listed) and gd.takes_purities(listed[row])


def _works_for_labor(
    test: Callable[[Character], bool],
) -> Callable[[ActionFacts, str], bool]:
    """Labor Points from a Story and Invest Time or Money: on This Season,
    for a character who works for Labor Points (a trader, for most
    investments)."""

    def rule(facts: ActionFacts, section: str) -> bool:
        character = facts.selected_character
        return (
            section == "section-char-season"
            and character is not None
            and character.grog_year is None
            and test(character)
        )

    return rule


def _breaks_clause(facts: ActionFacts, section: str) -> bool:
    """Break a Clause: on the Clauses list, for a chosen clause not yet
    broken."""
    covenant = facts.selected_covenant
    return (
        section == CLAUSES_SECTION
        and covenant is not None
        and charter_forms.can_break(covenant, facts.chosen_row(section))
    )


def _plans_journey(_facts: ActionFacts, section: str) -> bool:
    """Travel, the calculator: on Ahead, the Seasons page's or a
    covenant's."""
    return section in (AHEAD_SECTION, COV_AHEAD_SECTION)


def _on_charter_lord(facts: ActionFacts, section: str) -> bool:
    """Draft the Charter and Seek a Loophole: on a town's or a covenant's
    charter lords, with a lord chosen, while the saga uses the Charter
    Strength rule (TME p. 36)."""
    return (
        section in (CHARTER_LORDS_SECTION, COV_CHARTER_LORDS_SECTION)
        and facts.chosen_row(section) is not None
        and options.is_on(facts.saga, options.CHARTER_STRENGTH)
    )


def _imports(facts: ActionFacts, section: str) -> bool:
    return facts.selected_kind == NodeKind.SAGA or section in LIBRARY_SECTIONS


#: When each action that depends on the active section is offered. An
#: action in neither table is always offered.
_SECTION_RULES: dict[str, Callable[[ActionFacts, str], bool]] = {
    "add": _has_verb("add"),
    "remove": _has_verb("remove"),
    "edit": _has_verb("edit"),
    "restore": _restores,
    "improve": _improves,
    "instill_effect": _acts_on_device("instill_effect"),
    "use_charge": _acts_on_device("use_charge"),
    "use_effect": _acts_on_device("use_effect"),
    "share_spell": _shares_spell,
    "filter_lab_texts": _filters_lab_texts,
    "perform_ritual": _performs_ritual,
    "research_bonuses": _research_bonuses,
    "import_data": _imports,
    "impress_agent": _acts_on_agent(lambda _c, agent: agent_rules.can_impress(agent)),
    "spend_agency_xp": _acts_on_agent(agent_rules.can_spend),
    "set_agent_task": _acts_on_agent(lambda _c, agent: agent_rules.may_be_asked(agent)),
    "resolve_agent_task": _acts_on_agent(
        lambda _c, agent: agent_rules.recruited(agent)
    ),
    "add_purity": _adds_purity,
    "plan_journey": _plans_journey,
    "break_clause": _breaks_clause,
    "labor_story": _works_for_labor(lambda c: bool(merchants.work_abilities(c))),
    "invest_labor": _works_for_labor(merchants.earns_labor),
    # A craftsman's sale of his finished goods, on This Season.
    "sell_goods": _works_for_labor(lambda c: bool(selling.crafts(c))),
    **{action: _in_more_section(action) for action in MORE_SECTIONS},
    # An apothecary's searching and preserving, on This Season.
    "apothecary_store": _works_for_labor(apothecary.keeps_store),
    # The hunt and Area Lore on the road, beside Travel on Ahead.
    "hunt_on_journey": _plans_journey,
    "area_lore_on_journey": _plans_journey,
    # The lacuna and the pilgrim (HoH:S, The Church).
    "cast_in_lacuna": _casts_in_lacuna,
    "pilgrimage": _goes_on_pilgrimage,
    # Philosophic Alchemy's digestions, on This Season.
    "philosophic_alchemy": _works_for_labor(
        lambda c: bool(tmre_alchemy_rules.philosophic_tier(c))
    ),
    # The Great Elixir's test, on Aging & Warping.
    "great_elixir": lambda facts, section: (
        section == "section-aging"
        and facts.selected_character is not None
        and tmre_alchemy_rules.has_great_elixir(facts.selected_character)
    ),
    # Gaining and losing Virtues and Flaws in play (Grogs pp. 61-64).
    "change_virtues_flaws": lambda facts, section: (
        section in ("section-vf-virtues", "section-vf-flaws")
        and facts.selected_kind == NodeKind.CHARACTER
        and facts.selected_character is not None
    ),
    # Shaping the land by magic, on a covenant's Income (TME pp. 54-77).
    "shape_land": lambda facts, section: (
        section == "section-eco-income"
        and facts.selected_kind == NodeKind.COVENANT
        and facts.selected_covenant is not None
        and sourcebooks.in_play("TME", sourcebooks.saga_books(facts.saga))
    ),
    # Experiment on a Script, for a cult's degree with no Script yet, or one
    # whose Script won't do for a Mystagogue (TMRE p. 18).
    "experiment_script": lambda facts, section: (
        section == CULT_DEGREES_SECTION
        and cults_core.offers_experiment(
            facts.saga,
            facts.chosen_row(CULTS_SECTION),
            facts.chosen_row(CULT_DEGREES_SECTION),
        )
    ),
    # Charter Strength (TME p. 36), on a charter's chosen lord.
    "draft_charter": _on_charter_lord,
    "seek_loophole": _on_charter_lord,
}
