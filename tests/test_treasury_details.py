"""The Treasury's contested marks, craft lines, deficit options and the
year's purchases."""

from ars_magica_manager import economics as eco
from ars_magica_manager import goods
from ars_magica_manager.covenants import contested_now, settle_resource
from ars_magica_manager.forms import covenant as cov_forms
from ars_magica_manager.models import (
    PURCHASE_GOODS,
    Covenant,
    Economics,
    GoodDef,
    IncomeSource,
    Possession,
    Purchase,
    Saga,
)
from ars_magica_manager.sheets import covenant as cvs


def _saga() -> tuple[Saga, Covenant]:
    covenant = Covenant("cov1", "s1", "Fengheld", year_founded=1100)
    saga = Saga("s1", "Test", current_year=1220, covenants=[covenant])
    return saga, covenant


def test_an_unsettled_source_is_marked_struck_and_gives_nothing():
    saga, covenant = _saga()
    covenant.economics.income_sources = [
        IncomeSource("s", "Rents", income=40, contested=True)
    ]
    account = cvs.treasury(saga, covenant)
    assert account.income == 0
    assert account.groups[0].table.rows[0][1:5] == [
        cvs.CONTESTED_MARK,
        "Typical",
        "[s]40[/]",
        "[b $text-error]0[/]",
    ]
    assert "Settling Rents would bring £40" in account.settling


def test_settling_secures_five_years_and_lifts_the_mark():
    saga, covenant = _saga()
    source = IncomeSource("s", "Rents", income=40, contested=True)
    covenant.economics.income_sources = [source]
    settle_resource(source, 1220)
    assert source.secured_until == 1224
    account = cvs.treasury(saga, covenant)
    assert account.income == 40
    row = account.groups[0].table.rows[0]
    assert row[1] == "" and row[3] == "40"
    assert "Secured through 1224" in row[5]
    assert account.settling == ""
    assert contested_now(source, 1225)


def test_the_settle_form_writes_the_diary():
    saga, covenant = _saga()
    source = IncomeSource("s", "Rents", contested=True)
    form = cov_forms.settle_form(saga, covenant, source)
    form.apply({"year": 1221, "story": "The baron paid"})
    assert source.secured_until == 1225
    entry = covenant.diary[-1]
    assert entry.name == "Rents settled"
    assert "The baron paid" in entry.details


def test_an_unsettled_vis_source_is_marked_in_its_table():
    saga, covenant = _saga()
    covenant.possessions = [
        Possession(
            "v",
            "vis_source",
            "Silk",
            art="Vim",
            pawns=4,
            season="Autumn",
            contested=True,
        )
    ]
    group = next(
        g for g in cvs.possession_groups(saga, covenant) if g.kind == "vis_source"
    )
    assert group.table.rows[0][0] == "Silk"
    assert group.table.rows[0][1] == cvs.CONTESTED_MARK
    assert "[s]4[/]" in group.table.rows[0]
    assert group.table.columns[-1] == "Standing"


def test_purchases_go_onto_sundry_then_the_diary():
    saga, covenant = _saga()
    economics = covenant.economics
    economics.purchases = [Purchase("p", "A warhorse", 16.0, "Animals", "Summer")]
    summary = eco.summarize(saga, covenant)
    assert next(r for r in summary.expenditure if r.key == "sundry").first == 17
    eco.close_year(saga, covenant)
    assert economics.purchases == []
    assert economics.sundry == 1
    entry = covenant.diary[-1]
    assert (entry.year, entry.season, entry.category, entry.pounds) == (
        1220,
        "Summer",
        "Purchases & Sales",
        -16.0,
    )


def test_purchases_survive_a_save():
    economics = Economics(purchases=[Purchase("p", "Hay", 0.5, "Other", "Spring")])
    data = {"purchases": [vars(economics.purchases[0])]}
    assert Economics.from_dict(data).purchases == economics.purchases


def test_the_purchases_table_ends_with_the_pound_of_enumerus():
    saga, covenant = _saga()
    covenant.economics.purchases = [Purchase("p", "Hay", 0.5, "Other", "Spring")]
    table = cvs.treasury(saga, covenant).purchases.table
    assert table.rows[-1][1] == cvs.ENUMERUS
    assert table.key(0) == 0 and table.key(1) is None


def test_buying_a_good_prices_it_by_quality_and_quantity():
    saga, covenant = _saga()
    good = GoodDef("g", "Salt", prices=("10", "20", "40", "#"))
    assert goods.buying_prices(good) == [
        ("Shoddy", 10.0),
        ("Standard", 20.0),
        ("Superior", 40.0),
    ]
    choose = cov_forms.buy_from_goods(saga, covenant)
    form = choose.apply(good)
    form.apply({"quality": "Superior", "quantity": 2.0})
    bought = covenant.economics.purchases[-1]
    assert (bought.pounds, bought.kind, bought.good_id) == (80.0, PURCHASE_GOODS, "g")


def test_a_common_good_is_priced_from_its_pence():
    good = GoodDef("g", "Wagon", kind="common", sold_by="each", pence=(20.0, 20.0))
    assert dict(goods.buying_prices(good))["Standard"] == 20 / 240


def test_ways_out_show_only_when_wealth_cannot_cover_the_deficit():
    saga, covenant = _saga()
    covenant.economics.tithes = 10
    account = cvs.treasury(saga, covenant)
    assert [row[0] for row in account.ways_out.rows][-2:] == [
        "Let covenfolk go",
        "Neglect a whole category",
    ]
    covenant.economics.wealth = 100
    assert cvs.treasury(saga, covenant).ways_out.rows == []
