"""The Covenant sheet: Possessions, Economics, Inhabitants, Description,
Reputations, Boons & Hooks and the covenant itself."""

from __future__ import annotations

from typing import Any, ClassVar

from .... import (
    catalog,
    covenant_diary,
    covenant_forms,
    inhabitant_forms,
    seasons,
    sourcebooks,
    vis,
)
from .... import covenants as cov_rules
from .... import economics as eco
from .... import inhabitants as inh
from .... import possessions as pos
from ....commands import Form
from ....covenants import boon_hook_is_unknown
from ....markup import escape
from ....models import (
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    BOON_HOOK_RESOURCE,
    Character,
    Covenant,
    CovenantDiaryEntry,
    IncomeSource,
    VirtueFlawInstance,
    boon_hook_params,
    new_instance_id,
)
from ..fields import FieldsDialog
from ..forms import (
    _improve_income_dialog,
    _inhabitant_fields,
    _possession_dialog,
)
from ..pickers import (
    CovenantBoonHookPickerScreen,
    RemovalPickerScreen,
)
from ..prompts import (
    ConfirmScreen,
    _boon_hook_fields,
    _covenant_diary_entry_dialog,
)
from .base import (
    _BOON_HOOK_SECTION,
    WorkspaceBase,
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

    def _selected_possession(self, kind: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_possession(kind) if view is not None else None

    def _possession_entries(self, kind: str) -> list[pos.PossessionEntry]:
        covenant = self.selected_covenant
        if covenant is None:
            return []
        return pos.entries_for_kind(
            self.saga, covenant, kind, catalog.load_lab_virtue_flaw_catalog_by_id()
        )

    def _add_possession(self, kind: str) -> None:
        self._possession_form(kind, None)

    def _edit_possession(self, kind: str) -> None:
        """Edit the chosen possession."""
        entries = self._possession_entries(kind)
        self._chosen_or_pick(
            self._selected_possession(kind),
            [escape(e.name) or "(unnamed)" for e in entries],
            empty=f"No {pos.KIND_TITLES[kind]} to edit.",
            then=lambda index: self._possession_form(kind, entries[index]),
        )

    def _possession_form(self, kind: str, entry: pos.PossessionEntry | None) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        title = (
            f"Add a {pos.KIND_SINGULAR[kind]}"
            if entry is None
            else f"Edit {escape(entry.name or 'this ' + pos.KIND_SINGULAR[kind].lower())}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            pos.save_entry(covenant, kind, entry, values)
            self._commit(f"section-pos-{kind}")

        places: list[tuple[str, str]] = []
        place = ""
        if kind == "vis_store":
            places = vis.location_options(self.saga, covenant)
            place = vis.location_value(covenant, entry.record if entry else None)
            if place not in [value for _, value in places]:
                place = places[0][1]  # whoever kept it has left the covenant
        self.app.push_screen(
            _possession_dialog(title, kind, entry, places=places, place=place),
            handle_result,
        )

    def _remove_possession(self, kind: str) -> None:
        """Delete the chosen possession (after confirming). A laboratory listed as a sanctum can't be deleted here."""
        entries = self._possession_entries(kind)
        self._chosen_or_pick(
            self._selected_possession(kind),
            [escape(e.name) or "(unnamed)" for e in entries],
            empty=f"No {pos.KIND_TITLES[kind]} to remove.",
            then=lambda index: self._confirm_remove_possession(kind, entries[index]),
        )

    def _confirm_remove_possession(self, kind: str, entry: pos.PossessionEntry) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        if entry.auto:
            self.notify(
                f"{escape(entry.name)} is a laboratory of this covenant, so it "
                "can't be deleted here. Move it to another covenant from the "
                "laboratory's Identity instead."
            )
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and entry.record in covenant.possessions:
                covenant.possessions.remove(entry.record)
                self._commit(f"section-pos-{kind}")

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(entry.name or 'this entry')}?"),
            handle_confirmed,
        )

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

    def _add_income_source(self) -> None:
        self._income_form(None)

    def _edit_income_source(self) -> None:
        """Edit the chosen source of income."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        sources = covenant.economics.income_sources
        self._chosen_or_pick(
            self._selected_economics("income"),
            [escape(s.name) or "(unnamed)" for s in sources],
            empty="No sources of income to edit.",
            then=lambda index: self._income_form(sources[index]),
        )

    def _income_form(self, source: IncomeSource | None) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            covenant_forms.apply_income(covenant, source, values)
            self._commit("section-eco-income")

        self.app.push_screen(
            FieldsDialog(
                covenant_forms.income_title(source),
                covenant_forms.income_fields(source),
            ),
            handle_result,
        )

    def _remove_income_source(self) -> None:
        """Delete the chosen source of income (after confirming)."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        sources = covenant.economics.income_sources
        self._chosen_or_pick(
            self._selected_economics("income"),
            [escape(s.name) or "(unnamed)" for s in sources],
            empty="No sources of income to remove.",
            then=lambda index: self._confirm_remove_income_source(sources[index]),
        )

    def _confirm_remove_income_source(self, source: IncomeSource) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and source in covenant.economics.income_sources:
                covenant.economics.income_sources.remove(source)
                self._commit("section-eco-income")

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(source.name or 'this source of income')}?"),
            handle_confirmed,
        )

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

        self.app.push_screen(
            _improve_income_dialog(source, self.saga.current_year), handle_result
        )

    def _offer_emergency_draw(
        self, which: str, row: eco.Row, summary: eco.Summary
    ) -> None:
        """With a deficit, editing Emergency Savings first offers to cover it
        from Wealth: all of it, or as much as Wealth holds. No (or no Wealth to
        draw from) goes on to the ordinary form."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        deficit = -summary.surplus_deficit
        draw = eco.emergency_draw(summary)
        if draw == 0:
            self.notify(
                "There's no Wealth to draw from: the covenant is broke.",
                severity="warning",
            )
            self._economics_row_form(which, row, offer_draw=False)
            return
        outcome = (
            f"This moves {draw} from Wealth into Emergency Savings."
            if draw == deficit
            else f"Wealth only covers {draw} of it: all of it is drawn, and "
            f"{deficit - draw} stays uncovered."
        )

        def handle_confirmed(confirmed: bool | None) -> None:
            if not confirmed:
                self._economics_row_form(which, row, offer_draw=False)
                return
            eco.draw_from_wealth(covenant, draw)
            self._commit("section-eco-savings")
            self.notify(f"Drew {draw} from Wealth to cover the deficit.")

        self.app.push_screen(
            ConfirmScreen(
                "Do you wish to draw from Wealth to cover the deficit?\n\n"
                f"Deficit: {deficit}    Wealth: {summary.wealth}\n{outcome}",
                yes_label="Draw",
                yes_variant="success",
            ),
            handle_confirmed,
        )

    def _edit_economics_row(self, which: str) -> None:
        """Edit the chosen Yearly Expenditure / Cost Savings row (its Notes, and
        the numbers that are typed rather than calculated)."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        summary = eco.summarize(self.saga, covenant)
        rows = summary.expenditure if which == "expenditure" else summary.savings
        self._chosen_or_pick(
            self._selected_economics(which),
            [row.name for row in rows],
            empty="Nothing to edit here.",
            then=lambda index: self._economics_row_form(which, rows[index]),
        )

    def _economics_row_form(
        self, which: str, row: eco.Row, *, offer_draw: bool = True
    ) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        if offer_draw and row.key == "emergency_savings":
            summary = eco.summarize(self.saga, covenant)
            if summary.surplus_deficit < 0:
                self._offer_emergency_draw(which, row, summary)
                return

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            eco.apply_row_edit(covenant.economics, row.key, values)
            self._commit(f"section-eco-{which}")

        self.app.push_screen(
            FieldsDialog(
                f"Edit {row.name}",
                covenant_forms.economics_row_fields(covenant, which, row),
                validate=lambda values: eco.row_problem(row.key, values),
            ),
            handle_result,
        )

    # -- Covenant: Inhabitants tab --

    def _selected_inhabitant(self, kind: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_inhabitant(kind) if view is not None else None

    def _inhabitant_entries(self, kind: str) -> list[inh.InhabitantEntry]:
        covenant = self.selected_covenant
        if covenant is None:
            return []
        return inh.entries_for_kind(self.saga, covenant, kind)

    def _add_inhabitant(self, kind: str) -> None:
        """Add one. Grog-derived kinds first offer the covenant's unassigned
        grogs (or a brand-new person); Magi, Companions and animals go
        straight to the form."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        if kind not in inh.GROG_KINDS:
            self._inhabitant_form(kind, None, None)
            return

        grogs = inh.available_grogs(self.saga, covenant)
        labels = ["(New person -- not from a character sheet)"] + [
            escape(g.name)
            + (f"  (born {g.background.year_born})" if g.background.year_born else "")
            for g in grogs
        ]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._inhabitant_form(kind, None, grogs[index - 1] if index else None)

        self.app.push_screen(
            RemovalPickerScreen(f"Add a {inh.KIND_SINGULAR[kind]}", labels),
            handle_index,
        )

    def _edit_inhabitant(self, kind: str) -> None:
        """Edit the chosen inhabitant."""
        entries = self._inhabitant_entries(kind)
        self._chosen_or_pick(
            self._selected_inhabitant(kind),
            [escape(e.name) or "(unnamed)" for e in entries],
            empty=f"No {inh.KIND_TITLES[kind]} to edit.",
            then=lambda index: self._inhabitant_form(kind, entries[index], None),
        )

    def _inhabitant_form(
        self, kind: str, entry: inh.InhabitantEntry | None, grog: Character | None
    ) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        title = (
            f"Add a {inh.KIND_SINGULAR[kind]}"
            if entry is None
            else f"Edit {escape(entry.name or 'this ' + inh.KIND_SINGULAR[kind].lower())}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            inh.save_entry(covenant, kind, entry, values, grog)
            self._commit(f"section-inh-{kind}")

        self.app.push_screen(
            FieldsDialog(
                title,
                _inhabitant_fields(kind, entry, grog),
                validate=inh.form_problem,
            ),
            handle_result,
        )

    def _remove_inhabitant(self, kind: str) -> None:
        """Delete the chosen inhabitant (after confirming). People listed from a character sheet can't be deleted
        here -- that would mean changing the sheet."""
        entries = self._inhabitant_entries(kind)
        self._chosen_or_pick(
            self._selected_inhabitant(kind),
            [escape(e.name) or "(unnamed)" for e in entries],
            empty=f"No {inh.KIND_TITLES[kind]} to remove.",
            then=lambda index: self._confirm_remove_inhabitant(kind, entries[index]),
        )

    def _confirm_remove_inhabitant(self, kind: str, entry: inh.InhabitantEntry) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        name = escape(entry.name or "this entry")

        if entry.auto and entry.character is not None:
            # Listed from a character sheet (e.g. a magus who died): they stay
            # in the covenant on their sheet, but stop counting as an inhabitant.

            def handle_departed(confirmed: bool | None) -> None:
                if not confirmed:
                    return
                inh.mark_departed(covenant, kind, entry)
                self._commit(f"section-inh-{kind}")

            self.app.push_screen(
                ConfirmScreen(
                    f"Remove {name} from the {inh.KIND_TITLES[kind]} list?\n\n"
                    "They stay in the covenant on their character sheet, but "
                    "will no longer count as an inhabitant."
                ),
                handle_departed,
            )
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and entry.record in covenant.inhabitants:
                covenant.inhabitants.remove(entry.record)
                self._commit(f"section-inh-{kind}")

        self.app.push_screen(ConfirmScreen(f"Delete {name}?"), handle_confirmed)

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

        def do_restore(entry: inh.InhabitantEntry) -> None:
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

    def _selected_reputation(self) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_reputation() if view is not None else None

    def _attached_boons_hooks(
        self, covenant: Covenant, kind: str
    ) -> list[tuple[int, VirtueFlawInstance]]:
        """The covenant's attached Boons or Hooks (`kind`), each with its
        index into covenant.boons_hooks so callers can edit/delete the real
        entry from a filtered list."""
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        return [
            (index, bh)
            for index, bh in enumerate(covenant.boons_hooks)
            if bh.vf_id in by_id and by_id[bh.vf_id].type == kind
        ]

    def _add_boon_hook(self, kind: str) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        attached_ids = [bh.vf_id for bh in covenant.boons_hooks]

        def handle_result(instance: VirtueFlawInstance | None) -> None:
            if instance is not None:
                instance.id = instance.id or new_instance_id()
                covenant.boons_hooks.append(instance)
                self._commit(_BOON_HOOK_SECTION[kind])
                if instance.vf_id in cov_rules.RESOURCE_HOOKS:
                    self.notify(
                        "Link this Hook to the vis or income source it is about "
                        "(e on it, under Boons & Hooks), once that source exists.",
                        timeout=10,
                    )

        self.app.push_screen(
            CovenantBoonHookPickerScreen(
                kind, attached_ids, books=sourcebooks.saga_books(self.saga)
            ),
            handle_result,
        )

    def _selected_boon_hook(self, kind: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_boon_hook(kind) if view is not None else None

    def _remove_boon_hook(self, kind: str) -> None:
        """Delete the selected Boon/Hook (after confirming)."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        selected = self._selected_boon_hook(kind)
        if selected is not None:
            self._confirm_remove_boon_hook(kind, selected)
            return
        attached = self._attached_boons_hooks(covenant, kind)
        self._chosen_or_pick(
            None,
            [str(index) for index, _ in attached],
            empty=f"No {kind}s to remove.",
            then=lambda at: self._confirm_remove_boon_hook(kind, attached[at][0]),
        )

    def _confirm_remove_boon_hook(self, kind: str, index: int) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        label = catalog.describe_boon_hook(covenant.boons_hooks[index], by_id)

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del covenant.boons_hooks[index]
                self._commit(_BOON_HOOK_SECTION[kind])

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(label)}?"), handle_confirmed
        )

    def _edit_boon_hook(self, kind: str) -> None:
        """Edit the selected Boon/Hook's detail and description."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        selected = self._selected_boon_hook(kind)
        if selected is not None:
            self._edit_boon_hook_at(kind, selected)
            return
        attached = self._attached_boons_hooks(covenant, kind)
        self._chosen_or_pick(
            None,
            [str(index) for index, _ in attached],
            empty=f"No {kind}s to edit.",
            then=lambda at: self._edit_boon_hook_at(kind, attached[at][0]),
        )

    def _edit_boon_hook_at(self, kind: str, index: int) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        instance = covenant.boons_hooks[index]
        definition = by_id[instance.vf_id]

        def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            instance.params = boon_hook_params(
                result["detail"],
                result["description"],
                instance.params,
                unknown=result.get("unknown", False),
            )
            if "resource" in result:
                cov_rules.link_resource(covenant, instance, result["resource"] or "")
            self._commit(
                _BOON_HOOK_SECTION[kind], "section-eco-income", "section-pos-vis_source"
            )

        self.app.push_screen(
            FieldsDialog(
                f"{kind}: {escape(definition.name)}",
                _boon_hook_fields(
                    instance.params.get(BOON_HOOK_DETAIL, ""),
                    instance.params.get(BOON_HOOK_DESCRIPTION, ""),
                    can_be_unknown=definition.unknown,
                    unknown=boon_hook_is_unknown(instance, definition),
                    sources=(
                        cov_rules.resource_sources(covenant)
                        if instance.vf_id in cov_rules.RESOURCE_HOOKS
                        else None
                    ),
                    source=instance.params.get(BOON_HOOK_RESOURCE, ""),
                ),
            ),
            handle_result,
        )

    # -- Covenant --

    def _edit_covenant(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        form = covenant_forms.covenant_form(covenant)

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            form.apply(values)
            self._commit("section-cov-info", tree=True)

        self.app.push_screen(FieldsDialog(form.title, form.fields()), handle_result)

    def action_improve(self) -> None:
        self._improve_income_source()

    # -- Covenant: Diary --

    def _cov_diary_selection(self) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_diary_entry() if view is not None else None

    def _cov_diary_labels(self, covenant: Covenant) -> tuple[list[int], list[str]]:
        """The Diary rows in the order listed: their indexes into
        covenant.diary, and their labels."""
        rows = covenant_diary.rows(covenant.diary)
        return [i for i, _ in rows if i is not None], [label for _, label in rows]

    def _add_covenant_diary_entry(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return

        def handle_result(entry: CovenantDiaryEntry | None) -> None:
            if entry is not None:
                covenant.diary.append(entry)
                self._commit("tab-cov-diary")

        self.app.push_screen(
            _covenant_diary_entry_dialog(
                covenant,
                self.saga.current_year,
                default_season=self.saga.current_season,
            ),
            handle_result,
        )

    def _edit_covenant_diary_entry(self) -> None:
        """Edit the chosen Diary entry."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        order, labels = self._cov_diary_labels(covenant)

        def edit(index: int) -> None:
            def handle_result(entry: CovenantDiaryEntry | None) -> None:
                if entry is not None:
                    covenant.diary[index] = entry
                    self._commit("tab-cov-diary")

            self.app.push_screen(
                _covenant_diary_entry_dialog(
                    covenant, self.saga.current_year, existing=covenant.diary[index]
                ),
                handle_result,
            )

        selected = self._cov_diary_selection()
        if selected is not None:
            edit(selected)
            return
        self._chosen_or_pick(
            None,
            labels,
            empty="No Diary entries to edit.",
            then=lambda position: edit(order[position]),
        )

    def _remove_covenant_diary_entry(self) -> None:
        """Delete the chosen Diary entry (after confirming)."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        order, labels = self._cov_diary_labels(covenant)

        def remove(index: int) -> None:
            self._confirm_delete(
                covenant.diary, index, covenant.diary[index].name, "tab-cov-diary"
            )

        selected = self._cov_diary_selection()
        if selected is not None:
            remove(selected)
            return
        self._chosen_or_pick(
            None,
            labels,
            empty="No Diary entries to remove.",
            then=lambda position: remove(order[position]),
        )

    # -- Covenant: Seasons --

    def _season_person_then(self, kind: str, then: Any) -> None:
        """Act on the person chosen in the Seasons list of `kind`."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        people = seasons.covenant_people(self.saga, covenant, kind)
        view = self._covenant_sheet_view
        chosen = view.selected_season_person() if view is not None else None
        selected = people.index(chosen) if chosen in people else None
        self._chosen_or_pick(
            selected,
            [escape(c.name) for c in people],
            empty="Nobody to plan for here.",
            then=lambda index: then(people[index]),
        )

    def _plan_covenant_season(self, kind: str) -> None:
        self._season_person_then(
            kind, lambda c: self._plan_season_for(c, "tab-cov-seasons")
        )

    def _clear_covenant_season(self, kind: str) -> None:
        self._season_person_then(
            kind, lambda c: self._clear_season_plan_for(c, "tab-cov-seasons")
        )
