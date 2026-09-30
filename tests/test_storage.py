import pytest
from support import everything_saga

from ars_magica_manager import seasons, storage
from ars_magica_manager.models import (
    Ability,
    Aging,
    ArtScore,
    Background,
    BondPower,
    Book,
    Character,
    Characteristics,
    Covenant,
    CovenantDiaryEntry,
    Description,
    DeviceComponent,
    DiaryEntry,
    EnchantedDevice,
    Familiar,
    HermeticBackground,
    InstilledEffect,
    LabCharacteristics,
    Laboratory,
    LabSpecialtyEntry,
    NamedDescription,
    Possession,
    Saga,
    ScoredTrait,
    SeasonPlan,
    ShapeMaterialBonus,
    Spell,
    VirtueFlawInstance,
    Wounds,
)
from ars_magica_manager.rules import seasons as season_rules
from ars_magica_manager.rules.xp import ability_xp


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
                    "creo": ArtScore(xp=55),
                    "ignem": ArtScore(xp=15),
                },
                abilities=[
                    Ability(
                        name="Magic Theory",
                        category="Academic",
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
                specialties=[LabSpecialtyEntry("Ignem", 2, "Hearth spirit")],
                dropped_specializations=["Ignem"],
                sanctum_marked=True,
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


def test_delete_saga_removes_the_file_and_ignores_a_missing_one():
    storage.save_saga(Saga(id="doomed", name="Doomed"))
    storage.save_saga(Saga(id="kept", name="Kept"))
    storage.delete_saga("doomed")
    assert storage.list_sagas() == ["kept"]
    storage.delete_saga("doomed")  # already gone: not an error
    assert storage.list_sagas() == ["kept"]


def test_list_sagas_is_empty_when_the_sagas_folder_does_not_exist(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(storage, "SAGAS_DIR", tmp_path / "missing")
    assert storage.list_sagas() == []


def test_slugify_makes_a_filesystem_safe_id():
    assert storage.slugify("  The Order of Hermes! ") == "the_order_of_hermes"
    assert storage.slugify("???") == "id"


def test_generate_unique_id_adds_the_first_free_numeric_suffix():
    assert storage.generate_unique_id("Leandro", []) == "leandro"
    assert storage.generate_unique_id("Leandro", ["leandro"]) == "leandro_2"
    taken = ["leandro", "leandro_2", "leandro_3"]
    assert storage.generate_unique_id("Leandro", taken) == "leandro_4"


def test_generate_saga_id_avoids_sagas_already_on_disk():
    storage.save_saga(Saga(id="dammerstein", name="Dammerstein"))
    assert storage.generate_saga_id("Dammerstein") == "dammerstein_2"


def _one_of_everything_filled_in() -> Saga:
    """support.everything_saga() with every optional part set to something
    other than its default: what a long-played saga holds."""
    saga = everything_saga()
    saga.books_in_play = ["DE", "Covenants"]
    saga.keep_season_records = False
    cov = saga.covenants[0]
    cov.tribunal = "Rhine"
    cov.year_founded = 1100
    cov.aura = 3
    cov.notes = "An old keep."
    cov.economics.wealth = 5
    cov.economics.tithes = 1
    cov.economics.magic_savings = 2
    cov.economics.emergency_savings = 3
    cov.economics.notes = {"buildings": "Roof"}
    cov.economics.income_sources[0].type = "Greater"
    cov.economics.income_sources[0].income = 300
    cov.loyalty.familiarity = 4
    cov.loyalty.money = "Generous salary"
    cov.population.aging_magi = 1
    cov.population.other_people = 7
    cov.inhabitants[0].year_born = 1190
    cov.inhabitants[0].responsibility = "Steward"
    cov.possessions.append(
        Possession(
            id="pos-well",
            kind="vis_source",
            name="Well",
            art="Vim",
            pawns=3,
            season="Winter",
            location="Chapel",
        )
    )
    cov.possessions.append(
        Possession(
            id="pos-sword",
            kind="weapon",
            name="Sword",
            gear_id="weapon_long_sword",
            gear_type="Weapon or shield",
            gear_quality="Expensive",
            quantity=2,
            weapon_init=2,
            weapon_attack=4,
            weapon_defense=1,
            weapon_damage=6,
            load=1,
        )
    )
    cov.diary = [
        CovenantDiaryEntry(1220, "Summer", "Bought a mill", pounds=-12.0, loyalty=3)
    ]
    magus = saga.characters[0]
    magus.background.true_faith_score = 1
    magus.background.faith_points = 2
    magus.diary = [DiaryEntry(1219, "Winter", "Rest", "Quiet", "Other")]
    magus.invented_spells = [
        Spell(id="inv1", name="Lamp", technique="Creo", form="Ignem", level=10)
    ]
    saga.laboratories[0].aura_modifier = -2
    familiar = saga.familiars[0]
    familiar.species = "Raven"
    familiar.golden_cord = 3
    familiar.characteristics = Characteristics(stamina=3)
    familiar.base_soak = 5
    familiar.magic_resistance = 12
    familiar.abilities = [Ability("Athletics", xp=ability_xp(3), specialty="Running")]
    familiar.bond_powers = [
        BondPower(
            id="bp1",
            name="Speak with Beasts",
            level=15,
            technique="Creo",
            form="Animal",
            target_controller="Familiar",
            uses_per_day=3,
            penetration=5,
            vis_spent=2,
            cosmetic_trait="A crest",
        )
    ]
    saga.enchanted_devices.append(
        EnchantedDevice(
            id="dev-staff",
            name="Staff",
            holder_kind="character",
            holder_id="mag1",
            components=[DeviceComponent("staff", "wood", "large")],
            bonuses=[ShapeMaterialBonus(4, "destroy wood", "Axe")],
            attunements=[ShapeMaterialBonus(3, "air", "Agate", 1221, "Spring")],
            effects=[
                InstilledEffect(id="e0", name="Base", level=10),
                InstilledEffect(
                    id="e1",
                    name="Linked",
                    level=30,
                    linked_trigger=True,
                    linked_to="e0",
                ),
            ],
        )
    )
    seasons.set_plan(
        saga,
        SeasonPlan("mag1", 1220, "Spring", season_rules.OTHER, details="Tribunal"),
    )
    saga.season_records = [seasons.make_record(saga, seasons.resolve(saga))]
    return saga


def test_one_of_everything_survives_a_save():
    saga = _one_of_everything_filled_in()
    storage.save_saga(saga)
    assert storage.load_saga(saga.id) == saga


@pytest.mark.parametrize(
    ("model", "minimal"),
    [
        (Saga, {"id": "s", "name": "S"}),
        (Covenant, {"id": "c", "saga_id": "s", "name": "C"}),
        (Character, {"id": "c", "name": "C", "type": "magus"}),
        (Laboratory, {"id": "l", "covenant_id": "c", "name": "L"}),
        (Familiar, {"id": "f", "character_id": "m"}),
        (Spell, {"id": "a", "name": "A", "technique": "Creo", "form": "Ignem"}),
        (Book, {"id": "b", "name": "B", "type": "Other"}),
        (EnchantedDevice, {"id": "d", "name": "D"}),
    ],
    ids=lambda value: value.__name__ if isinstance(value, type) else "",
)
def test_a_save_from_before_a_field_existed_loads_with_its_default(model, minimal):
    """A record saved before later fields existed loads with each missing
    field at its default (the real migrations are tested with the model)."""
    assert model.from_dict(dict(minimal)) == model(**minimal)
