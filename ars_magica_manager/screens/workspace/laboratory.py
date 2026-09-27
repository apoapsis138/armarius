"""The Laboratory sheet: Identity, Characteristics, Specialties, Features,
Rooms, Raw Vis, Items and Diary."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from textual.screen import ModalScreen

from ...markup import escape
from ...models import (
    DiaryEntry,
    LabCharacteristics,
    Laboratory,
    NamedDescription,
    add_raw_vis,
    assign_laboratory_owner,
    replace_raw_vis,
)
from ..fields import (
    FieldsDialog,
)
from ..forms import (
    _lab_characteristics_fields,
    _lab_identity_fields,
)
from ..pickers import (
    RemovalPickerScreen,
)
from ..prompts import (
    _diary_entry_dialog,
    _item_dialog,
    _named_description_dialog,
    _raw_vis_dialog,
)
from .base import (
    WorkspaceBase,
)


def _diary_labels(lab: Laboratory) -> list[str]:
    """How the Diary's edit and remove pickers list its entries (markup)."""
    return [f"{e.year} {e.season} -- {escape(e.name)}" for e in lab.diary]


class LaboratoryActions(WorkspaceBase):
    """WorkspaceScreen's actions for the Laboratory sheet: Identity,
    Characteristics, Specialties, Features, Rooms, Raw Vis, Items and Diary."""

    # -- Laboratory: Identity / Characteristics --

    def _edit_lab_identity(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            lab.name = result["name"]
            lab.location = result["location"]
            lab.build_points = result["build_points"]
            lab.aura_modifier = result["aura_modifier"]
            lab.covenant_id = result["covenant_id"]
            self.selected_covenant = self.saga.covenant(lab.covenant_id)
            assign_laboratory_owner(self.saga, lab, result["owner_id"])
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

    # -- Laboratory: Specialties / Features / Rooms --

    def _add_specialty(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(item: str | None) -> None:
            if item is not None:
                lab.specialties.append(item)
                self._commit("section-lab-specialties")

        self.app.push_screen(
            _item_dialog("Add a Specialty", "Specialty"), handle_result
        )

    def _remove_specialty(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.specialties:
            self.notify("No Specialties to remove.")
            return

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.specialties[index]
                self._commit("section-lab-specialties")

        self.app.push_screen(
            RemovalPickerScreen(
                "Remove a Specialty", [escape(s) for s in lab.specialties]
            ),
            handle_result,
        )

    def _add_feature(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(item: str | None) -> None:
            if item is not None:
                lab.features.append(item)
                self._commit("section-lab-features")

        self.app.push_screen(_item_dialog("Add a Feature", "Feature"), handle_result)

    def _remove_feature(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.features:
            self.notify("No Features to remove.")
            return

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.features[index]
                self._commit("section-lab-features")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Feature", [escape(f) for f in lab.features]),
            handle_result,
        )

    def _add_room(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(room: NamedDescription | None) -> None:
            if room is not None:
                lab.rooms.append(room)
                self._commit("section-lab-rooms")

        self.app.push_screen(
            _named_description_dialog("Add a Room", "e.g. Vault"), handle_result
        )

    def _remove_room(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.rooms:
            self.notify("No Rooms to remove.")
            return

        labels = [escape(room.name) for room in lab.rooms]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.rooms[index]
                self._commit("section-lab-rooms")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Room", labels), handle_result
        )

    # -- Laboratory: Raw Vis / Items --

    def _add_lab_raw_vis(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(result: tuple[str, int] | None) -> None:
            if result is not None:
                art, pawns = result
                add_raw_vis(lab.raw_vis, art, pawns)
                self._commit("section-lab-raw-vis")

        self.app.push_screen(_raw_vis_dialog(), handle_result)

    def _remove_lab_raw_vis(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.raw_vis:
            self.notify("No Raw Vis to remove.")
            return

        arts = sorted(lab.raw_vis)
        labels = [f"{art.title()}: {lab.raw_vis[art]} pawn(s)" for art in arts]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.raw_vis[arts[index]]
                self._commit("section-lab-raw-vis")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Raw Vis entry", labels), handle_result
        )

    def _add_inventory_item(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(item: NamedDescription | None) -> None:
            if item is not None:
                lab.inventory_items.append(item)
                self._commit("section-lab-items")

        self.app.push_screen(
            _named_description_dialog("Add an Item", "e.g. Silver Mirror"),
            handle_result,
        )

    def _remove_inventory_item(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.inventory_items:
            self.notify("No Items to remove.")
            return

        labels = [escape(item.name) for item in lab.inventory_items]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.inventory_items[index]
                self._commit("section-lab-items")

        self.app.push_screen(
            RemovalPickerScreen("Remove an Item", labels), handle_result
        )

    # -- Laboratory: Diary --

    def _add_diary_entry(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(entry: DiaryEntry | None) -> None:
            if entry is not None:
                lab.diary.append(entry)
                self._commit("tab-lab-diary")

        self.app.push_screen(
            _diary_entry_dialog(
                self.saga.current_year, default_season=self.saga.current_season
            ),
            handle_result,
        )

    def _remove_diary_entry(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.diary:
            self.notify("No Diary entries to remove.")
            return

        labels = _diary_labels(lab)

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.diary[index]
                self._commit("tab-lab-diary")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Diary Entry", labels), handle_result
        )

    # -- Laboratory: edit an existing list entry --

    def _edit_lab_entry(
        self,
        *,
        picker_title: str,
        empty_message: str,
        labels: list[str],
        screen_for: Callable[[int], ModalScreen[Any]],
        apply: Callable[[int, Any], None],
        section_id: str,
    ) -> None:
        """Shared two-step flow for editing one entry of a laboratory list:
        pick which entry (same picker as Remove), then edit it in a
        pre-filled dialog built by `screen_for(index)`; `apply(index,
        result)` writes the result back before saving and refreshing."""
        if not labels:
            self.notify(empty_message)
            return

        def handle_index(index: int | None) -> None:
            if index is None:
                return

            def handle_result(result: Any) -> None:
                if result is None:
                    return
                apply(index, result)
                self._commit(section_id)

            self.app.push_screen(screen_for(index), handle_result)

        self.app.push_screen(RemovalPickerScreen(picker_title, labels), handle_index)

    def _edit_specialty(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Specialty?",
            empty_message="No Specialties to edit.",
            labels=[escape(s) for s in lab.specialties],
            screen_for=lambda i: _item_dialog(
                "Edit a Specialty", "Specialty", existing=lab.specialties[i]
            ),
            apply=lab.specialties.__setitem__,
            section_id="section-lab-specialties",
        )

    def _edit_feature(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Feature?",
            empty_message="No Features to edit.",
            labels=[escape(f) for f in lab.features],
            screen_for=lambda i: _item_dialog(
                "Edit a Feature", "Feature", existing=lab.features[i]
            ),
            apply=lab.features.__setitem__,
            section_id="section-lab-features",
        )

    def _edit_room(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Room?",
            empty_message="No Rooms to edit.",
            labels=[escape(room.name) for room in lab.rooms],
            screen_for=lambda i: _named_description_dialog(
                "Edit a Room", "e.g. Vault", existing=lab.rooms[i]
            ),
            apply=lab.rooms.__setitem__,
            section_id="section-lab-rooms",
        )

    def _edit_inventory_item(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Item?",
            empty_message="No Items to edit.",
            labels=[escape(item.name) for item in lab.inventory_items],
            screen_for=lambda i: _named_description_dialog(
                "Edit an Item", "e.g. Silver Mirror", existing=lab.inventory_items[i]
            ),
            apply=lab.inventory_items.__setitem__,
            section_id="section-lab-items",
        )

    def _edit_lab_raw_vis(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        arts = sorted(lab.raw_vis)

        def apply(index: int, result: tuple[str, int]) -> None:
            art, pawns = result
            replace_raw_vis(lab.raw_vis, arts[index], art, pawns)

        self._edit_lab_entry(
            picker_title="Edit which Raw Vis entry?",
            empty_message="No Raw Vis to edit.",
            labels=[f"{art.title()}: {lab.raw_vis[art]} pawn(s)" for art in arts],
            screen_for=lambda i: _raw_vis_dialog(
                existing=(arts[i], lab.raw_vis[arts[i]])
            ),
            apply=apply,
            section_id="section-lab-raw-vis",
        )

    def _edit_diary_entry(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Diary Entry?",
            empty_message="No Diary entries to edit.",
            labels=_diary_labels(lab),
            screen_for=lambda i: _diary_entry_dialog(
                self.saga.current_year, existing=lab.diary[i]
            ),
            apply=lab.diary.__setitem__,
            section_id="tab-lab-diary",
        )
