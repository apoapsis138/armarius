"""FieldsDialog's parsing of each field kind, on its own: the values it
gives while the form is edited (leniently) and on Save (checked, with the
first problem shown)."""

import json
import subprocess
import sys
from typing import Any

import pytest
from dialog_openers import contract_saga, new_app, open_dialog
from support import wait_until
from textual.app import App
from textual.widgets import Checkbox, Input, Select, Static, TextArea

from ars_magica_manager import ROOT, storage
from ars_magica_manager.tui.screens import DialogField, FieldsDialog


def _fields() -> list[DialogField]:
    return [
        DialogField("info", "Info", "info", "read only"),
        DialogField("name", "Name", "text", "  Ash  ", required=True),
        DialogField("count", "Count", "int", 3),
        DialogField("age", "Age", "optint", None),
        DialogField("weight", "Weight", "optfloat", 1.5),
        DialogField(
            "kind",
            "Kind",
            "select",
            "b",
            options=[("A", "a"), ("B", "b")],
            allow_blank=True,
        ),
        DialogField("ok", "OK", "check", True),
        DialogField("notes", "Notes", "area", "  line one\nline two  "),
    ]


class _Host(App[None]):
    def __init__(self, dialog: FieldsDialog) -> None:
        super().__init__()
        self.dialog = dialog
        self.result: Any = "not dismissed"

    def on_mount(self) -> None:
        def done(result: Any) -> None:
            self.result = result

        self.push_screen(self.dialog, done)


async def _open(fields: list[DialogField]):
    dialog: FieldsDialog = FieldsDialog("Test", fields)
    return dialog, _Host(dialog)


async def test_values_while_editing_are_lenient():
    dialog, app = await _open(_fields())
    async with app.run_test(size=(100, 40)) as pilot:
        await wait_until(pilot, lambda: dialog.is_mounted)
        assert dialog.current_values() == {
            "name": "Ash",
            "count": 3,
            "age": None,
            "weight": 1.5,
            "kind": "b",
            "ok": True,
            # Multi-line text loses only trailing whitespace: an
            # indented first line, like a Markdown list item, stays.
            "notes": "  line one\nline two",
        }
        dialog.query_one("#fld-count", Input).value = ""  # not a number (yet)
        dialog.query_one("#fld-weight", Input).value = "1."
        dialog.query_one("#fld-kind", Select).value = Select.NULL
        await pilot.pause()
        values = dialog.current_values()
        assert (values["count"], values["weight"], values["kind"]) == (None, 1.0, None)


async def test_save_returns_every_non_info_field_parsed():
    dialog, app = await _open(_fields())
    async with app.run_test(size=(100, 40)) as pilot:
        await wait_until(pilot, lambda: dialog.is_mounted)
        dialog.query_one("#fld-age", Input).value = "25"
        dialog.query_one("#fld-ok", Checkbox).value = False
        dialog.query_one("#fld-notes", TextArea).text = "changed"
        dialog.query_one("#btn-save").press()
        await wait_until(pilot, lambda: app.result != "not dismissed")
    assert app.result == {
        "name": "Ash",
        "count": 3,
        "age": 25,
        "weight": 1.5,
        "kind": "b",
        "ok": False,
        "notes": "changed",
    }


@pytest.mark.parametrize(
    ("field", "text", "message"),
    [
        ("name", "   ", "Name is required."),
        ("count", "", "Count must be a whole number."),
        ("count", "-", "Count must be a whole number."),
        ("age", "x", "Age must be a whole number."),
        ("weight", "abc", "Weight must be a number."),
    ],
)
async def test_save_refuses_the_first_bad_field(field, text, message):
    dialog, app = await _open(_fields())
    async with app.run_test(size=(100, 40)) as pilot:
        await wait_until(pilot, lambda: dialog.is_mounted)
        # Bypass the Input's own typing restrictions, like a paste would.
        dialog.query_one(f"#fld-{field}", Input).value = text
        dialog.query_one("#btn-save").press()
        await pilot.pause()
        assert app.screen is dialog
        assert str(dialog.query_one("#fields-error", Static).render()) == message


async def test_required_blank_optional_number_and_select():
    fields = [
        DialogField("age", "Age", "optint", None, required=True),
        DialogField("weight", "Weight", "optfloat", None, required=True),
        DialogField(
            "kind",
            "Kind",
            "select",
            None,
            options=[("A", "a")],
            required=True,
            allow_blank=True,
        ),
    ]
    dialog, app = await _open(fields)
    async with app.run_test(size=(100, 40)) as pilot:
        await wait_until(pilot, lambda: dialog.is_mounted)
        error = dialog.query_one("#fields-error", Static)
        for field, fix in (("age", "1"), ("weight", "2"), ("kind", None)):
            dialog.query_one("#btn-save").press()
            await pilot.pause()
            assert str(error.render()) == f"{field.title()} is required."
            if fix is None:
                dialog.query_one(f"#fld-{field}", Select).value = "a"
            else:
                dialog.query_one(f"#fld-{field}", Input).value = fix
        dialog.query_one("#btn-save").press()
        await wait_until(pilot, lambda: app.result != "not dismissed")
    assert app.result == {"age": 1, "weight": 2.0, "kind": "a"}


def test_pyright_flags_a_typed_dialog_without_build(tmp_path):
    # Without `build` the dialog dismisses with its values dict; typing it
    # as a FieldsDialog[Record] must be a type error, not a silent cast.
    probe = tmp_path / "probe.py"
    probe.write_text(
        "from ars_magica_manager.models import ScoredTrait\n"
        "from ars_magica_manager.tui.screens import FieldsDialog\n"
        "good: FieldsDialog[ScoredTrait] = FieldsDialog(\n"
        "    't', [], build=lambda v: ScoredTrait('a', 1)\n"
        ")\n"
        "plain: FieldsDialog = FieldsDialog('t', [])\n"
        "bad: FieldsDialog[ScoredTrait] = FieldsDialog('t', [])\n",
        encoding="utf-8",
    )
    run = subprocess.run(
        # --pythonpath: this interpreter's packages, as when run under uv.
        [
            sys.executable,
            "-m",
            "pyright",
            "--outputjson",
            "--pythonpath",
            sys.executable,
            str(probe),
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,  # exits non-zero on the expected error
    )
    report = json.loads(run.stdout)
    errors = [d for d in report["generalDiagnostics"] if d["severity"] == "error"]
    assert [e["range"]["start"]["line"] + 1 for e in errors] == [7], errors


async def test_a_stored_choice_not_in_the_list_is_kept():
    # It used to open blank, and Save cleared it unasked.
    fields = [
        DialogField(
            "house",
            "House",
            "select",
            "house_gone",
            options=[("Bonisagus", "house_bonisagus")],
            allow_blank=True,
        )
    ]
    dialog, app = await _open(fields)
    async with app.run_test(size=(100, 40)) as pilot:
        await wait_until(pilot, lambda: dialog.is_mounted)
        select = dialog.query_one("#fld-house", Select)
        assert select.value == "house_gone"
        shown = select.query_one("SelectCurrent #label", Static)
        assert str(shown.render()) == "house_gone (not in the list)"
        dialog.query_one("#btn-save").press()
        await wait_until(pilot, lambda: app.result != "not dismissed")
    assert app.result == {"house": "house_gone"}


@pytest.mark.parametrize(
    ("dialog_name", "change", "saved"),
    [
        (
            "edit hermetic background",
            lambda saga: setattr(saga.character("mag1").hermetic, "house", "gone"),
            lambda saga: saga.character("mag1").hermetic.house,
        ),
        (
            "edit lab identity",
            lambda saga: setattr(saga.laboratory("lab1"), "owner_id", "comp1"),
            lambda saga: saga.laboratory("lab1").owner_id,
        ),
    ],
)
async def test_saving_unchanged_keeps_a_value_the_list_lacks(
    dialog_name, change, saved
):
    # A House no longer in the catalog; a Lab Owner who isn't a magus.
    saga = contract_saga()
    change(saga)
    expected = saved(saga)
    app = new_app(saga)
    async with app.run_test(size=(140, 50)) as pilot:
        base, dialog = await open_dialog(pilot, app, dialog_name)
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is base)
    assert saved(storage.load_saga(saga.id)) == expected


# ---------------------------------------------------------------- fills


def _fill_fields(name: str = "", kind: str | None = None) -> list[DialogField]:
    """A "kind" select that suggests a size, a note and a name."""

    def fills(values: dict[str, Any]) -> dict[str, Any]:
        if values["kind"] == "big":
            return {"size": 9, "note": None, "name": "Big one", "shape": "round"}
        return {"size": 1, "shape": "nonsense"}  # not one of shape's options

    return [
        DialogField("name", "Name", "text", name),
        DialogField(
            "kind",
            "Kind",
            "select",
            kind,
            options=[("Big", "big"), ("Small", "small")],
            allow_blank=True,
            fills=fills,
        ),
        DialogField("size", "Size", "int", 5),
        DialogField("note", "Note", "optint", 3),
        DialogField(
            "shape",
            "Shape",
            "select",
            "square",
            options=[("R", "round"), ("S", "square")],
        ),
    ]


async def test_fills_waits_for_the_user_to_change_the_field():
    # Opened on a record that already has a kind: its own figures stay.
    dialog, app = await _open(_fill_fields(name="Mine", kind="big"))
    async with app.run_test(size=(100, 40)) as pilot:
        await wait_until(pilot, lambda: dialog.is_mounted)
        await pilot.pause()
        assert dialog.current_values() == {
            "name": "Mine",
            "kind": "big",
            "size": 5,
            "note": 3,
            "shape": "square",
        }


async def test_fills_suggests_other_fields_when_the_user_changes_it():
    dialog, app = await _open(_fill_fields())
    async with app.run_test(size=(100, 40)) as pilot:
        await wait_until(pilot, lambda: dialog.is_mounted)
        dialog.query_one("#fld-kind", Select).value = "big"
        assert await wait_until(pilot, lambda: dialog.current_values()["size"] == 9)
        # A None blanks a number; a select takes one of its options.
        assert dialog.current_values() == {
            "name": "Big one",
            "kind": "big",
            "size": 9,
            "note": None,
            "shape": "round",
        }
        dialog.query_one("#fld-size", Input).value = "7"  # still editable
        dialog.query_one("#fld-kind", Select).value = "small"
        assert await wait_until(pilot, lambda: dialog.current_values()["size"] == 1)
        # A value a select doesn't offer is left alone.
        assert dialog.current_values()["shape"] == "round"
        dialog.query_one("#fld-size", Input).value = "4"
        await pilot.pause()
        assert dialog.current_values()["size"] == 4  # no refill without a change
        dialog.query_one("#btn-save").press()
        await wait_until(pilot, lambda: app.result != "not dismissed")
    assert app.result["size"] == 4


async def test_delete_clears_a_picker_field_that_may_be_blank():
    fields = [
        DialogField("must", "Must", "picker", "kept", display=str),
        DialogField("may", "May", "picker", "gone", allow_blank=True, display=str),
    ]
    dialog, app = await _open(fields)
    async with app.run_test(size=(100, 40)) as pilot:
        await wait_until(pilot, lambda: dialog.is_mounted)
        for key in ("must", "may"):
            dialog.query_one(f"#fld-{key}").focus()
            await pilot.press("delete")
        assert dialog.current_values() == {"must": "kept", "may": None}
