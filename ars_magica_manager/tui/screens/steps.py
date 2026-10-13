"""Running the core's command steps (commands.py) in the terminal: a Form
as a FieldsDialog, a Choose as a searchable list (`ChooseScreen`, F3
listing what isn't offered too), a Confirm as a ConfirmScreen; an Act runs
at once and a Refuse is shown as a warning. The desktop runs the same
steps in its own dialogs (gui/forms.py), so a button whose steps live in
the core behaves the same in both."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, ClassVar

from textual.app import App
from textual.widgets import Static

from ...commands import Act, Choice, Choose, Confirm, Form, Refuse
from .fields import FieldsDialog
from .pickers import SearchablePickerScreen
from .prompts import ConfirmScreen, terminal_fields


class ChooseScreen(SearchablePickerScreen[int, int | None]):
    """A core Choose: its choices, searchable, with the highlighted one's
    details under the list; F3 lists the ones not offered too (each marked
    with why). Dismisses with the chosen entry's index into `choices`
    followed by `others`, or None."""

    LIST_VIEW_ID: ClassVar[str] = "choose-list"
    DETAILS_HEIGHT: ClassVar[int] = 10

    def __init__(self, step: Choose, choices: list[Choice]) -> None:
        super().__init__(step.title, empty_message=step.empty)
        self.choices = choices
        self.others = step.others() if step.others is not None else []
        self._narrowed = bool(self.others)

    def _all(self) -> list[Choice]:
        return [*self.choices, *self.others]

    def _load_entries(self) -> list[int]:
        return list(range(len(self._all())))

    def _in_play(self, entry: int) -> bool:
        # The others are marked already (commands.not_offered).
        return True

    def _candidates(self) -> list[int]:
        self._other_books = len(self.others)
        if self._show_other_books:
            return self._entries
        return [entry for entry in self._entries if entry < len(self.choices)]

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
    or None. Cancelling any step stops there (`done` isn't called); a
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

        app.push_screen(
            FieldsDialog(
                form.title,
                terminal_fields(form.fields()),
                validate=form.validate,
                live=form.live,
                save_label=form.save_label,
            ),
            handle_values,
        )
        return
    if isinstance(step, Choose):
        choose = step
        choices = choose.choices()
        if not choices and choose.others is None:
            warn(choose.title, choose.empty)
            return
        screen = ChooseScreen(choose, choices)

        def handle_index(index: int | None) -> None:
            if index is not None:
                run_steps(app, choose.apply(screen.value_of(index)), done, notify)

        app.push_screen(screen, handle_index)
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
    done(step)
