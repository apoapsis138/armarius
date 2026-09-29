"""The Character sheet: Info, Characteristics, Abilities, traits, Health, Arts,
Raw Vis, Hermetic Background, Known Spells, Inventory, This Season and the
Diary."""

from __future__ import annotations

from typing import Any

from ... import laboratories as lab_text
from ... import possessions as pos
from ... import seasons, sourcebooks, storage
from ... import spells as spl
from ...markup import escape
from ...models import (
    Ability,
    Aging,
    ArtScore,
    Background,
    Character,
    Description,
    DiaryEntry,
    HermeticBackground,
    KnownSpell,
    Possession,
    SeasonPlan,
    Wounds,
    add_raw_vis,
    assign_laboratory,
    known_fields,
    replace_raw_vis,
)
from ...rules import seasons as season_rules
from ..fields import (
    FieldsDialog,
)
from ..forms import (
    EditArtsScreen,
    MasteryEditScreen,
    _aging_fields,
    _biographical_fields,
    _character_info_dialog,
    _characteristics_fields,
    _characteristics_from,
    _fatigue_fields,
    _hermetic_fields,
    _possession_dialog,
    _season_plan_dialog,
    _wounds_fields,
)
from ..pickers import (
    AbilityPickerScreen,
    RemovalPickerScreen,
    SpellChooserScreen,
)
from ..prompts import (
    ConfirmScreen,
    _ability_fields,
    _ability_from,
    _ability_problem,
    _diary_entry_dialog,
    _raw_vis_dialog,
)
from .base import (
    WorkspaceBase,
)


class CharacterActions(WorkspaceBase):
    """WorkspaceScreen's actions for the Character sheet: Info,
    Characteristics, Abilities, traits, Health, Arts, Raw Vis, Hermetic
    Background, Known Spells and Inventory."""

    # -- Character Info / Characteristics --

    def _edit_character_info(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            character.name = result["name"]
            character.type = result.get("type", character.type)
            character.covenant_id = result["covenant_id"]
            self.selected_covenant = self.saga.covenant(character.covenant_id)
            if character.type == "magus":
                assign_laboratory(self.saga, character, result["laboratory_id"])
            background = character.background
            background.setting = result["setting"]
            background.confidence_score = result["confidence_score"]
            background.confidence_points = result["confidence_points"]
            background.true_faith_score = result["true_faith_score"]
            background.faith_points = result["faith_points"]
            background.size = result["size"]
            self._commit("section-char-info", tree=True)

        self.app.push_screen(
            _character_info_dialog(self.saga, character), handle_result
        )

    def _edit_characteristics(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                character.characteristics = _characteristics_from(result)
                self._commit("section-char-characteristics")

        self.app.push_screen(
            FieldsDialog(
                "Edit Characteristics",
                _characteristics_fields(character.characteristics),
            ),
            handle_result,
        )

    def _edit_biographical_detail(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                for attribute in known_fields(Background, result):
                    setattr(character.background, attribute, result[attribute])
                character.description = Description(**known_fields(Description, result))
                self._commit("section-char-biographical")
                # Age (derived from Year Born) lives in the top panel.
                self._refresh_character_section("section-char-info")

        self.app.push_screen(
            FieldsDialog(
                "Edit Biographical Detail",
                _biographical_fields(character.background, character.description),
            ),
            handle_result,
        )

    def _edit_aging(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                character.aging = Aging(**result)
                self._commit("section-aging")

        self.app.push_screen(
            FieldsDialog("Edit Aging & Warping", _aging_fields(character.aging)),
            handle_result,
        )

    # -- Abilities --

    def _add_ability(self) -> None:
        character = self.selected_character
        if character is None:
            return
        exclude_names = {a.name for a in character.abilities}

        def handle_result(ability: Ability | None) -> None:
            if ability is not None:
                character.abilities.append(ability)
                self._commit("tab-abilities")

        self.app.push_screen(
            AbilityPickerScreen(exclude_names, books=sourcebooks.saga_books(self.saga)),
            handle_result,
        )

    def _selected_ability(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_ability() if view is not None else None

    def _remove_ability(self) -> None:
        """Delete the chosen Ability (after confirming); with none chosen,
        ask which one first."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_ability(),
            [self._ability_label(a) for a in character.abilities],
            title="Remove an Ability",
            empty="No Abilities to remove.",
            then=lambda index: self._confirm_remove_ability(index),
        )

    def _confirm_remove_ability(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        self._confirm_delete(
            character.abilities, index, character.abilities[index].name, "tab-abilities"
        )

    def _edit_ability(self) -> None:
        """Edit the chosen Ability; with none chosen, ask which one."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_ability(),
            [self._ability_label(a) for a in character.abilities],
            title="Edit which Ability?",
            empty="No Abilities to edit.",
            then=lambda index: self._edit_ability_at(index),
        )

    def _edit_ability_at(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        existing = character.abilities[index]

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                character.abilities[index] = _ability_from(
                    existing.name, existing.category, result
                )
                self._commit("tab-abilities")

        self.app.push_screen(
            FieldsDialog(
                escape(existing.name),
                _ability_fields(existing),
                validate=_ability_problem,
            ),
            handle_result,
        )

    # -- Personality Traits / Reputations / Wounds / Fatigue --

    def _selected_personality_trait(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_personality_trait() if view is not None else None

    def _selected_character_reputation(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_reputation() if view is not None else None

    def _edit_wounds(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                character.wounds = Wounds(**result)
                self._commit("section-char-health")

        self.app.push_screen(
            FieldsDialog("Edit Wounds", _wounds_fields(character.wounds)),
            handle_result,
        )

    def _edit_fatigue(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                character.fatigue_level = result["level"]
                self._commit("section-char-health")

        self.app.push_screen(
            FieldsDialog(
                "Edit Fatigue Level", _fatigue_fields(character.fatigue_level)
            ),
            handle_result,
        )

    # -- Arts (magi only) --

    def _edit_arts(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(arts: dict[str, ArtScore] | None) -> None:
            if arts is not None:
                character.arts = arts
                self._commit("section-arts")

        self.app.push_screen(EditArtsScreen(character.arts), handle_result)

    # -- Raw Vis / Hermetic Background (magi only) --

    def _add_raw_vis(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: tuple[str, int] | None) -> None:
            if result is not None:
                art, pawns = result
                add_raw_vis(character.raw_vis, art, pawns)
                self._commit("section-raw-vis-hermetic")

        self.app.push_screen(_raw_vis_dialog(), handle_result)

    def _selected_raw_vis(self) -> int | None:
        view = self._character_sheet_view
        section = self._active_section()
        if view is None or section not in (
            "section-raw-vis-hermetic",
            "section-raw-vis-inventory",
        ):
            return None
        return view.selected_raw_vis(section)

    def _edit_raw_vis(self) -> None:
        """Edit the chosen Raw Vis entry; with none chosen, ask which one."""
        character = self.selected_character
        if character is None:
            return
        selected = self._selected_raw_vis()
        if selected is not None:
            self._edit_raw_vis_at(selected)
            return
        if not character.raw_vis:
            self.notify("No Raw Vis to edit.")
            return

        arts = sorted(character.raw_vis)
        labels = [f"{art.title()}: {character.raw_vis[art]} pawn(s)" for art in arts]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._edit_raw_vis_at(index)

        self.app.push_screen(
            RemovalPickerScreen("Edit which Raw Vis entry?", labels), handle_index
        )

    def _edit_raw_vis_at(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        arts = sorted(character.raw_vis)
        old_art = arts[index]

        def handle_result(result: tuple[str, int] | None) -> None:
            if result is not None:
                art, pawns = result
                replace_raw_vis(character.raw_vis, old_art, art, pawns)
                self._commit("section-raw-vis-hermetic")

        self.app.push_screen(
            _raw_vis_dialog(existing=(old_art, character.raw_vis[old_art])),
            handle_result,
        )

    def _remove_raw_vis(self) -> None:
        """Delete the chosen Raw Vis entry (after confirming); with none
        chosen, ask which one first."""
        character = self.selected_character
        if character is None:
            return
        selected = self._selected_raw_vis()
        if selected is not None:
            self._confirm_remove_raw_vis(selected)
            return
        if not character.raw_vis:
            self.notify("No Raw Vis to remove.")
            return

        arts = sorted(character.raw_vis)
        labels = [f"{art.title()}: {character.raw_vis[art]} pawn(s)" for art in arts]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._confirm_remove_raw_vis(index)

        self.app.push_screen(
            RemovalPickerScreen("Remove a Raw Vis entry", labels), handle_index
        )

    def _confirm_remove_raw_vis(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        art = sorted(character.raw_vis)[index]

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del character.raw_vis[art]
                self._commit("section-raw-vis-hermetic")

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(art.title())}?"), handle_confirmed
        )

    def _edit_hermetic_background(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                character.hermetic = HermeticBackground(**result)
                self._commit("section-hermetic-background")

        self.app.push_screen(
            FieldsDialog(
                "Edit Hermetic Background", _hermetic_fields(character.hermetic)
            ),
            handle_result,
        )

    # -- Spells known (magi only) --

    def _add_spell(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(spell_id: str | None) -> None:
            if spell_id is not None:
                character.spells_known.append(KnownSpell(spell_id=spell_id))
                self._commit("section-known-spells")

        self.app.push_screen(
            SpellChooserScreen(
                self.saga,
                exclude={k.spell_id for k in character.spells_known},
                title=f"Add a spell {escape(character.name)} knows",
            ),
            handle_result,
        )

    def _known_spell_name(self, known: KnownSpell) -> str:
        """A known spell's name (plain text; its id if it's missing)."""
        spell = spl.find_spell(self.saga, known.spell_id)
        return spell.name if spell else f"{known.spell_id} (unknown spell)"

    def _known_spell_labels(self, character: Character) -> list[str]:
        """The known spells' names, as picker labels (markup)."""
        return [escape(self._known_spell_name(k)) for k in character.spells_known]

    def _selected_known_spell(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_known_spell() if view is not None else None

    def _edit_spell_mastery(self) -> None:
        """Edit the chosen known spell's Mastery; with none chosen, ask
        which one."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_known_spell(),
            self._known_spell_labels(character),
            title="Edit Mastery for which spell?",
            empty="No Spells to edit.",
            then=lambda index: self._edit_spell_mastery_at(index),
        )

    def _edit_spell_mastery_at(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        known = character.spells_known[index]
        spell = spl.find_spell(self.saga, known.spell_id)
        name = spell.name if spell else known.spell_id

        def handle_result(result: KnownSpell | None) -> None:
            if result is not None:
                character.spells_known[index] = result
                self._commit("section-known-spells")

        self.app.push_screen(MasteryEditScreen(name, known), handle_result)

    def _remove_spell(self) -> None:
        """Delete the chosen known spell (after confirming); with none
        chosen, ask which one first."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_known_spell(),
            self._known_spell_labels(character),
            title="Remove a Known Spell",
            empty="No Spells to remove.",
            then=lambda index: self._confirm_remove_spell(index),
        )

    def _confirm_remove_spell(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        self._confirm_delete(
            character.spells_known,
            index,
            self._known_spell_name(character.spells_known[index]),
            "section-known-spells",
        )

    # -- Inventory --

    def _selected_inventory_item(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_inventory_item() if view is not None else None

    def _add_item(self) -> None:
        """Add an item: ask which kind first (the section is one combined
        list, unlike the covenant Possessions tab's per-kind sections)."""
        character = self.selected_character
        if character is None:
            return

        def handle_kind(index: int | None) -> None:
            if index is not None:
                self._inventory_item_form(("weapon", "armor", "item")[index], None)

        self.app.push_screen(
            RemovalPickerScreen("Add which kind of item?", ["Weapon", "Armor", "Item"]),
            handle_kind,
        )

    def _inventory_item_form(self, kind: str, index: int | None) -> None:
        character = self.selected_character
        if character is None:
            return
        existing = character.inventory[index] if index is not None else None
        entry = pos.PossessionEntry(kind, existing) if existing is not None else None
        title = (
            f"Add a {pos.KIND_SINGULAR[kind]}"
            if existing is None
            else f"Edit {escape(existing.name or 'this item')}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            if index is not None and existing is not None:
                for key, value in values.items():
                    setattr(existing, key, value)
            else:
                character.inventory.append(
                    Possession(
                        id=storage.generate_unique_id(
                            values.get("name") or kind,
                            [item.id for item in character.inventory],
                        ),
                        kind=kind,
                        **values,
                    )
                )
            self._commit("section-inventory")

        self.app.push_screen(_possession_dialog(title, kind, entry), handle_result)

    def _edit_item(self) -> None:
        """Edit the chosen item; with none chosen, ask which one."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_inventory_item(),
            [
                pos.row_label(pos.PossessionEntry(item.kind, item))
                for item in character.inventory
            ],
            title="Edit which item?",
            empty="No Items to edit.",
            then=lambda index: self._inventory_item_form(
                character.inventory[index].kind, index
            ),
        )

    def _remove_item(self) -> None:
        """Delete the chosen item (after confirming); with none chosen, ask
        which one first."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_inventory_item(),
            [
                pos.row_label(pos.PossessionEntry(item.kind, item))
                for item in character.inventory
            ],
            title="Remove an Item",
            empty="No Items to remove.",
            then=lambda index: self._confirm_remove_item(index),
        )

    def _confirm_remove_item(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return
        self._confirm_delete(
            character.inventory,
            index,
            character.inventory[index].name or "this item",
            "section-inventory",
        )

    # -- Character: This Season (the season's plan) --

    def _plan_season(self) -> None:
        """Plan the character's current season, or change the plan."""
        character = self.selected_character
        if character is None:
            return
        if not season_rules.is_planned(character):
            self.notify(
                "Grogs aren't planned season by season: they're updated once a "
                "year (Grogs, Chapter 5)."
            )
            return

        def handle_result(plan: SeasonPlan | None) -> None:
            if plan is not None:
                seasons.set_plan(self.saga, plan)
                self._commit("section-char-season")

        self.app.push_screen(
            _season_plan_dialog(
                self.saga, character, seasons.plan_for(self.saga, character)
            ),
            handle_result,
        )

    def _clear_season_plan(self) -> None:
        """Drop the character's plan for the current season (after
        confirming)."""
        character = self.selected_character
        if character is None:
            return
        plan = seasons.plan_for(self.saga, character)
        if plan is None:
            self.notify("Nothing is planned for this season.")
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and seasons.clear_plan(self.saga, character):
                self._commit("section-char-season")

        self.app.push_screen(
            ConfirmScreen(
                f"Clear {escape(character.name)}'s plan "
                f"({escape(seasons.plan_summary(self.saga, character, plan))})?"
            ),
            handle_confirmed,
        )

    # -- Character: Diary --

    def _selected_character_diary_entry(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_diary_entry() if view is not None else None

    def _character_diary_dialog(self, existing: DiaryEntry | None) -> Any:
        return _diary_entry_dialog(
            self.saga.current_year,
            existing=existing,
            default_season=self.saga.current_season,
            activities=[a.label for a in season_rules.ACTIVITIES.values()],
        )

    def _add_character_diary_entry(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(entry: DiaryEntry | None) -> None:
            if entry is not None:
                character.diary.append(entry)
                self._commit("tab-diary")

        self.app.push_screen(self._character_diary_dialog(None), handle_result)

    def _edit_character_diary_entry(self) -> None:
        """Edit the chosen Diary entry; with none chosen, ask which one."""
        character = self.selected_character
        if character is None:
            return

        def edit(index: int) -> None:
            def handle_result(entry: DiaryEntry | None) -> None:
                if entry is not None:
                    character.diary[index] = entry
                    self._commit("tab-diary")

            self.app.push_screen(
                self._character_diary_dialog(character.diary[index]), handle_result
            )

        self._chosen_or_pick(
            self._selected_character_diary_entry(),
            [label for _, label in lab_text.diary_rows(character.diary)],
            title="Edit which Diary Entry?",
            empty="No Diary entries to edit.",
            then=edit,
        )

    def _remove_character_diary_entry(self) -> None:
        """Delete the chosen Diary entry (after confirming); with none
        chosen, ask which one first."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_character_diary_entry(),
            [label for _, label in lab_text.diary_rows(character.diary)],
            title="Remove a Diary Entry",
            empty="No Diary entries to remove.",
            then=lambda index: self._confirm_delete(
                character.diary,
                index,
                character.diary[index].name or "this entry",
                "tab-diary",
            ),
        )
