"""The Covenant sheet: Possessions, Economics, Inhabitants, Description,
Reputations, Boons & Hooks and the covenant itself."""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from typing import Any, ClassVar

from .... import economics as eco
from .... import (
    guest_stays,
    hermetic_projects,
    menagerie,
    mobile_covenants,
    seasons,
    staged_projects,
)
from .... import inhabitants as inh
from ....commands import Command, Form
from ....forms import charter as charter_forms
from ....forms import covenant as covenant_forms
from ....forms import inhabitant as inhabitant_forms
from ....forms import ships as ship_forms
from ....forms import world as world_forms
from ....markup import escape
from ....models import (
    FULL,
    INHABITANT_KINDS,
    POSSESSION_KINDS,
    Covenant,
    IncomeSource,
    Saga,
)
from ....rules import covenfolk
from ....sections import (
    BEASTS_SECTION,
    CHARTER_SECTION,
    CLAUSES_SECTION,
    GUESTS_SECTION,
    PROJECTS_SECTION,
    WHEREABOUTS_SECTION,
)
from ..fields import FieldsDialog
from ..forms import (
    _improve_income_dialog,
)
from ..pickers import (
    RemovalPickerScreen,
)
from ..steps import run_steps
from .base import (
    WorkspaceBase,
    _SectionOps,
)


class CovenantActions(WorkspaceBase):
    """WorkspaceScreen's actions for the Covenant sheet: Possessions,
    Economics, Inhabitants, Description, Reputations, Boons & Hooks and the
    covenant itself."""

    def _run_form(self, form: Form, section: str) -> None:
        """Show a core form (commands.Form) and, once saved, apply it and
        refresh `section`."""

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            form.apply(values)
            self._commit(section)

        self.app.push_screen(
            FieldsDialog(form.title, form.fields(), validate=form.validate),
            handle_result,
        )

    # -- Covenant: Possessions tab --

    # -- Covenant: Economics tab --

    #: What the user types on a table row, by `Economics` attribute.
    _ECONOMICS_TYPED_LABELS: ClassVar[dict[str, str]] = {
        "tithes": "Amount (pounds a year)",
        "inflation": "Amount (pounds a year)",
        "sundry": "Amount (pounds a year, at least 1)",
        "magic_savings": "Savings (pounds a year)",
        "emergency_savings": "Savings (pounds a year)",
    }

    def _selected_economics(self, which: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_economics(which) if view is not None else None

    def _edit_wealth(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        form = covenant_forms.wealth_form(covenant)

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            form.apply(values)
            self._commit("section-eco-wealth")

        self.app.push_screen(FieldsDialog(form.title, form.fields()), handle_result)

    def _improve_income_source(self) -> None:
        """Improve the chosen source of income (manually simulating a year's
        Income Modification)."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        sources = covenant.economics.income_sources
        self._chosen_or_pick(
            self._selected_economics("income"),
            [escape(s.name) or "(unnamed)" for s in sources],
            empty="No sources of income to improve.",
            then=lambda index: self._improve_form(sources[index]),
        )

    def _improve_form(self, source: IncomeSource) -> None:
        def handle_result(result: tuple[int, str] | None) -> None:
            if result is None:
                return
            new_income, note = result
            source.income = new_income
            source.note = note
            self._commit("section-eco-income")

        covenant = self.selected_covenant
        limit = (
            (eco.magic_limit(self.saga, covenant), eco.magi_count(self.saga, covenant))
            if covenant is not None
            else None
        )
        self.app.push_screen(
            _improve_income_dialog(source, self.saga.current_year, limit),
            handle_result,
        )

    # -- Covenant: Inhabitants tab --

    def _restore_inhabitant(self, kind: str) -> None:
        """Bring back a departed Magus/Companion: still on their sheet, they
        simply start counting as an inhabitant again."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        entries = inh.departed_entries_for_kind(self.saga, covenant, kind)
        if not entries:
            self.notify(f"No departed {inh.KIND_TITLES[kind]} to restore.")
            return

        def do_restore(entry: covenfolk.InhabitantEntry) -> None:
            if entry.record is not None:
                entry.record.departed = False
                self._commit(f"section-inh-{kind}")

        def handle_index(index: int | None) -> None:
            if index is not None:
                do_restore(entries[index])

        self.app.push_screen(
            RemovalPickerScreen(
                f"Restore which {inh.KIND_SINGULAR[kind]}?",
                [escape(e.name) or "(unnamed)" for e in entries],
            ),
            handle_index,
        )

    def _edit_loyalty(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        self._run_form(
            inhabitant_forms.loyalty_form(self.saga, covenant), "section-inh-loyalty"
        )

    def _edit_population(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        self._run_form(
            inhabitant_forms.population_form(self.saga, covenant),
            "section-inh-population",
        )

    def _edit_miscellaneous(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        self._run_form(inhabitant_forms.misc_form(covenant), "section-inh-misc")

    # -- Covenant: Description / Reputations / Boons & Hooks --

    def _edit_covenant_description(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        self._run_form(
            covenant_forms.description_form(covenant), "section-cov-description"
        )

    # -- Covenant --

    def _edit_covenant(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        form = (
            covenant_forms.covenant_form(self.saga, covenant)
            if covenant.detail == FULL
            else world_forms.sketch_covenant_form(self.saga, covenant)
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            form.apply(values)
            self._commit("section-cov-info", tree=True)

        self.app.push_screen(
            FieldsDialog(form.title, form.fields(), validate=form.validate),
            handle_result,
        )

    def action_improve(self) -> None:
        self._improve_income_source()

    # -- Covenant: the Ships list's More (Hermetic Projects; City & Guild) --

    def _on_ship(
        self, build: Callable[[Saga, Covenant, int], Command], *, tree: bool = False
    ) -> None:
        """Run `build(saga, covenant, row)` on the chosen ship; `tree`: it
        may set up a Fight in Conflicts."""
        covenant = self.selected_covenant
        view = self._covenant_sheet_view
        row = view.selected_possession("ship") if view is not None else None
        if covenant is None or row is None:
            self.notify("Choose a ship first.", severity="warning")
            return
        run_steps(
            self.app,
            build(self.saga, covenant, row),
            lambda end: self._commit_told(
                end, "section-pos-ship", "tab-cov-diary", tree=tree
            ),
        )

    def action_detach_ship(self) -> None:
        """More's Detach for the chosen ship."""
        self._on_ship(mobile_covenants.detach_form)

    def action_rejoin_ship(self) -> None:
        """More's Rejoin for the chosen ship."""
        self._on_ship(mobile_covenants.rejoin_form)

    def action_plan_route(self) -> None:
        """More's Plan Route on Whereabouts."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        run_steps(
            self.app,
            mobile_covenants.plan_route(self.saga, covenant),
            lambda end: self._commit_told(end, WHEREABOUTS_SECTION),
        )

    def action_ship_stress(self) -> None:
        """More's Stress Check on the chosen ship."""
        self._on_ship(ship_forms.stress_check)

    def action_ship_combat(self) -> None:
        """More's Ship Combat for the chosen ship."""
        self._on_ship(ship_forms.ship_combat, tree=True)

    def action_ship_fate(self) -> None:
        """More's Sunk or Taken for the chosen ship."""
        self._on_ship(ship_forms.mark_fate, tree=True)

    # -- Covenant: shaping the land (Transforming Mythic Europe) --

    # -- Covenant: Charter tab --

    def action_seal_charter(self) -> None:
        """More's Seal the Charter: which magi have sealed it, and when."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        run_steps(
            self.app,
            charter_forms.seal_form(self.saga, covenant),
            lambda _end: self._commit(CHARTER_SECTION),
        )

    def action_break_clause(self) -> None:
        """More's Break a Clause on the chosen clause."""
        covenant = self.selected_covenant
        view = self._covenant_sheet_view
        if covenant is None or view is None:
            return
        run_steps(
            self.app,
            charter_forms.break_clause(
                self.saga, covenant, view.section_row(CLAUSES_SECTION)
            ),
            lambda _end: self._commit(CLAUSES_SECTION),
        )

    def _on_clause(self, build: Callable[[Saga, Covenant, int | None], Any]) -> None:
        """Run a More command built on the chosen clause."""
        covenant = self.selected_covenant
        view = self._covenant_sheet_view
        if covenant is None or view is None:
            return
        run_steps(
            self.app,
            build(self.saga, covenant, view.section_row(CLAUSES_SECTION)),
            # Ending a membership moves a magus out of the covenant.
            lambda _end: self._commit(CLAUSES_SECTION, CHARTER_SECTION, tree=True),
        )

    def _on_charter(self, build: Callable[[Saga, Covenant], Any]) -> None:
        """Run a More command built on the covenant's charter."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        run_steps(
            self.app,
            build(self.saga, covenant),
            lambda _end: self._commit(CHARTER_SECTION, CLAUSES_SECTION, tree=True),
        )

    def action_censure_clause(self) -> None:
        """More's Censure on the chosen broken clause."""
        self._on_clause(charter_forms.censure_clause)

    def action_charge_clause(self) -> None:
        """More's Charge at Tribunal on the chosen broken clause."""
        self._on_clause(charter_forms.charge)

    def action_use_charter_template(self) -> None:
        """More's Use a Template on the charter."""
        self._on_charter(charter_forms.use_template)

    def action_save_charter_template(self) -> None:
        """More's Save as Template on the charter."""
        self._on_charter(charter_forms.save_template)

    def action_forget_charter_template(self) -> None:
        """More's Forget a Template on the charter."""
        self._on_charter(lambda saga, _covenant: charter_forms.forget_template(saga))

    def action_end_membership(self) -> None:
        """More's End Membership on the charter."""
        self._on_charter(charter_forms.end_membership_step)

    def action_pay_fee(self) -> None:
        """More's Pay the Fee on the chosen guest."""
        covenant = self.selected_covenant
        view = self._covenant_sheet_view
        if covenant is None or view is None:
            return
        run_steps(
            self.app,
            guest_stays.pay_form(self.saga, covenant, view.section_row(GUESTS_SECTION)),
            lambda _end: self._commit(GUESTS_SECTION, "tab-cov-diary"),
        )

    # -- Covenant: Diary --

    def _covenant_section_ops(self) -> dict[str, _SectionOps]:
        """a / d / e (and More's Restore) on the covenant sheet (see
        WorkspaceScreen._section_ops)."""
        ops: dict[str, _SectionOps] = {
            "section-cov-info": _SectionOps(edit=self._edit_covenant),
            "section-cov-description": _SectionOps(
                edit=self._edit_covenant_description
            ),
            "section-cov-boons": self._core_ops_of("section-cov-boons"),
            "section-cov-hooks": self._core_ops_of("section-cov-hooks"),
            "section-eco-wealth": _SectionOps(edit=self._edit_wealth),
            "section-eco-income": self._core_ops_of("section-eco-income"),
            "section-eco-expenditure": self._core_ops_of("section-eco-expenditure"),
            "section-eco-savings": self._core_ops_of("section-eco-savings"),
            "section-inh-loyalty": _SectionOps(edit=self._edit_loyalty),
            "section-inh-population": _SectionOps(edit=self._edit_population),
            "section-inh-misc": _SectionOps(edit=self._edit_miscellaneous),
            "tab-cov-diary": self._core_ops_of("tab-cov-diary"),
        }
        for kind in INHABITANT_KINDS:
            # Only Magi/Companions can go "departed" (Inhabitant.departed).
            ops[f"section-inh-{kind}"] = self._core_ops_of(
                f"section-inh-{kind}",
                partial(self._restore_inhabitant, kind)
                if kind in covenfolk.AUTO_KINDS
                else None,
            )
        for kind, _ in seasons.SEASON_KINDS:
            # A Seasons list plans the person chosen: Add and Edit both do.
            section = f"section-cov-seasons-{kind}"
            plan = partial(self._core_verb, section, "edit")
            ops[section] = self._core_ops_of(section)._replace(add=plan)
        for kind in POSSESSION_KINDS:
            ops[f"section-pos-{kind}"] = self._core_ops_of(f"section-pos-{kind}")
        return ops

    # -- Covenant: Hermetic Projects (Hermetic Projects pp. 36-41) --

    def _on_projects(self, step: Callable[[Covenant], Command]) -> None:
        """Run `step(covenant)` on the covenant on show, then refresh its
        Projects tab (its sections follow one another)."""
        covenant = self.selected_covenant
        if covenant is None:
            return

        def done(end: object) -> None:
            self._commit(PROJECTS_SECTION, "section-cov-info")
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, step(covenant), done)

    def action_begin_project(self) -> None:
        """More's Begin Project: the first shows the Projects tab."""
        self._on_projects(partial(hermetic_projects.begin_form, self.saga))

    def action_tower_stress(self) -> None:
        """More's Stress Check on the tower shown."""
        self._on_projects(partial(hermetic_projects.stress_form, self.saga))

    def action_tower_conjure(self) -> None:
        """More's Conjure Levels on the tower shown."""
        self._on_projects(partial(hermetic_projects.conjure_form, self.saga))

    def action_show_project(self) -> None:
        """More's Show Project: the chosen project's tower on the tab."""
        view = self._covenant_sheet_view
        row = view.section_row(PROJECTS_SECTION) if view is not None else None
        self._on_projects(
            lambda covenant: hermetic_projects.show_project(self.saga, covenant, row)
        )

    # -- Covenant: a Menagerie (Hermetic Projects pp. 119-142) --

    def action_menagerie_award(self) -> None:
        """More's Reputation Award on the menagerie shown."""
        self._on_projects(lambda covenant: menagerie.award_form(self.saga, covenant))

    # -- Covenant: a staged project (Hermetic Projects pp. 9-118) --

    def action_warning_bell(self) -> None:
        """More's Warning Bell on the Burning City shown."""
        self._on_projects(partial(staged_projects.bell_form, self.saga))

    def action_gather_connection(self) -> None:
        """More's Gather a Connection on the Intangible Assassin shown."""
        self._on_projects(partial(staged_projects.gather_form, self.saga))

    def action_lower_aegis(self) -> None:
        """More's Lower an Aegis on the Intangible Assassin shown."""
        self._on_projects(partial(staged_projects.aegis_form, self.saga))

    def action_death_roll(self) -> None:
        """More's Death Roll on the Living Corpse shown."""
        self._on_projects(partial(staged_projects.death_form, self.saga))

    def action_tame_beast(self) -> None:
        """More's Tame a Beast on the chosen beast of the menagerie shown."""
        view = self._covenant_sheet_view
        row = view.section_row(BEASTS_SECTION) if view is not None else None
        self._on_projects(
            lambda covenant: menagerie.tame_form(self.saga, covenant, row)
        )
