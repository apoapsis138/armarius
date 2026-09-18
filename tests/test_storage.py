from ars_magica_manager import storage
from ars_magica_manager.models import (
    Ability,
    Book,
    Character,
    Characteristics,
    Covenant,
    Laboratory,
    Library,
    Saga,
    Spell,
    VirtueFlawInstance,
)


def _sample_saga() -> Saga:
    return Saga(
        id="saga_test",
        name="Test Saga",
        covenants=[Covenant(id="cov_1", saga_id="saga_test", name="Test Covenant")],
        characters=[
            Character(
                id="char_1",
                name="Leandro",
                type="magus",
                covenant_id="cov_1",
                characteristics=Characteristics(intelligence=3),
                arts={"creo": 10, "ignem": 5},
                abilities=[
                    Ability(name="Magic Theory", score=5, specialty="Lab Totals")
                ],
                virtues_flaws=[
                    VirtueFlawInstance(
                        vf_id="vf_affinity_with_art", params={"art": "creo"}
                    )
                ],
                assigned_lab_id="lab_1",
            )
        ],
        laboratories=[
            Laboratory(
                id="lab_1", covenant_id="cov_1", name="Test Lab", owner_id="char_1"
            )
        ],
        libraries=[Library(id="lib_1", covenant_id="cov_1", books=["book_1"])],
        books=[
            Book(id="book_1", type="Summa", subject="Magic Theory", quality=6, level=8)
        ],
        spells=[
            Spell(
                id="spell_1",
                name="Test Spell",
                technique="Creo",
                form="Ignem",
                level=10,
            )
        ],
    )


def test_saga_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "SAGAS_DIR", tmp_path)
    saga = _sample_saga()

    path = storage.save_saga(saga)
    loaded = storage.load_saga(saga.id)

    assert path.exists()
    assert loaded == saga
    assert storage.list_sagas() == ["saga_test"]
