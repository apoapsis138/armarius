"""The desktop's page for the Armarium or the Custodia Mirabilium
(stores.py): the store's filter (holder and type) over a table of its
items, with Add, Edit, Delete and Give, and the chosen item in the
inspector, its holder a link that opens it.

What it says comes from the core (stores.py), and what its buttons do
from forms/stores.py and giving.py, as the terminal's store sheet does.
The filter is kept while the page is drawn again after a change.
"""

from __future__ import annotations

from typing import Any, ClassVar

from PySide6.QtWidgets import QHBoxLayout, QLabel, QTableView, QVBoxLayout, QWidget

from .. import saga_index, stores
from ..forms import library as library_forms
from ..forms import stores as store_forms
from ..models import Saga
from .character_sheet import section
from .editing import Chooser, Run, follower, give_verb, verb_buttons
from .figures import fact_grid
from .pages import page_header
from .themes import Palette
from .widgets import (
    Codex,
    edit_button,
    filter_choice,
    offer_rows,
    scrolling_page,
    serif,
    table_view,
    text,
)

#: The list Find's Spot names on each store's page.
SPOT_LISTS = {stores.ARMARIUM: saga_index.BOOKS, stores.CUSTODIA: saga_index.DEVICES}


class StorePage(QWidget):
    """A store in the Codex layout: one chapter, its list."""

    #: Each store's filter as it was last set, by the store's key.
    remembered: ClassVar[dict[str, stores.Filter]] = {}

    def __init__(
        self,
        saga: Saga,
        store: stores.Store,
        p: Palette,
        run: Run = lambda _command: None,
    ) -> None:
        super().__init__()
        self.saga, self.store, self.p, self.run = saga, store, p, run
        wanted = StorePage.remembered.get(store.key, stores.Filter())
        self.shown: list[Any] = stores.shown(saga, store, wanted)
        if wanted.holder and not any(
            value == wanted.holder for _, value in stores.holder_choices(saga, store)
        ):
            # Nobody holds anything for that holder now.
            wanted = stores.Filter(kind=wanted.kind)
            self.shown = stores.shown(saga, store, wanted)
        self.wanted = wanted
        self.chooser = Chooser()
        self.ops = store_forms.store_ops(saga, store, lambda: self.shown)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(page_header(store.title, store.subtitle, p, store.icon))
        self.codex = Codex(p)
        self.codex.add(store.heading, store.icon, self._chapter())
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def _chapter(self) -> QWidget:
        p, saga, store = self.p, self.saga, self.store
        self.holder = filter_choice(
            "All holders", stores.holder_choices(saga, store)[1:]
        )
        self.kind = filter_choice("Any type", stores.kind_choices(store)[1:])
        for combo, value in (
            (self.holder, self.wanted.holder),
            (self.kind, self.wanted.kind),
        ):
            index = combo.findData(value) if value else 0
            combo.setCurrentIndex(max(index, 0))
            combo.currentIndexChanged.connect(self._refilter)
        filters = QWidget()
        row = QHBoxLayout(filters)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self.holder)
        row.addWidget(self.kind)
        row.addStretch(1)
        self.body = QWidget()
        self.rows = QVBoxLayout(self.body)
        self.rows.setContentsMargins(0, 0, 0, 0)
        self.table: QTableView | QLabel | None = None
        buttons = verb_buttons(
            self.ops,
            self.chooser,
            self.run,
            p,
            more=[give_verb(saga, store.gives, None, lambda: self.shown)],
        )
        if store.key == stores.ARMARIUM and len(store.items(saga)) > 1:
            # Several of the books listed given one owner at once.
            buttons.append(
                edit_button(
                    "Change Owner",
                    p,
                    lambda: self.run(library_forms.change_owner(saga, self.shown)),
                    "library",
                )
            )
        heading = section(
            stores.title(saga, store, self.shown),
            p,
            filters,
            offer_rows(self.body, SPOT_LISTS[store.key], self.choose),
            buttons=buttons,
        )
        self.title = heading.findChild(QLabel)
        self._fill()
        return scrolling_page(p, heading)

    def _fill(self) -> None:
        """Draw the table of what the filter shows."""
        p, saga, store = self.p, self.saga, self.store
        if self.table is not None:
            self.rows.removeWidget(self.table)
            # Hidden now: deleteLater leaves it drawn until the next turn.
            self.table.hide()
            self.table.deleteLater()
        grid = stores.grid(saga, store, self.shown)
        self.table = (
            table_view(grid.table(), p, self._inspect)
            if self.shown
            else text(grid.empty, p["dim"], serif(12.5, italic=True), wrap=True)
        )
        self.rows.addWidget(self.table)
        if self.title is not None:
            self.title.setText(stores.title(saga, store, self.shown))
        self.chooser.choose(None)

    def _refilter(self) -> None:
        holder, kind = self.holder.currentData(), self.kind.currentData()
        self.wanted = stores.Filter(
            holder=holder if isinstance(holder, str) else "",
            kind=kind if isinstance(kind, str) else "",
        )
        StorePage.remembered[self.store.key] = self.wanted
        self.shown = stores.shown(self.saga, self.store, self.wanted)
        self._fill()

    def _inspect(self, row: int) -> None:
        """Choose row `row` and show its item in the inspector, its
        holder a link that opens it."""
        self.chooser.choose(row)
        saga, store = self.saga, self.store
        item = self.shown[row]
        holder = fact_grid(
            [stores.holder_fact(saga, store, item)],
            self.p,
            1,
            follow=follower(self.run),
        )
        self.codex.inspect(
            store.cells(saga, item)[0],
            stores.subtitle(saga, store, item),
            stores.details(saga, store, item),
            None,
            None,
            holder,
        )

    def choose(self, item_id: str) -> QWidget | None:
        """Choose the row of the item `item_id` (Find), clearing a filter
        that hides it; None when the store has no such item."""
        if not any(item.id == item_id for item in self.store.items(self.saga)):
            return None
        if not any(item.id == item_id for item in self.shown):
            for combo in (self.holder, self.kind):
                combo.blockSignals(True)
                combo.setCurrentIndex(0)
                combo.blockSignals(False)
            self._refilter()
        row = next(n for n, item in enumerate(self.shown) if item.id == item_id)
        table = self.table
        if isinstance(table, QTableView):
            table.selectRow(row)
        self._inspect(row)
        return table
