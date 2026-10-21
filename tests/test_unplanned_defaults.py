"""A season left unplanned: the saga's default for each kind of character
(Work / Exposure, or Nothing), who Advance Season names (player
characters, and the others when the saga says so), the Unplanned Seasons
step's choices, and a grog's default year."""

from __future__ import annotations

import random

from ars_magica_manager import seasons
from ars_magica_manager.commands import Form
from ars_magica_manager.forms import advance as advance_forms
from ars_magica_manager.forms import creation as creation_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Saga,
    SeasonPlan,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.seasons import defaults


def _saga() -> Saga:
    magus = Character(id="m", name="Tiberius", type="magus")
    magus.abilities = [
        Ability("Latin", xp=ability_xp(4)),
        Ability("Magic Theory", xp=ability_xp(3)),
    ]
    scribe = Character(id="c", name="Bertram", type="companion")
    scribe.abilities = [
        Ability("Brawl", xp=ability_xp(3)),
        Ability("Profession: Scribe", xp=ability_xp(2)),
    ]
    scribe.background.player = "Hedda"
    grog = Character(id="g", name="Odo", type="grog")
    grog.abilities = [Ability("Single Weapon", xp=ability_xp(3))]
    return Saga(
        id="test_saga",
        name="Gaps",
        current_year=1220,
        current_season="Spring",
        characters=[magus, scribe, grog],
    )


def _advance(saga, answers=None) -> tuple[list[Form], advance_forms.Played]:
    """Advance a season, answering Unplanned Seasons with `answers` (and
    any Plan Season it opens with an Exposure in Brawl)."""
    asked: list[Form] = []
    step = advance_forms.play_season(saga, rng=lambda: random.Random(1))
    while isinstance(step, Form):
        asked.append(step)
        values = {f.key: f.value for f in step.fields() if f.kind != "info"}
        if step.title == "Unplanned Seasons":
            values.update(answers or {})
        elif step.title.startswith("Plan "):
            values.update(activity=rules.EXPOSURE, subject_1="ability:Brawl")
        step = step.apply(values)
    assert isinstance(step, advance_forms.Played)
    return asked, step


def _titles(asked: list[Form]) -> list[str]:
    return [f.title for f in asked]


def test_the_default_goes_into_the_profession_then_magic_theory_then_the_highest():
    saga = _saga()
    magus, scribe, _ = saga.characters
    assert defaults.exposure_ability(scribe) == "Profession: Scribe"
    assert defaults.exposure_ability(magus) == "Magic Theory"
    magus.abilities = magus.abilities[:1]
    assert defaults.exposure_ability(magus) == "Latin"
    magus.abilities.append(Ability("Profession: Scribe", xp=ability_xp(1)))
    assert defaults.exposure_ability(magus) == "Profession: Scribe"
    scribe.abilities = [
        Ability("Living Language: French", xp=ability_xp(5)),
        Ability("Brawl", xp=ability_xp(2)),
    ]
    assert defaults.exposure_ability(scribe) == "Brawl"
    scribe.abilities = scribe.abilities[:1]
    assert defaults.exposure_ability(scribe) == "Living Language: French"
    scribe.abilities = [Ability("Profession: Scribe", xp=ability_xp(2))]
    assert defaults.default_text(saga, scribe) == (
        "Work / Exposure in Profession: Scribe"
    )
    saga.unplanned_companions = defaults.NOTHING
    assert defaults.default_text(saga, scribe) == "nothing"


def test_only_player_characters_are_named_by_default():
    saga = _saga()
    assert [c.name for c in defaults.notified(saga)] == ["Bertram"]
    summary = seasons.advance_summary(saga)
    assert "Bertram (companion: Work / Exposure in Profession: Scribe)" in summary
    assert "Tiberius" not in summary
    saga.notify_npc_unplanned = True
    assert [c.name for c in defaults.notified(saga)] == ["Tiberius", "Bertram"]


def test_the_unnamed_take_the_default_and_the_diary_says_so():
    saga = _saga()
    magus, scribe, _ = saga.characters
    asked, _ = _advance(saga)
    step = next(f for f in asked if f.title == "Unplanned Seasons")
    labels = [f.label for f in step.fields()]
    assert "Bertram (companion)" in labels and not any("Tiberius" in x for x in labels)
    assert magus.diary[-1].name.endswith("(default)")
    assert magus.diary[-1].activity == "Work / Exposure"
    assert scribe.diary[-1].name.endswith("(default)")
    assert "Scribe" in scribe.diary[-1].details


def test_nothing_leaves_the_season_empty():
    saga = _saga()
    _, scribe, _ = saga.characters
    _advance(saga, {"gap_0": advance_forms.NOTHING})
    assert scribe.diary == []


def test_plan_it_now_opens_plan_season_and_carries_on():
    saga = _saga()
    _, scribe, _ = saga.characters
    asked, played = _advance(saga, {"gap_0": advance_forms.PLAN_NOW})
    assert "Plan Bertram's Season (Spring 1220)" in _titles(asked)
    assert scribe.diary[-1].activity == "Work / Exposure"
    assert not scribe.diary[-1].name.endswith("(default)")
    assert "Summer 1220" in played.message


def test_a_saga_set_to_nothing_asks_nobody_and_plans_nothing():
    saga = _saga()
    magus, scribe, _ = saga.characters
    saga.unplanned_magi = defaults.NOTHING
    scribe.background.player = ""
    asked, _ = _advance(saga)
    assert "Unplanned Seasons" not in _titles(asked)
    assert magus.diary == []
    assert scribe.diary[-1].name.endswith("(default)")


def test_a_broken_plan_can_be_planned_again():
    saga = _saga()
    _, scribe, _ = saga.characters
    seasons.set_plan(saga, SeasonPlan("c", 1220, "Spring", rules.READ, book_id="x"))
    asked, _ = _advance(saga, {"fix_0": advance_forms.PLAN_NOW})
    step = next(f for f in asked if f.title == "Unplanned Seasons")
    assert any(f.key == "fix_0" for f in step.fields())
    assert scribe.diary[-1].activity == "Work / Exposure"


def test_a_grog_with_no_yearly_update_gains_the_default_in_winter():
    saga = _saga()
    grog = saga.characters[2]
    saga.current_season = "Winter"
    before = grog.abilities[0].xp
    seasons.year_end_grogs(saga)
    assert grog.abilities[0].xp == before + 8
    assert grog.diary[-1].name == "Yearly update (default): Single Weapon +8"
    saga.unplanned_grogs = defaults.NOTHING
    seasons.year_end_grogs(saga)
    assert grog.abilities[0].xp == before + 8


def test_edit_saga_offers_the_settings():
    saga = _saga()
    fields = {f.key: f for f in creation_forms.saga_fields(saga)}
    assert fields["unplanned_magi"].value == defaults.EXPOSURE
    assert fields["notify_npc_unplanned"].value is False
    creation_forms.apply_saga(
        saga, {"unplanned_grogs": defaults.NOTHING, "notify_npc_unplanned": True}
    )
    assert saga.unplanned_grogs == defaults.NOTHING and saga.notify_npc_unplanned
