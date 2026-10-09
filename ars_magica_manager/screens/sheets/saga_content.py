"""The Saga Content view: one place for what the saga's pickers offer --
its books in play and own sources, the shared catalogs it hides, its House
Rules, its own spells and (for the storyguide) its players."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Static, TabbedContent, TabPane

from ... import saga_content as sc
from ...models import Saga, SagaSource
from ..widgets import SelectableList, SheetSection, TableHeader, counted
from .base import SheetView
from .lists import HouseRulesView, PlayersView, SpellListView

BOOKS_SECTION = "section-books-in-play"
SOURCES_SECTION = "section-saga-sources"
CATALOGS_SECTION = "section-catalogs"
HIDDEN_SECTION = "section-hidden-entries"

#: Each tab's list section: what a / e / d act on when focus is elsewhere
#: in the tab (the Spells tab's filter bar).
TAB_SECTIONS: dict[str, str] = {
    "tab-content-books": BOOKS_SECTION,
    "tab-content-catalogs": CATALOGS_SECTION,
    "tab-content-house-rules": "section-house-rules",
    "tab-content-spells": "section-spells",
    "tab-content-players": "section-players",
}


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

    def compose(self) -> ComposeResult:
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Books", "tab-content-books", self._books_tab)
            yield self._tab("Catalogs", "tab-content-catalogs", self._catalogs_tab)
            yield self._tab(
                "House Rules",
                "tab-content-house-rules",
                lambda: iter([HouseRulesView(self.saga)]),
            )
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
            yield self._panel(
                (BOOKS_SECTION, SOURCES_SECTION),
                lambda: sc.book_detail(saga, None),
                id="content-books-info",
            )

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
                        (CATALOGS_SECTION, HIDDEN_SECTION),
                        lambda: [
                            (i, sc.catalog_row(saga, key))
                            for i, key in enumerate(sc.CATALOGS)
                        ],
                        id="content-catalogs-list",
                        group="content-catalogs",
                    )
                with SheetSection(
                    title=self._titled(
                        HIDDEN_SECTION,
                        HIDDEN_SECTION,
                        lambda: counted("Hidden Entries", len(sc.hidden_entries(saga))),
                    ),
                    id=HIDDEN_SECTION,
                ):
                    yield TableHeader(sc.hidden_header())
                    yield self._list(
                        HIDDEN_SECTION,
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

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A row was chosen: fill its tab's details panel."""
        list_id = event.selectable_list.id or ""
        texts = {
            "content-books-list": (
                "#content-books-info",
                lambda: sc.book_detail(self.saga, self.selected_book()),
            ),
            "content-sources-list": (
                "#content-books-info",
                lambda: sc.source_detail(self.saga, self.selected_source()),
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
