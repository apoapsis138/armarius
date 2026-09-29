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

import re
from collections.abc import Sequence

from . import spells as spl
from .inhabitants import AUTO_KINDS, character_kind
from .markup import escape, fit
from .models import (
    SEASONS,
    ArtScore,
    Character,
    Covenant,
    DiaryEntry,
    Laboratory,
    Saga,
    SeasonPlan,
)
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
    if plan.activity == rules.ADVENTURE:
        subjects = ", ".join(
            f"{rules.subject_label(a.subject, names)} {a.points}" for a in shares
        )
        return f"{subjects} (Source Quality {plan.source_quality})"
    return ", ".join(rules.subject_label(a.subject, names) for a in shares)


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
    worked = rules.outcome(character, plan)
    lines = [f"[b]{escape(plan_summary(saga, character, plan))}[/]"]
    names = spell_names(saga, character)
    lines += [f"  {escape(_gain_line(g, names))}" for g in worked.gains]
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


def lab_planning_text(saga: Saga, lab: Laboratory) -> str:
    """The laboratory's Planning tab until it becomes the lab's own season
    planner (STORY-901): what its owner has planned for the season, planned
    on the owner's character sheet."""
    owner = saga.character(lab.owner_id)
    if owner is None:
        return "[dim]No owner: give the laboratory one to plan its seasons.[/]"
    name = escape(owner.name)
    lines = [
        f"[b]{name}: {saga.current_season} {saga.current_year}[/]",
        "",
        plan_text(saga, owner, how=f"Plan it on {name}'s Planning tab."),
        "",
    ]
    if plan_for(saga, owner) is not None:
        lines.append(f"[dim]Change it on {name}'s Planning tab.[/]")
    lines.append(
        "[dim]This tab becomes the laboratory's season planner in a later "
        "story; the Lab Totals have their own tab.[/]"
    )
    return "\n".join(lines)


def live_text(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    """The plan dialog's preview line(s) for the plan as typed so far."""
    worked = rules.outcome(character, plan)
    if worked.problems:
        return f"[$text-error]{escape(worked.problems[0])}[/]"
    names = spell_names(saga, character)
    lines = [escape(_gain_line(g, names)) for g in worked.gains]
    note = working_seasons_note(character, plan)
    if note:
        lines.append(f"[$text-warning]{escape(note)}[/]")
    return "\n".join(lines) or "[dim]Logged in the Diary with your notes.[/]"


# -- applying a season ----------------------------------------------------------


def resolve(saga: Saga) -> list[rules.Outcome]:
    """Every current-season plan's outcome, all worked out before any is
    applied."""
    return rules.outcomes(saga, due_plans(saga))


def _add_xp(character: Character, subject: str, amount: int) -> None:
    kind, _, name = subject.partition(":")
    if kind == "ability":
        ability = next(a for a in character.abilities if a.name == name)
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
