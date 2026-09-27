"""Every Textual screen, dialog and widget: the saga picker, the workspace
(navigation tree + sheet pane), the Character/Laboratory/Familiar/Covenant
sheets, the Book and Spell lists, and the add/edit dialogs and pickers."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from enum import StrEnum
from functools import cached_property, partial
from pathlib import Path
from typing import Any, ClassVar, NamedTuple

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.content import Content
from textual.css.query import NoMatches
from textual.events import DescendantBlur, DescendantFocus
from textual.screen import ModalScreen, Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    Collapsible,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
    TabbedContent,
    TabPane,
    Tree,
)
from textual.widgets._collapsible import CollapsibleTitle
from textual.widgets.tree import TreeNode

from .. import books as bk
from .. import catalog, creation, storage
from .. import economics as eco
from .. import familiars as fam
from .. import inhabitants as inh
from .. import possessions as pos
from .. import sheet_text as st
from .. import spells as spl
from ..markup import aligned, escape, markdown_inline
from ..models import (
    ART_ABBREVIATIONS,
    ART_DESCRIPTIONS,
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    FORMS,
    INCOME_TYPE_DEFAULTS,
    INCOME_TYPES,
    INHABITANT_KINDS,
    LAB_CHARACTERISTICS,
    LOYALTY_EQUIPMENT,
    LOYALTY_MONEY,
    POSSESSION_KINDS,
    SEASONS,
    SPELL_SOURCES,
    TECHNIQUES,
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
    character_age,
    covenant_boon_points,
    covenant_effective_aura,
    covenant_hook_points,
    known_fields,
    lab_aura_total,
    lab_base_safety,
    lab_characteristic_total,
    lab_free_virtues,
    lab_occupied_size,
    next_season,
    replace_raw_vis,
)
from .fields import _EMPHASIS_HINT, _description_field, _pairs
from .fields import DialogField as DialogField
from .fields import FieldsDialog as FieldsDialog
from .forms import DuplicateBookScreen as DuplicateBookScreen
from .forms import EditArtsScreen as EditArtsScreen
from .forms import EditFamiliarBindingScreen as EditFamiliarBindingScreen
from .forms import ImportScreen as ImportScreen
from .forms import ImproveIncomeScreen as ImproveIncomeScreen
from .forms import MasteryEditScreen as MasteryEditScreen
from .forms import SpellImportHelperScreen as SpellImportHelperScreen
from .forms import (
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
from .pickers import AbilityPickerScreen as AbilityPickerScreen
from .pickers import CovenantBoonHookPickerScreen as CovenantBoonHookPickerScreen
from .pickers import CsvFilePickerScreen as CsvFilePickerScreen
from .pickers import LabVirtueFlawPickerScreen as LabVirtueFlawPickerScreen
from .pickers import RemovalPickerScreen as RemovalPickerScreen
from .pickers import SpellChooserScreen as SpellChooserScreen
from .pickers import VirtueFlawPickerScreen as VirtueFlawPickerScreen
from .pickers import _CsvDirectoryTree as _CsvDirectoryTree
from .prompts import AdvanceSeasonScreen as AdvanceSeasonScreen
from .prompts import ConfirmScreen as ConfirmScreen
from .prompts import (
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
from .widgets import (
    BottomBar,
    PinnedCollapsible,
    SheetSection,
    TwoColumns,
    _balance_colour,
    _boon_hook_names,
    _sign_colored,
    _tab_placeholder,
    _tier_text,
)
from .widgets import SelectableList as SelectableList
from .widgets import ThemeBar as ThemeBar

_SAGA_ITEM_ID_PREFIX = "saga-"


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


#: The covenant Library tab's sections, where 'I' imports books into the
#: covenant's library.
_LIBRARY_SECTIONS: frozenset[str] = frozenset(
    {"section-lib-summary", "section-lib-books"}
)


#: Section ids of every book list (see BookListView); 'a' in any of them adds
#: a book, and 'e'/'A' act on books everywhere but the read-only Summary.
BOOK_SECTIONS: frozenset[str] = frozenset(
    {
        "section-lib-summary",
        "section-lib-books",
        "section-lab-books",
        "section-books",
        "section-unassigned-books",
    }
)


class BookListView(Vertical):
    """A list of books (the standard selectable list, under a column header)
    with a details panel for the chosen one.

    `books` is called whenever the list is (re)built, so it always reflects
    the saga: the covenant Library tab passes "every book in the covenant", a
    laboratory or character its own books, the saga's Unassigned Books node
    the books with no owner. Docked (Library tab, Unassigned Books), the
    list stretches down to the details panel docked below it (the Library
    tab adds a read-only Summary above it); inline (a laboratory's or
    character's Books section) the panel follows the list inside the section.
    """

    DEFAULT_CSS = """
    BookListView {
        height: auto;
    }

    BookListView.docked {
        height: 1fr;
    }

    BookListView .books-body {
        height: 1fr;
    }

    BookListView #lib-summary-body {
        width: 1fr;
        height: auto;
    }

    BookListView #lib-summary-left {
        width: 1fr;
        height: auto;
        margin-right: 4;
    }

    BookListView #lib-summary-right {
        width: 1fr;
        height: auto;
    }

    /* Docked, the book list fills the space down to the details panel. */
    BookListView.docked .books-section {
        height: 1fr;
    }

    BookListView.docked .books-section.-collapsed {
        height: auto;
    }

    BookListView.docked .books-section > Contents {
        height: 1fr;
    }

    BookListView.docked SelectableList,
    BookListView.docked SelectableList:focus {
        height: 1fr;
        max-height: 100%;
    }

    BookListView .books-header {
        width: 1fr;
        height: auto;
        color: $text-muted;
    }

    BookListView .books-panel {
        width: 1fr;
        height: auto;
        padding: 0 1;
    }

    /* With the book section's own bottom padding, two rows between the list
       and the panel. */
    BookListView.docked .books-panel {
        min-height: 6;
        max-height: 14;
        margin-top: 1;
        padding: 1 2;
        background: $panel;
    }
    """

    def __init__(
        self,
        saga: Saga,
        books: Callable[[], list[Book]],
        *,
        section_id: str,
        title: str = "Books",
        summary: bool = False,
        docked: bool = True,
    ) -> None:
        super().__init__(classes="docked" if docked else "")
        self.saga = saga
        self._books_source = books
        self.section_id = section_id
        self.title_text = title
        self.summary = summary
        self.docked = docked
        self._books: list[Book] = books()
        #: Width of the Subject column, fitted to the list (see on_resize).
        self._subject_cols = bk.SUBJECT_MIN_WIDTH

    def _title(self, checked: int = 0) -> str:
        total = sum(bk.cost(b, self.saga) for b in self._books)
        title = f"{self.title_text} ({len(self._books)}) - {total} Build Points"
        return title + (f" - {checked} marked" if checked else "")

    def _rows(self) -> list[tuple[int, str]]:
        return [
            (i, bk.row_label(self.saga, b, self._subject_cols))
            for i, b in enumerate(self._books)
        ]

    def _header(self) -> str:
        # Two more columns than the header's own indent: the check mark.
        return "  " + bk.table_header(self._subject_cols)

    def on_resize(self) -> None:
        """Give the Subject column whatever room the list has."""
        # The section's padding, then the check mark and selector (4 chars).
        cols = bk.subject_width(self.size.width - 4 - 4)
        if cols == self._subject_cols:
            return
        self._subject_cols = cols
        try:
            self.query_one(".books-header", Static).update(self._header())
            self.query_one(SelectableList).relabel([label for _, label in self._rows()])
        except NoMatches:
            return

    def _book_list(self) -> ComposeResult:
        with SheetSection(
            title=self._title(), id=self.section_id, classes="books-section"
        ):
            yield Static(self._header(), classes="books-header")
            yield SelectableList(self._rows(), id=f"{self.section_id}-list", multi=True)
            if not self.docked:
                yield Static(bk.detail_text(self.saga, None), classes="books-panel")

    def compose(self) -> ComposeResult:
        if not self.docked:
            yield from self._book_list()
            return
        with Vertical(classes="books-body"):
            if self.summary:
                left, right = bk.summary_texts(self._books, self.saga)
                with (
                    SheetSection(title="Summary", id="section-lib-summary"),
                    Horizontal(id="lib-summary-body"),
                ):
                    yield Static(left, id="lib-summary-left")
                    yield Static(right, id="lib-summary-right")
            yield from self._book_list()
        yield Static(bk.detail_text(self.saga, None), classes="books-panel")

    @property
    def books(self) -> list[Book]:
        """The books listed, in row order."""
        return self._books

    def checked_books(self) -> list[Book]:
        """The books marked (Space / Ctrl+click) for acting on together."""
        try:
            indexes = self.query_one(SelectableList).checked_data_indexes
        except NoMatches:
            return []
        return [self._books[i] for i in indexes if i < len(self._books)]

    def on_selectable_list_checked(self, event: SelectableList.Checked) -> None:
        event.stop()
        section = self.query_one(f"#{self.section_id}", Collapsible)
        section.title = self._title(len(self.checked_books()))

    def selected_book(self) -> Book | None:
        index = self.query_one(SelectableList).selected_data_index
        return (
            self._books[index]
            if index is not None and index < len(self._books)
            else None
        )

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        event.stop()
        book = (
            self._books[event.data_index]
            if event.data_index < len(self._books)
            else None
        )
        self.query_one(".books-panel", Static).update(bk.detail_text(self.saga, book))

    def rebuild(self) -> None:
        """Re-read the books (an edit can add one, remove one or move it to
        another owner's list) and re-render; the chosen book stays chosen if
        it's still listed, with its panel refreshed."""
        try:
            chosen = self.selected_book()
            self._books = self._books_source()
            self.query_one(f"#{self.section_id}", Collapsible).title = self._title()
            if self.summary:
                left, right = bk.summary_texts(self._books, self.saga)
                self.query_one("#lib-summary-left", Static).update(left)
                self.query_one("#lib-summary-right", Static).update(right)
            rows = self.query_one(SelectableList)
            rows.set_rows(self._rows())
            panel = self.query_one(".books-panel", Static)
            if chosen is not None and any(b is chosen for b in self._books):
                # Posts Chosen, which refreshes the panel.
                rows.highlighted = next(
                    i for i, b in enumerate(self._books) if b is chosen
                )
            else:
                panel.update(bk.detail_text(self.saga, None))
        except NoMatches:
            return  # the sheet is being replaced


#: The Spells view's list section (a/A/e act on the saga's own spells).
SPELL_SECTION = "section-spells"


class SpellListView(Vertical):
    """The saga's Spells view: a filter bar, the list of spells (the catalog
    plus the saga's own) stretching down to a scrolling details panel.

    Filters apply as they change: a search over name and description (every
    word must match), Technique, Form (both also match a requisite), Ritual,
    Source (a book, or the saga's own), and a level range (General spells pass
    any range). The section title shows how many of how many are listed.
    """

    DEFAULT_CSS = """
    SpellListView {
        height: 1fr;
    }

    SpellListView #spell-filters {
        height: auto;
        padding: 0 1;
    }

    SpellListView .spell-filter-row {
        height: 1;
        width: 1fr;
        margin-bottom: 1;
    }

    SpellListView #spell-search {
        width: 1fr;
        margin-right: 2;
    }

    SpellListView .spell-filter-row Select {
        width: 20;
        margin-right: 1;
    }

    SpellListView .spell-filter-label {
        width: auto;
        margin-right: 1;
        color: $text-muted;
    }

    SpellListView .spell-level {
        width: 7;
        margin-right: 1;
    }

    /* The list and the panel share the height 2:1, so both stay usable on
       a small terminal. */
    SpellListView #section-spells {
        height: 2fr;
    }

    SpellListView #section-spells.-collapsed {
        height: auto;
    }

    SpellListView #section-spells > Contents {
        height: 1fr;
    }

    SpellListView .spells-header {
        width: 1fr;
        height: auto;
        color: $text-muted;
    }

    SpellListView SelectableList,
    SpellListView SelectableList:focus {
        height: 1fr;
        max-height: 100%;
    }

    SpellListView #spell-panel {
        height: 1fr;
        min-height: 4;
        margin-top: 1;
        padding: 1 2;
        background: $panel;
    }
    """

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga
        self._all: list[Spell] = spl.all_spells(saga)
        self._shown: list[Spell] = list(self._all)

    def compose(self) -> ComposeResult:
        arts_blank = "(any)"
        with Vertical(id="spell-filters"):
            with Horizontal(classes="spell-filter-row"):
                yield Input(
                    placeholder="Search spell names and descriptions...",
                    id="spell-search",
                    compact=True,
                )
                yield Select(
                    [(f"{key} - {name}", key) for key, name in SPELL_SOURCES.items()]
                    + [("The saga's own", spl.OWN_SOURCE)],
                    prompt="Source: any",
                    id="spell-source",
                    compact=True,
                )
            with Horizontal(classes="spell-filter-row"):
                yield Select(
                    _pairs(TECHNIQUES),
                    prompt=f"Technique: {arts_blank}",
                    id="spell-technique",
                    compact=True,
                )
                yield Select(
                    _pairs(FORMS),
                    prompt=f"Form: {arts_blank}",
                    id="spell-form",
                    compact=True,
                )
                yield Select(
                    [("Rituals", "yes"), ("Formulaic", "no")],
                    prompt="Ritual: any",
                    id="spell-ritual",
                    compact=True,
                )
                yield Label("Level", classes="spell-filter-label")
                yield Input(
                    placeholder="from",
                    type="integer",
                    id="spell-min-level",
                    classes="spell-level",
                    compact=True,
                )
                yield Input(
                    placeholder="to",
                    type="integer",
                    id="spell-max-level",
                    classes="spell-level",
                    compact=True,
                )
        with SheetSection(title=self._title(), id=SPELL_SECTION):
            yield Static(spl.table_header(), classes="spells-header")
            yield SelectableList(self._rows(), id="spell-list")
        with VerticalScroll(id="spell-panel"):
            yield Static(spl.detail_text(self.saga, None), id="spell-panel-text")

    def _title(self) -> str:
        return f"Spells ({len(self._shown)} of {len(self._all)})"

    def _rows(self) -> list[tuple[int, str]]:
        return [(i, spl.row_label(self.saga, s)) for i, s in enumerate(self._shown)]

    @property
    def shown(self) -> list[Spell]:
        """The spells listed, in row order (after the filters)."""
        return self._shown

    def selected_spell(self) -> Spell | None:
        index = self.query_one("#spell-list", SelectableList).selected_data_index
        return (
            self._shown[index]
            if index is not None and index < len(self._shown)
            else None
        )

    def _filters(self) -> dict[str, Any]:
        def select(widget_id: str) -> str | None:
            value = self.query_one(widget_id, Select).value
            return value if isinstance(value, str) else None

        def number(widget_id: str) -> int | None:
            try:
                return int(self.query_one(widget_id, Input).value)
            except ValueError:
                return None

        ritual = select("#spell-ritual")
        return {
            "text": self.query_one("#spell-search", Input).value,
            "technique": select("#spell-technique"),
            "form": select("#spell-form"),
            "ritual": None if ritual is None else ritual == "yes",
            "source": select("#spell-source"),
            "min_level": number("#spell-min-level"),
            "max_level": number("#spell-max-level"),
        }

    def refilter(self) -> None:
        """Re-apply the filters (and re-read the spells, after an edit); the
        chosen spell stays chosen if it's still listed."""
        try:
            chosen = self.selected_spell()
            self._all = spl.all_spells(self.saga)
            self._shown = spl.filter_spells(self.saga, self._all, **self._filters())
            self.query_one(f"#{SPELL_SECTION}", Collapsible).title = self._title()
            rows = self.query_one("#spell-list", SelectableList)
            rows.set_rows(self._rows())
            position = next(
                (i for i, sp in enumerate(self._shown) if sp is chosen), None
            )
            if position is not None:
                rows.highlighted = position  # posts Chosen -> refreshes the panel
            else:
                self._show(None)
        except NoMatches:
            return

    def _show(self, spell: Spell | None) -> None:
        self.query_one("#spell-panel-text", Static).update(
            spl.detail_text(self.saga, spell)
        )
        self.query_one("#spell-panel", VerticalScroll).scroll_home(animate=False)

    def on_input_changed(self, event: Input.Changed) -> None:
        event.stop()
        self.refilter()

    def on_select_changed(self, event: Select.Changed) -> None:
        event.stop()
        self.refilter()

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        event.stop()
        index = event.data_index
        self._show(self._shown[index] if index < len(self._shown) else None)


class SheetView(Vertical):
    """Base of the four record sheets (Character, Laboratory, Familiar,
    Covenant) that WorkspaceScreen mounts into its detail pane: a fixed top
    panel above a TabbedContent. Holds the saga, the flag the workspace uses
    to tell the TabbedContent's first TabActivated from a real tab switch,
    and the layout rules every sheet shares."""

    DEFAULT_CSS = """
    SheetView {
        height: 1fr;
    }

    SheetView TabbedContent {
        height: 1fr;
    }

    SheetView TabPane {
        padding: 1 0;
    }

    SheetView VerticalScroll {
        height: 1fr;
        width: 1fr;
    }

    /* A selectable list's details panel: a gap below the list and its own
       shaded background, so it reads as a distinct panel. */
    SheetView .details-panel {
        width: 1fr;
        height: auto;
        min-height: 6;
        margin-top: 1;
        padding: 1 2;
        background: $panel;
    }

    /* The column headings above a table-like list. */
    SheetView .table-header {
        width: 1fr;
        height: auto;
        color: $text-muted;
    }
    """

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga
        #: Set once TabbedContent's initial TabActivated has been seen -- see
        #: WorkspaceScreen.on_tabbed_content_tab_activated().
        self.initial_tab_seen = False
        #: Per section id, what refresh_section() re-renders, in compose
        #: order. Filled while composing by _static()/_list()/_on_refresh(),
        #: so a widget's render call is written once, where it's built.
        self._refreshers: dict[str, list[Callable[[], None]]] = {}

    def refresh_section(self, section_id: str) -> None:
        """Re-render whatever shows `section_id` after its data changed. An
        id the sheet doesn't show does nothing (a change can be committed
        while another kind of sheet is on show)."""
        for refresh in self._refreshers.get(section_id, ()):
            try:
                refresh()
            except NoMatches:
                # The sheet is being replaced or torn down (a refresh from a
                # dialog callback can land after that).
                return

    def _on_refresh(
        self, sections: str | tuple[str, ...], refresh: Callable[[], None]
    ) -> None:
        """Run `refresh` whenever any of `sections` is refreshed."""
        for section in (sections,) if isinstance(sections, str) else sections:
            self._refreshers.setdefault(section, []).append(refresh)

    def _static(
        self,
        sections: str | tuple[str, ...],
        text: Callable[[], str],
        *,
        id: str,
        **kwargs: Any,
    ) -> Static:
        """A Static showing `text()`, re-rendered when `sections` refresh."""
        self._on_refresh(
            sections, lambda: self.query_one(f"#{id}", Static).update(text())
        )
        return Static(text(), id=id, **kwargs)

    def _list(
        self,
        sections: str | tuple[str, ...],
        rows: Callable[[], Sequence[tuple[int | None, str]]],
        *,
        id: str,
        group: str | None = None,
    ) -> SelectableList:
        """A SelectableList of `rows()`, re-filled when `sections` refresh."""
        self._on_refresh(
            sections, lambda: self.query_one(f"#{id}", SelectableList).set_rows(rows())
        )
        return SelectableList(rows(), id=id, group=group)

    @staticmethod
    def _inherited(value: str) -> str:
        """Dim a value that's derived or inherited (e.g. from the saga) and
        isn't edited here."""
        return f"[dim]{escape(value)}[/]"


class CharacterSheetView(SheetView):
    """The character sheet mounted into WorkspaceScreen's detail pane.

    A fixed top panel (Info above Characteristics -- not inside any tab,
    permanently expanded, same PinnedCollapsible pattern as
    CovenantSheetView/LaboratorySheetView) above the tabbed body. This is
    STORY-207's finished layout -- tab order: Description, Abilities,
    Virtues & Flaws, Hermetic Magic (magi only), Inventory, Laboratory
    (magi only), Diary.

    - Description (tab, id "tab-description"): Hermetic Background (magi
      only), Biographical Detail (merged Background + Description + the
      new Biography field), Personality Traits and Reputations (side by
      side), Aging & Warping, Health (merged Wounds + Fatigue, two
      columns, two independent Edit affordances).
    - Abilities (tab, id "tab-abilities"): a flat pane (no Collapsible)
      with the Abilities list and its details panel.
    - Virtues & Flaws (tab, id "tab-vf"): Virtues and Flaws as two
      independently-collapsible sections side by side (mirroring
      CovenantSheetView's Boons/Hooks), with one details panel below both,
      separate from either section.
    - Hermetic Magic (tab, id "tab-hermetic", magi only): Magical Arts
      (a PinnedCollapsible, not a toggleable SheetSection -- two side-by-
      side selectable columns, Techniques then Forms, each row Name/Level/
      XP; 'e' still opens EditArtsScreen to edit every Art at once), Raw
      Vis (the first of two duplicated instances, both backed by
      character.raw_vis and both mounted at once -- refresh_section()
      updates both lists regardless of which section id triggered it, so
      switching tabs never shows stale data), and Known Spells (folded in
      from the old "Spells" tab). The three lists (Techniques, Forms,
      Known Spells) share one details panel docked at the tab's bottom,
      outside every section -- see _refresh_hermetic_info().
    - Inventory (tab, id "tab-inventory"): Raw Vis (magi only, the second
      of the two duplicated instances -- see Hermetic Magic above),
      Personal Gear (renamed from "Inventory", same character.inventory
      data), Books.
    - Laboratory (tab, id "tab-lab", magi only) and Diary (tab, id
      "tab-diary", every character type): flat placeholder panes, no
      Collapsible, mirroring CovenantSheetView's own Diary placeholder
      (see the module-level _tab_placeholder() helper both share). Neither
      is in _CHARACTER_DISPATCH_TABS, so switching to either clears focus
      and 'e' falls back to editing the top panel -- the flat-tab
      focus-fallback logic every earlier slice set up for exactly this.
    """

    DEFAULT_CSS = """
    CharacterSheetView #char-top-panel {
        width: 1fr;
        height: auto;
    }

    CharacterSheetView #section-vf-virtues {
        margin-right: 2;
    }

    CharacterSheetView #hermetic-body {
        height: 1fr;
    }

    CharacterSheetView #arts-techniques-col {
        margin-right: 2;
    }

    CharacterSheetView .arts-col-title {
        text-style: bold;
    }

    CharacterSheetView .arts-header {
        color: $text-muted;
    }
    """

    def __init__(self, saga: Saga, character: Character) -> None:
        super().__init__(saga)
        self.character = character

    def compose(self) -> ComposeResult:
        character = self.character
        yield from self._top_panel()
        with TabbedContent(initial="tab-description"):
            with TabPane("Description", id="tab-description"):
                yield from self._description_tab()
            with TabPane("Abilities", id="tab-abilities"), VerticalScroll():
                yield self._list(
                    "tab-abilities", self._ability_rows, id="abilities-list"
                )
                yield self._static(
                    "tab-abilities",
                    lambda: self._ability_info_text(None),
                    id="ability-info",
                    classes="details-panel",
                )
            with TabPane("Virtues & Flaws", id="tab-vf"):
                yield from self._virtues_flaws_tab()
            if character.type == "magus":
                with TabPane("Hermetic Magic", id="tab-hermetic"):
                    yield from self._hermetic_tab()
            with TabPane("Inventory", id="tab-inventory"):
                yield from self._inventory_tab()
            if character.type == "magus":
                with TabPane("Laboratory", id="tab-lab"):
                    yield Static(_tab_placeholder("Laboratory"))
            with TabPane("Diary", id="tab-diary"):
                yield Static(_tab_placeholder("Diary"))

    def _top_panel(self) -> ComposeResult:
        """The always-visible info and Characteristics panels above the
        tabs."""
        character = self.character
        with Vertical(id="char-top-panel"):
            with PinnedCollapsible(
                title=escape(character.name), id="section-char-info"
            ):
                with TwoColumns(id="char-info-body"):
                    yield self._static(
                        "section-char-info", self._info_left_text, id="char-info-left"
                    )
                    yield self._static(
                        "section-char-info",
                        self._info_right_text,
                        id="char-info-right",
                    )
                yield Button("Edit (e)", id="btn-char-info-edit", compact=True)
            self._on_refresh("section-char-info", self._refresh_title)
            with PinnedCollapsible(
                title="Characteristics", id="section-char-characteristics"
            ):
                yield self._static(
                    "section-char-characteristics",
                    self._characteristics_text,
                    id="char-characteristics-content",
                )
                yield Button(
                    "Edit (e)", id="btn-char-characteristics-edit", compact=True
                )

    def _refresh_title(self) -> None:
        self.query_one("#section-char-info", Collapsible).title = self.character.name

    def _description_tab(self) -> ComposeResult:
        """Hermetic Background (magi), Biographical Detail, Personality
        Traits and Reputations, Aging & Warping, and Health."""
        character = self.character
        with VerticalScroll():
            if character.type == "magus":
                with (
                    SheetSection(
                        title="Hermetic Background",
                        id="section-hermetic-background",
                    ),
                    TwoColumns(id="hermetic-background-row"),
                ):
                    yield self._static(
                        "section-hermetic-background",
                        self._hermetic_background_left_text,
                        id="hermetic-background-left",
                    )
                    yield self._static(
                        "section-hermetic-background",
                        self._hermetic_background_right_text,
                        id="hermetic-background-right",
                    )
            with (
                SheetSection(
                    title="Biographical Detail", id="section-char-biographical"
                ),
                TwoColumns(id="char-biographical-row"),
            ):
                yield self._static(
                    "section-char-biographical",
                    self._biographical_left_text,
                    id="char-biographical-left",
                )
                yield self._static(
                    "section-char-biographical",
                    self._biographical_right_text,
                    id="char-biographical-right",
                )
            with TwoColumns(id="pt-rep-row"):
                with SheetSection(
                    title="Personality Traits", id="section-personality-traits"
                ):
                    yield self._list(
                        "section-personality-traits",
                        self._personality_trait_rows,
                        id="personality-traits-list",
                    )
                with SheetSection(title="Reputations", id="section-reputations"):
                    yield self._list(
                        "section-reputations",
                        self._reputation_rows,
                        id="character-reputations-list",
                    )
            with SheetSection(title="Aging & Warping", id="section-aging"):
                yield self._static(
                    "section-aging", self._aging_text, id="aging-content"
                )
            with (
                SheetSection(title="Health", id="section-char-health"),
                TwoColumns(id="char-health-row"),
            ):
                with Vertical(id="char-health-wounds-col"):
                    yield self._static(
                        "section-char-health", self._wounds_text, id="wounds-content"
                    )
                    yield Button(
                        "Edit Wounds (e)",
                        id="btn-char-health-wounds-edit",
                        compact=True,
                    )
                with Vertical(id="char-health-fatigue-col"):
                    yield self._static(
                        "section-char-health", self._fatigue_text, id="fatigue-content"
                    )
                    yield Button(
                        "Edit Fatigue",
                        id="btn-char-health-fatigue-edit",
                        compact=True,
                    )

    def _virtues_flaws_tab(self) -> ComposeResult:
        """The Virtue and Flaw lists side by side, and the details panel."""
        vf_sections = ("section-vf-virtues", "section-vf-flaws")
        with VerticalScroll():
            with TwoColumns(id="vf-row"):
                with SheetSection(title="Virtues", id="section-vf-virtues"):
                    yield self._list(
                        vf_sections,
                        lambda: self._vf_rows("Virtue"),
                        id="vf-virtues-list",
                        group="vf",
                    )
                with SheetSection(title="Flaws", id="section-vf-flaws"):
                    yield self._list(
                        vf_sections,
                        lambda: self._vf_rows("Flaw"),
                        id="vf-flaws-list",
                        group="vf",
                    )
            yield self._static(
                vf_sections,
                lambda: self._vf_info_text(None),
                id="vf-info",
                classes="details-panel",
            )

    #: Raw Vis deliberately appears twice (Hermetic Magic and Inventory tabs),
    #: both backed by character.raw_vis and both mounted at once
    #: (TabbedContent keeps inactive panes mounted, just hidden): either
    #: section id refreshes both lists, so neither goes stale.
    _RAW_VIS_SECTIONS = ("section-raw-vis-hermetic", "section-raw-vis-inventory")

    def _hermetic_tab(self) -> ComposeResult:
        """Magical Arts, Raw Vis and Known Spells (scrolling), and the
        details panel docked below them. Magi only."""
        with Vertical(id="hermetic-body"):
            with VerticalScroll(id="hermetic-scroll"):
                with (
                    PinnedCollapsible(title="Magical Arts", id="section-arts"),
                    TwoColumns(id="arts-row"),
                ):
                    with Vertical(id="arts-techniques-col"):
                        yield Static("Techniques", classes="arts-col-title")
                        yield Static(
                            self._arts_header_text(),
                            classes="arts-header",
                        )
                        yield self._list(
                            "section-arts",
                            lambda: self._arts_rows(TECHNIQUES),
                            id="arts-techniques-list",
                            group="hermetic",
                        )
                    with Vertical(id="arts-forms-col"):
                        yield Static("Forms", classes="arts-col-title")
                        yield Static(
                            self._arts_header_text(),
                            classes="arts-header",
                        )
                        yield self._list(
                            "section-arts",
                            lambda: self._arts_rows(FORMS),
                            id="arts-forms-list",
                            group="hermetic",
                        )
                with SheetSection(title="Raw Vis", id="section-raw-vis-hermetic"):
                    yield self._list(
                        self._RAW_VIS_SECTIONS,
                        self._raw_vis_rows,
                        id="raw-vis-list-hermetic",
                    )
                with SheetSection(title="Known Spells", id="section-known-spells"):
                    yield self._list(
                        "section-known-spells",
                        self._known_spell_rows,
                        id="known-spells-list",
                        group="hermetic",
                    )
            yield Static(
                "[dim]Select an Art or a Known Spell to see its details.[/]",
                id="hermetic-info",
                classes="details-panel",
            )
            self._on_refresh(
                ("section-arts", "section-known-spells"), self._refresh_hermetic_info
            )

    def _inventory_tab(self) -> ComposeResult:
        """Raw Vis (magi), Personal Gear and the character's Books."""
        character = self.character
        with VerticalScroll():
            if character.type == "magus":
                with SheetSection(title="Raw Vis", id="section-raw-vis-inventory"):
                    yield self._list(
                        self._RAW_VIS_SECTIONS,
                        self._raw_vis_rows,
                        id="raw-vis-list-inventory",
                    )
            with SheetSection(title="Personal Gear", id="section-inventory"):
                yield self._list(
                    "section-inventory", self._inventory_rows, id="inventory-list"
                )
                yield self._static(
                    "section-inventory",
                    lambda: self._inventory_info_text(None),
                    id="inventory-info",
                    classes="details-panel",
                )
            yield BookListView(
                self.saga,
                lambda: bk.books_owned_by(self.saga, "character", character.id),
                section_id="section-books",
                docked=False,
            )

    def selected_personality_trait(self) -> int | None:
        """Index into character.personality_traits of the chosen row, or None."""
        return self.query_one(
            "#personality-traits-list", SelectableList
        ).selected_data_index

    def selected_reputation(self) -> int | None:
        """Index into character.reputations of the chosen row, or None."""
        return self.query_one(
            "#character-reputations-list", SelectableList
        ).selected_data_index

    def selected_raw_vis(self, section_id: str) -> int | None:
        """Index into sorted(character.raw_vis) of the chosen row in
        whichever of the two Raw Vis lists `section_id` (one of
        "section-raw-vis-hermetic"/"section-raw-vis-inventory") names, or
        None."""
        list_id = (
            "#raw-vis-list-hermetic"
            if section_id == "section-raw-vis-hermetic"
            else "#raw-vis-list-inventory"
        )
        return self.query_one(list_id, SelectableList).selected_data_index

    def selected_known_spell(self) -> int | None:
        """Index into character.spells_known of the chosen row, or None."""
        return self.query_one("#known-spells-list", SelectableList).selected_data_index

    def selected_inventory_item(self) -> int | None:
        """Index into character.inventory of the chosen row, or None."""
        return self.query_one("#inventory-list", SelectableList).selected_data_index

    def selected_ability(self) -> int | None:
        """Index into character.abilities of the chosen row, or None."""
        return self.query_one("#abilities-list", SelectableList).selected_data_index

    def selected_virtue_flaw(self) -> int | None:
        """Index into character.virtues_flaws of the row chosen in either
        the Virtues or the Flaws list, or None if neither has one chosen."""
        virtues = self.query_one("#vf-virtues-list", SelectableList).selected_data_index
        if virtues is not None:
            return virtues
        return self.query_one("#vf-flaws-list", SelectableList).selected_data_index

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        list_id = event.selectable_list.id or ""
        if list_id == "abilities-list":
            event.stop()
            self.query_one("#ability-info", Static).update(
                self._ability_info_text(event.data_index)
            )
            return
        if list_id == "inventory-list":
            event.stop()
            self.query_one("#inventory-info", Static).update(
                self._inventory_info_text(event.data_index)
            )
            return
        if list_id in ("arts-techniques-list", "arts-forms-list", "known-spells-list"):
            event.stop()
            # One group (one selection across the three), one details panel.
            self._refresh_hermetic_info()
            return
        if list_id not in ("vf-virtues-list", "vf-flaws-list"):
            return
        event.stop()
        # A Virtue or Flaw row was chosen (the other list is unchosen: same
        # group): fill the details panel.
        self.query_one("#vf-info", Static).update(self._vf_info_text(event.data_index))

    def _info_left_text(self) -> str:
        b = self.character.background
        age = character_age(b.year_born, self.saga.current_year)
        return aligned(
            [
                ("Setting", b.setting or "(not set)"),
                (
                    "Age",
                    age if age is not None else "(unknown -- set Year Born)",
                ),
                ("Current Year", self._inherited(str(self.saga.current_year))),
                ("Current Season", self._inherited(self.saga.current_season)),
            ]
        )

    def _info_right_text(self) -> str:
        saga, character = self.saga, self.character
        covenant = saga.covenant(character.covenant_id)
        rows = [("Covenant", escape(covenant.name) if covenant else "(unassigned)")]
        if character.type == "magus":
            lab = saga.laboratory(character.assigned_lab_id)
            rows.append(
                ("Assigned Laboratory", escape(lab.name) if lab else "(unassigned)")
            )
        b = character.background
        rows += [
            ("Type", character.type),
            ("Confidence Score", str(b.confidence_score)),
            ("Confidence Points", str(b.confidence_points)),
            ("Size", str(b.size)),
        ]
        return aligned(rows)

    def _biographical_left_text(self) -> str:
        """Column 1 of Biographical Detail: every field except Biography
        (column 2, see _biographical_right_text()) -- the remaining
        Background fields (Setting/Confidence/Size live in the top panel)
        plus every Description field but the free-text Biography box."""
        b, d = self.character.background, self.character.description
        return "\n".join(
            [
                f"Player: {escape(b.player) or '(not set)'}",
                f"Birth Name: {escape(b.birth_name) or '(not set)'}",
                f"Year Born: {b.year_born if b.year_born is not None else '(not set)'}",
                f"Race/Nationality: {escape(b.race_nationality) or '(not set)'}",
                f"Place of Origin: {escape(b.place_of_origin) or '(not set)'}",
                f"Religion: {escape(b.religion) or '(not set)'}",
                f"Title/Profession: {escape(b.title_profession) or '(not set)'}",
                f"Height: {d.height if d.height is not None else '(not set)'}",
                f"Weight: {d.weight if d.weight is not None else '(not set)'}",
                f"Hair: {escape(d.hair) or '(not set)'}",
                f"Eyes: {escape(d.eyes) or '(not set)'}",
                f"Handedness: {d.handedness}",
                f"Physical Description: "
                f"{escape(d.physical_description) or '(not set)'}",
            ]
        )

    def _biographical_right_text(self) -> str:
        """Column 2 of Biographical Detail: just the free-text Biography
        box (distinct from Physical Description -- see Description's
        docstring in models.py)."""
        return escape(self.character.description.biography) or "(none recorded)"

    def _characteristics_text(self) -> str:
        return st.characteristics_text(self.character.characteristics)

    def _ability_rows(self) -> list[tuple[int | None, str]]:
        return st.ability_rows(self.character.abilities)

    def _ability_info_text(self, index: int | None) -> str:
        return st.ability_info_text(self.character.abilities, index)

    def _vf_rows(self, vf_type: str) -> list[tuple[int | None, str]]:
        return st.vf_rows(self.character.virtues_flaws, vf_type)

    def _vf_info_text(self, index: int | None) -> str:
        return st.vf_info_text(self.character.virtues_flaws, index)

    def _aging_text(self) -> str:
        a = self.character.aging
        return "\n".join(
            [
                f"Decrepitude: {a.decrepitude}",
                "Effects of Aging:",
                escape(a.effects) or "(none recorded)",
                "",
                f"Warping: {a.warping_score}/{a.warping_points}",
            ]
        )

    def _personality_trait_rows(self) -> list[tuple[int | None, str]]:
        return st.trait_rows(self.character.personality_traits)

    def _reputation_rows(self) -> list[tuple[int | None, str]]:
        # Unsigned, unlike every other Reputation list (STORY-1109 B14).
        return st.trait_rows(self.character.reputations, signed=False)

    def _wounds_text(self) -> str:
        return st.wounds_text(self.character.wounds, with_soak=True)

    def _fatigue_text(self) -> str:
        return st.fatigue_text(self.character.fatigue_level)

    def _raw_vis_rows(self) -> list[tuple[int | None, str]]:
        return [
            (index, f"{art.title()}: {self.character.raw_vis[art]} pawn(s)")
            for index, art in enumerate(sorted(self.character.raw_vis))
        ]

    def _hermetic_background_left_text(self) -> str:
        """Column 1 of Hermetic Background: everything but Wizard's Sigil
        (column 2, see _hermetic_background_right_text())."""
        h = self.character.hermetic
        house_catalog = catalog.load_house_catalog_by_id()
        house = house_catalog.get(h.house) if h.house else None
        return "\n".join(
            [
                f"House: {escape(house.name) if house else '(not set)'}",
                f"Domus Magna: {escape(h.domus_magna) or '(not set)'}",
                f"Primus: {escape(h.primus) or '(not set)'}",
                f"Parens: {escape(h.parens) or '(not set)'}",
                f"Covenant of Apprenticeship: "
                f"{escape(h.covenant_of_apprenticeship) or '(not set)'}",
                f"Age of Apprenticeship: "
                f"{h.age_of_apprenticeship if h.age_of_apprenticeship is not None else '(not set)'}",
            ]
        )

    def _hermetic_background_right_text(self) -> str:
        """Column 2 of Hermetic Background: just Wizard's Sigil."""
        sigil = self.character.hermetic.wizards_sigil
        return f"Wizard's Sigil: {escape(sigil) or '(not set)'}"

    _ARTS_NAME_WIDTH: ClassVar[int] = 16
    _ARTS_NUM_WIDTH: ClassVar[int] = 6

    def _arts_header_text(self) -> str:
        """Column titles above an Arts list, aligned with _art_row_label()
        (the two-character indent is the list's selector marker)."""
        return (
            f"  {'':<{self._ARTS_NAME_WIDTH}}"
            f"{'Level':>{self._ARTS_NUM_WIDTH}}{'XP':>{self._ARTS_NUM_WIDTH}}"
        )

    def _art_row_label(self, art: str) -> str:
        score = self.character.arts.get(art.lower(), ArtScore())
        name = f"{art} ({ART_ABBREVIATIONS[art]})"
        return (
            f"{name:<{self._ARTS_NAME_WIDTH}}"
            f"{score.level:>{self._ARTS_NUM_WIDTH}}{score.xp:>{self._ARTS_NUM_WIDTH}}"
        )

    def _arts_rows(self, arts: Sequence[str]) -> list[tuple[int, str]]:
        return [(i, self._art_row_label(art)) for i, art in enumerate(arts)]

    def _art_info_text(self, art: str) -> str:
        score = self.character.arts.get(art.lower(), ArtScore())
        return "\n".join(
            [
                f"[b]Name:[/] {art} ({ART_ABBREVIATIONS[art]})",
                f"[b]Level:[/] {score.level}    [b]XP:[/] {score.xp}",
                "",
                f"[b]Description:[/] {ART_DESCRIPTIONS[art]}",
            ]
        )

    def _refresh_hermetic_info(self) -> None:
        """The Hermetic Magic tab's single details panel, shared by the
        Magical Arts columns and Known Spells (only one of the three lists
        has a selection at a time -- see on_selectable_list_chosen())."""
        try:
            info = self.query_one("#hermetic-info", Static)
        except NoMatches:
            return
        index = self.query_one(
            "#arts-techniques-list", SelectableList
        ).selected_data_index
        if index is not None:
            info.update(self._art_info_text(TECHNIQUES[index]))
            return
        index = self.query_one("#arts-forms-list", SelectableList).selected_data_index
        if index is not None:
            info.update(self._art_info_text(FORMS[index]))
            return
        index = self.query_one("#known-spells-list", SelectableList).selected_data_index
        info.update(self._known_spell_info_text(index))

    def _known_spell_rows(self) -> list[tuple[int | None, str]]:
        rows: list[tuple[int | None, str]] = []
        for index, known in enumerate(self.character.spells_known):
            spell = spl.find_spell(self.saga, known.spell_id)
            if spell is None:
                rows.append((index, f"{escape(known.spell_id)} (unknown spell)"))
                continue
            label = spl.row_label(self.saga, spell)
            if known.mastery_score:
                label += f"  [b]Mastery {known.mastery_score}[/]"
            rows.append((index, label))
        return rows

    def _known_spell_info_text(self, index: int | None) -> str:
        if index is None:
            return "[dim]Select a spell to see its details.[/]"
        known = self.character.spells_known[index]
        spell = spl.find_spell(self.saga, known.spell_id)
        if spell is None:
            lines = [f"[red]Unknown spell: {escape(known.spell_id)}[/]"]
        else:
            lines = [spl.detail_text(self.saga, spell)]
        lines += [
            "",
            "[b]Mastery:[/]",
            f"Score {known.mastery_score}, XP {known.mastery_xp}",
        ]
        if known.mastery_abilities:
            for ability in known.mastery_abilities:
                lines.append(f"  {escape(ability.name)} {ability.level}/{ability.xp}")
        else:
            lines.append("  (no Mastery Abilities)")
        return "\n".join(lines)

    #: Character Inventory's group headers, in display order.
    _INVENTORY_KINDS: ClassVar[tuple[str, ...]] = ("weapon", "armor", "item")
    _INVENTORY_HEADERS: ClassVar[dict[str, str]] = {
        "weapon": "Weapons",
        "armor": "Armor",
        "item": "Other Items",
    }

    def _inventory_rows(self) -> list[tuple[int | None, str]]:
        """One selectable list for all of Inventory, with a header row before
        each non-empty kind (Weapons, Armor, Other Items)."""
        rows: list[tuple[int | None, str]] = []
        for kind in self._INVENTORY_KINDS:
            indexed = [
                (i, item)
                for i, item in enumerate(self.character.inventory)
                if item.kind == kind
            ]
            if not indexed:
                continue
            rows.append((None, self._INVENTORY_HEADERS[kind]))
            for index, item in indexed:
                rows.append((index, pos.row_label(pos.PossessionEntry(kind, item))))
        return rows

    def _inventory_info_text(self, index: int | None) -> str:
        if index is None:
            return "[dim]Select an item for its details.[/]"
        item = self.character.inventory[index]
        return pos.detail_text(pos.PossessionEntry(item.kind, item))


class LaboratorySheetView(SheetView):
    """The laboratory sheet mounted into WorkspaceScreen's detail pane.

    A fixed top panel (Identity above Characteristics -- not inside any
    tab, permanently expanded) above a 5-tab body mirroring the
    sheet's own pages: Planning (placeholder), Virtues & Flaws, Attributes
    (Specialties/Features/Rooms), Inventory (Raw Vis/Items), Diary. Its
    lists are still read-only Statics edited through pickers, not the
    selectable lists the other sheets use (STORY-303).
    """

    DEFAULT_CSS = """
    LaboratorySheetView #lab-top-panel {
        width: 1fr;
        height: auto;
    }

    LaboratorySheetView #lab-characteristics-body {
        width: 1fr;
        height: auto;
    }

    LaboratorySheetView #lab-characteristics-derived {
        width: auto;
        height: auto;
        margin-right: 6;
    }

    LaboratorySheetView #lab-characteristics-content {
        width: auto;
        height: auto;
    }
    """

    def __init__(self, saga: Saga, laboratory: Laboratory) -> None:
        super().__init__(saga)
        self.laboratory = laboratory

    def compose(self) -> ComposeResult:
        with Vertical(id="lab-top-panel"):
            with PinnedCollapsible(title="Identity", id="section-lab-identity"):
                yield self._static(
                    "section-lab-identity",
                    self._identity_text,
                    id="lab-identity-content",
                )
                yield Button("Edit (e)", id="btn-lab-identity-edit", compact=True)
            with PinnedCollapsible(
                title="Characteristics", id="section-lab-characteristics"
            ):
                with Horizontal(id="lab-characteristics-body"):
                    yield self._static(
                        "section-lab-characteristics",
                        self._characteristics_derived_text,
                        id="lab-characteristics-derived",
                    )
                    yield self._static(
                        "section-lab-characteristics",
                        self._characteristics_table_text,
                        id="lab-characteristics-content",
                    )
                yield Button(
                    "Edit (e)", id="btn-lab-characteristics-edit", compact=True
                )
        with TabbedContent(initial="tab-lab-planning"):
            with TabPane("Planning", id="tab-lab-planning"):
                yield self._static(
                    "tab-lab-planning", self._planning_text, id="lab-planning-content"
                )
            with TabPane("Virtues & Flaws", id="tab-lab-vf"):
                yield self._static("tab-lab-vf", self._vf_text, id="lab-vf-content")
            with TabPane("Attributes", id="tab-lab-attributes"), VerticalScroll():
                with SheetSection(title="Specialties", id="section-lab-specialties"):
                    yield self._static(
                        "section-lab-specialties",
                        self._specialties_text,
                        id="lab-specialties-content",
                    )
                with SheetSection(title="Features", id="section-lab-features"):
                    yield self._static(
                        "section-lab-features",
                        self._features_text,
                        id="lab-features-content",
                    )
                with SheetSection(title="Rooms", id="section-lab-rooms"):
                    yield self._static(
                        "section-lab-rooms", self._rooms_text, id="lab-rooms-content"
                    )
            with TabPane("Inventory", id="tab-lab-inventory"), VerticalScroll():
                with SheetSection(title="Raw Vis", id="section-lab-raw-vis"):
                    yield self._static(
                        "section-lab-raw-vis",
                        self._raw_vis_text,
                        id="lab-raw-vis-content",
                    )
                with SheetSection(title="Items", id="section-lab-items"):
                    yield self._static(
                        "section-lab-items", self._items_text, id="lab-items-content"
                    )
                yield BookListView(
                    self.saga,
                    lambda: bk.books_owned_by(
                        self.saga, "laboratory", self.laboratory.id
                    ),
                    section_id="section-lab-books",
                    docked=False,
                )
            with TabPane("Diary", id="tab-lab-diary"):
                yield self._static(
                    "tab-lab-diary", self._diary_text, id="lab-diary-content"
                )

    def _identity_text(self) -> str:
        saga, lab = self.saga, self.laboratory
        covenant = saga.covenant(lab.covenant_id)
        owner = saga.character(lab.owner_id)
        # Inherited from the covenant, including any Boons that raise it.
        covenant_aura = (
            covenant_effective_aura(
                covenant, catalog.load_covenant_boon_hook_catalog_by_id()
            )
            if covenant
            else 0
        )
        return "\n".join(
            [
                f"Name: {escape(lab.name)}",
                f"Location: {escape(lab.location) or '(not set)'}",
                f"Points: {lab.build_points}",
                f"Owner: {escape(owner.name) if owner else '(unassigned)'}",
                f"Covenant: {escape(covenant.name) if covenant else '(none)'}",
                f"Aura: {covenant_aura} (covenant) {lab.aura_modifier:+d} (modifier) "
                f"= {lab_aura_total(lab, covenant_aura)}",
            ]
        )

    def _characteristics_derived_text(self) -> str:
        lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
        lab = self.laboratory
        rows = [
            ("Occupied Size:", lab_occupied_size(lab, lab_catalog)),
            ("Free Virtues:", lab_free_virtues(lab, lab_catalog)),
            ("Base Safety:", lab_base_safety(lab, lab_catalog)),
        ]
        width = max(len(label) for label, _ in rows)
        return "\n".join(
            f"{label:<{width}} {_sign_colored(value, f'{value:g}')}"
            for label, value in rows
        )

    def _characteristics_table_text(self) -> str:
        """The 8 Characteristics as an aligned table: manual value, the
        summed Virtue+Flaw modifier, and the total after '='. Every number
        is coloured by sign (see _sign_colored())."""
        lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
        lab = self.laboratory
        rows = []
        for characteristic in LAB_CHARACTERISTICS:
            manual, virtue_sum, flaw_sum, total = lab_characteristic_total(
                lab, lab_catalog, characteristic
            )
            label = characteristic.replace("_", " ").title() + ":"
            rows.append((label, manual, virtue_sum + flaw_sum, total))
        label_width = max(len(label) for label, *_ in rows)
        num_width = max(
            len(f"{value:+d}")
            for _, manual, vf, total in rows
            for value in (manual, vf, total)
        )

        def cell(value: int) -> str:
            return _sign_colored(value, f"{value:>+{num_width}d}")

        return "\n".join(
            f"{label:<{label_width}} {cell(manual)} {cell(vf)} = {cell(total)}"
            for label, manual, vf, total in rows
        )

    def _planning_text(self) -> str:
        return "Lab activity planning isn't built yet -- coming in a future update."

    def _vf_text(self) -> str:
        if not self.laboratory.virtues_flaws:
            return "(none recorded)"

        lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
        lines: list[str] = []
        for vf_type in ("Virtue", "Flaw"):
            entries = [
                vf
                for vf in self.laboratory.virtues_flaws
                if (definition := lab_catalog.get(vf.vf_id)) is not None
                and definition.type == vf_type
            ]
            if not entries:
                continue
            lines.append(f"{vf_type}s:")
            for vf in entries:
                definition = lab_catalog.get(vf.vf_id)
                tier = definition.tier if definition is not None else "?"
                lines.append(
                    f"  {escape(catalog.describe_virtue_flaw(vf, lab_catalog))} "
                    f"({tier})"
                )
            lines.append("")
        return "\n".join(lines).rstrip()

    def _specialties_text(self) -> str:
        if not self.laboratory.specialties:
            return "(none recorded)"
        return "\n".join(f"  - {escape(s)}" for s in self.laboratory.specialties)

    def _features_text(self) -> str:
        if not self.laboratory.features:
            return "(none recorded)"
        return "\n".join(f"  - {escape(f)}" for f in self.laboratory.features)

    def _rooms_text(self) -> str:
        if not self.laboratory.rooms:
            return "(none recorded)"
        return "\n".join(
            f"  {escape(room.name)}: {escape(room.description) or '(no description)'}"
            for room in self.laboratory.rooms
        )

    def _raw_vis_text(self) -> str:
        if not self.laboratory.raw_vis:
            return "(none recorded)"
        return "\n".join(
            f"{art.title()}: {pawns} pawn(s)"
            for art, pawns in sorted(self.laboratory.raw_vis.items())
        )

    def _items_text(self) -> str:
        if not self.laboratory.inventory_items:
            return "(none recorded)"
        return "\n".join(
            f"  {escape(item.name)}: {escape(item.description) or '(no description)'}"
            for item in self.laboratory.inventory_items
        )

    def _diary_text(self) -> str:
        if not self.laboratory.diary:
            return "(none recorded)"
        lines = []
        for entry in self.laboratory.diary:
            lines.append(f"{entry.year} {entry.season} -- {escape(entry.name)}")
            if entry.details:
                lines.append(f"  {escape(entry.details)}")
        return "\n".join(lines)


class FamiliarSheetView(SheetView):
    """The Familiar sheet mounted into WorkspaceScreen's detail pane.

    A fixed top panel (Familiar Info -- not inside any tab, permanently
    expanded, same PinnedCollapsible pattern as the other sheets) above a
    5-tab body mirroring reference/familiar-rules-and-sheet.md: Identity &
    Cords (Binding & Cords, Virtues & Flaws, Personality Traits &
    Reputations), Characteristics (the 8 Characteristics plus the typed-in
    Base Soak/Magic Resistance figures) and Combat & Health (Wounds/Fatigue,
    reusing Character's own dialogs; Natural Weapons & Attacks, a free
    selectable list of weapon-kind Possessions -- same shape as Character's
    weapon rows, see STORY-205), Abilities and Bond Powers.
    """

    DEFAULT_CSS = """
    FamiliarSheetView #fam-top-panel {
        width: 1fr;
        height: auto;
    }
    """

    def __init__(self, saga: Saga, familiar: Familiar) -> None:
        super().__init__(saga)
        self.familiar = familiar

    def compose(self) -> ComposeResult:
        with (
            Vertical(id="fam-top-panel"),
            PinnedCollapsible(title="Familiar Info", id="section-fam-info"),
        ):
            yield self._static(
                "section-fam-info",
                lambda: fam.identity_text(self.saga, self.familiar),
                id="fam-info-content",
            )
            yield Button("Edit (e)", id="btn-fam-info-edit", compact=True)
        with TabbedContent(initial="tab-fam-identity"):
            with TabPane("Identity & Cords", id="tab-fam-identity"):
                yield from self._identity_tab()
            with (
                TabPane("Characteristics", id="tab-fam-characteristics"),
                SheetSection(title="Characteristics", id="section-fam-characteristics"),
            ):
                yield self._static(
                    "section-fam-characteristics",
                    lambda: fam.characteristics_text(self.familiar),
                    id="fam-characteristics-content",
                )
            with TabPane("Combat & Health", id="tab-fam-combat"):
                yield from self._combat_tab()
            with TabPane("Abilities", id="tab-fam-abilities"), VerticalScroll():
                yield Static(
                    "[dim]Languages: shares the Magus partner's Language "
                    "scores automatically.[/]"
                )
                yield self._list(
                    "tab-fam-abilities",
                    lambda: fam.ability_rows(self.familiar),
                    id="fam-abilities-list",
                )
                yield self._static(
                    "tab-fam-abilities",
                    lambda: fam.ability_info_text(self.familiar, None),
                    id="fam-ability-info",
                )
            with TabPane("Bond Powers", id="tab-fam-powers"), VerticalScroll():
                yield self._list(
                    "tab-fam-powers",
                    lambda: fam.bond_power_rows(self.familiar),
                    id="fam-bond-powers-list",
                )
                yield self._static(
                    "tab-fam-powers",
                    lambda: fam.bond_power_info_text(self.familiar, None),
                    id="fam-bond-powers-info",
                )

    def _identity_tab(self) -> ComposeResult:
        """Binding & Cords, the Virtue and Flaw lists with their details
        panel, and Personality Traits and Reputations."""
        vf_sections = ("section-fam-vf-virtues", "section-fam-vf-flaws")
        with VerticalScroll():
            with SheetSection(title="Binding & Cords", id="section-fam-binding"):
                yield self._static(
                    "section-fam-binding", self._binding_text, id="fam-binding-content"
                )
            with TwoColumns(id="fam-vf-row"):
                with SheetSection(title="Virtues", id="section-fam-vf-virtues"):
                    yield self._list(
                        vf_sections,
                        lambda: fam.vf_rows(self.familiar, "Virtue"),
                        id="fam-vf-virtues-list",
                        group="fam-vf",
                    )
                with SheetSection(title="Flaws", id="section-fam-vf-flaws"):
                    yield self._list(
                        vf_sections,
                        lambda: fam.vf_rows(self.familiar, "Flaw"),
                        id="fam-vf-flaws-list",
                        group="fam-vf",
                    )
            yield self._static(
                vf_sections,
                lambda: fam.vf_info_text(self.familiar, None),
                id="fam-vf-info",
            )
            with TwoColumns(id="fam-pt-rep-row"):
                with SheetSection(
                    title="Personality Traits", id="section-fam-personality-traits"
                ):
                    yield self._list(
                        "section-fam-personality-traits",
                        lambda: fam.personality_trait_rows(self.familiar),
                        id="fam-personality-traits-list",
                    )
                with SheetSection(title="Reputations", id="section-fam-reputations"):
                    yield self._list(
                        "section-fam-reputations",
                        lambda: fam.reputation_rows(self.familiar),
                        id="fam-reputations-list",
                    )

    def _combat_tab(self) -> ComposeResult:
        """Health (Wounds and Fatigue) and Natural Weapons & Attacks."""
        with VerticalScroll():
            with (
                SheetSection(title="Health", id="section-fam-health"),
                TwoColumns(id="fam-health-row"),
            ):
                with Vertical(id="fam-health-wounds-col"):
                    yield self._static(
                        "section-fam-health",
                        lambda: fam.wounds_text(self.familiar),
                        id="fam-wounds-content",
                    )
                    yield Button(
                        "Edit Wounds (e)",
                        id="btn-fam-health-wounds-edit",
                        compact=True,
                    )
                with Vertical(id="fam-health-fatigue-col"):
                    yield self._static(
                        "section-fam-health",
                        lambda: fam.fatigue_text(self.familiar),
                        id="fam-fatigue-content",
                    )
                    yield Button(
                        "Edit Fatigue",
                        id="btn-fam-health-fatigue-edit",
                        compact=True,
                    )
            with SheetSection(
                title="Natural Weapons & Attacks",
                id="section-fam-natural-weapons",
            ):
                yield self._list(
                    "section-fam-natural-weapons",
                    lambda: fam.natural_weapon_rows(self.familiar),
                    id="fam-natural-weapons-list",
                )
                yield self._static(
                    "section-fam-natural-weapons",
                    lambda: fam.natural_weapon_info_text(self.familiar, None),
                    id="fam-natural-weapons-info",
                )

    def _binding_text(self) -> str:
        return f"{fam.binding_text(self.familiar)}\n\n{fam.cords_text(self.familiar)}"

    def selected_virtue_flaw(self) -> int | None:
        """Index into familiar.virtues_flaws of the row chosen in either the
        Virtues or the Flaws list, or None if neither has one chosen."""
        virtues = self.query_one(
            "#fam-vf-virtues-list", SelectableList
        ).selected_data_index
        if virtues is not None:
            return virtues
        return self.query_one("#fam-vf-flaws-list", SelectableList).selected_data_index

    def selected_personality_trait(self) -> int | None:
        return self.query_one(
            "#fam-personality-traits-list", SelectableList
        ).selected_data_index

    def selected_reputation(self) -> int | None:
        return self.query_one(
            "#fam-reputations-list", SelectableList
        ).selected_data_index

    def selected_natural_weapon(self) -> int | None:
        return self.query_one(
            "#fam-natural-weapons-list", SelectableList
        ).selected_data_index

    def selected_ability(self) -> int | None:
        return self.query_one("#fam-abilities-list", SelectableList).selected_data_index

    def selected_bond_power(self) -> int | None:
        return self.query_one(
            "#fam-bond-powers-list", SelectableList
        ).selected_data_index

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        list_id = event.selectable_list.id or ""
        if list_id == "fam-natural-weapons-list":
            event.stop()
            self.query_one("#fam-natural-weapons-info", Static).update(
                fam.natural_weapon_info_text(self.familiar, event.data_index)
            )
            return
        if list_id == "fam-abilities-list":
            event.stop()
            self.query_one("#fam-ability-info", Static).update(
                fam.ability_info_text(self.familiar, event.data_index)
            )
            return
        if list_id == "fam-bond-powers-list":
            event.stop()
            self.query_one("#fam-bond-powers-info", Static).update(
                fam.bond_power_info_text(self.familiar, event.data_index)
            )
            return
        if list_id not in ("fam-vf-virtues-list", "fam-vf-flaws-list"):
            return
        event.stop()
        self.query_one("#fam-vf-info", Static).update(
            fam.vf_info_text(self.familiar, event.data_index)
        )


class CovenantSheetView(SheetView):
    """The covenant sheet mounted into WorkspaceScreen's detail pane.

    A permanent info panel (not inside any tab) above six tabs mirroring
    the covenant record sheet: Attributes, Inhabitants, Possessions,
    Economics, Library, Diary (still a placeholder).

    The panel's saga-level values (Saga, Storyguide, Current Season,
    Current Year) are inherited from the Saga and shown dimmed/read-only;
    the rest belong to the covenant and are edited with 'e'.
    """

    DEFAULT_CSS = """
    CovenantSheetView #cov-info-left {
        margin-right: 4;
    }

    CovenantSheetView #section-cov-boons {
        margin-right: 2;
    }

    CovenantSheetView #cov-bh-info {
        min-height: 8;
    }

    CovenantSheetView #inh-body,
    CovenantSheetView #pos-body,
    CovenantSheetView #eco-body {
        height: 1fr;
    }

    CovenantSheetView #inh-loyalty-left,
    CovenantSheetView #inh-misc-left,
    CovenantSheetView #eco-wealth-left {
        margin-right: 4;
    }

    /* The details panels docked below a scrolling tab stop growing at 14
       rows. */
    CovenantSheetView #inh-panel,
    CovenantSheetView #pos-panel,
    CovenantSheetView #eco-panel {
        max-height: 14;
    }
    """

    def __init__(self, saga: Saga, covenant: Covenant) -> None:
        super().__init__(saga)
        self.covenant = covenant

    def compose(self) -> ComposeResult:
        with PinnedCollapsible(title=escape(self.covenant.name), id="section-cov-info"):
            with TwoColumns(id="cov-info-body"):
                yield Static(self._info_left_text(), id="cov-info-left")
                yield Static(self._info_right_text(), id="cov-info-right")
            yield Button("Edit (e)", id="btn-cov-edit", compact=True)
        with TabbedContent(initial="tab-cov-attributes"):
            with TabPane("Attributes", id="tab-cov-attributes"), VerticalScroll():
                with SheetSection(title="Description", id="section-cov-description"):
                    yield Static(self._description_text(), id="cov-description-content")
                with SheetSection(title="Reputations", id="section-cov-reputations"):
                    yield SelectableList(
                        self._reputation_rows(), id="cov-reputations-list"
                    )
                with TwoColumns(id="cov-bh-row"):
                    with SheetSection(
                        title=self._bh_title("Boon"), id="section-cov-boons"
                    ):
                        yield SelectableList(
                            self._bh_entries("Boon"), id="cov-boons-list", group="bh"
                        )
                    with SheetSection(
                        title=self._bh_title("Hook"), id="section-cov-hooks"
                    ):
                        yield SelectableList(
                            self._bh_entries("Hook"), id="cov-hooks-list", group="bh"
                        )
                yield Static(
                    self._bh_info_text(None), id="cov-bh-info", classes="details-panel"
                )
            with TabPane("Inhabitants", id="tab-cov-inhabitants"):
                yield from self._inhabitants_tab()
            with TabPane("Possessions", id="tab-cov-possessions"):
                yield from self._possessions_tab()
            with TabPane("Economics", id="tab-cov-economics"):
                yield from self._economics_tab()
            with TabPane("Library", id="tab-cov-library"):
                yield BookListView(
                    self.saga,
                    lambda: bk.books_in_covenant(self.saga, self.covenant),
                    section_id="section-lib-books",
                    summary=True,
                )
            with TabPane("Diary", id="tab-cov-diary"):
                yield Static(_tab_placeholder("Diary"))

    def _inhabitants_tab(self) -> ComposeResult:
        """Loyalty, the Inhabitants summary and Miscellaneous blocks, one
        collapsible list per kind of inhabitant, and (docked below the
        scrolling part) the details panel of the chosen inhabitant."""
        covenant, saga = self.covenant, self.saga
        with Vertical(id="inh-body"):
            with VerticalScroll(id="inh-scroll"):
                with (
                    SheetSection(title="Loyalty", id="section-inh-loyalty"),
                    TwoColumns(id="inh-loyalty-body"),
                ):
                    yield Static(
                        inh.loyalty_left_text(saga, covenant), id="inh-loyalty-left"
                    )
                    yield Static(
                        inh.loyalty_right_text(saga, covenant), id="inh-loyalty-right"
                    )
                with SheetSection(title="Inhabitants", id="section-inh-population"):
                    yield Static(
                        inh.population_text(saga, covenant), id="inh-population-content"
                    )
                with SheetSection(title="Miscellaneous", id="section-inh-misc"):
                    left, right = inh.misc_text(covenant)
                    with TwoColumns(id="inh-misc-body"):
                        yield Static(left, id="inh-misc-left")
                        yield Static(right, id="inh-misc-right")
                for kind in INHABITANT_KINDS:
                    with SheetSection(
                        title=self._inh_title(kind), id=f"section-inh-{kind}"
                    ):
                        yield Static(
                            inh.table_header(kind), classes="table-header inh-header"
                        )
                        yield SelectableList(
                            self._inh_rows(kind), id=f"inh-{kind}-list", group="inh"
                        )
            yield Static(
                inh.detail_text(None, saga.current_year),
                id="inh-panel",
                classes="details-panel",
            )

    def _possessions_tab(self) -> ComposeResult:
        """One collapsible list per kind of possession over the details panel of
        the chosen one (docked below the scrolling part)."""
        with Vertical(id="pos-body"):
            with VerticalScroll(id="pos-scroll"):
                for kind in POSSESSION_KINDS:
                    with SheetSection(
                        title=pos.KIND_TITLES[kind], id=f"section-pos-{kind}"
                    ):
                        yield Static(
                            pos.table_header(kind), classes="table-header pos-header"
                        )
                        yield SelectableList(
                            self._pos_rows(kind), id=f"pos-{kind}-list", group="pos"
                        )
            yield Static(pos.detail_text(None), id="pos-panel", classes="details-panel")

    #: The three lists of the Economics tab (one selection across them).
    _ECO_LISTS: ClassVar[tuple[str, ...]] = ("income", "expenditure", "savings")

    def _economics_tab(self) -> ComposeResult:
        """Wealth, Sources of Income, Yearly Expenditure and Cost Savings over
        the details panel of the chosen row (docked below the scrolling part)."""
        summary = eco.summarize(self.saga, self.covenant)
        left, right = eco.wealth_texts(summary)
        with Vertical(id="eco-body"):
            with VerticalScroll(id="eco-scroll"):
                with (
                    SheetSection(title="Wealth", id="section-eco-wealth"),
                    TwoColumns(id="eco-wealth-body"),
                ):
                    yield Static(left, id="eco-wealth-left")
                    yield Static(right, id="eco-wealth-right")
                with SheetSection(title="Sources of Income", id="section-eco-income"):
                    yield Static(
                        eco.source_table_header(), classes="table-header eco-header"
                    )
                    yield SelectableList(
                        self._eco_rows("income", summary),
                        id="eco-income-list",
                        group="eco",
                    )
                with SheetSection(
                    title="Yearly Expenditure", id="section-eco-expenditure"
                ):
                    yield Static(
                        eco.table_header("Cost"), classes="table-header eco-header"
                    )
                    yield SelectableList(
                        self._eco_rows("expenditure", summary),
                        id="eco-expenditure-list",
                        group="eco",
                    )
                with SheetSection(title="Cost Savings", id="section-eco-savings"):
                    yield Static(
                        eco.table_header("Quantity"), classes="table-header eco-header"
                    )
                    yield SelectableList(
                        self._eco_rows("savings", summary),
                        id="eco-savings-list",
                        group="eco",
                    )
            yield Static(
                eco.source_detail_text(None), id="eco-panel", classes="details-panel"
            )

    def _eco_rows(self, which: str, summary: eco.Summary) -> list[tuple[int, str]]:
        if which == "income":
            sources = self.covenant.economics.income_sources
            return [(i, eco.source_row_label(s)) for i, s in enumerate(sources)]
        rows = summary.expenditure if which == "expenditure" else summary.savings
        return [(i, eco.row_label(row)) for i, row in enumerate(rows)]

    def selected_economics(self, which: str) -> int | None:
        """Index of the chosen row of the `which` list ("income" indexes the
        covenant's income sources; the others index the summary's rows)."""
        return self.query_one(f"#eco-{which}-list", SelectableList).selected_data_index

    def _eco_panel_text(self, which: str, index: int, summary: eco.Summary) -> str:
        if which == "income":
            sources = self.covenant.economics.income_sources
            return eco.source_detail_text(
                sources[index] if index < len(sources) else None
            )
        rows = summary.expenditure if which == "expenditure" else summary.savings
        first = "Cost" if which == "expenditure" else "Quantity"
        return eco.row_detail_text(rows[index] if index < len(rows) else None, first)

    def _rebuild_economics(self) -> None:
        """Recalculate everything on the tab. Anything on the sheet can move a
        figure (a new inhabitant, a laboratory's usage, the salary), so this
        also runs after edits made on other tabs. The chosen row stays chosen
        and its panel is refreshed."""
        summary = eco.summarize(self.saga, self.covenant)
        left, right = eco.wealth_texts(summary)
        self.query_one("#eco-wealth-left", Static).update(left)
        self.query_one("#eco-wealth-right", Static).update(right)
        any_chosen = False
        for which in self._ECO_LISTS:
            rows_list = self.query_one(f"#eco-{which}-list", SelectableList)
            chosen = rows_list.selected_data_index
            rows_list.set_rows(self._eco_rows(which, summary))
            # Posts Chosen, which refreshes the panel.
            if chosen is not None and rows_list.select_data_index(chosen):
                any_chosen = True
        if not any_chosen:
            self.query_one("#eco-panel", Static).update(eco.source_detail_text(None))

    def _pos_entries(self, kind: str) -> list[pos.PossessionEntry]:
        return pos.entries_for_kind(
            self.saga, self.covenant, kind, catalog.load_lab_virtue_flaw_catalog_by_id()
        )

    def _pos_rows(self, kind: str) -> list[tuple[int, str]]:
        return [(i, pos.row_label(e)) for i, e in enumerate(self._pos_entries(kind))]

    def selected_possession(self, kind: str) -> int | None:
        """Index into the `kind` list's entries of the chosen row, or None."""
        return self.query_one(f"#pos-{kind}-list", SelectableList).selected_data_index

    def _rebuild_possessions(self) -> None:
        """Re-render every list and reset the panel."""
        for kind in POSSESSION_KINDS:
            self.query_one(f"#pos-{kind}-list", SelectableList).set_rows(
                self._pos_rows(kind)
            )
        self.query_one("#pos-panel", Static).update(pos.detail_text(None))

    def _inh_entries(self, kind: str) -> list[inh.InhabitantEntry]:
        return inh.entries_for_kind(self.saga, self.covenant, kind)

    def _inh_rows(self, kind: str) -> list[tuple[int, str]]:
        return [(i, inh.row_label(e)) for i, e in enumerate(self._inh_entries(kind))]

    def _inh_title(self, kind: str) -> str:
        """ "Magi (1)": the list's headcount -- quantities added up."""
        return f"{inh.KIND_TITLES[kind]} ({inh.headcount(self._inh_entries(kind))})"

    def selected_inhabitant(self, kind: str) -> int | None:
        """Index into the `kind` list's entries of the chosen row, or None."""
        return self.query_one(f"#inh-{kind}-list", SelectableList).selected_data_index

    def _rebuild_inhabitants(self) -> None:
        """Re-render every list, its title, the population total and the panel
        (any change can move the headcounts and the calculated total)."""
        for kind in INHABITANT_KINDS:
            self._set_section_title(
                self.query_one(f"#section-inh-{kind}", Collapsible),
                self._inh_title(kind),
            )
            self.query_one(f"#inh-{kind}-list", SelectableList).set_rows(
                self._inh_rows(kind)
            )
        self.query_one("#inh-population-content", Static).update(
            inh.population_text(self.saga, self.covenant)
        )
        self.query_one("#inh-panel", Static).update(
            inh.detail_text(None, self.saga.current_year)
        )

    def refresh_section(self, section_id: str) -> None:
        try:
            self._refresh_section(section_id)
            if section_id.startswith(("section-inh-", "section-pos-", "section-cov-")):
                # These feed the Economics tab's figures.
                self._rebuild_economics()
            if section_id in ("section-cov-info", "section-cov-reputations") or (
                section_id.startswith("section-inh-")
                and section_id != "section-inh-loyalty"
            ):
                # Magi (Gift), Specialists/Companions (role bonus), covenant
                # Reputations and Living Conditions (Mundane) all feed the
                # Loyalty block, which lives on a different section.
                self._refresh_loyalty_text()
        except NoMatches:
            # The sheet is being replaced or torn down (a refresh from a
            # dialog callback can land after that) -- nothing left to update.
            return

    def _refresh_loyalty_text(self) -> None:
        self.query_one("#inh-loyalty-left", Static).update(
            inh.loyalty_left_text(self.saga, self.covenant)
        )
        self.query_one("#inh-loyalty-right", Static).update(
            inh.loyalty_right_text(self.saga, self.covenant)
        )

    def _refresh_section(self, section_id: str) -> None:
        if section_id == "section-cov-info":
            self.query_one("#section-cov-info", Collapsible).title = escape(
                self.covenant.name
            )
            self.query_one("#cov-info-left", Static).update(self._info_left_text())
            self.query_one("#cov-info-right", Static).update(self._info_right_text())
        elif section_id == "section-cov-description":
            self.query_one("#cov-description-content", Static).update(
                self._description_text()
            )
        elif section_id == "section-cov-reputations":
            self.query_one("#cov-reputations-list", SelectableList).set_rows(
                self._reputation_rows()
            )
        elif section_id == "section-inh-loyalty":
            self._refresh_loyalty_text()
        elif section_id in ("section-inh-population", "section-inh-misc"):
            self.query_one("#inh-population-content", Static).update(
                inh.population_text(self.saga, self.covenant)
            )
            left, right = inh.misc_text(self.covenant)
            self.query_one("#inh-misc-left", Static).update(left)
            self.query_one("#inh-misc-right", Static).update(right)
        elif section_id.startswith("section-inh-"):
            self._rebuild_inhabitants()
        elif section_id.startswith("section-pos-"):
            self._rebuild_possessions()
        elif section_id.startswith("section-eco-"):
            self._rebuild_economics()
        elif section_id in ("section-cov-boons", "section-cov-hooks"):
            self._rebuild_boons_hooks()
            # An Aura Boon changes the Aura shown in the info panel.
            self.refresh_section("section-cov-info")

    def _rebuild_boons_hooks(self) -> None:
        """Re-render both lists, both titles and the details panel. Always
        both: the two titles share one colour driven by comparing the totals,
        so a change to either kind can change the other's title too."""
        for kind in ("Boon", "Hook"):
            self._set_section_title(
                self.query_one(f"#section-cov-{kind.lower()}s", Collapsible),
                self._bh_title(kind),
            )
            self.query_one(f"#cov-{kind.lower()}s-list", SelectableList).set_rows(
                self._bh_entries(kind)
            )
        self.query_one("#cov-bh-info", Static).update(self._bh_info_text(None))

    def selected_boon_hook(self, kind: str) -> int | None:
        """Index into covenant.boons_hooks of the row currently selected in
        the `kind` ("Boon"/"Hook") list, or None if none is."""
        return self.query_one(
            f"#cov-{kind.lower()}s-list", SelectableList
        ).selected_data_index

    def selected_reputation(self) -> int | None:
        """Index into covenant.reputations of the chosen row, or None."""
        return self.query_one(
            "#cov-reputations-list", SelectableList
        ).selected_data_index

    @staticmethod
    def _set_section_title(section: Collapsible, title: str) -> None:
        """Set a section's title, forcing the label to repaint. Textual's
        Content compares equal on plain text alone, so a colour-only change
        (Hooks (7 pts) turning red) would otherwise leave the old colour
        showing."""
        section.title = title
        title_widget = section.query_one(CollapsibleTitle)
        # The label reactive skips "unchanged" values too, so store the new
        # Content directly (set_reactive bypasses that check), then repaint.
        title_widget.set_reactive(type(title_widget).label, Content.from_text(title))
        title_widget._update_label()

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A Boon or Hook row was chosen: fill the details panel. (Reputations
        have no panel -- a name and a score have nothing more to show.)"""
        list_id = event.selectable_list.id or ""
        if list_id.startswith("eco-") and list_id.endswith("-list"):
            event.stop()
            which = list_id[len("eco-") : -len("-list")]
            self.query_one("#eco-panel", Static).update(
                self._eco_panel_text(
                    which, event.data_index, eco.summarize(self.saga, self.covenant)
                )
            )
            return
        if list_id.startswith("inh-") and list_id.endswith("-list"):
            event.stop()
            kind = list_id[len("inh-") : -len("-list")]
            entries = self._inh_entries(kind)
            chosen = (
                entries[event.data_index] if event.data_index < len(entries) else None
            )
            self.query_one("#inh-panel", Static).update(
                inh.detail_text(chosen, self.saga.current_year)
            )
            return
        if list_id.startswith("pos-") and list_id.endswith("-list"):
            event.stop()
            kind = list_id[len("pos-") : -len("-list")]
            entries = self._pos_entries(kind)
            chosen = (
                entries[event.data_index] if event.data_index < len(entries) else None
            )
            self.query_one("#pos-panel", Static).update(pos.detail_text(chosen))
            return
        if list_id not in ("cov-boons-list", "cov-hooks-list"):
            return
        event.stop()
        self.query_one("#cov-bh-info", Static).update(
            self._bh_info_text(event.data_index)
        )

    def _aura_text(self) -> str:
        """The base Aura, plus where a Boon-raised total comes from."""
        cov = self.covenant
        effective = covenant_effective_aura(
            cov, catalog.load_covenant_boon_hook_catalog_by_id()
        )
        if effective == cov.aura:
            return str(cov.aura)
        return f"{effective} (base {cov.aura}, {effective - cov.aura:+d} Boons)"

    def _info_left_text(self) -> str:
        cov, saga = self.covenant, self.saga
        founded = "(not set)" if cov.year_founded is None else str(cov.year_founded)
        return aligned(
            [
                ("Saga", self._inherited(saga.name)),
                ("Storyguide", self._inherited(saga.storyguide or "(not set)")),
                ("Year Founded", founded),
                ("Aegis of the Hearth", str(cov.aegis_of_the_hearth)),
                ("Living Conditions (Magi)", str(cov.living_conditions_magi)),
                ("Aura", self._aura_text()),
            ]
        )

    def _info_right_text(self) -> str:
        cov, saga = self.covenant, self.saga
        return aligned(
            [
                ("Tribunal", escape(cov.tribunal) if cov.tribunal else "(not set)"),
                ("Current Season", self._inherited(saga.current_season)),
                ("Current Year", self._inherited(str(saga.current_year))),
                ("Aegis' Penetration", str(cov.aegis_penetration)),
                ("Living Conditions (Mundane)", str(cov.living_conditions_mundane)),
                ("Covenant Season", cov.covenant_season),
            ]
        )

    def _description_text(self) -> str:
        # Backed by Covenant.notes (the free-text field set at creation).
        text = self.covenant.notes.strip()
        return markdown_inline(text) if text else "(no description)"

    def _reputation_rows(self) -> list[tuple[int, str]]:
        """The covenant's Reputations as (index, label) rows. A bad Reputation
        the covenant doesn't know about is marked -- it doesn't count against
        Loyalty until it's known (see inhabitants.reputation_loyalty_penalty)."""
        return [
            (
                index,
                f"{escape(r.name)}: {r.score:+d}"
                + ("" if r.known else " [dim](not known by the covenant)[/]"),
            )
            for index, r in enumerate(self.covenant.reputations)
        ]

    def _bh_title(self, kind: str) -> str:
        """ "Boons (7 pts)" / "Hooks (7 pts)": Boons show the points they
        cost, Hooks the points they provide. The parenthesised total of BOTH
        titles takes one colour from comparing the two (see _balance_colour)."""
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        boons = covenant_boon_points(self.covenant, by_id)
        hooks = covenant_hook_points(self.covenant, by_id)
        points = boons if kind == "Boon" else hooks
        colour = _balance_colour(boons, hooks)
        unit = "pt" if points == 1 else "pts"
        return f"{kind}s [{colour}]({points:g} {unit})[/]"

    def _bh_entries(self, kind: str) -> list[tuple[int, str]]:
        """The attached Boons or Hooks of `kind` as (index into
        covenant.boons_hooks, display label) pairs, in attach order."""
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        return [
            (index, escape(catalog.describe_boon_hook(bh, by_id)))
            for index, bh in enumerate(self.covenant.boons_hooks)
            if bh.vf_id in by_id and by_id[bh.vf_id].type == kind
        ]

    def _bh_info_text(self, index: int | None) -> str:
        """The details panel for the attached Boon/Hook at `index` into
        covenant.boons_hooks: its name, type, notes, the user's own
        description (if any) and then the official rules text."""
        if index is None:
            return "[dim]Select a Boon or Hook to read its rules.[/]"
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        instance = self.covenant.boons_hooks[index]
        definition = by_id.get(instance.vf_id)
        if definition is None:
            return escape(f"{instance.vf_id} (not in catalog)")

        lines = [f"[b]Name:[/] {escape(catalog.describe_boon_hook(instance, by_id))}"]
        if definition.category:
            lines.append(f"[b]Type:[/] {definition.category}")
        lines.append(f"[b]Tier:[/] {_tier_text(definition)}")
        if definition.requires:
            lines.append(
                f"[b]Requires:[/] {_boon_hook_names(definition.requires, by_id)}"
            )
        if definition.excludes:
            lines.append(
                f"[b]Not with:[/] {_boon_hook_names(definition.excludes, by_id)}"
            )
        lines += st.effect_lines(definition.modifiers)
        if definition.repeatable:
            lines.append("[dim]May be taken more than once; the effects stack.[/]")
        # The user's own description leads; the official rules text follows.
        description = instance.params.get(BOON_HOOK_DESCRIPTION, "").strip()
        if description:
            lines += ["", "[b]Description:[/]", markdown_inline(description)]
        lines += ["", "[b]Rules:[/]", escape(definition.description)]
        return "\n".join(lines)


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


class SagaPickerScreen(Screen[None]):
    """Lists existing sagas; offers to create a new one or delete one."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("n", "create_saga", "New Saga"),
        ("A", "delete_saga", "Delete Saga"),
        Binding("delete", "delete_saga", "Delete Saga", show=False),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Select a saga to open, press 'n' to create a new one, "
            "or 'A' to delete the highlighted one.",
            id="picker-hint",
        )
        yield ListView(id="saga-list")
        yield BottomBar()

    async def on_mount(self) -> None:
        await self.refresh_list()

    async def refresh_list(self) -> None:
        list_view = self.query_one("#saga-list", ListView)
        # Must be awaited before re-adding items below, or a same-id item not
        # yet removed collides with its freshly-mounted replacement and
        # Textual raises DuplicateIds.
        await list_view.clear()

        saga_ids = storage.list_sagas()
        if not saga_ids:
            await list_view.append(
                ListItem(Label("No sagas yet -- press 'n' to create one."))
            )
            return

        items = []
        for saga_id in saga_ids:
            saga = storage.load_saga(saga_id)
            summary = (
                f"{escape(saga.name)}  —  "
                f"Storyguide: {escape(saga.storyguide) or '(unset)'}"
                f"  —  {saga.current_season} {saga.current_year}"
            )
            items.append(
                ListItem(Label(summary), id=f"{_SAGA_ITEM_ID_PREFIX}{saga_id}")
            )
        await list_view.extend(items)
        # append()/extend() don't set an initial highlight the way construction-time
        # children do, so keyboard/enter selection wouldn't work without this.
        list_view.index = 0

    def action_create_saga(self) -> None:
        async def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                storage.save_saga(
                    creation.new_saga(
                        values["name"],
                        values["storyguide"],
                        values["description"],
                        values["year"],
                        values["season"],
                    )
                )
                await self.refresh_list()

        self.app.push_screen(
            FieldsDialog("Create a New Saga", _saga_fields(None), save_label="Create"),
            handle_result,
        )

    def action_delete_saga(self) -> None:
        """Delete the highlighted saga's file, after confirming: this is
        permanent, so the message says so and No is the default."""
        item = self.query_one("#saga-list", ListView).highlighted_child
        if (
            item is None
            or item.id is None
            or not item.id.startswith(_SAGA_ITEM_ID_PREFIX)
        ):
            self.notify("No saga to delete.")
            return
        saga_id = item.id.removeprefix(_SAGA_ITEM_ID_PREFIX)
        try:
            name = storage.load_saga(saga_id).name
        except OSError, ValueError, TypeError, KeyError:
            name = saga_id  # unreadable file: still let it be deleted by id

        async def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                storage.delete_saga(saga_id)
                list_view = self.query_one("#saga-list", ListView)
                index = list_view.index or 0
                await self.refresh_list()
                remaining = len(storage.list_sagas())
                if remaining:  # keep the highlight near where it was
                    list_view.index = min(index, remaining - 1)

        self.app.push_screen(
            ConfirmScreen(
                f"Delete the saga {escape(name)}?\n\n"
                "Everything in it (covenants, characters, laboratories, "
                "library) is deleted for good. This cannot be undone.",
                yes_label="Delete",
            ),
            handle_confirmed,
        )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None or not item_id.startswith(_SAGA_ITEM_ID_PREFIX):
            return
        saga_id = item_id.removeprefix(_SAGA_ITEM_ID_PREFIX)
        saga = storage.load_saga(saga_id)
        self.app.push_screen(WorkspaceScreen(saga))
