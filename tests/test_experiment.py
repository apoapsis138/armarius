"""Arcane experimentation and original research (STORY-916)."""

import random

import pytest

from ars_magica_manager import seasons
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Breakthrough,
    Character,
    Characteristics,
    Covenant,
    Laboratory,
    Saga,
    SeasonPlan,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import experiment, lab_seasons
from ars_magica_manager.rules.xp import ability_xp, art_xp


class _Dice(random.Random):
    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):
        return self.faces.pop(0) if self.faces else 5


def _saga() -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=2)
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(6))]  # risk up to +2
    magus.arts = {"creo": ArtScore(xp=art_xp(10)), "ignem": ArtScore(xp=art_xp(10))}
    magus.assigned_lab_id = "lab"
    lab = Laboratory(id="lab", covenant_id="cov", name="Tower", owner_id="m")
    saga = Saga(
        id="s", name="S", covenants=[covenant], characters=[magus], laboratories=[lab]
    )
    saga.spells = [Spell("bolt", "Bolt", "Creo", "Ignem", level=10)]
    return saga


def _plan(**kw):
    values = {"lab_id": "lab", "spell_id": "bolt", "experimenting": True, "risk": 1}
    return SeasonPlan("m", 1220, "Spring", lab_seasons.INVENT, **(values | kw))


def test_the_risk_modifier_is_limited_by_magic_theory_when_seeking():
    assert [experiment.max_risk(mt) for mt in (1, 5, 6, 10, 11)] == [1, 1, 2, 2, 3]
    saga = _saga()
    magus = saga.character("m")
    found, _ = lab_seasons.work(saga, magus, _plan(risk=3, research="Ignem"))
    assert found == [
        "The risk modifier is 0 to +2 (by Magic Theory, seeking a Discovery)."
    ]
    # Plain experimenting: 0 to +3 whatever Magic Theory.
    assert lab_seasons.work(saga, magus, _plan(risk=3))[0] == []
    assert lab_seasons.work(saga, magus, _plan(risk=4))[0] == [
        "The risk modifier is 0 to +3."
    ]


def test_averse_to_risk_forbids_and_prone_to_chance_requires_experimenting():
    saga = _saga()
    magus = saga.character("m")
    magus.virtues_flaws = [VirtueFlawInstance(experiment.AVERSE)]
    assert lab_seasons.work(saga, magus, _plan())[0] == [
        "Tiberius is Averse to Risk: no experimenting."
    ]
    magus.virtues_flaws = [VirtueFlawInstance(experiment.PRONE)]
    assert lab_seasons.work(saga, magus, _plan(experimenting=False))[0] == [
        "Tiberius is Prone to Chance: this lab work must be experimental."
    ]


def test_cautious_sorcerer_rolls_three_fewer_botch_dice():
    magus = _saga().character("m")
    assert experiment.botch_dice(magus, 2, 3) == 6
    magus.virtues_flaws = [VirtueFlawInstance(experiment.CAUTIOUS)]
    assert experiment.botch_dice(magus, 2, 3) == 3
    assert experiment.botch_dice(magus, 0, 1) == 1  # never below one


def test_a_two_dice_flaw_shows_both_results():
    magus = _saga().character("m")
    magus.virtues_flaws = [VirtueFlawInstance("vf_creative_block")]
    # First roll 3 + 1 = 4; the second 8 + 1 = 9.
    chart = experiment.chart(_Dice(3, 8), 1, 0, "Creo", character=magus)
    assert chart.results[0] == "4: no extraordinary effects."
    assert chart.second == ["9: a special result or story event (storyguide)."]
    assert "The storyguide may use it instead." in chart.results[-1]


def test_experimenting_adds_a_simple_die_and_the_risk():
    saga = _saga()
    _, work = lab_seasons.work(saga, saga.character("m"), _plan(experiment_die=4))
    assert int(work.lab_total.total) == 10 + 10 + 2 + 6 + 4 + 1


def test_a_complete_failure_wastes_the_season():
    saga = _saga()
    seasons.set_plan(saga, _plan())
    # Simple die 5 for the Lab Total; the chart's stress die 7 + risk 1 = 8.
    worked = seasons.resolve(saga, _Dice(5, 7))
    assert "complete failure" in worked[0].notes[-1]
    seasons.apply(saga, worked)
    assert saga.character("m").spells_known == []
    assert saga.laboratories[0].diary[-1].name == "Arcane Experimentation"


def test_a_discovery_gives_experience_and_a_research_discovery():
    saga = _saga()
    seasons.set_plan(
        saga, _plan(research="Ignem at Arcane range", research_kind="Major")
    )
    # Die 5; chart 9 + 1 = 10: a Discovery; its sub-table 2 + 1 = 3: 15 xp MT.
    seasons.apply(saga, seasons.resolve(saga, _Dice(5, 9, 2)))
    magus = saga.character("m")
    mt = next(a for a in magus.abilities if a.name == "Magic Theory")
    assert mt.xp == ability_xp(6) + 15 + 2  # the Discovery and Exposure
    (goal,) = magus.breakthroughs
    assert (goal.name, goal.kind, goal.target) == ("Ignem at Arcane range", "Major", 45)
    # Seeking a Discovery, the risk goes on the chart, not the Lab Total.
    assert (goal.pending_magnitude, goal.discovery_lab_total) == (
        2,
        10 + 10 + 2 + 6 + 5,
    )
    assert [k.spell_id for k in magus.spells_known] == ["bolt"]


def test_a_roll_the_risk_can_move_onto_ten_is_asked_about():
    saga = _saga()
    seasons.set_plan(saga, _plan(research="Ignem"))
    # Die 5; chart 8 + 1 = 9: one away from 10, within the risk.
    worked = seasons.resolve(saga, _Dice(5, 8))
    ((outcome, question),) = seasons.discovery_moves(saga, worked)
    assert "moving its roll +1" in question
    seasons.take_discovery_move(saga, outcome, True)
    assert seasons.discovery_moves(saga, worked) == []
    seasons.apply(saga, worked)
    (goal,) = saga.character("m").breakthroughs
    assert (goal.discovery_shift, goal.pending_magnitude) == (1, 2)


def test_declining_the_move_keeps_the_roll():
    saga = _saga()
    seasons.set_plan(saga, _plan(research="Ignem"))
    worked = seasons.resolve(saga, _Dice(5, 8))
    ((outcome, _),) = seasons.discovery_moves(saga, worked)
    seasons.take_discovery_move(saga, outcome, False)
    seasons.apply(saga, worked)
    (goal,) = saga.character("m").breakthroughs
    assert (goal.discovery_shift, goal.pending_magnitude) == (0, 0)


def test_a_move_taken_is_made_again_without_asking():
    saga = _saga()
    saga.character("m").breakthroughs = [Breakthrough("Ignem", discovery_shift=1)]
    seasons.set_plan(saga, _plan(research="Ignem"))
    # Chart 8 + 1 = 9, moved +1 as before: a Discovery (sub-table 2 + 1: MT).
    worked = seasons.resolve(saga, _Dice(5, 8, 2))
    assert seasons.discovery_moves(saga, worked) == []
    seasons.apply(saga, worked)
    assert saga.character("m").breakthroughs[0].pending_magnitude == 2


def test_stabilizing_adds_the_magnitude_and_warps():
    saga = _saga()
    magus = saga.character("m")
    magus.breakthroughs = [
        Breakthrough(
            "Ignem",
            pending_magnitude=4,
            discovery_lab_total=30,
            discovery_technique="Creo",
            discovery_form="Ignem",
        )
    ]
    plan = SeasonPlan(
        "m", 1220, "Spring", experiment.STABILIZE, lab_id="lab", research="Ignem"
    )
    seasons.plan_lab_work(saga, plan)
    # Chart 3 + 0: nothing; Warping 4 - simple die 1 = 3 (then Twilight rolls).
    seasons.apply(saga, seasons.resolve(saga, _Dice(3, 1, 9, 0)))
    goal = magus.breakthroughs[0]
    assert (goal.points, goal.pending_magnitude) == (4, 0)
    assert magus.aging.warping_points + 5 * magus.aging.warping_score >= 3
    text = saga.books[-1]
    assert text.name == "Lab Text: Discovery toward Ignem"
    assert (text.text_kind, text.technique, text.form) == ("Other", "Creo", "Ignem")


def test_stabilizing_repeats_the_experiment_s_seasons_and_vis():
    saga = _saga()
    magus = saga.character("m")
    magus.raw_vis = {"creo": 3}
    magus.breakthroughs = [
        Breakthrough(
            "Ignem",
            pending_magnitude=2,
            discovery_seasons=2,
            discovery_lab_total=30,
            discovery_vis=2,
            discovery_vis_art="Creo",
        )
    ]
    plan = SeasonPlan(
        "m", 1220, "Spring", experiment.STABILIZE, lab_id="lab", research="Ignem"
    )
    _, work = lab_seasons.work(saga, magus, plan)
    assert (int(work.lab_total.total), work.vis_cost, work.finished) == (
        30,
        {"Creo": 2},
        False,
    )
    seasons.plan_lab_work(saga, plan)
    seasons.apply(saga, seasons.resolve(saga, _Dice(3)))
    goal = magus.breakthroughs[0]
    assert (goal.stabilizing_seasons, goal.points, magus.raw_vis["creo"]) == (1, 0, 1)


def test_seeking_an_insight():
    saga = _saga()
    plan = SeasonPlan(
        "m", 1220, "Spring", experiment.INTEGRATE, research="Ignem", die=10
    )
    assert rules.problems(saga.character("m"), plan, saga) == []
    seasons.set_plan(saga, plan)
    seasons.apply(saga, seasons.resolve(saga))
    assert saga.character("m").breakthroughs[0].insights == 1  # 2 + 6 + 10 = 18


def test_an_insight_s_invention_adds_its_magnitude_and_grants_the_goal():
    saga = _saga()
    magus = saga.character("m")
    magus.breakthroughs = [
        Breakthrough(
            "Ignem",
            target=5,
            points=3,
            insights=1,
            grant_kind="Ability",
            grant="Ignem Lore",
        )
    ]
    seasons.set_plan(saga, _plan(research="Ignem"))
    seasons.apply(saga, seasons.resolve(saga, _Dice(5, 3)))  # chart 3 + 1: nothing
    goal = magus.breakthroughs[0]
    assert (goal.points, goal.insights, goal.reached) == (5, 0, True)
    lore = next(a for a in magus.abilities if a.name == "Ignem Lore")
    assert lore.xp == 5


def test_a_disaster_loses_the_invention_so_far():
    saga = _saga()
    saga.spells[0].level = 25  # three seasons
    seasons.set_plan(saga, _plan())
    # Die 5; the chart botches: 2 botch dice (1 + risk 1), both 0.
    seasons.apply(saga, seasons.resolve(saga, _Dice(5, 0, 0, 0)))
    assert saga.lab_projects == []
    assert "The work so far is lost." in saga.laboratories[0].diary[-1].details


def test_an_explosion_wounds_everyone_and_wrecks_the_lab():
    saga = _saga()
    seasons.set_plan(saga, _plan(risk=3))
    # The chart botches with all 4 botch dice at 0.
    seasons.apply(saga, seasons.resolve(saga, _Dice(5, 0, 0, 0, 0, 0)))
    magus = saga.character("m")
    assert magus.wounds.heavy == 2
    assert "labvf_wrecked" in [vf.vf_id for vf in saga.laboratories[0].virtues_flaws]


def test_an_invented_spell_keeps_its_side_effect():
    saga = _saga()
    seasons.set_plan(saga, _plan())
    # Die 5; chart 4 + 1 = 5: a side effect (the table's entry for a 3).
    seasons.apply(saga, seasons.resolve(saga, _Dice(5, 4, 3)))
    magus = saga.character("m")
    (known,) = magus.spells_known
    spell = next(s for s in magus.invented_spells if s.id == known.spell_id)
    assert spell.experimental_effects == [f"Side effect: {experiment.SIDE_EFFECTS[3]}"]


# -- the Extraordinary Results chart, roll by roll (STORY-1129) ------------------


def _chart(roll: int, *faces: int, risk: int = 0) -> experiment.Extraordinary:
    """The chart's result for `roll` (already die + risk), its later dice
    showing `faces` (simple-die faces: 0 reads as 10)."""
    result = experiment.Extraordinary()
    experiment._apply(result, roll, _Dice(*faces), risk, "Ignem", None, 0)
    return result


def test_low_rolls_have_no_extraordinary_effect():
    assert _chart(4).results == ["4: no extraordinary effects."]


def test_a_five_or_six_is_a_side_effect():
    result = _chart(5, 1)
    assert result.effects == ["Side effect: sigil greatly exaggerated"]


def test_a_seven_is_no_benefit_and_a_nine_is_the_storyguides():
    assert _chart(7).no_benefit
    assert _chart(9).results == ["9: a special result or story event (storyguide)."]


def test_a_discovery_gives_experience_by_its_roll():
    def xp(face: int, risk: int = 0):
        return _chart(10, face, risk=risk).xp

    assert xp(4) == [("ability:Magic Theory", 15)]
    assert xp(6) == [("ability:Magic Theory", 15)]
    assert xp(8) == [("art:Ignem", 3)]
    assert xp(9) == [("art:Ignem", 3)]
    assert xp(9, risk=1) == [("ability:Magic Theory", 15)]  # two more rolls
    assert "15 xp in an Ability related to it" in _chart(10, 6).results[0]
    assert "raise Ignem to its next score" in _chart(10, 9).results[0]
    assert "two more Discovery rolls" in _chart(10, 0).results[0]  # 0 reads 10


def test_an_eleven_modifies_the_effect():
    assert _chart(11, 2).effects == [
        "Modified effect: reduced range, duration, target or potency"
    ]


@pytest.mark.xfail(
    strict=True,
    reason="B25: the modified-effect table rolls a new die for each row it "
    "checks, not one die for the table (experiment._apply, roll 11)",
)
def test_an_eleven_rolls_one_die_for_the_modified_effect():
    # One die of 10 (face 0) + risk 2 = 12: past every row, so the last.
    assert _chart(11, 0, 1, 1, 1, risk=2).effects == [
        "Modified effect: effect changed completely (same Technique and Form, "
        "similar level)"
    ]


def test_twelve_or_more_rolls_twice_more():
    # Each further roll is a stress die (no botch dice) + the risk.
    result = _chart(12, 3, 4)
    assert result.results == [
        "12: roll twice more.",
        "3: no extraordinary effects.",
        "4: no extraordinary effects.",
    ]


def test_three_zeroes_damage_the_lab():
    # A stress die of 0, then three botch dice of 0 among the four.
    result = experiment.Extraordinary()
    experiment._roll_once(
        result, _Dice(0, 0, 0, 0, 5), 0, 4, "Ignem", None, False, None
    )
    assert (result.zeroes, result.lab_flaw) == (3, "labvf_damaged")
    assert "the lab is Damaged" in result.results[0]


def test_a_move_onto_ten_made_before_is_made_again():
    # Seeking with the project's move so far (+1): a 9 becomes the Discovery.
    result = experiment.Extraordinary()
    experiment._roll_once(result, _Dice(9, 3), 0, 1, "Ignem", None, True, 1)
    assert result.results[0] == "The roll 9 moved by +1, as before."
    assert result.discovery


def test_goals_are_found_by_name_and_made_when_new():
    magus = _saga().character("m")
    assert experiment.find_goal(magus, "Ignem Mastery") is None
    made = experiment.goal(magus, " Ignem Mastery ", "Major")
    assert (made.name, made.target) == ("Ignem Mastery", 45)
    assert experiment.find_goal(magus, "ignem mastery") is made
    assert experiment.goal(magus, "IGNEM MASTERY") is made


def test_an_insight_roll():
    saga = _saga()
    magus = saga.character("m")

    def roll(die):
        return experiment.insight_roll(magus, _plan(die=die), None, 6)

    assert roll(0) == (False, "Botch: a false insight (it seems real until tried).")
    assert roll(10) == (True, "18 against 18: an insight.")  # Int 2 + MT 6 + 10
    assert roll(9) == (False, "17 against 18: nothing this season.")
    rolled, text = experiment.insight_roll(magus, _plan(), _Dice(9), 6)
    assert (rolled, text) == (False, "17 against 18: nothing this season.")
