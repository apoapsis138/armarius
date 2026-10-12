"""What an add/edit form asks for, independent of how it is drawn.

A form is a list of DialogField specs. The `_*_fields` builders in
tui/screens/forms/ return them; a front-end draws each field and hands back
what the user typed, and the functions here turn that into the form's
values: parsing numbers, checking required fields, and deciding which
fields are shown. The Textual front-end's FieldsDialog (tui/screens/fields.py)
draws them today; any other front-end draws the same specs."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any

from .markup import escape
from .models import Saga

#: The hint under every free-text field that is shown with markdown_inline.
EMPHASIS_HINT = "Supports **bold** and *italic*."


@dataclass
class DialogField:
    """One row of a form.

    `kind`: "text" (a stripped string), "secret" (text shown as dots: a
    passcode), "int" (a whole number), "optint" (a
    whole number or blank -> None), "optfloat" (a number, decimals allowed,
    or blank -> None), "select" (one of `options` as (label,
    value) pairs; blank -> None when `allow_blank`; a stored value that isn't
    among them is offered as "... (not in the list)"), "check" (a boolean),
    "area" (multi-line text, trailing whitespace dropped), "picker" (a button showing `display(value)`
    that opens the chooser `picker(value)` returns; its result becomes the
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
    #: Shown only while this returns True for the form's current values;
    #: re-checked as the user edits. A hidden field is left out of the
    #: result and isn't checked.
    show_if: Callable[[dict[str, Any]], bool] | None = None
    #: A "picker" field's chooser (for the Textual front-end, a screen
    #: dismissing with the new value, or None to keep the old one) and how
    #: it shows its value on the button.
    picker: Callable[[Any], Any] | None = None
    display: Callable[[Any], str] | None = None
    #: Suggested values for other fields when the user changes this one
    #: (the form's current values -> {key: value}; None blanks a
    #: number field). Never run as the form opens, so a record's own
    #: figures stay until its source field is changed; the user can still
    #: edit what it filled.
    fills: Callable[[dict[str, Any]], dict[str, Any]] | None = None


class FieldError(ValueError):
    """A field's text doesn't parse; the message is shown under the form."""


def parse_int(spec: DialogField, raw: str) -> int | None:
    if not raw and spec.kind == "optint":
        return None
    try:
        return int(raw)
    except ValueError:
        raise FieldError(f"{spec.label} must be a whole number.") from None


def parse_float(spec: DialogField, raw: str) -> float | None:
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        raise FieldError(f"{spec.label} must be a number.") from None


#: Field kinds whose entered text becomes a number. Every other kind's value
#: is what its widget holds.
PARSERS: dict[str, Callable[[DialogField, str], Any]] = {
    "int": parse_int,
    "optint": parse_int,
    "optfloat": parse_float,
}


def parsed(spec: DialogField, raw: Any) -> Any:
    """A field's value from what its widget holds, parsed; raises
    FieldError if it doesn't parse or is required and empty."""
    value = raw
    parse = PARSERS.get(spec.kind)
    if parse is not None:
        value = parse(spec, raw)
    if spec.required and value in (None, ""):
        raise FieldError(f"{spec.label} is required.")
    return value


def lenient(spec: DialogField, raw: Any) -> Any:
    """A field's value as it stands while the user is still typing: a
    number that doesn't parse (yet) is None, and nothing is required."""
    parse = PARSERS.get(spec.kind)
    if parse is None:
        return raw
    try:
        return parse(spec, raw)
    except FieldError:
        return None


def current_values(
    fields: Iterable[DialogField], read: Callable[[DialogField], Any]
) -> dict[str, Any]:
    """Every non-info field's value as it stands (see lenient), given
    `read`, which returns what a field's widget holds."""
    return {
        spec.key: lenient(spec, read(spec)) for spec in fields if spec.kind != "info"
    }


def shown(spec: DialogField, values: dict[str, Any]) -> bool:
    """Whether a field is shown for the form's current values."""
    return spec.show_if is None or bool(spec.show_if(values))


def result(
    fields: Iterable[DialogField], read: Callable[[DialogField], Any]
) -> dict[str, Any]:
    """The finished form: {key: value} for every shown, non-info field,
    given `read` (see current_values). Raises FieldError on the first field
    that doesn't parse or is required and empty."""
    fields = list(fields)
    current = current_values(fields, read)
    return {
        spec.key: parsed(spec, read(spec))
        for spec in fields
        if spec.kind != "info" and shown(spec, current)
    }


def select_choices(spec: DialogField) -> tuple[list[tuple[str, str]], str | None]:
    """A "select" field's options and the value chosen as the form opens
    (None: blank). A stored value the list no longer offers (a House gone
    from the catalog) is added as "... (not in the list)", so saving keeps
    it unless it's changed."""
    options = list(spec.options)
    values = [value for _, value in options]
    stored = spec.value
    if isinstance(stored, str) and stored and stored not in values:
        options.append((f"{escape(stored)} (not in the list)", stored))
        values.append(stored)
    if isinstance(stored, str) and stored in values:
        return options, stored
    if spec.allow_blank or not values:
        return options, None
    return options, values[0]


# -- what form builders share --


def year_born_field(value: int | None) -> DialogField:
    """Year Born is never required: blank means Unknown."""
    return DialogField("year_born", "Year Born (blank = Unknown)", "optint", value)


def pairs(values: Iterable[str]) -> list[tuple[str, str]]:
    """Select options whose label is the value itself."""
    return [(value, value) for value in values]


def covenant_options(saga: Saga) -> list[tuple[str, str]]:
    """Select options for choosing one of the saga's covenants."""
    return [(escape(c.name), c.id) for c in saga.covenants]


def description_field(value: str) -> DialogField:
    """The multi-line Description field most forms end with."""
    return DialogField("description", "Description", "area", value, hint=EMPHASIS_HINT)


def attr(record: object | None, attribute: str, default: Any) -> Any:
    """`record.attribute`, or `default` when there's no record yet (a form
    opened to add one)."""
    return getattr(record, attribute) if record is not None else default
