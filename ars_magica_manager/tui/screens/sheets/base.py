"""What every record sheet shares: SheetView and its lazily built tabs."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.content import Content
from textual.css.query import NoMatches
from textual.widget import Widget
from textual.widgets import (
    Button,
    Collapsible,
    Static,
    TabbedContent,
    TabPane,
)
from textual.widgets._collapsible import CollapsibleTitle

from .... import enchanted_devices as ed
from .... import world
from ....boon_hook_text import counted
from ....commands import SectionOps
from ....forms import world as world_forms
from ....markup import escape, inherited
from ....models import (
    FULL,
    Book,
    Character,
    Covenant,
    Laboratory,
    Saga,
)
from ....sections import ATTITUDE_SECTION, FAVOURS_SECTION, LINKS_SECTION
from ..widgets import DetailsPanel, SelectableList, SheetSection, first_stop
from .lists import BookListView


class LazyTabPane(TabPane):
    """A sheet tab whose contents are built the first time it's shown: mounting every
    tab when a sheet opens cost ~4 ms per widget for tabs nobody had looked at. Built
    from the current data, so a tab built late is never stale; until then its sections
    have no refreshers, so refreshing them does nothing."""

    def __init__(
        self, title: str, build: Callable[[], ComposeResult], *, id: str, lazy: bool
    ) -> None:
        super().__init__(title, id=id)
        self._build = build
        self.built = not lazy

    def compose(self) -> ComposeResult:
        if self.built:
            yield from self._build()

    async def ensure_built(self) -> None:
        if not self.built:
            self.built = True
            await self.recompose()


class SheetView(Vertical):
    """Base of the four record sheets (Character, Laboratory, Familiar,
    Covenant) that WorkspaceScreen mounts into its detail pane: a fixed top
    panel above a TabbedContent. Holds the saga, the flag the workspace uses
    to tell the TabbedContent's first TabActivated from a real tab switch,
    and the layout rules every sheet shares."""

    DEFAULT_CSS = """
    SheetView {
        height: 1fr;
    }

    SheetView TabbedContent {
        height: 1fr;
    }

    SheetView TabPane {
        padding: 1 0;
    }

    SheetView VerticalScroll {
        height: 1fr;
        width: 1fr;
    }

    /* A tab with a details panel: its scrolling part fills the space down
       to the panel (DetailsPanel), which is docked at the bottom. */
    SheetView .panel-body {
        height: 1fr;
    }

    /* A top panel's Edit button, with the In Creation / In Play switch
       beside it. */
    SheetView .sheet-buttons {
        width: auto;
        height: auto;
    }

    SheetView .sheet-buttons Button {
        margin-right: 2;
    }
    """

    def tab_first_stop(self, pane: TabPane) -> Widget | None:
        """Where focus goes when `pane` is switched to: its first stop
        (widgets.first_stop), unless a sheet says otherwise."""
        return first_stop(pane)

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga
        #: Set once TabbedContent's initial TabActivated has been seen -- see
        #: WorkspaceScreen.on_tabbed_content_tab_activated().
        self.initial_tab_seen = False
        #: Per section id, what refresh_section() re-renders, in compose
        #: order. Filled while composing by _static()/_list()/_on_refresh(),
        #: so a widget's render call is written once, where it's built.
        self._refreshers: dict[str, list[Callable[[], None]]] = {}
        #: Refreshers for every section id a test accepts (a family of
        #: sections, or all of them), run after the section's own; filled by
        #: _on_refresh_matching().
        self._matching_refreshers: list[
            tuple[Callable[[str], bool], Callable[[], None]]
        ] = []
        #: The ids of the tabs _tab() has made, in order (they are numbered
        #: as they go; the workspace's 1 to 9 keys open them).
        self.tab_ids: list[str] = []
        #: The core's Add, Edit and Delete (commands.SectionOps) for each
        #: section in sections.CORE_SECTIONS this sheet shows.
        self.core_ops: dict[str, SectionOps] = {}

    def section_row(self, section_id: str) -> int | None:
        """The chosen row of `section_id`'s list, by its data index; 0 for a
        section with no list (its one Edit), None with no row chosen."""
        try:
            section = self.query_one(f"#{section_id}")
        except NoMatches:
            return None
        lists = section.query(SelectableList)
        if not lists:
            return 0
        return lists.first().selected_data_index

    #: The tab shown first, built as the sheet opens (the others are built on
    #: first visit -- see LazyTabPane). A sheet may choose it per record.
    INITIAL_TAB: str = ""

    def _tab(
        self, title: str, id: str, build: Callable[[], ComposeResult]
    ) -> LazyTabPane:
        """A tab showing what `build` composes, built when first shown. Its
        title leads with its number: the key that opens it."""
        self.tab_ids.append(id)
        return LazyTabPane(
            f"{len(self.tab_ids)} {title}",
            build,
            id=id,
            lazy=id != self.INITIAL_TAB,
        )

    @property
    def creation_record(self) -> Character | Covenant | Laboratory | None:
        """The record whose In Creation / In Play mode the top panel shows; None for a
        sheet without one."""
        return None

    def _mode_label(self) -> str:
        record = self.creation_record
        return "In Creation" if record is not None and record.in_creation else "In Play"

    def _top_buttons(self, edit_id: str) -> ComposeResult:
        """The top panel's Edit button and, beside it, the switch between In
        Creation and In Play: labelled with the current mode, changed only by
        clicking it or More's "In Creation / In Play" -- no key of its own."""
        record = self.creation_record
        with Horizontal(classes="sheet-buttons"):
            yield Button("Edit (e)", id=edit_id, compact=True)
            mode = Button(self._mode_label(), id="btn-mode", compact=True)
            # A Line or Sketch record has no creation mode: Promote makes it
            # a full one, In Creation.
            mode.display = getattr(record, "detail", FULL) == FULL
            yield mode
            # The Creation Worksheet, while In Creation.
            worksheet = Button("Creation Worksheet", id="btn-worksheet", compact=True)
            worksheet.display = record is not None and record.in_creation
            yield worksheet
        self._on_refresh("section-creation", self._refresh_mode)

    def _refresh_mode(self) -> None:
        record = self.creation_record
        self.query_one("#btn-mode", Button).label = self._mode_label()
        self.query_one("#btn-worksheet", Button).display = (
            record is not None and record.in_creation
        )

    @staticmethod
    def _scrolling(build: Callable[[], ComposeResult]) -> Callable[[], ComposeResult]:
        """`build`, wrapped in a VerticalScroll (a flat tab)."""

        def scrolling() -> ComposeResult:
            with VerticalScroll():
                yield from build()

        return scrolling

    async def on_tabbed_content_tab_activated(
        self, event: TabbedContent.TabActivated
    ) -> None:
        # Build the tab before the event bubbles on to the workspace, which
        # focuses the tab's first section.
        if isinstance(event.pane, LazyTabPane):
            await event.pane.ensure_built()

    async def build_all_tabs(self) -> None:
        """Build every tab now (for code and tests that walk all of a
        sheet's sections)."""
        for pane in self.query(LazyTabPane):
            await pane.ensure_built()

    def refresh_section(self, section_id: str) -> None:
        """Re-render whatever shows `section_id` after its data changed: its
        own refreshers, then the matching ones (each once). An id the sheet
        doesn't show does nothing (a change can be committed while another
        kind of sheet is on show)."""
        refreshers = [
            *self._refreshers.get(section_id, ()),
            *(
                refresh
                for match, refresh in self._matching_refreshers
                if match(section_id)
            ),
        ]
        for refresh in dict.fromkeys(refreshers):
            try:
                refresh()
            except NoMatches:
                # A tab not built yet (it is built from the current data), or
                # the sheet is being replaced or torn down (a refresh from a
                # dialog callback can land after that).
                continue

    def refresh_all(self) -> None:
        """Re-render every section the sheet shows (after a change that may
        touch any part of the record, such as a Creation Worksheet step)."""
        for section_id in list(self._refreshers):
            self.refresh_section(section_id)

    def _on_refresh(
        self, sections: str | tuple[str, ...], refresh: Callable[[], None]
    ) -> None:
        """Run `refresh` whenever any of `sections` is refreshed."""
        for section in (sections,) if isinstance(sections, str) else sections:
            self._refreshers.setdefault(section, []).append(refresh)

    def _on_refresh_matching(
        self, match: Callable[[str], bool], refresh: Callable[[], None]
    ) -> None:
        """Run `refresh` whenever a section id `match` accepts is refreshed
        (for what depends on a whole family of sections, or on any change)."""
        self._matching_refreshers.append((match, refresh))

    def _book_list(
        self,
        owner_sections: tuple[str, ...],
        books: Callable[[], list[Book]],
        *,
        section_id: str,
        **kwargs: Any,
    ) -> BookListView:
        """A BookListView, rebuilt when its own section refreshes or any of
        `owner_sections` does (they show the name of an owner its Location
        column shows, so a rename there shows up in the list too)."""
        view = BookListView(self.saga, books, section_id=section_id, **kwargs)
        self._on_refresh((section_id, *owner_sections), view.rebuild)
        return view

    def _static(
        self,
        sections: str | tuple[str, ...],
        text: Callable[[], str],
        *,
        id: str,
        **kwargs: Any,
    ) -> Static:
        """A Static showing `text()`, re-rendered when `sections` refresh."""
        self._on_refresh(
            sections, lambda: self.query_one(f"#{id}", Static).update(text())
        )
        return Static(text(), id=id, **kwargs)

    @staticmethod
    def _set_section_title(section: Collapsible, title: str) -> None:
        """Set a section's title, forcing the label to repaint. Textual's
        Content compares equal on plain text alone, so a colour-only change
        (Hooks (7 pts) turning red) would otherwise leave the old colour
        showing."""
        section.title = title
        title_widget = section.query_one(CollapsibleTitle)
        # The label reactive skips "unchanged" values too, so store the new
        # Content directly (set_reactive bypasses that check), then repaint.
        title_widget.set_reactive(type(title_widget).label, Content.from_text(title))
        title_widget._update_label()

    def _titled(
        self, sections: str | tuple[str, ...], id: str, title: Callable[[], str]
    ) -> str:
        """`title()`, for the section `id` to start with; it's set again
        whenever `sections` refresh (a count or total in it can change)."""
        self._on_refresh(
            sections,
            lambda: self._set_section_title(
                self.query_one(f"#{id}", Collapsible), title()
            ),
        )
        return title()

    def _panel(
        self, sections: str | tuple[str, ...], text: Callable[[], str], *, id: str
    ) -> DetailsPanel:
        """A DetailsPanel showing `text()`, re-rendered when `sections`
        refresh; `id` is its text's."""
        self._on_refresh(
            sections, lambda: self.query_one(f"#{id}", Static).update(text())
        )
        return DetailsPanel(text(), id=id)

    def _relations(self, record: Any, *, attitude: bool = True) -> ComposeResult:
        """A world record's Attitude (toward each player covenant), Favours
        and Links sections, edited through the core (world_forms)."""
        saga = self.saga
        if attitude:
            with SheetSection(title="Attitude", id=ATTITUDE_SECTION):
                yield self._list(
                    ATTITUDE_SECTION,
                    lambda: world_forms.attitude_rows(saga, record),
                    id="attitude-list",
                )
        with SheetSection(
            title=self._titled(
                FAVOURS_SECTION,
                FAVOURS_SECTION,
                lambda: counted("Favours", len(record.favours)),
            ),
            id=FAVOURS_SECTION,
        ):
            yield self._list(
                FAVOURS_SECTION,
                lambda: (
                    world.favour_rows(record.favours)
                    or [(None, "[$label]None owed.[/]")]
                ),
                id="favours-list",
            )
        with SheetSection(
            title=self._titled(
                LINKS_SECTION,
                LINKS_SECTION,
                lambda: counted("Links", len(record.links)),
            ),
            id=LINKS_SECTION,
        ):
            yield self._list(
                LINKS_SECTION,
                lambda: (
                    world_forms.link_rows(saga, record)
                    or [(None, "[$label]No links.[/]")]
                ),
                id="links-list",
            )

    def _list(
        self,
        sections: str | tuple[str, ...],
        rows: Callable[[], Sequence[tuple[int | None, str]]],
        *,
        id: str,
        group: str | None = None,
    ) -> SelectableList:
        """A SelectableList of `rows()`, re-filled when `sections` refresh."""
        self._on_refresh(
            sections, lambda: self.query_one(f"#{id}", SelectableList).set_rows(rows())
        )
        return SelectableList(rows(), id=id, group=group)

    def _devices(
        self, kind: str, holder_id: str, section_id: str, *, group: str
    ) -> ComposeResult:
        """The Enchanted Devices section: the devices `kind`
        `holder_id` holds, each followed by its effects."""
        with SheetSection(
            title=self._titled(
                section_id,
                section_id,
                lambda: counted(
                    "Enchanted Devices", len(ed.held_by(self.saga, kind, holder_id))
                ),
            ),
            id=section_id,
        ):
            yield self._list(
                section_id,
                lambda: ed.device_rows(self.saga, kind, holder_id),
                id=f"{section_id}-list",
                group=group,
            )

    def selected_device_row(self, section_id: str) -> int | None:
        """Index into enchanted_devices.device_targets of the row chosen in
        `section_id`'s Enchanted Devices list, or None."""
        return self.query_one(f"#{section_id}-list", SelectableList).selected_data_index

    def _device_panel_text(
        self, kind: str, holder_id: str, index: int | None, hint: str
    ) -> str:
        """The details panel for row `index` of a device list (None: `hint`)."""
        if index is None:
            return hint
        targets = ed.device_targets(self.saga, kind, holder_id)
        if index >= len(targets):
            return hint
        return ed.target_info_text(self.saga, targets[index])

    @staticmethod
    def _inherited(value: str) -> str:
        """A value that's derived or inherited (e.g. from the saga) and
        isn't edited here."""
        return inherited(escape(value))
