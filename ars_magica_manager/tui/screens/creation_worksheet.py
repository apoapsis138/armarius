"""The Creation Worksheet: a step-by-step screen that walks a
covenant, laboratory or character In Creation through the book's order.

It fills the screen. The left column is the progress list, one row per step
marked with how its checks stand; the right shows the chosen step: its
budget and what's spent, the step's list (what was spent or taken there),
its creation checks and buttons for the step's other edits, with the
chosen row's details docked below. a adds to the step's list, e edits the
chosen row and d takes it back, as on every list of the sheets. The user
moves freely between steps. The worksheet edits the real record (no
draft): its keys and buttons open the sheet's own dialogs through the
workspace, and every step's checks are worked out again when a dialog
closes. The last step's "Move to In Play" shows every check first.

What each step shows and does comes from the core's worksheet
(worksheet.py), which the desktop draws too: its buttons and rows start
the core's command steps, run here in the terminal's own dialogs
(steps.py).
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Label, OptionList, Static
from textual.widgets.option_list import Option

from ... import worksheet as ws
from ...commands import Command
from ...forms import worksheet as wf
from ...rules import creation as rules
from .fields import ModalDialog
from .widgets import DetailsPanel, SelectableList, TableHeader

if TYPE_CHECKING:
    from .workspace.screen import WorkspaceScreen


class CreationWorksheetScreen(ModalDialog[None]):
    """The worksheet for `record`, opened from its sheet's top panel while
    it is In Creation (and on its own when the record is made). Escape
    closes it; everything is saved as it's edited."""

    help_id = "creation-worksheet"

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "cancel", "Close"),
        Binding("a", "add", "Add", show=False),
        Binding("e", "edit", "Edit", show=False),
        Binding("d", "delete", "Delete", show=False),
    ]

    DEFAULT_CSS = """
    CreationWorksheetScreen {
        align: center middle;
    }

    #ws-dialog {
        width: 100%;
        height: 100%;
        padding: 0 1;
    }

    #ws-title {
        height: auto;
    }

    #ws-body {
        height: 1fr;
    }

    #ws-steps-column {
        width: 28;
        height: 1fr;
        margin-right: 2;
    }

    #ws-steps {
        height: auto;
        max-height: 1fr;
    }

    #ws-progress {
        height: auto;
        margin-top: 1;
        color: $text-muted;
    }

    #ws-step-column {
        width: 1fr;
        height: 1fr;
    }

    #ws-step {
        width: 1fr;
        height: 1fr;
    }

    #ws-step-title {
        height: 1;
        text-style: bold;
    }

    #ws-budget, #ws-checks {
        height: auto;
        margin-top: 1;
    }

    #ws-list-header {
        margin-top: 1;
    }

    #ws-list, #ws-list:focus {
        max-height: 100;
    }

    /* One button a row: a step can have several, and a row of them
       would run off the screen. */
    #ws-actions {
        width: 100%;
        height: auto;
        margin-top: 1;
    }

    #ws-actions Button {
        margin-bottom: 1;
        min-width: 0;
    }

    #ws-hint {
        height: 1;
        color: $text-muted;
    }
    """

    def __init__(
        self, workspace: WorkspaceScreen, record: wf.Record, step: str | None = None
    ) -> None:
        super().__init__()
        self.workspace = workspace
        self.saga = workspace.saga
        self.record = record
        steps = rules.steps_for(record)
        self.steps = steps
        keys = [s.key for s in steps]
        self.step = step if step in keys else keys[0]
        #: The rows of the step's list on show, by data index.
        self._rows: list[ws.Row] = []
        self._busy = asyncio.Lock()

    # -- composing --

    def compose(self) -> ComposeResult:
        with Vertical(id="ws-dialog", classes="dialog-box"):
            yield Label("", id="ws-title", classes="dialog-title")
            with Horizontal(id="ws-body"):
                with Vertical(id="ws-steps-column"):
                    yield OptionList(*self._step_options(), id="ws-steps", compact=True)
                    yield Static("", id="ws-progress")
                with Vertical(id="ws-step-column"):
                    yield Label("", id="ws-step-title")
                    with VerticalScroll(id="ws-step", can_focus=False):
                        yield Static("", id="ws-budget")
                        yield TableHeader("", id="ws-list-header")
                        yield SelectableList(id="ws-list")
                        yield Static("", id="ws-checks")
                        yield Vertical(id="ws-actions")
                    yield DetailsPanel("", id="ws-details")
            yield Label("", id="ws-hint")

    async def on_mount(self) -> None:
        steps = self.query_one("#ws-steps", OptionList)
        steps.highlighted = [s.key for s in self.steps].index(self.step)
        steps.focus()
        await self._refresh()

    def _step_options(self) -> list[Option]:
        return [Option(self._step_prompt(step), id=step.key) for step in self.steps]

    def _step_prompt(self, step: rules.Step) -> str:
        return ws.step_label(self.saga, self.record, step)

    # -- refreshing --

    def on_screen_resume(self) -> None:
        # A dialog opened from a step's key or button has closed: the record
        # may have changed. Its result is handled around now, so look once
        # the screen has settled.
        self.call_after_refresh(self._refresh)

    def record_changed(self) -> None:
        """The workspace saved a change (see WorkspaceBase._commit)."""
        self.call_after_refresh(self._refresh)

    async def _refresh(self) -> None:
        # Refreshes can overlap (a dialog closing, then its save): one at a
        # time, or two rebuilds of the step's buttons would collide.
        async with self._busy:
            await self._refresh_now()

    async def _refresh_now(self) -> None:
        if not self.is_attached or self not in self.app.screen_stack:
            return  # closed since the refresh was asked for
        record = self.record
        self.query_one("#ws-title", Label).update(ws.title(record))
        steps = self.query_one("#ws-steps", OptionList)
        now = rules.steps_for(record)
        if [s.key for s in now] != [s.key for s in self.steps]:
            # A change of type or tradition adds or drops a step.
            self.steps = now
            keys = [s.key for s in now]
            self.step = self.step if self.step in keys else keys[0]
            with self.prevent(OptionList.OptionHighlighted):
                steps.clear_options()
                steps.add_options(self._step_options())
                steps.highlighted = keys.index(self.step)
        else:
            for position, step in enumerate(self.steps):
                steps.replace_option_prompt_at_index(position, self._step_prompt(step))
        self.query_one("#ws-progress", Static).update(
            ws.progress_text(self.saga, record)
        )
        await self._show_step_now(keep_row=True)

    async def _show_step(self) -> None:
        async with self._busy:
            await self._show_step_now(keep_row=False)

    async def _show_step_now(self, *, keep_row: bool) -> None:
        step = next(s for s in self.steps if s.key == self.step)
        panel = ws.panel_for(self.record, step.key)
        self.query_one("#ws-step-title", Label).update(step.title)
        self.query_one("#ws-budget", Static).update(
            panel.budget(self.saga, self.record)
        )
        self._show_list(panel.list, keep_row=keep_row)
        found = rules.checks(self.saga, self.record, step.key)
        self.query_one("#ws-checks", Static).update(ws.check_lines(found))
        actions = self.query_one("#ws-actions", Vertical)
        await actions.remove_children()
        buttons = [
            Button(action.label, id=f"ws-action-{i}", compact=True)
            for i, action in enumerate(panel.actions(self.saga, self.record))
        ]
        if step is self.steps[-1]:
            buttons.append(
                Button("Move to In Play", id="ws-play", variant="primary", compact=True)
            )
        await actions.mount_all(buttons)
        self._show_hint()

    def _show_list(self, step_list: ws.StepList | None, *, keep_row: bool) -> None:
        """The step's list and its details panel (both hidden without one);
        `keep_row`: choose the row at the same place again (after an edit)."""
        header = self.query_one("#ws-list-header", TableHeader)
        listing = self.query_one("#ws-list", SelectableList)
        details = self.query_one(DetailsPanel)
        for widget in (header, listing, details):
            widget.display = step_list is not None
        if step_list is None:
            self._rows = []
            return
        position = listing.highlighted if keep_row else None
        self._rows = step_list.rows(self.saga, self.record)
        header.update(step_list.header)
        listing.set_rows(
            [
                (None if row.heading else index, row.label)
                for index, row in enumerate(self._rows)
            ]
        )
        if position is not None and listing.row_count:
            listing.choose_near(min(position, listing.row_count - 1))
        self._show_details()

    def _chosen_row(self) -> ws.Row | None:
        index = self.query_one("#ws-list", SelectableList).selected_data_index
        if index is None or index >= len(self._rows):
            return None
        return self._rows[index]

    def _show_details(self) -> None:
        step_list = ws.panel_for(self.record, self.step).list
        row = self._chosen_row()
        if row is not None:
            text = row.details
        else:
            text = f"[dim]{step_list.hint if step_list else ''}[/]"
        self.query_one("#ws-details", Static).update(text)

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        event.stop()
        self._show_details()
        self._show_hint()

    def _show_hint(self) -> None:
        """The key line: what a, e and d do on this step."""
        step_list = ws.panel_for(self.record, self.step).list
        keys = []
        if step_list is not None:
            if step_list.add is not None:
                keys.append(f"a: {step_list.add_label}")
            if step_list.edit_label is not None:
                keys.append(f"e: {step_list.edit_label}")
            keys.append(f"d: {step_list.delete_label}")
        keys += ["Tab: next part", "Escape: close (saved as you go)"]
        self.query_one("#ws-hint", Label).update(" · ".join(keys))

    async def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        key = event.option.id
        if event.option_list.id == "ws-steps" and key and key != self.step:
            self.step = key
            await self._show_step()

    # -- a / e / d on the step's list --

    def action_add(self) -> None:
        step_list = ws.panel_for(self.record, self.step).list
        if step_list is None or step_list.add is None:
            return
        self._run(step_list.add(self.saga, self.record))

    def action_edit(self) -> None:
        self._act_on_row("edit")

    def action_delete(self) -> None:
        self._act_on_row("delete")

    def _act_on_row(self, verb: str) -> None:
        if ws.panel_for(self.record, self.step).list is None:
            return
        row = self._chosen_row()
        if row is None:
            self.notify("Choose a row first.")
            return
        act = row.edit if verb == "edit" else row.delete
        if act is None:
            self.notify(
                f"That row can't be {'changed' if verb == 'edit' else 'taken back'} here."
            )
            return
        self._run(act())

    # -- buttons --

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        event.stop()
        if button_id == "ws-play":
            self._move_to_play()
        elif button_id.startswith("ws-action-"):
            panel = ws.panel_for(self.record, self.step)
            actions = panel.actions(self.saga, self.record)
            self._run(actions[int(button_id.removeprefix("ws-action-"))].start())

    def _run(self, command: Command) -> None:
        self.workspace._run_steps(command)

    def _move_to_play(self) -> None:
        """Show the review of every check, then move the record to In Play
        (with strict creation rules, not while a must is broken) and close
        the worksheet."""

        def moved() -> None:
            if not self.record.in_creation and self.is_attached:
                self.dismiss(None)

        self.workspace._run_steps(
            wf.move_to_play(self.saga, self.record), tree=True, then=moved
        )
