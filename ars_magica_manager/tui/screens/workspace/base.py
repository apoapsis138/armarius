"""The workspace's shared tables and its base class: the screen's state, the
navigation tree, the detail pane, focus and section tracking, the plumbing
behind a / e / d, More and New, and the actions that aren't about one kind
of record."""

from __future__ import annotations

import asyncio
import io
import json
import re
import uuid
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, replace
from dataclasses import field as dataclass_field
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

from .... import (
    actions,
    advance_forms,
    arms,
    catalog,
    character_templates,
    creation,
    creation_forms,
    deletion,
    giving,
    import_forms,
    menu_forms,
    neighbour_forms,
    neighbours,
    packs,
    place_events,
    places,
    presence,
    ruins,
    seasons,
    sourcebooks,
    storage,
    towns,
    transfer,
    tribunal_forms,
    tribunals,
    world,
)
from .... import books as bk
from .... import familiars as fam
from .... import laboratories as lab_rules
from .... import players as pl
from .... import sheet_text as st
from ....actions import (
    MORE_MENU,
    NEW_MENU,
    RECORD_SECTION,
    MenuItem,
    NodeKind,
)
from ....markup import escape
from ....models import (
    FOCUS_FLAWS,
    FULL,
    Ability,
    Character,
    CharacterTemplateDef,
    Covenant,
    Familiar,
    GrogYear,
    Laboratory,
    Neighbour,
    Player,
    Saga,
    ScoredTrait,
    SeasonPlan,
    Tribunal,
    VirtueFlawInstance,
    link_unlinked_features,
    new_instance_id,
)
from ....rules import activities as season_rules
from ....rules import creation as creation_rules
from ....rules import creation_characteristics as cch
from ....rules import creation_covenant as cov_creation
from ....rules import options as rule_options
from ....sections import (
    CASES_SECTION,
    DIARY_SECTION,
    FAIRS_SECTION,
    NEIGHBOUR_INFO_SECTION,
    REGION_INFO_SECTION,
    SEASONS_INFO_SECTION,
    TABLES_SECTION,
    TRIBUNAL_INFO_SECTION,
)
from ... import hosting
from ..creation_worksheet import CreationWorksheetScreen
from ..fields import (
    FieldsDialog,
)
from ..forms import (
    _character_create_dialog,
    _covenant_create_fields,
    _familiar_create_fields,
    _grog_year_dialog,
    _laboratory_create_fields,
    _saga_fields,
    _season_plan_dialog,
    saga_rule_options,
    template_key,
)
from ..help import HelpContext, HelpScreen, shown_keys
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
    _scored_trait_dialog,
)
from ..season_records import SeasonSummaryScreen
from ..sheets import (
    LAB_FEATURE_SECTIONS,
    LAB_TEXTS_SECTION,
    LAB_VF_SECTIONS,
    SPELL_SECTION,
    TAB_SECTIONS,
    BookListView,
    CharacterSheetView,
    CovenantSheetView,
    FamiliarSheetView,
    LaboratorySheetView,
    NeighbourSheetView,
    RegionSheetView,
    SagaContentSheetView,
    SeasonsSheetView,
    SheetView,
    TribunalSheetView,
)
from ..steps import run_steps
from ..widgets import (
    BottomBar,
    SelectableList,
    SheetSection,
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
    prompt_options={"include_reach": True},
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
    prompt_options={"include_reach": True},
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
        "include_reach": True,
    },
)


#: Which sheet section each covenant Boon/Hook kind lives in.
_BOON_HOOK_SECTION = {"Boon": "section-cov-boons", "Hook": "section-cov-hooks"}


#: Each tree node's help page (help/*.md), by the kind of node selected.
_HELP_PAGES: dict[NodeKind, str] = {
    NodeKind.SAGA: "saga",
    NodeKind.COVENANT: "covenant",
    NodeKind.CHARACTER_GROUP: "character-group",
    NodeKind.CHARACTER: "character",
    NodeKind.FAMILIAR: "familiar",
    NodeKind.LABORATORY_GROUP: "laboratory-group",
    NodeKind.LABORATORY: "laboratory",
    NodeKind.BOOK_GROUP: "unassigned-books",
    NodeKind.SEASONS: "seasons",
    NodeKind.SAGA_CONTENT: "saga-content",
    NodeKind.REGION: "region",
    NodeKind.TRIBUNAL: "tribunal",
    NodeKind.NEIGHBOUR_GROUP: "region",
    NodeKind.NEIGHBOUR: "neighbour",
}

#: How often, in seconds, a hosted saga's copies look for each other's saves
#: and say who has which record open.
_SHARED_TICK = 2.0

#: What only the storyguide may do, whatever a player owns:
#: making records, the saga's calendar, reading files on the host's disk,
#: writing out the whole saga, and moving vis or spells between characters.
_STORYGUIDE_ACTIONS = frozenset(
    {
        "new",
        "create_covenant",
        "create_tribunal",
        "create_neighbour",
        "roll_fair",
        "roll_table",
        "found_covenant",
        "create_character",
        "create_laboratory",
        "create_familiar",
        "advance_season",
        "set_date",
        "import_data",
        "give",
        "give_silver",
        "share_spell",
        "update_record",
        "export_saga",
        "export_pack",
    }
)

#: What anyone signed in may do anywhere: move around, read, and export
#: (which only reads the saga).
_LOOKING_ACTIONS = frozenset(
    {
        "filter",
        "toggle_section",
        "show_tab",
        "help",
        "step_out",
        "quit",
        "more",
        "export_record",
    }
)

#: The More commands whose handler isn't `action_<action>`.
_MENU_HANDLERS: dict[str, str] = {
    "lab_text_access": "_edit_lab_text_access",
    "edit_fatigue": "_edit_fatigue",
    "edit_familiar_fatigue": "_edit_familiar_fatigue",
    "creation_worksheet": "_open_creation_worksheet",
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


def _deletion_of(
    saga: Saga,
    record: Covenant | Character | Laboratory | Familiar | Tribunal | Neighbour,
) -> tuple[list[str], Callable[[], None]]:
    """What deleting `record` would do, for the confirmation, and the
    function that does it."""
    if isinstance(record, Neighbour):
        return (
            neighbours.deletion_consequences(saga, record),
            partial(neighbours.delete, saga, record),
        )
    if isinstance(record, Tribunal):
        return (
            tribunals.deletion_consequences(saga, record),
            partial(tribunals.delete, saga, record),
        )
    if isinstance(record, Covenant):
        return (
            deletion.covenant_consequences(saga, record),
            partial(deletion.delete_covenant, saga, record),
        )
    if isinstance(record, Character):
        return (
            deletion.character_consequences(saga, record),
            partial(deletion.delete_character, saga, record),
        )
    if isinstance(record, Familiar):
        return (
            deletion.familiar_consequences(saga, record),
            partial(deletion.delete_familiar, saga, record),
        )
    return (
        deletion.laboratory_consequences(saga, record),
        partial(deletion.delete_laboratory, saga, record),
    )


def _tree_node_with_data(tree: Tree, data: tuple) -> TreeNode | None:
    """The first node of `tree` whose `.data` is `data`, or None."""
    pending = [tree.root]
    while pending:
        node = pending.pop()
        if node.data == data:
            return node
        pending.extend(node.children)
    return None


#: The character sheet sections advancing the season can change.
_SEASON_SECTIONS: tuple[str, ...] = (
    "section-char-info",
    "tab-abilities",
    "section-arts",
    "section-casting",
    "section-known-spells",
    "section-char-season",
    "tab-diary",
)


class _ScreenFacts:
    """The workspace as actions.available sees it (actions.ActionFacts)."""

    def __init__(self, screen: WorkspaceBase) -> None:
        self._screen = screen

    @property
    def saga(self) -> Saga:
        return self._screen.saga

    @property
    def selected_kind(self) -> NodeKind | None:
        return self._screen.selected_kind

    @property
    def selected_covenant(self) -> Covenant | None:
        return self._screen.selected_covenant

    @property
    def selected_character(self) -> Character | None:
        return self._screen.selected_character

    @property
    def selected_laboratory(self) -> Laboratory | None:
        return self._screen.selected_laboratory

    def active_section(self) -> str | None:
        return self._screen._active_section()

    def player_may(self, action: str) -> bool:
        return self._screen._player_may(action)

    def on_record(self) -> bool:
        return self._screen._on_record()

    def creation_record(self) -> Character | Covenant | Laboratory | None:
        view = self._screen._current_sheet_view()
        return view.creation_record if view is not None else None

    def device_action_enabled(self, action: str) -> bool:
        return self._screen._device_action_enabled(action)

    def to_give(self) -> giving.Gift | None:
        return self._screen._to_give()

    def record_to_export(self) -> transfer.Record | None:
        return self._screen._record_to_export()

    def record_to_delete(
        self,
    ) -> Covenant | Character | Laboratory | Familiar | Tribunal | Neighbour | None:
        return self._screen._record_to_delete()

    def can_send_files(self) -> bool:
        # Over SSH there is nowhere to send the file.
        return hosting.transport() != "ssh"


class WorkspaceBase(Screen[None]):
    """The workspace's state and everything its actions share: the navigation
    tree and detail pane, which section is active, saving and refreshing
    (_commit), and the a / e / d plumbing. The per-record actions live in the
    mixins WorkspaceScreen combines."""

    #: One verb per key, everywhere (see reference/
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
        ("question_mark", "help", "Help"),
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
        "help",
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
        NodeKind.TRIBUNAL: (set(), TRIBUNAL_INFO_SECTION),
        NodeKind.REGION: (set(), REGION_INFO_SECTION),
        NodeKind.NEIGHBOUR_GROUP: (set(), REGION_INFO_SECTION),
        NodeKind.NEIGHBOUR: (set(), NEIGHBOUR_INFO_SECTION),
        NodeKind.SEASONS: (set(), SEASONS_INFO_SECTION),
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
        # Its user-made entries join the shared catalogs.
        catalog.use_saga(saga)
        self.selected_kind: NodeKind = NodeKind.SAGA
        self.selected_covenant: Covenant | None = None
        self.selected_character: Character | None = None
        self.selected_laboratory: Laboratory | None = None
        self.selected_familiar: Familiar | None = None
        self.selected_tribunal: Tribunal | None = None
        self.selected_neighbour: Neighbour | None = None
        self._character_sheet_view: CharacterSheetView | None = None
        self._laboratory_sheet_view: LaboratorySheetView | None = None
        self._covenant_sheet_view: CovenantSheetView | None = None
        self._familiar_sheet_view: FamiliarSheetView | None = None
        self._saga_content_view: SagaContentSheetView | None = None
        self._tribunal_sheet_view: TribunalSheetView | None = None
        self._region_sheet_view: RegionSheetView | None = None
        self._neighbour_sheet_view: NeighbourSheetView | None = None
        self._seasons_view: SeasonsSheetView | None = None
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
        if not self._is_storyguide():
            storage.guard = self._guard_save
        player = self._signed_in()
        storage.saved_by = player.name if player is not None else ""
        if self.saga.players:
            # Others may have the saga open (a hosted saga).
            self._session = uuid.uuid4().hex
            self.set_interval(_SHARED_TICK, self._shared_tick)
        await self._show_saga_detail()
        note = storage.newer_save_note(self.saga)
        if note is not None:
            self.notify(
                note, title="Saved by a newer Armarius", severity="warning", timeout=20
            )

    def on_unmount(self) -> None:
        # Back to the saga list: whoever signed in to this saga is signed out.
        self.app.player = None  # type: ignore[attr-defined]
        storage.guard = None
        storage.saved_by = ""
        if self._session is not None:
            presence.leave(self._session)

    # -- other copies of a hosted saga --

    #: This copy's presence id while the saga has players (presence.py).
    _session: str | None = None
    #: Who this copy last said is also on the open record, so each is
    #: announced once.
    _also_here: tuple[str | None, frozenset[str]] = (None, frozenset())

    def _who(self) -> str:
        player = self._signed_in()
        return player.name if player is not None else ""

    def _open_record_key(self) -> str | None:
        """The record on show, as "characters:mag1", for presence."""
        records = {
            NodeKind.CHARACTER: ("characters", self.selected_character),
            NodeKind.FAMILIAR: ("familiars", self.selected_familiar),
            NodeKind.LABORATORY: ("laboratories", self.selected_laboratory),
            NodeKind.COVENANT: ("covenants", self.selected_covenant),
            NodeKind.TRIBUNAL: ("tribunals", self.selected_tribunal),
            NodeKind.NEIGHBOUR: ("neighbours", self.selected_neighbour),
        }
        kind, record = records.get(self.selected_kind, ("", None))
        return f"{kind}:{record.id}" if record is not None else None

    async def _shared_tick(self) -> None:
        """Every few seconds: pick up another copy's save, and say who else
        has the open record."""
        changed = storage.reload_into(self.saga)
        if changed:
            await self._show_reloaded(changed)
        if self._session is None:
            return
        record = self._open_record_key()
        presence.note(self._session, self.saga.id, self._who(), record)
        others = frozenset(presence.others_on(self._session, self.saga.id, record))
        last_record, announced = self._also_here
        new = others - announced if record == last_record else others
        self._also_here = (record, others)
        if new and record is not None:
            name = self._shown_name()
            self.notify(
                f"{escape(', '.join(sorted(new)))} "
                f"{'is' if len(new) == 1 else 'are'} also on {escape(name)}.",
                timeout=6,
            )

    async def _show_reloaded(self, changed: list[tuple[str, str]]) -> None:
        """Show what another copy saved: the tree, the header, and the sheet
        on show refreshed in place (its tab and chosen rows stay), or the
        saga if its record is gone."""
        who = self.saga.saved_by or "The storyguide"
        record = self._open_record_key()
        open_changed = record is not None and tuple(record.split(":", 1)) in changed
        gone = record is not None and not self._open_record_exists()
        self._update_saga_clock()
        tree = self._nav_tree()
        current = tree.cursor_node.data if tree.cursor_node is not None else None
        self._rebuild_tree()
        if gone:
            tree.select_node(tree.root)
            self.notify(f"{escape(who)} deleted what you had open.", severity="warning")
            return
        node = _tree_node_with_data(tree, current) if current is not None else None
        if node is not None:
            tree.move_cursor(node)
        view = self._current_sheet_view()
        if view is not None:
            for section in list(view._refreshers):
                view.refresh_section(section)
        elif node is not None:
            tree.select_node(node)  # a list node: show it afresh
        for screen in self.app.screen_stack:
            record_changed = getattr(screen, "record_changed", None)
            if callable(record_changed):
                record_changed()
        if open_changed:
            self.notify(
                f"{escape(who)} changed {escape(self._shown_name())}; reloaded."
            )
        else:
            self.notify(f"Updated by {escape(who)}.", timeout=3)

    def _open_record_exists(self) -> bool:
        records = {
            NodeKind.CHARACTER: (self.saga.characters, self.selected_character),
            NodeKind.FAMILIAR: (self.saga.familiars, self.selected_familiar),
            NodeKind.LABORATORY: (self.saga.laboratories, self.selected_laboratory),
            NodeKind.COVENANT: (self.saga.covenants, self.selected_covenant),
            NodeKind.TRIBUNAL: (self.saga.tribunals, self.selected_tribunal),
            NodeKind.NEIGHBOUR: (self.saga.neighbours, self.selected_neighbour),
        }
        listed, record = records.get(self.selected_kind, ([], None))
        return record is None or any(r is record for r in listed)

    def _guard_save(
        self, before: dict[str, Any], after: dict[str, Any]
    ) -> tuple[dict[str, Any], list[str]]:
        """The last check before a signed-in player's save:
        what they may not change isn't saved, and they're told."""
        kept, refused = pl.guard_changes(self._signed_in(), before, after)
        if refused:
            self.notify(
                "Not saved: only the storyguide can change "
                + escape(", ".join(refused)),
                severity="warning",
            )
        return kept, refused

    def _update_saga_clock(self) -> None:
        """Shows the saga's current date in the Header, on every screen of
        the workspace -- the saga owns the calendar, everything inherits it."""
        saga = self.saga
        player = self._signed_in()
        who = f" | {escape(player.name)}" if player is not None else ""
        self.sub_title = (
            f"{escape(saga.name)} | {saga.current_season} {saga.current_year}{who}"
        )

    def _rebuild_tree(self) -> None:
        tree = self._nav_tree()
        tree.reset(escape(self.saga.name), data=(NodeKind.SAGA,))
        tree.root.expand()

        # The troupe's covenants at the top; the others in the Region,
        # each under its Tribunal.
        for covenant in self.saga.covenants:
            if covenant.played:
                self._add_covenant_node(tree.root, covenant, expand=True)
        self._add_region(tree.root)

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
        tree.root.add_leaf("Saga Content", data=(NodeKind.SAGA_CONTENT,))

    def _add_covenant_node(self, parent, covenant: Covenant, *, expand: bool) -> None:
        """A covenant's node, with its characters and laboratories under it.
        A covenant kept at Line or Sketch detail lists only the groups it
        has anything in."""
        characters = [c for c in self.saga.characters if c.covenant_id == covenant.id]
        labs = [lab for lab in self.saga.laboratories if lab.covenant_id == covenant.id]
        label = escape(world.marked_name(covenant)) + _creating(covenant)
        data = (NodeKind.COVENANT, covenant.id)
        full = covenant.detail == FULL
        if not full and not characters and not labs:
            parent.add_leaf(label, data=data)
            return
        cov_node = parent.add(label, data=data, expand=expand)
        if full or characters:
            char_group = cov_node.add(
                f"Characters ({len(characters)})",
                data=(NodeKind.CHARACTER_GROUP, covenant.id),
                expand=True,
            )
            for character in characters:
                self._add_character_node(char_group, character)
        if full or labs:
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

    def _add_region(self, parent) -> None:
        """The Region: each Tribunal with the covenants the troupe doesn't
        play under it, then any such covenant that has no Tribunal."""
        region = parent.add("The Region", data=(NodeKind.REGION,), expand=True)
        others = [c for c in self.saga.covenants if not c.played]
        for tribunal in self.saga.tribunals:
            node = region.add(
                escape(tribunal.name),
                data=(NodeKind.TRIBUNAL, tribunal.id),
                expand=True,
            )
            for covenant in others:
                if covenant.tribunal_id == tribunal.id:
                    self._add_covenant_node(node, covenant, expand=False)
        known = {t.id for t in self.saga.tribunals}
        for covenant in others:
            if covenant.tribunal_id not in known:
                self._add_covenant_node(region, covenant, expand=False)
        for group in neighbours.GROUPS:
            members = neighbours.members(self.saga, group.key)
            if not members:
                continue
            node = region.add(
                f"{group.title} ({len(members)})",
                data=(NodeKind.NEIGHBOUR_GROUP, group.key),
                expand=False,
            )
            for neighbour in members:
                node.add_leaf(
                    escape(neighbour.name), data=(NodeKind.NEIGHBOUR, neighbour.id)
                )

    def _add_character_node(self, parent, character: Character) -> None:
        """A character's own tree node: a plain leaf, unless it's a magus
        with a bound Familiar, in which case it becomes an expandable node
        with the Familiar as its one child leaf (nested under its creator,
        never its own group)."""
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
        self._saga_content_view = None
        self._tribunal_sheet_view = None
        self._region_sheet_view = None
        self._neighbour_sheet_view = None
        self._seasons_view = None

        handler = self._NODE_SELECTED.get(kind)
        if handler is not None:
            await handler(self, data[1] if len(data) > 1 else None)

        if self._current_sheet_view() is None:
            # Enter on a node moves into what it shows: a list view's list.
            for rows in self._detail_pane().query(SelectableList):
                rows.focus()
                break
        self.refresh_bindings()

    # What selecting each kind of tree node does: set the selection and
    # show its detail. `ident` is the node's record or covenant id, if any.

    async def _select_saga(self, ident: str | None) -> None:
        self.selected_covenant = None
        self.selected_character = None
        self.selected_laboratory = None
        self.selected_familiar = None
        await self._show_saga_detail()

    async def _select_covenant(self, ident: str | None) -> None:
        covenant = next(c for c in self.saga.covenants if c.id == ident)
        self.selected_covenant = covenant
        self.selected_character = None
        self.selected_laboratory = None
        self.selected_familiar = None
        await self._show_covenant_detail(covenant)

    async def _select_character_group(self, ident: str | None) -> None:
        covenant = self.saga.covenant(ident)
        self.selected_covenant = covenant
        self.selected_character = None
        await self._show_placeholder_detail(
            f"Characters in {covenant.name}" if covenant else "Unassigned Characters",
            "Select a character from the tree, or press 'n' to add one."
            if covenant
            else "These characters aren't assigned to a covenant. Select one "
            "from the tree, or press 'n' to add one.",
        )

    async def _select_character(self, ident: str | None) -> None:
        character = next(c for c in self.saga.characters if c.id == ident)
        self.selected_character = character
        self.selected_covenant = self.saga.covenant(character.covenant_id)
        self.selected_familiar = None
        await self._show_character_detail(character)

    async def _select_familiar(self, ident: str | None) -> None:
        familiar = next(f for f in self.saga.familiars if f.id == ident)
        self.selected_familiar = familiar
        self.selected_character = self.saga.character(familiar.character_id)
        self.selected_covenant = (
            self.saga.covenant(self.selected_character.covenant_id)
            if self.selected_character is not None
            else None
        )
        await self._show_familiar_detail(familiar)

    async def _select_laboratory_group(self, ident: str | None) -> None:
        covenant = self.saga.covenant(ident)
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

    async def _select_laboratory(self, ident: str | None) -> None:
        lab = next(lab for lab in self.saga.laboratories if lab.id == ident)
        self.selected_laboratory = lab
        self.selected_covenant = self.saga.covenant(lab.covenant_id)
        await self._show_laboratory_detail(lab)

    async def _select_saga_content(self, ident: str | None) -> None:
        self.selected_covenant = None
        view = SagaContentSheetView(self.saga, players=self._is_storyguide())
        await self._set_detail(view)
        self._saga_content_view = view
        self._focus_first_section(initial=True)

    async def _select_seasons(self, ident: str | None) -> None:
        self.selected_covenant = None
        view = SeasonsSheetView(self.saga)
        await self._set_detail(view)
        self._seasons_view = view
        self._focus_first_section(initial=True)

    async def _select_region(self, ident: str | None) -> None:
        """The Region, or (`ident`) one of its groups of neighbours, whose
        list takes focus."""
        self.selected_covenant = None
        view = RegionSheetView(self.saga, ident)
        await self._set_detail(view)
        self._region_sheet_view = view
        group = next((g for g in neighbours.GROUPS if g.key == ident), None)
        if group is not None and view.query(f"#{group.section_id}"):
            self.call_after_refresh(
                view.query_one(f"#{group.section_id}", SheetSection).focus_section
            )
        else:
            self._focus_first_section(initial=True)

    async def _select_neighbour(self, ident: str | None) -> None:
        neighbour = self.saga.neighbour(ident)
        if neighbour is None:
            return
        self.selected_covenant = None
        self.selected_neighbour = neighbour
        view = NeighbourSheetView(self.saga, neighbour)
        await self._set_detail(view)
        self._neighbour_sheet_view = view
        self._focus_first_section(initial=True)

    async def _select_tribunal(self, ident: str | None) -> None:
        tribunal = self.saga.tribunal(ident)
        if tribunal is None:
            return
        self.selected_covenant = None
        self.selected_tribunal = tribunal
        await self._show_tribunal_detail(tribunal)

    async def _show_tribunal_detail(self, tribunal: Tribunal) -> None:
        view = TribunalSheetView(self.saga, tribunal)
        await self._set_detail(view)
        self._tribunal_sheet_view = view
        self._focus_first_section(initial=True)

    async def _select_book_group(self, ident: str | None) -> None:
        self.selected_covenant = None
        await self._set_detail(
            BookListView(
                self.saga,
                lambda: bk.unassigned_books(self.saga),
                section_id="section-unassigned-books",
                title="Unassigned Books",
            )
        )

    #: The handler for each kind of tree node (Strategy, as a table).
    _NODE_SELECTED: ClassVar[
        dict[NodeKind, Callable[[WorkspaceBase, str | None], Awaitable[None]]]
    ] = {
        NodeKind.SAGA: _select_saga,
        NodeKind.COVENANT: _select_covenant,
        NodeKind.CHARACTER_GROUP: _select_character_group,
        NodeKind.CHARACTER: _select_character,
        NodeKind.FAMILIAR: _select_familiar,
        NodeKind.LABORATORY_GROUP: _select_laboratory_group,
        NodeKind.LABORATORY: _select_laboratory,
        NodeKind.SAGA_CONTENT: _select_saga_content,
        NodeKind.SEASONS: _select_seasons,
        NodeKind.BOOK_GROUP: _select_book_group,
        NodeKind.REGION: _select_region,
        NodeKind.TRIBUNAL: _select_tribunal,
        NodeKind.NEIGHBOUR_GROUP: _select_region,
        NodeKind.NEIGHBOUR: _select_neighbour,
    }

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if not self._player_may(action):
            return False
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
        """Whether `action` can run where focus is (actions.available)."""
        return actions.available(action, _ScreenFacts(self))

    # -- focus: one stop per section, the tree, Esc and the tab numbers --

    @property
    def focus_chain(self) -> list[Widget]:
        """Tab and Shift+Tab stop once per section."""
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
        return section is not None and section == RECORD_SECTION.get(self.selected_kind)

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
            lambda: [item for item in MORE_MENU if self._available(item.action)],
        )

    def _new_items(self) -> list[MenuItem]:
        """What New can make from the selected tree node."""
        return self._in_pass(
            "new",
            lambda: [item for item in NEW_MENU if self._available(item.action)],
        )

    def _run_menu_item(self, item: MenuItem) -> None:
        getattr(self, _MENU_HANDLERS.get(item.action, f"action_{item.action}"))()

    def _run_menu(self, title: str, items: list[MenuItem]) -> None:
        """Run the only item directly; with several, ask which."""
        if not items:
            return
        if len(items) == 1:
            self._run_menu_item(items[0])
            return
        by_action = {item.action: item for item in items}

        def handle_choice(action: str | None) -> None:
            if action is not None:
                self._run_menu_item(by_action[action])

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
        """What / filters here: the Lab Texts list, the Spells list or the
        Region's neighbours."""
        if self._active_section() == LAB_TEXTS_SECTION:
            return "lab_texts"
        if self._active_section() == SPELL_SECTION:
            return "spells"
        if self._active_section() in self._NEIGHBOUR_GROUP_SECTIONS:
            return "neighbours"
        return None

    def action_filter(self) -> None:
        target = self._filter_target()
        if target == "lab_texts":
            self.action_filter_lab_texts()
        elif target == "neighbours":
            self._filter_neighbours()
        elif target == "spells":
            try:
                self.query_one("#spell-search").focus()
            except NoMatches:
                pass

    def action_filter_lab_texts(self) -> None:
        raise NotImplementedError

    _NEIGHBOUR_GROUP_SECTIONS: ClassVar[frozenset[str]] = frozenset(
        g.section_id for g in neighbours.GROUPS
    )

    def _filter_neighbours(self) -> None:
        """/ on a list of the Region: narrow every list to a region and a
        kind (neighbour_filter), then redraw them and their titles."""

        def done(_end: object) -> None:
            if self._region_sheet_view is not None:
                self._region_sheet_view.refresh_all()

        run_steps(self.app, neighbour_forms.filter_form(self.saga), done)

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
        """The covenant, laboratory or character whose node is selected: what More's
        Export exports."""
        if self.selected_kind == NodeKind.CHARACTER:
            return self.selected_character
        if self.selected_kind == NodeKind.LABORATORY:
            return self.selected_laboratory
        if self.selected_kind == NodeKind.COVENANT:
            return self.selected_covenant
        return None

    def action_export_record(self) -> None:
        """More's Export on a covenant, laboratory or character: write it to a file
        that another saga can import."""
        record = self._record_to_export()
        if record is None:
            return

        def handle_result(result: tuple[Path, bool] | None) -> None:
            if result is None:
                return
            path, with_members = result
            if self.app.is_web:
                # A browser copy: the file goes to the player's
                # computer as a download, not to a folder on the host.
                data = transfer.export_data(
                    self.saga, record, with_members=with_members
                )
                self.app.deliver_binary(
                    io.BytesIO(json.dumps(data, indent=2).encode("utf-8")),
                    save_filename=path.name,
                    mime_type="application/json",
                )
                self.notify(
                    f"Exported {escape(record.name)}: your browser downloads it."
                )
                return
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

    def action_export_saga(self) -> None:
        """More's Export Saga on the saga: write every record to a file
        that Import reads back (A Whole Saga)."""
        if self.app.is_web:
            # A browser copy: the file goes to the player's computer.
            data = transfer.export_saga_data(self.saga)
            self.app.deliver_binary(
                io.BytesIO(json.dumps(data, indent=2).encode("utf-8")),
                save_filename=transfer.saga_file_name(self.saga),
                mime_type="application/json",
            )
            self.notify(
                f"Exported {escape(self.saga.name)}: your browser downloads it."
            )
            return

        def done(end: object) -> None:
            if isinstance(end, list) and end:
                self.notify("\n".join(end))

        run_steps(
            self.app, menu_forms.export_saga(self.saga, storage.EXPORTS_DIR), done
        )

    def action_export_pack(self) -> None:
        """More's Export Pack on the saga: write the chosen Tribunals,
        covenants, places and neighbours to a content pack."""

        def download(name: str, data: dict[str, Any]) -> list[str]:
            self.app.deliver_binary(
                io.BytesIO(json.dumps(data, indent=2).encode("utf-8")),
                save_filename=name,
                mime_type="application/json",
            )
            return [f"Exported {escape(data['name'])}: your browser downloads it."]

        # A browser copy: the file goes to the player's computer.
        deliver = download if self.app.is_web else None

        def done(end: object) -> None:
            if isinstance(end, list) and end:
                self.notify("\n".join(end))

        run_steps(
            self.app, packs.export_pack(self.saga, storage.EXPORTS_DIR, deliver), done
        )

    def action_update_record(self) -> None:
        """More's Update from a File on a covenant, laboratory or
        character: read an export of it over it, after showing what
        changes."""
        record = self._record_to_export()
        if record is None:
            return

        def done(end: object) -> None:
            if not isinstance(end, list):
                return
            view = self._current_sheet_view()
            self._commit(*(view._refreshers if view is not None else ()), tree=True)
            if end:
                self.notify("\n".join(end))

        run_steps(self.app, import_forms.update_record(self.saga, record), done)

    def _to_give(self) -> giving.Gift | None:
        """What More's Give would give (see GivingActions)."""
        return None

    def _active_section(self) -> str | None:
        return self._in_pass("section", self._find_active_section)

    def _find_active_section(self) -> str | None:
        """Which sheet section is "active" for a / e / d and More: the
        nearest Collapsible around whatever has focus -- which also covers a
        sheet's top panel, outside its tabs. With none, a flat tab that
        dispatches on its own id (see _SHEET_DISPATCH), otherwise the sheet's
        always-visible top section, so 'e' edits the record from any tab.
        The Unassigned Books node has no sheet, just a section; on Saga
        Content, a tab acts on its list (TAB_SECTIONS)."""
        if self.selected_kind == NodeKind.BOOK_GROUP:
            return "section-unassigned-books"
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
        if self.selected_kind == NodeKind.SAGA_CONTENT:
            return TAB_SECTIONS.get(tab_id)
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
        seasons list, so e plans lab work straight away -- and
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
                stop = view.tab_first_stop(view.query_one(f"#{tabbed.active}", TabPane))
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
            NodeKind.TRIBUNAL: self.selected_tribunal,
            NodeKind.NEIGHBOUR: self.selected_neighbour,
        }.get(self.selected_kind)
        if record is not None:
            return record.name
        where = f" in {covenant.name}" if covenant is not None else ""
        return {
            NodeKind.CHARACTER_GROUP: f"Characters{where}",
            NodeKind.LABORATORY_GROUP: f"Laboratories{where}",
            NodeKind.SAGA_CONTENT: "Saga Content",
            NodeKind.SEASONS: "Seasons",
            NodeKind.BOOK_GROUP: "Unassigned Books",
            NodeKind.REGION: "The Region",
            NodeKind.NEIGHBOUR_GROUP: "The Region",
        }.get(self.selected_kind, "")

    def _update_where(self) -> None:
        """Say where focus is in the row above the footer:
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
                if section is not None and section.id != RECORD_SECTION.get(
                    self.selected_kind
                ):
                    parts.append(_COUNT.sub("", _plain(section.title)))
            if isinstance(focused, SelectableList) and focused.chosen_text:
                parts.append(focused.chosen_text)
        bar.set_where("  ›  ".join(escape(part) for part in parts if part))

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen(self.help_context()))

    def help_context(self) -> HelpContext:
        """What Help opens on: the focused section, its tab and
        the sheet or view on show, then finding your way around; with the
        where-am-I row's words and the keys the footer offers here."""
        ids: list[str] = []
        focused = self.app.focused
        view = self._current_sheet_view()
        if focused is not None and view is not None and not self._tree_focused():
            section = section_of(focused)
            if section is not None and section.id:
                ids.append(section.id)
            tabbed = view.query_one(TabbedContent)
            if tabbed.active:
                ids.append(tabbed.active)
        page = _HELP_PAGES.get(self.selected_kind)
        if page is not None:
            ids.append(page)
        ids.append("workspace")
        keys = shown_keys(self, self.GLOBAL_ACTIONS)
        more = self._more_items()
        if len(more) > 1:
            keys.append("m More: " + ", ".join(item.label for item in more))
        try:
            where = self.query_one(BottomBar).where
        except NoMatches:
            where = ""
        return HelpContext(ids, where, keys)

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
        lines.append(
            "Books in play: "
            + sourcebooks.summary(saga.books_in_play, sourcebooks.saga_sources(saga))
        )
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
            NodeKind.SAGA_CONTENT: self._saga_content_view,
            NodeKind.TRIBUNAL: self._tribunal_sheet_view,
            NodeKind.REGION: self._region_sheet_view,
            NodeKind.NEIGHBOUR_GROUP: self._region_sheet_view,
            NodeKind.NEIGHBOUR: self._neighbour_sheet_view,
            NodeKind.SEASONS: self._seasons_view,
        }.get(self.selected_kind)

    def _open_creation_worksheet(
        self, record: Covenant | Character | Laboratory | None = None
    ) -> None:
        """The Creation Worksheet for `record`, or for the record on show
        while it is In Creation."""
        if record is None:
            view = self._current_sheet_view()
            record = view.creation_record if view is not None else None
        if record is not None:
            self.app.push_screen(CreationWorksheetScreen(self, record))  # type: ignore[arg-type]

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
        focused list always has one; with none (the section is
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
        """The top panel's In Creation / In Play switch: asks
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
            if isinstance(record, Covenant):
                note = cov_creation.leftover_note(self.saga, record)
                if note:
                    message += f"\n\n{escape(note)}"
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

    def _books_changed(self) -> None:
        """After a change that may touch books (the library's actions
        redraw the book lists and the tree's Unassigned Books)."""

    def _commit(self, *sections: str, tree: bool = False) -> None:
        """Save a change: write the saga, rebuild the navigation tree if a
        name or the structure changed (`tree`), and refresh `sections` of the
        sheet on show -- the one whose handler made the change."""
        storage.save_saga(self.saga)
        # The sheet on show, before rebuilding the tree lets it go.
        shown = self._current_sheet_view()
        if tree:
            self._rebuild_tree()
        view = self._current_sheet_view()
        if view is not None:
            for section in sections:
                view.refresh_section(section)
        # A Tribunal whose customs changed shows their tabs instead.
        if isinstance(view, TribunalSheetView) and view.stale():
            self.call_later(self._show_tribunal_detail, view.tribunal)
        # A neighbour whose kind changed shows its new kind's tab.
        if isinstance(shown, NeighbourSheetView) and shown.stale():
            self.call_later(self._select_neighbour, shown.neighbour.id)
        # An open Creation Worksheet shows the record too.
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
                    self.saga,
                    values["name"],
                    values["notes"],
                    season=values["season"] or "Spring",
                    aura_realm=values["aura_realm"] or "Magic",
                )
                storage.save_saga(self.saga)
                self._rebuild_tree()
                self.selected_covenant = covenant
                self.selected_kind = NodeKind.COVENANT
                await self._show_covenant_detail(covenant)
                self._open_creation_worksheet(covenant)

        self.app.push_screen(
            FieldsDialog(
                "Create a New Covenant", _covenant_create_fields(), save_label="Create"
            ),
            handle_result,
        )

    def action_create_tribunal(self) -> None:
        before = {t.id for t in self.saga.tribunals}

        def done(_end: object) -> None:
            storage.save_saga(self.saga)
            self._rebuild_tree()
            made = [t for t in self.saga.tribunals if t.id not in before]
            if made:
                node = _tree_node_with_data(
                    self._nav_tree(), (NodeKind.TRIBUNAL, made[-1].id)
                )
                if node is not None:
                    self.call_after_refresh(self._nav_tree().select_node, node)

        run_steps(self.app, tribunal_forms.new_tribunal_form(self.saga), done)

    def action_create_neighbour(self) -> None:
        before = {n.id for n in self.saga.neighbours}

        def done(_end: object) -> None:
            storage.save_saga(self.saga)
            self._rebuild_tree()
            made = [n for n in self.saga.neighbours if n.id not in before]
            if made:
                node = _tree_node_with_data(
                    self._nav_tree(), (NodeKind.NEIGHBOUR, made[-1].id)
                )
                if node is not None:
                    self.call_after_refresh(self._nav_tree().select_node, node)

        run_steps(self.app, neighbour_forms.new_neighbour(self.saga), done)

    def action_withdraw_case(self) -> None:
        """More's Withdraw on the docket's chosen case."""
        view = self._tribunal_sheet_view
        row = view.section_row(CASES_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            tribunal_forms.withdraw_case(view.tribunal, row),
            lambda _end: self._commit(CASES_SECTION),
        )

    def action_roll_fair(self) -> None:
        """More's Roll Income on a town's chosen fair."""
        view = self._neighbour_sheet_view
        row = view.section_row(FAIRS_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            towns.roll_fair(self.saga, view.neighbour, row),
            lambda _end: self._commit(FAIRS_SECTION),
        )

    def action_roll_table(self) -> None:
        """More's Roll on a place's chosen roll table."""
        view = self._neighbour_sheet_view
        row = view.section_row(TABLES_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            place_events.roll_table(self.saga, view.neighbour, row),
            lambda _end: self._commit(TABLES_SECTION, DIARY_SECTION),
        )

    def action_create_character(self) -> None:
        covenant = self.selected_covenant

        async def create(
            values: dict[str, Any],
            template: CharacterTemplateDef | None = None,
            blanks: dict[str, str] | None = None,
        ) -> None:
            character = creation.add_character(
                self.saga, values["name"], values["type"], values["covenant_id"]
            )
            if template is not None:
                character_templates.apply(self.saga, character, template, blanks)
            storage.save_saga(self.saga)
            self._rebuild_tree()
            self.selected_character = character
            self.selected_kind = NodeKind.CHARACTER
            await self._show_character_detail(character)
            self._open_creation_worksheet(character)

        async def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            template = character_templates.find(
                values.get(template_key(values["type"]))
            )
            wanted = character_templates.blanks(template) if template else []
            if template is None or not wanted:
                await create(values, template)
                return

            async def handle_blanks(filled: dict[str, Any] | None) -> None:
                # Cancelling the names cancels the new character.
                if filled is not None:
                    await create(values, template, filled)

            self.app.push_screen(
                FieldsDialog(
                    f"{escape(template.name)} template",
                    creation_forms.blanks_fields(wanted),
                    save_label="Use",
                ),
                handle_blanks,
            )

        self.app.push_screen(
            _character_create_dialog(self.saga, covenant.id if covenant else None),
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
                self._open_creation_worksheet(lab)

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

    # -- deleting a covenant, character, laboratory or Familiar --

    def _record_to_delete(
        self,
    ) -> Covenant | Character | Laboratory | Familiar | Tribunal | Neighbour | None:
        """The record d deletes: the covenant, character, laboratory or
        Familiar selected in the tree, if that's what's selected."""
        return {
            NodeKind.COVENANT: self.selected_covenant,
            NodeKind.CHARACTER: self.selected_character,
            NodeKind.LABORATORY: self.selected_laboratory,
            NodeKind.FAMILIAR: self.selected_familiar,
            NodeKind.TRIBUNAL: self.selected_tribunal,
            NodeKind.NEIGHBOUR: self.selected_neighbour,
        }.get(self.selected_kind)

    def action_delete_record(self) -> None:
        """Delete the selected record, after a confirmation that says what
        happens to what it owns (see deletion). A Familiar's magus is shown
        afterwards; otherwise the saga."""
        record = self._record_to_delete()
        if record is None:
            return
        saga = self.saga
        consequences, delete = _deletion_of(saga, record)
        message = f"Delete {escape(record.name)}?"
        if consequences:
            message += "\n\n" + "\n".join(map(escape, consequences))
        magus = fam.magus_of(saga, record) if isinstance(record, Familiar) else None

        async def handle_confirmed(confirmed: bool | None) -> None:
            if not confirmed:
                return
            delete()
            storage.save_saga(saga)
            self._rebuild_tree()
            if magus is not None:
                await self._show_character(magus)
            else:
                await self._show_saga_root()

        self.app.push_screen(ConfirmScreen(message), handle_confirmed)

    async def _show_character(self, character: Character) -> None:
        """Select `character`, in the tree and the detail pane."""
        self.selected_kind = NodeKind.CHARACTER
        self.selected_character = character
        self.selected_covenant = self.saga.covenant(character.covenant_id)
        self.selected_laboratory = None
        self.selected_familiar = None
        self._character_sheet_view = None
        self._familiar_sheet_view = None
        self._saga_content_view = None
        tree = self._nav_tree()
        node = _tree_node_with_data(tree, (NodeKind.CHARACTER, character.id))
        if node is not None:
            # A rebuilt tree has no lines until it next renders.
            self.call_after_refresh(tree.move_cursor, node)
        await self._show_character_detail(character)
        self.refresh_bindings()

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
        self._saga_content_view = None
        tree = self._nav_tree()
        tree.move_cursor(tree.root)
        await self._show_saga_detail()
        self.refresh_bindings()

    def _section_op(self, name: str) -> Callable[[], None] | None:
        """The active section's handler for `name` ("add", "remove", "edit"
        or "restore"), if it has one."""
        ops = self._section_ops.get(self._active_section() or "")
        return None if ops is None else getattr(ops, name)

    #: Core sections whose changes can rename or add records in the tree.
    _TREE_SECTIONS: ClassVar[frozenset[str]] = frozenset(
        {
            "section-cov-magi",
            TRIBUNAL_INFO_SECTION,
            NEIGHBOUR_INFO_SECTION,
            *(g.section_id for g in neighbours.GROUPS),
        }
    )

    def _core_verb(self, section: str, verb: str) -> None:
        """Run the sheet's core Add, Edit or Delete (commands.SectionOps)
        for `section` on its chosen row, then save and redraw it."""
        view = self._current_sheet_view()
        ops = view.core_ops.get(section) if view is not None else None
        step_of = getattr(ops, verb, None) if ops is not None else None
        if view is None or step_of is None:
            return
        if verb == "add":
            step = step_of()
        else:
            row = view.section_row(section)
            if row is None:
                return
            step = step_of(row)
        run_steps(
            self.app,
            step,
            lambda _end: self._commit(section, tree=section in self._TREE_SECTIONS),
        )

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

    # -- who is using this copy --

    def _signed_in(self) -> Player | None:
        """The player signed in to this browser copy; None in the
        storyguide's own window, which never signs in."""
        return getattr(self.app, "player", None)

    def _player_may(self, action: str) -> bool:
        """Whether whoever is signed in may run `action` here:
        the storyguide anything; a player moves around and reads anywhere,
        and changes only what they may change (players.may_change)."""
        if self._is_storyguide():
            return True
        if action in _STORYGUIDE_ACTIONS:
            return False
        return action in _LOOKING_ACTIONS or self._may_change_here()

    def _may_change_here(self) -> bool:
        """Whether whoever is signed in may change the record on show."""
        record = {
            NodeKind.CHARACTER: self.selected_character,
            NodeKind.FAMILIAR: self.selected_familiar,
            NodeKind.LABORATORY: self.selected_laboratory,
            NodeKind.COVENANT: self.selected_covenant,
            NodeKind.TRIBUNAL: self.selected_tribunal,
            NodeKind.NEIGHBOUR: self.selected_neighbour,
        }.get(self.selected_kind)
        return pl.may_change(self.saga, self._signed_in(), record)

    def _is_storyguide(self) -> bool:
        """Whether whoever is using this copy runs the saga: the
        storyguide's own window, or a browser copy signed in as a
        storyguide."""
        if not self.app.is_web:
            return True
        player = self._signed_in()
        return player is not None and player.role == pl.STORYGUIDE

    # -- Saga --

    def _edit_saga(self) -> None:
        async def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            self.saga.rule_options = saga_rule_options(
                result, kept=self.saga.rule_options
            )
            for field, value in result.items():
                setattr(self.saga, field, value)
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
        """Advance the saga by one season: the core's steps
        (advance_forms), the first drawn as the Advance Time dialog."""
        saga = self.saga

        def done(end: object) -> None:
            if isinstance(end, advance_forms.Played):
                storage.save_saga(saga)
                self.run_worker(self._season_played(end))

        def handle_result(confirmed: bool | None) -> None:
            if confirmed:
                run_steps(
                    self.app,
                    advance_forms.play_season(saga, storage.backup_saga),
                    done,
                )

        self.app.push_screen(
            AdvanceSeasonScreen(advance_forms.advance_text(saga)), handle_result
        )

    async def _season_played(self, played: advance_forms.Played) -> None:
        """Save the season played out and redraw what it changed: xp
        (scores, casting and lab totals), the Diary, This Season and
        Wealth; then show its results."""
        saga = self.saga
        await self._apply_saga_date(saga.current_season, saga.current_year)
        for section in _SEASON_SECTIONS:
            self._refresh_character_section(section)
        self._refresh_laboratory_section("tab-lab-planning")
        self._refresh_covenant_section("tab-cov-seasons")
        self._refresh_covenant_section("section-cov-ahead")
        if self._seasons_view is not None:
            self._seasons_view.refresh_all()
        if played.advanced.added:
            self._refresh_covenant_section("section-eco-wealth")
        if saga.keep_season_records and played.results:
            self._rebuild_tree()
        if played.results:
            self.app.push_screen(SeasonSummaryScreen(saga, played.advanced.record))
        self.notify(played.message)

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
        """Set up a grog's yearly update."""

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

    def action_edit_arms(self) -> None:
        """More's Arms on a covenant, or a lord, town or faction: its shield
        and blazon."""
        record = self._record_to_delete()
        if record is None or not arms.bears_arms(record):
            return
        section = (
            NEIGHBOUR_INFO_SECTION
            if isinstance(record, Neighbour)
            else "section-cov-info"
        )
        run_steps(self.app, arms.arms_form(record), lambda _end: self._commit(section))

    def action_found_covenant(self) -> None:
        """More's Found a Covenant Here on a ruined covenant's site: New
        Covenant, prefilled, raised on the ruin; then its worksheet."""
        record = self._record_to_delete()
        if not isinstance(record, Neighbour) or not places.is_ruin(record):
            return
        before = {c.id for c in self.saga.covenants}

        async def show(covenant: Covenant) -> None:
            self.selected_covenant = covenant
            self.selected_kind = NodeKind.COVENANT
            await self._show_covenant_detail(covenant)
            self._open_creation_worksheet(covenant)

        def finished(_end: object) -> None:
            fresh = [c for c in self.saga.covenants if c.id not in before]
            self._commit(NEIGHBOUR_INFO_SECTION, tree=True)
            if fresh:
                self.run_worker(show(fresh[-1]))

        run_steps(self.app, ruins.found_form(self.saga, record), finished)

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
                if isinstance(target, Character):
                    cch.apply_virtue(self.saga, target, instance)
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
                    self._refresh_character_section("section-char-characteristics")

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
                refusal=(
                    partial(cch.virtue_refusal, self.saga, target)
                    if isinstance(target, Character)
                    else None
                ),
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
            if isinstance(target, Character):
                instance = target.virtues_flaws[index]
                change = cch.removal_change(self.saga, target, instance)
                if change is not None:
                    self._confirm_delete_stepped(target, index, name, change)
                    return
            self._confirm_delete(target.virtues_flaws, index, name, section)

        self._chosen_or_pick(
            selected,
            [vf.vf_id for vf in target.virtues_flaws],
            empty="No Virtues/Flaws to remove.",
            then=confirm,
        )

    def _confirm_delete_stepped(
        self,
        character: Character,
        index: int,
        name: str,
        change: tuple[str, int, int],
    ) -> None:
        """Delete a Great or Poor (Characteristic) after confirming,
        moving its Characteristic back the point it added."""
        characteristic, before, after = change
        message = (
            f"Delete {escape(name)}? {characteristic} goes from {before:+d} "
            f"to {after:+d}."
        )

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                cch.unapply_virtue(self.saga, character, character.virtues_flaws[index])
                del character.virtues_flaws[index]
                self._commit("section-vf-virtues", "section-char-characteristics")

        self.app.push_screen(ConfirmScreen(message), handle_confirmed)

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
