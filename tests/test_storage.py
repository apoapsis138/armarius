import dataclasses
import json

import pytest
from support import everything_saga

from ars_magica_manager import models, seasons, settings, storage
from ars_magica_manager.models import (
    Ability,
    AbilityDef,
    Agent,
    Aging,
    Alchemy,
    AnimalForm,
    ArcaneConnection,
    ArtScore,
    ArtworkPlan,
    Attitude,
    Background,
    BodyVis,
    BondPower,
    Book,
    BoundBeing,
    Breakthrough,
    Case,
    Character,
    Characteristics,
    CharacterPower,
    CharterClause,
    CharterSeal,
    Codex,
    Combatant,
    ConstantEffect,
    Covenant,
    CovenantBoonHookDef,
    CovenantCharter,
    CovenantDiaryEntry,
    CovenantStop,
    CreationXp,
    Creature,
    CreatureAttack,
    CreaturePower,
    Description,
    DeviceComponent,
    DiaryEntry,
    Digestion,
    Discipline,
    Disease,
    ElixirIngredient,
    EnchantedDevice,
    ExperimentalEffect,
    Familiar,
    Favour,
    Fight,
    FightEntry,
    FightGroup,
    FightSide,
    Formula,
    GoodDef,
    GoodPurity,
    Grip,
    GrogYear,
    HermeticBackground,
    InstilledEffect,
    Investment,
    LabCharacteristicGrant,
    LabCharacteristics,
    LabItemBenefit,
    Laboratory,
    LabProject,
    LabSpecialtyEntry,
    LabSpecialtyGrant,
    LabTextAccess,
    LabVirtueFlawDef,
    Link,
    MasteryAbility,
    Modifier,
    NamedDescription,
    Ordeal,
    Player,
    Possession,
    Progress,
    Purity,
    PurityExample,
    Reason,
    RefusedVendetta,
    ResearchAttempt,
    RouteStop,
    Ruling,
    Saga,
    SagaSource,
    ScoredTrait,
    ScriptPart,
    SeasonPlan,
    SeasonRecord,
    SeasonRecordLine,
    ShapeMaterialBonus,
    Siege,
    SiegeEvent,
    Spell,
    SpellDesign,
    TraditionEffect,
    TreasuryEntry,
    TribunalDiaryEntry,
    VirtueFlawDef,
    VirtueFlawInstance,
    WorldTurn,
    Wounds,
    WoundState,
    XpAllocation,
)
from ars_magica_manager.rules import activities as season_rules
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
    saga = _sample_saga()

    path = storage.save_saga(saga).path
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
    monkeypatch.setattr(storage.paths, "_in_use", tmp_path / "missing")
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
    saga.tribunals[0].meets_every = 5
    cov.year_founded = 1100
    cov.aura = 3
    cov.notes = "An old keep."
    cov.economics.wealth = 5
    cov.economics.tithes = 1
    cov.economics.magic_savings = 2
    cov.economics.emergency_savings = 3
    # Technological savings (Transforming Mythic Europe).
    cov.economics.saving_devices = ["dev-broom"]
    cov.economics.ritual_magnitudes = 4
    cov.economics.magic_grain = 20000
    cov.economics.grain_care = "Protected"
    cov.economics.bread_share = "Three quarters"
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
    # A covenant's ship (Hermetic Projects; City & Guild).
    cov.possessions.append(
        Possession(
            id="pos-cog",
            kind="ship",
            name="Grauwal",
            ship=models.Ship(
                ship_type="buss",
                kind_name="Small cog",
                quality="Excellent",
                damage_lost=1,
                repaired=True,
                magnitudes=2,
                ballistae=1,
                fighters_tons=0.5,
                close_to_home=True,
                home_port="Terschelling",
            ),
        )
    )
    cov.diary = [
        CovenantDiaryEntry(1220, "Summer", "Bought a mill", pounds=-12.0, loyalty=3)
    ]
    magus = saga.characters[0]
    magus.background.true_faith_score = 1
    magus.background.faith_points = 2
    magus.diary = [DiaryEntry(1219, "Winter", "Rest", "Quiet", "Other")]
    # A Virtue gained by magic for a while (Grogs pp. 62-63).
    magus.virtues_flaws.append(
        VirtueFlawInstance(
            "vf_keen_vision", temporary=True, ends_year=1221, ends_season="Winter"
        )
    )
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
            extra_spaces=2,
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


# -- stale keys from older saves ---------------------------------


def _add_diary_and_charter(covenant: Covenant, magus_id: str) -> None:
    """A diary entry, and a charter with a clause and a magus's seal."""
    covenant.diary.append(CovenantDiaryEntry(1220))
    covenant.economics.purchases.append(models.Purchase("p", "Hay", 1.0))
    covenant.inhabitants.append(
        models.Inhabitant(
            id="arr", kind="turb", quantity=2, arrivals=[models.Arrival(1, 1220)]
        )
    )
    covenant.stops.append(CovenantStop(1220, "Spring", "somewhere"))
    covenant.route.append(RouteStop("somewhere"))
    covenant.charter_of_covenant = CovenantCharter(
        clauses=[
            CharterClause(
                "1",
                "Share all vis.",
                1220,
                "Spring",
                status="Broken",
                censure=models.Censure(magus_id, withheld=["Library"]),
            )
        ],
        seals=[CharterSeal(magus_id, 1220, "Spring")],
    )
    # A land project: an island raised by magic (Transforming Mythic Europe).
    covenant.land_projects.append(
        models.LandProject("land-1", "The Island", features=["sea_gate"])
    )
    # A Hermetic Project, with a work and a craft device (Hermetic Projects).
    covenant.hermetic_projects.append(
        models.HermeticProject(
            name="The Spire",
            works=[models.ProjectWork(name="Heights", levels=4, quality="Standard")],
            devices=[models.CraftDevice(name="The Arms of Hercules")],
        )
    )
    # A staged project, with a stage (Hermetic Projects).
    covenant.hermetic_projects.append(
        models.HermeticProject(
            name="The Hearth",
            kind="Burning City",
            stages=[models.ProjectStage(name="Find a volcano")],
        )
    )
    # A Menagerie, with a beast and a breeding (Hermetic Projects).
    covenant.hermetic_projects.append(
        models.HermeticProject(
            name="The Spur Menagerie",
            kind="Menagerie",
            beasts=[models.Beast(name="Bock", might=10, brands=["a palm brand"])],
            breedings=[models.Breeding(pair="Bock × Geiß", young=1)],
        )
    )


def _add_animal_and_formula(magus: Character) -> None:
    magus.animal = AnimalForm("hoofed", "Horse", "Horse", lifespan=30)
    magus.formula_designs.append(Formula("Theriac of Vipers", level=10))
    # Hermetic alchemy (TMRE ch. 5).
    magus.alchemy = Alchemy(
        digestion=Digestion(
            "lab1", season="Spring", year=1220, totals=[12], extra_room=True
        ),
        ingredients=[ElixirIngredient("amber", 3)],
        immortal_age=161,
    )
    magus.magic_might = 30
    # A Criamon magus's Enigma (HoH:MC pp. 50-73).
    magus.enigma = models.Enigma(
        path="seeming",
        aptitude_path="seeming",
        reached=[models.StationReached("vf_station_of_true_sight", "Autumn", 1214)],
        stigmata=[models.Stigma("Eyelids", "A spiral", "station", year=1214)],
    )


def _add_own_goods_and_abilities(saga: Saga) -> None:
    """The saga's own good, purity and Ability (HoH:S p. 104)."""
    saga.charter_templates.append(
        models.CharterTemplate(
            "accord", "Accord", clauses=[CharterClause("1", "Share all vis.")]
        )
    )
    saga.custom_goods.append(
        GoodDef(
            "custom_good_amber",
            "Amber",
            prices=("#", "500*", "1,000", ""),
            purity=Purity(1000, "By content.", (PurityExample("Standard", "500*"),)),
        )
    )
    saga.good_purities.append(GoodPurity("purity_1", "custom_good_amber", "Dull", 40))
    saga.custom_abilities.append(
        AbilityDef("custom_ability_x", "X", "Supernatural", realm="Magic")
    )
    # And a Mystery Cult of its own (TMRE pp. 13-19).
    _add_own_cult(saga)


def _add_own_cult(saga: Saga) -> None:
    """A Mystery Cult of the saga's own, a degree and its Script (TMRE pp.
    13-19)."""
    saga.custom_cults.append(
        models.MysteryCult(
            "custom_cult_x",
            "X",
            "X Lore",
            degrees=[
                models.CultDegree(
                    "degree_1",
                    "First",
                    "vf_affinity_with_art",
                    {"art": "vim"},
                    models.CultScript(
                        "Rite",
                        [models.CultComponent("ordeal_minor", 3, "", "vf_visions")],
                        # What an experiment wrote into it (TMRE p. 18).
                        traits=["Devoted to the cult +1"],
                        virtues=["vf_second_sight"],
                        initiates="vf_elemental_magic",
                    ),
                )
            ],
        )
    )


def _add_players_sources_and_codex(saga: Saga) -> None:
    saga.players.append(Player("ana", "Ana", "player", "scrypt$00$00"))
    saga.sources.append(SagaSource("HR", "House rules"))
    saga.codices.append(Codex("codex", "Bound together", palimpsest=True))
    saga.books[0].codex_id = "codex"


def _saga_with_every_record() -> Saga:  # noqa: PLR0915
    """everything_saga() plus one of each saved record it lacks, so every
    dataclass a saga file holds appears at least once."""
    saga = everything_saga()
    magus = next(c for c in saga.characters if c.type == "magus")
    magus.arts["Creo"] = ArtScore(xp=6)
    magus.spells_known[0].mastery_abilities.append(MasteryAbility("Fast Casting"))
    magus.breakthroughs.append(
        Breakthrough(
            "Holistic",
            log=[
                ResearchAttempt(
                    1220, "Spring", "seek", effects=[ExperimentalEffect("side")]
                )
            ],
        )
    )
    magus.bound_beings.append(BoundBeing("Corvus", tradition="trad_folk_witches"))
    magus.tradition_effects.append(
        TraditionEffect("Fetch", tradition="trad_gruagachan", uses=["Gruagach Give"])
    )
    magus.powers.append(CharacterPower("Owl", "Greater Power", level=30))
    magus.covers.append(models.DeepCover("Reynard", role="a mercenary"))
    magus.stirpes.append(models.Stirps("Rooster", form="Animal", level=10))
    magus.constant_effects.append(ConstantEffect("Ring of Flight", powerful=True))
    magus.progress.append(Progress("vis", "Study"))
    magus.goals.append(models.PlayerGoal("g", "Master Creo", subject="art:creo"))
    magus.ordeals, magus.refused_vendettas = (
        [Ordeal("Minor")],
        [RefusedVendetta("Rival", 3)],
    )
    magus.agents.append(Agent("Bishop Benedict", bond_trait="Thankful", bond=1))
    # A cleric's career (The Church).
    magus.church = models.ChurchCareer(
        grade="Lector",
        diocese="Konstanz",
        ordinations=[models.Ordination("Doorkeeper", "Spring", 1205, die=7)],
        petitions=[
            models.Petition(
                "Leave",
                arguments={"Intrigue": 2},
                argument_rolls={"Intrigue": 11},
                original=9,
            )
        ],
        cases=[models.CanonCase("Slander", verdict="guilty", punishment="Monition")],
    )
    magus.creation_xp.append(CreationXp("later_life", "ability:Latin", 5))
    magus.lab_text_access["x"] = LabTextAccess(15, "decoded")
    magus.grog_year, magus.investments, magus.stay = (
        GrogYear(),
        [Investment("speculation")],
        models.GuestStay("cov_sketch", 1220, "Spring", fee_kind="vis", fee=3),
    )
    magus.discipline.append(Discipline(1220, kind="improved_rations", seasons=4))
    magus.wounds = Wounds(
        light=1,
        states=[WoundState("light", "disease", 3)],
        diseases=[Disease("Coryza")],
        conditions=["noble_diet"],
    )
    _add_animal_and_formula(magus)
    saga.laboratories[0].arcane_connections.append(ArcaneConnection("ac", "a tree"))
    saga.laboratories[0].item_benefits.append(
        LabItemBenefit(
            "ib",
            "dev-lab",
            "eff1",
            specializations=[LabSpecialtyGrant("Ignem", 1)],
            characteristics=[LabCharacteristicGrant("safety", 1)],
        )
    )
    _add_diary_and_charter(saga.covenants[0], magus.id)
    rhine = saga.tribunals[0]
    rhine.cases.append(Case("Interference"))
    rhine.rulings.append(Ruling("No new covenants on the Rhine"))
    rhine.treasury.append(TreasuryEntry("vis", 5, "Vim"))
    # A diary entry, and an argument with its polemic (TME pp. 27-35).
    rhine.diary, rhine.arguments = (
        [TribunalDiaryEntry(1221)],
        [models.Argument("Charters", texts=[models.PolemicText(book_id="b")])],
    )
    device = saga.enchanted_devices[0]
    device.bonuses.append(ShapeMaterialBonus(3, "fire", "Oak"))
    saga.season_plans.append(
        SeasonPlan(
            magus.id,
            1220,
            "Spring",
            season_rules.EXPOSURE,
            [XpAllocation("ability:Latin")],
            design=SpellDesign("key"),
            artwork=ArtworkPlan(assistants=1),
            script_components=[ScriptPart("quest")],
        )
    )
    saga.season_records.append(
        SeasonRecord(1220, "Spring", lines=[SeasonRecordLine(magus.id, "M")])
    )
    saga.lab_projects.append(LabProject(magus.id, saga.spells[0].id))
    saga.world_turns.append(WorldTurn(1220, lines=["Threats: the ford floods"]))
    bonus = Modifier("study_total", amount=1)
    saga.custom_virtues_flaws.append(
        VirtueFlawDef("vf", "VF", "Virtue", "General", "Minor", 1, modifiers=[bonus])
    )
    saga.custom_lab_virtues_flaws.append(
        LabVirtueFlawDef("lvf", "LVF", "Virtue", "Structure", "Minor", 1)
    )
    saga.custom_boons_hooks.append(CovenantBoonHookDef("bh", "BH", "Boon", "Minor", 1))
    _add_own_goods_and_abilities(saga)
    _add_players_sources_and_codex(saga)
    other = saga.covenants[0]
    other.attitudes.append(Attitude(other.id, 1, [Reason("Helped at the ford", 1)]))
    other.favours.append(Favour("Shelter", "Fengheld", other.id))
    # With a covenant's ship (Hermetic Projects; City & Guild).
    other.links, other.possessions = (
        [*other.links, Link("characters", magus.id, "its founder")],
        [
            *other.possessions,
            Possession(id="pos-ship", kind="ship", name="Möwe", ship=models.Ship()),
        ],
    )
    saga.creatures.append(
        Creature(
            "boglin",
            "Boglin",
            attacks=[CreatureAttack("Bite")],
            powers=[CreaturePower("Vanish")],
            vis=[BodyVis(1, "Herbam", "in its heart")],
        )
    )
    saga.fights.append(
        Fight(
            "A fray",
            sides=[
                FightSide(
                    "Ours",
                    combatants=[Combatant("Grog", id="g1"), Combatant("Grog", id="g2")],
                    groups=[FightGroup("Turb", ["g1", "g2"])],
                ),
                FightSide("Theirs"),
            ],
            log=[FightEntry(1, "A blow.", ["Attack 12"])],
            grips=[Grip("g2", "g1", 3)],
        )
    )
    saga.sieges.append(
        Siege(
            "A siege",
            events=[SiegeEvent(7, "Keep the stockade", "It holds.")],
            outworks=[models.Outwork("The Accursed Tower")],
        )
    )
    # A marriage (Lords of Men pp. 10-11).
    saga.marriages.append(
        models.Marriage(bride="Adelheid", groom_ref="neighbour:gottfried", lands=2)
    )
    # A Session with who played whom.
    saga.sessions.append(
        models.Session(
            "s1",
            castings=[models.Casting(player_id="p1", character_id=magus.id)],
        )
    )
    # An ask for a teacher's season.
    saga.teach_requests.append(
        models.TeachRequest("t1", magus.id, magus.id, "ability:Latin", "Spring", 1220)
    )
    # The Atlas: a map of its own and a pin on it.
    saga.maps, saga.pins = (
        [models.AtlasMap("rhine", "The Rhine", "ab.png", 30, 20)],
        [models.Pin("rhine", "neighbours", "gottfried", 0.5, 0.25)],
    )
    return saga


def _stale(value: object, target: type | None) -> object:
    """`asdict(value)`, with an unknown key added to each dict that holds a
    `target` record (to every record when `target` is None)."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        data = {
            f.name: _stale(getattr(value, f.name), target)
            for f in dataclasses.fields(value)
        }
        if target is None or type(value) is target:
            data["retired_field"] = "from an older version"
        return data
    if isinstance(value, (list, tuple)):
        return [_stale(item, target) for item in value]
    if isinstance(value, dict):
        return {key: _stale(item, target) for key, item in value.items()}
    return value


def _record_types(value: object) -> set[type]:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        found = {type(value)}
        for f in dataclasses.fields(value):
            found |= _record_types(getattr(value, f.name))
        return found
    if isinstance(value, (list, tuple)):
        return set().union(*(_record_types(item) for item in value))
    if isinstance(value, dict):
        return set().union(*(_record_types(item) for item in value.values()))
    return set()


_SAVED_TYPES = sorted(
    _record_types(_saga_with_every_record()), key=lambda t: t.__name__
)


def test_the_stale_key_fixture_holds_every_saved_record():
    """Every dataclass that can sit in a saga file is in the fixture, so the
    stale-key test below covers it (a new saved record must be added)."""
    not_saved = {
        "ArmorDef", "CharacterTemplateDef", "CovenantSituationDef",
        "GrogTemplateDef",
        "HouseDef", "LabFeatureDef", "ShapeMaterialDef", "TraditionDef",
        "TraditionTraining", "WeaponDef", "CastingRule", "MagicalDefense",
        "DispelRule", "GroupCasting", "OpeningRule", "InitiationRule",
        "InitiationScript", "Advancement", "TraditionActivity", "BondRule",
        "PoolDef", "WarpingRule", "Guideline", "EffectParameter", "ArmorPieceDef",
        "SpellGuidelineDef",
    }  # fmt: skip
    every = {
        cls.__name__
        for cls in vars(models).values()
        if isinstance(cls, type)
        and dataclasses.is_dataclass(cls)
        and cls.__module__.startswith(f"{models.__name__}.")
    }
    assert every - not_saved == {t.__name__ for t in _SAVED_TYPES}


@pytest.mark.parametrize("record", _SAVED_TYPES, ids=lambda t: t.__name__)
def test_a_save_with_a_stale_key_still_loads(record):
    """A key the app no longer knows (a field since removed or renamed) in
    any saved record is dropped on load instead of stopping the saga
    opening."""
    saga = _saga_with_every_record()
    stale = _stale(saga, record)
    assert "retired_field" in json.dumps(stale)
    assert Saga.from_dict(stale) == Saga.from_dict(dataclasses.asdict(saga))


def test_a_save_with_stale_keys_everywhere_still_loads():
    saga = _saga_with_every_record()
    assert Saga.from_dict(_stale(saga, None)) == Saga.from_dict(
        dataclasses.asdict(saga)
    )


def test_storage_follows_the_data_folder_whenever_it_changes(tmp_path):
    """Nothing about the folder is fixed when storage is imported: a folder
    chosen later is where the next save goes, settings and exports too."""
    chosen = tmp_path / "chosen"
    storage.paths.remember_data_dir(chosen)
    storage.save_saga(Saga(id="moved", name="Moved"))
    assert (chosen / "sagas" / "moved.json").is_file()
    assert storage.exports_dir() == chosen / "exports"
    assert settings.settings_path() == chosen / "app_settings.json"
