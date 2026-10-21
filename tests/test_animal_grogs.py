"""Animal grogs (Grogs, Chapter 7: Horses & Hounds): the kinds and their
penalties, Size on Strength and Quickness, the Virtues and Flaws an
animal holds, its pre-adult life and Language, its aging through the
seasons, the book's sample Dog, Horse and Hawk, and hounds on the
covenant's lists."""

import random
from fractions import Fraction

import pytest

from ars_magica_manager import catalog, creation
from ars_magica_manager import grog_templates as gt
from ars_magica_manager import inhabitants as inh
from ars_magica_manager.forms import animal as animal_forms
from ars_magica_manager.models import (
    Ability,
    AnimalForm,
    Character,
    Characteristics,
    Covenant,
    Inhabitant,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import animal_aging, creation_access
from ars_magica_manager.rules import animal_grogs as ag
from ars_magica_manager.rules import creation as rules
from ars_magica_manager.rules import creation_characteristics as cch
from ars_magica_manager.rules import creation_later as later
from ars_magica_manager.rules import creation_packages as packages
from ars_magica_manager.rules import creation_virtues as cv
from ars_magica_manager.rules.creation_base import steps_for
from ars_magica_manager.seasons.animal_aging import season_aging

VFS = catalog.load_virtue_flaw_catalog_by_id()
ANIMALS = catalog.load_animal_template_catalog()


def _animal(kind="clawed", species="Dog", lifespan=None, **changes) -> Character:
    character = Character(
        id="rex",
        name="Rex",
        type="grog",
        animal=AnimalForm(kind, species, species, lifespan),
        **changes,
    )
    return character


def _from_template(template_id, age_index=0, status=None):
    template = gt.find(template_id)
    assert template is not None
    saga = Saga(id="s", name="S", current_year=1220)
    grog = creation.add_character(saga, "Rex", "grog", None)
    choices = gt.Choices(
        age=age_index,
        status=status or template.statuses[0],
        virtues_flaws=[gt.instance(e) for e in template.virtues_flaws],
    )
    values = {b: f"The {b}" for b in gt.blanks(template, choices)}
    gt.apply(saga, grog, template, choices, values)
    return saga, grog, template, choices


def _failing(saga, character, step=None):
    return {
        c.label: c.status
        for c in rules.checks(saga, character, step)
        if c.status != "pass"
    }


# -- kinds --


def test_each_kind_has_the_book_s_penalties_with_humans():
    assert {k: (v.presence, v.communication) for k, v in ag.KINDS.items()} == {
        "clawed": (-2, -5),
        "hoofed": (-4, -5),
        "bird": (-1, -2),
        "fish": (-5, -6),
    }
    assert ag.penalties_text(_animal()) == "Presence -2, Communication -5"
    assert ag.penalties_text(_animal(), short=True) == "Pre -2, Com -5"
    assert ag.penalties_text(Character(id="p", name="P", type="grog")) == ""
    assert ag.describe(AnimalForm("hoofed", "Horse")) == "Horse, a Hoofed Beast"


# -- aging --


def test_the_aging_table_is_the_book_s():
    assert animal_aging.TABLE["clawed"] == animal_aging.AgingFigures(9, 1, 6, 2, 5)
    assert animal_aging.TABLE["hoofed"] == animal_aging.AgingFigures(27, 3, 20, 5, 2)
    assert animal_aging.TABLE["bird"] == animal_aging.AgingFigures(
        81, 8, 55, 15, Fraction(1, 2)
    )
    assert animal_aging.TABLE["fish"] == animal_aging.AgingFigures(
        243, 24, 170, 50, Fraction(1, 5)
    )


def test_a_species_of_its_own_scales_the_human_figures_by_its_lifespan():
    # A cat living 15 years: 50 / 15 = 3.33, so three rolls a year.
    cat = animal_aging.kind_figures("clawed", 15)
    assert cat == animal_aging.AgingFigures(15, 2, 11, 3, 3)
    # Its kind's own lifespan keeps the book's figures.
    assert animal_aging.kind_figures("clawed", 9) == animal_aging.TABLE["clawed"]
    # A lifespan longer than a man's rolls less often than once a year.
    tortoise = animal_aging.kind_figures("fish", 150)
    assert tortoise.rolls_a_year == Fraction(1, 3)
    assert animal_aging.scaled(50) == animal_aging.HUMAN


def test_an_animal_s_age_adds_by_its_kind_s_years_a_point():
    dog = _animal()
    assert animal_aging.start_age(dog) == 6
    assert animal_aging.age_modifier(dog, 7) == 4  # 7 / 2 rounded up
    person = Character(id="p", name="P", type="grog")
    assert animal_aging.start_age(person) is None
    assert animal_aging.age_modifier(person, 41) == 5


def test_the_rolls_are_spread_over_the_seasons_the_spare_ones_in_winter():
    dog, horse = _animal(), _animal("hoofed", "Horse")
    seasons = ("Spring", "Summer", "Autumn", "Winter")
    assert [animal_aging.rolls_in_season(dog, 7, s) for s in seasons] == [1, 1, 1, 2]
    assert [animal_aging.rolls_in_season(horse, 21, s) for s in seasons] == [
        0,
        1,
        0,
        1,
    ]
    hawk = _animal("bird", "Hawk")
    # Every second year from 55, in Winter.
    assert animal_aging.rolls_in_year(hawk, 55) == 1
    assert animal_aging.rolls_in_season(hawk, 55, "Winter") == 1
    assert animal_aging.rolls_in_year(hawk, 56) == 0
    assert animal_aging.rolls_between(dog, 6, 8) == 10


def test_an_animal_ages_as_the_seasons_pass():
    saga = Saga(id="s", name="S", current_year=1220, current_season="Winter")
    dog = _animal()
    dog.background.year_born = 1212  # 8: past its 6
    dog.in_creation = False
    young = _animal("clawed", "Puppy")
    young.id = "pup"
    young.background.year_born = 1218
    young.in_creation = False
    saga.characters = [dog, young]
    lines = season_aging(saga, random.Random(1))
    assert len(lines) == 2  # the dog's two Winter rolls; the puppy is too young


def test_the_aging_roll_uses_the_animal_s_modifier():
    from ars_magica_manager.rules import aging

    dog = _animal()
    dog.background.year_born = 1210
    assert aging.start_age(dog) == 6


# -- Size --


def test_size_adds_to_strength_and_takes_from_quickness():
    horse = _animal("hoofed", "Horse")
    assert ag.size_adjustment(horse, "strength", 2) == 4
    assert ag.size_adjustment(horse, "quickness", 2) == -2
    assert ag.size_adjustment(horse, "stamina", 2) == 0
    person = Character(id="p", name="P", type="grog")
    assert ag.size_adjustment(person, "strength", 2) == 0
    horse.background.size = 2
    assert cch.size_adjustment(horse, "strength") == 4


# -- Virtues and Flaws --


def test_no_hands_and_mute_are_free_and_a_major_personality_flaw_counts_minor():
    dog = _animal()
    assert ag.counted(dog, VFS["vf_no_hands"]) is None
    assert ag.counted(dog, VFS["vf_mute"]) is None
    major = next(
        d
        for d in VFS.values()
        if d.side == "Flaw"
        and d.tier == "Major"
        and "Personality" in (d.category, *d.extra_categories)
    )
    counted = ag.counted(dog, major)
    assert counted is not None and counted.tier == "Minor" and counted.cost == -1
    person = Character(id="p", name="P", type="grog")
    assert ag.counted(person, VFS["vf_mute"]) is VFS["vf_mute"]


def test_an_animal_s_free_flaws_show_as_free():
    dog = _animal(
        virtues_flaws=[VirtueFlawInstance(f) for f in ("vf_no_hands", "vf_mute")]
    )
    benefit = cv.animal_benefit(dog)
    assert benefit is not None
    assert set(benefit.free_indices) == {0, 1}


def test_an_animal_is_refused_human_society_and_the_wrong_social_status():
    chooser = catalog.VirtueFlawChooser.for_character(_animal())
    assert chooser.animal
    assert "human society" in chooser.refusal(VFS["vf_educated"])
    assert chooser.refusal(VFS["vf_companion_animal"]) == ""
    knight = next(
        d
        for d in VFS.values()
        if "Social Status" in (d.category, *d.extra_categories)
        and d.id not in ag.STATUSES
    )
    assert "human society" in chooser.refusal(knight)
    assert chooser.refusal(VFS["vf_no_hands"]) == ""


def test_the_book_s_pool_is_in_the_catalog():
    for vf_id in (*ag.POOL_VIRTUES, *ag.POOL_FLAWS, *ag.STATUSES, *ag.FREE_FLAWS):
        assert vf_id in VFS, vf_id
    for vf_id in ag.HUMAN_SOCIETY:
        assert vf_id in VFS, vf_id
    assert ag.RESTRICTED_LEARNING in VFS


# -- Languages and xp --


def test_a_human_language_is_learnt_at_4_plus_cunning_read_down_by_a_negative_one():
    dog = _animal(characteristics=Characteristics(intelligence=-2))
    assert ag.language_quality(dog, "Living Language: French") == 2
    assert ag.language_quality(dog, "Dog") is None
    assert ag.understood(dog, "Living Language: French", 3) == 1
    dog.abilities = [Ability("Living Language: French", xp=15)]
    assert ag.language_lines(dog) == [
        "Understands Living Language: French 2 as 0 (Cunning -2)"
    ]
    clever = _animal(characteristics=Characteristics(intelligence=1))
    assert ag.understood(clever, "Living Language: French", 3) == 3


def test_an_animal_has_120_xp_to_its_grown_age_then_15_a_year():
    assert ag.years_xp("clawed", 1) == 120
    assert ag.years_xp("clawed", 4) == 165
    assert ag.years_xp("hoofed", 10) == 225
    assert ag.years_xp("bird", 8) == 120


def test_an_animal_has_pre_adult_life_in_place_of_early_childhood():
    saga = Saga(id="s", name="S", current_year=1220)
    dog = _animal(in_creation=True)
    keys = [s.key for s in steps_for(dog)]
    assert "youth" in keys and "childhood" not in keys
    person = Character(id="p", name="P", type="grog", in_creation=True)
    keys = [s.key for s in steps_for(person)]
    assert "childhood" in keys and "youth" not in keys
    assert later.xp_a_year(dog) == 15
    assert not packages.offered(saga, dog)


def test_the_ability_cap_is_read_at_the_age_scaled_to_a_human_life():
    saga = Saga(id="s", name="S", current_year=1220)
    dog = _animal()
    dog.background.year_born = 1216
    assert ag.cap_age(saga, dog) == 22  # 4 * 50 / 9
    person = Character(id="p", name="P", type="grog")
    person.background.year_born = 1200
    assert ag.cap_age(saga, person) == 20


# -- the templates --


@pytest.mark.parametrize(
    ("template_id", "age_index", "xp"),
    [
        ("at_dog", 0, 120),
        ("at_dog", 1, 165),
        ("at_horse", 0, 120),
        ("at_horse", 1, 225),
        ("at_hawk", 0, 120),
    ],
)
def test_a_sample_spends_its_age_s_xp_with_the_language_apart(
    template_id, age_index, xp
):
    _, grog, template, _ = _from_template(template_id, age_index)
    language = [x for x in grog.creation_xp if x.note == ag.LANGUAGE_NOTE]
    assert [(x.step, x.xp) for x in language] == [("youth", 15)]
    others = [x for x in grog.creation_xp if x.note != ag.LANGUAGE_NOTE]
    assert sum(x.xp for x in others) == xp
    assert sum(x.xp for x in others if x.step == "youth") == 120
    assert gt.template_xp(template, template.ages[age_index]["age"]) == xp


def test_the_book_has_three_animal_samples():
    assert [(t.name, [a["age"] for a in t.ages]) for t in ANIMALS] == [
        ("Dog", [1, 4]),
        ("Horse", [3, 10]),
        ("Hawk", [8]),
    ]
    assert all(t.page == 137 for t in ANIMALS)
    # They stay apart from the nineteen human templates.
    assert not {t.id for t in ANIMALS} & {t.id for t in gt.templates(None)}


def test_a_sample_is_an_animal_with_its_free_flaws_size_and_status():
    _, grog, _, _ = _from_template("at_horse", status="vf_companion_animal")
    assert grog.animal == AnimalForm("hoofed", "Horse", "Horse")
    assert grog.background.size == 2
    ids = [vf.vf_id for vf in grog.virtues_flaws]
    assert {"vf_restricted_learning", "vf_no_hands", "vf_mute"} <= set(ids)
    assert grog.characteristics.strength == 4
    assert grog.characteristics.quickness == -2
    assert ("Loyal to Master", 1) in [
        (t.name, t.score) for t in grog.personality_traits
    ]
    assert grog.in_creation


def test_a_sample_breaks_none_of_an_animal_s_rules():
    saga, grog, _, _ = _from_template("at_dog")
    failing = _failing(saga, grog)
    for step in ("concept", "youth", "later_life"):
        assert not [
            label
            for label, status in _failing(saga, grog, step).items()
            if status == "warn"
        ], (step, failing)


def test_the_template_limits_refuse_human_society():
    template = gt.find("at_dog")
    assert template is not None
    chosen = [
        VirtueFlawInstance("vf_companion_animal"),
        VirtueFlawInstance("vf_restricted_learning"),
        VirtueFlawInstance("vf_educated"),
    ]
    problem = gt.limit_problem(chosen, gt.animal_form(template))
    assert problem and "society" in problem


# -- the creation checks --


def test_the_checks_name_what_an_animal_lacks():
    saga = Saga(id="s", name="S", current_year=1220)
    dog = _animal(in_creation=True)
    dog.background.year_born = 1218
    failing = _failing(saga, dog)
    assert failing["An animal takes Restricted Learning"] == "warn"
    assert failing["No Hands and Mute, held free"] == "advice"
    assert failing["Domestic Animal, Wanderer or Companion Animal"] == "warn"
    assert failing["The animal Language at 2"] == "warn"


def test_animal_ken_is_never_above_the_animal_language():
    saga = Saga(id="s", name="S", current_year=1220)
    dog = _animal(in_creation=True)
    dog.abilities = [Ability("Dog", xp=15), Ability("Animal Ken", xp=30)]
    failing = _failing(saga, dog, "later_life")
    assert failing["Animal Ken no higher than Dog"] == "warn"


def test_the_animal_form_makes_a_grog_an_animal_and_back():
    saga = Saga(id="s", name="S", current_year=1220)
    grog = creation.add_character(saga, "Rex", "grog", None)
    values = {
        "kind": "clawed",
        "species": "Dog",
        "language": "",
        "lifespan": None,
        "size": -1,
    }
    assert animal_forms.animal_problem(values) is None
    assert animal_forms.animal_problem({**values, "species": ""})
    assert animal_forms.animal_problem({**values, "lifespan": 0})
    animal_forms.apply_animal(grog, values)
    assert grog.animal == AnimalForm("clawed", "Dog", "Dog")
    assert grog.background.size == -1
    assert {"vf_restricted_learning", "vf_no_hands", "vf_mute"} <= {
        vf.vf_id for vf in grog.virtues_flaws
    }
    assert [(x.step, x.target, x.xp) for x in grog.creation_xp] == [
        ("youth", "Dog", 15)
    ]
    animal_forms.apply_animal(grog, {**values, "species": "Hound", "language": "Hound"})
    assert [(x.target, x.xp) for x in grog.creation_xp] == [("Hound", 15)]
    animal_forms.apply_animal(grog, {"kind": animal_forms.PERSON})
    assert grog.animal is None
    assert grog.creation_xp == []
    assert not [a for a in grog.abilities if a.xp]


def test_an_animal_s_supernatural_opening_virtues_count_as_society():
    # A Virtue opening Academic, Arcane or Martial Abilities is about people.
    assert ag.about_society(VFS["vf_educated"], creation_access.OPENS)


# -- the covenant's hounds --


def test_hounds_are_listed_but_not_counted_as_inhabitants():
    covenant = Covenant(id="c", saga_id="s", name="C")
    saga = Saga(id="s", name="S", covenants=[covenant])
    before = inh.total_inhabitants(saga, covenant)
    covenant.inhabitants.append(
        Inhabitant(id="h", kind="hound", name="Pack", quantity=6)
    )
    assert inh.total_inhabitants(saga, covenant) == before
    covenant.inhabitants.append(
        Inhabitant(id="n", kind="horse", name="Nags", quantity=2)
    )
    assert inh.total_inhabitants(saga, covenant) == before + 2
    assert inh.KIND_TITLES["hound"] == "Hounds"


def test_horses_and_hounds_offer_the_covenant_s_animal_grogs():
    covenant = Covenant(id="c", saga_id="s", name="C")
    dog = _animal(covenant_id="c")
    man = Character(id="m", name="Man", type="grog", covenant_id="c")
    saga = Saga(id="s", name="S", covenants=[covenant], characters=[dog, man])
    assert inh.takes_grogs("hound") and inh.takes_grogs("horse")
    assert not inh.takes_grogs("livestock")
    assert inh.available_grogs(saga, covenant, "hound") == [dog]
    assert inh.available_grogs(saga, covenant, "horse") == [dog]
    assert inh.available_grogs(saga, covenant, "turb") == [man]
