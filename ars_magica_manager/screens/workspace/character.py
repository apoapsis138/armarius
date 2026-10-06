"""The Character sheet: Info, Characteristics, Abilities, traits, Health, Arts,
Raw Vis, Hermetic Background, Known Spells, Inventory, This Season and the
Diary."""

from __future__ import annotations

import random
from typing import Any

from ... import laboratories as lab_text
from ... import possessions as pos
from ... import seasons, sourcebooks, storage
from ... import spells as spl
from ...markup import escape
from ...models import (
    Ability,
    ArtScore,
    Background,
    Breakthrough,
    Character,
    Description,
    DiaryEntry,
    HermeticBackground,
    KnownSpell,
    LabTextAccess,
    Possession,
    Spell,
    Wounds,
    add_raw_vis,
    assign_laboratory,
    known_fields,
    replace_raw_vis,
)
from ...rules import activities as season_rules
from ...rules import aging as aging_rules
from ..fields import (
    FieldsDialog,
)
from ..forms import (
    EditArtsScreen,
    MasteryEditScreen,
    _aging_fields,
    _biographical_fields,
    _breakthrough_dialog,
    _character_info_dialog,
    _characteristics_dialog,
    _characteristics_from,
    _fatigue_fields,
    _hermetic_fields,
    _possession_dialog,
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
    _lab_text_access_dialog,
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
            # Only a magus has a free House Virtue.
            self._commit(
                "section-char-info", "section-vf-virtues", "section-vf-flaws", tree=True
            )

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
            _characteristics_dialog(self.saga, character), handle_result
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
                _biographical_fields(
                    character.background,
                    character.description,
                    self.saga.players,
                    may_assign=self._is_storyguide(),
                ),
            ),
            handle_result,
        )

    def _edit_aging(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            gained = result.pop("gain_warping", 0) or 0
            aging = character.aging
            if result["decrepitude"] != aging.decrepitude:
                aging.decrepitude_points = aging_rules.points_for_score(
                    result["decrepitude"]
                )
            # Only the fields on the form: the rest (Longevity, Aging Points)
            # stays as it is.
            for key, value in result.items():
                setattr(aging, key, value)
            if gained > 0:
                notes = seasons.gain_warping(
                    self.saga, character, gained, random.Random()
                )
                self.notify(" ".join(notes), timeout=12)
            self._commit("section-aging", "tab-diary")

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
        """Delete the chosen Ability (after confirming)."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_ability(),
            [self._ability_label(a) for a in character.abilities],
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
        """Edit the chosen Ability."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_ability(),
            [self._ability_label(a) for a in character.abilities],
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
        """Edit the chosen Raw Vis entry."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_raw_vis(),
            sorted(character.raw_vis),
            empty="No Raw Vis to edit.",
            then=self._edit_raw_vis_at,
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
        """Delete the chosen Raw Vis entry (after confirming)."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_raw_vis(),
            sorted(character.raw_vis),
            empty="No Raw Vis to remove.",
            then=self._confirm_remove_raw_vis,
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
                # The House decides which Virtue is free.
                self._commit(
                    "section-hermetic-background",
                    "section-vf-virtues",
                    "section-vf-flaws",
                )

        self.app.push_screen(
            FieldsDialog(
                "Edit Hermetic Background", _hermetic_fields(character.hermetic)
            ),
            handle_result,
        )

    def _edit_lab_text_access(self) -> None:
        """Set whose raw Lab Texts the magus reads, and to what level: an author's entry
        is added, changed, or -- at level 0 -- removed."""
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: tuple[str, int, str] | None) -> None:
            if result is None:
                return
            author, level, via = result
            if level > 0:
                character.lab_text_access[author] = LabTextAccess(level, via)
            else:
                character.lab_text_access.pop(author, None)
            self._commit("section-hermetic-background", "section-books")

        self.app.push_screen(
            _lab_text_access_dialog(self.saga, character), handle_result
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
        """Edit the chosen known spell's Mastery."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_known_spell(),
            self._known_spell_labels(character),
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
        """Delete the chosen known spell (after confirming)."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_known_spell(),
            self._known_spell_labels(character),
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

    def action_share_spell(self) -> None:
        """Make one of the magus's invented spells available to the saga: the chosen
        Known Spell if it is one of his own, else the one picked from them. It moves to
        the saga's Spells."""
        character = self.selected_character
        if character is None:
            return
        shareable = spl.shareable_spells(character)
        if not shareable:
            self.notify("No invented spells to share.")
            return

        def confirm(spell: Spell) -> None:
            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    spl.share_invented_spell(self.saga, character, spell)
                    self._commit("section-known-spells", tree=True)

            self.app.push_screen(
                ConfirmScreen(
                    f"Make {escape(spell.name)} available to the whole saga? It "
                    f"moves to the saga's Spells, where anyone can learn it or "
                    f"write it up; {escape(character.name)} still knows it.",
                    yes_label="Share",
                    yes_variant="primary",
                ),
                handle_confirmed,
            )

        chosen = self._selected_known_spell()
        if chosen is not None and chosen < len(character.spells_known):
            spell_id = character.spells_known[chosen].spell_id
            own = next((s for s in shareable if s.id == spell_id), None)
            if own is not None:
                confirm(own)
                return
        if len(shareable) == 1:
            confirm(shareable[0])
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                confirm(shareable[index])

        self.app.push_screen(
            RemovalPickerScreen(
                "Share which invented spell?",
                [f"{escape(s.name)} ({spl.shorthand(s)})" for s in shareable],
            ),
            handle_index,
        )

    # -- Research Goals --

    def _selected_research_goal(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_research_goal() if view is not None else None

    def _research_goal_labels(self, character: Character) -> list[str]:
        return [escape(b.name) for b in character.breakthroughs]

    def _add_research_goal(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: Breakthrough | None) -> None:
            if result is not None:
                character.breakthroughs.append(result)
                self._commit("section-research-goals")

        self.app.push_screen(_breakthrough_dialog(None), handle_result)

    def _edit_research_goal(self) -> None:
        """Edit the chosen research goal."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_research_goal(),
            self._research_goal_labels(character),
            empty="No research goals to edit.",
            then=self._edit_research_goal_at,
        )

    def _edit_research_goal_at(self, index: int) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: Breakthrough | None) -> None:
            if result is not None:
                character.breakthroughs[index] = result
                self._commit("section-research-goals")

        self.app.push_screen(
            _breakthrough_dialog(character.breakthroughs[index]), handle_result
        )

    def _remove_research_goal(self) -> None:
        """Delete the chosen research goal (after confirming)."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_research_goal(),
            self._research_goal_labels(character),
            empty="No research goals to remove.",
            then=lambda index: self._confirm_delete(
                character.breakthroughs,
                index,
                character.breakthroughs[index].name,
                "section-research-goals",
            ),
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
        """Edit the chosen item."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_inventory_item(),
            [
                pos.row_label(pos.PossessionEntry(item.kind, item))
                for item in character.inventory
            ],
            empty="No Items to edit.",
            then=lambda index: self._inventory_item_form(
                character.inventory[index].kind, index
            ),
        )

    def _remove_item(self) -> None:
        """Delete the chosen item (after confirming)."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_inventory_item(),
            [
                pos.row_label(pos.PossessionEntry(item.kind, item))
                for item in character.inventory
            ],
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
        if self.selected_character is not None:
            self._plan_season_for(self.selected_character, "section-char-season")

    def _clear_season_plan(self) -> None:
        """Drop the character's plan for the current season (after
        confirming)."""
        if self.selected_character is not None:
            self._clear_season_plan_for(self.selected_character, "section-char-season")

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
        """Edit the chosen Diary entry."""
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
            empty="No Diary entries to edit.",
            then=edit,
        )

    def _remove_character_diary_entry(self) -> None:
        """Delete the chosen Diary entry (after confirming)."""
        character = self.selected_character
        if character is None:
            return
        self._chosen_or_pick(
            self._selected_character_diary_entry(),
            [label for _, label in lab_text.diary_rows(character.diary)],
            empty="No Diary entries to remove.",
            then=lambda index: self._confirm_delete(
                character.diary,
                index,
                character.diary[index].name or "this entry",
                "tab-diary",
            ),
        )
