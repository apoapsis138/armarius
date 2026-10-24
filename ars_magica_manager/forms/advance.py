"""Advance Season as the core's command steps (commands.py), so the
terminal and the desktop play a season out the same way.

The question first (what the season's plans will do, and the new year's
note), then, at the year's end with a covenant in deficit, whether to
advance anyway; then whether anything interrupted work that runs until
it's done, whether each contested resource whose security lapsed was
secured, what each experiment's results are (Experiment Results: which
roll stands, its effects, Discoveries and special results, and whether to
take a Discovery its risk can reach), and whether each magus setting up a
new laboratory spends the next season finishing it. Only then is the season played out (seasons.finish_season)
and the date moved on. The last step ends with `Played`: what the season
did and the line saying so, for the front-end to show the season's
results.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any

from .. import aging_due, seasons, tribunal_terms, world_turns
from .. import economics as eco
from ..commands import Command, Confirm, Form
from ..form_spec import DialogField
from ..markup import escape
from ..models import SEASONS, Character, Saga, SeasonPlan, next_season
from ..rules import laboratory_seasons as ls
from ..rules.activities import ACTIVITIES, Outcome
from ..seasons import defaults, repeat
from ..seasons.advance import Advanced
from . import experiment_results
from . import season as season_forms

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
        "A new year: each covenant's surplus is added to its Wealth (a "
        "deficit Emergency Savings didn't cover is taken from it), inflation "
        "grows a pound per hundred spent, and Emergency Savings start again "
        "at 0."
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
        "Balance its books first (the date stays), or advance anyway? "
        "Advancing takes what Emergency Savings didn't cover from its Wealth "
        "(DE p. 189)."
    )


def play_season(
    saga: Saga, backup: Backup = None, rng: Callable[[], random.Random] = random.Random
) -> Command | Played:
    """Advance Season once its question is answered Yes: at the year's
    end with a covenant in deficit, ask whether to advance anyway."""
    owed = aging_due.due(saga)
    if owed:
        # Aging Points a disease Crisis left are placed before the next
        # season is played; cancelling leaves the date as it is.
        return aging_due.place_form(saga, owed, lambda: _after_due(saga, backup, rng))
    return _after_due(saga, backup, rng)


def _after_due(
    saga: Saga, backup: Backup, rng: Callable[[], random.Random]
) -> Command | Played:
    in_deficit = (
        eco.covenants_in_deficit(saga) if saga.current_season == SEASONS[-1] else []
    )
    if in_deficit:
        return Confirm(
            deficit_question(in_deficit),
            lambda: _interrupted(saga, backup, rng),
            yes_label="Advance anyway",
            title="A Covenant in Deficit",
        )
    return _interrupted(saga, backup, rng)


def interrupted_plans(saga: Saga) -> list[SeasonPlan]:
    """The season's plans for work that runs over several seasons until
    it's done, whose seasons are worked out again once it is played."""
    return [
        p
        for p in seasons.due_plans(saga)
        if repeat.runs_until_done(p) and saga.character(p.character_id) is not None
    ]


def _interruption_fields(saga: Saga, index: int, plan: SeasonPlan) -> list[DialogField]:
    character = saga.character(plan.character_id)
    assert character is not None
    later = repeat.later_seasons(saga, plan)
    until = f", planned to {later[-1].season} {later[-1].year}" if later else ""
    fields = [
        DialogField(
            f"_plan_{index}",
            "",
            "info",
            f"{escape(character.name)}: "
            f"{escape(seasons.plan_summary(saga, character, plan))}{until}.",
        )
    ]
    activity = ACTIVITIES.get(plan.activity)
    if plan.lab_id:
        fields.append(
            DialogField(
                f"days_{index}",
                "Days away from the laboratory",
                "int",
                plan.days_away,
                hint="Up to 10 cost nothing; 11 to 20 lower the Lab Total; "
                "more rule out lab work this season.",
            )
        )
    elif activity is not None and activity.distractable:
        fields.append(
            DialogField(
                f"months_{index}",
                "Months lost",
                "int",
                plan.months_lost,
                hint="Each full month lost to distractions cuts the season's "
                "total by a third (0 to 3).",
            )
        )
    fields.append(
        DialogField(
            f"lost_{index}",
            "The whole season lost",
            "check",
            False,
            hint="Nothing is done on it this season.",
        )
    )
    return fields


def _interrupted(saga: Saga, backup: Backup, rng: Callable[[], random.Random]):
    """Whether anything interrupted the season's work that runs until it's
    done (days away, months lost, or the whole season), so that the
    seasons it still needs are worked out from what it really did; then
    the rest of the season."""
    due = interrupted_plans(saga)
    if not due:
        return _gaps(saga, (), backup, rng)

    def validate(values: dict[str, Any]) -> str | None:
        for index, _plan in enumerate(due):
            months = values.get(f"months_{index}") or 0
            days = values.get(f"days_{index}") or 0
            if not 0 <= months <= 3:
                return "Months lost must be 0 to 3."
            if not 0 <= days <= 92:
                return "Days away must be 0 to 92."
        return None

    def apply(values: dict[str, Any]):
        lost: list[SeasonPlan] = []
        for index, plan in enumerate(due):
            if values.get(f"lost_{index}"):
                lost.append(plan)
                continue
            if f"days_{index}" in values:
                plan.days_away = values.get(f"days_{index}") or 0
            if f"months_{index}" in values:
                plan.months_lost = values.get(f"months_{index}") or 0
        return _gaps(saga, tuple(lost), backup, rng)

    def fields() -> list[DialogField]:
        found = [
            DialogField(
                "_why",
                "",
                "info",
                "Work that runs over several seasons until it's done: say if "
                "anything interrupted it this season. The seasons it still "
                "needs are worked out again once the season is played.",
            )
        ]
        for index, plan in enumerate(due):
            found += _interruption_fields(saga, index, plan)
        return found

    return Form(
        "Interruptions",
        fields,
        apply,
        validate=validate,
        save_label="Continue",
        help_id="advance-interrupted",
    )


#: The Unplanned Seasons step's choices.
DEFAULT, NOTHING, PLAN_NOW, LEAVE = "default", "nothing", "plan", "leave"


def _shown(saga: Saga, character_id: str) -> bool:
    character = saga.character(character_id)
    return character is not None and (
        saga.notify_npc_unplanned or defaults.is_player_character(character)
    )


def broken_plans(saga: Saga) -> list[Outcome]:
    """The season's plans that can't be carried out, for the characters
    Advance Season names (players', and others' when the saga says so)."""
    return [
        o for o in seasons.resolve(saga) if not o.ok and _shown(saga, o.character_id)
    ]


def fill_defaults(saga: Saga, skip: set[str] | None = None) -> None:
    """Plan the saga's default season for everyone left with nothing
    planned, but those in `skip` (left with nothing)."""
    for character in seasons.unplanned(saga):
        if skip and character.id in skip:
            continue
        plan = defaults.default_plan(saga, character)
        if plan is not None:
            seasons.set_plan(saga, plan)


def _plan_each(saga: Saga, people: list[Character], then: Callable[[], Any]) -> Any:
    """Plan Season for each of `people` in turn, then `then()`."""
    if not people:
        return then()
    form = season_forms.plan_season(saga, people[0])

    def apply(values: dict[str, Any]) -> Any:
        form.apply(values)
        return _plan_each(saga, people[1:], then)

    return replace(form, apply=apply, save_label="Save and continue")


def _gaps(
    saga: Saga,
    lost: tuple[SeasonPlan, ...],
    backup: Backup,
    rng: Callable[[], random.Random],
):
    """Who has nothing planned, and whose plan can't be carried out: each
    takes the saga's default, nothing, or is planned now; then the rest
    of the season. The characters it doesn't name (non-player characters,
    unless the saga says to) take the saga's default."""
    missing = defaults.notified(saga)
    broken = broken_plans(saga)

    def then() -> Any:
        return _secured(saga, lost, backup, rng)

    if not missing and not broken:
        fill_defaults(saga)
        return then()

    def options(character: Character) -> list[tuple[str, str]]:
        text = defaults.default_text(saga, character)
        found = [] if text == "nothing" else [(f"Default: {text}", DEFAULT)]
        return [*found, ("Nothing this season", NOTHING), ("Plan it now", PLAN_NOW)]

    def fields() -> list[DialogField]:
        found = [
            DialogField(
                "_why",
                "",
                "info",
                "Nothing is planned for these characters this season. Each "
                "can take the saga's default (Edit Saga), do nothing, or be "
                "planned now.",
            )
            if missing
            else DialogField("_why", "", "info", "These plans can't be carried out.")
        ]
        for index, character in enumerate(missing):
            choices = options(character)
            found.append(
                DialogField(
                    f"gap_{index}",
                    f"{escape(character.name)} ({character.type})",
                    "select",
                    choices[0][1],
                    options=choices,
                )
            )
        for index, outcome in enumerate(broken):
            character = saga.character(outcome.character_id)
            assert character is not None
            found.append(
                DialogField(
                    f"fix_{index}",
                    f"{escape(character.name)}: "
                    f"{escape(seasons.plan_summary(saga, character, outcome.plan))}",
                    "select",
                    LEAVE,
                    options=[
                        ("Leave it: it is skipped", LEAVE),
                        ("Plan it again now", PLAN_NOW),
                    ],
                    hint=escape(outcome.problems[0]),
                )
            )
        return found

    def apply(values: dict[str, Any]):
        chosen = {c.id: values.get(f"gap_{i}") for i, c in enumerate(missing)}
        planned = [c for c in missing if chosen[c.id] == PLAN_NOW]
        for index, outcome in enumerate(broken):
            if values.get(f"fix_{index}") == PLAN_NOW:
                character = saga.character(outcome.character_id)
                if character is not None:
                    planned.append(character)
        skip = {cid for cid, how in chosen.items() if how != DEFAULT}

        def after() -> Any:
            fill_defaults(saga, skip)
            return then()

        return _plan_each(saga, planned, after)

    return Form(
        "Unplanned Seasons",
        fields,
        apply,
        save_label="Continue",
        help_id="advance-unplanned",
    )


def _secured(
    saga: Saga,
    lost: tuple[SeasonPlan, ...],
    backup: Backup,
    rng: Callable[[], random.Random],
):
    """Whether each contested resource whose security lapsed was secured
    this season (a tick each), then the season played out."""
    lapsed = seasons.lapsed_resources(saga)
    if not lapsed:
        return _discoveries(saga, {}, lost, backup, rng)

    def apply(values: dict[str, Any]):
        answers = {
            resource_id: bool(values.get(f"secured_{index}"))
            for index, (resource_id, _label) in enumerate(lapsed)
        }
        return _discoveries(saga, answers, lost, backup, rng)

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
    lost: tuple[SeasonPlan, ...],
    backup: Backup,
    rng: Callable[[], random.Random],
):
    """Work out every plan's outcome (before any is applied, so a season's
    results can't change that same season; a season lost isn't played),
    ask the storyguide about each experiment's results (which roll stands,
    its effects, Discoveries and special results, and whether to take a
    Discovery its risk can reach), then play the season out."""
    gone = {p.character_id for p in lost}
    worked = [o for o in seasons.resolve(saga, rng()) if o.character_id not in gone]
    return experiment_results.experiment_results(
        saga,
        worked,
        lambda: _new_labs(saga, worked, secured, lost, backup, rng),
        rng,
    )


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
    lost: tuple[SeasonPlan, ...],
    backup: Backup,
    rng: Callable[[], random.Random],
):
    """Whether each magus setting up a new laboratory would like to spend
    the next season finishing it (a tick each, ticked; untick to decline),
    then the season played out."""
    found = new_lab_seasons(saga, worked)
    if not found:
        return _world_turns(saga, worked, secured, (), lost, backup, rng)

    def apply(values: dict[str, Any]):
        finish = tuple(
            o for index, o in enumerate(found) if values.get(f"finish_{index}")
        )
        return _world_turns(saga, worked, secured, finish, lost, backup, rng)

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
    lost: tuple[SeasonPlan, ...],
    backup: Backup,
    rng: Callable[[], random.Random],
):
    """When Winter is played: the yearly step's review of what the year
    brought (world_turns), then the season played out."""
    found = (
        world_turns.proposals(saga, rng()) if saga.current_season == SEASONS[-1] else []
    )
    if not found:
        return _finish(saga, worked, secured, finish, lost, backup, rng)
    return world_turns.review(
        saga, found, lambda: _finish(saga, worked, secured, finish, lost, backup, rng)
    )


def _finish(
    saga: Saga,
    worked: list[Any],
    secured: dict[str, bool],
    finish: tuple[Outcome, ...],
    lost: tuple[SeasonPlan, ...],
    backup: Backup,
    rng: Callable[[], random.Random],
) -> Played:
    """Play the season out in the rules' order and move the date on (the
    caller saves); then plan the second season of each new laboratory
    `finish` names."""
    whose = [
        (c.name, seasons.plan_summary(saga, c, p))
        for p in lost
        if (c := saga.character(p.character_id)) is not None
    ]
    done = seasons.finish_season(saga, worked, secured, rng(), backup=backup, lost=lost)
    message = f"It is now {saga.current_season} {saga.current_year}."
    if done.applied:
        message += (
            f" Seasons applied for {', '.join(c.name for c in done.applied)}"
            " (see each one's Diary)."
        )
    for name, what in whose:
        message += f" {name}'s season of {what} was lost."
    for line in done.forecast:
        message += f" {line}"
    for outcome in finish:
        planned = seasons.plan_lab_finish(saga, outcome)
        magus = saga.character(outcome.character_id)
        lab = saga.laboratory(planned.lab_id) if planned else None
        if magus is not None and lab is not None:
            message += f" {magus.name} finishes {lab.name} this season (planned)."
    if done.added:
        message += (
            " Wealth: "
            + ", ".join(f"{name} {amount:+d}" for name, amount in done.added)
            + "."
        )
    due = tribunal_terms.come_due(saga)
    if due:
        message += " " + " ".join(due)
    for character in aging_due.due(saga):
        message += (
            f" {character.name} survived a disease Crisis: place the Aging "
            "Point (More on Aging & Warping, or asked before the next season)."
        )
    return Played(done, escape(message), bool(worked or done.year_end))


def records_note(saga: Saga) -> str:
    """Where the season's results are kept, under them."""
    return (
        "Kept under Seasons."
        if saga.keep_season_records
        else "Season records are off (Edit Saga): each character's Diary "
        "still has theirs."
    )
