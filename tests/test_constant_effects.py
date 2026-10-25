"""Constant supernatural effects warp a character each year (DE pp.
390-391), and a Warping laboratory's Personality Traits add up to its
Warping (DE p. 289)."""

import random

from ars_magica_manager import catalog, seasons
from ars_magica_manager import laboratories as labs
from ars_magica_manager.forms import constant_effect as constant_forms
from ars_magica_manager.models import (
    Character,
    ConstantEffect,
    Covenant,
    Laboratory,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import warping


def test_each_constant_effect_warps_a_point_a_year():
    assert warping.constant_points(ConstantEffect("Ward")) == 1
    assert warping.constant_points(ConstantEffect("Ring", powerful=True)) == 5
    made_for = ConstantEffect("Ring", powerful=True, designed_for=True)
    assert warping.constant_points(made_for) == 1
    assert warping.first_point(ConstantEffect("Ring", powerful=True)) == 1
    assert warping.first_point(made_for) == 0


def _saga() -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    grog = Character(id="g", name="Hob", type="grog", covenant_id="cov")
    return Saga(id="s", name="S", covenants=[covenant], characters=[grog])


def test_the_years_end_adds_their_warping():
    saga = _saga()
    grog = saga.character("g")
    grog.constant_effects = [
        ConstantEffect("Ring of Flight", realm="Faerie", powerful=True),
        ConstantEffect("Ward"),
    ]
    saga.current_season = "Winter"
    seasons.year_end_aging(saga, random.Random(0))
    assert warping.total_points(grog) == 6
    assert any("Ring of Flight 5" in entry.details + entry.name for entry in grog.diary)


def test_adding_a_powerful_effect_gives_its_first_point():
    saga = _saga()
    grog = saga.character("g")
    form = constant_forms.ops(saga, grog).add()
    form.apply({"name": "Ring", "realm": "Magic", "powerful": True})
    assert [e.name for e in grog.constant_effects] == ["Ring"]
    assert warping.total_points(grog) == 1
    form = constant_forms.ops(saga, grog).add()
    form.apply({"name": "Ward", "realm": "Magic", "powerful": False})
    assert warping.total_points(grog) == 1


def test_a_warping_labs_traits_should_add_up_to_its_warping():
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    saga = _saga()
    lab = Laboratory(
        id="lab",
        covenant_id="cov",
        name="Tower",
        virtues_flaws=[VirtueFlawInstance("labvf_shrouded")],  # Warping +1
    )
    assert "should add up to +1 (+0 now" in labs.traits_warning(lab, by_id, saga)
    lab.personality_traits = [ScoredTrait("Secretive", 1)]
    assert labs.traits_warning(lab, by_id, saga) == ""
    assert (
        labs.traits_warning(
            Laboratory(id="x", covenant_id="cov", name="X"), by_id, saga
        )
        == ""
    )
