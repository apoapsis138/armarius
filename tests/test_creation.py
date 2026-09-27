from ars_magica_manager import creation, storage
from ars_magica_manager.models import Saga


def _saga() -> Saga:
    return Saga(id="s", name="Saga")


def test_new_saga_takes_the_form_values_and_a_fresh_id():
    storage.save_saga(Saga(id="rhine", name="Rhine"))
    saga = creation.new_saga("Rhine", "Ann", "A saga", 1221, "Summer")
    assert saga.id != "rhine"
    assert saga.id.startswith("rhine")
    assert (saga.name, saga.storyguide, saga.description) == ("Rhine", "Ann", "A saga")
    assert (saga.current_year, saga.current_season) == (1221, "Summer")
    assert saga.covenants == [] and saga.characters == []


def test_add_covenant_appends_one_with_a_unique_id():
    saga = _saga()
    first = creation.add_covenant(saga, "Keep", "Old")
    second = creation.add_covenant(saga, "Keep")
    assert saga.covenants == [first, second]
    assert first.id != second.id
    assert (first.saga_id, first.name, first.notes) == ("s", "Keep", "Old")
    assert second.notes == ""


def test_add_character_appends_one_of_the_given_type():
    saga = _saga()
    character = creation.add_character(saga, "Ulla", "companion", "cov1")
    assert saga.characters == [character]
    assert (character.name, character.type, character.covenant_id) == (
        "Ulla",
        "companion",
        "cov1",
    )


def test_add_laboratory_sets_its_size_and_covenant():
    saga = _saga()
    lab = creation.add_laboratory(saga, "Cellar", 2, None)
    assert saga.laboratories == [lab]
    assert (lab.name, lab.covenant_id, lab.characteristics.size) == (
        "Cellar",
        None,
        2,
    )


def test_nothing_is_saved():
    saga = _saga()
    creation.add_covenant(saga, "Keep")
    creation.new_saga("Unsaved", "Ann", "", 1220, "Spring")
    assert storage.list_sagas() == []
