"""Needs You: what is waiting on the storyguide, from each source (open
stories, those to revisit, experimental effects to describe, overdue
threat stages), and Open going to the record each is dealt with on."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import attention, threats
from ars_magica_manager.commands import Act, Go, Refuse
from ars_magica_manager.models import (
    STORY_EVENT,
    CovenantDiaryEntry,
    ExperimentalEffect,
    Spell,
)
from ars_magica_manager.rules import experiment


def _saga():
    """The sample saga with its covenant played and nothing else needing
    the storyguide: the Hollow Crown's overdue stage settled."""
    saga = everything_saga()
    saga.current_year, saga.current_season = 1220, "Summer"
    covenant = saga.covenants[0]
    covenant.played = True
    crown = saga.neighbour("crown")
    assert crown is not None
    for stage in threats.stages(crown):
        stage["outcome"] = "Happened"
    return saga, covenant


def _needs(saga):
    return [(i.need, i.title) for i in attention.items(saga)]


def test_nothing_needs_you_says_so():
    saga, _covenant = _saga()
    assert attention.items(saga) == []
    assert attention.title(saga) == "Needs You (0)"
    assert attention.fact(saga).value == "nothing"
    assert attention.grid(saga).empty.startswith("Nothing needs you")


def test_open_stories_come_after_those_to_revisit():
    saga, covenant = _saga()
    covenant.diary += [
        CovenantDiaryEntry(
            1219, "Spring", "Old smoke", category=STORY_EVENT, status="Open"
        ),
        CovenantDiaryEntry(
            1220,
            "Spring",
            "The salamander",
            category=STORY_EVENT,
            status="Open",
            revisit_year=1220,
        ),
        CovenantDiaryEntry(
            1218,
            "Spring",
            "Not yet",
            category=STORY_EVENT,
            status="Open",
            revisit_year=1225,
        ),
        CovenantDiaryEntry(
            1218, "Spring", "Told", category=STORY_EVENT, status="Resolved"
        ),
    ]
    assert _needs(saga) == [
        (attention.REVISIT, "The salamander"),
        (attention.STORY, "Not yet"),
        (attention.STORY, "Old smoke"),
    ]
    item = attention.items(saga)[0]
    assert item.ref is not None and item.ref.id == covenant.id
    assert item.where == f"{covenant.name}'s Diary"
    assert "Revisit year, 1220, has come" in item.detail
    assert attention.fact(saga).value == "3"
    assert attention.grid(saga).styles == {(0, 1): "$text-warning"}


def test_a_story_of_a_covenant_not_played_is_not_listed():
    saga, covenant = _saga()
    covenant.played = False
    covenant.diary.append(
        CovenantDiaryEntry(1219, "Spring", "Elsewhere", category=STORY_EVENT)
    )
    assert attention.items(saga) == []


def test_which_experimental_effects_need_describing():
    side = ExperimentalEffect("side", "minor side benefit")
    special = ExperimentalEffect("special", "the creation changed")
    bare = ExperimentalEffect("modified", "decreased parameter")
    changed = ExperimentalEffect("modified", "increased parameter", range="Voice")
    stronger = ExperimentalEffect("modified", "increased potency", potency=1)
    named = ExperimentalEffect("side", "minor flaw", "It smells of brimstone")
    assert [
        experiment.needs_description(e)
        for e in (side, special, bare, changed, stronger, named)
    ] == [True, True, True, False, False, False]
    assert experiment.describe(special).endswith("(not yet described)")
    assert "(not yet described)" not in experiment.describe(changed)


def test_a_spell_to_describe_opens_through_its_inventor():
    saga, _covenant = _saga()
    magus = saga.character("mag1")
    assert magus is not None
    spell = Spell(
        id="sp-own",
        name="Aurelia's Flame",
        technique="Creo",
        form="Ignem",
        level=10,
        experimental_effects=[
            ExperimentalEffect("side", "minor side benefit"),
            ExperimentalEffect("side", "minor flaw", "Sparks fly"),
        ],
    )
    magus.invented_spells.append(spell)
    [item] = attention.items(saga)
    assert item.need == attention.EFFECT
    assert item.title == "Aurelia's Flame: 1 experimental effect"
    assert item.ref is not None and item.ref.id == magus.id
    assert "Known Spells" in item.where
    spell.experimental_effects[0].description = "It warms the caster"
    assert attention.items(saga) == []


def test_a_saga_spell_no_one_knows_is_not_listed():
    saga, _covenant = _saga()
    saga.spells.append(
        Spell(
            id="sp-lost",
            name="Lost Words",
            technique="Creo",
            form="Ignem",
            level=5,
            experimental_effects=[ExperimentalEffect("side", "minor flaw")],
        )
    )
    assert attention.items(saga) == []


def test_an_item_effect_and_a_bond_power_open_through_holder_and_familiar():
    saga, _covenant = _saga()
    wand = next(d for d in saga.enchanted_devices if d.id == "dev-lab")
    wand.effects[0].experimental_effects.append(
        ExperimentalEffect("side", "major flaw")
    )
    familiar = saga.familiars[0]
    familiar.bond_powers[0].experimental_effects.append(
        ExperimentalEffect("special", "the creation changed")
    )
    items = attention.items(saga)
    assert [(i.title, i.ref and i.ref.kind) for i in items] == [
        ("Wand, Pilum: 1 experimental effect", "laboratories"),
        (f"{familiar.name}, Speak: 1 experimental effect", "familiars"),
    ]


def test_a_dated_stage_pending_after_its_season_is_overdue():
    saga, _covenant = _saga()
    crown = saga.neighbour("crown")
    assert crown is not None
    cattle, ford, _crowning = threats.stages(crown)
    cattle["outcome"] = threats.PENDING
    ford["outcome"] = threats.PENDING
    # Spring 1219 has passed; the ford (Winter 1220) is still to come.
    assert _needs(saga) == [(attention.OVERDUE, "The Hollow Crown: Cattle go missing")]
    [item] = attention.items(saga)
    assert item.ref is not None and item.ref.kind == "neighbours"
    assert "Due Spring 1219" in item.detail
    # A delay of a year and more moves it past now.
    crown.details["delay"] = 6
    assert attention.items(saga) == []
    crown.details["delay"] = 0
    crown.details[threats.DORMANT] = True
    assert attention.items(saga) == []


def test_open_goes_to_the_record_and_refuses_with_none():
    saga, covenant = _saga()
    covenant.diary.append(
        CovenantDiaryEntry(1219, "Spring", "Smoke", category=STORY_EVENT)
    )
    step = attention.ops(saga).edit(0)
    assert isinstance(step, Act)
    end = step.apply()
    assert isinstance(end, Go) and end.ref.id == covenant.id
    assert attention.ops(saga).rows() == ["Smoke"]
    assert isinstance(attention.ops(saga).edit(5), Refuse)
    assert "Smoke" in attention.text(saga, 0)
    assert attention.text(saga, 5) == ""
