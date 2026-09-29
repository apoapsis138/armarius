"""The workspace's shared tables and its base class: the screen's state, the
navigation tree, the detail pane, focus and section tracking, the plumbing
behind a/A/e/r and the actions that aren't about one kind of record."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from enum import StrEnum
from functools import cached_property, partial
from typing import Any, ClassVar, NamedTuple

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.events import DescendantBlur, DescendantFocus
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    Collapsible,
    Header,
    Static,
    TabbedContent,
    TabPane,
    Tree,
)
from textual.widgets.tree import TreeNode

from ... import books as bk
from ... import catalog, creation, deletion, sourcebooks, storage
from ... import economics as eco
from ... import familiars as fam
from ... import laboratories as lab_rules
from ... import sheet_text as st
from ... import spells as spl
from ...markup import escape
from ...models import (
    FOCUS_FLAWS,
    SEASONS,
    Ability,
    Character,
    Covenant,
    Familiar,
    Laboratory,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
    link_unlinked_features,
    new_instance_id,
    next_season,
)
from ..fields import (
    FieldsDialog,
)
from ..forms import (
    _character_create_fields,
    _covenant_create_fields,
    _familiar_create_fields,
    _laboratory_create_fields,
    _saga_fields,
)
from ..pickers import (
    LabVirtueFlawPickerScreen,
    RemovalPickerScreen,
    VirtueFlawPickerScreen,
)
from ..prompts import (
    AdvanceSeasonScreen,
    ConfirmScreen,
    _date_fields,
    _scored_trait_dialog,
)
from ..sheets import (
    _LIBRARY_SECTIONS,
    DEVICE_SECTIONS,
    LAB_FEATURE_SECTIONS,
    LAB_VF_SECTIONS,
    SPELL_SECTION,
    BookListView,
    CharacterSheetView,
    CovenantSheetView,
    FamiliarSheetView,
    LaboratorySheetView,
    SheetView,
    SpellListView,
)
from ..widgets import BottomBar

#: Covenant Reputations run from -3 to +3.
_COVENANT_REPUTATION_RANGE = (-3, 3)


class _SectionOps(NamedTuple):
    """What the a / A / e / r keys do in one sheet section (None: nothing,
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
    BOOK_GROUP = "book_group"


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


class WorkspaceBase(Screen[None]):
    """The workspace's state and everything its actions share: the navigation
    tree and detail pane, which section is active, saving and refreshing
    (_commit), and the a/A/e/r plumbing. The per-record actions live in the
    mixins WorkspaceScreen combines."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("n", "create_covenant", "New Covenant"),
        ("c", "create_character", "New Character"),
        ("l", "create_laboratory", "New Laboratory"),
        ("f", "create_familiar", "Bind Familiar"),
        ("ctrl+d", "delete_record", "Delete"),
        ("a", "add", "Add"),
        ("A", "remove", "Remove"),
        ("e", "edit", "Edit"),
        ("r", "restore", "Restore"),
        ("i", "improve", "Improve"),
        ("i", "instill_effect", "Instill"),
        ("u", "use_charge", "Charge"),
        ("I", "import_data", "Import"),
        ("t", "advance_season", "Advance Season"),
        # Works everywhere, but left out of the footer to keep it short.
        Binding("T", "set_date", "Set Date", show=False),
        ("v", "add_virtue_flaw", "Add Virtue/Flaw"),
        ("V", "remove_virtue_flaw", "Remove Virtue/Flaw"),
        ("escape", "app.pop_screen", "Back"),
        ("q", "quit", "Quit"),
    ]

    #: Covenant tabs that own their own a/A/e dispatch (keyed by tab id):
    #: the Diary, a flat pane with no sections. On any other tab, with
    #: nothing focused in a section, the dispatch falls back to the
    #: always-visible info panel. See _active_section().
    _COVENANT_DISPATCH_TABS: ClassVar[set[str]] = {"tab-cov-diary"}

    #: Character tabs that own their own a/A/e dispatch (keyed by tab id),
    #: same idea as _COVENANT_DISPATCH_TABS -- "tab-abilities" is a flat
    #: pane with no sub-sections, so it dispatches on its own tab id rather
    #: than falling back to the top panel. See _active_section().
    _CHARACTER_DISPATCH_TABS: ClassVar[set[str]] = {"tab-abilities"}

    #: Familiar tabs that own their own a/A/e dispatch (keyed by tab id),
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

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="workspace-body"):
            yield Tree(escape(self.saga.name), data=(NodeKind.SAGA,), id=NAV_TREE_ID)
            yield VerticalScroll(id=DETAIL_PANE_ID)
        yield BottomBar()

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
                escape(covenant.name),
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
                lab_group.add_leaf(escape(lab.name), data=(NodeKind.LABORATORY, lab.id))

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
                group.add_leaf(escape(lab.name), data=(NodeKind.LABORATORY, lab.id))
        # Books with no owner file under the saga.
        loose_books = bk.unassigned_books(self.saga)
        if loose_books:
            tree.root.add_leaf(
                f"Unassigned Books ({len(loose_books)})", data=(NodeKind.BOOK_GROUP,)
            )
        tree.root.add_leaf(self._spells_label(), data=(NodeKind.SPELLS,))

    def _add_character_node(self, parent, character: Character) -> None:
        """A character's own tree node: a plain leaf, unless it's a magus
        with a bound Familiar, in which case it becomes an expandable node
        with the Familiar as its one child leaf (nested under its creator,
        never its own group -- see kanban STORY-206)."""
        label = f"{escape(character.name)} ({character.type})"
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
                "Select a character from the tree, or press 'c' to add one."
                if covenant
                else "These characters aren't assigned to a covenant. Select one "
                "from the tree, or press 'c' to add one.",
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
                "Select a laboratory from the tree, or press 'l' to add one."
                if covenant
                else "These laboratories aren't assigned to a covenant. Select "
                "one from the tree, or press 'l' to add one.",
            )
        elif kind == NodeKind.LABORATORY:
            lab = next(lab for lab in self.saga.laboratories if lab.id == data[1])
            self.selected_laboratory = lab
            self.selected_covenant = self.saga.covenant(lab.covenant_id)
            await self._show_laboratory_detail(lab)
        elif kind == NodeKind.SPELLS:
            self.selected_covenant = None
            await self._set_detail(SpellListView(self.saga))
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

        self.refresh_bindings()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if (
            action in _CREATE_PLACES
            and self.selected_kind not in _CREATE_PLACES[action]
        ):
            return False
        if action == "edit" and self.selected_kind == NodeKind.SAGA:
            return True
        if action in ("add", "remove", "edit", "restore"):
            return self._section_op(action) is not None
        if action == "improve":
            return self._active_section() == "section-eco-income"
        if action in ("instill_effect", "use_charge"):
            return (
                self._active_section() in DEVICE_SECTIONS
                and self._device_action_enabled(action)
            )
        if action == "import_data":
            return (
                self.selected_kind == NodeKind.SAGA
                or self._active_section() in _LIBRARY_SECTIONS
            )
        if action in ("add_virtue_flaw", "remove_virtue_flaw"):
            if self.selected_kind == NodeKind.LABORATORY:
                return self._active_section() in LAB_VF_SECTIONS
            if self.selected_kind == NodeKind.FAMILIAR:
                return self._active_section() in (
                    "section-fam-vf-virtues",
                    "section-fam-vf-flaws",
                )
            return self._active_section() in ("section-vf-virtues", "section-vf-flaws")
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

    def _active_section(self) -> str | None:
        """Which sheet section is "active" for a/A/e (and v/V) dispatch: the
        nearest Collapsible around whatever has focus -- which also covers a
        sheet's top panel, outside its tabs. With none, a flat tab that
        dispatches on its own id (see _SHEET_DISPATCH), otherwise the sheet's
        always-visible top section, so 'e' edits the record from any tab.
        The Unassigned Books and Spells nodes have no sheet, just a section."""
        if self.selected_kind == NodeKind.BOOK_GROUP:
            return "section-unassigned-books"
        if self.selected_kind == NodeKind.SPELLS:
            return SPELL_SECTION
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
        # tab's first section focus so 'e'/'a'/'A' work immediately without
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
        """Give the sheet a focused section, so 'e'/'a'/'A' work straight away.

        When a sheet is first shown (`initial`), focus its first section
        anywhere -- the always-visible top panel. On a later tab switch, focus
        that tab's first section, or clear focus for a flat tab: the top
        panel lives outside the tabs, so a tab switch never blurs it, and
        leaving it focused would make _active_section() keep reporting it.

        The Laboratory is the exception on first showing: its default tab
        (Planning) is flat, so it looks at the active tab first and only then
        falls back to the top panel."""
        view = self._current_sheet_view()
        if view is None:
            return
        active_tab_first = self.selected_kind == NodeKind.LABORATORY
        try:
            if initial and not active_tab_first:
                collapsible = view.query(Collapsible).first()
            else:
                tabbed = view.query_one(TabbedContent)
                if not tabbed.active:
                    return
                pane = view.query_one(f"#{tabbed.active}", TabPane)
                collapsible = pane.query(Collapsible).first()
        except NoMatches:
            if not initial:
                self.screen.set_focus(None)
                return
            if not active_tab_first:
                return
            try:
                collapsible = view.query(Collapsible).first()
            except NoMatches:
                return
        collapsible.query_one("CollapsibleTitle").focus()

    def on_descendant_focus(self, event: DescendantFocus) -> None:
        # Focus can move between Collapsible sections within the same tab
        # (no TabActivated message for that) -- keep bindings in sync then
        # too, or the Footer hint and check_action gating go stale.
        self.refresh_bindings()

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
        """Edit the chosen entry; with none chosen, ask which."""
        traits = self._traits(spec)
        if traits is None:
            return
        self._chosen_or_pick(
            getattr(self, spec.selected)(),
            [label for _, label in st.trait_rows(traits)],
            title=f"Edit which {spec.noun}?",
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
        """Delete the chosen entry, after confirming; with none chosen, ask
        which one first."""
        traits = self._traits(spec)
        if traits is None:
            return

        def remove(index: int) -> None:
            self._confirm_delete(traits, index, traits[index].name, spec.section)

        self._chosen_or_pick(
            getattr(self, spec.selected)(),
            [label for _, label in st.trait_rows(traits)],
            title=f"Remove a {spec.noun}",
            empty=f"No {spec.noun}s to remove.",
            then=remove,
        )

    def _chosen_or_pick(
        self,
        selected: int | None,
        labels: Sequence[str],
        *,
        title: str,
        empty: str,
        then: Callable[[int], object],
    ) -> None:
        """Act on a list entry by index: the chosen row's if there is one
        (`selected`), else the one picked from `labels` in a picker titled
        `title` -- or, with no entries at all, just say `empty`."""
        if selected is not None and selected < len(labels):
            then(selected)
            return
        if not labels:
            self.notify(empty)
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                then(index)

        self.app.push_screen(RemovalPickerScreen(title, list(labels)), handle_index)

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
                    self.saga, values["name"], values["size"], values["covenant_id"]
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
        """The record ctrl+d deletes: the covenant, character or laboratory
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

    # -- Saga --

    def _edit_saga(self) -> None:
        async def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
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
            new_year = saga.current_season == SEASONS[-1]
            # A new year (Winter -> Spring): each covenant's surplus goes into
            # its Wealth before the date moves on.
            added = eco.close_all_years(saga) if new_year else []
            await self._apply_saga_date(
                *next_season(saga.current_season, saga.current_year)
            )
            message = f"It is now {saga.current_season} {saga.current_year}."
            if added:
                message += " Added to Wealth: " + ", ".join(
                    f"{name} {amount}" for name, amount in added
                )
                message += "."
                self._refresh_covenant_section("section-eco-wealth")
            self.notify(escape(message))

        self.app.push_screen(
            AdvanceSeasonScreen(saga.current_season, saga.current_year),
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
        is_lab = self.selected_kind == NodeKind.LABORATORY
        is_familiar = self.selected_kind == NodeKind.FAMILIAR

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
        # Opened on the side of the section it was launched from.
        flaws = self._active_section() in ("section-vf-flaws", "section-fam-vf-flaws")
        chooser = (
            catalog.VirtueFlawChooser.for_familiar(target, books)
            if isinstance(target, Familiar)
            else catalog.VirtueFlawChooser.for_character(target, books)
        )
        self.app.push_screen(
            VirtueFlawPickerScreen(
                target.virtues_flaws,
                side="Flaw" if flaws else "Virtue",
                chooser=chooser,
            ),
            handle_result,
        )

    def action_remove_virtue_flaw(self) -> None:
        """Delete a Virtue/Flaw of the character, laboratory or familiar on
        show, after confirming: the row chosen in its Virtues or Flaws list,
        or (with none chosen) the one picked from all of them."""
        target = self._virtue_flaw_target()
        if target is None:
            return
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

        selected = self._selected_virtue_flaw(target)
        if selected is not None:
            confirm(selected)
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                confirm(index)

        labels = [
            escape(catalog.describe_virtue_flaw(vf, vf_catalog))
            for vf in target.virtues_flaws
        ]
        self.app.push_screen(
            RemovalPickerScreen("Remove a Virtue or Flaw", labels), handle_index
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
        """Whether i / u can act on the chosen device row (see
        DeviceActions)."""
        return False

    @cached_property
    def _section_ops(self) -> dict[str, _SectionOps]:
        """Per section id, its a/A/e/r handlers (see WorkspaceScreen)."""
        raise NotImplementedError
