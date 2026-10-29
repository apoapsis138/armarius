"""Labor Points from stories and what they are worth in money (City &
Guild pp. 37-40, Errata p. 56), the merchants' investments (pp. 110-130),
and wealth a covenant makes by magic (Covenants pp. 57-58, 65)."""

from dataclasses import replace

import pytest

from ars_magica_manager import deeds, labor, seasons
from ars_magica_manager import economics as eco
from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Covenant,
    IncomeSource,
    Investment,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import merchants as mr
from ars_magica_manager.seasons import plans


def _merchant(*virtues: str, saga_year: int = 1220) -> tuple[Saga, Character]:
    marco = Character(id="m1", name="Marco", type="companion")
    marco.characteristics.communication = 2
    marco.characteristics.intelligence = 1
    marco.characteristics.dexterity = 1
    marco.abilities = [
        Ability("Profession: Merchant", xp=75),  # 5
        Ability("Leadership", xp=15),  # 2
        Ability("Intrigue", xp=30),  # 3
        Ability("Area Lore: Venice", xp=50),  # 4
        Ability("Carousing", xp=15),  # 2
    ]
    marco.virtues_flaws = [VirtueFlawInstance(v) for v in virtues or ("vf_merchant",)]
    saga = Saga(id="s", name="S", characters=[marco])
    saga.current_year = saga_year
    return saga, marco


WORK = {"ability": "Profession: Merchant"}


# -- money ---------------------------------------------------------------


def test_nine_labor_points_are_a_quarter_of_the_years_income():
    # The Errata's 9, for every band (City & Guild p. 40; Errata p. 56).
    assert mr.lp_value(9, "trivial") == 2.5
    assert mr.lp_value(9, "lesser") == 10
    assert mr.pounds_text(mr.lp_value(9, "greater")) == "63 pounds"
    assert mr.pounds_text(mr.lp_value(9, "legendary")) == "250 pounds"
    assert mr.pounds_text(mr.lp_value(9, "trivial")) == "2.5 pounds"
    # Money put into a business, read the other way, rounded down.
    assert mr.lp_for_money(10, "lesser") == 9
    assert mr.lp_for_money(5, "typical") == 1


def test_the_band_follows_the_social_status_unless_set():
    _, marco = _merchant("vf_merchant")
    assert mr.band(marco) == "minor"
    marco.income_band = "lesser"
    assert mr.band(marco) == "lesser"
    _, capo = _merchant("vf_capo")
    assert mr.band(capo) == "greater"
    nobody = Character(id="n", name="N", type="grog")
    assert mr.band(nobody) == "" and mr.value_line(nobody) == ""


def test_this_season_says_what_the_labor_points_are_worth():
    saga, marco = _merchant()
    marco.labor_points = 36
    text = plans.livelihood_text(marco, saga.current_year)
    assert "Worth about 20 pounds to a Minor income" in text
    assert "9 Labor Points are a quarter of its 20 pounds a year" in text


# -- Labor Points from a story ---------------------------------------------


def test_a_season_of_labor_points_is_characteristic_plus_ability_times_wealth():
    _, marco = _merchant()
    assert mr.season_labor(marco, "Profession: Merchant", "communication") == 21
    marco.virtues_flaws.append(VirtueFlawInstance("vf_wealthy"))
    assert mr.season_labor(marco, "Profession: Merchant", "communication") == 42


def test_a_story_award_is_seasons_of_labor_points_rounded_down():
    saga, marco = _merchant()
    form = labor.story_form(saga, marco)
    assert isinstance(form, Form)
    values = {"award": "central", **WORK}
    assert labor.story_award(marco, values)[0] == 42
    # Half a season of 21 is 10 (DE p. 6).
    assert labor.story_award(marco, {"award": "subplot", **WORK})[0] == 10
    # The seasons can be changed (antique sailing instructions: ½ to 1½).
    assert labor.story_award(marco, {**values, "seasons": "1.5"})[0] == 31
    lines = form.apply({**values, "story": "The Doge's ring", "band": "lesser"})
    assert marco.labor_points == 42 and marco.income_band == "lesser"
    assert "Labor Points now 42." in lines
    assert marco.diary[-1].name == "Labor Points from a story: The Doge's ring"


def test_the_stories_offered_suit_the_kind_of_merchant():
    _, craftsman = _merchant("vf_craftsman")
    keys = {a.key for a in mr.stories_for(craftsman)}
    assert "central" in keys and "crop_failure" not in keys
    _, marco = _merchant("vf_merchant")
    keys = {a.key for a in mr.stories_for(marco)}
    assert {"crop_failure", "brigands"} <= keys and "loot" not in keys
    _, factor = _merchant("vf_factor")
    keys = {a.key for a in mr.stories_for(factor)}
    # A poorer kind's stories suit the richer ones (p. 111).
    assert {"brigands", "loot", "withdrawal"} <= keys and "branch" not in keys


def test_a_story_needs_a_craft_or_profession():
    saga = Saga(id="s", name="S")
    knight = Character(id="k", name="Kurt", type="companion")
    assert isinstance(labor.story_form(saga, knight), Refuse)


# -- investments -----------------------------------------------------------


def test_charity_trickles_into_a_reputation_and_calls_a_crowd():
    saga, marco = _merchant()
    form = labor.invest_form(saga, marco)
    assert isinstance(form, Form)
    marco.labor_points = 60
    gift = {"kind": "charity", "name": "bread dole", "lp": 15, **WORK}
    gift |= {"reputation": "Generous", "merchant": mr.CARRIER}
    form.apply(gift)  # 15 of a 21-point season: no experience yet
    assert marco.labor_points == 45
    form.apply({**gift, "lp": 10})  # 25 in all: one season's worth
    generous = next(r for r in marco.reputations if r.name == "Generous")
    assert generous.deeds == 1
    assert len(marco.investments) == 1 and marco.investments[0].lp == 25
    generous.score = 2
    lines = mr.investment_lines(marco, saga.current_year)
    # (Communication 2 + Leadership 2) x 2 x 2 (a local carrier).
    assert "a crowd of 16 at short notice, 32 with a week's" in lines[0]
    assert "a crowd needs" in mr.investment_lines(marco, saga.current_year + 2)[0]


def test_a_speculation_pays_a_tenth_a_year_and_comes_back_when_ended():
    saga, marco = _merchant()
    marco.labor_points = 100
    form = labor.invest_form(saga, marco)
    assert isinstance(form, Form)
    found = labor.outcome(saga, marco, {"kind": "speculation", "lp": 60, **WORK})
    assert "+6 a year" in found.lines[0] and "6 guard(s)" in found.lines[0]
    form.apply({"kind": "speculation", "name": "wool", "lp": 60, **WORK})
    assert marco.labor_points == 40
    assert mr.year_returns(marco, 1220) == []  # not the year it began
    assert mr.year_returns(marco, 1221) == [("Speculation (wool)", 6)]
    fields = {f.key: f for f in labor.invest_fields(marco)}
    assert fields["which"].value == "0"
    form.apply({"kind": "end", "which": "0"})
    assert marco.labor_points == 100 and not marco.investments


def test_an_introduction_pays_three_seasons_two_years_on():
    saga, marco = _merchant()
    marco.labor_points = 50
    form = labor.invest_form(saga, marco)
    assert isinstance(form, Form)
    form.apply({"kind": "introduction", "name": "Pisa and Genoa", **WORK})
    assert marco.labor_points == 8
    assert mr.year_returns(marco, 1221) == []
    assert mr.year_returns(marco, 1222) == [("Introduction (Pisa and Genoa)", 63)]
    assert not marco.investments


def test_the_winter_upkeep_counts_what_investments_pay():
    saga, marco = _merchant()
    marco.labor_points = 10
    marco.investments.append(Investment(mr.SPECULATION, "salt", 100, 1219))
    seasons.year_end_business(saga)
    assert marco.labor_points == 10 - 36 + 10
    assert "Speculation (salt) +10" in marco.diary[-1].details


def test_an_investment_costing_more_than_his_surplus_is_refused():
    saga, marco = _merchant()
    form = labor.invest_form(saga, marco)
    assert isinstance(form, Form) and form.validate is not None
    marco.labor_points = 20
    assert form.validate({"kind": "marriage", **WORK}) == (
        "It costs 42 Labor Points; Marco has 20."
    )
    # Each sumptuous item costs 1 x the Wealth Multiplier (3).
    assert form.validate({"kind": "drawings", "items": 6}) is None
    assert form.validate({"kind": "drawings", "items": 7}) == (
        "It costs 21 Labor Points; Marco has 20."
    )


def test_a_boom_foreseen_by_intelligence_and_area_lore():
    assert mr.boom_return(18, 20, False)[0] == 40
    assert mr.boom_return(15, 20, False)[0] == 30
    assert mr.boom_return(10, 20, False)[0] == 20
    assert mr.boom_return(6, 20, False)[0] == 16
    assert "destroyed" in mr.boom_return(25, 20, True)[1]
    saga, marco = _merchant()
    marco.labor_points = 20
    found = labor.outcome(saga, marco, {"kind": "boom", "lp": 20, "die": 10})
    # Intelligence 1 + Area Lore 4 + 10 = 15.
    assert found.labor == 10 and "= 15" in found.lines[0]


def test_legal_action_and_the_richer_merchants_investments():
    assert mr.legal_result(8, 10, "true") and not mr.legal_result(8, 10, "")
    assert not mr.legal_result(12, 10, "outlandish")
    saga, factor = _merchant("vf_factor")
    offered = {k.key for k in mr.investments_for(factor)}
    assert {"smuggling", "government", "talent"} <= offered and "party" not in offered
    # (Communication 2 + Leadership 2) x 3 = 12: two Favors.
    found = labor.outcome(saga, factor, {"kind": "talent"})
    assert found.labor == 12 and "2 Favor(s)" in found.lines[0]
    assert labor.outcome(saga, factor, {"kind": "government"}).labor == 15
    assert labor.outcome(saga, factor, {"kind": "smuggling"}).labor == 12


def test_a_capos_lavish_party_spends_silver_for_favors():
    saga, capo = _merchant("vf_capo")
    capo.silver = 10
    form = labor.invest_form(saga, capo)
    assert isinstance(form, Form) and form.validate is not None
    party = {"kind": "party", "die": 5, "party_trait": "communication"}
    party |= {"theme": "Carousing", "pounds": 6}
    assert form.validate({**party, "pounds": 11}) == "Marco has 10 pounds of silver."
    # 5 + 2 + 2 + 3 (pounds, at most Intrigue 3) = 12: three Favors.
    lines = form.apply(party)
    assert "= 12" in lines[0] and "3 Favor(s)" in lines[0]
    assert capo.silver == 4


def test_money_put_into_the_business_buys_labor_points():
    saga, marco = _merchant()
    marco.silver = 20
    form = labor.invest_form(saga, marco)
    assert isinstance(form, Form)
    form.apply({"kind": "money", "pounds": 20})  # a Minor business
    assert marco.labor_points == 36 and marco.silver == 0


def test_a_craftsman_may_only_put_money_into_his_business():
    _, smith = _merchant("vf_craftsman")
    assert [k.key for k in mr.investments_for(smith)] == ["money"]


# -- where they are offered ------------------------------------------------


@pytest.mark.parametrize("action", ["labor_story", "invest_labor"])
def test_offered_on_this_season_for_one_who_works(action):
    saga, marco = _merchant()
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="m1")
    assert available(action, replace(page, section="section-char-season"))
    assert not available(action, replace(page, section="section-reputations"))
    assert action in {i.action for i in menu_forms.placed(page, deeds.SEASON_WORK)}
    marco.abilities, marco.virtues_flaws = [], []
    assert not available(action, replace(page, section="section-char-season"))


# -- wealth made by magic --------------------------------------------------


def test_wealth_made_by_magic_against_the_tribunals_limit():
    covenant = Covenant(id="c", saga_id="s", name="Fengheld", unnamed_magi=1)
    saga = Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=[
            Character(id=f"m{i}", name=f"M{i}", type="magus", covenant_id="c")
            for i in range(3)
        ],
    )
    assert eco.magic_limit(saga, covenant) == 8
    assert "Over the limit" not in eco.magic_wealth_text(8, 8, 4)
    assert "Over the limit" in eco.magic_wealth_text(9, 8, 4)
    source = IncomeSource(id="i", name="Silver mine", type="Typical")
    live = menu_forms.improve_live(source, (8, 4))
    text = live({"effect": "Growth", "magic": True})
    assert "Made by magic: 5 pound(s) a year" in text and "8 for 4 magi" in text
    assert "Over the limit" in live({"effect": "Boom", "magic": True})
    assert "Made by magic" not in live({"effect": "Boom"})
    form = menu_forms.improve_form(saga, source, covenant)
    confirm = form.apply({"effect": "Growth", "magic": True})
    confirm.apply()
    assert source.income == 105 and "Growth by magic" in source.note


def test_the_reputation_a_marriage_brokers_is_one_experience_point():
    saga, marco = _merchant()
    marco.labor_points = 50
    marco.reputations.append(ScoredTrait("Matchmaker", 1))
    form = labor.invest_form(saga, marco)
    assert isinstance(form, Form)
    form.apply(
        {
            "kind": "marriage",
            "name": "the Contarini",
            "reputation": "matchmaker",
            **WORK,
        }
    )
    assert marco.reputations[0].deeds == 1 and marco.labor_points == 8
    assert "Social Contacts until Winter 1223" in mr.investment_lines(marco, 1220)[0]
