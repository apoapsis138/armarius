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

from . import enchanted_devices as ed
from . import spells as spl
from .familiars import familiar_of
from .inhabitants import AUTO_KINDS, character_kind
from .markup import escape, fit
from .models import (
    SEASONS,
    TEXT_ENCHANTMENT,
    TEXT_LONGEVITY,
    TEXT_OTHER,
    TEXT_SPELL,
    Ability,
    ArcaneConnection,
    ArtScore,
    Book,
    Character,
    Covenant,
    CovenantDiaryEntry,
    DiaryEntry,
    EnchantedDevice,
    InstilledEffect,
    KnownSpell,
    Laboratory,
    LabProject,
    Possession,
    Progress,
    Saga,
    SeasonPlan,
    SeasonRecord,
    SeasonRecordLine,
    Spell,
    SpellDesign,
    VirtueFlawInstance,
    new_instance_id,
    next_season,
)
from .rules import aging as aging_rules
from .rules import apprentice_seasons as aps
from .rules import book_seasons as bs
from .rules import enchant_seasons as es
from .rules import experiment as ex
from .rules import familiar_seasons as fs
from .rules import lab_seasons, study
from .rules import laboratory_seasons as ls
from .rules import seasons as rules
from .rules import supplement_work as sw
from .rules import warping as warping_rules
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


def _book_plan_subject(saga: Saga, plan: SeasonPlan, names: dict[str, str]) -> str:
    """What a season of book work is on: the book, or the subject written."""
    if plan.activity in (bs.WRITE_SUMMA, bs.WRITE_TRACTATUS):
        shares = rules.allocations(plan)
        subject = rules.subject_label(shares[0].subject, names) if shares else ""
        return plan.title.strip() or subject
    if plan.activity == bs.REWRITE_TEXTS:
        return "own raw Lab Texts"
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
    if plan.activity == bs.TEACH_ABBREVIATIONS and work.access:
        return f"can read the teacher's Lab Texts up to level {work.access[2]}"
    made = work.made
    if made is not None and work.needed > 1:
        text = f"+{work.points_gained} points, {work.points_after}/{work.needed}"
        if work.finished:
            return text + f", done: {made.name} (Quality {made.quality})"
        left = -(-(work.needed - work.points_after) // max(1, work.points_gained))
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
    names = spell_names(saga, character)
    shares = rules.allocations(plan)
    first = rules.subject_label(shares[0].subject, names) if shares else ""
    if plan.activity in bs.SHEET_ACTIVITIES or plan.activity == bs.DECODE_TEXT:
        return _book_plan_subject(saga, plan, names)
    if plan.activity == ls.ASSIST:
        lead = saga.character(plan.teacher_id)
        return lead.name if lead else ""
    if plan.activity in aps.ACTIVITIES:
        student = saga.character(plan.subject_id)
        if plan.activity == aps.TEACH_VIRTUE and student is not None:
            virtue = next(
                (n for n, i in aps.teachable_virtues(character) if i == plan.effect_id),
                "",
            )
            return f"{virtue} to {student.name}"
        return student.name if student is not None else ""
    if activity.lab:
        if plan.activity == lab_seasons.TAMING:
            return plan.title.strip()
        if plan.activity in ls.ACTIVITIES:
            lab = saga.laboratory(plan.lab_id)
            return lab.name if lab else ""
        if plan.activity in fs.ACTIVITIES:
            familiar = familiar_of(saga, character.id)
            if familiar is None:
                return ""
            power = fs.power_of(familiar, plan)
            if plan.activity == fs.EMPOWER and power is not None:
                return f"{power.name} for {familiar.name}"
            return familiar.name
        if plan.activity in es.ACTIVITIES:
            device = es.device_of(saga, plan)
            if device is None:
                return ""
            effect = es.effect_of(device, plan)
            if plan.activity == es.INSTIL and effect is not None:
                return f"{ed.effect_name(effect)} in {device.name}"
            return device.name
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
        return grog_year_text(character)
    extra = livelihood_text(character)
    text = _plan_text(saga, character, how)
    return f"{text}\n\n{extra}" if extra else text


def _plan_text(saga: Saga, character: Character, how: str) -> str:
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
    if worked.book_work is not None:
        lines.insert(0, escape(book_text(worked.book_work, plan)))
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
    if worked.book_work is not None:
        lines.append(book_text(worked.book_work, plan) + ".")
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


def _living_conditions(saga: Saga, character: Character) -> int:
    """The Living Conditions modifier: the covenant's for magi or mundanes,
    plus half the Health of a magus's laboratory."""
    covenant = saga.covenant(character.covenant_id)
    living = 0
    if covenant is not None:
        living = (
            covenant.living_conditions_magi
            if character.type == "magus"
            else covenant.living_conditions_mundane
        )
    lab = saga.laboratory(character.assigned_lab_id)
    if lab is not None and character.type == "magus":
        from . import catalog
        from .laboratories import lab_characteristic_total

        health = lab_characteristic_total(
            lab, catalog.load_lab_virtue_flaw_catalog_by_id(), "health"
        )[3]
        living += health // 2
    return living


def _home_aura(saga: Saga, character: Character) -> tuple[int, str]:
    covenant = saga.covenant(character.covenant_id)
    if covenant is None:
        return 0, "Magic"
    from . import catalog
    from .covenants import covenant_effective_aura

    boons = catalog.load_covenant_boon_hook_catalog_by_id()
    return covenant_effective_aura(covenant, boons), covenant.aura_realm


def _yearly_warping(saga: Saga, character: Character) -> str:
    """A year's automatic Warping Points (STORY-909): +1 for a Longevity
    Ritual, and living in a strong aura of another realm (a magus gains none
    from a Magic aura). Returns what was added ("" for nothing)."""
    gained: list[str] = []
    points = 0
    if character.aging.longevity_modifier:
        points += 1
        gained.append("Longevity Ritual 1")
    aura, realm = _home_aura(saga, character)
    if not (character.type == "magus" and realm == "Magic"):
        from_aura = warping_rules.aura_points(aura)
        if from_aura:
            points += from_aura
            gained.append(f"{realm} aura {aura}: {from_aura}")
    if not points:
        return ""
    warping_rules.set_total(character, warping_rules.total_points(character) + points)
    return f"Warping Points +{points} ({', '.join(gained)}); Warping Score now {character.aging.warping_score}."


def gain_warping(
    saga: Saga, character: Character, points: int, rng: random.Random
) -> list[str]:
    """Add Warping Points from one event (STORY-909); 2 or more take a
    magus to the edge of Wizard's Twilight. Writes a Diary entry and returns
    its lines."""
    warping_rules.set_total(character, warping_rules.total_points(character) + points)
    notes = [
        f"+{points} Warping Points; Warping Score {character.aging.warping_score}."
    ]
    name = f"Warping +{points}"
    if character.type == "magus" and points >= 2:
        aura, _ = _home_aura(saga, character)
        result = warping_rules.twilight(character, points, aura, rng, saga)
        notes += result.notes
        if result.entered:
            name = "Wizard's Twilight"
            warping_rules.set_total(
                character, warping_rules.total_points(character) + result.extra_points
            )
            if result.seasons:
                season, year = saga.current_season, saga.current_year
                for _ in range(result.seasons - 1):
                    season, year = next_season(season, year)
                character.aging.twilight_until = f"{season} {year}"
                notes.append(
                    f"Lost in Twilight through {season} {year}: no seasons can be "
                    "planned until then."
                )
    character.diary.append(
        DiaryEntry(
            year=saga.current_year,
            season=saga.current_season,
            name=name,
            details="\n".join(notes)
            + f"\nRule: {_cite(warping_rules.TWILIGHT_SOURCE)}",
            activity="Aging",
        )
    )
    return notes


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


def year_end_grogs(saga: Saga) -> list[SeasonRecordLine]:
    """The grogs' yearly update (STORY-924), in Winter: their training,
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


def age_character(
    saga: Saga,
    character: Character,
    age: int,
    rng: random.Random,
    *,
    living: int | None = None,
    when: tuple[str, int] | None = None,
    label: str = "Aging",
) -> SeasonRecordLine:
    """One character's aging roll (STORY-904): apparent age, Aging Points and
    Characteristics, Decrepitude, a Crisis; written in the Diary. Pre-play
    aging (STORY-1310) gives its own Living Conditions, the (season, year)
    the roll belongs to, and a label for the Diary."""
    familiar = familiar_of(saga, character.id)
    bronze = familiar.bronze_cord if familiar is not None else 0
    if living is None:
        living = _living_conditions(saga, character)
    season, year = (
        when if when is not None else (saga.current_season, saga.current_year)
    )
    result = aging_rules.roll(character, age, living, bronze, rng, saga)
    aging = character.aging
    if result.apparent:
        aging.apparent_age = (
            aging.apparent_age if aging.apparent_age is not None else age - 1
        ) + 1
    elif aging.apparent_age is None:
        aging.apparent_age = age - 1
    notes = list(result.notes)
    for name, points in result.points.items():
        aging.aging_points[name] = aging.aging_points.get(name, 0) + points
        aging.decrepitude_points += points
        score = getattr(character.characteristics, name)
        if aging.aging_points[name] > abs(score):
            setattr(character.characteristics, name, score - 1)
            aging.aging_points[name] = 0
            notes.append(f"{name.title()} falls to {score - 1:+d}.")
    if result.points:
        gained = ", ".join(f"{n.title()} {p}" for n, p in result.points.items())
        notes.append(f"Aging Points: {gained}.")
    aging.decrepitude = aging_rules.decrepitude_score(aging.decrepitude_points)
    if result.crisis:
        text, ends = aging_rules.crisis(character, age, aging.decrepitude, rng, saga)
        notes.append(text)
        if ends:
            aging.longevity_modifier = 0
        after, after_year = next_season(season, year)
        aging.recovering = f"{after} {after_year}"
    summary = (
        "no apparent aging"
        if not result.apparent
        else "apparent age +1"
        + (f", {sum(result.points.values())} Aging Point(s)" if result.points else "")
        + (", an Aging Crisis" if result.crisis else "")
    )
    character.diary.append(
        DiaryEntry(
            year=year,
            season=season,
            name=f"{label}: {summary}",
            details="\n".join(notes) + f"\nRule: {_cite(aging_rules.SOURCE)}",
            activity="Aging",
        )
    )
    return SeasonRecordLine(
        character.id,
        character.name,
        character.covenant_id,
        label,
        "",
        summary,
    )


def year_end_aging(saga: Saga, rng: random.Random) -> list[SeasonRecordLine]:
    """The Winter aging rolls (STORY-904), made when Winter is applied:
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


# -- the covenant's seasons (STORY-906) ---------------------------------------


def _vis_sources(covenant: Covenant) -> list:
    return [p for p in covenant.possessions if p.kind == "vis_source"]


def lapsed_resources(saga: Saga) -> list[tuple[str, str]]:
    """The contested resources to ask about before advancing: (id, label)
    for vis sources harvested this season and, in Winter, income sources,
    whose security has lapsed."""
    year = saga.current_year
    found: list[tuple[str, str]] = []
    for covenant in saga.covenants:
        for source in _vis_sources(covenant):
            if (
                source.contested
                and source.season == saga.current_season
                and (source.secured_until or 0) < year
            ):
                found.append(
                    (source.id, f"{covenant.name}'s {source.name or 'vis source'}")
                )
        if saga.current_season == SEASONS[-1]:
            for income in covenant.economics.income_sources:
                if income.contested and (income.secured_until or 0) < year:
                    found.append(
                        (
                            income.id,
                            f"{covenant.name}'s {income.name or 'income source'}",
                        )
                    )
    return found


def _add_vis(covenant: Covenant, art: str, pawns: int, name: str) -> None:
    store = next(
        (
            p
            for p in covenant.possessions
            if p.kind == "vis_store" and p.art.lower() == art.lower()
        ),
        None,
    )
    if store is None:
        covenant.possessions.append(
            Possession(
                id=f"vis_{new_instance_id()}",
                kind="vis_store",
                name=f"{art} vis",
                art=art,
                pawns=pawns,
                location_kind="covenant",
                location_id=covenant.id,
            )
        )
    else:
        store.pawns += pawns


def available(resource, year: int) -> bool:
    """Whether a vis or income source gives anything this year: not contested,
    or secured through it (Hedda 2026-09-30: an unaddressed contested
    resource isn't available until it is addressed)."""
    return not resource.contested or (resource.secured_until or 0) >= year


def covenant_season(saga: Saga, secured: dict[str, bool]) -> list[SeasonRecordLine]:
    """What the season does for each covenant (STORY-906): its vis sources
    harvested into its vis stores, and in Winter, Dwindling Resources shrink
    by a tenth. A contested resource gives nothing until it is addressed:
    `secured` answers "Was it secured this season?" for each lapsed one
    (yes: secured for five years), and a year that ends with it unaddressed
    is written in the covenant Diary. Returns record lines."""
    season, year = saga.current_season, saga.current_year
    lines: list[SeasonRecordLine] = []
    for covenant in saga.covenants:
        resources = [*_vis_sources(covenant), *covenant.economics.income_sources]
        for resource in resources:
            if secured.get(resource.id):
                resource.secured_until = year + 4
        harvested: list[str] = []
        for source in _vis_sources(covenant):
            if source.season != season or not source.art or source.pawns <= 0:
                continue
            if not available(source, year):
                covenant.diary.append(
                    CovenantDiaryEntry(
                        year,
                        season,
                        f"{source.name or 'A vis source'} not harvested",
                        "A contested resource not yet secured: no harvest.",
                        category="Covenant Season",
                    )
                )
                continue
            _add_vis(covenant, source.art, source.pawns, source.name)
            harvested.append(f"{source.pawns} {source.art}")
            covenant.diary.append(
                CovenantDiaryEntry(
                    year,
                    season,
                    f"Vis harvested: {source.name or source.art}",
                    f"{source.pawns} pawn(s) of {source.art} vis into the vis stores.",
                    category="Covenant Season",
                    vis_pawns=source.pawns,
                    vis_art=source.art,
                )
            )
        if season == SEASONS[-1]:
            for resource in resources:
                if not available(resource, year):
                    covenant.diary.append(
                        CovenantDiaryEntry(
                            year,
                            season,
                            f"{resource.name or 'A resource'} not received",
                            "A contested resource still unresolved at the year's "
                            "end: the covenant receives nothing from it this year.",
                            category="Covenant Season",
                        )
                    )
            for income in covenant.economics.income_sources:
                if income.dwindling:
                    income.income = round(income.current_income * 0.9)
            for source in _vis_sources(covenant):
                if source.dwindling:
                    source.pawns = int(source.pawns * 0.9)
        if harvested:
            lines.append(
                SeasonRecordLine(
                    covenant.id,
                    covenant.name,
                    covenant.id,
                    "Vis harvest",
                    "",
                    ", ".join(harvested),
                )
            )
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
            if work is not None and plan.activity in lab_seasons.MULTI_SEASON:
                key = project_key(plan) or ""
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
            and plan.activity == previous.plan.activity
            and plan.activity in lab_seasons.MULTI_SEASON
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
    paid = ", ".join(f"{n} pawn(s) of {art}" for art, n in work.vis_cost.items() if n)
    if plan.activity == bs.DECODE_TEXT:
        text = (
            f"Lab Total {total}: +{work.points_gained} points, "
            f"{work.points_after}/{work.level}"
        )
        if work.finished:
            return text + ", decoded this season"
        return text + f", {lab_seasons.seasons_left(work)} more season(s)"
    if plan.activity == lab_seasons.TAMING:
        text = (
            f"Lab Total {total}: +{work.points_gained} points, "
            f"{work.points_after}/{work.level}"
        )
        if work.finished:
            return text + ", tamed this season"
        return text + f", {lab_seasons.seasons_left(work)} more season(s)"
    if plan.activity == ls.MOVE:
        if plan.by_spell:
            return f"moved by spell to {plan.title.strip()}"
        if work.finished:
            return (
                f"reassembled at {plan.title.strip()}; the journey broke two "
                "years' maintenance"
            )
        return " ".join(work.notes).rstrip(".")
    if plan.activity == ls.BUILD:
        return (
            "the laboratory is finished"
            if work.second_season
            else "the laboratory works, with the Basic Flaw until next season"
        )
    if plan.activity == ls.REFINE:
        return f"Refinement {work.refinement}"
    if plan.activity == ls.TAKE_OVER:
        return f"taken over; Refinement {work.refinement}"
    if plan.activity == fs.BIND:
        cords = "/".join(str(c) for c in fs.cords_of(plan))
        return (
            f"Lab Total {total} against level {work.level}: bound, cords "
            f"{cords} (golden/silver/bronze)" + (f"; {paid} vis" if paid else "")
        )
    if plan.activity == fs.EMPOWER:
        text = (
            f"Lab Total {total}: +{work.points_gained} points, "
            f"{work.points_after}/{work.level}"
        )
        if paid:
            text += f"; {paid} vis"
        if work.finished:
            return text + ", instilled this season"
        return text + f", {lab_seasons.seasons_left(work)} more season(s)"
    if plan.activity == es.OPEN:
        return f"{paid} vis: opened for enchantment"
    if plan.activity == es.ATTUNE:
        return "attuned as a talisman"
    if plan.activity == es.INVESTIGATE:
        found = len(work.revealed)
        return (
            f"Lab Total {total}: {found} power(s) found"
            if found
            else f"Lab Total {total} against level {work.level}"
        )
    if plan.activity == es.CHARGED_WORK:
        return f"Lab Total {total} against level {work.level}: {work.charges} charge(s)"
    if plan.activity == es.LESSER_WORK:
        return f"Lab Total {total} against level {work.level}: made; {paid} vis"
    if plan.activity == es.INSTIL:
        text = (
            f"Lab Total {total}: +{work.points_gained} points, "
            f"{work.points_after}/{work.level}"
        )
        if paid:
            text += f"; {paid} vis"
        if work.finished:
            return text + ", instilled this season"
        return text + f", {lab_seasons.seasons_left(work)} more season(s)"
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
    if plan.activity == bs.DECODE_TEXT and work.finished:
        return "decoded"
    if plan.activity == lab_seasons.TAMING and work.finished:
        return "tamed"
    if plan.activity == ls.MOVE:
        return "moved" if plan.by_spell or work.finished else "moving"
    if plan.activity == ls.BUILD:
        return "finished" if work.second_season else "set up (Basic)"
    if plan.activity in (ls.REFINE, ls.TAKE_OVER):
        return f"Refinement {work.refinement}"
    if plan.activity == fs.BIND:
        return "bound"
    if plan.activity == fs.EMPOWER and work.finished:
        return "instilled"
    if plan.activity == es.OPEN:
        return "opened"
    if plan.activity == es.ATTUNE:
        return "attuned"
    if plan.activity == es.INVESTIGATE:
        return f"against level {work.level}"
    if plan.activity == es.CHARGED_WORK:
        return f"{work.charges} charge(s)"
    if plan.activity == es.LESSER_WORK:
        return "made"
    if plan.activity == es.INSTIL and work.finished:
        return "instilled"
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
    if character is None or plan.activity not in lab_seasons.MULTI_SEASON:
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
        raw=True,
        author_id=magus.id,
        text_kind=TEXT_SPELL,
    )


def _effect_text(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    device: EnchantedDevice,
    effect: InstilledEffect,
) -> Book:
    """The raw Lab Text of an effect just instilled (STORY-508): a snapshot
    of the effect and of the device it went into (the device may be given
    away or lost; the text is exact to that shape and material)."""
    kind = es.text_device_type(device)
    parts = [
        " ".join(p for p in (c.size, c.material, c.description) if p)
        for c in device.components
    ]
    return Book(
        id=f"labtext_effect_{magus.id}_{new_instance_id()}",
        name=f"Lab Text: {effect.name or 'an effect'} ({device.name})",
        type="Lab Text",
        author=magus.name,
        author_id=magus.id,
        raw=True,
        owner_kind="laboratory",
        owner_id=lab.id,
        year_published=saga.current_year,
        # The level it was instilled at (with its uses a day and the rest).
        level=ed.modified_level(device, effect),
        text_kind=TEXT_ENCHANTMENT,
        technique=effect.technique,
        form=effect.form,
        effect_rdt=" / ".join(
            part or "?" for part in (effect.range, effect.duration, effect.target)
        ),
        device_type=kind,
        shape_material="; ".join(p for p in parts if p),
        description=effect.description,
    )


def _longevity_text(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    subject: Character,
    lab_total: int,
    extra_vis: int = 0,
) -> Book:
    """The raw Lab Text of a Longevity Ritual (STORY-508): Creo Corpus, its
    level the ritual's Lab Total; it lets the ritual be performed again."""
    return Book(
        id=f"labtext_longevity_{magus.id}_{new_instance_id()}",
        name=f"Lab Text: Longevity Ritual for {subject.name}",
        type="Lab Text",
        author=magus.name,
        author_id=magus.id,
        raw=True,
        owner_kind="laboratory",
        owner_id=lab.id,
        year_published=saga.current_year,
        level=max(0, lab_total),
        text_kind=TEXT_LONGEVITY,
        technique="Creo",
        form="Corpus",
        ritual_subject=subject.name,
        ritual_extra_vis=max(0, extra_vis),
    )


def project_key(plan: SeasonPlan) -> str | None:
    """What ties a plan's seasons of invention together: its design, or the
    spell it invents."""
    if plan.activity == es.INSTIL:
        return f"effect:{plan.effect_id}" if plan.effect_id else None
    if plan.activity == fs.EMPOWER:
        return f"bond:{plan.effect_id}" if plan.effect_id else None
    if plan.activity == lab_seasons.TAMING:
        return f"taming:{plan.title.strip()}"
    if plan.activity == bs.DECODE_TEXT:
        return f"decode:{plan.book_id}" if plan.book_id else None
    if plan.design is not None:
        return f"design:{plan.design.key}"
    return plan.spell_id


def _same_spell(a: Spell, b: Spell) -> bool:
    fields_ = ("name", "technique", "form", "level", "range", "duration", "target")
    return all(getattr(a, f) == getattr(b, f) for f in fields_) and sorted(
        a.requisites
    ) == sorted(b.requisites)


def _with_effects(
    saga: Saga, magus: Character, spell: Spell, effects: list[str]
) -> Spell:
    """The spell as invented with its experimental effects: the magus's own
    record (a copy when it was someone else's), which anyone learning it
    learns, warts and all."""
    if not any(s is spell for s in magus.invented_spells):
        own = spl.add_invented_spell(
            saga, magus, spell.name, spell.technique, spell.form
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
            setattr(own, attribute, getattr(spell, attribute))
        own.source = "Invented"
        spell = own
    spell.experimental_effects += effects
    return spell


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
    es.OPEN: "Open Item for Enchantment",
    es.INSTIL: "Instill Effect (Invested Device)",
    es.LESSER_WORK: "Lesser Enchantment",
    es.CHARGED_WORK: "Charged Item",
    es.ATTUNE: "Other",
    fs.BIND: "Bind Familiar",
    fs.EMPOWER: "Empower Familiar Bond",
    ls.BUILD: "Build/Modify Laboratory",
    ls.REFINE: "Refine Laboratory",
    ls.TAKE_OVER: "Build/Modify Laboratory",
    ls.MOVE: "Build/Modify Laboratory",
    bs.DECODE_TEXT: "Translate Lab Text",
    es.INVESTIGATE: "Other",
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
    if plan.activity in es.ACTIVITIES:
        _apply_enchanting(saga, magus, lab, plan, work)
    if plan.activity in fs.ACTIVITIES:
        _apply_familiar(saga, magus, plan, work)
    if plan.activity in ls.ACTIVITIES:
        _apply_laboratory(saga, magus, lab, plan, work)
    if plan.activity == lab_seasons.TAMING:
        _apply_taming(saga, magus, lab, plan, work)
    if plan.activity == bs.DECODE_TEXT and work.access is not None:
        key = lab_seasons.decode_key(magus, work.access[1])
        saga.lab_projects = [p for p in saga.lab_projects if p.spell_id != key]
        if work.finished:
            _, author, level = work.access
            bs.grant_access(magus, author, level, "decoded")
        else:
            saga.lab_projects.append(LabProject(magus.id, key, work.points_after))
            season, year = next_season(plan.season, plan.year)
            if plan_for(saga, magus, season, year) is None:
                set_plan(saga, replace(plan, season=season, year=year, days_away=0))
    if work.subject is not None and work.longevity:
        work.subject.aging.longevity_modifier = work.longevity
        work.subject.aging.longevity_year = plan.year
        work.subject.aging.longevity_by = magus.name
        saga.books.append(
            _longevity_text(
                saga,
                magus,
                lab,
                work.subject,
                int(work.lab_total.total),
                plan.extra_vis,
            )
        )
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


def perform_ritual_again(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    text: Book,
    vis_art: str,
    vis_from: str,
) -> list[str]:
    """Perform a Longevity Ritual again from its Lab Text, now (STORY-509):
    it takes no season, so nothing is planned -- the vis is paid, the
    subject's Longevity modifier is set, and the laboratory's and the
    subject's Diaries record it. Returns the problems (nothing is done
    with any)."""
    found, again = lab_seasons.ritual_again(saga, magus, lab, text, vis_art, vis_from)
    if again is None:
        return found
    plan = SeasonPlan(
        magus.id,
        saga.current_year,
        saga.current_season,
        lab_seasons.LONGEVITY,
        lab_id=lab.id,
        vis_from=vis_from,
    )
    pool = lab_seasons.vis_pool(saga, magus, plan)
    key = vis_art.lower()
    left = pool.get(key, 0) - again.pawns
    if left > 0:
        pool[key] = left
    else:
        pool.pop(key, None)
    subject = again.subject
    subject.aging.longevity_modifier = again.modifier
    subject.aging.longevity_year = saga.current_year
    subject.aging.longevity_by = magus.name
    done = (
        f"{again.pawns} pawn(s) of {vis_art} vis; aging rolls -{again.modifier}. "
        "From its Lab Text: no season taken."
    )
    lab.diary.append(
        DiaryEntry(
            year=saga.current_year,
            season=saga.current_season,
            name=f"Longevity Ritual performed again: {subject.name}",
            details=f"{magus.name}: {done}",
            activity=_LAB_DIARY_ACTIVITY.get(lab_seasons.LONGEVITY, "Longevity Ritual"),
        )
    )
    subject.diary.append(
        DiaryEntry(
            year=saga.current_year,
            season=saga.current_season,
            name=f"Longevity Ritual performed again by {magus.name}",
            details=done,
        )
    )
    return []


def _apply_enchanting(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    plan: SeasonPlan,
    work: lab_seasons.LabWork,
) -> None:
    """What a season of enchanting does to its device (STORY-905); an
    effect instilled leaves a raw Lab Text in the laboratory (STORY-508)."""
    device, effect = work.device, work.effect
    if device is None:
        return
    instilling = (es.LESSER_WORK, es.CHARGED_WORK, es.INSTIL)
    if effect is not None and plan.activity in instilling and work.finished:
        saga.books.append(_effect_text(saga, magus, lab, device, effect))
    making = (es.OPEN, es.LESSER_WORK, es.CHARGED_WORK, es.ATTUNE)
    if plan.activity in making and not device.maker_id and not device.maker_name:
        device.maker_id = magus.id
    if plan.activity == es.OPEN:
        device.pawns_opened += work.vis_cost.get("Vim", 0)
    elif plan.activity == es.ATTUNE:
        device.talisman = True
    elif plan.activity == es.INVESTIGATE:
        for found in device.effects:
            if found.id in work.revealed:
                found.known = True
    elif plan.activity == es.CHARGED_WORK:
        device.lab_total = int(work.lab_total.total)
        device.charges_made = None
        device.charges_left = None
    elif effect is not None and plan.activity == es.LESSER_WORK:
        effect.instilling_progress = None
    elif effect is not None and plan.activity == es.INSTIL:
        if work.finished:
            effect.instilling_progress = None
            project = project_key(plan)
            saga.season_plans = [
                p
                for p in saga.season_plans
                if not (
                    p.character_id == magus.id
                    and p.activity == es.INSTIL
                    and project_key(p) == project
                    and (p.season, p.year) != (plan.season, plan.year)
                )
            ]
        else:
            effect.instilling_progress = work.points_after
            season, year = next_season(plan.season, plan.year)
            if plan_for(saga, magus, season, year) is None:
                set_plan(saga, replace(plan, season=season, year=year, days_away=0))


def _apply_familiar(
    saga: Saga, magus: Character, plan: SeasonPlan, work: lab_seasons.LabWork
) -> None:
    """What a season of familiar work does (STORY-908)."""
    familiar = work.familiar
    if familiar is None:
        return
    if plan.activity == fs.BIND:
        familiar.binding_technique = plan.technique
        familiar.binding_form = plan.form
        familiar.binding_lab_total = int(work.lab_total.total)
        familiar.target_binding_level = work.level
        familiar.vis_spent_binding += sum(work.vis_cost.values())
        familiar.golden_cord, familiar.silver_cord, familiar.bronze_cord = fs.cords_of(
            plan
        )
        if familiar.year_bound is None:
            familiar.season_bound, familiar.year_bound = plan.season, plan.year
        return
    power = work.power
    if power is None:
        return
    power.vis_spent += sum(work.vis_cost.values())
    project = project_key(plan)
    if work.finished:
        power.instilling_progress = None
        saga.season_plans = [
            p
            for p in saga.season_plans
            if not (
                p.character_id == magus.id
                and p.activity == fs.EMPOWER
                and project_key(p) == project
                and (p.season, p.year) != (plan.season, plan.year)
            )
        ]
    else:
        power.instilling_progress = work.points_after
        season, year = next_season(plan.season, plan.year)
        if plan_for(saga, magus, season, year) is None:
            set_plan(saga, replace(plan, season=season, year=year, days_away=0))


def _copy_book(saga: Saga, book: Book) -> Book:
    ids = {b.id for b in saga.books}
    book_id, n = book.id, 2
    while book_id in ids:
        book_id, n = f"{book.id}_{n}", n + 1
    return replace(book, id=book_id)


def apply_supplement(
    saga: Saga, character: Character, plan: SeasonPlan, work: sw.SupplementWork
) -> None:
    """What a supplement season does besides experience (decision 38):
    Labor Points, a workshop's scores, progress records (finished ones
    noted), books written, Virtues gained, formulas, an Aging roll."""
    character.labor_points += work.labor_points
    character.workshop_innovation += work.innovation
    character.workshop_raw_materials += work.raw_materials
    for kind, name, target, points in work.progress:
        record = sw.progress_of(character, kind, name)
        if record is None or record.done:
            record = Progress(kind, name, target)
            character.progress.append(record)
        record.points += points
        record.target = target or record.target
        if record.target and record.points >= record.target and not record.done:
            record.done = True
            if kind == "formula":
                character.formulas.append(name)
            character.diary.append(
                DiaryEntry(
                    year=plan.year,
                    season=plan.season,
                    name=f"Finished: {name}",
                    details=f"{record.points}/{record.target}: "
                    + _FINISHED.get(kind, "done."),
                    activity=rules.ACTIVITIES[plan.activity].label,
                )
            )
    for book in work.books:
        saga.books.append(_copy_book(saga, book))
    for vf_id in work.add_vfs:
        if vf_id:
            character.virtues_flaws.append(VirtueFlawInstance(vf_id))
    if plan.activity == "undergo_initiation":
        if work.ordeal:
            character.ordeal, character.initiations_since_ordeal = work.ordeal, 0
        elif character.ordeal:
            character.initiations_since_ordeal += 1
    if work.summa_level is not None:
        book_id, level = work.summa_level
        book = next((b for b in saga.books if b.id == book_id), None)
        if book is not None:
            book.level = level
    if plan.activity == "bind_catalog":
        character.raw_vis["vim"] = character.raw_vis.get("vim", 0) - 1
        if not character.raw_vis["vim"]:
            del character.raw_vis["vim"]
        lab = saga.laboratory(character.assigned_lab_id)
        if lab is not None:
            lab.arcane_connections.append(
                ArcaneConnection(
                    new_instance_id(),
                    "the covenant library (its catalog)",
                    fixed=True,
                    fixed_year=plan.year,
                    fixed_season=plan.season,
                )
            )
    if work.aging_roll:
        born = character.background.year_born
        if born is not None:
            age_character(saga, character, saga.current_year - born, random.Random())


#: What finishing each kind of progress means.
_FINISHED = {
    "item": "the item is made.",
    "pilgrimage": "the pilgrimage's aim is achieved; the troupe picks its outcome "
    "(a Virtue, a Flaw lost, a penance met...).",
    "taming": "the animal is tamed.",
    "artwork": "the work of art is finished.",
    "formula": "the formula is known.",
}


def year_end_business(saga: Saga) -> list[SeasonRecordLine]:
    """A business's yearly costs (City & Guild), in Winter: 36 Labor Points,
    and 5 for each point of Raw Materials."""
    lines: list[SeasonRecordLine] = []
    for character in saga.characters:
        if not character.labor_points and not character.workshop_raw_materials:
            continue
        cost = (
            sw.BUSINESS_UPKEEP
            + sw.RAW_MATERIALS_UPKEEP * character.workshop_raw_materials
        )
        character.labor_points -= cost
        character.diary.append(
            DiaryEntry(
                year=saga.current_year,
                season=saga.current_season,
                name=f"Business upkeep: -{cost} Labor Points",
                details=f"Labor Points now {character.labor_points} (City & Guild).",
                activity="Aging",
            )
        )
        lines.append(
            SeasonRecordLine(
                character.id,
                character.name,
                character.covenant_id,
                "Business upkeep",
                "",
                f"-{cost} Labor Points",
            )
        )
    return lines


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
    if character.ordeal:
        lines.append(
            f"Last Ordeal: {character.ordeal} ({character.initiations_since_ordeal} "
            "Initiation(s) since)"
        )
    return "\n".join(escape(line) for line in lines)


def apply_book_work(
    saga: Saga, character: Character, plan: SeasonPlan, work: bs.BookWork
) -> None:
    """A season of book work (STORY-910, 914): points toward a summa, the
    books made, Lab Texts rewritten, who can read whose Lab Texts."""
    key = bs.project_key(plan)
    saga.lab_projects = [p for p in saga.lab_projects if p.spell_id != key]
    if not work.finished:
        saga.lab_projects.append(LabProject(character.id, key, work.points_after))
        season, year = next_season(plan.season, plan.year)
        if plan_for(saga, character, season, year) is None:
            set_plan(saga, replace(plan, season=season, year=year))
        return
    if work.made is not None:
        for _ in range(max(1, work.copies)):
            saga.books.append(_copy_book(saga, work.made))
    for book in saga.books:
        if book.id in work.rewritten:
            book.raw = False
    if work.access is not None:
        reader_id, author, level = work.access
        reader = saga.character(reader_id)
        if reader is not None:
            bs.grant_access(reader, author, level, "taught")


def _apply_taming(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    plan: SeasonPlan,
    work: lab_seasons.LabWork,
) -> None:
    """A season of Hermetic taming: its points; tamed, a Lab Text of it."""
    name = plan.title.strip()
    record = sw.progress_of(magus, "taming", name)
    if record is None or record.done:
        record = Progress("taming", name, work.level)
        magus.progress.append(record)
    record.points = work.points_after
    if work.finished:
        record.done = True
        saga.books.append(
            Book(
                id=f"taming_{magus.id}_{new_instance_id()}",
                name=f"Lab Text: taming {name}",
                type="Lab Text",
                author=magus.name,
                author_id=magus.id,
                raw=True,
                owner_kind="laboratory",
                owner_id=lab.id,
                year_published=plan.year,
                level=work.level,
                text_kind=TEXT_OTHER,
                technique="Rego",
                form=plan.form,
                description=f"Taming a creature like {name} (Might {work.level}).",
            )
        )
    else:
        season, year = next_season(plan.season, plan.year)
        if plan_for(saga, magus, season, year) is None:
            set_plan(saga, replace(plan, season=season, year=year, days_away=0))


def _apply_laboratory(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    plan: SeasonPlan,
    work: lab_seasons.LabWork,
) -> None:
    """What a season of work on the laboratory does (STORY-915)."""
    if plan.activity == ls.MOVE:
        for vf_id in work.loses_vf:
            ls.remove_vf(lab, vf_id)
        for vf_id in work.gains_vf:
            ls.add_vf(lab, vf_id)
        if plan.by_spell or work.finished:
            lab.location = plan.title.strip()
            lab.move_seasons = 0
        else:
            lab.move_seasons += 1
            season, year = next_season(plan.season, plan.year)
            if plan_for(saga, magus, season, year) is None:
                set_plan(saga, replace(plan, season=season, year=year, days_away=0))
        return
    if plan.activity == ls.BUILD:
        if work.second_season:
            ls.remove_vf(lab, ls.BASIC)
        else:
            ls.add_vf(lab, ls.BASIC)
            season, year = next_season(plan.season, plan.year)
            if plan_for(saga, magus, season, year) is None:
                set_plan(saga, replace(plan, season=season, year=year, days_away=0))
        return
    # Refining or taking over: the Refinement it now has, and the roll's
    # Virtues and Flaws.
    lab.characteristics.refinement += work.refinement - ls.refinement(lab)
    for vf_id in work.loses_vf:
        ls.remove_vf(lab, vf_id)
    for vf_id in work.gains_vf:
        ls.add_vf(lab, vf_id)


def _apply_experiment(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    plan: SeasonPlan,
    work: lab_seasons.LabWork,
) -> bool:
    """What the Extraordinary Results do (STORY-916; Hedda 2026-09-30: applied
    automatically and noted in the Diary): Discovery xp; a Disaster's Warping,
    lab Flaws and wounds; a destroyed creation; the effects the creation
    keeps; research points. True when nothing else of the season applies."""
    chart = work.experiment
    assert chart is not None
    for subject, xp in chart.xp:
        _add_xp(magus, subject, xp)
    lines = list(chart.results)
    everyone = [magus, *ls.assistants(saga, magus, plan)]
    if chart.zeroes:
        for person in everyone:
            gain_warping(saga, person, chart.zeroes, random.Random())
    if chart.lab_flaw:
        ls.add_vf(lab, chart.lab_flaw)
    if chart.zeroes >= 4:
        for person in everyone:
            person.wounds.heavy += 2
        lines.append("Two Heavy Wounds for everyone in the lab.")
    if chart.zeroes >= 5:
        for person in everyone:
            person.wounds.incapacitated = True
        lines.append("An Incapacitating Wound for everyone in the lab.")
    creation = plan.activity in _CREATIONS
    if chart.zeroes >= 2 or (chart.failure and chart.failure_die == 0 and creation):
        lines.append(_destroy(saga, magus, plan, work, whole=chart.zeroes < 2))
    elif chart.effects and not chart.wasted:
        _keep_effects(saga, plan, work, chart.effects)
    # A goal named on the plan and not yet on the sheet is made, of the
    # kind the plan chose.
    goal = (
        ex.goal(magus, plan.research, plan.research_kind)
        if plan.research.strip()
        else None
    )
    stop = chart.wasted
    if plan.activity == ex.STABILIZE and goal is not None:
        stop = True
        pool = lab_seasons.vis_pool(saga, magus, plan)
        for art, pawns in work.vis_cost.items():
            left = pool.get(art.lower(), 0) - pawns
            if left > 0:
                pool[art.lower()] = left
            else:
                pool.pop(art.lower(), None)
        if chart.wasted or chart.no_benefit:
            goal.stabilizing_seasons = 0
            lines.append("The Discovery isn't stabilized: try again.")
        else:
            goal.stabilizing_seasons += 1
            if work.finished:
                goal.points += work.research_magnitude
                lines.append(
                    f"Stabilized: +{work.research_magnitude} points toward "
                    f"{goal.name} ({goal.points}/{goal.target}); a Lab Text of it "
                    "is written."
                )
                goal.pending_magnitude = 0
                goal.stabilizing_seasons = 0
                goal.discovery_shift = 0
                saga.books.append(_discovery_text(saga, magus, lab, goal, work))
        if work.finished or chart.wasted or chart.no_benefit:
            warping = work.research_warping
            if warping:
                gain_warping(saga, magus, warping, random.Random())
    elif goal is not None and goal.insights > 0 and work.finished and not chart.wasted:
        magnitude = max(1, -(-work.level // 5))
        goal.points += magnitude
        goal.insights -= 1
        lines.append(
            f"The insight's effect is invented: +{magnitude} points toward "
            f"{goal.name} ({goal.points}/{goal.target})."
        )
    elif goal is not None and chart.discovery and not chart.wasted:
        goal.pending_magnitude = max(1, -(-work.level // 5))
        goal.discovery_seasons = max(1, lab_seasons.seasons_left(work) + 1)
        goal.discovery_lab_total = int(work.lab_total.total)
        goal.discovery_risk = plan.risk
        goal.discovery_vis = sum(work.vis_cost.values())
        goal.discovery_vis_art = next(iter(work.vis_cost), "")
        made = work.spell or work.effect
        goal.discovery_technique = made.technique if made else plan.technique
        goal.discovery_form = made.form if made else plan.form
        lines.append(
            f"A Discovery toward {goal.name}: stabilize it (magnitude "
            f"{goal.pending_magnitude}) in a later season."
        )
    if goal is not None:
        lines += _goal_reached(magus, goal)
    lab.diary.append(
        DiaryEntry(
            year=plan.year,
            season=plan.season,
            name="Arcane Experimentation",
            details=f"{magus.name}: " + " ".join(lines),
            activity="Arcane Experimentation",
        )
    )
    return stop


#: Lab work whose creation a Complete Failure (a simple die of 0) destroys.
_CREATIONS = (
    es.INSTIL,
    es.LESSER_WORK,
    es.CHARGED_WORK,
    fs.BIND,
    fs.EMPOWER,
)


def _destroy(
    saga: Saga,
    magus: Character,
    plan: SeasonPlan,
    work: lab_seasons.LabWork,
    *,
    whole: bool,
) -> str:
    """A creation destroyed: an invention's or instilling's progress lost
    (Disaster), or with `whole` (a Complete Failure's 0) the item or the
    familiar itself."""
    key = project_key(plan)
    saga.lab_projects = [
        p
        for p in saga.lab_projects
        if not (
            p.character_id == magus.id
            and p.spell_id == (work.spell.id if work.spell else key)
        )
    ]
    saga.season_plans = [
        p
        for p in saga.season_plans
        if not (
            p.character_id == magus.id
            and key is not None
            and project_key(p) == key
            and (p.year, SEASONS.index(p.season))
            > (plan.year, SEASONS.index(plan.season))
        )
    ]
    device, effect = work.device, work.effect
    if device is not None and (
        whole or plan.activity in (es.LESSER_WORK, es.CHARGED_WORK)
    ):
        if device in saga.enchanted_devices:
            saga.enchanted_devices.remove(device)
        return f"{device.name} is destroyed."
    if device is not None and effect is not None:
        if effect in device.effects:
            device.effects.remove(effect)
        return f"{ed.effect_name(effect)} is lost from {device.name}."
    familiar = work.familiar
    if familiar is not None and whole and plan.activity in (fs.BIND, fs.EMPOWER):
        if familiar in saga.familiars:
            saga.familiars.remove(familiar)
        return f"{familiar.name} is destroyed."
    if work.power is not None:
        work.power.instilling_progress = 0
        return f"{work.power.name}'s progress is lost."
    if plan.activity == lab_seasons.TAMING:
        record = sw.progress_of(magus, "taming", plan.title.strip())
        if record is not None:
            record.points = 0
        return "The taming's progress is lost."
    return "The work so far is lost."


def _keep_effects(
    saga: Saga, plan: SeasonPlan, work: lab_seasons.LabWork, effects: list[str]
) -> None:
    """Side effects and modified effects stay with the creation ("warts and
    all"): an invention carries them to its spell; an item's effect and a
    bond power keep them in their description."""
    if work.effect is not None:
        extra = "; ".join(effects)
        work.effect.description = (
            f"{work.effect.description}\nExperimental: {extra}".strip()
        )
    elif work.power is not None:
        extra = "; ".join(effects)
        work.power.cosmetic_trait = f"{work.power.cosmetic_trait} ({extra})".strip()
    elif plan.activity == lab_seasons.INVENT:
        work.carried_effects = list(effects)


def _goal_reached(magus: Character, goal) -> list[str]:
    """A research goal reaching its target grants what it names (Hedda
    2026-09-30: automatically): an Ability (the points as its xp), or a
    Virtue."""
    if goal.reached or goal.points < goal.target:
        return []
    goal.reached = True
    lines = [f"The {goal.kind} Breakthrough {goal.name} is made."]
    if goal.grant_kind == "Ability" and goal.grant:
        found = next((a for a in magus.abilities if a.name == goal.grant), None)
        if found is None:
            found = Ability(goal.grant, category="Arcane")
            magus.abilities.append(found)
        found.xp += goal.points
        lines.append(f"{goal.grant}: +{goal.points} xp.")
    elif goal.grant_kind == "Virtue" and goal.grant:
        magus.virtues_flaws.append(VirtueFlawInstance(goal.grant))
        lines.append("Its Virtue is added.")
    else:
        lines.append("The troupe records what it grants.")
    return lines


def _discovery_text(saga, magus, lab, goal, work) -> Book:
    return Book(
        id=f"discovery_{magus.id}_{new_instance_id()}",
        name=f"Lab Text: Discovery toward {goal.name}",
        type="Lab Text",
        author=magus.name,
        author_id=magus.id,
        raw=True,
        owner_kind="laboratory",
        owner_id=lab.id,
        year_published=saga.current_year,
        level=5 * work.research_magnitude,
        text_kind=TEXT_OTHER,
        technique=goal.discovery_technique,
        form=goal.discovery_form,
    )


def apply_lab_work(saga: Saga, magus: Character, outcome: rules.Outcome) -> None:
    """A season of lab work: the invention's points, and when it's done, the
    spell known, a Lab Text in the laboratory and the lab's Diary entry."""
    work = outcome.lab_work
    plan = outcome.plan
    lab = saga.laboratory(plan.lab_id)
    if work is None or lab is None:
        return
    if work.experiment is not None and _apply_experiment(saga, magus, lab, plan, work):
        return
    spell = work.spell
    if spell is None:
        _apply_one_season_work(saga, magus, lab, outcome, work)
        return
    carried = (
        next(
            (
                p.effects
                for p in saga.lab_projects
                if p.character_id == magus.id and p.spell_id == spell.id
            ),
            [],
        )
        + work.carried_effects
    )
    saga.lab_projects = [
        p
        for p in saga.lab_projects
        if not (p.character_id == magus.id and p.spell_id == spell.id)
    ]
    if work.finished:
        project = spell.id
        if plan.design is not None:
            spell = _invented_spell(saga, magus, plan.design)
        if carried:
            spell = _with_effects(saga, magus, spell, carried)
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
        saga.lab_projects.append(
            LabProject(magus.id, spell.id, work.points_after, carried)
        )
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


# -- asking about a Discovery (STORY-916) -------------------------------------


def discovery_moves(
    saga: Saga, worked: Sequence[rules.Outcome]
) -> list[tuple[rules.Outcome, str]]:
    """The experiments seeking a Discovery whose chart roll the risk
    modifier can move onto 10, with the question to ask."""
    found: list[tuple[rules.Outcome, str]] = []
    for outcome in worked:
        work = outcome.lab_work
        chart = work.experiment if work is not None else None
        if chart is None or chart.discovery_shift is None:
            continue
        character = saga.character(outcome.character_id)
        name = character.name if character else "The magus"
        found.append(
            (
                outcome,
                f"{name}'s experiment toward {outcome.plan.research.strip()} can "
                f"reach a Discovery by moving its roll {chart.discovery_shift:+d} "
                "(within the risk modifier). Take it? The same move is then made "
                "every season of this project and when stabilizing.",
            )
        )
    return found


def take_discovery_move(saga: Saga, outcome: rules.Outcome, yes: bool) -> None:
    """Record the answer: a Discovery, and the move kept on the goal."""
    work = outcome.lab_work
    chart = work.experiment if work is not None else None
    character = saga.character(outcome.character_id)
    if work is None or chart is None or chart.discovery_shift is None:
        return
    if character is None or not yes:
        chart.discovery_shift = None
        if chart.no_benefit:
            plain = chart.fallback
            if isinstance(plain, lab_seasons.LabWork):
                plain.experiment = chart
                outcome.lab_work = plain
            else:
                chart.wasted = True
        chart.fallback = None
        return
    goal = ex.goal(character, outcome.plan.research, outcome.plan.research_kind)
    goal.discovery_shift = chart.discovery_shift
    art = work.spell.technique if work.spell is not None else "Vim"
    ex.move_to_discovery(chart, random.Random(), outcome.plan.risk, art, saga)
    chart.fallback = None
    outcome.notes = [
        n for n in outcome.notes if not n.startswith("Extraordinary Results: ")
    ] + ["Extraordinary Results: " + " ".join(chart.results)]
