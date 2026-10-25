"""Advancing the season: working out every plan's outcome and applying
them, a grog's year, the year's aging, and the season's record."""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from .. import economics as eco
from ..enchanted_devices import new_day
from ..markup import escape, problem, todo
from ..models import (
    SEASONS,
    Character,
    DiaryEntry,
    ResearchAttempt,
    Saga,
    SeasonPlan,
    SeasonRecord,
    SeasonRecordLine,
    VirtueFlawInstance,
    next_season,
)
from ..rules import activities as rules
from ..rules import agents as agent_rules
from ..rules import aging as aging_rules
from ..rules import apprentice_seasons as aps
from ..rules import experiment as ex
from ..rules import (
    house_virtue,
    medicine,
    research,
    study_virtues,
    tradition_seasons,
    work_virtues,
)
from ..rules import laboratory_seasons as ls
from ..rules import warping as warping_rules
from ..tables import Table
from ..world import takes_part_in_play
from .animal_aging import season_aging
from .character_effects import (
    _add_xp,
    _yearly_warping,
    age_character,
    diary_entry,
    gain_warping,
)
from .covenant import covenant_season
from .defaults import default_text, grog_default, notified
from .healing import season_healing
from .lab_apply import (
    apply_book_work,
    apply_lab_work,
    apply_supplement,
    set_up_new_lab,
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
from .repeat import reforecast


def resolve(saga: Saga, rng: random.Random | None = None) -> list[rules.Outcome]:
    """Every current-season plan's outcome, all worked out before any is
    applied. With `rng`, dice are rolled (advancing); without, it is a
    preview and vis study waits for its roll."""
    return rules.outcomes(saga, due_plans(saga), rng)


def _apply_insight(character: Character, outcome: rules.Outcome) -> None:
    """A season seeking an insight: an insight gained on the goal, and the
    season in its Research log either way."""
    plan = outcome.plan
    if plan.activity != ex.INTEGRATE or not plan.research.strip():
        return
    goal = ex.goal(character, plan.research, plan.research_kind)
    if outcome.insight:
        goal.insights += 1
    research.record(
        goal,
        ResearchAttempt(
            year=plan.year,
            season=plan.season,
            kind="insight",
            work=plan.title.strip(),
            result=" ".join(outcome.notes),
            insight=bool(outcome.insight),
        ),
    )


def _record_raised(character: Character, outcome: rules.Outcome) -> None:
    """Master of None: the subjects a season's own Advancement Total raised
    (not experience a Virtue shared), with the year."""
    if outcome.plan.activity in rules.ADVANCEMENT_ACTIVITIES:
        study_virtues.record_raised(
            character,
            [g.subject for g in outcome.gains if g.result.xp and not g.via],
            outcome.plan.year,
        )


def _apply_apprentice(saga: Saga, outcome: rules.Outcome) -> None:
    """An apprentice's Arts opened, or a Hermetic Virtue taught."""
    work = outcome.apprentice_work
    student = saga.character(outcome.plan.subject_id)
    if work is None or student is None:
        return
    if outcome.plan.activity == aps.OPEN_ARTS:
        aps.open_arts(student, work)
    elif outcome.plan.activity == aps.TEACH_VIRTUE and work.succeeds:
        student.virtues_flaws.append(VirtueFlawInstance(outcome.plan.effect_id or ""))
        if work.flaw_id:
            student.virtues_flaws.append(VirtueFlawInstance(work.flaw_id))


def _apply_warping(saga: Saga, character: Character, outcome: rules.Outcome) -> None:
    """A botch's Warping Points, with the Twilight check at two or more."""
    if outcome.warping:
        gain_warping(
            saga, character, outcome.warping, random.Random(), aura=outcome.warping_aura
        )


def _apply_agency(character: Character, outcome: rules.Outcome) -> None:
    """An Adventure season's experience brings as much Agency experience
    (Lords of Men pp. 24-25); no other season does. The season's own
    experience counts, not what a Virtue shares from it."""
    if outcome.plan.activity != rules.ADVENTURE:
        return
    gained = agent_rules.adventure_agency(
        sum(g.result.xp for g in outcome.gains if not g.via)
    )
    if not gained:
        return
    character.agency_xp += gained
    if character.agents:
        outcome.notes.append(
            f"Agency experience +{gained} (now {character.agency_xp} unspent)."
        )


def _apply_warping_and_agency(
    saga: Saga, character: Character, outcome: rules.Outcome
) -> None:
    """A botch's Warping, and an Adventure's Agency experience."""
    _apply_warping(saga, character, outcome)
    _apply_agency(character, outcome)


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
        _record_raised(character, outcome)
        if outcome.lab_work is not None:
            apply_lab_work(saga, character, outcome)
        if outcome.plan.activity == ls.NEW:
            set_up_new_lab(saga, character, outcome)
        if outcome.book_work is not None:
            apply_book_work(saga, character, outcome.plan, outcome.book_work)
        if outcome.faith:
            character.background.faith_points += outcome.faith
        if outcome.supplement is not None:
            apply_supplement(saga, character, outcome.plan, outcome.supplement)
        _apply_insight(character, outcome)
        _apply_warping_and_agency(saga, character, outcome)
        hedge = outcome.tradition_work
        if hedge is not None and outcome.plan.activity == rules.OPEN_TRADITION:
            opened = saga.character(outcome.plan.subject_id)
            if opened is not None:
                tradition_seasons.apply_opening(opened, hedge)
        _apply_apprentice(saga, outcome)
        if outcome.tractatus and (
            outcome.realia or outcome.tractatus not in character.tractatus_read
        ):
            character.tractatus_read.append(outcome.tractatus)
        if outcome.summa and outcome.summa not in character.summae_read:
            character.summae_read.append(outcome.summa)
        if outcome.glossed:
            glossed = next((b for b in saga.books if b.id == outcome.glossed), None)
            if glossed is not None:
                glossed.glossed = True
        if outcome.vis_spent is not None:
            pool = rules.vis_pool(saga, character, outcome.plan)
            _, art, pawns = outcome.vis_spent
            key = art.lower()
            pool[key] = max(0, pool.get(key, 0) - pawns)
            if not pool[key]:
                del pool[key]
        if outcome.plan.activity in medicine.EUCRASIA_SEASONS:
            lost = medicine.lose_eucrasia(
                character,
                outcome.plan.year,
                medicine.EUCRASIA_SEASONS[outcome.plan.activity],
            )
            if lost:
                outcome.notes.append(lost)
        character.diary.append(diary_entry(saga, character, outcome))
        applied.append(character)
    house_virtue.count_seasons(saga, [o.plan for o in worked if o.ok])
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
        if rules.is_planned(character) or not takes_part_in_play(character):
            continue
        year = character.grog_year
        default = grog_default(saga, character) if year is None else None
        if year is None and default is None:
            continue
        if year is not None:
            gains = [(ability, xp) for ability, xp, _ in grog_year_gains(character)]
        else:
            assert default is not None
            gains = [default]
        for ability, xp in gains:
            _add_xp(character, rules.ability_subject(ability), xp)
        summary = ", ".join(f"{a} +{xp}" for a, xp in gains) or "no xp"
        if year is None:
            details = (
                "No yearly update was set up: the saga's default, 2 xp of "
                "Exposure a season in their highest Ability (Edit Saga)."
            )
        else:
            details = "Grogs, Chapter 5, Updating Grogs" + (
                f"; {year.story_awards} story award(s) took seasons of it."
                if year.story_awards
                else "."
            )
            year.story_awards = 0
        character.diary.append(
            DiaryEntry(
                year=saga.current_year,
                season=saga.current_season,
                name=f"Yearly update{' (default)' if year is None else ''}: {summary}",
                details=details,
                activity="Aging",
            )
        )
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
        if not takes_part_in_play(character):
            continue
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
        if character.animal is not None:
            continue  # an animal rolls in its kind's seasons (season_aging)
        born = character.background.year_born
        age = None if born is None else saga.current_year - born
        if age is None:
            continue
        real_age = age
        # Age Quickly and Demonic Blood age by an effective age (DE pp. 76,
        # 119); a body in Twilight doesn't age at all (DE p. 229).
        age = aging_rules.effective_age(character, age)
        if not aging_rules.rolls_this_year(character, age):
            continue
        if work_virtues.forest_replaces_aging(character):
            continue  # its Warping Point stands in for the roll (_yearly_warping)
        if warping_rules.in_twilight(saga, character):
            continue
        for _ in range(aging_rules.rolls_per_year(character, real_age)):
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
    missing = notified(saga)
    if missing:
        who = ", ".join(
            f"{escape(c.name)} ({c.type}: {escape(default_text(saga, c))})"
            for c in missing
        )
        lines.append(todo(f"Nothing planned for: {who}. Each is asked about next."))
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
    #: Work that runs until done whose seasons were worked out again: a
    #: line for each change (repeat.reforecast).
    forecast: list[str] = field(default_factory=list)


def finish_season(
    saga: Saga,
    worked: Sequence[rules.Outcome],
    secured: dict[str, bool],
    rng: random.Random,
    backup: Callable[[Saga], object] | None = None,
    lost: Sequence[SeasonPlan] = (),
) -> Advanced:
    """Play out the season, once its questions are answered (`secured`: was
    each lapsed contested resource secured; the Discovery moves already
    taken), in the rules' order (from the workspace's Advance
    Time): `backup` the saga if anything is planned; apply each plan; in
    Winter, the year's end -- grogs, business, then aging; the covenants'
    season (harvests, resources); the season record; at a new year, each
    covenant's surplus into its Wealth; then the date moves on (the caller
    saves it). Work that runs until done has its seasons worked out again
    once its season is applied (`lost`: the plans whose season was lost to
    an interruption)."""
    new_year = saga.current_season == SEASONS[-1]
    record = make_record(saga, worked)
    if worked and backup is not None:
        backup(saga)
    applied = apply(saga, worked)
    forecast = reforecast(saga, worked, lost)
    year_end = (
        year_end_grogs(saga) + year_end_business(saga) + year_end_aging(saga, rng)
        if new_year
        else []
    )
    year_end += season_aging(saga, rng)
    year_end += season_healing(saga, rng)
    year_end += covenant_season(saga, secured)
    record.lines += year_end
    if saga.keep_season_records and (worked or year_end):
        saga.season_records.append(record)
    added = eco.close_all_years(saga) if new_year else []
    if new_year:
        neglect = neglected_upkeep(saga)
        record.lines += neglect
        year_end += neglect
    saga.current_season, saga.current_year = next_season(
        saga.current_season, saga.current_year
    )
    # A new season brings new days: every device's uses come back.
    new_day(saga)
    return Advanced(record, applied, year_end, added, forecast)


def neglected_upkeep(saga: Saga) -> list[SeasonRecordLine]:
    """A line for each laboratory of a covenant that closed the year broke:
    its Upkeep went unpaid, so it gains a Flaw (or loses a Virtue) that
    lowers it (DE p. 288)."""
    lines: list[SeasonRecordLine] = []
    for covenant in filter(takes_part_in_play, saga.covenants):
        for lab in eco.neglected_laboratories(saga, covenant):
            owner = saga.character(lab.owner_id)
            lines.append(
                SeasonRecordLine(
                    owner.id if owner is not None else "",
                    lab.name,
                    covenant.id,
                    "Upkeep unpaid",
                    "",
                    "Give it a Flaw, or take a Virtue away, that lowers its "
                    "Upkeep (DE p. 288).",
                )
            )
    return lines


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


def _record_cells(
    saga: Saga, record: SeasonRecord
) -> list[tuple[str, list[tuple[str, str]]]]:
    """A season's record grouped by covenant: each covenant's name, then
    each person's name and what they did and what it gave (markup)."""
    order: list[str | None] = []
    for line in record.lines:
        if line.covenant_id not in order:
            order.append(line.covenant_id)
    groups = []
    for covenant_id in order:
        covenant = saga.covenant(covenant_id)
        people = []
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
            people.append((line.name, did))
        groups.append((covenant.name if covenant else "No covenant", people))
    return groups


def record_text(saga: Saga, record: SeasonRecord) -> str:
    """A season's record as markup: grouped by covenant, one line a person
    with what they did and what it gave."""
    lines = [f"[b]{record.season} {record.year}[/]"]
    if not record.lines:
        return lines[0] + "\n[dim]Nobody's season was planned or applied.[/]"
    for heading, people in _record_cells(saga, record):
        lines += ["", f"[b]{escape(heading)}[/]"]
        lines += [f"  {escape(name)}: {did}" for name, did in people]
    return "\n".join(lines)


def record_table(saga: Saga, record: SeasonRecord) -> Table:
    """A season's record as a table (markup): a heading row per covenant,
    then a row per person with what they did and what it gave."""
    rows: list[list[str]] = []
    keys: list[int | None] = []
    for heading, people in _record_cells(saga, record):
        rows.append([f"[b]{escape(heading)}[/]", ""])
        keys.append(None)
        for name, did in people:
            rows.append([escape(name), did])
            keys.append(len(keys))
    return Table(["Who", "What they did"], rows, keys, markup=True, stretch=1)
