"""The Covenant sheet."""

from __future__ import annotations

from collections.abc import Callable
from typing import ClassVar

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.widgets import (
    Collapsible,
    Static,
    TabbedContent,
)

from .... import (
    ahead,
    ahead_forms,
    arms,
    book_value,
    catalog,
    seasons,
    tribunals,
    world,
    world_forms,
)
from .... import books as bk
from .... import covenant_build as cov_build
from .... import covenant_diary as cov_diary
from .... import economics as eco
from .... import inhabitants as inh
from .... import possessions as pos
from ....boon_hook_text import (
    boon_hook_info_text,
    boon_hook_rows,
    boon_hook_title,
    counted,
)
from ....covenants import (
    boon_hook_problems,
    covenant_effective_aura,
)
from ....markup import aligned, escape, markdown_inline, problem
from ....models import (
    FULL,
    INHABITANT_KINDS,
    LINE,
    POSSESSION_KINDS,
    Character,
    Covenant,
    Saga,
)
from ....rules import realms
from ....sections import COV_AHEAD_SECTION, MAGI_SECTION, WHAT_MATTERS_SECTION
from ..widgets import (
    DetailsPanel,
    PinnedCollapsible,
    SelectableList,
    SheetSection,
    TableHeader,
    TwoColumns,
)
from .base import SheetView


class CovenantSheetView(SheetView):
    """The covenant sheet mounted into WorkspaceScreen's detail pane.

    A permanent info panel (not inside any tab) above eight tabs mirroring
    the covenant record sheet: Attributes, Inhabitants, Seasons (who has
    planned what this season), Possessions, Economics, Library,
    Diary, and Build (what its Build Points went on).

    The panel's saga-level values (Saga, Storyguide, Current Season,
    Current Year) are inherited from the Saga and shown dimmed/read-only;
    the rest belong to the covenant and are edited with 'e'.
    """

    def __init__(self, saga: Saga, covenant: Covenant) -> None:
        super().__init__(saga)
        self.covenant = covenant
        #: A Line or Sketch covenant: its magi, What Matters and attitudes
        #: on one Overview, and only its Diary beside it.
        self.sketch = covenant.detail != FULL
        if self.sketch:
            self.INITIAL_TAB = "tab-cov-overview"
            self.core_ops = world_forms.covenant_ops(saga, covenant)
        elif not covenant.played:
            self.core_ops = world_forms.record_ops(saga, covenant)
        if not self.sketch:
            self.core_ops = {
                **self.core_ops,
                COV_AHEAD_SECTION: ahead_forms.ahead_ops(saga, covenant),
            }
        self._register_refreshers()

    def _register_refreshers(self) -> None:
        """What each of the sheet's sections feeds besides its own widgets
        (those register themselves as they're built). A refresher whose tab
        isn't built yet is skipped: the tab is built from the current data."""
        on = self._on_refresh
        on("section-cov-info", self._refresh_info)
        on("section-cov-description", self._refresh_description)
        on("section-cov-reputations", self._refresh_reputations)
        on("section-inh-loyalty", self._refresh_loyalty_text)
        on(("section-inh-population", "section-inh-misc"), self._refresh_population)
        # An Aura Boon changes the Aura in the info panel, and so Loyalty.
        on(
            ("section-cov-boons", "section-cov-hooks"),
            self._rebuild_boons_hooks,
        )
        on(("section-cov-boons", "section-cov-hooks"), self._refresh_info)
        on(("section-cov-boons", "section-cov-hooks"), self._refresh_loyalty_text)
        # A Story Event can unlock a Hidden Resources Boon's Build Points.
        on("tab-cov-diary", self._rebuild_boons_hooks)

        def family(*prefixes: str) -> Callable[[str], bool]:
            return lambda section_id: section_id.startswith(prefixes)

        inhabitants = family("section-inh-")
        summaries = (
            "section-inh-loyalty",
            "section-inh-population",
            "section-inh-misc",
        )
        match = self._on_refresh_matching
        # Any other Inhabitants section is one of the lists.
        match(
            lambda s: inhabitants(s) and s not in summaries, self._rebuild_inhabitants
        )
        match(family("section-pos-"), self._rebuild_possessions)
        match(family("section-eco-"), self._rebuild_economics)
        # Marking someone departed takes them off the Seasons lists.
        match(inhabitants, lambda: SheetView.refresh_section(self, "tab-cov-seasons"))
        # Every change can change what the Build Points went on, and
        # Poverty's warning depends on the Boons, Hooks and income.
        match(lambda _: True, self._refresh_build)
        match(lambda _: True, self._refresh_bh_warnings)
        # Inhabitants, Possessions and the covenant's own sections feed the
        # Economics tab's figures.
        match(
            family("section-inh-", "section-pos-", "section-cov-"),
            self._rebuild_economics,
        )
        # Magi (Gift), Specialists/Companions (role bonus), covenant
        # Reputations and Living Conditions (Mundane) feed the Loyalty block,
        # which lives on a different section; so do the Diary's Loyalty
        # points (Actions and Events).
        match(
            lambda s: (
                s in ("section-cov-info", "section-cov-reputations", "tab-cov-diary")
                or (inhabitants(s) and s != "section-inh-loyalty")
            ),
            self._refresh_loyalty_text,
        )

    @property
    def creation_record(self) -> Covenant:
        return self.covenant

    INITIAL_TAB = "tab-cov-attributes"

    def compose(self) -> ComposeResult:
        with PinnedCollapsible(title=escape(self.covenant.name), id="section-cov-info"):
            with TwoColumns(id="cov-info-body", text=True):
                yield Static(self._info_left_text(), id="cov-info-left")
                yield Static(self._info_right_text(), id="cov-info-right")
            if self.sketch:
                yield self._static(
                    "section-cov-info", self._summary_text, id="cov-summary"
                )
            yield from self._top_buttons("btn-cov-edit")
        if self.sketch:
            with TabbedContent(initial=self.INITIAL_TAB):
                yield self._tab(
                    "Overview", "tab-cov-overview", self._scrolling(self._overview_tab)
                )
                yield self._tab("Diary", "tab-cov-diary", self._diary_tab)
            return
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Attributes", "tab-cov-attributes", self._attributes_tab)
            yield self._tab("Inhabitants", "tab-cov-inhabitants", self._inhabitants_tab)
            yield self._tab("Seasons", "tab-cov-seasons", self._seasons_tab)
            yield self._tab("Possessions", "tab-cov-possessions", self._possessions_tab)
            yield self._tab("Economics", "tab-cov-economics", self._economics_tab)
            yield self._tab("Library", "tab-cov-library", self._library_tab)
            yield self._tab("Diary", "tab-cov-diary", self._diary_tab)
            yield self._tab("Build", "tab-cov-build", self._scrolling(self._build_tab))

    def _summary_text(self) -> str:
        summary = self.covenant.summary.strip()
        if not summary:
            return "[$label]In the Saga: not written yet. Edit the covenant to say.[/]"
        return markdown_inline(summary)

    def _overview_tab(self) -> ComposeResult:
        """A Line or Sketch covenant: its magi and their votes, What Matters
        beside its attitude to each player covenant, then favours and
        links. A Line covenant has only its attitudes, favours and links."""
        saga, covenant = self.saga, self.covenant
        if covenant.detail != LINE:
            with SheetSection(
                title=self._titled(
                    (MAGI_SECTION, "section-cov-info"),
                    MAGI_SECTION,
                    lambda: world_forms.magi_title(saga, covenant),
                ),
                id=MAGI_SECTION,
            ):
                yield self._list(
                    (MAGI_SECTION, "section-cov-info"),
                    lambda: world_forms.magi_rows(saga, covenant),
                    id="cov-magi-list",
                )
            with TwoColumns(id="cov-sketch-row"):
                with SheetSection(title="What Matters", id=WHAT_MATTERS_SECTION):
                    yield self._static(
                        WHAT_MATTERS_SECTION,
                        lambda: world_forms.what_matters_text(covenant),
                        id="cov-what-matters",
                    )
                with Vertical():
                    yield from self._relations(covenant)
        else:
            yield from self._relations(covenant)

    def _build_tab(self) -> ComposeResult:
        """What the covenant's Build Points went on: the one
        place Build Points show once the covenant is in play."""
        with SheetSection(
            title=cov_build.title(self.saga, self.covenant), id="section-cov-build"
        ):
            yield Static(
                cov_build.table_text(self.saga, self.covenant), id="cov-build-table"
            )
        with SheetSection(title="What's Counted", id="section-cov-build-items"):
            yield Static(
                cov_build.items_text(self.saga, self.covenant), id="cov-build-items"
            )

    def _refresh_build(self) -> None:
        """Anything the covenant owns can change its Build Points."""
        # The top panel shows the Build Points spent while In Creation.
        self.query_one("#cov-info-right", Static).update(self._info_right_text())
        self._set_section_title(
            self.query_one("#section-cov-build", Collapsible),
            cov_build.title(self.saga, self.covenant),
        )
        self.query_one("#cov-build-table", Static).update(
            cov_build.table_text(self.saga, self.covenant)
        )
        self.query_one("#cov-build-items", Static).update(
            cov_build.items_text(self.saga, self.covenant)
        )

    def _attributes_tab(self) -> ComposeResult:
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                with SheetSection(title="Description", id="section-cov-description"):
                    yield Static(self._description_text(), id="cov-description-content")
                with SheetSection(
                    title=self._titled(
                        "section-cov-reputations",
                        "section-cov-reputations",
                        lambda: counted("Reputations", len(self.covenant.reputations)),
                    ),
                    id="section-cov-reputations",
                ):
                    yield SelectableList(
                        self._reputation_rows(), id="cov-reputations-list"
                    )
                # Takes no room unless there is something to warn about.
                warnings = Static(self._bh_warnings_text(), id="cov-bh-warnings")
                warnings.display = bool(self._bh_warnings_text())
                yield warnings
                if not self.covenant.played:
                    yield from self._relations(self.covenant)
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

    def _seasons_tab(self) -> ComposeResult:
        """Who is in the covenant and what each has planned for the current
        season, by kind, over the chosen person's details."""
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                with SheetSection(
                    title=self._titled(
                        COV_AHEAD_SECTION,
                        COV_AHEAD_SECTION,
                        lambda: ahead.title(self.saga, self.covenant),
                    ),
                    id=COV_AHEAD_SECTION,
                ):
                    yield self._list(
                        COV_AHEAD_SECTION,
                        lambda: ahead.grid(self.saga, self.covenant).lines(),
                        id="cov-ahead-list",
                    )
                for kind, title in seasons.SEASON_KINDS:
                    section = f"section-cov-seasons-{kind}"
                    with SheetSection(
                        title=self._titled(
                            "tab-cov-seasons",
                            section,
                            lambda kind=kind, title=title: seasons.season_title(
                                self.saga, self.covenant, kind, title
                            ),
                        ),
                        id=section,
                    ):
                        yield self._list(
                            "tab-cov-seasons",
                            lambda kind=kind: seasons.season_rows(
                                self.saga, self.covenant, kind
                            ),
                            id=f"cov-seasons-{kind}-list",
                            group="seasons",
                        )
            yield self._panel(
                "tab-cov-seasons",
                lambda: seasons.season_info_text(self.saga, None),
                id="cov-seasons-info",
            )

    def selected_season_person(self) -> Character | None:
        """The person chosen in any of the Seasons lists, or None."""
        for kind, _ in seasons.SEASON_KINDS:
            try:
                chosen = self.query_one(
                    f"#cov-seasons-{kind}-list", SelectableList
                ).selected_data_index
            except NoMatches:
                return None  # the tab isn't built yet
            if chosen is not None:
                people = seasons.covenant_people(self.saga, self.covenant, kind)
                return people[chosen] if chosen < len(people) else None
        return None

    def _library_tab(self) -> ComposeResult:
        yield self._book_list(
            ("section-cov-info",),
            lambda: bk.books_in_covenant(self.saga, self.covenant),
            section_id="section-lib-books",
            summary=True,
            research=lambda: book_value.research_count(self.saga, self.covenant),
        )

    def _diary_tab(self) -> ComposeResult:
        with Vertical(classes="panel-body"):
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
        and its panel is refreshed, unless the list gained or lost a row (a
        delete would otherwise choose the next row in its place)."""
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
            rows = self._eco_rows(which, summary)
            if len(rows) != rows_list.row_count:
                chosen = None
            rows_list.set_rows(rows)
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

    def _refresh_loyalty_text(self) -> None:
        self.query_one("#inh-loyalty-left", Static).update(
            inh.loyalty_left_text(self.saga, self.covenant)
        )
        self.query_one("#inh-loyalty-right", Static).update(
            inh.loyalty_right_text(self.saga, self.covenant)
        )

    def _refresh_info(self) -> None:
        self.query_one("#section-cov-info", Collapsible).title = escape(
            self.covenant.name
        )
        self.query_one("#cov-info-left", Static).update(self._info_left_text())
        self.query_one("#cov-info-right", Static).update(self._info_right_text())

    def _refresh_description(self) -> None:
        self.query_one("#cov-description-content", Static).update(
            self._description_text()
        )

    def _refresh_reputations(self) -> None:
        self.query_one("#cov-reputations-list", SelectableList).set_rows(
            self._reputation_rows()
        )

    def _refresh_population(self) -> None:
        self.query_one("#inh-population-content", Static).update(
            inh.population_text(self.saga, self.covenant)
        )
        left, right = inh.misc_text(self.covenant)
        self.query_one("#inh-misc-left", Static).update(left)
        self.query_one("#inh-misc-right", Static).update(right)

    def _bh_warnings_text(self) -> str:
        """Boons and Hooks that don't fit together, one line
        each in the theme's error colour; "" when all is well."""
        problems = boon_hook_problems(
            self.covenant, catalog.load_covenant_boon_hook_catalog_by_id()
        )
        return "\n".join(problem(escape(p)) for p in problems)

    def _refresh_bh_warnings(self) -> None:
        text = self._bh_warnings_text()
        warnings = self.query_one("#cov-bh-warnings", Static)
        warnings.update(text)
        warnings.display = bool(text)

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
        if list_id.startswith("cov-seasons-"):
            event.stop()
            self.query_one("#cov-seasons-info", Static).update(
                seasons.season_info_text(self.saga, self.selected_season_person())
            )
            return
        if list_id == "cov-ahead-list":
            event.stop()
            found = ahead.shown(self.saga, self.covenant)
            index = event.data_index
            if index < len(found):
                self.query_one("#cov-seasons-info", Static).update(
                    ahead.detail_text(self.saga, found[index])
                )
            return
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

    def _aura_realm_text(self) -> str:
        """The aura's realm, and how it touches Hermetic magic when that
        isn't simply +aura."""
        cov = self.covenant
        effective = covenant_effective_aura(
            cov, catalog.load_covenant_boon_hook_catalog_by_id()
        )
        note = realms.aura_note(cov.aura_realm, effective)
        return cov.aura_realm + (f" ({note})" if note else "")

    def _tribunal_text(self) -> str:
        tribunal = tribunals.of(self.saga, self.covenant)
        return escape(tribunal.name) if tribunal is not None else "(not set)"

    def _info_left_text(self) -> str:
        cov, saga = self.covenant, self.saga
        if self.sketch:
            rows = [("Tribunal", self._tribunal_text())]
            if cov.detail != LINE:
                founded = (
                    "(not set)" if cov.year_founded is None else str(cov.year_founded)
                )
                rows += [("Founded", founded), ("Season", cov.covenant_season)]
            return aligned(rows)
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
        if self.sketch:
            played = "yes" if cov.played else "no"
            rows = [("Detail", f"{cov.detail}   played: {played}")]
            if cov.detail != LINE:
                rows += [
                    ("Votes", world.votes_text(saga, cov)),
                    ("Aura", self._aura_text()),
                ]
            return aligned(rows + self._arms_rows())
        return aligned(
            [
                ("Tribunal", self._tribunal_text()),
                ("Current Season", self._inherited(saga.current_season)),
                ("Current Year", self._inherited(str(saga.current_year))),
                ("Aegis' Penetration", str(cov.aegis_penetration)),
                ("Living Conditions (Mundane)", str(cov.living_conditions_mundane)),
                ("Covenant Season", cov.covenant_season),
                ("Aura Realm", self._aura_realm_text()),
                # While it's being created: what's spent of its Build Points.
                *(
                    [("Build Points", cov_build.summary(saga, cov))]
                    if cov.in_creation
                    else []
                ),
                *self._arms_rows(),
            ]
        )

    def _arms_rows(self) -> list[tuple[str, str]]:
        borne = arms.arms_of(self.covenant)
        if borne is None:
            return []
        motto = [("Motto", f"[i]{escape(borne.motto)}[/]")] if borne.motto else []
        return [*motto, ("Arms", escape(arms.blazon(borne)))]

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
        return boon_hook_title(self.covenant, kind)

    def _bh_entries(self, kind: str) -> list[tuple[int, str]]:
        return boon_hook_rows(self.covenant, kind)

    def _bh_info_text(self, index: int | None) -> str:
        return boon_hook_info_text(self.covenant, index)
