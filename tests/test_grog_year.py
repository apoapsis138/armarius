"""The grogs' yearly update (STORY-924)."""

from ars_magica_manager import seasons
from ars_magica_manager.models import Ability, Character, GrogYear, Saga
from ars_magica_manager.rules.xp import ability_xp


def _saga(**year) -> Saga:
    grog = Character(id="g", name="Hugo", type="grog")
    grog.abilities = [Ability("Single Weapon", xp=ability_xp(3))]
    grog.grog_year = GrogYear(
        vocational="Single Weapon", practice="Brawl", exposure="Awareness", **year
    )
    saga = Saga(id="s", name="S", characters=[grog])
    saga.current_season = "Winter"
    return saga


def _xp(grog, name):
    return next((a.xp for a in grog.abilities if a.name == name), 0)


def test_winter_gives_the_yearly_xp():
    saga = _saga()
    lines = seasons.year_end_grogs(saga)
    grog = saga.character("g")
    assert _xp(grog, "Single Weapon") == ability_xp(3) + 7
    assert (_xp(grog, "Brawl"), _xp(grog, "Awareness")) == (4, 2)
    assert lines[0].result == "Single Weapon +7, Brawl +4, Awareness +2"


def test_story_awards_take_seasons_in_order():
    saga = _saga(story_awards=2)  # exposure, then vocational
    seasons.year_end_grogs(saga)
    grog = saga.character("g")
    assert (_xp(grog, "Single Weapon"), _xp(grog, "Awareness")) == (ability_xp(3), 0)
    assert _xp(grog, "Brawl") == 4
    assert grog.grog_year.story_awards == 0  # cleared for the new year


def test_the_planning_tab_shows_the_update():
    text = seasons.plan_text(_saga(), _saga().character("g"))
    assert "Yearly update (applied in Winter)" in text
    assert "Brawl +4 xp (practice)" in text
