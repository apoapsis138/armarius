"""Saga Content's Add, Edit and Delete (saga spells, House Rules, players,
sources, books in play, catalogs, hidden entries), without a front-end."""

from __future__ import annotations

from typing import Any

from ars_magica_manager import commands, form_spec, sourcebooks
from ars_magica_manager import house_rules as hr
from ars_magica_manager import players as pl
from ars_magica_manager import saga_content as sc
from ars_magica_manager import spells as spl
from ars_magica_manager.forms import saga_content as scf
from ars_magica_manager.models import (
    Character,
    Saga,
    SagaSource,
    VirtueFlawInstance,
)
from ars_magica_manager.remote.passcodes import RemotePasscodes, passcodes_path


def _answer(form: commands.Command, typed: dict[str, Any]):
    """The values `form` saves with `typed` over its prefill, and its
    validation problem."""
    assert isinstance(form, commands.Form)
    fields = form.fields()
    raw = {f.key: f.value for f in fields} | typed
    values = form_spec.result(fields, lambda f: raw[f.key])
    problem = form.validate(values) if form.validate else None
    return values, problem


def _save(form: commands.Command, typed: dict[str, Any]) -> Any:
    values, problem = _answer(form, typed)
    assert problem is None
    assert isinstance(form, commands.Form)
    return form.apply(values)


def _saga() -> Saga:
    return Saga(
        id="s",
        name="S",
        characters=[Character(id="c1", name="Ana", type="companion")],
    )


def test_a_saga_spell_is_added_edited_and_deleted():
    saga = _saga()
    ops = scf.spell_ops(saga, lambda: list(saga.spells))
    assert ops.add is not None and ops.edit is not None and ops.remove is not None
    form = ops.add()
    assert isinstance(form, commands.Form) and form.title == "Add a Spell"
    _, problem = _answer(
        form,
        {
            "name": "Spark",
            "technique": "Creo",
            "form": "Ignem",
            "level": "0",
            "range": "Touch",
            "duration": "Momentary",
            "target": "Individual",
        },
    )
    assert problem == "Level must be at least 1 (or blank for a General spell)."
    _save(
        form,
        {
            "name": "Spark",
            "technique": "Creo",
            "form": "Ignem",
            "level": "5",
            "range": scf.OTHER,
            "range_other": "Road",
            "duration": "Momentary",
            "target": "Individual",
        },
    )
    [spell] = saga.spells
    assert (spell.name, spell.level, spell.range) == ("Spark", 5, "Road")
    assert ops.rows() == ["Spark"]
    edit = ops.edit(0)
    assert isinstance(edit, commands.Form) and edit.title == "Edit Spark"
    _save(edit, {"name": "Big Spark"})
    assert saga.spells[0].name == "Big Spark"
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question == "Delete Big Spark?"
    confirm.apply()
    assert saga.spells == []


def test_a_catalog_spell_is_read_only():
    saga = _saga()
    catalog_spell = spl.all_spells(saga)[0]
    ops = scf.spell_ops(saga, lambda: [catalog_spell])
    assert ops.edit is not None and ops.remove is not None
    for step in (ops.edit(0), ops.remove(0)):
        assert isinstance(step, commands.Refuse)
        assert "catalog spell, so it's read-only" in step.why


def test_a_house_rule_is_added_edited_and_refused_while_held():
    saga = _saga()
    ops = scf.house_rule_ops(saga)
    assert ops.add is not None and ops.edit is not None and ops.remove is not None
    form = ops.add()
    assert isinstance(form, commands.Form) and form.title == "Add a House Rule"
    _save(form, {"kind": hr.CHARACTER, "name": "Storm-Touched", "vf_type": "Virtue"})
    [(kind, entry)] = hr.all_entries(saga)
    assert (kind, entry.name, entry.type, entry.cost) == (
        hr.CHARACTER,
        "Storm-Touched",
        "Virtue",
        1,
    )
    assert form.live is not None
    assert "costs 1 point" in form.live({"vf_type": "Virtue", "tier": "Minor"})
    # The same name, type and tier again is refused.
    _, problem = _answer(ops.add(), {"name": "Storm-Touched"})
    assert problem == "There is already a Minor Virtue called Storm-Touched."
    edit = ops.edit(0)
    assert isinstance(edit, commands.Form)
    assert edit.fields()[0].kind == "info"  # what it is for is fixed
    _save(edit, {"tier": "Major"})
    [(kind, entry)] = hr.all_entries(saga)
    assert entry.cost == 3
    saga.characters[0].virtues_flaws.append(VirtueFlawInstance(entry.id))
    refused = ops.remove(0)
    assert isinstance(refused, commands.Refuse)
    assert refused.why == "Storm-Touched is held by Ana: remove it there first."
    saga.characters[0].virtues_flaws.clear()
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    confirm.apply()
    assert hr.all_entries(saga) == []


def test_a_covenant_house_rule_takes_a_boon_or_hook():
    saga = _saga()
    ops = scf.house_rule_ops(saga)
    assert ops.add is not None
    _save(ops.add(), {"kind": hr.COVENANT, "name": "Old Feud", "bh_type": "Hook"})
    [(kind, entry)] = hr.all_entries(saga)
    assert (kind, entry.type, entry.cost) == (hr.COVENANT, "Hook", -1)


def test_a_player_is_added_edited_and_deleted():
    saga = _saga()
    ops = scf.player_ops(saga)
    assert ops.add is not None and ops.edit is not None and ops.remove is not None
    _, problem = _answer(ops.add(), {"name": "Jo", "passcode": "secret"})
    assert problem == "A passcode needs at least 14 characters."
    _save(ops.add(), {"name": "Jo", "passcode": "secret passcode phrase"})
    [player] = saga.players
    remote = RemotePasscodes(passcodes_path(saga.name))
    assert pl.passcode_matches(player, "secret passcode phrase")
    assert remote.allows(player)
    _, problem = _answer(ops.add(), {"name": "Jo", "passcode": "x" * 14})
    assert problem == "There is already a player called Jo."
    # A blank passcode keeps theirs.
    _save(ops.edit(0), {"role": pl.STORYGUIDE})
    assert player.role == pl.STORYGUIDE
    assert pl.passcode_matches(player, "secret passcode phrase")
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question.startswith("Delete the player Jo?")
    confirm.apply()
    assert saga.players == []
    assert not remote.allows(player)


def test_a_blank_passcode_makes_a_table_only_player():
    saga = _saga()
    _save(scf.player_ops(saga).add(), {"name": "Mo"})
    [player] = saga.players
    assert player.passcode_hash == ""
    assert pl.sign_in(saga, "Mo", "") is None
    assert "table-only" in pl.detail_text(saga, player)


def test_a_saga_source_is_added_renamed_and_refused_while_cited():
    saga = _saga()
    ops = scf.source_ops(saga)
    assert ops.add is not None and ops.edit is not None and ops.remove is not None
    _save(ops.add(), {"abbreviation": "HR", "title": "Our rules"})
    assert [s.abbreviation for s in saga.sources] == ["HR"]
    _, problem = _answer(ops.add(), {"abbreviation": "HR"})
    assert problem is not None
    hr.add(
        saga,
        hr.CHARACTER,
        {"name": "X", "type": "Virtue", "tier": "Minor", "source": "HR"},
    )
    _save(ops.edit(0), {"abbreviation": "OR"})
    assert saga.custom_virtues_flaws[0].source == "OR"
    refused = ops.remove(0)
    assert isinstance(refused, commands.Refuse)
    assert refused.why == "OR is cited by X: change them first."
    hr.recite(saga, "OR", "")
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    confirm.apply()
    assert saga.sources == []


def test_the_books_in_play_are_ticked():
    saga = _saga()
    saga.sources.append(SagaSource(abbreviation="HR", title="Ours"))
    form = scf.books_form(saga)
    fields = form.fields()
    keys = [f.key for f in fields if f.kind == "check"]
    assert keys[-1] == scf.BOOK_KEY + "HR"
    assert len(keys) == len(sourcebooks.SUPPLEMENTS) + 1
    assert all(f.value for f in fields if f.kind == "check")
    ticked = {key: key == scf.BOOK_KEY + "HR" for key in keys}
    _save(form, ticked)
    assert [b for b in sc.every_book(saga) if sc.is_in_play(saga, b)] == [
        sourcebooks.CORE,
        "HR",
    ]


def test_a_catalog_is_offered_or_not():
    saga = _saga()
    ops = scf.catalog_ops(saga)
    assert ops.add is None and ops.remove is None and ops.edit is not None
    assert ops.rows()[0] == "Virtues & Flaws"
    edit = ops.edit(ops.rows().index("Abilities"))
    assert isinstance(edit, commands.Form) and edit.title == "Catalog: Abilities"
    _save(edit, {"shown": False})
    assert saga.hidden_catalogs == ["abilities"]


def test_a_catalog_entry_is_hidden_then_offered_again():
    saga = _saga()
    ops = scf.hidden_ops(saga, lambda: "abilities")
    assert ops.add is not None and ops.remove is not None and ops.edit is None
    form = ops.add()
    assert isinstance(form, commands.Form) and form.save_label == "Next"
    assert form.fields()[0].value == "abilities"
    choose = _save(form, {})
    assert isinstance(choose, commands.Choose)
    assert saga.hidden_entries == {}  # nothing changes until the entry is chosen
    first = choose.choices()[0]
    choose.apply(first.value)
    assert saga.hidden_entries == {"abilities": [first.value]}
    assert len(choose.choices()) == len(scf.hideable(saga, "abilities"))
    assert first.value not in [c.value for c in choose.choices()]
    assert len(ops.rows()) == 1
    confirm = ops.remove(0)
    assert isinstance(confirm, commands.Confirm)
    assert confirm.question.endswith("again?")
    confirm.apply()
    assert saga.hidden_entries == {}
