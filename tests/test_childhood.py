"""Young characters (Apprentices, Chapter Two): the Aging Chart and the
Child Virtues that move it, Child and Inherited Virtues by age, a
parent's vocation, the transitions of maturation and the standard
apprenticeship model (a saga option)."""

from __future__ import annotations

import random

import pytest

from ars_magica_manager import seasons, worksheet
from ars_magica_manager.forms import worksheet as wf
from ars_magica_manager.models import (
    Ability,
    Character,
    CreationXp,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import childhood, options
from ars_magica_manager.rules import creation as rules
from ars_magica_manager.rules import creation_later as later
from ars_magica_manager.rules import creation_magus as magus

YEAR = 1220


def _saga(*, books: list[str] | None = None, model: bool = False) -> Saga:
    saga = Saga(id="s", name="S", current_year=YEAR, books_in_play=books)
    if model:
        saga.rule_options = {options.STANDARD_APPRENTICESHIP: True}
    return saga


def _character(type_: str = "companion", years: int | None = 10, *vf_ids: str):
    character = Character(id="c", name="C", type=type_, in_creation=True)  # type: ignore[arg-type]
    character.background.year_born = None if years is None else YEAR - years
    character.virtues_flaws = [VirtueFlawInstance(vf_id) for vf_id in vf_ids]
    return character


def _by_label(found):
    return {c.label: (c.status, c.detail) for c in found}


# -- The Aging Chart --


@pytest.mark.parametrize(
    ("years", "modifier", "size"),
    [(0, -10, -3), (2, -8, -3), (3, -7, -2), (7, -4, -2), (9, -3, -2), (12, -1, -1)]
    + [(13, -1, -1), (14, 0, 0), (30, 0, 0)],
)
def test_the_aging_chart_by_age(years, modifier, size):
    child = _character()
    assert childhood.characteristic_modifier(child, years) == modifier
    assert childhood.size_for_age(child, years) == size


def test_a_late_bloomer_is_a_category_behind():
    # The book's example: a child of 12 has -2 and Size -2.
    bloomer = _character("companion", 12, childhood.LATE_BLOOMER)
    assert childhood.characteristic_modifier(bloomer, 12) == -2
    assert childhood.size_for_age(bloomer, 12) == -2
    assert childhood.characteristic_modifier(bloomer, 16) == -1
    assert childhood.charted(bloomer, 16)


def test_grows_quickly_moves_only_size():
    quick = _character("companion", 12, childhood.GROWS_QUICKLY)
    assert childhood.size_for_age(quick, 12) == 0
    assert childhood.characteristic_modifier(quick, 12) == -1


def test_deft_halves_its_characteristics_modifier_toward_zero():
    deft = _character("companion", 9)
    deft.virtues_flaws = [
        VirtueFlawInstance(childhood.DEFT, {"characteristic": "Strength"})
    ]
    assert childhood.characteristic_modifier(deft, 9, "strength") == -1
    assert childhood.characteristic_modifier(deft, 9, "stamina") == -3
    assert childhood.characteristic_modifier(deft, 0, "strength") == -5


def test_size_virtues_wait_a_year_and_never_go_below_minus_three():
    large = _character("companion", 1, "vf_large")
    assert childhood.size_for_age(large, 0) == -3
    assert childhood.size_for_age(large, 1) == -2  # the book's first birthday
    assert childhood.size_for_age(large, 14) == 1
    small = _character("companion", 1, "vf_small_frame")
    assert childhood.size_for_age(small, 11) == -3
    assert childhood.size_for_age(small, 12) == -2  # the book's 12
    dwarf = _character("companion", 1, "vf_dwarf")
    assert childhood.size_for_age(dwarf, 13) == -3
    assert childhood.size_for_age(dwarf, 14) == -2  # the book's 14


def test_the_characteristics_step_shows_the_modifier_and_the_size_for_age():
    child = _character("companion", 9)
    found = _by_label(rules.checks(_saga(), child, "characteristics"))
    assert found["Characteristic Modifier at age 9"] == (
        "pass",
        "-3 to every Characteristic's rolls",
    )
    assert found["Size -2 at age 9"] == (
        "advice",
        "Size +0: set the base Size to -2",
    )
    child.background.size = -2
    found = _by_label(rules.checks(_saga(), child, "characteristics"))
    assert found["Size -2 at age 9"][0] == "pass"


def test_no_aging_chart_checks_for_adults_or_without_the_book():
    adult = _character("companion", 25)
    labels = _by_label(rules.checks(_saga(), adult, "characteristics"))
    assert not any("at age" in label for label in labels)
    child = _character("companion", 9)
    labels = _by_label(rules.checks(_saga(books=[]), child, "characteristics"))
    assert not any("at age" in label for label in labels)


# -- Child and Inherited Virtues and Flaws --


def test_child_virtues_only_to_twenty():
    for years, status in ((20, "pass"), (21, "warn")):
        found = _by_label(
            rules.checks(
                _saga(),
                _character("companion", years, "vf_boundless_energy"),
                "virtues_flaws",
            )
        )
        assert found["Child Virtues and Flaws only to age 20"] == (
            status,
            f"age {years}: Boundless Energy",
        )


def test_inherited_virtues_for_magi_and_companions_manifested_by_21():
    grog = _character("grog", 10)
    grog.virtues_flaws = [
        VirtueFlawInstance("vf_inherited_virtue", {"virtue": "Large"})
    ]
    found = _by_label(rules.checks(_saga(), grog, "virtues_flaws"))
    assert found["Inherited Virtues and Flaws only for magi and companions"] == (
        "warn",
        "grog: Inherited Large",
    )
    assert found["Inherited Virtues and Flaws manifest by 21"][0] == "pass"
    grown = _character("companion", 21)
    grown.virtues_flaws = list(grog.virtues_flaws)
    found = _by_label(rules.checks(_saga(), grown, "virtues_flaws"))
    assert found["Inherited Virtues and Flaws manifest by 21"][0] == "warn"
    assert found["Inherited Virtues and Flaws only for magi and companions"][0] == (
        "pass"
    )


def test_no_virtue_that_grants_xp_younger_than_14():
    found = _by_label(
        rules.checks(
            _saga(), _character("companion", 13, "vf_warrior"), "virtues_flaws"
        )
    )
    assert found["No Virtue that grants xp younger than 14"] == (
        "warn",
        "age 13: Warrior",
    )
    found = _by_label(
        rules.checks(
            _saga(), _character("companion", 14, "vf_warrior"), "virtues_flaws"
        )
    )
    assert "No Virtue that grants xp younger than 14" not in found


def test_turbulence_prone_needs_the_gift():
    found = _by_label(
        rules.checks(
            _saga(), _character("companion", 9, "vf_turbulence_prone"), "virtues_flaws"
        )
    )
    assert found["Turbulence Prone only with The Gift"][0] == "warn"
    gifted = _character("companion", 9, "vf_turbulence_prone", "vf_the_gift")
    found = _by_label(rules.checks(_saga(), gifted, "virtues_flaws"))
    assert "Turbulence Prone only with The Gift" not in found


def test_none_of_the_young_checks_without_apprentices_in_play():
    character = _character("grog", 25, "vf_boundless_energy", "vf_warrior")
    labels = _by_label(rules.checks(_saga(books=[]), character, "virtues_flaws"))
    assert not any("Child" in label or "grants xp" in label for label in labels)


# -- A parent's vocation --


def _knights_son(score: int) -> Character:
    son = _character("companion", 12)
    son.creation_conditions.vocation = "Single Weapon"
    son.creation_conditions.vocation_score = 7
    son.abilities.append(Ability("Single Weapon", xp=5 * score * (score + 1) // 2))
    son.creation_xp.append(CreationXp("later_life", "Single Weapon", 15))
    return son


def test_a_childs_vocation_is_capped_at_half_the_parents_score():
    found = _by_label(rules.checks(_saga(), _knights_son(3), "later_life"))
    assert found["Single Weapon at most half the parent's 7"] == ("pass", "3 of 3")
    found = _by_label(rules.checks(_saga(), _knights_son(4), "later_life"))
    assert found["Single Weapon at most half the parent's 7"] == ("warn", "4 of 3")


def test_the_vocation_may_be_learned_though_of_a_closed_type():
    found = _by_label(rules.checks(_saga(), _knights_son(3), "later_life"))
    assert "Only Abilities the character may learn" not in found
    son = _knights_son(3)
    son.creation_conditions.vocation = ""
    found = _by_label(rules.checks(_saga(), son, "later_life"))
    assert found["Only Abilities the character may learn"] == ("warn", "Single Weapon")


def test_past_14_only_the_age_cap_remains():
    son = _knights_son(4)
    son.background.year_born = YEAR - 15
    labels = _by_label(rules.checks(_saga(), son, "later_life"))
    assert not any("half the parent" in label for label in labels)


def test_the_worksheet_asks_for_the_vocation_of_a_young_character():
    saga = _saga()
    labels = [
        a.label
        for a in worksheet.panel_for(_character(), "later_life").actions(
            saga, _character()
        )
    ]
    assert "Parent's vocation" in labels
    adult = _character("companion", 30)
    assert not childhood.vocation_offered(saga, adult)
    assert not childhood.vocation_offered(_saga(books=[]), _character())


def test_the_vocation_form_saves_and_refuses_a_score_without_a_vocation():
    character = _character()
    form = wf.parent_vocation(character)
    assert form.validate is not None
    assert form.validate({"vocation": " ", "vocation_score": 4})
    assert form.validate({"vocation": "Craft: Smith", "vocation_score": -1})
    form.apply({"vocation": " Craft: Smith ", "vocation_score": 6})
    assert (
        character.creation_conditions.vocation,
        character.creation_conditions.vocation_score,
    ) == ("Craft: Smith", 6)
    assert later.later_life_budget(_saga(), character) >= 0


# -- Transitions of maturation --


def test_the_transitions_fall_at_8_15_and_21():
    assert [y for y in range(30) if childhood.transition(y)] == [8, 15, 21]


def test_the_year_end_notes_next_years_transition():
    saga = _saga()
    child = _character("companion", 14, "vf_boundless_energy")
    child.in_creation = False
    adult = _character("companion", 40)
    adult.id = "d"
    adult.in_creation = False
    saga.characters = [child, adult]
    lines = childhood.year_end_transitions(saga, saga.characters)
    assert [(line.character_id, line.what) for line in lines] == [
        ("c", "child to adolescent")
    ]
    assert "may be kept until 21: Boundless Energy" in lines[0].result
    assert child.diary[-1].name == "Transition of maturation at 15"


def test_at_21_child_virtues_must_go():
    text = childhood.transition_text(
        _character("companion", 20, "vf_boundless_energy"), 21
    )
    assert "must be exchanged now: Boundless Energy" in text


def test_winter_adds_the_transitions_to_the_years_end():
    saga = _saga()
    saga.current_season = "Winter"
    child = _character("companion", 7)
    child.in_creation = False
    saga.characters = [child]
    done = seasons.finish_season(saga, [], {}, random.Random(1))
    assert any(line.activity == "Transition of maturation" for line in done.year_end)


def test_no_transitions_without_apprentices_in_play():
    saga = _saga(books=[])
    child = _character("companion", 7)
    assert childhood.year_end_transitions(saga, [child]) == []


# -- The standard apprenticeship model --


def test_the_model_year_by_year():
    assert childhood.model_budget(0) == childhood.ModelBudget(0, 0, 0)
    assert childhood.model_budget(5) == childhood.ModelBudget(5, 95, 0)
    assert childhood.model_budget(12) == childhood.ModelBudget(12, 228, 0)
    assert childhood.model_budget(13) == childhood.ModelBudget(13, 234, 40)
    assert childhood.model_budget(15) == childhood.ModelBudget(15, 246, 120)
    # A Skilled Parens: the DE's 60 xp and 30 levels more over the whole.
    assert childhood.model_budget(15, 1) == childhood.ModelBudget(15, 306, 150)
    assert childhood.model_budget(15, -1) == childhood.ModelBudget(15, 186, 90)


def _apprentice(years: int, *vf_ids: str) -> Character:
    character = _character("magus", 10 + years, *vf_ids)
    character.hermetic.age_of_apprenticeship = 10
    return character


def test_the_option_is_off_by_default_and_only_with_apprentices():
    assert not options.is_on(_saga(), options.STANDARD_APPRENTICESHIP)
    keys = [o.key for o in options.offered(_saga(books=[]))]
    assert options.STANDARD_APPRENTICESHIP not in keys
    assert options.STANDARD_APPRENTICESHIP in [
        o.key for o in options.offered(_saga(books=["App"]))
    ]


def test_without_the_option_an_apprentice_has_the_des_240():
    apprentice = _apprentice(5)
    assert magus.xp_budget(apprentice, _saga()) == 240
    assert magus.level_budget(apprentice, _saga()) == 120


def test_with_the_option_an_apprentice_has_the_years_so_far():
    saga = _saga(model=True)
    apprentice = _apprentice(5, "vf_skilled_parens")
    assert magus.years_apprenticed(saga, apprentice) == 5
    assert magus.xp_budget(apprentice, saga) == 120
    assert magus.level_budget(apprentice, saga) == 0
    # A finished magus keeps the DE's.
    assert magus.xp_budget(_apprentice(15), saga) == 240
    assert magus.xp_budget(_apprentice(14), saga) == 240


def test_model_checks_pool_xp_and_levels_and_leave_gauntlet_to_come():
    saga = _saga(model=True)
    apprentice = _apprentice(13)
    apprentice.creation_xp = [
        CreationXp("apprenticeship", "Creo", 250),
        CreationXp("apprenticeship_spells", "spell_x", 20),
    ]
    found = _by_label(rules.checks(saga, apprentice, "apprenticeship"))
    label = "Standard apprenticeship, 13 years: 234 xp and 40 spell levels"
    assert found[label] == ("pass", "250 xp and 20 levels, 270 of 274")
    assert found["Apprenticeship xp and spell levels spent"] == ("advice", "4 unspent")
    assert found["Parma Magica at least 1 by Gauntlet"][0] == "advice"
    apprentice.creation_xp[0].xp = 260
    found = _by_label(rules.checks(saga, apprentice, "apprenticeship"))
    assert found[label] == ("warn", "260 xp and 20 levels, 280 of 274, 6 too many")


def test_the_worksheet_shows_the_model():
    saga = _saga(model=True)
    apprentice = _apprentice(3)
    text = worksheet.panel_for(apprentice, "apprenticeship").budget(saga, apprentice)
    assert "Standard apprenticeship (Apprentices p. 14): 3 of 15 years, 57 xp" in text
