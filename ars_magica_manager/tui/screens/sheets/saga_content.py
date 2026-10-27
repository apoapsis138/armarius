"""The Saga Content view: one place for what the saga's pickers offer --
its books in play and own sources, the shared catalogs it hides, its House
Rules, its own spells and (for the storyguide) its players."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Static, TabbedContent, TabPane

from .... import saga_content as sc
from .... import traditions
from ....boon_hook_text import counted
from ....forms import goods as goods_forms
from ....forms import mystery_cults as cult_forms
from ....models import Saga, SagaSource
from ....sections import (
    BOOKS_SECTION,
    CATALOGS_SECTION,
    CULT_DEGREES_SECTION,
    CULT_SCRIPT_SECTION,
    CULT_SECTION,
    CULTS_SECTION,
    GOODS_SECTION,
    HIDDEN_SECTION,
    HOUSE_RULES_SECTION,
    PLAYERS_SECTION,
    SOURCES_SECTION,
    SPELL_SECTION,
    TRADITIONS_SECTION,
)
from ..widgets import SelectableList, SheetSection, TableHeader
from .base import SheetView
from .lists import HouseRulesView, PlayersView, SpellListView

#: Each tab's list section: what a / e / d act on when focus is elsewhere
#: in the tab (the Spells tab's filter bar).
TAB_SECTIONS: dict[str, str] = {
    "tab-content-books": BOOKS_SECTION,
    "tab-content-catalogs": CATALOGS_SECTION,
    "tab-content-goods": GOODS_SECTION,
    "tab-content-house-rules": HOUSE_RULES_SECTION,
    "tab-content-spells": SPELL_SECTION,
    "tab-content-players": PLAYERS_SECTION,
    "tab-content-cults": CULTS_SECTION,
}

#: The Goods tab's list and its details panel.
GOODS_LIST = "content-goods-list"
GOODS_INFO = "content-goods-info"

#: The Mystery Cults tab's sections, which each change redraws whole (a
#: cult's degrees and Scripts are counted and named in the others), its
#: lists and its details panel; and what choosing a cult or a degree
#: redraws.
CULT_SECTIONS = (CULTS_SECTION, CULT_SECTION, CULT_DEGREES_SECTION, CULT_SCRIPT_SECTION)
CULTS_LIST = "content-cults-list"
DEGREES_LIST = "content-cult-degrees-list"
SCRIPT_LIST = "content-cult-scripts-list"
CULTS_INFO = "content-cults-info"
_CULT_CHOSEN = "content-cult-chosen"
_DEGREE_CHOSEN = "content-cult-degree-chosen"


class SagaContentSheetView(SheetView):
    """The Saga Content view mounted into the workspace's detail pane: tabs
    for Books (in play, and the saga's own sources), Catalogs (whole
    catalogs and single entries the saga hides), House Rules, Spells and,
    for the storyguide, Players. The last three are the list views that
    used to be tree nodes of their own."""

    INITIAL_TAB = "tab-content-books"

    def __init__(self, saga: Saga, *, players: bool) -> None:
        super().__init__(saga)
        #: Whether the Players tab is shown (to the storyguide only).
        self.players = players
        #: The Mystery Cults tab's chosen cult and degree (data indexes),
        #: kept across redraws, which clear the lists' choices; and the
        #: section whose row the details panel shows.
        self.cult_index: int | None = None
        self.degree_index: int | None = None
        self._cult_panel: tuple[str, int | None] = (CULTS_SECTION, None)

    def compose(self) -> ComposeResult:
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Books", "tab-content-books", self._books_tab)
            yield self._tab("Catalogs", "tab-content-catalogs", self._catalogs_tab)
            yield self._tab("Goods", "tab-content-goods", self._goods_tab)
            yield self._tab(
                "House Rules",
                "tab-content-house-rules",
                lambda: iter([HouseRulesView(self.saga)]),
            )
            yield self._tab("Mystery Cults", "tab-content-cults", self._cults_tab)
            yield self._tab(
                "Spells", "tab-content-spells", lambda: iter([SpellListView(self.saga)])
            )
            if self.players:
                yield self._tab(
                    "Players",
                    "tab-content-players",
                    lambda: iter([PlayersView(self.saga)]),
                )

    def tab_first_stop(self, pane: TabPane) -> Widget | None:
        """The Spells tab's list, not the search box above it: a / e / d
        work straight away, and / moves to the search."""
        if pane.id == "tab-content-spells":
            found = pane.query("#spell-list")
            if found:
                return found.first()
        return super().tab_first_stop(pane)

    # -- Books --

    def _books_tab(self) -> ComposeResult:
        saga = self.saga
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                with SheetSection(
                    title=self._titled(BOOKS_SECTION, BOOKS_SECTION, self._books_title),
                    id=BOOKS_SECTION,
                ):
                    yield TableHeader(sc.books_header())
                    yield self._list(
                        (BOOKS_SECTION, SOURCES_SECTION),
                        lambda: list(
                            enumerate(map(self._book_row, sc.every_book(saga)))
                        ),
                        id="content-books-list",
                        group="content-books",
                    )
                with SheetSection(
                    title=self._titled(
                        SOURCES_SECTION,
                        SOURCES_SECTION,
                        lambda: counted("Saga Sources", len(saga.sources)),
                    ),
                    id=SOURCES_SECTION,
                ):
                    yield TableHeader(sc.sources_header())
                    yield self._list(
                        SOURCES_SECTION,
                        lambda: [
                            (i, sc.source_row(saga, s))
                            for i, s in enumerate(saga.sources)
                        ],
                        id="content-sources-list",
                        group="content-books",
                    )
                with SheetSection(
                    title=self._titled(
                        (BOOKS_SECTION, TRADITIONS_SECTION),
                        TRADITIONS_SECTION,
                        self._traditions_title,
                    ),
                    id=TRADITIONS_SECTION,
                ):
                    yield TableHeader(sc.traditions_header())
                    yield self._list(
                        (BOOKS_SECTION, TRADITIONS_SECTION),
                        lambda: list(enumerate(sc.tradition_rows(saga))),
                        id="content-traditions-list",
                        group="content-books",
                    )
            yield self._panel(
                (BOOKS_SECTION, SOURCES_SECTION),
                lambda: sc.book_detail(saga, None),
                id="content-books-info",
            )

    def _traditions_title(self) -> str:
        shown = traditions.in_play(self.saga)
        on = sum(1 for t in shown if traditions.is_on(self.saga, t.id))
        return f"Traditions Offered ({on} of {len(shown)})"

    def _book_row(self, book: str) -> str:
        return sc.book_row(self.saga, book)

    def _books_title(self) -> str:
        every = sc.every_book(self.saga)
        in_play = sum(1 for b in every if sc.is_in_play(self.saga, b))
        return f"Books in Play ({in_play} of {len(every)})"

    def _chosen(self, list_id: str) -> int | None:
        """The data index of the chosen row of a list (None before its tab
        is first shown)."""
        found = self.query(f"#{list_id}").results(SelectableList)
        rows = next(found, None)
        return rows.selected_data_index if rows is not None else None

    def selected_book(self) -> str | None:
        index = self._chosen("content-books-list")
        every = sc.every_book(self.saga)
        return every[index] if index is not None and index < len(every) else None

    def selected_source(self) -> SagaSource | None:
        index = self._chosen("content-sources-list")
        sources = self.saga.sources
        return sources[index] if index is not None and index < len(sources) else None

    # -- Catalogs --

    def _catalogs_tab(self) -> ComposeResult:
        saga = self.saga
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                with SheetSection(
                    title=self._titled(
                        CATALOGS_SECTION,
                        CATALOGS_SECTION,
                        lambda: counted("Catalogs", len(sc.CATALOGS)),
                    ),
                    id=CATALOGS_SECTION,
                ):
                    yield TableHeader(sc.catalogs_header())
                    yield self._list(
                        (CATALOGS_SECTION, HIDDEN_SECTION, GOODS_SECTION),
                        lambda: [
                            (i, sc.catalog_row(saga, key))
                            for i, key in enumerate(sc.CATALOGS)
                        ],
                        id="content-catalogs-list",
                        group="content-catalogs",
                    )
                with SheetSection(
                    title=self._titled(
                        (HIDDEN_SECTION, GOODS_SECTION),
                        HIDDEN_SECTION,
                        lambda: counted("Hidden Entries", len(sc.hidden_entries(saga))),
                    ),
                    id=HIDDEN_SECTION,
                ):
                    yield TableHeader(sc.hidden_header())
                    yield self._list(
                        (HIDDEN_SECTION, GOODS_SECTION),
                        lambda: [
                            (i, sc.hidden_row(key, entry))
                            for i, (key, entry) in enumerate(sc.hidden_entries(saga))
                        ],
                        id="content-hidden-list",
                        group="content-catalogs",
                    )
            yield self._panel(
                (CATALOGS_SECTION, HIDDEN_SECTION),
                lambda: sc.catalog_detail(saga, None),
                id="content-catalogs-info",
            )

    def selected_catalog(self) -> str | None:
        index = self._chosen("content-catalogs-list")
        keys = list(sc.CATALOGS)
        return keys[index] if index is not None and index < len(keys) else None

    def selected_hidden(self) -> tuple[str, Any] | None:
        index = self._chosen("content-hidden-list")
        hidden = sc.hidden_entries(self.saga)
        return hidden[index] if index is not None and index < len(hidden) else None

    # -- Goods --

    def _goods_tab(self) -> ComposeResult:
        """The Goods catalog and the saga's own goods, with the chosen
        good's details under them."""
        saga = self.saga
        self.core_ops[GOODS_SECTION] = goods_forms.ops(saga)
        #: What the list follows: its own changes, and a good hidden,
        #: offered again or the whole catalog switched off on Catalogs.
        follows = (GOODS_SECTION, CATALOGS_SECTION, HIDDEN_SECTION)
        with Vertical(classes="panel-body"):
            with (
                VerticalScroll(),
                SheetSection(
                    title=self._titled(
                        follows, GOODS_SECTION, lambda: goods_forms.title(saga)
                    ),
                    id=GOODS_SECTION,
                ),
            ):
                yield self._static(
                    follows,
                    lambda: goods_forms.header(saga, two_lines=True),
                    id="content-goods-header",
                )
                yield TableHeader(goods_forms.table_header())
                yield self._list(follows, lambda: goods_forms.rows(saga), id=GOODS_LIST)
            yield self._panel(
                follows,
                lambda: goods_forms.info(
                    saga, self.section_row(GOODS_SECTION), wide=True
                ),
                id=GOODS_INFO,
            )

    # -- Mystery Cults --

    def chosen_cult(self) -> int | None:
        return self.cult_index

    def chosen_degree(self) -> int | None:
        return self.degree_index

    def _cults_tab(self) -> ComposeResult:
        """The saga's own Mystery Cults, the chosen one, its degrees and
        the chosen degree's Script, with the chosen row's details under
        them (forms/mystery_cults.py)."""
        saga = self.saga
        cult, degree = self.chosen_cult, self.chosen_degree
        self.core_ops[CULTS_SECTION] = cult_forms.cults_ops(saga)
        self.core_ops[CULT_SECTION] = cult_forms.cult_ops(saga, cult)
        self.core_ops[CULT_DEGREES_SECTION] = cult_forms.degree_ops(saga, cult)
        self.core_ops[CULT_SCRIPT_SECTION] = cult_forms.script_ops(saga, cult, degree)
        follows = CULT_SECTIONS
        on_cult = (*follows, _CULT_CHOSEN)
        on_degree = (*on_cult, _DEGREE_CHOSEN)
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                with SheetSection(
                    title=self._titled(
                        follows, CULTS_SECTION, lambda: cult_forms.cults_title(saga)
                    ),
                    id=CULTS_SECTION,
                ):
                    yield TableHeader(cult_forms.cults_header())
                    yield self._list(
                        follows, lambda: cult_forms.cult_rows(saga), id=CULTS_LIST
                    )
                with SheetSection(
                    title=self._titled(
                        on_cult, CULT_SECTION, lambda: cult_forms.cult_title(saga, cult)
                    ),
                    id=CULT_SECTION,
                ):
                    yield self._static(
                        on_cult,
                        lambda: cult_forms.cult_text(saga, cult),
                        id="content-cult-text",
                    )
                with SheetSection(
                    title=self._titled(
                        on_cult,
                        CULT_DEGREES_SECTION,
                        lambda: cult_forms.degrees_title(saga, cult),
                    ),
                    id=CULT_DEGREES_SECTION,
                ):
                    yield TableHeader(cult_forms.degrees_header())
                    yield self._list(
                        on_cult,
                        lambda: cult_forms.degree_rows(saga, cult),
                        id=DEGREES_LIST,
                    )
                with SheetSection(
                    title=self._titled(
                        on_degree,
                        CULT_SCRIPT_SECTION,
                        lambda: cult_forms.script_title(saga, cult, degree),
                    ),
                    id=CULT_SCRIPT_SECTION,
                ):
                    yield TableHeader(cult_forms.script_header())
                    yield self._list(
                        on_degree,
                        lambda: cult_forms.script_rows(saga, cult, degree),
                        id=SCRIPT_LIST,
                    )
            yield self._panel(on_degree, self._cult_panel_text, id=CULTS_INFO)
        # After a change redraws the lists, choose the cult and degree again.
        self._on_refresh(follows, self._rechoose_cult)

    def _cult_panel_text(self) -> str:
        section, row = self._cult_panel
        return cult_forms.panel_text(
            self.saga, self.chosen_cult, self.chosen_degree, section, row
        )

    def _rechoose_cult(self) -> None:
        """Choose the remembered cult and degree again in the redrawn lists
        (or forget one that is gone)."""
        cults = self.query_one(f"#{CULTS_LIST}", SelectableList)
        if self.cult_index is not None and not cults.select_data_index(self.cult_index):
            self.cult_index = self.degree_index = None
            self.refresh_section(_CULT_CHOSEN)
            return
        degrees = self.query_one(f"#{DEGREES_LIST}", SelectableList)
        if self.degree_index is not None and not degrees.select_data_index(
            self.degree_index
        ):
            self.degree_index = None
            self.refresh_section(_DEGREE_CHOSEN)

    def _cult_chosen(self, list_id: str, index: int) -> bool:
        """A row of the Mystery Cults tab was chosen: follow it. False for a
        list of another tab."""
        if list_id == CULTS_LIST:
            self._cult_panel = (CULTS_SECTION, index)
            if index != self.cult_index:
                self.cult_index, self.degree_index = index, None
                self.refresh_section(_CULT_CHOSEN)
                return True
        elif list_id == DEGREES_LIST:
            self._cult_panel = (CULT_DEGREES_SECTION, index)
            if index != self.degree_index:
                self.degree_index = index
                self.refresh_section(_DEGREE_CHOSEN)
                return True
        elif list_id == SCRIPT_LIST:
            self._cult_panel = (CULT_SCRIPT_SECTION, index)
        else:
            return False
        self.query_one(f"#{CULTS_INFO}", Static).update(self._cult_panel_text())
        return True

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A row was chosen: fill its tab's details panel."""
        list_id = event.selectable_list.id or ""
        if self._cult_chosen(list_id, event.data_index):
            event.stop()
            return
        if list_id == GOODS_LIST:
            event.stop()
            self.query_one(f"#{GOODS_INFO}", Static).update(
                goods_forms.info(self.saga, event.data_index, wide=True)
            )
            return
        texts = {
            "content-books-list": (
                "#content-books-info",
                lambda: sc.book_detail(self.saga, self.selected_book()),
            ),
            "content-sources-list": (
                "#content-books-info",
                lambda: sc.source_detail(self.saga, self.selected_source()),
            ),
            "content-traditions-list": (
                "#content-books-info",
                lambda: sc.tradition_detail(
                    self.saga, self._chosen("content-traditions-list")
                ),
            ),
            "content-catalogs-list": (
                "#content-catalogs-info",
                lambda: sc.catalog_detail(self.saga, self.selected_catalog()),
            ),
            "content-hidden-list": (
                "#content-catalogs-info",
                lambda: sc.hidden_detail(self.selected_hidden()),
            ),
        }
        found = texts.get(list_id)
        if found is None:
            return
        event.stop()
        panel, text = found
        self.query_one(panel, Static).update(text())
