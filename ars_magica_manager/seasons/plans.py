"""Each character's season plan: keeping it, the subjects it can go into,
companions' working seasons, and the text the sheets show for a plan
(lab work, a grog's year and a livelihood included)."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import replace
from functools import partial

from .. import enchanted_devices as ed
from .. import spells as spl
from ..familiars import familiar_of
from ..inhabitants import AUTO_KINDS, character_kind
from ..markup import escape, markdown_text, problem, todo
from ..models import SEASONS, Book, Character, Saga, SeasonPlan, next_season
from ..rules import activities as rules
from ..rules import apprentice_seasons as aps
from ..rules import book_seasons as bs
from ..rules import enchant_seasons as es
from ..rules import familiar_seasons as fs
from ..rules import lab_seasons, study
from ..rules import laboratory_seasons as ls
from ..rules import supplement_work as sw
from ..rules import xp as xp_rules
from ..rules.rounding import round_up
from ..tables import Table
from ..world import takes_part_in_play


def plan_for(
    saga: Saga, character: Character, season: str | None = None, year: int | None = None
) -> SeasonPlan | None:
    """`character`'s plan for a season (by default the saga's current one)."""
    season = season or saga.current_season
    year = saga.current_year if year is None else year
    return next(
        (
            p
            for p in saga.season_plans
            if p.character_id == character.id and (p.season, p.year) == (season, year)
        ),
        None,
    )


def set_plan(saga: Saga, plan: SeasonPlan) -> None:
    """Lock in `plan`, replacing the character's plan for that season."""
    saga.season_plans = [
        p
        for p in saga.season_plans
        if (p.character_id, p.season, p.year)
        != (plan.character_id, plan.season, plan.year)
    ]
    saga.season_plans.append(plan)


def schedule(saga: Saga, plan: SeasonPlan, count: int) -> list[SeasonPlan]:
    """Plan `count` more seasons like `plan` straight after its season,
    stopping at the first season already planned for something else (each
    starts without the months lost or days away of the one it copies).
    Returns the plans added."""
    added: list[SeasonPlan] = []
    season, year = plan.season, plan.year
    character = saga.character(plan.character_id)
    for _ in range(max(0, count)):
        season, year = next_season(season, year)
        if character is None or plan_for(saga, character, season, year) is not None:
            break
        follow = replace(
            plan, season=season, year=year, days_away=0, months_lost=0, more_needed=0
        )
        set_plan(saga, follow)
        added.append(follow)
    return added


def when_label(plan: SeasonPlan) -> str:
    return f"{plan.season} {plan.year}"


def series_text(saga: Saga, plan: SeasonPlan) -> str:
    """ "Season 2 of 4, until it's done (to Summer 1221)", or "" for a plan
    of one season."""
    if not plan.series:
        return ""
    whole = sorted(
        (
            p
            for p in saga.season_plans
            if p.character_id == plan.character_id and p.series == plan.series
        ),
        key=lambda p: (p.year, SEASONS.index(p.season)),
    )
    if len(whole) < 2 and not plan.more_needed:
        return ""
    place = next((i for i, p in enumerate(whole) if p is plan), 0) + 1
    how = ", until it's done" if plan.until_done else ""
    return f"Season {place} of {len(whole)}{how} (to {when_label(whole[-1])})"


def more_needed_text(plan: SeasonPlan) -> str:
    """What the last planned season of unfinished work says, or ""."""
    if not plan.more_needed:
        return ""
    seasons_ = "season" if plan.more_needed == 1 else "seasons"
    return (
        f"The work needs {plan.more_needed} more {seasons_} after this one, "
        "but the season after is planned for something else."
    )


def clear_plan(
    saga: Saga, character: Character, season: str | None = None, year: int | None = None
) -> bool:
    """Drop `character`'s plan for a season (by default the current one);
    whether there was one."""
    plan = plan_for(saga, character, season, year)
    if plan is None:
        return False
    saga.season_plans.remove(plan)
    return True


def is_departed(saga: Saga, character: Character) -> bool:
    """Whether a magus or companion is marked departed in their covenant
    (Inhabitants: died, left...)."""
    covenant = saga.covenant(character.covenant_id)
    kind = character_kind(character)
    if covenant is None or kind not in AUTO_KINDS:
        return False
    return any(
        r.departed
        for r in covenant.inhabitants
        if r.kind == kind and r.character_id == character.id
    )


def unplanned(saga: Saga) -> list[Character]:
    """The magi and companions (Mythic or not) with nothing planned for the
    current season, leaving out any marked departed."""
    return [
        c
        for c in saga.characters
        if rules.is_planned(c)
        and takes_part_in_play(c)
        and not is_departed(saga, c)
        and plan_for(saga, c) is None
    ]


def due_plans(saga: Saga) -> list[SeasonPlan]:
    """The plans for the current season."""
    key = (saga.current_season, saga.current_year)
    return [p for p in saga.season_plans if (p.season, p.year) == key]


def spell_names(saga: Saga, character: Character) -> dict[str, str]:
    """Spell id -> name for the spells `character` knows."""
    names: dict[str, str] = {}
    for known in character.spells_known:
        spell = spl.find_spell(saga, known.spell_id)
        names[known.spell_id] = spell.name if spell else known.spell_id
    return names


def subject_options(saga: Saga, character: Character) -> list[tuple[str, str]]:
    """(label, subject) Select options for a plan's subjects."""
    return [
        (escape(label), subject)
        for label, subject in rules.subjects(character, spell_names(saga, character))
    ]


def working_seasons_done(character: Character, year: int, before: str) -> int:
    """Working seasons `character` has logged in `year` before `before`."""
    labels = {a.label for a in rules.ACTIVITIES.values() if a.working}
    earlier = SEASONS[: SEASONS.index(before)]
    return sum(
        1
        for entry in character.diary
        if entry.year == year and entry.season in earlier and entry.activity in labels
    )


def working_seasons_note(character: Character, plan: SeasonPlan) -> str | None:
    """A companion's plan that leaves too few seasons this year for their two
    working seasons: why (DE Ch. 10, Assigning Seasons). A reminder, not a
    block: a season of adventure or recovery can take a working season's
    place."""
    if character.type not in rules.WORKING_TYPES:
        return None
    activity = rules.ACTIVITIES.get(plan.activity)
    if activity is None or activity.working:
        return None
    done = working_seasons_done(character, plan.year, plan.season)
    owed = rules.WORKING_SEASONS_PER_YEAR - done
    left = len(SEASONS) - SEASONS.index(plan.season) - 1
    if owed <= left:
        return None
    return (
        f"A companion works {rules.WORKING_SEASONS_PER_YEAR} seasons a year "
        f"(DE Ch. 10, Assigning Seasons): {done} worked in {plan.year} so far, "
        f"and this leaves {left} season(s) for the other {owed}."
    )


def _cite(source: str) -> str:
    """A rule's citation without its web address."""
    return re.sub(r"\s*\(https?://[^)]*\)\s*$", "", source)


def _book_plan_subject(saga: Saga, plan: SeasonPlan, names: dict[str, str]) -> str:
    """What a season of book work is on: the book, or the subject written."""
    if plan.activity in (bs.WRITE_SUMMA, bs.WRITE_TRACTATUS):
        shares = rules.allocations(plan)
        subject = rules.subject_label(shares[0].subject, names) if shares else ""
        return plan.title.strip() or subject
    if plan.activity == bs.REWRITE_TEXTS:
        return "own raw Lab Texts"
    if plan.activity == bs.EDIT_FLORILEGIUM:
        subject = plan.florilegium_subject
        return plan.title.strip() or (
            rules.subject_label(subject, names) if subject else ""
        )
    if plan.activity == bs.TEACH_ABBREVIATIONS:
        student = saga.character(plan.subject_id)
        return f"to {student.name}" if student else ""
    book = next((b for b in saga.books if b.id == plan.book_id), None)
    if book is None:
        return ""
    if plan.activity == bs.TRANSLATE_BOOK and plan.language:
        return f"{book_label(book)} into {plan.language}"
    return book_label(book)


def book_text(work: bs.BookWork, plan: SeasonPlan) -> str:
    """How a season of book work stands (plain text)."""
    if plan.activity == bs.REWRITE_TEXTS:
        return f"{len(work.rewritten)} Lab Text(s) rewritten for general use"
    if work.florilegium is not None:
        title, bound, bonus = work.florilegium
        return f"done: {title}, {len(bound)} tractatus at +{bonus} Quality"
    if plan.activity == bs.TEACH_ABBREVIATIONS and work.access:
        return f"can read the teacher's Lab Texts up to level {work.access[2]}"
    made = work.made
    if made is not None and work.needed > 1:
        text = f"+{work.points_gained} points, {work.points_after}/{work.needed}"
        if work.finished:
            return text + f", done: {made.name} (Quality {made.quality})"
        left = round_up((work.needed - work.points_after) / max(1, work.points_gained))
        return text + f", {left} more season(s)"
    if made is not None:
        copies = f"{work.copies} x " if work.copies > 1 else ""
        quality = f" (Quality {made.quality})" if made.quality is not None else ""
        return f"done: {copies}{made.name}{quality}"
    return ""


def plan_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    """What the plan's season is on, without the activity: "Latin",
    "Latin 5, Creo 3 (Source Quality 8)", or Other's first line of notes
    ("" when there's nothing to name)."""
    activity = rules.ACTIVITIES.get(plan.activity)
    if activity is None or not activity.gives_xp:
        return plan.details.strip().splitlines()[0] if plan.details.strip() else ""
    subject = _SUBJECTS.get(plan.activity) or (
        _spell_subject if activity.lab else _xp_subject
    )
    return subject(saga, character, plan)


def _xp_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    """The subjects the experience goes into: "Latin, Creo"."""
    names = spell_names(saga, character)
    return ", ".join(
        rules.subject_label(a.subject, names) for a in rules.allocations(plan)
    )


def _first_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    shares = rules.allocations(plan)
    names = spell_names(saga, character)
    return rules.subject_label(shares[0].subject, names) if shares else ""


def _book_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    return _book_plan_subject(saga, plan, spell_names(saga, character))


def _assist_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    lead = saga.character(plan.teacher_id)
    return lead.name if lead else ""


def _apprentice_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    student = saga.character(plan.subject_id)
    if plan.activity == aps.TEACH_VIRTUE and student is not None:
        virtue = next(
            (n for n, i in aps.teachable_virtues(character) if i == plan.effect_id),
            "",
        )
        return f"{virtue} to {student.name}"
    return student.name if student is not None else ""


def _taming_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    return plan.title.strip()


def _laboratory_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    lab = saga.laboratory(plan.lab_id)
    return lab.name if lab else ""


def _familiar_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    familiar = familiar_of(saga, character.id)
    if familiar is None:
        return ""
    power = fs.power_of(familiar, plan)
    if plan.activity == fs.EMPOWER and power is not None:
        return f"{power.name} for {familiar.name}"
    return familiar.name


def _device_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    device = es.device_of(saga, plan)
    if device is None:
        return ""
    effect = es.effect_of(device, plan)
    if plan.activity == es.INSTIL and effect is not None:
        return f"{ed.effect_name(effect)} in {device.name}"
    return device.name


def _connection_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    connection = lab_seasons.connection_of(saga, plan)
    return connection.to if connection is not None else ""


def _longevity_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    subject = lab_seasons.subject_of(saga, character, plan)
    if subject is None:
        return ""
    return "own" if subject is character else f"for {subject.name}"


def _spell_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    """The spell invented, or learned from a Lab Text: "Pilum of Fire (CrIg 20)"."""
    if plan.activity == lab_seasons.LAB_TEXT:
        text = lab_seasons.lab_text_of(saga, plan)
        spell = spl.find_spell(saga, text.spell_id) if text else None
    else:
        spell = (
            lab_seasons.design_spell(plan.design)
            if plan.design is not None
            else lab_seasons.the_spell(saga, plan)
        )
    return f"{spell.name} ({spl.shorthand(spell)})" if spell else ""


def _read_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    book = next((b for b in saga.books if b.id == plan.book_id), None)
    return book_label(book) if book else ""


def _taught_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    first = _first_subject(saga, character, plan)
    teacher = saga.character(plan.teacher_id)
    joiner = "from" if plan.activity == rules.TAUGHT else "with"
    return f"{first} {joiner} {teacher.name}" if teacher and first else first


def _vis_study_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    shares = rules.allocations(plan)
    if not shares:
        return _xp_subject(saga, character, plan)
    pawns = study.vis_pawns(rules.score(character, shares[0].subject))
    return f"{_first_subject(saga, character, plan)} ({pawns} pawn(s) of vis)"


def _adventure_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    names = spell_names(saga, character)
    subjects = ", ".join(
        f"{rules.subject_label(a.subject, names)} {a.points}"
        for a in rules.allocations(plan)
    )
    return f"{subjects} (Source Quality {plan.source_quality})"


#: What a season of each activity is on (Strategy, as a table). An activity
#: not listed names its spell if it is lab work, else its xp's subjects.
_SUBJECTS: dict[str, Callable[[Saga, Character, SeasonPlan], str]] = {
    **{key: _book_subject for key in (*bs.SHEET_ACTIVITIES, bs.DECODE_TEXT)},
    ls.ASSIST: _assist_subject,
    ls.NEW: lambda saga, character, plan: ls.new_lab_name(character, plan),
    **{key: _apprentice_subject for key in aps.ACTIVITIES},
    lab_seasons.TAMING: _taming_subject,
    **{key: _laboratory_subject for key in ls.ACTIVITIES},
    **{key: _familiar_subject for key in fs.ACTIVITIES},
    **{key: _device_subject for key in es.ACTIVITIES},
    lab_seasons.EXTRACT: lambda saga, character, plan: "Vim vis",
    lab_seasons.FIX_AC: _connection_subject,
    lab_seasons.LONGEVITY: _longevity_subject,
    rules.READ: _read_subject,
    rules.TAUGHT: _taught_subject,
    rules.TRAINED: _taught_subject,
    rules.VIS_STUDY: _vis_study_subject,
    rules.ADVENTURE: _adventure_subject,
}


def book_label(book: Book) -> str:
    """A book as the planner names it: "De Ignis (Ignem summa, L12 Q15)"."""
    subject = book.art or book.ability or "?"
    kind = "tractatus" if book.type == "Tractatus" else "summa"
    level = f"L{book.level} " if book.level is not None and kind == "summa" else ""
    return f"{book.name} ({subject} {kind}, {level}Q{book.quality})"


def plan_summary(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    """One line naming what's planned: "Practice: Latin",
    "Adventure: Latin 5, Creo 3 (Source Quality 8)" (plain text)."""
    activity = rules.ACTIVITIES.get(plan.activity)
    label = activity.label if activity else plan.activity
    subject = plan_subject(saga, character, plan)
    return f"{label}: {subject}" if subject else label


def _gain_line(gain: rules.XpGain, names: dict[str, str]) -> str:
    """ "Latin: Advancement Total 4, +4 xp (score 3, 34 -> 38 xp)" (plain)."""
    factor = rules.subject_factor(gain.subject)
    before = xp_rules.score_from_xp(gain.before, factor)
    after = xp_rules.score_from_xp(gain.after, factor)
    scores = f"score {before}" if before == after else f"score {before} -> {after}"
    notes = "".join(f" {n}" for n in gain.result.notes)
    return (
        f"{rules.subject_label(gain.subject, names)}: Advancement Total "
        f"{gain.result.advancement_total}, +{gain.result.xp} xp "
        f"({scores}, {gain.before} -> {gain.after} xp).{notes}"
    )


#: How many seasons after the current one a character's plans reach: with
#: the current season, a full year.
AHEAD = 3


def seasons_ahead(saga: Saga) -> list[tuple[str, int]]:
    """The seasons after the current one that can be planned, in order."""
    found = [next_season(saga.current_season, saga.current_year)]
    while len(found) < AHEAD:
        found.append(next_season(*found[-1]))
    return found


def planning_year(saga: Saga) -> list[tuple[str, int]]:
    """The current season and the seasons ahead: the year that can be
    planned."""
    return [(saga.current_season, saga.current_year), *seasons_ahead(saga)]


def ahead_rows(saga: Saga, character: Character) -> list[tuple[int, str]]:
    """The Seasons Ahead list: each season after the current one and what
    the character has planned for it."""
    rows = []
    for index, (season, year) in enumerate(seasons_ahead(saga)):
        plan = plan_for(saga, character, season, year)
        what = plan_summary(saga, character, plan) if plan else "nothing planned"
        if plan is not None and plan.more_needed:
            what += " (needs more seasons)"
        rows.append((index, f"{f'{season} {year}':<14}{what}"))
    return rows


def ahead_table(saga: Saga, character: Character) -> Table:
    """ahead_rows as a table (markup): the season, and the plan."""
    rows = []
    for season, year in seasons_ahead(saga):
        plan = plan_for(saga, character, season, year)
        what = (
            escape(plan_summary(saga, character, plan))
            if plan
            else "[dim]nothing planned[/]"
        )
        if plan is not None and plan.more_needed:
            what += f"  {todo('needs more seasons')}"
        rows.append([f"{season} {year}", what])
    return Table(["Season", "Plan"], rows, markup=True, stretch=1)


def ahead_title(saga: Saga) -> str:
    """ "Seasons Ahead (Summer 1220 - Winter 1220)"."""
    ahead = seasons_ahead(saga)
    (first, first_year), (last, last_year) = ahead[0], ahead[-1]
    return f"Seasons Ahead ({first} {first_year} - {last} {last_year})"


def ahead_info(
    saga: Saga, character: Character, index: int | None, how: str = "Press e"
) -> str:
    """The chosen season ahead's plan and what it will give, worked out
    from the character as they stand now (the seasons before it are not
    counted). `how` says how to plan a free season."""
    ahead = seasons_ahead(saga)
    if index is None or not 0 <= index < len(ahead):
        return f"[dim]Choose a season to see its plan. {how} to plan it.[/]"
    season, year = ahead[index]
    text = _plan_text(saga, character, f"{how} to plan it.", season, year)
    if plan_for(saga, character, season, year) is None:
        return text
    return (
        f"{text}\n[dim]Worked out from {escape(character.name)} as they stand "
        "now, before the seasons in between.[/]"
    )


def plan_text(
    saga: Saga, character: Character, how: str = "Press e to plan the season."
) -> str:
    """The character sheet's This Season section: the plan and what it will
    give, worked out from the character as they stand now. `how` says where
    to plan when nothing is planned yet."""
    if not rules.is_planned(character):
        return grog_year_text(character)
    extra = livelihood_text(character)
    text = _plan_text(saga, character, how)
    return f"{text}\n\n{extra}" if extra else text


def _plan_text(
    saga: Saga,
    character: Character,
    how: str,
    season: str | None = None,
    year: int | None = None,
) -> str:
    plan = plan_for(saga, character, season, year)
    if plan is None:
        season = season or saga.current_season
        year = saga.current_year if year is None else year
        return f"[dim]Nothing planned for {season} {year}. {how}[/]"
    worked = rules.outcome(character, plan, saga)
    lines = [f"[b]{escape(plan_summary(saga, character, plan))}[/]"]
    names = spell_names(saga, character)
    lines += [f"  {escape(_gain_line(g, names))}" for g in worked.gains]
    lines += [f"  {escape(n)}" for n in worked.notes]
    if worked.lab_work is not None:
        lines.append(f"  {escape(work_text(worked.lab_work, plan))}")
    if plan.lab_id:
        lab = saga.laboratory(plan.lab_id)
        where = escape(lab.name) if lab else "the laboratory"
        lines.append(f"  [dim]Lab work, planned on {where}'s Planning tab.[/]")
    if plan.days_away:
        lines.append(f"  {plan.days_away} days away from the laboratory.")
    if worked.pending_roll:
        lines.append("  [dim]The die is rolled when the season is applied.[/]")
    if plan.months_lost and worked.activity and worked.activity.distractable:
        lines.append(f"  {plan.months_lost} month(s) lost to distractions.")
    lines += [problem(escape(p)) for p in worked.problems]
    series = series_text(saga, plan)
    if series:
        lines.append(f"  [dim]{escape(series)}.[/]")
    if plan.more_needed:
        lines.append(todo(escape(more_needed_text(plan))))
    note = working_seasons_note(character, plan)
    if note:
        lines.append(todo(escape(note)))
    if plan.details.strip() and worked.activity and worked.activity.gives_xp:
        lines.append(f"[dim]Notes:[/] {markdown_text(plan.details.strip())}")
    if worked.activity is not None:
        lines.append(f"[dim]Rule: {escape(_cite(worked.activity.source))}[/]")
    return "\n".join(lines)


def live_text(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    """The plan dialog's preview line(s) for the plan as typed so far."""
    worked = rules.outcome(character, plan, saga)
    if worked.problems:
        return problem(escape(worked.problems[0]))
    names = spell_names(saga, character)
    lines = [escape(_gain_line(g, names)) for g in worked.gains]
    lines += [escape(n) for n in worked.notes]
    if worked.lab_work is not None:
        lines.insert(0, escape(work_text(worked.lab_work, plan)))
    if worked.book_work is not None:
        lines.insert(0, escape(book_text(worked.book_work, plan)))
    if worked.pending_roll:
        lines.append("[dim]The die is rolled when the season is applied.[/]")
    note = working_seasons_note(character, plan)
    if note:
        lines.append(todo(escape(note)))
    return "\n".join(lines) or "[dim]Logged in the Diary with your notes.[/]"


#: The seasons a grog's story awards remove, in order (Grogs Ch. 5).
_AWARD_ORDER = ("exposure", "vocational", "practice", "exposure_2")


def grog_year_gains(character: Character) -> list[tuple[str, int, str]]:
    """(Ability, xp, kind) a grog's yearly update gives, less the seasons
    story awards take."""
    year = character.grog_year
    if year is None:
        return []
    gains = {
        "vocational": (year.vocational, year.vocational_xp, "vocational"),
        "practice": (year.practice, 4, "practice"),
        "exposure": (year.exposure, 2, "exposure"),
        "exposure_2": (year.exposure_2, 2, "exposure"),
    }
    for key in _AWARD_ORDER[: max(0, year.story_awards)]:
        gains.pop(key, None)
    return [g for g in gains.values() if g[0]]


def grog_year_text(character: Character) -> str:
    """A grog's Planning tab: the yearly update (Grogs Ch. 5)."""
    year = character.grog_year
    head = (
        "[dim]Grogs aren't planned season by season: they're updated once a "
        "year, in Winter (Grogs, Chapter 5). Press e to set it up.[/]"
    )
    if year is None:
        return head
    lines = ["[b]Yearly update (applied in Winter)[/]"]
    for ability, xp, kind in grog_year_gains(character):
        lines.append(f"  {escape(ability)} +{xp} xp ({kind})")
    if year.story_awards:
        lines.append(
            f"  {year.story_awards} story award(s) this year take "
            f"{min(year.story_awards, 4)} season(s) of it."
        )
    if len(lines) == 1:
        lines.append("  [dim]nothing chosen yet[/]")
    return "\n".join(lines)


def work_text(work: lab_seasons.LabWork, plan: SeasonPlan) -> str:
    """How a season's lab work stands (plain text)."""
    text = _WORK_TEXT.get(plan.activity, partial(_points_text, done="invented"))
    return text(work, plan)


def _paid(work: lab_seasons.LabWork) -> str:
    """The vis the work spends: "2 pawn(s) of Vim"."""
    return ", ".join(f"{n} pawn(s) of {art}" for art, n in work.vis_cost.items() if n)


def _points_text(
    work: lab_seasons.LabWork, plan: SeasonPlan, *, done: str, vis: bool = False
) -> str:
    """Work over seasons: the points gained toward its level (and with
    `vis`, the vis spent), then `done` this season or the seasons left."""
    text = (
        f"Lab Total {int(work.lab_total.total)}: +{work.points_gained} points, "
        f"{work.points_after}/{work.level}"
    )
    if vis and _paid(work):
        text += f"; {_paid(work)} vis"
    if work.finished:
        return text + f", {done} this season"
    return text + f", {lab_seasons.seasons_left(work)} more season(s)"


def _against_level(work: lab_seasons.LabWork) -> str:
    return f"Lab Total {int(work.lab_total.total)} against level {work.level}"


def _move_text(work: lab_seasons.LabWork, plan: SeasonPlan) -> str:
    if plan.by_spell:
        return f"moved by spell to {plan.title.strip()}"
    if work.finished:
        return (
            f"reassembled at {plan.title.strip()}; the journey broke two "
            "years' maintenance"
        )
    return " ".join(work.notes).rstrip(".")


def _build_text(work: lab_seasons.LabWork, plan: SeasonPlan) -> str:
    return (
        "the laboratory is finished"
        if work.second_season
        else "the laboratory works, with the Basic Flaw until next season"
    )


def _bind_text(work: lab_seasons.LabWork, plan: SeasonPlan) -> str:
    cords = "/".join(str(c) for c in fs.cords_of(plan))
    paid = _paid(work)
    return f"{_against_level(work)}: bound, cords {cords} (golden/silver/bronze)" + (
        f"; {paid} vis" if paid else ""
    )


def _investigate_text(work: lab_seasons.LabWork, plan: SeasonPlan) -> str:
    found = len(work.revealed)
    if found:
        return f"Lab Total {int(work.lab_total.total)}: {found} power(s) found"
    return _against_level(work)


def _longevity_work_text(work: lab_seasons.LabWork, plan: SeasonPlan) -> str:
    name = work.subject.name if work.subject is not None else "?"
    paid = ", ".join(f"{n} pawn(s) of {art}" for art, n in work.vis_cost.items())
    return (
        f"Lab Total {int(work.lab_total.total)}: aging rolls -{work.longevity} "
        f"for {name}; {paid} vis"
    )


#: How a season of each kind of lab work stands (Strategy, as a table). Lab
#: work not listed invents a spell.
_WORK_TEXT: dict[str, Callable[[lab_seasons.LabWork, SeasonPlan], str]] = {
    bs.DECODE_TEXT: partial(_points_text, done="decoded"),
    lab_seasons.TAMING: partial(_points_text, done="tamed"),
    ls.MOVE: _move_text,
    ls.BUILD: _build_text,
    ls.REFINE: lambda work, plan: f"Refinement {work.refinement}",
    ls.TAKE_OVER: lambda work, plan: f"taken over; Refinement {work.refinement}",
    fs.BIND: _bind_text,
    fs.EMPOWER: partial(_points_text, done="instilled", vis=True),
    es.OPEN: lambda work, plan: f"{_paid(work)} vis: opened for enchantment",
    es.ATTUNE: lambda work, plan: "attuned as a talisman",
    es.INVESTIGATE: _investigate_text,
    es.CHARGED_WORK: lambda work, plan: (
        f"{_against_level(work)}: {work.charges} charge(s)"
    ),
    es.LESSER_WORK: lambda work, plan: (
        f"{_against_level(work)}: made; {_paid(work)} vis"
    ),
    es.INSTIL: partial(_points_text, done="instilled", vis=True),
    lab_seasons.EXTRACT: lambda work, plan: (
        f"Lab Total {int(work.lab_total.total)}: {work.vis_gained} pawn(s) of Vim vis"
    ),
    lab_seasons.FIX_AC: lambda work, plan: (
        "1 pawn of Vim vis: the Arcane Connection is fixed"
    ),
    lab_seasons.LONGEVITY: _longevity_work_text,
    lab_seasons.LAB_TEXT: lambda work, plan: (
        f"{_against_level(work)}: learned this season"
    ),
}


def livelihood_text(character: Character) -> str:
    """The Planning tab's lines on Labor Points, a workshop, progress and
    formulas (empty when there's nothing)."""
    lines: list[str] = []
    if (
        character.labor_points
        or character.workshop_innovation
        or (character.workshop_raw_materials)
    ):
        lines.append(
            f"Labor Points {character.labor_points} ({sw.wealth(character)}); "
            f"workshop Innovation {character.workshop_innovation}, Raw Materials "
            f"{character.workshop_raw_materials}"
        )
    for record in character.progress:
        if record.done or record.kind == "university":
            continue
        lines.append(f"{record.name}: {record.points}/{record.target} ({record.kind})")
    years = sum(r.points for r in character.progress if r.kind == "university")
    if years:
        lines.append(f"University: {years} season(s) studied")
    if character.formulas:
        lines.append("Formulas: " + ", ".join(character.formulas))
    if character.ordeals:
        ordeals = ", ".join(
            f"{o.size} ({o.initiations_since} Initiation(s) since)"
            for o in character.ordeals
        )
        lines.append(
            f"Past Ordeals: {ordeals}; the next Initiation's Target "
            f"-{sw.ordeal_reduction(character)}"
        )
    return "\n".join(escape(line) for line in lines)
