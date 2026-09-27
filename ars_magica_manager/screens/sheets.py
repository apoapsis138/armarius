"""The record sheets mounted in the workspace's detail pane (Character,
Laboratory, Familiar, Covenant) and the Book and Spell list views."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.content import Content
from textual.css.query import NoMatches
from textual.widgets import (
    Button,
    Collapsible,
    Input,
    Label,
    Select,
    Static,
    TabbedContent,
    TabPane,
)
from textual.widgets._collapsible import CollapsibleTitle

from .. import books as bk
from .. import catalog
from .. import economics as eco
from .. import familiars as fam
from .. import inhabitants as inh
from .. import possessions as pos
from .. import sheet_text as st
from .. import spells as spl
from ..arts import ART_ABBREVIATIONS, ART_DESCRIPTIONS, FORMS, TECHNIQUES
from ..covenants import (
    covenant_boon_points,
    covenant_effective_aura,
    covenant_hook_points,
)
from ..laboratories import (
    lab_aura_total,
    lab_base_safety,
    lab_characteristic_total,
    lab_free_virtues,
    lab_occupied_size,
)
from ..markup import aligned, escape, markdown_inline
from ..models import (
    BOON_HOOK_DESCRIPTION,
    INHABITANT_KINDS,
    LAB_CHARACTERISTICS,
    POSSESSION_KINDS,
    SPELL_SOURCES,
    ArtScore,
    Book,
    Character,
    Covenant,
    Familiar,
    Laboratory,
    Saga,
    Spell,
    character_age,
)
from .fields import _pairs
from .widgets import (
    PinnedCollapsible,
    SelectableList,
    SheetSection,
    TwoColumns,
    _balance_colour,
    _boon_hook_names,
    _sign_colored,
    _tab_placeholder,
    _tier_text,
)

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
