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

from .... import arms, neighbour_filter, neighbours, open_stories
from ....forms import neighbour as neighbour_forms
from ....markup import aligned, escape, markdown_text
from ....models import Covenant, Neighbour, Saga
from ....neighbour_lists import KindTab
from ....references import Fact
from ....sections import (
    ATTITUDE_SECTION,
    FAVOURS_SECTION,
    NEIGHBOUR_INFO_SECTION,
    REGION_COVENANTS_SECTION,
    REGION_INFO_SECTION,
    REGION_STORIES_SECTION,
)
from ....sheets import region as region_sheet
from ..widgets import (
    PinnedCollapsible,
    SelectableList,
    SheetSection,
    TwoColumns,
    fact_markup,
)
from .base import SheetView
from .kind_tabs import KindTabsView, list_id

#: Every list of neighbours the Region can show.
_GROUP_SECTIONS = tuple(g.section_id for g in neighbours.GROUPS)


def _list_id(section_id: str) -> str:
    return list_id(section_id)


def _facts_text(facts: list[Fact], column: int) -> str:
    half = (len(facts) + 1) // 2
    shown = facts[:half] if column == 0 else facts[half:]
    return aligned([(f.label, fact_markup(f)) for f in shown])


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
        #: The open story chosen, by its row (None: a neighbour is shown).
        self._story: int | None = None

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
                with SheetSection(
                    title=self._titled(
                        REGION_STORIES_SECTION,
                        REGION_STORIES_SECTION,
                        lambda: open_stories.title(saga),
                    ),
                    id=REGION_STORIES_SECTION,
                ):
                    yield self._list(
                        (REGION_STORIES_SECTION, *_GROUP_SECTIONS),
                        lambda: open_stories.grid(saga).lines(),
                        id=_list_id(REGION_STORIES_SECTION),
                    )
            yield self._panel(
                (
                    *_GROUP_SECTIONS,
                    REGION_COVENANTS_SECTION,
                    REGION_STORIES_SECTION,
                    FAVOURS_SECTION,
                ),
                self._details,
                id="region-info-panel",
            )

    def _details(self) -> str:
        if self._story is not None:
            return open_stories.text(self.saga, self._story)
        chosen = self._chosen
        if isinstance(chosen, Neighbour) and chosen not in self.saga.neighbours:
            chosen = self._chosen = None
        return region_sheet.details_text(self.saga, chosen)

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A row was chosen: show it in the details panel."""
        list_id = event.selectable_list.id or ""
        index = event.data_index
        if list_id == _list_id(REGION_STORIES_SECTION):
            event.stop()
            self._story = index
            self.query_one("#region-info-panel", Static).update(self._details())
            return
        self._story = None
        if list_id == _list_id(REGION_COVENANTS_SECTION):
            listed: list = region_sheet.others(self.saga)
        else:
            group = next(
                (g for g in neighbours.GROUPS if _list_id(g.section_id) == list_id),
                None,
            )
            if group is None:
                return
            listed = neighbour_filter.shown(self.saga, group.key)
        event.stop()
        self._chosen = listed[index] if index < len(listed) else None
        self.query_one("#region-info-panel", Static).update(self._details())


class NeighbourSheetView(KindTabsView):
    """A neighbour: its facts and summary, then its standing with the
    troupe."""

    DEFAULT_CSS = """
    NeighbourSheetView #nb-top-panel {
        width: 1fr;
        height: auto;
    }
    """

    INITIAL_TAB = "tab-nb-standing"
    KIND_WATCHED = (NEIGHBOUR_INFO_SECTION,)

    def __init__(self, saga: Saga, neighbour: Neighbour) -> None:
        super().__init__(saga)
        self.neighbour = neighbour
        self.core_ops = neighbour_forms.neighbour_ops(saga, neighbour)
        #: The kind the sheet was built for: its tab is theirs.
        self.kind = neighbours.kind_of(neighbour)
        if self.kind.tab is not None:
            self.INITIAL_TAB = self.kind.tab.tab_id
        #: The further tabs the sheet was built with.
        self._shown_more = [m.tab_id for m in self._more_tabs()]

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
                yield self._tab(
                    tab.title, tab.tab_id, partial(self._kind_tab, tab, facts=True)
                )
            for more in (m for m in self._more_tabs() if not m.after_standing):
                yield self._tab(more.title, more.tab_id, partial(self._kind_tab, more))
            yield self._tab(
                "Standing" if self.kind.attitude else "Found Here",
                "tab-nb-standing",
                self._standing_tab,
            )
            for more in (m for m in self._more_tabs() if m.after_standing):
                yield self._tab(more.title, more.tab_id, partial(self._kind_tab, more))
            yield from self._secrets_tab(self.neighbour)

    def stale(self) -> bool:
        """Whether the neighbour's kind changed since the sheet was built,
        so its tab is no longer theirs, or a tab shown only on some of
        the kind's neighbours (a place's Tomb) comes or goes."""
        return neighbours.kind_of(self.neighbour) is not self.kind or (
            self._shown_more != [m.tab_id for m in self._more_tabs()]
        )

    def _more_tabs(self) -> list[KindTab]:
        """The kind's further tabs this neighbour shows."""
        return [m for m in self.kind.more if m.shows(self.neighbour)]

    def kind_holder(self) -> Neighbour:
        return self.neighbour

    def kind_tabs(self) -> list[KindTab]:
        tab = self.kind.tab
        return ([tab] if tab is not None else []) + self._more_tabs()

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A row of a kind's list was chosen: show it in its tab's details
        panel, when the tab has one."""
        self._kind_row_chosen(event)

    def _kind_facts(self) -> str:
        facts = self.kind.facts
        if facts is None:
            return ""
        return aligned(
            [
                (f.label, fact_markup(f) or "[$label]—[/]")
                for f in facts(self.saga, self.neighbour)
            ]
        )

    def _refresh_title(self) -> None:
        panel = self.query_one(f"#{NEIGHBOUR_INFO_SECTION}", Collapsible)
        panel.title = escape(self.neighbour.name)

    def _facts(self, column: int) -> str:
        facts = region_sheet.neighbour_facts(self.saga, self.neighbour)
        borne = arms.arms_of(self.neighbour)
        if borne is not None:
            if borne.motto:
                facts.append(Fact("Motto", borne.motto))
            facts.append(Fact("Arms", arms.blazon(borne)))
        return _facts_text(facts, column)

    def _summary_text(self) -> str:
        summary = self.neighbour.summary.strip()
        if not summary:
            return "[$label]Summary: not written yet. Edit the neighbour to say.[/]"
        return markdown_text(summary)

    def _standing_tab(self) -> ComposeResult:
        yield from self._relations(self.neighbour, attitude=self.kind.attitude)
