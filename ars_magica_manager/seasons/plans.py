"""Each character's season plan: keeping it, the subjects it can go into,
companions' working seasons, and the text the sheets show for a plan
(lab work, a grog's year and a livelihood included)."""

from __future__ import annotations

import re

from .. import enchanted_devices as ed
from .. import spells as spl
from ..familiars import familiar_of
from ..inhabitants import AUTO_KINDS, character_kind
from ..markup import escape, problem, todo
from ..models import SEASONS, Book, Character, Saga, SeasonPlan
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
    lines += [problem(escape(p)) for p in worked.problems]
    note = working_seasons_note(character, plan)
    if note:
        lines.append(todo(escape(note)))
    if plan.details.strip() and worked.activity and worked.activity.gives_xp:
        lines.append(f"[dim]Notes:[/] {escape(plan.details.strip())}")
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
