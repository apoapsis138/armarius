"""Against the Dark's creatures and character options: the vampires'
build by the book and the kukudhi as a player character (pp. 114-121),
the dragon-born Magic Kin (p. 108), and the crowned Slavic, Magyar and
Vlach kings' free Shapeshifter and the varcolac (p. 122)."""

import pytest

from ars_magica_manager import catalog
from ars_magica_manager import choice_templates as ct
from ars_magica_manager.forms import choice_templates as choice_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Creature,
    CreaturePower,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation
from ars_magica_manager.rules import creation_virtues as cv
from ars_magica_manager.rules import transylvania as tr
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.sheets import creature as creature_sheet

VFS = catalog.load_virtue_flaw_catalog_by_id()


def _vf(vf_id: str, **params: str) -> VirtueFlawInstance:
    return VirtueFlawInstance(vf_id, params)


def _vampire(name: str = "Moroi of Brasov", **changes) -> Creature:
    """The book's Human-like Vampire (p. 118), as the Bestiary has it."""
    creature = Creature(
        id="c1",
        name=name,
        realm="Faerie",
        might=15,
        might_form="Corpus",
        virtues_flaws=[
            _vf("vf_negative_reaction"),
            _vf("vf_feast_of_the_dead"),
            _vf("vf_humanoid_faerie"),
            _vf("vf_increased_faerie_might"),
            _vf("vf_increased_faerie_might"),
            _vf("vf_lesser_power", power="Sap the Life"),
            _vf("vf_incognizant"),
            _vf("vf_traditional_ward", ward="sunlight"),
            _vf("vf_traditional_ward", ward="running water"),
        ],
        powers=[CreaturePower("Sap the Life", 2, 1, "Corpus", level=15)],
    )
    for key, value in changes.items():
        setattr(creature, key, value)
    return creature


def test_the_book_lists_have_their_counts_and_name_the_catalog():
    assert len(tr.PRECAUTIONS) == 21
    assert len(tr.LIMITATIONS) == 12
    assert len(tr.DISPATCH) == 8
    assert len(tr.POWERS) == 8
    for vf_id, _ in (*tr.COMMON_VIRTUES, *tr.COMMON_FLAWS, *tr.DRAGON_BORN_VIRTUES):
        assert vf_id in VFS, vf_id
    assert all(vf_id in VFS for vf_id in tr.DRAGON_BORN_FLAWS)
    assert tr.SHAPESHIFTER in VFS


@pytest.mark.parametrize(
    ("days", "haunting", "stage"),
    [
        (0, 7, "zduhacz"),
        (6, 7, "zduhacz"),
        (7, 7, "gadja"),
        (46, 7, "gadja"),
        (47, 7, "platenik"),
        (39, 40, "zduhacz"),
        (79, 40, "gadja"),
        (80, 40, "platenik"),
        (7 * 365 - 1, 7, "platenik"),
        (7 * 365, 7, "kukudhi"),
    ],
)
def test_the_vampires_life(days, haunting, stage):
    assert tr.life_stage(days, haunting_days=haunting) == stage


def test_a_zduhacz_haunts_for_seven_or_forty_days():
    with pytest.raises(ValueError, match="7 or 40"):
        tr.life_stage(3, haunting_days=10)


def test_vampires_are_busiest_from_st_andrews_eve_to_st_georges_eve():
    assert tr.vampires_active(11, 30)
    assert tr.vampires_active(1, 15)
    assert tr.vampires_active(4, 23)
    assert not tr.vampires_active(4, 24)
    assert not tr.vampires_active(11, 29)
    assert not tr.vampires_active(7, 1)


def test_which_creatures_are_vampires():
    assert tr.is_vampire(_vampire())
    assert tr.is_vampire(_vampire("Vampire Tree"))
    # Feast of the Dead and Sap the Life make one whatever its name.
    assert tr.is_vampire(_vampire("The Thing in the Mill"))
    feeder = _vampire("A Hungry Sprite", powers=[])
    feeder.virtues_flaws = [
        vf for vf in feeder.virtues_flaws if "power" not in vf.params
    ]
    assert not tr.is_vampire(feeder)
    # The broukolak is a demon (p. 120).
    assert not tr.is_vampire(_vampire("Broukolak", realm="Infernal"))
    assert tr.is_kukudhi(_vampire("Kukudhi of Laniena"))
    assert not tr.is_kukudhi(_vampire())


def test_a_vampire_by_the_book_has_nothing_missing():
    assert tr.problems(_vampire()) == []
    assert [lim.rule for lim in tr.limitations_of(_vampire())] == [
        "Cannot cross running water"
    ]


def test_a_vampire_without_the_books_musts():
    bare = Creature(
        id="c2",
        name="Vampire",
        realm="Faerie",
        might=5,
        virtues_flaws=[_vf("vf_traditional_ward", ward="fire")],
    )
    found = " ".join(tr.problems(bare))
    assert "Feast of the Dead (p. 116)" in found
    assert "Traditional Ward of sunlight" in found
    assert "Sap the Life" in found
    assert "a physical form, a level of cognizance, a Social Interaction" in found
    assert "None of p. 116's limitations" in found


def test_limitations_come_from_wards_and_restricted_might():
    many = _vampire()
    many.virtues_flaws += [
        _vf("vf_restricted_might_major"),
        _vf("vf_sovereign_ward", ward="those born on a Saturday"),
        _vf("vf_traditional_ward", ward="garlic"),
    ]
    rules = [lim.rule for lim in tr.limitations_of(many)]
    assert rules[:2] == [
        "Cannot spend Might points on a Saturday",
        "Cannot harm anyone born on a Saturday",
    ]
    assert len(rules) == 4
    assert "4 of p. 116's limitations" in " ".join(tr.problems(many))


def test_a_kukudhi_passes_for_human_and_is_not_bound_by_day():
    kukudhi = _vampire("Kukudhi")
    kukudhi.virtues_flaws.append(_vf("vf_traditional_ward", ward="its resting place"))
    found = " ".join(tr.problems(kukudhi))
    assert "lost the vampire's bond to its resting place" in found
    assert "passes for human" in found
    kukudhi.virtues_flaws = [
        vf
        for vf in kukudhi.virtues_flaws
        if vf.vf_id != "vf_negative_reaction"
        and vf.params.get("ward") != "its resting place"
    ] + [_vf("vf_passes_for_human")]
    assert tr.problems(kukudhi) == []
    assert any("dhampirs" in note for note in tr.notes(kukudhi))


def test_a_kukudhi_as_a_player_character():
    saga = Saga(id="s", name="s", current_year=1220)
    kukudhi = _vampire("Kukudhi")
    kukudhi.abilities = [Ability("Brawl", xp=ability_xp(5))]
    # Its points by the catalog's costs, as the sheet counts them.
    points = tr.balance(kukudhi)
    expected_virtues = sum(
        int(VFS[vf.vf_id].cost)
        for vf in kukudhi.virtues_flaws
        if VFS[vf.vf_id].cost > 0
    )
    assert points.virtue_points == expected_virtues
    notes = tr.player_notes(saga, kukudhi)
    # No magi: the book's age of 21 gives 360 Pretense points (RoP:F p. 46).
    assert "360 Pretense points at the magi's age of 21, 75 spent" in notes[1]
    assert "older magi" in notes[2]
    assert tr.player_notes(saga, _vampire()) == []


def test_faerie_player_balance():
    assert tr.FaerieBalance(10, 10).as_companion
    assert not tr.FaerieBalance(11, 11).as_companion
    assert not tr.FaerieBalance(5, 4).as_companion
    assert tr.FaerieBalance(9, 4).as_magus
    assert not tr.FaerieBalance(10, 4).as_magus
    assert tr.FaerieBalance(21, 10).as_magus
    assert not tr.FaerieBalance(23, 11).as_magus


def test_the_magi_age_is_the_played_magis_average():
    saga = Saga(id="s", name="s", current_year=1220)
    a = Character(id="a", name="A", type="magus")
    a.background.year_born = 1190
    b = Character(id="b", name="B", type="magus")
    b.background.year_born = 1180
    b.background.player = "Hedda"
    saga.characters = [a, b]
    assert tr.magi_age(saga) == 40
    b.background.player = ""
    assert tr.magi_age(saga) == 35


def test_the_creature_sheet_shows_the_vampire_facts():
    saga = Saga(id="s", name="s", current_year=1220)
    labels = {f.label: f.value for f in creature_sheet.facts(saga, _vampire("Kukudhi"))}
    assert "passes for human" in labels["Vampire design"]
    assert "obeys cannot cross running water" in labels["As a vampire"]
    assert "Pretense points" in labels["As a player character"]
    plain = {f.label for f in creature_sheet.facts(saga, _vampire())}
    assert "Vampire design" not in plain
    assert "As a player character" not in plain


# -- the dragon-born and the varcolac (choice templates) --


def _chosen(template_id: str, **values: str) -> list[VirtueFlawInstance]:
    template = ct.find(template_id)
    assert template is not None
    return ct.chosen(template, choice_forms.choices_from(template, values))


def test_the_dragon_born_take_the_inherited_virtues():
    chosen = _chosen("ct_dragon_born", status="vf_covenfolk", slot_0_3="vf_avaricious")
    assert chosen == [
        _vf("vf_covenfolk"),
        _vf("vf_greater_immunity", hazard="fire"),
        _vf("vf_personal_power", power="lungs of the fish"),
        _vf("vf_self_confident"),
        _vf("vf_avaricious"),
    ]
    other = _chosen(
        "ct_dragon_born",
        variant="2",
        status="vf_covenfolk",
        slot_2_1="Wings of the Wyrm",
        slot_2_3="vf_lecherous",
    )
    assert _vf("vf_personal_power", power="wings of the wyrm") in other
    template = ct.find("ct_dragon_born")
    assert template is not None
    # Five Virtue points to one Flaw point: more Flaws are needed.
    assert "take another Flaw" in (ct.limit_problem(template, chosen) or "")
    paid = [*chosen, _vf("vf_dark_secret"), _vf("vf_reckless")]
    assert ct.limit_problem(template, paid) is None


@pytest.mark.parametrize(
    ("variant", "ids"),
    [
        ("0", ["vf_shapeshifter"]),
        ("1", ["vf_shapeshifter", "vf_lycanthrope"]),
        ("2", ["vf_skinchanger"]),
        (
            "3",
            ["vf_nightwalker_tradition", "vf_nightwalker", "vf_versatile_phantasticum"],
        ),
    ],
)
def test_the_varcolac_changes_by_birth_by_learning_or_as_a_nightwalker(variant, ids):
    chosen = _chosen("ct_varcolac", variant=variant, status="vf_covenfolk")
    assert [vf.vf_id for vf in chosen[1:]] == ids


def test_the_templates_are_offered_with_against_the_dark():
    saga = Saga(id="s", name="s")
    saga.books_in_play = ["AtD"]
    offered = {t.id for t in ct.templates(saga, "companion")}
    assert {"ct_dragon_born", "ct_varcolac"} <= offered
    assert "Against the Dark" in ct.where(ct.find("ct_dragon_born"))


# -- crowned kings (p. 122) --


def _king(people: str, *, shapeshifter: bool = True) -> Character:
    king = Character(id="k", name="Stefan", type="companion", in_creation=True)
    king.background.church_rank = "King (crowned)"
    king.background.race_nationality = people
    king.virtues_flaws = [_vf("vf_landed_noble")]
    if shapeshifter:
        king.virtues_flaws.append(_vf("vf_shapeshifter"))
    king.virtues_flaws.append(_vf("vf_reckless"))
    return king


def test_a_crowned_slavic_magyar_or_vlach_king_has_shapeshifter_free():
    for people in ("Serbian", "Magyar", "Vlach", "South Slav"):
        assert tr.royal_shapeshifter(_king(people))
    assert not tr.royal_shapeshifter(_king("Frankish"))
    uncrowned = _king("Magyar")
    uncrowned.background.church_rank = ""
    assert not tr.royal_shapeshifter(uncrowned)
    king = _king("Serbian")
    benefit = cv.free_benefit(king)
    assert benefit.free_indices == frozenset({1})
    assert benefit.virtue_points == 3
    assert "his crown" in benefit.giver
    # Shapeshifter's 3 points are outside the balance.
    fewest, most = cv.virtue_allowance(king, 1)
    assert (fewest, most) == (4, 4)
    assert cv.virtue_allowance(_king("Frankish"), 1) == (1, 1)


def test_the_kings_creation_check():
    saga = Saga(id="s", name="s", current_year=1220)
    held = [
        c
        for c in creation.checks(saga, _king("Serbian"), "virtues_flaws")
        if "crowned" in c.label
    ]
    assert held and held[0].status == "pass"
    missing = [
        c
        for c in creation.checks(
            saga, _king("Serbian", shapeshifter=False), "virtues_flaws"
        )
        if "crowned" in c.label
    ]
    assert missing and missing[0].status == "advice"
    assert "a wolf, a lion and a dragon" in missing[0].detail
    assert not [
        c
        for c in creation.checks(saga, _king("Frankish"), "virtues_flaws")
        if "crowned" in c.label
    ]


def test_a_peoples_name_must_start_the_word():
    assert tr.royal_shapeshifter(_king("Russian"))
    assert not tr.royal_shapeshifter(_king("Prussian"))
