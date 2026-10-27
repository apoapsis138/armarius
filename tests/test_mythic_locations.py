"""Mythic Locations' Mercurian rituals (pp. 96-101): the catalog's rituals,
translating and inventing them, their own effects, the aqueduct, and the
integrations they open."""

import pytest

from ars_magica_manager import catalog, spells
from ars_magica_manager.arts import ARTS
from ars_magica_manager.models import (
    Ability,
    Aging,
    ArtScore,
    Character,
    Saga,
)
from ars_magica_manager.rules import integrations
from ars_magica_manager.rules import mythic_locations as ml
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _magus(*abilities: tuple[str, int], arts: int = 0, id: str = "m") -> Character:
    return Character(
        id=id,
        name="Gaius",
        type="magus",
        abilities=[Ability(name, xp=ability_xp(score)) for name, score in abilities],
        arts={art.lower(): ArtScore(xp=art_xp(arts)) for art in ARTS} if arts else {},
    )


# -- the catalog ----------------------------------------------------------


def test_the_catalog_holds_each_recovered_ritual_as_the_book_prints_it():
    by_id = catalog.load_spell_catalog_by_id()
    found = {
        i: (
            by_id[i].technique[:2] + by_id[i].form[:2],
            by_id[i].level,
            by_id[i].ritual,
            by_id[i].source,
        )
        for i in ml.RITUAL_IDS
    }
    assert found == {
        "spell_purification": ("CrCo", 40, True, "ML"),
        "spell_the_scrying_pool": ("InIm", 20, True, "ML"),
        "spell_raising_the_auxiliaries_for_a_day": ("CrMe", 35, True, "ML"),
        "spell_penetrate_the_regio_skin": ("CrVi", 25, True, "ML"),
        "spell_blessing_of_mercury": ("CrVi", 30, True, "ML"),
        "spell_transformation_of_flesh_to_spirit": ("CrVi", 60, True, "ML"),
        "spell_wizard_s_initiation": ("CrVi", 75, True, "ML"),
        "spell_consecration_of_mercury_s_house": ("CrVi", 55, True, "ML"),
        "spell_commune_with_mercury": ("InVi", 20, True, "ML"),
    }
    assert by_id["spell_penetrate_the_regio_skin"].requisites == ["Rego"]
    assert by_id["spell_wizard_s_initiation"].requisites == ["Corpus"]


def test_the_details_panel_says_how_a_mercurian_ritual_is_learned():
    by_id = catalog.load_spell_catalog_by_id()
    text = spells.detail_text(
        Saga(id="s", name="s"), by_id["spell_wizard_s_initiation"]
    )
    assert "done at 150 points" in text
    assert "one season at a Lab Total of 225" in text
    assert "temple consecrated to Mercury" in text
    assert "It never works" in text
    other = spells.detail_text(Saga(id="s", name="s"), by_id["spell_the_scrying_pool"])
    assert "Mercurian ritual" in other and "consecrated" not in other
    plain = next(s for s in by_id.values() if s.source == "DE" and s.level)
    assert "Mercurian" not in spells.detail_text(Saga(id="s", name="s"), plain)


# -- reading, translating, inventing (p. 97) ------------------------------


def test_reading_needs_latin_and_magic_theory():
    assert ml.can_read(_magus((ml.LATIN, 4), (ml.MAGIC_THEORY, 1)))
    assert not ml.can_read(_magus((ml.LATIN, 4)))
    assert not ml.can_read(_magus((ml.MAGIC_THEORY, 4)))


def test_a_translation_season_adds_the_lab_total_less_the_level():
    first = ml.translate_season(0, 30, 20)
    assert first == ml.Translation(points=10, gained=10, finished=False)
    second = ml.translate_season(first.points, 50, 20)
    assert second == ml.Translation(points=40, gained=30, finished=True)
    assert ml.translation_points(20, 20) == 0
    assert ml.seasons_to_translate(20, 20) is None
    assert ml.seasons_to_translate(30, 20) == 4


def test_three_times_the_level_translates_in_one_season():
    assert ml.seasons_to_translate(120, 40) == 1
    assert ml.seasons_to_translate(119, 40) == 2


def test_earlier_translations_add_their_highest_magnitude():
    assert ml.translation_bonus([]) == 0
    assert ml.translation_bonus([20, 55, 30]) == 11
    # Lab Total 50 + 11 against level 40: 21 points.
    assert ml.translation_points(50, 40, ml.translation_bonus([55])) == 21


def test_inventing_from_the_copy_is_the_lab_text_rule():
    assert ml.can_invent(40, 40)
    assert not ml.can_invent(39, 40)


# -- Purification ---------------------------------------------------------


def _old(**aging: object) -> Character:
    target = _magus(id="t")
    target.aging = Aging(**aging)  # type: ignore[arg-type]
    return target


def test_purification_cannot_be_self_cast_or_on_no_decrepitude():
    caster = _magus()
    assert ml.purification_problems(caster, _old(decrepitude=2)) == []
    assert ml.purification_problems(caster, caster)[0].startswith("The caster")
    assert "no Decrepitude" in ml.purification_problems(caster, _old())[0]


def test_purification_lowers_decrepitude_looks_and_aging_points():
    target = _old(
        decrepitude=2,
        decrepitude_points=20,
        aging_points={"strength": 3, "stamina": 1, "quickness": 4},
    )
    changes = ml.purify(target, 70)
    assert target.aging.decrepitude == 1
    assert target.aging.decrepitude_points == 5
    assert target.aging.apparent_age == 65
    assert target.aging.aging_points == {"strength": 2, "stamina": 1, "quickness": 0}
    assert changes[0] == "Decrepitude 2 -> 1."
    again = ml.purify(target, 70)
    assert target.aging.apparent_age == 60 and target.aging.decrepitude == 0
    assert again and ml.purify(target, 70) == []


def test_the_player_chooses_where_purifications_aging_points_come_off():
    target = _old(
        decrepitude=2,
        decrepitude_points=20,
        aging_points={"strength": 3, "stamina": 1, "quickness": 4},
    )
    assert ml.default_purification(target) == {"quickness": 4, "strength": 1}
    assert "at most 5" in ml.purification_choice_problem(
        target, {"strength": 3, "quickness": 3}
    )
    assert "only 1" in ml.purification_choice_problem(target, {"stamina": 2})
    with pytest.raises(ValueError):
        ml.purify(target, 70, {"stamina": 2})
    assert target.aging.decrepitude == 2  # a refused choice changes nothing
    changes = ml.purify(target, 70, {"stamina": 1, "strength": 2})
    assert target.aging.aging_points == {"strength": 1, "stamina": 0, "quickness": 4}
    assert "1 Aging Point(s) off Stamina." in changes


# -- the other rituals ----------------------------------------------------


def test_transformation_raises_the_aura_only_for_a_strong_enough_caster():
    strong = _magus(arts=10)
    assert ml.transformation_aura(strong, 5, 26) == 6
    assert ml.transformation_aura(strong, 5, 25) == 5
    weak = _magus(arts=10)
    weak.arts["vim"] = ArtScore(xp=art_xp(9))
    problems = ml.transformation_problems(weak, 5, 30)
    assert problems == ["Arts under twice the aura (10): Vim."]
    assert ml.transformation_aura(_magus(arts=30), 10, 100) == 10


def test_wizards_initiation_never_works_and_consecration_makes_an_aura():
    assert not ml.initiation_works()
    assert ml.INITIATION_BOTCH_DICE == 1
    assert ml.consecrated_aura(0) == 1
    assert ml.consecrated_aura(3) == 3


@pytest.mark.parametrize(("roll", "placed"), [(1, False), (2, True)])
def test_the_regio_skin_opening_is_placed_by_dex_plus_finesse(roll, placed):
    assert ml.regio_skin_placed(1, 3, roll) is placed


# -- the aqueduct ---------------------------------------------------------


def test_neglecting_the_aqueduct():
    assert ml.neglect_ease(1) == 4
    assert ml.clogs(3, 1) and not ml.clogs(4, 1)
    assert not ml.clogs(1, 0)
    assert ml.catch_up_seasons(3) == 6
    assert ml.catch_up_seasons(50) == ml.AQUEDUCT_REPAIR_SEASONS == 40


# -- integrations ---------------------------------------------------------


def test_the_mercurian_integrations_are_research_goals():
    found = {
        i.name: (i.kind, i.target, i.grant_kind, i.grant)
        for i in integrations.INTEGRATIONS
        if i.book == integrations.ML
    }
    assert found == {
        "Mercurian aura creation": ("Minor", 30, "", ""),
        "Mercurian aura raising": ("Minor", 30, "", ""),
        "Mercurian regio entrance": ("Minor", 30, "", ""),
        "Mercurian Magic": ("Major", 45, "Virtue", "vf_mercurian_magic"),
        "Wizard's Initiation repaired": ("Hermetic", 60, "", ""),
    }
