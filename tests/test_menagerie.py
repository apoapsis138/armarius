"""A Menagerie of magical beasts, the second kind of Hermetic Project
(Hermetic Projects pp. 119-142; errata pp. 81-82; Realms of Power: Magic
p. 53; DE pp. 384-385): upkeep, staff, realia, young beasts' Might,
Acclimation, the optional breeding rolls, taming, and the Projects tab's
sections for a menagerie."""

import random

from ars_magica_manager import hermetic_projects as hpc
from ars_magica_manager import menagerie as men
from ars_magica_manager import storage
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.form_spec import DialogField
from ars_magica_manager.manors import manors_of
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Covenant,
    HermeticProject,
    Neighbour,
    Saga,
)
from ars_magica_manager.models.character import Progress
from ars_magica_manager.models.menagerie import (
    BEAST,
    BEST,
    CARNIVORE,
    FEMALE,
    MALE,
    MENAGERIE,
    TRANSFORMED,
    Beast,
    Breeding,
)
from ars_magica_manager.rules import covenfolk, lab_seasons
from ars_magica_manager.rules import menagerie as mg
from ars_magica_manager.seasons.plans import plan_for
from ars_magica_manager.sections import (
    BEASTS_SECTION,
    BREEDINGS_SECTION,
    MENAGERIE_SECTION,
    PROJECTS_SECTION,
    TOWER_SECTION,
)

PLACE = "place_meadow"


def menagerie(**changes) -> HermeticProject:
    """The Spur Menagerie, the preview's sample: a pair of Goats of
    Virtue, their kid, four Hares of Virtue and an Eagle being tamed."""
    project = HermeticProject(
        id="spur",
        name="The Spur Menagerie",
        kind=MENAGERIE,
        season="Spring",
        year=1216,
        place_id=PLACE,
        handler_ids=["ol", "lech"],
        owner_id="corvinus",
        reputation="Keeper of Beasts",
        beasts=[
            Beast(
                id="bock",
                name="Bock",
                breed="Goat of Virtue",
                might=10,
                sex=MALE,
                tamed=True,
                brands=["The Brand of the Aroused Stallion (ReAn 35), a palm"],
            ),
            Beast(
                id="geiss", name="Geiß", breed="Goat of Virtue", might=10, tamed=True
            ),
            Beast(
                id="kid",
                name="Zicklein",
                breed="Goat of Virtue",
                might=10,
                size=-2,
                born=1219,
            ),
            Beast(
                id="hares",
                name="Hare of Virtue",
                breed="Hare of Virtue",
                might=5,
                size=-3,
                count=4,
                sex="both",
            ),
            Beast(
                id="eagle",
                name="Sturmfeder",
                breed="Eagle of Virtue",
                might=15,
                size=-1,
                diet=CARNIVORE,
                tamer_id="corvinus",
            ),
        ],
    )
    for key, value in changes.items():
        setattr(project, key, value)
    return project


def menagerie_saga(project: HermeticProject | None = None, aura: int = 5) -> Saga:
    return Saga(
        id="men_saga",
        name="The Menagerie",
        storyguide="Hedda",
        current_season="Spring",
        current_year=1220,
        covenants=[
            Covenant(
                id="dam",
                saga_id="men_saga",
                name="Dammerstein",
                place_id=PLACE,
                hermetic_projects=[project or menagerie()],
            )
        ],
        neighbours=[
            Neighbour(
                id=PLACE,
                name="The upper meadow",
                kind="place",
                realm="Magic",
                details={"aura": aura},
            )
        ],
        characters=[
            Character(
                id="ol",
                name="Ol Thomae",
                type="grog",
                covenant_id="dam",
                abilities=[Ability(name="Animal Handling", category="General", xp=50)],
            ),
            Character(id="lech", name="Lech", type="grog", covenant_id="dam"),
            Character(
                id="corvinus",
                name="Corvinus",
                type="magus",
                covenant_id="dam",
                characteristics=Characteristics(intelligence=2),
            ),
            Character(
                id="anna",
                name="Anna",
                type="companion",
                covenant_id="dam",
                characteristics=Characteristics(intelligence=1),
                abilities=[
                    Ability(name="Animal Handling", category="General", xp=105),
                    Ability(name="Magic Lore", category="Arcane", xp=30),
                ],
            ),
        ],
    )


def _project(saga: Saga) -> HermeticProject:
    return saga.covenants[0].hermetic_projects[0]


def _holder(saga: Saga) -> Neighbour:
    return manors_of(saga.covenants[0])


def _values(form: Form, **changes) -> dict:
    values = {f.key: f.value for f in form.fields() if isinstance(f, DialogField)}
    values.update(changes)
    return values


class Dice(random.Random):
    """A Random whose d10s come in the order given (0 a zero face)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *_args, **_kwargs) -> int:  # type: ignore[override]
        return self.faces.pop(0)


# -- upkeep, staff, realia (HP pp. 123, 136) -----------------------------------


def test_a_horse_costs_one_point_and_each_size_halves_or_doubles():
    assert mg.inhabitant_points(Beast(size=3)) == 1
    assert mg.inhabitant_points(Beast(size=0, count=8)) == 1
    assert mg.inhabitant_points(Beast(size=4)) == 2
    assert mg.inhabitant_points(Beast(size=5)) == 4


def test_twelve_wolves_cost_three_points():
    # The book's own example (p. 123, reprinted by errata p. 82).
    wolves = Beast(size=0, count=12, diet=CARNIVORE)
    assert mg.upkeep(HermeticProject(kind=MENAGERIE, beasts=[wolves])) == 3


def test_the_sample_menagerie_costs_and_counts_toward_inhabitants():
    saga = menagerie_saga()
    project = _project(saga)
    # Goats 1/8 + 1/8 + 1/32 + hares 4/64 + eagle 2/16, rounded up.
    assert mg.upkeep(project) == 1
    covenant = saga.covenants[0]
    with_beasts = covenfolk.inhabitant_points(saga, covenant)
    project.beasts = []
    assert covenfolk.inhabitant_points(saga, covenant) == with_beasts - 1


def test_handlers_tend_ten_tame_herbivores_a_point():
    saga = menagerie_saga()
    project = _project(saga)
    # Ol Thomae's Animal Handling 4 (Lech has none): 40.
    assert mg.can_tend(saga, project) == 40
    # Tame goats 1 each; the kid and the hares wild (x5); the eagle a
    # wild carnivore (x10).
    assert mg.load(saga, project) == 1 + 1 + 5 + 20 + 10


def test_realia_counts_magical_breeds():
    project = menagerie()
    assert mg.breeds(project) == ["Goat of Virtue", "Hare of Virtue", "Eagle of Virtue"]
    assert mg.realia_quality(project) == 3
    project.beasts.append(Beast(name="Warped dog", kind=TRANSFORMED))
    assert mg.realia_quality(project) == 3


def test_a_brand_is_material_two_times_its_size():
    assert [mg.brand_material(w) for w in ("palm", "haunch", "back")] == [4, 6, 8]


# -- young beasts and Acclimation (HP p. 134; RoP: Magic p. 53) ---------------


def test_a_young_beasts_might_is_a_fifth_until_grown():
    kid = menagerie().beasts[2]
    assert mg.is_young(kid, 1220)
    assert mg.might_now(kid, 1220) == 2
    assert not mg.is_young(kid, 1224)
    assert mg.might_now(kid, 1224) == 10
    # Rounded down, but a magical beast keeps 1.
    assert mg.might_now(Beast(might=4, born=1220), 1220) == 1
    assert mg.might_now(Beast(might=12, born=1220, maturity=3), 1220) == 4


def test_acclimation_needs_an_aura_of_might_over_five():
    eagle = menagerie().beasts[4]
    assert mg.acclimation(eagle, 5, 1220) is None
    assert mg.acclimation(eagle, 2, 1220) == 3
    assert mg.acclimation(Beast(might=55), 10, 1220) == 0
    assert mg.acclimation(Beast(kind=TRANSFORMED), 0, 1220) is None


def test_the_block_warns_of_acclimation_and_too_many_beasts():
    saga = menagerie_saga(aura=2)
    _project(saga).handler_ids = ["lech"]
    text = men.block_text(saga, _holder(saga))
    assert "Sturmfeder (Might 15)" in text and "aura of 3" in text
    assert "staff can tend 0" in text


# -- the beasts' states (DE p. 384) --------------------------------------------


def test_states_tamed_young_wild_and_taming():
    saga = menagerie_saga()
    project = _project(saga)
    states = [mg.state(saga, b, 1220).words for b in project.beasts]
    assert states == ["Tamed", "Tamed", "Young", "Wild", "Wild"]
    corvinus = saga.character("corvinus")
    assert corvinus is not None
    corvinus.progress.append(Progress("taming", "Sturmfeder", 15, 9))
    assert mg.state(saga, project.beasts[4], 1220).words == "Taming: 9 of 15"
    corvinus.progress[0].done = True
    assert mg.is_tamed(saga, project.beasts[4])


# -- breeding (HP pp. 140-142) -------------------------------------------------


def test_breeding_roll_modifiers_for_the_goats():
    saga = menagerie_saga()
    bock, geiss = _project(saga).beasts[:2]
    ol = saga.character("ol")
    mods = mg.breeding_modifiers(
        saga,
        bock,
        geiss,
        mg.Conditions(diet=1, environment=-2, spell=5, handler=ol),
        1220,
    )
    assert dict(mods) == {
        "adequate diet": 1,
        "unsatisfactory environment": -2,
        "a Hermetic spell": 2,
        "herbivore": 1,
        "Ol Thomae's Animal Handling 4 / 5": 1,
        "magical, Might 10": -2,
        "tamed": 3,
    }


def test_a_carnivore_an_only_pair_and_ferocity():
    saga = menagerie_saga()
    lion = Beast(name="Lion", might=0, diet=CARNIVORE, ferocity=2, sex=MALE)
    lioness = Beast(name="Lioness", diet=CARNIVORE)
    mods = dict(
        mg.breeding_modifiers(
            saga, lion, lioness, mg.Conditions(only_pair=True, similar=True), 1220
        )
    )
    assert mods == {
        "carnivore": -1,
        "the only pair of its kind": -3,
        "similar animals near": 1,
        "aggressive, Ferocity 2": -2,
    }


def test_the_only_pair_counts_their_kind_of_any_breed():
    # HP p. 131: a kind (horses) holds several breeds (destrier, jennet);
    # the -3 of p. 141 is for the only beasts of their kind.
    stallion = Beast(name="Bayard", animal="Horse", breed="Destrier", sex=MALE)
    mare = Beast(name="Blanche", animal="Horse", breed="Destrier")
    jennet = Beast(name="Lucia", animal="horse ", breed="Jennet")
    hound = Beast(name="Gelert", animal="Dog", breed="Alaunt")
    alone = menagerie(beasts=[stallion, mare, hound])
    assert mg.only_of_kind(alone, stallion, mare)
    other_breed = menagerie(beasts=[stallion, mare, jennet, hound])
    assert not mg.only_of_kind(other_breed, stallion, mare)


def test_the_only_pair_without_an_animal_compares_breeds():
    project = menagerie()
    bock, geiss = project.beasts[0], project.beasts[1]
    # A kid of the same breed is kept: not the only pair.
    assert not mg.only_of_kind(project, bock, geiss)
    project.beasts.remove(project.beasts[2])
    assert mg.only_of_kind(project, bock, geiss)


def test_breeding_botches_by_count():
    assert mg.breeding_botch(1) == "one of the pair escapes"
    assert mg.breeding_botch(2) == "one of the pair is sterile"
    assert mg.breeding_botch(4) == "one of the pair is hurt mating, or worse"


def test_the_inheritance_tables():
    assert mg.for_the_best(0, True).words.startswith("a Major Supernatural Flaw")
    assert mg.for_the_best(2, False).stamina == -1
    assert mg.for_the_best(12, False).words == "like its parents"
    assert mg.for_the_best(14, False).stamina == 1
    assert "Minor Supernatural Virtue" in mg.for_the_best(17, False).words
    assert "Major Supernatural Virtue" in mg.for_the_best(18, False).words
    assert mg.for_the_beast(5, True).dies
    assert mg.for_the_beast(13, False).like_dam
    assert "Minor Virtue" in mg.for_the_beast(14, False).words
    assert "Major Virtue" in mg.for_the_beast(20, False).words


def test_offspring_modifiers_a_spell_a_magnitude_and_a_ligature():
    dam = Beast(name="Mare", cross_bonus=True)
    mods = mg.offspring_modifiers(
        dam, BEAST, mg.Conditions(diet=1, spell=3, ligature=5)
    )
    assert dict(mods) == {
        "diet": 1,
        "a Hermetic spell": 3,
        "a ligature": 3,
        "Mare, a crossbred dam": 3,
    }


def test_birth_interval_doubles_per_size_above_zero():
    assert mg.birth_interval(-2) == 2
    assert mg.birth_interval(0) == 2
    assert mg.birth_interval(3) == 16


def test_breed_a_pair_rolls_keeps_the_breeding_and_adds_the_young():
    saga = menagerie_saga()
    project = _project(saga)
    # Breeding Roll die 9 (succeeds); one young: sex die 4 (male), its
    # roll for the best 9 + 1 + 1 = 11 (like its parents).
    form = men.breed_form(saga, saga.covenants[0], rng=Dice(9, 4, 9))
    assert isinstance(form, Form)
    values = _values(form, aim=BEST, sire="bock", dam="geiss", handler="ol")
    assert form.validate is not None and form.validate(values) is None
    assert form.live is not None and "against 9" in form.live(values)
    form.apply(values)
    breeding = project.breedings[-1]
    assert breeding.pair == "Bock × Geiß" and breeding.young == 1
    young = project.beasts[-1]
    assert (young.sex, young.born, young.breed, young.might) == (
        MALE,
        1220,
        "Goat of Virtue",
        10,
    )
    assert "like its parents" in young.note


def test_a_failed_breeding_has_no_young():
    saga = menagerie_saga()
    project = _project(saga)
    before = len(project.beasts)
    form = men.breed_form(saga, saga.covenants[0], rng=Dice(2))
    assert isinstance(form, Form)
    form.apply(_values(form, sire="bock", dam="geiss", diet="-2", environment="-2"))
    assert project.breedings[-1].result == "No young"
    assert len(project.beasts) == before


def test_breed_a_pair_needs_a_male_and_a_female():
    saga = menagerie_saga(menagerie(beasts=[Beast(name="Geiß")]))
    assert isinstance(men.breed_form(saga, saga.covenants[0]), Refuse)


# -- taming (DE pp. 384-385; HP p. 135) ----------------------------------------


def test_tame_a_beast_plans_a_magus_lab_season():
    saga = menagerie_saga()
    corvinus = saga.character("corvinus")
    assert corvinus is not None
    corvinus.assigned_lab_id = "lab1"
    form = men.tame_form(saga, saga.covenants[0], 4)
    assert isinstance(form, Form)
    plan = men.tame_plan(saga, corvinus, _project(saga).beasts[4], "Spring", 1220)
    assert (plan.activity, plan.title, plan.form, plan.book_level) == (
        lab_seasons.TAMING,
        "Sturmfeder",
        "Animal",
        15,
    )


def test_tame_a_beast_plans_a_companions_season():
    saga = menagerie_saga()
    form = men.tame_form(saga, saga.covenants[0], 3)
    assert isinstance(form, Form)
    values = _values(form, who="anna")
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    anna = saga.character("anna")
    assert anna is not None
    plan = plan_for(saga, anna)
    assert plan is not None and (plan.activity, plan.title, plan.book_level) == (
        "tame_animal",
        "Hare of Virtue",
        5,
    )
    assert _project(saga).beasts[3].tamer_id == "anna"
    # A second plan for the same season is refused.
    again = men.tame_form(saga, saga.covenants[0], 3)
    assert isinstance(again, Form) and again.validate is not None
    assert "already has a plan" in (again.validate(_values(again, who="anna")) or "")


def test_a_grogs_taming_is_kept_now():
    saga = menagerie_saga()
    form = men.tame_form(saga, saga.covenants[0], 2)
    assert isinstance(form, Form)
    # Ol Thomae: Int 0 + Animal Handling 4 - Might 2 (the kid, young) = 2.
    form.apply(_values(form, who="ol"))
    ol = saga.character("ol")
    assert ol is not None
    record = ol.progress[0]
    assert (record.kind, record.name, record.points, record.target) == (
        "taming",
        "Zicklein",
        2,
        2,
    )
    assert record.done
    assert mg.is_tamed(saga, _project(saga).beasts[2])


def test_tame_a_beast_refuses_the_tamed_and_the_intelligent():
    saga = menagerie_saga()
    assert isinstance(men.tame_form(saga, saga.covenants[0], 0), Refuse)
    _project(saga).beasts[3].cunning = False
    assert isinstance(men.tame_form(saga, saga.covenants[0], 3), Refuse)


# -- the Projects tab ----------------------------------------------------------


def test_a_menagerie_shown_has_its_own_sections():
    saga = menagerie_saga()
    tab = hpc.projects_tab(saga, saga.covenants[0])
    assert [p.section_id for p in tab.parts()] == [
        PROJECTS_SECTION,
        MENAGERIE_SECTION,
        BEASTS_SECTION,
        BREEDINGS_SECTION,
    ]
    ops = hpc.covenant_ops(saga, saga.covenants[0])
    assert {BEASTS_SECTION, BREEDINGS_SECTION, MENAGERIE_SECTION} <= set(ops)
    assert TOWER_SECTION not in ops


def test_the_lists_and_facts():
    saga = menagerie_saga()
    holder = _holder(saga)
    assert men.beasts_title(saga, holder) == "Beasts (8, in 5 rows)"
    grid = men.beasts_grid(saga, holder)
    assert grid.rows[2][2:] == ["2", "female", "Young"]
    facts = {f.label: f.value for f in men.menagerie_facts(saga, holder)}
    assert facts["Site"] == "The upper meadow, Magic aura 5"
    assert facts["Staff"] == "Ol Thomae (Animal Handling 4), Lech"
    assert facts["Upkeep"] == "1 Inhabitants point"
    assert facts["Reputation"].startswith("Keeper of Beasts 0")
    assert facts["As realia"] == "3 breeds: Magic Lore, Quality 3"
    assert hpc.progress(_project(saga)) == "8 beasts"
    assert hpc.note(_project(saga)) == "3 breeds"


def test_beast_and_breeding_ops():
    saga = menagerie_saga()
    holder = _holder(saga)
    project = _project(saga)
    project.breedings.append(Breeding(pair="Bock × Geiß", result="No young"))
    ops = men.beasts_ops(saga, holder)
    assert ops.add is not None and ops.edit is not None and ops.remove is not None
    add = ops.add()
    assert isinstance(add, Form)
    values = _values(add, name="Basilisk", kind="Beast of Legend", might=20, size=-1)
    assert add.validate is not None and add.validate(values) is None
    add.apply(values)
    assert project.beasts[-1].name == "Basilisk"
    bad = _values(add, name="Dog", kind=TRANSFORMED, might=5)
    assert "no Magic Might" in (add.validate(bad) or "")
    remove = ops.remove(0)
    assert isinstance(remove, Confirm)
    edit = men.breedings_ops(saga, holder).edit
    assert edit is not None
    form = edit(0)
    assert isinstance(form, Form)
    form.apply(_values(form, result="Two kids", young=2))
    assert (project.breedings[0].result, project.breedings[0].young) == ("Two kids", 2)


def test_the_project_form_has_the_menagerie_fields():
    saga = menagerie_saga()
    covenant = saga.covenants[0]
    form = hpc.project_form(saga, covenant, _project(saga))
    fields = {f.key: f for f in form.fields()}
    values = _values(form)
    for key in ("handler_0", "owner_id", "reputation"):
        assert fields[key].show_if is not None and fields[key].show_if(values)
    mason = fields["mason_id"].show_if
    assert mason is not None and not mason(values)
    form.apply(_values(form, handler_0="anna", handler_1="ol", handler_2="anna"))
    assert _project(saga).handler_ids == ["anna", "ol"]


def test_the_menagerie_round_trips_through_a_save():
    saga = menagerie_saga()
    _project(saga).breedings.append(Breeding(pair="Bock × Geiß", young=1))
    storage.save_saga(saga)
    loaded = storage.load_saga(saga.id)
    project = _project(loaded)
    assert project.kind == MENAGERIE
    assert [b.name for b in project.beasts] == [b.name for b in menagerie().beasts]
    assert project.beasts[2].born == 1219
    assert project.beasts[0].brands == menagerie().beasts[0].brands
    assert project.breedings[0].young == 1
    assert project.handler_ids == ["ol", "lech"]


def test_a_bad_beast_is_reported_by_name():
    data = {"kind": MENAGERIE, "beasts": [{"name": "Bock", "sex": "both ways"}]}
    try:
        HermeticProject.from_dict(data, "Dammerstein")
    except ValueError as error:
        assert "Bock" in str(error) and "sex" in str(error)
    else:
        raise AssertionError("a bad sex should be refused")


def test_beasts_of_female_and_male_for_breeding():
    project = menagerie()
    assert [b.name for b in men._sires(project)] == ["Bock", "Hare of Virtue"]
    assert FEMALE in {b.sex for b in men._dams(project)}
