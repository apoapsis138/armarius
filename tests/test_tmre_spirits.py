"""Hermetic spirit magic and Hermetic theurgy (The Mysteries Revised
Edition pp. 64-88, Errata p. 50), checked against the book's own worked
examples, and More's Spirits and Names calculator."""

import random

from ars_magica_manager import actions
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import tmre_spirits as forms
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import realms
from ars_magica_manager.rules import tmre_spirits as ts


def _art_xp(score: int) -> int:
    return score * (score + 1) // 2


def _magus(*virtues: str, **arts: int) -> Character:
    magus = Character(
        id="m",
        name="Graculus",
        type="magus",
        characteristics=Characteristics(intelligence=3, perception=2, stamina=1),
        abilities=[
            Ability("Magic Theory", xp=75),  # 5
            Ability("Magic Lore", xp=30),  # 3
        ],
        virtues_flaws=[VirtueFlawInstance(v) for v in virtues],
    )
    for art, score in arts.items():
        magus.arts[art] = ArtScore(xp=_art_xp(score))
    return magus


def _saga(magus: Character) -> Saga:
    saga = Saga(id="s", name="Test", current_year=1220, current_season="Spring")
    saga.characters.append(magus)
    saga.characters.append(Character(id="p", name="Plain", type="magus"))
    return saga


# -- Hermetic Empowerment (pp. 64-66) --


def test_medicas_staff_drains_its_spirit_as_the_book_says():
    # A Might 27 spirit heals two Incapacitating Wounds (35), then can't
    # power a third, but heals a Medium Wound (25) once (p. 65).
    uses = ts.drain_uses(27, [35, 35, 35, 25, 25])
    assert [(u.powered, u.might_left) for u in uses] == [
        (True, 20),
        (True, 13),
        (False, 13),
        (True, 8),
        (False, 8),
    ]
    assert ts.might_drained(25) == 5 and ts.might_drained(35) == 7


def test_might_need_only_reach_half_the_ritual_level():
    # The Errata (p. 50) corrects p. 66 to agree with p. 65.
    assert ts.can_power(13, 25)
    assert not ts.can_power(12, 25)


def test_the_empowering_prison_holds_half_its_base_level():
    assert ts.prison_holds(48) == 24
    assert ts.prison_level(24) == 48


# -- Spirit Familiar (pp. 66-69) --


def test_a_spirit_familiar_bond_uses_the_worse_aura():
    magus = _magus(ts.SPIRIT_FAMILIAR, rego=10, vim=8)
    assert ts.spirit_familiar_level(15) == 40
    assert ts.bonding_aura(3, 1) == 1
    assert ts.spirit_familiar_total(magus, "Rego", "Vim", 1) == 10 + 8 + 3 + 5 + 1
    assert ts.bonding_vis(27) == 6
    assert ts.familiar_pyramid_points(17) == 3
    assert ts.hekate_bonus(2, 3) == 6 and ts.hekate_bonus(2, 9) == 10


def test_a_daimon_familiar_takes_a_fifth_of_its_might_in_vis():
    assert ts.daimon_familiar_vis(21) == 5
    assert ts.daimon_rejects(30, 20) and not ts.daimon_rejects(40, 20)


# -- Inscription on the Soul (pp. 69-70) --


def test_blending_with_substance_matches_the_sapphire_and_the_tongue():
    assert ts.blending_level([2, 2, 3]) == 25
    assert ts.blending_level([6, 3]) == 40
    assert ts.blending_warping(25) == 1 and ts.blending_warping(40) == 2


# -- Living Ghost (pp. 70-74) --


def test_graculus_becomes_a_living_ghost_of_might_fifty():
    graculus = _magus(ts.LIVING_GHOST, rego=28, mentem=26)
    limit, arts = ts.best_combination(graculus, focus=True)
    assert (limit, arts) == (80, "Rego Mentem")
    assert ts.best_combination(graculus)[0] == 54
    assert ts.bind_ghost_level(30) == 60
    assert ts.ghost_might(80, 30, limit) == 50
    assert ts.ghost_problems(80, 30, limit) == []
    assert ts.ghost_problems(70, 30, limit)
    # Fifteen points spent as vis, twelve spaces opened (p. 74).
    assert ts.restored_might(35, 12, 50) == 47
    assert ts.restored_might(35, 20, 50) == 50
    assert ts.familiar_joins_vis(11) == 3


# -- Names of Power and the theurgic Lab Total (pp. 76-79) --


def test_names_of_power_never_add_more_than_magic_theory():
    assert ts.name_level(3) == 15
    assert ts.names_bonus([3, 4], 5) == 5
    assert ts.names_bonus([1, 2], 5) == 3


def test_the_theurgic_lab_total_adds_realm_lore_and_names():
    magus = _magus(ts.HERMETIC_THEURGY, creo=10, ignem=8)
    total = ts.theurgic_lab_total(
        magus, "Creo", "Ignem", lore="Magic Lore", aura_modifier=3, names=9
    )
    # 10 + 8 + Int 3 + MT 5 + aura 3 + Lore 3 + Names (capped at MT) 5.
    assert total == 37


# -- Invoking spirits (pp. 78-81) --


def test_akkala_casts_pilum_of_fire_in_a_faerie_aura():
    # Might 20, a level 4 Faerie aura (+2), Range raised to Sight (p. 80).
    aura = realms.aura_modifier(realms.HERMETIC, "Faerie", 4)
    cast = ts.spell_spirit(20, 20, aura, step=1)
    assert (cast.casting_total, cast.level, cast.succeeds) == (22, 25, True)
    assert cast.penetration == -3
    # Sun duration: two magnitudes on the Might 20 base.
    assert ts.invoke_level(20, duration_levels=10) == 30


def test_nissila_penetrates_in_a_divine_aura():
    aura = realms.aura_modifier(realms.HERMETIC, "Divine", 3)
    cast = ts.spell_spirit(20, 20, aura, penetration_levels=15)
    # The book prints 11 - 20 + 30 as +23 (p. 80); the formula gives 21.
    assert (cast.casting_total, cast.succeeds, cast.penetration) == (11, True, 21)
    assert not ts.spell_spirit(20, 20, -11).succeeds
    assert ts.spell_spirit_problem(15, 20)


def test_a_form_spirit_casts_at_half_its_might():
    cast = ts.form_spirit(15, 0, 8)
    assert (cast.casting_total, cast.succeeds, cast.penetration) == (8, True, 0)
    assert not ts.form_spirit(15, 0, 9).succeeds


def test_a_daimon_pact_gathers_points_until_the_aspect_comes():
    pact = ts.daimon_pact(30, 20)
    assert (pact.points, pact.castings, pact.at_once) == (10, 2, False)
    assert ts.daimon_pact(30, 20, gathered=10).castings == 1
    assert ts.daimon_pact(40, 20).at_once
    assert ts.daimon_pact(20, 20).castings is None
    assert ts.daimon_points(42) == 9


# -- Ascendancy to the Hall of Heroes (pp. 82-86) --


def test_gloria_needs_eleven_ceremonies():
    gloria = _magus(ts.ASCENDANCY, rego=34, animal=32)
    gloria.characteristics = Characteristics(quickness=-1, strength=-2, perception=-1)
    best, _arts = ts.best_combination(gloria)
    assert ts.ascendant_minimum(best) == 66
    assert ts.ascendant_minimum(20) == 40
    cost = ts.negative_characteristics_cost(gloria)
    assert cost == 5
    # Her 17 Virtue points beat her 14 Flaw points: nothing more (p. 84).
    needed = ts.transformation_needed(66, cost, 2, 17, 14)
    assert needed == 91
    points = ts.transformation_points(75, 66)
    assert points == 9
    assert ts.ceremonies(needed, 0, points) == 11
    assert ts.transformation_needed(66, 0, 0, 10, 12) == 66 + 60
    assert ts.ascended_might(66) == 33


# -- Synthemata (pp. 86-88) --


def test_synthemata_add_their_level_to_penetration():
    assert ts.synthemata_least_level(20) == 20
    assert ts.synthemata_least_level(20, lasting=True) == 25
    assert ts.synthemata_penetration(25, lasting=True) == 20
    assert ts.synthemata_points(40, 20, 10) == 10
    assert ts.typical_name_hiding(21) == 10
    assert ts.hedge_lord_bonus(15) == 10


def test_the_synthemata_lab_total_uses_realm_lore_not_magic_theory():
    magus = _magus(ts.HERMETIC_SYNTHEMATA, muto=7, vim=9)
    total = ts.synthemata_lab_total(
        magus, lore="Magic Lore", aura_modifier=2, bonuses=4
    )
    assert total == 7 + 9 + 3 + 3 + 2 + 4


def test_intuiting_is_perception_and_lore_against_might_and_hiding():
    magus = _magus(ts.SYNTHEMATA_MAGIA)
    assert ts.intuit_total(magus, "Magic Lore", 3) == 2 + 3 + 3
    assert ts.intuit_ease(10, 3, 5) == 18


# -- More's Spirits and Names --


def test_the_calculator_offers_each_virtues_workings():
    theurgist = _magus(ts.HERMETIC_THEURGY)
    keys = [key for _label, key in forms.workings(theurgist)]
    assert keys[:4] == [
        forms.SPELL_SPIRIT,
        forms.FORM_SPIRIT,
        forms.DAIMON_PACT,
        forms.THEURGIC_LAB,
    ]
    assert forms.GHOST not in keys
    ghost = _magus(ts.LIVING_GHOST)
    assert [key for _l, key in forms.workings(ghost)] == [
        forms.DAIMON_PACT,
        forms.GHOST,
    ]
    assert not forms.offers(_magus())


def test_every_working_says_something():
    magus = _magus(*ts.VIRTUES, rego=12, vim=10, mentem=8)
    saga = _saga(magus)
    form = forms.spirits_form(saga, magus, random.Random(3))
    assert isinstance(form, Form)
    defaults = {f.key: f.value for f in form.fields()}
    for _label, key in forms.workings(magus):
        said = forms.lines(magus, {**defaults, "working": key, "bonuses": "3, 2"})
        assert said and all(said), key
        assert form.apply({**defaults, "working": key, "bonuses": "3, 2"})
    assert magus.diary == []


def test_a_bad_list_is_refused():
    assert forms.problem({"bonuses": "3, two"})
    assert forms.problem({"rituals": "25, 35"}) is None


def test_intuiting_rolls_against_the_spirits_figures():
    magus = _magus(ts.SYNTHEMATA_MAGIA)
    saga = _saga(magus)
    form = forms.spirits_form(saga, magus, random.Random(1))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    values.update(working=forms.INTUIT, might=10, name_hiding=5, aura=0)
    said = form.apply(values)
    assert "against 15" in said[0]


def test_the_spell_spirit_line_names_its_penetration():
    magus = _magus(ts.HERMETIC_THEURGY)
    values = {
        "working": forms.SPELL_SPIRIT,
        "might": 20,
        "power_level": 20,
        "penetration_levels": 15,
        "aura": 3,
        "aura_realm": "Divine",
    }
    said = forms.lines(magus, values)
    assert "level 35" in said[0]
    assert "casts at 11" in said[1] and "Penetration +21" in said[1]


def test_only_a_mystery_holder_finds_it_on_known_spells():
    magus = _magus(ts.HERMETIC_THEURGY)
    saga = _saga(magus)
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="m")
    assert "Spirits and Names" in [
        i.label for i in menu_forms.placed(page, "Magic Outside the Lab")
    ]
    plain = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="p")
    assert not actions.available("spirits_and_names", plain)
    assert isinstance(forms.spirits_form(saga, saga.character("p")), Refuse)
