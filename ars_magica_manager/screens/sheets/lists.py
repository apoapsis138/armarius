"""The list views in the workspace's detail pane: books (and Lab Texts),
House Rules, players and the saga's spells."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.widgets import (
    Collapsible,
    Input,
    Label,
    Select,
    Static,
)

from ... import books as bk
from ... import house_rules as hr
from ... import lab_texts as lt
from ... import players as pl
from ... import spells as spl
from ...arts import FORMS, TECHNIQUES
from ...models import (
    Book,
    Character,
    Player,
    Saga,
    Spell,
)
from ..fields import _pairs
from ..widgets import (
    DETAILS_PANEL_MAX_HEIGHT,
    DETAILS_PANEL_MIN_HEIGHT,
    DetailsPanel,
    SelectableList,
    SheetSection,
    TableHeader,
    TwoColumns,
    counted,
)

#: The covenant Library tab's sections, where More's Import puts books into the
#: covenant's library.
_LIBRARY_SECTIONS: frozenset[str] = frozenset(
    {"section-lib-summary", "section-lib-books"}
)


#: The Enchanted Devices section of each sheet, and the kind of
#: holder whose devices it lists.
DEVICE_SECTIONS: dict[str, str] = {
    "section-char-devices": "character",
    "section-lab-devices": "laboratory",
    "section-cov-devices": "covenant",
}


#: The laboratory's Lab Texts database: a book list of its own.
LAB_TEXTS_SECTION = "section-lab-texts"

#: Section ids of every book list (see BookListView); 'a' in any of them adds
#: a book, and e / d act on books everywhere but the read-only Summary.
BOOK_SECTIONS: frozenset[str] = frozenset(
    {
        "section-lib-summary",
        "section-lib-books",
        "section-lab-books",
        "section-books",
        "section-unassigned-books",
        LAB_TEXTS_SECTION,
    }
)


#: Rows a docked book list keeps however short the screen (see
#: _fit_panel); and what its section takes besides the rows: its title,
#: padding and column header.
BOOK_LIST_MIN_ROWS = 5
_BOOK_SECTION_CHROME = 5


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

    /* A row narrower than its columns is cut short, not wrapped onto a
       second line: one book, one row. */
    BookListView SelectableList, BookListView .books-header {
        text-wrap: nowrap;
        text-overflow: ellipsis;
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
        research: Callable[[], str] | None = None,
    ) -> None:
        """`research`: the Summary's Research count (plain text, "" for
        none), for a covenant's library."""
        super().__init__(classes="docked" if docked else "")
        self.group = group
        self._research = research
        self.saga = saga
        self._books_source = books
        self.section_id = section_id
        self.title_text = title
        self.summary = summary
        self.docked = docked
        #: Grouped: the books of one codex are listed together.
        self._books: list[Book] = bk.grouped(saga, books())
        #: Width of the Subject column, fitted to the list (see on_resize).
        self._subject_cols = bk.SUBJECT_MIN_WIDTH

    def _summary(self) -> tuple[str, str]:
        research = self._research() if self._research else ""
        return bk.summary_texts(self._books, self.saga, research=research)

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
        """Give the Subject column whatever room the list has, and keep
        rows for the list on a short screen."""
        self._fit_panel()
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

    def _fit_panel(self) -> None:
        """On a short screen the details panel gives up rows (its text
        scrolls) so the list keeps BOOK_LIST_MIN_ROWS of them: the panel
        grows to fit its text, up to DETAILS_PANEL_MAX_HEIGHT, and below it
        a big Summary left the list none."""
        if not self.docked:
            return
        try:
            panel = self.query_one(DetailsPanel)
            summary = (
                self.query_one("#section-lib-summary").outer_size.height
                if self.summary
                else 0
            )
        except NoMatches:
            return
        spare = self.size.height - summary - _BOOK_SECTION_CHROME - BOOK_LIST_MIN_ROWS
        # The panel's top margin is outside its height.
        cap = max(DETAILS_PANEL_MIN_HEIGHT, min(DETAILS_PANEL_MAX_HEIGHT, spare - 1))
        panel.styles.max_height = cap

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
                left, right = self._summary()
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
            self._books = bk.grouped(self.saga, self._books_source())
            self.query_one(f"#{self.section_id}", Collapsible).title = self._title()
            if self.summary:
                left, right = self._summary()
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


#: The House Rules view's list section (a / e / d act on user-made entries).
HOUSE_RULES_SECTION = "section-house-rules"


class HouseRulesView(Vertical):
    """The saga's House Rules: its user-made Virtues, Flaws,
    Boons and Hooks in one list, stretching down to the details panel of
    the chosen one."""

    DEFAULT_CSS = """
    HouseRulesView {
        height: 1fr;
    }

    HouseRulesView .house-rules-body {
        height: 1fr;
    }
    """

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga
        self._entries = hr.all_entries(saga)

    def _title(self) -> str:
        return counted("House Rules", len(self._entries))

    def _rows(self) -> list[tuple[int, str]]:
        return [
            (i, hr.row_label(kind, entry))
            for i, (kind, entry) in enumerate(self._entries)
        ]

    def compose(self) -> ComposeResult:
        with (
            Vertical(classes="house-rules-body"),
            SheetSection(title=self._title(), id=HOUSE_RULES_SECTION),
        ):
            yield TableHeader("  " + hr.table_header())
            yield SelectableList(self._rows(), id="house-rules-list")
        yield DetailsPanel(hr.detail_text(self.saga, None), id="house-rules-panel")

    def selected_entry(self) -> tuple[str, hr.Entry] | None:
        index = self.query_one("#house-rules-list", SelectableList).selected_data_index
        if index is None or index >= len(self._entries):
            return None
        return self._entries[index]

    @property
    def entries(self) -> list[tuple[str, hr.Entry]]:
        return self._entries

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        event.stop()
        chosen = (
            self._entries[event.data_index]
            if event.data_index < len(self._entries)
            else None
        )
        self.query_one("#house-rules-panel", Static).update(
            hr.detail_text(self.saga, chosen)
        )

    def rebuild(self) -> None:
        """Re-read the entries after an add, edit or delete."""
        try:
            self._entries = hr.all_entries(self.saga)
            self.query_one(f"#{HOUSE_RULES_SECTION}", Collapsible).title = self._title()
            self.query_one("#house-rules-list", SelectableList).set_rows(self._rows())
            self.query_one("#house-rules-panel", Static).update(
                hr.detail_text(self.saga, None)
            )
        except NoMatches:
            return  # the view is being replaced


#: The Players view's list section (a / e / d act on the saga's players).
PLAYERS_SECTION = "section-players"


class PlayersView(Vertical):
    """Who can sign in to the saga from a browser, in one list
    stretching down to the details panel of the chosen player."""

    DEFAULT_CSS = """
    PlayersView {
        height: 1fr;
    }

    PlayersView .players-body {
        height: 1fr;
    }
    """

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga

    def _title(self) -> str:
        return counted("Players", len(self.saga.players))

    def _rows(self) -> list[tuple[int, str]]:
        return [(i, pl.row_label(p)) for i, p in enumerate(self.saga.players)]

    def compose(self) -> ComposeResult:
        with (
            Vertical(classes="players-body"),
            SheetSection(title=self._title(), id=PLAYERS_SECTION),
        ):
            yield TableHeader("  " + pl.table_header())
            yield SelectableList(self._rows(), id="players-list")
        yield DetailsPanel(pl.detail_text(self.saga, None), id="players-panel")

    def selected_player(self) -> Player | None:
        index = self.query_one("#players-list", SelectableList).selected_data_index
        if index is None or index >= len(self.saga.players):
            return None
        return self.saga.players[index]

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        event.stop()
        players = self.saga.players
        chosen = players[event.data_index] if event.data_index < len(players) else None
        self.query_one("#players-panel", Static).update(
            pl.detail_text(self.saga, chosen)
        )

    def rebuild(self) -> None:
        """Re-read the players after an add, edit or delete."""
        try:
            self.query_one(f"#{PLAYERS_SECTION}", Collapsible).title = self._title()
            self.query_one("#players-list", SelectableList).set_rows(self._rows())
            self.query_one("#players-panel", Static).update(
                pl.detail_text(self.saga, None)
            )
        except NoMatches:
            return  # the view is being replaced


class LabTextListView(BookListView):
    """A laboratory's Lab Texts database: the book list with the
    Lab Texts' own columns (lab_texts.table_header), narrowed by a filter
    and read for one reader, the laboratory's owner (`reader`, called as
    the list is built). Always inline: the sheet's shared panel shows the
    chosen text."""

    def __init__(
        self,
        saga: Saga,
        books: Callable[[], list[Book]],
        reader: Callable[[], Character | None],
        *,
        section_id: str,
        group: str | None = None,
    ) -> None:
        self._all_texts = books
        self._reader = reader
        self.filter = lt.Filter()
        super().__init__(
            saga,
            self._shown,
            section_id=section_id,
            title="Lab Texts",
            docked=False,
            group=group,
        )
        self._layout = lt.Columns()

    @property
    def reader(self) -> Character | None:
        return self._reader()

    def _shown(self) -> list[Book]:
        return lt.filtered(self.saga, self._reader(), self._all_texts(), self.filter)

    def _title(self, checked: int = 0) -> str:
        title = lt.title(len(self._books), len(self._all_texts()), self.filter)
        return title + (f" - {checked} marked" if checked else "")

    def _rows(self) -> list[tuple[int, str]]:
        reader = self._reader()
        return [
            (i, lt.row_label(self.saga, reader, b, self._layout))
            for i, b in enumerate(self._books)
        ]

    def _header(self) -> str:
        return "  " + lt.table_header(self._layout)

    def on_resize(self) -> None:
        """Give the Name column whatever room the list has (and the Sigil
        column only where it fits)."""
        layout = lt.columns(self.size.width - 4 - 4)
        if layout == self._layout:
            return
        self._layout = layout
        try:
            self.query_one(".books-header", Static).update(self._header())
            self.query_one(SelectableList).relabel([label for _, label in self._rows()])
        except NoMatches:
            return

    def set_filter(self, wanted: lt.Filter) -> None:
        self.filter = wanted
        self.rebuild()

    def detail_text(self, index: int | None) -> str:
        book = (
            self._books[index]
            if index is not None and index < len(self._books)
            else None
        )
        return lt.detail_text(self.saga, self._reader(), book)


#: The Spells view's list section (a / e / d act on the saga's own spells).
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
        #: Before any filter is set: the spells in play.
        self._shown: list[Spell] = spl.filter_spells(saga, self._all)

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
                    [(f"{key} - {name}", key) for key, name in spl.catalog_sources()]
                    + [
                        ("The saga's own", spl.OWN_SOURCE),
                        ("Not in play", spl.OUT_OF_PLAY_SOURCE),
                    ],
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
