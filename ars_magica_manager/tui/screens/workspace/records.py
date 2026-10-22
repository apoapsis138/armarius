"""WorkspaceScreen's actions on the saga's world records: creating each kind of
record from New, and the More menu's record commands (arms, founding a
covenant at a ruin, beginning a dormant story, a Tribunal's cases, fairs and
tables)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from .... import (
    arms,
    character_templates,
    choice_templates,
    creation,
    grog_templates,
    place_events,
    places,
    ruins,
    storage,
    threats,
    towns,
)
from .... import familiars as fam
from ....actions import (
    NodeKind,
)
from ....commands import Go
from ....forms import choice_templates as choice_forms
from ....forms import creation as creation_forms
from ....forms import creature as creature_forms
from ....forms import go_to as go_to_forms
from ....forms import neighbour as neighbour_forms
from ....forms import tribunal as tribunal_forms
from ....markup import escape
from ....models import (
    Character,
    CharacterTemplateDef,
    Covenant,
    Neighbour,
)
from ....sections import (
    CASES_SECTION,
    DIARY_SECTION,
    FAIRS_SECTION,
    NEIGHBOUR_INFO_SECTION,
    STAGES_SECTION,
    TABLES_SECTION,
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
            and fam.familiar_of(self.saga, character.id) is None
            else None
        )

        async def handle_result(values: dict[str, Any] | None) -> None:
            magus = (
                None if values is None else self.saga.character(values["character_id"])
            )
            if values is not None and magus is not None:
                familiar = fam.bind_familiar(self.saga, magus, values["name"])
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
