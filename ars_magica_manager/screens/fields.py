"""The modal-dialog base and the config-driven FieldsDialog form, with the
small helpers form builders share."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any, ClassVar, cast, overload

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Checkbox,
    Input,
    Label,
    Select,
    Static,
    TextArea,
)

from ..markup import escape
from ..models import (
    Saga,
)


def _year_born_field(value: int | None) -> DialogField:
    """Year Born is never required: blank means Unknown."""
    return DialogField("year_born", "Year Born (blank = Unknown)", "optint", value)


def _pairs(values: Iterable[str]) -> list[tuple[str, str]]:
    """Select options whose label is the value itself."""
    return [(value, value) for value in values]


def _covenant_options(saga: Saga) -> list[tuple[str, str]]:
    """Select options for choosing one of the saga's covenants."""
    return [(escape(c.name), c.id) for c in saga.covenants]


#: The hint under every free-text field that is shown with markdown_inline.
_EMPHASIS_HINT = "Supports **bold** and *italic*."


def _description_field(value: str) -> DialogField:
    """The multi-line Description field most forms end with."""
    return DialogField("description", "Description", "area", value, hint=_EMPHASIS_HINT)


def _attr(record: object | None, attribute: str, default: Any) -> Any:
    """`record.attribute`, or `default` when there's no record yet (a form
    opened to add one)."""
    return getattr(record, attribute) if record is not None else default


class ModalDialog[ResultT](ModalScreen[ResultT]):
    """Base of the app's modal dialogs: Escape (or a dialog's Cancel button
    calling action_cancel) dismisses with CANCEL_RESULT."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "cancel", "Cancel"),
        # Help; a field being typed in takes the ? first.
        Binding("question_mark", "app.help", "Help", show=False),
    ]

    # Every dialog's box (its outer container has class "dialog-box") and
    # title ("dialog-title"); each dialog sets its own size and padding.
    # Their theme colours are in styles.py.
    DEFAULT_CSS = """
    ModalDialog .dialog-box {
        border: round $accent;
        background: $surface;
    }

    ModalDialog .dialog-title {
        width: 100%;
        text-style: bold;
    }
    """

    #: What the dialog dismisses with when cancelled.
    CANCEL_RESULT: ClassVar[Any] = None

    #: The dialog's own help page (help/*.md), if it has one; without one,
    #: Help shows the page of the screen it was opened from.
    help_id: str | None = None

    def action_cancel(self) -> None:
        self.dismiss(self.CANCEL_RESULT)

    def help_context(self) -> Any:
        """What Help opens on here (a screens.help.HelpContext), or None to
        show the screen below's."""
        if self.help_id is None:
            return None
        from .help import HelpContext  # help.py builds on this module

        return HelpContext([self.help_id])

    def _select_value(self, selector: str) -> str | None:
        """The chosen value of the Select at `selector`, or None if blank."""
        value = self.query_one(selector, Select).value
        return value if isinstance(value, str) else None


@dataclass
class DialogField:
    """One row of a FieldsDialog.

    `kind`: "text" (a stripped string), "secret" (text shown as dots: a
    passcode), "int" (a whole number), "optint" (a
    whole number or blank -> None), "optfloat" (a number, decimals allowed,
    or blank -> None), "select" (one of `options` as (label,
    value) pairs; blank -> None when `allow_blank`; a stored value that isn't
    among them is offered as "... (not in the list)"), "check" (a boolean),
    "area" (multi-line text, trailing whitespace dropped), "picker" (a button showing `display(value)`
    that opens the screen `picker(value)` returns; its result becomes the
    value; Delete clears it when `allow_blank`) or "info" (read-only text,
    not returned).
    """

    key: str
    label: str
    kind: str
    value: object = None
    options: list[tuple[str, str]] = dataclass_field(default_factory=list)
    required: bool = False
    allow_blank: bool = False
    placeholder: str = ""
    hint: str = ""
    #: Shown only while this returns True for the form's current values
    #: (`FieldsDialog.current_values`); re-checked as the user edits. A hidden
    #: field is left out of the result and isn't checked.
    show_if: Callable[[dict[str, Any]], bool] | None = None
    #: A "picker" field's chooser (a screen dismissing with the new value, or
    #: None to keep the old one) and how it shows its value on the button.
    picker: Callable[[Any], Screen[Any]] | None = None
    display: Callable[[Any], str] | None = None
    #: Suggested values for other fields when the user changes this one
    #: (`FieldsDialog.current_values` -> {key: value}; None blanks a
    #: number field). Never run as the form opens, so a record's own
    #: figures stay until its source field is changed; the user can still
    #: edit what it filled.
    fills: Callable[[dict[str, Any]], dict[str, Any]] | None = None


class _FieldError(ValueError):
    """A field's text doesn't parse; the message is shown under the form."""


def _parse_int(spec: DialogField, raw: str) -> int | None:
    if not raw and spec.kind == "optint":
        return None
    try:
        return int(raw)
    except ValueError:
        raise _FieldError(f"{spec.label} must be a whole number.") from None


def _parse_float(spec: DialogField, raw: str) -> float | None:
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        raise _FieldError(f"{spec.label} must be a number.") from None


#: Field kinds whose widget text becomes a number. Every other kind's value is
#: what FieldsDialog._read gets from its widget.
_PARSERS: dict[str, Callable[[DialogField, str], Any]] = {
    "int": _parse_int,
    "optint": _parse_int,
    "optfloat": _parse_float,
}


class FieldsDialog[ResultT = dict[str, Any]](ModalDialog[ResultT | None]):
    """A config-driven form: one compact row per DialogField, scrolling if the
    terminal is short (Save/Cancel stay put). Dismisses with {key: value} for
    every non-info field, or None if cancelled. `validate` gets the finished
    dict and returns an error message, or None if it's fine. `save_label`
    names the button that completes it ("Save", "Create"...). With `build`,
    it dismisses with `build(values)` instead (e.g. a finished record). With
    `confirm`, saving first opens the screen it returns for the values (a
    ConfirmScreen) and the form stays open unless that answers yes.

    Fields can depend on each other while the form is open: a field's
    `show_if` shows/hides it, and `live` (markup, from the current values)
    fills a line above the error, both refreshed on every change; a
    field's `fills` suggests other fields' values when the user changes
    it."""

    DEFAULT_CSS = """
    FieldsDialog {
        align: center middle;
    }

    #fields-dialog {
        width: 84;
        max-width: 100%;
        height: auto;
        max-height: 100%;
        padding: 1 2;
    }

    #fields-scroll {
        height: auto;
    }

    .fd-field {
        width: 100%;
        height: auto;
    }

    .fd-row {
        width: 100%;
        height: 1;
    }

    .fd-label {
        width: 30;
    }

    .fd-row Input, .fd-row Select, .fd-row .fd-picker {
        width: 1fr;
    }

    .fd-row .fd-picker {
        content-align: left middle;
        text-align: left;
    }

    /* A number needs a few columns, not the row: a short well breaks up a
       long form's run of fields. */
    .fd-row Input.fd-number {
        width: 10;
    }

    .fd-value {
        width: 1fr;
        color: $text-muted;
    }

    .fd-area-label {
        margin-top: 1;
    }

    .fd-area {
        height: 6;
    }

    .fd-hint {
        color: $text-muted;
        height: auto;
    }

    /* A field's hint sits under the field, past its label (.fd-label). */
    .fd-row-hint {
        padding-left: 30;
    }

    #fields-live {
        height: auto;
        margin-top: 1;
    }

    #fields-error {
        color: $error;
        height: auto;
    }

    #fields-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    # Without `build` the dialog dismisses with its values dict, so it can
    # only be a FieldsDialog[dict[str, Any]]; with `build`, whatever that
    # returns. (The overloads let pyright catch a FieldsDialog[Record] that
    # forgot its `build`.)
    @overload
    def __init__(
        self: FieldsDialog[dict[str, Any]],
        title: str,
        fields: list[DialogField],
        *,
        validate: Callable[[dict[str, Any]], str | None] | None = None,
        live: Callable[[dict[str, Any]], str] | None = None,
        save_label: str = "Save",
        build: None = None,
        confirm: Callable[[dict[str, Any]], Screen[bool]] | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        title: str,
        fields: list[DialogField],
        *,
        validate: Callable[[dict[str, Any]], str | None] | None = None,
        live: Callable[[dict[str, Any]], str] | None = None,
        save_label: str = "Save",
        build: Callable[[dict[str, Any]], ResultT],
        confirm: Callable[[dict[str, Any]], Screen[bool]] | None = None,
    ) -> None: ...

    def __init__(
        self,
        title: str,
        fields: list[DialogField],
        *,
        validate: Callable[[dict[str, Any]], str | None] | None = None,
        live: Callable[[dict[str, Any]], str] | None = None,
        save_label: str = "Save",
        build: Callable[[dict[str, Any]], ResultT] | None = None,
        confirm: Callable[[dict[str, Any]], Screen[bool]] | None = None,
    ) -> None:
        super().__init__()
        self.title_text = title
        self.fields = fields
        self.validate = validate
        self.live = live
        self.save_label = save_label
        self.build = build
        self.confirm = confirm
        self._picked: dict[str, Any] = {}  # "picker" fields' current values
        # The value each `fills` field last filled from (or opened with).
        self._filled_from: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        with Vertical(id="fields-dialog", classes="dialog-box"):
            yield Label(self.title_text, id="fields-title", classes="dialog-title")
            # The scroll itself never takes focus, so the first field has it
            # as the form opens and typing goes there (found
            # signing in over SSH, where the first letters went nowhere).
            with VerticalScroll(id="fields-scroll", can_focus=False):
                for spec in self.fields:
                    with Vertical(classes="fd-field", id=f"fdw-{spec.key}"):
                        yield from self._widgets(spec)
            if self.live is not None:
                yield Static("", id="fields-live")
            yield Static("", id="fields-error")
            with Horizontal(id="fields-buttons"):
                yield Button(self.save_label, id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def _widgets(self, spec: DialogField) -> ComposeResult:
        widget_id = f"fld-{spec.key}"
        if spec.kind == "area":
            yield Label(spec.label, classes="fd-area-label")
            yield TextArea(str(spec.value or ""), id=widget_id, classes="fd-area")
            if spec.hint:
                yield Static(spec.hint, classes="fd-hint")
            return
        with Horizontal(classes="fd-row"):
            yield Label(spec.label, classes="fd-label")
            if spec.kind in ("text", "secret"):
                yield Input(
                    value=str(spec.value or ""),
                    placeholder=spec.placeholder,
                    password=spec.kind == "secret",
                    id=widget_id,
                    compact=True,
                )
            elif spec.kind in ("int", "optint"):
                yield Input(
                    value="" if spec.value is None else str(spec.value),
                    type="integer",
                    id=widget_id,
                    classes="fd-number",
                    compact=True,
                )
            elif spec.kind == "optfloat":
                yield Input(
                    value="" if spec.value is None else str(spec.value),
                    type="number",
                    id=widget_id,
                    classes="fd-number",
                    compact=True,
                )
            elif spec.kind == "select":
                options = list(spec.options)
                values = [value for _, value in options]
                stored = spec.value
                if isinstance(stored, str) and stored and stored not in values:
                    # A stored choice the list no longer offers (a House gone
                    # from the catalog): show it, so Save keeps it unless it's
                    # changed.
                    options.append((f"{escape(stored)} (not in the list)", stored))
                    values.append(stored)
                if spec.value in values:
                    current = spec.value
                elif spec.allow_blank or not values:
                    current = Select.NULL
                else:
                    current = values[0]
                yield Select(
                    options,
                    value=current,
                    allow_blank=spec.allow_blank,
                    prompt=spec.placeholder or "(none)",
                    id=widget_id,
                    compact=True,
                )
            elif spec.kind == "check":
                yield Checkbox("", value=bool(spec.value), id=widget_id, compact=True)
            elif spec.kind == "picker":
                self._picked[spec.key] = spec.value
                yield Button(
                    self._picker_label(spec),
                    id=widget_id,
                    compact=True,
                    classes="fd-picker",
                )
            else:  # info
                yield Static(escape(str(spec.value)), classes="fd-value")
        if spec.hint:
            yield Static(spec.hint, classes="fd-hint fd-row-hint")

    def on_mount(self) -> None:
        self._fit()
        values = self.current_values()
        self._filled_from = {f.key: values.get(f.key) for f in self.fields if f.fills}
        self._react()

    def on_resize(self) -> None:
        self._refit()

    def _fit(self) -> None:
        """Cap the scrolling region so the title, live and error lines and
        the buttons always stay on screen, however short the terminal is."""
        reserved = 11
        if self.live is not None:
            # Its margin, and however many rows it wraps to.
            live = self.query_one("#fields-live")
            reserved += 1 + max(1, live.outer_size.height)
        self.query_one("#fields-scroll").styles.max_height = max(
            4, self.size.height - reserved
        )

    def _refit(self) -> None:
        """_fit again once the live line has rewrapped -- unless the form
        has been closed in the meantime."""
        try:
            self._fit()
        except NoMatches:
            pass  # closed: its widgets are gone

    def _read(self, spec: DialogField) -> Any:
        """A (non-info) field's value as its widget holds it: stripped text
        for text, number and area fields, None for a blank select."""
        if spec.kind == "picker":
            return self._picked.get(spec.key)
        widget_id = f"#fld-{spec.key}"
        if spec.kind == "select":
            value = self.query_one(widget_id, Select).value
            return value if isinstance(value, str) else None
        if spec.kind == "check":
            return self.query_one(widget_id, Checkbox).value
        if spec.kind == "area":
            # Only the end: an indented first line (a Markdown list) stays.
            return self.query_one(widget_id, TextArea).text.rstrip()
        return self.query_one(widget_id, Input).value.strip()  # text, numbers

    def _value(self, spec: DialogField) -> Any:
        """A field's value, parsed; raises _FieldError if it doesn't parse or
        is required and empty."""
        value = self._read(spec)
        parse = _PARSERS.get(spec.kind)
        if parse is not None:
            value = parse(spec, value)
        if spec.required and value in (None, ""):
            raise _FieldError(f"{spec.label} is required.")
        return value

    def current_values(self) -> dict[str, Any]:
        """Every non-info field's value as it stands, leniently: a number
        that doesn't parse (yet) is None; nothing is validated."""
        values: dict[str, Any] = {}
        for spec in self.fields:
            if spec.kind == "info":
                continue
            value = self._read(spec)
            parse = _PARSERS.get(spec.kind)
            if parse is not None:
                try:
                    value = parse(spec, value)
                except _FieldError:
                    value = None
            values[spec.key] = value
        return values

    def _picker_label(self, spec: DialogField) -> str:
        value = self._picked.get(spec.key)
        if value in (None, ""):
            return escape(spec.placeholder or "(choose...)")
        return escape(spec.display(value) if spec.display else str(value))

    def _open_picker(self, spec: DialogField) -> None:
        def handle_choice(choice: Any) -> None:
            if choice is None:
                return
            self._picked[spec.key] = choice
            self.query_one(f"#fld-{spec.key}", Button).label = self._picker_label(spec)
            self._react()

        if spec.picker is not None:
            self.app.push_screen(spec.picker(self._picked.get(spec.key)), handle_choice)

    def _shown(self, spec: DialogField, values: dict[str, Any]) -> bool:
        return spec.show_if is None or bool(spec.show_if(values))

    def _write(self, spec: DialogField, value: Any) -> None:
        """Put `value` in a field's widget (a select's only if it's one of
        its options)."""
        widget_id = f"#fld-{spec.key}"
        if spec.kind == "select":
            select = self.query_one(widget_id, Select)
            if value is None and spec.allow_blank:
                select.clear()
            elif any(option == value for _, option in spec.options):
                select.value = value
        elif spec.kind == "check":
            self.query_one(widget_id, Checkbox).value = bool(value)
        elif spec.kind in ("text", "secret", "int", "optint", "optfloat"):
            self.query_one(widget_id, Input).value = "" if value is None else str(value)

    def _fill(self) -> None:
        """Run the `fills` of each field the user has changed since it last
        filled (or since the form opened)."""
        for spec in self.fields:
            if spec.fills is None:
                continue
            values = self.current_values()
            if values.get(spec.key) == self._filled_from.get(spec.key):
                continue
            self._filled_from[spec.key] = values.get(spec.key)
            by_key = {f.key: f for f in self.fields}
            for key, value in spec.fills(values).items():
                if key in by_key:
                    self._write(by_key[key], value)

    def _react(self) -> None:
        """Show/hide fields and refresh the live line for the current values."""
        if self._filled_from:
            self._fill()
        if self.live is None and not any(f.show_if for f in self.fields):
            return
        values = self.current_values()
        for spec in self.fields:
            if spec.show_if is not None:
                self.query_one(f"#fdw-{spec.key}").display = self._shown(spec, values)
        if self.live is not None:
            self.query_one("#fields-live", Static).update(self.live(values))
            self.call_after_refresh(self._refit)

    def on_select_changed(self, event: Select.Changed) -> None:
        self._react()

    def on_input_changed(self, event: Input.Changed) -> None:
        self._react()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self._react()

    def on_key(self, event: events.Key) -> None:
        """Delete or Backspace on a "picker" field that may be blank clears
        it."""
        if event.key not in ("delete", "backspace"):
            return
        focused = self.focused
        if not isinstance(focused, Button) or not focused.has_class("fd-picker"):
            return
        key = (focused.id or "").removeprefix("fld-")
        spec = next((f for f in self.fields if f.key == key), None)
        if spec is None or not spec.allow_blank:
            return
        event.stop()
        self._picked[key] = None
        focused.label = self._picker_label(spec)
        self._react()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-save":
            self._save()
        else:
            key = (event.button.id or "").removeprefix("fld-")
            spec = next(
                (f for f in self.fields if f.key == key and f.kind == "picker"), None
            )
            if spec is not None and spec.picker is not None:
                event.stop()
                self._open_picker(spec)

    def _save(self) -> None:
        error = self.query_one("#fields-error", Static)
        result: dict[str, Any] = {}
        current = self.current_values()
        for spec in self.fields:
            if spec.kind == "info" or not self._shown(spec, current):
                continue
            try:
                result[spec.key] = self._value(spec)
            except _FieldError as problem:
                error.update(str(problem))
                return
        problem = self.validate(result) if self.validate else None
        if problem:
            error.update(problem)
            return
        # Without `build`, ResultT is the dict itself (see the overloads).
        value = self.build(result) if self.build else cast(ResultT, result)
        if self.confirm is None:
            self.dismiss(value)
            return

        def answered(confirmed: bool | None) -> None:
            if confirmed:
                self.dismiss(value)

        self.app.push_screen(self.confirm(result), answered)
