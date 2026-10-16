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

from . import arms, giving, places, seasons, sourcebooks, world
from . import book_value as bv
from . import familiars as fam
from . import inhabitants as inh
from . import lab_texts as lt
from . import spells as spl
from .models import (
    FULL,
    INHABITANT_KINDS,
    POSSESSION_KINDS,
    TEXT_LONGEVITY,
    Character,
    Covenant,
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
    # Virtues and Flaws can't be edited, only added and deleted.
    for section in (
        "section-vf-virtues",
        "section-vf-flaws",
        "section-fam-vf-virtues",
        "section-fam-vf-flaws",
        *LAB_VF_SECTIONS,
    ):
        verbs[section] = _ADD_REMOVE
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
    ) -> Covenant | Character | Laboratory | Familiar | Tribunal | Neighbour | None: ...

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
    kind = facts.selected_kind
    if action in CREATE_PLACES and kind not in CREATE_PLACES[action]:
        return False
    if action == "edit" and kind == NodeKind.SAGA:
        return True
    if action == "set_date":
        return kind == NodeKind.SAGA
    if action in ("export_saga", "export_pack"):
        return kind == NodeKind.SAGA and facts.can_send_files()
    if action in ("toggle_mode", "creation_worksheet"):
        record = facts.creation_record()
        return (
            record is not None
            and facts.on_record()
            and getattr(record, "detail", FULL) == FULL
            and (action == "toggle_mode" or record.in_creation)
        )
    if action in ("promote", "demote"):
        record = facts.creation_record()
        if not isinstance(record, (Character, Covenant)) or not facts.on_record():
            return False
        step = world.promoted if action == "promote" else world.demoted
        return step(record.detail) is not None
    if action == "give":
        found = facts.to_give()
        return found is not None and giving.blocked(facts.saga, *found) is None
    if action == "give_silver":
        purse = silver_purse(facts)
        return (
            purse is not None
            and giving.blocked(facts.saga, giving.SILVER, purse) is None
        )
    if action == "export_record":
        return (
            facts.can_send_files()
            and facts.record_to_export() is not None
            and facts.on_record()
        )
    if action == "update_record":
        return facts.record_to_export() is not None and facts.on_record()
    if action == "create_familiar":
        character = facts.selected_character
        if kind == NodeKind.CHARACTER and (
            character is None or character.type != "magus"
        ):
            return False
        return bool(fam.unbonded_magi(facts.saga))
    if action == "delete_record":
        return facts.record_to_delete() is not None
    if action == "edit_arms":
        record = facts.record_to_delete()
        return facts.on_record() and record is not None and arms.bears_arms(record)
    if action == "found_covenant":
        return facts.on_record() and places.is_ruin(facts.record_to_delete())
    if action not in _BY_SECTION:
        return True
    return _available_in_section(action, facts, facts.active_section() or "")


#: The actions whose availability depends on the section focus is in.
_BY_SECTION = frozenset(
    {
        "add",
        "remove",
        "edit",
        "restore",
        *MORE_SECTIONS,
        "improve",
        "instill_effect",
        "use_charge",
        "share_spell",
        "filter_lab_texts",
        "perform_ritual",
        "research_bonuses",
        "import_data",
    }
)


def _available_in_section(action: str, facts: ActionFacts, section: str) -> bool:
    """`available` for the actions that depend on the active section."""
    if action in ("add", "remove", "edit"):
        return action in SECTION_VERBS.get(section, ())
    if action == "restore":
        # Offered only while someone has departed (Magi, Companions).
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
    if action in MORE_SECTIONS:
        return section == MORE_SECTIONS[action]
    if action == "improve":
        return section == "section-eco-income"
    if action in ("instill_effect", "use_charge"):
        return section in DEVICE_SECTIONS and facts.device_action_enabled(action)
    if action == "share_spell":
        character = facts.selected_character
        return (
            section == "section-known-spells"
            and character is not None
            and bool(spl.shareable_spells(character))
        )
    if action == "filter_lab_texts":
        return section == LAB_TEXTS_SECTION
    if action == "perform_ritual":
        lab = facts.selected_laboratory
        return (
            section == LAB_TEXTS_SECTION
            and lab is not None
            and any(
                lt.kind(b) == TEXT_LONGEVITY
                for b in lt.texts_of(facts.saga, "laboratory", lab.id)
            )
        )
    if action == "research_bonuses":
        # Library research values are Covenants'.
        covenant = facts.selected_covenant
        return (
            sourcebooks.in_play(bv.SOURCE_BOOK, sourcebooks.saga_books(facts.saga))
            and facts.selected_kind == NodeKind.COVENANT
            and section in LIBRARY_SECTIONS
            and covenant is not None
            and bool(bv.library_subjects(facts.saga, covenant))
        )
    # import_data
    return facts.selected_kind == NodeKind.SAGA or section in LIBRARY_SECTIONS
