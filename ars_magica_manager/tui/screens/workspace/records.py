"""WorkspaceScreen's actions on the saga's world records: creating each kind of
record from New, and the More menu's record commands (arms, founding a
covenant at a ruin, beginning a dormant story, a Tribunal's cases, fairs and
tables)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from .... import (
    arms,
    battles,
    character_templates,
    choice_templates,
    conflicts,
    creation,
    grog_templates,
    lords,
    manors,
    marriages,
    open_stories,
    place_events,
    places,
    ruins,
    storage,
    threats,
    town_charter,
    town_court,
    towns,
    tribunal_packages,
)
from .... import familiars as fam
from .... import tombs as tomb_rules
from ....actions import (
    NodeKind,
)
from ....commands import Command, Go
from ....forms import charter_strength as charter_strength_forms
from ....forms import choice_templates as choice_forms
from ....forms import creation as creation_forms
from ....forms import creature as creature_forms
from ....forms import go_to as go_to_forms
from ....forms import hunting as hunting_forms
from ....forms import neighbour as neighbour_forms
from ....forms import polemic as polemic_forms
from ....forms import threshold as threshold_forms
from ....forms import tribunal as tribunal_forms
from ....forms import wizards_war
from ....markup import escape
from ....models import (
    Character,
    CharacterTemplateDef,
    Covenant,
    Neighbour,
)
from ....sections import (
    ARGUMENT_TEXTS_SECTION,
    BATTLES_SECTION,
    CASES_SECTION,
    CHARTER_LORDS_SECTION,
    COURT_CASES_SECTION,
    COV_CHARTER_LORDS_SECTION,
    DIARY_SECTION,
    ESTABLISHMENTS_SECTION,
    FAIRS_SECTION,
    GILDS_SECTION,
    GRATITUDE_SECTION,
    HOUSEHOLD_SECTION,
    LIBRARY_CREDIT_SECTION,
    LIBRARY_RULES_SECTION,
    LIBRARY_SEARCHES_SECTION,
    MANORS_SECTION,
    MARRIAGE_TERMS_SECTION,
    MARRIAGES_SECTION,
    NEIGHBOUR_INFO_SECTION,
    REGION_STORIES_SECTION,
    REGION_THREATS_SECTION,
    STAGES_SECTION,
    TABLES_SECTION,
    TOKENS_SECTION,
    TOMB_TRAPS_SECTION,
    TOMB_WARDS_SECTION,
    TREASURY_SECTION,
)
from ..fields import (
    FieldsDialog,
)
from ..forms import (
    _character_create_dialog,
    _covenant_create_fields,
    _familiar_create_fields,
    _laboratory_create_fields,
    template_key,
)
from ..sheets.base import SheetView
from ..steps import run_steps
from .base import (
    WorkspaceBase,
    _tree_node_with_data,
)

#: The tree node that shows each kind of record a page can name
#: (references.KINDS).
_REF_NODES: dict[str, NodeKind] = {
    "characters": NodeKind.CHARACTER,
    "covenants": NodeKind.COVENANT,
    "laboratories": NodeKind.LABORATORY,
    "familiars": NodeKind.FAMILIAR,
    "tribunals": NodeKind.TRIBUNAL,
    "neighbours": NodeKind.NEIGHBOUR,
    "creatures": NodeKind.CREATURE,
}


class RecordActions(WorkspaceBase):
    # -- creation actions --

    def action_create_covenant(self) -> None:
        async def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                covenant = creation.add_covenant(
                    self.saga,
                    values["name"],
                    values["notes"],
                    season=values["season"] or "Spring",
                    aura_realm=values["aura_realm"] or "Magic",
                )
                storage.save_saga(self.saga)
                self._rebuild_tree()
                self.selected_covenant = covenant
                self.selected_kind = NodeKind.COVENANT
                await self._show_covenant_detail(covenant)
                self._open_creation_worksheet(covenant)

        self.app.push_screen(
            FieldsDialog(
                "Create a New Covenant", _covenant_create_fields(), save_label="Create"
            ),
            handle_result,
        )

    def action_create_tribunal(self) -> None:
        before = {t.id for t in self.saga.tribunals}

        def done(_end: object) -> None:
            storage.save_saga(self.saga)
            self._rebuild_tree()
            made = [t for t in self.saga.tribunals if t.id not in before]
            if made:
                node = _tree_node_with_data(
                    self._nav_tree(), (NodeKind.TRIBUNAL, made[-1].id)
                )
                if node is not None:
                    self.call_after_refresh(self._nav_tree().select_node, node)

        run_steps(self.app, tribunal_forms.new_tribunal_form(self.saga), done)

    def action_create_neighbour(self) -> None:
        before = {n.id for n in self.saga.neighbours}

        def done(_end: object) -> None:
            storage.save_saga(self.saga)
            self._rebuild_tree()
            made = [n for n in self.saga.neighbours if n.id not in before]
            if made:
                node = _tree_node_with_data(
                    self._nav_tree(), (NodeKind.NEIGHBOUR, made[-1].id)
                )
                if node is not None:
                    self.call_after_refresh(self._nav_tree().select_node, node)

        run_steps(self.app, neighbour_forms.new_neighbour(self.saga), done)

    def action_create_creature(self) -> None:
        before = {c.id for c in self.saga.creatures}

        def done(_end: object) -> None:
            storage.save_saga(self.saga)
            self._rebuild_tree()
            made = [c for c in self.saga.creatures if c.id not in before]
            if made:
                node = _tree_node_with_data(
                    self._nav_tree(), (NodeKind.CREATURE, made[-1].id)
                )
                if node is not None:
                    self.call_after_refresh(self._nav_tree().select_node, node)

        run_steps(self.app, creature_forms.new_creature_form(self.saga), done)

    def action_withdraw_case(self) -> None:
        """More's Withdraw on the docket's chosen case."""
        view = self._tribunal_sheet_view
        row = view.section_row(CASES_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            tribunal_forms.withdraw_case(view.tribunal, row),
            lambda _end: self._commit(CASES_SECTION),
        )

    def action_war_end(self) -> None:
        """More's War's End on the docket's chosen Wizard's War."""
        view = self._tribunal_sheet_view
        row = view.section_row(CASES_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            wizards_war.end_form(self.saga, view.tribunal, row),
            lambda _end: self._commit(CASES_SECTION),
        )

    def _package_verb(self, action: str, section: str, *also: str) -> None:
        """A Tribunal package's More command on its list's chosen row; the
        sections `also` changed are refreshed beside its own."""
        view = self._tribunal_sheet_view
        row = view.section_row(section) if view is not None else None
        if view is None or row is None:
            return
        verb = tribunal_packages.package_verb(view.tribunal, action)
        if verb is None:
            return
        run_steps(
            self.app,
            verb.build(self.saga, view.tribunal, row),
            lambda _end: self._commit(section, *also),
        )

    def action_neutralize_shard(self) -> None:
        """More's Neutralize a Shard on the Theban tokens' chosen magus."""
        self._package_verb("neutralize_shard", TOKENS_SECTION)

    def action_tribunal_longevity(self) -> None:
        """More's Longevity Ritual on the Theban tokens."""
        self._package_verb("tribunal_longevity", TOKENS_SECTION)

    def action_lend_vis(self) -> None:
        """More's Lend Vis on the Theban tokens' chosen magus."""
        self._package_verb("lend_vis", TOKENS_SECTION, TREASURY_SECTION)

    def action_repay_vis_loan(self) -> None:
        """More's Repay a Loan on the Theban tokens' chosen magus."""
        self._package_verb("repay_vis_loan", TOKENS_SECTION, TREASURY_SECTION)

    def action_rhine_mark(self) -> None:
        """More's Mark of Approval on the Rhine's Gilds."""
        self._package_verb("rhine_mark", GILDS_SECTION)

    def action_rhine_challenge(self) -> None:
        """More's Archmage's Challenge on the Rhine's Gilds."""
        self._package_verb("rhine_challenge", GILDS_SECTION)

    def action_library_search(self) -> None:
        """More's Search the Great Library on the Rhine's Great Library."""
        self._package_verb(
            "library_search",
            LIBRARY_RULES_SECTION,
            LIBRARY_CREDIT_SECTION,
            LIBRARY_SEARCHES_SECTION,
        )

    def action_roll_fair(self) -> None:
        """More's Roll Income on a town's chosen fair."""
        view = self._neighbour_sheet_view
        row = view.section_row(FAIRS_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            towns.roll_fair(self.saga, view.neighbour, row),
            lambda _end: self._commit(FAIRS_SECTION),
        )

    def action_court_roll(self) -> None:
        """More's Court Roll on a town's chosen case."""
        view = self._neighbour_sheet_view
        row = view.section_row(COURT_CASES_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            town_court.court_roll(self.saga, view.neighbour, row),
            lambda _end: self._commit(COURT_CASES_SECTION),
        )

    def action_redeem_gratitude(self) -> None:
        """More's Redeem Gratitude on a lord's chosen debt."""
        view = self._neighbour_sheet_view
        row = view.section_row(GRATITUDE_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            lords.redeem_form(self.saga, view.neighbour, row),
            lambda _end: self._commit(GRATITUDE_SECTION, DIARY_SECTION),
        )

    def _manors_holder(self) -> tuple[SheetView, Neighbour] | None:
        """The sheet on show with a Manors tab, and the record whose manors
        it shows: a lord, or a full covenant's manors."""
        view = self._neighbour_sheet_view
        if view is not None:
            return view, view.neighbour
        covenant_view = self._covenant_sheet_view
        if covenant_view is not None and not covenant_view.sketch:
            return covenant_view, manors.manors_of(covenant_view.covenant)
        return None

    def action_buy_manor(self) -> None:
        """More's Buy a Manor on a lord's or a covenant's Manors."""
        found = self._manors_holder()
        if found is None:
            return
        run_steps(
            self.app,
            manors.buy_form(self.saga, found[1]),
            lambda _end: self._commit(MANORS_SECTION, DIARY_SECTION),
        )

    def action_assart(self) -> None:
        """More's Assart on the chosen manor."""
        found = self._manors_holder()
        row = found[0].section_row(MANORS_SECTION) if found is not None else None
        if found is None or row is None:
            return
        run_steps(
            self.app,
            manors.assart_form(self.saga, found[1], row),
            lambda _end: self._commit(MANORS_SECTION, DIARY_SECTION),
        )

    def action_winter_roll(self) -> None:
        """More's Winter Roll on the chosen kennels, mews or stables."""
        found = self._manors_holder()
        row = (
            found[0].section_row(ESTABLISHMENTS_SECTION) if found is not None else None
        )
        if found is None or row is None:
            return
        run_steps(
            self.app,
            manors.winter_roll(self.saga, found[1], row),
            lambda _end: self._commit(ESTABLISHMENTS_SECTION),
        )

    def action_settle_inheritance(self) -> None:
        """More's Settle an Inheritance on a lord's Household."""
        view = self._neighbour_sheet_view
        if view is None:
            return
        run_steps(
            self.app,
            manors.settle_form(self.saga, view.neighbour),
            lambda _end: self._commit(
                HOUSEHOLD_SECTION, NEIGHBOUR_INFO_SECTION, DIARY_SECTION
            ),
        )

    def action_battle_event(self) -> None:
        """More's Battle Event on a lord's chosen battle."""
        view = self._neighbour_sheet_view
        row = view.section_row(BATTLES_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            battles.event_for(self.saga, view.neighbour, row),
            lambda _end: self._commit(BATTLES_SECTION),
        )

    def _conflict_command(self, action: str) -> None:
        """A More command on Conflicts' chosen fight or siege (conflicts.COMMANDS),
        then save and redraw its list and the panel showing it."""
        view = self._conflicts_view
        section = conflicts.SECTION_OF[action]
        row = view.section_row(section) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            conflicts.command(self.saga, action, row),
            lambda _end: self._commit(section),
        )

    def action_conflict_battle_event(self) -> None:
        """More's Battle Event on Conflicts' chosen battle."""
        self._conflict_command("conflict_battle_event")

    def action_fight_options(self) -> None:
        """More's Combat Options on the chosen fight: Lords of Men's
        optional rules worked out for one of its characters."""
        self._conflict_command("fight_options")

    def action_group_morale(self) -> None:
        """More's Discipline or Morale on the chosen fight's group."""
        self._conflict_command("group_morale")

    def action_rally_group(self) -> None:
        """More's Rally a Group on the chosen fight."""
        self._conflict_command("rally_group")

    def action_battle_muster(self) -> None:
        """More's Muster and Aftermath on Conflicts' chosen battle: allies,
        mercenaries, the Deployment Total, and how the day ends."""
        self._conflict_command("battle_muster")

    def action_next_blow(self) -> None:
        """More's Next Blow on the chosen fight."""
        self._conflict_command("next_blow")

    def action_next_round(self) -> None:
        """More's Next Round on the chosen fight."""
        self._conflict_command("next_round")

    def action_add_combatant(self) -> None:
        """More's Add Combatant on the chosen fight."""
        self._conflict_command("add_combatant")

    def action_edit_combatant(self) -> None:
        """More's Edit Combatant on the chosen fight."""
        self._conflict_command("edit_combatant")

    def action_remove_combatant(self) -> None:
        """More's Remove Combatant on the chosen fight."""
        self._conflict_command("remove_combatant")

    def action_form_group(self) -> None:
        """More's Form a Group on the chosen fight."""
        self._conflict_command("form_group")

    def action_break_group(self) -> None:
        """More's Break up a Group on the chosen fight."""
        self._conflict_command("break_group")

    def action_restart_fight(self) -> None:
        """More's Restart the Fight on the chosen fight."""
        self._conflict_command("restart_fight")

    def action_siege_actions(self) -> None:
        """More's Siege Actions on the chosen siege: deployments, a supplies
        story or spell, running the stockade, the castle taken."""
        self._conflict_command("siege_actions")

    def action_next_siege_event(self) -> None:
        """More's Next Siege Event on the chosen siege."""
        self._conflict_command("next_siege_event")

    def action_roll_table(self) -> None:
        """More's Roll on a place's chosen roll table."""
        view = self._neighbour_sheet_view
        row = view.section_row(TABLES_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            place_events.roll_table(self.saga, view.neighbour, row),
            lambda _end: self._commit(TABLES_SECTION, DIARY_SECTION),
        )

    def action_create_character(self) -> None:
        covenant = self.selected_covenant

        async def created(character: Character) -> None:
            storage.save_saga(self.saga)
            self._rebuild_tree()
            self.selected_character = character
            self.selected_kind = NodeKind.CHARACTER
            await self._show_character_detail(character)
            self._open_creation_worksheet(character)

        async def create(
            values: dict[str, Any],
            template: CharacterTemplateDef | None = None,
            blanks: dict[str, str] | None = None,
        ) -> None:
            character = creation.add_character(
                self.saga, values["name"], values["type"], values["covenant_id"]
            )
            if template is not None:
                character_templates.apply(self.saga, character, template, blanks)
            await created(character)

        async def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            grog = grog_templates.find(values.get(template_key(values["type"])))
            if grog is not None:
                made: list[Character] = []
                run_steps(
                    self.app,
                    creation_forms.grog_template_steps(
                        self.saga, values, grog, made.append
                    ),
                    lambda _end: self._grog_created(made, created),
                )
                return
            chosen = choice_templates.find(values.get(template_key(values["type"])))
            if chosen is not None:
                made = []
                run_steps(
                    self.app,
                    choice_forms.choice_template_steps(
                        self.saga, values, chosen, made.append
                    ),
                    lambda _end: self._grog_created(made, created),
                )
                return
            as_companion = choice_forms.grog_companion_find(
                values.get(template_key(values["type"]))
            )
            if as_companion is not None:
                made = []
                run_steps(
                    self.app,
                    choice_forms.grog_companion_steps(
                        self.saga, values, as_companion, made.append
                    ),
                    lambda _end: self._grog_created(made, created),
                )
                return
            template = character_templates.find(
                values.get(template_key(values["type"]))
            )
            wanted = character_templates.blanks(template) if template else []
            if template is None or not wanted:
                await create(values, template)
                return

            async def handle_blanks(filled: dict[str, Any] | None) -> None:
                # Cancelling the names cancels the new character.
                if filled is not None:
                    await create(values, template, filled)

            self.app.push_screen(
                FieldsDialog(
                    f"{escape(template.name)} template",
                    creation_forms.blanks_fields(wanted),
                    save_label="Use",
                ),
                handle_blanks,
            )

        self.app.push_screen(
            _character_create_dialog(self.saga, covenant.id if covenant else None),
            handle_result,
        )

    def _grog_created(
        self, made: list[Character], created: Callable[[Character], Awaitable[None]]
    ) -> None:
        if made:
            self.call_later(created, made[0])

    def action_create_laboratory(self) -> None:
        covenant = self.selected_covenant

        async def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                lab = creation.add_laboratory(
                    self.saga,
                    values["name"],
                    values["size"],
                    values["covenant_id"],
                    starting=values.get("starting", False),
                )
                storage.save_saga(self.saga)
                self._rebuild_tree()
                self.selected_laboratory = lab
                self.selected_kind = NodeKind.LABORATORY
                await self._show_laboratory_detail(lab)
                self._open_creation_worksheet(lab)

        self.app.push_screen(
            FieldsDialog(
                "Create a New Laboratory",
                _laboratory_create_fields(self.saga, covenant.id if covenant else None),
                save_label="Create",
            ),
            handle_result,
        )

    def action_create_familiar(self) -> None:
        if not fam.unbonded_magi(self.saga):
            self.notify("Every magus already has a bound Familiar.")
            return
        # The magus on show is the default. (selected_character outlives it:
        # a laboratory or Spells shown afterwards leaves it set.)
        character = self.selected_character
        default_magus_id = (
            character.id
            if character is not None
            and self.selected_kind == NodeKind.CHARACTER
            and character.type == "magus"
            and self.saga.familiar_of(character.id) is None
            else None
        )

        async def handle_result(values: dict[str, Any] | None) -> None:
            magus = (
                None if values is None else self.saga.character(values["character_id"])
            )
            if values is not None and magus is not None:
                familiar = fam.bind_familiar(
                    self.saga,
                    magus,
                    values["name"],
                    bound=bool(values.get("bound", True)),
                )
                storage.save_saga(self.saga)
                self._rebuild_tree()
                self.selected_familiar = familiar
                self.selected_character = self.saga.character(familiar.character_id)
                self.selected_kind = NodeKind.FAMILIAR
                await self._show_familiar_detail(familiar)

        self.app.push_screen(
            FieldsDialog(
                "Bind a New Familiar",
                _familiar_create_fields(self.saga, default_magus_id),
                save_label="Create",
            ),
            handle_result,
        )

    def action_edit_arms(self) -> None:
        """More's Arms on a covenant, or a lord, town or faction: its shield
        and blazon."""
        record = self._record_to_delete()
        if record is None or not arms.bears_arms(record):
            return
        section = (
            NEIGHBOUR_INFO_SECTION
            if isinstance(record, Neighbour)
            else "section-cov-info"
        )
        run_steps(self.app, arms.arms_form(record), lambda _end: self._commit(section))

    def action_found_covenant(self) -> None:
        """More's Found a Covenant Here on a ruined covenant's site: New
        Covenant, prefilled, raised on the ruin; then its worksheet."""
        record = self._record_to_delete()
        if not isinstance(record, Neighbour) or not places.is_ruin(record):
            return
        before = {c.id for c in self.saga.covenants}

        async def show(covenant: Covenant) -> None:
            self.selected_covenant = covenant
            self.selected_kind = NodeKind.COVENANT
            await self._show_covenant_detail(covenant)
            self._open_creation_worksheet(covenant)

        def finished(_end: object) -> None:
            fresh = [c for c in self.saga.covenants if c.id not in before]
            self._commit(NEIGHBOUR_INFO_SECTION, tree=True)
            if fresh:
                self.run_worker(show(fresh[-1]))

        run_steps(self.app, ruins.found_form(self.saga, record), finished)

    def action_go_to(self) -> None:
        """More's Go To: one of the records the page names, opened."""
        record = self._record_to_delete()
        if record is None:
            return

        def follow(end: object) -> None:
            if isinstance(end, Go):
                self.action_open_ref(end.ref.kind, end.ref.id)

        run_steps(self.app, go_to_forms.go_to(self.saga, record), follow)

    def action_open_ref(self, kind: str, record_id: str) -> None:
        """Open the record a name on the page links to (a click on it, or
        Go To): its node chosen in the tree, the branches above it
        opened."""
        node_kind = _REF_NODES.get(kind)
        tree = self._nav_tree()
        node = (
            _tree_node_with_data(tree, (node_kind, record_id))
            if node_kind is not None
            else None
        )
        if node is None:
            self.notify("That record isn't in the saga's tree.", severity="warning")
            return
        above = node.parent
        while above is not None:
            above.expand()
            above = above.parent
        tree.move_cursor(node)
        tree.select_node(node)

    def action_begin_story(self) -> None:
        """More's Begin This Story on a dormant threat."""
        record = self._record_to_delete()
        if not threats.is_dormant(record):
            return
        assert isinstance(record, Neighbour)
        run_steps(
            self.app,
            threats.begin_command(self.saga, record),
            lambda _end: self._commit(NEIGHBOUR_INFO_SECTION, STAGES_SECTION),
        )

    def action_grow_story(self) -> None:
        """More's Grow into a Threat on the Region's chosen open story."""
        view = self._region_sheet_view
        row = view.section_row(REGION_STORIES_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            open_stories.grow_form(self.saga, row),
            lambda _end: self._commit(REGION_STORIES_SECTION, REGION_THREATS_SECTION),
        )

    def action_delay_threat(self) -> None:
        """More's Delay or Hasten on a threat under way."""
        record = self._record_to_delete()
        if not threats.is_threat(record) or threats.is_dormant(record):
            return
        assert isinstance(record, Neighbour)
        run_steps(
            self.app,
            threats.delay_form(self.saga, record),
            lambda _end: self._commit(NEIGHBOUR_INFO_SECTION, STAGES_SECTION),
        )

    # -- the hunt and Area Lore on a manor (Lords of Men, City & Guild) --

    def _on_manor(self, build: Callable[..., Command]) -> None:
        """Run `build(saga, holder, row)` on the chosen manor."""
        found = self._manors_holder()
        row = found[0].section_row(MANORS_SECTION) if found is not None else None
        if found is None or row is None:
            return
        run_steps(
            self.app,
            build(self.saga, found[1], row),
            lambda _end: self._commit(MANORS_SECTION, DIARY_SECTION),
        )

    def action_hunt_on_manor(self) -> None:
        """More's The Hunt on the chosen manor."""
        self._on_manor(hunting_forms.hunt_on_manor)

    def action_area_lore_on_manor(self) -> None:
        """More's Area Lore in the chosen manor's hinterland."""
        self._on_manor(hunting_forms.area_lore_on_manor)

    # -- a tomb's trap springs (Lands of the Nile) --

    def action_cross_threshold(self) -> None:
        """More's Cross the Threshold on a place with a Faerie aura."""
        view = self._neighbour_sheet_view
        if view is None:
            return
        run_steps(
            self.app,
            threshold_forms.threshold_form(self.saga, view.neighbour),
            lambda _end: self._commit(NEIGHBOUR_INFO_SECTION, DIARY_SECTION),
        )

    def action_overcome_trap(self) -> None:
        """More's Overcome It on a tomb's chosen trap."""
        view = self._neighbour_sheet_view
        row = view.section_row(TOMB_TRAPS_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            tomb_rules.overcome_trap(self.saga, view.neighbour, row),
            lambda _end: self._commit(TOMB_TRAPS_SECTION, DIARY_SECTION),
        )

    def action_overcome_ward(self) -> None:
        """More's Overcome It on a tomb's chosen talisman or ward."""
        view = self._neighbour_sheet_view
        row = view.section_row(TOMB_WARDS_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            tomb_rules.overcome_ward(self.saga, view.neighbour, row),
            lambda _end: self._commit(TOMB_WARDS_SECTION, DIARY_SECTION),
        )

    # -- a lord's marriages --

    def action_end_marriage(self) -> None:
        """More's End a Marriage on a lord's chosen marriage: a lord who
        dies goes on to Settle an Inheritance."""
        view = self._neighbour_sheet_view
        row = view.section_row(MARRIAGES_SECTION) if view is not None else None
        if view is None or row is None:
            return
        run_steps(
            self.app,
            marriages.end_form(self.saga, view.neighbour, row),
            lambda _end: self._commit(
                MARRIAGES_SECTION,
                MARRIAGE_TERMS_SECTION,
                HOUSEHOLD_SECTION,
                NEIGHBOUR_INFO_SECTION,
                DIARY_SECTION,
            ),
        )

    # -- polemic and Charter Strength (Transforming Mythic Europe) --

    def action_circulate_text(self) -> None:
        """More's Circulate a Text on the chosen argument's chosen text."""
        view = self._tribunal_sheet_view
        if view is None:
            return
        run_steps(
            self.app,
            polemic_forms.circulate_form(
                self.saga,
                view.tribunal,
                view.chosen_argument,
                view.section_row(ARGUMENT_TEXTS_SECTION),
            ),
            lambda _end: self._commit(ARGUMENT_TEXTS_SECTION),
        )

    def _charter_lords(self) -> tuple[Neighbour, str, int] | None:
        """The charter whose lord is chosen: a town's, or the covenant's own
        (as the town record its forms act on), its section and the row."""
        view = self._current_sheet_view()
        if view is None:
            return None
        if self.selected_kind == NodeKind.NEIGHBOUR and self._neighbour_sheet_view:
            charter: Neighbour | None = self._neighbour_sheet_view.neighbour
            section = CHARTER_LORDS_SECTION
        else:
            covenant = self.selected_covenant
            charter = town_charter.charter_of(covenant) if covenant else None
            section = COV_CHARTER_LORDS_SECTION
        row = view.section_row(section)
        if charter is None or row is None:
            return None
        return charter, section, row

    def action_draft_charter(self) -> None:
        """More's Draft the Charter on the chosen charter lord."""
        found = self._charter_lords()
        if found is None:
            return
        charter, section, row = found
        run_steps(
            self.app,
            charter_strength_forms.draft_form(self.saga, charter, row),
            lambda _end: self._commit(section),
        )

    def action_seek_loophole(self) -> None:
        """More's Seek a Loophole on the chosen charter lord."""
        found = self._charter_lords()
        if found is None:
            return
        charter, section, row = found
        run_steps(
            self.app,
            charter_strength_forms.loophole_form(self.saga, charter, row),
            lambda _end: self._commit(section),
        )
