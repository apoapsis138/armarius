"""Updating a record from an export of it (record_update.py): the file's
version replaces it in place, keeping its id and where it sits in the
saga, and the preview says what changes first."""

from __future__ import annotations

import json

import pytest
from support import everything_saga

from ars_magica_manager import record_update as ru
from ars_magica_manager import transfer
from ars_magica_manager.models import Book, Character, Saga


def _magus(saga: Saga) -> Character:
    return next(c for c in saga.characters if c.type == "magus" and c.assigned_lab_id)


def _export(saga: Saga, record: transfer.Record, **options) -> dict:
    """The record's export, as read back from its file."""
    return json.loads(json.dumps(transfer.export_data(saga, record, **options)))


def test_a_character_is_updated_in_place_keeping_its_place():
    saga = everything_saga()
    magus = _magus(saga)
    covenant, lab = magus.covenant_id, magus.assigned_lab_id
    data = _export(saga, magus)
    held = {b.id for b in saga.books if b.owner_id == magus.id}
    magus.name = "Somebody Else"
    magus.abilities = []
    plan = ru.plan_update(saga, magus, data)
    assert plan.changes[0] == f"Name: Somebody Else → {data['name']}"
    assert any(line.startswith("Abilities: ") for line in plan.changes)
    ru.apply(saga, plan)
    assert saga.character(magus.id) is magus
    assert magus.name == data["name"] and magus.abilities
    assert (magus.covenant_id, magus.assigned_lab_id) == (covenant, lab)
    lab_record = saga.laboratory(lab)
    assert lab_record is not None and lab_record.owner_id == magus.id
    # Its books came back under the same ids, not as copies.
    assert {b.id for b in saga.books if b.owner_id == magus.id} == held
    assert ru.plan_update(saga, magus, data).changes == []


def test_what_it_holds_is_replaced_by_the_files():
    saga = everything_saga()
    magus = _magus(saga)
    data = _export(saga, magus)
    saga.books.append(
        Book(
            id="extra",
            name="Stray Notes",
            type="Tractatus",
            owner_kind="character",
            owner_id=magus.id,
        )
    )
    plan = ru.plan_update(saga, magus, data)
    assert "Books: 1 removed" in plan.changes
    ru.apply(saga, plan)
    assert all(b.id != "extra" for b in saga.books)


def test_a_file_from_another_saga_keeps_the_records_own_id():
    saga = everything_saga()
    magus = _magus(saga)
    data = _export(saga, magus)
    data["saga"]["characters"][0]["id"] = "someone-elsewhere"
    plan = ru.plan_update(saga, magus, data)
    assert plan.incoming.id == magus.id
    ru.apply(saga, plan)
    assert saga.character(magus.id) is magus
    assert saga.character("someone-elsewhere") is None


def test_the_file_must_hold_the_same_kind_of_record():
    saga = everything_saga()
    data = _export(saga, saga.laboratories[0])
    with pytest.raises(ValueError, match="holds a laboratory, not a character"):
        ru.plan_update(saga, _magus(saga), data)


def test_a_covenant_with_its_members_updates_the_covenant_only():
    saga = everything_saga()
    covenant = saga.covenants[0]
    data = _export(saga, covenant, with_members=True)
    names = sorted(c.name for c in saga.characters)
    data["saga"]["covenants"][0]["notes"] = "Rebuilt after the fire."
    plan = ru.plan_update(saga, covenant, data)
    assert any(line.startswith("Notes: ") for line in plan.changes)
    text = ru.preview(plan, "keep.amm.json")
    assert text.startswith(f"Update {covenant.name} from keep.amm.json")
    assert "left as they are here" in text
    ru.apply(saga, plan)
    assert covenant.notes == "Rebuilt after the fire."
    assert sorted(c.name for c in saga.characters) == names
    # Its inhabitants still point at their sheets.
    linked = [i.character_id for i in covenant.inhabitants if i.character_id]
    assert all(saga.character(i) is not None for i in linked)


def test_the_preview_says_where_it_stays():
    saga = everything_saga()
    lab = saga.laboratories[0]
    data = _export(saga, lab)
    lab.name = "Old Name"
    text = ru.preview(ru.plan_update(saga, lab, data), "lab.amm.json")
    assert "Name: Old Name → " in text
    assert "Its covenant and owner stay as they are here." in text
