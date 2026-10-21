"""Original research as a process: a goal's stage, the odds of its chart
rolls, and the Research log each season adds to."""

import json
import random
from dataclasses import asdict

from support import strip_markup
from test_experiment import _Dice, _plan, _saga

from ars_magica_manager import research_text, seasons, sheet_text
from ars_magica_manager.models import (
    Breakthrough,
    Character,
    ResearchAttempt,
    SeasonPlan,
)
from ars_magica_manager.rules import experiment, research


def test_a_goal_s_stage_follows_its_state():
    goal = Breakthrough("Horizon")
    assert research.stage(goal) is research.Stage.NOT_STARTED
    goal.log.append(ResearchAttempt(1220, "Spring", "seek"))
    assert research.stage(goal) is research.Stage.SEEKING
    goal.insights = 1
    assert research.stage(goal) is research.Stage.INSIGHT
    goal.pending_magnitude = 3
    assert research.stage(goal) is research.Stage.DISCOVERY
    goal.stabilizing_seasons = 1
    assert research.stage(goal) is research.Stage.STABILIZING
    goal.retry_season, goal.retry_year = "Summer", 1220
    assert research.stage(goal) is research.Stage.RETRY
    goal.reached = True
    assert research.stage(goal) is research.Stage.REACHED
    assert research.STEPS[research.step(goal)] == "Spread"


def test_a_secret_target_is_not_shown():
    goal = Breakthrough("Horizon", points=12, hidden_target=True)
    assert research.target_text(goal) == "12 points (target kept by the storyguide)"
    assert "/30" not in sheet_text.goal_row(goal)
    goal.reached = True
    assert research.target_text(goal) == "12/30 points"


def test_the_stress_die_s_chances_add_up():
    values = research.stress_values()
    assert abs(sum(values.values()) + research.zero_chance() - 1) < 1e-4
    assert abs(values[2] - 0.1) < 1e-9  # a face of 2; no 1 then 1
    assert abs(values[4] - 0.11) < 1e-3  # a 4, or a 1 then a 2


def test_seeking_odds_grow_with_the_risk():
    one, two, three = (research.seeking_odds(r, 1 + r + 3) for r in (1, 2, 3))
    # Risk +1 reaches 10 from a die of 8-10, less nothing: 8 + 1 = 9, fine.
    assert 0.21 < one.success < 0.23
    # Risk +2: a die of 6 lands on 8, a Complete Failure, so 7-10 only.
    assert 0.32 < two.success < 0.34
    assert one.success < two.success < three.success
    assert abs(two.disaster - 0.1 * (1 - 0.9**6)) < 1e-9
    assert [o.risk for o in research.risk_table(7, 3)] == [1, 2]


def test_stabilizing_odds_avoid_the_harmful_results():
    odds = research.stabilizing_odds(1, 1, 5)
    # Harm on a moved 7 or 8: a die of 5 or 6.
    assert 0.20 < odds.harmful < 0.22
    assert abs(odds.success + odds.harmful + odds.disaster - 1) < 1e-4


def test_the_chart_s_bands():
    assert research.band_of(10).label == "Discovery"
    assert research.band_of(15).tone == "twice"
    assert research.band_of(-1).label == "no effect"


def test_each_season_is_logged_on_the_goal():
    saga = _saga()
    seasons.set_plan(saga, _plan(research="Ignem", risk=2))
    # Die 5; chart 9 + 2 = 11 (modified: 4 + 2), moved -1 to a Discovery.
    worked = seasons.resolve(saga, _Dice(5, 9, 4))
    ((outcome, _),) = seasons.discovery_moves(saga, worked)
    seasons.take_discovery_move(saga, outcome, True)
    seasons.apply(saga, worked)
    (goal,) = saga.character("m").breakthroughs
    (attempt,) = goal.log
    assert (attempt.kind, attempt.work, attempt.die, attempt.roll, attempt.move) == (
        "seek",
        "bolt",
        9,
        11,
        -1,
    )
    assert attempt.discovery and attempt.points == 0
    assert "modified effect" in attempt.result
    assert attempt.botch_dice == 1 + 2


def test_a_stabilization_is_logged_with_its_points_and_warping():
    saga = _saga()
    magus = saga.character("m")
    magus.breakthroughs = [
        Breakthrough(
            "Ignem",
            pending_magnitude=2,
            discovery_lab_total=30,
            discovery_risk=1,
            discovery_shift=1,
            discovered_from=["bolt"],
        )
    ]
    plan = SeasonPlan(
        "m", 1220, "Spring", experiment.STABILIZE, lab_id="lab", research="Ignem"
    )
    seasons.plan_lab_work(saga, plan)
    # Die 2 + 1 = 3, moved +1 = 4: stabilized; Warping 2 - simple die 1 = 1.
    seasons.apply(saga, seasons.resolve(saga, _Dice(2, 1, 9, 9)))
    (attempt,) = magus.breakthroughs[0].log
    assert (attempt.kind, attempt.work, attempt.points, attempt.warping) == (
        "stabilize",
        "bolt",
        2,
        1,
    )
    assert (attempt.risk, attempt.move, attempt.lab_total) == (1, 1, 30)


def test_an_insight_season_is_logged():
    saga = _saga()
    plan = SeasonPlan(
        "m", 1220, "Spring", experiment.INTEGRATE, research="Ignem", die=10
    )
    seasons.set_plan(saga, plan)
    seasons.apply(saga, seasons.resolve(saga, random.Random(0)))
    (attempt,) = saga.character("m").breakthroughs[0].log
    assert (attempt.kind, attempt.die) == ("insight", None)
    assert "an insight" in attempt.result


def test_the_log_survives_a_save():
    goal = Breakthrough("Horizon", hidden_target=True)
    goal.log.append(ResearchAttempt(1220, "Spring", "seek", die=4, risk=1))
    magus = Character(id="m", name="M", type="magus", breakthroughs=[goal])
    again = Character.from_dict(json.loads(json.dumps(asdict(magus))))
    assert again.breakthroughs[0].log[0].roll == 5
    assert again.breakthroughs[0].hidden_target


def _magus_with_research() -> Character:
    magus = Character(id="m", name="Aurelia", type="magus")
    horizon = Breakthrough("Horizon", pending_magnitude=5, discovery_risk=1)
    horizon.discovery_shift = 1
    horizon.log = [
        ResearchAttempt(
            1221,
            "Autumn",
            "seek",
            "far glimpse",
            5,
            31,
            1,
            8,
            2,
            move=1,
            discovery=True,
        ),
        ResearchAttempt(
            1221,
            "Winter",
            "stabilize",
            "far glimpse",
            5,
            31,
            1,
            6,
            2,
            move=1,
            result="8: complete failure.",
        ),
    ]
    event = Breakthrough("Event")
    event.log = [ResearchAttempt(1222, "Spring", "insight", "tablet", insight=True)]
    magus.breakthroughs = [horizon, event]
    return magus


def test_the_research_log_lists_every_goal_s_seasons_newest_first():
    magus = _magus_with_research()
    seasons_ = [(a.season, a.year) for _, a in research_text.log_entries(magus)]
    assert seasons_ == [("Spring", 1222), ("Winter", 1221), ("Autumn", 1221)]
    rows = [strip_markup(text) for _, text in research_text.log_rows(magus)]
    assert rows[0].endswith("insight")
    assert "Stabilize far glimp" in rows[1] and rows[1].endswith("failure")
    assert rows[2].endswith("Discovery")


def test_a_season_s_details_show_its_roll_on_the_chart():
    goal, attempt = research_text.log_entries(_magus_with_research())[1]
    text = research_text.attempt_panel(goal, attempt)
    assert "die 6 + risk 1 = 7, moved +1 = 8" in text
    # The band the moved roll landed in is the one marked.
    assert "[b $text-primary]▸ 8 failure ◂[/]" in text


def test_a_goal_s_details_show_its_steps_and_odds():
    magus = _magus_with_research()
    text = strip_markup(
        research_text.goal_panel(_saga(), magus, magus.breakthroughs[0])
    )
    assert "▶ Stabilize" in text
    assert "Odds of stabilizing (risk +1, move +1" in text
    seeking = research_text.goal_panel(_saga(), magus, Breakthrough("Parma"))
    assert "Odds of a Discovery" in seeking


def _plan_form(saga):
    from ars_magica_manager.forms.lab_plan import LabPlanForm

    magus = saga.character("m")
    return LabPlanForm(saga, magus, saga.laboratories[0], "Spring", 1220, None)


def test_planning_lab_work_offers_the_magus_s_goals_and_the_odds_of_each_risk():
    saga = _saga()
    magus = saga.character("m")
    magus.breakthroughs = [
        Breakthrough("Horizon", kind="Major"),
        Breakthrough("Done", reached=True),
    ]
    form = _plan_form(saga)
    field = next(f for f in form._common_fields() if f.key == "research")
    assert [value for _, value in field.options] == ["Horizon"]
    # Magic Theory 6 allows risk up to +2.
    assert form.risk_hint() == "Chance of a Discovery when seeking one: +1 22%, +2 32%."
    assert form.plan_of({"activity": "x", "research": "Horizon"}).research_kind == (
        "Major"
    )


def test_the_line_above_schedule_gives_the_season_s_odds():
    saga = _saga()
    magus = saga.character("m")
    goal = Breakthrough("Horizon", pending_magnitude=2, discovery_risk=1)
    goal.discovery_shift = 1
    magus.breakthroughs = [goal]
    form = _plan_form(saga)
    seeking = strip_markup(form._odds_line(saga, magus, _plan(research="Horizon")))
    assert seeking.startswith("Odds Discovery 22%")
    stabilizing = SeasonPlan(
        "m", 1220, "Spring", experiment.STABILIZE, lab_id="lab", research="Horizon"
    )
    line = strip_markup(form._odds_line(saga, magus, stabilizing))
    assert line.startswith("Odds stabilized 77%")
    assert "(risk +1 and move +1, as before)" in line
    assert form._odds_line(saga, magus, _plan(research="")) == ""
