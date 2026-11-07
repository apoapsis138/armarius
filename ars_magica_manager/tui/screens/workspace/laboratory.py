"""The Laboratory sheet: Identity, Characteristics, Sanctum,
Specializations and their sources, Features, Rooms, Raw Vis, Equipment &
Stores and Diary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .... import laboratories as lab_text
from .... import seasons
from ....forms import lab_plan as lab_plan_forms
from ....forms import laboratory as lf
from ....models import (
    LAB_SPECIALIZATIONS,
    Character,
    LabCharacteristics,
    Laboratory,
    SeasonPlan,
)
from ....rules import lab_seasons
from ..fields import (
    FieldsDialog,
)
from ..forms import (
    _lab_characteristics_fields,
    _lab_identity_fields,
)
from ..invent_spell import InventSpellScreen
from ..steps import run_steps
from ..widgets import ToggleList
from .base import (
    WorkspaceBase,
    _SectionOps,
)


@dataclass(frozen=True)
class _NamedList:
    """One of the lab's name + description lists (Rooms, Equipment &
    Stores), for the shared add/edit/remove."""

    attr: str  # the Laboratory list: "rooms" or "inventory_items"
    noun: str  # "Room"
    plural: str  # "Rooms"
    article: str  # "a Room"
    example: str  # the Name field's placeholder
    selected: str  # the LaboratorySheetView method giving the chosen row


#: Per sheet section, its name + description list.
_NAMED_LISTS = {
    "section-lab-rooms": _NamedList(
        "rooms", "Room", "Rooms", "a Room", "e.g. Vault", "selected_room"
    ),
    "section-lab-items": _NamedList(
        "inventory_items",
        "Equipment & Stores entry",
        "Equipment & Stores entries",
        "an Equipment & Stores entry",
        "e.g. Silver Mirror",
        "selected_item",
    ),
}


class LaboratoryActions(WorkspaceBase):
    """WorkspaceScreen's actions for the Laboratory sheet: Identity,
    Characteristics, Sanctum, Specializations and their sources, Features,
    Rooms, Raw Vis, Equipment & Stores and Diary. The selectable lists
    (Specialization sources, Rooms, Raw Vis, Equipment & Stores, Diary) act
    on the chosen row, falling back to a picker when none is chosen; every
    delete confirms."""

    # -- Laboratory: Identity / Characteristics --

    def _edit_lab_identity(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            lf.apply_identity(self.saga, lab, result)
            self.selected_covenant = self.saga.covenant(lab.covenant_id)
            self._commit("section-lab-identity", tree=True)

        self.app.push_screen(
            FieldsDialog(
                "Edit Laboratory Identity", _lab_identity_fields(self.saga, lab)
            ),
            handle_result,
        )

    def _edit_lab_characteristics(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                lab.characteristics = LabCharacteristics(**result)
                self._commit("section-lab-characteristics")

        self.app.push_screen(
            FieldsDialog(
                "Edit Laboratory Characteristics (manual value)",
                _lab_characteristics_fields(lab.characteristics),
            ),
            handle_result,
        )

    # -- Laboratory: Specializations --

    def on_toggle_list_toggled(self, event: ToggleList.Toggled) -> None:
        """Space on the Specializations grid: turn the chosen one off or on,
        or say why not."""
        lab = self.selected_laboratory
        if lab is None or event.toggle_list.id != "lab-specializations-list":
            return
        event.stop()
        refusal = lab_text.toggle_specialization(
            self.saga, lab, LAB_SPECIALIZATIONS[event.data_index]
        )
        if refusal is not None:
            self.notify(refusal, severity="warning")
            return
        self._commit("section-lab-specializations")

    # -- Laboratory: the selectable lists --

    def _lab_view_selection(self, method: str) -> int | None:
        """The chosen row's index from the lab sheet's `method` (e.g.
        "selected_room"), or None with no lab sheet on show."""
        view = self._laboratory_sheet_view
        return getattr(view, method)() if view is not None else None

    # -- Laboratory: Planning --

    def _lab_owner_for_planning(self) -> tuple[Laboratory, Character] | None:
        lab = self.selected_laboratory
        if lab is None:
            return None
        owner = self.saga.character(lab.owner_id)
        if owner is None or owner.type != "magus":
            self.notify(lab_plan_forms.NO_OWNER)
            return None
        return lab, owner

    def _chosen_lab_season(self) -> tuple[str, int]:
        """The first season of the chosen row (the current season if none)."""
        lab = self.selected_laboratory
        index = self._lab_view_selection("selected_lab_season") or 0
        rows = seasons.lab_queue(self.saga, lab) if lab is not None else []
        if not rows:
            return self.saga.current_season, self.saga.current_year
        row = rows[min(index, len(rows) - 1)]
        return row.season, row.year

    def _plan_lab_season(self, *, new: bool = False) -> None:
        """Plan lab work for the chosen season (the current one if none) on
        the Invent Spell screen; `new` starts from a blank design."""
        found = self._lab_owner_for_planning()
        if found is None:
            return
        lab, owner = found
        season, year = self._chosen_lab_season()
        existing = None if new else seasons.plan_for(self.saga, owner, season, year)

        def handle_result(plan: SeasonPlan | None) -> None:
            if plan is None:
                return
            added = seasons.plan_lab_work(self.saga, plan)
            self._commit("tab-lab-planning")
            if added:
                last = added[-1]
                self.notify(f"Planned through {last.season} {last.year} to finish it.")

        self.app.push_screen(
            InventSpellScreen(
                self.saga,
                owner,
                lab,
                season,
                year,
                existing,
                activity=lab_seasons.INVENT if new else None,
            ),
            handle_result,
        )

    def _new_lab_design(self) -> None:
        """Plan inventing a new spell from a blank design."""
        self._plan_lab_season(new=True)

    def _clear_lab_season(self) -> None:
        """Clear the chosen season's plan (after confirming)."""
        lab = self.selected_laboratory
        if lab is None or self._lab_owner_for_planning() is None:
            return
        index = self._lab_view_selection("selected_lab_season")
        run_steps(
            self.app,
            lab_plan_forms.clear_lab_season(self.saga, lab, index),
            lambda _end: self._commit("tab-lab-planning"),
            notify=lambda _title, why: self.notify(why),
        )

    def _laboratory_section_ops(self) -> dict[str, _SectionOps]:
        """a / d / e on the laboratory sheet (see
        WorkspaceScreen._section_ops)."""
        ops: dict[str, _SectionOps] = {
            "section-lab-identity": _SectionOps(edit=self._edit_lab_identity),
            "section-lab-characteristics": _SectionOps(
                edit=self._edit_lab_characteristics
            ),
            "section-lab-specialties": self._core_ops_of("section-lab-specialties"),
            "section-lab-features": self._core_ops_of("section-lab-features"),
            "section-lab-raw-vis": self._core_ops_of("section-lab-raw-vis"),
            "tab-lab-planning": _SectionOps(
                self._new_lab_design, self._clear_lab_season, self._plan_lab_season
            ),
            "tab-lab-diary": self._core_ops_of("tab-lab-diary"),
            "section-lab-connections": self._core_ops_of("section-lab-connections"),
        }
        for section in ("section-lab-rooms", "section-lab-items"):
            ops[section] = self._core_ops_of(section)
        return ops
