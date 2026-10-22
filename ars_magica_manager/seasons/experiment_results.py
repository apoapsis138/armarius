"""The storyguide's word on each experiment of the season, asked before the
season is played out (Advance Season's Experiment results step): which of
two rolls stands, what each side or modified effect is, where a
Discovery's experience goes, what a special result becomes, a Disaster's
choice, and whether to move the roll onto a Discovery.

The chart is rolled when the season's outcomes are worked out; nothing is
applied until the season is played, so the answers change the outcome
first (seasons.lab_apply applies it).
"""

from __future__ import annotations

import random
from collections.abc import Sequence

from .. import spells as spl
from ..models import Character, Saga
from ..rules import activities as rules
from ..rules import dice, lab_seasons
from ..rules import experiment as ex
from ..rules import lab as lab_rules
from .lab_apply import take_discovery_move


def experiments_to_settle(
    saga: Saga, worked: Sequence[rules.Outcome]
) -> list[rules.Outcome]:
    """The season's experiments with something for the storyguide to
    decide (see Extraordinary.choices)."""
    found = []
    for outcome in worked:
        work = outcome.lab_work
        chart = work.experiment if work is not None else None
        if chart is None or saga.character(outcome.character_id) is None:
            continue
        if chart.choices:
            found.append(outcome)
    return found


def vis_needed(outcome: rules.Outcome) -> int:
    """The extra vis a special result can ask of the work: the effect's
    magnitude (with its modifications) plus the risk modifier."""
    work = outcome.lab_work
    assert work is not None
    return spl.level_magnitude(work.level) + max(0, outcome.plan.risk)


def vis_to_hand(saga: Saga, magus: Character, outcome: rules.Outcome) -> dict[str, int]:
    """The vis of the work's Technique and Form left to the magus once the
    season's own vis is paid ({Art: pawns})."""
    work = outcome.lab_work
    assert work is not None
    pool = lab_seasons.vis_pool(saga, magus, outcome.plan)
    paid = {art.lower(): pawns for art, pawns in work.vis_cost.items()}
    found: dict[str, int] = {}
    for art in lab_seasons.made_arts(work, outcome.plan):
        left = pool.get(art.lower(), 0) - paid.get(art.lower(), 0)
        if left > 0:
            found[art] = left
    return found


def bonus_spell_limit(outcome: rules.Outcome) -> int:
    """The highest level of the spell a special result lets the magus also
    create: one they could invent in a single season (half the Lab Total)."""
    work = outcome.lab_work
    assert work is not None
    return int(work.lab_total.total) // 2


def settle_experiment(
    saga: Saga,
    outcome: rules.Outcome,
    settlement: ex.Settlement,
    rng: random.Random | None = None,
) -> None:
    """Record the storyguide's answers on the outcome: the roll that
    stands (its work worked out again), its effects and Discoveries as
    chosen, the extra vis paid or, without it, a Complete Failure, and the
    move onto a Discovery taken or declined."""
    character = saga.character(outcome.character_id)
    work = outcome.lab_work
    if character is None or work is None or work.experiment is None:
        return
    if settlement.second and work.experiment.other is not None:
        work.experiment = ex.take_other(work.experiment)
        rules.settle_chart(outcome, character, saga)
        work = outcome.lab_work
        assert work is not None and work.experiment is not None
    chart = work.experiment
    ex.settle(chart, settlement, character)
    for special in settlement.specials[: chart.specials]:
        if special.kind == "vis" and not chart.wasted:
            _extra_vis(saga, character, outcome, chart, rng or random.Random())
    if chart.discovery_shift is not None:
        take_discovery_move(saga, outcome, settlement.move)
    rules.settle_chart(outcome, character, saga)


def _extra_vis(
    saga: Saga,
    magus: Character,
    outcome: rules.Outcome,
    chart: ex.Extraordinary,
    rng: random.Random,
) -> None:
    """The extra vis a special result asks for, from the Technique's vis or
    else the Form's; without enough (or more than the magus can handle in
    a season) it is a Complete Failure."""
    need = vis_needed(outcome)
    to_hand = vis_to_hand(saga, magus, outcome)
    for art, pawns in chart.extra_vis.items():
        to_hand[art] = to_hand.get(art, 0) - pawns
    work = outcome.lab_work
    assert work is not None
    handled = sum(work.vis_cost.values()) + sum(chart.extra_vis.values())
    limit = lab_rules.vis_limit(magus)
    art = next((a for a, left in to_hand.items() if left >= need), None)
    if art is not None and handled + need <= limit:
        chart.extra_vis[art] = chart.extra_vis.get(art, 0) + need
        chart.results.append(
            f"The work needs {need} more pawn(s) of vis: paid in {art}."
        )
        return
    chart.wasted = chart.failure = True
    chart.failure_die = dice.simple_die(rng) % 10
    chart.results.append(
        f"The work needs {need} more pawn(s) of {' or '.join(to_hand) or 'its Arts'} "
        "vis, which can't be had or handled this season: a Complete Failure "
        "(the season is wasted)."
    )
