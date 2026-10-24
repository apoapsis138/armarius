"""The machinery of the dialog contract tests (test_dialog_contracts_*.py,
one file per area of the app): the Contract each form is held to, and the
driver that runs one form's contract in one app session.

The contracts test the app's form dialogs, keyed by what the user sees.

Each dialog is opened the way the app opens it (dialog_openers.py) and
driven by its field labels, never by widget ids, so the same tests hold
before and after a dialog is rebuilt (e.g. as a FieldsDialog). For each:

- the form is pre-filled with the record's current values;
- Cancel after editing leaves the saved saga untouched;
- an invalid entry keeps the dialog open with an error and saves nothing;
- a valid edit, saved, lands in the saved saga.

A field is found by the text of its label (a prefix match, ignoring a
trailing colon), or -- for the few fields drawn without a label -- by an
alias to its widget id. A Checkbox may also be found by its own label.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from dialog_openers import contract_saga, new_app, open_dialog, reopen_dialog
from support import build_all_tabs, strip_markup, wait_until
from textual.widget import Widget
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    Input,
    Label,
    Select,
    Static,
    TextArea,
)

from ars_magica_manager import storage
from ars_magica_manager.models import Possession, Saga, VirtueFlawInstance
from ars_magica_manager.tui.screens import SelectableList

SAGA_ID = contract_saga().id

#: The button that completes a dialog (whatever its label says).
SAVE_BUTTON_IDS = ("btn-save", "btn-create", "btn-confirm")


@dataclass
class Contract:
    #: Label -> the value shown when the dialog opens.
    prefill: dict[str, Any]
    #: Label -> a new value (text for inputs, a value for selects, a bool for
    #: checkboxes); saved, then `saved` must return `expected`.
    edits: dict[str, Any]
    saved: Callable[[Saga], Any]
    expected: Any
    #: Label -> a value the dialog must refuse, or several such entries,
    #: each refused on its own (None: nothing to refuse).
    invalid: dict[str, Any] | list[dict[str, Any]] | None = None
    #: Selector -> text the screen shows there once the edit is saved (the
    #: sheet, panel or tree refreshed): a Collapsible's title, a list's rows
    #: or a Static's text, markup stripped.
    shown: dict[str, str] = field(default_factory=dict)
    #: Label -> widget id, for fields drawn without a label.
    aliases: dict[str, str] = field(default_factory=dict)
    #: Selector -> text the dialog itself shows once `edits` are typed,
    #: before saving (a live line worked out from them).
    live: dict[str, str] = field(default_factory=dict)


#: A self-initiation into Affinity with Ignem, with a Major Ordeal.
INITIATION = {
    "Activity": "undergo_initiation",
    "Script bonus": "12",
    "Mystagogue's Lore": "Mercere Lore",
    "Virtue initiated": VirtueFlawInstance("vf_affinity_with_art", {"art": "ignem"}),
    "Ordeal": "gain",
    "Flaw gained": VirtueFlawInstance("vf_deficient_technique", {"technique": "creo"}),
}

#: A Resolved Story Event linked to the covenant's Hidden Resources Boon.
HIDDEN_STORY = {
    "Category": "Story Event",
    "Name": "Past the guardian",
    "Status": "Resolved",
    "Linked Boon/Hook": "bh-hr",
}

#: The same, linked to its Illusory Resources Hook.
ILLUSORY_STORY = {**HIDDEN_STORY, "Linked Boon/Hook": "bh-ir"}


def character(saga: Saga):
    return next(c for c in saga.characters if c.id == "mag1")


def familiar(saga: Saga):
    return saga.familiars[0]


def laboratory(saga: Saga):
    return saga.laboratories[0]


def covenant(saga: Saga):
    return saga.covenants[0]


def sketch_covenant(saga: Saga):
    return saga.covenant("cov_sketch")


def last_gear(possessions: list[Possession], kind: str) -> tuple:
    """The last weapon's (or armor's) name, book entry, Quality and
    figures."""
    item = [p for p in possessions if p.kind == kind][-1]
    head = (item.name, item.gear_id, item.gear_quality)
    if kind == "armor":
        return (*head, item.gear_type, item.armor_protection, item.load)
    figures = (item.weapon_init, item.weapon_attack, item.weapon_defense)
    return (*head, *figures, item.weapon_damage, item.load)


def all_sagas() -> list[Saga]:
    return [storage.load_saga(saga_id) for saga_id in storage.list_sagas()]


def device(saga: Saga, device_id: str):
    return next(d for d in saga.enchanted_devices if d.id == device_id)


# -- finding and setting fields by label --

_INPUTS = (Input, Select, TextArea, Checkbox)


def _is_input(widget: Widget) -> bool:
    """A field's widget: an input, or a "picker" field's button."""
    return isinstance(widget, _INPUTS) or (
        isinstance(widget, Button) and widget.has_class("fd-picker")
    )


def _text(widget: Widget) -> str:
    return str(widget.render()).strip().rstrip(":").strip()


def field_widget(dialog, label: str, aliases: dict[str, str]) -> Widget:
    """The input widget for the field labelled `label` in `dialog`."""
    widgets = list(dialog.query("*"))
    for position, widget in enumerate(widgets):
        if isinstance(widget, Checkbox) and str(widget.label).startswith(label):
            return widget
        if type(widget) in (Label, Static) and _text(widget).startswith(label):
            following = next((w for w in widgets[position + 1 :] if _is_input(w)), None)
            if following is not None:
                return following
    if label in aliases:
        return dialog.query_one(f"#{aliases[label]}")
    raise AssertionError(f"no field labelled {label!r}")


def field_value(widget: Widget) -> Any:
    if isinstance(widget, Button):  # a picker field: what it holds
        return widget.screen._picked.get((widget.id or "").removeprefix("fld-"))
    if isinstance(widget, (Input, Select)):
        return widget.value
    if isinstance(widget, TextArea):
        return widget.text
    assert isinstance(widget, Checkbox)
    return widget.value


def set_field(widget: Widget, value: Any) -> None:
    if isinstance(widget, Button):  # a picker field: as if it were chosen
        dialog = widget.screen
        dialog._picked[(widget.id or "").removeprefix("fld-")] = value
        dialog._react()
        return
    if isinstance(widget, (Input, Select)):
        widget.value = value
    elif isinstance(widget, TextArea):
        widget.text = value
    else:
        assert isinstance(widget, Checkbox)
        widget.value = value


def save_button(dialog) -> Button:
    return next(b for b in dialog.query(Button) if b.id in SAVE_BUTTON_IDS)


def cancel_button(dialog) -> Button:
    return dialog.query_one("#btn-cancel", Button)


def error_text(dialog) -> str:
    """Any error message the dialog shows."""
    return " ".join(
        _text(w)
        for w in dialog.query("Static, Label")
        if w.id and w.id.endswith("error") and _text(w)
    )


def _saved_file() -> str:
    return storage.saga_path(SAGA_ID).read_text(encoding="utf-8")


async def _fill(pilot, dialog, contract: Contract, values: dict[str, Any]) -> None:
    for label, value in values.items():
        set_field(field_widget(dialog, label, contract.aliases), value)
    await pilot.pause()


def _invalid_entries(contract: Contract) -> list[dict[str, Any]]:
    if contract.invalid is None:
        return []
    if isinstance(contract.invalid, dict):
        return [contract.invalid]
    return contract.invalid


def shown_text(screen, selector: str) -> str:
    """What `screen` shows at `selector`: a Collapsible's title, a list's
    rows (one per line) or a Static's text, markup stripped."""
    widget = screen.query_one(selector)
    if isinstance(widget, Collapsible):
        text = widget.title
    elif isinstance(widget, SelectableList):
        text = "\n".join(label for _, label in widget._rows)
    else:
        text = str(widget.render())
    return strip_markup(text)


async def _close(pilot, app, dialog, button: Button) -> None:
    button.press()
    assert await wait_until(pilot, lambda: app.screen is not dialog), (
        f"still open: {error_text(dialog)!r}"
    )
    await pilot.pause()


async def run_contract(name: str, contract: Contract) -> None:
    """Run form `name`'s `contract` in one app session, at 120x45 (the
    smallest size the user works at):

    - the whole dialog, and its Save and Cancel buttons, are on screen (a
      long form scrolls between them);
    - it's pre-filled with the record's current values;
    - Cancel after editing saves nothing;
    - each invalid entry is refused with an error, the dialog staying open
      and nothing saved;
    - a valid edit, saved, lands in the saved saga and the screen shows it.
    """
    app = new_app()
    before = _saved_file()
    async with app.run_test(size=(120, 45)) as pilot:
        base, dialog = await open_dialog(pilot, app, name)
        for button in (save_button(dialog), cancel_button(dialog)):
            region = button.region
            assert region.height > 0, button.id
            assert region.x >= 0 and region.right <= 120, (button.id, region)
            assert region.y >= 0 and region.bottom <= 45, (button.id, region)

        prefilled = {
            label: field_value(field_widget(dialog, label, contract.aliases))
            for label in contract.prefill
        }
        assert prefilled == contract.prefill, prefilled

        await _fill(pilot, dialog, contract, contract.edits)
        await _close(pilot, app, dialog, cancel_button(dialog))
        assert _saved_file() == before

        for entry in _invalid_entries(contract):
            dialog = await reopen_dialog(pilot, app, base, name)
            await _fill(pilot, dialog, contract, entry)
            save_button(dialog).press()
            assert await wait_until(pilot, lambda d=dialog: error_text(d) != ""), entry
            assert app.screen is dialog, entry
            await _close(pilot, app, dialog, cancel_button(dialog))
            assert _saved_file() == before, entry
        if name == "create saga":
            assert storage.list_sagas() == [SAGA_ID]

        dialog = await reopen_dialog(pilot, app, base, name)
        view = getattr(base, "_current_sheet_view", lambda: None)()
        if contract.shown and view is not None:
            # Build every tab now, so the save has to refresh what's shown.
            await build_all_tabs(pilot, view)
        await _fill(pilot, dialog, contract, contract.edits)
        for selector, text in contract.live.items():
            assert await wait_until(
                pilot, lambda s=selector, t=text, d=dialog: t in shown_text(d, s)
            ), (selector, shown_text(dialog, selector))
        await _close(pilot, app, dialog, save_button(dialog))
        # The screen shows the saved values (its sheet was refreshed).
        for selector, text in contract.shown.items():
            assert await wait_until(
                pilot, lambda s=selector, t=text: t in shown_text(base, s)
            ), (selector, shown_text(base, selector))
    assert contract.saved(storage.load_saga(SAGA_ID)) == contract.expected
