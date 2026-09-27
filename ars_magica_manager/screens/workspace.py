"""The workspace: the saga's navigation tree beside the detail pane, and every
action on the records shown there."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from enum import StrEnum
from functools import cached_property, partial
from pathlib import Path
from typing import Any, ClassVar, NamedTuple

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.events import DescendantBlur, DescendantFocus
from textual.screen import ModalScreen, Screen
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
from textual.widgets.tree import TreeNode

from .. import books as bk
from .. import catalog, creation, storage
from .. import economics as eco
from .. import familiars as fam
from .. import inhabitants as inh
from .. import possessions as pos
from .. import sheet_text as st
from .. import spells as spl
from ..markup import escape
from ..models import (
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    INCOME_TYPE_DEFAULTS,
    INCOME_TYPES,
    INHABITANT_KINDS,
    LOYALTY_EQUIPMENT,
    LOYALTY_MONEY,
    POSSESSION_KINDS,
    SEASONS,
    Ability,
    Aging,
    ArtScore,
    Background,
    BondPower,
    Book,
    Character,
    Covenant,
    Description,
    DiaryEntry,
    Familiar,
    HermeticBackground,
    IncomeSource,
    KnownSpell,
    LabCharacteristics,
    Laboratory,
    NamedDescription,
    Possession,
    Saga,
    ScoredTrait,
    Spell,
    VirtueFlawInstance,
    Wounds,
    add_raw_vis,
    assign_laboratory,
    assign_laboratory_owner,
    boon_hook_params,
    known_fields,
    next_season,
    replace_raw_vis,
)
from .fields import (
    _EMPHASIS_HINT,
    DialogField,
    FieldsDialog,
    _description_field,
    _pairs,
)
from .forms import (
    DuplicateBookScreen,
    EditArtsScreen,
    EditFamiliarBindingScreen,
    ImportScreen,
    ImproveIncomeScreen,
    MasteryEditScreen,
    SpellImportHelperScreen,
    _aging_fields,
    _biographical_fields,
    _bond_power_fields,
    _book_fields,
    _book_from_values,
    _book_live,
    _character_create_fields,
    _character_info_fields,
    _characteristics_fields,
    _characteristics_from,
    _covenant_create_fields,
    _covenant_fields,
    _familiar_characteristics_fields,
    _familiar_create_fields,
    _familiar_info_fields,
    _fatigue_fields,
    _hermetic_fields,
    _inhabitant_fields,
    _lab_characteristics_fields,
    _lab_identity_fields,
    _laboratory_create_fields,
    _possession_fields,
    _saga_fields,
    _spell_fields,
    _spell_from_values,
    _spell_live,
    _spell_problem,
    _wounds_fields,
)
from .pickers import (
    AbilityPickerScreen,
    CovenantBoonHookPickerScreen,
    CsvFilePickerScreen,
    LabVirtueFlawPickerScreen,
    RemovalPickerScreen,
    SpellChooserScreen,
    VirtueFlawPickerScreen,
)
from .prompts import (
    AdvanceSeasonScreen,
    ConfirmScreen,
    _ability_fields,
    _ability_from,
    _boon_hook_fields,
    _date_fields,
    _diary_entry_dialog,
    _item_dialog,
    _named_description_dialog,
    _raw_vis_dialog,
    _scored_trait_dialog,
)
from .sheets import (
    _LIBRARY_SECTIONS,
    BOOK_SECTIONS,
    SPELL_SECTION,
    BookListView,
    CharacterSheetView,
    CovenantSheetView,
    FamiliarSheetView,
    LaboratorySheetView,
    SheetView,
    SpellListView,
)
from .widgets import BottomBar

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
    signed: bool = True  # scores shown as "+2" (not "2") in the picker
    confirm_remove: bool = True
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
    signed=False,  # unlike every other Reputation list (STORY-1109 B14)
)


_FAMILIAR_TRAITS = _TraitList(
    "selected_familiar",
    "personality_traits",
    "section-fam-personality-traits",
    "Personality Trait",
    "e.g. Loyal",
    "_selected_familiar_personality_trait",
    confirm_remove=False,  # STORY-1109 B6
)


_FAMILIAR_REPUTATIONS = _TraitList(
    "selected_familiar",
    "reputations",
    "section-fam-reputations",
    "Reputation",
    "e.g. Fierce Protector",
    "_selected_familiar_reputation",
    signed=False,
    confirm_remove=False,  # STORY-1109 B6
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


class WorkspaceScreen(Screen[None]):
    """Persistent nav tree (left) + detail pane (right) for one open saga.

    Replaces the old Saga -> Covenant -> Character/Lab/Library drill-down
    screens with a single workspace: the whole saga's structure is always
    visible in the tree, and selecting any node swaps the detail pane on
    the right, so comparing siblings doesn't mean popping all the way back
    up and down again.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        ("n", "create_covenant", "New Covenant"),
        ("c", "create_character", "New Character"),
        ("l", "create_laboratory", "New Laboratory"),
        ("f", "create_familiar", "Bind Familiar"),
        ("a", "add", "Add"),
        ("A", "remove", "Remove"),
        ("e", "edit", "Edit"),
        ("r", "restore", "Restore"),
        ("i", "improve", "Improve"),
        ("I", "import_data", "Import"),
        ("t", "advance_season", "Advance Season"),
        ("T", "set_date", "Set Date"),
        ("v", "add_virtue_flaw", "Add Virtue/Flaw"),
        ("V", "remove_virtue_flaw", "Remove Virtue/Flaw"),
        ("escape", "app.pop_screen", "Back"),
        ("q", "quit", "Quit"),
    ]

    #: Covenant tabs that own their own a/A/e dispatch (keyed by tab id).
    #: None: every covenant tab's content is in Collapsible sections, so with
    #: nothing focused in one the dispatch falls back to the always-visible
    #: info panel. See _active_section().
    _COVENANT_DISPATCH_TABS: ClassVar[set[str]] = set()

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
        if action == "create_covenant":
            return self.selected_kind == NodeKind.SAGA
        # Characters and labs may be created anywhere: a selected covenant
        # is just the default for the dialog's optional Covenant field.
        if action == "edit" and self.selected_kind == NodeKind.SAGA:
            return True
        if action in ("add", "remove", "edit", "restore"):
            return self._section_op(action) is not None
        if action == "improve":
            return self._active_section() == "section-eco-income"
        if action == "import_data":
            return (
                self.selected_kind == NodeKind.SAGA
                or self._active_section() in _LIBRARY_SECTIONS
            )
        if action in ("add_virtue_flaw", "remove_virtue_flaw"):
            if self.selected_kind == NodeKind.LABORATORY:
                return self._active_section() == "tab-lab-vf"
            if self.selected_kind == NodeKind.FAMILIAR:
                return self._active_section() in (
                    "section-fam-vf-virtues",
                    "section-fam-vf-flaws",
                )
            return self._active_section() in ("section-vf-virtues", "section-vf-flaws")
        if action == "create_familiar":
            return bool(fam.unbonded_magi(self.saga))
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """The sheets' Edit buttons."""
        handler = {
            "btn-lab-identity-edit": self._edit_lab_identity,
            "btn-lab-characteristics-edit": self._edit_lab_characteristics,
            "btn-cov-edit": self._edit_covenant,
            "btn-char-info-edit": self._edit_character_info,
            "btn-char-characteristics-edit": self._edit_characteristics,
            "btn-char-health-wounds-edit": self._edit_wounds,
            "btn-char-health-fatigue-edit": self._edit_fatigue,
            "btn-fam-info-edit": self._edit_familiar_info,
            "btn-fam-health-wounds-edit": self._edit_familiar_wounds,
            "btn-fam-health-fatigue-edit": self._edit_familiar_fatigue,
        }.get(event.button.id or "")
        if handler is not None:
            event.stop()
            handler()

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
            [label for _, label in st.trait_rows(traits, signed=spec.signed)],
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
        """Delete the chosen entry (asking first, unless `spec` says not to);
        with none chosen, ask which one."""
        traits = self._traits(spec)
        if traits is None:
            return

        def remove(index: int) -> None:
            if spec.confirm_remove:
                self._confirm_delete(traits, index, traits[index].name, spec.section)
            else:
                del traits[index]
                self._commit(spec.section)

        self._chosen_or_pick(
            getattr(self, spec.selected)(),
            [label for _, label in st.trait_rows(traits, signed=spec.signed)],
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
        character = self.selected_character
        default_magus_id = (
            character.id
            if character is not None
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

    # -- generic Add/Remove/Edit dispatch, by the active section of any sheet --

    @cached_property
    def _section_ops(self) -> dict[str, _SectionOps]:
        """What a/A/e/r do in each sheet section, keyed by the section id
        _active_section() reports. check_action enables a key only where it
        has an entry here, so a binding and its action can't disagree. Built
        once: check_action runs on every Footer refresh."""
        ops: dict[str, _SectionOps] = {
            SPELL_SECTION: _SectionOps(
                lambda: self._spell_form(None),
                self._remove_saga_spell,
                self._edit_saga_spell,
            ),
            # Character sheet
            "section-char-info": _SectionOps(edit=self._edit_character_info),
            "section-char-characteristics": _SectionOps(
                edit=self._edit_characteristics
            ),
            "section-char-biographical": _SectionOps(
                edit=self._edit_biographical_detail
            ),
            "tab-abilities": _SectionOps(
                self._add_ability, self._remove_ability, self._edit_ability
            ),
            "section-aging": _SectionOps(edit=self._edit_aging),
            # Health has two dialogs behind two Edit buttons (Wounds and
            # Fatigue); 'e' opens Wounds, Fatigue is button-only.
            "section-char-health": _SectionOps(edit=self._edit_wounds),
            "section-arts": _SectionOps(edit=self._edit_arts),
            "section-hermetic-background": _SectionOps(
                edit=self._edit_hermetic_background
            ),
            "section-known-spells": _SectionOps(
                self._add_spell, self._remove_spell, self._edit_spell_mastery
            ),
            "section-inventory": _SectionOps(
                self._add_item, self._remove_item, self._edit_item
            ),
            "section-raw-vis-hermetic": _SectionOps(
                self._add_raw_vis, self._remove_raw_vis, self._edit_raw_vis
            ),
            "section-raw-vis-inventory": _SectionOps(
                self._add_raw_vis, self._remove_raw_vis, self._edit_raw_vis
            ),
            # Familiar sheet
            "section-fam-info": _SectionOps(edit=self._edit_familiar_info),
            "section-fam-binding": _SectionOps(edit=self._edit_familiar_binding),
            "section-fam-characteristics": _SectionOps(
                edit=self._edit_familiar_characteristics
            ),
            "section-fam-health": _SectionOps(edit=self._edit_familiar_wounds),
            "section-fam-natural-weapons": _SectionOps(
                self._add_familiar_natural_weapon,
                self._remove_familiar_natural_weapon,
                self._edit_familiar_natural_weapon,
            ),
            "tab-fam-abilities": _SectionOps(
                self._add_familiar_ability,
                self._remove_familiar_ability,
                self._edit_familiar_ability,
            ),
            "tab-fam-powers": _SectionOps(
                self._add_familiar_bond_power,
                self._remove_familiar_bond_power,
                self._edit_familiar_bond_power,
            ),
            # Laboratory sheet
            "section-lab-identity": _SectionOps(edit=self._edit_lab_identity),
            "section-lab-characteristics": _SectionOps(
                edit=self._edit_lab_characteristics
            ),
            "section-lab-specialties": _SectionOps(
                self._add_specialty, self._remove_specialty, self._edit_specialty
            ),
            "section-lab-features": _SectionOps(
                self._add_feature, self._remove_feature, self._edit_feature
            ),
            "section-lab-rooms": _SectionOps(
                self._add_room, self._remove_room, self._edit_room
            ),
            "section-lab-raw-vis": _SectionOps(
                self._add_lab_raw_vis, self._remove_lab_raw_vis, self._edit_lab_raw_vis
            ),
            "section-lab-items": _SectionOps(
                self._add_inventory_item,
                self._remove_inventory_item,
                self._edit_inventory_item,
            ),
            "tab-lab-diary": _SectionOps(
                self._add_diary_entry, self._remove_diary_entry, self._edit_diary_entry
            ),
            # Covenant sheet
            "section-cov-info": _SectionOps(edit=self._edit_covenant),
            "section-cov-description": _SectionOps(
                edit=self._edit_covenant_description
            ),
            "section-cov-boons": _SectionOps(
                lambda: self._add_boon_hook("Boon"),
                lambda: self._remove_boon_hook("Boon"),
                lambda: self._edit_boon_hook("Boon"),
            ),
            "section-cov-hooks": _SectionOps(
                lambda: self._add_boon_hook("Hook"),
                lambda: self._remove_boon_hook("Hook"),
                lambda: self._edit_boon_hook("Hook"),
            ),
            "section-eco-wealth": _SectionOps(edit=self._edit_wealth),
            "section-eco-income": _SectionOps(
                self._add_income_source,
                self._remove_income_source,
                self._edit_income_source,
            ),
            "section-eco-expenditure": _SectionOps(
                edit=lambda: self._edit_economics_row("expenditure")
            ),
            "section-eco-savings": _SectionOps(
                edit=lambda: self._edit_economics_row("savings")
            ),
            "section-inh-loyalty": _SectionOps(edit=self._edit_loyalty),
            "section-inh-population": _SectionOps(edit=self._edit_population),
            "section-inh-misc": _SectionOps(edit=self._edit_miscellaneous),
        }
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
        for section in BOOK_SECTIONS:
            listed = section != "section-lib-summary"  # the summary lists none
            ops[section] = _SectionOps(
                lambda: self._book_form(None),
                self._remove_book if listed else None,
                self._edit_book if listed else None,
            )
        for kind in INHABITANT_KINDS:
            ops[f"section-inh-{kind}"] = _SectionOps(
                partial(self._add_inhabitant, kind),
                partial(self._remove_inhabitant, kind),
                partial(self._edit_inhabitant, kind),
                # Only Magi/Companions can go "departed" (Inhabitant.departed).
                partial(self._restore_inhabitant, kind)
                if kind in inh.AUTO_KINDS
                else None,
            )
        for kind in POSSESSION_KINDS:
            ops[f"section-pos-{kind}"] = _SectionOps(
                partial(self._add_possession, kind),
                partial(self._remove_possession, kind),
                partial(self._edit_possession, kind),
            )
        return ops

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

    # -- Spells (the saga's Spells view) --

    def _spells_label(self) -> str:
        return f"Spells ({len(spl.all_spells(self.saga))})"

    def _spell_view(self) -> SpellListView | None:
        try:
            return self._detail_pane().query(SpellListView).first()
        except NoMatches:
            return None

    def _spells_changed(self) -> None:
        view = self._spell_view()
        if view is not None:
            view.refilter()
        node = _tree_node_with_data(self._nav_tree(), (NodeKind.SPELLS,))
        if node is not None:
            node.set_label(self._spells_label())

    def _chosen_own_spell(self, verb: str) -> Spell | None:
        """The chosen spell if it's one of the saga's own; otherwise say why
        not (nothing chosen, or a read-only catalog spell)."""
        view = self._spell_view()
        spell = view.selected_spell() if view is not None else None
        if spell is None:
            self.notify(f"Choose a spell to {verb} first.")
            return None
        if not spl.is_own(self.saga, spell):
            self.notify(
                f"{escape(spell.name)} is a catalog spell, so it's read-only. To "
                "make your own version, add a spell with a."
            )
            return None
        return spell

    def _edit_saga_spell(self) -> None:
        spell = self._chosen_own_spell("edit")
        if spell is not None:
            self._spell_form(spell)

    def _spell_form(self, spell: Spell | None) -> None:
        saga = self.saga
        title = "Add a Spell" if spell is None else f"Edit {escape(spell.name)}"

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            target = spell
            if target is None:
                target = spl.add_own_spell(
                    saga, values["name"], values["technique"], values["form"]
                )
            _spell_from_values(target, values)
            storage.save_saga(saga)
            self._spells_changed()

        self.app.push_screen(
            FieldsDialog(
                title,
                _spell_fields(spell),
                validate=_spell_problem,
                live=_spell_live,
            ),
            handle_result,
        )

    def _remove_saga_spell(self) -> None:
        spell = self._chosen_own_spell("delete")
        if spell is None:
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and spell in self.saga.spells:
                self.saga.spells.remove(spell)
                storage.save_saga(self.saga)
                self._spells_changed()

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(spell.name)}?"), handle_confirmed
        )

    # -- Books (Library tab, laboratory/character Books, Unassigned Books) --

    def _book_view(self) -> BookListView | None:
        """The book list showing in the detail pane, if any (a sheet shows at
        most one)."""
        try:
            return self._detail_pane().query(BookListView).first()
        except NoMatches:
            return None

    def _default_book_owner(self) -> str:
        """Owner a new book starts with: wherever it's being added from."""
        if self.selected_kind == NodeKind.CHARACTER and self.selected_character:
            return bk.owner_value("character", self.selected_character.id)
        if self.selected_kind == NodeKind.LABORATORY and self.selected_laboratory:
            return bk.owner_value("laboratory", self.selected_laboratory.id)
        if self.selected_kind == NodeKind.COVENANT and self.selected_covenant:
            return bk.owner_value("covenant", self.selected_covenant.id)
        return ""

    def _pick_book(self, title: str, then: Callable[[Book], None]) -> None:
        """Act on the chosen book; with none chosen, ask which one."""
        view = self._book_view()
        if view is None:
            return
        chosen = view.selected_book()
        if chosen is not None:
            then(chosen)
            return
        listed = list(view.books)
        if not listed:
            self.notify("No books here yet.")
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                then(listed[index])

        self.app.push_screen(
            RemovalPickerScreen(
                title, [escape(b.name) or "(untitled)" for b in listed]
            ),
            handle_index,
        )

    def _marked_books(self) -> list[Book]:
        view = self._book_view()
        return view.checked_books() if view is not None else []

    def _edit_book(self) -> None:
        """Edit the chosen book; with books marked, change their owner."""
        marked = self._marked_books()
        if marked:
            self._change_owner_of(marked)
            return
        self._pick_book("Edit which book?", self._book_form)

    def _change_owner_of(self, books: list[Book]) -> None:
        """Give several books one new owner (the only edit that makes sense
        for many at once), confirming first."""
        saga = self.saga
        count = len(books)
        plural = "s" if count != 1 else ""
        owners = {bk.owner_value(b.owner_kind, b.owner_id) for b in books}
        current = owners.pop() if len(owners) == 1 else None
        if current is not None and bk.is_unassigned(saga, books[0]):
            current = ""

        def handle_owner(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            owner = values["owner"]
            label = next(lbl for lbl, value in bk.owner_options(saga) if value == owner)

            def handle_confirmed(confirmed: bool | None) -> None:
                if not confirmed:
                    return
                kind, owner_id = bk.parse_owner_value(owner)
                for book in books:
                    book.owner_kind, book.owner_id = kind, owner_id
                storage.save_saga(saga)
                self._books_changed()

            self.app.push_screen(
                ConfirmScreen(
                    f"Changing ownership of {count} book{plural} to "
                    f"[b]{escape(label)}[/]. Continue?",
                    yes_label="Change",
                    yes_variant="success",
                ),
                handle_confirmed,
            )

        self.app.push_screen(
            FieldsDialog(
                f"Change the owner of {count} book{plural}",
                [
                    DialogField(
                        "_books",
                        "Books",
                        "info",
                        ", ".join(b.name or "(untitled)" for b in books),
                    ),
                    DialogField(
                        "owner",
                        "New owner",
                        "select",
                        current,
                        options=bk.owner_options(saga),
                        required=True,
                        allow_blank=True,
                        placeholder="(choose the new owner)",
                    ),
                ],
            ),
            handle_owner,
        )

    def _book_form(self, book: Book | None) -> None:
        saga = self.saga
        title = (
            "Add a Book" if book is None else f"Edit {escape(book.name or 'this book')}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            target = book
            if target is None:
                target = bk.add_book(saga, values["name"], values["type"])
            _book_from_values(target, values, saga)
            storage.save_saga(saga)
            self._books_changed()

        self.app.push_screen(
            FieldsDialog(
                title,
                _book_fields(saga, book, self._default_book_owner()),
                validate=bk.form_problem,
                live=lambda values: _book_live(values, saga),
            ),
            handle_result,
        )

    def _remove_book(self) -> None:
        """Delete the chosen book, or every marked one, after confirming."""
        marked = self._marked_books()
        if marked:
            count = len(marked)

            def handle_all(confirmed: bool | None) -> None:
                if not confirmed:
                    return
                for book in marked:
                    if book in self.saga.books:
                        self.saga.books.remove(book)
                storage.save_saga(self.saga)
                self._books_changed()

            self.app.push_screen(
                ConfirmScreen(
                    f"Are you sure you want to delete {count} "
                    f"book{'s' if count != 1 else ''}?"
                ),
                handle_all,
            )
            return

        def confirm(book: Book) -> None:
            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed and book in self.saga.books:
                    self.saga.books.remove(book)
                    storage.save_saga(self.saga)
                    self._books_changed()

            self.app.push_screen(
                ConfirmScreen(f"Delete {escape(book.name or 'this book')}?"),
                handle_confirmed,
            )

        self._pick_book("Remove a Book", confirm)

    def action_import_data(self) -> None:
        """'I': on the saga, choose what to import (Books or Spells so far);
        on a covenant's Library tab, import books straight into its library."""
        if self.selected_kind == NodeKind.SAGA:

            def handle_kind(kind: str | None) -> None:
                if kind == "books":
                    self._import_books(None)
                elif kind == "spells":
                    self._import_spells()

            self.app.push_screen(ImportScreen(), handle_kind)
        elif (
            self.selected_covenant is not None
            and self._active_section() in _LIBRARY_SECTIONS
        ):
            self._import_books(self.selected_covenant)

    def _import_books(self, covenant: Covenant | None) -> None:
        """Pick a CSV file, preview what it holds, then add its books: all
        owned by `covenant`, or all unassigned when it's None (the file's own
        owner column isn't used)."""
        saga = self.saga
        destination = (
            f"into {covenant.name}'s library"
            if covenant is not None
            else "as unassigned books"
        )

        def handle_path(path: Path | None) -> None:
            if path is None:
                return
            try:
                result = bk.read_books_csv(path)
            except (OSError, ValueError) as problem:
                self.notify(
                    f"Couldn't read {escape(path.name)}: {escape(str(problem))}",
                    severity="error",
                )
                return
            if not result.books:
                reason = f" {escape(result.skipped[0])}" if result.skipped else ""
                self.notify(
                    f"No books to import from {escape(path.name)}.{reason}",
                    severity="warning",
                )
                return

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    self._add_imported_books(result.books, covenant, destination)

            self.app.push_screen(
                ConfirmScreen(
                    bk.import_preview(
                        result, path.name, destination, {b.name for b in saga.books}
                    ),
                    yes_label="Import",
                    yes_variant="success",
                ),
                handle_confirmed,
            )

        title = (
            f"Import books into {covenant.name}'s library"
            if covenant is not None
            else "Import books (as unassigned books)"
        )
        self.app.push_screen(CsvFilePickerScreen(title, Path.cwd()), handle_path)

    def _add_imported_books(
        self, books: list[Book], covenant: Covenant | None, destination: str
    ) -> None:
        """Add confirmed imported books, asking about each one whose name is
        already taken (Duplicate / Duplicate All / Skip / Skip All). Nothing
        is added until every question is answered."""
        saga = self.saga

        def finish(accepted: list[Book], skipped: int) -> None:
            bk.add_imported_books(saga, accepted, covenant)
            if accepted:
                storage.save_saga(saga)
                self._books_changed()
                if self.selected_kind == NodeKind.SAGA:
                    self.call_later(self._show_saga_detail)  # its Books count
            count = len(accepted)
            message = f"Imported {count} book{'s' if count != 1 else ''}"
            message += f" {destination}" if count else ""
            if skipped:
                message += f"; skipped {skipped} duplicate{'s' if skipped != 1 else ''}"
            self.notify(escape(message + "."))

        self._ask_about_duplicates(books, {b.name for b in saga.books}, "book", finish)

    def _ask_about_duplicates(
        self,
        items: list[Any],
        names: set[str],
        noun: str,
        finish: Callable[[list[Any], int], None],
    ) -> None:
        """Go through imported items (anything with a `.name`), asking about
        each whose name is already taken -- by `names` or earlier in `items` --
        (Duplicate / Duplicate All / Skip / Skip All), then call
        `finish(accepted, skipped)`. Nothing is added until every question is
        answered."""
        pending = list(items)
        accepted: list[Any] = []
        taken = set(names)
        state: dict[str, Any] = {"all": None, "skipped": 0}

        def take(item: Any, answer: str) -> None:
            if answer == "skip":
                state["skipped"] += 1
            else:
                accepted.append(item)
                taken.add(item.name)

        def step() -> None:
            while pending:
                item = pending[0]
                if item.name in taken and state["all"] is None:
                    remaining = len(bk.duplicate_names(pending[1:], taken))

                    def handle_answer(answer: str | None, item=item) -> None:
                        answer = answer or "skip"
                        if answer.endswith("_all"):
                            answer = answer[: -len("_all")]
                            state["all"] = answer
                        pending.pop(0)
                        take(item, answer)
                        step()

                    self.app.push_screen(
                        DuplicateBookScreen(item.name, remaining, noun=noun),
                        handle_answer,
                    )
                    return
                pending.pop(0)
                take(item, state["all"] if item.name in taken else "duplicate")
            finish(accepted, state["skipped"])

        step()

    def _import_spells(self) -> None:
        """The Import Spells helper, then pick a CSV, preview it, and add its
        spells to the saga's own (asking about duplicate names)."""
        saga = self.saga

        def handle_path(path: Path | None) -> None:
            if path is None:
                return
            try:
                result = spl.read_spells_csv(path)
            except (OSError, ValueError) as problem:
                self.notify(
                    f"Couldn't read {escape(path.name)}: {escape(str(problem))}",
                    severity="error",
                )
                return
            if not result.spells:
                reason = f" {escape(result.skipped[0])}" if result.skipped else ""
                self.notify(
                    f"No spells to import from {escape(path.name)}.{reason}",
                    severity="warning",
                )
                return
            existing = {sp.name for sp in spl.all_spells(saga)}

            def finish(accepted: list[Spell], skipped: int) -> None:
                spl.add_imported_spells(saga, accepted)
                if accepted:
                    storage.save_saga(saga)
                    self._spells_changed()
                count = len(accepted)
                message = f"Imported {count} spell{'s' if count != 1 else ''}"
                if skipped:
                    message += (
                        f"; skipped {skipped} duplicate{'s' if skipped != 1 else ''}"
                    )
                self.notify(escape(message + "."))

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    self._ask_about_duplicates(result.spells, existing, "spell", finish)

            self.app.push_screen(
                ConfirmScreen(
                    spl.spell_import_preview(result, path.name, existing),
                    yes_label="Import",
                    yes_variant="success",
                ),
                handle_confirmed,
            )

        def handle_helper(choice: str | None) -> None:
            if choice == "choose":
                self.app.push_screen(
                    CsvFilePickerScreen(
                        "Import spells (into the saga's own spells)", Path.cwd()
                    ),
                    handle_path,
                )

        self.app.push_screen(SpellImportHelperScreen(Path.cwd()), handle_helper)

    def _books_changed(self) -> None:
        """After any book edit: re-render the book list on show, and keep the
        tree's Unassigned Books node in step (it appears, changes count or goes
        away as books lose and gain owners)."""
        view = self._book_view()
        if view is not None:
            view.rebuild()
        tree = self._nav_tree()
        node = _tree_node_with_data(tree, (NodeKind.BOOK_GROUP,))
        count = len(bk.unassigned_books(self.saga))
        if node is not None and count:
            node.set_label(f"Unassigned Books ({count})")
        elif node is not None:
            node.remove()
        elif count:
            tree.root.add_leaf(
                f"Unassigned Books ({count})", data=(NodeKind.BOOK_GROUP,)
            )

    # -- Covenant: Possessions tab --

    def _selected_possession(self, kind: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_possession(kind) if view is not None else None

    def _possession_entries(self, kind: str) -> list[pos.PossessionEntry]:
        covenant = self.selected_covenant
        if covenant is None:
            return []
        return pos.entries_for_kind(
            self.saga, covenant, kind, catalog.load_lab_virtue_flaw_catalog_by_id()
        )

    def _add_possession(self, kind: str) -> None:
        self._possession_form(kind, None)

    def _edit_possession(self, kind: str) -> None:
        """Edit the chosen possession; with none chosen, ask which one."""
        entries = self._possession_entries(kind)
        self._chosen_or_pick(
            self._selected_possession(kind),
            [escape(e.name) or "(unnamed)" for e in entries],
            title=f"Edit which {pos.KIND_SINGULAR[kind]}?",
            empty=f"No {pos.KIND_TITLES[kind]} to edit.",
            then=lambda index: self._possession_form(kind, entries[index]),
        )

    def _possession_form(self, kind: str, entry: pos.PossessionEntry | None) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        title = (
            f"Add a {pos.KIND_SINGULAR[kind]}"
            if entry is None
            else f"Edit {escape(entry.name or 'this ' + pos.KIND_SINGULAR[kind].lower())}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            pos.save_entry(covenant, kind, entry, values)
            self._commit(f"section-pos-{kind}")

        self.app.push_screen(
            FieldsDialog(
                title, _possession_fields(kind, entry), validate=pos.form_problem
            ),
            handle_result,
        )

    def _remove_possession(self, kind: str) -> None:
        """Delete the chosen possession (after confirming); with none chosen,
        ask which one. A laboratory listed as a sanctum can't be deleted here."""
        entries = self._possession_entries(kind)
        self._chosen_or_pick(
            self._selected_possession(kind),
            [escape(e.name) or "(unnamed)" for e in entries],
            title=f"Remove a {pos.KIND_SINGULAR[kind]}",
            empty=f"No {pos.KIND_TITLES[kind]} to remove.",
            then=lambda index: self._confirm_remove_possession(kind, entries[index]),
        )

    def _confirm_remove_possession(self, kind: str, entry: pos.PossessionEntry) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        if entry.auto:
            self.notify(
                f"{escape(entry.name)} is a laboratory of this covenant, so it "
                "can't be deleted here. Move it to another covenant from the "
                "laboratory's Identity instead."
            )
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and entry.record in covenant.possessions:
                covenant.possessions.remove(entry.record)
                self._commit(f"section-pos-{kind}")

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(entry.name or 'this entry')}?"),
            handle_confirmed,
        )

    # -- Covenant: Economics tab --

    #: What the user types on a table row, by `Economics` attribute.
    _ECONOMICS_TYPED_LABELS: ClassVar[dict[str, str]] = {
        "tithes": "Amount (pounds a year)",
        "inflation": "Amount (pounds a year)",
        "sundry": "Amount (pounds a year, at least 1)",
        "magic_savings": "Savings (pounds a year)",
        "emergency_savings": "Savings (pounds a year)",
    }

    def _selected_economics(self, which: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_economics(which) if view is not None else None

    def _edit_wealth(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        economics = covenant.economics

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            economics.wealth = values["wealth"]
            self._commit("section-eco-wealth")

        self.app.push_screen(
            FieldsDialog(
                "Edit Wealth",
                [
                    DialogField(
                        "wealth", "Wealth (pounds in stores)", "int", economics.wealth
                    )
                ],
            ),
            handle_result,
        )

    def _add_income_source(self) -> None:
        self._income_form(None)

    def _edit_income_source(self) -> None:
        """Edit the chosen source of income; with none chosen, ask which one."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        sources = covenant.economics.income_sources
        self._chosen_or_pick(
            self._selected_economics("income"),
            [escape(s.name) or "(unnamed)" for s in sources],
            title="Edit which source of income?",
            empty="No sources of income to edit.",
            then=lambda index: self._income_form(sources[index]),
        )

    def _income_form(self, source: IncomeSource | None) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        title = (
            "Add a Source of Income"
            if source is None
            else f"Edit {escape(source.name or 'this source of income')}"
        )
        usual = ", ".join(f"{t} {n}" for t, n in INCOME_TYPE_DEFAULTS.items())
        fields = [
            DialogField(
                "name", "Name", "text", source.name if source else "", required=True
            ),
            DialogField(
                "type",
                "Type",
                "select",
                source.type if source else "Typical",
                options=_pairs(INCOME_TYPES),
                required=True,
            ),
            DialogField(
                "income",
                "Current Income (blank = usual)",
                "optint",
                source.income if source else None,
                hint=f"Usual per year: {usual}.",
            ),
            _description_field(source.description if source else ""),
        ]

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            if source is None:
                eco.add_income_source(covenant, values)
            else:
                for key, value in values.items():
                    setattr(source, key, value)
            self._commit("section-eco-income")

        self.app.push_screen(FieldsDialog(title, fields), handle_result)

    def _remove_income_source(self) -> None:
        """Delete the chosen source of income (after confirming); with none
        chosen, ask which one."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        sources = covenant.economics.income_sources
        self._chosen_or_pick(
            self._selected_economics("income"),
            [escape(s.name) or "(unnamed)" for s in sources],
            title="Remove a source of income",
            empty="No sources of income to remove.",
            then=lambda index: self._confirm_remove_income_source(sources[index]),
        )

    def _confirm_remove_income_source(self, source: IncomeSource) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and source in covenant.economics.income_sources:
                covenant.economics.income_sources.remove(source)
                self._commit("section-eco-income")

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(source.name or 'this source of income')}?"),
            handle_confirmed,
        )

    def _improve_income_source(self) -> None:
        """Improve the chosen source of income (manually simulating a year's
        Income Modification); with none chosen, ask which one."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        sources = covenant.economics.income_sources
        self._chosen_or_pick(
            self._selected_economics("income"),
            [escape(s.name) or "(unnamed)" for s in sources],
            title="Improve which source of income?",
            empty="No sources of income to improve.",
            then=lambda index: self._improve_form(sources[index]),
        )

    def _improve_form(self, source: IncomeSource) -> None:
        def handle_result(result: tuple[int, str] | None) -> None:
            if result is None:
                return
            new_income, note = result
            source.income = new_income
            source.note = note
            self._commit("section-eco-income")

        self.app.push_screen(
            ImproveIncomeScreen(source, self.saga.current_year), handle_result
        )

    def _offer_emergency_draw(
        self, which: str, row: eco.Row, summary: eco.Summary
    ) -> None:
        """With a deficit, editing Emergency Savings first offers to cover it
        from Wealth: all of it, or as much as Wealth holds. No (or no Wealth to
        draw from) goes on to the ordinary form."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        deficit = -summary.surplus_deficit
        draw = eco.emergency_draw(summary)
        if draw == 0:
            self.notify(
                "There's no Wealth to draw from: the covenant is broke.",
                severity="warning",
            )
            self._economics_row_form(which, row, offer_draw=False)
            return
        outcome = (
            f"This moves {draw} from Wealth into Emergency Savings."
            if draw == deficit
            else f"Wealth only covers {draw} of it: all of it is drawn, and "
            f"{deficit - draw} stays uncovered."
        )

        def handle_confirmed(confirmed: bool | None) -> None:
            if not confirmed:
                self._economics_row_form(which, row, offer_draw=False)
                return
            eco.draw_from_wealth(covenant, draw)
            self._commit("section-eco-savings")
            self.notify(f"Drew {draw} from Wealth to cover the deficit.")

        self.app.push_screen(
            ConfirmScreen(
                "Do you wish to draw from Wealth to cover the deficit?\n\n"
                f"Deficit: {deficit}    Wealth: {summary.wealth}\n{outcome}",
                yes_label="Draw",
                yes_variant="success",
            ),
            handle_confirmed,
        )

    def _edit_economics_row(self, which: str) -> None:
        """Edit the chosen Yearly Expenditure / Cost Savings row (its Notes, and
        the numbers that are typed rather than calculated); with none chosen,
        ask which one."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        summary = eco.summarize(self.saga, covenant)
        rows = summary.expenditure if which == "expenditure" else summary.savings
        selected = self._selected_economics(which)
        if selected is not None and selected < len(rows):
            self._economics_row_form(which, rows[selected])
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._economics_row_form(which, rows[index])

        self.app.push_screen(
            RemovalPickerScreen("Edit which row?", [row.name for row in rows]),
            handle_index,
        )

    def _economics_row_form(
        self, which: str, row: eco.Row, *, offer_draw: bool = True
    ) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        if offer_draw and row.key == "emergency_savings":
            summary = eco.summarize(self.saga, covenant)
            if summary.surplus_deficit < 0:
                self._offer_emergency_draw(which, row, summary)
                return
        economics = covenant.economics
        first = "Cost" if which == "expenditure" else "Quantity"
        fields = [DialogField("_n", "Row", "info", row.name)]
        if row.typed:
            fields += [
                DialogField(
                    attribute,
                    self._ECONOMICS_TYPED_LABELS[attribute],
                    "int",
                    getattr(economics, attribute),
                )
                for attribute in row.typed
            ]
        else:
            fields += [
                DialogField(
                    "_c", f"{first} (calculated)", "info", eco.money(row.first)
                ),
                DialogField(
                    "_s", "Savings (calculated)", "info", eco.money(row.savings)
                ),
            ]
        fields.append(
            DialogField("notes", "Notes", "text", economics.notes.get(row.key, ""))
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            eco.apply_row_edit(economics, row.key, values)
            self._commit(f"section-eco-{which}")

        self.app.push_screen(
            FieldsDialog(
                f"Edit {row.name}",
                fields,
                validate=lambda values: eco.row_problem(row.key, values),
            ),
            handle_result,
        )

    # -- Covenant: Inhabitants tab --

    def _selected_inhabitant(self, kind: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_inhabitant(kind) if view is not None else None

    def _inhabitant_entries(self, kind: str) -> list[inh.InhabitantEntry]:
        covenant = self.selected_covenant
        if covenant is None:
            return []
        return inh.entries_for_kind(self.saga, covenant, kind)

    def _add_inhabitant(self, kind: str) -> None:
        """Add one. Grog-derived kinds first offer the covenant's unassigned
        grogs (or a brand-new person); Magi, Companions and animals go
        straight to the form."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        if kind not in inh.GROG_KINDS:
            self._inhabitant_form(kind, None, None)
            return

        grogs = inh.available_grogs(self.saga, covenant)
        labels = ["(New person -- not from a character sheet)"] + [
            escape(g.name)
            + (f"  (born {g.background.year_born})" if g.background.year_born else "")
            for g in grogs
        ]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._inhabitant_form(kind, None, grogs[index - 1] if index else None)

        self.app.push_screen(
            RemovalPickerScreen(f"Add a {inh.KIND_SINGULAR[kind]}", labels),
            handle_index,
        )

    def _edit_inhabitant(self, kind: str) -> None:
        """Edit the chosen inhabitant; with none chosen, ask which one."""
        entries = self._inhabitant_entries(kind)
        self._chosen_or_pick(
            self._selected_inhabitant(kind),
            [escape(e.name) or "(unnamed)" for e in entries],
            title=f"Edit which {inh.KIND_SINGULAR[kind]}?",
            empty=f"No {inh.KIND_TITLES[kind]} to edit.",
            then=lambda index: self._inhabitant_form(kind, entries[index], None),
        )

    def _inhabitant_form(
        self, kind: str, entry: inh.InhabitantEntry | None, grog: Character | None
    ) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        title = (
            f"Add a {inh.KIND_SINGULAR[kind]}"
            if entry is None
            else f"Edit {escape(entry.name or 'this ' + inh.KIND_SINGULAR[kind].lower())}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            inh.save_entry(covenant, kind, entry, values, grog)
            self._commit(f"section-inh-{kind}")

        self.app.push_screen(
            FieldsDialog(
                title,
                _inhabitant_fields(kind, entry, grog),
                validate=inh.form_problem,
            ),
            handle_result,
        )

    def _remove_inhabitant(self, kind: str) -> None:
        """Delete the chosen inhabitant (after confirming); with none chosen,
        ask which one. People listed from a character sheet can't be deleted
        here -- that would mean changing the sheet."""
        entries = self._inhabitant_entries(kind)
        self._chosen_or_pick(
            self._selected_inhabitant(kind),
            [escape(e.name) or "(unnamed)" for e in entries],
            title=f"Remove a {inh.KIND_SINGULAR[kind]}",
            empty=f"No {inh.KIND_TITLES[kind]} to remove.",
            then=lambda index: self._confirm_remove_inhabitant(kind, entries[index]),
        )

    def _confirm_remove_inhabitant(self, kind: str, entry: inh.InhabitantEntry) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        name = escape(entry.name or "this entry")

        if entry.auto and entry.character is not None:
            # Listed from a character sheet (e.g. a magus who died): they stay
            # in the covenant on their sheet, but stop counting as an inhabitant.

            def handle_departed(confirmed: bool | None) -> None:
                if not confirmed:
                    return
                inh.mark_departed(covenant, kind, entry)
                self._commit(f"section-inh-{kind}")

            self.app.push_screen(
                ConfirmScreen(
                    f"Remove {name} from the {inh.KIND_TITLES[kind]} list?\n\n"
                    "They stay in the covenant on their character sheet, but "
                    "will no longer count as an inhabitant."
                ),
                handle_departed,
            )
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and entry.record in covenant.inhabitants:
                covenant.inhabitants.remove(entry.record)
                self._commit(f"section-inh-{kind}")

        self.app.push_screen(ConfirmScreen(f"Delete {name}?"), handle_confirmed)

    def _restore_inhabitant(self, kind: str) -> None:
        """Bring back a departed Magus/Companion: still on their sheet, they
        simply start counting as an inhabitant again."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        entries = inh.departed_entries_for_kind(self.saga, covenant, kind)
        if not entries:
            self.notify(f"No departed {inh.KIND_TITLES[kind]} to restore.")
            return

        def do_restore(entry: inh.InhabitantEntry) -> None:
            if entry.record is not None:
                entry.record.departed = False
                self._commit(f"section-inh-{kind}")

        def handle_index(index: int | None) -> None:
            if index is not None:
                do_restore(entries[index])

        self.app.push_screen(
            RemovalPickerScreen(
                f"Restore which {inh.KIND_SINGULAR[kind]}?",
                [escape(e.name) or "(unnamed)" for e in entries],
            ),
            handle_index,
        )

    def _edit_loyalty(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        loyalty = covenant.loyalty
        styles = inh.governance_names(covenant)
        if styles:
            governance = DialogField(
                "_g",
                "Type of Governance",
                "info",
                f"{', '.join(styles)} (from your Boons)",
            )
        else:
            governance = DialogField(
                "governance", "Type of Governance", "text", loyalty.governance
            )
        base = inh.base_loyalty(self.saga, covenant)
        modifiers = inh.total_modifiers(self.saga, covenant)
        fields = [
            governance,
            DialogField("_bp", "Base Loyalty Points", "info", base),
            DialogField("_tm", "Total modifiers", "info", modifiers),
            DialogField("_cp", "Current Loyalty Points", "info", base + modifiers),
            DialogField(
                "_ps",
                "Prevailing Loyalty Score",
                "info",
                inh.prevailing_loyalty_score(base + modifiers),
            ),
            DialogField(
                "_lc",
                "Living Conditions (from the covenant's Living Conditions (Mundane))",
                "info",
                inh.living_conditions_loyalty(covenant),
            ),
            DialogField(
                "equipment",
                "Equipment",
                "select",
                loyalty.equipment,
                options=_pairs(LOYALTY_EQUIPMENT),
            ),
            DialogField(
                "money",
                "Money",
                "select",
                loyalty.money,
                options=_pairs(LOYALTY_MONEY),
            ),
            DialogField(
                "pension",
                "  Pension? (half Wages until death)",
                "check",
                loyalty.pension,
            ),
            DialogField(
                "_sp",
                "Specialists (Presence + Ability of Steward/Chamberlain/Turb "
                "Captain/Autocrat)",
                "info",
                inh.specialists_loyalty(self.saga, covenant),
            ),
            DialogField("familiarity", "Familiarity", "int", loyalty.familiarity),
            DialogField(
                "_rp",
                "Reputation (-5 per point of a known bad Reputation)",
                "info",
                inh.reputation_loyalty_penalty(covenant),
            ),
            DialogField(
                "actions_and_events",
                "Actions and events",
                "int",
                loyalty.actions_and_events,
            ),
            DialogField(
                "magical_influence",
                "Magical Influence",
                "int",
                loyalty.magical_influence,
            ),
        ]

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            for key, value in values.items():
                setattr(loyalty, key, value)
            self._commit("section-inh-loyalty")

        self.app.push_screen(FieldsDialog("Edit Loyalty", fields), handle_result)

    def _edit_population(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        pop = covenant.population
        fields = [
            DialogField(
                "_tm",
                "Number of Teamsters",
                "info",
                inh.other_covenfolk_count(self.saga, covenant, "Teamster"),
            ),
            DialogField(
                "_tn",
                "Teamsters Needed",
                "info",
                inh.minimum_teamsters(self.saga, covenant),
            ),
            DialogField(
                "_sv",
                "Number of Servants",
                "info",
                inh.other_covenfolk_count(self.saga, covenant, "Servant"),
            ),
            DialogField(
                "_sn",
                "Servants Needed",
                "info",
                inh.minimum_servants(self.saga, covenant),
            ),
            DialogField(
                "_lb",
                "Number of Laborers",
                "info",
                inh.other_covenfolk_count(self.saga, covenant, "Laborer"),
            ),
            DialogField("other_people", "Other People", "int", pop.other_people),
            DialogField(
                "_t",
                "Total Inhabitants",
                "info",
                f"{inh.total_inhabitants(self.saga, covenant)} (calculated)",
            ),
        ]

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            for key, value in values.items():
                setattr(pop, key, value)
            self._commit("section-inh-population")

        self.app.push_screen(FieldsDialog("Edit Inhabitants", fields), handle_result)

    def _edit_miscellaneous(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        pop = covenant.population
        fields = [
            DialogField("aging_magi", "Aging for Magi", "int", pop.aging_magi),
            DialogField("aging_mundane", "Aging for Mundane", "int", pop.aging_mundane),
            DialogField("magic_laborers", "Magic Laborers", "int", pop.magic_laborers),
            DialogField("magic_servants", "Magic Servants", "int", pop.magic_servants),
            DialogField(
                "magic_teamsters", "Magic Teamsters", "int", pop.magic_teamsters
            ),
            DialogField("magic_turbula", "Magic Turbula", "int", pop.magic_turbula),
        ]

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            for key, value in values.items():
                setattr(pop, key, value)
            self._commit("section-inh-misc")

        self.app.push_screen(FieldsDialog("Edit Miscellaneous", fields), handle_result)

    # -- Covenant: Description / Reputations / Boons & Hooks --

    def _edit_covenant_description(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                covenant.notes = result["notes"]
                self._commit("section-cov-description")

        self.app.push_screen(
            FieldsDialog(
                "Edit Covenant Description",
                [
                    DialogField(
                        "notes",
                        "Description",
                        "area",
                        covenant.notes,
                        hint=_EMPHASIS_HINT,
                    )
                ],
            ),
            handle_result,
        )

    def _selected_reputation(self) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_reputation() if view is not None else None

    def _attached_boons_hooks(
        self, covenant: Covenant, kind: str
    ) -> list[tuple[int, VirtueFlawInstance]]:
        """The covenant's attached Boons or Hooks (`kind`), each with its
        index into covenant.boons_hooks so callers can edit/delete the real
        entry from a filtered list."""
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        return [
            (index, bh)
            for index, bh in enumerate(covenant.boons_hooks)
            if bh.vf_id in by_id and by_id[bh.vf_id].type == kind
        ]

    def _add_boon_hook(self, kind: str) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        attached_ids = [bh.vf_id for bh in covenant.boons_hooks]

        def handle_result(instance: VirtueFlawInstance | None) -> None:
            if instance is not None:
                covenant.boons_hooks.append(instance)
                self._commit(_BOON_HOOK_SECTION[kind])

        self.app.push_screen(
            CovenantBoonHookPickerScreen(kind, attached_ids), handle_result
        )

    def _selected_boon_hook(self, kind: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_boon_hook(kind) if view is not None else None

    def _remove_boon_hook(self, kind: str) -> None:
        """Delete the selected Boon/Hook (after confirming). With nothing
        selected in this section, ask which one first."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        selected = self._selected_boon_hook(kind)
        if selected is not None:
            self._confirm_remove_boon_hook(kind, selected)
            return

        attached = self._attached_boons_hooks(covenant, kind)
        if not attached:
            self.notify(f"No {kind}s to remove.")
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        labels = [catalog.describe_boon_hook(bh, by_id) for _, bh in attached]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._confirm_remove_boon_hook(kind, attached[index][0])

        self.app.push_screen(
            RemovalPickerScreen(f"Remove a {kind}", labels), handle_index
        )

    def _confirm_remove_boon_hook(self, kind: str, index: int) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        label = catalog.describe_boon_hook(covenant.boons_hooks[index], by_id)

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del covenant.boons_hooks[index]
                self._commit(_BOON_HOOK_SECTION[kind])

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(label)}?"), handle_confirmed
        )

    def _edit_boon_hook(self, kind: str) -> None:
        """Edit the selected Boon/Hook's detail and description. With nothing
        selected in this section, ask which one first."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        selected = self._selected_boon_hook(kind)
        if selected is not None:
            self._edit_boon_hook_at(kind, selected)
            return

        attached = self._attached_boons_hooks(covenant, kind)
        if not attached:
            self.notify(f"No {kind}s to edit.")
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        labels = [catalog.describe_boon_hook(bh, by_id) for _, bh in attached]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._edit_boon_hook_at(kind, attached[index][0])

        self.app.push_screen(
            RemovalPickerScreen(f"Edit which {kind}?", labels), handle_index
        )

    def _edit_boon_hook_at(self, kind: str, index: int) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        instance = covenant.boons_hooks[index]

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            instance.params = boon_hook_params(
                result["detail"], result["description"], instance.params
            )
            self._commit(_BOON_HOOK_SECTION[kind])

        self.app.push_screen(
            FieldsDialog(
                f"{kind}: {escape(by_id[instance.vf_id].name)}",
                _boon_hook_fields(
                    instance.params.get(BOON_HOOK_DETAIL, ""),
                    instance.params.get(BOON_HOOK_DESCRIPTION, ""),
                ),
            ),
            handle_result,
        )

    # -- Covenant --

    def _edit_covenant(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            for field, value in result.items():
                setattr(covenant, field, value)
            self._commit("section-cov-info", tree=True)

        self.app.push_screen(
            FieldsDialog("Edit Covenant", _covenant_fields(covenant)), handle_result
        )

    def _edit_saga(self) -> None:
        async def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
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

    # -- Character Info / Characteristics --

    def _edit_character_info(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            character.name = result["name"]
            character.covenant_id = result["covenant_id"]
            self.selected_covenant = self.saga.covenant(character.covenant_id)
            if character.type == "magus":
                assign_laboratory(self.saga, character, result["laboratory_id"])
            background = character.background
            background.setting = result["setting"]
            background.confidence_score = result["confidence_score"]
            background.confidence_points = result["confidence_points"]
            background.size = result["size"]
            self._commit("section-char-info", tree=True)

        self.app.push_screen(
            FieldsDialog(
                "Edit Character Info", _character_info_fields(self.saga, character)
            ),
            handle_result,
        )

    def _edit_characteristics(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                character.characteristics = _characteristics_from(result)
                self._commit("section-char-characteristics")

        self.app.push_screen(
            FieldsDialog(
                "Edit Characteristics",
                _characteristics_fields(character.characteristics),
            ),
            handle_result,
        )

    def _edit_biographical_detail(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                for attribute in known_fields(Background, result):
                    setattr(character.background, attribute, result[attribute])
                character.description = Description(**known_fields(Description, result))
                self._commit("section-char-biographical")
                # Age (derived from Year Born) lives in the top panel.
                self._refresh_character_section("section-char-info")

        self.app.push_screen(
            FieldsDialog(
                "Edit Biographical Detail",
                _biographical_fields(character.background, character.description),
            ),
            handle_result,
        )

    def _edit_aging(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                character.aging = Aging(**result)
                self._commit("section-aging")

        self.app.push_screen(
            FieldsDialog("Edit Aging & Warping", _aging_fields(character.aging)),
            handle_result,
        )

    # -- Abilities --

    def _add_ability(self) -> None:
        character = self.selected_character
        if character is None:
            return
        exclude_names = {a.name for a in character.abilities}

        def handle_result(ability: Ability | None) -> None:
            if ability is not None:
                character.abilities.append(ability)
                self._commit("tab-abilities")

        self.app.push_screen(AbilityPickerScreen(exclude_names), handle_result)

    def _selected_ability(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_ability() if view is not None else None

    @staticmethod
    def _ability_label(a: Ability) -> str:
        specialty = f" ({escape(a.specialty)})" if a.specialty else ""
        return f"{escape(a.name)}{specialty} {a.level} {a.xp}/{a.xp_to_next}"

    def _remove_ability(self) -> None:
        """Delete the chosen Ability (after confirming); with none chosen,
        ask which one first."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_ability(),
            [self._ability_label(a) for a in character.abilities],
            title="Remove an Ability",
            empty="No Abilities to remove.",
            then=lambda index: self._confirm_remove_ability(index),
        )

    def _confirm_remove_ability(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        self._confirm_delete(
            character.abilities, index, character.abilities[index].name, "tab-abilities"
        )

    def _edit_ability(self) -> None:
        """Edit the chosen Ability; with none chosen, ask which one."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_ability(),
            [self._ability_label(a) for a in character.abilities],
            title="Edit which Ability?",
            empty="No Abilities to edit.",
            then=lambda index: self._edit_ability_at(index),
        )

    def _edit_ability_at(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        existing = character.abilities[index]

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                character.abilities[index] = _ability_from(
                    existing.name, existing.category, result
                )
                self._commit("tab-abilities")

        self.app.push_screen(
            FieldsDialog(escape(existing.name), _ability_fields(existing)),
            handle_result,
        )

    # -- Personality Traits / Reputations / Wounds / Fatigue --

    def _selected_personality_trait(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_personality_trait() if view is not None else None

    def _selected_character_reputation(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_reputation() if view is not None else None

    def _edit_wounds(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                character.wounds = Wounds(**result)
                self._commit("section-char-health")

        self.app.push_screen(
            FieldsDialog("Edit Wounds", _wounds_fields(character.wounds)),
            handle_result,
        )

    def _edit_fatigue(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                character.fatigue_level = result["level"]
                self._commit("section-char-health")

        self.app.push_screen(
            FieldsDialog(
                "Edit Fatigue Level", _fatigue_fields(character.fatigue_level)
            ),
            handle_result,
        )

    # -- Arts (magi only) --

    def _edit_arts(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(arts: dict[str, ArtScore] | None) -> None:
            if arts is not None:
                character.arts = arts
                self._commit("section-arts")

        self.app.push_screen(EditArtsScreen(character.arts), handle_result)

    # -- Raw Vis / Hermetic Background (magi only) --

    def _add_raw_vis(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: tuple[str, int] | None) -> None:
            if result is not None:
                art, pawns = result
                add_raw_vis(character.raw_vis, art, pawns)
                self._commit("section-raw-vis-hermetic")

        self.app.push_screen(_raw_vis_dialog(), handle_result)

    def _selected_raw_vis(self) -> int | None:
        view = self._character_sheet_view
        section = self._active_section()
        if view is None or section not in (
            "section-raw-vis-hermetic",
            "section-raw-vis-inventory",
        ):
            return None
        return view.selected_raw_vis(section)

    def _edit_raw_vis(self) -> None:
        """Edit the chosen Raw Vis entry; with none chosen, ask which one."""
        character = self.selected_character
        if character is None:
            return
        selected = self._selected_raw_vis()
        if selected is not None:
            self._edit_raw_vis_at(selected)
            return
        if not character.raw_vis:
            self.notify("No Raw Vis to edit.")
            return

        arts = sorted(character.raw_vis)
        labels = [f"{art.title()}: {character.raw_vis[art]} pawn(s)" for art in arts]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._edit_raw_vis_at(index)

        self.app.push_screen(
            RemovalPickerScreen("Edit which Raw Vis entry?", labels), handle_index
        )

    def _edit_raw_vis_at(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        arts = sorted(character.raw_vis)
        old_art = arts[index]

        def handle_result(result: tuple[str, int] | None) -> None:
            if result is not None:
                art, pawns = result
                replace_raw_vis(character.raw_vis, old_art, art, pawns)
                self._commit("section-raw-vis-hermetic")

        self.app.push_screen(
            _raw_vis_dialog(existing=(old_art, character.raw_vis[old_art])),
            handle_result,
        )

    def _remove_raw_vis(self) -> None:
        """Delete the chosen Raw Vis entry (after confirming); with none
        chosen, ask which one first."""
        character = self.selected_character
        if character is None:
            return
        selected = self._selected_raw_vis()
        if selected is not None:
            self._confirm_remove_raw_vis(selected)
            return
        if not character.raw_vis:
            self.notify("No Raw Vis to remove.")
            return

        arts = sorted(character.raw_vis)
        labels = [f"{art.title()}: {character.raw_vis[art]} pawn(s)" for art in arts]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._confirm_remove_raw_vis(index)

        self.app.push_screen(
            RemovalPickerScreen("Remove a Raw Vis entry", labels), handle_index
        )

    def _confirm_remove_raw_vis(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        art = sorted(character.raw_vis)[index]

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del character.raw_vis[art]
                self._commit("section-raw-vis-hermetic")

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(art.title())}?"), handle_confirmed
        )

    def _edit_hermetic_background(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                character.hermetic = HermeticBackground(**result)
                self._commit("section-hermetic-background")

        self.app.push_screen(
            FieldsDialog(
                "Edit Hermetic Background", _hermetic_fields(character.hermetic)
            ),
            handle_result,
        )

    # -- Spells known (magi only) --

    def _add_spell(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(spell_id: str | None) -> None:
            if spell_id is not None:
                character.spells_known.append(KnownSpell(spell_id=spell_id))
                self._commit("section-known-spells")

        self.app.push_screen(
            SpellChooserScreen(
                self.saga,
                exclude={k.spell_id for k in character.spells_known},
                title=f"Add a spell {escape(character.name)} knows",
            ),
            handle_result,
        )

    def _known_spell_labels(self, character: Character) -> list[str]:
        labels = []
        for known in character.spells_known:
            spell = spl.find_spell(self.saga, known.spell_id)
            labels.append(
                escape(spell.name)
                if spell
                else f"{escape(known.spell_id)} (unknown spell)"
            )
        return labels

    def _selected_known_spell(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_known_spell() if view is not None else None

    def _edit_spell_mastery(self) -> None:
        """Edit the chosen known spell's Mastery; with none chosen, ask
        which one."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_known_spell(),
            self._known_spell_labels(character),
            title="Edit Mastery for which spell?",
            empty="No Spells to edit.",
            then=lambda index: self._edit_spell_mastery_at(index),
        )

    def _edit_spell_mastery_at(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        known = character.spells_known[index]
        spell = spl.find_spell(self.saga, known.spell_id)
        name = spell.name if spell else known.spell_id

        def handle_result(result: KnownSpell | None) -> None:
            if result is not None:
                character.spells_known[index] = result
                self._commit("section-known-spells")

        self.app.push_screen(MasteryEditScreen(name, known), handle_result)

    def _remove_spell(self) -> None:
        """Delete the chosen known spell (after confirming); with none
        chosen, ask which one first."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_known_spell(),
            self._known_spell_labels(character),
            title="Remove a Known Spell",
            empty="No Spells to remove.",
            then=lambda index: self._confirm_remove_spell(index),
        )

    def _confirm_remove_spell(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        self._confirm_delete(
            character.spells_known,
            index,
            self._known_spell_labels(character)[index],
            "section-known-spells",
        )

    # -- Inventory --

    def _selected_inventory_item(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_inventory_item() if view is not None else None

    def _add_item(self) -> None:
        """Add an item: ask which kind first (the section is one combined
        list, unlike the covenant Possessions tab's per-kind sections)."""
        character = self.selected_character
        if character is None:
            return

        def handle_kind(index: int | None) -> None:
            if index is not None:
                self._inventory_item_form(("weapon", "armor", "item")[index], None)

        self.app.push_screen(
            RemovalPickerScreen("Add which kind of item?", ["Weapon", "Armor", "Item"]),
            handle_kind,
        )

    def _inventory_item_form(self, kind: str, index: int | None) -> None:
        character = self.selected_character
        if character is None:
            return
        existing = character.inventory[index] if index is not None else None
        entry = pos.PossessionEntry(kind, existing) if existing is not None else None
        title = (
            f"Add a {pos.KIND_SINGULAR[kind]}"
            if index is None
            else f"Edit {escape(existing.name or 'this item')}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            if index is not None and existing is not None:
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                character.inventory.append(
                    Possession(
                        id=storage.generate_unique_id(
                            values.get("name") or kind,
                            [item.id for item in character.inventory],
                        ),
                        kind=kind,
                        **values,
                    )
                )
            self._commit("section-inventory")

        self.app.push_screen(
            FieldsDialog(
                title, _possession_fields(kind, entry), validate=pos.form_problem
            ),
            handle_result,
        )

    def _edit_item(self) -> None:
        """Edit the chosen item; with none chosen, ask which one."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_inventory_item(),
            [
                pos.row_label(pos.PossessionEntry(item.kind, item))
                for item in character.inventory
            ],
            title="Edit which item?",
            empty="No Items to edit.",
            then=lambda index: self._inventory_item_form(
                character.inventory[index].kind, index
            ),
        )

    def _remove_item(self) -> None:
        """Delete the chosen item (after confirming); with none chosen, ask
        which one first."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_inventory_item(),
            [
                pos.row_label(pos.PossessionEntry(item.kind, item))
                for item in character.inventory
            ],
            title="Remove an Item",
            empty="No Items to remove.",
            then=lambda index: self._confirm_remove_item(index),
        )

    def _confirm_remove_item(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        self._confirm_delete(
            character.inventory,
            index,
            character.inventory[index].name or "this item",
            "section-inventory",
        )

    # -- Laboratory: Identity / Characteristics --

    def _edit_lab_identity(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            lab.name = result["name"]
            lab.location = result["location"]
            lab.build_points = result["build_points"]
            lab.aura_modifier = result["aura_modifier"]
            lab.covenant_id = result["covenant_id"]
            self.selected_covenant = self.saga.covenant(lab.covenant_id)
            assign_laboratory_owner(self.saga, lab, result["owner_id"])
            self._commit("section-lab-identity", tree=True)

        self.app.push_screen(
            FieldsDialog(
                "Edit Laboratory Identity", _lab_identity_fields(self.saga, lab)
            ),
            handle_result,
        )

    def _edit_lab_characteristics(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                lab.characteristics = LabCharacteristics(**result)
                self._commit("section-lab-characteristics")

        self.app.push_screen(
            FieldsDialog(
                "Edit Laboratory Characteristics (manual value)",
                _lab_characteristics_fields(lab.characteristics),
            ),
            handle_result,
        )

    # -- Laboratory: Specialties / Features / Rooms --

    def _add_specialty(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(item: str | None) -> None:
            if item is not None:
                lab.specialties.append(item)
                self._commit("section-lab-specialties")

        self.app.push_screen(
            _item_dialog("Add a Specialty", "Specialty"), handle_result
        )

    def _remove_specialty(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.specialties:
            self.notify("No Specialties to remove.")
            return

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.specialties[index]
                self._commit("section-lab-specialties")

        self.app.push_screen(
            RemovalPickerScreen(
                "Remove a Specialty", [escape(s) for s in lab.specialties]
            ),
            handle_result,
        )

    def _add_feature(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(item: str | None) -> None:
            if item is not None:
                lab.features.append(item)
                self._commit("section-lab-features")

        self.app.push_screen(_item_dialog("Add a Feature", "Feature"), handle_result)

    def _remove_feature(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.features:
            self.notify("No Features to remove.")
            return

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.features[index]
                self._commit("section-lab-features")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Feature", [escape(f) for f in lab.features]),
            handle_result,
        )

    def _add_room(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(room: NamedDescription | None) -> None:
            if room is not None:
                lab.rooms.append(room)
                self._commit("section-lab-rooms")

        self.app.push_screen(
            _named_description_dialog("Add a Room", "e.g. Vault"), handle_result
        )

    def _remove_room(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.rooms:
            self.notify("No Rooms to remove.")
            return

        labels = [escape(room.name) for room in lab.rooms]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.rooms[index]
                self._commit("section-lab-rooms")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Room", labels), handle_result
        )

    # -- Laboratory: Raw Vis / Items --

    def _add_lab_raw_vis(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(result: tuple[str, int] | None) -> None:
            if result is not None:
                art, pawns = result
                add_raw_vis(lab.raw_vis, art, pawns)
                self._commit("section-lab-raw-vis")

        self.app.push_screen(_raw_vis_dialog(), handle_result)

    def _remove_lab_raw_vis(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.raw_vis:
            self.notify("No Raw Vis to remove.")
            return

        arts = sorted(lab.raw_vis)
        labels = [f"{art.title()}: {lab.raw_vis[art]} pawn(s)" for art in arts]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.raw_vis[arts[index]]
                self._commit("section-lab-raw-vis")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Raw Vis entry", labels), handle_result
        )

    def _add_inventory_item(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(item: NamedDescription | None) -> None:
            if item is not None:
                lab.inventory_items.append(item)
                self._commit("section-lab-items")

        self.app.push_screen(
            _named_description_dialog("Add an Item", "e.g. Silver Mirror"),
            handle_result,
        )

    def _remove_inventory_item(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.inventory_items:
            self.notify("No Items to remove.")
            return

        labels = [escape(item.name) for item in lab.inventory_items]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.inventory_items[index]
                self._commit("section-lab-items")

        self.app.push_screen(
            RemovalPickerScreen("Remove an Item", labels), handle_result
        )

    # -- Laboratory: Diary --

    def _add_diary_entry(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(entry: DiaryEntry | None) -> None:
            if entry is not None:
                lab.diary.append(entry)
                self._commit("tab-lab-diary")

        self.app.push_screen(
            _diary_entry_dialog(
                self.saga.current_year, default_season=self.saga.current_season
            ),
            handle_result,
        )

    def _remove_diary_entry(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.diary:
            self.notify("No Diary entries to remove.")
            return

        labels = [
            f"{entry.year} {entry.season} -- {escape(entry.name)}"
            for entry in lab.diary
        ]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.diary[index]
                self._commit("tab-lab-diary")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Diary Entry", labels), handle_result
        )

    # -- Laboratory: edit an existing list entry --

    def _edit_lab_entry(
        self,
        *,
        picker_title: str,
        empty_message: str,
        labels: list[str],
        screen_for: Callable[[int], ModalScreen[Any]],
        apply: Callable[[int, Any], None],
        section_id: str,
    ) -> None:
        """Shared two-step flow for editing one entry of a laboratory list:
        pick which entry (same picker as Remove), then edit it in a
        pre-filled dialog built by `screen_for(index)`; `apply(index,
        result)` writes the result back before saving and refreshing."""
        if not labels:
            self.notify(empty_message)
            return

        def handle_index(index: int | None) -> None:
            if index is None:
                return

            def handle_result(result: Any) -> None:
                if result is None:
                    return
                apply(index, result)
                self._commit(section_id)

            self.app.push_screen(screen_for(index), handle_result)

        self.app.push_screen(RemovalPickerScreen(picker_title, labels), handle_index)

    def _edit_specialty(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Specialty?",
            empty_message="No Specialties to edit.",
            labels=[escape(s) for s in lab.specialties],
            screen_for=lambda i: _item_dialog(
                "Edit a Specialty", "Specialty", existing=lab.specialties[i]
            ),
            apply=lab.specialties.__setitem__,
            section_id="section-lab-specialties",
        )

    def _edit_feature(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Feature?",
            empty_message="No Features to edit.",
            labels=[escape(f) for f in lab.features],
            screen_for=lambda i: _item_dialog(
                "Edit a Feature", "Feature", existing=lab.features[i]
            ),
            apply=lab.features.__setitem__,
            section_id="section-lab-features",
        )

    def _edit_room(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Room?",
            empty_message="No Rooms to edit.",
            labels=[escape(room.name) for room in lab.rooms],
            screen_for=lambda i: _named_description_dialog(
                "Edit a Room", "e.g. Vault", existing=lab.rooms[i]
            ),
            apply=lab.rooms.__setitem__,
            section_id="section-lab-rooms",
        )

    def _edit_inventory_item(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Item?",
            empty_message="No Items to edit.",
            labels=[escape(item.name) for item in lab.inventory_items],
            screen_for=lambda i: _named_description_dialog(
                "Edit an Item", "e.g. Silver Mirror", existing=lab.inventory_items[i]
            ),
            apply=lab.inventory_items.__setitem__,
            section_id="section-lab-items",
        )

    def _edit_lab_raw_vis(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        arts = sorted(lab.raw_vis)

        def apply(index: int, result: tuple[str, int]) -> None:
            art, pawns = result
            replace_raw_vis(lab.raw_vis, arts[index], art, pawns)

        self._edit_lab_entry(
            picker_title="Edit which Raw Vis entry?",
            empty_message="No Raw Vis to edit.",
            labels=[f"{art.title()}: {lab.raw_vis[art]} pawn(s)" for art in arts],
            screen_for=lambda i: _raw_vis_dialog(
                existing=(arts[i], lab.raw_vis[arts[i]])
            ),
            apply=apply,
            section_id="section-lab-raw-vis",
        )

    def _edit_diary_entry(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Diary Entry?",
            empty_message="No Diary entries to edit.",
            labels=[f"{e.year} {e.season} -- {e.name}" for e in lab.diary],
            screen_for=lambda i: _diary_entry_dialog(
                self.saga.current_year, existing=lab.diary[i]
            ),
            apply=lab.diary.__setitem__,
            section_id="tab-lab-diary",
        )

    def action_improve(self) -> None:
        self._improve_income_source()

    # -- shared Character/Laboratory/Familiar Virtue & Flaw actions --

    def action_add_virtue_flaw(self) -> None:
        target = self._virtue_flaw_target()
        if target is None:
            return
        existing_ids = {vf.vf_id for vf in target.virtues_flaws}
        is_lab = self.selected_kind == NodeKind.LABORATORY
        is_familiar = self.selected_kind == NodeKind.FAMILIAR
        picker = LabVirtueFlawPickerScreen if is_lab else VirtueFlawPickerScreen

        def handle_result(instance: VirtueFlawInstance | None) -> None:
            if instance is not None:
                target.virtues_flaws.append(instance)
                storage.save_saga(self.saga)
                if is_lab:
                    self._refresh_laboratory_section("tab-lab-vf")
                elif is_familiar:
                    self._refresh_familiar_section("section-fam-vf-virtues")
                else:
                    self._refresh_character_section("section-vf-virtues")

        self.app.push_screen(picker(existing_ids), handle_result)

    def action_remove_virtue_flaw(self) -> None:
        is_lab = self.selected_kind == NodeKind.LABORATORY
        is_familiar = self.selected_kind == NodeKind.FAMILIAR
        if (
            not is_lab
            and not is_familiar
            and self._active_section()
            in (
                "section-vf-virtues",
                "section-vf-flaws",
            )
        ):
            self._remove_character_virtue_flaw()
            return

        target = self._virtue_flaw_target()
        if target is None:
            return
        if not target.virtues_flaws:
            self.notify("No Virtues/Flaws to remove.")
            return

        vf_catalog = (
            catalog.load_lab_virtue_flaw_catalog_by_id()
            if is_lab
            else catalog.load_virtue_flaw_catalog_by_id()
        )
        labels = [
            escape(catalog.describe_virtue_flaw(vf, vf_catalog))
            for vf in target.virtues_flaws
        ]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del target.virtues_flaws[index]
                storage.save_saga(self.saga)
                if is_lab:
                    self._refresh_laboratory_section("tab-lab-vf")
                elif is_familiar:
                    self._refresh_familiar_section("section-fam-vf-virtues")
                else:
                    self._refresh_character_section("section-vf-virtues")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Virtue or Flaw", labels), handle_result
        )

    def _selected_character_virtue_flaw(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_virtue_flaw() if view is not None else None

    def _remove_character_virtue_flaw(self) -> None:
        """Delete the chosen character Virtue/Flaw (after confirming); with
        none chosen, ask which one first."""
        character = self.selected_character
        if character is None:
            return
        selected = self._selected_character_virtue_flaw()
        if selected is not None:
            self._confirm_remove_character_virtue_flaw(selected)
            return
        if not character.virtues_flaws:
            self.notify("No Virtues/Flaws to remove.")
            return

        vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
        labels = [
            escape(catalog.describe_virtue_flaw(vf, vf_catalog))
            for vf in character.virtues_flaws
        ]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._confirm_remove_character_virtue_flaw(index)

        self.app.push_screen(
            RemovalPickerScreen("Remove a Virtue or Flaw", labels), handle_index
        )

    def _confirm_remove_character_virtue_flaw(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
        self._confirm_delete(
            character.virtues_flaws,
            index,
            catalog.describe_virtue_flaw(character.virtues_flaws[index], vf_catalog),
            "section-vf-virtues",
        )

    # -- Familiar: Info & Binding --

    def _edit_familiar_info(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            result["season_bound"] = result["season_bound"] or ""
            for field_name, value in result.items():
                setattr(familiar, field_name, value)
            self._commit("section-fam-info", tree=True)

        self.app.push_screen(
            FieldsDialog("Edit Familiar", _familiar_info_fields(familiar)),
            handle_result,
        )

    def _edit_familiar_binding(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, object] | None) -> None:
            if result is None:
                return
            for field_name, value in result.items():
                setattr(familiar, field_name, value)
            self._commit("section-fam-binding")

        self.app.push_screen(EditFamiliarBindingScreen(familiar), handle_result)

    def _edit_familiar_characteristics(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            familiar.characteristics = _characteristics_from(result)
            familiar.base_soak = result["base_soak"]
            familiar.magic_resistance = result["magic_resistance"]
            self._commit("section-fam-characteristics")

        self.app.push_screen(
            FieldsDialog(
                "Edit Characteristics", _familiar_characteristics_fields(familiar)
            ),
            handle_result,
        )

    # -- Familiar: Combat & Health --

    def _edit_familiar_wounds(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                familiar.wounds = Wounds(soak=familiar.wounds.soak, **result)
                self._commit("section-fam-health")

        self.app.push_screen(
            FieldsDialog("Edit Wounds", _wounds_fields(familiar.wounds, soak=False)),
            handle_result,
        )

    def _edit_familiar_fatigue(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                familiar.fatigue_level = result["level"]
                self._commit("section-fam-health")

        self.app.push_screen(
            FieldsDialog("Edit Fatigue Level", _fatigue_fields(familiar.fatigue_level)),
            handle_result,
        )

    def _selected_familiar_natural_weapon(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_natural_weapon() if view is not None else None

    def _familiar_natural_weapon_form(self, index: int | None) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        existing = familiar.natural_weapons[index] if index is not None else None
        entry = (
            pos.PossessionEntry("weapon", existing) if existing is not None else None
        )
        title = (
            "Add a Natural Weapon"
            if index is None
            else f"Edit {escape(existing.name or 'this attack')}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            if index is not None and existing is not None:
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                familiar.natural_weapons.append(
                    Possession(
                        id=storage.generate_unique_id(
                            values.get("name") or "weapon",
                            [item.id for item in familiar.natural_weapons],
                        ),
                        kind="weapon",
                        **values,
                    )
                )
            self._commit("section-fam-natural-weapons")

        self.app.push_screen(
            FieldsDialog(
                title, _possession_fields("weapon", entry), validate=pos.form_problem
            ),
            handle_result,
        )

    def _add_familiar_natural_weapon(self) -> None:
        self._familiar_natural_weapon_form(None)

    def _edit_familiar_natural_weapon(self) -> None:
        """Edit the chosen attack; with none chosen, ask which one."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_natural_weapon(),
            [
                pos.row_label(pos.PossessionEntry("weapon", weapon))
                for weapon in familiar.natural_weapons
            ],
            title="Edit which attack?",
            empty="No Natural Weapons to edit.",
            then=lambda index: self._familiar_natural_weapon_form(index),
        )

    def _remove_familiar_natural_weapon(self) -> None:
        """Delete the chosen attack (after confirming); with none chosen,
        ask which one first."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_natural_weapon(),
            [
                pos.row_label(pos.PossessionEntry("weapon", weapon))
                for weapon in familiar.natural_weapons
            ],
            title="Remove which attack?",
            empty="No Natural Weapons to remove.",
            then=lambda index: self._confirm_remove_familiar_natural_weapon(index),
        )

    def _confirm_remove_familiar_natural_weapon(self, index: int) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._confirm_delete(
            familiar.natural_weapons,
            index,
            familiar.natural_weapons[index].name or "this attack",
            "section-fam-natural-weapons",
        )

    # -- Familiar: Abilities --

    def _selected_familiar_ability(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_ability() if view is not None else None

    def _add_familiar_ability(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        exclude_names = {a.name for a in familiar.abilities}

        def handle_result(ability: Ability | None) -> None:
            if ability is not None:
                familiar.abilities.append(ability)
                self._commit("tab-fam-abilities")

        self.app.push_screen(AbilityPickerScreen(exclude_names), handle_result)

    def _edit_familiar_ability(self) -> None:
        """Edit the chosen Ability; with none chosen, ask which one."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_ability(),
            [self._ability_label(a) for a in familiar.abilities],
            title="Edit which Ability?",
            empty="No Abilities to edit.",
            then=lambda index: self._edit_familiar_ability_at(index),
        )

    def _edit_familiar_ability_at(self, index: int) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        existing = familiar.abilities[index]

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                familiar.abilities[index] = _ability_from(
                    existing.name, existing.category, result
                )
                self._commit("tab-fam-abilities")

        self.app.push_screen(
            FieldsDialog(escape(existing.name), _ability_fields(existing)),
            handle_result,
        )

    def _remove_familiar_ability(self) -> None:
        """Delete the chosen Ability (after confirming); with none chosen,
        ask which one first."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_ability(),
            [self._ability_label(a) for a in familiar.abilities],
            title="Remove an Ability",
            empty="No Abilities to remove.",
            then=lambda index: self._confirm_remove_familiar_ability(index),
        )

    def _confirm_remove_familiar_ability(self, index: int) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._confirm_delete(
            familiar.abilities,
            index,
            familiar.abilities[index].name,
            "tab-fam-abilities",
        )

    # -- Familiar: Bond Powers --

    def _selected_familiar_bond_power(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_bond_power() if view is not None else None

    def _familiar_bond_power_form(self, index: int | None) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        existing = familiar.bond_powers[index] if index is not None else None
        title = (
            "Add a Bond Power"
            if existing is None
            else f"Edit {escape(existing.name) or 'this Bond Power'}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            # "select" fields with allow_blank dismiss None for "not set";
            # BondPower uses "" like Familiar.binding_technique/_form do.
            values["technique"] = values.get("technique") or ""
            values["form"] = values.get("form") or ""
            if existing is not None:
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                familiar.bond_powers.append(
                    BondPower(
                        id=storage.generate_unique_id(
                            values.get("name") or "power",
                            [p.id for p in familiar.bond_powers],
                        ),
                        **values,
                    )
                )
            self._commit("tab-fam-powers")

        self.app.push_screen(
            FieldsDialog(title, _bond_power_fields(existing)), handle_result
        )

    def _add_familiar_bond_power(self) -> None:
        self._familiar_bond_power_form(None)

    def _edit_familiar_bond_power(self) -> None:
        """Edit the chosen Bond Power; with none chosen, ask which one."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_bond_power(),
            [escape(p.name) or "(unnamed)" for p in familiar.bond_powers],
            title="Edit which Bond Power?",
            empty="No Bond Powers to edit.",
            then=lambda index: self._familiar_bond_power_form(index),
        )

    def _remove_familiar_bond_power(self) -> None:
        """Delete the chosen Bond Power (after confirming); with none
        chosen, ask which one first."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_bond_power(),
            [escape(p.name) or "(unnamed)" for p in familiar.bond_powers],
            title="Remove a Bond Power",
            empty="No Bond Powers to remove.",
            then=lambda index: self._confirm_remove_familiar_bond_power(index),
        )

    def _confirm_remove_familiar_bond_power(self, index: int) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._confirm_delete(
            familiar.bond_powers,
            index,
            familiar.bond_powers[index].name or "this Bond Power",
            "tab-fam-powers",
        )

    # -- Familiar: Personality Traits & Reputations --

    def _selected_familiar_personality_trait(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_personality_trait() if view is not None else None

    def _selected_familiar_reputation(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_reputation() if view is not None else None

    def _virtue_flaw_target(self) -> Character | Laboratory | Familiar | None:
        if (
            self.selected_kind == NodeKind.LABORATORY
            and self._active_section() == "tab-lab-vf"
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
