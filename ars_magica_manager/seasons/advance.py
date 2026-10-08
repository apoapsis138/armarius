"""Advancing the season: working out every plan's outcome and applying
them, a grog's year, the year's aging, and the season's record."""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from .. import economics as eco
from ..markup import escape, problem, todo
from ..models import (
    SEASONS,
    Character,
    DiaryEntry,
    Saga,
    SeasonRecord,
    SeasonRecordLine,
    VirtueFlawInstance,
    next_season,
)
from ..rules import activities as rules
from ..rules import aging as aging_rules
from ..rules import apprentice_seasons as aps
from ..rules import experiment as ex
from ..rules import warping as warping_rules
from .character_effects import _add_xp, _yearly_warping, age_character, diary_entry
from .covenant import covenant_season
from .lab_apply import (
    apply_book_work,
    apply_lab_work,
    apply_supplement,
    year_end_business,
)
from .plans import (
    _cite,
    due_plans,
    grog_year_gains,
    plan_subject,
    spell_names,
    unplanned,
    work_text,
)


def resolve(saga: Saga, rng: random.Random | None = None) -> list[rules.Outcome]:
    """Every current-season plan's outcome, all worked out before any is
    applied. With `rng`, dice are rolled (advancing); without, it is a
    preview and vis study waits for its roll."""
    return rules.outcomes(saga, due_plans(saga), rng)


def apply(saga: Saga, worked: Sequence[rules.Outcome]) -> list[Character]:
    """Apply outcomes worked out by resolve(): add each one's experience and
    write its Diary entry. Outcomes that can't be carried out are skipped.
    Then the current season's plans (and any older ones left over) are
    removed. Returns the characters whose season was applied."""
    applied: list[Character] = []
    for outcome in worked:
        character = saga.character(outcome.character_id)
        if character is None or not outcome.ok:
            continue
        for gain in outcome.gains:
            if gain.result.xp:
                _add_xp(character, gain.subject, gain.result.xp)
        if outcome.lab_work is not None:
            apply_lab_work(saga, character, outcome)
        if outcome.book_work is not None:
            apply_book_work(saga, character, outcome.plan, outcome.book_work)
        if outcome.faith:
            character.background.faith_points += outcome.faith
        if outcome.supplement is not None:
            apply_supplement(saga, character, outcome.plan, outcome.supplement)
        if outcome.insight:
            ex.goal(
                character, outcome.plan.research, outcome.plan.research_kind
            ).insights += 1
        work = outcome.apprentice_work
        student = saga.character(outcome.plan.subject_id)
        if work is not None and student is not None:
            if outcome.plan.activity == aps.OPEN_ARTS:
                aps.open_arts(student, work)
            elif outcome.plan.activity == aps.TEACH_VIRTUE and work.succeeds:
                student.virtues_flaws.append(
                    VirtueFlawInstance(outcome.plan.effect_id or "")
                )
        if outcome.tractatus and outcome.tractatus not in character.tractatus_read:
            character.tractatus_read.append(outcome.tractatus)
        if outcome.summa and outcome.summa not in character.summae_read:
            character.summae_read.append(outcome.summa)
        if outcome.vis_spent is not None:
            pool = rules.vis_pool(saga, character, outcome.plan)
            _, art, pawns = outcome.vis_spent
            key = art.lower()
            pool[key] = max(0, pool.get(key, 0) - pawns)
            if not pool[key]:
                del pool[key]
        character.diary.append(diary_entry(saga, character, outcome))
        applied.append(character)
    now = (saga.current_year, SEASONS.index(saga.current_season))
    saga.season_plans = [
        p for p in saga.season_plans if (p.year, SEASONS.index(p.season)) > now
    ]
    return applied


def year_end_grogs(saga: Saga) -> list[SeasonRecordLine]:
    """The grogs' yearly update, in Winter: their training,
    practice and exposure xp; the year's story awards are then cleared."""
    lines: list[SeasonRecordLine] = []
    for character in saga.characters:
        if rules.is_planned(character) or character.grog_year is None:
            continue
        gains = grog_year_gains(character)
        for ability, xp, _ in gains:
            _add_xp(character, rules.ability_subject(ability), xp)
        summary = ", ".join(f"{a} +{xp}" for a, xp, _ in gains) or "no xp"
        character.diary.append(
            DiaryEntry(
                year=saga.current_year,
                season=saga.current_season,
                name=f"Yearly update: {summary}",
                details="Grogs, Chapter 5, Updating Grogs"
                + (
                    f"; {character.grog_year.story_awards} story award(s) took "
                    "seasons of it."
                    if character.grog_year.story_awards
                    else "."
                ),
                activity="Aging",
            )
        )
        character.grog_year.story_awards = 0
        lines.append(
            SeasonRecordLine(
                character.id,
                character.name,
                character.covenant_id,
                "Yearly update",
                "",
                summary,
            )
        )
    return lines


def year_end_aging(saga: Saga, rng: random.Random) -> list[SeasonRecordLine]:
    """The Winter aging rolls, made when Winter is applied:
    apparent age, Aging Points and Characteristics, Decrepitude, Crises,
    each written in the character's Diary. Returns a record line for each
    character who rolled."""
    lines: list[SeasonRecordLine] = []
    for character in saga.characters:
        warped = _yearly_warping(saga, character)
        if warped:
            character.diary.append(
                DiaryEntry(
                    year=saga.current_year,
                    season=saga.current_season,
                    name="Warping",
                    details=f"{warped}\nRule: {_cite(warping_rules.SOURCE)}",
                    activity="Aging",
                )
            )
        born = character.background.year_born
        age = None if born is None else saga.current_year - born
        if age is None or not aging_rules.rolls_this_year(character, age):
            continue
        lines.append(age_character(saga, character, age, rng))
    return lines


def advance_summary(saga: Saga) -> str:
    """What advancing will do with the season's plans, for the Advance
    Season dialog: who has nothing planned, and any plan that can't be
    carried out (markup)."""
    lines: list[str] = []
    worked = resolve(saga)
    ready = [o for o in worked if o.ok]
    if ready:
        lines.append(f"{len(ready)} planned season(s) will be applied.")
    missing = unplanned(saga)
    if missing:
        who = ", ".join(f"{escape(c.name)} ({c.type})" for c in missing)
        lines.append(
            todo(f"Nothing planned for: {who}. They gain nothing this season.")
        )
    for outcome in worked:
        if not outcome.ok:
            character = saga.character(outcome.character_id)
            name = character.name if character else outcome.character_id
            lines.append(
                problem(
                    f"{escape(name)}'s plan can't be carried out: "
                    f"{escape(outcome.problems[0])}"
                )
            )
    return "\n".join(lines)


@dataclass
class Advanced:
    """What playing out a season did (finish_season)."""

    #: The season's record (kept in the saga if it keeps them).
    record: SeasonRecord
    #: Whose planned seasons were applied.
    applied: list[Character]
    #: The year end's and the covenants' lines (aging, grogs, business,
    #: harvests, resources).
    year_end: list[SeasonRecordLine]
    #: At a new year, each covenant's surplus added to its Wealth: (name,
    #: amount).
    added: list[tuple[str, int]]


def finish_season(
    saga: Saga,
    worked: Sequence[rules.Outcome],
    secured: dict[str, bool],
    rng: random.Random,
    backup: Callable[[Saga], object] | None = None,
) -> Advanced:
    """Play out the season, once its questions are answered (`secured`: was
    each lapsed contested resource secured; the Discovery moves already
    taken), in the rules' order (from the workspace's Advance
    Time): `backup` the saga if anything is planned; apply each plan; in
    Winter, the year's end -- grogs, business, then aging; the covenants'
    season (harvests, resources); the season record; at a new year, each
    covenant's surplus into its Wealth; then the date moves on (the caller
    saves it)."""
    new_year = saga.current_season == SEASONS[-1]
    record = make_record(saga, worked)
    if worked and backup is not None:
        backup(saga)
    applied = apply(saga, worked)
    year_end = (
        year_end_grogs(saga) + year_end_business(saga) + year_end_aging(saga, rng)
        if new_year
        else []
    )
    year_end += covenant_season(saga, secured)
    record.lines += year_end
    if saga.keep_season_records and (worked or year_end):
        saga.season_records.append(record)
    added = eco.close_all_years(saga) if new_year else []
    saga.current_season, saga.current_year = next_season(
        saga.current_season, saga.current_year
    )
    return Advanced(record, applied, year_end, added)


def make_record(saga: Saga, worked: Sequence[rules.Outcome]) -> SeasonRecord:
    """The record of the current season: every worked-out plan (made before
    it is applied), then each magus or companion who had nothing planned."""
    lines: list[SeasonRecordLine] = []
    for outcome in worked:
        character = saga.character(outcome.character_id)
        if character is None:
            continue
        activity = outcome.activity
        names = spell_names(saga, character)
        if outcome.ok:
            result = ", ".join(
                f"{rules.subject_label(g.subject, names)} +{g.result.xp} xp"
                for g in outcome.gains
            )
            if outcome.lab_work is not None:
                result = f"{work_text(outcome.lab_work, outcome.plan)}; {result}"
        else:
            result = f"not carried out: {outcome.problems[0]}"
        lines.append(
            SeasonRecordLine(
                character_id=character.id,
                name=character.name,
                covenant_id=character.covenant_id,
                activity=activity.label if activity else outcome.plan.activity,
                what=plan_subject(saga, character, outcome.plan),
                result=result,
            )
        )
    lines += [SeasonRecordLine(c.id, c.name, c.covenant_id) for c in unplanned(saga)]
    return SeasonRecord(saga.current_year, saga.current_season, lines)


def record_label(record: SeasonRecord) -> str:
    """ "Spring 1220 (3 people)": a record's row in the Seasons list."""
    return f"{record.season} {record.year} ({len(record.lines)} people)"


def record_text(saga: Saga, record: SeasonRecord) -> str:
    """A season's record as markup: grouped by covenant, one line a person
    with what they did and what it gave."""
    lines = [f"[b]{record.season} {record.year}[/]"]
    if not record.lines:
        return lines[0] + "\n[dim]Nobody's season was planned or applied.[/]"
    order: list[str | None] = []
    for line in record.lines:
        if line.covenant_id not in order:
            order.append(line.covenant_id)
    for covenant_id in order:
        covenant = saga.covenant(covenant_id)
        heading = covenant.name if covenant else "No covenant"
        lines += ["", f"[b]{escape(heading)}[/]"]
        for line in record.lines:
            if line.covenant_id != covenant_id:
                continue
            if not line.activity:
                did = todo("nothing planned")
            else:
                did = escape(
                    f"{line.activity}: {line.what}" if line.what else line.activity
                )
                if line.result.startswith("not carried out"):
                    did += f" -- {problem(escape(line.result))}"
                elif line.result:
                    did += f" -- {escape(line.result)}"
            lines.append(f"  {escape(line.name)}: {did}")
    return "\n".join(lines)
