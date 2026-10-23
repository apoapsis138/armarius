"""A covenant's sections' Add, Edit and Delete without a front-end: Edit
Covenant and its Description, Boons and Hooks, the Treasury, the
Inhabitants, the Possessions and the library's books."""

from __future__ import annotations

from typing import Any

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import books as bk
from ars_magica_manager import commands, form_spec
from ars_magica_manager import economics as eco
from ars_magica_manager import house_rules as hr
from ars_magica_manager.forms import covenant as covenant_forms
from ars_magica_manager.forms import inhabitant as inhabitant_forms
from ars_magica_manager.forms import library as library_forms
from ars_magica_manager.forms import possession as possession_forms
from ars_magica_manager.models import (
    Character,
    IncomeSource,
    Inhabitant,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import library


def _answer(form: Any, typed: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    """The values `form` saves with `typed` over its fields' own, shown
    fields only, and its validation's refusal (or None)."""
    assert isinstance(form, commands.Form)
    fields = form.fields()
    raw = {f.key: f.value for f in fields} | typed
    shown = [f for f in fields if f.kind != "info" and form_spec.shown(f, raw)]
    values = form_spec.result(shown, lambda f: raw[f.key])
    problem = form.validate(values) if form.validate else None
    return values, problem


def _save(form: Any, typed: dict[str, Any]) -> Any:
    values, problem = _answer(form, typed)
    assert problem is None, problem
    return form.apply(values)


def test_edit_covenant_and_its_description():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    form = covenant_forms.covenant_form(saga, covenant)
    assert form.title == "Edit Covenant"
    _save(form, {"name": "Fengheld", "aura": "5"})
    assert (covenant.name, covenant.aura) == ("Fengheld", 5)
    form = covenant_forms.description_form(covenant)
    assert form.title == "Edit Covenant Description"
    assert form.fields()[0].value == "A nice place"
    _save(form, {"notes": "A *quiet* place"})
    assert covenant.notes == "A *quiet* place"


def test_a_boon_is_chosen_from_the_catalog_then_edited_and_deleted():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    ops = covenant_forms.boon_hook_ops(saga, covenant, "Boon")
    assert ops.add and ops.edit and ops.remove
    choose = ops.add()
    assert isinstance(choose, commands.Choose)
    assert choose.title == "Add a Boon"
    choices = choose.choices()
    wealth = next(c for c in choices if c.value.id == "covbh_boon_major_wealth")
    assert wealth.label.startswith("Wealth")
    assert wealth.detail
    form = choose.apply(wealth.value)
    assert form.title == "Boon: Wealth"
    assert covenant.boons_hooks == []  # nothing until the form is saved
    assert _save(form, {"detail": "a silver mine"}) == []
    assert [bh.vf_id for bh in covenant.boons_hooks] == ["covbh_boon_major_wealth"]
    assert covenant.boons_hooks[0].id
    assert ops.rows() == ["Wealth - a silver mine"]
    taken = next(c for c in choose.choices() if c.value.id == wealth.value.id)
    assert "(taken x1)" in taken.label
    _save(ops.edit(0), {"detail": "a gold mine"})
    assert ops.rows() == ["Wealth - a gold mine"]
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question == "Delete Wealth - a gold mine?"
    confirm.apply()
    assert covenant.boons_hooks == []


def test_a_sagas_own_boon_names_its_choices_when_taken_and_when_edited():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    entry = hr.add(
        saga,
        hr.COVENANT,
        {
            "name": "Vis Spring",
            "type": "Boon",
            "tier": "Minor",
            "category": "Resources",
            "parameters": ["form", "keeper"],
        },
    )
    ops = covenant_forms.boon_hook_ops(saga, covenant, "Boon")
    assert ops.add and ops.edit
    choose = ops.add()
    assert isinstance(choose, commands.Choose)
    form = choose.apply(entry)
    keys = [f.key for f in form.fields()]
    assert keys[:2] == ["form", "keeper"]
    form_field = form.fields()[0]
    assert form_field.kind == "select"
    assert ("Aquam", "aquam") in form_field.options
    _save(form, {"form": "aquam", "keeper": "Old Hilde", "detail": "the well"})
    assert covenant.boons_hooks[0].params == {
        "form": "aquam",
        "keeper": "old hilde",
        "detail": "the well",
    }
    assert ops.rows() == ["Vis Spring (Aquam, Old Hilde) - the well"]
    edit = ops.edit(0)
    assert [f.value for f in edit.fields()[:2]] == ["aquam", "Old Hilde"]
    _save(edit, {"form": "terram"})
    assert ops.rows() == ["Vis Spring (Terram, Old Hilde) - the well"]


def test_a_hooks_rows_skip_the_boons_and_a_resource_hook_says_to_link_it():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    covenant.boons_hooks.append(VirtueFlawInstance("covbh_boon_major_wealth"))
    ops = covenant_forms.boon_hook_ops(saga, covenant, "Hook")
    assert ops.rows() == []
    choose = ops.add()
    contested = next(
        c.value
        for c in choose.choices()
        if c.value.id == "covbh_hook_minor_contested_resource"
    )
    notes = _save(choose.apply(contested), {})
    assert notes and "Link this Hook" in notes[0]
    assert len(ops.rows()) == 1
    edit = ops.edit(0)
    assert "resource" in [f.key for f in edit.fields()]
    ops.remove(0).apply()
    assert [bh.vf_id for bh in covenant.boons_hooks] == ["covbh_boon_major_wealth"]


def test_wealth_and_sources_of_income():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    _save(covenant_forms.wealth_form(covenant), {"wealth": "120"})
    assert covenant.economics.wealth == 120
    ops = covenant_forms.income_ops(covenant)
    form = ops.add()
    assert form.title == "Add a Source of Income"
    _save(form, {"name": "Mill", "income": "40"})
    sources = covenant.economics.income_sources
    assert [(s.name, s.income) for s in sources] == [("Mill", 40)]
    edit = ops.edit(0)
    assert edit.title == "Edit Mill"
    _save(edit, {"contested": True, "secured_until": "1225"})
    assert (sources[0].contested, sources[0].secured_until) == (True, 1225)
    ops.remove(0).apply()
    assert sources == []


def test_a_required_name_is_refused():
    covenant = _sample_saga_with_covenant().covenants[0]
    form = covenant_forms.income_ops(covenant).add()
    fields = form.fields()
    raw = {f.key: f.value for f in fields}
    try:
        form_spec.result([f for f in fields if f.kind != "info"], lambda f: raw[f.key])
    except form_spec.FieldError as error:
        assert str(error) == "Name is required."
    else:
        raise AssertionError("an empty Name was accepted")


def test_an_expenditure_row_takes_its_typed_figures_and_notes():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    ops = covenant_forms.economics_row_ops(saga, covenant, "expenditure")
    assert ops.add is None and ops.remove is None and ops.edit
    index = next(
        i
        for i, row in enumerate(eco.summarize(saga, covenant).expenditure)
        if row.key == "sundry"
    )
    form = ops.edit(index)
    assert isinstance(form, commands.Form)
    _values, problem = _answer(form, {"sundry": "0"})
    assert problem == "There's a cost of at least 1 pound of sundries every year."
    _save(form, {"sundry": "4", "notes": "candles"})
    assert covenant.economics.sundry == 4
    assert covenant.economics.notes["sundry"] == "candles"


def test_emergency_savings_with_a_deficit_offers_to_draw_from_wealth():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    covenant.economics.wealth = 1000
    covenant.economics.sundry = 500  # far more than it earns
    summary = eco.summarize(saga, covenant)
    assert summary.surplus_deficit < 0
    ops = covenant_forms.economics_row_ops(saga, covenant, "savings")
    index = next(
        i for i, row in enumerate(summary.savings) if row.key == "emergency_savings"
    )
    choose = ops.edit(index)
    assert isinstance(choose, commands.Choose)
    labels = [c.label for c in choose.choices()]
    assert labels[0] == "Draw from Wealth"
    # Choosing to edit the row instead leads to its ordinary form.
    assert isinstance(choose.apply(covenant_forms.EDIT_ROW), commands.Form)
    assert covenant.economics.wealth == 1000
    notes = choose.apply(covenant_forms.DRAW)
    assert notes and notes[0].startswith("Drew ")
    assert covenant.economics.wealth == 1000 + summary.surplus_deficit
    assert covenant.economics.emergency_savings == -summary.surplus_deficit


def test_loyalty_population_and_miscellaneous():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    form = inhabitant_forms.loyalty_form(saga, covenant)
    assert form.title == "Edit Loyalty"
    _save(form, {"familiarity": "3", "pension": True})
    assert (covenant.loyalty.familiarity, covenant.loyalty.pension) == (3, True)
    _save(inhabitant_forms.population_form(saga, covenant), {"other_people": "7"})
    assert covenant.population.other_people == 7
    _save(inhabitant_forms.misc_form(covenant), {"aging_magi": "2"})
    assert covenant.population.aging_magi == 2


def test_adding_editing_and_deleting_an_inhabitant():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    ops = inhabitant_forms.inhabitant_ops(saga, covenant, "turb")
    form = ops.add()  # no grogs to offer: straight to the form
    assert isinstance(form, commands.Form)
    assert form.title == "Add a Turb Member"
    _values, problem = _answer(form, {"name": "The watch", "quantity": "0"})
    assert problem == "Quantity must be at least 1."
    _save(form, {"name": "The watch", "quantity": "6"})
    assert ops.rows() == ["The watch"]
    edit = ops.edit(0)
    assert edit.title == "Edit The watch"
    _save(edit, {"responsibility": "Walls"})
    assert covenant.inhabitants[0].responsibility == "Walls"
    confirm = ops.remove(0)
    assert confirm.question == "Delete The watch?"
    confirm.apply()
    assert covenant.inhabitants == []


def test_a_grog_kind_first_offers_the_covenants_grogs():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    saga.characters.append(
        Character(id="g1", name="Rolf", type="grog", covenant_id="cov1")
    )
    choose = inhabitant_forms.inhabitant_ops(saga, covenant, "specialist").add()
    assert isinstance(choose, commands.Choose)
    choices = choose.choices()
    assert [c.label for c in choices] == [inhabitant_forms.NEW_PERSON, "Rolf"]
    form = choose.apply(choices[1].value)
    assert form.fields()[0].value == "Rolf"
    assert covenant.inhabitants == []
    _save(form, {})
    assert covenant.inhabitants[0].character_id == "g1"


def test_a_magus_from_a_sheet_is_removed_from_the_list_not_deleted():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    ops = inhabitant_forms.inhabitant_ops(saga, covenant, "magus")
    assert ops.rows() == ["Leandro"]
    confirm = ops.remove(0)
    assert confirm.question.startswith("Remove Leandro from the Magi list?")
    confirm.apply()
    assert ops.rows() == []
    assert saga.characters[0].covenant_id == "cov1"


def test_adding_editing_and_deleting_a_possession():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    ops = possession_forms.possession_ops(saga, covenant, "item")
    form = ops.add()
    assert form.title == "Add a Item"
    _save(form, {"name": "Silver chalice", "quantity": "2"})
    assert ops.rows() == ["Silver chalice"]
    _save(ops.edit(0), {"quantity": "3"})
    assert covenant.possessions[-1].quantity == 3
    ops.remove(0).apply()
    assert ops.rows() == []


def test_a_vis_store_asks_where_it_is_kept():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    ops = possession_forms.possession_ops(saga, covenant, "vis_store")
    edit = ops.edit(0)
    assert edit.title == "Edit Ignem Vis"
    assert "place" in [f.key for f in edit.fields()]
    _save(edit, {"pawns": "9"})
    assert covenant.possessions[0].pawns == 9


def test_a_sanctum_from_a_laboratory_cannot_be_deleted_here():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    ops = possession_forms.possession_ops(saga, covenant, "sanctum")
    assert ops.rows() == ["Leandro's Sanctum"]
    refused = ops.remove(0)
    assert isinstance(refused, commands.Refuse)
    assert "laboratory of this covenant" in refused.why


def test_adding_editing_and_deleting_a_book():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    owner = bk.owner_value("covenant", covenant.id)
    ops = library_forms.book_ops(
        saga, lambda: library.books_in_covenant(saga, covenant), owner
    )
    form = ops.add()
    assert form.title == "Add a Book"
    try:
        _answer(form, {"name": "De Igne", "type": "Tractatus", "subject_kind": "Art"})
    except form_spec.FieldError as error:
        # The Art is asked for, and required, once the Type is a tractatus.
        assert str(error) == "Art is required."
    else:
        raise AssertionError("a tractatus with no Art was accepted")
    _save(
        form,
        {
            "name": "De Igne",
            "type": "Tractatus",
            "subject_kind": "Art",
            "art": "Ignem",
            "quality": "7",
        },
    )
    assert ops.rows()[-1] == "De Igne"
    added = saga.books[-1]
    assert (added.type, added.art, added.quality) == ("Tractatus", "Ignem", 7)
    assert (added.owner_kind, added.owner_id) == ("covenant", "cov1")
    _save(ops.edit(2), {"quality": "8"})
    assert added.quality == 8
    confirm = ops.remove(2)
    assert confirm.question == "Delete De Igne?"
    confirm.apply()
    assert added not in saga.books


def test_the_book_forms_spell_is_chosen_from_a_searchable_list():
    saga = _sample_saga_with_covenant()
    lab_text = saga.books[1]
    fields = {f.key: f for f in library_forms.book_fields(saga, lab_text, "")}
    spell = fields["spell_id"]
    assert spell.kind == "picker" and spell.choose is not None
    step = spell.choose(None)
    assert isinstance(step, commands.Choose)
    first = step.choices()[0]
    assert step.apply(first.value) == commands.Picked(first.value)
    picked = library_forms.book_fields(
        saga, lab_text, "", spell_picker=lambda _current: None
    )
    assert next(f for f in picked if f.key == "spell_id").kind == "picker"


def test_cancelling_a_form_changes_nothing():
    """Every step builds without changing the saga: only apply does."""
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    covenant.economics.income_sources.append(IncomeSource("s1", "Mill"))
    covenant.inhabitants.append(Inhabitant("i1", "turb", "The watch"))
    before = repr(saga)
    for ops in (
        covenant_forms.income_ops(covenant),
        inhabitant_forms.inhabitant_ops(saga, covenant, "turb"),
        possession_forms.possession_ops(saga, covenant, "vis_store"),
        covenant_forms.boon_hook_ops(saga, covenant, "Boon"),
    ):
        assert ops.add is not None
        step = ops.add()
        if isinstance(step, commands.Form):
            step.fields()
        if ops.edit is not None and ops.rows():
            ops.edit(0).fields()
        if ops.remove is not None and ops.rows():
            ops.remove(0)
    assert repr(saga) == before
