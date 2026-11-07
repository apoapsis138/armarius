"""The Character sheet: Info, Characteristics, Abilities, traits, Health, Arts,
Raw Vis, Hermetic Background, Known Spells, Inventory, This Season and the
Diary."""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from typing import Any

from .... import (
    creation,
    section_verbs,
    traditions,
    world,
)
from .... import spells as spl
from ....arts import ARTS
from ....forms import character as character_forms
from ....forms import interests as interests_forms
from ....forms import menu as menu_forms
from ....markup import escape
from ....models import (
    Character,
    Covenant,
    HermeticBackground,
    LabTextAccess,
    Spell,
)
from ....rules import disease
from ....sections import (
    CHAR_AHEAD_SECTION,
    CONSTANT_EFFECTS_SECTION,
    POWERS_SECTION,
)
from ..fields import (
    FieldsDialog,
)
from ..forms import (
    EditArtsScreen,
    _character_info_dialog,
    _characteristics_dialog,
    _characteristics_from,
)
from ..pickers import (
    RemovalPickerScreen,
)
from ..prompts import (
    ConfirmScreen,
    _lab_text_access_dialog,
)
from ..steps import run_steps
from .base import (
    WorkspaceBase,
    _SectionOps,
)


class CharacterActions(WorkspaceBase):
    """WorkspaceScreen's actions for the Character sheet: Info,
    Characteristics, Abilities, traits, Health, Arts, Raw Vis, Hermetic
    Background, Known Spells and Inventory."""

    # -- Promote / Demote --

    def action_promote(self) -> None:
        self._change_detail(world.promoted)

    def action_demote(self) -> None:
        self._change_detail(world.demoted)

    def _change_detail(self, step: Any) -> None:
        """More's Promote or Demote: the character's or covenant's detail
        level one step up or down (the core asks first). The sheet is built
        again, since a sketch's tabs are not a full record's."""
        view = self._current_sheet_view()
        record = view.creation_record if view is not None else None
        if not isinstance(record, (Character, Covenant)):
            return
        detail = step(record.detail)
        if detail is None:
            return

        def done(_end: object) -> None:
            if isinstance(record, Character):
                self._commit("section-char-info", tree=True)
                self.call_later(self._show_character, record)
            else:
                self._commit("section-cov-info", tree=True)
                self.call_later(self._show_covenant_detail, record)

        run_steps(self.app, menu_forms.change_detail(self.saga, record, detail), done)

    # -- Traditions --

    def action_edit_traditions(self) -> None:
        """More's Traditions: join or leave non-Hermetic traditions. The
        sheet is built again, since each tradition has a tab."""
        character = self.selected_character
        if character is None:
            return

        def done(_end: object) -> None:
            self._commit("section-char-info", "tab-abilities")
            self.call_later(self._show_character, character)

        run_steps(self.app, menu_forms.character_traditions(self.saga, character), done)

    # -- an apprentice's magic and the Gauntlet (Apprentices) --

    # -- Character Info / Characteristics --

    def _edit_character_info(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            character_forms.apply_character_info(self.saga, character, result)
            self.selected_covenant = self.saga.covenant(character.covenant_id)
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
                character_forms.apply_biographical(character, result)
                self._commit("section-char-biographical")
                # Age (derived from Year Born) lives in the top panel.
                self._refresh_character_section("section-char-info")

        self.app.push_screen(
            FieldsDialog(
                "Edit Biographical Detail",
                character_forms.biographical_fields(
                    character.background,
                    character.description,
                    self.saga.players,
                    may_assign=self._is_storyguide(),
                    academe=disease.on(self.saga),
                ),
                validate=character_forms.biographical_problem,
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
            notes = character_forms.apply_aging(self.saga, character, result)
            if notes:
                self.notify(" ".join(notes), timeout=12)
            self._commit("section-aging", "tab-diary")

        self.app.push_screen(
            FieldsDialog(
                "Edit Aging & Warping",
                character_forms.aging_fields(character.aging, self.saga, character),
            ),
            handle_result,
        )

    # -- Abilities --

    def _core_refreshed(self, section: str) -> tuple[str, ...]:
        if section in (ability_sections := self._ability_sections()):
            return ability_sections
        if section in section_verbs.RAW_VIS_SECTIONS:
            return section_verbs.RAW_VIS_SECTIONS
        return super()._core_refreshed(section)

    def _ability_sections(self) -> tuple[str, ...]:
        """The sections an Ability of the character on show can sit in: the
        Abilities chapter and each of their traditions' chapters."""
        character = self.selected_character
        chapters = traditions.of(character) if character is not None else []
        return (
            "tab-abilities",
            *(traditions.tradition_section(t.id) for t in chapters),
        )

    # -- Personality Traits / Reputations / Wounds / Fatigue --

    def _edit_wounds(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is not None:
                character.wounds = character_forms.apply_wounds(
                    character.wounds, result
                )
                self._commit("section-char-health")

        academe = disease.on(self.saga) or bool(character.wounds.diseases)
        self.app.push_screen(
            FieldsDialog(
                "Edit Wounds",
                character_forms.wounds_fields(character.wounds, academe=academe),
            ),
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
                "Edit Fatigue Level",
                character_forms.fatigue_fields(character.fatigue_level),
            ),
            handle_result,
        )

    # -- Arts (magi only) --

    def _edit_arts(self) -> None:
        character = self.selected_character
        if character is None:
            return

        form = character_forms.arts_form(character)

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                form.apply(values)
                self._commit("section-arts")

        self.app.push_screen(
            EditArtsScreen(
                form,
                character.virtues_flaws,
                note=creation.worksheet_note(character, ARTS),
            ),
            handle_result,
        )

    # -- Raw Vis / Hermetic Background (magi only) --

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
                "Edit Hermetic Background",
                character_forms.hermetic_fields(
                    character.hermetic,
                    mercurian=character_forms.is_mercurian(character),
                ),
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

    def _selected_known_spell(self) -> int | None:
        view = self._character_sheet_view
        return view.selected_known_spell() if view is not None else None

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

    def _character_section_ops(self) -> dict[str, _SectionOps]:
        """a / d / e on the character sheet (see
        WorkspaceScreen._section_ops)."""
        return {
            "section-char-info": _SectionOps(edit=self._edit_character_info),
            "section-char-characteristics": _SectionOps(
                edit=self._edit_characteristics
            ),
            "section-char-biographical": _SectionOps(
                edit=self._edit_biographical_detail
            ),
            "tab-abilities": self._core_ops_of("tab-abilities"),
            **{
                traditions.tradition_section(t.id): self._core_ops_of(
                    traditions.tradition_section(t.id)
                )
                for t in traditions.all_traditions()
            },
            **{
                traditions.effects_section(t.id): _SectionOps(
                    partial(self._core_verb, traditions.effects_section(t.id), "add"),
                    partial(
                        self._core_verb, traditions.effects_section(t.id), "remove"
                    ),
                    partial(self._core_verb, traditions.effects_section(t.id), "edit"),
                )
                for t in traditions.all_traditions()
            },
            **{
                traditions.bonds_section(t.id): _SectionOps(
                    partial(self._core_verb, traditions.bonds_section(t.id), "add"),
                    partial(self._core_verb, traditions.bonds_section(t.id), "remove"),
                    partial(self._core_verb, traditions.bonds_section(t.id), "edit"),
                )
                for t in traditions.all_traditions()
            },
            **{
                traditions.pools_section(t.id): _SectionOps(
                    edit=partial(
                        self._core_verb, traditions.pools_section(t.id), "edit"
                    )
                )
                for t in traditions.all_traditions()
            },
            POWERS_SECTION: _SectionOps(
                partial(self._core_verb, POWERS_SECTION, "add"),
                partial(self._core_verb, POWERS_SECTION, "remove"),
                partial(self._core_verb, POWERS_SECTION, "edit"),
            ),
            CONSTANT_EFFECTS_SECTION: _SectionOps(
                partial(self._core_verb, CONSTANT_EFFECTS_SECTION, "add"),
                partial(self._core_verb, CONSTANT_EFFECTS_SECTION, "remove"),
                partial(self._core_verb, CONSTANT_EFFECTS_SECTION, "edit"),
            ),
            "section-aging": _SectionOps(edit=self._edit_aging),
            # Health has two dialogs behind two Edit buttons (Wounds and
            # Fatigue); 'e' opens Wounds, Fatigue is button-only.
            "section-char-health": _SectionOps(edit=self._edit_wounds),
            "section-arts": _SectionOps(edit=self._edit_arts),
            "section-hermetic-background": _SectionOps(
                edit=self._edit_hermetic_background
            ),
            "section-known-spells": self._core_ops_of("section-known-spells"),
            "section-research-goals": self._core_ops_of("section-research-goals"),
            "section-inventory": self._core_ops_of("section-inventory"),
            "section-raw-vis-hermetic": self._core_ops_of("section-raw-vis-hermetic"),
            "section-raw-vis-inventory": self._core_ops_of("section-raw-vis-inventory"),
            "section-char-season": self._core_ops_of("section-char-season"),
            CHAR_AHEAD_SECTION: self._core_ops_of(CHAR_AHEAD_SECTION),
            "tab-diary": self._core_ops_of("tab-diary"),
        }

    # -- the Theban Tribunal's Byzantine customs --

    def _byzantine_step(self, build: Callable[..., Any], *sections: str) -> None:
        """Run a Byzantine custom's More command on the character on show,
        then save, redraw and say what it did."""
        character = self.selected_character
        if character is None:
            return

        def done(end: object) -> None:
            self._commit(*sections, "tab-diary")
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, build(self.saga, character), done)

    # -- dealing with faeries (RoP: Faerie) --

    # -- the lacuna and the pilgrim (HoH:S, The Church) --

    # -- devotion and the saints (The Church, RoP: The Divine) --

    # -- holy influence and tempers (RoP: The Divine) --

    # -- mystic paths, God's aid, the Font and the Commanding Aura --

    def action_edit_interests(self) -> None:
        """More's Interests: the kinds of deed a person's More offers, or
        what a covenant's sheet leaves out."""
        covenant = self.selected_covenant
        if self.selected_character is None and covenant is not None:
            run_steps(
                self.app,
                interests_forms.covenant_interests_form(self.saga, covenant),
                lambda _end: self._commit(),
            )
            return
        self._byzantine_step(interests_forms.interests_form)

    # -- House Verditius's Hubris and vendettas --

    # -- Hermetic spirit magic and theurgy (The Mysteries Revised Edition) --

    # -- Dream magic and Hermetic sacrifice (The Mysteries Revised Edition) --

    # -- Divination and Hermetic astrology (The Mysteries Revised Edition) --

    # -- House Acclaim and Reputation rolls (HoH:TL, HoH:S, LoH, DE) --

    # -- Philosophic Alchemy's digestions (The Mysteries Revised Edition) --

    # -- The Great Elixir's test (The Mysteries Revised Edition) --

    # -- Gaining and losing Virtues and Flaws in play (Grogs pp. 61-64) --

    # -- A cleric's career (The Church) --

    # -- A Criamon magus's path (Houses of Hermes: Mystery Cults) --
