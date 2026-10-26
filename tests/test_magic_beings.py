"""Magic beings by the book (Realms of Power: Magic pp. 51-56, 78-79,
128-139; Definitive Edition pp. 449-451)."""

from ars_magica_manager.forms import creature as creature_forms
from ars_magica_manager.models import (
    Ability,
    Characteristics,
    Creature,
    CreaturePower,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import magic_build as mb
from ars_magica_manager.sheets import creature as sheet


def _vf(*ids: str) -> list[VirtueFlawInstance]:
    return [VirtueFlawInstance(v) for v in ids]


def test_advancement_loses_the_might_less_two_a_pawn():
    # p. 52: Might 10, 15 xp: 5 kept; 5 pawns keep all 15; 4 pawns keep 13
    # (Errata p. 63 corrects the printed 7).
    assert mb.advancement_total(15, 10) == 5
    assert mb.advancement_total(15, 10, pawns=5) == 15
    assert mb.advancement_total(15, 10, pawns=4) == 13
    assert mb.pawns_to_clear(10) == 5
    # Gifted, learning a Supernatural Ability: its others count too, and
    # it eats at most its Might a season.
    assert (
        mb.advancement_total(20, 3, pawns=10, gifted=True, other_supernatural=6) == 17
    )
    assert mb.transformation_cost(12)[0] == "gain a Minor Quality"
    assert mb.vis_study_botch_dice(15) == 3


def test_acclimation_tables():
    # p. 53: Might 15 always within an aura of 3, half the time 8, no visits.
    assert mb.aura_needed(15) == (3, 8, None)
    assert mb.aura_needed(0) == (1, 5, 8)
    assert mb.aura_needed(51) == (None, None, None)
    # p. 54: Might 15 constantly three seasons; a level 30 effect two.
    assert mb.effect_seasons(15) == (3, None, None)
    assert mb.effect_seasons(30) == (2, 4, None)
    assert mb.effect_seasons(60) == (1, 1, 1)
    assert mb.vis_needed(15) == 8
    assert mb.vis_consumption(10).startswith("transformation")
    assert mb.vis_consumption(5) == "a negative side effect"


def test_a_magic_beings_advancement_shows_on_its_sheet():
    beast = Creature(id="b", name="B", realm="Magic", might=15)
    found = " ".join(f.value for f in sheet.build_facts(beast))
    assert "loses its Might (15)" in found and "8 pawn(s) of vis a year" in found


def test_a_beast_of_virtue():
    caladrius = Creature(
        id="c",
        name="Caladrius",
        realm="Magic",
        might=14,
        virtues_flaws=_vf(
            "vf_magic_animal", "vf_magical_friend", "vf_essential_virtue"
        ),
    )
    assert mb.beast_of_virtue_problems(caladrius) == []
    assert "about 3 pawn(s)" in mb.beast_of_virtue_notes(caladrius)[0]
    lame = Creature(
        id="d",
        name="Dog of Virtue",
        realm="Magic",
        might=5,
        virtues_flaws=_vf("vf_magic_animal", "vf_lame"),
        powers=[CreaturePower("Heal", quality="Focus Power")],
    )
    found = " ".join(mb.beast_of_virtue_problems(lame))
    assert "Essential Virtue" in found and "Lame" in found
    notes = " ".join(mb.beast_of_virtue_notes(lame))
    assert "Social Status" in notes and "not Focus Power" in notes


def test_a_transformed_animal():
    # p. 79: the Dog that Flew, Warping Score 3, two Minor Flaws.
    dog = Creature(
        id="f",
        name="Dog that Flew",
        warping_score=3,
        virtues_flaws=_vf("vf_form_monstrosity", "vf_warped_senses"),
    )
    assert mb.transformed_problems(dog) == []
    assert "2 Minor Flaw(s)" in mb.transformed_notes(dog)[0]
    early = Creature(
        id="e", name="E", warping_score=1, virtues_flaws=_vf("vf_lesser_power")
    )
    assert "only at Warping Score 5" in " ".join(mb.transformed_problems(early))
    assert mb.warping_gains(7) == (2, 1, 2)
    magical = Creature(id="m", name="M", realm="Magic", might=5, warping_score=2)
    assert "no Warping Score" in mb.transformed_problems(magical)[0]


def test_the_warping_score_is_on_the_form_and_cleared_with_a_realm():
    saga = Saga(id="s", name="S")
    beast = Creature(id="x", name="X", warping_score=2)
    saga.creatures.append(beast)
    keys = [f.key for f in creature_forms.info_fields(saga, beast)]
    assert "warping_score" in keys
    values = {f.key: f.value for f in creature_forms.info_fields(saga, beast)}
    creature_forms.apply_info(saga, beast, {**values, "realm": "Magic"})
    assert beast.warping_score == 0
    assert Creature.from_dict({"id": "o", "name": "Old"}).warping_score == 0


def test_an_awakened_tree():
    oak = Creature(id="o", name="Old Oak", might=5, realm="Magic")
    found = " ".join(mb.tree_problems(oak))
    assert "no Might" in found and "Cunning" in found
    ridden = Creature(
        id="r",
        name="Walking Willow",
        realm="Magic",
        might=3,
        cunning=True,
        powers=[CreaturePower("Manifestation", might_cost=3)],
    )
    assert mb.tree_problems(ridden) == []
    assert mb.tree_notes(ridden)
    # Its Might is the power's activation cost while it lasts (p. 128).
    ridden.might = 5
    assert "activation cost (3)" in " ".join(mb.tree_problems(ridden))


def test_a_familiar_learns_as_a_human():
    # Errata p. 63's sentence for RoP: Magic p. 52 (DE p. 267).
    being = Creature(id="b", name="Owl", realm="Magic", might=10)
    assert any("familiar" in note for note in mb.advancement_notes(being))


def test_a_magic_thing_never_tires():
    cloak = Creature(id="a", name="Amiculum", realm="Magic", might=5)
    cloak.virtues_flaws = _vf("vf_magic_thing")
    assert "No Fatigue" in mb.magic_thing_problems(cloak)[0]
    cloak.tires = False
    assert mb.magic_thing_problems(cloak) == []


def test_elemental_size_by_might():
    # DE p. 450: Might 1 Size -18, 2 -15, 5 -6, 15 0, 30 +9, 50 +21.
    assert [mb.elemental_size(m) for m in (1, 2, 5, 10, 15, 30, 50)] == [
        -18,
        -15,
        -6,
        -3,
        0,
        9,
        21,
    ]
    assert mb.elemental_size(3) == -12  # the gold nugget's Might 3 (p. 451)
    assert mb.typical_characteristics(17) == (4, 3, 2, 1, 0, 0, -2, -4)


def _earth_elemental() -> Creature:
    # DE p. 452 / RoP: Magic p. 137.
    return Creature(
        id="g",
        name="Earth Elemental",
        realm="Magic",
        might=15,
        might_form="Terram",
        cunning=True,
        characteristics=Characteristics(
            intelligence=0,
            perception=1,
            presence=-2,
            communication=-4,
            strength=3,
            stamina=6,
            dexterity=2,
            quickness=0,
        ),
        virtues_flaws=_vf(
            "vf_magic_thing",
            "vf_ways_of_the_land",
            "vf_poor_memory",
            "vf_short_attention_span",
            "vf_simple_minded",
        ),
        powers=[CreaturePower("Crush"), CreaturePower("Slake Thirst", might_cost=1)],
        abilities=[Ability("Brawl", xp=30), Ability("Athletics", xp=30)],
        tires=False,
    )


def test_the_books_earth_elemental_fits():
    earth = _earth_elemental()
    assert mb.element_of(earth) == "earth"
    assert mb.problems(earth) == []
    notes = " ".join(mb.notes(earth))
    assert "aura of 3" in notes and "5 points a pawn of Terram" in notes


def test_what_an_elemental_lacks():
    water = _earth_elemental()
    water.might_form = "Aquam"
    water.size = 2
    water.characteristics = Characteristics(
        intelligence=4,
        perception=-2,
        strength=3,
        stamina=3,
        dexterity=1,
        quickness=-4,
    )
    water.virtues_flaws = _vf("vf_poor_memory")
    water.abilities = [Ability("Brawl", xp=30)]
    found = " ".join(mb.elemental_problems(water))
    assert "Size +0" in found
    assert "Short Attention Span" in found and "Ways of the (Land)" in found
    assert "the power Drown" in found
    assert "Swim of at least" in found
    # Per -2: the book's own water elemental (p. 137) breaks p. 134's rule.
    assert "Per are never negative" in found
