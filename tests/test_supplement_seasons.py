"""The supplement activities."""

from ars_magica_manager import seasons
from ars_magica_manager.models import Character, Saga, SeasonPlan, XpAllocation
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import supplement_seasons as sup


def _saga() -> Saga:
    return Saga(
        id="s",
        name="S",
        characters=[Character(id="c", name="Alys", type="companion")],
    )


def _plan(activity, subject="ability:Church Lore", **kw):
    return SeasonPlan(
        "c", 1220, "Spring", activity, [XpAllocation(subject)] if subject else [], **kw
    )


def test_every_supplement_story_has_its_activities():
    stories = {a.story for a in sup.ACTIVITIES}
    assert stories == {
        "913",
        "918",
        "919",
        "920",
        "921",
        "922",
        "923",
        "931",
        "AM-2",
        "FAITH-1",
        "FAITH-2",
        "MOH",
        # The Mysteries Revised Edition's Lesser Elixir.
        "TMRE-1",
        "TMRE-2",
        "TMRE-5",
    }
    assert all(a.key in rules.ACTIVITIES for a in sup.ACTIVITIES)
    assert list(rules.ACTIVITIES)[-1] == rules.OTHER


def test_good_works_gives_2_xp_and_a_faith_point():
    saga = _saga()
    seasons.set_plan(saga, _plan("good_works"))
    seasons.apply(saga, seasons.resolve(saga))
    alys = saga.character("c")
    assert alys.abilities[0].xp == 2 and alys.background.faith_points == 1


def test_worship_needs_the_auras_source_quality():
    saga = _saga()
    alys = saga.character("c")
    found = rules.problems(alys, _plan("worship"), saga)
    assert found == ["Type the Source Quality: the church's Divine aura."]
    worked = rules.outcome(alys, _plan("worship", source_quality=4), saga)
    assert worked.gains[0].result.xp == 4


def test_convalescing_gives_nothing():
    saga = _saga()
    worked = rules.outcome(saga.character("c"), _plan("convalesce", subject=""), saga)
    assert worked.ok and worked.gains == []
