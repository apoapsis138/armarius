"""The modal-dialog base and the config-driven FieldsDialog form, with the
small helpers form builders share."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any, ClassVar, cast

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
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

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    #: What the dialog dismisses with when cancelled.
    CANCEL_RESULT: ClassVar[Any] = None

    def action_cancel(self) -> None:
        self.dismiss(self.CANCEL_RESULT)

    def _select_value(self, selector: str) -> str | None:
        """The chosen value of the Select at `selector`, or None if blank."""
        value = self.query_one(selector, Select).value
        return value if isinstance(value, str) else None


@dataclass
class DialogField:
    """One row of a FieldsDialog.

    `kind`: "text" (a stripped string), "int" (a whole number), "optint" (a
    whole number or blank -> None), "optfloat" (a number, decimals allowed,
    or blank -> None), "select" (one of `options` as (label,
    value) pairs; blank -> None when `allow_blank`), "check" (a boolean),
    "area" (multi-line text), "picker" (a button showing `display(value)`
    that opens the screen `picker(value)` returns; its result becomes the
    value) or "info" (read-only text, not returned).
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


class FieldsDialog[ResultT = dict[str, Any]](ModalDialog[ResultT | None]):
    """A config-driven form: one compact row per DialogField, scrolling if the
    terminal is short (Save/Cancel stay put). Dismisses with {key: value} for
    every non-info field, or None if cancelled. `validate` gets the finished
    dict and returns an error message, or None if it's fine. `save_label`
    names the button that completes it ("Save", "Create"...). With `build`,
    it dismisses with `build(values)` instead (e.g. a finished record).

    Fields can depend on each other while the form is open: a field's
    `show_if` shows/hides it, and `live` (markup, from the current values)
    fills a line above the error, both refreshed on every change."""

    DEFAULT_CSS = """
    FieldsDialog {
        align: center middle;
    }

    #fields-dialog {
        width: 84;
        max-width: 100%;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
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

    def __init__(
        self,
        title: str,
        fields: list[DialogField],
        *,
        validate: Callable[[dict[str, Any]], str | None] | None = None,
        live: Callable[[dict[str, Any]], str] | None = None,
        save_label: str = "Save",
        build: Callable[[dict[str, Any]], ResultT] | None = None,
    ) -> None:
        super().__init__()
        self.title_text = title
        self.fields = fields
        self.validate = validate
        self.live = live
        self.save_label = save_label
        self.build = build
        self._picked: dict[str, Any] = {}  # "picker" fields' current values

    def compose(self) -> ComposeResult:
        with Vertical(id="fields-dialog"):
            yield Label(self.title_text, id="fields-title")
            with VerticalScroll(id="fields-scroll"):
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
            if spec.kind == "text":
                yield Input(
                    value=str(spec.value or ""),
                    placeholder=spec.placeholder,
                    id=widget_id,
                    compact=True,
                )
            elif spec.kind in ("int", "optint"):
                yield Input(
                    value="" if spec.value is None else str(spec.value),
                    type="integer",
                    id=widget_id,
                    compact=True,
                )
            elif spec.kind == "optfloat":
                yield Input(
                    value="" if spec.value is None else str(spec.value),
                    type="number",
                    id=widget_id,
                    compact=True,
                )
            elif spec.kind == "select":
                values = [value for _, value in spec.options]
                if spec.value in values:
                    current = spec.value
                elif spec.allow_blank or not values:
                    current = Select.NULL
                else:
                    current = values[0]
                yield Select(
                    spec.options,
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
            yield Static(spec.hint, classes="fd-hint")

    def on_mount(self) -> None:
        self._fit()
        self._react()

    def on_resize(self) -> None:
        self._fit()

    def _fit(self) -> None:
        """Cap the scrolling region so the title, error line and buttons always
        stay on screen, however short the terminal is."""
        reserved = 11 + (2 if self.live is not None else 0)
        self.query_one("#fields-scroll").styles.max_height = max(
            4, self.size.height - reserved
        )

    def current_values(self) -> dict[str, Any]:
        """Every non-info field's value as it stands, leniently: a number
        that doesn't parse (yet) is None; nothing is validated."""
        values: dict[str, Any] = {}
        for spec in self.fields:
            if spec.kind == "info":
                continue
            widget = self.query_one(f"#fld-{spec.key}")
            if spec.kind == "text":
                values[spec.key] = widget.value.strip()
            elif spec.kind in ("int", "optint"):
                try:
                    values[spec.key] = int(widget.value.strip())
                except ValueError:
                    values[spec.key] = None
            elif spec.kind == "optfloat":
                try:
                    values[spec.key] = float(widget.value.strip())
                except ValueError:
                    values[spec.key] = None
            elif spec.kind == "select":
                values[spec.key] = (
                    widget.value if isinstance(widget.value, str) else None
                )
            elif spec.kind == "check":
                values[spec.key] = bool(widget.value)
            elif spec.kind == "picker":
                values[spec.key] = self._picked.get(spec.key)
            else:  # area
                values[spec.key] = widget.text.strip()
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

        self.app.push_screen(spec.picker(self._picked.get(spec.key)), handle_choice)

    def _shown(self, spec: DialogField, values: dict[str, Any]) -> bool:
        return spec.show_if is None or bool(spec.show_if(values))

    def _react(self) -> None:
        """Show/hide fields and refresh the live line for the current values."""
        if self.live is None and not any(f.show_if for f in self.fields):
            return
        values = self.current_values()
        for spec in self.fields:
            if spec.show_if is not None:
                self.query_one(f"#fdw-{spec.key}").display = self._shown(spec, values)
        if self.live is not None:
            self.query_one("#fields-live", Static).update(self.live(values))

    def on_select_changed(self, event: Select.Changed) -> None:
        self._react()

    def on_input_changed(self, event: Input.Changed) -> None:
        self._react()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
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
            widget = self.query_one(f"#fld-{spec.key}")
            if spec.kind == "text":
                value: Any = widget.value.strip()
                if spec.required and not value:
                    error.update(f"{spec.label} is required.")
                    return
            elif spec.kind in ("int", "optint"):
                raw = widget.value.strip()
                if not raw and spec.kind == "optint":
                    value = None
                    if spec.required:
                        error.update(f"{spec.label} is required.")
                        return
                else:
                    try:
                        value = int(raw)
                    except ValueError:
                        error.update(f"{spec.label} must be a whole number.")
                        return
            elif spec.kind == "optfloat":
                raw = widget.value.strip()
                if not raw:
                    value = None
                    if spec.required:
                        error.update(f"{spec.label} is required.")
                        return
                else:
                    try:
                        value = float(raw)
                    except ValueError:
                        error.update(f"{spec.label} must be a number.")
                        return
            elif spec.kind == "select":
                value = widget.value if isinstance(widget.value, str) else None
                if spec.required and value is None:
                    error.update(f"{spec.label} is required.")
                    return
            elif spec.kind == "check":
                value = bool(widget.value)
            elif spec.kind == "picker":
                value = self._picked.get(spec.key)
                if spec.required and value in (None, ""):
                    error.update(f"{spec.label} is required.")
                    return
            else:  # area
                value = widget.text.strip()
            result[spec.key] = value
        problem = self.validate(result) if self.validate else None
        if problem:
            error.update(problem)
            return
        self.dismiss(self.build(result) if self.build else cast(ResultT, result))
