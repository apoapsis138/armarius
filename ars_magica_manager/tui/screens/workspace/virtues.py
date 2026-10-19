"""WorkspaceScreen's Virtues and Flaws actions, shared by the character,
familiar and laboratory sheets: adding one, and deleting one with what it
changed undone."""

from __future__ import annotations

from functools import partial

from .... import (
    catalog,
    sourcebooks,
    storage,
)
from .... import laboratories as lab_rules
from ....actions import (
    NodeKind,
)
from ....markup import escape
from ....models import (
    FOCUS_FLAWS,
    Character,
    Familiar,
    Laboratory,
    VirtueFlawInstance,
    link_unlinked_features,
    new_instance_id,
)
from ....rules import creation_characteristics as cch
from ..pickers import (
    LabVirtueFlawPickerScreen,
    VirtueFlawPickerScreen,
)
from ..prompts import (
    ConfirmScreen,
)
from ..sheets import (
    LAB_FEATURE_SECTIONS,
    LAB_VF_SECTIONS,
)
from .base import (
    WorkspaceBase,
    _SectionOps,
)


class VirtueFlawActions(WorkspaceBase):
    # -- shared Character/Laboratory/Familiar Virtue & Flaw actions --

    def action_add_virtue_flaw(self) -> None:
        target = self._virtue_flaw_target()
        if target is None:
            return
        # Opened on the side of the section it was launched from.
        flaws = self._active_section() in ("section-vf-flaws", "section-fam-vf-flaws")
        self._add_virtue_flaw_to(target, "Flaw" if flaws else "Virtue")

    def _add_virtue_flaw_to(
        self, target: Character | Laboratory | Familiar, side: str = "Virtue"
    ) -> None:
        """Pick a Virtue or Flaw (opened on `side`) and add it to `target`
        (also the Creation Worksheet's Virtues and Flaws step)."""
        is_lab = isinstance(target, Laboratory)
        is_familiar = isinstance(target, Familiar)

        def handle_result(instance: VirtueFlawInstance | None) -> None:
            if instance is not None:
                target.virtues_flaws.append(instance)
                if isinstance(target, Character):
                    cch.apply_virtue(self.saga, target, instance)
                if isinstance(target, Laboratory):
                    # A Feature waiting for a Virtue gets a new Feature Virtue.
                    instance.id = new_instance_id()
                    link_unlinked_features(target)
                storage.save_saga(self.saga)
                if is_lab:
                    for section in LAB_FEATURE_SECTIONS:
                        self._refresh_laboratory_section(section)
                elif is_familiar:
                    self._refresh_familiar_section("section-fam-vf-virtues")
                else:
                    self._refresh_character_section("section-vf-virtues")
                    self._refresh_character_section("section-char-characteristics")

        books = sourcebooks.saga_books(self.saga)
        if isinstance(target, Laboratory):
            existing_ids = {vf.vf_id for vf in target.virtues_flaws}
            self.app.push_screen(
                LabVirtueFlawPickerScreen(
                    existing_ids, books=books, saga=self.saga, lab=target
                ),
                handle_result,
            )
            return
        chooser = (
            catalog.VirtueFlawChooser.for_familiar(target, books)
            if isinstance(target, Familiar)
            else catalog.VirtueFlawChooser.for_character(target, books)
        )
        self.app.push_screen(
            VirtueFlawPickerScreen(
                target.virtues_flaws,
                side=side,
                chooser=chooser,
                own_abilities=[a.name for a in target.abilities],
                refusal=(
                    partial(cch.virtue_refusal, self.saga, target)
                    if isinstance(target, Character)
                    else None
                ),
            ),
            handle_result,
        )

    def action_remove_virtue_flaw(self) -> None:
        """Delete a Virtue/Flaw of the character, laboratory or familiar on
        show, after confirming: the row chosen in its Virtues or Flaws
        list."""
        target = self._virtue_flaw_target()
        if target is None:
            return
        self._remove_virtue_flaw_from(target, self._selected_virtue_flaw(target))

    def _remove_virtue_flaw_from(
        self, target: Character | Laboratory | Familiar, selected: int | None = None
    ) -> None:
        """Delete `target`'s Virtue/Flaw at `selected` after confirming."""
        if not target.virtues_flaws:
            self.notify("No Virtues/Flaws to remove.")
            return
        vf_catalog = (
            catalog.load_lab_virtue_flaw_catalog_by_id()
            if isinstance(target, Laboratory)
            else catalog.load_virtue_flaw_catalog_by_id()
        )
        if isinstance(target, Laboratory):
            section = LAB_VF_SECTIONS[0]
        elif isinstance(target, Familiar):
            section = "section-fam-vf-virtues"
        else:
            section = "section-vf-virtues"

        def confirm(index: int) -> None:
            name = catalog.describe_virtue_flaw(target.virtues_flaws[index], vf_catalog)
            if isinstance(target, Laboratory):
                self._confirm_delete_lab_virtue_flaw(target, index, name)
                return
            if isinstance(target, Character):
                instance = target.virtues_flaws[index]
                change = cch.removal_change(self.saga, target, instance)
                if change is not None:
                    self._confirm_delete_stepped(target, index, name, change)
                    return
            self._confirm_delete(target.virtues_flaws, index, name, section)

        self._chosen_or_pick(
            selected,
            [vf.vf_id for vf in target.virtues_flaws],
            empty="No Virtues/Flaws to remove.",
            then=confirm,
        )

    def _confirm_delete_stepped(
        self,
        character: Character,
        index: int,
        name: str,
        change: tuple[str, int, int],
    ) -> None:
        """Delete a Great or Poor (Characteristic) after confirming,
        moving its Characteristic back the point it added."""
        characteristic, before, after = change
        message = (
            f"Delete {escape(name)}? {characteristic} goes from {before:+d} "
            f"to {after:+d}."
        )

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                cch.unapply_virtue(self.saga, character, character.virtues_flaws[index])
                del character.virtues_flaws[index]
                self._commit("section-vf-virtues", "section-char-characteristics")

        self.app.push_screen(ConfirmScreen(message), handle_confirmed)

    def _confirm_delete_lab_virtue_flaw(
        self, lab: Laboratory, index: int, name: str
    ) -> None:
        """Delete a lab Virtue/Flaw after confirming, saying what goes with
        it: the Feature built on a Feature Virtue, or the Focus (and its
        points) of a Focus Flaw."""
        instance = lab.virtues_flaws[index]
        feature = lab_rules.feature_on(lab, instance)
        focus = lab_rules.focus_feature(lab)
        message = f"Delete {escape(name)}?"
        if feature is not None:
            message += f" Its Feature, {escape(feature.name)}, goes too."
        elif instance.vf_id in FOCUS_FLAWS and focus is not None:
            message += (
                f" {escape(focus.name)} stops being the Focus and loses its "
                "Focus points."
            )

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                counted = lab_rules.counted_specializations(lab)
                del lab.virtues_flaws[index]
                lab_rules.prune_features(lab)
                lab_rules.reconcile_dropped(lab, counted)
                self._commit(*LAB_FEATURE_SECTIONS)

        self.app.push_screen(ConfirmScreen(message), handle_confirmed)

    def _selected_virtue_flaw(
        self, target: Character | Laboratory | Familiar
    ) -> int | None:
        """The row chosen in the target's Virtues or Flaws list, if any."""
        if isinstance(target, Character) and self._character_sheet_view is not None:
            return self._character_sheet_view.selected_virtue_flaw()
        if isinstance(target, Laboratory) and self._laboratory_sheet_view is not None:
            return self._laboratory_sheet_view.selected_virtue_flaw()
        if isinstance(target, Familiar) and self._familiar_sheet_view is not None:
            return self._familiar_sheet_view.selected_virtue_flaw()
        return None

    def _virtue_flaw_target(self) -> Character | Laboratory | Familiar | None:
        if (
            self.selected_kind == NodeKind.LABORATORY
            and self._active_section() in LAB_VF_SECTIONS
        ):
            return self.selected_laboratory
        if self.selected_kind == NodeKind.CHARACTER and self._active_section() in (
            "section-vf-virtues",
            "section-vf-flaws",
        ):
            return self.selected_character
        if self.selected_kind == NodeKind.FAMILIAR and self._active_section() in (
            "section-fam-vf-virtues",
            "section-fam-vf-flaws",
        ):
            return self.selected_familiar
        return None

    def _virtue_flaw_section_ops(self) -> dict[str, _SectionOps]:
        """a / d on the Virtues and Flaws lists (character, laboratory,
        familiar), like any other list. They can't be edited, only added and
        deleted (see WorkspaceScreen._section_ops)."""
        return {
            section: _SectionOps(
                self.action_add_virtue_flaw, self.action_remove_virtue_flaw
            )
            for section in (
                "section-vf-virtues",
                "section-vf-flaws",
                "section-fam-vf-virtues",
                "section-fam-vf-flaws",
                *LAB_VF_SECTIONS,
            )
        }
