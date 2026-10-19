"""A raw vis store's Add, Edit and Delete, without a front-end."""

from __future__ import annotations

from typing import Any

from ars_magica_manager import commands, form_spec
from ars_magica_manager.forms import vis as vis_forms


def _values(form: commands.Form, typed: dict[str, Any]) -> dict[str, Any]:
    fields = form.fields()
    raw = {f.key: f.value for f in fields} | typed
    return form_spec.result(fields, lambda f: raw[f.key])


def test_add_merges_into_an_art_already_held():
    pool = {"vim": 2}
    ops = vis_forms.raw_vis_ops(pool)
    assert ops.add is not None
    form = ops.add()
    assert isinstance(form, commands.Form)
    assert (form.title, form.save_label) == ("Add Raw Vis", "Add")
    form.apply(_values(form, {"art": "ignem", "pawns": "3"}))
    form.apply(_values(form, {"art": "vim", "pawns": "1"}))
    assert pool == {"vim": 3, "ignem": 3}
    assert ops.rows() == ["Ignem: 3 pawn(s)", "Vim: 3 pawn(s)"]


def test_an_art_is_required():
    form = vis_forms.raw_vis_ops({}).add
    assert form is not None
    step = form()
    assert isinstance(step, commands.Form)
    try:
        _values(step, {"pawns": "2"})
    except form_spec.FieldError as error:
        assert str(error) == "Art is required."
    else:
        raise AssertionError("an Art should be required")


def test_edit_and_delete_act_on_the_alphabetical_row():
    pool = {"vim": 2, "creo": 4}
    ops = vis_forms.raw_vis_ops(pool)
    assert ops.edit is not None and ops.remove is not None
    edit = ops.edit(0)  # Creo
    assert isinstance(edit, commands.Form)
    assert [f.value for f in edit.fields()] == ["creo", 4]
    edit.apply(_values(edit, {"art": "vim"}))  # onto Vim: merges
    assert pool == {"vim": 6}
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question == "Delete Vim vis?"
    confirm.apply()
    assert pool == {}


def test_a_characters_pool_works_the_same_as_a_labs():
    """A character's pool works the same as a lab's: the ops only see the
    dict."""
    from ars_magica_manager.models import Character

    character = Character(id="c", name="Leandro", type="magus")
    ops = vis_forms.raw_vis_ops(character.raw_vis)
    assert ops.add is not None
    form = ops.add()
    assert isinstance(form, commands.Form)
    form.apply(_values(form, {"art": "corpus", "pawns": "5"}))
    assert character.raw_vis == {"corpus": 5}
