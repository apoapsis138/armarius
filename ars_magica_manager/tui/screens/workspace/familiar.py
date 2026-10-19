"""The Familiar sheet: Info, Binding & Cords, Characteristics, Health, Natural
Weapons, Abilities, Bond Powers and traits."""

from __future__ import annotations

from typing import Any

from .... import possessions as pos
from .... import sourcebooks, storage
from ....forms import character as character_forms
from ....forms import familiar as ff
from ....markup import escape
from ....models import (
    Ability,
    Possession,
    Wounds,
)
from ..fields import (
    FieldsDialog,
)
from ..forms import (
    _possession_dialog,
)
from ..pickers import (
    AbilityPickerScreen,
)
from ..prompts import (
    _ability_dialog,
    _ability_from,
)
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
                familiar.wounds = Wounds(soak=familiar.wounds.soak, **result)
                self._commit("section-fam-health")

        self.app.push_screen(
            FieldsDialog(
                "Edit Wounds",
                character_forms.wounds_fields(familiar.wounds, soak=False),
            ),
            handle_result,
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

    def _selected_familiar_natural_weapon(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_natural_weapon() if view is not None else None

    def _familiar_natural_weapon_form(self, index: int | None) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        existing = familiar.natural_weapons[index] if index is not None else None
        entry = (
            pos.PossessionEntry("weapon", existing) if existing is not None else None
        )
        title = (
            "Add a Natural Weapon"
            if existing is None
            else f"Edit {escape(existing.name or 'this attack')}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            if index is not None and existing is not None:
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                familiar.natural_weapons.append(
                    Possession(
                        id=storage.generate_unique_id(
                            values.get("name") or "weapon",
                            [item.id for item in familiar.natural_weapons],
                        ),
                        kind="weapon",
                        **values,
                    )
                )
            self._commit("section-fam-natural-weapons")

        self.app.push_screen(
            _possession_dialog(title, "weapon", entry, natural=True), handle_result
        )

    def _add_familiar_natural_weapon(self) -> None:
        self._familiar_natural_weapon_form(None)

    def _edit_familiar_natural_weapon(self) -> None:
        """Edit the chosen attack."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_natural_weapon(),
            [
                pos.row_label(pos.PossessionEntry("weapon", weapon))
                for weapon in familiar.natural_weapons
            ],
            empty="No Natural Weapons to edit.",
            then=lambda index: self._familiar_natural_weapon_form(index),
        )

    def _remove_familiar_natural_weapon(self) -> None:
        """Delete the chosen attack (after confirming)."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_natural_weapon(),
            [
                pos.row_label(pos.PossessionEntry("weapon", weapon))
                for weapon in familiar.natural_weapons
            ],
            empty="No Natural Weapons to remove.",
            then=lambda index: self._confirm_remove_familiar_natural_weapon(index),
        )

    def _confirm_remove_familiar_natural_weapon(self, index: int) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._confirm_delete(
            familiar.natural_weapons,
            index,
            familiar.natural_weapons[index].name or "this attack",
            "section-fam-natural-weapons",
        )

    # -- Familiar: Abilities --

    def _selected_familiar_ability(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_ability() if view is not None else None

    def _add_familiar_ability(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        exclude_names = {a.name for a in familiar.abilities}

        def handle_result(ability: Ability | None) -> None:
            if ability is not None:
                familiar.abilities.append(ability)
                self._commit("tab-fam-abilities")

        self.app.push_screen(
            AbilityPickerScreen(
                exclude_names,
                books=sourcebooks.saga_books(self.saga),
                virtues_flaws=familiar.virtues_flaws,
            ),
            handle_result,
        )

    def _edit_familiar_ability(self) -> None:
        """Edit the chosen Ability."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_ability(),
            [self._ability_label(a) for a in familiar.abilities],
            empty="No Abilities to edit.",
            then=lambda index: self._edit_familiar_ability_at(index),
        )

    def _edit_familiar_ability_at(self, index: int) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        existing = familiar.abilities[index]

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                familiar.abilities[index] = _ability_from(
                    existing.name, existing.category, result
                )
                self._commit("tab-fam-abilities")

        self.app.push_screen(
            _ability_dialog(existing.name, existing, familiar.virtues_flaws),
            handle_result,
        )

    def _remove_familiar_ability(self) -> None:
        """Delete the chosen Ability (after confirming)."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_ability(),
            [self._ability_label(a) for a in familiar.abilities],
            empty="No Abilities to remove.",
            then=lambda index: self._confirm_remove_familiar_ability(index),
        )

    def _confirm_remove_familiar_ability(self, index: int) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._confirm_delete(
            familiar.abilities,
            index,
            familiar.abilities[index].name,
            "tab-fam-abilities",
        )

    # -- Familiar: Bond Powers --

    def _selected_familiar_bond_power(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_bond_power() if view is not None else None

    def _familiar_bond_power_form(self, index: int | None) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        existing = familiar.bond_powers[index] if index is not None else None
        title = (
            "Add a Bond Power"
            if existing is None
            else f"Edit {escape(existing.name) or 'this Bond Power'}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            ff.save_bond_power(familiar.bond_powers, existing, values)
            self._commit("tab-fam-powers")

        self.app.push_screen(
            FieldsDialog(title, ff.bond_power_fields(existing)), handle_result
        )

    def _add_familiar_bond_power(self) -> None:
        self._familiar_bond_power_form(None)

    def _edit_familiar_bond_power(self) -> None:
        """Edit the chosen Bond Power."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_bond_power(),
            [escape(p.name) or "(unnamed)" for p in familiar.bond_powers],
            empty="No Bond Powers to edit.",
            then=lambda index: self._familiar_bond_power_form(index),
        )

    def _remove_familiar_bond_power(self) -> None:
        """Delete the chosen Bond Power (after confirming)."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_bond_power(),
            [escape(p.name) or "(unnamed)" for p in familiar.bond_powers],
            empty="No Bond Powers to remove.",
            then=lambda index: self._confirm_remove_familiar_bond_power(index),
        )

    def _confirm_remove_familiar_bond_power(self, index: int) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._confirm_delete(
            familiar.bond_powers,
            index,
            familiar.bond_powers[index].name or "this Bond Power",
            "tab-fam-powers",
        )

    # -- Familiar: Personality Traits & Reputations --

    def _selected_familiar_personality_trait(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_personality_trait() if view is not None else None

    def _selected_familiar_reputation(self) -> int | None:
        view = self._familiar_sheet_view
        return view.selected_reputation() if view is not None else None

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
            "section-fam-natural-weapons": _SectionOps(
                self._add_familiar_natural_weapon,
                self._remove_familiar_natural_weapon,
                self._edit_familiar_natural_weapon,
            ),
            "tab-fam-abilities": _SectionOps(
                self._add_familiar_ability,
                self._remove_familiar_ability,
                self._edit_familiar_ability,
            ),
            "tab-fam-powers": _SectionOps(
                self._add_familiar_bond_power,
                self._remove_familiar_bond_power,
                self._edit_familiar_bond_power,
            ),
        }
