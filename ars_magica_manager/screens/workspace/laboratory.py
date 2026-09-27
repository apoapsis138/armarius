"""The Laboratory sheet: Identity, Characteristics, Sanctum,
Specializations and their sources, Features, Rooms, Raw Vis, Equipment &
Stores and Diary."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from textual.screen import ModalScreen

from ... import laboratories as lab_text
from ...markup import escape
from ...models import (
    LAB_SPECIALIZATIONS,
    DiaryEntry,
    LabCharacteristics,
    LabSpecialtyEntry,
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
    ConfirmScreen,
    _diary_entry_dialog,
    _item_dialog,
    _lab_specialty_entry_dialog,
    _named_description_dialog,
    _raw_vis_dialog,
    _sanctum_marked_dialog,
)
from ..widgets import ToggleList
from .base import (
    WorkspaceBase,
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

    def _edit_lab_sanctum(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(marked: bool | None) -> None:
            if marked is not None:
                lab.sanctum_marked = marked
                self._commit("section-lab-sanctum")

        self.app.push_screen(_sanctum_marked_dialog(lab.sanctum_marked), handle_result)

    # -- Laboratory: Specializations --

    def on_toggle_list_toggled(self, event: ToggleList.Toggled) -> None:
        """Space on the Specializations grid: turn the chosen one off or on,
        or say why not."""
        lab = self.selected_laboratory
        if lab is None or event.toggle_list.id != "lab-specializations-list":
            return
        event.stop()
        refusal = lab_text.toggle_specialization(
            lab, LAB_SPECIALIZATIONS[event.data_index]
        )
        if refusal is not None:
            self.notify(refusal, severity="warning")
            return
        self._commit("section-lab-specializations")

    def _add_specialty_entry(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(entry: LabSpecialtyEntry | None) -> None:
            if entry is not None:
                counted = lab_text.counted_specializations(lab)
                lab.specialties.append(entry)
                self._commit_specialties(counted)

        self.app.push_screen(_lab_specialty_entry_dialog(), handle_result)

    def _edit_specialty_entry(self) -> None:
        """Edit the chosen Specialization source; with none chosen, ask which
        one."""
        lab = self.selected_laboratory
        if lab is None:
            return

        def edit(index: int) -> None:
            def handle_result(entry: LabSpecialtyEntry | None) -> None:
                if entry is not None:
                    counted = lab_text.counted_specializations(lab)
                    lab.specialties[index] = entry
                    self._commit_specialties(counted)

            self.app.push_screen(
                _lab_specialty_entry_dialog(lab.specialties[index]), handle_result
            )

        self._chosen_or_pick(
            self._lab_view_selection("selected_specialty_entry"),
            [label for _, label in lab_text.specialty_entry_rows(lab)],
            title="Edit which Specialization source?",
            empty="No Specialization sources to edit.",
            then=edit,
        )

    def _remove_specialty_entry(self) -> None:
        """Delete the chosen Specialization source (after confirming); with
        none chosen, ask which one first."""
        lab = self.selected_laboratory
        if lab is None:
            return

        def confirm(index: int) -> None:
            entry = lab.specialties[index]
            name = " ".join(
                part
                for part in (
                    entry.specialization,
                    f"{entry.points:+d}" if entry.specialization else "",
                    f"({entry.source})" if entry.source else "",
                )
                if part
            )

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    counted = lab_text.counted_specializations(lab)
                    del lab.specialties[index]
                    self._commit_specialties(counted)

            self.app.push_screen(
                ConfirmScreen(f"Delete {escape(name)}?"), handle_confirmed
            )

        self._chosen_or_pick(
            self._lab_view_selection("selected_specialty_entry"),
            [label for _, label in lab_text.specialty_entry_rows(lab)],
            title="Remove a Specialization source",
            empty="No Specialization sources to remove.",
            then=confirm,
        )

    def _commit_specialties(self, previously_counted: set[str]) -> None:
        """Save a change to the Specialization sources: a Specialization it
        newly makes count arrives turned off if it would break a cap."""
        lab = self.selected_laboratory
        if lab is None:
            return
        lab_text.reconcile_dropped(lab, previously_counted)
        self._commit("section-lab-specialties")

    # -- Laboratory: Features (free text until STORY-308) --

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
        """Two-step flow for editing a Feature: pick
        which entry (same picker as Remove), then edit it in a pre-filled
        dialog built by `screen_for(index)`; `apply(index, result)` writes
        the result back before saving and refreshing."""
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

    # -- Laboratory: the selectable lists --

    def _lab_view_selection(self, method: str) -> int | None:
        """The chosen row's index from the lab sheet's `method` (e.g.
        "selected_room"), or None with no lab sheet on show."""
        view = self._laboratory_sheet_view
        return getattr(view, method)() if view is not None else None

    # -- Laboratory: Rooms / Equipment & Stores (name + description lists) --

    def _add_named(self, section: str) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        spec = _NAMED_LISTS[section]
        entries: list[NamedDescription] = getattr(lab, spec.attr)

        def handle_result(entry: NamedDescription | None) -> None:
            if entry is not None:
                entries.append(entry)
                self._commit(section)

        self.app.push_screen(
            _named_description_dialog(f"Add {spec.article}", spec.example),
            handle_result,
        )

    def _edit_named(self, section: str) -> None:
        """Edit the chosen entry; with none chosen, ask which one."""
        lab = self.selected_laboratory
        if lab is None:
            return
        spec = _NAMED_LISTS[section]
        entries: list[NamedDescription] = getattr(lab, spec.attr)

        def edit(index: int) -> None:
            def handle_result(entry: NamedDescription | None) -> None:
                if entry is not None:
                    entries[index] = entry
                    self._commit(section)

            self.app.push_screen(
                _named_description_dialog(
                    f"Edit {spec.article}", spec.example, existing=entries[index]
                ),
                handle_result,
            )

        self._chosen_or_pick(
            self._lab_view_selection(spec.selected),
            [label for _, label in lab_text.named_rows(entries)],
            title=f"Edit which {spec.noun}?",
            empty=f"No {spec.plural} to edit.",
            then=edit,
        )

    def _remove_named(self, section: str) -> None:
        """Delete the chosen entry (after confirming); with none chosen, ask
        which one first."""
        lab = self.selected_laboratory
        if lab is None:
            return
        spec = _NAMED_LISTS[section]
        entries: list[NamedDescription] = getattr(lab, spec.attr)
        self._chosen_or_pick(
            self._lab_view_selection(spec.selected),
            [label for _, label in lab_text.named_rows(entries)],
            title=f"Remove {spec.article}",
            empty=f"No {spec.plural} to remove.",
            then=lambda index: self._confirm_delete(
                entries, index, entries[index].name, section
            ),
        )

    # -- Laboratory: Raw Vis --

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

    def _edit_lab_raw_vis(self) -> None:
        """Edit the chosen Raw Vis entry; with none chosen, ask which one."""
        lab = self.selected_laboratory
        if lab is None:
            return
        arts = sorted(lab.raw_vis)

        def edit(index: int) -> None:
            old_art = arts[index]

            def handle_result(result: tuple[str, int] | None) -> None:
                if result is not None:
                    art, pawns = result
                    replace_raw_vis(lab.raw_vis, old_art, art, pawns)
                    self._commit("section-lab-raw-vis")

            self.app.push_screen(
                _raw_vis_dialog(existing=(old_art, lab.raw_vis[old_art])),
                handle_result,
            )

        self._chosen_or_pick(
            self._lab_view_selection("selected_raw_vis"),
            [label for _, label in lab_text.raw_vis_rows(lab)],
            title="Edit which Raw Vis entry?",
            empty="No Raw Vis to edit.",
            then=edit,
        )

    def _remove_lab_raw_vis(self) -> None:
        """Delete the chosen Raw Vis entry (after confirming); with none
        chosen, ask which one first."""
        lab = self.selected_laboratory
        if lab is None:
            return
        arts = sorted(lab.raw_vis)

        def confirm(index: int) -> None:
            art = arts[index]

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    del lab.raw_vis[art]
                    self._commit("section-lab-raw-vis")

            self.app.push_screen(
                ConfirmScreen(f"Delete {escape(art.title())} vis?"), handle_confirmed
            )

        self._chosen_or_pick(
            self._lab_view_selection("selected_raw_vis"),
            [label for _, label in lab_text.raw_vis_rows(lab)],
            title="Remove a Raw Vis entry",
            empty="No Raw Vis to remove.",
            then=confirm,
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

    def _edit_diary_entry(self) -> None:
        """Edit the chosen Diary entry; with none chosen, ask which one."""
        lab = self.selected_laboratory
        if lab is None:
            return

        def edit(index: int) -> None:
            def handle_result(entry: DiaryEntry | None) -> None:
                if entry is not None:
                    lab.diary[index] = entry
                    self._commit("tab-lab-diary")

            self.app.push_screen(
                _diary_entry_dialog(self.saga.current_year, existing=lab.diary[index]),
                handle_result,
            )

        self._chosen_or_pick(
            self._lab_view_selection("selected_diary_entry"),
            [label for _, label in lab_text.diary_rows(lab.diary)],
            title="Edit which Diary Entry?",
            empty="No Diary entries to edit.",
            then=edit,
        )

    def _remove_diary_entry(self) -> None:
        """Delete the chosen Diary entry (after confirming); with none
        chosen, ask which one first."""
        lab = self.selected_laboratory
        if lab is None:
            return
        self._chosen_or_pick(
            self._lab_view_selection("selected_diary_entry"),
            [label for _, label in lab_text.diary_rows(lab.diary)],
            title="Remove a Diary Entry",
            empty="No Diary entries to remove.",
            then=lambda index: self._confirm_delete(
                lab.diary, index, lab.diary[index].name, "tab-lab-diary"
            ),
        )
