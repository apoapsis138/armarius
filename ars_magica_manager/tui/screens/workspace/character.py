"""The Character sheet: Info, Characteristics, Abilities, traits, Health, Arts,
Raw Vis, Hermetic Background, Known Spells, Inventory, This Season and the
Diary."""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from typing import Any

from .... import (
    aging_due,
    creation,
    disputations,
    guest_stays,
    health,
    labor,
    melee_events,
    section_verbs,
    selling,
    session_end,
    tourney_season,
    traditions,
    world,
)
from .... import baraka as baraka_forms
from .... import devotion as devotion_forms
from .... import mystic_paths as mystic_forms
from .... import spells as spl
from .... import theban_customs as byzantine
from ....arts import ARTS
from ....commands import Command
from ....forms import acclaim as acclaim_forms
from ....forms import agents as agent_forms
from ....forms import apothecary as apothecary_forms
from ....forms import beast as beast_forms
from ....forms import boost as boost_forms
from ....forms import careers as career_forms
from ....forms import certamen_duel as certamen_forms
from ....forms import character as character_forms
from ....forms import church as church_forms
from ....forms import covers as cover_forms
from ....forms import craft_magic as craft_forms
from ....forms import criamon as criamon_forms
from ....forms import faerie_dealings as faerie_forms
from ....forms import galdor as galdor_forms
from ....forms import gauntlet as gauntlet_forms
from ....forms import goetic as goetic_forms
from ....forms import grog_story as grog_story_forms
from ....forms import grogs as grog_forms
from ....forms import hedge_cast as hedge_cast_forms
from ....forms import holy_influence as holy_influence_forms
from ....forms import hubris as hubris_forms
from ....forms import interests as interests_forms
from ....forms import lacuna as lacuna_forms
from ....forms import menu as menu_forms
from ....forms import mystery_cults as cult_forms
from ....forms import pilgrimage as pilgrimage_forms
from ....forms import season as season_forms
from ....forms import sin as sin_forms
from ....forms import tmre_alchemy as tmre_alchemy_forms
from ....forms import tmre_divination as tmre_divination_forms
from ....forms import tmre_dreams as tmre_dream_forms
from ....forms import tmre_spirits as tmre_spirit_forms
from ....forms import trait_roll as trait_roll_forms
from ....forms import tunnel as tunnel_forms
from ....forms import turbulence as turbulence_forms
from ....forms import twilight as twilight_forms
from ....forms import vf_change as vf_change_forms
from ....forms import whereabouts as whereabouts_forms
from ....markup import escape
from ....models import (
    Character,
    Covenant,
    HermeticBackground,
    LabTextAccess,
    Saga,
    Spell,
)
from ....rules import disease, galdor
from ....sections import (
    AGENTS_SECTION,
    CHAR_AHEAD_SECTION,
    CONSTANT_EFFECTS_SECTION,
    FAITH_SECTION,
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

    def _agent_step(
        self, build: Callable[[Character, int], Any], *sections: str
    ) -> None:
        """Run a More command on the Agents list's chosen agent, then save,
        redraw the list (and `sections`) and say what it did."""
        character = self.selected_character
        view = self._current_sheet_view()
        row = view.section_row(AGENTS_SECTION) if view is not None else None
        if character is None or row is None:
            return

        def done(end: object) -> None:
            self._commit(AGENTS_SECTION, *sections)
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, build(character, row), done)

    def action_impress_agent(self) -> None:
        """More's Impress on the chosen potential agent."""
        self._agent_step(partial(agent_forms.impress, self.saga))

    def action_spend_agency_xp(self) -> None:
        """More's Spend Agency Experience on the chosen agent."""
        self._agent_step(agent_forms.spend)

    def action_set_agent_task(self) -> None:
        """More's Set a Task for the chosen agent."""
        self._agent_step(partial(agent_forms.set_task, self.saga))

    def action_resolve_agent_task(self) -> None:
        """More's Resolve the Task for the chosen agent: his own roll, kept
        in the Diary."""
        self._agent_step(partial(agent_forms.resolve, self.saga), "tab-diary")

    def action_take_harm(self) -> None:
        """More's Take Harm on Health: an injury, poison, disease or
        deprivation, rolled and kept in the Diary."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            health.take_harm_form(self.saga, character),
            lambda _end: self._commit("section-char-health"),
        )

    def action_place_aging_points(self) -> None:
        """More's Place Aging Points on Aging & Warping: those a disease
        Crisis left, each in a Characteristic chosen."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            aging_due.character_form(self.saga, character),
            lambda _end: self._commit("section-aging", "section-char-characteristics"),
        )

    def action_boost_spell(self) -> None:
        """More's Boost a Spell on Known Spells: the pawns and botch dice a
        boost takes, worked out (a calculator: it changes nothing)."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app, boost_forms.boost_form(self.saga, character), lambda _e: None
        )

    def action_hedge_cast(self) -> None:
        """More's Cast a Power: a hedge tradition's casting rolled, kept in
        the Diary."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            hedge_cast_forms.cast_form(self.saga, character),
            lambda end: self._commit_told(end, "section-aging", "tab-diary"),
        )

    def action_galdor_conjure(self) -> None:
        """More's Conjure a Spirit: a song rolled, kept in the Diary."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            galdor_forms.conjure_form(self.saga, character),
            lambda end: self._commit_told(
                end, "section-aging", "section-char-health", "tab-diary"
            ),
        )

    def action_galdor_bargain(self) -> None:
        """More's Bargain with a Lord: a deal kept with the tradition's
        bound beings."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            galdor_forms.bargain_form(self.saga, character),
            lambda end: self._commit_told(
                end, traditions.bonds_section(galdor.TRADITION_ID), "tab-diary"
            ),
        )

    def action_galdor_bind(self) -> None:
        """More's Bind an Item: a spirit bound, the item kept with the
        tradition's effects."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            galdor_forms.bind_form(self.saga, character),
            lambda end: self._commit_told(
                end,
                traditions.effects_section(galdor.TRADITION_ID),
                "section-aging",
                "tab-diary",
            ),
        )

    def action_trait_roll(self) -> None:
        """More's Roll on Personality Traits: a trait roll, resisting
        mental influence or the familiar's rescue, with the Silver Cord."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app, trait_roll_forms.roll_form(self.saga, character), lambda _e: None
        )

    def action_disguise_roll(self) -> None:
        """More's Disguise Roll on Covers: a cover's Disguise roll worked
        out and rolled (shown, not kept)."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            cover_forms.disguise_form(self.saga, character),
            lambda _e: None,
        )

    def action_resolve_twilight(self) -> None:
        """More's Resolve Twilight on Aging & Warping: the storyguide's
        choice of its effects, applied and kept in the Diary."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            twilight_forms.resolve_twilight_form(self.saga, character),
            lambda _end: self._commit("section-aging"),
        )

    def action_end_session(self) -> None:
        """More's End of Session on Reputations: Confidence Points and
        Reputation deeds, kept in the Diary."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            session_end.end_session_form(self.saga, character),
            lambda _end: self._commit("section-reputations", "section-char-info"),
        )

    def action_tourney_season(self) -> None:
        """More's Tournament on Reputations: a season on the tourney circuit
        counted toward his Prudhomme Reputation, kept in the Diary."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            tourney_season.tourney_form(self.saga, character),
            lambda _end: self._commit("section-reputations", "tab-diary"),
        )

    def action_melee_event(self) -> None:
        """More's Melee Event on Reputations: a roll on the Melee Events
        Table, and the ransom fair from the knight it presents."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            melee_events.melee_form(self.saga, character),
            lambda _end: self._commit("section-reputations", "tab-diary"),
        )

    def action_labor_story(self) -> None:
        """More's Labor Points from a Story on This Season: a story's award
        in seasons' worth of Labor Points, kept in the Diary."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            labor.story_form(self.saga, character),
            lambda _end: self._commit("section-char-season", "tab-diary"),
        )

    def action_grog_story_xp(self) -> None:
        """More's Story Experience on a grog's This Season: the story's
        xp at once, counted against the yearly update."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            grog_story_forms.story_form(self.saga, character),
            lambda _end: self._commit("section-char-season", "tab-diary"),
        )

    def action_plan_copying(self) -> None:
        """More's Plan Copying on a grog's This Season: a season of copying
        a book or Lab Texts, planned like anyone's."""
        self._grog_copying(season_forms.copying_form)

    def action_clear_copying(self) -> None:
        """More's Clear Copying: drop a grog's season of copying."""
        self._grog_copying(season_forms.clear_copying_form)

    def _grog_copying(self, build: Callable[[Saga, Character | None], Command]) -> None:
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            build(self.saga, character),
            lambda _end: self._commit("section-char-season"),
        )

    def action_invest_labor(self) -> None:
        """More's Invest Time or Money on This Season: a merchant's
        investment of Labor Points or money, kept in the Diary."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            labor.invest_form(self.saga, character),
            lambda _end: self._commit(
                "section-char-season",
                "section-reputations",
                "section-inventory",
                "tab-diary",
            ),
        )

    def action_sell_goods(self) -> None:
        """More's Sell Finished Goods on This Season: the haggling roll for
        a craftsman's sale, kept in the Diary."""
        character = self.selected_character
        if character is None:
            return

        def done(end: object) -> None:
            self._commit("section-char-season", "tab-diary")
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, selling.sell_form(self.saga, character), done)

    def action_make_ligature(self) -> None:
        """More's Make a Ligature beside Abilities: a scholar's ligature
        roll, kept in the Diary."""
        self._apothecary_step(apothecary_forms.ligature_form, "section-char-season")

    def action_apothecary_store(self) -> None:
        """More's Apothecary's Store on This Season: a search for an
        ingredient or preserving one, kept in the Diary."""
        self._apothecary_step(apothecary_forms.store_form, "section-char-season")

    def action_artist_career(self) -> None:
        """More's An Artist's Career beside Abilities: a sponsor sought or
        kept, a performance, an Artist Reputation deed, kept in the Diary."""
        self._apothecary_step(career_forms.artist_form, "section-char-season")

    def action_scholar_career(self) -> None:
        """More's A Scholar's Career beside Abilities: a place at a school
        sought, or an Academic Reputation deed, kept in the Diary."""
        self._apothecary_step(career_forms.scholar_form, "section-char-season")

    def _apothecary_step(self, form: Callable[..., Any], section: str) -> None:
        character = self.selected_character
        if character is None:
            return

        def done(end: object) -> None:
            self._commit(section, "tab-diary")
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, form(self.saga, character), done)

    def action_command_beast(self) -> None:
        """More's Command the Beast on a tamed animal's Personality Traits:
        the command's roll and any Loyalty test."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            beast_forms.command_form(self.saga, character),
            lambda _end: self._commit("section-personality-traits"),
        )

    def _covenfolk_step(self, build: Callable[..., Any], *sections: str) -> None:
        """Run a More command on the grog on show, then save, redraw and
        say what it did."""
        character = self.selected_character
        if character is None:
            return

        def done(end: object) -> None:
            self._commit(*sections, tree=True)
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, build(self.saga, character), done)

    def action_discipline_grog(self) -> None:
        """More's Reward or Punish on a grog: his record and Diary, wounds
        and Fatigue, and the covenant's Loyalty."""
        self._covenfolk_step(
            grog_forms.discipline_form,
            "section-personality-traits",
            "section-char-health",
            "section-char-info",
        )

    def action_grog_pension(self) -> None:
        """More's Pension on a grog: he retires, or his widow is pensioned."""
        self._covenfolk_step(grog_forms.pension_form, "section-char-info")

    def action_craft_by_magic(self) -> None:
        """More's Craft by Magic on Known Spells: the calculator, and a roll
        of it; nothing is kept."""
        character = self.selected_character
        if character is None:
            return

        def done(end: object) -> None:
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, craft_forms.craft_form(self.saga, character), done)

    def action_indulge_sin(self) -> None:
        """More's Confidence through Sin on Personality Traits: the point
        kept, and a ceremony's Warping Point."""
        character = self.selected_character
        if character is None:
            return

        def done(end: object) -> None:
            self._commit("section-char-info", "section-aging", "tab-diary")
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, sin_forms.sin_form(self.saga, character), done)

    def action_infernal_influence(self) -> None:
        """More's Infernal Influence on Personality Traits: the roll, kept
        in the Diary."""
        character = self.selected_character
        if character is None:
            return

        def done(end: object) -> None:
            self._commit("section-char-info", "tab-diary")
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, sin_forms.influence_form(self.saga, character), done)

    def action_ars_goetia(self) -> None:
        """More's Ars Goetia: a Goetic Art's total and a roll of it; nothing
        is kept."""
        character = self.selected_character
        if character is None:
            return

        def done(end: object) -> None:
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, goetic_forms.goetic_form(self.saga, character), done)

    # -- an apprentice's magic and the Gauntlet (Apprentices) --

    def _apprentice_step(
        self, form: Command, *sections: str, tree: bool = False
    ) -> None:
        def done(end: object) -> None:
            self._commit(*sections, "tab-diary", tree=tree)
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, form, done)

    def action_turbulence(self) -> None:
        """More's Turbulence: the rolls to incur and control one, kept in
        the Diary (and on a laboratory season's Assist plan)."""
        character = self.selected_character
        if character is None:
            return
        self._apprentice_step(
            turbulence_forms.turbulence_form(self.saga, character),
            "section-char-info",
            "section-char-season",
        )

    def action_gauntlet(self) -> None:
        """More's Gauntlet on an apprentice; passed, he becomes a magus."""
        character = self.selected_character
        if character is None:
            return
        self._apprentice_step(
            gauntlet_forms.gauntlet_form(self.saga, character),
            "section-char-info",
            "section-vf-virtues",
            "section-vf-flaws",
            tree=True,
        )

    def action_lose_the_gift(self) -> None:
        """More's Lose the Gift: lost for good, or suppressed."""
        character = self.selected_character
        if character is None:
            return
        self._apprentice_step(
            gauntlet_forms.lose_gift_form(self.saga, character),
            "section-char-info",
            "section-vf-virtues",
            "section-vf-flaws",
        )

    def action_learn_cantation(self) -> None:
        """More's Learn a Cantation on Known Spells (a saga option)."""
        character = self.selected_character
        if character is None:
            return
        self._apprentice_step(
            gauntlet_forms.cantation_form(self.saga, character),
            "section-known-spells",
        )

    def action_recovery_roll(self) -> None:
        """More's Recovery Roll on Health: a roll for each wound now."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            health.recovery_form(self.saga, character),
            lambda _end: self._commit("section-char-health"),
        )

    def action_disputatio(self) -> None:
        """More's Disputatio: a schoolmen's debate with another character,
        kept in both Diaries."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            disputations.disputatio_form(self.saga, character),
            lambda _end: self._commit("section-char-info"),
        )

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

    def action_theban_letter(self) -> None:
        """More's Hermetic Letter: composing or reading a rhetorical letter."""
        self._byzantine_step(byzantine.letter_form)

    def action_invoke_oath(self) -> None:
        """More's Invoke a Broken Oath: the Oath Invocation roll, and the
        malediction it lays."""
        self._byzantine_step(
            byzantine.oath_form, "section-vf-virtues", "section-vf-flaws"
        )

    def action_make_greek_fire(self) -> None:
        """More's Make Greek Fire: a season's botch roll."""
        self._byzantine_step(byzantine.greek_fire_form)

    def action_paint_icon(self) -> None:
        """More's Paint an Icon: an eikon for a church's Relics."""
        self._byzantine_step(byzantine.icon_form)

    def action_venerate_icon(self) -> None:
        """More's Venerate an Icon: its bonus, and in an emergency a roll
        and a Fatigue level."""
        self._byzantine_step(byzantine.venerate_form, "section-char-health")

    def action_mothers_curse(self) -> None:
        """More's A Mother's Curse: a Lesser Malediction on the sheet."""
        self._byzantine_step(
            byzantine.curse_form, "section-vf-virtues", "section-vf-flaws"
        )

    # -- dealing with faeries (RoP: Faerie) --

    def action_ars_fabulosa(self) -> None:
        """More's Ars Fabulosa: a bargaining power's roll, kept in the
        Diary, its Fatigue level and the Traits' experience on the sheet."""
        self._byzantine_step(
            faerie_forms.ars_fabulosa_form,
            "section-char-health",
            "section-personality-traits",
        )

    def action_faerie_bargain(self) -> None:
        """More's A Faerie Bargain: how it ended, kept in the Diary, and
        the Sympathy Trait it moves or the -3 one it gives."""
        self._byzantine_step(
            faerie_forms.faerie_bargain_form, "section-personality-traits"
        )

    def action_faerie_offer(self) -> None:
        """More's An Offer to Faerie: the roll, kept in the Diary, and its
        Long-Term Fatigue level."""
        self._byzantine_step(faerie_forms.faerie_offer_form, "section-char-health")

    # -- the lacuna and the pilgrim (HoH:S, The Church) --

    def action_cast_in_lacuna(self) -> None:
        """More's Cast in a Lacuna on Known Spells: the calculator, and a
        roll of it; nothing is kept."""
        character = self.selected_character
        if character is None:
            return

        def done(end: object) -> None:
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, lacuna_forms.lacuna_form(self.saga, character), done)

    def action_pilgrimage(self) -> None:
        """More's Pilgrimage on This Season: a pilgrimage begun, an element
        overcome or failed, or its aim claimed, kept in the Diary."""
        self._byzantine_step(
            pilgrimage_forms.pilgrimage_form,
            "section-char-season",
            "section-vf-virtues",
            "section-vf-flaws",
            "section-personality-traits",
        )

    # -- devotion and the saints (The Church, RoP: The Divine) --

    def action_invoke_saint(self) -> None:
        """More's Invoke a Saint: the roll, kept in the Diary."""
        self._byzantine_step(devotion_forms.invoke_form, FAITH_SECTION)

    def action_threaten_saint(self) -> None:
        """More's Threaten a Saint: the roll and the Confidence spent."""
        self._byzantine_step(
            devotion_forms.threaten_form, FAITH_SECTION, "section-personality-traits"
        )

    def action_invoke_baraka(self) -> None:
        """More's Invoke Baraka: the roll, kept in the Diary."""
        self._byzantine_step(baraka_forms.baraka_form)

    def action_hajj(self) -> None:
        """More's The Hajj: Pious +3 and 3 Faith Points."""
        self._byzantine_step(
            baraka_forms.hajj_form,
            FAITH_SECTION,
            "section-personality-traits",
            "section-char-info",
        )

    def action_patron_saint(self) -> None:
        """More's Patron Saint: the saint he calls on as his own."""
        self._byzantine_step(devotion_forms.patron_form, FAITH_SECTION)

    def action_devotion_points(self) -> None:
        """More's Devotion Points: a Devotion begun or raised."""
        self._byzantine_step(
            devotion_forms.points_form, FAITH_SECTION, "section-char-season"
        )

    def action_act_of_piety(self) -> None:
        """More's Indulgence, Vigil or Fast: the Faith, Confidence, Piety
        and Fatigue each brings."""
        self._byzantine_step(
            devotion_forms.piety_form,
            "section-char-health",
            "section-personality-traits",
            "section-reputations",
        )

    # -- holy influence and tempers (RoP: The Divine) --

    def action_holy_influence(self) -> None:
        """More's Holy Influence in the Faith section: the roll, kept in
        the Diary."""
        self._byzantine_step(
            holy_influence_forms.holy_influence_form, "section-char-info"
        )

    # -- mystic paths, God's aid, the Font and the Commanding Aura --

    def action_mystic_path(self) -> None:
        """More's Mystic Path: the path followed or left, in the Diary."""
        self._byzantine_step(
            mystic_forms.mystic_path_form, FAITH_SECTION, "section-char-season"
        )

    def action_spiritual_path(self) -> None:
        """More's Spiritual Path: a path begun, a Quest Component counted,
        or its Revelation claimed."""
        self._byzantine_step(
            mystic_forms.spiritual_path_form,
            "section-char-season",
            "section-char-info",
            "section-vf-virtues",
            "section-vf-flaws",
        )

    def action_monistic_revelation(self) -> None:
        """More's Monistic Revelation: the integration roll and what it
        brings."""
        self._byzantine_step(
            mystic_forms.monistic_revelation_form,
            "section-vf-virtues",
            "section-char-season",
        )

    def action_gods_aid(self) -> None:
        """More's Invoke God's Aid: the prayer's roll and the point spent."""
        self._byzantine_step(mystic_forms.gods_aid_form, "section-char-info")

    def action_experiment_script(self) -> None:
        """More's Experiment on a Script on a Mystagogue's record."""
        self._byzantine_step(cult_forms.mystagogue_experiment)

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

    def action_font_of_knowledge(self) -> None:
        """More's Font of Knowledge: the roll, kept in the Diary."""
        self._byzantine_step(mystic_forms.font_form)

    def action_commanding_aura(self) -> None:
        """More's Commanding Aura: withdrawn until penance, or restored."""
        self._byzantine_step(mystic_forms.commanding_aura_form, "section-char-health")

    # -- House Verditius's Hubris and vendettas --

    def action_verditius_hubris(self) -> None:
        """More's Hubris: its experience, a vendetta refused or resisted."""
        self._byzantine_step(
            hubris_forms.hubris_form,
            "section-personality-traits",
            "section-reputations",
        )

    # -- Hermetic spirit magic and theurgy (The Mysteries Revised Edition) --

    def action_spirits_and_names(self) -> None:
        """More's Spirits and Names: a working's totals and a roll of it;
        nothing is kept."""
        character = self.selected_character
        if character is None:
            return

        def done(end: object) -> None:
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, tmre_spirit_forms.spirits_form(self.saga, character), done)

    # -- Dream magic and Hermetic sacrifice (The Mysteries Revised Edition) --

    def action_dream_working(self) -> None:
        """More's Dream Working: a dream traveler's roll, kept in the Diary."""
        self._byzantine_step(tmre_dream_forms.dream_form, "section-known-spells")

    def action_whereabouts(self) -> None:
        """More's Current Location on Casting Scores: the aura he is in now."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            whereabouts_forms.where_form(self.saga, character),
            lambda _end: self._commit("section-casting"),
        )

    def action_guest_stay(self) -> None:
        """More's Stay as Guest on Casting Scores: a stay at another
        covenant."""
        character = self.selected_character
        if character is None:
            return
        run_steps(
            self.app,
            guest_stays.stay_form(self.saga, character),
            lambda _end: self._commit("section-casting"),
        )

    def action_certamen_duel(self) -> None:
        """More's Certamen: a duel with another magus, played out."""
        self._byzantine_step(certamen_forms.duel_form, "section-known-spells")

    def action_hermetic_sacrifice(self) -> None:
        """More's Hermetic Sacrifice: the vis a sacrifice stands in for, kept
        in the Diary."""
        self._byzantine_step(tmre_dream_forms.sacrifice_form, "section-known-spells")

    # -- Divination and Hermetic astrology (The Mysteries Revised Edition) --

    def action_tmre_divination(self) -> None:
        """More's Divination: a divination rolled, kept in the Diary."""
        self._byzantine_step(tmre_divination_forms.divination_form)

    def action_tmre_astrology(self) -> None:
        """More's Astrology: a horoscope or reckoning rolled, kept in the
        Diary."""
        self._byzantine_step(tmre_divination_forms.astrology_form)

    # -- House Acclaim and Reputation rolls (HoH:TL, HoH:S, LoH, DE) --

    def action_house_acclaim(self) -> None:
        """More's House Acclaim: an award or a roll, kept in the Diary."""
        self._byzantine_step(acclaim_forms.acclaim_form, "section-reputations")

    def action_reputation_roll(self) -> None:
        """More's Reputation Roll: has someone heard of it, kept in the
        Diary."""
        self._byzantine_step(acclaim_forms.roll_form)

    # -- Philosophic Alchemy's digestions (The Mysteries Revised Edition) --

    def action_philosophic_alchemy(self) -> None:
        """More's Philosophic Alchemy on This Season: a digestion settled
        beside his other work, or abandoned; kept in the Diary."""
        self._apothecary_step(tmre_alchemy_forms.digestion_form, "section-char-season")

    # -- The Great Elixir's test (The Mysteries Revised Edition) --

    def action_great_elixir(self) -> None:
        """More's Test the Great Elixir on Aging & Warping: the potion
        drunk and tested, kept in the Diary."""
        self._apothecary_step(tmre_alchemy_forms.great_elixir_form, "section-aging")

    # -- Gaining and losing Virtues and Flaws in play (Grogs pp. 61-64) --

    def action_change_virtues_flaws(self) -> None:
        """More's Gain or Lose in Play on Virtues & Flaws: a Virtue or Flaw
        gained, lost, or exchanged, kept in the Diary."""
        self._byzantine_step(
            vf_change_forms.change_form,
            "section-vf-virtues",
            "section-vf-flaws",
            "section-char-characteristics",
        )

    # -- A cleric's career (The Church) --

    def action_perform_exorcism(self) -> None:
        """More's Perform an Exorcism on Holy Orders: the roll, said."""
        self._byzantine_step(church_forms.exorcism_step)

    # -- A Criamon magus's path (Houses of Hermes: Mystery Cults) --

    def action_follow_avenue(self) -> None:
        """More's Follow an Avenue on the path: the Initiation season that
        follows it, planned."""
        self._byzantine_step(
            criamon_forms.avenue_step,
            "section-char-criamon-path",
            "section-char-ahead",
            "tab-planning",
        )

    def action_open_tunnel(self) -> None:
        """More's Open a Tunnel on Known Spells (Hermetic Projects): the
        calculator, and Cast's roll of the tunnel; nothing is kept."""
        character = self.selected_character
        if character is None:
            return

        def done(end: object) -> None:
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, tunnel_forms.tunnel_form(self.saga, character), done)
