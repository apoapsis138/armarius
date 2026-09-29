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
from .. import catalog, faith
from .. import covenant_diary as cov_diary
from .. import economics as eco
from .. import enchanted_devices as ed
from .. import familiars as fam
from .. import inhabitants as inh
from .. import laboratories as lab_text
from .. import possessions as pos
from .. import sheet_text as st
from .. import spells as spl
from ..arts import ART_ABBREVIATIONS, ART_DESCRIPTIONS, FORMS, TECHNIQUES
from ..covenants import (
    UNKNOWN_HOOK_POINTS,
    boon_hook_is_unknown,
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
    DetailsPanel,
    PinnedCollapsible,
    SelectableList,
    SheetSection,
    StackingColumns,
    TableHeader,
    ToggleList,
    TwoColumns,
    _boon_hook_names,
    _sign_colored,
    _tab_placeholder,
    _tier_text,
    counted,
    match_colour,
    points_title,
)

#: The covenant Library tab's sections, where 'I' imports books into the
#: covenant's library.
_LIBRARY_SECTIONS: frozenset[str] = frozenset(
    {"section-lib-summary", "section-lib-books"}
)


#: The Enchanted Devices section of each sheet (STORY-305), and the kind of
#: holder whose devices it lists.
DEVICE_SECTIONS: dict[str, str] = {
    "section-char-devices": "character",
    "section-lab-devices": "laboratory",
    "section-cov-devices": "covenant",
}


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
    list stretches down to its details panel docked below it (the Library
    tab adds a read-only Summary above it). Inline (a character's or
    laboratory's Inventory tab) it's just a section with no panel of its
    own: Chosen bubbles up to the sheet, which shows the book in the tab's
    shared panel, and `group` shares one choice with the tab's other lists.
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
        group: str | None = None,
    ) -> None:
        super().__init__(classes="docked" if docked else "")
        self.group = group
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
        title = counted(self.title_text, len(self._books))
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
            yield TableHeader(self._header(), classes="books-header")
            yield SelectableList(
                self._rows(), id=f"{self.section_id}-list", multi=True, group=self.group
            )

    def compose(self) -> ComposeResult:
        if not self.docked:
            yield from self._book_list()
            return
        with Vertical(classes="books-body"):
            if self.summary:
                left, right = bk.summary_texts(self._books, self.saga)
                with (
                    SheetSection(title="Summary", id="section-lib-summary"),
                    TwoColumns(id="lib-summary-body", text=True),
                ):
                    yield Static(left, id="lib-summary-left")
                    yield Static(right, id="lib-summary-right")
            yield from self._book_list()
        yield DetailsPanel(bk.detail_text(self.saga, None), text_classes="books-panel")

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
        if not self.docked:
            return  # the sheet shows it
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
            if chosen is not None and any(b is chosen for b in self._books):
                # Posts Chosen, which refreshes the panel.
                rows.highlighted = next(
                    i for i, b in enumerate(self._books) if b is chosen
                )
            elif self.docked:
                self.query_one(".books-panel", Static).update(
                    bk.detail_text(self.saga, None)
                )
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

    SpellListView SelectableList,
    SpellListView SelectableList:focus {
        height: 1fr;
        max-height: 100%;
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
            yield TableHeader(spl.table_header())
            yield SelectableList(self._rows(), id="spell-list")
        yield DetailsPanel(spl.detail_text(self.saga, None), id="spell-panel-text")

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

    /* A tab with a details panel: its scrolling part fills the space down
       to the panel (DetailsPanel), which is docked at the bottom. */
    SheetView .panel-body {
        height: 1fr;
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

    def _book_list(
        self,
        owner_sections: tuple[str, ...],
        books: Callable[[], list[Book]],
        *,
        section_id: str,
        **kwargs: Any,
    ) -> BookListView:
        """A BookListView, rebuilt when its own section refreshes or any of
        `owner_sections` does (they show the name of an owner its Location
        column shows, so a rename there shows up in the list too)."""
        view = BookListView(self.saga, books, section_id=section_id, **kwargs)
        self._on_refresh((section_id, *owner_sections), view.rebuild)
        return view

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

    def _titled(
        self, sections: str | tuple[str, ...], id: str, title: Callable[[], str]
    ) -> str:
        """`title()`, for the section `id` to start with; it's set again
        whenever `sections` refresh (a count or total in it can change)."""
        self._on_refresh(
            sections,
            lambda: self._set_section_title(
                self.query_one(f"#{id}", Collapsible), title()
            ),
        )
        return title()

    def _panel(
        self, sections: str | tuple[str, ...], text: Callable[[], str], *, id: str
    ) -> DetailsPanel:
        """A DetailsPanel showing `text()`, re-rendered when `sections`
        refresh; `id` is its text's."""
        self._on_refresh(
            sections, lambda: self.query_one(f"#{id}", Static).update(text())
        )
        return DetailsPanel(text(), id=id)

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

    def _devices(
        self, kind: str, holder_id: str, section_id: str, *, group: str
    ) -> ComposeResult:
        """The Enchanted Devices section (STORY-305): the devices `kind`
        `holder_id` holds, each followed by its effects."""
        with SheetSection(
            title=self._titled(
                section_id,
                section_id,
                lambda: counted(
                    "Enchanted Devices", len(ed.held_by(self.saga, kind, holder_id))
                ),
            ),
            id=section_id,
        ):
            yield self._list(
                section_id,
                lambda: ed.device_rows(self.saga, kind, holder_id),
                id=f"{section_id}-list",
                group=group,
            )

    def selected_device_row(self, section_id: str) -> int | None:
        """Index into enchanted_devices.device_targets of the row chosen in
        `section_id`'s Enchanted Devices list, or None."""
        return self.query_one(f"#{section_id}-list", SelectableList).selected_data_index

    def _device_panel_text(
        self, kind: str, holder_id: str, index: int | None, hint: str
    ) -> str:
        """The details panel for row `index` of a device list (None: `hint`)."""
        if index is None:
            return hint
        targets = ed.device_targets(self.saga, kind, holder_id)
        if index >= len(targets):
            return hint
        return ed.target_info_text(self.saga, targets[index])

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

    CharacterSheetView .arts-col-title {
        text-style: bold;
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
            with (
                TabPane("Abilities", id="tab-abilities"),
                Vertical(classes="panel-body"),
            ):
                with VerticalScroll():
                    yield self._list(
                        "tab-abilities", self._ability_rows, id="abilities-list"
                    )
                yield self._panel(
                    "tab-abilities",
                    lambda: self._ability_info_text(None),
                    id="ability-info",
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
                with TwoColumns(id="char-info-body", text=True):
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
        self.query_one("#section-char-info", Collapsible).title = escape(
            self.character.name
        )

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
                    TwoColumns(id="hermetic-background-row", text=True),
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
                TwoColumns(id="char-biographical-row", text=True),
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
                    title=self._titled(
                        "section-personality-traits",
                        "section-personality-traits",
                        lambda: counted(
                            "Personality Traits",
                            len(self.character.personality_traits),
                        ),
                    ),
                    id="section-personality-traits",
                ):
                    yield self._list(
                        "section-personality-traits",
                        self._personality_trait_rows,
                        id="personality-traits-list",
                    )
                with SheetSection(
                    title=self._titled(
                        "section-reputations",
                        "section-reputations",
                        lambda: counted("Reputations", len(self.character.reputations)),
                    ),
                    id="section-reputations",
                ):
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
                TwoColumns(id="char-health-row", text=True),
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
        with Vertical(classes="panel-body"):
            with VerticalScroll(), TwoColumns(id="vf-row"):
                with SheetSection(
                    title=self._titled(
                        vf_sections,
                        "section-vf-virtues",
                        lambda: self._vf_title("Virtue"),
                    ),
                    id="section-vf-virtues",
                ):
                    yield self._list(
                        vf_sections,
                        lambda: self._vf_rows("Virtue"),
                        id="vf-virtues-list",
                        group="vf",
                    )
                with SheetSection(
                    title=self._titled(
                        vf_sections, "section-vf-flaws", lambda: self._vf_title("Flaw")
                    ),
                    id="section-vf-flaws",
                ):
                    yield self._list(
                        vf_sections,
                        lambda: self._vf_rows("Flaw"),
                        id="vf-flaws-list",
                        group="vf",
                    )
            yield self._panel(
                vf_sections, lambda: self._vf_info_text(None), id="vf-info"
            )

    #: Raw Vis deliberately appears twice (Hermetic Magic and Inventory tabs),
    #: both backed by character.raw_vis and both mounted at once
    #: (TabbedContent keeps inactive panes mounted, just hidden): either
    #: section id refreshes both lists, so neither goes stale.
    _RAW_VIS_SECTIONS = ("section-raw-vis-hermetic", "section-raw-vis-inventory")
    #: The Hermetic Magic details panel with nothing chosen.
    _HERMETIC_INFO_PLACEHOLDER = (
        "[dim]Select an Art or a Known Spell to see its details.[/]"
    )

    def _hermetic_tab(self) -> ComposeResult:
        """Magical Arts, Raw Vis and Known Spells (scrolling), and the
        details panel docked below them. Magi only."""
        with Vertical(id="hermetic-body", classes="panel-body"):
            with VerticalScroll(id="hermetic-scroll"):
                yield self._static(
                    ("section-char-devices", "section-arts"),
                    lambda: ed.talisman_line(self.saga, self.character),
                    id="hermetic-talisman",
                )
                with (
                    PinnedCollapsible(title="Magical Arts", id="section-arts"),
                    TwoColumns(id="arts-row"),
                ):
                    with Vertical(id="arts-techniques-col"):
                        yield Static("Techniques", classes="arts-col-title")
                        yield TableHeader(self._arts_header_text())
                        yield self._list(
                            "section-arts",
                            lambda: self._arts_rows(TECHNIQUES),
                            id="arts-techniques-list",
                            group="hermetic",
                        )
                    with Vertical(id="arts-forms-col"):
                        yield Static("Forms", classes="arts-col-title")
                        yield TableHeader(self._arts_header_text())
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
                with SheetSection(
                    title=self._titled(
                        "section-known-spells",
                        "section-known-spells",
                        lambda: counted(
                            "Known Spells", len(self.character.spells_known)
                        ),
                    ),
                    id="section-known-spells",
                ):
                    yield self._list(
                        "section-known-spells",
                        self._known_spell_rows,
                        id="known-spells-list",
                        group="hermetic",
                    )
            yield DetailsPanel(self._HERMETIC_INFO_PLACEHOLDER, id="hermetic-info")
            self._on_refresh(
                ("section-arts", "section-known-spells"), self._refresh_hermetic_info
            )

    def _inventory_tab(self) -> ComposeResult:
        """Raw Vis (magi), Personal Gear and the character's Books over the
        details panel of the chosen item or book."""
        character = self.character
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                if character.type == "magus":
                    with SheetSection(title="Raw Vis", id="section-raw-vis-inventory"):
                        yield self._list(
                            self._RAW_VIS_SECTIONS,
                            self._raw_vis_rows,
                            id="raw-vis-list-inventory",
                        )
                with SheetSection(
                    title=self._titled(
                        "section-inventory",
                        "section-inventory",
                        lambda: counted("Personal Gear", len(self.character.inventory)),
                    ),
                    id="section-inventory",
                ):
                    yield self._list(
                        "section-inventory",
                        self._inventory_rows,
                        id="inventory-list",
                        group="char-inv",
                    )
                yield from self._devices(
                    "character", character.id, "section-char-devices", group="char-inv"
                )
                yield self._book_list(
                    ("section-char-info",),
                    lambda: bk.books_owned_by(self.saga, "character", character.id),
                    section_id="section-books",
                    docked=False,
                    group="char-inv",
                )
            yield DetailsPanel(self._inventory_info_text(None), id="inventory-info")
        self._on_refresh(
            (
                "section-inventory",
                "section-char-devices",
                "section-books",
                "section-char-info",
            ),
            self._refresh_inventory_info,
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
        if list_id in (
            "inventory-list",
            "section-char-devices-list",
            "section-books-list",
        ):
            event.stop()
            # One group (one selection across the three), one details panel.
            self._refresh_inventory_info()
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
        ]
        if faith.shows_faith(character):
            rows += [
                ("True Faith Score", str(b.true_faith_score)),
                ("Faith Points", str(b.faith_points)),
            ]
        rows.append(("Size", str(b.size)))
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

    def _vf_title(self, vf_type: str) -> str:
        """ "Virtues (3 pts)" / "Flaws (3 pts)": the points each side comes
        to, both coloured by whether they balance."""
        vfs = self.character.virtues_flaws
        virtues = st.vf_points(vfs, "Virtue")
        flaws = st.vf_points(vfs, "Flaw")
        return points_title(
            f"{vf_type}s",
            virtues if vf_type == "Virtue" else flaws,
            match_colour(virtues, flaws),
        )

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
        return st.trait_rows(self.character.reputations)

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
            f"{'Score':>{self._ARTS_NUM_WIDTH}}{'XP':>{self._ARTS_NUM_WIDTH}}"
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
                st.xp_line(score.progress),
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
        if index is None:  # nothing chosen in any of the panel's three lists
            return self._HERMETIC_INFO_PLACEHOLDER
        known = self.character.spells_known[index]
        spell = spl.find_spell(self.saga, known.spell_id)
        if spell is None:
            lines = [f"[$text-error]Unknown spell: {escape(known.spell_id)}[/]"]
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
        """One selectable list for all of Inventory, with a header row --
        its title and column titles -- before each non-empty kind (Weapons,
        Armor, Other Items)."""
        rows: list[tuple[int | None, str]] = []
        for kind in self._INVENTORY_KINDS:
            indexed = [
                (i, item)
                for i, item in enumerate(self.character.inventory)
                if item.kind == kind
            ]
            if not indexed:
                continue
            rows.append((None, pos.group_header(kind, self._INVENTORY_HEADERS[kind])))
            for index, item in indexed:
                rows.append((index, pos.row_label(pos.PossessionEntry(kind, item))))
        return rows

    #: The Inventory tab's details panel with nothing chosen.
    _INVENTORY_HINT = (
        "[dim]Select an item, an enchanted device or a book to see its details.[/]"
    )

    def _inventory_info_text(self, index: int | None) -> str:
        if index is None:
            return self._INVENTORY_HINT
        item = self.character.inventory[index]
        return pos.detail_text(pos.PossessionEntry(item.kind, item))

    def _refresh_inventory_info(self) -> None:
        """The Inventory tab's details panel: the chosen item, enchanted
        device or book (one selection across the three lists), else the
        hint."""
        info = self.query_one("#inventory-info", Static)
        index = self.query_one("#inventory-list", SelectableList).selected_data_index
        if index is not None and index < len(self.character.inventory):
            info.update(self._inventory_info_text(index))
            return
        device = self.selected_device_row("section-char-devices")
        if device is not None:
            info.update(
                self._device_panel_text(
                    "character", self.character.id, device, self._INVENTORY_HINT
                )
            )
            return
        book = self.query_one(BookListView).selected_book()
        info.update(
            bk.detail_text(self.saga, book)
            if book is not None
            else self._inventory_info_text(None)
        )


#: The lab's Virtues and Flaws sections: either refreshes both lists and
#: their shared details panel.
LAB_VF_SECTIONS = ("section-lab-vf-virtues", "section-lab-vf-flaws")

#: What refreshes the lab's Characteristics: their own section, and the
#: Virtues & Flaws (whose modifiers and points feed every figure there).
_LAB_CHARACTERISTICS_SECTIONS = ("section-lab-characteristics", *LAB_VF_SECTIONS)
#: The Features list follows its own changes and the Virtues & Flaws' (a
#: Feature Virtue or Focus Flaw deleted).
LAB_FEATURE_SECTIONS = ("section-lab-features", *LAB_VF_SECTIONS)
#: The sections whose changes can move a Specialization's score.
LAB_SPECIALIZATION_SECTIONS = (
    "section-lab-specializations",
    "section-lab-specialties",
    *LAB_FEATURE_SECTIONS,
)


class LaboratorySheetView(SheetView):
    """The laboratory sheet mounted into WorkspaceScreen's detail pane.

    A fixed top panel (not inside any tab, permanently expanded) above a
    5-tab body mirroring the sheet's own pages: Planning (placeholder),
    Virtues & Flaws, Attributes (Sanctum, Specializations and their sources,
    Features, Rooms), Inventory (Raw Vis/Equipment & Stores/Books), Diary. The panel follows
    reference/lab-sheet-design-doc.md: Identity, titled with the lab's name,
    in two columns with the Aura below; then Characteristics in three
    columns (derived figures, then the 8 Characteristics four and four).
    Both stack their columns when the pane is too narrow (StackingColumns).

    Virtues & Flaws (two lists side by side, one details panel, and a
    warning line when the lab is over capacity or has two Focuses), Rooms,
    Raw Vis, Equipment & Stores and the Diary are selectable lists, with a
    details panel where there's more to show than the row (STORY-303).

    Specializations (STORY-307) is a grid of each Specialization's total
    over every source, grouped Activity / Art with each cap's count in the
    header, where Space turns the chosen one off or on (ToggleList); the
    hand-entered sources are a list nested inside it ("Specializations:
    Other"). Features (STORY-308) lists the lab's Features, each built on
    one of its Feature Virtues. Neither section collapses.

    The Attributes and Inventory tabs each have one details panel docked
    below their scrolling lists, as on the covenant's tabs (STORY-309): the
    chosen row of any of the tab's lists (one choice between them) shows
    there.
    """

    DEFAULT_CSS = """
    LaboratorySheetView #lab-top-panel {
        width: 1fr;
        height: auto;
    }

    LaboratorySheetView #lab-vf-warnings {
        margin-bottom: 1;
    }

    /* A blank row above the derived figures. The blank rows here are
       padding: any margin rule (even margin-top alone) replaces the whole
       margin, and with it the gap StackingColumns gives each column. */
    LaboratorySheetView #lab-characteristics-derived {
        padding: 1 0 0 0;
    }

    /* Stacked (narrow pane): no blank row above the derived figures, a
       blank row between the blocks instead. Only vertical padding changes,
       so StackingColumns measures the same width either way. */
    LaboratorySheetView #lab-characteristics-body.-stacked > * {
        padding: 0 0 1 0;
    }

    LaboratorySheetView #lab-characteristics-body.-stacked
        > #lab-characteristics-right {
        padding: 0;
    }
    """

    def __init__(self, saga: Saga, laboratory: Laboratory) -> None:
        super().__init__(saga)
        self.laboratory = laboratory

    def compose(self) -> ComposeResult:
        yield from self._top_panel()
        with TabbedContent(initial="tab-lab-planning"):
            with TabPane("Planning", id="tab-lab-planning"):
                yield self._static(
                    "tab-lab-planning", self._planning_text, id="lab-planning-content"
                )
            with TabPane("Virtues & Flaws", id="tab-lab-vf"):
                yield from self._virtues_flaws_tab()
            with TabPane("Attributes", id="tab-lab-attributes"):
                yield from self._attributes_tab()
            with TabPane("Inventory", id="tab-lab-inventory"):
                yield from self._inventory_tab()
            with (
                TabPane("Diary", id="tab-lab-diary"),
                Vertical(classes="panel-body"),
            ):
                with VerticalScroll():
                    yield self._list(
                        "tab-lab-diary",
                        lambda: lab_text.diary_rows(self.laboratory.diary),
                        id="lab-diary-list",
                    )
                yield self._panel(
                    "tab-lab-diary",
                    lambda: lab_text.diary_info_text(self.laboratory.diary, None),
                    id="lab-diary-info",
                )

    def _virtues_flaws_tab(self) -> ComposeResult:
        """Any warning about the Virtues & Flaws as a whole, the Virtue and
        Flaw lists side by side, and their shared details panel."""
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                warnings = self._static(
                    (*LAB_VF_SECTIONS, "section-lab-characteristics"),
                    lambda: lab_text.vf_warnings(self.laboratory),
                    id="lab-vf-warnings",
                )
                warnings.display = bool(lab_text.vf_warnings(self.laboratory))
                yield warnings
                self._on_refresh(
                    (*LAB_VF_SECTIONS, "section-lab-characteristics"),
                    self._show_vf_warnings_if_any,
                )
                with TwoColumns(id="lab-vf-row"):
                    with SheetSection(
                        title=self._titled(
                            LAB_VF_SECTIONS,
                            "section-lab-vf-virtues",
                            lambda: points_title(
                                "Virtues", lab_text.vf_points(self.laboratory, "Virtue")
                            ),
                        ),
                        id="section-lab-vf-virtues",
                    ):
                        yield self._list(
                            LAB_VF_SECTIONS,
                            lambda: lab_text.vf_rows(self.laboratory, "Virtue"),
                            id="lab-vf-virtues-list",
                            group="lab-vf",
                        )
                    with SheetSection(
                        title=self._titled(
                            LAB_VF_SECTIONS,
                            "section-lab-vf-flaws",
                            lambda: points_title(
                                "Flaws", lab_text.vf_points(self.laboratory, "Flaw")
                            ),
                        ),
                        id="section-lab-vf-flaws",
                    ):
                        yield self._list(
                            LAB_VF_SECTIONS,
                            lambda: lab_text.vf_rows(self.laboratory, "Flaw"),
                            id="lab-vf-flaws-list",
                            group="lab-vf",
                        )
            yield self._panel(
                LAB_VF_SECTIONS,
                lambda: lab_text.vf_info_text(self.laboratory, None),
                id="lab-vf-info",
            )

    def _attributes_tab(self) -> ComposeResult:
        """Specializations (with the hand-entered sources nested in it),
        Features and Rooms over the details panel of the chosen row, docked
        below the scrolling part."""
        with Vertical(id="lab-attr-body", classes="panel-body"):
            with VerticalScroll(id="lab-attr-scroll"):
                with PinnedCollapsible(
                    title="Specializations", id="section-lab-specializations"
                ):
                    yield ToggleList(
                        lab_text.specialization_rows(self.laboratory),
                        id="lab-specializations-list",
                        group="lab-attr",
                    )
                    self._on_refresh(
                        LAB_SPECIALIZATION_SECTIONS, self._refresh_specializations
                    )
                    with SheetSection(
                        title=self._titled(
                            "section-lab-specialties",
                            "section-lab-specialties",
                            lambda: counted(
                                "Specializations: Other",
                                len(self.laboratory.specialties),
                            ),
                        ),
                        id="section-lab-specialties",
                    ):
                        yield self._list(
                            "section-lab-specialties",
                            lambda: lab_text.specialty_entry_rows(self.laboratory),
                            id="lab-specialties-list",
                            group="lab-attr",
                        )
                with PinnedCollapsible(
                    title=self._titled(
                        LAB_FEATURE_SECTIONS,
                        "section-lab-features",
                        lambda: lab_text.features_title(self.laboratory),
                    ),
                    id="section-lab-features",
                ):
                    yield self._list(
                        LAB_FEATURE_SECTIONS,
                        lambda: lab_text.feature_rows(self.laboratory),
                        id="lab-features-list",
                        group="lab-attr",
                    )
                with SheetSection(
                    title=self._titled(
                        "section-lab-rooms",
                        "section-lab-rooms",
                        lambda: counted("Rooms", len(self.laboratory.rooms)),
                    ),
                    id="section-lab-rooms",
                ):
                    yield self._list(
                        "section-lab-rooms",
                        lambda: lab_text.named_rows(self.laboratory.rooms),
                        id="lab-rooms-list",
                        group="lab-attr",
                    )
            yield DetailsPanel(lab_text.ATTRIBUTES_PANEL_HINT, id="lab-attr-panel")
        self._on_refresh(
            ("section-lab-rooms", *LAB_SPECIALIZATION_SECTIONS),
            lambda: self._refresh_panel("lab-attr-panel"),
        )

    def _inventory_tab(self) -> ComposeResult:
        """Raw Vis, Equipment & Stores, Enchanted Devices and the lab's Books
        over the details panel of the chosen row, docked below the scrolling
        part."""
        with Vertical(id="lab-inv-body", classes="panel-body"):
            with VerticalScroll(id="lab-inv-scroll"):
                with SheetSection(title="Raw Vis", id="section-lab-raw-vis"):
                    yield self._list(
                        "section-lab-raw-vis",
                        lambda: lab_text.raw_vis_rows(self.laboratory),
                        id="lab-raw-vis-list",
                        group="lab-inv",
                    )
                with SheetSection(
                    title=self._titled(
                        "section-lab-items",
                        "section-lab-items",
                        lambda: counted(
                            "Equipment & Stores", len(self.laboratory.inventory_items)
                        ),
                    ),
                    id="section-lab-items",
                ):
                    yield self._list(
                        "section-lab-items",
                        lambda: lab_text.named_rows(self.laboratory.inventory_items),
                        id="lab-items-list",
                        group="lab-inv",
                    )
                yield from self._devices(
                    "laboratory",
                    self.laboratory.id,
                    "section-lab-devices",
                    group="lab-inv",
                )
                yield self._book_list(
                    ("section-lab-identity",),
                    lambda: bk.books_owned_by(
                        self.saga, "laboratory", self.laboratory.id
                    ),
                    section_id="section-lab-books",
                    docked=False,
                    group="lab-inv",
                )
            yield DetailsPanel(lab_text.INVENTORY_PANEL_HINT, id="lab-inv-panel")
        self._on_refresh(
            (
                "section-lab-raw-vis",
                "section-lab-items",
                "section-lab-devices",
                "section-lab-books",
                "section-lab-identity",
            ),
            lambda: self._refresh_panel("lab-inv-panel"),
        )

    def _refresh_specializations(self) -> None:
        """Re-fill the grid, keeping the chosen Specialization chosen (the
        panel follows it) if it's still there."""
        grid = self.query_one("#lab-specializations-list", ToggleList)
        chosen = grid.selected_data_index
        grid.set_rows(lab_text.specialization_rows(self.laboratory))
        if chosen is not None:
            grid.select_data_index(chosen)

    def _panels(self) -> dict[str, tuple[str, Callable[[int | None], str]]]:
        """Per list, the details panel its chosen row shows in and that
        row's text (None: nothing chosen)."""
        lab = self.laboratory
        return {
            "lab-vf-virtues-list": (
                "lab-vf-info",
                lambda i: lab_text.vf_info_text(lab, i),
            ),
            "lab-vf-flaws-list": (
                "lab-vf-info",
                lambda i: lab_text.vf_info_text(lab, i),
            ),
            "lab-specializations-list": (
                "lab-attr-panel",
                lambda i: lab_text.specialization_info_text(lab, i),
            ),
            "lab-specialties-list": (
                "lab-attr-panel",
                lambda i: lab_text.specialty_entry_info_text(lab, i),
            ),
            "lab-features-list": (
                "lab-attr-panel",
                lambda i: (
                    lab_text.feature_info_text(lab, i)
                    if i is not None
                    else lab_text.ATTRIBUTES_PANEL_HINT
                ),
            ),
            "lab-rooms-list": (
                "lab-attr-panel",
                lambda i: (
                    lab_text.named_info_text(lab.rooms, i, "a Room")
                    if i is not None
                    else lab_text.ATTRIBUTES_PANEL_HINT
                ),
            ),
            "lab-raw-vis-list": (
                "lab-inv-panel",
                lambda i: lab_text.raw_vis_info_text(lab, i),
            ),
            "lab-items-list": (
                "lab-inv-panel",
                lambda i: (
                    lab_text.named_info_text(lab.inventory_items, i, "an entry")
                    if i is not None
                    else lab_text.INVENTORY_PANEL_HINT
                ),
            ),
            "section-lab-devices-list": (
                "lab-inv-panel",
                lambda i: self._device_panel_text(
                    "laboratory", lab.id, i, lab_text.INVENTORY_PANEL_HINT
                ),
            ),
            "section-lab-books-list": ("lab-inv-panel", self._book_panel_text),
            "lab-diary-list": (
                "lab-diary-info",
                lambda i: lab_text.diary_info_text(lab.diary, i),
            ),
        }

    def _book_panel_text(self, index: int | None) -> str:
        if index is None:
            return lab_text.INVENTORY_PANEL_HINT
        books = self.query_one(BookListView).books
        return bk.detail_text(self.saga, books[index] if index < len(books) else None)

    def _refresh_panel(self, panel_id: str) -> None:
        """After a refresh: the shared panel shows whichever of its lists
        still has a row chosen (re-filled lists lose theirs), else the
        hint."""
        panels = self._panels()
        for list_id, (target, text) in panels.items():
            if target != panel_id:
                continue
            index = self._selected(list_id)
            if index is not None:
                self.query_one(f"#{panel_id}", Static).update(text(index))
                return
        text = next(text for target, text in panels.values() if target == panel_id)
        self.query_one(f"#{panel_id}", Static).update(text(None))

    def _show_vf_warnings_if_any(self) -> None:
        warnings = self.query_one("#lab-vf-warnings", Static)
        warnings.display = bool(lab_text.vf_warnings(self.laboratory))

    def _selected(self, list_id: str) -> int | None:
        return self.query_one(f"#{list_id}", SelectableList).selected_data_index

    def selected_virtue_flaw(self) -> int | None:
        """Index into laboratory.virtues_flaws of the row chosen in either the
        Virtues or the Flaws list, or None if neither has one chosen."""
        virtue = self._selected("lab-vf-virtues-list")
        return virtue if virtue is not None else self._selected("lab-vf-flaws-list")

    def selected_specialization(self) -> int | None:
        """Index into LAB_SPECIALIZATIONS of the grid's chosen row, or None."""
        return self._selected("lab-specializations-list")

    def selected_specialty_entry(self) -> int | None:
        """Index into laboratory.specialties of the chosen source, or None."""
        return self._selected("lab-specialties-list")

    def selected_feature(self) -> int | None:
        """Index into laboratory.features of the chosen row, or None."""
        return self._selected("lab-features-list")

    def selected_room(self) -> int | None:
        """Index into laboratory.rooms of the chosen row, or None."""
        return self._selected("lab-rooms-list")

    def selected_item(self) -> int | None:
        """Index into laboratory.inventory_items of the chosen row, or None."""
        return self._selected("lab-items-list")

    def selected_raw_vis(self) -> int | None:
        """Index into sorted(laboratory.raw_vis) of the chosen row, or None."""
        return self._selected("lab-raw-vis-list")

    def selected_diary_entry(self) -> int | None:
        """Index into laboratory.diary of the chosen row, or None."""
        return self._selected("lab-diary-list")

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """Fill the chosen row's details panel."""
        panel = self._panels().get(event.selectable_list.id or "")
        if panel is None:
            return
        event.stop()
        panel_id, text = panel
        self.query_one(f"#{panel_id}", Static).update(text(event.data_index))

    def _top_panel(self) -> ComposeResult:
        """The always-visible Identity and Characteristics panels above the
        tabs."""
        with Vertical(id="lab-top-panel"):
            with PinnedCollapsible(
                title=escape(self.laboratory.name), id="section-lab-identity"
            ):
                with StackingColumns(id="lab-identity-body", equal=True):
                    yield self._static(
                        "section-lab-identity",
                        self._identity_left_text,
                        id="lab-identity-left",
                    )
                    yield self._static(
                        "section-lab-identity",
                        self._identity_right_text,
                        id="lab-identity-right",
                    )
                yield self._static(
                    "section-lab-identity", self._aura_text, id="lab-identity-aura"
                )
                yield Button("Edit (e)", id="btn-lab-identity-edit", compact=True)
            self._on_refresh("section-lab-identity", self._refresh_identity_layout)
            with PinnedCollapsible(
                title="Characteristics", id="section-lab-characteristics"
            ):
                with StackingColumns(id="lab-characteristics-body"):
                    yield self._static(
                        _LAB_CHARACTERISTICS_SECTIONS,
                        self._characteristics_derived_text,
                        id="lab-characteristics-derived",
                    )
                    yield self._static(
                        _LAB_CHARACTERISTICS_SECTIONS,
                        lambda: self._characteristics_column_text(
                            LAB_CHARACTERISTICS[:4]
                        ),
                        id="lab-characteristics-left",
                    )
                    yield self._static(
                        _LAB_CHARACTERISTICS_SECTIONS,
                        lambda: self._characteristics_column_text(
                            LAB_CHARACTERISTICS[4:]
                        ),
                        id="lab-characteristics-right",
                    )
                yield Button(
                    "Edit (e)", id="btn-lab-characteristics-edit", compact=True
                )
            self._on_refresh(
                _LAB_CHARACTERISTICS_SECTIONS,
                lambda: self.query_one(
                    "#lab-characteristics-body", StackingColumns
                ).restack(),
            )

    def _refresh_identity_layout(self) -> None:
        """After an Identity edit: the title follows a rename, and longer or
        shorter values can change whether the columns fit side by side."""
        self.query_one("#section-lab-identity", Collapsible).title = escape(
            self.laboratory.name
        )
        self.query_one("#lab-identity-body", StackingColumns).restack()

    def _identity_left_text(self) -> str:
        covenant = self.saga.covenant(self.laboratory.covenant_id)
        owner = self.saga.character(self.laboratory.owner_id)
        return aligned(
            [
                ("Covenant", escape(covenant.name) if covenant else "(none)"),
                ("Owner", escape(owner.name) if owner else "(unassigned)"),
            ]
        )

    def _identity_right_text(self) -> str:
        lab = self.laboratory
        return aligned(
            [
                ("Location", escape(lab.location) or "(not set)"),
                ("Points", lab.build_points),
                ("Sanctum?", "Yes" if lab.sanctum_marked else "No"),
            ]
        )

    def _aura_text(self) -> str:
        lab = self.laboratory
        covenant = self.saga.covenant(lab.covenant_id)
        # Inherited from the covenant, including any Boons that raise it.
        covenant_aura = (
            covenant_effective_aura(
                covenant, catalog.load_covenant_boon_hook_catalog_by_id()
            )
            if covenant
            else 0
        )
        return (
            f"Aura: {covenant_aura} (covenant) {lab.aura_modifier:+d} (modifier) "
            f"= {lab_aura_total(lab, covenant_aura)}"
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

    def _characteristics_column_text(self, characteristics: Sequence[str]) -> str:
        """One column of Characteristics as an aligned table: manual value,
        the summed Virtue+Flaw modifier, and the total after '='. Numbers
        are as wide as the widest of all 8, so both columns line up, and
        coloured by sign (see _sign_colored())."""
        lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
        lab = self.laboratory
        rows: dict[str, tuple[int, int, int]] = {}
        for characteristic in LAB_CHARACTERISTICS:
            manual, virtue_sum, flaw_sum, total = lab_characteristic_total(
                lab, lab_catalog, characteristic
            )
            rows[characteristic] = (manual, virtue_sum + flaw_sum, total)
        num_width = max(len(f"{value:+d}") for row in rows.values() for value in row)
        labels = {c: c.replace("_", " ").title() + ":" for c in characteristics}
        label_width = max(len(label) for label in labels.values())

        def cell(value: int) -> str:
            return _sign_colored(value, f"{value:>+{num_width}d}")

        lines = []
        for characteristic in characteristics:
            manual, vf, total = rows[characteristic]
            lines.append(
                f"{labels[characteristic]:<{label_width}} "
                f"{cell(manual)} {cell(vf)} = {cell(total)}"
            )
        return "\n".join(lines)

    def _planning_text(self) -> str:
        return "Lab activity planning isn't built yet -- coming in a future update."


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
            with (
                TabPane("Abilities", id="tab-fam-abilities"),
                Vertical(classes="panel-body"),
            ):
                with VerticalScroll():
                    yield Static(
                        "[dim]Languages: shares the Magus partner's Language "
                        "scores automatically.[/]"
                    )
                    yield self._list(
                        "tab-fam-abilities",
                        lambda: fam.ability_rows(self.familiar),
                        id="fam-abilities-list",
                    )
                yield self._panel(
                    "tab-fam-abilities",
                    lambda: fam.ability_info_text(self.familiar, None),
                    id="fam-ability-info",
                )
            with (
                TabPane("Bond Powers", id="tab-fam-powers"),
                Vertical(classes="panel-body"),
            ):
                with VerticalScroll():
                    yield self._list(
                        "tab-fam-powers",
                        lambda: fam.bond_power_rows(self.familiar),
                        id="fam-bond-powers-list",
                    )
                yield self._panel(
                    "tab-fam-powers",
                    lambda: fam.bond_power_info_text(self.familiar, None),
                    id="fam-bond-powers-info",
                )

    def _identity_tab(self) -> ComposeResult:
        """Binding & Cords, the Virtue and Flaw lists with their details
        panel, and Personality Traits and Reputations."""
        vf_sections = ("section-fam-vf-virtues", "section-fam-vf-flaws")
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                with SheetSection(title="Binding & Cords", id="section-fam-binding"):
                    yield self._static(
                        "section-fam-binding",
                        self._binding_text,
                        id="fam-binding-content",
                    )
                with TwoColumns(id="fam-vf-row"):
                    with SheetSection(
                        title=self._titled(
                            vf_sections,
                            "section-fam-vf-virtues",
                            lambda: points_title(
                                "Virtues",
                                st.vf_points(self.familiar.virtues_flaws, "Virtue"),
                            ),
                        ),
                        id="section-fam-vf-virtues",
                    ):
                        yield self._list(
                            vf_sections,
                            lambda: fam.vf_rows(self.familiar, "Virtue"),
                            id="fam-vf-virtues-list",
                            group="fam-vf",
                        )
                    with SheetSection(
                        title=self._titled(
                            vf_sections,
                            "section-fam-vf-flaws",
                            lambda: points_title(
                                "Flaws",
                                st.vf_points(self.familiar.virtues_flaws, "Flaw"),
                            ),
                        ),
                        id="section-fam-vf-flaws",
                    ):
                        yield self._list(
                            vf_sections,
                            lambda: fam.vf_rows(self.familiar, "Flaw"),
                            id="fam-vf-flaws-list",
                            group="fam-vf",
                        )
                with TwoColumns(id="fam-pt-rep-row"):
                    with SheetSection(
                        title=self._titled(
                            "section-fam-personality-traits",
                            "section-fam-personality-traits",
                            lambda: counted(
                                "Personality Traits",
                                len(self.familiar.personality_traits),
                            ),
                        ),
                        id="section-fam-personality-traits",
                    ):
                        yield self._list(
                            "section-fam-personality-traits",
                            lambda: fam.personality_trait_rows(self.familiar),
                            id="fam-personality-traits-list",
                        )
                    with SheetSection(
                        title=self._titled(
                            "section-fam-reputations",
                            "section-fam-reputations",
                            lambda: counted(
                                "Reputations", len(self.familiar.reputations)
                            ),
                        ),
                        id="section-fam-reputations",
                    ):
                        yield self._list(
                            "section-fam-reputations",
                            lambda: fam.reputation_rows(self.familiar),
                            id="fam-reputations-list",
                        )
            yield self._panel(
                vf_sections,
                lambda: fam.vf_info_text(self.familiar, None),
                id="fam-vf-info",
            )

    def _combat_tab(self) -> ComposeResult:
        """Health (Wounds and Fatigue) and Natural Weapons & Attacks, over
        the details panel of the chosen weapon."""
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                with (
                    SheetSection(title="Health", id="section-fam-health"),
                    TwoColumns(id="fam-health-row", text=True),
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
                    title=self._titled(
                        "section-fam-natural-weapons",
                        "section-fam-natural-weapons",
                        lambda: counted(
                            "Natural Weapons & Attacks",
                            len(self.familiar.natural_weapons),
                        ),
                    ),
                    id="section-fam-natural-weapons",
                ):
                    yield TableHeader(pos.table_header("weapon"))
                    yield self._list(
                        "section-fam-natural-weapons",
                        lambda: fam.natural_weapon_rows(self.familiar),
                        id="fam-natural-weapons-list",
                    )
            yield self._panel(
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
    Economics, Library, Diary.

    The panel's saga-level values (Saga, Storyguide, Current Season,
    Current Year) are inherited from the Saga and shown dimmed/read-only;
    the rest belong to the covenant and are edited with 'e'.
    """

    def __init__(self, saga: Saga, covenant: Covenant) -> None:
        super().__init__(saga)
        self.covenant = covenant

    def compose(self) -> ComposeResult:
        with PinnedCollapsible(title=escape(self.covenant.name), id="section-cov-info"):
            with TwoColumns(id="cov-info-body", text=True):
                yield Static(self._info_left_text(), id="cov-info-left")
                yield Static(self._info_right_text(), id="cov-info-right")
            yield Button("Edit (e)", id="btn-cov-edit", compact=True)
        with TabbedContent(initial="tab-cov-attributes"):
            with (
                TabPane("Attributes", id="tab-cov-attributes"),
                Vertical(classes="panel-body"),
            ):
                with VerticalScroll():
                    with SheetSection(
                        title="Description", id="section-cov-description"
                    ):
                        yield Static(
                            self._description_text(), id="cov-description-content"
                        )
                    with SheetSection(
                        title=self._titled(
                            "section-cov-reputations",
                            "section-cov-reputations",
                            lambda: counted(
                                "Reputations", len(self.covenant.reputations)
                            ),
                        ),
                        id="section-cov-reputations",
                    ):
                        yield SelectableList(
                            self._reputation_rows(), id="cov-reputations-list"
                        )
                    with TwoColumns(id="cov-bh-row"):
                        with SheetSection(
                            title=self._bh_title("Boon"), id="section-cov-boons"
                        ):
                            yield SelectableList(
                                self._bh_entries("Boon"),
                                id="cov-boons-list",
                                group="bh",
                            )
                        with SheetSection(
                            title=self._bh_title("Hook"), id="section-cov-hooks"
                        ):
                            yield SelectableList(
                                self._bh_entries("Hook"),
                                id="cov-hooks-list",
                                group="bh",
                            )
                yield DetailsPanel(self._bh_info_text(None), id="cov-bh-info")
            with TabPane("Inhabitants", id="tab-cov-inhabitants"):
                yield from self._inhabitants_tab()
            with TabPane("Possessions", id="tab-cov-possessions"):
                yield from self._possessions_tab()
            with TabPane("Economics", id="tab-cov-economics"):
                yield from self._economics_tab()
            with TabPane("Library", id="tab-cov-library"):
                yield self._book_list(
                    ("section-cov-info",),
                    lambda: bk.books_in_covenant(self.saga, self.covenant),
                    section_id="section-lib-books",
                    summary=True,
                )
            with (
                TabPane("Diary", id="tab-cov-diary"),
                Vertical(classes="panel-body"),
            ):
                with VerticalScroll():
                    yield self._list(
                        "tab-cov-diary",
                        lambda: cov_diary.rows(self.covenant.diary),
                        id="cov-diary-list",
                    )
                yield self._panel(
                    "tab-cov-diary",
                    lambda: cov_diary.info_text(self.covenant, None),
                    id="cov-diary-info",
                )

    def _inhabitants_tab(self) -> ComposeResult:
        """Loyalty, the Inhabitants summary and Miscellaneous blocks, one
        collapsible list per kind of inhabitant, and (docked below the
        scrolling part) the details panel of the chosen inhabitant."""
        covenant, saga = self.covenant, self.saga
        with Vertical(id="inh-body", classes="panel-body"):
            with VerticalScroll(id="inh-scroll"):
                with (
                    SheetSection(title="Loyalty", id="section-inh-loyalty"),
                    TwoColumns(id="inh-loyalty-body", text=True),
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
                    with TwoColumns(id="inh-misc-body", text=True):
                        yield Static(left, id="inh-misc-left")
                        yield Static(right, id="inh-misc-right")
                for kind in INHABITANT_KINDS:
                    with SheetSection(
                        title=self._inh_title(kind), id=f"section-inh-{kind}"
                    ):
                        yield TableHeader(inh.table_header(kind))
                        yield SelectableList(
                            self._inh_rows(kind), id=f"inh-{kind}-list", group="inh"
                        )
            yield DetailsPanel(inh.detail_text(None, saga.current_year), id="inh-panel")

    def _possessions_tab(self) -> ComposeResult:
        """One collapsible list per kind of possession over the details panel of
        the chosen one (docked below the scrolling part)."""
        with Vertical(id="pos-body", classes="panel-body"):
            with VerticalScroll(id="pos-scroll"):
                for kind in POSSESSION_KINDS:
                    with SheetSection(
                        title=self._pos_title(kind), id=f"section-pos-{kind}"
                    ):
                        yield TableHeader(pos.table_header(kind))
                        yield SelectableList(
                            self._pos_rows(kind), id=f"pos-{kind}-list", group="pos"
                        )
                yield from self._devices(
                    "covenant", self.covenant.id, "section-cov-devices", group="pos"
                )
                self._on_refresh(
                    "section-cov-devices",
                    lambda: self.query_one("#pos-panel", Static).update(
                        pos.detail_text(None)
                    ),
                )
            yield DetailsPanel(pos.detail_text(None), id="pos-panel")

    #: The three lists of the Economics tab (one selection across them).
    _ECO_LISTS: ClassVar[tuple[str, ...]] = ("income", "expenditure", "savings")

    def _economics_tab(self) -> ComposeResult:
        """Wealth, Sources of Income, Yearly Expenditure and Cost Savings over
        the details panel of the chosen row (docked below the scrolling part)."""
        summary = eco.summarize(self.saga, self.covenant)
        left, right = eco.wealth_texts(summary)
        with Vertical(id="eco-body", classes="panel-body"):
            with VerticalScroll(id="eco-scroll"):
                with (
                    SheetSection(title="Wealth", id="section-eco-wealth"),
                    TwoColumns(id="eco-wealth-body", text=True),
                ):
                    yield Static(left, id="eco-wealth-left")
                    yield Static(right, id="eco-wealth-right")
                with SheetSection(title=self._income_title(), id="section-eco-income"):
                    yield TableHeader(eco.source_table_header(), classes="eco-header")
                    yield SelectableList(
                        self._eco_rows("income", summary),
                        id="eco-income-list",
                        group="eco",
                    )
                with SheetSection(
                    title="Yearly Expenditure", id="section-eco-expenditure"
                ):
                    yield TableHeader(eco.table_header("Cost"), classes="eco-header")
                    yield SelectableList(
                        self._eco_rows("expenditure", summary),
                        id="eco-expenditure-list",
                        group="eco",
                    )
                with SheetSection(title="Cost Savings", id="section-eco-savings"):
                    yield TableHeader(
                        eco.table_header("Quantity"), classes="eco-header"
                    )
                    yield SelectableList(
                        self._eco_rows("savings", summary),
                        id="eco-savings-list",
                        group="eco",
                    )
            yield DetailsPanel(eco.source_detail_text(None), id="eco-panel")

    def _income_title(self) -> str:
        return counted("Sources of Income", len(self.covenant.economics.income_sources))

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
        self._set_section_title(
            self.query_one("#section-eco-income", Collapsible), self._income_title()
        )
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

    def _pos_title(self, kind: str) -> str:
        return counted(pos.KIND_TITLES[kind], len(self._pos_entries(kind)))

    def _rebuild_possessions(self) -> None:
        """Re-render every list and its title, and reset the panel."""
        for kind in POSSESSION_KINDS:
            self._set_section_title(
                self.query_one(f"#section-pos-{kind}", Collapsible),
                self._pos_title(kind),
            )
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
        super().refresh_section(section_id)  # the Library's book list
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
            if section_id == "tab-cov-diary":
                # The Diary's Loyalty points feed Actions and Events.
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
            # An Aura Boon changes the Aura shown in the info panel, and so
            # what the info panel feeds (Loyalty; Economics is rebuilt by
            # refresh_section for every section-cov-* already).
            self._refresh_section("section-cov-info")
            self._refresh_loyalty_text()

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

    def selected_diary_entry(self) -> int | None:
        """Index into covenant.diary of the chosen row, or None."""
        return self.query_one("#cov-diary-list", SelectableList).selected_data_index

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A Boon or Hook row was chosen: fill the details panel. (Reputations
        have no panel -- a name and a score have nothing more to show.)"""
        list_id = event.selectable_list.id or ""
        if list_id == "cov-diary-list":
            event.stop()
            self.query_one("#cov-diary-info", Static).update(
                cov_diary.info_text(self.covenant, event.data_index)
            )
            return
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
        if list_id == "section-cov-devices-list":
            event.stop()
            self.query_one("#pos-panel", Static).update(
                self._device_panel_text(
                    "covenant",
                    self.covenant.id,
                    event.data_index,
                    pos.detail_text(None),
                )
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
        cost, Hooks the points they provide. Both totals share one colour:
        plain while the Boons cost less than the Hooks provide (points still
        to spend), $text-success when they match, $text-error when the Boons
        cost more."""
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        boons = covenant_boon_points(self.covenant, by_id)
        hooks = covenant_hook_points(self.covenant, by_id)
        colour = None if boons < hooks else match_colour(boons, hooks)
        if kind == "Boon":
            return points_title("Boons", boons, colour)
        return points_title("Hooks", hooks, colour)

    def _bh_entries(self, kind: str) -> list[tuple[int, str]]:
        """The attached Boons or Hooks of `kind` as (index into
        covenant.boons_hooks, display label) pairs, in attach order."""
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        return [
            (
                index,
                escape(catalog.describe_boon_hook(bh, by_id))
                + (
                    f" [dim](Unknown, {UNKNOWN_HOOK_POINTS} pts)[/]"
                    if boon_hook_is_unknown(bh, by_id[bh.vf_id])
                    else ""
                ),
            )
            for index, bh in enumerate(self.covenant.boons_hooks)
            if bh.vf_id in by_id and by_id[bh.vf_id].type == kind
        ]

    def _bh_info_text(self, index: int | None) -> str:
        """The details panel for the attached Boon/Hook at `index` into
        covenant.boons_hooks: its name, type, notes, the user's own
        description (if any), then the official rules text and the book it
        comes from."""
        if index is None:
            return "[dim]Select a Boon or Hook to see its details.[/]"
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        instance = self.covenant.boons_hooks[index]
        definition = by_id.get(instance.vf_id)
        if definition is None:
            return escape(f"{instance.vf_id} (not in catalog)")

        lines = [f"[b]Name:[/] {escape(catalog.describe_boon_hook(instance, by_id))}"]
        if definition.category:
            lines.append(f"[b]Type:[/] {definition.category}")
        lines.append(f"[b]Tier:[/] {_tier_text(definition)}")
        if boon_hook_is_unknown(instance, definition):
            lines.append(
                f"[b]Unknown:[/] Yes (counts {UNKNOWN_HOOK_POINTS} points, "
                "as a Major Hook)"
            )
        elif definition.unknown:
            lines.append("[dim]May be Unknown (mark it in its Edit form).[/]")
        if definition.requires:
            lines.append(
                f"[b]Requires:[/] {_boon_hook_names(definition.requires, by_id)}"
            )
        if definition.requires_any:
            lines.append(
                "[b]Requires one of:[/] "
                + _boon_hook_names(definition.requires_any, by_id)
            )
        if definition.excludes:
            lines.append(
                f"[b]Not with:[/] {_boon_hook_names(definition.excludes, by_id)}"
            )
        lines += st.effect_lines(definition.modifiers)
        if definition.max_count:
            lines.append(
                f"[dim]May be taken up to {definition.max_count} times; "
                "the effects stack.[/]"
            )
        elif definition.repeatable:
            lines.append("[dim]May be taken more than once; the effects stack.[/]")
        # The user's own description leads; the official rules text follows.
        description = instance.params.get(BOON_HOOK_DESCRIPTION, "").strip()
        if description:
            lines += ["", "[b]Description:[/]", markdown_inline(description)]
        lines += ["", "[b]Rules:[/]", escape(definition.description)]
        if definition.source:
            lines += ["", f"[dim]Source: {escape(definition.source)}[/]"]
        return "\n".join(lines)
