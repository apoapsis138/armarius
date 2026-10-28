"""Grogs' rewards, punishments and pensions (Grogs pp. 23-26, Covenants
pp. 38-40, DE p. 186) and the Finesse Ease Factors of craft magic (DE pp.
306-308)."""

import random

import pytest

from ars_magica_manager import actions, economics
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.casting_text import option_lines
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import craft_magic as craft_forms
from ars_magica_manager.forms import grogs as grog_forms
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Covenant,
    Discipline,
    Inhabitant,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import craft_magic as cm
from ars_magica_manager.rules import grog_discipline as gd


def _saga() -> Saga:
    saga = Saga(id="s", name="Test", current_year=1220, current_season="Spring")
    saga.covenants.append(Covenant(id="cov", saga_id="s", name="Fengheld"))
    grog = Character(id="g", name="Hugo", type="grog", covenant_id="cov")
    saga.characters.append(grog)
    saga.covenants[0].inhabitants.append(
        Inhabitant(id="i1", kind="turb", name="Hugo", character_id="g")
    )
    magus = Character(
        id="m",
        name="Leandro",
        type="magus",
        covenant_id="cov",
        characteristics=Characteristics(intelligence=3, perception=1),
        abilities=[Ability("Finesse", xp=15)],  # score 2
    )
    saga.characters.append(magus)
    return saga


def _grog(saga: Saga) -> Character:
    grog = saga.character("g")
    assert grog is not None
    return grog


def _give(saga: Saga, **values) -> list[str]:
    form = grog_forms.discipline_form(saga, _grog(saga))
    assert isinstance(form, Form)
    filled = {f.key: f.value for f in form.fields()}
    filled.update(values)
    assert form.validate is not None and form.validate(filled) is None
    return form.apply(filled)


# -- the rules --


def test_flogging_and_whipping_wound_as_the_book_says():
    assert [gd.flogging(b) for b in (1, 5, 10)] == [(1, 1), (2, 3), (3, 5)]
    assert gd.whipping(10, short=False) == ["light"]
    assert gd.whipping(30, short=False) == ["medium"]
    assert gd.whipping(50, short=True) == ["heavy", "heavy"]
    assert gd.whipping(5, short=False) == []
    assert gd.whipping_recovery(10) == 1 and gd.whipping_recovery(20) == 7


def test_the_punishments_are_in_order_of_severity():
    assert gd.PUNISHMENTS[0] == gd.CASTIGATION
    assert gd.PUNISHMENTS[-1] == gd.FUSTUARIUM
    assert gd.PUNISHMENTS.index(gd.FLOGGING) < gd.PUNISHMENTS.index(gd.WHIPPING)


def test_rations_change_living_conditions_for_the_aging_year():
    grog = Character(id="g", name="Hugo", type="grog")
    grog.discipline.append(Discipline(1220, "Spring", gd.IMPROVED_RATIONS, 4))
    assert gd.rations_living(grog, 1220) == 1
    assert gd.rations_living(grog, 1221) == 0
    # A year from Summer covers only three seasons of 1220.
    late = Character(id="h", name="Odo", type="grog")
    late.discipline.append(Discipline(1220, "Summer", gd.IMPROVED_RATIONS, 4))
    assert gd.rations_living(late, 1220) == 0
    poor = Character(id="p", name="Wat", type="grog")
    poor.discipline.append(Discipline(1220, "Spring", gd.REDUCED_RATIONS, 2))
    assert gd.rations_living(poor, 1220) == -1
    poor.discipline.append(Discipline(1220, "Autumn", gd.REDUCED_RATIONS, 1))
    assert gd.rations_living(poor, 1220) == -2
    # A month on reduced rations is under a season: no change.
    month = Character(id="q", name="Tom", type="grog")
    month.discipline.append(Discipline(1220, "Spring", gd.REDUCED_RATIONS, 0))
    assert gd.rations_living(month, 1220) == 0


def test_retirement_ends_improved_rations():
    grog = Character(id="g", name="Hugo", type="grog")
    grog.discipline.append(Discipline(1220, "Spring", gd.IMPROVED_RATIONS, None))
    grog.discipline.append(
        Discipline(1220, "Autumn", gd.RETIRED, None, note=gd.PENSION)
    )
    assert gd.rations_living(grog, 1220) == 0


def test_loyalty_cost_follows_covenants():
    officer = gd.loyalty_cost(gd.BRUTAL, ordered_by=gd.OFFICER, just=True, prevailing=0)
    assert officer.points == 0
    unjust = gd.loyalty_cost(
        gd.RESTRAINT, ordered_by=gd.OFFICER, just=False, prevailing=0
    )
    assert unjust.points == -6
    # A magus's just punishment costs only when Prevailing Loyalty isn't positive.
    assert (
        gd.loyalty_cost(gd.BRUTAL, ordered_by=gd.MAGUS, just=True, prevailing=1).points
        == 0
    )
    assert (
        gd.loyalty_cost(gd.BRUTAL, ordered_by=gd.MAGUS, just=True, prevailing=0).points
        == -12
    )
    # A loved victim adds his Reputation; a disliked one takes it off, not past 0.
    loved = gd.loyalty_cost(
        gd.PUBLIC_HUMILIATION,
        ordered_by=gd.MAGUS,
        just=False,
        prevailing=2,
        reputation=2,
    )
    assert loved.points == -5
    disliked = gd.loyalty_cost(
        gd.MINOR_HUMILIATION,
        ordered_by=gd.MAGUS,
        just=False,
        prevailing=0,
        reputation=-3,
    )
    assert disliked.points == 0
    # Wounds the magus deals himself, one step worse by magic.
    own = gd.loyalty_cost(
        gd.BRUTAL,
        ordered_by=gd.MAGUS,
        just=True,
        prevailing=3,
        own_wounds=["light", "light"],
        by_magic=True,
    )
    assert own.points == -12


def test_pay_and_a_half_and_pensions_change_wages():
    saga = _saga()
    covenant = saga.covenants[0]
    grog = _grog(saga)
    before = economics.summarize(saga, covenant)
    assert gd.wage_adjustment(saga, covenant, 1.0) == 0
    # A turb grog in a Spring covenant: 1 point, 0.2 pounds of Wages a year.
    grog.discipline.append(Discipline(1220, "Spring", gd.PAY_AND_A_HALF, None))
    assert gd.wage_adjustment(saga, covenant, 1.0) == pytest.approx(0.1)
    grog.discipline.append(
        Discipline(1220, "Spring", gd.RETIRED, None, note=gd.PENSION)
    )
    # Retiring stops the extra pay and halves his Wages.
    assert gd.wage_adjustment(saga, covenant, 1.0) == pytest.approx(-0.1)
    grog.discipline[-1].note = gd.RENT
    assert gd.wage_adjustment(saga, covenant, 2.0) == pytest.approx(-0.4)
    assert economics.summarize(saga, covenant) is not None
    assert before is not None


# -- the forms --


def test_a_whipping_wounds_him_and_writes_both_diaries():
    saga = _saga()
    said = _give(
        saga,
        kind=gd.WHIPPING,
        lashes=30,
        short_whip=True,
        ordered_by=gd.MAGUS,
        just=False,
        note="theft",
    )
    grog = _grog(saga)
    assert grog.wounds.medium == 2
    assert [d.kind for d in grog.discipline] == [gd.WHIPPING]
    assert grog.diary[-1].name == "Whipping: theft"
    [entry] = saga.covenants[0].diary
    assert entry.loyalty == -12 and entry.category == "Loyalty Event"
    assert "30 lashes: 2 Medium Wounds." in said


def test_a_fitting_punishment_from_an_officer_costs_no_loyalty():
    saga = _saga()
    _give(saga, kind=gd.CASTIGATION, loyal_change=-1)
    grog = _grog(saga)
    [entry] = saga.covenants[0].diary
    assert entry.loyalty is None
    assert grog.personality_traits == [ScoredTrait("Loyal to Covenant", -1)]


def test_promotion_and_demotion_set_his_rank():
    saga = _saga()
    _give(saga, kind=gd.PROMOTION, rank="custos")
    assert gd.rank(_grog(saga)) == "custos"
    _give(saga, kind=gd.IMPROVED_EQUIPMENT, note="an expensive sword")
    said = _give(saga, kind=gd.REDUCTION_IN_RANK, rank="grog")
    assert gd.rank(_grog(saga)) == "grog"
    assert any("an expensive sword" in line for line in said)


def test_improved_rations_last_as_chosen():
    saga = _saga()
    _give(saga, kind=gd.IMPROVED_RATIONS, duration="A year")
    assert _grog(saga).discipline[0].seasons == 4
    assert gd.rations_living(_grog(saga), 1220) == 1


def test_dismissal_takes_him_off_the_lists():
    saga = _saga()
    _give(saga, kind=gd.DISMISSAL, leaves=True)
    assert _grog(saga).covenant_id is None
    assert saga.covenants[0].inhabitants == []


def test_the_fustuarium_kills_him():
    saga = _saga()
    _give(saga, kind=gd.FUSTUARIUM)
    assert _grog(saga).wounds.dead
    assert isinstance(grog_forms.discipline_form(saga, _grog(saga)), Refuse)


def test_retiring_and_a_widows_pension():
    saga = _saga()
    covenant = saga.covenants[0]
    form = grog_forms.pension_form(saga, _grog(saga))
    assert isinstance(form, Form)
    form.apply({"terms": gd.PENSION, "grants": True, "note": ""})
    assert covenant.loyalty.pension
    assert gd.retirement(_grog(saga)) is not None
    assert isinstance(grog_forms.pension_form(saga, _grog(saga)), Refuse)
    _grog(saga).wounds.dead = True
    widow = grog_forms.pension_form(saga, _grog(saga))
    assert isinstance(widow, Form)
    widow.apply({"grants": True, "note": ""})
    assert covenant.loyalty.pensioners == 1
    assert isinstance(grog_forms.pension_form(saga, _grog(saga)), Refuse)


def test_only_a_grog_in_a_covenant_is_rewarded():
    saga = _saga()
    assert isinstance(grog_forms.discipline_form(saga, saga.character("m")), Refuse)
    _grog(saga).covenant_id = None
    assert isinstance(grog_forms.discipline_form(saga, _grog(saga)), Refuse)


def test_the_grog_commands_are_offered_on_a_grog_only():
    saga = _saga()
    grog = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="g")
    labels = [item.label for item in menu_forms.placed(grog, "Personality Traits")]
    # Roll: a trait roll, with the Silver Cord's help for a familiar's master.
    # The saints and the Church are on the Religion chapter's Faith.
    assert labels == ["Reward or Punish", "Pension", "Roll"]
    # A grog may pray to the saints, but can't spend Confidence on God's
    # aid; with no Pious trait he has no Devotions to keep.
    assert [i.label for i in menu_forms.placed(grog, "Faith")] == [
        "Invoke a Saint",
        "Patron Saint",
        "Indulgence, Vigil or Fast",
    ]
    magus = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="m")
    assert [i.label for i in menu_forms.placed(magus, "Personality Traits")] == ["Roll"]
    assert not menu_forms.placed(magus, "Known Spells")
    assert [i.label for i in menu_forms.placed(magus, "Magic Outside the Lab")] == [
        "Craft by Magic",
        "Cast in a Lacuna",
    ]
    # Where he is: the aura his casting counts (DE pp. 410-411).
    assert [i.label for i in menu_forms.placed(magus, "Current Location")] == [
        "Current Location"
    ]
    assert not actions.available("craft_by_magic", grog)


# -- craft magic --


def test_the_ease_factor_table_holds_the_magic_and_a_days_work():
    assert cm.task_ease("Trivial") == 3
    assert cm.task_ease("Almost Impossible") == 27
    assert cm.task_ease("Average", "A season") == 18
    assert cm.mundane_ease(9, "A year") == 21
    assert cm.creo_ease(cm.SINGLE) == 0
    assert cm.creo_ease(cm.FEW) == 3
    assert cm.creo_ease(cm.ELABORATE, "Hard", "A month") == 18


def test_rego_uses_perception_and_creo_intelligence():
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None
    assert cm.roll_base(magus, cm.REGO) == 1 + 2
    assert cm.roll_base(magus, cm.CREO) == 3 + 2
    assert cm.roll_base(magus, cm.REGO, precise=2) == 5
    magus.virtues_flaws.append(VirtueFlawInstance("vf_clumsy_magic"))
    assert cm.roll_base(magus, cm.CREO) == 2
    assert cm.needed(2, 15) == 13 and cm.needed(20, 3) == 1


def test_the_casting_notes_show_the_craft_rolls():
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None
    [line] = [x for x in option_lines(saga, magus) if x.startswith("Craft magic")]
    assert "Rego Perception + Finesse +3" in line
    assert "Creo Intelligence + Finesse +5" in line


def test_the_calculator_rolls_without_keeping_anything():
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None
    form = craft_forms.craft_form(saga, magus, random.Random(3))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert craft_forms.ease_of(values) == 12
    assert craft_forms.lines(magus, values)[0].endswith("the die must reach 9.")
    values.update(technique=cm.CREO, detail=cm.FEW)
    assert craft_forms.ease_of(values) == 3
    said = form.apply(values)
    assert said and "against 3" in said[0]
    assert magus.diary == []
    assert isinstance(craft_forms.craft_form(saga, saga.character("g")), Refuse)
