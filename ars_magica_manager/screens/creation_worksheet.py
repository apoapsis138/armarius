"""The Creation Worksheet (STORY-1302): a step-by-step screen that walks a
covenant, laboratory or character In Creation through the book's order.

The left column is the progress list, one row per step marked with how its
checks stand; the right shows the chosen step: its budget and what's spent,
its creation checks, and buttons for the step's edits. The user moves
freely between steps. The worksheet edits the real record (no draft): its
buttons open the sheet's own dialogs through the workspace, and every
step's checks are worked out again when a dialog closes. The last step's
"Move to In Play" shows every check first.

Each step's story (STORY-1303 to 1313) registers a StepPanel for its step:
the budget text and the buttons. A step with no panel shows its checks.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Label, OptionList, Static
from textual.widgets.option_list import Option

from .. import creation
from ..markup import escape
from ..models import Character, Covenant, Laboratory, Saga
from ..rules import creation as rules
from .fields import ModalDialog
from .prompts import ConfirmScreen

if TYPE_CHECKING:
    from .workspace.screen import WorkspaceScreen

Record = Character | Covenant | Laboratory

MARKS: dict[str, str] = {
    "pass": "[$text-success]✔[/]",
    "warn": "[$text-error]✘[/]",
    "advice": "[$text-warning]![/]",
    "none": "[dim]○[/]",
}


def check_lines(found: list[rules.Check]) -> str:
    """Creation checks as worksheet lines: a mark, the rule, what the record
    has."""
    if not found:
        return "[dim]No creation checks at this step.[/]"
    return "\n".join(
        f"{MARKS[c.status]} {escape(c.label)}: {escape(c.detail)}" for c in found
    )


@dataclass
class StepAction:
    """A button on a step: `run(workspace, record)` opens the dialog that
    edits this part of the record."""

    label: str
    run: Callable[[WorkspaceScreen, Record], None]


@dataclass
class StepPanel:
    """What a step shows above its checks."""

    #: The step's budget and what's spent, as markup (may be "").
    budget: Callable[[Saga, Record], str] = lambda saga, record: ""
    #: The step's buttons for this record.
    actions: Callable[[Saga, Record], list[StepAction]] = lambda saga, record: []


#: (record kind, step key) -> the step's panel; each step's story adds its
#: own. Record kind: "character", "covenant" or "laboratory".
PANELS: dict[tuple[str, str], StepPanel] = {}


def record_kind(record: Record) -> str:
    if isinstance(record, Character):
        return "character"
    if isinstance(record, Covenant):
        return "covenant"
    return "laboratory"


def panel_for(record: Record, step: str) -> StepPanel:
    return PANELS.get((record_kind(record), step), StepPanel())


class CreationWorksheetScreen(ModalDialog[None]):
    """The worksheet for `record`, opened from its sheet's top panel while
    it is In Creation. Escape closes it; everything is saved as it's
    edited."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Close")]

    DEFAULT_CSS = """
    CreationWorksheetScreen {
        align: center middle;
    }

    #ws-dialog {
        width: 118;
        max-width: 100%;
        height: 40;
        max-height: 100%;
        border: round $accent;
        padding: 0 1;
        background: $surface;
    }

    #ws-title {
        width: 100%;
        height: 1;
        text-style: bold;
    }

    #ws-body {
        height: 1fr;
    }

    #ws-steps-column {
        width: 30;
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

    /* One button a row: a step can have several, and a row of them
       would run off the dialog. */
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
        self, workspace: WorkspaceScreen, record: Record, step: str | None = None
    ) -> None:
        super().__init__()
        self.workspace = workspace
        self.saga = workspace.saga
        self.record = record
        steps = rules.steps_for(record)
        self.steps = steps
        keys = [s.key for s in steps]
        self.step = step if step in keys else keys[0]
        self._busy = asyncio.Lock()

    # -- composing --

    def compose(self) -> ComposeResult:
        with Vertical(id="ws-dialog"):
            yield Label("", id="ws-title")
            with Horizontal(id="ws-body"):
                with Vertical(id="ws-steps-column"):
                    yield OptionList(*self._step_options(), id="ws-steps", compact=True)
                    yield Static("", id="ws-progress")
                with VerticalScroll(id="ws-step"):
                    yield Label("", id="ws-step-title")
                    yield Static("", id="ws-budget")
                    yield Static("", id="ws-checks")
                    yield Vertical(id="ws-actions")
            yield Label(
                "Up/Down: step · Tab: the step's buttons · Escape: close "
                "(everything is saved as you go)",
                id="ws-hint",
            )

    async def on_mount(self) -> None:
        steps = self.query_one("#ws-steps", OptionList)
        steps.highlighted = [s.key for s in self.steps].index(self.step)
        steps.focus()
        await self._refresh()

    def _step_options(self) -> list[Option]:
        return [Option(self._step_prompt(step), id=step.key) for step in self.steps]

    def _step_prompt(self, step: rules.Step) -> str:
        found = rules.checks(self.saga, self.record, step.key)
        return f"{MARKS[rules.step_status(found)]} {step.title}"

    # -- refreshing --

    def on_screen_resume(self) -> None:
        # A dialog opened from a step's button has closed: the record may
        # have changed. Its result is handled around now, so look once the
        # screen has settled.
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
        mode = "In Creation" if record.in_creation else "In Play"
        self.query_one("#ws-title", Label).update(
            f"Creation Worksheet: {escape(record.name)} ({mode})"
        )
        steps = self.query_one("#ws-steps", OptionList)
        for position, step in enumerate(self.steps):
            steps.replace_option_prompt_at_index(position, self._step_prompt(step))
        statuses = [
            rules.step_status(rules.checks(self.saga, record, s.key))
            for s in self.steps
        ]
        # Steps with no checks (a review) don't count either way.
        checked = [status for status in statuses if status != "none"]
        done = sum(status == "pass" for status in checked)
        found = rules.checks(self.saga, record)
        self.query_one("#ws-progress", Static).update(
            f"{done} of {len(checked)} steps pass\n{rules.summary(found)}"
        )
        await self._show_step_now()

    async def _show_step(self) -> None:
        async with self._busy:
            await self._show_step_now()

    async def _show_step_now(self) -> None:
        step = next(s for s in self.steps if s.key == self.step)
        panel = panel_for(self.record, step.key)
        self.query_one("#ws-step-title", Label).update(step.title)
        self.query_one("#ws-budget", Static).update(
            panel.budget(self.saga, self.record)
        )
        found = rules.checks(self.saga, self.record, step.key)
        self.query_one("#ws-checks", Static).update(check_lines(found))
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

    async def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        key = event.option.id
        if event.option_list.id == "ws-steps" and key and key != self.step:
            self.step = key
            await self._show_step()

    # -- buttons --

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        event.stop()
        if button_id == "ws-play":
            self._move_to_play()
        elif button_id.startswith("ws-action-"):
            panel = panel_for(self.record, self.step)
            actions = panel.actions(self.saga, self.record)
            actions[int(button_id.removeprefix("ws-action-"))].run(
                self.workspace, self.record
            )

    def _move_to_play(self) -> None:
        """Show the review of every check, then move the record to In Play
        (with strict creation rules, not while a must is broken)."""
        record = self.record
        if not record.in_creation:
            self.notify(f"{escape(record.name)} is already In Play.")
            return
        found = rules.checks(self.saga, record)
        if not rules.can_move_to_play(self.saga, record):
            self.notify(
                f"{escape(record.name)} stays In Creation: it breaks "
                f"{len(rules.broken_musts(found))} creation rule(s) it must "
                "follow, and this saga enforces them strictly.",
                severity="warning",
            )
            return
        open_checks = [c for c in found if c.status != "pass"]
        review = "\n".join(
            f"{MARKS[c.status]} {escape(c.label)}" for c in open_checks[:12]
        )
        if len(open_checks) > 12:
            review += f"\n...and {len(open_checks) - 12} more"
        message = f"Move {escape(record.name)} to In Play? Creation checks: {rules.summary(found)}."
        if review:
            message += f"\n\n{review}"

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                creation.set_in_creation(self.saga, record, False)
                self.workspace._commit("section-creation", tree=True)
                self.dismiss(None)

        self.app.push_screen(
            ConfirmScreen(message, yes_label="Move to In Play", yes_variant="primary"),
            handle_confirmed,
        )


# The step panels register themselves on import.
from . import creation_steps  # noqa: F401
