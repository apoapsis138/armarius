import re
from dataclasses import asdict

import pytest
from support import strip_markup

from ars_magica_manager import economics as eco
from ars_magica_manager import inhabitants as inh
from ars_magica_manager.models import (
    INCOME_TYPE_DEFAULTS,
    INCOME_TYPES,
    Ability,
    Background,
    Character,
    Covenant,
    Economics,
    IncomeSource,
    Inhabitant,
    LabCharacteristics,
    Laboratory,
    Possession,
    Saga,
    VirtueFlawInstance,
)


def _saga(season: str = "Spring") -> tuple[Saga, Covenant]:
    covenant = Covenant(id="cov1", saga_id="s", name="Dammerstein")
    covenant.covenant_season = season
    saga = Saga(
        id="s",
        name="Saga",
        current_year=1220,
        covenants=[covenant],
        characters=[
            Character(
                id="mag1",
                name="Corvinus",
                type="magus",
                covenant_id="cov1",
                background=Background(year_born=1195),
            ),
            Character(id="comp1", name="Alys", type="companion", covenant_id="cov1"),
            Character(
                id="grog1",
                name="Old Thomae",
                type="grog",
                covenant_id="cov1",
                abilities=[Ability(name="Craft: Smith", level=5)],
            ),
        ],
        laboratories=[],
    )
    return saga, covenant


def _row(rows: list[eco.Row], key: str) -> eco.Row:
    return next(r for r in rows if r.key == key)


# ---------------------------------------------------------------- the rules


@pytest.mark.parametrize(
    ("score", "points"),
    [
        (-6, 1),
        (-5, 1),
        (-1, 7),
        (0, 10),
        (1, 15),
        (2, 30),
        (5, 150),
        (6, 210),
        (15, 1200),
    ],
)
def test_upkeep_points_follow_the_book(score, points):
    assert eco.upkeep_points(score) == points


def test_summarize_uses_inhabitants_points_formula():
    """inhabitant_points() itself is covered in test_inhabitants.py (it moved
    there so the minimum Servants/Teamsters formulas could use it too); this
    just checks summarize() picks it up correctly."""
    saga, cov = _saga("Summer")
    cov.inhabitants = [Inhabitant(id="t", kind="turb", name="Turb", quantity=2)]
    assert eco.summarize(saga, cov).inhabitant_points == inh.inhabitant_points(
        saga, cov
    )


def test_laboratory_points_use_the_labs_upkeep_and_the_sanctums_usage():
    saga, cov = _saga()
    saga.laboratories = [
        Laboratory(
            id="lab1",
            covenant_id="cov1",
            name="Crucible",
            characteristics=LabCharacteristics(upkeep=2),
        ),
        Laboratory(id="lab2", covenant_id="cov1", name="Second"),  # Upkeep 0
        Laboratory(
            id="lab3",
            covenant_id="cov2",
            name="Not Ours",
            characteristics=LabCharacteristics(upkeep=5),
        ),
    ]
    # Crucible 30, Second 10, both Standard usage by default.
    assert eco.laboratory_points(saga, cov) == 40
    cov.possessions = [
        Possession(id="s1", kind="sanctum", lab_id="lab1", usage="Heavy (3+ Seasons)"),
        Possession(
            id="s2", kind="sanctum", lab_id="lab2", usage="Light (1 Season or Less)"
        ),
    ]
    # 30 * 1.5 + 10 * 0.5 = 50, a whole number already.
    assert eco.laboratory_points(saga, cov) == 50


def test_a_manual_sanctum_uses_its_own_upkeep_as_a_score_blank_counting_as_zero():
    saga, cov = _saga()
    cov.possessions = [
        Possession(id="a", kind="sanctum", name="Hidden Study", upkeep=1),
        Possession(id="b", kind="sanctum", name="Unmeasured"),
    ]
    assert eco.laboratory_points(saga, cov) == 15 + 10


def test_weapon_and_armor_points_come_from_type_quality_and_quantity():
    saga, cov = _saga()
    cov.possessions = [
        Possession(
            id="a",
            kind="weapon",
            name="Spears",
            quantity=10,
            gear_type="Weapon or shield",
            gear_quality="Standard",
        ),  # 40
        Possession(
            id="b",
            kind="armor",
            name="Mail",
            quantity=2,
            gear_type="Full armor",
            gear_quality="Expensive",
        ),  # 128
        Possession(
            id="c",
            kind="weapon",
            name="Trebuchet",
            gear_type="Heavy catapult or trebuchet",
            gear_quality="Expensive",
        ),  # 32
        Possession(id="d", kind="weapon", name="Old, unsorted"),  # not set: 0
        Possession(id="e", kind="item", name="Lens", quantity=5),  # not gear
    ]
    from ars_magica_manager import possessions as pos

    assert pos.gear_points(saga, cov) == 40 + 128 + 32


# --------------------------------------------------------------- expenditure


def _sized_covenant() -> tuple[Saga, Covenant]:
    """100 points of inhabitants (turb x100 in Spring), 40 of laboratories, 320
    of weapons: round numbers so every cost is easy to check by hand."""
    saga, cov = _saga()
    saga.characters = []
    cov.inhabitants = [Inhabitant(id="t", kind="turb", name="Turb", quantity=100)]
    cov.possessions = [
        Possession(id="s", kind="sanctum", name="Lab", upkeep=3),  # 60 -> x1
        Possession(
            id="s2",
            kind="sanctum",
            name="Lab 2",
            upkeep=-3,
            usage="Light (1 Season or Less)",
        ),
        Possession(
            id="w",
            kind="weapon",
            name="Swords",
            quantity=80,
            gear_type="Weapon or shield",
            gear_quality="Standard",
        ),  # 320
    ]
    return saga, cov


def test_each_expenditure_category_follows_its_rule():
    saga, cov = _sized_covenant()
    # Sanctums: upkeep 3 = 60 points; upkeep -3 = 3 points x0.5 = 1.5 -> 61.5,
    # rounded up to 62.
    summary = eco.summarize(saga, cov)
    assert summary.inhabitant_points == 100
    assert summary.laboratory_points == 62
    assert summary.gear_points == 320
    cost = {r.key: r.first for r in summary.expenditure}
    assert cost["buildings"] == 10
    assert cost["consumables"] == 20
    assert cost["provisions"] == 50
    assert cost["wages"] == 20
    assert cost["laboratories"] == 7  # 62 / 10 = 6.2, rounded up
    assert cost["weapons"] == 1
    assert cost["writing"] == 0  # no magi in this covenant
    assert cost["sundry"] == 1  # at least 1 pound of sundries every year
    assert summary.before_savings == 10 + 20 + 50 + 20 + 7 + 1 + 0 + 1
    assert summary.cost_savings == 0
    assert summary.total_expenditure == summary.before_savings


def test_building_boons_add_to_the_buildings_expense_and_stack():
    saga, cov = _sized_covenant()  # Buildings is 10 without any Boons
    cov.boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_shell_keep"),  # +2
        VirtueFlawInstance(vf_id="covbh_boon_major_curtain_walls_and_mural_towers"),
        VirtueFlawInstance(vf_id="covbh_boon_minor_important_building"),  # +2
        VirtueFlawInstance(vf_id="covbh_boon_minor_important_building"),  # +2 again
        VirtueFlawInstance(vf_id="covbh_boon_minor_aura"),  # not a building Boon
    ]
    row = _row(eco.summarize(saga, cov).expenditure, "buildings")
    assert row.first == 10 + 2 + 5 + 2 + 2
    assert row.basis == (
        "100 pts of inhabitants / 10 + Shell Keep +2, "
        "Curtain Walls and Mural Towers +5, Important Building +2, "
        "Important Building +2"
    )


def test_wages_follow_the_salary_in_loyalty():
    saga, cov = _sized_covenant()
    for money, multiplier in (
        ("No salary", 0),
        ("Half salary", 0.5),
        ("Standard salary", 1),
        ("Generous salary", 1.5),
        ("Lavish salary", 2),
    ):
        cov.loyalty.money = money
        wages = _row(eco.summarize(saga, cov).expenditure, "wages")
        assert wages.first == 20 * multiplier
    assert wages.note == "x2"


def test_writing_materials_cost_one_pound_per_magus_and_book_craftsperson():
    saga, cov = _saga()  # one magus
    cov.inhabitants = [
        Inhabitant(id="a", kind="craftsperson", name="Binder", field_of_work="Books"),
        Inhabitant(
            id="b", kind="craftsperson", name="Illuminator", field_of_work="Books"
        ),
        Inhabitant(
            id="c", kind="craftsperson", name="Smith", field_of_work="Consumables"
        ),
    ]
    assert _row(eco.summarize(saga, cov).expenditure, "writing").first == 3


def test_tithes_inflation_and_sundry_are_typed_and_included():
    saga, cov = _sized_covenant()
    base = eco.summarize(saga, cov).before_savings
    cov.economics.tithes = 3
    cov.economics.inflation = 2
    cov.economics.sundry = 5  # was 1 (the minimum default): +4, not +5
    summary = eco.summarize(saga, cov)
    assert summary.before_savings == base + 9
    assert _row(summary.expenditure, "tithes").typed == ("tithes",)


def test_sundry_defaults_to_one():
    # The minimum is enforced by the edit dialog (screens.py), not here.
    assert Economics().sundry == 1


# ------------------------------------------------------------------ savings


def test_laborers_save_a_pound_each_up_to_half_of_provisions():
    saga, cov = _sized_covenant()  # Provisions 50 -> limit 25
    cov.inhabitants.append(
        Inhabitant(
            id="lb", kind="inhabitant", name="Laborers", quantity=10, role="Laborer"
        )
    )
    summary = eco.summarize(saga, cov)
    assert _row(summary.savings, "laborers").savings == 10
    assert _row(summary.expenditure, "provisions").savings == 10
    # Laborers are inhabitants too (one point each), so provisions move; recompute.
    cov.inhabitants[-1].quantity = 60
    summary = eco.summarize(saga, cov)
    provisions = _row(summary.expenditure, "provisions")
    assert _row(summary.savings, "laborers").savings == provisions.first / 2


def test_common_and_rare_craftspeople_save_by_ability_within_the_craft_limit():
    saga, cov = _sized_covenant()  # Consumables 20 -> 20% per craft = 4
    cov.inhabitants += [
        # Common, Ability 5: 1 + 2 = 3 pounds.
        Inhabitant(
            id="a",
            kind="craftsperson",
            name="Thomae",
            field_of_work="Consumables",
            skill_value=5,
            responsibility="Blacksmith",
        ),
        # A rare craft saves its Ability outright: Provisions limit 20% of 50 = 10.
        Inhabitant(
            id="b",
            kind="craftsperson",
            name="Brewer",
            field_of_work="Provisions",
            skill_value=4,
            rare=True,
            responsibility="Brewer",
        ),
    ]
    summary = eco.summarize(saga, cov)
    # +4 points of inhabitants (2 craftspeople x 2 points) change the costs.
    consumables = _row(summary.expenditure, "consumables")
    assert consumables.savings == 3 < 0.2 * consumables.first
    assert _row(summary.expenditure, "provisions").savings == 4
    craft = _row(summary.savings, "craftspeople")
    assert craft.first == 2 and craft.savings == 7


def test_one_craft_cannot_save_more_than_its_limit_but_two_crafts_can():
    saga, cov = _sized_covenant()
    smiths = [
        Inhabitant(
            id=f"s{i}",
            kind="craftsperson",
            name=f"Smith {i}",
            field_of_work="Consumables",
            skill_value=10,
            responsibility="Blacksmith",
        )
        for i in range(4)
    ]  # 4 x (1 + 5) = 24, far over the limit
    cov.inhabitants += smiths
    summary = eco.summarize(saga, cov)
    cost = _row(summary.expenditure, "consumables")
    assert cost.first == 22 and cost.savings == 5  # capped at ~20% of 21.6, rounded up

    cov.inhabitants.append(
        Inhabitant(
            id="w",
            kind="craftsperson",
            name="Weaver",
            field_of_work="Consumables",
            skill_value=10,
            responsibility="Weaver",
        )
    )
    cost = _row(eco.summarize(saga, cov).expenditure, "consumables")
    assert cost.first == 22 and cost.savings == 9  # two crafts, each capped


def test_books_and_no_field_save_nothing_and_a_linked_ability_sets_the_score():
    saga, cov = _saga()
    cov.inhabitants = [
        Inhabitant(id="t", kind="turb", name="Turb", quantity=100),  # sizeable costs
        Inhabitant(id="a", kind="craftsperson", name="Binder", field_of_work="Books"),
        Inhabitant(id="b", kind="craftsperson", name="Idle", field_of_work="None"),
        Inhabitant(
            id="c",
            kind="craftsperson",
            name="Old Thomae",
            character_id="grog1",
            field_of_work="Consumables",
            linked_ability="Craft: Smith",
            skill_value=1,  # typed, but the sheet's Ability (5) wins
        ),
    ]
    craft = _row(eco.summarize(saga, cov).savings, "craftspeople")
    assert craft.first == 1  # only the one with a field that saves
    assert craft.savings == 3  # 1 + 5 // 2, well under the 20% limit


def test_magic_and_emergency_savings_are_typed_and_only_reduce_the_total():
    saga, cov = _sized_covenant()
    cov.economics.magic_savings = 4
    cov.economics.emergency_savings = 7
    summary = eco.summarize(saga, cov)
    assert _row(summary.savings, "magic").savings == 4
    assert _row(summary.savings, "emergency_savings").savings == 7
    assert summary.cost_savings == 11
    assert summary.total_expenditure == summary.before_savings - 11
    assert all(r.savings == 0 for r in summary.expenditure)


def test_cost_savings_rows_match_the_books_four_categories():
    """No "Specialists" row -- that was never a real Cost Saving category
    (the book only has Laborers, Craftspeople, Magic and Emergency Savings;
    Specialists is a Loyalty bonus, not an Economics saving)."""
    saga, cov = _sized_covenant()
    assert [r.key for r in eco.summarize(saga, cov).savings] == [
        "laborers",
        "craftspeople",
        "magic",
        "emergency_savings",
    ]


def test_savings_never_exceed_a_categorys_cost():
    saga, cov = _saga()
    cov.inhabitants = [
        Inhabitant(id="a", kind="turb", name="Guard", quantity=10),
        *(
            Inhabitant(
                id=f"c{i}",
                kind="craftsperson",
                name=f"C{i}",
                field_of_work="Building",
                skill_value=20,
                rare=True,
                responsibility=f"craft {i}",
            )
            for i in range(9)
        ),
    ]
    row = _row(eco.summarize(saga, cov).expenditure, "buildings")
    assert row.savings <= row.first


# ------------------------------------------------------------------ income


def test_an_income_sources_income_follows_its_type_until_typed_over():
    for type_ in INCOME_TYPES:
        assert (
            IncomeSource(id="x", name="n", type=type_).current_income
            == (INCOME_TYPE_DEFAULTS[type_])
        )
    assert INCOME_TYPE_DEFAULTS == {
        "None": 0,
        "Lesser": 40,
        "Typical": 100,
        "Greater": 250,
        "Legendary": 1000,
    }
    typed = IncomeSource(id="x", name="Mine", type="Typical", income=130)
    assert typed.current_income == 130
    with pytest.raises(ValueError):
        IncomeSource(id="x", name="n", type="Huge")


def test_total_income_and_wealth_texts():
    saga, cov = _sized_covenant()
    cov.economics.income_sources = [
        IncomeSource(id="a", name="Salt Mine", type="Typical"),
        IncomeSource(id="b", name="Toll", type="Lesser", income=55),
    ]
    cov.economics.wealth = 12
    summary = eco.summarize(saga, cov)
    assert summary.income == 155 and summary.wealth == 12
    left, right = (strip_markup(t) for t in eco.wealth_texts(summary))
    assert re.search(r"Points of Inhabitants:\s+100\b", left)
    assert re.search(r"Points of Weapons and Armor:\s+320\b", left)
    assert re.search(r"Wealth:\s+12\b", left)
    assert re.search(r"Total Income:\s+155\b", right)
    assert "Expenditure (Before Cost Savings)" in right
    assert "Cost Savings" in right and "Total Expenditure" in right
    assert summary.surplus_deficit == summary.income - summary.total_expenditure
    signed = re.escape(f"{summary.surplus_deficit:+d}")
    assert re.search(rf"Surplus/Deficit:\s+{signed}\b", right)


def test_surplus_deficit_is_colored_cyan_when_positive_red_when_negative():
    saga, cov = _sized_covenant()  # a fair bit of expenditure, no income yet
    deficit_summary = eco.summarize(saga, cov)
    assert deficit_summary.surplus_deficit < 0
    _, deficit_right = eco.wealth_texts(deficit_summary)
    assert f"[red]{deficit_summary.surplus_deficit:+d}[/]" in deficit_right

    cov.economics.income_sources = [IncomeSource(id="a", name="Mine", type="Legendary")]
    surplus_summary = eco.summarize(saga, cov)
    assert surplus_summary.surplus_deficit > 0
    _, surplus_right = eco.wealth_texts(surplus_summary)
    assert f"[cyan]{surplus_summary.surplus_deficit:+d}[/]" in surplus_right


def test_surplus_deficit_of_exactly_zero_is_colored_cyan():
    saga, cov = _sized_covenant()
    summary = eco.summarize(saga, cov)
    cov.economics.income_sources = [
        IncomeSource(
            id="a", name="Mine", type="Typical", income=summary.total_expenditure
        )
    ]
    even_summary = eco.summarize(saga, cov)
    assert even_summary.surplus_deficit == 0
    _, right = eco.wealth_texts(even_summary)
    assert "[cyan]+0[/]" in right


def test_source_text_shows_where_the_income_comes_from_and_renders_emphasis():
    usual = IncomeSource(id="a", name="[Mine]", type="Greater")
    assert eco.source_row_label(usual) == "\\[Mine]              Greater        250"
    assert "(the usual for Greater)" in eco.source_detail_text(usual)
    typed = IncomeSource(
        id="b", name="Toll", type="Lesser", income=55, description="Paid **in kind**."
    )
    text = eco.source_detail_text(typed)
    assert "55 (typed; Lesser is usually 40)" in text
    assert "[b]in kind[/b]" in text or "in kind" in text
    assert "Select a source" in eco.source_detail_text(None)


def test_source_row_and_panel_show_the_note():
    plain = IncomeSource(id="a", name="Mine", type="Typical")
    assert eco.source_row_label(plain) == "Mine                Typical        100"
    assert "Note" not in eco.source_detail_text(plain)

    noted = IncomeSource(
        id="b",
        name="[Toll] bridge",
        type="Typical",
        note="1220 - Toll experienced Boom",
        description="A busy crossing.",
    )
    label = eco.source_row_label(noted)
    assert label == (
        "\\[Toll] bridge       Typical        100  1220 - Toll experienced Boom"
    )
    text = eco.source_detail_text(noted)
    # The Note comes before the Description.
    assert text.index("Note:") < text.index("Description:")
    assert "1220 - Toll experienced Boom" in text
    assert "A busy crossing." in text


# ------------------------------------------------------------- improvement


def test_income_multiplier_text_matches_the_income_modification_table():
    assert eco.income_multiplier_text("Slump") == "x0.5"
    assert eco.income_multiplier_text("Contraction") == "x0.8"
    assert eco.income_multiplier_text("Stagnation") == "x0.95"
    assert eco.income_multiplier_text("Status Quo") == "x1"
    assert eco.income_multiplier_text("Growth") == "x1.05"
    assert eco.income_multiplier_text("Expansion") == "x1.2"
    assert eco.income_multiplier_text("Boom") == "x1.5"


def test_projected_income_applies_the_multiplier_and_rounds():
    assert eco.projected_income(100, "Status Quo") == 100
    assert eco.projected_income(100, "Boom") == 150
    assert eco.projected_income(100, "Slump") == 50
    assert eco.projected_income(41, "Stagnation") == 39  # 38.95 -> rounded up
    assert eco.projected_income(41, "Growth") == 44  # 43.05 -> rounded up


def test_improvement_note_follows_the_two_templates():
    grown = eco.improvement_note(1220, "Salt Mine", "Boom", 100, 150)
    assert grown == (
        "1220 - Salt Mine experienced Boom changing Income from 100 to 150."
    )
    steady = eco.improvement_note(1220, "Salt Mine", "Status Quo", 100, 100)
    assert steady == (
        "1220 - Salt Mine experienced no growth or setbacks. Status Quo maintained."
    )
    # An unnamed source still reads sensibly.
    assert eco.improvement_note(1220, "", "Growth", 100, 105).startswith(
        "1220 - This source of income experienced Growth"
    )


def test_table_rows_line_up_and_truncate_long_notes():
    saga, cov = _sized_covenant()
    cov.economics.notes["buildings"] = "x" * 100
    summary = eco.summarize(saga, cov)
    label = strip_markup(eco.row_label(_row(summary.expenditure, "buildings")))
    assert label.startswith("Buildings") and label.endswith("…")
    assert len(label) < 80
    header = eco.table_header("Cost")
    assert header.index("Cost") + len("Cost") == 2 + 20 + 8  # right edge of the column
    assert "Savings" in header and header.endswith("Notes")


# ------------------------------------------------------------ persistence


def test_economics_round_trips_through_dicts():
    economics = Economics(
        income_sources=[IncomeSource(id="a", name="Mine", type="Greater", income=300)],
        wealth=5,
        tithes=1,
        magic_savings=2,
        emergency_savings=3,
        notes={"buildings": "Roof"},
    )
    covenant = Covenant(id="c", saga_id="s", name="N", economics=economics)
    loaded = Covenant.from_dict(asdict(covenant))
    assert loaded.economics == economics


def test_a_stale_specialists_field_from_before_this_session_is_dropped():
    data = asdict(Covenant(id="c", saga_id="s", name="N"))
    data["economics"]["specialists_quantity"] = 2
    data["economics"]["specialists_savings"] = 7
    data["economics"]["magic_items_quantity"] = 4
    loaded = Covenant.from_dict(data)
    assert loaded.economics == Economics()


def test_a_covenant_saved_before_economics_existed_loads_with_defaults():
    data = asdict(Covenant(id="c", saga_id="s", name="N"))
    data.pop("economics")
    data["population"].pop("other_people")
    loaded = Covenant.from_dict(data)
    assert loaded.economics == Economics()
    assert loaded.population.other_people == 0


def _with_deficit(deficit: int, wealth: int) -> tuple[Saga, Covenant]:
    """A covenant running a `deficit`-pound deficit (Tithes set to make it)."""
    saga, cov = _sized_covenant()
    # Enough income for a surplus before Tithes, so Tithes can make the deficit.
    cov.economics.income_sources = [
        IncomeSource(id="i", name="Mine", type="Typical", income=500)
    ]
    cov.economics.tithes = 0
    surplus = eco.summarize(saga, cov).surplus_deficit
    cov.economics.tithes = surplus + deficit
    cov.economics.wealth = wealth
    assert eco.summarize(saga, cov).surplus_deficit == -deficit
    return saga, cov


def test_emergency_savings_warns_of_a_deficit_and_of_being_broke():
    saga, cov = _with_deficit(36, wealth=100)
    row = _row(eco.summarize(saga, cov).savings, "emergency_savings")
    assert row.status == "Covenant operating at a deficit"
    assert "[red]Covenant operating at a deficit[/]" in eco.row_label(row)
    assert "Covenant operating at a deficit" in strip_markup(
        eco.row_detail_text(row, "Q")
    )

    cov.economics.wealth = 35  # one short of the deficit
    row = _row(eco.summarize(saga, cov).savings, "emergency_savings")
    assert row.status == (
        "Covenant is broke - see rulebook for narrative and mechanical consequences"
    )

    cov.economics.tithes = 0  # no deficit: no warning
    assert _row(eco.summarize(saga, cov).savings, "emergency_savings").status == ""


def test_drawing_from_wealth_covers_the_deficit():
    saga, cov = _with_deficit(36, wealth=100)
    draw = eco.emergency_draw(eco.summarize(saga, cov))
    assert draw == 36
    eco.draw_from_wealth(cov, draw)
    assert (cov.economics.emergency_savings, cov.economics.wealth) == (36, 64)
    summary = eco.summarize(saga, cov)
    assert summary.surplus_deficit == 0
    assert _row(summary.savings, "emergency_savings").status == ""
    assert eco.emergency_draw(summary) == 0  # nothing left to cover


def test_drawing_takes_all_the_wealth_when_it_falls_short():
    saga, cov = _with_deficit(36, wealth=10)
    draw = eco.emergency_draw(eco.summarize(saga, cov))
    assert draw == 10
    eco.draw_from_wealth(cov, draw)
    assert (cov.economics.emergency_savings, cov.economics.wealth) == (10, 0)
    summary = eco.summarize(saga, cov)
    assert summary.surplus_deficit == -26
    assert _row(summary.savings, "emergency_savings").status.startswith(
        "Covenant is broke"
    )
    assert eco.emergency_draw(summary) == 0  # no Wealth left


def test_the_year_end_adds_the_surplus_to_wealth_and_resets_emergency_savings():
    saga, cov = _sized_covenant()
    cov.economics.income_sources = [
        IncomeSource(id="i", name="Mine", type="Typical", income=200)
    ]
    cov.economics.wealth = 5
    cov.economics.emergency_savings = 7
    surplus = eco.summarize(saga, cov).surplus_deficit
    assert surplus > 0
    assert eco.close_year(saga, cov) == surplus
    assert cov.economics.wealth == 5 + surplus
    assert cov.economics.emergency_savings == 0

    # A deficit doesn't take from Wealth by itself: that's the draw's job.
    saga, cov = _with_deficit(20, wealth=50)
    assert eco.close_year(saga, cov) == 0
    assert cov.economics.wealth == 50


def test_add_income_source_gives_it_a_unique_id():
    _, cov = _saga()
    first = eco.add_income_source(cov, {"name": "Mill", "type": "Typical", "income": 5})
    second = eco.add_income_source(
        cov, {"name": "Mill", "type": "Typical", "income": 5}
    )
    assert (first.id, second.id) == ("mill", "mill_2")
    assert cov.economics.income_sources[-2:] == [first, second]


def test_apply_row_edit_sets_figures_and_keeps_or_drops_the_note():
    _, cov = _saga()
    economics = cov.economics
    eco.apply_row_edit(economics, "tithes", {"tithes": 7, "notes": "To Durenmar"})
    assert economics.tithes == 7 and economics.notes["tithes"] == "To Durenmar"
    eco.apply_row_edit(economics, "tithes", {"tithes": 7, "notes": ""})
    assert "tithes" not in economics.notes


def test_covenants_in_deficit_and_closing_every_year():
    saga, cov = _with_deficit(36, wealth=100)
    other = Covenant(id="cov2", saga_id=saga.id, name="Prosperous")
    other.economics.income_sources = [
        IncomeSource(id="i", name="Mine", type="Typical", income=500)
    ]
    saga.covenants.append(other)
    other_surplus = eco.summarize(saga, other).surplus_deficit
    assert other_surplus > 0
    assert eco.covenants_in_deficit(saga) == [(cov.name, -36)]
    # A deficit adds nothing to Wealth; a surplus is added (see close_year).
    assert eco.close_all_years(saga) == [(cov.name, 0), (other.name, other_surplus)]
    assert cov.economics.wealth == 100


def test_row_problem_requires_at_least_one_pound_of_sundries():
    assert eco.row_problem("sundry", {"sundry": 0})
    assert eco.row_problem("sundry", {"sundry": 1}) is None
    assert eco.row_problem("tithes", {"tithes": 0}) is None
