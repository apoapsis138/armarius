"""Advance Season as the core's command steps (commands.py), so the
terminal and the desktop play a season out the same way.

The question first (what the season's plans will do, and the new year's
note), then, at the year's end with a covenant in deficit, whether to
advance anyway; then whether each contested resource whose security
lapsed was secured, whether to take each Discovery an experiment's
risk can reach, and whether each magus setting up a new laboratory
spends the next season finishing it. Only then is the season played out (seasons.finish_season)
and the date moved on. The last step ends with `Played`: what the season
did and the line saying so, for the front-end to show the season's
results.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .. import economics as eco
from .. import seasons, tribunal_terms, world_turns
from ..commands import Command, Confirm, Form
from ..form_spec import DialogField
from ..markup import escape
from ..models import SEASONS, Saga, next_season
from ..rules import laboratory_seasons as ls
from ..rules.activities import Outcome
from ..seasons.advance import Advanced

#: Backs the saga up before a season with plans is applied
#: (storage.backup_saga), or None not to.
Backup = Callable[[Saga], object] | None


@dataclass(frozen=True)
class Played:
    """What advancing did: the season played out and the line telling
    the new date, whose seasons were applied and what Wealth gained."""

    advanced: Advanced
    message: str
    #: Whether there is anything to show: a plan worked out, or the
    #: year's or the covenants' lines.
    results: bool


@dataclass(frozen=True)
class AdvanceText:
    """The Advance Season question's parts (markup; "" for none)."""

    question: str
    plans: str
    year_note: str
    note: str

    def whole(self) -> str:
        return "\n\n".join(
            part
            for part in (self.question, self.plans, self.year_note, self.note)
            if part
        )


def advance_text(saga: Saga) -> AdvanceText:
    """What advancing from the saga's date will do, to ask first."""
    season, year = saga.current_season, saga.current_year
    new_season, new_year = next_season(season, year)
    plans = seasons.advance_summary(saga)
    new = new_year != year
    return AdvanceText(
        f"Advance the saga from {season} {year} to {new_season} {new_year}?",
        plans,
        "A new year: each covenant's surplus is added to its Wealth, "
        "and Emergency Savings start again at 0."
        if new
        else "",
        "[dim]Advanced by mistake? Set Date (More on the saga) puts the date back"
        + (" (Wealth isn't changed back)." if new else ".")
        + (
            " The saga is backed up first (sagas/backups in your data folder)."
            if plans
            else ""
        )
        + "[/]",
    )


def advance_season(
    saga: Saga, backup: Backup = None, rng: Callable[[], random.Random] = random.Random
) -> Confirm:
    """Advance the saga by one season: asked first, then played out."""
    return Confirm(
        advance_text(saga).whole(),
        lambda: play_season(saga, backup, rng),
        yes_label="Advance",
        title="Advance Time",
    )


def deficit_question(in_deficit: list[tuple[str, int]]) -> str:
    lines = "\n".join(f"  {escape(name)}: {deficit}" for name, deficit in in_deficit)
    return (
        "The year ends with a covenant in deficit:\n\n"
        f"{lines}\n\n"
        "Balance its books first (the date stays), or advance anyway? The "
        "deficit isn't taken from its Wealth by itself."
    )


def play_season(
    saga: Saga, backup: Backup = None, rng: Callable[[], random.Random] = random.Random
) -> Command | Played:
    """Advance Season once its question is answered Yes: at the year's
    end with a covenant in deficit, ask whether to advance anyway."""
    in_deficit = (
        eco.covenants_in_deficit(saga) if saga.current_season == SEASONS[-1] else []
    )
    if in_deficit:
        return Confirm(
            deficit_question(in_deficit),
            lambda: _secured(saga, backup, rng),
            yes_label="Advance anyway",
            title="A Covenant in Deficit",
        )
    return _secured(saga, backup, rng)


def _secured(saga: Saga, backup: Backup, rng: Callable[[], random.Random]):
    """Whether each contested resource whose security lapsed was secured
    this season (a tick each), then the season played out."""
    lapsed = seasons.lapsed_resources(saga)
    if not lapsed:
        return _discoveries(saga, {}, backup, rng)

    def apply(values: dict[str, Any]):
        answers = {
            resource_id: bool(values.get(f"secured_{index}"))
            for index, (resource_id, _label) in enumerate(lapsed)
        }
        return _discoveries(saga, answers, backup, rng)

    return Form(
        "Contested Resources",
        lambda: [
            DialogField(
                "_why",
                "",
                "info",
                "Tick each contested resource secured this season: it is then "
                "secure for five years. One not secured loses its harvest or "
                "income.",
            ),
            *(
                DialogField(
                    f"secured_{index}", f"{escape(label)} secured", "check", False
                )
                for index, (_id, label) in enumerate(lapsed)
            ),
        ],
        apply,
        save_label="Continue",
    )


def _discoveries(
    saga: Saga,
    secured: dict[str, bool],
    backup: Backup,
    rng: Callable[[], random.Random],
):
    """Work out every plan's outcome (before any is applied, so a season's
    results can't change that same season), ask whether to take each
    Discovery an experiment's risk can reach, then play the season out."""
    worked = seasons.resolve(saga, rng())
    moves = seasons.discovery_moves(saga, worked)
    if not moves:
        return _new_labs(saga, worked, secured, backup, rng)

    def apply(values: dict[str, Any]):
        for index, (outcome, _text) in enumerate(moves):
            seasons.take_discovery_move(
                saga, outcome, bool(values.get(f"move_{index}"))
            )
        return _new_labs(saga, worked, secured, backup, rng)

    fields: list[DialogField] = []
    for index, (_outcome, text) in enumerate(moves):
        fields += [
            DialogField(f"_move_{index}", "", "info", text),
            DialogField(f"move_{index}", "Take the Discovery", "check", False),
        ]
    return Form("Discoveries", lambda: fields, apply, save_label="Continue")


def new_lab_seasons(saga: Saga, worked: list[Any]) -> list[Outcome]:
    """The season's first seasons of a new laboratory that will be applied."""
    return [
        o
        for o in worked
        if isinstance(o, Outcome)
        and o.ok
        and o.plan.activity == ls.NEW
        and saga.character(o.character_id) is not None
    ]


def _new_labs(
    saga: Saga,
    worked: list[Any],
    secured: dict[str, bool],
    backup: Backup,
    rng: Callable[[], random.Random],
):
    """Whether each magus setting up a new laboratory would like to spend
    the next season finishing it (a tick each, ticked; untick to decline),
    then the season played out."""
    found = new_lab_seasons(saga, worked)
    if not found:
        return _world_turns(saga, worked, secured, (), backup, rng)

    def apply(values: dict[str, Any]):
        finish = tuple(
            o for index, o in enumerate(found) if values.get(f"finish_{index}")
        )
        return _world_turns(saga, worked, secured, finish, backup, rng)

    fields: list[DialogField] = []
    for index, outcome in enumerate(found):
        magus = saga.character(outcome.character_id)
        assert magus is not None
        name = ls.new_lab_name(magus, outcome.plan)
        fields += [
            DialogField(
                f"_finish_{index}",
                "",
                "info",
                f"{escape(magus.name)} sets up {escape(name)} this season: it "
                "works with the Basic Flaw (-3 General Quality) until a second "
                "season's work in it removes the Flaw.",
            ),
            DialogField(
                f"finish_{index}",
                f"Would you like {escape(magus.name)} to finish it next season?",
                "check",
                True,
                hint="Plans the next season as lab work setting it up; untick "
                "to plan that season yourself.",
            ),
        ]
    return Form(
        "A New Laboratory",
        lambda: fields,
        apply,
        save_label="Continue",
        help_id="advance-new-lab",
    )


def _world_turns(
    saga: Saga,
    worked: list[Any],
    secured: dict[str, bool],
    finish: tuple[Outcome, ...],
    backup: Backup,
    rng: Callable[[], random.Random],
):
    """When Winter is played: the yearly step's review of what the year
    brought (world_turns), then the season played out."""
    found = (
        world_turns.proposals(saga, rng()) if saga.current_season == SEASONS[-1] else []
    )
    if not found:
        return _finish(saga, worked, secured, finish, backup, rng)
    return world_turns.review(
        saga, found, lambda: _finish(saga, worked, secured, finish, backup, rng)
    )


def _finish(
    saga: Saga,
    worked: list[Any],
    secured: dict[str, bool],
    finish: tuple[Outcome, ...],
    backup: Backup,
    rng: Callable[[], random.Random],
) -> Played:
    """Play the season out in the rules' order and move the date on (the
    caller saves); then plan the second season of each new laboratory
    `finish` names."""
    done = seasons.finish_season(saga, worked, secured, rng(), backup=backup)
    message = f"It is now {saga.current_season} {saga.current_year}."
    if done.applied:
        message += (
            f" Seasons applied for {', '.join(c.name for c in done.applied)}"
            " (see each one's Diary)."
        )
    for outcome in finish:
        planned = seasons.plan_lab_finish(saga, outcome)
        magus = saga.character(outcome.character_id)
        lab = saga.laboratory(planned.lab_id) if planned else None
        if magus is not None and lab is not None:
            message += f" {magus.name} finishes {lab.name} this season (planned)."
    if done.added:
        message += (
            " Added to Wealth: "
            + ", ".join(f"{name} {amount}" for name, amount in done.added)
            + "."
        )
    due = tribunal_terms.come_due(saga)
    if due:
        message += " " + " ".join(due)
    return Played(done, escape(message), bool(worked or done.year_end))


def records_note(saga: Saga) -> str:
    """Where the season's results are kept, under them."""
    return (
        "Kept under Seasons."
        if saga.keep_season_records
        else "Season records are off (Edit Saga): each character's Diary "
        "still has theirs."
    )
