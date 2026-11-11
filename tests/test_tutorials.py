"""The tutorial sagas shipped in data/tutorials: one per walkthrough guide,
each readable as a saga file, each started as a fresh saga of its own."""

import json

import pytest

from ars_magica_manager import storage, title_page, tutorials
from ars_magica_manager.commands import Picked
from ars_magica_manager.forms import saga as saga_forms


def test_every_guide_has_a_tutorial_in_order():
    found = tutorials.listed()
    assert [t.number for t in found] == list(range(1, 18))
    assert found[0].title == "Making a Magus"
    assert found[0].label == "1. Making a Magus (Spring 1220)"
    assert all(not t.title[0].isdigit() for t in found)


def test_the_guides_ship_beside_them_as_one_book():
    assert tutorials.GUIDE_BOOK.is_file()
    assert tutorials.GUIDE_BOOK.read_bytes()[:5] == b"%PDF-"


def test_every_tutorial_reads_as_a_saga_file():
    broken = []
    for tutorial in tutorials.listed():
        data = json.loads(tutorial.path.read_text(encoding="utf-8"))
        try:
            storage.saga_from_data(data)
        except ValueError as problem:
            broken.append(f"{tutorial.path.name}: {problem}")
    assert not broken, "\n".join(broken)


def test_a_tutorial_carries_no_players_or_seats():
    with_players = [
        t.path.name
        for t in tutorials.listed()
        if json.loads(t.path.read_text(encoding="utf-8")).get("players")
    ]
    assert not with_players


def test_starting_a_tutorial_twice_gives_two_fresh_sagas():
    tutorial = tutorials.listed()[0]
    first = tutorials.start(tutorial)
    second = tutorials.start(tutorial)
    assert first.id != second.id
    assert set(storage.list_sagas()) == {first.id, second.id}
    again = storage.load_saga(second.id)
    assert again.name == "Making a Magus"
    assert all(c.saga_id == second.id for c in again.covenants)


def test_the_form_lists_every_tutorial_and_opens_the_new_saga():
    form = saga_forms.tutorial_form()
    (field,) = form.fields()
    assert len(field.options) == 17
    assert field.value == "1"
    assert form.live is not None
    assert "The Walkthroughs.pdf" in form.live({"tutorial": "3"})
    end = form.apply({"tutorial": "3"})
    assert isinstance(end, Picked)
    assert storage.load_saga(str(end.value)).name == "A Year at Rabenstein"


def test_the_title_page_offers_the_tutorials():
    page = title_page.title_page([])
    learn = next(c for c in page.choices if c.key == title_page.LEARN)
    assert title_page.TUTORIAL in [c.key for c in learn.then]


def test_a_tutorial_file_that_is_not_a_saga_is_named(tmp_path):
    (tmp_path / "01_broken.json").write_text("[1, 2]", encoding="utf-8")
    with pytest.raises(ValueError, match="01_broken.json"):
        tutorials.listed(tmp_path)
