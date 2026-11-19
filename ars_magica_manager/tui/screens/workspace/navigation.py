"""WorkspaceScreen's navigation: what selecting each kind of node in the saga's
tree shows."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import ClassVar

from textual.widgets import (
    Tree,
)

from .... import (
    neighbours,
    stores,
    viewing,
)
from ....actions import (
    NodeKind,
)
from ....where import RECORD_KINDS, Where
from ..sheets import (
    BestiarySheetView,
    ConflictsSheetView,
    CreatureSheetView,
    RegionSheetView,
    SagaContentSheetView,
    SeasonsSheetView,
)
from ..sheets.stores import StoreSheetView
from ..widgets import (
    SelectableList,
    SheetSection,
)
from .base import WorkspaceBase

#: The tree nodes whose id is the page's: a record's, or the covenant a
#: list of characters or laboratories belongs to.
_HAS_ID = frozenset(
    {*RECORD_KINDS, NodeKind.CHARACTER_GROUP, NodeKind.LABORATORY_GROUP}
)


class NavigationActions(WorkspaceBase):
    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        data = event.node.data
        if data is None:
            return

        kind: NodeKind = data[0]
        ident = data[1] if len(data) > 1 else None
        # A record's id, or the covenant whose lists these are; the
        # Region's groups are by key, not the page's record.
        self.where = Where(kind, ident if kind in _HAS_ID else None)
        self.detail_settled = False  # a new view is on its way
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
        self._store_view = None

        handler = self._NODE_SELECTED.get(kind)
        if handler is not None:
            await handler(self, ident)

        if self._current_sheet_view() is None:
            # Enter on a node moves into what it shows: a list view's list.
            for rows in self._detail_pane().query(SelectableList):
                self._focus_stop(rows)  # the view's first focus (settling)
                break
        spot, self._spot_after_open = self._spot_after_open, None
        if spot is not None:
            self.open_spot(*spot)
        self.refresh_bindings()
        # Settle even when the node swapped no view in (_set_detail does too).
        self.call_later(self._settle_unless_tabs_pending, self._detail_generation)

    # What selecting each kind of tree node does: set the selection and
    # show its detail. `ident` is the node's record or covenant id, if any.

    async def _select_saga(self, ident: str | None) -> None:
        await self._show_saga_detail()

    async def _select_covenant(self, ident: str | None) -> None:
        covenant = next(c for c in self.saga.covenants if c.id == ident)
        await self._show_covenant_detail(covenant)

    async def _select_character_group(self, ident: str | None) -> None:
        covenant = self.saga.covenant(ident)
        await self._show_placeholder_detail(
            f"Characters in {covenant.name}" if covenant else "Unassigned Characters",
            "Select a character from the tree, or press 'n' to add one."
            if covenant
            else "These characters aren't assigned to a covenant. Select one "
            "from the tree, or press 'n' to add one.",
        )

    async def _select_character(self, ident: str | None) -> None:
        character = next(c for c in self.saga.characters if c.id == ident)
        await self._show_character_detail(character)

    async def _select_familiar(self, ident: str | None) -> None:
        familiar = next(f for f in self.saga.familiars if f.id == ident)
        await self._show_familiar_detail(familiar)

    async def _select_laboratory_group(self, ident: str | None) -> None:
        covenant = self.saga.covenant(ident)
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
        await self._show_laboratory_detail(lab)

    async def _select_saga_content(self, ident: str | None) -> None:
        view = SagaContentSheetView(
            self.saga, players=viewing.reads(part="tab-content-players")
        )
        await self._set_detail(view)
        self._saga_content_view = view
        self._focus_first_section(initial=True)

    async def _select_seasons(self, ident: str | None) -> None:
        view = SeasonsSheetView(self.saga)
        await self._set_detail(view)
        self._seasons_view = view
        self._focus_first_section(initial=True)

    async def _select_region(self, ident: str | None) -> None:
        """The Region, or (`ident`) one of its groups of neighbours, whose
        list takes focus."""
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
        view = BestiarySheetView(self.saga)
        await self._set_detail(view)
        self._bestiary_view = view
        self._focus_first_section(initial=True)

    async def _select_conflicts(self, _ident: str | None) -> None:
        view = ConflictsSheetView(self.saga)
        await self._set_detail(view)
        self._conflicts_view = view
        self._focus_first_section(initial=True)

    async def _select_creature(self, ident: str | None) -> None:
        creature = self.saga.creature(ident)
        if creature is None:
            return
        view = CreatureSheetView(self.saga, creature)
        await self._set_detail(view)
        self._creature_sheet_view = view
        self._focus_first_section(initial=True)

    async def _select_tribunal(self, ident: str | None) -> None:
        tribunal = self.saga.tribunal(ident)
        if tribunal is None:
            return
        await self._show_tribunal_detail(tribunal)

    async def _select_store(self, _ident: str | None) -> None:
        """The Armarium or the Custodia Mirabilium (the node's kind is the
        store's key)."""
        view = StoreSheetView(self.saga, stores.STORES[self.selected_kind.value])
        await self._set_detail(view)
        self._store_view = view
        self._focus_first_section(initial=True)

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
        NodeKind.ARMARIUM: _select_store,
        NodeKind.CUSTODIA: _select_store,
        NodeKind.REGION: _select_region,
        NodeKind.TRIBUNAL: _select_tribunal,
        NodeKind.NEIGHBOUR_GROUP: _select_region,
        NodeKind.NEIGHBOUR: WorkspaceBase._select_neighbour,
        NodeKind.BESTIARY: _select_bestiary,
        NodeKind.CREATURE: _select_creature,
        NodeKind.CONFLICTS: _select_conflicts,
    }
