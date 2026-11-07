"""Conflicts: the saga's battles, fights and sieges. Its facts, then the
Battles, Fights and Sieges lists, over the chosen one in full. What they
show is worked out in battles.py, fights.py and sieges.py, and
conflicts.py edits and plays them."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Static, TabbedContent

from .... import battles, conflicts, fights, sieges, viewing
from ....markup import aligned
from ....models import Saga
from ....sections import (
    CONFLICT_BATTLES_SECTION,
    CONFLICTS_INFO_SECTION,
    FIGHTS_SECTION,
    SIEGES_SECTION,
)
from ..widgets import (
    PinnedCollapsible,
    SelectableList,
    SheetSection,
    TwoColumns,
    fact_markup,
)
from .base import SheetView

#: The one choice the three lists share: the details panel shows it.
_GROUP = "conflicts"
_PANEL = "conflicts-info-panel"


def _list_id(section_id: str) -> str:
    return f"{section_id.removeprefix('section-')}-list"


class ConflictsSheetView(SheetView):
    """Conflicts: how many battles, fights and sieges, then the three lists
    over the chosen one in full."""

    DEFAULT_CSS = """
    ConflictsSheetView #conflicts-top-panel {
        width: 1fr;
        height: auto;
    }
    """

    INITIAL_TAB = "tab-conflicts"

    def __init__(self, saga: Saga) -> None:
        super().__init__(saga)
        #: The list and row the details panel shows.
        self._chosen: tuple[str, int] | None = None

    def compose(self) -> ComposeResult:
        watched = (
            CONFLICTS_INFO_SECTION,
            CONFLICT_BATTLES_SECTION,
            FIGHTS_SECTION,
            SIEGES_SECTION,
        )
        with (
            Vertical(id="conflicts-top-panel"),
            PinnedCollapsible(title="Conflicts", id=CONFLICTS_INFO_SECTION),
            TwoColumns(id="conflicts-info-body", text=True),
        ):
            yield self._static(
                watched, lambda: self._facts(0), id="conflicts-info-left"
            )
            yield self._static(
                watched, lambda: self._facts(1), id="conflicts-info-right"
            )
        with TabbedContent(initial=self.INITIAL_TAB):
            yield self._tab("Fights and Sieges", "tab-conflicts", self._lists_tab)

    def _facts(self, column: int) -> str:
        facts = conflicts.header_facts(self.saga)
        half = (len(facts) + 1) // 2
        shown = facts[:half] if column == 0 else facts[half:]
        return aligned([(f.label, fact_markup(f)) for f in viewing.facts(shown)])

    def _lists_tab(self) -> ComposeResult:
        saga = self.saga
        with Vertical(classes="panel-body"):
            with VerticalScroll():
                for section, title, grid in (
                    (CONFLICT_BATTLES_SECTION, battles.title, battles.grid),
                    (FIGHTS_SECTION, fights.title, fights.grid),
                    (SIEGES_SECTION, sieges.title, sieges.grid),
                ):
                    with SheetSection(
                        title=self._titled(
                            section, section, lambda title=title: title(saga)
                        ),
                        id=section,
                    ):
                        yield self._list(
                            section,
                            lambda grid=grid: grid(saga).lines(),
                            id=_list_id(section),
                            group=_GROUP,
                        )
            yield self._panel(
                (CONFLICT_BATTLES_SECTION, FIGHTS_SECTION, SIEGES_SECTION),
                self._details,
                id=_PANEL,
            )

    def _details(self) -> str:
        if self._chosen is not None:
            section, index = self._chosen
            if section == CONFLICT_BATTLES_SECTION:
                battle = battles.battle_of(self.saga, index)
                if battle is not None:
                    return battles.info(self.saga, battle)
            elif section == FIGHTS_SECTION:
                fight = fights.fight_of(self.saga, index)
                if fight is not None:
                    return fights.info(self.saga, fight)
            else:
                siege = sieges.siege_of(self.saga, index)
                if siege is not None:
                    return sieges.info(self.saga, siege)
        return "[$label]Choose a battle, fight or siege to see it in full.[/]"

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A battle, fight or siege was chosen: show it in full."""
        for section in (CONFLICT_BATTLES_SECTION, FIGHTS_SECTION, SIEGES_SECTION):
            if event.selectable_list.id == _list_id(section):
                event.stop()
                self._chosen = (section, event.data_index)
                self.query_one(f"#{_PANEL}", Static).update(self._details())
                return
