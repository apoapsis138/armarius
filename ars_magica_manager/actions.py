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

from . import arms, giving, places, seasons, sourcebooks, threats, traditions, world
from . import book_value as bv
from . import familiars as fam
from . import inhabitants as inh
from . import lab_texts as lt
from . import spells as spl
from .models import (
    FULL,
    INHABITANT_KINDS,
    LINE,
    POSSESSION_KINDS,
    TEXT_LONGEVITY,
    Character,
    Covenant,
    Creature,
    Familiar,
    Laboratory,
    Neighbour,
    Saga,
    Tribunal,
)
from .sections import (
    BOOK_SECTIONS,
    BOOKS_SECTION,
    CASES_SECTION,
    CATALOGS_SECTION,
    CORE_SECTIONS,
    CREATURE_INFO_SECTION,
    DEVICE_SECTIONS,
    FAIRS_SECTION,
    HIDDEN_SECTION,
    HOUSE_RULES_SECTION,
    LAB_TEXTS_SECTION,
    LAB_VF_SECTIONS,
    LIBRARY_SECTIONS,
    NEIGHBOUR_INFO_SECTION,
    PLAYERS_SECTION,
    SILVER_SECTIONS,
    SOURCES_SECTION,
    SPELL_SECTION,
    TABLES_SECTION,
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
            _ALL3 | {"restore"} if kind in inh.AUTO_KINDS else _ALL3
        )
    for kind, _ in seasons.SEASON_KINDS:
        verbs[f"section-cov-seasons-{kind}"] = _ALL3
    for section in DEVICE_SECTIONS:
        verbs[section] = _ALL3
    for kind in POSSESSION_KINDS:
        verbs[f"section-pos-{kind}"] = _ALL3
    for tradition in traditions.all_traditions():
        verbs[traditions.tradition_section(tradition.id)] = _ALL3
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
    MenuItem("p", "perform_ritual", "Perform Ritual"),
    MenuItem("s", "share_spell", "Share Spell"),
    MenuItem("g", "give", "Give"),
    MenuItem("s", "give_silver", "Give Silver"),
    MenuItem("l", "lab_text_access", "Lab Texts Read"),
    MenuItem("t", "edit_traditions", "Traditions"),
    MenuItem("f", "edit_fatigue", "Edit Fatigue"),
    MenuItem("f", "edit_familiar_fatigue", "Edit Fatigue"),
    MenuItem("i", "import_data", "Import"),
    MenuItem("b", "research_bonuses", "Set Up Research Library"),
    MenuItem("x", "export_record", "Export"),
    MenuItem("x", "export_saga", "Export Saga"),
    MenuItem("k", "export_pack", "Export Pack"),
    MenuItem("u", "update_record", "Update from a File"),
    MenuItem("m", "toggle_mode", "In Creation / In Play"),
    MenuItem("p", "promote", "Promote"),
    MenuItem("o", "demote", "Demote"),
    MenuItem("w", "creation_worksheet", "Creation Worksheet"),
    MenuItem("t", "set_date", "Set Date"),
    MenuItem("a", "edit_arms", "Arms"),
    MenuItem("w", "withdraw_case", "Withdraw"),
    MenuItem("r", "roll_fair", "Roll Income"),
    MenuItem("r", "roll_table", "Roll"),
    MenuItem("f", "found_covenant", "Found a Covenant Here"),
    MenuItem("b", "begin_story", "Begin This Story"),
)

#: The More commands offered in one section only, by that section's id.
MORE_SECTIONS: dict[str, str] = {
    "lab_text_access": "section-hermetic-background",
    "edit_fatigue": "section-char-health",
    "edit_familiar_fatigue": "section-fam-health",
    "withdraw_case": CASES_SECTION,
    "roll_fair": FAIRS_SECTION,
    "roll_table": TABLES_SECTION,
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


#: When each action that acts on the record on show (or the saga) is
#: offered, one rule per action (Strategy, as a table).
_RECORD_RULES: dict[str, Callable[[ActionFacts], bool]] = {
    "set_date": _on_saga,
    "export_saga": _exports_saga,
    "export_pack": _exports_saga,
    "toggle_mode": partial(_in_full_creation, worksheet=False),
    "creation_worksheet": partial(_in_full_creation, worksheet=True),
    "promote": partial(_changes_detail, up=True),
    "demote": partial(_changes_detail, up=False),
    "give": _gives,
    "edit_traditions": _joins_traditions,
    "give_silver": _gives_silver,
    "export_record": _exports_record,
    "update_record": _updates_record,
    "create_familiar": _binds_familiar,
    "delete_record": _deletes_record,
    "edit_arms": _bears_arms,
    "found_covenant": _on_ruin,
    "begin_story": _on_dormant_threat,
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
    "share_spell": _shares_spell,
    "filter_lab_texts": _filters_lab_texts,
    "perform_ritual": _performs_ritual,
    "research_bonuses": _research_bonuses,
    "import_data": _imports,
    **{action: _in_more_section(action) for action in MORE_SECTIONS},
}
