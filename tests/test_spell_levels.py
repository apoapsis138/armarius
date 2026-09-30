"""Spell levels from their design (STORY-810)."""

import pytest

from ars_magica_manager import spells
from ars_magica_manager.models import Spell
from ars_magica_manager.rules import spell_levels as sl
from ars_magica_manager.screens.forms import _level_fill


@pytest.mark.parametrize(
    ("level", "magnitudes", "result"),
    [
        (4, 1, 5),
        (4, 2, 10),
        (3, 3, 10),
        (5, 3, 20),
        (15, -5, 2),  # the book's example: 15 -> 10 -> 5 -> 4 -> 3 -> 2
        (2, -4, 1),
    ],
)
def test_adding_and_removing_magnitudes(level, magnitudes, result):
    assert sl.add_magnitudes(level, magnitudes) == result


def test_a_spell_from_its_design():
    # Weaver's Trap of Webs: Base 5, +2 Voice, +2 Sun, +2 Group = 35.
    design = sl.spell_level(5, "Voice", "Sun", "Group")
    assert design is not None and design.level == 35
    assert design.design_line(5) == "Base 5, +2 Voice, +2 Sun, +2 Group"
    assert not design.ritual_required


def test_what_makes_a_ritual():
    year = sl.spell_level(1, "Touch", "Year", "Individual")  # 10, raised to 20
    assert year is not None and year.ritual_required and year.level == 20
    assert sl.spell_level(40, "Sight", "Sun", "Individual").ritual_required  # 55
    assert not sl.spell_level(3, "Touch", "Sun", "Vision").ritual_required


def test_a_supplements_own_parameter_has_no_worked_out_level():
    assert sl.spell_level(5, "Dream", "Sun", "Individual") is None


def test_extra_magnitudes_are_size_or_requisites():
    # Summoning the Creeping Death: Base 10, +1 Touch, +1 Diameter = 20,
    # listed at 25.
    assert sl.extra_magnitudes(10, "Touch", "Diameter", "Individual", 25) == 1
    assert sl.extra_magnitudes(10, "Touch", "Diameter", "Individual", 20) == 0
    assert sl.extra_magnitudes(10, "Touch", "Diameter", "Individual", 22) == 1


def test_the_design_line_in_the_spell_details():
    spell = Spell(
        id="s",
        name="Summoning",
        technique="Creo",
        form="Animal",
        level=25,
        base_level=10,
        range="Touch",
        duration="Diameter",
        target="Individual",
    )
    assert spells.design_text(spell) == (
        "Base 10, +1 Touch, +1 Diameter, +0 Individual, +1 size/requisites = 25"
    )
    spell.base_level = None
    assert spells.design_text(spell) == ""


def test_the_spell_form_fills_the_level():
    values = {
        "base_level": 5,
        "range": "Voice",
        "duration": "Sun",
        "target": "Group",
        "ritual": False,
    }
    assert _level_fill(values) == {"level": 35}
    assert _level_fill({**values, "base_level": None}) == {}
    assert _level_fill({**values, "range": "__other__", "range_other": "Dream"}) == {}


def test_a_virtues_extra_parameter_costs_as_its_standard_one():
    """Road (Road Magic) costs as Voice; Season (Spell Timing) as Moon and
    needs a Ritual (reference/spell-parameters.md)."""
    assert sl.spell_level(5, "Road", "Sun", "Individual").level == 25
    season = sl.spell_level(5, "Touch", "Season", "Individual")
    assert season.level == 25 and season.ritual_required
    assert [e.name for e in sl.extra_parameters("range", {"vf_road_magic"})] == [
        "Road",
        "Road Network",
    ]
    assert sl.extra_parameters("range", set()) == []


def test_a_custom_parameter_takes_typed_magnitudes():
    design = sl.spell_level(
        5, "Touch", "Dream", "Individual", custom_steps={"duration": 3}
    )
    assert design.level == 25
