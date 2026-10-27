"""A lord's and a covenant's Manors tab: the rules it works out (Lords of
Men pp. 9-12, 30-33, 48, 58-61, 71-87; its errata p. 74; Covenants pp.
56-58)."""

import random

import pytest

from ars_magica_manager import economics as eco
from ars_magica_manager import lords, manors, neighbours
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import neighbour as neighbour_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Covenant,
    IncomeSource,
    Neighbour,
    Saga,
)
from ars_magica_manager.rules import dice
from ars_magica_manager.sections import (
    ESTABLISHMENTS_SECTION,
    HOUSEHOLD_SECTION,
    MANOR_CHECK_SECTION,
    MANORS_SECTION,
)


def _saga() -> Saga:
    marshal = Character(id="ulrich", name="Ulrich", type="grog")
    marshal.characteristics.intelligence = 1
    marshal.abilities = [Ability("Profession: Marshal", "General", 75)]  # 5
    lord = Neighbour(
        id="dieter",
        name="Count Dieter",
        kind="lord",
        ruler="Dieter II",
        answers_to="liege",
    )
    lord.details = {"title": "count", "wealth": "Average", "manors": 3}
    liege = Neighbour(id="liege", name="The Emperor", kind="lord")
    covenant = Covenant(id="cov", name="Dammarstein", saga_id="m")
    covenant.economics.income_sources = [
        IncomeSource(id="rents", name="Rents of the Kohlergrund", type="Lesser"),
        IncomeSource(id="flocks", name="Flocks", type="Lesser", income=10),
    ]
    covenant.economics.wealth = 900
    return Saga(
        id="m",
        name="Manors",
        characters=[marshal],
        neighbours=[lord, liege],
        covenants=[covenant],
        current_year=1220,
        current_season="Winter",
    )


def _lord(saga: Saga) -> Neighbour:
    found = saga.neighbour("dieter")
    assert found is not None
    return found


def _covenant(saga: Saga) -> Covenant:
    found = saga.covenant("cov")
    assert found is not None
    return found


def _form(command: object) -> Form:
    assert isinstance(command, Form)
    return command


# -- the tabs --


def test_a_lord_has_a_manors_tab_after_his_fief_and_a_covenant_has_one_too():
    kind = neighbours.KINDS["lord"]
    assert [t.title for t in kind.more] == ["Manors", "Marriages", "Diary"]
    assert not kind.more[0].after_standing
    tab = manors.LORD_TAB
    assert [p.section_id for p in tab.parts()] == [
        MANORS_SECTION,
        ESTABLISHMENTS_SECTION,
        HOUSEHOLD_SECTION,
    ]
    assert [p.section_id for p in manors.COVENANT_TAB.parts()] == [
        MANOR_CHECK_SECTION,
        MANORS_SECTION,
        ESTABLISHMENTS_SECTION,
    ]


def test_the_lords_and_the_covenants_sections_have_their_verbs():
    saga = _saga()
    ops = neighbour_forms.neighbour_ops(saga, _lord(saga))
    assert ops[MANORS_SECTION].add is not None
    assert ops[ESTABLISHMENTS_SECTION].remove is not None
    assert ops[HOUSEHOLD_SECTION].edit is not None
    held = manors.covenant_ops(saga, _covenant(saga))
    assert set(held) == {MANORS_SECTION, ESTABLISHMENTS_SECTION, MANOR_CHECK_SECTION}


# -- a manor --


def test_a_manor_yields_twenty_pounds_its_mill_and_bakery_inside_it():
    saga = _saga()
    lord = _lord(saga)
    lord.details["manor_list"] = [
        {"name": "Katzenelnbogen", "acres": 640, "mill": True, "bakery": True},
        {"name": "Hohenstein", "acres": 480},
    ]
    assert manors.total_yield(lord) == 40
    assert manors.total_acres(lord) == 1120
    grid = manors.manors_grid(saga, lord)
    assert grid.rows[0][-2:] == ["20 £", "mill, bakery"]
    info = manors.manor_info(saga, lord, 0)
    assert "mill and bakery by custom already inside it" in info
    assert "40 pounds" in manors.manors_header(saga, lord)


def test_a_manor_a_third_off_six_hundred_acres_is_unusual():
    assert not manors.unusual_size(800)
    assert not manors.unusual_size(400)
    assert manors.unusual_size(801)
    assert manors.unusual_size(399)
    assert not manors.unusual_size(None)


def test_peasant_land_spread_and_worth():
    manor: manors.Manor = {
        "name": "M",
        "hides": 1,
        "virgates": 6,
        "bovates": 9,
        "cottars": 15,
    }
    assert manors.spread(manor) == (20, 30, 50)
    assert manors.peasant_worth(manor) == 4 + 6
    assert manors.spread({"name": "Empty"}) is None


def test_the_demesne_flock_by_its_land_is_two_thirds_of_the_sheep():
    assert manors.flock({"name": "M"}) == 600
    assert manors.flock({"name": "M", "terrain": "Marsh"}) == 1000
    assert manors.flock({"name": "M", "terrain": "Wooded"}) == 300
    assert manors.flock({"name": "M", "sheep": 450}) == 450
    assert manors.manor_sheep({"name": "M"}) == 900


def test_crops_are_sown_and_reaped_by_the_acre():
    sown = manors.crops({"name": "M", "winter": 60, "spring": 20})
    assert sown == [("winter", 60, 120, 480), ("spring", 20, 80, 320)]


def test_the_dues_are_ticks_and_notes_not_sums():
    saga = _saga()
    lord = _lord(saga)
    lord.details["manor_list"] = [
        {"name": "M", "due_heriot": True, "court": "Heriot the best copper pan"}
    ]
    info = manors.manor_info(saga, lord, 0)
    assert "Heriot" in info and "Heriot the best copper pan" in info
    assert "pounds" not in info.split("Manor court")[1]


def test_the_manor_form_refuses_more_land_by_use_than_acres():
    problem = manors._manor_problem({"acres": 600, "demesne": 400, "waste": 300})
    assert problem is not None and "700" in problem
    assert manors._manor_problem({"acres": 600, "demesne": 200}) is None
    assert manors._manor_problem({"hides": -1}) is not None


# -- the Fief from the rows --


def test_the_fief_counts_the_manors_rows_or_the_typed_count_without_them():
    saga = _saga()
    lord = _lord(saga)
    assert lords.manors(lord) == 3
    assert lords.manors_text(lord).startswith("3 (as entered")
    lord.details["manor_list"] = [{"name": f"M{i}"} for i in range(5)]
    assert lords.manors(lord) == 5
    assert lords.income(lord) == 100
    facts = {f.label: f.value for f in lords.facts(saga, lord)}
    assert facts["Manors"] == "5 (from his Manors tab)"
    assert facts["Income"].startswith("100 pounds a year")
    assert facts["Surplus"] == "100 pounds a year (LoM p. 32)"
    # Relief: a year's income, at most 5 a manor and 100 for a count.
    assert lords.relief(lord) == 25


@pytest.mark.parametrize(
    ("rank", "wealth", "words"),
    [
        ("landed", "Poor", "none (LoM p. 31)"),
        ("landed", "Average", "10 pounds a year (LoM p. 31)"),
        ("landed", "Wealthy", "20 pounds a year (LoM p. 31)"),
        ("baron", "Wealthy", "100 pounds a year"),
        ("count", "Wealthy", "250 pounds a year (LoM p. 32)"),
        ("duke", "Average", "no figure in the book (LoM p. 32)"),
    ],
)
def test_surplus_is_chapter_threes_own_figure(rank, wealth, words):
    lord = Neighbour(id="l", name="L", kind="lord")
    lord.details = {"title": rank, "wealth": wealth}
    assert lords.surplus_text(lord).startswith(words)


# -- kennels, mews and stables --


def test_the_tables_are_the_books_with_the_errata_excellent_stables():
    excellent = manors.TABLES["Stables"]["Excellent"]
    assert (excellent.capacity, excellent.upkeep, excellent.staff) == (40, 3, 12)
    assert excellent.living == 2 and excellent.per_head
    assert manors.TABLES["Kennels"]["Standard"] == manors.Grade(16, 1, 2, 0)
    assert manors.TABLES["Mews"]["Superior"] == manors.Grade(15, 5, 3, 1)
    assert manors.TABLES["Kennels"]["Royal"].upkeep == 100


def test_a_stable_befitting_its_owner_is_free_kennels_and_mews_always_pay():
    saga = _saga()
    count = _lord(saga)
    stables: manors.Establishment = {
        "kind": "Stables",
        "quality": "Excellent",
        "animals": 26,
    }
    assert manors.upkeep(count, stables) == 0
    count.details["title"] = "landed"
    assert manors.upkeep(count, stables) == 78
    covenant = manors.manors_of(_covenant(saga))
    assert (
        manors.upkeep(
            covenant, {"kind": "Stables", "quality": "Standard", "animals": 6}
        )
        == 0
    )
    assert (
        manors.upkeep(
            covenant, {"kind": "Stables", "quality": "Superior", "animals": 10}
        )
        == 20
    )
    assert manors.upkeep(count, {"kind": "Kennels", "quality": "Standard"}) == 1
    assert manors.upkeep(count, {"kind": "Mews", "quality": "Superior"}) == 5


def test_a_failed_winter_roll_lowers_the_quality_not_the_upkeep():
    saga = _saga()
    lord = _lord(saga)
    lord.details["title"] = "landed"
    entry: manors.Establishment = {
        "kind": "Stables",
        "quality": "Excellent",
        "lowered": 1,
        "animals": 10,
    }
    assert manors.quality_now(entry) == "Superior"
    assert manors.grade(entry).capacity == 18
    assert manors.upkeep(lord, entry) == 30


def test_capacity_takes_a_third_again_of_young_and_breeding_stock():
    entry: manors.Establishment = {"kind": "Kennels", "quality": "Superior"}
    assert manors.most_animals(entry) == 64


def test_superior_and_better_need_a_specialist_with_twice_the_living():
    entry: manors.Establishment = {"kind": "Mews", "quality": "Excellent"}
    assert manors.needs_specialist(entry)
    assert not manors.needs_specialist({"kind": "Mews", "quality": "Standard"})
    assert manors.keeps_living({**entry, "profession": 3}) is False
    assert manors.keeps_living({**entry, "profession": 4}) is True
    assert manors.keeps_living({"kind": "Mews", "quality": "Standard"}) is None


def test_unpaid_upkeep_drops_a_class_at_once_and_only_once():
    saga = _saga()
    lord = _lord(saga)
    ops = manors.estab_ops(saga, lord)
    assert ops.add is not None and ops.edit is not None
    _form(ops.add()).apply({"kind": "Mews", "quality": "Superior", "unpaid": True})
    entry = manors.establishments(lord)[0]
    assert entry["quality"] == "Standard"
    _form(ops.edit(0)).apply({"kind": "Mews", "quality": "Standard", "unpaid": True})
    assert entry["quality"] == "Standard"


def test_an_unpaid_season_loses_fifteen_percent_rounded_up():
    assert manors.season_loss(7) == 2
    assert manors.season_loss(20) == 3
    saga = _saga()
    lord = _lord(saga)
    lord.details["establishments"] = [
        {"kind": "Mews", "quality": "Superior", "animals": 7, "unpaid": True},
        {"kind": "Stables", "quality": "Standard", "animals": 6},
    ]
    _covenant(saga).manors["establishments"] = [
        {"kind": "Kennels", "quality": "Standard", "animals": 16, "unpaid": True}
    ]
    lines = manors.season_losses(saga)
    assert [line.result for line in lines] == [
        "Lost 2 of 7 birds (LoM p. 59).",
        "Lost 3 of 16 hounds (LoM p. 59).",
    ]
    assert lines[1].covenant_id == "cov"
    assert manors.establishments(lord)[0]["animals"] == 5
    assert manors.establishments(lord)[1]["animals"] == 6


def _die(value: int, botch: bool = False) -> dice.DieResult:
    if botch:
        return dice.DieResult(value=0, faces=(0,), botch_faces=(0,))
    return dice.DieResult(value=value, faces=(value,))


@pytest.mark.parametrize(
    ("value", "botch", "lowered", "after", "said"),
    [
        (3, False, 1, 0, "back to Excellent"),
        (2, False, 0, 1, "down to Superior"),
        (0, True, 0, 1, "catastrophe"),
    ],
)
def test_the_winter_roll_is_intelligence_and_profession_against_nine(
    monkeypatch, value, botch, lowered, after, said
):
    saga = _saga()
    lord = _lord(saga)
    lord.details["establishments"] = [
        {"kind": "Stables", "quality": "Excellent", "lowered": lowered}
    ]
    monkeypatch.setattr(dice, "stress_die", lambda *_a, **_k: _die(value, botch))
    form = _form(manors.winter_roll(saga, lord, 0, random.Random(1)))
    assert form.live is not None
    assert "Stress die + [b]6[/]" in form.live({"who": "ulrich"})
    result = form.apply({"who": "ulrich", "ability": "profession"})
    entry = manors.establishments(lord)[0]
    assert entry.get("lowered") == after
    assert any(said in line for line in result)
    assert "Ulrich" in entry["roll"]
    assert isinstance(manors.winter_roll(saga, lord, 4), Refuse)


def test_the_winter_roll_without_a_sheet_uses_the_specialists_figures():
    saga = _saga()
    entry: manors.Establishment = {
        "kind": "Kennels",
        "specialist": "Jutta",
        "intelligence": 2,
        "profession": 4,
    }
    terms = manors.husbandry(saga, entry, {"intelligence": 2, "score": 4})
    assert (terms.who, terms.ability, terms.total) == (
        "Jutta",
        "Profession: Master of Kennels",
        6,
    )
    handling = manors.husbandry(saga, entry, {"ability": "handling"})
    assert handling.ability == "Animal Handling"


# -- the household --


def test_the_household_shows_the_relief_owed_his_liege():
    saga = _saga()
    lord = _lord(saga)
    manors.household(lord).update(
        {"retinue": 28, "mesnie": "6 knights", "custom": "Primogeniture"}
    )
    facts = {f.label: f.value for f in manors.household_facts(saga, lord)}
    assert facts["Retinue"] == "28: 6 knights"
    assert facts["Inheritance"].endswith("relief 15 pounds to The Emperor")


def test_settling_an_inheritance_makes_the_heir_the_ruler():
    saga = _saga()
    lord = _lord(saga)
    manors.household(lord)["heirs"] = "Dieter (14), then Berthold (11)"
    form = _form(manors.settle_form(saga, lord))
    heir = next(f for f in form.fields() if f.key == "heir")
    assert heir.value == "Dieter"
    lines = form.apply(
        {
            "heir": "Dieter III",
            "custom": "Divided among sons",
            "share": 3,
            "widow": True,
        }
    )
    assert lord.ruler == "Dieter III"
    text = " ".join(lines)
    assert "divided between 3 heirs, about 1 each" in text
    assert "relief of 15 pounds" in text
    assert "the profit (not the income) of a third of his land" in text
    assert lord.details["diary"][-1]["text"].startswith("Dieter III inherits")


# -- Buy a Manor and Assart --


def test_buying_a_manor_costs_thirty_to_fifty_times_its_income():
    saga = _saga()
    lord = _lord(saga)
    form = _form(manors.buy_form(saga, lord))
    assert form.live is not None
    assert "40 times" in form.live({"price": 800})
    assert "Outside" in form.live({"price": 1200})
    assert form.validate is not None and form.validate({"price": 0})
    form.apply({"name": "Hagen", "acres": 600, "price": 800})
    assert manors.manor_list(lord)[-1]["name"] == "Hagen"
    assert "Hagen for 800 pounds" in lord.details["diary"][-1]["text"]


def test_a_covenant_pays_for_a_manor_from_its_wealth():
    saga = _saga()
    covenant = _covenant(saga)
    holder = manors.manors_of(covenant)
    form = _form(manors.buy_form(saga, holder))
    assert form.validate is not None
    assert form.validate({"price": 1000, "pay": True}) is not None
    form.apply({"name": "Ebersbach", "price": 700, "pay": True})
    assert covenant.economics.wealth == 200
    assert covenant.manors["manor_list"][0]["name"] == "Ebersbach"


def test_assarting_clears_an_acre_a_laborer_a_month_from_the_waste():
    saga = _saga()
    lord = _lord(saga)
    lord.details["manor_list"] = [{"name": "M", "waste": 60, "demesne": 200}]
    form = _form(manors.assart_form(saga, lord, 0))
    assert form.validate is not None
    assert form.validate({"laborers": 10, "months": 7}) is not None
    form.apply({"laborers": 4, "months": 6, "into": "demesne"})
    manor = manors.manor_list(lord)[0]
    assert (manor["waste"], manor["demesne"]) == (36, 224)
    assert manors.cleared({"laborers": 4, "months": 6, "acres": 2}) == 2
    assert isinstance(manors.assart_form(saga, lord, 3), Refuse)


# -- a covenant's manors beside its income --


def test_a_covenants_manors_are_a_check_beside_its_source_never_added():
    saga = _saga()
    covenant = _covenant(saga)
    holder = manors.manors_of(covenant)
    before = eco.summarize(saga, covenant).income
    assert "Choose the source" in manors.check_text(saga, holder)
    covenant.manors["manor_list"] = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
    _form(manors.edit_check(saga, holder)).apply(
        {"agriculture_source": "rents", "livestock_source": None}
    )
    text = manors.check_text(saga, holder)
    assert "3 x 20 = [b]60 pounds[/]" in text
    assert "20 pounds above the source this year" in text
    assert eco.summarize(saga, covenant).income == before


def test_sheep_manors_check_against_the_livestock_source():
    saga = _saga()
    covenant = _covenant(saga)
    holder = manors.manors_of(covenant)
    covenant.manors.update(
        {
            "manor_list": [{"name": "A"}, {"name": "B", "farming": "Sheep"}],
            "agriculture_source": "rents",
            "livestock_source": "flocks",
        }
    )
    text = manors.check_text(saga, holder)
    assert "Agriculture source" in text and "Livestock source" in text
    assert "1 x 20 = [b]20 pounds[/]" in text
    assert "20 pounds below the source" in text
    assert "10 pounds above" in text


def test_a_covenant_without_manors_loads_and_keeps_them_round_trip():
    old = Covenant.from_dict({"id": "c", "saga_id": "m", "name": "Old"})
    assert old.manors == {}
    held = Covenant.from_dict(
        {
            "id": "c",
            "saga_id": "m",
            "name": "New",
            "manors": {"manor_list": [{"name": "A"}]},
        }
    )
    assert held.manors["manor_list"] == [{"name": "A"}]
    with pytest.raises(ValueError, match="manors"):
        Covenant.from_dict({"id": "c", "saga_id": "m", "name": "Bad", "manors": [1]})
