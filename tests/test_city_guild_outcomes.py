"""City & Guild's season outcomes: workshop exertion's results and its
Aging roll (pp. 73-74), the (Craft) Reputation (p. 74), a laborer's
service (p. 76) and selling finished goods (pp. 74-76)."""

import random
from dataclasses import replace

import pytest

from ars_magica_manager import seasons, selling
from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import season as season_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Covenant,
    Saga,
    ScoredTrait,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import aging
from ars_magica_manager.rules import selling as sl
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules.season_work import city_guild as cg
from ars_magica_manager.rules.xp import ability_xp


class Faces(random.Random):
    """A d10 that shows the faces given, in order (then 5s)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *_args, **_kwargs) -> int:  # type: ignore[override]
        return self.faces.pop(0) if self.faces else 5


def _saga(dexterity: int = 2, born: int | None = None) -> Saga:
    smith = Character(id="c", name="Wulf", type="companion")
    smith.characteristics = Characteristics(
        dexterity=dexterity, communication=1, presence=2
    )
    smith.abilities = [
        Ability("Craft: Smith", xp=ability_xp(6)),
        Ability("Bargain", xp=ability_xp(3)),
    ]
    smith.background.year_born = born
    return Saga(id="s", name="S", characters=[smith])


def _plan(activity, subject="ability:Craft: Smith", season="Spring", **kw):
    return SeasonPlan("c", 1220, season, activity, [XpAllocation(subject)], **kw)


def _work(saga, plan, rng=None):
    return sw.work(saga, saga.character("c"), plan, rng)


def _run(saga, plan, rng=None):
    saga.current_season, saga.current_year = plan.season, plan.year
    seasons.set_plan(saga, plan)
    seasons.apply(saga, seasons.resolve(saga, rng or random.Random(1)))
    return saga.character("c")


def _reputation(character, name):
    return next((r for r in character.reputations if r.name == name), None)


# -- workshop exertion (pp. 73-74) ---------------------------------------------


def test_exertion_invention_banks_labor_points_toward_innovation():
    saga = _saga()
    # Simple die 5; exertion roll 9 (invention); a simple die of 4 banked.
    work = _work(saga, _plan("workshop_production", experimenting=True), Faces(5, 9, 4))
    assert work.progress == [(cg.INNOVATION_KIND, cg.INNOVATION_BANK, 0, 4)]
    assert "invention" in work.notes[0] and "(4)" in work.notes[0]
    wulf = _run(saga, _plan("workshop_production", experimenting=True), Faces(5, 9, 4))
    assert cg.banked_innovation(wulf) == 4
    # Innovation 1 costs 100, 4 of them banked: 96 Labor Points do it.
    wulf.labor_points = 96
    assert not sw.problems(saga, wulf, _plan("improve_workshop", title="Innovation"))
    wulf.labor_points = 95
    assert (
        "4 banked by inventions"
        in (sw.problems(saga, wulf, _plan("improve_workshop", title="Innovation"))[0])
    )
    wulf.labor_points = 96
    _run(saga, _plan("improve_workshop", title="Innovation", season="Summer"))
    assert (wulf.workshop_innovation, wulf.labor_points) == (1, 0)
    assert cg.banked_innovation(wulf) == 0


def test_exertion_reputation_and_understanding():
    saga = _saga()
    # A stress die of 1 then 5 is 10: a simple die of 3 xp in the Reputation.
    work = _work(
        saga, _plan("workshop_production", experimenting=True), Faces(5, 1, 5, 3)
    )
    assert work.reputation_xp[0] == ("Smith", 3)
    # 1 then 6 is 12: a simple die of 7 xp in the Craft.
    work = _work(
        saga, _plan("workshop_production", experimenting=True), Faces(5, 1, 6, 7)
    )
    assert work.ability_xp == [("Craft: Smith", 7)]
    before = saga.character("c").abilities[0].xp
    wulf = _run(
        saga, _plan("workshop_production", experimenting=True), Faces(5, 1, 6, 7)
    )
    # 7 from the exertion, 2 from the season's Exposure.
    assert wulf.abilities[0].xp == before + 7 + 2


def test_exertion_no_benefit_and_disaster():
    saga = _saga()
    lost = _work(saga, _plan("workshop_production", experimenting=True), Faces(5, 6))
    assert "+ simple die 0" in lost.notes[0]
    assert "Workshop Total 8 " in lost.notes[1]
    ruin = _work(saga, _plan("workshop_production", experimenting=True), Faces(5, 0, 0))
    assert "disaster" in ruin.notes[0] and ruin.aging_roll


def test_exertion_on_excellent_and_wondrous_items():
    saga = _saga()
    # Dex 2 + Craft 6 = 8, + a simple die of 7: 15, the excellent item's level.
    made = _work(
        saga,
        _plan("make_excellent_item", title="Sword", experimenting=True),
        Faces(7, 2),
    )
    assert made.progress == [("item", "Sword", 1, 1)] and made.aging_roll
    form = season_forms._supplement_plan_values(
        saga.character("c"), "make_wondrous_item", {"exert": True}
    )
    assert form["experimenting"] is True


def test_a_young_craftsman_exerting_rolls_a_simple_die():
    young = _work(
        _saga(born=1200), _plan("workshop_production", experimenting=True), Faces(5, 2)
    )
    assert young.aging_roll and young.aging_young
    assert "under 35" in young.notes[0]
    old = _work(
        _saga(born=1180), _plan("workshop_production", experimenting=True), Faces(5, 2)
    )
    assert old.aging_roll and not old.aging_young
    # The aging roll itself: a simple die (a face of 0 is 10, not a botch),
    # and its 13 (10 + 25 / 10 rounded up) gives Aging Points but no Crisis.
    wulf = _saga().character("c")
    roll = aging.roll(wulf, 25, 0, 0, Faces(0), young=True)
    assert (roll.total, roll.crisis) == (13, False) and roll.any_points


def test_an_exerted_season_applies_its_aging_roll():
    saga = _saga(born=1200)
    wulf = _run(saga, _plan("workshop_production", experimenting=True), Faces(5, 2))
    assert any(e.activity == "Aging" for e in wulf.diary)


# -- the (Craft) Reputation (p. 74) --------------------------------------------


def test_six_over_the_standard_level_earns_reputation():
    saga = _saga()
    wulf = _run(saga, _plan("workshop_production", other_modifier=4))
    smith = _reputation(wulf, "Smith")
    assert smith is not None and (smith.score, smith.deeds) == (0, 1)
    # Just short of it: nothing.
    work = _work(saga, _plan("workshop_production", other_modifier=3))
    assert work.reputation_xp == []


def test_shoddy_seasons_running_lower_the_reputation():
    saga = _saga(dexterity=-5)
    wulf = _run(saga, _plan("workshop_production"))
    assert wulf.reputations == []
    assert f"{cg.SHODDY} (Craft: Smith)" in wulf.diary[-1].details
    wulf = _run(saga, _plan("workshop_production", season="Summer"))
    bad = _reputation(wulf, "Shoddy Smith")
    assert bad is not None and bad.deeds == 1
    # A season between breaks the run.
    work = _work(saga, _plan("workshop_production", season="Winter"))
    assert work.reputation_xp == []


def test_reputation_experience_rises_and_falls_as_an_ability():
    wulf = _saga().character("c")
    cg.add_trade_reputation(wulf, "Smith", 15)
    smith = _reputation(wulf, "Smith")
    assert smith is not None and (smith.score, smith.deeds) == (2, 0)
    cg.add_trade_reputation(wulf, "Smith", -1)
    assert (smith.score, smith.deeds) == (1, 9)
    # 14 xp left in it; the 12 more lost go to a Reputation as a bad smith.
    cg.add_trade_reputation(wulf, "Smith", -26)
    bad = _reputation(wulf, "Shoddy Smith")
    assert (smith.score, smith.deeds) == (0, 0)
    # The bad craftsman's Reputation is scored positive (C&G p. 74; DE p. 386).
    assert bad is not None and (bad.score, bad.deeds) == (1, 7)
    cg.add_trade_reputation(wulf, "Smith", -3)
    assert (bad.score, bad.deeds) == (2, 0)
    assert cg.reputation_xp(ScoredTrait("X", 2, deeds=1)) == 16


def test_a_wondrous_item_made_earns_reputation():
    saga = _saga()
    wulf = saga.character("c")
    wulf.virtues_flaws = [
        VirtueFlawInstance("vf_touched_by_realm", params={"realm": "Magic"})
    ]
    # Workshop Total 8 against level 3: 5 toward 3, made this season.
    made = _work(saga, _plan("make_wondrous_item", title="Ring", book_level=3))
    assert ("Smith", 1) in made.reputation_xp
    # Against 20 it is far off: no Reputation yet.
    slow = _work(saga, _plan("make_wondrous_item", title="Ring", book_level=20))
    assert slow.reputation_xp == []


def test_a_wondrous_season_also_earns_the_margin_point():
    # Any season 6 or more over the standard goods' Craft Level 6 earns 1,
    # and making a wondrous item also grants 1 (City & Guild p. 74).
    saga = _saga()
    wulf = saga.character("c")
    wulf.virtues_flaws = [
        VirtueFlawInstance("vf_touched_by_realm", params={"realm": "Magic"})
    ]
    # Workshop Total 12 against level 20: 6 or more over 6, not made yet.
    slow = _work(
        saga,
        _plan("make_wondrous_item", title="Ring", book_level=20, other_modifier=4),
    )
    assert slow.reputation_xp == [("Smith", 1)]
    # Total 12 against level 3: made this season, so both points.
    made = _work(
        saga,
        _plan("make_wondrous_item", title="Ring", book_level=3, other_modifier=4),
    )
    assert made.reputation_xp == [("Smith", 1), ("Smith", 1)]


# -- a laborer's service (p. 76) -----------------------------------------------


def test_a_laborers_service():
    saga = _saga()
    wulf = saga.character("c")
    wulf.characteristics.strength = 2
    wulf.abilities.append(Ability("Profession: Scribe", xp=ability_xp(4)))
    work = _work(saga, _plan("working_season", "ability:Profession: Scribe"))
    # Labor Points: Communication 1 + Scribe 4 (p. 38); the Labor Total uses
    # the primary Characteristic, Strength by default (pp. 67, 76).
    assert work.notes[0].startswith("Labor Points: (Communication + Profession")
    assert work.labor_points == 5 * 3
    assert (
        "Labor Total 6 (Strength + Profession: Scribe) against Profession "
        "Level 6: Standard service"
    ) in work.notes[1]
    # The plan's Characteristic is his primary one, not the Labor Points'.
    picked = _work(
        saga,
        _plan(
            "working_season", "ability:Profession: Scribe", characteristic="presence"
        ),
    )
    assert picked.labor_points == 5 * 3
    assert "Labor Total 6 (Presence + Profession: Scribe)" in picked.notes[1]
    assert cg.labor_quality(12) == "Superior" and cg.labor_quality(20) == "Superior"
    assert cg.labor_quality(5) == "Shoddy"
    # A Craft's working season is not a laborer's.
    assert len(_work(saga, _plan("working_season")).notes) == 1


@pytest.mark.parametrize(
    ("realm", "level"),
    [("Magic", 7), ("Faerie", 7), ("Infernal", 7), ("Divine", 6)],
)
def test_an_aura_raises_the_profession_level(realm, level):
    # Raised as a Craft Level is, +1 in an Infernal, Faerie or Magic aura
    # and not a Divine one (City & Guild pp. 69, 76).
    saga = _saga()
    saga.covenants.append(
        Covenant(id="cov", saga_id="s", name="Cov", aura=3, aura_realm=realm)
    )
    wulf = saga.character("c")
    wulf.covenant_id = "cov"
    wulf.characteristics.strength = 2
    wulf.abilities.append(Ability("Profession: Scribe", xp=ability_xp(4)))
    assert cg.profession_level(saga, wulf) == level
    work = _work(saga, _plan("working_season", "ability:Profession: Scribe"))
    quality = "Shoddy" if level == 7 else "Standard"
    assert f"Profession Level {level}" in work.notes[1]
    assert f"{quality} service" in work.notes[1]


# -- selling finished goods (pp. 74-76) ----------------------------------------


@pytest.mark.parametrize(
    ("total", "change"), [(8, 0), (9, 10), (10, 20), (13, 50), (20, 50)]
)
def test_selling_to_a_typical_customer(total, change):
    assert sl.typical_change(total) == change


def test_selling_to_an_important_customer():
    assert sl.opposed_change(12, 9) == 30
    assert sl.opposed_change(5, 12) == -50
    assert sl.opposed_change(9, 9) == 0
    assert sl.sale(200, sl.IMPORTANT, 12, 9) == sl.Sale(30, 260)
    assert sl.sale(200, sl.IMPORTANT, 12, 9, botched=True) == sl.Sale(0, 0, True)
    assert sl.sale(15, sl.TYPICAL, 10) == sl.Sale(20, 18)


def test_the_sale_form():
    saga = _saga()
    wulf = saga.character("c")
    form = selling.sell_form(saga, wulf, Faces(3))
    assert isinstance(form, Form)
    values = {"goods": "8 shortswords", "standard": 200, "customer": sl.TYPICAL}
    assert form.validate is not None and form.live is not None
    assert form.validate({**values, "standard": 0})
    assert form.validate({**values, "die": 11})
    # Presence 2 + Bargain 3 = 5: a die of 4 sells 10% over, 8 the most.
    live = form.live(values)
    assert "A die of 4 or more sells 10% over; 8 or more, the most" in live
    lines = form.apply(values)
    # Die 3: 8 against 9, the standard price.
    assert "The standard price: 200 pence." in lines
    assert wulf.diary[-1].name == "Sold: 8 shortswords"
    typed = form.apply({**values, "die": 7})
    assert "40% over the standard price: 280 pence for 200." in typed
    against = form.apply(
        {**values, "customer": sl.IMPORTANT, "theirs": 12, "die": 4, "botched": True}
    )
    assert any("next to nothing" in line for line in against)


def test_selling_is_offered_to_a_craftsman_on_this_season():
    saga = _saga()
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="c")
    assert available("sell_goods", replace(page, section="section-char-season"))
    assert not available("sell_goods", replace(page, section="section-reputations"))
    assert "sell_goods" in {i.action for i in menu_forms.placed(page, "This Season")}
    saga.character("c").abilities = []
    assert not available("sell_goods", replace(page, section="section-char-season"))
    assert isinstance(selling.sell_form(saga, saga.character("c")), Refuse)
