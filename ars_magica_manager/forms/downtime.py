"""Downtime runs: advancing the saga several seasons at once, to a chosen
season or to the next Tribunal, the plans repeating (DE p. 528: a pulsed
saga plays a burst of stories, then lets years of downtime pass).

The run takes one backup first, then plays each season out as Advance
Season does, with the same questions; each that changes what its season
does stops the run there to be answered (a covenant in deficit,
interrupted work, a lapsed contested resource, experiment results, a new
laboratory, a mobile covenant's move). Only each Winter's World Turns
review waits: it is rolled in its year and kept, and all of them are asked
together at the end, oldest first. A player character whose plans have run
out stops the run at that season, with their Plan Season form; anyone else
takes the saga's "nothing planned" default, and the end says who. A run
stops before the next Tribunal's season only when that was its end.

Each season played is kept (saved) before the next is asked, so cancelling
a question leaves the seasons already played, with the date where it got
to. The end shows each player character's What changed over the whole run
(what_changed.py).

Pattern: deferred Commands, as world_turns' Proposals are, looped over the
existing season step: the run wraps Advance Season's own steps and goes on
from where each season ends."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from typing import Any

from .. import what_changed, world, world_turns
from ..commands import Confirm, Form, Then, notes
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import SEASONS, Character, Saga, season_order
from ..rules import activities as rules
from ..seasons import plans
from ..seasons.defaults import is_player_character
from . import advance
from . import season as season_forms

TITLE = "Downtime"
HELP_ID = "downtime-run"
SOURCE = "Ars Magica Definitive Edition, pulsed sagas, p. 528"

#: What a run goes to.
TO_SEASON, TO_TRIBUNAL = "season", "tribunal"
#: A run longer than this many years asks first.
LONG_RUN = 10


@dataclass
class Run:
    """A downtime run under way: where it ends (a season order), the dice
    that keep each Winter's review, the player characters as they stood at
    its start, and what it has done so far."""

    saga: Saga
    end: int
    rng: advance.Deferring
    kept: dict[str, dict[str, Any]]
    played: int = 0
    defaulted: list[str] = field(default_factory=list)


def next_tribunal(saga: Saga) -> tuple[str, int] | None:
    """The season and year of the next Tribunal meeting of a troupe
    covenant's Tribunal (any Tribunal when no covenant names one)."""
    homes = {c.tribunal_id for c in world.player_covenants(saga) if c.tribunal_id}
    now = _now(saga)
    found = [
        (season_order(season=t.next_season or SEASONS[0], year=t.next_year), t)
        for t in saga.tribunals
        if t.next_year is not None and (not homes or t.id in homes)
    ]
    found = [(order, t) for order, t in found if order > now]
    if not found:
        return None
    _order, tribunal = min(found, key=lambda pair: pair[0])
    assert tribunal.next_year is not None
    return tribunal.next_season or SEASONS[0], tribunal.next_year


def fields(saga: Saga) -> list[DialogField]:
    meeting = next_tribunal(saga)
    to_options = [("A season I choose", TO_SEASON)]
    if meeting is not None:
        to_options.append(
            (f"The next Tribunal ({meeting[0]} {meeting[1]})", TO_TRIBUNAL)
        )

    def by_season(values: dict[str, Any]) -> bool:
        return values.get("to") != TO_TRIBUNAL

    return [
        DialogField("to", "Run until", "select", TO_SEASON, options=to_options),
        DialogField(
            "season",
            "Season",
            "select",
            saga.current_season,
            options=pairs(SEASONS),
            show_if=by_season,
        ),
        DialogField(
            "year",
            "Year",
            "int",
            saga.current_year + 1,
            show_if=by_season,
            hint="The run stops when the saga reaches this season, before it "
            "is played.",
        ),
    ]


def _end(saga: Saga, values: dict[str, Any]) -> int | None:
    if values.get("to") == TO_TRIBUNAL:
        meeting = next_tribunal(saga)
        return season_order(season=meeting[0], year=meeting[1]) if meeting else None
    return season_order(
        season=values.get("season") or SEASONS[0], year=int(values.get("year") or 0)
    )


def problem(saga: Saga, values: dict[str, Any]) -> str | None:
    end = _end(saga, values)
    if end is None:
        return "No Tribunal meeting is set ahead."
    if end <= _now(saga):
        return "Choose a season after this one."
    return None


def downtime_form(
    saga: Saga,
    backup: advance.Backup = None,
    rng: Callable[[], random.Random] = random.Random,
) -> Form:
    """Run downtime: where to, then (a long run asks first) the run."""

    def apply(values: dict[str, Any]) -> Any:
        end = _end(saga, values)
        assert end is not None
        now = _now(saga)
        start = lambda: _start(saga, end, backup, rng)
        if (end - now) / len(SEASONS) > LONG_RUN:
            return Confirm(
                f"Run {(end - now) // len(SEASONS)} years of downtime? Every "
                "season is played out in turn.",
                start,
                yes_label="Run",
                title=TITLE,
            )
        return start()

    return Form(
        TITLE,
        lambda: fields(saga),
        apply,
        validate=lambda values: problem(saga, values),
        save_label="Run",
        help_id=HELP_ID,
    )


def _start(
    saga: Saga,
    end: int,
    backup: advance.Backup,
    rng: Callable[[], random.Random],
) -> Any:
    if backup is not None:
        backup(saga)
    played = [c for c in saga.characters if is_player_character(c)]
    run = Run(saga, end, advance.Deferring(rng), what_changed.keep_all(saga, played))
    return _season(run)


def _now(saga: Saga) -> int:
    return season_order(season=saga.current_season, year=saga.current_year)


def ran_out(saga: Saga) -> list[Character]:
    """Player characters who plan seasons and have nothing planned for the
    season about to be played."""
    return [
        c
        for c in saga.characters
        if is_player_character(c)
        and rules.is_planned(c)
        and plans.plan_for(saga, c) is None
    ]


def _season(run: Run) -> Any:
    """The next season of the run, or its end."""
    saga = run.saga
    if _now(saga) >= run.end:
        return _finish(run)
    waiting = ran_out(saga)
    if waiting:
        character = waiting[0]
        form = season_forms.plan_season(saga, character)
        return replace(
            form,
            title=f"{form.title} (the run waits: {escape(character.name)}'s "
            "plans have run out)",
            apply=lambda values: _go_on(form.apply(values), run),
        )
    run.defaulted.extend(
        f"{c.name} ({saga.current_season} {saga.current_year})"
        for c in saga.characters
        if rules.is_planned(c)
        and not is_player_character(c)
        and plans.plan_for(saga, c) is None
    )
    return _wrap(advance.play_season(saga, None, run.rng), run)


def _go_on(result: Any, run: Run) -> Any:
    """After a plan is made mid-run: on with the season (a plan form that
    asks more goes on asking first)."""
    if _is_step(result):
        return _wrap(result, run, after=lambda: _season(run))
    return _season(run)


def _is_step(value: object) -> bool:
    return hasattr(value, "apply") and not isinstance(value, advance.Played)


def _wrap(step: Any, run: Run, after: Callable[[], Any] | None = None) -> Any:
    """Advance Season's step `step`, its answer going on through the run:
    a season played out goes on to the next (kept first); `after` is what
    follows a step that ends with nothing (a plan saved)."""
    if isinstance(step, advance.Played):
        return _played(step, run)
    if isinstance(step, Then):
        return Then(_wrap(step.step, run, after))
    if not _is_step(step):
        return after() if after is not None else step
    original = step.apply

    def apply(*given: Any) -> Any:
        return _wrap(original(*given), run, after)

    return replace(step, apply=apply)


def _played(played: advance.Played, run: Run) -> Any:
    run.played += 1
    # Keep each season played before the next is asked.
    following = _season(run)
    return Then(following) if _is_step(following) else following


def _finish(run: Run) -> Any:
    """The run's end: the Winters' reviews, oldest first, then what the
    run did."""
    deferred = list(run.rng.deferred)
    run.rng.deferred.clear()
    return _reviews(run, deferred)


def _reviews(run: Run, deferred: list[advance.Deferred]) -> Any:
    if not deferred:
        return _summary(run)
    first, rest = deferred[0], deferred[1:]
    return world_turns.review(
        run.saga,
        list(first.found),
        lambda: _reviews(run, rest),
        (first.year, first.season),
    )


def _summary(run: Run) -> list[str]:
    saga = run.saga
    lines = [
        f"Downtime: {run.played} season{'' if run.played == 1 else 's'} played; "
        f"it is now {saga.current_season} {saga.current_year}."
    ]
    for character in saga.characters:
        before = run.kept.get(character.id)
        if before is None:
            continue
        changed = what_changed.changes(saga, before, character)
        if changed:
            lines.append(f"{character.name}: {'; '.join(changed)}.")
    if run.defaulted:
        lines.append(
            "With nothing planned, took the saga's default: "
            + ", ".join(run.defaulted)
            + "."
        )
    return notes(*(escape(line) for line in lines))
