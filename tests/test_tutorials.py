"""The tutorial sagas shipped in data/tutorials: one per walkthrough guide,
each readable as a saga file, each started as a fresh saga of its own, its
characters and covenants showing the interests their guide uses and no
more than their Default Interests besides."""

import json
from functools import cache
from pathlib import Path

import pytest

from ars_magica_manager import deeds, storage, title_page, tutorials
from ars_magica_manager.commands import Picked
from ars_magica_manager.forms import saga as saga_forms
from ars_magica_manager.models import Saga

#: Each guide's featured characters, the ones its steps open or act on, and
#: the interests those steps need on (an action's interest, or the interest
#: whose chapter a step opens). Read from the guides; a guide whose steps
#: only make new characters features none of its saga's.
FEATURED: dict[int, dict[str, tuple[str, ...]]] = {
    1: {"Leandro of Bonisagus": ()},
    2: {},
    3: {"Leandro of Bonisagus": (), "Adelheid of Flambeau": ()},
    4: {"Adelheid of Flambeau": (deeds.RESEARCH,)},
    5: {"Adelheid of Flambeau": ()},
    6: {
        "Hephaestina of Verditius": (),
        "Ottokar of Verditius": (),
        "Leandro of Bonisagus": (),
    },
    7: {
        "Leandro of Bonisagus": (deeds.HERMETIC_MYSTERIES,),
        "Adelheid of Flambeau": (deeds.INSIGHT,),
        "Ottokar of Verditius": (deeds.HERMETIC_MYSTERIES,),
        "Magister Albrecht of Esslingen": (),
    },
    8: {},
    9: {},
    10: {
        "Meister Heinz the Mason": (),
        "Meister Ruprecht the Shipwright": (),
        "Martin the Woodward": (),
        "Leandro of Bonisagus": (),
        "Adelheid of Flambeau": (),
    },
    11: {"Sir Aimery of Vaux": (deeds.KNIGHTLY, deeds.AGENTS)},
    12: {"Sir Aimery of Vaux": (), "Ulrich the Bold": ()},
    13: {
        "Adelheid of Flambeau": (),
        "Rudolf of Tremere": (),
        "Signum Irruptus": (),
        "Murion": (),
        "Stentorius": (),
        "Theoderich of Augsburg": (),
    },
    14: {"Murion": ()},
    15: {"Murion": ()},
    16: {"Adelheid of Flambeau": ()},
    17: {
        "Thekla of Jerbiton": (),
        "Wolfram of Tytalus": (),
        "Bruno of Mercere": (),
        "Rosamund of Bonisagus": (),
    },
}

#: The covenant interests each guide's steps use, by covenant; every other
#: covenant of its saga uses none.
COVENANTS_USE: dict[int, dict[str, tuple[str, ...]]] = {
    10: {"Rabenstein": (deeds.SHIPS,)},
    11: {"Val Sombre": (deeds.MANORS,)},
}


@cache
def _texts() -> tuple[tuple[int, str], ...]:
    return tuple(
        (t.number, t.path.read_text(encoding="utf-8")) for t in tutorials.listed()
    )


def _sagas() -> list[tuple[int, Saga]]:
    """Each tutorial as a saga of its own, read afresh for each test."""
    return [(n, storage.saga_from_data(json.loads(text))) for n, text in _texts()]


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


def test_every_guide_step_finds_the_interests_it_needs_on():
    wrong = []
    for number, saga in _sagas():
        people = {c.name: c for c in saga.characters}
        for name, needs in FEATURED[number].items():
            if name not in people:
                wrong.append(f"{number}: no {name}")
                continue
            off = deeds.interests_off(people[name])
            wrong += [f"{number}: {name} has {i} off" for i in needs if i in off]
    assert not wrong, "\n".join(wrong)


def test_a_walkthrough_character_has_its_defaults_and_its_guides_needs_on():
    """Only those: a character in the background, a pack saga's crowd
    among them, is at its plain Default Interests."""
    wrong = []
    for number, saga in _sagas():
        for character in saga.characters:
            needs = FEATURED[number].get(character.name, ())
            off = deeds.interests_off(character)
            should = [i for i in deeds.defaults_off(character) if i not in needs]
            wrong += [
                f"{number}: {character.name} has {i} on" for i in should if i not in off
            ]
            wrong += [
                f"{number}: {character.name} has {i} off"
                for i in off
                if i not in should
            ]
    assert not wrong, "\n".join(wrong)


def test_every_tutorial_has_its_guides_table():
    numbers = [t.number for t in tutorials.listed()]
    assert sorted(FEATURED) == numbers
    assert set(COVENANTS_USE) <= set(numbers)


def test_a_covenant_has_manors_and_ships_off_unless_its_guide_uses_them():
    wrong = []
    for number, saga in _sagas():
        uses = COVENANTS_USE.get(number, {})
        for covenant in saga.covenants:
            used = uses.get(covenant.name, ())
            unused = [i for i in deeds.COVENANT_INTERESTS if i not in used]
            if sorted(covenant.interests_off) != sorted(unused):
                wrong.append(
                    f"{number}: {covenant.name} has {covenant.interests_off} off"
                )
        wrong += [
            f"{number}: no covenant {name}"
            for name in uses
            if name not in {c.name for c in saga.covenants}
        ]
    assert not wrong, "\n".join(wrong)


def test_a_tutorial_file_that_is_not_a_saga_is_named(tmp_path: Path):
    (tmp_path / "01_broken.json").write_text("[1, 2]", encoding="utf-8")
    with pytest.raises(ValueError, match="01_broken.json"):
        tutorials.listed(tmp_path)
