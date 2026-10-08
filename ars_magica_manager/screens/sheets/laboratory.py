"""The Laboratory sheet."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Collapsible,
    Static,
    TabbedContent,
)

from ... import books as bk
from ... import catalog, lab_planning, seasons
from ... import lab_texts as lt
from ... import laboratories as lab_text
from ...covenants import (
    covenant_effective_aura,
)
from ...laboratories import (
    lab_aura_total,
    lab_base_safety,
    lab_characteristic_total,
    lab_free_virtues,
    lab_occupied_size,
)
from ...markup import aligned, escape
from ...models import (
    LAB_CHARACTERISTICS,
    Laboratory,
    Saga,
)
from ...rules import realms
from ..widgets import (
    DetailsPanel,
    PinnedCollapsible,
    SelectableList,
    SheetSection,
    StackingColumns,
    ToggleList,
    TwoColumns,
    _sign_colored,
    counted,
    points_title,
)
from .base import SheetView
from .lists import LAB_TEXTS_SECTION, BookListView, LabTextListView

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


#: The lab sheet sections whose changes move its Lab Totals.
_LAB_TOTAL_SECTIONS: tuple[str, ...] = (
    "tab-lab-totals",
    "section-lab-identity",
    "section-lab-characteristics",
    "section-lab-specializations",
    "section-lab-specialties",
    "section-lab-features",
    "section-lab-vf-virtues",
    "section-lab-vf-flaws",
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
    details panel where there's more to show than the row.

    Specializations is a grid of each Specialization's total
    over every source, grouped Activity / Art with each cap's count in the
    header, where Space turns the chosen one off or on (ToggleList); the
    hand-entered sources are a list nested inside it ("Specializations:
    Other"). Features lists the lab's Features, each built on
    one of its Feature Virtues. Neither section collapses.

    The Attributes and Inventory tabs each have one details panel docked
    below their scrolling lists, as on the covenant's tabs: the
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

    @property
    def creation_record(self) -> Laboratory:
        return self.laboratory

    INITIAL_TAB = "tab-lab-planning"

    def compose(self) -> ComposeResult:
        yield from self._top_panel()
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Planning", "tab-lab-planning", self._planning_tab)
            yield self._tab(
                "Lab Totals", "tab-lab-totals", self._scrolling(self._totals_tab)
            )
            yield self._tab("Virtues & Flaws", "tab-lab-vf", self._virtues_flaws_tab)
            yield self._tab("Attributes", "tab-lab-attributes", self._attributes_tab)
            yield self._tab("Inventory", "tab-lab-inventory", self._inventory_tab)
            yield self._tab("Diary", "tab-lab-diary", self._diary_tab)

    def _planning_tab(self) -> ComposeResult:
        """The owner's coming seasons: lab work is planned here,
        with the chosen season's plan and Lab Total docked below."""
        sections = ("tab-lab-planning", "section-lab-identity", *_LAB_TOTAL_SECTIONS)
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                yield self._static(
                    sections,
                    self._planning_heading,
                    id="lab-planning-heading",
                )
                yield self._list(
                    sections,
                    lambda: seasons.lab_queue_rows(self.saga, self.laboratory),
                    id="lab-seasons-list",
                )
            yield self._panel(
                sections,
                lambda: seasons.lab_queue_info(self.saga, self.laboratory, None),
                id="lab-seasons-info",
            )

    def _planning_heading(self) -> str:
        owner = self.saga.character(self.laboratory.owner_id)
        if owner is None:
            return "[dim]No owner: give the laboratory one to plan its seasons.[/]"
        return (
            f"[b]{escape(owner.name)}'s seasons[/]  [dim]e plan lab work, "
            "a start a new spell, d clear[/]"
        )

    def selected_lab_season(self) -> int | None:
        """The chosen row of the Planning tab's seasons (0: the current)."""
        return self._selected("lab-seasons-list")

    def _totals_tab(self) -> ComposeResult:
        """The Lab Totals grid, the Base Lab Total and what each activity
        adds, each its own section."""
        for title, section, text in (
            (
                "Lab Totals",
                "section-lab-totals-grid",
                lab_planning.lab_totals_grid_text,
            ),
            (
                "Base Lab Total",
                "section-lab-totals-base",
                lab_planning.base_lab_total_text,
            ),
            (
                "By Activity",
                "section-lab-totals-activity",
                lab_planning.activity_totals_text,
            ),
        ):
            with SheetSection(title=title, id=section):
                yield self._static(
                    _LAB_TOTAL_SECTIONS,
                    lambda text=text: text(
                        self.saga,
                        self.laboratory,
                        self.saga.character(self.laboratory.owner_id),
                    ),
                    id=f"{section}-content",
                )

    def _diary_tab(self) -> ComposeResult:
        with Vertical(classes="panel-body"):
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
                with SheetSection(
                    title=self._titled(
                        "section-lab-connections",
                        "section-lab-connections",
                        lambda: counted(
                            "Arcane Connections",
                            len(self.laboratory.arcane_connections),
                        ),
                    ),
                    id="section-lab-connections",
                ):
                    yield self._list(
                        "section-lab-connections",
                        lambda: lab_text.connection_rows(self.laboratory),
                        id="lab-connections-list",
                        group="lab-inv",
                    )
                yield from self._devices(
                    "laboratory",
                    self.laboratory.id,
                    "section-lab-devices",
                    group="lab-inv",
                )
                yield self._lab_text_list()
                yield self._book_list(
                    ("section-lab-identity",),
                    lambda: lt.other_books_of(
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
                "section-lab-connections",
                "section-lab-devices",
                LAB_TEXTS_SECTION,
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
            "lab-connections-list": (
                "lab-inv-panel",
                lambda i: lab_text.connection_info_text(lab, i),
            ),
            "section-lab-devices-list": (
                "lab-inv-panel",
                lambda i: self._device_panel_text(
                    "laboratory", lab.id, i, lab_text.INVENTORY_PANEL_HINT
                ),
            ),
            f"{LAB_TEXTS_SECTION}-list": ("lab-inv-panel", self._lab_text_panel_text),
            "section-lab-books-list": ("lab-inv-panel", self._book_panel_text),
            "lab-diary-list": (
                "lab-diary-info",
                lambda i: lab_text.diary_info_text(lab.diary, i),
            ),
            "lab-seasons-list": (
                "lab-seasons-info",
                lambda i: seasons.lab_queue_info(self.saga, lab, i),
            ),
        }

    def _lab_text_list(self) -> LabTextListView:
        """The Lab Texts database, read for the lab's owner;
        rebuilt with the lab's other books (a book's Type can change) and
        when the owner does."""
        view = LabTextListView(
            self.saga,
            lambda: lt.texts_of(self.saga, "laboratory", self.laboratory.id),
            lambda: self.saga.character(self.laboratory.owner_id),
            section_id=LAB_TEXTS_SECTION,
            group="lab-inv",
        )
        self._on_refresh(
            (LAB_TEXTS_SECTION, "section-lab-books", "section-lab-identity"),
            view.rebuild,
        )
        return view

    def lab_text_view(self) -> LabTextListView:
        return self.query_one(LabTextListView)

    def _lab_text_panel_text(self, index: int | None) -> str:
        return self.lab_text_view().detail_text(index)

    def _book_panel_text(self, index: int | None) -> str:
        if index is None:
            return lab_text.INVENTORY_PANEL_HINT
        books = self.query_one("#section-lab-books", Collapsible).parent
        assert isinstance(books, BookListView)
        listed = books.books
        return bk.detail_text(self.saga, listed[index] if index < len(listed) else None)

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

    def selected_connection(self) -> int | None:
        """Index into laboratory.arcane_connections of the chosen row, or
        None."""
        return self._selected("lab-connections-list")

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
                yield from self._top_buttons("btn-lab-identity-edit")
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
                ("Build Points", lab_text.lab_build_points(lab)),
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
        realm = covenant.aura_realm if covenant else "Magic"
        total = lab_aura_total(lab, covenant_aura)
        note = realms.aura_note(realm, total)
        return (
            f"Aura: {covenant_aura} (covenant) {lab.aura_modifier:+d} (modifier) "
            f"= {total} {realm}" + (f" ({note})" if note else "")
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
