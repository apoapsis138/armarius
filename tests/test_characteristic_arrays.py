"""Characteristic arrays: offered to any character on the standard 7-point
budget, placed by rank, each value used exactly once."""

from __future__ import annotations

from ars_magica_manager.models import Character, VirtueFlawInstance
from ars_magica_manager.rules import creation_characteristics as cch

ARRAY = (3, 2, 2, 1, 1, 0, -1, -3)


def _scores(**set_to: int) -> dict[str, int]:
    return {key: set_to.get(key, 0) for key, _ in cch.CHARACTERISTICS}


def test_every_array_spends_the_standard_points():
    for array in cch.GROG_ARRAYS:
        assert sum(cch.cost(n) for n in array) == cch.BUDGET


def test_offered_to_every_character_type_on_the_standard_budget():
    for kind in ("magus", "companion", "grog"):
        character = Character(id="c", name="C", type=kind)
        assert cch.arrays_offered(character)
        assert cch.arrays_withheld(character) == ""


def test_not_offered_with_improved_characteristics_and_says_why():
    character = Character(id="c", name="C", type="companion")
    character.virtues_flaws.append(VirtueFlawInstance(cch.IMPROVED))
    assert not cch.arrays_offered(character)
    assert cch.arrays_withheld(character) == (
        "each array spends 7 points, and this character has 10"
    )


def test_placed_by_rank_puts_the_highest_on_the_highest_ties_in_book_order():
    character = Character(id="c", name="C", type="grog")
    character.characteristics.quickness = 2
    character.characteristics.perception = 1
    placed = cch.placed_by_rank(character, ARRAY)
    assert placed == {
        "quickness": 3,
        "perception": 2,
        "intelligence": 2,
        "strength": 1,
        "stamina": 1,
        "presence": 0,
        "communication": -1,
        "dexterity": -3,
    }


def test_a_placement_using_each_value_once_passes():
    placed = dict(zip([k for k, _ in cch.CHARACTERISTICS], ARRAY, strict=True))
    assert cch.placement_problem(ARRAY, placed) is None


def test_a_value_used_twice_and_one_left_out_are_named():
    placed = dict(zip([k for k, _ in cch.CHARACTERISTICS], ARRAY, strict=True))
    placed["dexterity"] = 3
    problem = cch.placement_problem(ARRAY, placed)
    assert problem == (
        "Each of the array's values goes on one Characteristic; "
        "used too often: +3; left out: -1"
    )


def test_a_blank_form_names_every_value_left_out_once():
    problem = cch.placement_problem(ARRAY, _scores())
    assert problem is not None
    assert "used too often: +0 (7 times)" in problem
