"""The Familiar sheet: Info, Binding & Cords, Characteristics, Health, Natural
Weapons, Abilities, Bond Powers and traits."""

from __future__ import annotations

from typing import Any

from ... import possessions as pos
from ... import storage
from ...markup import escape
from ...models import (
    Ability,
    BondPower,
    Possession,
    Wounds,
)
from ..fields import (
    FieldsDialog,
)
from ..forms import (
    EditFamiliarBindingScreen,
    _bond_power_fields,
    _characteristics_from,
    _familiar_characteristics_fields,
    _familiar_info_fields,
    _fatigue_fields,
    _possession_dialog,
    _wounds_fields,
)
from ..pickers import (
    AbilityPickerScreen,
)
from ..prompts import (
    _ability_fields,
    _ability_from,
)
from .base import (
    WorkspaceBase,
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
            result["season_bound"] = result["season_bound"] or ""
            for field_name, value in result.items():
                setattr(familiar, field_name, value)
            self._commit("section-fam-info", tree=True)

        self.app.push_screen(
            FieldsDialog("Edit Familiar", _familiar_info_fields(familiar)),
            handle_result,
        )

    def _edit_familiar_binding(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, object] | None) -> None:
            if result is None:
                return
            for field_name, value in result.items():
                setattr(familiar, field_name, value)
            self._commit("section-fam-binding")

        self.app.push_screen(EditFamiliarBindingScreen(familiar), handle_result)

    def _edit_familiar_characteristics(self) -> None:
        familiar = self.selected_familiar
        if familiar is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            familiar.characteristics = _characteristics_from(result)
            familiar.base_soak = result["base_soak"]
            familiar.magic_resistance = result["magic_resistance"]
            self._commit("section-fam-characteristics")

        self.app.push_screen(
            FieldsDialog(
                "Edit Characteristics", _familiar_characteristics_fields(familiar)
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
            FieldsDialog("Edit Wounds", _wounds_fields(familiar.wounds, soak=False)),
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
            FieldsDialog("Edit Fatigue Level", _fatigue_fields(familiar.fatigue_level)),
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
        """Edit the chosen attack; with none chosen, ask which one."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_natural_weapon(),
            [
                pos.row_label(pos.PossessionEntry("weapon", weapon))
                for weapon in familiar.natural_weapons
            ],
            title="Edit which attack?",
            empty="No Natural Weapons to edit.",
            then=lambda index: self._familiar_natural_weapon_form(index),
        )

    def _remove_familiar_natural_weapon(self) -> None:
        """Delete the chosen attack (after confirming); with none chosen,
        ask which one first."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_natural_weapon(),
            [
                pos.row_label(pos.PossessionEntry("weapon", weapon))
                for weapon in familiar.natural_weapons
            ],
            title="Remove which attack?",
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

        self.app.push_screen(AbilityPickerScreen(exclude_names), handle_result)

    def _edit_familiar_ability(self) -> None:
        """Edit the chosen Ability; with none chosen, ask which one."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_ability(),
            [self._ability_label(a) for a in familiar.abilities],
            title="Edit which Ability?",
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
            FieldsDialog(escape(existing.name), _ability_fields(existing)),
            handle_result,
        )

    def _remove_familiar_ability(self) -> None:
        """Delete the chosen Ability (after confirming); with none chosen,
        ask which one first."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_ability(),
            [self._ability_label(a) for a in familiar.abilities],
            title="Remove an Ability",
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
            # "select" fields with allow_blank dismiss None for "not set";
            # BondPower uses "" like Familiar.binding_technique/_form do.
            values["technique"] = values.get("technique") or ""
            values["form"] = values.get("form") or ""
            if existing is not None:
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                familiar.bond_powers.append(
                    BondPower(
                        id=storage.generate_unique_id(
                            values.get("name") or "power",
                            [p.id for p in familiar.bond_powers],
                        ),
                        **values,
                    )
                )
            self._commit("tab-fam-powers")

        self.app.push_screen(
            FieldsDialog(title, _bond_power_fields(existing)), handle_result
        )

    def _add_familiar_bond_power(self) -> None:
        self._familiar_bond_power_form(None)

    def _edit_familiar_bond_power(self) -> None:
        """Edit the chosen Bond Power; with none chosen, ask which one."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_bond_power(),
            [escape(p.name) or "(unnamed)" for p in familiar.bond_powers],
            title="Edit which Bond Power?",
            empty="No Bond Powers to edit.",
            then=lambda index: self._familiar_bond_power_form(index),
        )

    def _remove_familiar_bond_power(self) -> None:
        """Delete the chosen Bond Power (after confirming); with none
        chosen, ask which one first."""
        familiar = self.selected_familiar
        if familiar is None:
            return
        self._chosen_or_pick(
            self._selected_familiar_bond_power(),
            [escape(p.name) or "(unnamed)" for p in familiar.bond_powers],
            title="Remove a Bond Power",
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
