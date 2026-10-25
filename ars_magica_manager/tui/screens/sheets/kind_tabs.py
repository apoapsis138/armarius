"""The tabs a kind of neighbour adds to its sheet (neighbour_lists.KindTab),
drawn for any sheet that shows them: a neighbour's, and a covenant's
Manors tab, whose record is adapted to a neighbour's (manors.manors_of)."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Static

from ....markup import aligned, escape
from ....models import Neighbour, Saga
from ....neighbour_lists import KindBlock, KindList, KindTab
from ..widgets import SelectableList, SheetSection, TwoColumns, fact_markup
from .base import SheetView


def list_id(section_id: str) -> str:
    return f"{section_id.removeprefix('section-')}-list"


def panel_id(tab: KindTab) -> str:
    """The id of a kind's tab's details panel: its tab id's, as info."""
    return f"{tab.tab_id.removeprefix('tab-')}-info"


class KindTabsView(SheetView):
    """A sheet showing kind tabs: their lists and blocks over a details
    panel for the chosen row, when the tab has one."""

    #: Sections whose change every kind tab's text follows besides its own
    #: (the record's top panel).
    KIND_WATCHED: tuple[str, ...] = ()

    def __init__(self, saga: Saga) -> None:
        super().__init__(saga)
        #: Per tab with a details panel, the list and row it shows.
        self._kind_chosen: dict[str, tuple[KindList, int]] = {}

    def kind_holder(self) -> Neighbour:
        """The record the kind tabs show."""
        raise NotImplementedError

    def kind_tabs(self) -> list[KindTab]:
        """The kind tabs the sheet shows."""
        raise NotImplementedError

    def _kind_facts(self) -> str:
        """What the kind works out, shown at the top of its first tab."""
        return ""

    def _kind_tab(self, tab: KindTab, facts: bool = False) -> ComposeResult:
        """What the kind works out (on its first tab, `facts`), then its
        lists and blocks; over a details panel for the chosen row, when the
        tab has one."""
        if not tab.panel:
            yield from self._kind_parts(tab, facts)
            return
        with Vertical(classes="panel-body"):
            yield from self._kind_parts(tab, facts)
            yield self._panel(
                self._watched(tab),
                lambda: self._kind_panel_text(tab),
                id=panel_id(tab),
            )

    def _watched(self, tab: KindTab) -> tuple[str, ...]:
        return (*self.KIND_WATCHED, *(part.section_id for part in tab.parts()))

    def _kind_parts(self, tab: KindTab, facts: bool) -> ComposeResult:
        saga, n = self.saga, self.kind_holder()
        watched = self._watched(tab)
        with VerticalScroll():
            if facts:
                # What is worked out follows every kind tab: a lord's manors
                # count on his Fief.
                every = tuple(
                    part.section_id for t in self.kind_tabs() for part in t.parts()
                )
                yield self._static(
                    (*self.KIND_WATCHED, *every), self._kind_facts, id="nb-kind-facts"
                )
            for part in tab.parts():
                if isinstance(part, KindBlock):
                    yield from self._kind_block(part, watched)
                    continue
                with SheetSection(
                    title=self._titled(
                        watched, part.section_id, lambda e=part: e.title(saga, n)
                    ),
                    id=part.section_id,
                ):
                    if part.header is not None:
                        header = part.header
                        yield self._static(
                            watched,
                            lambda h=header: h(saga, n),
                            id=f"{list_id(part.section_id)}-header",
                        )
                    yield self._list(
                        watched,
                        lambda e=part: e.grid(saga, n).lines(),
                        id=list_id(part.section_id),
                    )

    def _kind_block(self, block: KindBlock, watched: tuple[str, ...]) -> ComposeResult:
        """A block of worked-out text: its facts, its text, then its
        columns."""
        saga, n = self.saga, self.kind_holder()
        stem = block.section_id.removeprefix("section-")
        with SheetSection(title=block.title, id=block.section_id):
            facts, text = block.facts, block.text
            if facts is not None:
                yield self._static(
                    watched,
                    lambda: aligned(
                        [
                            (f.label, fact_markup(f) or "[$label]—[/]")
                            for f in facts(saga, n)
                        ]
                    ),
                    id=f"{stem}-facts",
                )
            if text is not None:
                yield self._static(watched, lambda: text(saga, n), id=f"{stem}-text")
            columns = block.columns
            if columns is not None:
                with TwoColumns(id=f"{stem}-columns", text=True):
                    for index in range(len(columns(saga, n))):
                        yield self._static(
                            watched,
                            lambda i=index: columns(saga, n)[i],
                            id=f"{stem}-column-{index}",
                        )

    def _kind_panel_text(self, tab: KindTab) -> str:
        """The details panel of `tab`: its chosen row in full, or its hint."""
        chosen = self._kind_chosen.get(tab.tab_id)
        if chosen is None:
            return tab.panel
        entry, index = chosen
        n = self.kind_holder()
        grid = entry.grid(self.saga, n)
        if index not in grid.keys:
            return tab.panel
        if entry.info is None:
            return grid.row_text(index)
        name = grid.rows[grid.keys.index(index)][0]
        info = entry.info(self.saga, n, index)
        return f"[b]{escape(name)}[/]\n{info}" if info else tab.panel

    def _kind_row_chosen(self, event: SelectableList.Chosen) -> bool:
        """Show a chosen row of a kind tab's list in its tab's details
        panel, when the tab has one; whether it was one."""
        chosen_id = event.selectable_list.id or ""
        for tab in self.kind_tabs():
            if not tab.panel:
                continue
            entry = next(
                (e for e in tab.lists if list_id(e.section_id) == chosen_id), None
            )
            if entry is None:
                continue
            event.stop()
            self._kind_chosen[tab.tab_id] = (entry, event.data_index)
            self.query_one(f"#{panel_id(tab)}", Static).update(
                self._kind_panel_text(tab)
            )
            return True
        return False
