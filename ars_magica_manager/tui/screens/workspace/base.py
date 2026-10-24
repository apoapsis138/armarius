"""The workspace's shared tables and its base class: the screen's state, the
navigation tree, the detail pane, focus and section tracking, the plumbing
behind a / e / d, More and New, and the actions that aren't about one kind
of record."""

from __future__ import annotations

import asyncio
import re
import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from dataclasses import field as dataclass_field
from functools import cached_property, partial
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
    catalog,
    creation,
    creatures,
    deletion,
    giving,
    help_text,
    hosting,
    neighbours,
    presence,
    seasons,
    sourcebooks,
    storage,
    transfer,
    tribunals,
    world,
)
from .... import books as bk
from .... import familiars as fam
from .... import players as pl
from .... import sheet_text as st
from ....actions import (
    MORE_MENU,
    NEW_MENU,
    RECORD_SECTION,
    MenuItem,
    NodeKind,
)
from ....forms import neighbour as neighbour_forms
from ....forms import season as season_forms
from ....markup import escape
from ....models import (
    FULL,
    Ability,
    Character,
    Covenant,
    Creature,
    Familiar,
    GrogYear,
    Laboratory,
    Neighbour,
    Player,
    Saga,
    ScoredTrait,
    Tribunal,
)
from ....rules import activities as season_rules
from ....rules import creation as creation_rules
from ....rules import creation_covenant as cov_creation
from ....rules import options as rule_options
from ....sections import (
    BESTIARY_INFO_SECTION,
    CONFLICT_BATTLES_SECTION,
    CONFLICTS_INFO_SECTION,
    CORE_SECTIONS,
    CREATURE_INFO_SECTION,
    FIGHTS_SECTION,
    NEIGHBOUR_INFO_SECTION,
    REGION_INFO_SECTION,
    SEASONS_INFO_SECTION,
    SIEGES_SECTION,
    TRIBUNAL_INFO_SECTION,
)
from ..creation_worksheet import CreationWorksheetScreen
from ..fields import (
    FieldsDialog,
)
from ..forms import (
    _grog_year_dialog,
    _saga_fields,
    _season_plan_dialog,
    saga_rule_options,
)
from ..help import HelpContext, HelpScreen, shown_keys
from ..prompts import (
    ConfirmScreen,
    MenuScreen,
    _scored_trait_dialog,
    terminal_fields,
)
from ..sheets import (
    LAB_TEXTS_SECTION,
    SPELL_SECTION,
    TAB_SECTIONS,
    BestiarySheetView,
    CharacterSheetView,
    ConflictsSheetView,
    CovenantSheetView,
    CreatureSheetView,
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
    NodeKind.BESTIARY: "bestiary",
    NodeKind.CREATURE: "creature",
    NodeKind.CONFLICTS: "conflicts",
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
        "create_creature",
        "roll_fair",
        "roll_table",
        "battle_event",
        "conflict_battle_event",
        "next_blow",
        "next_round",
        "add_combatant",
        "edit_combatant",
        "remove_combatant",
        "form_group",
        "break_group",
        "restart_fight",
        "next_siege_event",
        "found_covenant",
        "begin_story",
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
        "host_saga",
        "stop_hosting",
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
        "go_to",
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
    record: Covenant
    | Character
    | Laboratory
    | Familiar
    | Tribunal
    | Neighbour
    | Creature,
) -> tuple[list[str], Callable[[], None]]:
    """What deleting `record` would do, for the confirmation, and the
    function that does it."""
    if isinstance(record, Creature):
        return (
            creatures.deletion_consequences(saga, record),
            partial(creatures.delete, saga, record),
        )
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


def _section_named(view: Widget, section_id: str) -> Collapsible | None:
    """The section of `view` with id `section_id`, if it is built."""
    return next(view.query(f"#{section_id}").results(Collapsible), None)


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
    ) -> (
        Covenant
        | Character
        | Laboratory
        | Familiar
        | Tribunal
        | Neighbour
        | Creature
        | None
    ):
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
            Binding(
                str(number % 10), f"show_tab({number})", f"Tab {number}", show=False
            )
            for number in range(1, 11)
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
        NodeKind.BESTIARY: (set(), BESTIARY_INFO_SECTION),
        NodeKind.CREATURE: (set(), CREATURE_INFO_SECTION),
        NodeKind.CONFLICTS: (set(), CONFLICTS_INFO_SECTION),
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
        self.selected_creature: Creature | None = None
        self._character_sheet_view: CharacterSheetView | None = None
        self._laboratory_sheet_view: LaboratorySheetView | None = None
        self._covenant_sheet_view: CovenantSheetView | None = None
        self._familiar_sheet_view: FamiliarSheetView | None = None
        self._saga_content_view: SagaContentSheetView | None = None
        self._tribunal_sheet_view: TribunalSheetView | None = None
        self._region_sheet_view: RegionSheetView | None = None
        self._neighbour_sheet_view: NeighbourSheetView | None = None
        self._bestiary_view: BestiarySheetView | None = None
        self._creature_sheet_view: CreatureSheetView | None = None
        self._conflicts_view: ConflictsSheetView | None = None
        self._seasons_view: SeasonsSheetView | None = None
        #: One detail-pane swap at a time (see _set_detail).
        self._detail_lock = asyncio.Lock()
        #: While the Footer's keys are worked out (active_bindings), what
        #: _in_pass() has computed so far: every binding asks where focus
        #: is, and that answer is the same for all of them.
        self._pass: dict[str, Any] | None = None
        #: The section Help's Go there asked for, focused once its tab is
        #: shown (instead of the tab's first section).
        self._go_section: str | None = None

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
    #: Whether the saga file couldn't be read at the last tick (said once).
    _unreadable: bool = False

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
            NodeKind.CREATURE: ("creatures", self.selected_creature),
        }
        kind, record = records.get(self.selected_kind, ("", None))
        return f"{kind}:{record.id}" if record is not None else None

    async def _shared_tick(self) -> None:
        """Every few seconds: pick up another copy's save, and say who else
        has the open record."""
        try:
            changed = storage.reload_into(self.saga)
        except ValueError as problem:
            if not self._unreadable:
                self.notify(
                    f"Another copy's save couldn't be read: {escape(str(problem))}. "
                    "Your copy keeps its own data, and your next save replaces "
                    "the damaged file.",
                    severity="warning",
                    timeout=10,
                )
            self._unreadable = True
            changed = None
        else:
            self._unreadable = False
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
            NodeKind.CREATURE: (self.saga.creatures, self.selected_creature),
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
        self._add_bestiary(tree.root)
        tree.root.add_leaf(
            f"Conflicts ({len(self.saga.battles) + len(self.saga.fights) + len(self.saga.sieges)})",
            data=(NodeKind.CONFLICTS,),
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
        tree.root.add_leaf("Saga Content", data=(NodeKind.SAGA_CONTENT,))

    def _add_covenant_node(
        self, parent: TreeNode[Any], covenant: Covenant, *, expand: bool
    ) -> None:
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

    def _add_region(self, parent: TreeNode[Any]) -> None:
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

    def _add_bestiary(self, parent: TreeNode[Any]) -> None:
        """The Bestiary: every creature, by name."""
        listed = creatures.listed(self.saga)
        node = parent.add(
            f"Bestiary ({len(listed)})", data=(NodeKind.BESTIARY,), expand=False
        )
        for creature in listed:
            node.add_leaf(escape(creature.name), data=(NodeKind.CREATURE, creature.id))

    def _add_character_node(self, parent: TreeNode[Any], character: Character) -> None:
        """A character's own tree node: a plain leaf, unless it's a magus
        with a bound Familiar, in which case it becomes an expandable node
        with the Familiar as its one child leaf (nested under its creator,
        never its own group)."""
        label = f"{escape(character.name)} ({character.type}){_creating(character)}"
        familiar = (
            self.saga.familiar_of(character.id) if character.type == "magus" else None
        )
        if familiar is None:
            parent.add_leaf(label, data=(NodeKind.CHARACTER, character.id))
            return
        node = parent.add(label, data=(NodeKind.CHARACTER, character.id), expand=True)
        node.add_leaf(
            f"Familiar: {escape(familiar.name)}", data=(NodeKind.FAMILIAR, familiar.id)
        )

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

    async def _show_tribunal_detail(self, tribunal: Tribunal) -> None:
        view = TribunalSheetView(self.saga, tribunal)
        await self._set_detail(view)
        self._tribunal_sheet_view = view
        self._focus_first_section(initial=True)

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
        """1 to 9, and 0 for the tenth: open that tab of the sheet on show
        and move into it."""
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
        if not self._focus_go_section():
            self._focus_first_section(initial=initial)
        self.refresh_bindings()

    def go_to(self, place: str) -> bool:
        """Help's Go there: open `place` (a tab's or section's id, as the
        help names them) on the sheet on show, once Help has closed, and
        move into it; False when the sheet has no such place."""
        view = self._current_sheet_view()
        if view is None:
            return False
        if place in view.tab_ids:
            tab, section = place, None
        else:
            found = _section_named(view, place)
            if found is not None:
                pane = next(
                    (w for w in found.ancestors if isinstance(w, TabPane)), None
                )
                tab = pane.id if pane is not None else None
            else:
                # In a tab not built yet: the help says which tab it's on.
                topic = help_text.book(help_text.TUI).topics.get(place)
                if topic is None or topic.page not in view.tab_ids:
                    return False
                tab = topic.page
            section = place
        self.call_after_refresh(self._go_there, tab, section)
        return True

    def _go_there(self, tab: str | None, section: str | None) -> None:
        view = self._current_sheet_view()
        if view is None:
            return
        self._go_section = section
        tabbed = view.query_one(TabbedContent)
        if tab is not None and tabbed.active != tab:
            tabbed.active = tab  # TabActivated focuses the section
        elif not self._focus_go_section():
            self._focus_first_section()

    def _focus_go_section(self) -> bool:
        """Focus the section Go there asked for, if there is one and the
        sheet has it."""
        section_id, self._go_section = self._go_section, None
        view = self._current_sheet_view()
        if section_id is None or view is None:
            return False
        found = _section_named(view, section_id)
        if found is None:
            return False
        section_stop(found).focus()
        return True

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
            NodeKind.CREATURE: self.selected_creature,
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
            NodeKind.BESTIARY: "The Bestiary",
            NodeKind.CONFLICTS: "Conflicts",
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
        return HelpContext(ids, where, keys, self.go_to)

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
            for widget in widgets:
                if isinstance(widget, SheetView):
                    widget.show_secrets = self._is_storyguide()
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
            NodeKind.BESTIARY: self._bestiary_view,
            NodeKind.CREATURE: self._creature_sheet_view,
            NodeKind.CONFLICTS: self._conflicts_view,
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

    # -- deleting a covenant, character, laboratory or Familiar --

    def _record_to_delete(
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
    ):
        """The record d deletes: the covenant, character, laboratory or
        Familiar selected in the tree, if that's what's selected."""
        return {
            NodeKind.COVENANT: self.selected_covenant,
            NodeKind.CHARACTER: self.selected_character,
            NodeKind.LABORATORY: self.selected_laboratory,
            NodeKind.FAMILIAR: self.selected_familiar,
            NodeKind.TRIBUNAL: self.selected_tribunal,
            NodeKind.NEIGHBOUR: self.selected_neighbour,
            NodeKind.CREATURE: self.selected_creature,
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
            # Conflicts' count in the tree.
            CONFLICT_BATTLES_SECTION,
            FIGHTS_SECTION,
            SIEGES_SECTION,
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
            NodeKind.CREATURE: self.selected_creature,
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
            FieldsDialog("Edit Saga", terminal_fields(_saga_fields(self.saga))),
            handle_result,
        )

    # -- season plans (shared by the character and covenant sheets) --

    def _plan_season_for(
        self,
        character: Character,
        section: str,
        when: tuple[str, int] | None = None,
    ) -> None:
        """Plan `character`'s season `when` (the current one by default), or
        change its plan, then refresh `section`."""
        if not season_rules.is_planned(character):
            self._grog_year_for(character, section)
            return
        when = when or (self.saga.current_season, self.saga.current_year)
        existing = seasons.plan_for(self.saga, character, *when)

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                season_forms.save_season(self.saga, character, values, existing, when)
                self._commit(section)

        self.app.push_screen(
            _season_plan_dialog(self.saga, character, existing, when),
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

    def _clear_season_plan_for(
        self,
        character: Character,
        section: str,
        when: tuple[str, int] | None = None,
    ) -> None:
        """Drop `character`'s plan for season `when` (the current one by
        default; after confirming), then refresh `section`."""
        run_steps(
            self.app,
            season_forms.clear_season(self.saga, character, when),
            lambda _end: self._commit(section),
            notify=lambda _title, why: self.notify(why),
        )

    @staticmethod
    def _ability_label(a: Ability) -> str:
        specialty = f" ({escape(a.specialty)})" if a.specialty else ""
        return f"{escape(a.name)}{specialty} {st.score_text(a.progress)}"

    def _device_action_enabled(self, action: str) -> bool:
        """Whether More's Instill / Use a Charge can act on the chosen device row (see
        DeviceActions)."""
        return False

    def _shared_section_ops(self) -> dict[str, _SectionOps]:
        """a / d / e on the sections several sheets share: scored traits
        and the core sections (see
        WorkspaceScreen._section_ops)."""
        ops: dict[str, _SectionOps] = {}
        for spec in (
            _CHARACTER_TRAITS,
            _CHARACTER_REPUTATIONS,
            _FAMILIAR_TRAITS,
            _FAMILIAR_REPUTATIONS,
            _COVENANT_REPUTATIONS,
        ):
            ops[spec.section] = _SectionOps(
                partial(self._add_trait, spec),
                partial(self._remove_trait, spec),
                partial(self._edit_trait, spec),
            )
        for section, verbs in CORE_SECTIONS.items():
            ops[section] = _SectionOps(
                *(
                    partial(self._core_verb, section, verb) if verb in verbs else None
                    for verb in ("add", "remove", "edit")
                )
            )
        return ops

    @cached_property
    def _section_ops(self) -> dict[str, _SectionOps]:
        """Per section id, its a / d / e handlers (see WorkspaceScreen)."""
        raise NotImplementedError
