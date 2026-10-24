"""Derived character values."""

import pytest

from ars_magica_manager import sheet_text
from ars_magica_manager.models import (
    Character,
    Characteristics,
    Possession,
    VirtueFlawInstance,
    Wounds,
)
from ars_magica_manager.rules import derived


def _character(*vf_ids: str, **kw) -> Character:
    return Character(
        id="c",
        name="C",
        type="companion",
        virtues_flaws=[VirtueFlawInstance(vf_id=v) for v in vf_ids],
        **kw,
    )


@pytest.mark.parametrize(
    ("vf_ids", "size"),
    [((), 0), (("vf_large",), 1), (("vf_giant_blood",), 2), (("vf_dwarf",), -2)],
)
def test_size_from_virtues_and_flaws(vf_ids, size):
    assert derived.size(_character(*vf_ids)).total == size


def test_size_text_shows_where_it_comes_from():
    assert sheet_text.size_text(_character()) == "0"
    assert sheet_text.size_text(_character("vf_large")) == "1 (base 0, Large +1)"


@pytest.mark.parametrize(
    ("size", "bands"),
    [
        (0, [(1, 5), (6, 10), (11, 15), (16, 20), (21, None)]),
        (2, [(1, 7), (8, 14), (15, 21), (22, 28), (29, None)]),
        (-3, [(1, 2), (3, 4), (5, 6), (7, 8), (9, None)]),
        (-6, [(1, 1), (2, 2), (3, 3), (4, 4), (5, None)]),
    ],
)
def test_damage_table(size, bands):
    assert [(low, high) for _, low, high in derived.wound_ranges(size)] == bands


def test_wound_for_an_excess():
    assert derived.wound_for(0, 0) is None
    assert derived.wound_for(7, 0) == "Medium"
    assert derived.wound_for(21, 0) == "Dead"
    assert derived.wound_for(7, 2) == "Light"


def test_penalties_add_up():
    assert derived.wound_penalty(Wounds(light=2, medium=1, heavy=1)) == -10
    assert derived.fatigue_penalty("tired") == -3
    assert derived.fatigue_penalty("winded") == 0


@pytest.mark.parametrize(
    ("load", "burden"), [(0, 0), (1, 1), (2, 1), (3, 2), (7, 3), (55, 10), (66, 11)]
)
def test_burden(load, burden):
    assert derived.burden(load) == burden


def test_encumbrance_is_burden_less_positive_strength():
    assert derived.encumbrance(7, 0) == 3
    assert derived.encumbrance(7, 2) == 1
    assert derived.encumbrance(7, 5) == 0
    assert derived.encumbrance(7, -2) == 3  # no extra penalty for low Strength


def test_soak_from_stamina_armour_virtues_and_the_adjustment():
    character = _character(
        "vf_tough",
        characteristics=Characteristics(stamina=2),
        inventory=[
            Possession(
                id="a", kind="armor", name="Leather", armor_protection=2, load=2
            ),
            Possession(id="b", kind="armor", name="Chain", armor_protection=6, load=6),
            Possession(id="w", kind="weapon", name="Sword", load=1, quantity=2),
        ],
        wounds=Wounds(soak=-1),
    )
    soak = derived.soak(character)
    assert soak.total == 2 + 6 + 3 - 1
    assert derived.terms(soak) == "Stamina +2, Chain +6, Tough +3, Adjustment -1"
    # Only the armour worn (the Chain) and the weapons carried (DE p. 403).
    assert derived.carried_load(character.inventory) == 6 + 2


def test_frail_and_nephilim():
    assert derived.soak(_character("vf_frail")).total == -3
    assert derived.size(_character("vf_blood_of_the_nephilim")).total == 1
