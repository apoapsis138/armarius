"""Plans that repeat: a plan saved for several seasons, or until its work
is done, and the seasons it still needs worked out again once a season of
it has been played (an interruption can set it back, a good season bring
it forward).

How many seasons a kind of work needs is a hook per activity (Strategy,
as a table): `SEASONS_NEEDED`. Lab work's comes from the points its Lab
Total puts in each season, book work's from its points, reading a summa's
from the experience still to gain up to its Level.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import replace

from .. import books
from ..models import SEASONS, Character, Saga, SeasonPlan, new_instance_id, next_season
from ..rules import activities as rules
from ..rules import book_seasons as bs
from ..rules import creation_access as access
from ..rules import lab_seasons, study
from ..rules import xp as xp_rules
from ..rules.rounding import round_up
from .lab_queue import scheduled_with
from .plans import plan_summary, schedule, set_plan, when_label

#: The Plan Season form's For field and its choices: this season only,
#: until the work is done, or a number of seasons.
FOR = "repeat"
ONCE = "once"
UNTIL_DONE = "until_done"
FOR_OPTIONS: list[tuple[str, str]] = [
    ("This season", ONCE),
    ("Until it's done", UNTIL_DONE),
    *((f"{n} seasons", str(n)) for n in range(2, 5)),
]

#: The most seasons a plan is repeated for (ten years); work that needs
#: more is planned that far, its last season saying how many more.
LONGEST = 40

#: The seasons a plan's work needs from its season on, that season
#: included (0: nothing is left to do; None: it can't be worked out).
Needed = Callable[[Saga, Character, SeasonPlan], int | None]


def _lab_needed(saga: Saga, character: Character, plan: SeasonPlan) -> int | None:
    found, work = lab_seasons.work(saga, character, plan)
    if found or work is None:
        return None
    return 1 + lab_seasons.seasons_left(work)


def _book_needed(saga: Saga, character: Character, plan: SeasonPlan) -> int | None:
    found, work = bs.work(saga, character, plan)
    if found or work is None or not work.points_gained:
        return None
    return max(0, round_up((work.needed - work.points_before) / work.points_gained))


def _reading_needed(saga: Saga, character: Character, plan: SeasonPlan) -> int | None:
    """A summa is read until the reader's score reaches its Level; a
    tractatus takes its one season."""
    book = next((b for b in saga.books if b.id == plan.book_id), None)
    if book is None:
        return None
    if book.type == "Tractatus":
        return 1
    subject = bs.book_subject(book)
    quality = books.effective_quality(saga, book)
    if not subject or quality is None or book.level is None:
        return None
    kind, _, name = subject.partition(":")
    is_art = kind == "art"
    factor = xp_rules.ART_FACTOR if is_art else access.ability_factor(name)
    room = xp_rules.xp_for_score(book.level, factor) - rules.subject_xp(
        character, subject
    )
    if room <= 0:
        return 0
    if rules.problems(character, plan, saga):
        return None
    each = study.season_of_study(
        character, name, quality, activity="reading", is_art=is_art
    ).xp
    return round_up(room / each) if each > 0 else None


#: Each kind of work that can be planned until it's done (Strategy).
SEASONS_NEEDED: dict[str, Needed] = {
    **{key: _lab_needed for key in lab_seasons.MULTI_SEASON},
    **{key: _book_needed for key in bs.MULTI_SEASON},
    rules.READ: _reading_needed,
}


def seasons_needed(saga: Saga, character: Character, plan: SeasonPlan) -> int | None:
    """The seasons `plan`'s work needs from its season on (None: it isn't
    work that runs until done, or can't be worked out)."""
    needed = SEASONS_NEEDED.get(plan.activity)
    return None if needed is None else needed(saga, character, plan)


def can_run_until_done(activity: str) -> bool:
    return activity in SEASONS_NEEDED


def runs_until_done(plan: SeasonPlan) -> bool:
    """Whether `plan`'s seasons are worked out again as it goes: one saved
    until done, or lab work that runs over several seasons."""
    return plan.until_done or (
        bool(plan.lab_id) and plan.activity in lab_seasons.MULTI_SEASON
    )


def _after(plan: SeasonPlan, other: SeasonPlan) -> bool:
    return (other.year, SEASONS.index(other.season)) > (
        plan.year,
        SEASONS.index(plan.season),
    )


def later_seasons(saga: Saga, plan: SeasonPlan) -> list[SeasonPlan]:
    """The seasons planned to continue `plan`'s work after it, in order."""
    return [
        p
        for p in scheduled_with(saga, plan)
        if p.character_id == plan.character_id and _after(plan, p)
    ]


def plan_repeats(
    saga: Saga, character: Character, plan: SeasonPlan, choice: str
) -> list[SeasonPlan]:
    """Lock in `plan` For `choice` (FOR_OPTIONS): its later seasons
    planned straight after it, up to the first season already planned.
    Returns the plans added after the first."""
    if choice not in {value for _, value in FOR_OPTIONS} or choice == ONCE:
        set_plan(saga, plan)
        return []
    plan.until_done = choice == UNTIL_DONE
    plan.series = new_instance_id()
    if plan.until_done:
        count = (seasons_needed(saga, character, plan) or 1) - 1
    else:
        count = int(choice) - 1
    set_plan(saga, plan)
    added = schedule(saga, plan, min(count, LONGEST - 1))
    if plan.until_done:
        (added[-1] if added else plan).more_needed = count - len(added)
    return added


def drop_later(saga: Saga, plan: SeasonPlan) -> None:
    """Clear the seasons planned to continue `plan` (it is rescheduled)."""
    for later in later_seasons(saga, plan):
        saga.season_plans.remove(later)


def _finished(outcome: rules.Outcome) -> bool:
    work = outcome.lab_work or outcome.book_work
    return outcome.ok and work is not None and work.finished


def reforecast(
    saga: Saga, worked: Sequence[rules.Outcome], lost: Sequence[SeasonPlan] = ()
) -> list[str]:
    """Once a season is applied, the seasons each piece of work that runs
    until done still needs, worked out again from where it now stands:
    more planned straight after its last (or a note that the season after
    is taken), or those no longer needed cleared. `lost`, the plans whose
    whole season was lost. Returns a line for each change."""
    due = [(o.plan, _finished(o)) for o in worked if runs_until_done(o.plan)]
    due += [(p, False) for p in lost if runs_until_done(p)]
    lines = []
    for plan, finished in due:
        line = _reforecast(saga, plan, finished)
        if line:
            lines.append(line)
    return lines


def _reforecast(saga: Saga, plan: SeasonPlan, finished: bool) -> str:
    character = saga.character(plan.character_id)
    if character is None:
        return ""
    later = later_seasons(saga, plan)
    if finished:
        needed = 0
    else:
        season, year = next_season(plan.season, plan.year)
        probe = (
            later[0]
            if later
            else replace(plan, season=season, year=year, days_away=0, months_lost=0)
        )
        found = seasons_needed(saga, character, probe)
        if found is None:
            return ""
        needed = found
    what = plan_summary(saga, character, plan)
    if needed < len(later):
        for dropped in later[needed:]:
            saga.season_plans.remove(dropped)
        kept = later[:needed]
        if kept:
            kept[-1].more_needed = 0
            return (
                f"{character.name}'s {what} needs fewer seasons: it now ends "
                f"in {when_label(kept[-1])}."
            )
        return (
            f"{character.name}'s {what} is done: the seasons planned after "
            "it are cleared."
        )
    if needed == len(later):
        return ""
    for each in later:
        each.more_needed = 0
    added = schedule(saga, later[-1] if later else plan, needed - len(later))
    short = needed - len(later) - len(added)
    last = (later + added)[-1] if later or added else None
    if last is not None:
        last.more_needed = short
    if added:
        line = (
            f"{character.name}'s {what} was worked out again: it now runs to "
            f"{when_label(added[-1])}."
        )
        if short:
            line += f" It needs {short} more after that, a season planned already."
        return line
    return (
        f"{character.name}'s {what} needs {short} more season(s), but the "
        "season after is planned for something else."
    )
