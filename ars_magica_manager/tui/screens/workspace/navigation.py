"""WorkspaceScreen's navigation: what selecting each kind of node in the saga's
tree shows."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import ClassVar

from textual.widgets import (
    Tree,
)

from .... import books as bk
from .... import (
    neighbours,
)
from ....actions import (
    NodeKind,
)
from ..sheets import (
    BestiarySheetView,
    BookListView,
    ConflictsSheetView,
    CreatureSheetView,
    RegionSheetView,
    SagaContentSheetView,
    SeasonsSheetView,
)
from ..widgets import (
    SelectableList,
    SheetSection,
)
from .base import WorkspaceBase


class NavigationActions(WorkspaceBase):
    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        data = event.node.data
        if data is None:
            return

        kind: NodeKind = data[0]
        self.selected_kind = kind
        self._character_sheet_view = None
        self._laboratory_sheet_view = None
        self._covenant_sheet_view = None
        self._familiar_sheet_view = None
        self._saga_content_view = None
        self._tribunal_sheet_view = None
        self._region_sheet_view = None
        self._neighbour_sheet_view = None
        self._bestiary_view = None
        self._creature_sheet_view = None
        self._conflicts_view = None
        self._seasons_view = None

        handler = self._NODE_SELECTED.get(kind)
        if handler is not None:
            await handler(self, data[1] if len(data) > 1 else None)

        if self._current_sheet_view() is None:
            # Enter on a node moves into what it shows: a list view's list.
            for rows in self._detail_pane().query(SelectableList):
                rows.focus()
                break
        spot, self._spot_after_open = self._spot_after_open, None
        if spot is not None:
            self.open_spot(*spot)
        self.refresh_bindings()

    # What selecting each kind of tree node does: set the selection and
    # show its detail. `ident` is the node's record or covenant id, if any.

    async def _select_saga(self, ident: str | None) -> None:
        self.selected_covenant = None
        self.selected_character = None
        self.selected_laboratory = None
        self.selected_familiar = None
        await self._show_saga_detail()

    async def _select_covenant(self, ident: str | None) -> None:
        covenant = next(c for c in self.saga.covenants if c.id == ident)
        self.selected_covenant = covenant
        self.selected_character = None
        self.selected_laboratory = None
        self.selected_familiar = None
        await self._show_covenant_detail(covenant)

    async def _select_character_group(self, ident: str | None) -> None:
        covenant = self.saga.covenant(ident)
        self.selected_covenant = covenant
        self.selected_character = None
        await self._show_placeholder_detail(
            f"Characters in {covenant.name}" if covenant else "Unassigned Characters",
            "Select a character from the tree, or press 'n' to add one."
            if covenant
            else "These characters aren't assigned to a covenant. Select one "
            "from the tree, or press 'n' to add one.",
        )

    async def _select_character(self, ident: str | None) -> None:
        character = next(c for c in self.saga.characters if c.id == ident)
        self.selected_character = character
        self.selected_covenant = self.saga.covenant(character.covenant_id)
        self.selected_familiar = None
        await self._show_character_detail(character)

    async def _select_familiar(self, ident: str | None) -> None:
        familiar = next(f for f in self.saga.familiars if f.id == ident)
        self.selected_familiar = familiar
        self.selected_character = self.saga.character(familiar.character_id)
        self.selected_covenant = (
            self.saga.covenant(self.selected_character.covenant_id)
            if self.selected_character is not None
            else None
        )
        await self._show_familiar_detail(familiar)

    async def _select_laboratory_group(self, ident: str | None) -> None:
        covenant = self.saga.covenant(ident)
        self.selected_covenant = covenant
        self.selected_laboratory = None
        await self._show_placeholder_detail(
            f"Laboratories in {covenant.name}"
            if covenant
            else "Unassigned Laboratories",
            "Select a laboratory from the tree, or press 'n' to add one."
            if covenant
            else "These laboratories aren't assigned to a covenant. Select "
            "one from the tree, or press 'n' to add one.",
        )

    async def _select_laboratory(self, ident: str | None) -> None:
        lab = next(lab for lab in self.saga.laboratories if lab.id == ident)
        self.selected_laboratory = lab
        self.selected_covenant = self.saga.covenant(lab.covenant_id)
        await self._show_laboratory_detail(lab)

    async def _select_saga_content(self, ident: str | None) -> None:
        self.selected_covenant = None
        view = SagaContentSheetView(self.saga, players=self._is_storyguide())
        await self._set_detail(view)
        self._saga_content_view = view
        self._focus_first_section(initial=True)

    async def _select_seasons(self, ident: str | None) -> None:
        self.selected_covenant = None
        view = SeasonsSheetView(self.saga)
        await self._set_detail(view)
        self._seasons_view = view
        self._focus_first_section(initial=True)

    async def _select_region(self, ident: str | None) -> None:
        """The Region, or (`ident`) one of its groups of neighbours, whose
        list takes focus."""
        self.selected_covenant = None
        view = RegionSheetView(self.saga, ident)
        await self._set_detail(view)
        self._region_sheet_view = view
        group = next((g for g in neighbours.GROUPS if g.key == ident), None)
        if group is not None and view.query(f"#{group.section_id}"):
            self.call_after_refresh(
                view.query_one(f"#{group.section_id}", SheetSection).focus_section
            )
        else:
            self._focus_first_section(initial=True)

    async def _select_bestiary(self, _ident: str | None) -> None:
        self.selected_covenant = None
        view = BestiarySheetView(self.saga)
        await self._set_detail(view)
        self._bestiary_view = view
        self._focus_first_section(initial=True)

    async def _select_conflicts(self, _ident: str | None) -> None:
        self.selected_covenant = None
        view = ConflictsSheetView(self.saga)
        await self._set_detail(view)
        self._conflicts_view = view
        self._focus_first_section(initial=True)

    async def _select_creature(self, ident: str | None) -> None:
        creature = self.saga.creature(ident)
        if creature is None:
            return
        self.selected_covenant = None
        self.selected_creature = creature
        view = CreatureSheetView(self.saga, creature)
        await self._set_detail(view)
        self._creature_sheet_view = view
        self._focus_first_section(initial=True)

    async def _select_tribunal(self, ident: str | None) -> None:
        tribunal = self.saga.tribunal(ident)
        if tribunal is None:
            return
        self.selected_covenant = None
        self.selected_tribunal = tribunal
        await self._show_tribunal_detail(tribunal)

    async def _select_book_group(self, ident: str | None) -> None:
        self.selected_covenant = None
        await self._set_detail(
            BookListView(
                self.saga,
                lambda: bk.unassigned_books(self.saga),
                section_id="section-unassigned-books",
                title="Unassigned Books",
            )
        )

    #: The handler for each kind of tree node (Strategy, as a table).
    _NODE_SELECTED: ClassVar[
        dict[NodeKind, Callable[[NavigationActions, str | None], Awaitable[None]]]
    ] = {
        NodeKind.SAGA: _select_saga,
        NodeKind.COVENANT: _select_covenant,
        NodeKind.CHARACTER_GROUP: _select_character_group,
        NodeKind.CHARACTER: _select_character,
        NodeKind.FAMILIAR: _select_familiar,
        NodeKind.LABORATORY_GROUP: _select_laboratory_group,
        NodeKind.LABORATORY: _select_laboratory,
        NodeKind.SAGA_CONTENT: _select_saga_content,
        NodeKind.SEASONS: _select_seasons,
        NodeKind.BOOK_GROUP: _select_book_group,
        NodeKind.REGION: _select_region,
        NodeKind.TRIBUNAL: _select_tribunal,
        NodeKind.NEIGHBOUR_GROUP: _select_region,
        NodeKind.NEIGHBOUR: WorkspaceBase._select_neighbour,
        NodeKind.BESTIARY: _select_bestiary,
        NodeKind.CREATURE: _select_creature,
        NodeKind.CONFLICTS: _select_conflicts,
    }
