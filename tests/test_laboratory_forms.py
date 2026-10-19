"""A laboratory's forms and lists (Identity, Characteristics,
Specialization sources, Features, Rooms, Equipment & Stores, Arcane
Connections), without a front-end."""

from __future__ import annotations

from typing import Any

from screen_helpers import _saga_with_bare_laboratory

from ars_magica_manager import commands, form_spec
from ars_magica_manager.forms import laboratory as lf
from ars_magica_manager.models import (
    Character,
    LabFeature,
    LabSpecialtyEntry,
    VirtueFlawInstance,
)


def _values(form: commands.Form, typed: dict[str, Any]) -> dict[str, Any]:
    fields = form.fields()
    raw = {f.key: f.value for f in fields} | typed
    return form_spec.result(fields, lambda f: raw[f.key])


def _saved(form: commands.Form, typed: dict[str, Any]) -> Any:
    """Save `form` with `typed`, as a front-end would; what it leads to."""
    values = _values(form, typed)
    assert form.validate is None or form.validate(values) is None
    return form.apply(values)


def test_identity_moves_the_owner_both_ways():
    saga = _saga_with_bare_laboratory()
    saga.characters.append(Character(id="char2", name="Bea", type="magus"))
    lab = saga.laboratories[0]
    saga.characters[0].assigned_lab_id = lab.id
    form = lf.identity_form(saga, lab)
    assert form.title == "Edit Laboratory Identity"
    _saved(
        form,
        {"name": "Tower", "aura_modifier": "2", "owner_id": "char2", "location": "Up"},
    )
    assert (lab.name, lab.aura_modifier, lab.location) == ("Tower", 2, "Up")
    assert lab.owner_id == "char2"
    assert saga.characters[1].assigned_lab_id == lab.id
    assert saga.characters[0].assigned_lab_id is None


def test_identity_keeps_an_owner_who_is_no_longer_a_magus():
    saga = _saga_with_bare_laboratory()
    saga.characters[0].type = "companion"
    options = lf.owner_options(saga, "char1")
    assert options == [("Leandro (companion)", "char1")]


def test_characteristics_are_the_typed_values():
    lab = _saga_with_bare_laboratory().laboratories[0]
    form = lf.characteristics_form(lab)
    assert form.title == "Edit Laboratory Characteristics (manual value)"
    _saved(form, {"safety": "2", "upkeep": "-1"})
    assert (lab.characteristics.safety, lab.characteristics.upkeep) == (2, -1)


def test_specialization_sources_add_edit_delete_and_refuse_zero():
    lab = _saga_with_bare_laboratory().laboratories[0]
    ops = lf.specialty_ops(lab)
    assert ops.add and ops.edit and ops.remove
    add = ops.add()
    assert isinstance(add, commands.Form)
    assert (add.title, add.save_label) == ("Add a Specialization source", "Add")
    zero = _values(add, {"specialization": "Terram", "points": "0"})
    assert add.validate is not None and add.validate(zero) == "Points can't be 0."
    _saved(add, {"specialization": "Terram", "points": "1", "source": "Cave"})
    assert lab.specialties == [LabSpecialtyEntry("Terram", 1, "Cave")]
    assert ops.rows() == ["Terram +1 (Cave)"]
    edit = ops.edit(0)
    assert isinstance(edit, commands.Form)
    assert edit.title == "Edit a Specialization source"
    _saved(edit, {"points": "-2"})
    assert lab.specialties[0].points == -2
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question == "Delete Terram -2 (Cave)?"
    confirm.apply()
    assert lab.specialties == []


def test_adding_a_feature_with_a_new_virtue_confirms_and_changes_nothing_until_saved():
    lab = _saga_with_bare_laboratory().laboratories[0]
    ops = lf.feature_ops(lab)
    assert ops.add is not None
    first = ops.add()
    assert isinstance(first, commands.Form)
    assert (first.title, first.save_label) == ("Add a Feature", "Next")
    confirm = _saved(
        first,
        {
            "feature_type": "custom",
            "virtue": lf.NEW_FEATURE_VIRTUE + "labvf_lesser_feature",
        },
    )
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question.startswith(
        "Add a Lesser Feature Virtue to the lab (1 point"
    )
    assert confirm.yes_label == "Add"
    details = confirm.apply()
    assert isinstance(details, commands.Form)
    assert details.save_label == "Add"
    assert lab.features == [] and lab.virtues_flaws == []  # nothing yet
    _saved(details, {"name": "Brass Cauldron", "point0": "Ignem"})
    [feature] = lab.features
    [virtue] = lab.virtues_flaws
    assert (feature.name, feature.feature_id) == ("Brass Cauldron", None)
    assert virtue.vf_id == "labvf_lesser_feature" and feature.virtue_id == virtue.id
    assert [g.specialization for g in feature.allocations] == ["Ignem"]


def test_editing_a_feature_on_a_free_virtue_then_deleting_it_keeps_the_virtue():
    lab = _saga_with_bare_laboratory().laboratories[0]
    lab.virtues_flaws.append(VirtueFlawInstance("labvf_lesser_feature", id="v1"))
    lab.features.append(LabFeature("f1", "Old", virtue_id="v1"))
    ops = lf.feature_ops(lab)
    assert ops.edit and ops.remove
    first = ops.edit(0)
    assert isinstance(first, commands.Form)
    assert first.title == "Edit a Feature"
    assert [f.value for f in first.fields()] == ["custom", "v1"]
    details = _saved(first, {})
    assert isinstance(details, commands.Form)
    assert details.save_label == "Save"
    _saved(details, {"name": "New", "point0": "Vim"})
    assert [f.name for f in lab.features] == ["New"]
    assert lab.features[0].id == "f1"
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question == (
        "Delete New? Its Lesser Feature Virtue stays, free for another Feature."
    )
    confirm.apply()
    assert lab.features == [] and len(lab.virtues_flaws) == 1


def test_rooms_and_equipment_add_edit_delete():
    lab = _saga_with_bare_laboratory().laboratories[0]
    for section, attribute, title in (
        ("section-lab-rooms", "rooms", "Add a Room"),
        ("section-lab-items", "inventory_items", "Add an Equipment & Stores entry"),
    ):
        ops = lf.named_ops(lab, section)
        assert ops.add and ops.edit and ops.remove
        add = ops.add()
        assert isinstance(add, commands.Form) and add.title == title
        _saved(add, {"name": "Vault", "description": "Dark"})
        edit = ops.edit(0)
        assert isinstance(edit, commands.Form)
        _saved(edit, {"name": "Crypt"})
        entries = getattr(lab, attribute)
        assert [(e.name, e.description) for e in entries] == [("Crypt", "Dark")]
        assert ops.rows() == ["Crypt"]
        confirm = ops.remove(0)
        assert isinstance(confirm, commands.Confirm)
        assert confirm.question == "Delete Crypt?"
        confirm.apply()
        assert getattr(lab, attribute) == []


def test_arcane_connections_keep_their_id_and_drop_lasts_when_fixed():
    lab = _saga_with_bare_laboratory().laboratories[0]
    ops = lf.connection_ops(lab)
    assert ops.add and ops.edit and ops.remove
    add = ops.add()
    assert isinstance(add, commands.Form)
    assert add.title == "Add an Arcane Connection"
    _saved(add, {"to": "a lock of hair", "lasts": "a year"})
    [connection] = lab.arcane_connections
    assert (connection.fixed, connection.lasts) == (False, "a year")
    edit = ops.edit(0)
    assert isinstance(edit, commands.Form)
    _saved(edit, {"fixed": True})
    assert lab.arcane_connections[0].id == connection.id
    assert (lab.arcane_connections[0].fixed, lab.arcane_connections[0].lasts) == (
        True,
        "",
    )
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question == "Delete the Arcane Connection to a lock of hair?"
    confirm.apply()
    assert lab.arcane_connections == []
