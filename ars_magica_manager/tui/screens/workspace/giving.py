"""WorkspaceScreen's Give: More's Give hands the chosen row of a Raw Vis,
books, Enchanted Devices or gear list to another record of the saga, and
Give Silver gives from a character's purse (on Personal Gear) or a
covenant's Wealth. The steps are the core's (giving.give), as on the
desktop."""

from __future__ import annotations

from typing import Any

from .... import enchanted_devices as ed
from .... import giving, vis
from ....actions import NodeKind, silver_purse
from ....possessions import entries_for_kind
from ....sections import GIVE_SECTIONS
from ..sheets.lists import BookListView
from .base import _ScreenFacts
from .creation import CreationActions


class GivingActions(CreationActions):
    """WorkspaceScreen's Give and Give Silver."""

    def _shown_holder(self) -> giving.Holder | None:
        """The character, laboratory or covenant whose sheet is on show."""
        return {
            NodeKind.CHARACTER: self.selected_character,
            NodeKind.LABORATORY: self.selected_laboratory,
            NodeKind.COVENANT: self.selected_covenant,
        }.get(self.selected_kind or NodeKind.SAGA)

    def _to_give(self) -> giving.Gift | None:
        section = self._active_section()
        kind = GIVE_SECTIONS.get(section or "")
        store = self._store_view
        if kind is not None and store is not None and section == store.store.section:
            # A store's row, held by anyone or by nobody.
            thing = store.chosen()
            return giving.gift(self.saga, kind, None, thing) if thing else None
        shown = self._shown_holder()
        if section is None or kind is None or shown is None:
            return None
        thing = self._chosen_thing(section, kind, shown)
        if thing is None:
            return None
        return giving.gift(self.saga, kind, shown, thing)

    def _chosen_thing(self, section: str, kind: str, shown: giving.Holder) -> Any:
        """The chosen row's thing in `section`, a list of `kind`, or None."""
        if kind == giving.BOOK:
            views = [
                v
                for v in self._detail_pane().query(BookListView)
                if v.section_id == section
            ]
            return views[0].selected_book() if views else None
        view = self._current_sheet_view()
        if view is None:
            return None
        if kind == giving.DEVICE:
            row = view.selected_device_row(section)
            targets = ed.device_targets(self.saga, giving.kind_of(shown), shown.id)
            return targets[row][0] if row is not None and row < len(targets) else None
        if kind == giving.VIS:
            return self._chosen_vis(section, shown)
        return self._chosen_gear(section, shown)

    def _chosen_vis(self, section: str, shown: giving.Holder) -> vis.Held | None:
        held = vis.held(shown)
        row: int | None = None
        if section == "section-pos-vis_store":
            if self._covenant_sheet_view is not None:
                row = self._covenant_sheet_view.selected_possession("vis_store")
        elif section == "section-lab-raw-vis":
            if self._laboratory_sheet_view is not None:
                row = self._laboratory_sheet_view.selected_raw_vis()
        elif self._character_sheet_view is not None:
            row = self._character_sheet_view.selected_raw_vis(section)
        return held[row] if row is not None and row < len(held) else None

    def _chosen_gear(self, section: str, shown: giving.Holder) -> Any:
        if section == "section-inventory":
            view = self._character_sheet_view
            row = view.selected_inventory_item() if view is not None else None
            gear = giving.gear(shown)
            return gear[row] if row is not None and row < len(gear) else None
        covenant = self.selected_covenant
        if self._covenant_sheet_view is None or covenant is None:
            return None
        kind = section.removeprefix("section-pos-")
        row = self._covenant_sheet_view.selected_possession(kind)
        entries = entries_for_kind(self.saga, covenant, kind)
        return entries[row].record if row is not None and row < len(entries) else None

    def action_give(self) -> None:
        """Give the chosen row's thing to another record of the saga."""
        found = self._to_give()
        if found is not None:
            self._run_steps(
                giving.give_gift(self.saga, found), then=self.refresh_bindings
            )

    def action_give_silver(self) -> None:
        """Give pounds of silver from the purse on show."""
        purse = silver_purse(_ScreenFacts(self))
        if purse is not None:
            self._run_steps(
                giving.give(self.saga, giving.SILVER, purse),
                then=self.refresh_bindings,
            )
