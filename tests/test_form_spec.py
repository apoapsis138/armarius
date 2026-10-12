"""form_spec: a form's values from what the user typed, with no screen
involved (any front-end draws the fields; these rules are shared)."""

import pytest

from ars_magica_manager import form_spec as fs
from ars_magica_manager.form_spec import DialogField


def _fields() -> list[DialogField]:
    return [
        DialogField("info", "Info", "info", "read only"),
        DialogField("name", "Name", "text", required=True),
        DialogField("count", "Count", "int"),
        DialogField("age", "Age", "optint"),
        DialogField("weight", "Weight", "optfloat"),
        DialogField(
            "note", "Note", "text", show_if=lambda values: values.get("count") == 2
        ),
    ]


def _reader(typed: dict[str, object]):
    return lambda spec: typed.get(spec.key, "")


def test_result_parses_numbers_and_leaves_out_info_and_hidden_fields():
    typed = {"name": "Ash", "count": "3", "age": "", "weight": "1.5", "note": "x"}
    assert fs.result(_fields(), _reader(typed)) == {
        "name": "Ash",
        "count": 3,
        "age": None,
        "weight": 1.5,
    }


def test_a_field_shown_by_another_is_returned():
    typed = {"name": "Ash", "count": "2", "note": "x"}
    assert fs.result(_fields(), _reader(typed))["note"] == "x"


@pytest.mark.parametrize(
    ("typed", "message"),
    [
        ({"name": "", "count": "1"}, "Name is required."),
        ({"name": "Ash", "count": "lots"}, "Count must be a whole number."),
        ({"name": "Ash", "count": "1", "weight": "heavy"}, "Weight must be a number."),
    ],
)
def test_result_names_the_first_problem(typed, message):
    with pytest.raises(fs.FieldError, match=message):
        fs.result(_fields(), _reader(typed))


def test_current_values_are_lenient():
    typed = {"name": "", "count": "lots"}
    values = fs.current_values(_fields(), _reader(typed))
    assert values["name"] == "" and values["count"] is None
    assert "info" not in values


def test_select_keeps_a_stored_value_the_list_no_longer_offers():
    spec = DialogField(
        "house", "House", "select", "Diedne", options=[("Tytalus", "Tytalus")]
    )
    options, chosen = fs.select_choices(spec)
    assert options[-1] == ("Diedne (not in the list)", "Diedne")
    assert chosen == "Diedne"


@pytest.mark.parametrize(("allow_blank", "chosen"), [(True, None), (False, "a")])
def test_select_without_a_value_is_blank_or_first(allow_blank, chosen):
    spec = DialogField(
        "x",
        "X",
        "select",
        None,
        options=[("A", "a"), ("B", "b")],
        allow_blank=allow_blank,
    )
    assert fs.select_choices(spec)[1] == chosen
