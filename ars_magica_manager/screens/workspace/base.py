"""The workspace's shared tables and its base class: the screen's state, the
navigation tree, the detail pane, focus and section tracking, the plumbing
behind a / e / d, More and New, and the actions that aren't about one kind
of record."""

from __future__ import annotations

import asyncio
import random
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from dataclasses import field as dataclass_field
from enum import StrEnum
from functools import cached_property, partial
from pathlib import Path
from typing import Any, ClassVar, NamedTuple

from textual.app import ComposeResult
from textual.binding import ActiveBinding, Binding, BindingType
from textual.containers import Horizontal, VerticalScroll
from textual.content import Content
from textual.css.query import NoMatches
from textual.events import DescendantBlur, DescendantFocus
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    Collapsible,
    Header,
    Static,
    TabbedContent,
    TabPane,
    Tree,
)
from textual.widgets._collapsible import CollapsibleTitle
from textual.widgets.tree import TreeNode

from ... import books as bk
from ... import (
    catalog,
    creation,
    deletion,
    seasons,
    sourcebooks,
    storage,
    transfer,
    vis,
)
from ... import economics as eco
from ... import familiars as fam
from ... import house_rules as hr
from ... import inhabitants as inh
from ... import lab_texts as lt
from ... import laboratories as lab_rules
from ... import sheet_text as st
from ... import spells as spl
from ...markup import escape
from ...models import (
    FOCUS_FLAWS,
    SEASONS,
    TEXT_LONGEVITY,
    Ability,
    Character,
    Covenant,
    Familiar,
    GrogYear,
    Laboratory,
    Saga,
    ScoredTrait,
    SeasonPlan,
    VirtueFlawInstance,
    link_unlinked_features,
    new_instance_id,
    next_season,
)
from ...rules import creation as creation_rules
from ...rules import options as rule_options
from ...rules import seasons as season_rules
from ..fields import (
    FieldsDialog,
)
from ..forms import (
    _character_create_fields,
    _covenant_create_fields,
    _familiar_create_fields,
    _grog_year_dialog,
    _laboratory_create_fields,
    _saga_fields,
    _season_plan_dialog,
    saga_rule_options,
)
from ..pickers import (
    LabVirtueFlawPickerScreen,
    VirtueFlawPickerScreen,
)
from ..prompts import (
    AdvanceSeasonScreen,
    ConfirmScreen,
    MenuScreen,
    _date_fields,
    _export_dialog,
    _move_vis_dialog,
    _scored_trait_dialog,
)
from ..season_records import SeasonRecordsView, SeasonSummaryScreen
from ..sheets import (
    _LIBRARY_SECTIONS,
    DEVICE_SECTIONS,
    HOUSE_RULES_SECTION,
    LAB_FEATURE_SECTIONS,
    LAB_TEXTS_SECTION,
    LAB_VF_SECTIONS,
    SPELL_SECTION,
    BookListView,
    CharacterSheetView,
    CovenantSheetView,
    FamiliarSheetView,
    HouseRulesView,
    LaboratorySheetView,
    SheetView,
    SpellListView,
)
from ..widgets import (
    BottomBar,
    SelectableList,
    SheetSection,
    first_stop,
    is_stop,
    section_of,
    section_stop,
    sheet_focus_chain,
)

#: Covenant Reputations run from -3 to +3.
_COVENANT_REPUTATION_RANGE = (-3, 3)


def _creating(record: Character | Covenant | Laboratory) -> str:
    """The navigation tree's mark on a record still In Creation."""
    return " (creating)" if record.in_creation else ""


class _SectionOps(NamedTuple):
    """What a, d, e and More's Restore do in one sheet section (None: nothing,
    and the key is disabled there). See WorkspaceScreen._section_ops()."""

    add: Callable[[], None] | None = None
    remove: Callable[[], None] | None = None
    edit: Callable[[], None] | None = None
    restore: Callable[[], None] | None = None


@dataclass(frozen=True)
class _TraitList:
    """One of the sheets' scored-trait lists -- a record's Personality Traits
    or Reputations -- for WorkspaceScreen's shared add/edit/remove."""

    owner: str  # the WorkspaceScreen attribute holding the record
    attr: str  # the record's list: "personality_traits" or "reputations"
    section: str
    noun: str  # "Personality Trait" or "Reputation"
    example: str
    selected: str  # the WorkspaceScreen method giving the chosen row's index
    prompt_options: dict[str, Any] = dataclass_field(default_factory=dict)


_CHARACTER_TRAITS = _TraitList(
    "selected_character",
    "personality_traits",
    "section-personality-traits",
    "Personality Trait",
    "e.g. Brave",
    "_selected_personality_trait",
)


_CHARACTER_REPUTATIONS = _TraitList(
    "selected_character",
    "reputations",
    "section-reputations",
    "Reputation",
    "e.g. Skilled Enchanter",
    "_selected_character_reputation",
)


_FAMILIAR_TRAITS = _TraitList(
    "selected_familiar",
    "personality_traits",
    "section-fam-personality-traits",
    "Personality Trait",
    "e.g. Loyal",
    "_selected_familiar_personality_trait",
)


_FAMILIAR_REPUTATIONS = _TraitList(
    "selected_familiar",
    "reputations",
    "section-fam-reputations",
    "Reputation",
    "e.g. Fierce Protector",
    "_selected_familiar_reputation",
)


_COVENANT_REPUTATIONS = _TraitList(
    "selected_covenant",
    "reputations",
    "section-cov-reputations",
    "Reputation",
    "e.g. Feared by the local nobility",
    "_selected_reputation",
    prompt_options={
        "min_score": _COVENANT_REPUTATION_RANGE[0],
        "max_score": _COVENANT_REPUTATION_RANGE[1],
        "include_known": True,
    },
)


#: Which sheet section each covenant Boon/Hook kind lives in.
_BOON_HOOK_SECTION = {"Boon": "section-cov-boons", "Hook": "section-cov-hooks"}


class NodeKind(StrEnum):
    """What a nav-tree node stands for: the first item of its `.data` tuple
    (the second, where there is one, is the record's or covenant's id).
    Also `WorkspaceScreen.selected_kind`."""

    SAGA = "saga"
    COVENANT = "covenant"
    CHARACTER_GROUP = "character_group"
    CHARACTER = "character"
    FAMILIAR = "familiar"
    LABORATORY_GROUP = "laboratory_group"
    LABORATORY = "laboratory"
    SPELLS = "spells"
    HOUSE_RULES = "house_rules"
    SEASONS = "seasons"
    BOOK_GROUP = "book_group"


#: Each sheet's own section: the top panel that names the record. With
#: focus there (or on its tree node), d and More act on the record itself.
_RECORD_SECTION: dict[NodeKind, str] = {
    NodeKind.CHARACTER: "section-char-info",
    NodeKind.COVENANT: "section-cov-info",
    NodeKind.LABORATORY: "section-lab-identity",
    NodeKind.FAMILIAR: "section-fam-info",
}


#: Where in the tree each record can be created (STORY-110): the saga, and
#: the covenant, group or record it would sit beside -- so a sheet's footer
#: offers only what belongs there. A new character or laboratory defaults
#: to the covenant on show. Binding a Familiar also needs a magus without
#: one (and, on a character's node, that character to be a magus).
_CREATE_PLACES: dict[str, frozenset[NodeKind]] = {
    "create_covenant": frozenset({NodeKind.SAGA}),
    "create_character": frozenset(
        {
            NodeKind.SAGA,
            NodeKind.COVENANT,
            NodeKind.CHARACTER_GROUP,
            NodeKind.CHARACTER,
        }
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
        {
            NodeKind.SAGA,
            NodeKind.COVENANT,
            NodeKind.CHARACTER_GROUP,
            NodeKind.CHARACTER,
        }
    ),
}


class MenuItem(NamedTuple):
    """One entry of the More or New menu: the letter that picks it, the
    action WorkspaceBase._available() is asked about, its label, and the
    method that runs it (by default `action_<action>`)."""

    letter: str
    action: str
    label: str
    handler: str = ""

    def run(self, screen: WorkspaceBase) -> None:
        getattr(screen, self.handler or f"action_{self.action}")()


#: New (n): what can be made, each offered only where it belongs (see
#: _CREATE_PLACES).
_NEW_MENU: tuple[MenuItem, ...] = (
    MenuItem("v", "create_covenant", "New Covenant"),
    MenuItem("c", "create_character", "New Character"),
    MenuItem("l", "create_laboratory", "New Laboratory"),
    MenuItem("f", "create_familiar", "Bind Familiar"),
)


#: More (m): what only a few sections, or the record itself, can do. Each
#: is offered only where _available() says it applies.
_MORE_MENU: tuple[MenuItem, ...] = (
    MenuItem("r", "restore", "Restore"),
    MenuItem("i", "improve", "Improve Income"),
    MenuItem("i", "instill_effect", "Instill an Effect"),
    MenuItem("c", "use_charge", "Use a Charge"),
    MenuItem("p", "perform_ritual", "Perform Ritual"),
    MenuItem("s", "share_spell", "Share Spell"),
    MenuItem("v", "move_vis", "Move Vis"),
    MenuItem("l", "lab_text_access", "Lab Texts Read", "_edit_lab_text_access"),
    MenuItem("f", "edit_fatigue", "Edit Fatigue", "_edit_fatigue"),
    MenuItem("f", "edit_familiar_fatigue", "Edit Fatigue", "_edit_familiar_fatigue"),
    MenuItem("i", "import_data", "Import"),
    MenuItem("x", "export_record", "Export"),
    MenuItem("m", "toggle_mode", "In Creation / In Play"),
    MenuItem(
        "w", "creation_worksheet", "Creation Worksheet", "_open_creation_worksheet"
    ),
    MenuItem("t", "set_date", "Set Date"),
)


#: The sections More offers something in by their id alone.
_MORE_SECTIONS: dict[str, str] = {
    "lab_text_access": "section-hermetic-background",
    "edit_fatigue": "section-char-health",
    "edit_familiar_fatigue": "section-fam-health",
}


#: A tab label's leading number, and a title's trailing count or points.
_TAB_NUMBER = re.compile(r"^\d+ ")
_COUNT = re.compile(r"\s*\([^)]*\)\s*$")


def _plain(markup: str) -> str:
    """`markup` as plain text."""
    return Content.from_markup(markup).plain.strip()


def _short(name: str, width: int = 24) -> str:
    """`name`, cut to fit a footer label."""
    return name if len(name) <= width else name[: width - 1] + "…"


#: What e and d say when no row is chosen (a collapsed section).
CHOOSE_FIRST = "Choose a row first."


#: Widget ids of the workspace's two panes (also used in its DEFAULT_CSS).
NAV_TREE_ID = "nav-tree"


DETAIL_PANE_ID = "detail-pane"


def _tree_node_with_data(tree: Tree, data: tuple) -> TreeNode | None:
    """The first node of `tree` whose `.data` is `data`, or None."""
    pending = [tree.root]
    while pending:
        node = pending.pop()
        if node.data == data:
            return node
        pending.extend(node.children)
    return None


#: The character sheet sections advancing the season can change (STORY-903).
_SEASON_SECTIONS: tuple[str, ...] = (
    "section-char-info",
    "tab-abilities",
    "section-arts",
    "section-casting",
    "section-known-spells",
    "section-char-season",
    "tab-diary",
)


_CHARACTER_VIS_SECTIONS = ("section-raw-vis-hermetic", "section-raw-vis-inventory")

#: The sections a move of raw vis changes on its source's sheet (STORY-412).
_VIS_REFRESH: dict[str, tuple[str, ...]] = {
    vis.CHARACTER: (*_CHARACTER_VIS_SECTIONS, "tab-diary"),
    vis.LABORATORY: ("section-lab-raw-vis", "tab-lab-diary"),
    vis.COVENANT: ("section-pos-vis_store", "tab-cov-diary"),
}


class WorkspaceBase(Screen[None]):
    """The workspace's state and everything its actions share: the navigation
    tree and detail pane, which section is active, saving and refreshing
    (_commit), and the a / e / d plumbing. The per-record actions live in the
    mixins WorkspaceScreen combines."""

    #: One verb per key, everywhere (STORY-1004's rules; see reference/
    #: UI_Conventions.md): a / e / d act on whatever has focus -- the
    #: highlighted row of a list, a section, or the record itself. What only
    #: a few sections can do is in More (m); what can be made is in New (n).
    #: The footer shows the first group at its left and GLOBAL_ACTIONS at
    #: its right.
    BINDINGS: ClassVar[list[BindingType]] = [
        ("a", "add", "Add"),
        ("e", "edit", "Edit"),
        ("d", "delete", "Delete"),
        Binding("delete", "delete", "Delete", show=False),
        ("slash", "filter", "Filter"),
        ("m", "more", "More"),
        ("n", "new", "New"),
        ("t", "advance_season", "Advance Season"),
        ("escape", "step_out", "Back"),
        ("q", "quit", "Quit"),
        # Moving around: not in the footer (the tabs show their numbers).
        Binding("c", "toggle_section", "Collapse", show=False),
        *(
            Binding(str(number), f"show_tab({number})", f"Tab {number}", show=False)
            for number in range(1, 10)
        ),
    ]

    #: The actions shown at the footer's right end: always there, whatever
    #: has focus.
    GLOBAL_ACTIONS: ClassVar[tuple[str, ...]] = (
        "new",
        "advance_season",
        "step_out",
        "quit",
    )

    #: Covenant tabs that own their own a / e / d dispatch (keyed by tab id):
    #: the Diary, a flat pane with no sections. On any other tab, with
    #: nothing focused in a section, the dispatch falls back to the
    #: always-visible info panel. See _active_section().
    _COVENANT_DISPATCH_TABS: ClassVar[set[str]] = {"tab-cov-diary"}

    #: Character tabs that own their own a / e / d dispatch (keyed by tab id),
    #: same idea as _COVENANT_DISPATCH_TABS -- "tab-abilities" and the Diary
    #: are flat panes with no sub-sections, so they dispatch on their own tab
    #: id rather than falling back to the top panel. See _active_section().
    _CHARACTER_DISPATCH_TABS: ClassVar[set[str]] = {"tab-abilities", "tab-diary"}

    #: Familiar tabs that own their own a / e / d dispatch (keyed by tab id),
    #: same idea as _CHARACTER_DISPATCH_TABS -- both are flat panes with no
    #: sub-sections. See _active_section().
    _FAMILIAR_DISPATCH_TABS: ClassVar[set[str]] = {
        "tab-fam-abilities",
        "tab-fam-powers",
    }

    #: Per sheet kind: the tabs that dispatch on their own id, and the
    #: section a tab with no focused section falls back to (None: the tab
    #: itself -- every Laboratory tab dispatches). See _active_section().
    _SHEET_DISPATCH: ClassVar[dict[NodeKind, tuple[set[str], str | None]]] = {
        NodeKind.CHARACTER: (_CHARACTER_DISPATCH_TABS, "section-char-info"),
        NodeKind.LABORATORY: (set(), None),
        NodeKind.COVENANT: (_COVENANT_DISPATCH_TABS, "section-cov-info"),
        NodeKind.FAMILIAR: (_FAMILIAR_DISPATCH_TABS, "section-fam-info"),
    }

    DEFAULT_CSS = """
    #workspace-body {
        height: 1fr;
    }

    #nav-tree {
        width: 34;
        border-right: solid $accent;
    }

    #detail-pane {
        width: 1fr;
        padding: 1 2;
    }
    """

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga
        # Its user-made entries join the shared catalogs (STORY-708).
        catalog.use_saga(saga)
        self.selected_kind: NodeKind = NodeKind.SAGA
        self.selected_covenant: Covenant | None = None
        self.selected_character: Character | None = None
        self.selected_laboratory: Laboratory | None = None
        self.selected_familiar: Familiar | None = None
        self._character_sheet_view: CharacterSheetView | None = None
        self._laboratory_sheet_view: LaboratorySheetView | None = None
        self._covenant_sheet_view: CovenantSheetView | None = None
        self._familiar_sheet_view: FamiliarSheetView | None = None
        #: One detail-pane swap at a time (see _set_detail).
        self._detail_lock = asyncio.Lock()
        #: While the Footer's keys are worked out (active_bindings), what
        #: _in_pass() has computed so far: every binding asks where focus
        #: is, and that answer is the same for all of them.
        self._pass: dict[str, Any] | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="workspace-body"):
            yield Tree(escape(self.saga.name), data=(NodeKind.SAGA,), id=NAV_TREE_ID)
            yield VerticalScroll(id=DETAIL_PANE_ID)
        yield BottomBar(right_actions=self.GLOBAL_ACTIONS)

    def _nav_tree(self) -> Tree:
        return self.query_one(f"#{NAV_TREE_ID}", Tree)

    def _detail_pane(self) -> VerticalScroll:
        return self.query_one(f"#{DETAIL_PANE_ID}", VerticalScroll)

    async def on_mount(self) -> None:
        self._update_saga_clock()
        self._rebuild_tree()
        await self._show_saga_detail()

    def _update_saga_clock(self) -> None:
        """Shows the saga's current date in the Header, on every screen of
        the workspace -- the saga owns the calendar, everything inherits it."""
        saga = self.saga
        self.sub_title = (
            f"{escape(saga.name)} | {saga.current_season} {saga.current_year}"
        )

    def _rebuild_tree(self) -> None:
        tree = self._nav_tree()
        tree.reset(escape(self.saga.name), data=(NodeKind.SAGA,))
        tree.root.expand()

        for covenant in self.saga.covenants:
            cov_node = tree.root.add(
                escape(covenant.name) + _creating(covenant),
                data=(NodeKind.COVENANT, covenant.id),
                expand=True,
            )

            characters = [
                c for c in self.saga.characters if c.covenant_id == covenant.id
            ]
            char_group = cov_node.add(
                f"Characters ({len(characters)})",
                data=(NodeKind.CHARACTER_GROUP, covenant.id),
                expand=True,
            )
            for character in characters:
                self._add_character_node(char_group, character)

            labs = [
                lab for lab in self.saga.laboratories if lab.covenant_id == covenant.id
            ]
            lab_group = cov_node.add(
                f"Laboratories ({len(labs)})",
                data=(NodeKind.LABORATORY_GROUP, covenant.id),
                expand=True,
            )
            for lab in labs:
                lab_group.add_leaf(
                    escape(lab.name) + _creating(lab),
                    data=(NodeKind.LABORATORY, lab.id),
                )

        # Characters and labs with no (or a no-longer-existing) covenant live
        # directly under the saga -- assigning to a covenant is optional, and
        # this is where things land if they're taken out of one.
        covenant_ids = {c.id for c in self.saga.covenants}
        loose_characters = [
            c for c in self.saga.characters if c.covenant_id not in covenant_ids
        ]
        if loose_characters:
            group = tree.root.add(
                f"Unassigned Characters ({len(loose_characters)})",
                data=(NodeKind.CHARACTER_GROUP, None),
                expand=True,
            )
            for character in loose_characters:
                self._add_character_node(group, character)
        loose_labs = [
            lab for lab in self.saga.laboratories if lab.covenant_id not in covenant_ids
        ]
        if loose_labs:
            group = tree.root.add(
                f"Unassigned Laboratories ({len(loose_labs)})",
                data=(NodeKind.LABORATORY_GROUP, None),
                expand=True,
            )
            for lab in loose_labs:
                group.add_leaf(
                    escape(lab.name) + _creating(lab),
                    data=(NodeKind.LABORATORY, lab.id),
                )
        # Books with no owner file under the saga.
        loose_books = bk.unassigned_books(self.saga)
        if loose_books:
            tree.root.add_leaf(
                f"Unassigned Books ({len(loose_books)})", data=(NodeKind.BOOK_GROUP,)
            )
        tree.root.add_leaf(
            f"Seasons ({len(self.saga.season_records)})",
            data=(NodeKind.SEASONS,),
        )
        tree.root.add_leaf(self._spells_label(), data=(NodeKind.SPELLS,))
        tree.root.add_leaf(self._house_rules_label(), data=(NodeKind.HOUSE_RULES,))

    def _add_character_node(self, parent, character: Character) -> None:
        """A character's own tree node: a plain leaf, unless it's a magus
        with a bound Familiar, in which case it becomes an expandable node
        with the Familiar as its one child leaf (nested under its creator,
        never its own group -- see kanban STORY-206)."""
        label = f"{escape(character.name)} ({character.type}){_creating(character)}"
        familiar = (
            fam.familiar_of(self.saga, character.id)
            if character.type == "magus"
            else None
        )
        if familiar is None:
            parent.add_leaf(label, data=(NodeKind.CHARACTER, character.id))
            return
        node = parent.add(label, data=(NodeKind.CHARACTER, character.id), expand=True)
        node.add_leaf(
            f"Familiar: {escape(familiar.name)}", data=(NodeKind.FAMILIAR, familiar.id)
        )

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        data = event.node.data
        if data is None:
            return

        kind: NodeKind = data[0]
        self.selected_kind = kind
        self._character_sheet_view = None
        self._laboratory_sheet_view = None
        self._covenant_sheet_view = None
        self._familiar_sheet_view = None

        if kind == NodeKind.SAGA:
            self.selected_covenant = None
            self.selected_character = None
            self.selected_laboratory = None
            self.selected_familiar = None
            await self._show_saga_detail()
        elif kind == NodeKind.COVENANT:
            covenant = next(c for c in self.saga.covenants if c.id == data[1])
            self.selected_covenant = covenant
            self.selected_character = None
            self.selected_laboratory = None
            self.selected_familiar = None
            await self._show_covenant_detail(covenant)
        elif kind == NodeKind.CHARACTER_GROUP:
            covenant = self.saga.covenant(data[1])
            self.selected_covenant = covenant
            self.selected_character = None
            await self._show_placeholder_detail(
                f"Characters in {covenant.name}"
                if covenant
                else "Unassigned Characters",
                "Select a character from the tree, or press 'n' to add one."
                if covenant
                else "These characters aren't assigned to a covenant. Select one "
                "from the tree, or press 'n' to add one.",
            )
        elif kind == NodeKind.CHARACTER:
            character = next(c for c in self.saga.characters if c.id == data[1])
            self.selected_character = character
            self.selected_covenant = self.saga.covenant(character.covenant_id)
            self.selected_familiar = None
            await self._show_character_detail(character)
        elif kind == NodeKind.FAMILIAR:
            familiar = next(f for f in self.saga.familiars if f.id == data[1])
            self.selected_familiar = familiar
            self.selected_character = self.saga.character(familiar.character_id)
            self.selected_covenant = (
                self.saga.covenant(self.selected_character.covenant_id)
                if self.selected_character is not None
                else None
            )
            await self._show_familiar_detail(familiar)
        elif kind == NodeKind.LABORATORY_GROUP:
            covenant = self.saga.covenant(data[1])
            self.selected_covenant = covenant
            self.selected_laboratory = None
            await self._show_placeholder_detail(
                f"Laboratories in {covenant.name}"
                if covenant
                else "Unassigned Laboratories",
                "Select a laboratory from the tree, or press 'n' to add one."
                if covenant
                else "These laboratories aren't assigned to a covenant. Select "
                "one from the tree, or press 'n' to add one.",
            )
        elif kind == NodeKind.LABORATORY:
            lab = next(lab for lab in self.saga.laboratories if lab.id == data[1])
            self.selected_laboratory = lab
            self.selected_covenant = self.saga.covenant(lab.covenant_id)
            await self._show_laboratory_detail(lab)
        elif kind == NodeKind.SPELLS:
            self.selected_covenant = None
            await self._set_detail(SpellListView(self.saga))
        elif kind == NodeKind.HOUSE_RULES:
            self.selected_covenant = None
            await self._set_detail(HouseRulesView(self.saga))
        elif kind == NodeKind.SEASONS:
            self.selected_covenant = None
            await self._set_detail(SeasonRecordsView(self.saga))
        elif kind == NodeKind.BOOK_GROUP:
            self.selected_covenant = None
            await self._set_detail(
                BookListView(
                    self.saga,
                    lambda: bk.unassigned_books(self.saga),
                    section_id="section-unassigned-books",
                    title="Unassigned Books",
                )
            )

        if self._current_sheet_view() is None:
            # Enter on a node moves into what it shows: a list view's list.
            for rows in self._detail_pane().query(SelectableList):
                rows.focus()
                break
        self.refresh_bindings()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "delete":
            return self._deletes_record() or self._section_op("remove") is not None
        if action == "more":
            return bool(self._more_items())
        if action == "new":
            return bool(self._new_items())
        if action == "filter":
            return self._filter_target() is not None
        if action == "toggle_section":
            return isinstance(section_of(self.app.focused), SheetSection)
        if action == "show_tab":
            number = parameters[0] if parameters else 0
            return isinstance(number, int) and number <= len(self._tab_ids())
        return self._available(action)

    def _available(self, action: str) -> bool:
        """Whether `action` can run where focus is: what enables a/e and
        decides what More and New offer."""
        if (
            action in _CREATE_PLACES
            and self.selected_kind not in _CREATE_PLACES[action]
        ):
            return False
        if action == "edit" and self.selected_kind == NodeKind.SAGA:
            return True
        if action in ("add", "remove", "edit"):
            return self._section_op(action) is not None
        if action == "restore":
            # Offered only while someone has departed (Magi, Companions).
            covenant = self.selected_covenant
            section = self._active_section() or ""
            return (
                self._section_op(action) is not None
                and covenant is not None
                and bool(
                    inh.departed_entries_for_kind(
                        self.saga, covenant, section.removeprefix("section-inh-")
                    )
                )
            )
        if action == "set_date":
            return self.selected_kind == NodeKind.SAGA
        if action in _MORE_SECTIONS:
            return self._active_section() == _MORE_SECTIONS[action]
        if action in ("toggle_mode", "creation_worksheet"):
            view = self._current_sheet_view()
            record = view.creation_record if view is not None else None
            return (
                record is not None
                and self._on_record()
                and (action == "toggle_mode" or record.in_creation)
            )
        if action == "improve":
            return self._active_section() == "section-eco-income"
        if action in ("instill_effect", "use_charge"):
            return (
                self._active_section() in DEVICE_SECTIONS
                and self._device_action_enabled(action)
            )
        if action == "share_spell":
            character = self.selected_character
            return (
                self._active_section() == "section-known-spells"
                and character is not None
                and bool(spl.shareable_spells(character))
            )
        if action == "filter_lab_texts":
            return self._active_section() == LAB_TEXTS_SECTION
        if action == "perform_ritual":
            lab = self.selected_laboratory
            return (
                self._active_section() == LAB_TEXTS_SECTION
                and lab is not None
                and any(
                    lt.kind(b) == TEXT_LONGEVITY
                    for b in lt.texts_of(self.saga, "laboratory", lab.id)
                )
            )
        if action == "move_vis":
            holder = self._vis_holder()
            return (
                holder is not None
                and bool(vis.held(holder))
                and bool(vis.destinations(self.saga, holder))
            )
        if action == "export_record":
            return self._record_to_export() is not None and self._on_record()
        if action == "import_data":
            return (
                self.selected_kind == NodeKind.SAGA
                or self._active_section() in _LIBRARY_SECTIONS
            )
        if action == "create_familiar":
            character = self.selected_character
            if self.selected_kind == NodeKind.CHARACTER and (
                character is None or character.type != "magus"
            ):
                return False
            return bool(fam.unbonded_magi(self.saga))
        if action == "delete_record":
            return self._record_to_delete() is not None
        return True

    # -- focus: one stop per section, the tree, Esc and the tab numbers --

    @property
    def focus_chain(self) -> list[Widget]:
        """Tab and Shift+Tab stop once per section (STORY-1005)."""
        return sheet_focus_chain(super().focus_chain)

    def set_focus(
        self,
        widget: Widget | None,
        scroll_visible: bool = True,
        from_app_focus: bool = False,
    ) -> None:
        # Which section had focus before this call -- a mouse press focuses
        # what it lands on before the click arrives, so a section's title
        # needs this to tell the click that focuses it from the click that
        # collapses it (SheetSection).
        self.section_before_focus = section_of(self.focused)
        if widget is not None and not self._takes_focus(widget):
            # A click on a sheet's button, tab strip or scrolling area:
            # none is a Tab stop, so focus there would strand the keys. A
            # button's section takes it instead; the rest leave it be.
            section = section_of(widget) if isinstance(widget, Button) else None
            if section is None:
                return
            widget = section_stop(section)
        super().set_focus(widget, scroll_visible, from_app_focus)

    def _takes_focus(self, widget: Widget) -> bool:
        """Whether `widget` can hold focus: anything outside the detail
        pane, and inside it a Tab stop or a section's title."""
        if isinstance(widget, CollapsibleTitle) or is_stop(widget):
            return True
        try:
            pane = self._detail_pane()
        except NoMatches:
            return True
        return widget is not pane and pane not in widget.ancestors

    def _tree_focused(self) -> bool:
        focused = self.app.focused
        return focused is not None and focused.id == NAV_TREE_ID

    def _on_record(self) -> bool:
        """Whether focus is on the record itself rather than one of its
        sections: its tree node, or the top panel that names it. There,
        d deletes the record and More offers Export and the like."""
        if self._tree_focused():
            return True
        section = self._active_section()
        return section is not None and section == _RECORD_SECTION.get(
            self.selected_kind
        )

    def action_step_out(self) -> None:
        """Esc: from the sheet back to the tree; from the tree, back to the
        saga picker."""
        focused = self.app.focused
        if focused is not None and self._detail_pane() in focused.ancestors:
            self._nav_tree().focus()
        else:
            self.app.pop_screen()

    def _in_pass(self, key: str, compute: Callable[[], Any]) -> Any:
        """`compute()`, worked out once per Footer pass (see _pass); outside
        a pass, every time."""
        if self._pass is None:
            return compute()
        if key not in self._pass:
            self._pass[key] = compute()
        return self._pass[key]

    def _tab_ids(self) -> list[str]:
        """The ids of the tabs of the sheet on show, in order."""
        view = self._current_sheet_view()
        return [] if view is None else view.tab_ids

    def action_show_tab(self, number: int) -> None:
        """1 to 9: open that tab of the sheet on show and move into it."""
        view = self._current_sheet_view()
        tab_ids = self._tab_ids()
        if view is None or not 1 <= number <= len(tab_ids):
            return
        tabbed = view.query_one(TabbedContent)
        if tabbed.active == tab_ids[number - 1]:
            # Already open: no TabActivated to move focus, so do it here.
            self._focus_first_section()
        else:
            tabbed.active = tab_ids[number - 1]

    def action_toggle_section(self) -> None:
        """c: collapse or expand the focused section."""
        section = section_of(self.app.focused)
        if isinstance(section, SheetSection):
            section.toggle()

    # -- d, More, New and Filter --

    def _deletes_record(self) -> bool:
        return self._on_record() and self._record_to_delete() is not None

    def action_delete(self) -> None:
        if self._deletes_record():
            self.action_delete_record()
        elif (handler := self._section_op("remove")) is not None:
            handler()

    def _more_items(self) -> list[MenuItem]:
        """What More offers where focus is."""
        return self._in_pass(
            "more",
            lambda: [item for item in _MORE_MENU if self._available(item.action)],
        )

    def _new_items(self) -> list[MenuItem]:
        """What New can make from the selected tree node."""
        return self._in_pass(
            "new",
            lambda: [item for item in _NEW_MENU if self._available(item.action)],
        )

    def _run_menu(self, title: str, items: list[MenuItem]) -> None:
        """Run the only item directly; with several, ask which."""
        if not items:
            return
        if len(items) == 1:
            items[0].run(self)
            return
        by_action = {item.action: item for item in items}

        def handle_choice(action: str | None) -> None:
            if action is not None:
                by_action[action].run(self)

        self.app.push_screen(
            MenuScreen(
                title, [(item.letter, item.action, item.label) for item in items]
            ),
            handle_choice,
        )

    def action_more(self) -> None:
        self._run_menu("More", self._more_items())

    def action_new(self) -> None:
        self._run_menu("New", self._new_items())

    def _filter_target(self) -> str | None:
        """What / filters here: the Lab Texts list or the Spells list."""
        if self._active_section() == LAB_TEXTS_SECTION:
            return "lab_texts"
        if self.selected_kind == NodeKind.SPELLS:
            return "spells"
        return None

    def action_filter(self) -> None:
        target = self._filter_target()
        if target == "lab_texts":
            self.action_filter_lab_texts()
        elif target == "spells":
            try:
                self.query_one("#spell-search").focus()
            except NoMatches:
                pass

    def action_filter_lab_texts(self) -> None:
        raise NotImplementedError

    def action_toggle_mode(self) -> None:
        self._toggle_creation_mode()

    def _key_labels(self) -> dict[str, str]:
        """Footer labels that depend on where focus is: what d deletes, and
        a menu key that has only one thing to do says what."""
        labels: dict[str, str] = {}
        if self.selected_kind == NodeKind.SAGA:
            labels["edit"] = "Edit Saga"
        if self._deletes_record():
            record = self._record_to_delete()
            if record is not None:
                labels["delete"] = f"Delete {escape(_short(record.name))}"
        more = self._more_items()
        if len(more) == 1:
            labels["more"] = more[0].label
        new = self._new_items()
        if len(new) == 1:
            labels["new"] = new[0].label
        return labels

    @property
    def active_bindings(self) -> dict[str, ActiveBinding]:
        """The screen's bindings, labelled for where focus is (see
        _key_labels)."""
        self._pass = {}
        try:
            bindings = super().active_bindings
            labels = self._key_labels()
        finally:
            self._pass = None
        if not labels:
            return bindings
        return {
            key: active._replace(
                binding=replace(
                    active.binding, description=labels[active.binding.action]
                )
            )
            if active.binding.action in labels
            else active
            for key, active in bindings.items()
        }

    def _record_to_export(self) -> transfer.Record | None:
        """The covenant, laboratory or character whose node is selected
        (STORY-109): what More's Export exports."""
        if self.selected_kind == NodeKind.CHARACTER:
            return self.selected_character
        if self.selected_kind == NodeKind.LABORATORY:
            return self.selected_laboratory
        if self.selected_kind == NodeKind.COVENANT:
            return self.selected_covenant
        return None

    def action_export_record(self) -> None:
        """More's Export on a covenant, laboratory or character: write it to a file
        that another saga can import (STORY-109)."""
        record = self._record_to_export()
        if record is None:
            return

        def handle_result(result: tuple[Path, bool] | None) -> None:
            if result is None:
                return
            path, with_members = result
            try:
                transfer.export_to(path, self.saga, record, with_members=with_members)
            except OSError as problem:
                self.notify(
                    f"Couldn't write {escape(path.name)}: {escape(str(problem))}",
                    severity="error",
                )
                return
            self.notify(f"Exported {escape(record.name)} to {escape(str(path))}.")

        self.app.push_screen(_export_dialog(record, storage.EXPORTS_DIR), handle_result)

    def _vis_holder(self) -> vis.Holder | None:
        """Whose raw vis the active section lists (STORY-412): the
        character's or the laboratory's pool, or the covenant's Raw Vis
        Stores. None anywhere else."""
        section = self._active_section()
        if section in _CHARACTER_VIS_SECTIONS:
            return self.selected_character
        if section == "section-lab-raw-vis":
            return self.selected_laboratory
        if section == "section-pos-vis_store":
            return self.selected_covenant
        return None

    def action_move_vis(self) -> None:
        """Move raw vis from the sheet on show to another covenant,
        laboratory or magus (STORY-412): the chosen row's, else the one
        picked. Both sides' Diaries record it."""
        holder = self._vis_holder()
        section = self._active_section()
        if holder is None or section is None:
            return
        held = vis.held(holder)
        selected: int | None = None
        if isinstance(holder, Covenant):
            if self._covenant_sheet_view is not None:
                selected = self._covenant_sheet_view.selected_possession("vis_store")
        elif isinstance(holder, Character):
            if self._character_sheet_view is not None:
                selected = self._character_sheet_view.selected_raw_vis(section)
        elif self._laboratory_sheet_view is not None:
            selected = self._laboratory_sheet_view.selected_raw_vis()
        if selected is not None and selected >= len(held):
            selected = None
        if selected is None and len(held) == 1:
            selected = 0  # only one thing to move: no need to ask which

        self._chosen_or_pick(
            selected,
            [escape(h.label) for h in held],
            empty="No Raw Vis to move.",
            then=lambda index: self._move_vis_form(holder, held[index]),
        )

    def _move_vis_form(self, holder: vis.Holder, what: vis.Held) -> None:
        """Ask how many of `what`'s pawns leave `holder` and who gets them,
        then move them."""
        destinations = vis.destinations(self.saga, holder)
        if not destinations:
            self.notify("Nowhere else in the saga to move raw vis to.")
            return

        def handle_result(result: tuple[int, str] | None) -> None:
            if result is None:
                return
            pawns, value = result
            destination = vis.parse_destination(self.saga, value)
            if destination is None:
                return
            vis.move(self.saga, holder, what, pawns, destination)
            self._commit(*_VIS_REFRESH[vis.kind_of(holder)])
            self.refresh_bindings()
            self.notify(
                f"Moved {pawns} pawn(s) of {what.art} vis to "
                f"{escape(destination.name)}."
            )

        self.app.push_screen(
            _move_vis_dialog(holder.name, what, destinations), handle_result
        )

    def _active_section(self) -> str | None:
        return self._in_pass("section", self._find_active_section)

    def _find_active_section(self) -> str | None:
        """Which sheet section is "active" for a / e / d and More: the
        nearest Collapsible around whatever has focus -- which also covers a
        sheet's top panel, outside its tabs. With none, a flat tab that
        dispatches on its own id (see _SHEET_DISPATCH), otherwise the sheet's
        always-visible top section, so 'e' edits the record from any tab.
        The Unassigned Books and Spells nodes have no sheet, just a section."""
        if self.selected_kind == NodeKind.BOOK_GROUP:
            return "section-unassigned-books"
        if self.selected_kind == NodeKind.SPELLS:
            return SPELL_SECTION
        if self.selected_kind == NodeKind.HOUSE_RULES:
            return HOUSE_RULES_SECTION
        view = self._current_sheet_view()
        if view is None:
            return None
        try:
            tab_id = view.query_one(TabbedContent).active
        except NoMatches:
            return None
        if not tab_id:
            return None

        focused = self.app.focused
        if focused is not None:
            for widget in focused.ancestors_with_self:
                if isinstance(widget, Collapsible) and widget.id:
                    return widget.id
        own_tabs, fallback = self._SHEET_DISPATCH[self.selected_kind]
        return tab_id if fallback is None or tab_id in own_tabs else fallback

    def on_tabbed_content_tab_activated(
        self, event: TabbedContent.TabActivated
    ) -> None:
        # Keep the Footer's binding hints (and check_action gating) in sync
        # with whichever tab the user just switched to, and give the new
        # tab's first section focus so a / e / d work immediately without
        # requiring an explicit Tab-key navigation first.
        view = self._current_sheet_view()
        initial = False
        if view is not None:
            # TabbedContent announces its initial tab once, right after
            # mounting. That's not a user tab switch, and treating it as one
            # would clear the focus _show_*_detail() just set.
            initial = not view.initial_tab_seen
            view.initial_tab_seen = True
        self._focus_first_section(initial=initial)
        self.refresh_bindings()

    def _focus_first_section(self, *, initial: bool = False) -> None:
        """Give the sheet a focused section, so a / e / d work straight away.

        When a sheet is first shown (`initial`), focus its first section
        anywhere -- the always-visible top panel. On a later tab switch, focus
        the tab's first stop (see widgets.first_stop): its first section, or
        a flat tab's list. A tab with nothing to focus clears focus: the top
        panel lives outside the tabs, so a tab switch never blurs it, and
        leaving it focused would make _active_section() keep reporting it.

        The Laboratory is the exception on first showing: its default tab
        (Planning) is flat, so it looks at the active tab first -- its
        seasons list, so e plans lab work straight away (STORY-901) -- and
        only then falls back to the top panel."""
        view = self._current_sheet_view()
        if view is None:
            return
        stop: Widget | None = None
        if not initial or self.selected_kind == NodeKind.LABORATORY:
            try:
                tabbed = view.query_one(TabbedContent)
                if not tabbed.active:
                    return
                stop = first_stop(view.query_one(f"#{tabbed.active}", TabPane))
            except NoMatches:
                stop = None
            if stop is None and not initial:
                self.screen.set_focus(None)
                return
        if stop is None:
            try:
                stop = section_stop(view.query(Collapsible).first())
            except NoMatches:
                return
        stop.focus()

    def on_descendant_focus(self, event: DescendantFocus) -> None:
        # Focus can move between Collapsible sections within the same tab
        # (no TabActivated message for that) -- keep bindings in sync then
        # too, or the Footer hint and check_action gating go stale.
        self.refresh_bindings()
        self._update_where()

    def on_selectable_list_moved(self, event: SelectableList.Moved) -> None:
        event.stop()
        self._update_where()

    def _shown_name(self) -> str:
        """What the selected tree node shows: the record's name, or what
        the node lists."""
        covenant = self.selected_covenant
        record = {
            NodeKind.SAGA: self.saga,
            NodeKind.COVENANT: covenant,
            NodeKind.CHARACTER: self.selected_character,
            NodeKind.LABORATORY: self.selected_laboratory,
            NodeKind.FAMILIAR: self.selected_familiar,
        }.get(self.selected_kind)
        if record is not None:
            return record.name
        where = f" in {covenant.name}" if covenant is not None else ""
        return {
            NodeKind.CHARACTER_GROUP: f"Characters{where}",
            NodeKind.LABORATORY_GROUP: f"Laboratories{where}",
            NodeKind.SPELLS: "Spells",
            NodeKind.HOUSE_RULES: "House Rules",
            NodeKind.SEASONS: "Seasons",
            NodeKind.BOOK_GROUP: "Unassigned Books",
        }.get(self.selected_kind, "")

    def _update_where(self) -> None:
        """Say where focus is in the row above the footer (STORY-1008):
        the tree node on show, then the tab, section and chosen row."""
        try:
            bar = self.query_one(BottomBar)
        except NoMatches:
            return
        parts = [self._shown_name()]
        focused = self.app.focused
        if focused is not None and not self._tree_focused():
            view = self._current_sheet_view()
            section = section_of(focused)
            if view is not None:
                tabbed = view.query_one(TabbedContent)
                # The top panel belongs to no tab.
                if tabbed.active and tabbed in focused.ancestors:
                    label = str(tabbed.get_tab(tabbed.active).label)
                    parts.append(_TAB_NUMBER.sub("", label))
                if section is not None and section.id != _RECORD_SECTION.get(
                    self.selected_kind
                ):
                    parts.append(_COUNT.sub("", _plain(section.title)))
            if isinstance(focused, SelectableList) and focused.chosen_text:
                parts.append(focused.chosen_text)
        bar.set_where("  ›  ".join(escape(part) for part in parts if part))

    def on_descendant_blur(self, event: DescendantBlur) -> None:
        self.refresh_bindings()

    async def _set_detail(self, *widgets: Widget) -> None:
        detail_pane = self._detail_pane()
        # One swap at a time: two in flight at once interleave their removes
        # and mounts, leaving both sheets mounted or removing one mid-mount.
        async with self._detail_lock:
            # Must be awaited before mounting replacements below, or a same-id
            # widget not yet removed collides with its freshly-mounted
            # replacement and Textual raises DuplicateIds.
            await detail_pane.remove_children()
            await detail_pane.mount(*widgets)

    async def _show_placeholder_detail(self, title: str, hint: str) -> None:
        await self._set_detail(Static(f"{title}\n\n{hint}"))

    async def _show_saga_detail(self) -> None:
        saga = self.saga
        lines = [
            f"Saga: {escape(saga.name)}",
            f"Storyguide: {escape(saga.storyguide)}",
            f"Current date: {saga.current_season} {saga.current_year}",
        ]
        if saga.description:
            lines.append(f"Description: {escape(saga.description)}")
        lines.append(f"Books in play: {sourcebooks.summary(saga.books_in_play)}")
        lines.append(f"Optional rules: {rule_options.summary(saga)}")
        lines += [
            "",
            f"Covenants: {len(saga.covenants)}",
            f"Characters: {len(saga.characters)}",
            f"Laboratories: {len(saga.laboratories)}",
            f"Books: {len(saga.books)}",
            f"Spells: {len(saga.spells)}",
        ]
        await self._set_detail(Static("\n".join(lines)))

    async def _show_covenant_detail(self, covenant: Covenant) -> None:
        view = CovenantSheetView(self.saga, covenant)
        await self._set_detail(view)
        self._covenant_sheet_view = view
        self._focus_first_section(initial=True)

    async def _show_laboratory_detail(self, lab: Laboratory) -> None:
        view = LaboratorySheetView(self.saga, lab)
        await self._set_detail(view)
        self._laboratory_sheet_view = view
        self._focus_first_section(initial=True)

    async def _show_character_detail(self, character: Character) -> None:
        view = CharacterSheetView(self.saga, character)
        await self._set_detail(view)
        self._character_sheet_view = view
        self._focus_first_section(initial=True)

    async def _show_familiar_detail(self, familiar: Familiar) -> None:
        view = FamiliarSheetView(self.saga, familiar)
        await self._set_detail(view)
        self._familiar_sheet_view = view
        self._focus_first_section(initial=True)

    def _current_sheet_view(self) -> SheetView | None:
        """The sheet on show for the selected tree node, if it has one."""
        return {
            NodeKind.CHARACTER: self._character_sheet_view,
            NodeKind.LABORATORY: self._laboratory_sheet_view,
            NodeKind.COVENANT: self._covenant_sheet_view,
            NodeKind.FAMILIAR: self._familiar_sheet_view,
        }.get(self.selected_kind)

    # -- scored-trait lists (Personality Traits, Reputations) --

    def _traits(self, spec: _TraitList) -> list[ScoredTrait] | None:
        owner = getattr(self, spec.owner)
        return None if owner is None else getattr(owner, spec.attr)

    def _trait_prompt(
        self, spec: _TraitList, title: str, existing: ScoredTrait | None = None
    ) -> FieldsDialog[ScoredTrait]:
        return _scored_trait_dialog(
            title, spec.example, existing, **spec.prompt_options
        )

    def _add_trait(self, spec: _TraitList) -> None:
        traits = self._traits(spec)
        if traits is None:
            return

        def handle_result(trait: ScoredTrait | None) -> None:
            if trait is not None:
                traits.append(trait)
                self._commit(spec.section)

        self.app.push_screen(
            self._trait_prompt(spec, f"Add a {spec.noun}"), handle_result
        )

    def _edit_trait(self, spec: _TraitList) -> None:
        """Edit the chosen entry."""
        traits = self._traits(spec)
        if traits is None:
            return
        self._chosen_or_pick(
            getattr(self, spec.selected)(),
            [label for _, label in st.trait_rows(traits)],
            empty=f"No {spec.noun}s to edit.",
            then=lambda index: self._edit_trait_at(spec, traits, index),
        )

    def _edit_trait_at(
        self, spec: _TraitList, traits: list[ScoredTrait], index: int
    ) -> None:
        def handle_result(trait: ScoredTrait | None) -> None:
            if trait is not None:
                traits[index] = trait
                self._commit(spec.section)

        self.app.push_screen(
            self._trait_prompt(spec, f"Edit a {spec.noun}", traits[index]),
            handle_result,
        )

    def _remove_trait(self, spec: _TraitList) -> None:
        """Delete the chosen entry, after confirming."""
        traits = self._traits(spec)
        if traits is None:
            return

        def remove(index: int) -> None:
            self._confirm_delete(traits, index, traits[index].name, spec.section)

        self._chosen_or_pick(
            getattr(self, spec.selected)(),
            [label for _, label in st.trait_rows(traits)],
            empty=f"No {spec.noun}s to remove.",
            then=remove,
        )

    def _chosen_or_pick(
        self,
        selected: int | None,
        labels: Sequence[str],
        *,
        empty: str,
        then: Callable[[int], object],
    ) -> None:
        """Act on a list entry by index: the chosen row's (`selected`). A
        focused list always has one (STORY-1005); with none (the section is
        collapsed), act on the only entry there is, else say to choose a
        row -- or, with no entries at all, just say `empty`. Nothing asks
        "which one?" any more (the name is from when a picker did)."""
        if selected is not None and selected < len(labels):
            then(selected)
        elif not labels:
            self.notify(empty)
        elif len(labels) == 1:
            then(0)  # only one: no need to choose it
        else:
            self.notify(CHOOSE_FIRST)

    def _confirm_delete(
        self, entries: list[Any], index: int, name: str, section: str
    ) -> None:
        """Ask "Delete <name>?" (No by default); on Yes, delete
        `entries[index]`, save and refresh `section`."""

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del entries[index]
                self._commit(section)

        self.app.push_screen(ConfirmScreen(f"Delete {escape(name)}?"), handle_confirmed)

    def _toggle_creation_mode(self) -> None:
        """The top panel's In Creation / In Play switch (STORY-1301): asks
        first either way. With strict creation rules on, a record that
        breaks a rule it must follow stays In Creation."""
        view = self._current_sheet_view()
        record = view.creation_record if view is not None else None
        if record is None:
            return
        name = escape(record.name)
        if record.in_creation:
            if not creation_rules.can_move_to_play(self.saga, record):
                broken = creation_rules.broken_musts(
                    creation_rules.checks(self.saga, record)
                )
                self.notify(
                    f"{name} stays In Creation: it breaks {len(broken)} "
                    "creation rule(s) it must follow, and this saga enforces "
                    "them strictly.",
                    severity="warning",
                )
                return
            found = creation_rules.checks(self.saga, record)
            message = (
                f"Move {name} to In Play? Creation checks: "
                f"{creation_rules.summary(found)}. They stop once it is In Play."
            )
        else:
            message = (
                f"Move {name} back to In Creation? The creation checks come "
                "back until it moves to In Play again."
            )

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                creation.set_in_creation(self.saga, record, not record.in_creation)
                self._commit("section-creation", tree=True)

        self.app.push_screen(ConfirmScreen(message), handle_confirmed)

    def _commit(self, *sections: str, tree: bool = False) -> None:
        """Save a change: write the saga, rebuild the navigation tree if a
        name or the structure changed (`tree`), and refresh `sections` of the
        sheet on show -- the one whose handler made the change."""
        storage.save_saga(self.saga)
        if tree:
            self._rebuild_tree()
        view = self._current_sheet_view()
        if view is not None:
            for section in sections:
                view.refresh_section(section)
        # An open Creation Worksheet shows the record too (STORY-1302).
        for screen in self.app.screen_stack:
            changed = getattr(screen, "record_changed", None)
            if callable(changed):
                changed()

    def _refresh_character_section(self, section_id: str) -> None:
        if self._character_sheet_view is not None:
            self._character_sheet_view.refresh_section(section_id)

    def _refresh_covenant_section(self, section_id: str) -> None:
        if self._covenant_sheet_view is not None:
            self._covenant_sheet_view.refresh_section(section_id)

    def _refresh_familiar_section(self, section_id: str) -> None:
        if self._familiar_sheet_view is not None:
            self._familiar_sheet_view.refresh_section(section_id)

    def _refresh_laboratory_section(self, section_id: str) -> None:
        if self._laboratory_sheet_view is not None:
            self._laboratory_sheet_view.refresh_section(section_id)

    # -- creation actions --

    def action_create_covenant(self) -> None:
        async def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                covenant = creation.add_covenant(
                    self.saga, values["name"], values["notes"]
                )
                storage.save_saga(self.saga)
                self._rebuild_tree()
                self.selected_covenant = covenant
                self.selected_kind = NodeKind.COVENANT
                await self._show_covenant_detail(covenant)

        self.app.push_screen(
            FieldsDialog(
                "Create a New Covenant", _covenant_create_fields(), save_label="Create"
            ),
            handle_result,
        )

    def action_create_character(self) -> None:
        covenant = self.selected_covenant

        async def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                character = creation.add_character(
                    self.saga, values["name"], values["type"], values["covenant_id"]
                )
                storage.save_saga(self.saga)
                self._rebuild_tree()
                self.selected_character = character
                self.selected_kind = NodeKind.CHARACTER
                await self._show_character_detail(character)

        self.app.push_screen(
            FieldsDialog(
                "Create a New Character",
                _character_create_fields(self.saga, covenant.id if covenant else None),
                save_label="Create",
            ),
            handle_result,
        )

    def action_create_laboratory(self) -> None:
        covenant = self.selected_covenant

        async def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                lab = creation.add_laboratory(
                    self.saga,
                    values["name"],
                    values["size"],
                    values["covenant_id"],
                    starting=values.get("starting", False),
                )
                storage.save_saga(self.saga)
                self._rebuild_tree()
                self.selected_laboratory = lab
                self.selected_kind = NodeKind.LABORATORY
                await self._show_laboratory_detail(lab)

        self.app.push_screen(
            FieldsDialog(
                "Create a New Laboratory",
                _laboratory_create_fields(self.saga, covenant.id if covenant else None),
                save_label="Create",
            ),
            handle_result,
        )

    def action_create_familiar(self) -> None:
        if not fam.unbonded_magi(self.saga):
            self.notify("Every magus already has a bound Familiar.")
            return
        # The magus on show is the default. (selected_character outlives it:
        # a laboratory or Spells shown afterwards leaves it set.)
        character = self.selected_character
        default_magus_id = (
            character.id
            if character is not None
            and self.selected_kind == NodeKind.CHARACTER
            and character.type == "magus"
            and fam.familiar_of(self.saga, character.id) is None
            else None
        )

        async def handle_result(values: dict[str, Any] | None) -> None:
            magus = (
                None if values is None else self.saga.character(values["character_id"])
            )
            if values is not None and magus is not None:
                familiar = fam.bind_familiar(self.saga, magus, values["name"])
                storage.save_saga(self.saga)
                self._rebuild_tree()
                self.selected_familiar = familiar
                self.selected_character = self.saga.character(familiar.character_id)
                self.selected_kind = NodeKind.FAMILIAR
                await self._show_familiar_detail(familiar)

        self.app.push_screen(
            FieldsDialog(
                "Bind a New Familiar",
                _familiar_create_fields(self.saga, default_magus_id),
                save_label="Create",
            ),
            handle_result,
        )

    # -- deleting a covenant, character or laboratory --

    def _record_to_delete(self) -> Covenant | Character | Laboratory | None:
        """The record d deletes: the covenant, character or laboratory
        selected in the tree, if that's what's selected."""
        return {
            NodeKind.COVENANT: self.selected_covenant,
            NodeKind.CHARACTER: self.selected_character,
            NodeKind.LABORATORY: self.selected_laboratory,
        }.get(self.selected_kind)

    def action_delete_record(self) -> None:
        """Delete the selected covenant, character or laboratory, after a
        confirmation that says what happens to what it owns (see deletion)."""
        record = self._record_to_delete()
        if record is None:
            return
        saga = self.saga
        if isinstance(record, Covenant):
            consequences = deletion.covenant_consequences(saga, record)
            delete: Callable[[], None] = partial(deletion.delete_covenant, saga, record)
        elif isinstance(record, Character):
            consequences = deletion.character_consequences(saga, record)
            delete = partial(deletion.delete_character, saga, record)
        else:
            consequences = deletion.laboratory_consequences(saga, record)
            delete = partial(deletion.delete_laboratory, saga, record)
        message = f"Delete {escape(record.name)}?"
        if consequences:
            message += "\n\n" + "\n".join(map(escape, consequences))

        async def handle_confirmed(confirmed: bool | None) -> None:
            if not confirmed:
                return
            delete()
            storage.save_saga(saga)
            self._rebuild_tree()
            await self._show_saga_root()

        self.app.push_screen(ConfirmScreen(message), handle_confirmed)

    async def _show_saga_root(self) -> None:
        """Select the saga itself, in the tree and the detail pane."""
        self.selected_kind = NodeKind.SAGA
        self.selected_covenant = None
        self.selected_character = None
        self.selected_laboratory = None
        self.selected_familiar = None
        self._character_sheet_view = None
        self._laboratory_sheet_view = None
        self._covenant_sheet_view = None
        self._familiar_sheet_view = None
        tree = self._nav_tree()
        tree.move_cursor(tree.root)
        await self._show_saga_detail()
        self.refresh_bindings()

    def _section_op(self, name: str) -> Callable[[], None] | None:
        """The active section's handler for `name` ("add", "remove", "edit"
        or "restore"), if it has one."""
        ops = self._section_ops.get(self._active_section() or "")
        return None if ops is None else getattr(ops, name)

    def action_add(self) -> None:
        if (handler := self._section_op("add")) is not None:
            handler()

    def action_remove(self) -> None:
        if (handler := self._section_op("remove")) is not None:
            handler()

    def action_edit(self) -> None:
        if self.selected_kind == NodeKind.SAGA:
            self._edit_saga()
        elif (handler := self._section_op("edit")) is not None:
            handler()

    def action_restore(self) -> None:
        if (handler := self._section_op("restore")) is not None:
            handler()

    # -- navigation tree labels --

    def _spells_label(self) -> str:
        return f"Spells ({len(spl.all_spells(self.saga))})"

    def _house_rules_label(self) -> str:
        return f"House Rules ({len(hr.all_entries(self.saga))})"

    # -- Saga --

    def _edit_saga(self) -> None:
        async def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            self.saga.rule_options = saga_rule_options(result)
            for field, value in result.items():
                setattr(self.saga, field, value)
            self.saga.books_in_play = sourcebooks.normalized(self.saga.books_in_play)
            self._commit(tree=True)
            self._update_saga_clock()
            await self._show_saga_detail()

        self.app.push_screen(
            FieldsDialog("Edit Saga", _saga_fields(self.saga)), handle_result
        )

    # -- Saga time --

    async def _apply_saga_date(self, season: str, year: int) -> None:
        """Single path for every change to the saga's calendar: store it, then
        refresh everything that inherits it (Header, covenant panel, saga
        summary)."""
        saga = self.saga
        saga.current_season, saga.current_year = season, year
        storage.save_saga(saga)
        self._update_saga_clock()
        self._refresh_covenant_section("section-cov-info")
        if self.selected_kind == NodeKind.SAGA:
            await self._show_saga_detail()

    def action_advance_season(self) -> None:
        saga = self.saga

        async def handle_result(confirmed: bool | None) -> None:
            if not confirmed:
                return
            if saga.current_season == SEASONS[-1]:
                in_deficit = eco.covenants_in_deficit(saga)
                if in_deficit:
                    self._offer_to_resolve_deficit(in_deficit, advance)
                    return
            await advance()

        async def advance() -> None:
            # Contested resources whose security lapsed: was each secured
            # this season (STORY-906)? Asked one by one, then the season
            # is played out.
            lapsed = seasons.lapsed_resources(saga)
            answers: dict[str, bool] = {}

            async def ask(index: int) -> None:
                if index >= len(lapsed):
                    await play_out(answers)
                    return
                resource_id, label = lapsed[index]

                async def answered(yes: bool | None) -> None:
                    answers[resource_id] = bool(yes)
                    await ask(index + 1)

                self.app.push_screen(
                    ConfirmScreen(
                        f"Was {escape(label)} secured this season? (A contested "
                        "resource: yes secures it for five years; no loses its "
                        "harvest or income.)"
                    ),
                    answered,
                )

            await ask(0)

        async def play_out(answers: dict[str, bool]) -> None:
            # Every plan's outcome is worked out before any is applied, so a
            # season's results can't change that same season (STORY-903).
            worked = seasons.resolve(saga, random.Random())
            # An experiment seeking a Discovery whose roll the risk can move
            # onto 10: asked each time (Hedda 2026-09-30).
            moves = seasons.discovery_moves(saga, worked)

            async def ask_move(index: int) -> None:
                if index >= len(moves):
                    await finish(answers, worked)
                    return
                outcome, text = moves[index]

                async def answered(yes: bool | None) -> None:
                    seasons.take_discovery_move(saga, outcome, bool(yes))
                    await ask_move(index + 1)

                self.app.push_screen(ConfirmScreen(escape(text)), answered)

            await ask_move(0)

        async def finish(answers: dict[str, bool], worked: list[Any]) -> None:
            new_year = saga.current_season == SEASONS[-1]
            record = seasons.make_record(saga, worked)
            if worked:
                storage.backup_saga(saga)
            applied = seasons.apply(saga, worked)
            # Winter ends the year: the aging rolls (STORY-904).
            aged = (
                seasons.year_end_grogs(saga)
                + seasons.year_end_business(saga)
                + seasons.year_end_aging(saga, random.Random())
                if new_year
                else []
            )
            record.lines += aged
            harvest = seasons.covenant_season(saga, answers)
            record.lines += harvest
            aged += harvest
            if saga.keep_season_records and (worked or aged):
                saga.season_records.append(record)
            # A new year (Winter -> Spring): each covenant's surplus goes into
            # its Wealth before the date moves on.
            added = eco.close_all_years(saga) if new_year else []
            await self._apply_saga_date(
                *next_season(saga.current_season, saga.current_year)
            )
            # Applied seasons change xp (scores, casting and lab totals) and
            # the Diary; the new date changes This Season.
            for section in _SEASON_SECTIONS:
                self._refresh_character_section(section)
            self._refresh_laboratory_section("tab-lab-planning")
            self._refresh_covenant_section("tab-cov-seasons")
            if saga.keep_season_records and worked:
                self._rebuild_tree()
            if worked or aged:
                self.app.push_screen(SeasonSummaryScreen(saga, record))
            message = f"It is now {saga.current_season} {saga.current_year}."
            if applied:
                message += (
                    f" Seasons applied for {', '.join(c.name for c in applied)}"
                    " (see each one's Diary)."
                )
            if added:
                message += " Added to Wealth: " + ", ".join(
                    f"{name} {amount}" for name, amount in added
                )
                message += "."
                self._refresh_covenant_section("section-eco-wealth")
            self.notify(escape(message))

        self.app.push_screen(
            AdvanceSeasonScreen(
                saga.current_season,
                saga.current_year,
                seasons.advance_summary(saga),
            ),
            handle_result,
        )

    def _offer_to_resolve_deficit(
        self, in_deficit: list[tuple[str, int]], advance: Callable[[], Any]
    ) -> None:
        """Before the year rolls over with a covenant in deficit: Yes (the
        focused, Escape answer) leaves the date alone so the books can be
        balanced; No advances anyway."""
        lines = "\n".join(
            f"  {escape(name)}: {deficit}" for name, deficit in in_deficit
        )

        async def handle_answer(resolve: bool | None) -> None:
            if resolve:
                self.notify(
                    "The year hasn't advanced. Balance the books, then press t again."
                )
                return
            await advance()

        self.app.push_screen(
            ConfirmScreen(
                "The Covenant is currently in a deficit - do you wish to attempt "
                f"to resolve this?\n\n{lines}",
                yes_variant="primary",
                safe_answer=True,
            ),
            handle_answer,
        )

    # -- season plans (shared by the character and covenant sheets) --

    def _plan_season_for(self, character: Character, section: str) -> None:
        """Plan `character`'s current season, or change the plan, then
        refresh `section`."""
        if not season_rules.is_planned(character):
            self._grog_year_for(character, section)
            return

        def handle_result(plan: SeasonPlan | None) -> None:
            if plan is not None:
                seasons.set_plan(self.saga, plan)
                self._commit(section)

        self.app.push_screen(
            _season_plan_dialog(
                self.saga, character, seasons.plan_for(self.saga, character)
            ),
            handle_result,
        )

    def _grog_year_for(self, character: Character, section: str) -> None:
        """Set up a grog's yearly update (STORY-924)."""

        def handle_result(year: GrogYear | None) -> None:
            if year is not None:
                character.grog_year = year
                self._commit(section)

        self.app.push_screen(
            _grog_year_dialog(character, character.grog_year), handle_result
        )

    def _clear_season_plan_for(self, character: Character, section: str) -> None:
        """Drop `character`'s plan for the current season (after
        confirming), then refresh `section`."""
        plan = seasons.plan_for(self.saga, character)
        if plan is None:
            self.notify(f"Nothing is planned for {character.name} this season.")
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and seasons.clear_plan(self.saga, character):
                self._commit(section)

        self.app.push_screen(
            ConfirmScreen(
                f"Clear {escape(character.name)}'s plan "
                f"({escape(seasons.plan_summary(self.saga, character, plan))})?"
            ),
            handle_confirmed,
        )

    def action_set_date(self) -> None:
        saga = self.saga

        async def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            season, year = result["season"], result["year"]
            if (season, year) == (saga.current_season, saga.current_year):
                return
            await self._apply_saga_date(season, year)
            self.notify(f"Date set to {season} {year}.")

        self.app.push_screen(
            FieldsDialog(
                "Set the Saga's Date",
                _date_fields(saga.current_season, saga.current_year),
                save_label="Set",
            ),
            handle_result,
        )

    @staticmethod
    def _ability_label(a: Ability) -> str:
        specialty = f" ({escape(a.specialty)})" if a.specialty else ""
        return f"{escape(a.name)}{specialty} {st.score_text(a.progress)}"

    # -- shared Character/Laboratory/Familiar Virtue & Flaw actions --

    def action_add_virtue_flaw(self) -> None:
        target = self._virtue_flaw_target()
        if target is None:
            return
        # Opened on the side of the section it was launched from.
        flaws = self._active_section() in ("section-vf-flaws", "section-fam-vf-flaws")
        self._add_virtue_flaw_to(target, "Flaw" if flaws else "Virtue")

    def _add_virtue_flaw_to(
        self, target: Character | Laboratory | Familiar, side: str = "Virtue"
    ) -> None:
        """Pick a Virtue or Flaw (opened on `side`) and add it to `target`
        (also the Creation Worksheet's Virtues and Flaws step)."""
        is_lab = isinstance(target, Laboratory)
        is_familiar = isinstance(target, Familiar)

        def handle_result(instance: VirtueFlawInstance | None) -> None:
            if instance is not None:
                target.virtues_flaws.append(instance)
                if isinstance(target, Laboratory):
                    # A Feature waiting for a Virtue gets a new Feature Virtue.
                    instance.id = new_instance_id()
                    link_unlinked_features(target)
                storage.save_saga(self.saga)
                if is_lab:
                    for section in LAB_FEATURE_SECTIONS:
                        self._refresh_laboratory_section(section)
                elif is_familiar:
                    self._refresh_familiar_section("section-fam-vf-virtues")
                else:
                    self._refresh_character_section("section-vf-virtues")

        books = sourcebooks.saga_books(self.saga)
        if isinstance(target, Laboratory):
            existing_ids = {vf.vf_id for vf in target.virtues_flaws}
            self.app.push_screen(
                LabVirtueFlawPickerScreen(existing_ids, books=books), handle_result
            )
            return
        chooser = (
            catalog.VirtueFlawChooser.for_familiar(target, books)
            if isinstance(target, Familiar)
            else catalog.VirtueFlawChooser.for_character(target, books)
        )
        self.app.push_screen(
            VirtueFlawPickerScreen(
                target.virtues_flaws,
                side=side,
                chooser=chooser,
                own_abilities=[a.name for a in target.abilities],
            ),
            handle_result,
        )

    def action_remove_virtue_flaw(self) -> None:
        """Delete a Virtue/Flaw of the character, laboratory or familiar on
        show, after confirming: the row chosen in its Virtues or Flaws
        list."""
        target = self._virtue_flaw_target()
        if target is None:
            return
        self._remove_virtue_flaw_from(target, self._selected_virtue_flaw(target))

    def _remove_virtue_flaw_from(
        self, target: Character | Laboratory | Familiar, selected: int | None = None
    ) -> None:
        """Delete `target`'s Virtue/Flaw at `selected` after confirming."""
        if not target.virtues_flaws:
            self.notify("No Virtues/Flaws to remove.")
            return
        vf_catalog = (
            catalog.load_lab_virtue_flaw_catalog_by_id()
            if isinstance(target, Laboratory)
            else catalog.load_virtue_flaw_catalog_by_id()
        )
        if isinstance(target, Laboratory):
            section = LAB_VF_SECTIONS[0]
        elif isinstance(target, Familiar):
            section = "section-fam-vf-virtues"
        else:
            section = "section-vf-virtues"

        def confirm(index: int) -> None:
            name = catalog.describe_virtue_flaw(target.virtues_flaws[index], vf_catalog)
            if isinstance(target, Laboratory):
                self._confirm_delete_lab_virtue_flaw(target, index, name)
                return
            self._confirm_delete(target.virtues_flaws, index, name, section)

        self._chosen_or_pick(
            selected,
            [vf.vf_id for vf in target.virtues_flaws],
            empty="No Virtues/Flaws to remove.",
            then=confirm,
        )

    def _confirm_delete_lab_virtue_flaw(
        self, lab: Laboratory, index: int, name: str
    ) -> None:
        """Delete a lab Virtue/Flaw after confirming, saying what goes with
        it: the Feature built on a Feature Virtue, or the Focus (and its
        points) of a Focus Flaw."""
        instance = lab.virtues_flaws[index]
        feature = lab_rules.feature_on(lab, instance)
        focus = lab_rules.focus_feature(lab)
        message = f"Delete {escape(name)}?"
        if feature is not None:
            message += f" Its Feature, {escape(feature.name)}, goes too."
        elif instance.vf_id in FOCUS_FLAWS and focus is not None:
            message += (
                f" {escape(focus.name)} stops being the Focus and loses its "
                "Focus points."
            )

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                counted = lab_rules.counted_specializations(lab)
                del lab.virtues_flaws[index]
                lab_rules.prune_features(lab)
                lab_rules.reconcile_dropped(lab, counted)
                self._commit(*LAB_FEATURE_SECTIONS)

        self.app.push_screen(ConfirmScreen(message), handle_confirmed)

    def _selected_virtue_flaw(
        self, target: Character | Laboratory | Familiar
    ) -> int | None:
        """The row chosen in the target's Virtues or Flaws list, if any."""
        if isinstance(target, Character) and self._character_sheet_view is not None:
            return self._character_sheet_view.selected_virtue_flaw()
        if isinstance(target, Laboratory) and self._laboratory_sheet_view is not None:
            return self._laboratory_sheet_view.selected_virtue_flaw()
        if isinstance(target, Familiar) and self._familiar_sheet_view is not None:
            return self._familiar_sheet_view.selected_virtue_flaw()
        return None

    def _virtue_flaw_target(self) -> Character | Laboratory | Familiar | None:
        if (
            self.selected_kind == NodeKind.LABORATORY
            and self._active_section() in LAB_VF_SECTIONS
        ):
            return self.selected_laboratory
        if self.selected_kind == NodeKind.CHARACTER and self._active_section() in (
            "section-vf-virtues",
            "section-vf-flaws",
        ):
            return self.selected_character
        if self.selected_kind == NodeKind.FAMILIAR and self._active_section() in (
            "section-fam-vf-virtues",
            "section-fam-vf-flaws",
        ):
            return self.selected_familiar
        return None

    def _device_action_enabled(self, action: str) -> bool:
        """Whether More's Instill / Use a Charge can act on the chosen device row (see
        DeviceActions)."""
        return False

    @cached_property
    def _section_ops(self) -> dict[str, _SectionOps]:
        """Per section id, its a / d / e handlers (see WorkspaceScreen)."""
        raise NotImplementedError
