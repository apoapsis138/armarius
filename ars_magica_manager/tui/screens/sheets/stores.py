"""The Armarium and the Custodia Mirabilium (stores.py) as the terminal
draws them: one sheet for either store, its filter (holder and type) over
the list of the store's items, the chosen one's details docked below.

The list's Add, Edit and Delete are the core's (forms/stores.py),
counting into the rows the filter shows now; More's Give gives the
chosen row's item (sections.GIVE_SECTIONS)."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Select, Static, TabbedContent, TabPane

from .... import stores
from ....forms import stores as store_forms
from ....markup import aligned
from ....models import Saga
from ..widgets import SelectableList, SheetSection, fact_markup
from .base import SheetView

#: A store's tab, by its key: the sheet's one tab.
TABS = {stores.ARMARIUM: "tab-armarium", stores.CUSTODIA: "tab-custodia"}


def list_id(store: stores.Store) -> str:
    return f"{store.section.removeprefix('section-')}-list"


class StoreSheetView(SheetView):
    """A store: its filter, then its list over the chosen item's details."""

    DEFAULT_CSS = """
    StoreSheetView .store-filters {
        height: 1;
        width: 1fr;
        margin: 0 1 1 1;
    }

    StoreSheetView .store-filters Select {
        width: 36;
        margin-right: 2;
    }
    """

    def __init__(self, saga: Saga, store: stores.Store) -> None:
        super().__init__(saga)
        self.store = store
        self.INITIAL_TAB = TABS[store.key]
        self.filter = stores.Filter()
        self._shown: list[Any] = stores.shown(saga, store, self.filter)
        self._chosen: Any | None = None
        self._holder_options = self._holders()
        self.state_ops[store.section] = store_forms.store_ops(
            saga, store, lambda: self._shown
        )

    @property
    def shown(self) -> list[Any]:
        """The items listed, in row order."""
        return self._shown

    def tab_first_stop(self, pane: TabPane) -> Widget | None:
        """The list, not the filter above it: a, e and d act there."""
        found = pane.query(f"#{list_id(self.store)}")
        return found.first() if found else super().tab_first_stop(pane)

    def _item_list(self) -> SelectableList:
        return self.query_one(f"#{list_id(self.store)}", SelectableList)

    def marked(self) -> list[Any]:
        """The items marked (Space or Ctrl+click) for acting on together:
        the Armarium's books only."""
        rows = self._item_list().checked_data_indexes
        return [self._shown[i] for i in rows if i < len(self._shown)]

    def chosen(self) -> Any | None:
        """The item on the chosen row."""
        row = self._item_list().selected_data_index
        return self._shown[row] if row is not None and row < len(self._shown) else None

    def compose(self) -> ComposeResult:
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab(self.store.heading, TABS[self.store.key], self._store_tab)

    def _store_tab(self) -> ComposeResult:
        store = self.store
        with Vertical(classes="panel-body"):
            with Horizontal(classes="store-filters"):
                yield Select(
                    self._holder_options,
                    prompt="Holder: all",
                    id="store-holder",
                    compact=True,
                )
                yield Select(
                    stores.kind_choices(store)[1:],
                    prompt="Type: any",
                    id="store-kind",
                    compact=True,
                )
            self._on_refresh(store.section, self._refilter)
            with (
                VerticalScroll(),
                SheetSection(title=self._title(), id=store.section),
            ):
                yield SelectableList(
                    self._rows(),
                    id=list_id(store),
                    # Several books are given one owner, or deleted, at once.
                    multi=store.key == stores.ARMARIUM,
                )
            yield self._panel(store.section, self._details, id="store-details")

    def _holders(self) -> list[tuple[str, str]]:
        """The holder filter's choices but "All holders" (the Select's
        blank)."""
        return stores.holder_choices(self.saga, self.store)[1:]

    def _title(self) -> str:
        return stores.title(self.saga, self.store, self._shown)

    def _rows(self) -> list[tuple[int | None, str]]:
        return stores.grid(self.saga, self.store, self._shown).lines()

    def _details(self) -> str:
        item = self._chosen
        if item is not None and item not in self._shown:
            item = self._chosen = None
        if item is None:
            return stores.details(self.saga, self.store, None)
        holder = stores.holder_fact(self.saga, self.store, item)
        return "\n".join(
            [
                aligned([(holder.label, fact_markup(holder))]),
                "",
                stores.details(self.saga, self.store, item),
            ]
        )

    def _refilter(self) -> None:
        """Re-read the store through the filter and redraw the list (the
        chosen item stays chosen while it is listed). The holders offered
        follow who holds anything now."""
        holders = self._holders()
        if holders != self._holder_options:
            self._holder_options = holders
            select = self.query_one("#store-holder", Select)
            with select.prevent(Select.Changed):
                select.set_options(holders)
                if any(value == self.filter.holder for _, value in holders):
                    select.value = self.filter.holder
                else:
                    self.filter = stores.Filter(kind=self.filter.kind)
        chosen = self._chosen
        self._shown = stores.shown(self.saga, self.store, self.filter)
        self._set_section_title(
            self.query_one(f"#{self.store.section}", SheetSection), self._title()
        )
        rows = self._item_list()
        rows.set_rows(self._rows())
        if chosen is not None and chosen in self._shown:
            rows.select_data_index(self._shown.index(chosen))

    def choose(self, item_id: str) -> bool:
        """Choose the row of the item `item_id` (Find), clearing a filter
        that hides it; False when the store has no such item."""
        if not any(item.id == item_id for item in self.store.items(self.saga)):
            return False
        if not any(item.id == item_id for item in self._shown):
            for select_id in ("#store-holder", "#store-kind"):
                select = self.query_one(select_id, Select)
                with select.prevent(Select.Changed):
                    select.clear()
            self.filter = stores.Filter()
            self._refilter()
        index = next(n for n, item in enumerate(self._shown) if item.id == item_id)
        return self._item_list().select_data_index(index)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id not in ("store-holder", "store-kind"):
            return
        event.stop()
        holder = self.query_one("#store-holder", Select).value
        kind = self.query_one("#store-kind", Select).value
        wanted = stores.Filter(
            holder=holder if isinstance(holder, str) else "",
            kind=kind if isinstance(kind, str) else "",
        )
        if wanted != self.filter:
            self.filter = wanted
            self.refresh_section(self.store.section)

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        if event.selectable_list.id != list_id(self.store):
            return
        event.stop()
        index = event.data_index
        self._chosen = self._shown[index] if 0 <= index < len(self._shown) else None
        self.query_one("#store-details", Static).update(self._details())
