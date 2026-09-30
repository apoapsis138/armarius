"""Season plans and advancing the season (STORY-903): keeping each
character's plan, the text the sheets show for it, and applying a season.

Advancing works out every plan's outcome first (rules.seasons.outcomes), from
the saga as it stood before the season, and only then applies them, so one
character's results can't change another's (or their own) that same season:
raising Magic Theory by Exposure doesn't raise this season's Lab Total. Each
applied outcome adds experience and writes a Diary entry on the character;
the applied plans are then removed. Like the other domain modules it returns
markup text, never widgets."""

from __future__ import annotations

import random
import re
from collections.abc import Sequence
from dataclasses import dataclass, field, replace

from . import spells as spl
from .inhabitants import AUTO_KINDS, character_kind
from .markup import escape, fit
from .models import (
    SEASONS,
    Ability,
    ArtScore,
    Book,
    Character,
    Covenant,
    DiaryEntry,
    KnownSpell,
    Laboratory,
    LabProject,
    Saga,
    SeasonPlan,
    SeasonRecord,
    SeasonRecordLine,
    Spell,
    SpellDesign,
    next_season,
)
from .rules import lab_seasons, study
from .rules import seasons as rules
from .rules import xp as xp_rules

# -- plans --------------------------------------------------------------------


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


def clear_plan(saga: Saga, character: Character) -> bool:
    """Drop `character`'s plan for the current season; whether there was one."""
    plan = plan_for(saga, character)
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


# -- companions' working seasons ----------------------------------------------


def working_seasons_done(character: Character, year: int, before: str) -> int:
    """Working seasons `character` has logged in `year` before `before`."""
    label = rules.ACTIVITIES[rules.EXPOSURE].label
    earlier = SEASONS[: SEASONS.index(before)]
    return sum(
        1
        for entry in character.diary
        if entry.year == year and entry.season in earlier and entry.activity == label
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


# -- text ---------------------------------------------------------------------


def _cite(source: str) -> str:
    """A rule's citation without its web address."""
    return re.sub(r"\s*\(https?://[^)]*\)\s*$", "", source)


def plan_subject(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    """What the plan's season is on, without the activity: "Latin",
    "Latin 5, Creo 3 (Source Quality 8)", or Other's first line of notes
    ("" when there's nothing to name)."""
    activity = rules.ACTIVITIES.get(plan.activity)
    if activity is None or not activity.gives_xp:
        return plan.details.strip().splitlines()[0] if plan.details.strip() else ""
    names = spell_names(saga, character)
    shares = rules.allocations(plan)
    first = rules.subject_label(shares[0].subject, names) if shares else ""
    if activity.lab:
        if plan.activity == lab_seasons.EXTRACT:
            return "Vim vis"
        if plan.activity == lab_seasons.FIX_AC:
            connection = lab_seasons.connection_of(saga, plan)
            return connection.to if connection is not None else ""
        if plan.activity == lab_seasons.LONGEVITY:
            subject = lab_seasons.subject_of(saga, character, plan)
            if subject is None:
                return ""
            return "own" if subject is character else f"for {subject.name}"
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
    if plan.activity == rules.READ:
        book = next((b for b in saga.books if b.id == plan.book_id), None)
        return book_label(book) if book else ""
    if plan.activity in (rules.TAUGHT, rules.TRAINED):
        teacher = saga.character(plan.teacher_id)
        joiner = "from" if plan.activity == rules.TAUGHT else "with"
        return f"{first} {joiner} {teacher.name}" if teacher and first else first
    if plan.activity == rules.VIS_STUDY and shares:
        pawns = study.vis_pawns(rules.score(character, shares[0].subject))
        return f"{first} ({pawns} pawn(s) of vis)"
    if plan.activity == rules.ADVENTURE:
        subjects = ", ".join(
            f"{rules.subject_label(a.subject, names)} {a.points}" for a in shares
        )
        return f"{subjects} (Source Quality {plan.source_quality})"
    return ", ".join(rules.subject_label(a.subject, names) for a in shares)


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


def plan_text(
    saga: Saga, character: Character, how: str = "Press e to plan the season."
) -> str:
    """The character sheet's This Season section: the plan and what it will
    give, worked out from the character as they stand now. `how` says where
    to plan when nothing is planned yet."""
    if not rules.is_planned(character):
        return (
            "[dim]Grogs aren't planned season by season: they're updated once "
            "a year (Grogs, Chapter 5), which comes with a later story.[/]"
        )
    plan = plan_for(saga, character)
    if plan is None:
        return (
            f"[dim]Nothing planned for {saga.current_season} {saga.current_year}. "
            f"{how}[/]"
        )
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
    lines += [f"[$text-error]{escape(p)}[/]" for p in worked.problems]
    note = working_seasons_note(character, plan)
    if note:
        lines.append(f"[$text-warning]{escape(note)}[/]")
    if plan.details.strip() and worked.activity and worked.activity.gives_xp:
        lines.append(f"[dim]Notes:[/] {escape(plan.details.strip())}")
    if worked.activity is not None:
        lines.append(f"[dim]Rule: {escape(_cite(worked.activity.source))}[/]")
    return "\n".join(lines)


def live_text(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    """The plan dialog's preview line(s) for the plan as typed so far."""
    worked = rules.outcome(character, plan, saga)
    if worked.problems:
        return f"[$text-error]{escape(worked.problems[0])}[/]"
    names = spell_names(saga, character)
    lines = [escape(_gain_line(g, names)) for g in worked.gains]
    lines += [escape(n) for n in worked.notes]
    if worked.lab_work is not None:
        lines.insert(0, escape(work_text(worked.lab_work, plan)))
    if worked.pending_roll:
        lines.append("[dim]The die is rolled when the season is applied.[/]")
    note = working_seasons_note(character, plan)
    if note:
        lines.append(f"[$text-warning]{escape(note)}[/]")
    return "\n".join(lines) or "[dim]Logged in the Diary with your notes.[/]"


# -- applying a season ----------------------------------------------------------


def resolve(saga: Saga, rng: random.Random | None = None) -> list[rules.Outcome]:
    """Every current-season plan's outcome, all worked out before any is
    applied. With `rng`, dice are rolled (advancing); without, it is a
    preview and vis study waits for its roll."""
    return rules.outcomes(saga, due_plans(saga), rng)


def _add_xp(character: Character, subject: str, amount: int) -> None:
    kind, _, name = subject.partition(":")
    if kind == "ability":
        ability = next((a for a in character.abilities if a.name == name), None)
        if ability is None:
            # Taught, trained or read in an Ability they didn't have yet.
            ability = Ability(name)
            character.abilities.append(ability)
        ability.xp += amount
    elif kind == "art":
        character.arts.setdefault(name.lower(), ArtScore()).xp += amount
    elif kind == "mastery":
        known = next(k for k in character.spells_known if k.spell_id == name)
        known.mastery_xp += amount
        # Mastery's score and xp are both typed on the sheet: the xp can only
        # raise the score, never lower one typed higher.
        known.mastery_score = max(
            known.mastery_score,
            xp_rules.score_from_xp(known.mastery_xp, xp_rules.ABILITY_FACTOR),
        )


def diary_entry(saga: Saga, character: Character, worked: rules.Outcome) -> DiaryEntry:
    """The character Diary entry recording an applied season."""
    plan = worked.plan
    activity = worked.activity
    names = spell_names(saga, character)
    # The Diary's Activity column names the activity already.
    name = plan_subject(saga, character, plan) or (
        activity.label if activity else plan.activity
    )
    if worked.gains:
        total = sum(g.result.xp for g in worked.gains)
        name += f" (+{total} xp)"
    lines = [_gain_line(g, names) for g in worked.gains]
    lines += worked.notes
    if worked.lab_work is not None:
        lines.append(work_text(worked.lab_work, plan) + ".")
    if plan.days_away:
        lines.append(f"{plan.days_away} days away from the laboratory.")
    if plan.months_lost and activity and activity.distractable:
        lines.append(f"{plan.months_lost} month(s) lost to distractions.")
    if plan.details.strip() and activity and activity.gives_xp:
        lines.append(f"Notes: {plan.details.strip()}")
    elif plan.details.strip():
        lines.append(plan.details.strip())
    if activity is not None:
        lines.append(f"Rule: {_cite(activity.source)}")
    return DiaryEntry(
        year=plan.year,
        season=plan.season,
        name=name,
        details="\n".join(lines),
        activity=activity.label if activity else plan.activity,
    )


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
        if outcome.tractatus and outcome.tractatus not in character.tractatus_read:
            character.tractatus_read.append(outcome.tractatus)
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
            f"[$text-warning]Nothing planned for: {who}. They gain nothing "
            "this season.[/]"
        )
    for outcome in worked:
        if not outcome.ok:
            character = saga.character(outcome.character_id)
            name = character.name if character else outcome.character_id
            lines.append(
                f"[$text-error]{escape(name)}'s plan can't be carried out: "
                f"{escape(outcome.problems[0])}[/]"
            )
    return "\n".join(lines)


# -- the covenant's Seasons tab (STORY-912) -----------------------------------

#: The covenant Seasons tab's lists: (character kind, title). A Mythic
#: Companion is listed with the Companions.
SEASON_KINDS: tuple[tuple[str, str], ...] = (
    ("magus", "Magi"),
    ("companion", "Companions"),
    ("grog", "Grogs"),
)
#: Width of the name column in the Seasons lists.
_NAME_WIDTH = 24


def covenant_people(saga: Saga, covenant: Covenant, kind: str) -> list[Character]:
    """The covenant's characters of `kind` (a SEASON_KINDS key), in the
    saga's order, leaving out any marked departed."""
    return [
        c
        for c in saga.characters
        if c.covenant_id == covenant.id
        and character_kind(c) == kind
        and not is_departed(saga, c)
    ]


def season_title(saga: Saga, covenant: Covenant, kind: str, title: str) -> str:
    """A Seasons list's title: "Magi (1 of 2 planned)", or "Grogs (3)"."""
    people = covenant_people(saga, covenant, kind)
    if kind == "grog":
        return f"{title} ({len(people)})"
    planned = sum(1 for c in people if plan_for(saga, c) is not None)
    return f"{title} ({planned} of {len(people)} planned)"


def season_rows(saga: Saga, covenant: Covenant, kind: str) -> list[tuple[int, str]]:
    """(index, row) per person: their name and what they have planned for
    the current season ("Practice: Latin"), or that nothing is."""
    rows: list[tuple[int, str]] = []
    for index, character in enumerate(covenant_people(saga, covenant, kind)):
        name = character.name + (
            " (Mythic)" if character.type == "mythic companion" else ""
        )
        name = escape(fit(name, _NAME_WIDTH).ljust(_NAME_WIDTH))
        if not rules.is_planned(character):
            what = "[dim]updated yearly[/]"
        else:
            plan = plan_for(saga, character)
            what = (
                escape(plan_summary(saga, character, plan))
                if plan is not None
                else "[$text-warning]nothing planned[/]"
            )
        rows.append((index, f"{name}  {what}"))
    return rows


def season_info_text(saga: Saga, character: Character | None) -> str:
    """The Seasons tab's details panel for the chosen person."""
    if character is None:
        return "[dim]Select someone to see their season.[/]"
    return f"[b]{escape(character.name)}[/]\n" + plan_text(saga, character)


# -- season records (STORY-911) --------------------------------------------------


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
                did = "[$text-warning]nothing planned[/]"
            else:
                did = escape(
                    f"{line.activity}: {line.what}" if line.what else line.activity
                )
                if line.result.startswith("not carried out"):
                    did += f" -- [$text-error]{escape(line.result)}[/]"
                elif line.result:
                    did += f" -- {escape(line.result)}"
            lines.append(f"  {escape(line.name)}: {did}")
    return "\n".join(lines)


# -- lab work (STORY-901) ----------------------------------------------------------

#: How many seasons the laboratory's Planning tab shows, the current first.
QUEUE_LENGTH = 4


def upcoming(saga: Saga, count: int = QUEUE_LENGTH) -> list[tuple[str, int]]:
    """The current season and the ones after it."""
    seasons_: list[tuple[str, int]] = [(saga.current_season, saga.current_year)]
    while len(seasons_) < count:
        seasons_.append(next_season(*seasons_[-1]))
    return seasons_


#: How far ahead the Planning tab looks for scheduled lab work.
QUEUE_HORIZON = 40


@dataclass
class QueueRow:
    """One row of the laboratory's Planning tab: a scheduled activity and
    the seasons it spans (or a season with nothing planned). For inventing,
    the work is where it stands at its last season."""

    season: str
    year: int
    plan: SeasonPlan | None
    end_season: str = ""
    end_year: int = 0
    work: lab_seasons.LabWork | None = None
    problems: list[str] = field(default_factory=list)

    @property
    def span(self) -> str:
        first = _season_label(self.season, self.year)
        if not self.end_season or (self.end_season, self.end_year) == (
            self.season,
            self.year,
        ):
            return first
        return f"{first} - {_season_label(self.end_season, self.end_year)}"


def lab_queue(saga: Saga, lab: Laboratory) -> list[QueueRow]:
    """The owner's scheduled activities from this season on, one row each
    with the seasons it spans; seasons with nothing planned in between,
    and the first free season after the last. An invention's points carry
    from season to season, so each row shows where it will stand."""
    owner = saga.character(lab.owner_id)
    if owner is None:
        return [QueueRow(saga.current_season, saga.current_year, None)]
    seasons_ = upcoming(saga, QUEUE_HORIZON)
    last = max(
        (
            i
            for i, (season, year) in enumerate(seasons_)
            if plan_for(saga, owner, season, year) is not None
        ),
        default=-1,
    )
    rows: list[QueueRow] = []
    carried: dict[str, int] = {}
    for season, year in seasons_[: last + 2]:
        plan = plan_for(saga, owner, season, year)
        work = None
        found: list[str] = []
        if plan is not None and plan.lab_id:
            found, work = lab_seasons.work(saga, owner, plan)
            if (
                work is not None
                and work.spell is not None
                and plan.activity == lab_seasons.INVENT
            ):
                key = work.spell.id
                work.points_before = carried.get(key, work.points_before)
                work.finished = work.points_after >= work.level
                carried[key] = work.points_after
        previous = rows[-1] if rows else None
        if (
            previous is not None
            and plan is not None
            and previous.plan is not None
            and plan.lab_id
            and previous.plan.lab_id
            and plan.activity == previous.plan.activity == lab_seasons.INVENT
            and project_key(plan) == project_key(previous.plan)
            and not found
            and not previous.problems
        ):
            previous.end_season, previous.end_year = season, year
            previous.work = work
            continue
        rows.append(QueueRow(season, year, plan, season, year, work, found))
    return rows


def _season_label(season: str, year: int) -> str:
    return f"{season} {year}"


def work_text(work: lab_seasons.LabWork, plan: SeasonPlan) -> str:
    """How a season's lab work stands (plain text)."""
    total = int(work.lab_total.total)
    if plan.activity == lab_seasons.EXTRACT:
        return f"Lab Total {total}: {work.vis_gained} pawn(s) of Vim vis"
    if plan.activity == lab_seasons.FIX_AC:
        return "1 pawn of Vim vis: the Arcane Connection is fixed"
    if plan.activity == lab_seasons.LONGEVITY:
        name = work.subject.name if work.subject is not None else "?"
        paid = ", ".join(f"{n} pawn(s) of {art}" for art, n in work.vis_cost.items())
        return (
            f"Lab Total {total}: aging rolls -{work.longevity} for {name}; {paid} vis"
        )
    if plan.activity == lab_seasons.LAB_TEXT:
        return f"Lab Total {total} against level {work.level}: learned this season"
    text = (
        f"Lab Total {total}: +{work.points_gained} points, "
        f"{work.points_after}/{work.level}"
    )
    if work.finished:
        return text + ", invented this season"
    left = lab_seasons.seasons_left(work)
    return text + f", {left} more season(s)"


def _progress(work: lab_seasons.LabWork, plan: SeasonPlan) -> str:
    """A queue row's short progress: "8/15 points", "invented"."""
    if plan.activity == lab_seasons.EXTRACT:
        return f"+{work.vis_gained} Vim"
    if plan.activity == lab_seasons.FIX_AC:
        return "fixed"
    if plan.activity == lab_seasons.LONGEVITY:
        return f"aging -{work.longevity}"
    if work.finished:
        return "learned" if plan.activity == lab_seasons.LAB_TEXT else "invented"
    return f"{work.points_after}/{work.level} points"


def lab_queue_rows(saga: Saga, lab: Laboratory) -> list[tuple[int, str]]:
    """The laboratory Planning tab's rows: each coming season and what its
    owner has planned."""
    owner = saga.character(lab.owner_id)
    rows: list[tuple[int, str]] = []
    for index, row in enumerate(lab_queue(saga, lab)):
        when = row.span.ljust(27)
        if owner is None:
            what = "[dim]no owner[/]"
        elif row.plan is None:
            what = "[$text-warning]nothing planned[/]"
        else:
            what = escape(plan_summary(saga, owner, row.plan))
            if not row.plan.lab_id:
                what += f" [dim](on {escape(owner.name)}'s sheet)[/]"
            elif row.problems:
                what += "  [$text-error]can't be done (see below)[/]"
            elif row.work is not None:
                what += f"  [dim]{escape(_progress(row.work, row.plan))}[/]"
        rows.append((index, f"{when}{what}"))
    return rows


def lab_queue_info(saga: Saga, lab: Laboratory, index: int | None) -> str:
    """The Planning tab's details panel: the chosen season's plan and its
    Lab Total, line by line."""
    if index is None:
        return (
            "[dim]Select an activity to see its plan and Lab Total (e changes "
            "it; on a free season, e plans one). Seasons spent otherwise "
            "(reading, adventure...) are planned on the character sheet.[/]"
        )
    rows = lab_queue(saga, lab)
    if index >= len(rows):
        return ""
    row = rows[index]
    owner = saga.character(lab.owner_id)
    head = f"[b]{row.span}[/]"
    if owner is None:
        return head + "\n[dim]Give the laboratory an owner to plan its seasons.[/]"
    if row.plan is None:
        return head + "\n[dim]Nothing planned. Press e to plan lab work.[/]"
    lines = [head, f"[b]{escape(plan_summary(saga, owner, row.plan))}[/]"]
    if not row.plan.lab_id:
        lines.append(
            f"[dim]Planned on {escape(owner.name)}'s sheet. Planning lab work "
            "here replaces it.[/]"
        )
        return "\n".join(lines)
    lines += [f"[$text-error]{escape(p)}[/]" for p in row.problems]
    if row.work is not None:
        lines.append(escape(work_text(row.work, row.plan)))
        for line in row.work.lab_total.lines:
            if line.amount is not None:
                lines.append(f"  {escape(line.label)} {line.amount:+g}")
            elif line.multiplier is not None:
                lines.append(f"  {escape(line.label)} x{line.multiplier:g}")
    if row.plan.days_away:
        lines.append(f"{row.plan.days_away} days away from the laboratory.")
    return "\n".join(lines)


def scheduled_with(saga: Saga, plan: SeasonPlan) -> list[SeasonPlan]:
    """`plan` and, for lab work, the later seasons scheduled to continue it
    (the same project), in season order."""
    key = project_key(plan) if plan.lab_id else None
    start = (plan.year, SEASONS.index(plan.season))
    found = [plan, *_subject_plans(saga, plan)]
    if key is not None:
        found += [
            p
            for p in saga.season_plans
            if p is not plan
            and p.character_id == plan.character_id
            and p.lab_id
            and project_key(p) == key
            and (p.year, SEASONS.index(p.season)) > start
        ]
    return sorted(found, key=lambda p: (p.year, SEASONS.index(p.season)))


def plan_lab_work(saga: Saga, plan: SeasonPlan) -> list[SeasonPlan]:
    """Lock in a lab plan and, for an invention that will take more seasons,
    the same plan for each season it's projected to need (where nothing else
    is planned). Returns the plans added after the first."""
    # Rescheduling replaces the seasons planned to continue it.
    start = (plan.year, SEASONS.index(plan.season))
    key = project_key(plan)
    saga.season_plans = [
        p
        for p in saga.season_plans
        if not (
            p.character_id == plan.character_id
            and p.lab_id
            and key is not None
            and project_key(p) == key
            and (p.year, SEASONS.index(p.season)) > start
        )
    ]
    for old in _subject_plans(saga, plan):
        saga.season_plans.remove(old)
    set_plan(saga, plan)
    character = saga.character(plan.character_id)
    if character is not None and plan.activity == lab_seasons.LONGEVITY:
        _plan_subject(saga, character, plan)
    if character is None or plan.activity != lab_seasons.INVENT:
        return []
    found, work = lab_seasons.work(saga, character, plan)
    if found or work is None:
        return []
    added: list[SeasonPlan] = []
    season, year = plan.season, plan.year
    for _ in range(lab_seasons.seasons_left(work)):
        season, year = next_season(season, year)
        if plan_for(saga, character, season, year) is not None:
            break
        follow = replace(plan, season=season, year=year, days_away=0)
        set_plan(saga, follow)
        added.append(follow)
    return added


def _subject_plans(saga: Saga, plan: SeasonPlan) -> list[SeasonPlan]:
    """The season planned for the subject of the magus's Longevity Ritual
    in `plan`'s season."""
    return [
        p
        for p in saga.season_plans
        if p.activity == lab_seasons.LONGEVITY_SUBJECT
        and p.subject_id == plan.character_id
        and (p.season, p.year) == (plan.season, plan.year)
    ]


def _plan_subject(saga: Saga, magus: Character, plan: SeasonPlan) -> None:
    """Plan the subject's season with the magus (when they're planned season
    by season and have nothing else planned)."""
    subject = lab_seasons.subject_of(saga, magus, plan)
    if subject is None or subject is magus or not rules.is_planned(subject):
        return
    if plan_for(saga, subject, plan.season, plan.year) is not None:
        return
    set_plan(
        saga,
        SeasonPlan(
            subject.id,
            plan.year,
            plan.season,
            lab_seasons.LONGEVITY_SUBJECT,
            details=f"The subject of {magus.name}'s Longevity Ritual.",
            subject_id=magus.id,
        ),
    )


def _lab_text_book(saga: Saga, magus: Character, lab: Laboratory, spell) -> Book:
    ids = {b.id for b in saga.books}
    base = f"labtext_{spell.id}_{magus.id}"
    book_id, n = base, 2
    while book_id in ids:
        book_id, n = f"{base}_{n}", n + 1
    return Book(
        id=book_id,
        name=f"Lab Text: {spell.name}",
        type="Lab Text",
        author=magus.name,
        owner_kind="laboratory",
        owner_id=lab.id,
        year_published=saga.current_year,
        spell_id=spell.id,
        spell_name=spell.name,
    )


def project_key(plan: SeasonPlan) -> str | None:
    """What ties a plan's seasons of invention together: its design, or the
    spell it invents."""
    if plan.design is not None:
        return f"design:{plan.design.key}"
    return plan.spell_id


def _same_spell(a: Spell, b: Spell) -> bool:
    fields_ = ("name", "technique", "form", "level", "range", "duration", "target")
    return all(getattr(a, f) == getattr(b, f) for f in fields_) and sorted(
        a.requisites
    ) == sorted(b.requisites)


def _invented_spell(saga: Saga, magus: Character, design: SpellDesign) -> Spell:
    """The spell a finished design gives: the spell it started from when it
    wasn't changed, otherwise a new spell of the magus's own."""
    designed = lab_seasons.design_spell(design)
    source = spl.find_spell(saga, design.source_spell_id)
    if source is not None and _same_spell(source, designed):
        return source
    spell = spl.add_invented_spell(
        saga, magus, designed.name, designed.technique, designed.form
    )
    for attribute in (
        "level",
        "description",
        "requisites",
        "range",
        "duration",
        "target",
        "ritual",
        "base_level",
    ):
        setattr(spell, attribute, getattr(designed, attribute))
    spell.source = "Invented"
    return spell


_LAB_DIARY_ACTIVITY = {
    lab_seasons.EXTRACT: "Extract Vis",
    lab_seasons.FIX_AC: "Fix Arcane Connection",
    lab_seasons.LONGEVITY: "Longevity Ritual",
}


def _apply_one_season_work(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    outcome: rules.Outcome,
    work: lab_seasons.LabWork,
) -> None:
    """Extracting vis, fixing an Arcane Connection or a Longevity Ritual:
    vis paid or gained, the subject's Longevity modifier, the lab's Diary."""
    plan = outcome.plan
    pool = lab_seasons.vis_pool(saga, magus, plan)
    for art, pawns in work.vis_cost.items():
        key = art.lower()
        pool[key] = max(0, pool.get(key, 0) - pawns)
        if not pool[key]:
            del pool[key]
    if work.vis_gained:
        pool["vim"] = pool.get("vim", 0) + work.vis_gained
    connection = lab_seasons.connection_of(saga, plan)
    if plan.activity == lab_seasons.FIX_AC and connection is not None:
        connection.fixed = True
        connection.lasts = ""
        connection.fixed_year, connection.fixed_season = plan.year, plan.season
    if work.subject is not None and work.longevity:
        work.subject.aging.longevity_modifier = work.longevity
        work.subject.aging.longevity_year = plan.year
        work.subject.aging.longevity_by = magus.name
    activity = rules.ACTIVITIES[plan.activity]
    subject = plan_subject(saga, magus, plan)
    lab.diary.append(
        DiaryEntry(
            year=plan.year,
            season=plan.season,
            name=f"{activity.label}: {subject}" if subject else activity.label,
            details=f"{magus.name}: {work_text(work, plan)}.",
            activity=_LAB_DIARY_ACTIVITY.get(plan.activity, activity.label),
        )
    )


def apply_lab_work(saga: Saga, magus: Character, outcome: rules.Outcome) -> None:
    """A season of lab work: the invention's points, and when it's done, the
    spell known, a Lab Text in the laboratory and the lab's Diary entry."""
    work = outcome.lab_work
    plan = outcome.plan
    lab = saga.laboratory(plan.lab_id)
    if work is None or lab is None:
        return
    spell = work.spell
    if spell is None:
        _apply_one_season_work(saga, magus, lab, outcome, work)
        return
    saga.lab_projects = [
        p
        for p in saga.lab_projects
        if not (p.character_id == magus.id and p.spell_id == spell.id)
    ]
    if work.finished:
        project = spell.id
        if plan.design is not None:
            spell = _invented_spell(saga, magus, plan.design)
        if not any(k.spell_id == spell.id for k in magus.spells_known):
            magus.spells_known.append(KnownSpell(spell_id=spell.id))
        if plan.activity == lab_seasons.INVENT:
            saga.books.append(_lab_text_book(saga, magus, lab, spell))
        # Plans made to continue it are no longer needed.
        saga.season_plans = [
            p
            for p in saga.season_plans
            if not (
                p.character_id == magus.id
                and project_key(p) == project
                and p.activity == lab_seasons.INVENT
                and (p.season, p.year) != (plan.season, plan.year)
            )
        ]
    else:
        saga.lab_projects.append(LabProject(magus.id, spell.id, work.points_after))
        season, year = next_season(plan.season, plan.year)
        if plan_for(saga, magus, season, year) is None:
            set_plan(saga, replace(plan, season=season, year=year, days_away=0))
    lab.diary.append(
        DiaryEntry(
            year=plan.year,
            season=plan.season,
            name=f"{spell.name} ({spl.shorthand(spell)})",
            details=f"{magus.name}: {work_text(work, plan)}."
            + (
                " A Lab Text was written."
                if work.finished and plan.activity == lab_seasons.INVENT
                else ""
            ),
            activity="Invent Spell",
        )
    )
