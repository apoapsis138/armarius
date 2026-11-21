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
    seasons,
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
    Session,
    Tribunal,
)
from .rules import (
    covenfolk,
)
from .sections import (
    BOOK_SECTIONS,
    BOOKS_SECTION,
    CATALOGS_SECTION,
    CHAR_AHEAD_SECTION,
    CORE_SECTIONS,
    CREATURE_INFO_SECTION,
    DEVICE_SECTIONS,
    HANDOUTS_SECTION,
    HIDDEN_SECTION,
    HOUSE_RULES_SECTION,
    LAB_VF_SECTIONS,
    NEIGHBOUR_INFO_SECTION,
    PLAYERS_SECTION,
    SCENES_SECTION,
    SESSION_INFO_SECTION,
    SESSION_SCENES_SECTION,
    SESSIONS_SECTION,
    SILVER_SECTIONS,
    SOURCES_SECTION,
    SPELL_SECTION,
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
    #: One Session's own page (sheets/session.py).
    SESSION = "session"


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
        SESSION_INFO_SECTION: _EDIT,
        SCENES_SECTION: _ALL3,
        SESSION_SCENES_SECTION: _ALL3,
        HANDOUTS_SECTION: _ALL3,
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
    NodeKind.SESSION: SESSION_INFO_SECTION,
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

    @property
    def selected_session(self) -> Session | None:
        """The Session on show, on a Session's own page."""
        ...

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
