"""The Laboratory sheet: Identity, Characteristics, Sanctum,
Specializations and their sources, Features, Rooms, Raw Vis, Equipment &
Stores and Diary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .... import laboratories as lab_text
from .... import laboratory_forms as lf
from .... import seasons
from ....markup import escape
from ....models import (
    LAB_SPECIALIZATIONS,
    ArcaneConnection,
    Character,
    DiaryEntry,
    LabCharacteristics,
    LabFeature,
    Laboratory,
    LabSpecialtyEntry,
    NamedDescription,
    SeasonPlan,
    add_raw_vis,
    replace_raw_vis,
)
from ....rules import lab_seasons
from ..fields import (
    FieldsDialog,
)
from ..forms import (
    NEW_FEATURE_VIRTUE,
    _lab_characteristics_fields,
    _lab_feature_dialog,
    _lab_feature_type_dialog,
    _lab_identity_fields,
)
from ..invent_spell import InventSpellScreen
from ..prompts import (
    ConfirmScreen,
    _arcane_connection_dialog,
    _diary_entry_dialog,
    _lab_specialty_entry_dialog,
    _named_description_dialog,
    _raw_vis_dialog,
)
from ..sheets import LAB_FEATURE_SECTIONS
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
        """Edit the chosen Specialization source."""
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
            empty="No Specialization sources to edit.",
            then=edit,
        )

    def _remove_specialty_entry(self) -> None:
        """Delete the chosen Specialization source (after confirming)."""
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

    # -- Laboratory: Features --

    def _add_feature(self) -> None:
        lab = self.selected_laboratory
        if lab is not None:
            self._feature_flow(lab, None)

    def _edit_feature(self) -> None:
        """Edit the chosen Feature (type and Virtue, then name, points and
        Focus)."""
        lab = self.selected_laboratory
        if lab is None:
            return
        self._chosen_or_pick(
            self._lab_view_selection("selected_feature"),
            [escape(f.name) for f in lab.features],
            empty="No Features to edit.",
            then=lambda index: self._feature_flow(lab, lab.features[index]),
        )

    def _feature_flow(self, lab: Laboratory, feature: LabFeature | None) -> None:
        """Add (`feature` None) or edit a Feature in two steps: which Feature
        and the Virtue it's built on -- confirming first if that means adding
        a new Feature Virtue -- then its name, points and Focus. Nothing
        changes until the second step is saved."""

        def handle_type(result: tuple[str | None, str] | None) -> None:
            if result is None:
                return
            feature_id, virtue_choice = result
            if not virtue_choice.startswith(NEW_FEATURE_VIRTUE):
                self._feature_details(lab, feature, feature_id, virtue_choice)
                return
            vf_id = virtue_choice.removeprefix(NEW_FEATURE_VIRTUE)

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    self._feature_details(lab, feature, feature_id, virtue_choice)

            self.app.push_screen(
                ConfirmScreen(lf.new_feature_virtue_question(lab, vf_id)),
                handle_confirmed,
            )

        self.app.push_screen(_lab_feature_type_dialog(lab, feature), handle_type)

    def _feature_details(
        self,
        lab: Laboratory,
        feature: LabFeature | None,
        feature_id: str | None,
        virtue_choice: str,
    ) -> None:
        """The second step of _feature_flow: the Feature's name, points and
        Focus, for a `feature_id` Feature (None: Custom) on the Virtue
        `virtue_choice` (an instance id, or NEW_FEATURE_VIRTUE + a catalog
        id to add one with it); saving adds or updates the Feature."""
        if virtue_choice.startswith(NEW_FEATURE_VIRTUE):
            virtue_vf_id = virtue_choice.removeprefix(NEW_FEATURE_VIRTUE)
        else:
            virtue_vf_id = next(
                vf.vf_id for vf in lab.virtues_flaws if vf.id == virtue_choice
            )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            lf.save_feature(lab, feature, feature_id, virtue_choice, values)
            self._commit(*LAB_FEATURE_SECTIONS)

        self.app.push_screen(
            _lab_feature_dialog(lab, feature_id, virtue_vf_id, feature),
            handle_result,
        )

    def _remove_feature(self) -> None:
        """Delete the chosen Feature (after confirming; its Feature Virtue
        stays, free for another)."""
        lab = self.selected_laboratory
        if lab is None:
            return

        def confirm(index: int) -> None:
            feature = lab.features[index]
            virtue = lab_text.feature_virtue(lab, feature)
            keeps = (
                f" Its {lab_text.tier_word(virtue.vf_id)} Feature Virtue stays, "
                "free for another Feature."
                if virtue
                else ""
            )

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    counted = lab_text.counted_specializations(lab)
                    del lab.features[index]
                    lab_text.reconcile_dropped(lab, counted)
                    self._commit(*LAB_FEATURE_SECTIONS)

            self.app.push_screen(
                ConfirmScreen(f"Delete {escape(feature.name)}?{keeps}"),
                handle_confirmed,
            )

        self._chosen_or_pick(
            self._lab_view_selection("selected_feature"),
            [escape(f.name) for f in lab.features],
            empty="No Features to remove.",
            then=confirm,
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
        """Edit the chosen entry."""
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
            empty=f"No {spec.plural} to edit.",
            then=edit,
        )

    def _remove_named(self, section: str) -> None:
        """Delete the chosen entry (after confirming)."""
        lab = self.selected_laboratory
        if lab is None:
            return
        spec = _NAMED_LISTS[section]
        entries: list[NamedDescription] = getattr(lab, spec.attr)
        self._chosen_or_pick(
            self._lab_view_selection(spec.selected),
            [label for _, label in lab_text.named_rows(entries)],
            empty=f"No {spec.plural} to remove.",
            then=lambda index: self._confirm_delete(
                entries, index, entries[index].name, section
            ),
        )

    # -- Laboratory: Arcane Connections --

    def _add_connection(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(connection: ArcaneConnection | None) -> None:
            if connection is not None:
                lab.arcane_connections.append(connection)
                self._commit("section-lab-connections")

        self.app.push_screen(
            _arcane_connection_dialog("Add an Arcane Connection"), handle_result
        )

    def _edit_connection(self) -> None:
        """Edit the chosen Arcane Connection."""
        lab = self.selected_laboratory
        if lab is None:
            return

        def edit(index: int) -> None:
            def handle_result(connection: ArcaneConnection | None) -> None:
                if connection is not None:
                    lab.arcane_connections[index] = connection
                    self._commit("section-lab-connections")

            self.app.push_screen(
                _arcane_connection_dialog(
                    "Edit an Arcane Connection", lab.arcane_connections[index]
                ),
                handle_result,
            )

        self._chosen_or_pick(
            self._lab_view_selection("selected_connection"),
            [c.to for c in lab.arcane_connections],
            empty="No Arcane Connections to edit.",
            then=edit,
        )

    def _remove_connection(self) -> None:
        """Delete the chosen Arcane Connection (after confirming)."""
        lab = self.selected_laboratory
        if lab is None:
            return
        entries = lab.arcane_connections
        self._chosen_or_pick(
            self._lab_view_selection("selected_connection"),
            [c.to for c in entries],
            empty="No Arcane Connections to remove.",
            then=lambda index: self._confirm_delete(
                entries,
                index,
                f"the Arcane Connection to {entries[index].to}",
                "section-lab-connections",
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
        """Edit the chosen Raw Vis entry."""
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
            empty="No Raw Vis to edit.",
            then=edit,
        )

    def _remove_lab_raw_vis(self) -> None:
        """Delete the chosen Raw Vis entry (after confirming)."""
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
            empty="No Raw Vis to remove.",
            then=confirm,
        )

    # -- Laboratory: Planning --

    def _lab_owner_for_planning(self) -> tuple[Laboratory, Character] | None:
        lab = self.selected_laboratory
        if lab is None:
            return None
        owner = self.saga.character(lab.owner_id)
        if owner is None or owner.type != "magus":
            self.notify("Give the laboratory a magus as its owner to plan lab work.")
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
        found = self._lab_owner_for_planning()
        if found is None:
            return
        _, owner = found
        season, year = self._chosen_lab_season()
        plan = seasons.plan_for(self.saga, owner, season, year)
        if plan is None:
            self.notify(f"Nothing is planned for {season} {year}.")
            return

        removed = seasons.scheduled_with(self.saga, plan)

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                for each in removed:
                    self.saga.season_plans.remove(each)
                self._commit("tab-lab-planning")

        span = (
            f"{season} {year}"
            if len(removed) == 1
            else f"{season} {year} - {removed[-1].season} {removed[-1].year}"
        )
        self.app.push_screen(
            ConfirmScreen(
                f"Clear {escape(owner.name)}'s plan for {span} "
                f"({escape(seasons.plan_summary(self.saga, owner, plan))})?"
            ),
            handle_confirmed,
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
        """Edit the chosen Diary entry."""
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
            empty="No Diary entries to edit.",
            then=edit,
        )

    def _remove_diary_entry(self) -> None:
        """Delete the chosen Diary entry (after confirming)."""
        lab = self.selected_laboratory
        if lab is None:
            return
        self._chosen_or_pick(
            self._lab_view_selection("selected_diary_entry"),
            [label for _, label in lab_text.diary_rows(lab.diary)],
            empty="No Diary entries to remove.",
            then=lambda index: self._confirm_delete(
                lab.diary, index, lab.diary[index].name, "tab-lab-diary"
            ),
        )
