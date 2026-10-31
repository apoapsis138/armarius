"""Egyptian tombs (Lands of the Nile pp. 32-35, 40-46, 55-56): the rules
of rules.egyptian_tombs, and a place's Tomb tab in tombs.py."""

import random

import pytest

from ars_magica_manager import neighbours, tombs
from ars_magica_manager.book_packs import africa as africa_pack
from ars_magica_manager.book_packs import nile as nile_pack
from ars_magica_manager.book_packs.builder import Builder
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


def _values(form: Form, **changes: object) -> dict[str, object]:
    return {**{f.key: f.value for f in form.fields()}, **changes}


def _party_saga(place: Neighbour) -> Saga:
    saga = _saga(place)
    corvinus = Character(id="corvinus", name="Corvinus", type="magus")
    corvinus.characteristics.quickness = 3
    saga.characters.append(corvinus)
    return saga


def test_overcome_it_goes_in_order_and_ends_in_the_diary():
    """pp. 32-33: the one in danger first, each rolls for his own action
    against an Ease Factor moved for it, and the trap goes last."""
    place = _tomb()
    saga = _party_saga(place)
    opening = tombs.overcome_trap(saga, place, 0, random.Random(3))
    assert isinstance(opening, Form) and opening.live is not None
    values = _values(opening, who="gregor", with_corvinus=True)
    assert "Order: Gregor, Corvinus, then it acts" in opening.live(values)
    first = opening.apply(values)
    assert isinstance(first, Form) and first.live is not None
    assert first.title.startswith("Gregor Acts")
    moved = _values(first, adjust=-3, roll="Qik + Athletics", action="vaults clear")
    assert "Quickness 1 + Athletics 0 + stress die against 9" in first.live(moved)
    second = first.apply(moved)
    assert isinstance(second, Form) and second.title.startswith("Corvinus Acts")
    assert second.live is not None
    assert "Gregor, vaults clear," in second.live(_values(second))
    last = second.apply(_values(second, fast_cast=True))
    assert isinstance(last, Form) and last.title.startswith("It Acts")
    labels = [f.label for f in last.fields()]
    assert "Corvinus is helped, or out of its reach" in labels
    assert last.live is not None
    assert "Corvinus" in last.live(_values(last))
    ended = last.apply(_values(last, outcome="He lands on a ledge."))
    assert isinstance(ended, list)
    written = tombs.place_events.diary(place)[-1]["text"]
    assert written.startswith("Gregor, vaults clear,")
    assert "Fast-Cast" in written
    assert written.endswith("He lands on a ledge.")
    assert tombs.traps(place)[0]["sprung"] is True


def test_a_fast_cast_spell_that_works_clears_the_trap():
    """Only those who failed and weren't helped suffer it (p. 33)."""
    place = _tomb()
    saga = _party_saga(place)
    opening = tombs.overcome_trap(saga, place, 0, random.Random(3))
    assert isinstance(opening, Form)
    first = opening.apply(_values(opening, who="gregor", with_corvinus=True))
    assert isinstance(first, Form)
    second = first.apply(_values(first, roll="Qik + Athletics", adjust=-90))
    assert isinstance(second, Form)
    last = second.apply(_values(second, fast_cast=True, spell_saved=True))
    assert isinstance(last, Form) and last.title.startswith("It Acts")
    assert "Corvinus is helped, or out of its reach" not in [
        f.label for f in last.fields()
    ]


def test_one_who_is_helped_does_not_suffer_it():
    assert et.suffering(["Gregor", "Viktor"], {"Viktor"}) == ["Gregor"]
    place = _tomb()
    saga = _saga(place)
    gregor = saga.character("gregor")
    assert gregor is not None
    spring = tombs.Springing(
        saga,
        place,
        tombs._trap_obstacle(tombs.traps(place)[0]),
        [gregor],
        random.Random(1),
        [tombs.Acted(gregor, "Gregor fails.", False)],
    )
    form = tombs.it_acts(spring)
    form.apply(_values(form, spared_gregor=True))
    assert "Nobody suffered Drop." in tombs.place_events.diary(place)[-1]["text"]


class _Rolls(random.Random):
    """A generator whose die always shows `face` (a stress die's 1 rolls
    again; 0 may botch)."""

    def __init__(self, face: int) -> None:
        super().__init__(0)
        self.face = face

    def randint(self, a: int, b: int) -> int:
        return self.face


def test_a_spotted_trap_can_be_dealt_with_unsprung():
    """p. 44: seen first, there is time; dealing with it stops it springing."""
    place = _tomb()
    place.details["tomb_traps"][0]["spot"] = 6
    saga = _saga(place)
    saga.character("gregor").characteristics.perception = 3
    opening = tombs.overcome_trap(saga, place, 0, _Rolls(9))
    assert isinstance(opening, Form)
    seen = opening.apply(
        _values(opening, who="gregor", look=True, light="Perfect light")
    )
    assert isinstance(seen, Form) and seen.title.startswith("Spotted")
    assert seen.live is not None
    assert "against 3: spots it" in seen.live({})
    seen.apply({"then": tombs.DEAL})
    assert tombs.traps(place)[0]["sprung"] is True


def test_nobody_spotting_it_goes_straight_to_the_actions():
    place = _tomb()
    saga = _saga(place)
    opening = tombs.overcome_trap(saga, place, 0, _Rolls(2))
    assert isinstance(opening, Form)
    step = opening.apply(
        _values(opening, who="gregor", look=True, light="Near darkness")
    )
    assert isinstance(step, Form) and step.title.startswith("Gregor Acts")
    assert step.live is not None
    assert "sees nothing" in step.live(_values(step))


def test_a_sprung_trap_is_reset_before_it_springs_again():
    place = _tomb()
    saga = _saga(place)
    trap = tombs.traps(place)[0]
    trap["sprung"] = True
    assert "sprung" in tombs.traps_grid(saga, place).rows[0][2]
    step = tombs.overcome_trap(saga, place, 0)
    assert isinstance(step, Confirm)
    step.apply()
    assert "sprung" not in trap
    trap.update(sprung=True, once=True)
    assert isinstance(tombs.overcome_trap(saga, place, 0), Refuse)


def test_a_trap_that_resets_itself_is_offered_as_reset():
    place = _tomb()
    saga = _saga(place)
    gregor = saga.character("gregor")
    trap = tombs.traps(place)[0]
    trap["resets"] = True
    spring = tombs.Springing(
        saga, place, tombs._trap_obstacle(trap), [gregor], random.Random(1)
    )
    fields = {f.key: f for f in tombs.it_acts(spring).fields()}
    assert fields["left"].value == tombs.RESET
    trap.pop("resets")
    trap["once"] = True
    fields = {f.key: f for f in tombs.it_acts(spring).fields()}
    assert [value for _label, value in fields["left"].options] == [tombs.SPRUNG]


def test_a_talisman_or_ward_is_overcome_like_a_trap():
    """pp. 35, 42: its Ease Factor, and Magic Resistance passes it."""
    place = _tomb()
    saga = _saga(place)
    opening = tombs.overcome_ward(saga, place, 1, random.Random(1))
    assert isinstance(opening, Form)
    assert "look" not in {f.key for f in opening.fields()}
    action = opening.apply(_values(opening, who="gregor"))
    assert isinstance(action, Form)
    last = action.apply(_values(action, resistance=0))
    assert isinstance(last, Form)
    assert not [f for f in last.fields() if f.key.startswith("spared_")]
    last.apply(_values(last))
    written = tombs.place_events.diary(place)[-1]["text"]
    assert "passes untouched" in written and "Nobody suffered Turn." in written


def test_an_enchantment_in_nobodys_way_has_no_ease_factor():
    place = _tomb()
    place.details["tomb_wards"].append(
        {"name": "Face", "kind": et.NO_OBSTACLE, "art": "CrIm", "level": 15}
    )
    saga = _saga(place)
    assert tombs.ward_ease(tombs.wards(place)[-1]) is None
    assert tombs.wards_grid(saga, place).rows[-1][3] == "no roll, 6 BP"
    assert tombs.spent(place)["talismans and wards"] == 34
    assert isinstance(tombs.overcome_ward(saga, place, 2), Refuse)


def test_a_printed_ease_factor_stands_beside_the_rule():
    """Arrakkamani's ward, p. 92: level 57 prints 24, not 9 + 12."""
    ward: tombs.TombWard = {"name": "S", "kind": et.WARD, "level": 57}
    assert tombs.ward_ease(ward) == 21
    assert tombs.ward_ease({**ward, "ease": 24}) == 24


def test_a_trap_treated_as_several_pays_for_each_harm():
    """p. 46: the pit, 9 + 6 at Ease Factor 12; p. 92: the darts, three
    minor injuries at Ease Factor 6."""
    assert et.trap_build_points("serious", 12, 6) == 21
    assert et.trap_build_points("minor", 6, 12) == 19
    assert tombs.trap_points({"name": "P", "harm": "serious", "ease": 12}) == 15
    assert (
        tombs.trap_points({"name": "P", "harm": "serious", "ease": 12, "further_bp": 6})
        == 21
    )


def test_a_roll_may_take_off_encumbrance():
    gregor = Character(id="g", name="Gregor", type="grog")
    gregor.characteristics.quickness = 2
    value, words = tombs.roll_score(gregor, "Qik + Athletics - Encumbrance")
    assert value == 2 and words.endswith("- Encumbrance 0")
    assert tombs.roll_problem("Qik + Athletics - Encumbrance") is None
    assert tombs.roll_problem("") is None
    assert tombs.roll_problem("Qik + Athletics - Wounds") is not None
    assert tombs.roll_problem("Luck + Dice") is not None


def test_a_place_of_examples_has_no_budget_and_is_not_offered():
    place = _tomb()
    place.details["tomb_kind"] = et.EXAMPLES.key
    saga = _saga(place)
    assert "too many" not in tombs.tomb_text(saga, place)
    assert [f.label for f in tombs.tomb_facts(saga, place)] == ["Kind", "Build Points"]
    assert et.EXAMPLES.key not in et.KINDS


def test_the_places_own_aura_shows_when_boons_raise_it():
    place = _tomb()
    place.details["aura"] = 6
    facts = {f.label: f.value for f in tombs.tomb_facts(_saga(place), place)}
    assert facts["Magic aura"] == "6 (base 4; raised by Boons or its site)"


# -- the book's records in the packs --


@pytest.fixture(scope="module")
def nile() -> Saga:
    return nile_pack.assemble().saga


def _place(saga: Saga, name: str) -> Neighbour:
    return next(n for n in saga.neighbours if n.name == name)


@pytest.mark.parametrize(
    ("name", "kind", "spent"),
    [
        # p. 46: its fear curse by the rule, 10, not the printed 6.
        (
            "The Tomb of Queen Cleopatra",
            "major_monarch",
            {
                "curses": 42,
                "talismans and wards": 76,
                "traps": 45,
                "other resources": 325,
            },
        ),
        # p. 92: 259 overall, so its enchantments are 50, not the printed 52.
        (
            "The Pyramid of Arrakkamani",
            "major_monarch",
            {
                "curses": 18,
                "talismans and wards": 50,
                "traps": 55,
                "other resources": 136,
            },
        ),
    ],
)
def test_the_books_tombs_add_up_as_printed(nile, name, kind, spent):
    place = _place(nile, name)
    assert tombs.is_tomb(place) and place.details["tomb_kind"] == kind
    assert tombs.spent(place) == spent


def test_the_pyramids_records_cost_what_the_book_prints(nile):
    place = _place(nile, "The Pyramid of Arrakkamani")
    assert [tombs.trap_points(t) for t in tombs.traps(place)] == [15, 6, 19, 15]
    assert [tombs.ward_points(w) for w in tombs.wards(place)] == [10, 16, 24]
    assert [tombs.ward_ease(w) for w in tombs.wards(place)] == [11, 14, 24]


def test_the_book_prints_each_examples_cost_and_ease_factor(nile):
    traps = {
        t["name"]: tombs.trap_points(t)
        for t in tombs.traps(_place(nile, "Traps of the Tombs"))
    }
    assert traps == {
        "Labyrinth": 4,
        "Prison Room": 7,
        "Rock Fall": 9,
        "Medicinal Powders": 12,
        "Head Wires": 15,
        "Head Wires behind a Pit": 21,
        "Dead Drop": 18,
    }
    talismans = tombs.wards(_place(nile, "Talismans of the Tombs"))
    assert [(tombs.ward_ease(w), tombs.ward_points(w)) for w in talismans] == [
        (14, 16),
        (10, 8),
        (None, 6),
        (12, 12),
    ]
    wards = tombs.wards(_place(nile, "Wards of the Tombs"))
    assert [tombs.ward_ease(w) for w in wards] == [17, 15, 19]
    curses = tombs.curses(_place(nile, "Curses of the Tombs"))
    assert [c["name"] for c in curses][-1] == "The Hollow Promise of a Swift Death"
    assert [tombs.curse_points(c) for c in curses] == [
        18,
        10,
        18,
        14,
        14,
        10,
        10,
        22,
        4,
    ]


def test_the_cleopatra_pit_is_spotted_at_three_more_than_it_is_avoided(nile):
    pit = tombs.traps(_place(nile, "The Tomb of Queen Cleopatra"))[1]
    assert (pit["ease"], pit["spot"]) == (12, 15)


def test_the_guilds_name_is_as_the_errata_has_it(nile):
    """Errata p. 87."""
    assert any("Al-Matalibeen" in n.name for n in nile.neighbours)
    assert not any("Al-Majalibeen" in n.name for n in nile.neighbours)


def test_the_builder_refuses_a_record_the_rules_cant_cost():
    place = Neighbour(id="p", name="P", kind="place")
    with pytest.raises(ValueError, match="P, Bad"):
        Builder.tomb(place, traps=[tombs.TombTrap(name="Bad", harm="no", ease=3)])
    with pytest.raises(ValueError, match="P, Weak"):
        Builder.tomb(
            place, curses=[tombs.TombCurse(name="Weak", kind=et.GREATER, level=5)]
        )


def test_tin_hinans_tomb_is_marked_and_holds_only_what_the_book_prints():
    place = _place(africa_pack.assemble().saga, "The Tomb of Tin Hinan")
    assert tombs.is_tomb(place)
    assert not tombs.traps(place) and not tombs.curses(place)
    assert tombs.spent_total(place) == 0


def test_overcome_it_needs_a_trap():
    place = _tomb()
    assert isinstance(tombs.overcome_trap(_saga(place), place, 9), Refuse)


def test_a_roll_of_a_characteristic_alone():
    gregor = Character(id="g", name="Gregor", type="grog")
    gregor.characteristics.stamina = 2
    assert tombs.roll_score(gregor, "Sta") == (2, "Stamina 2")
    with pytest.raises(ValueError):
        tombs.roll_score(gregor, "Luck + Dice")
