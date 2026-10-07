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
from ..forms import _buy_specialist_dialog
from ..pickers import RemovalPickerScreen, SpellChooserScreen
from ..prompts import (
    ConfirmScreen,
    _blanks_dialog,
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


class CreationActions(WorkspaceBase):
    def _spend_creation_xp(
        self,
        character: Character,
        step: str,
        targets: Sequence[str],
        note: str = "",
        title: str = "Spend xp",
    ) -> None:
        """Spend some of `step`'s pool xp on an Ability or Art (and give an
        Ability its Specialty)."""

        def handle_result(result: tuple[str, int, str] | None) -> None:
            if result is not None:
                target, xp, specialty = result
                creation.spend_creation_xp(
                    character, CreationXp(step, target, xp, note)
                )
                creation.set_specialty(character, target, specialty)
                self._commit(*XP_SECTIONS)

        self.app.push_screen(
            _creation_xp_dialog(title, targets, saga=self.saga, character=character),
            handle_result,
        )

    def _change_creation_entry(
        self, character: Character, entry: CreationXp, targets: Sequence[str]
    ) -> None:
        """Change what `entry` spent its pool xp on, or how much (the xp it
        gained comes off first, so an Affinity's half again is undone
        exactly)."""

        def handle_result(result: tuple[str, int, str] | None) -> None:
            if result is not None:
                target, xp, specialty = result
                creation.change_creation_xp(character, entry, target, xp)
                creation.set_specialty(character, target, specialty)
                self._commit(*XP_SECTIONS)

        self.app.push_screen(
            _creation_xp_dialog(
                "Change xp",
                targets,
                (entry.target, entry.xp),
                saga=self.saga,
                character=character,
                replacing=entry,
            ),
            handle_result,
        )

    def _refund_creation_entry(self, character: Character, entry: CreationXp) -> None:
        """Take `entry`'s pool xp back, after asking: the xp it gained comes
        off its Ability or Art."""

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                creation.refund_creation_xp(character, entry)
                self._commit(*XP_SECTIONS)

        gained = creation.gained_xp(entry)
        also = f" ({gained} xp comes off it)" if gained != entry.xp else ""
        self.app.push_screen(
            ConfirmScreen(
                f"Take back the {entry.xp} xp spent on {escape(entry.target)}?{also}",
                yes_label="Take back",
            ),
            handle_confirmed,
        )

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

    def _drop_training_package(self, character: Character, note: str) -> None:
        """Take back every xp of the package taken as `note`, after asking."""
        taken = next((t for t in packages.taken(character) if t.note == note), None)
        if taken is None:
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if not confirmed:
                return
            for entry in [
                x for x in cx.entries(character, "package") if x.note == note
            ]:
                creation.refund_creation_xp(character, entry)
            self._commit(*XP_SECTIONS)

        self.app.push_screen(
            ConfirmScreen(
                f"Drop the {escape(taken.name)} package ({taken.years} years) "
                "and take back all its xp?",
                yes_label="Drop",
            ),
            handle_confirmed,
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

    def _forget_creation_spell(self, character: Character, entry: CreationXp) -> None:
        """Forget a spell learned at creation, after asking."""
        spell = spl.find_spell(self.saga, entry.target)
        name = escape(spell.name if spell else entry.target)

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                creation.forget_creation_spell(character, entry)
                self._commit(*SPELL_SECTIONS)

        self.app.push_screen(
            ConfirmScreen(f"Forget {name}?", yes_label="Forget"),
            handle_confirmed,
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
        """Add one of the books' Covenant Situations: a ready-made set of
        Boons and Hooks, on top of any the user added. One applied before is
        replaced, after a warning."""
        books = sourcebooks.saga_books(self.saga)
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        all_situations = catalog.load_covenant_situation_catalog()
        situations = [s for s in all_situations if sourcebooks.in_play(s.source, books)]

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
            earlier = cov_rules.situation_in_use(covenant)
            if earlier is not None:
                old_id, count = earlier
                old = next((s for s in all_situations if s.id == old_id), None)
                old_name = escape(old.name) if old is not None else "A Situation"
                message = (
                    f"{old_name} is already applied. Using "
                    f"{escape(situation.name)} removes the {count} Boons and Hooks "
                    f"it brought and adds {len(added)}. "
                    f"{escape(situation.description)} Boons and Hooks you added "
                    "yourself stay."
                )
                yes_label, variant = "Replace", "error"
            else:
                message = (
                    f"Add {escape(situation.name)}'s {len(added)} Boons and Hooks "
                    f"to {escape(covenant.name)}? {escape(situation.description)}"
                )
                if covenant.boons_hooks:
                    message += " The ones it already has stay."
                yes_label, variant = "Add", "primary"
            if situation.notes:
                message += f"\n\n[dim]{escape(situation.notes)}[/]"

            def handle_confirmed(confirmed: bool | None) -> None:
                if confirmed:
                    cov_rules.use_situation(covenant, added)
                    self._commit(
                        "section-cov-boons",
                        "section-cov-hooks",
                        "section-eco-income",
                        "section-pos-vis_source",
                    )

            self.app.push_screen(
                ConfirmScreen(message, yes_label=yes_label, yes_variant=variant),
                handle_confirmed,
            )

        self.app.push_screen(
            RemovalPickerScreen(
                "Use a Covenant Situation", [label(s) for s in situations]
            ),
            handle_index,
        )

    def _buy_specialist(self, covenant: Covenant) -> None:
        """Buy someone with Build Points: a new line on the Inhabitants tab,
        in the category their Ability gives them (a craftsperson, the turb or
        a specialist). A grog or companion built as a character costs
        nothing; assign them there as usual."""

        def handle_result(result: tuple[str, dict[str, Any]] | None) -> None:
            if result is not None:
                kind, values = result
                inh.save_entry(covenant, kind, None, values)
                self._commit(f"section-inh-{kind}")

        self.app.push_screen(
            _buy_specialist_dialog(sourcebooks.saga_books(self.saga)), handle_result
        )

    # -- New Laboratory --

    def _toggle_starting_lab(self, lab: Laboratory) -> None:
        """Whether the lab is one of its covenant's starting labs (paid for
        from the covenant's Build Points)."""
        lab.starting = not lab.starting
        self._commit("section-lab-identity")
