"""The Grogs Aging Chart: the chart's arithmetic (rules/grog_aging.py),
applying it to a grog (aging_chart.py), the worksheet's button and form,
and the Ability cap it moves."""

from __future__ import annotations

import random

import pytest

from ars_magica_manager import aging_chart
from ars_magica_manager import worksheet as ws
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import worksheet as wf
from ars_magica_manager.models import (
    AnimalForm,
    Character,
    Covenant,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation_access as access
from ars_magica_manager.rules import grog_aging as rules


def _grog(age: int = 45, **kw) -> Character:
    grog = Character(
        id="g1", name="Paul", type="grog", covenant_id="cov1", in_creation=True, **kw
    )
    grog.background.year_born = 1220 - age
    return grog


def _saga(grog: Character, books: list[str] | None = None) -> Saga:
    return Saga(
        id="s",
        name="Saga",
        covenants=[Covenant(id="cov1", saga_id="s", name="Keep")],
        characters=[grog],
        books_in_play=books,
    )


def _decades(character: Character, end: int, kind: rules.Kind, living: int = 0):
    return rules.decades(
        35, end, lambda age: rules.aging_score(character, age, living), kind
    )


# -- the chart --


def test_the_chart_reads_its_rows_and_clamps_off_the_chart():
    assert rules.chart(5, "average") == (5, 1)
    assert rules.chart(9, "mild") == (7, 1)
    assert rules.chart(10, "harsh") == (12, 2)
    assert rules.chart(14, "harsh") == rules.chart(10, "harsh")
    assert rules.chart(-2, "mild") == rules.chart(1, "mild")


def test_pauls_decade_is_one_decade_at_the_higher_aging_score():
    # Grogs' example: 45, Living Conditions 0: 6 years at 4 and 4 at 5,
    # taken as 10 years at 5.
    paul = _grog()
    assert [rules.aging_score(paul, age, 0) for age in (35, 40, 41, 44)] == [4, 4, 5, 5]
    (decade,) = _decades(paul, 45, "average")
    assert (decade.first, decade.last, decade.score) == (35, 44, 5)
    assert rules.total([decade], 0, False).points == 5
    assert rules.total(_decades(paul, 45, "harsh"), 0, False).points == 6


def test_pauls_crises_give_decrepitude_and_a_share_of_the_points():
    paul = _grog()
    average = rules.total(_decades(paul, 45, "average"), 0, True)
    # Decrepitude 1 (5 points) + half of 5, rounded up = 8.
    assert (average.crises, average.decrepitude, average.points) == (1, 1, 8)
    harsh = rules.total(_decades(paul, 45, "harsh"), 0, True)
    # Decrepitude 2 (15 points) + a third of 6 = 17.
    assert (harsh.crises, harsh.decrepitude, harsh.points) == (2, 2, 17)


def test_crises_build_on_the_decrepitude_already_there():
    paul = _grog()
    found = _decades(paul, 45, "average")
    # 7 points is Decrepitude 1: one crisis takes it to 2 (15 points).
    sum_up = rules.total(found, 7, True)
    assert (sum_up.decrepitude, sum_up.crisis_points, sum_up.chart_points) == (2, 8, 3)


def test_a_part_decade_takes_its_share_rounded_up():
    # 60: 25 rolls, two whole decades and 5 years at score 6 (55-59).
    found = _decades(_grog(60), 60, "average")
    assert [(d.first, d.last, d.score, d.points, d.crises) for d in found] == [
        (35, 44, 5, 5, 1),
        (45, 54, 6, 6, 1),
        (55, 59, 6, 3, 1),
    ]
    assert rules.total(found, 0, False).points == 14
    # Three crises: Decrepitude 3 (30) + 14 / 4 rounded up.
    assert rules.total(found, 0, True).points == 34


def test_living_conditions_and_mild_aging_lower_the_score():
    mild = _grog(virtues_flaws=[VirtueFlawInstance("vf_mild_aging")])
    assert rules.aging_score(mild, 45, 1) == 3
    assert rules.kinds_allowed(mild) == ("mild",)
    poor = _grog(virtues_flaws=[VirtueFlawInstance("vf_poor_living_conditions")])
    assert rules.aging_score(poor, 45, 0) == 6
    assert rules.kinds_allowed(poor) == ("harsh",)
    assert rules.kinds_allowed(_grog()) == rules.KINDS


@pytest.mark.parametrize(
    ("points", "expected"),
    [
        (1, [1, 0, 0, 0, 0]),
        (5, [2, 1, 1, 1, 0]),
        (8, [4, 2, 1, 1, 0]),
        (12, [6, 3, 2, 1, 0]),
    ],
)
def test_the_chart_points_fall_as_the_aging_table_spreads_them(points, expected):
    assert [n for _, _, n in rules.shares(points)] == expected


def test_one_more_point_never_takes_one_from_another_group():
    for points in range(40):
        before = [n for _, _, n in rules.shares(points)]
        after = [n for _, _, n in rules.shares(points + 1)]
        assert all(b <= a for b, a in zip(before, after, strict=True))


def test_points_are_placed_and_characteristics_fall():
    scores = dict.fromkeys(rules.aging.CHARACTERISTICS, 0)
    scores["strength"] = 2
    placed = rules.placements(5, 0, scores)
    # Pairs first, the first named first, then "any" on the highest.
    assert placed == ["quickness", "perception", "strength", "any", "any"]
    points: dict[str, int] = {}
    applied = rules.place_points(placed, scores, points, unaging=False)
    assert applied.gained == {"quickness": 1, "perception": 1, "strength": 3}
    assert scores["quickness"] == -1 and scores["perception"] == -1
    # Strength 2 takes three points: the third is past 2, so it falls to 1.
    assert scores["strength"] == 1 and points["strength"] == 0
    assert "Strength falls to +1." in applied.notes


def test_apparent_age_moves_the_whole_decade_at_or_under_the_points():
    (decade,) = _decades(_grog(), 45, "average")
    assert rules.apparent_years(decade, 5) == 10
    assert rules.apparent_years(decade, 7) == 7
    short = rules.Decade(35, 39, 4, 2, 1)
    assert rules.apparent_years(short, 8) == 4


# -- applying it to a grog --


def test_the_chart_is_offered_to_an_older_grog_while_grogs_is_in_play():
    assert aging_chart.offered(_saga(_grog()), _grog())
    assert not aging_chart.offered(_saga(_grog(), books=[]), _grog())
    assert aging_chart.offered(_saga(_grog(), books=["Grogs"]), _grog())
    assert not aging_chart.offered(_saga(_grog(35)), _grog(35))
    companion = _grog()
    companion.type = "companion"
    assert not aging_chart.offered(_saga(companion), companion)
    horse = _grog()
    horse.animal = AnimalForm(kind="hoofed", species="Horse", language="Horse")
    assert not aging_chart.offered(_saga(horse), horse)


def _finish_labels(saga: Saga, grog: Character) -> list[str]:
    return [a.label for a in ws.PANELS[("character", "finish")].actions(saga, grog)]


def test_finishing_touches_offers_the_chart_beside_the_roll():
    grog = _grog()
    labels = _finish_labels(_saga(grog), grog)
    assert labels.index("Use the Grogs Aging Chart") == (
        labels.index("Roll pre-play aging") + 1
    )
    assert "Use the Grogs Aging Chart" not in _finish_labels(_saga(grog, []), grog)


def test_applying_the_chart_ages_the_grog_and_notes_the_choice():
    grog = _grog()
    saga = _saga(grog)
    notes = aging_chart.apply(saga, grog, "harsh", False, True, random.Random(3))
    aging = grog.aging
    assert sum(aging.aging_points.values()) <= 6
    assert aging.decrepitude_points == 6 and aging.decrepitude == 1
    c = grog.characteristics
    assert sum(getattr(c, n) for n in rules.aging.CHARACTERISTICS) < 0
    assert grog.creation_conditions.aged_to == 44
    assert grog.creation_conditions.aging_chart == "harsh"
    assert grog.creation_conditions.aging_chart_cap == 1
    assert aging.apparent_age is not None and 35 <= aging.apparent_age <= 44
    (entry,) = grog.diary
    assert entry.year == 1219 and entry.season == "Winter"
    assert "the Grogs Aging Chart (harsh): 6 Aging Point(s)" in entry.name
    assert "Ability cap 1 higher at creation." in notes
    assert not aging_chart.offered(saga, grog)
    assert aging_chart.worksheet_text(grog) == (
        "the Grogs Aging Chart, harsh aging (Ability cap 1 higher)"
    )


def test_the_chart_with_crises_gives_decrepitude():
    grog = _grog()
    aging_chart.apply(_saga(grog), grog, "average", True, False, random.Random(1))
    assert grog.aging.decrepitude_points == 8 and grog.aging.decrepitude == 1
    assert grog.creation_conditions.aging_chart_cap == 0


def test_harsh_aging_raises_the_ability_cap_and_mild_lowers_it():
    grog = _grog()
    assert access.ability_cap_for(grog, 45, "Brawl") == 8
    grog.creation_conditions.aging_chart_cap = 1
    assert access.ability_cap_for(grog, 45, "Brawl") == 9
    assert access.character_ability_cap(grog, 45) == 9
    grog.creation_conditions.aging_chart_cap = -1
    assert access.ability_cap_for(grog, 45, "Brawl") == 7


# -- the form --


def test_the_form_asks_the_kind_crises_and_cap():
    grog = _grog()
    form = wf.grog_aging_chart(_saga(grog), grog)
    assert isinstance(form, Form)
    fields = {f.key: f for f in form.fields()}
    assert fields["kind"].value == "average"
    assert [v for _, v in fields["kind"].options] == ["mild", "average", "harsh"]
    assert fields["crises"].value is False
    show_if = fields["move_cap"].show_if
    assert show_if is not None
    assert not show_if({"kind": "average"}) and show_if({"kind": "harsh"})
    assert form.live is not None
    assert "Ages 35-44 (10 years) at Aging Score 5: 5 Aging Point(s), 1 crisis." in (
        form.live({"kind": "average", "crises": False})
    )
    assert "Total: 8 Aging Point(s)" in form.live({"kind": "average", "crises": True})


def test_the_form_has_its_help_topic_in_both_front_ends():
    from ars_magica_manager import help_text as ht

    grog = _grog()
    form = wf.grog_aging_chart(_saga(grog), grog)
    assert isinstance(form, Form)
    for front_end in (ht.TUI, ht.GUI):
        assert ht.load(front_end).topic(form.help_id) is not None


def test_the_form_offers_only_the_kind_a_virtue_requires():
    grog = _grog(virtues_flaws=[VirtueFlawInstance("vf_mild_aging")])
    fields = {f.key: f for f in wf.grog_aging_chart_fields(grog)}
    assert fields["kind"].value == "mild"
    assert fields["kind"].options == [("Mild", "mild")]


def test_the_form_refuses_when_nothing_is_due():
    grog = _grog(30)
    assert isinstance(wf.grog_aging_chart(_saga(grog), grog), Refuse)
