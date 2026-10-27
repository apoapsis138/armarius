"""Egyptian tombs (Lands of the Nile pp. 32-35, 40-46, 55-56): the rules
of rules.egyptian_tombs, and a place's Tomb tab in tombs.py."""

import random

import pytest

from ars_magica_manager import neighbours, tombs
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.forms import neighbour as neighbour_forms
from ars_magica_manager.models import Character, Neighbour, Saga
from ars_magica_manager.rules import egyptian_tombs as et

# -- the rules --


@pytest.mark.parametrize(
    ("key", "aura", "points"),
    [
        ("major_monarch", 5, 500),
        ("minor_monarch", 4, 250),
        ("lesser_royal", 3, 100),
        ("dignitary", 3, 50),
    ],
)
def test_a_tombs_kind_gives_its_aura_and_build_points(key, aura, points):
    """LotN p. 40."""
    assert (et.KINDS[key].aura, et.KINDS[key].build_points) == (aura, points)


def test_a_burial_ground_tethers_one_a_century_to_five():
    assert [et.tether_score(c) for c in (0, 1, 3, 5, 6, 12)] == [0, 1, 3, 5, 5, 5]


def test_decay_lowers_the_aura_but_not_below_zero():
    assert et.tomb_aura("minor_monarch", 1) == 3
    assert et.tomb_aura("dignitary", 9) == 0
    assert et.tomb_aura("no longer known") == 3


@pytest.mark.parametrize(
    ("level", "points"),
    # The book's examples, pp. 41-42, 46: Apedemak's Strength, the
    # Destroying Uraeus, On the Presentation of Face, On Lowering the
    # Waters (rounded up), the Shrouded Oasis, the Djet.
    [(40, 16), (20, 8), (15, 6), (28, 12), (50, 20), (100, 40)],
)
def test_an_enchantment_costs_two_points_a_magnitude(level, points):
    assert et.enchantment_build_points(level) == points


def test_a_hollow_curse_costs_nothing_and_a_malediction_has_its_base():
    assert et.curse_build_points(et.HOLLOW, 30) == 0
    assert et.curse_build_points(et.GREATER, 45) == 18
    assert et.curse_problem(et.LESSER, 5) is not None
    assert et.curse_problem(et.GREATER, 25) is not None
    assert et.curse_problem(et.GREATER, 45) is None
    assert et.curse_problem(et.EFFECT, 0) is not None
    assert et.curse_problem(et.HOLLOW, 0) is None


@pytest.mark.parametrize(
    ("kind", "level", "ease"),
    # pp. 40-42: Apedemak 14, the Uraeus 10, Lowering the Waters 12; Turn
    # the Interloper 15, Nothing But Sky and Sand 17, A Sovereign Ward 19.
    [
        (et.TALISMAN, 40, 14),
        (et.TALISMAN, 20, 10),
        (et.TALISMAN, 28, 12),
        (et.WARD, 30, 15),
        (et.WARD, 39, 17),
        (et.WARD, 49, 19),
    ],
)
def test_overcoming_a_talisman_or_ward_without_magic(kind, level, ease):
    assert et.overcome_ease(kind, level) == ease


def test_magic_resistance_at_least_the_penetration_passes_untouched():
    assert et.passes_untouched(0, 0)
    assert et.passes_untouched(20, 16)
    assert not et.passes_untouched(10, 16)
    # A grog has no Magic Resistance at all, even against Penetration 0.
    assert not et.passes_untouched(None, 0)


@pytest.mark.parametrize(
    ("harm", "ease", "points"),
    # p. 43's examples: the Labyrinth 4, Prison Room 7, Rock Fall 9,
    # Medicinal Powders 12, Head Wires 15, Dead Drop 18.
    [
        ("scare", 6, 4),
        ("minor", 6, 7),
        ("minor", 9, 9),
        ("serious", 9, 12),
        ("minor", 15, 15),
        ("fatal", 12, 18),
    ],
)
def test_a_traps_build_points(harm, ease, points):
    assert et.trap_build_points(harm, ease) == points


def test_a_trap_of_an_unknown_harm_or_ease_is_refused():
    with pytest.raises(ValueError, match="harms"):
        et.trap_build_points("tickles", 3)
    with pytest.raises(ValueError, match="Ease Factor"):
        et.trap_build_points("scare", 4)


def test_spotting_a_trigger_by_the_light():
    """p. 44: -3 in perfect light, +3 by a single flame, +6 in near
    darkness."""
    assert et.spot_ease(12, "Perfect light") == 9
    assert et.spot_ease(12, "A single flame") == 15
    assert et.spot_ease(12, "Near darkness") == 18
    assert et.spot_ease(12, "Torches or lanterns") == 12


def test_the_one_in_danger_acts_first_then_by_quickness():
    """p. 33: the trap acts after them all."""
    order = et.action_order(
        [("Viktor", 1, False), ("Gregor", -1, True), ("Corvinus", 3, False)]
    )
    assert order == ["Gregor", "Corvinus", "Viktor"]


# -- the tomb on a place --


def _tomb() -> Neighbour:
    return Neighbour(
        id="grave",
        name="The Giant's Grave",
        kind="place",
        details={
            "tomb": True,
            "tomb_kind": "minor_monarch",
            "tomb_centuries": 6,
            "tomb_decay": 1,
            "tomb_other_bp": 47,
            "tomb_curses": [
                {"name": "Fear", "kind": et.EFFECT, "art": "CrMe", "level": 25},
                {"name": "Lost", "kind": et.LESSER, "art": "CrMe", "level": 25},
                {"name": "Bog", "kind": et.HOLLOW},
            ],
            "tomb_wards": [
                {"name": "Boar", "kind": et.TALISMAN, "art": "MuTe", "level": 40},
                {"name": "Turn", "kind": et.WARD, "art": "ReCo", "level": 30},
            ],
            "tomb_traps": [
                {"name": "Drop", "harm": "fatal", "ease": 12},
                {"name": "Stones", "harm": "minor", "ease": 9},
                {"name": "Maze", "harm": "scare", "ease": 6},
            ],
        },
    )


def _saga(place: Neighbour) -> Saga:
    gregor = Character(id="gregor", name="Gregor", type="grog")
    gregor.characteristics.quickness = 1
    return Saga(id="s", name="S", neighbours=[place], characters=[gregor])


def test_the_tombs_build_points_add_up_as_the_preview_drew_them():
    place = _tomb()
    assert tombs.spent(place) == {
        "curses": 20,
        "talismans and wards": 28,
        "traps": 31,
        "other resources": 47,
    }
    facts = {f.label: f.value for f in tombs.tomb_facts(_saga(place), place)}
    assert facts["Build Points"] == "126 of 250"
    assert facts["Magic aura"] == "3 (base 4; decayed)"
    assert facts["Tethers"] == "a burial ground 6 centuries in use: 5"


def test_overspending_is_shown_in_red():
    place = _tomb()
    place.details["tomb_other_bp"] = 200
    assert "$text-error" in tombs.tomb_text(_saga(place), place)


def test_the_lists_show_their_costs_and_ease_factors():
    place = _tomb()
    saga = _saga(place)
    assert tombs.curses_grid(saga, place).rows[2][1:] == [
        "no force",
        "",
        "0 BP",
    ]
    assert tombs.wards_grid(saga, place).rows[0][3] == "EF 14, 16 BP"
    assert tombs.traps_grid(saga, place).rows[0][3] == "18 BP"
    assert tombs.curses_title(saga, place) == "Curses (20 BP)"
    assert [e.badge for e in tombs.wards_ledger(saga, place)] == ["EF 14", "EF 15"]
    assert "12 for the harm + 6 for Ease Factor 12 = 18" in tombs.trap_info(
        saga, place, 0
    )


def test_the_tab_shows_only_on_a_tomb():
    place = _tomb()
    assert tombs.TOMB_TAB.shows(place)
    place.details["tomb"] = False
    assert not tombs.TOMB_TAB.shows(place)
    # Its lists still have their verbs, so a sheet built before the mark
    # changed acts on them as it shows them.
    ops = neighbour_forms.neighbour_ops(_saga(place), place)
    assert ops["section-nb-tomb-traps"].add is not None


def test_the_tomb_box_is_offered_with_lands_of_the_nile_or_once_marked():
    place = _tomb()
    place.details["tomb"] = False
    saga = _saga(place)
    saga.books_in_play = []
    assert tombs.mark_fields(saga, place) == []
    saga.books_in_play = ["LotN"]
    assert [f.key for f in tombs.mark_fields(saga, place)] == ["tomb"]
    saga.books_in_play = []
    place.details["tomb"] = True
    marked = tombs.mark_fields(saga, place)
    assert [f.key for f in marked] == ["tomb"]
    assert marked[0].value is True
    # New Place's keys always include it, so the box is kept in details.
    kind = neighbours.KINDS["place"]
    assert kind.fields is not None
    assert "tomb" in {f.key for f in kind.fields(saga, None)}


def test_adding_a_trap_keeps_its_ease_as_a_number():
    place = _tomb()
    saga = _saga(place)
    form = tombs.trap_ops(saga, place).add()
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    values.update(name="Head Wires", harm="minor", ease="15")
    assert form.validate is not None and form.validate(values) is None
    assert form.live is not None
    assert "[b]15 Build Points[/]" in form.live(values)
    form.apply(values)
    assert tombs.traps(place)[-1]["ease"] == 15
    assert tombs.spent(place)["traps"] == 46


def test_a_hollow_curse_keeps_no_level_and_a_malediction_needs_its_base():
    place = _tomb()
    form = tombs.curse_ops(_saga(place), place).add()
    assert isinstance(form, Form) and form.validate is not None
    values = {f.key: f.value for f in form.fields()}
    values.update(name="Seth", kind=et.GREATER, level=25, condition="Whoever")
    assert "level 30" in (form.validate(values) or "")
    values.update(kind=et.HOLLOW)
    assert form.validate(values) is None
    form.apply(values)
    assert "level" not in tombs.curses(place)[-1]


def test_edit_tomb_refuses_more_than_ten_points_of_hooks():
    place = _tomb()
    form = tombs.edit_tomb(_saga(place), place)
    assert form.validate is not None
    values = {f.key: f.value for f in form.fields()}
    values["tomb_hook_points"] = 11
    assert "10" in (form.validate(values) or "")
    values["tomb_hook_points"] = 4
    assert form.validate(values) is None


def test_overcome_it_rolls_against_the_traps_ease_factor():
    place = _tomb()
    saga = _saga(place)
    form = tombs.overcome_trap(saga, place, 0, random.Random(3))
    assert isinstance(form, Form) and form.live is not None
    values = {f.key: f.value for f in form.fields()}
    values.update(who="gregor", in_danger=True, adjust=-3, roll="Qik + Athletics")
    live = form.live(values)
    assert "adjusted to 9" in live
    assert "Quickness 1 + Athletics 0 + stress die against 9" in live
    assert "Order: Gregor, then the trap" in live
    step = form.apply(values)
    assert isinstance(step, Confirm)
    step.apply()
    written = tombs.place_events.diary(place)[-1]["text"]
    assert written.startswith("Gregor") and written.endswith("against Drop.")


def test_a_fast_cast_spell_is_not_rolled_against_the_trap():
    place = _tomb()
    saga = _saga(place)
    form = tombs.overcome_trap(saga, place, 0)
    assert isinstance(form, Form) and form.live is not None
    values = {f.key: f.value for f in form.fields()}
    values.update(who="gregor", fast_cast=True)
    assert "Fast-Cast" in form.live(values)
    assert isinstance(form.apply(values), list)


def test_overcome_it_needs_a_trap():
    place = _tomb()
    assert isinstance(tombs.overcome_trap(_saga(place), place, 9), Refuse)


def test_a_roll_of_a_characteristic_alone():
    gregor = Character(id="g", name="Gregor", type="grog")
    gregor.characteristics.stamina = 2
    assert tombs.roll_score(gregor, "Sta") == (2, "Stamina 2")
    with pytest.raises(ValueError):
        tombs.roll_score(gregor, "Luck + Dice")
