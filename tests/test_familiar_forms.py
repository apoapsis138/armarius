"""A familiar's Edit forms and its lists' Add, Edit and Delete, without a
front-end."""

from __future__ import annotations

from typing import Any

from ars_magica_manager import commands, form_spec
from ars_magica_manager.forms import familiar as familiar_forms
from ars_magica_manager.models import (
    Ability,
    BondPower,
    Familiar,
    Possession,
    Saga,
)


def _familiar() -> Familiar:
    return Familiar(id="f1", character_id="m1", name="Nox")


def _answer(form: Any, typed: dict[str, Any]):
    """The form's values with `typed` over what it opens with, and the
    problem its validate finds (raises FieldError on a bad field)."""
    assert isinstance(form, commands.Form)
    fields = form.fields()
    raw = {f.key: f.value for f in fields} | typed
    values = form_spec.result(fields, lambda f: raw[f.key])
    problem = form.validate(values) if form.validate else None
    return values, problem


def _save(form: Any, typed: dict[str, Any]) -> Any:
    values, problem = _answer(form, typed)
    assert problem is None
    return form.apply(values)


def test_editing_the_familiar_sets_its_details_and_a_blank_season_is_unset():
    f = _familiar()
    f.season_bound = "Spring"
    form = familiar_forms.edits(f)["Familiar"]
    assert form.title == "Edit Familiar"
    _save(form, {"name": "Umbra", "season_bound": None, "magic_might": "15"})
    assert (f.name, f.season_bound, f.magic_might) == ("Umbra", "", 15)


def test_editing_the_binding_sets_its_cords_as_scores():
    f = _familiar()
    form = familiar_forms.edits(f)["Binding & Cords"]
    assert form.title == "Edit Binding & Cords"
    _save(form, {"binding_technique": "Creo", "golden_cord": "3", "bronze_cord": "1"})
    assert (f.binding_technique, f.binding_form) == ("Creo", "")
    assert (f.golden_cord, f.silver_cord, f.bronze_cord) == (3, 0, 1)


def test_editing_characteristics_sets_soak_and_magic_resistance_too():
    f = _familiar()
    _save(
        familiar_forms.edits(f)["Characteristics"],
        {"quickness": "3", "base_soak": "4", "magic_resistance": "20"},
    )
    assert (f.characteristics.quickness, f.base_soak, f.magic_resistance) == (
        3,
        4,
        20,
    )


def test_editing_wounds_keeps_its_soak_and_fatigue_sets_the_level():
    f = _familiar()
    f.wounds.soak = 2
    form = familiar_forms.edits(f)["Wounds"]
    assert "soak" not in [field.key for field in form.fields()]
    _save(form, {"light": "2", "dead": False})
    assert (f.wounds.light, f.wounds.soak) == (2, 2)
    _save(familiar_forms.edits(f)["Fatigue"], {"level": "winded"})
    assert f.fatigue_level == "winded"


def test_add_edit_and_delete_a_natural_weapon():
    f = _familiar()
    ops = familiar_forms.natural_weapon_ops(f)
    assert ops.add and ops.edit and ops.remove
    form = ops.add()
    assert isinstance(form, commands.Form)
    assert form.title == "Add a Natural Weapon"
    assert "load" not in [field.key for field in form.fields()]
    [book] = [field for field in form.fields() if field.key == "gear_id"]
    assert book.label == "Natural Weapon" and book.fills is not None
    filled = book.fills({"name": "", "gear_id": "natural_teeth"})
    assert filled["weapon_attack"] == 3
    _values, problem = _answer(form, {"name": "Bite", "quantity": "0"})
    assert problem == "Quantity must be at least 1."
    _save(form, {"name": "Bite", "weapon_attack": "3"})
    assert [(w.name, w.kind, w.weapon_attack) for w in f.natural_weapons] == [
        ("Bite", "weapon", 3)
    ]
    assert ops.rows() == ["Bite"]
    edit = ops.edit(0)
    assert isinstance(edit, commands.Form) and edit.title == "Edit Bite"
    _save(edit, {"weapon_damage": "2"})
    assert f.natural_weapons[0].weapon_damage == 2
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question == "Delete Bite?"
    confirm.apply()
    assert f.natural_weapons == []


def test_an_unnamed_natural_weapon_is_this_attack():
    f = _familiar()
    f.natural_weapons.append(Possession(id="w", kind="weapon", name=""))
    ops = familiar_forms.natural_weapon_ops(f)
    assert ops.remove is not None
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question == "Delete this attack?"


def test_adding_an_ability_chooses_it_from_the_catalog_then_asks_its_xp():
    saga = Saga(id="s", name="S")
    f = _familiar()
    f.abilities.append(Ability(name="Brawl", category="General"))
    ops = familiar_forms.ability_ops(saga, f)
    assert ops.add is not None
    choose = ops.add()
    assert isinstance(choose, commands.Choose)
    assert choose.title == "Add an Ability"
    choices = choose.choices()
    names = [c.value.name for c in choices]
    assert "Athletics" in names and "Brawl" not in names
    athletics = next(c.value for c in choices if c.value.name == "Athletics")
    form = choose.apply(athletics)
    assert isinstance(form, commands.Form) and form.save_label == "Confirm"
    assert f.abilities[-1].name == "Brawl"  # nothing added before the last step
    assert form.live is not None and form.live({"xp": 5}).startswith("Athletics: ")
    _values, problem = _answer(form, {"xp": "-1"})
    assert problem == "XP can't be negative."
    _save(form, {"xp": "5", "specialty": "Climbing"})
    added = f.abilities[-1]
    assert (added.name, added.xp, added.specialty) == ("Athletics", 5, "Climbing")


def test_a_templated_ability_asks_what_it_names_first():
    saga = Saga(id="s", name="S")
    f = _familiar()
    ops = familiar_forms.ability_ops(saga, f)
    assert ops.add is not None
    choose = ops.add()
    assert isinstance(choose, commands.Choose)
    craft = next(c.value for c in choose.choices() if c.value.name == "Craft: {craft}")
    params = choose.apply(craft)
    assert isinstance(params, commands.Form)
    assert [field.key for field in params.fields()] == ["craft"]
    details = _save(params, {"craft": "Smith"})
    assert f.abilities == []
    assert isinstance(details, commands.Form)
    _save(details, {"xp": "15"})
    assert [(a.name, a.xp) for a in f.abilities] == [("Craft: Smith", 15)]


def test_edit_and_delete_an_ability():
    saga = Saga(id="s", name="S")
    f = _familiar()
    f.abilities.append(Ability(name="Brawl", category="General", xp=5))
    ops = familiar_forms.ability_ops(saga, f)
    assert ops.edit and ops.remove
    edit = ops.edit(0)
    assert isinstance(edit, commands.Form) and edit.title == "Brawl"
    _save(edit, {"xp": "15", "specialty": ""})
    assert (f.abilities[0].xp, f.abilities[0].specialty) == (15, None)
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question == "Delete Brawl?"
    confirm.apply()
    assert f.abilities == []


def test_add_edit_and_delete_a_bond_power():
    f = _familiar()
    ops = familiar_forms.bond_power_ops(f)
    assert ops.add and ops.edit and ops.remove
    form = ops.add()
    assert isinstance(form, commands.Form) and form.title == "Add a Bond Power"
    _save(form, {"name": "Silent Wings", "level": "10", "form": "Imaginem"})
    [power] = f.bond_powers
    assert (power.name, power.level, power.technique, power.form) == (
        "Silent Wings",
        10,
        "",
        "Imaginem",
    )
    assert power.id
    edit = ops.edit(0)
    assert isinstance(edit, commands.Form) and edit.title == "Edit Silent Wings"
    _save(edit, {"technique": "Perdo"})
    assert f.bond_powers[0].technique == "Perdo"
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question == "Delete Silent Wings?"
    confirm.apply()
    assert f.bond_powers == []


def test_a_new_bond_power_gets_an_id_of_its_own():
    f = _familiar()
    f.bond_powers.append(BondPower("silent_wings", "Silent Wings"))
    familiar_forms.save_bond_power(
        f.bond_powers, None, {"name": "Silent Wings", "technique": None, "form": None}
    )
    assert len({p.id for p in f.bond_powers}) == 2
