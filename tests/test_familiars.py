import pytest

from ars_magica_manager import familiars as fam
from ars_magica_manager.models import (
    Ability,
    BondPower,
    Character,
    Characteristics,
    Familiar,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
)
from ars_magica_manager.rules.xp import ability_xp


def _saga() -> tuple[Saga, Character, Familiar]:
    magus = Character(id="mag1", name="Corvinus", type="magus")
    familiar = Familiar(id="fam1", character_id="mag1", name="Ashwing")
    saga = Saga(id="s", name="Saga", characters=[magus], familiars=[familiar])
    return saga, magus, familiar


def test_familiar_of_finds_the_one_bound_to_a_character():
    saga, _magus, familiar = _saga()
    assert fam.familiar_of(saga, "mag1") is familiar
    assert fam.familiar_of(saga, "someone-else") is None


def test_magus_of_finds_the_binding_character():
    saga, magus, familiar = _saga()
    assert fam.magus_of(saga, familiar) is magus


def test_magus_of_returns_none_if_the_character_no_longer_exists():
    familiar = Familiar(id="fam1", character_id="gone", name="Ashwing")
    saga = Saga(id="s", name="Saga", familiars=[familiar])
    assert fam.magus_of(saga, familiar) is None


@pytest.mark.parametrize(
    "score,expected", [(0, 0), (1, 5), (2, 15), (3, 30), (4, 50), (5, 75)]
)
def test_cord_cost_follows_the_fixed_table(score, expected):
    assert fam.cord_cost(score) == expected


def test_identity_text_shows_the_magus_and_core_fields():
    saga, _magus, familiar = _saga()
    familiar.species = "Raven"
    familiar.season_bound = "Spring"
    familiar.year_bound = 1220
    familiar.magic_might = 10
    familiar.might_pool = 8
    familiar.size = -2
    familiar.wound_multiplier = 1
    text = fam.identity_text(saga, familiar)
    assert "Magus Partner: Corvinus" in text
    assert "Species / Description: Raven" in text
    assert "Season / Year Bound: Spring 1220" in text
    assert "Magic Might Score: 10 (Current Pool: 8)" in text
    assert "Size: -2 (Wound Multiplier: 1)" in text


def test_identity_text_handles_unset_fields():
    saga, _magus, familiar = _saga()
    text = fam.identity_text(saga, familiar)
    assert "Species / Description: (not set)" in text
    assert "Season / Year Bound: (not set)" in text
    assert "Magic Might Score: 0" in text
    assert "(Current Pool" not in text


def test_binding_text_shows_typed_in_fields_with_no_formula():
    _, _magus, familiar = _saga()
    familiar.binding_technique = "Creo"
    familiar.binding_form = "Animal"
    familiar.binding_lab_total = 45
    familiar.target_binding_level = 40
    familiar.vis_spent_binding = 3
    text = fam.binding_text(familiar)
    assert "Binding Arts Used: Creo / Animal" in text
    assert "Initial Binding Lab Total: 45" in text
    assert "Target Binding Level: 40" in text
    assert "Cumulative Vis Spent on Binding: 3 pawns" in text


def test_cords_text_shows_score_cost_and_the_mechanical_blurb():
    _, _magus, familiar = _saga()
    familiar.golden_cord = 2
    text = fam.cords_text(familiar)
    assert "Golden Cord: +2 (15 pts)" in text
    assert "Botch Dice" in text
    assert "Silver Cord: +0 (0 pts)" in text
    assert "Bronze Cord: +0 (0 pts)" in text


def test_vf_rows_filters_by_type_and_shows_the_tier():
    _, _magus, familiar = _saga()
    familiar.virtues_flaws = [
        VirtueFlawInstance(vf_id="vf_true_friend"),
        VirtueFlawInstance(vf_id="vf_wrathful"),
    ]
    virtues = fam.vf_rows(familiar, "Virtue")
    flaws = fam.vf_rows(familiar, "Flaw")
    assert [i for i, _ in virtues] == [0]
    assert "True Friend" in virtues[0][1] and "Minor" in virtues[0][1]
    assert [i for i, _ in flaws] == [1]
    assert "Wrathful" in flaws[0][1]


def test_personality_trait_and_reputation_rows_show_signed_scores():
    _, _magus, familiar = _saga()
    familiar.personality_traits = [ScoredTrait(name="Loyal (Partner)", score=3)]
    familiar.reputations = [ScoredTrait(name="Fierce", score=-1)]
    assert fam.personality_trait_rows(familiar) == [(0, "Loyal (Partner): +3")]
    assert fam.reputation_rows(familiar) == [(0, "Fierce: -1")]


def test_characteristics_text_shows_signed_scores_and_typed_in_defenses():
    _, _magus, familiar = _saga()
    familiar.characteristics = Characteristics(
        intelligence=2, perception=-1, stamina=3, quickness=1
    )
    familiar.base_soak = 5
    familiar.magic_resistance = 12
    text = fam.characteristics_text(familiar)
    assert "Int: +2" in text
    assert "Per: -1" in text
    assert "Sta: +3" in text
    assert "Qik: +1" in text
    assert "Base Soak: 5" in text
    assert "Magic Resistance: 12" in text


def test_ability_rows_groups_by_category_with_headers():
    _, _magus, familiar = _saga()
    familiar.abilities = [
        Ability(
            name="Athletics", category="General", xp=ability_xp(3), specialty="Running"
        ),
        Ability(name="Magic Theory", category="Arcane", xp=ability_xp(2)),
    ]
    rows = fam.ability_rows(familiar)
    assert rows == [
        (None, "General"),
        (0, "Athletics (Running) 3 30/50"),
        (None, "Arcane"),
        (1, "Magic Theory 2 15/30"),
    ]


def test_ability_info_text_shows_catalog_description():
    _, _magus, familiar = _saga()
    familiar.abilities = [Ability(name="Athletics", category="General")]
    assert fam.ability_info_text(familiar, None) == (
        "[dim]Select an Ability to see its details.[/]"
    )
    assert "General physical prowess" in fam.ability_info_text(familiar, 0)


def test_bond_power_rows_and_info_text():
    _, _magus, familiar = _saga()
    familiar.bond_powers = [
        BondPower(
            id="p1",
            name="Speak with Beasts",
            level=15,
            technique="Creo",
            form="Animal",
            target_controller="Familiar (controlled by Magus)",
            uses_per_day=3,
            penetration=5,
            vis_spent=2,
            cosmetic_trait="A feathered crest",
        )
    ]
    assert fam.bond_power_rows(familiar) == [(0, "Speak with Beasts")]
    assert fam.bond_power_info_text(familiar, None) == (
        "[dim]Select a Bond Power to see its details.[/]"
    )
    text = fam.bond_power_info_text(familiar, 0)
    assert "Speak with Beasts" in text
    assert "Level:[/] 15" in text
    assert "Creo / Animal" in text
    assert "Familiar (controlled by Magus)" in text
    assert "Uses/Day:[/] 3" in text
    assert "Penetration:[/] 5" in text
    assert "Vis Spent:[/] 2" in text
    assert "A feathered crest" in text


def test_unbonded_magi_are_the_magi_without_a_familiar():
    saga, magus, _familiar = _saga()
    free = Character(id="mag2", name="Aelia", type="magus")
    companion = Character(id="comp1", name="Alys", type="companion")
    saga.characters += [free, companion]
    assert fam.unbonded_magi(saga) == [free]
    assert magus not in fam.unbonded_magi(saga)


def test_bind_familiar_adds_it_and_grants_the_bond_to_both_partners():
    saga, _magus, _familiar = _saga()
    magus = Character(id="mag2", name="Aelia", type="magus")
    saga.characters.append(magus)
    familiar = fam.bind_familiar(saga, magus, "Ashwing")
    assert saga.familiars[-1] is familiar
    assert familiar.id == "ashwing"  # from the name; "fam1" doesn't clash
    assert familiar.character_id == "mag2" and familiar.name == "Ashwing"
    for partner in (familiar, magus):
        assert [vf.vf_id for vf in partner.virtues_flaws] == ["vf_true_friend"]
        assert [(t.name, t.score) for t in partner.personality_traits] == [
            ("Loyal (Partner)", 3)
        ]
