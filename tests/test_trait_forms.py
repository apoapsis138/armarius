"""Personality Traits and Reputations' Add, Edit and Delete, without a
front-end."""

from __future__ import annotations

from ars_magica_manager import commands, form_spec
from ars_magica_manager.forms import trait as trait_forms
from ars_magica_manager.models import ScoredTrait


def _answer(form: commands.Form, typed: dict[str, str | bool]):
    fields = form.fields()
    raw = {f.key: f.value for f in fields} | typed
    values = form_spec.result(fields, lambda f: raw[f.key])
    problem = form.validate(values) if form.validate else None
    return values, problem


def test_add_edit_and_delete_a_trait():
    traits: list[ScoredTrait] = []
    ops = trait_forms.trait_ops(traits, "section-personality-traits")
    assert ops.add is not None and ops.edit is not None and ops.remove is not None
    form = ops.add()
    assert isinstance(form, commands.Form)
    assert form.title == "Add a Personality Trait"
    values, problem = _answer(form, {"name": "Brave", "score": "2"})
    assert problem is None
    assert form.apply(values) is None
    assert [(t.name, t.score) for t in traits] == [("Brave", 2)]
    assert ops.rows()[0].startswith("Brave")
    edit = ops.edit(0)
    assert isinstance(edit, commands.Form)
    assert edit.fields()[0].value == "Brave"
    edit.apply(_answer(edit, {"score": "-1"})[0])
    assert traits[0].score == -1
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question == "Delete Brave?"
    confirm.apply()
    assert traits == []


def test_a_covenant_reputation_has_no_cap_and_may_be_unknown():
    traits: list[ScoredTrait] = []
    ops = trait_forms.trait_ops(traits, "section-cov-reputations")
    assert ops.add is not None
    form = ops.add()
    assert isinstance(form, commands.Form)
    keys = [f.key for f in form.fields()]
    assert keys == ["name", "score", "type", "reach", "bad", "known"]
    # No cap: a Major Prestige Boon's Reputation is 9 (DE p. 184).
    _values, problem = _answer(form, {"name": "Famed", "score": "9"})
    assert problem is None
    values, problem = _answer(form, {"name": "Feared", "score": "-2", "known": False})
    assert problem is None
    form.apply(values)
    assert traits[0].known is False
