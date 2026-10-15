"""The Region and a neighbour's sheet. The Region shows the saga's world
beyond the troupe's covenants: the other covenants, and the neighbours
in a list per group (lords and towns, the Church, universities,
factions, threats), each with its attitude toward the troupe; a
neighbour's sheet shows its facts, then its attitude, favours and links.
What they show is worked out in region_sheet.py and edited through
neighbour_forms.py."""

from __future__ import annotations

from functools import partial

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Button, Collapsible, Static, TabbedContent

from .... import neighbour_forms, neighbours, region_sheet
from ....character_sheet import Fact
from ....markup import aligned, escape, markdown_inline
from ....models import Covenant, Neighbour, Saga
from ....neighbour_lists import KindTab
from ....sections import (
    ATTITUDE_SECTION,
    FAVOURS_SECTION,
    NEIGHBOUR_INFO_SECTION,
    REGION_COVENANTS_SECTION,
    REGION_INFO_SECTION,
)
from ..widgets import PinnedCollapsible, SelectableList, SheetSection, TwoColumns
from .base import SheetView

#: Every list of neighbours the Region can show.
_GROUP_SECTIONS = tuple(g.section_id for g in neighbours.GROUPS)


def _list_id(section_id: str) -> str:
    return f"{section_id.removeprefix('section-')}-list"


def _facts_text(facts: list[Fact], column: int) -> str:
    half = (len(facts) + 1) // 2
    shown = facts[:half] if column == 0 else facts[half:]
    return aligned([(f.label, escape(f.value)) for f in shown])


class RegionSheetView(SheetView):
    """The Region: its facts, then its lists, over the chosen entry's
    details."""

    DEFAULT_CSS = """
    RegionSheetView #region-top-panel {
        width: 1fr;
        height: auto;
    }
    """

    INITIAL_TAB = "tab-region-neighbours"

    def __init__(self, saga: Saga, group: str | None = None) -> None:
        super().__init__(saga)
        self.core_ops = neighbour_forms.region_ops(saga)
        #: The group the sheet was opened on, whose list takes focus.
        self.group = group
        self._chosen: Neighbour | Covenant | None = None

    def compose(self) -> ComposeResult:
        watched = (REGION_INFO_SECTION, *_GROUP_SECTIONS, REGION_COVENANTS_SECTION)
        with (
            Vertical(id="region-top-panel"),
            PinnedCollapsible(title="The Region", id=REGION_INFO_SECTION),
            TwoColumns(id="region-info-body", text=True),
        ):
            yield self._static(watched, lambda: self._facts(0), id="region-info-left")
            yield self._static(watched, lambda: self._facts(1), id="region-info-right")
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Neighbours", "tab-region-neighbours", self._neighbours_tab)

    def _facts(self, column: int) -> str:
        return _facts_text(region_sheet.facts(self.saga), column)

    def _neighbours_tab(self) -> ComposeResult:
        saga = self.saga
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                with SheetSection(
                    title=self._titled(
                        REGION_COVENANTS_SECTION,
                        REGION_COVENANTS_SECTION,
                        lambda: region_sheet.covenants_title(saga),
                    ),
                    id=REGION_COVENANTS_SECTION,
                ):
                    yield self._list(
                        REGION_COVENANTS_SECTION,
                        lambda: region_sheet.covenants_grid(saga).lines(),
                        id=_list_id(REGION_COVENANTS_SECTION),
                    )
                for group in neighbours.groups_shown(saga):
                    with SheetSection(
                        title=self._titled(
                            group.section_id,
                            group.section_id,
                            lambda key=group.key: region_sheet.group_title(saga, key),
                        ),
                        id=group.section_id,
                    ):
                        yield self._list(
                            (*_GROUP_SECTIONS, ATTITUDE_SECTION),
                            lambda key=group.key: region_sheet.group_grid(
                                saga, key
                            ).lines(),
                            id=_list_id(group.section_id),
                        )
            yield self._panel(
                (*_GROUP_SECTIONS, REGION_COVENANTS_SECTION, FAVOURS_SECTION),
                self._details,
                id="region-info-panel",
            )

    def _details(self) -> str:
        chosen = self._chosen
        if isinstance(chosen, Neighbour) and chosen not in self.saga.neighbours:
            chosen = self._chosen = None
        return region_sheet.details_text(self.saga, chosen)

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A row was chosen: show it in the details panel."""
        list_id = event.selectable_list.id or ""
        index = event.data_index
        if list_id == _list_id(REGION_COVENANTS_SECTION):
            listed: list = region_sheet.others(self.saga)
        else:
            group = next(
                (g for g in neighbours.GROUPS if _list_id(g.section_id) == list_id),
                None,
            )
            if group is None:
                return
            listed = neighbours.members(self.saga, group.key)
        event.stop()
        self._chosen = listed[index] if index < len(listed) else None
        self.query_one("#region-info-panel", Static).update(self._details())


class NeighbourSheetView(SheetView):
    """A neighbour: its facts and summary, then its standing with the
    troupe."""

    DEFAULT_CSS = """
    NeighbourSheetView #nb-top-panel {
        width: 1fr;
        height: auto;
    }
    """

    INITIAL_TAB = "tab-nb-standing"

    def __init__(self, saga: Saga, neighbour: Neighbour) -> None:
        super().__init__(saga)
        self.neighbour = neighbour
        self.core_ops = neighbour_forms.neighbour_ops(saga, neighbour)
        #: The kind the sheet was built for: its tab is theirs.
        self.kind = neighbours.kind_of(neighbour)
        if self.kind.tab is not None:
            self.INITIAL_TAB = self.kind.tab.tab_id

    def compose(self) -> ComposeResult:
        with (
            Vertical(id="nb-top-panel"),
            PinnedCollapsible(
                title=escape(self.neighbour.name), id=NEIGHBOUR_INFO_SECTION
            ),
        ):
            self._on_refresh(NEIGHBOUR_INFO_SECTION, self._refresh_title)
            with TwoColumns(id="nb-info-body", text=True):
                yield self._static(
                    NEIGHBOUR_INFO_SECTION, lambda: self._facts(0), id="nb-info-left"
                )
                yield self._static(
                    NEIGHBOUR_INFO_SECTION, lambda: self._facts(1), id="nb-info-right"
                )
            yield self._static(
                NEIGHBOUR_INFO_SECTION, self._summary_text, id="nb-summary"
            )
            yield Button("Edit (e)", id="btn-nb-edit", compact=True)
        with TabbedContent(initial=self.INITIAL_TAB):
            tab = self.kind.tab
            if tab is not None:
                yield self._tab(tab.title, tab.tab_id, partial(self._kind_tab, tab))
            yield self._tab("Standing", "tab-nb-standing", self._standing_tab)

    def stale(self) -> bool:
        """Whether the neighbour's kind changed since the sheet was built,
        so its tab is no longer theirs."""
        return neighbours.kind_of(self.neighbour) is not self.kind

    def _kind_tab(self, tab: KindTab) -> ComposeResult:
        """What the kind works out, then its lists."""
        saga, n = self.saga, self.neighbour
        watched = (NEIGHBOUR_INFO_SECTION, *(e.section_id for e in tab.lists))
        with VerticalScroll():
            yield self._static(watched, self._kind_facts, id="nb-kind-facts")
            for entry in tab.lists:
                with SheetSection(
                    title=self._titled(
                        watched, entry.section_id, lambda e=entry: e.title(saga, n)
                    ),
                    id=entry.section_id,
                ):
                    yield self._list(
                        watched,
                        lambda e=entry: e.grid(saga, n).lines(),
                        id=_list_id(entry.section_id),
                    )

    def _kind_facts(self) -> str:
        facts = self.kind.facts
        if facts is None:
            return ""
        return aligned(
            [
                (f.label, escape(f.value) or "[$label]—[/]")
                for f in facts(self.saga, self.neighbour)
            ]
        )

    def _refresh_title(self) -> None:
        panel = self.query_one(f"#{NEIGHBOUR_INFO_SECTION}", Collapsible)
        panel.title = escape(self.neighbour.name)

    def _facts(self, column: int) -> str:
        return _facts_text(
            region_sheet.neighbour_facts(self.saga, self.neighbour), column
        )

    def _summary_text(self) -> str:
        summary = self.neighbour.summary.strip()
        if not summary:
            return "[$label]Summary: not written yet. Edit the neighbour to say.[/]"
        return markdown_inline(summary)

    def _standing_tab(self) -> ComposeResult:
        yield from self._relations(self.neighbour)
