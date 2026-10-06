"""Saving when several copies of the app share a saga file."""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager

import pytest

from ars_magica_manager import storage
from ars_magica_manager.merge import merge
from ars_magica_manager.models import Book, Character, Saga

# -- merge() on plain data --


def test_only_what_we_changed_is_applied():
    base = {"a": 1, "b": 1}
    merged, conflicts = merge(base, {"a": 2, "b": 1}, {"a": 1, "b": 3})
    assert merged == {"a": 2, "b": 3}
    assert conflicts == []


def test_both_changing_the_same_value_keeps_ours_and_says_where():
    merged, conflicts = merge({"x": {"y": 1}}, {"x": {"y": 2}}, {"x": {"y": 3}})
    assert merged == {"x": {"y": 2}}
    assert conflicts == ["x.y"]


def test_records_merge_by_id():
    base = {"rs": [{"id": "a", "v": 1}, {"id": "b", "v": 1}, {"id": "c", "v": 1}]}
    ours = {"rs": [{"id": "a", "v": 2}, {"id": "c", "v": 1}, {"id": "d", "v": 1}]}
    theirs = {"rs": [{"id": "a", "v": 1}, {"id": "b", "v": 1}, {"id": "c", "v": 5}]}
    merged, conflicts = merge(base, ours, theirs)
    # a: ours changed; b: ours deleted; c: theirs changed; d: ours added.
    assert merged == {
        "rs": [{"id": "a", "v": 2}, {"id": "c", "v": 5}, {"id": "d", "v": 1}]
    }
    assert conflicts == []


def test_records_both_sides_added_are_all_kept():
    base = {"rs": []}
    merged, _ = merge(base, {"rs": [{"id": "a"}]}, {"rs": [{"id": "b"}]})
    assert merged == {"rs": [{"id": "b"}, {"id": "a"}]}


def test_deleting_a_record_the_other_side_changed_is_a_conflict_ours_wins():
    base = {"rs": [{"id": "a", "v": 1}]}
    merged, conflicts = merge(base, {"rs": []}, {"rs": [{"id": "a", "v": 2}]})
    assert merged == {"rs": []}
    assert conflicts == ["rs[a]"]


def test_lists_without_ids_are_one_value():
    base = {"tags": ["x"]}
    merged, conflicts = merge(base, {"tags": ["x", "y"]}, {"tags": ["x", "z"]})
    assert merged == {"tags": ["x", "y"]}
    assert conflicts == ["tags"]


# -- save_saga with two copies of the app --


@contextmanager
def _copy(seen: dict) -> Iterator[None]:
    """Act as one copy of the app: its own memory of what it last saw."""
    kept = storage._last_seen
    storage._last_seen = seen
    try:
        yield
    finally:
        storage._last_seen = kept


def _saga() -> Saga:
    saga = Saga(id="dammerstein", name="Dammerstein")
    saga.characters = [
        Character(id="mag1", name="Corvinus", type="magus"),
        Character(id="com1", name="Banna", type="companion"),
    ]
    saga.books = [Book(id="b1", name="Summa on Ignem", type="Summa")]
    return saga


@pytest.fixture
def two_copies():
    storage.save_saga(_saga())
    gm, ana = {}, {}
    with _copy(gm):
        gm_saga = storage.load_saga("dammerstein")
    with _copy(ana):
        ana_saga = storage.load_saga("dammerstein")
    return (gm, gm_saga), (ana, ana_saga)


def test_two_copies_changing_different_records_both_keep_their_changes(two_copies):
    (gm, gm_saga), (ana, ana_saga) = two_copies
    ana_saga.character("com1").name = "Banna the Bold"
    with _copy(ana):
        storage.save_saga(ana_saga)
    gm_saga.character("mag1").name = "Corvinus of Bonisagus"
    gm_saga.books.append(Book(id="b2", name="Tractatus on Corpus", type="Tractatus"))
    with _copy(gm):
        storage.save_saga(gm_saga)
        assert storage.last_conflicts == []

    on_disk = storage.load_saga("dammerstein")
    assert [c.name for c in on_disk.characters] == [
        "Corvinus of Bonisagus",
        "Banna the Bold",
    ]
    assert [b.id for b in on_disk.books] == ["b1", "b2"]


def test_two_copies_changing_different_fields_of_one_character(two_copies):
    (gm, gm_saga), (ana, ana_saga) = two_copies
    ana_saga.character("com1").name = "Banna the Bold"
    with _copy(ana):
        storage.save_saga(ana_saga)
    gm_saga.character("com1").covenant_id = "cov1"
    with _copy(gm):
        storage.save_saga(gm_saga)

    banna = storage.load_saga("dammerstein").character("com1")
    assert (banna.name, banna.covenant_id) == ("Banna the Bold", "cov1")


def test_the_later_save_wins_the_same_value(two_copies):
    (gm, gm_saga), (ana, ana_saga) = two_copies
    ana_saga.character("com1").name = "Banna the Bold"
    with _copy(ana):
        storage.save_saga(ana_saga)
    gm_saga.character("com1").name = "Banna the Wise"
    with _copy(gm):
        storage.save_saga(gm_saga)
        assert storage.last_conflicts == ["characters[com1].name"]
    assert storage.load_saga("dammerstein").character("com1").name == "Banna the Wise"


def test_a_copy_that_changed_nothing_never_undoes_another(two_copies):
    (gm, gm_saga), (ana, ana_saga) = two_copies
    ana_saga.characters = [c for c in ana_saga.characters if c.id != "com1"]
    with _copy(ana):
        storage.save_saga(ana_saga)
    # The storyguide's copy still holds Banna in memory, unchanged.
    gm_saga.description = "A solo campaign"
    with _copy(gm):
        storage.save_saga(gm_saga)

    on_disk = storage.load_saga("dammerstein")
    assert [c.id for c in on_disk.characters] == ["mag1"]
    assert on_disk.description == "A solo campaign"


def test_one_copy_saving_alone_writes_exactly_its_saga():
    saga = _saga()
    storage.save_saga(saga)
    saga.characters.reverse()
    saga.books.clear()
    storage.save_saga(saga)
    on_disk = json.loads(storage.saga_path("dammerstein").read_text(encoding="utf-8"))
    assert [c["id"] for c in on_disk["characters"]] == ["com1", "mag1"]
    assert on_disk["books"] == []


def test_a_lock_left_by_a_copy_that_died_is_taken_over(monkeypatch):
    lock = storage.SAGAS_DIR / ".dammerstein.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text("")
    monkeypatch.setattr(storage, "_LOCK_WAIT", 0.1)
    storage.save_saga(_saga())  # waits briefly, then takes it over
    assert storage.load_saga("dammerstein").name == "Dammerstein"
    assert not lock.exists()


def test_reading_a_saga_file_gives_the_same_data_every_time():
    """A save compares the file as another copy left it with what this copy
    loaded: reading the same file twice must not differ (no fresh random
    ids), or a copy would see changes nobody made."""
    from test_storage import _saga_with_every_record

    saga = _saga_with_every_record()
    storage.save_saga(saga)
    path = storage.saga_path(saga.id)
    data = json.loads(path.read_text(encoding="utf-8"))
    # An older save: laboratory Virtues and covenant Boons without ids.
    for lab in data["laboratories"]:
        for vf in lab["virtues_flaws"]:
            vf["id"] = ""
    for covenant in data["covenants"]:
        for bh in covenant["boons_hooks"]:
            bh["id"] = ""
    text = json.dumps(data)
    assert storage._normalized(text) == storage._normalized(text)


def test_an_older_file_two_copies_loaded_still_merges_by_record():
    saga = _saga()
    saga.laboratories = []
    storage.save_saga(saga)
    path = storage.saga_path("dammerstein")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["laboratories"] = [
        {
            "id": "lab1",
            "name": "Tower",
            "covenant_id": None,
            "virtues_flaws": [{"vf_id": "labvf_a"}],
        }
    ]
    path.write_text(json.dumps(data), encoding="utf-8")
    gm, ana = {}, {}
    with _copy(gm):
        gm_saga = storage.load_saga("dammerstein")
    with _copy(ana):
        ana_saga = storage.load_saga("dammerstein")
    ana_saga.character("com1").name = "Banna the Bold"
    with _copy(ana):
        storage.save_saga(ana_saga)
    gm_saga.laboratories[0].virtues_flaws.clear()
    with _copy(gm):
        storage.save_saga(gm_saga)
    on_disk = storage.load_saga("dammerstein")
    assert on_disk.laboratories[0].virtues_flaws == []
    assert on_disk.character("com1").name == "Banna the Bold"


def test_another_copys_changes_survive_this_copys_next_saves(two_copies):
    # Found running two real processes: after merging, a copy's second save
    # took the file to be its own saga again and wrote the other's out.
    (gm, gm_saga), (ana, ana_saga) = two_copies
    ana_saga.books.append(Book(id="ana1", name="Ana's notes", type="Tractatus"))
    with _copy(ana):
        storage.save_saga(ana_saga)
    for name in ("Corvinus I", "Corvinus II"):
        gm_saga.character("mag1").name = name
        with _copy(gm):
            storage.save_saga(gm_saga)

    on_disk = storage.load_saga("dammerstein")
    assert [b.id for b in on_disk.books] == ["b1", "ana1"]
    assert on_disk.character("mag1").name == "Corvinus II"
