"""The Covenfolk chapter's ledgers: Loyalty's figures and meaning, the
situational modifiers, staffing and the household."""

from ars_magica_manager import covenfolk_ledger as ledger
from ars_magica_manager import economics as eco
from ars_magica_manager.models import Covenant, Inhabitant, Saga
from ars_magica_manager.sheets import covenant as cvs


def _saga() -> tuple[Saga, Covenant]:
    covenant = Covenant("cov1", "s1", "Fengheld", year_founded=1219)
    saga = Saga("s1", "Test", current_year=1220, covenants=[covenant])
    return saga, covenant


def test_a_score_reads_the_sample_score_nearest_zero():
    assert ledger.meaning_band(3) == 2
    assert ledger.meaning_band(-3) == -2
    assert ledger.meaning_band(9) == 6
    assert "revolt" in ledger.meaning(-7)


def test_points_to_the_next_score_follow_the_ability_table():
    assert ledger.points_to_next(21, 2) == 9  # +3 at 30
    assert ledger.points_to_next(-18, -2) == 4  # -1 above -15
    assert ledger.points_to_next(0, 0) == 5


def test_the_four_figures_add_up():
    saga, covenant = _saga()
    base, modifiers, points, score = ledger.figures(saga, covenant)
    assert int(points.value) == int(base.value) + int(modifiers.value)
    assert score.caption == "Prevailing"


def test_money_lists_each_salary_and_its_wages():
    saga, covenant = _saga()
    money = next(
        ln for ln in ledger.modifier_lines(saga, covenant) if ln.name == "Money"
    )
    assert "[b]Standard salary  +0[/]" in money.detail
    assert "Lavish salary: Wages x2" in money.detail


def test_staffing_reads_met_shortfall_or_excess_in_words():
    assert ledger.standing(3, 3) == "[dim]Met[/]"
    assert "Shortfall of 2" in ledger.standing(4, 6)
    assert ledger.standing(5, 4) == "Excess of 1"


def test_a_short_staff_line_says_what_goes_wrong():
    saga, covenant = _saga()
    covenant.inhabitants.append(
        Inhabitant(id="t", kind="turb", name="Turb", quantity=17)
    )
    servants = next(
        ln for ln in ledger.staffing_lines(saga, covenant) if ln.name == "Servants"
    )
    assert "Shortfall of" in servants.cells[2]
    assert "DE p. 196" in servants.detail


def test_the_household_ends_with_its_total_and_costs_a_pound_a_point():
    saga, covenant = _saga()
    covenant.inhabitants.append(
        Inhabitant(id="t", kind="turb", name="Turb", quantity=4)
    )
    lines = ledger.household_lines(saga, covenant)
    assert lines[-1].name == "Total"
    assert lines[-1].cells[1] == str(eco.summarize(saga, covenant).inhabitant_points)
    turb = next(ln for ln in lines if ln.name.startswith("Turb"))
    assert turb.cells == ("4", "4", "£4")


def test_a_capped_craftsperson_shows_the_cap():
    saga, covenant = _saga()
    covenant.inhabitants = [
        Inhabitant(id="t", kind="turb", name="Turb", quantity=20),
        Inhabitant(
            id="s",
            kind="craftsperson",
            name="Smith",
            field_of_work="Consumables",
            skill_value=10,
            responsibility="Blacksmith",
        ),
    ]
    group = next(
        g for g in cvs.inhabitant_groups(saga, covenant) if g.kind == "craftsperson"
    )
    saves = group.table.columns.index("Saves")
    assert group.table.rows[0][saves].endswith("(cap)")
