"""The Goods catalog's rules: City & Guild's Prices of Goods table
(pp. 141-142) and Price List (p. 144) as data, the errata's ton (p. 57),
and Saga Content's Goods tab's core (forms/goods.py)."""

from dataclasses import asdict

import pytest

from ars_magica_manager import actions, catalog
from ars_magica_manager import goods as gd
from ars_magica_manager import saga_content as sc
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.forms import goods as gf
from ars_magica_manager.models import COMMODITY, COMMON, GoodDef, Saga
from ars_magica_manager.sections import GOODS_SECTION

#: Every row of the Prices of Goods table, as printed (C&G pp. 141-142):
#: Shoddy, Standard, Superior, Expensive; "" where the book is blank.
PRINTED = {
    "Alum": ("*", "200", "400", "#"),
    "Brassware": ("150", "300", "600", "1500"),
    "Copper": ("*", "*", "*", "200"),
    "Cotton Cloth": ("100", "200", "400", "10,000"),
    "Cotton, Raw": ("40", "50", "100", "250"),
    "Dye": ("10", "50", "", "20,000"),
    "Fuel": ("1", "2", "3", "n/a"),
    "Fish": ("50", "75", "100", "#"),
    "Flax": ("20", "45", "90", "250"),
    "Fur and Hides": ("1", "50", "100", "250"),
    "Foodstuffs": ("1", "10", "20", "50"),
    "Gemstones": ("2,000 (fake)", "10,000", "80,000", "100,000"),
    "Glassware": ("#", "1,500", "2,000", "2,500"),
    "Gold": ("*", "*", "*", "24,200"),
    "Grain": ("1", "5", "10", "25"),
    "Hemp Cloth": ("45", "60", "100", "#"),
    "Hemp, Raw": ("15", "20", "25", "#"),
    "Horses": ("2", "4", "8", "64"),
    "Ink": ("10", "25", "50", "10,000"),
    "Iron": ("*", "*", "*", "120"),
    "Ironware and Weapons": ("125", "250", "500", "2,500"),
    "Lead": ("*", "*", "*", "60"),
    "Leather": ("150", "250", "500", "2,500"),
    "Linen Cloth": ("125", "175", "350", "1,750"),
    "Oil": ("2", "10", "20", "100"),
    "Paper": ("75", "150", "300", "#"),
    "Pearls": ("5 (fake)", "80,000", "120,000", "n/a"),
    "Pewterware": ("375", "750", "1,500", "#"),
    "Pitch": ("1", "2", "4", "20"),
    "Potash": ("20", "#", "#", "400"),
    "Pottery": ("20", "70", "140", "700"),
    "Saffron": ("*", "*", "*", "25,000"),
    "Salt": ("*", "*", "*", "120"),
    "Silk Cloth": ("12,500", "25,000", "50,000", "#"),
    "Silk, Raw": ("300", "500", "600", "#"),
    "Silver": ("250*", "1,650*", "2,200*", "2,420"),
    "Slaves": ("1", "2", "4", "#"),
    "Soap": ("0.5", "1", "5", "10"),
    "Spices": ("5", "50", "1,500", "2,000"),
    "Tapestries": ("100", "3,000", "6,000", "#"),
    "Timber": ("2.5", "5", "10", "25"),
    "Tin": ("*", "*", "*", "250"),
    "Wax": ("2", "5", "10", "#"),
    "Wine": ("5", "10", "20", "50"),
    "Wool Cloth": ("50", "150", "300", "3,000"),
    "Wool, Raw": ("25", "50", "100", "500"),
}

#: The Price List's standard prices, as printed, and in pence (C&G p. 144;
#: 12 pence a shilling, 240 a pound, p. 143).
COMMON_PRINTED = {
    "Longbow": ("15 shillings", 180),
    "Cart": ("10 pennies", 10),
    "Chainmail, full": ("2 pounds", 480),
    "Chainmail, partial": ("1 pound", 240),
    "Chair": ("8 pennies", 8),
    "Chamber pot": ("20 pennies", 20),
    "Chest with lock": ("2 and 1/2 pounds", 600),
    "Dagger": ("6 pennies", 6),
    "Gallon of ale": ("half a penny", 0.5),
    "Great sword": ("13 shillings", 156),
    "Heavy Leather, full": ("2 and 1/2 shillings", 30),
    "Heavy Leather, partial": ("15 pennies", 15),
    "House, luxurious": ("50 pounds", 12000),
    "House, peasant": ("2 pounds", 480),
    "House, urban": ("5 pounds", 1200),
    "Leather Scale, full": ("10 shillings", 120),
    "Leather Scale, partial": ("5 shillings", 60),
    "Loaf of bread": ("half a penny", 0.5),
    "Long sword": ("10 shillings", 120),
    "Non-Hermetic books": ("11 shillings", 132),
    "Pair of shoes": ("6 – 16 pennies", (6, 16)),
    "Shield, buckler": ("3 shillings", 36),
    "Shield, heater": ("8 shillings", 96),
    "Shield, round": ("8 pennies", 8),
    "Short sword": ("3 shillings", 36),
    "Shovel": ("4 pennies", 4),
    "Tunic, dyed": ("8 shillings", 96),
    "Tunic, fur lined": ("13 shillings", 156),
    "Tunic, peasant": ("16 pennies", 16),
    "Tunic, wool": ("5 shillings", 60),
    "Wagon": ("20 pennies", 20),
}

#: The table's goods marked * (priced by purity).
BY_PURITY = {
    "Alum",
    "Copper",
    "Gold",
    "Iron",
    "Lead",
    "Saffron",
    "Salt",
    "Silver",
    "Tin",
}


def _goods() -> dict[str, GoodDef]:
    return {g.name: g for g in catalog.load_goods_catalog() if g.source}


def _saga() -> Saga:
    saga = Saga(id="goods", name="Goods")
    catalog.use_saga(saga)
    return saga


@pytest.fixture(autouse=True)
def _no_saga_in_use():
    yield
    catalog.use_saga(None)


def _index(saga: Saga, name: str) -> int:
    return next(i for i, g in enumerate(gd.listed(saga)) if g.name == name)


# -- the catalog --


def test_catalog_has_every_good_of_both_lists_in_the_books_order():
    shared = [g for g in catalog.load_goods_catalog() if g.source]
    commodities = [g.name for g in shared if g.kind == COMMODITY]
    common = [g.name for g in shared if g.kind == COMMON]
    assert commodities == list(PRINTED)
    assert common == list(COMMON_PRINTED)
    assert len({g.id for g in shared}) == len(shared) == 46 + 31


def test_every_printed_price_is_present_as_printed():
    goods = _goods()
    wrong = [
        f"{name}: {goods[name].prices} != {prices}"
        for name, prices in PRINTED.items()
        if goods[name].prices != prices
    ]
    assert not wrong, wrong
    for name, (printed, pence) in COMMON_PRINTED.items():
        good = goods[name]
        low, high = pence if isinstance(pence, tuple) else (pence, pence)
        assert good.prices == ("", printed, "", ""), name
        assert good.pence == (low, high), name
        assert good.page == 144 and good.sold_by == "each"


def test_every_commodity_has_a_class_and_a_page():
    goods = _goods()
    for name in PRINTED:
        good = goods[name]
        assert good.commodity_class in gd.CLASSES, name
        assert good.class_page in {"134", "135", "136", "137", "138"}, name
        assert good.page in (141, 142), name
    assert goods["Salt"].commodity_class == "bulk"
    assert goods["Glassware"].commodity_class == "manufactured"
    assert goods["Pearls"].commodity_class == "luxury"


def test_the_starred_goods_are_priced_by_purity():
    goods = _goods()
    assert {n for n, g in goods.items() if gd.by_purity(g)} == BY_PURITY
    assert gd.takes_purities(goods["Iron"])
    assert goods["Iron"].purity is not None
    assert goods["Iron"].purity.pure_price == 120


def test_how_goods_are_sold():
    goods = _goods()
    assert goods["Wine"].sold_by == "tun"
    assert goods["Horses"].sold_by == "head"
    assert "Two horses to the ton" in goods["Horses"].sale
    assert goods["Silk Cloth"].sold_by == "roll"
    assert goods["Gold"].sold_by == "pound"
    assert "5 and 10 pounds each" in goods["Slaves"].sale
    assert goods["Grain"].sources and "1/640" in goods["Grain"].sale


def test_sources_come_from_the_commercial_lists():
    goods = _goods()
    silver = goods["Silver"].sources
    assert any("Jihlava after 1222" in s for s in silver)
    assert any("Freiberg, Goslar" in s for s in silver)
    assert any(s.startswith("England") for s in silver)
    assert any(s.startswith("Crete") for s in goods["Saffron"].sources)


# -- silver, the ton, gemstones, pearls, dye, alum --


def test_silver_keeps_2420_with_the_errata_ton_noted():
    silver = _goods()["Silver"]
    assert silver.prices[3] == "2,420"
    assert silver.purity is not None and silver.purity.pure_price == 2420
    assert [(e.label, e.price) for e in silver.purity.examples] == [
        ("Shoddy", "250*"),
        ("Standard", "1,650*"),
        ("Superior", "2,200*"),
    ]
    percents = [
        round(gd.purity_percent(gd.price_value(e.price) or 0, 2420))
        for e in silver.purity.examples
    ]
    assert percents == [10, 68, 91]
    assert "2,240 pounds" in silver.note
    # Gold is ten times silver on the same table (p. 141).
    assert gd.price_value(_goods()["Gold"].prices[3]) == 10 * 2420
    assert gd.POUNDS_PER_TON == 2240 and gd.OUNCES_PER_POUND == 16
    assert gd.TABLE_POUNDS_PER_TON == 2420


def test_silver_details_show_the_purities_and_the_weights():
    saga = _saga()
    text = gf.info(saga, _index(saga, "Silver"), wide=True)
    assert "2,420" in text and "1,650*[/] (68%)" in text
    assert "about 68% silver" in gf.info(saga, _index(saga, "Silver"), wide=False)
    assert "1/2,240 ton" in text and "errata p. 57" in text


def test_gemstones_per_ounce_by_column():
    gems = _goods()["Gemstones"]
    assert gems.sold_by == "ounce"
    assert gems.per_ounce == ("", "0.26", "2.07", "2.58")
    for printed, per in zip(gems.prices[1:], gems.per_ounce[1:], strict=True):
        assert f"{gd.per_ounce(gd.price_value(printed) or 0):.2f}" == per
    # The book's note: 2 an ounce for average, 2 1/2 for fine (p. 141).
    assert "2 1/2 pounds an ounce for fine" in gems.sale
    assert "Superior and Expensive match" in gems.per_ounce_note


def test_pearls_per_ounce_are_the_books_figures():
    pearls = _goods()["Pearls"]
    assert pearls.per_ounce == ("", "2", "3", "")
    assert pearls.prices == ("5 (fake)", "80,000", "120,000", "n/a")


def test_dye_superior_stays_blank():
    dye = _goods()["Dye"]
    assert dye.prices == ("10", "50", "", "20,000")
    assert gd.price_value(dye.prices[2]) is None
    saga = _saga()
    assert "blank" in gf.info(saga, _index(saga, "Dye"), wide=True)


def test_alum_has_no_pure_price_and_takes_no_purity():
    alum = _goods()["Alum"]
    assert gd.by_purity(alum) and not gd.takes_purities(alum)
    saga = _saga()
    assert isinstance(gf.add_purity(saga, _index(saga, "Alum")), Refuse)


def test_price_values():
    assert gd.price_value("1,650*") == 1650
    assert gd.price_value("2,000 (fake)") == 2000
    assert gd.price_value("2.5") == 2.5
    assert gd.price_value("1500") == 1500
    for mark in ("#", "*", "n/a", ""):
        assert gd.price_value(mark) is None
    assert gd.price_at_purity(2420, 50) == 1210


def test_money_text():
    assert gd.coins(180) == "15 s"
    assert gd.coins(600) == "2½ £"
    assert gd.coins(0.5) == "½ d"
    assert gd.coins(20) == "20 d"
    assert gd.coins_range((6, 16)) == "6–16 d"
    assert gd.pounds_shillings_pence(90) == "7 s 6 d"
    assert gd.pounds_shillings_pence(900) == "3 £ 15 s"


def test_common_goods_follow_p144s_multipliers():
    saga = _saga()
    text = gf.info(saga, _index(saga, "Longbow"), wide=True)
    assert "15 shillings" in text
    assert "Shoddy x0.5 [b]7 s 6 d[/]" in text
    assert "Superior x2 [b]1 £ 10 s[/]" in text
    assert "Excellent x5 [b]3 £ 15 s[/]" in text


def test_a_bad_price_is_refused_naming_the_good():
    with pytest.raises(ValueError, match="Lumber"):
        GoodDef.from_dict(
            {"id": "x", "name": "Lumber", "prices": ["1", "2", "3", "lots"]}
        )


# -- the saga's list --


def test_listed_hides_a_hidden_good_and_the_whole_catalog():
    saga = _saga()
    sc.hide_entry(saga, gd.CATALOG_KEY, "good_silver")
    names = [g.name for g in gd.listed(saga)]
    assert "Silver" not in names and "Gold" in names
    sc.set_catalog_shown(saga, gd.CATALOG_KEY, False)
    assert gd.listed(saga) == []
    assert "not offered" in gf.header(saga)


def test_goods_is_one_of_saga_contents_catalogs():
    assert sc.CATALOGS[gd.CATALOG_KEY].label == "Goods"
    assert len(sc.CATALOGS[gd.CATALOG_KEY].shared()) == 77


def test_rows_have_a_heading_per_group():
    saga = _saga()
    saga.custom_goods.append(GoodDef(id="custom_good_amber", name="Amber"))
    headings = [text for index, text in gf.rows(saga) if index is None]
    assert [h.split("  ")[0].removeprefix("[b]") for h in headings] == [
        "Bulk goods",
        "Manufactured goods",
        "Luxury goods",
        "Common goods",
        "The saga's own[/]",
    ]
    assert gf.table(saga).keys is not None


# -- Add, Edit, Delete --


def test_a_catalog_good_is_read_only_and_hidden_not_deleted():
    saga = _saga()
    ops = gf.ops(saga)
    row = _index(saga, "Grain")
    assert isinstance(ops.edit(row), Refuse)
    hide = ops.remove(row)
    assert isinstance(hide, Confirm) and hide.yes_label == "Hide"
    hide.apply()
    assert saga.hidden_entries[gd.CATALOG_KEY] == ["good_grain"]


def test_add_edit_and_delete_a_good_of_the_sagas_own():
    saga = _saga()
    ops = gf.ops(saga)
    form = ops.add()
    assert isinstance(form, Form)
    values = {
        "name": "Amber",
        "kind": COMMODITY,
        "commodity_class": "luxury",
        "sold_by": "ton",
        "shoddy": "#",
        "standard": "500",
        "superior": "1,000",
        "expensive": "",
        "pure_price": None,
        "sources": "the Baltic; Hungary",
        "description": "",
    }
    assert form.validate is not None and form.validate(values) is None
    assert form.validate({**values, "standard": "lots"}) is not None
    form.apply(values)
    amber = saga.custom_goods[0]
    assert amber.id == "custom_good_amber" and amber.prices == ("#", "500", "1,000", "")
    assert amber.sources == ("the Baltic", "Hungary")
    row = _index(saga, "Amber")
    edit = ops.edit(row)
    assert isinstance(edit, Form)
    edit.apply({**values, "kind": COMMON, "pence": 30})
    assert saga.custom_goods[0].pence == (30, 30)
    assert saga.custom_goods[0].prices[1] == "2½ s"
    delete = ops.remove(row)
    assert isinstance(delete, Confirm) and delete.question == "Delete Amber?"
    delete.apply()
    assert saga.custom_goods == []


def test_a_common_good_needs_its_price():
    saga = _saga()
    assert gf.problem(saga, None, {"name": "Rope", "kind": COMMON}) is not None
    assert gf.problem(saga, None, {"name": "Rope", "kind": COMMON, "pence": 4}) is None


# -- Add a Purity --


def test_add_a_purity_prices_it_by_metal_content():
    saga = _saga()
    row = _index(saga, "Silver")
    form = gf.add_purity(saga, row)
    assert isinstance(form, Form) and form.live is not None
    assert "1,210" in form.live({"label": "Coin", "percent": 50})
    assert form.validate is not None
    assert form.validate({"label": "Coin", "percent": None}) is not None
    assert form.validate({"label": "Coin", "percent": 150}) is not None
    form.apply({"label": "Coin", "percent": 50})
    [purity] = saga.good_purities
    assert (purity.good_id, purity.label, purity.percent) == ("good_silver", "Coin", 50)
    assert "Coin, 50% [b]1,210[/]" in gf.info(saga, row, wide=True)
    again = gf.add_purity(saga, row)
    assert isinstance(again, Form)
    assert any(f.key == f"remove:{purity.id}" for f in again.fields())
    again.apply({"label": "", "percent": None, f"remove:{purity.id}": True})
    assert saga.good_purities == []


def test_add_a_purity_is_refused_for_a_good_not_priced_by_purity():
    saga = _saga()
    assert isinstance(gf.add_purity(saga, _index(saga, "Grain")), Refuse)
    assert not gf.offers_purity(saga, _index(saga, "Grain"))
    assert gf.offers_purity(saga, _index(saga, "Tin"))


class _Facts:
    def __init__(self, saga: Saga, row: int | None) -> None:
        self.saga, self.row = saga, row

    def chosen_row(self, _section: str) -> int | None:
        return self.row

    def active_section(self) -> str:
        return GOODS_SECTION

    def player_may(self, _action: str) -> bool:
        return True


def test_more_offers_add_a_purity_only_on_a_good_priced_by_purity():
    saga = _saga()
    rule = actions._SECTION_RULES["add_purity"]
    assert rule(_Facts(saga, _index(saga, "Silver")), GOODS_SECTION)  # type: ignore[arg-type]
    assert not rule(_Facts(saga, _index(saga, "Grain")), GOODS_SECTION)  # type: ignore[arg-type]
    assert not rule(_Facts(saga, _index(saga, "Silver")), "section-spells")  # type: ignore[arg-type]


def test_the_sagas_goods_and_purities_are_saved():
    saga = _saga()
    saga.custom_goods.append(
        GoodDef(
            id="custom_good_rope",
            name="Rope",
            kind=COMMON,
            pence=(4, 4),
            prices=("", "4 d", "", ""),
            sold_by="each",
        )
    )
    gf.add_purity(saga, _index(saga, "Tin")).apply({"label": "Pewter", "percent": 80})  # type: ignore[union-attr]
    loaded = Saga.from_dict(asdict(saga))
    assert loaded.custom_goods == saga.custom_goods
    assert loaded.good_purities == saga.good_purities
