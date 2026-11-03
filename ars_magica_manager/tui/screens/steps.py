"""Running the core's command steps (commands.py) in the terminal: a Form
as a FieldsDialog, a Choose as a searchable list (`ChooseScreen`, F3
listing what isn't offered too), a Confirm as a ConfirmScreen, a ChooseFile as the
list of files (CsvFilePickerScreen); an Act runs at once and a Refuse is shown as a warning. The desktop runs the same
steps in its own dialogs (gui/forms.py), so a button whose steps live in
the core behaves the same in both."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal
from textual.widgets import Input, Select, Static

from ...commands import (
    RECENT,
    Act,
    Choice,
    Choose,
    ChooseFile,
    Confirm,
    Form,
    Refuse,
    Then,
    filter_values,
    heading,
    passes,
)
from ...markup import escape
from ..heraldry import beside
from .fields import FieldsDialog
from .pickers import CsvFilePickerScreen, SearchablePickerScreen
from .prompts import ConfirmScreen, terminal_fields


class ChooseScreen(SearchablePickerScreen[int, int | None]):
    """A core Choose: its choices, searchable, with the highlighted one's
    details under the list; F3 lists the ones not offered too (each marked
    with why). A Choose with filters gets a drop-down for each above the
    list (F2 steps through the first), the list headed by each entry's
    value of the first, and its recent entries first while nothing narrows
    it. Dismisses with the chosen entry's index into its entries, or None
    (`value_of` gives the value)."""

    LIST_VIEW_ID: ClassVar[str] = "choose-list"
    DETAILS_HEIGHT: ClassVar[int] = 10

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("f2", "next_filter_value", "Next type", show=False),
    ]

    DEFAULT_CSS = """
    ChooseScreen #choose-filters {
        width: 1fr;
        height: 1;
        margin: 0 0 1 0;
    }

    ChooseScreen #choose-filters Select {
        width: 36;
        margin-right: 2;
    }
    """

    def __init__(self, step: Choose, choices: list[Choice]) -> None:
        super().__init__(step.title, empty_message=step.empty)
        self.step = step
        self.choices = choices
        self.others = step.others() if step.others is not None else []
        self.recent = step.recent() if step.recent is not None else []
        self._narrowed = bool(self.others)
        #: Each filter's chosen value (None: any).
        self.chosen: dict[str, str | None] = dict.fromkeys(step.filters)

    def _all(self) -> list[Choice]:
        return [*self.choices, *self.others, *self.recent]

    def _is_recent(self, entry: int) -> bool:
        return entry >= len(self.choices) + len(self.others)

    def _load_entries(self) -> list[int]:
        return list(range(len(self._all())))

    def _in_play(self, entry: int) -> bool:
        # The others are marked already (commands.not_offered).
        return True

    def _candidates(self) -> list[int]:
        self._other_books = len(self.others)
        listed = len(self.choices) + (len(self.others) if self._show_other_books else 0)
        found = [
            entry for entry in range(listed) if passes(self._all()[entry], self.chosen)
        ]
        if any(value is not None for value in self.chosen.values()):
            return found
        return [entry for entry in self._entries if self._is_recent(entry)] + found

    def _match(self, entries: list[int], needle: str) -> list[int]:
        return super()._match(
            [entry for entry in entries if not self._is_recent(entry)], needle
        )

    def _heading(self, entry: int) -> str:
        return (
            RECENT if self._is_recent(entry) else heading(self.step, self._all()[entry])
        )

    def _compose_filters(self) -> ComposeResult:
        if not self.step.filters:
            return
        with Horizontal(id="choose-filters"):
            for index, name in enumerate(self.step.filters):
                yield Select(
                    [
                        (escape(f"{name}: {v}"), v)
                        for v in filter_values(self.choices, name)
                    ],
                    prompt=f"{name}: any",
                    id=f"choose-filter-{index}",
                    compact=True,
                )

    def action_next_filter_value(self) -> None:
        """The first filter's next value, after the last back to any."""
        if not self.step.filters:
            return
        name = self.step.filters[0]
        values: list[str | None] = [None, *filter_values(self.choices, name)]
        following = values[(values.index(self.chosen[name]) + 1) % len(values)]
        select = self.query_one("#choose-filter-0", Select)
        if following is None:
            select.clear()
        else:
            select.value = following

    async def on_select_changed(self, event: Select.Changed) -> None:
        event.stop()
        index = int((event.select.id or "").removeprefix("choose-filter-"))
        value = event.value if isinstance(event.value, str) else None
        self.chosen[self.step.filters[index]] = value
        await self._render_list(self.query_one("#picker-search", Input).value)

    def _update_books_note(self) -> None:
        if not self._narrowed:
            return
        shown = "listed (F3 hides them)" if self._show_other_books else "hidden"
        hint = "" if self._show_other_books else " (F3 shows them)"
        self.query_one("#picker-books", Static).update(
            f"{len(self.others)} not offered here {shown}{hint}"
        )

    def _search_text(self, entry: int) -> str:
        choice = self._all()[entry]
        return f"{choice.label} {choice.search}"

    def _label_for(self, entry: int) -> str:
        return self._all()[entry].label

    def _item_id(self, entry: int) -> str:
        return f"choice-{entry}"

    def _details(self, entry: int) -> str:
        return self._all()[entry].detail

    def _on_entry_selected(self, entry: int) -> None:
        self.dismiss(entry)

    def value_of(self, index: int) -> Any:
        return self._all()[index].value


def run_steps(
    app: App[Any],
    step: object,
    done: Callable[[object], None],
    notify: Callable[[str, str], None] | None = None,
) -> None:
    """Show `step` and each step it leads to; once the last is answered,
    `done(what it ended with)`: a list of notes, a commands.Picked value,
    or None. A commands.Then calls `done(None)` and goes on to its step.
    Cancelling any step stops there (`done` isn't called); a
    Refuse is told with `notify(title, why)` (a warning by default) and
    stops too, as it changed nothing."""

    def warn(title: str, why: str) -> None:
        if notify is not None:
            notify(title, why)
        else:
            app.notify(why, title=title, severity="warning")

    while isinstance(step, Act):
        step = step.apply()
    if isinstance(step, Refuse):
        warn(step.title, step.why)
        return
    if isinstance(step, Form):
        form = step

        def handle_values(values: dict[str, Any] | None) -> None:
            if values is not None:
                run_steps(app, form.apply(values), done, notify)

        dialog = FieldsDialog(
            form.title,
            terminal_fields(form.fields()),
            validate=form.validate,
            live=_with_picture(form),
            inspector=form.inspector,
            save_label=form.save_label,
            cancel_label=form.cancel_label,
        )
        dialog.help_id = form.help_id or None
        app.push_screen(dialog, handle_values)
        return
    if isinstance(step, Choose):
        choose = step
        choices = choose.choices()
        if not choices and choose.others is None:
            warn(choose.title, choose.empty)
            return
        screen = ChooseScreen(choose, choices)
        screen.help_id = choose.help_id or None

        def handle_index(index: int | None) -> None:
            if index is not None:
                run_steps(app, choose.apply(screen.value_of(index)), done, notify)

        app.push_screen(screen, handle_index)
        return
    if isinstance(step, ChooseFile):
        choose_file = step

        def handle_path(path: Path | None) -> None:
            if path is not None:
                run_steps(app, choose_file.apply(path), done, notify)

        app.push_screen(
            CsvFilePickerScreen(step.title, step.start, suffix=step.suffixes),
            handle_path,
        )
        return
    if isinstance(step, Confirm):
        confirm = step

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                run_steps(app, confirm.apply(), done, notify)

        variant = "error" if confirm.yes_label in ("Delete", "Remove") else "primary"
        app.push_screen(
            ConfirmScreen(
                confirm.question, yes_label=confirm.yes_label, yes_variant=variant
            ),
            handle_confirmed,
        )
        return
    if isinstance(step, Then):
        # The steps so far are kept (saved and redrawn), then the next.
        done(None)
        run_steps(app, step.step, done, notify)
        return
    done(step)


def _with_picture(form: Form) -> Callable[[dict[str, Any]], str] | None:
    """The form's live line, with its picture (a shield) drawn beside it in
    half-blocks."""
    live, picture = form.live, form.picture
    if picture is None:
        return live
    return lambda values: beside(picture(values), live(values) if live else "")
