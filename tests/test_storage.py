from ars_magica_manager import storage
from ars_magica_manager.models import (
    Ability,
    Aging,
    ArtScore,
    Background,
    Book,
    Character,
    Characteristics,
    Covenant,
    Description,
    DiaryEntry,
    HermeticBackground,
    LabCharacteristics,
    Laboratory,
    NamedDescription,
    Saga,
    ScoredTrait,
    Spell,
    VirtueFlawInstance,
    Wounds,
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
                arts={
                    "creo": ArtScore(level=10, xp=55),
                    "ignem": ArtScore(level=5, xp=15),
                },
                abilities=[
                    Ability(
                        name="Magic Theory",
                        category="Academic",
                        level=5,
                        xp=75,
                        specialty="Lab Totals",
                    )
                ],
                virtues_flaws=[
                    VirtueFlawInstance(
                        vf_id="vf_affinity_with_art", params={"art": "creo"}
                    )
                ],
                assigned_lab_id="lab_1",
                background=Background(
                    player="Alex", birth_name="Leandro of Bonisagus", year_born=1180
                ),
                description=Description(height=1.8, handedness="left"),
                aging=Aging(decrepitude=1, warping_score=2, warping_points=5),
                wounds=Wounds(light=1, medium=0, heavy=0),
                fatigue_level="winded",
                personality_traits=[ScoredTrait(name="Curious", score=3)],
                reputations=[ScoredTrait(name="Skilled Enchanter", score=2)],
                raw_vis={"creo": 5, "ignem": 3},
                hermetic=HermeticBackground(house="house_bonisagus", parens="Trianoma"),
            )
        ],
        laboratories=[
            Laboratory(
                id="lab_1",
                covenant_id="cov_1",
                name="Test Lab",
                owner_id="char_1",
                location="Black Forest",
                build_points=50,
                characteristics=LabCharacteristics(size=1, safety=-1),
                specialties=["Ignem"],
                rooms=[NamedDescription(name="Vault", description="A locked cellar")],
                inventory_items=[
                    NamedDescription(name="Silver Mirror", description="For scrying")
                ],
                raw_vis={"creo": 5, "ignem": 3},
                diary=[
                    DiaryEntry(
                        year=1220,
                        season="Spring",
                        name="Invented a spell",
                        details="A quiet season of study.",
                    )
                ],
                virtues_flaws=[VirtueFlawInstance(vf_id="labvf_superior_construction")],
            )
        ],
        books=[
            Book(
                id="book_1",
                name="Theory",
                type="Ability Summa",
                ability="Magic Theory",
                quality=6,
                level=8,
                owner_kind="covenant",
                owner_id="cov_1",
            )
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
