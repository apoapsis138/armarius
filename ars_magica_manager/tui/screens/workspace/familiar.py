"""The Familiar sheet: Info, Binding & Cords, Characteristics, Health, Natural
Weapons, Abilities, Bond Powers and traits."""

from __future__ import annotations

from typing import Any

from ....forms import character as character_forms
from ....forms import familiar as ff
from ....forms import trait_roll as trait_roll_forms
from ..fields import (
    FieldsDialog,
)
from ..steps import run_steps
from .base import (
    WorkspaceBase,
    _SectionOps,
)


class FamiliarActions(WorkspaceBase):
    """WorkspaceScreen's actions for the Familiar sheet: Info, Binding & Cords,
    Characteristics, Health, Natural Weapons, Abilities, Bond Powers and
    traits."""

    # -- Familiar: Info & Binding --

    def _edit_familiar_info(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            ff.apply_info(familiar, result)
            self._commit("section-fam-info", tree=True)

        self.app.push_screen(
            FieldsDialog("Edit Familiar", ff.info_fields(familiar)),
            handle_result,
        )

    def _edit_familiar_binding(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            ff.apply_binding(familiar, result)
            self._commit("section-fam-binding")

        self.app.push_screen(
            FieldsDialog("Edit Binding & Cords", ff.binding_fields(familiar)),
            handle_result,
        )

    def _edit_familiar_characteristics(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            ff.apply_characteristics(familiar, result)
            self._commit("section-fam-characteristics")

        self.app.push_screen(
            FieldsDialog(
                "Edit Characteristics", ff.familiar_characteristics_fields(familiar)
            ),
            handle_result,
        )

    # -- Familiar: Combat & Health --

    def _edit_familiar_wounds(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                familiar.wounds = familiar.wounds.with_counts(
                    soak=familiar.wounds.soak, **result
                )
                self._commit("section-fam-health")

        self.app.push_screen(
            FieldsDialog(
                "Edit Wounds",
                character_forms.wounds_fields(familiar.wounds, soak=False),
            ),
            handle_result,
        )

    def action_familiar_trait_roll(self) -> None:
        """More's Roll on the familiar's Personality Traits, with its
        Silver Cord (DE p. 267)."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        run_steps(
            self.app, trait_roll_forms.roll_form(self.saga, familiar), lambda _e: None
        )

    def _edit_familiar_fatigue(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                familiar.fatigue_level = result["level"]
                self._commit("section-fam-health")

        self.app.push_screen(
            FieldsDialog(
                "Edit Fatigue Level",
                character_forms.fatigue_fields(familiar.fatigue_level),
            ),
            handle_result,
        )

    # -- Familiar: Personality Traits & Reputations --

    def _familiar_section_ops(self) -> dict[str, _SectionOps]:
        """a / d / e on the familiar sheet (see
        WorkspaceScreen._section_ops)."""
        return {
            "section-fam-info": _SectionOps(edit=self._edit_familiar_info),
            "section-fam-binding": _SectionOps(edit=self._edit_familiar_binding),
            "section-fam-characteristics": _SectionOps(
                edit=self._edit_familiar_characteristics
            ),
            "section-fam-health": _SectionOps(edit=self._edit_familiar_wounds),
            "section-fam-natural-weapons": self._core_ops_of(
                "section-fam-natural-weapons"
            ),
            "tab-fam-abilities": self._core_ops_of("tab-fam-abilities"),
            "tab-fam-powers": self._core_ops_of("tab-fam-powers"),
        }
