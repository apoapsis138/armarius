"""WorkspaceScreen's actions for the Creation Worksheet's xp steps: spending a step's xp
on an Ability or Art, changing or taking it back, the Native Language and the sample
childhoods. The worksheet's buttons call these; each saves and refreshes the sheet
below."""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from typing import Any

from ... import catalog, creation, sourcebooks
from ... import covenants as cov_rules
from ... import inhabitants as inh
from ... import spells as spl
from ...markup import escape
from ...models import (
    Character,
    Covenant,
    CovenantSituationDef,
    CreationXp,
    Laboratory,
    Spell,
)
from ...rules import creation_later as later
from ...rules import creation_magus as magus_rules
from ...rules import creation_packages as packages
from ...rules import creation_xp as cx
from ..pickers import RemovalPickerScreen, SpellChooserScreen
from ..prompts import (
    ConfirmScreen,
    InfoScreen,
    _blanks_dialog,
    _buy_specialist_dialog,
    _creation_xp_dialog,
    _gauntlet_conditions_dialog,
    _native_language_dialog,
    _power_level_dialog,
    _spell_level_dialog,
)
from .base import _CHARACTER_REPUTATIONS, _CHARACTER_TRAITS, WorkspaceBase

#: What the xp steps change on the sheet.
XP_SECTIONS = ("tab-abilities", "section-arts")
#: And the spell steps.
SPELL_SECTIONS = ("section-known-spells",)


def _label(entry: CreationXp) -> str:
    return f"{escape(entry.target)}: {entry.xp} xp"


class CreationActions(WorkspaceBase):
    def _spend_creation_xp(
        self,
        character: Character,
        step: str,
        targets: Sequence[str],
        note: str = "",
        title: str = "Spend xp",
    ) -> None:
        def handle_result(result: tuple[str, int] | None) -> None:
            if result is not None:
                target, xp = result
                creation.spend_creation_xp(
                    character, CreationXp(step, target, xp, note)
                )
                self._commit(*XP_SECTIONS)

        self.app.push_screen(_creation_xp_dialog(title, targets), handle_result)

    def _pick_creation_xp(
        self,
        character: Character,
        step: str,
        title: str,
        then: Any,
        *,
        note: str | None = None,
    ) -> None:
        """Ask which of `step`'s entries (`note`'s only, if given), then
        call `then(entry)`."""
        found = [
            x for x in cx.entries(character, step) if note is None or x.note == note
        ]
        if not found:
            self.notify("Nothing spent at this step yet.")
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                then(found[index])

        self.app.push_screen(
            RemovalPickerScreen(title, [_label(x) for x in found]), handle_index
        )

    def _change_creation_xp(
        self,
        character: Character,
        step: str,
        targets: Sequence[str],
        *,
        note: str | None = None,
    ) -> None:
        def edit(entry: CreationXp) -> None:
            def handle_result(result: tuple[str, int] | None) -> None:
                if result is not None:
                    creation.change_creation_xp(character, entry, *result)
                    self._commit(*XP_SECTIONS)

            self.app.push_screen(
                _creation_xp_dialog("Change xp", targets, (entry.target, entry.xp)),
                handle_result,
            )

        self._pick_creation_xp(character, step, "Change which?", edit, note=note)

    def _refund_creation_xp(
        self, character: Character, step: str, *, note: str | None = None
    ) -> None:
        def refund(entry: CreationXp) -> None:
            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    creation.refund_creation_xp(character, entry)
                    self._commit(*XP_SECTIONS)

            self.app.push_screen(
                ConfirmScreen(
                    f"Take back {entry.xp} xp from {escape(entry.target)}?",
                    yes_label="Take back",
                ),
                handle_confirmed,
            )

        self._pick_creation_xp(character, step, "Take back which?", refund, note=note)

    # -- Early Childhood --

    def _set_native_language(self, character: Character) -> None:
        """Choose the Native Language: its 75 childhood xp."""
        native = next(
            (x for x in cx.entries(character, "childhood") if x.note == cx.NATIVE),
            None,
        )

        def handle_result(language: str | None) -> None:
            if language is None:
                return
            if native is None:
                creation.spend_creation_xp(
                    character,
                    CreationXp("childhood", language, cx.NATIVE_XP, cx.NATIVE),
                )
            else:
                creation.change_creation_xp(character, native, language, cx.NATIVE_XP)
            self._commit(*XP_SECTIONS)

        self.app.push_screen(
            _native_language_dialog(native.target if native else ""), handle_result
        )

    def _apply_sample_childhood(self, character: Character) -> None:
        """Spend the 45 childhood xp as one of the sample childhoods,
        replacing what was spent there (the Native Language stays)."""
        childhoods = cx.childhoods_in_play(self.saga)

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._ask_childhood_blanks(character, childhoods[index])

        self.app.push_screen(
            RemovalPickerScreen(
                "Use a sample childhood (replaces the 45 xp)",
                [cx.childhood_label(c) for c in childhoods],
            ),
            handle_index,
        )

    def _ask_blanks(
        self,
        title: str,
        rows: cx.XpRows,
        then: Callable[[list[tuple[str, int]]], None],
    ) -> None:
        """Ask for the names `rows` leave blank ("Area Lore: {area}"), then
        call `then` with the filled-in (Ability, xp)."""
        blanks = cx.template_blanks(rows)

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                then(cx.fill_template(rows, values))

        if not blanks:
            then(list(rows))
            return
        self.app.push_screen(_blanks_dialog(title, blanks), handle_result)

    def _ask_childhood_blanks(
        self, character: Character, childhood: cx.Childhood
    ) -> None:
        def apply(filled: list[tuple[str, int]]) -> None:
            for entry in cx.entries(character, "childhood"):
                if entry.note != cx.NATIVE:
                    creation.refund_creation_xp(character, entry)
            for target, xp in filled:
                creation.spend_creation_xp(
                    character, CreationXp("childhood", target, xp)
                )
            self._commit(*XP_SECTIONS)

        self._ask_blanks(f"{childhood.name} childhood", childhood.xp, apply)

    # -- Grogs training packages --

    def _take_training_package(self, character: Character) -> None:
        """Pick a Grogs training package and its length, fill its blanks,
        and spend its xp (a Later Life quick build)."""
        choices = [
            (package, years)
            for package in packages.PACKAGES
            for years, rows in ((5, package.five), (3, package.three))
            if rows
        ]

        def handle_index(index: int | None) -> None:
            if index is None:
                return
            package, years = choices[index]
            note = packages.Taken(
                package.name, years, packages.next_time(character, package.name)
            ).note

            def apply(filled: list[tuple[str, int]]) -> None:
                for target, xp in filled:
                    creation.spend_creation_xp(
                        character, CreationXp("package", target, xp, note)
                    )
                self._commit(*XP_SECTIONS)

            rows = tuple(packages.package_xp(package, years))
            self._ask_blanks(f"{package.name} ({years} years)", rows, apply)

        self.app.push_screen(
            RemovalPickerScreen(
                "Take a training package",
                [packages.package_label(p, y) for p, y in choices],
            ),
            handle_index,
        )

    def _drop_training_package(self, character: Character) -> None:
        """Take back every xp of one package taken."""
        found = packages.taken(character)

        def handle_index(index: int | None) -> None:
            if index is None:
                return
            note = found[index].note
            for entry in [
                x for x in cx.entries(character, "package") if x.note == note
            ]:
                creation.refund_creation_xp(character, entry)
            self._commit(*XP_SECTIONS)

        self.app.push_screen(
            RemovalPickerScreen(
                "Drop which package?",
                [f"{escape(t.name)} ({t.years} years)" for t in found],
            ),
            handle_index,
        )

    # -- Later Life --

    def _record_free_scores(self, character: Character) -> None:
        """The free first 5 xp in each Supernatural Ability a Virtue grants."""
        for name in later.free_scores_missing(character):
            creation.spend_creation_xp(
                character,
                CreationXp("free", name, later.FREE_SUPERNATURAL_XP),
            )
        self._commit(*XP_SECTIONS)

    # -- spells learned at creation --

    def _learn_creation_spell(self, character: Character, step: str) -> None:
        """Pick a spell to learn at `step` ("apprenticeship_spells" or
        "gauntlet_spells"); a General-level spell asks at what level."""

        def handle_spell(spell_id: str | None) -> None:
            spell = spl.find_spell(self.saga, spell_id)
            if spell is not None:
                self._learn_spell_at_its_level(character, step, spell)

        self.app.push_screen(
            SpellChooserScreen(
                self.saga,
                exclude={k.spell_id for k in character.spells_known},
                title=f"A spell {escape(character.name)} learns",
                details=lambda spell: (
                    f"[b]{escape(character.name)}'s Lab Total for it (aura 3):[/] "
                    f"{magus_rules.spell_cap(self.saga, character, spell)}"
                ),
            ),
            handle_spell,
        )

    def _learn_spell_at_its_level(
        self, character: Character, step: str, spell: Spell
    ) -> None:
        """Learn `spell` at `step` at its level, asking for one if it's a
        General-level spell."""

        def learn(level: int | None) -> None:
            if level is not None:
                creation.learn_creation_spell(character, step, spell.id, level)
                self._commit(*SPELL_SECTIONS)

        if spell.level is not None:
            learn(spell.level)
            return
        self.app.push_screen(_spell_level_dialog(spell.name), learn)

    def _show_creation_spell(self, character: Character, step: str) -> None:
        """A learned spell's full details (its Arts, Range, Duration,
        Target, description) and the magus's Lab Total for it."""
        found = cx.entries(character, step)

        def spell_of(entry: CreationXp) -> Spell | None:
            return spl.find_spell(self.saga, entry.target)

        def handle_index(index: int | None) -> None:
            if index is None:
                return
            spell = spell_of(found[index])
            if spell is None:
                return
            cap = magus_rules.spell_cap(self.saga, character, spell)
            text = (
                spl.detail_text(self.saga, spell)
                + f"\n\n[b]Learned at level:[/] {found[index].xp}"
                + f"\n[b]{escape(character.name)}'s Lab Total for it (aura 3):[/] {cap}"
            )
            self.app.push_screen(InfoScreen(escape(spell.name), text))

        labels = [
            escape(spell.name) if (spell := spell_of(x)) else escape(x.target)
            for x in found
        ]
        self.app.push_screen(
            RemovalPickerScreen("Show which spell?", labels), handle_index
        )

    def _forget_creation_spell(self, character: Character, step: str) -> None:
        found = cx.entries(character, step)
        if not found:
            self.notify("No spells learned at this step yet.")
            return

        def name(entry: CreationXp) -> str:
            spell = spl.find_spell(self.saga, entry.target)
            return escape(spell.name if spell else entry.target)

        def handle_index(index: int | None) -> None:
            if index is None:
                return
            entry = found[index]

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    creation.forget_creation_spell(character, entry)
                    self._commit(*SPELL_SECTIONS)

            self.app.push_screen(
                ConfirmScreen(f"Forget {name(entry)}?", yes_label="Forget"),
                handle_confirmed,
            )

        self.app.push_screen(
            RemovalPickerScreen(
                "Forget which spell?",
                [f"{name(x)} (level {x.xp})" for x in found],
            ),
            handle_index,
        )

    # -- Years past Gauntlet and pre-play aging --

    def _edit_gauntlet_conditions(self, character: Character) -> None:
        conditions = character.creation_conditions

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                for key, value in values.items():
                    setattr(conditions, key, value)
                self._commit()

        self.app.push_screen(_gauntlet_conditions_dialog(conditions), handle_result)

    def _roll_pre_play_aging(self, character: Character) -> None:
        """The aging rolls a character older than 35 makes before play,
        after asking (they can't be taken back)."""
        due = magus_rules.aging_due(self.saga, character)
        if not due:
            self.notify("No aging rolls to make.")
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if not confirmed:
                return
            summaries = creation.pre_play_aging(self.saga, character, random.Random())
            self._commit("section-aging", "tab-diary", "section-char-characteristics")
            self.notify(escape("; ".join(summaries)), timeout=12)

        self.app.push_screen(
            ConfirmScreen(
                f"Roll {due} aging roll(s) for {escape(character.name)}? "
                "Each is written in the Diary and can't be undone.",
                yes_label="Roll",
                yes_variant="primary",
            ),
            handle_confirmed,
        )

    # -- Finishing Touches --

    def _add_character_trait(self) -> None:
        self._add_trait(_CHARACTER_TRAITS)

    def _add_character_reputation(self) -> None:
        self._add_trait(_CHARACTER_REPUTATIONS)

    # -- New Covenant --

    def _choose_power_level(self, covenant: Covenant) -> None:
        def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                covenant.power_level = values["power_level"]
                covenant.build_points_budget = values["build_points_budget"]
                covenant.magi_without_lab = values["magi_without_lab"]
                covenant.year_founded = values["year_founded"]
                self._commit("section-cov-info")

        self.app.push_screen(_power_level_dialog(covenant), handle_result)

    def _use_covenant_situation(self, covenant: Covenant) -> None:
        """Add one of the books' Covenant Situations: a
        ready-made set of Boons and Hooks, on top of any it already has."""
        books = sourcebooks.saga_books(self.saga)
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        situations = [
            s
            for s in catalog.load_covenant_situation_catalog()
            if sourcebooks.in_play(s.source, books)
        ]

        def label(situation: CovenantSituationDef) -> str:
            hooks, boons = cov_rules.situation_points(situation, by_id)
            book = sourcebooks.SOURCEBOOKS.get(situation.source, situation.source)
            return (
                f"{escape(situation.name)}  [dim]{hooks:g} Hook, {boons:g} Boon "
                f"points; {escape(book)}[/]"
            )

        def handle_index(index: int | None) -> None:
            if index is None:
                return
            situation = situations[index]
            added = cov_rules.situation_instances(situation)
            message = (
                f"Add {escape(situation.name)}'s {len(added)} Boons and Hooks to "
                f"{escape(covenant.name)}? {escape(situation.description)}"
            )
            if covenant.boons_hooks:
                message += " The ones it already has stay."
            if situation.notes:
                message += f"\n\n[dim]{escape(situation.notes)}[/]"

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    covenant.boons_hooks.extend(added)
                    self._commit("section-cov-boons", "section-cov-hooks")

            self.app.push_screen(
                ConfirmScreen(message, yes_label="Add", yes_variant="primary"),
                handle_confirmed,
            )

        self.app.push_screen(
            RemovalPickerScreen(
                "Use a Covenant Situation", [label(s) for s in situations]
            ),
            handle_index,
        )

    def _buy_specialist(self, covenant: Covenant) -> None:
        """Buy an NPC specialist or teacher with Build Points: a new line on
        the Inhabitants tab. (A grog or companion built as a character
        costs nothing; assign them there as usual.)"""

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                inh.save_entry(covenant, "specialist", None, values)
                self._commit("section-inh-specialist")

        self.app.push_screen(_buy_specialist_dialog(), handle_result)

    # -- New Laboratory --

    def _toggle_starting_lab(self, lab: Laboratory) -> None:
        """Whether the lab is one of its covenant's starting labs (paid for
        from the covenant's Build Points)."""
        lab.starting = not lab.starting
        self._commit("section-lab-identity")
