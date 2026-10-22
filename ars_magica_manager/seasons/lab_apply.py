"""Applying a season's lab work: inventing, enchanting, familiars,
supplement activities, book work, taming, experiments and Discoveries."""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import replace

from .. import book_kinds, research_text, spell_parameters, storage
from .. import books as bk
from .. import enchanted_devices as ed
from .. import spells as spl
from ..models import (
    SEASONS,
    STORY_EVENT,
    TEXT_OTHER,
    Ability,
    ArcaneConnection,
    Book,
    Breakthrough,
    Character,
    CovenantDiaryEntry,
    DiaryEntry,
    KnownSpell,
    Laboratory,
    LabProject,
    Ordeal,
    Progress,
    ResearchAttempt,
    Saga,
    SeasonPlan,
    SeasonRecordLine,
    VirtueFlawInstance,
    new_instance_id,
    next_season,
)
from ..rules import activities as rules
from ..rules import book_seasons as bs
from ..rules import creation_access as access
from ..rules import creation_characteristics as cch
from ..rules import enchant_seasons as es
from ..rules import experiment as ex
from ..rules import familiar_seasons as fs
from ..rules import lab_seasons, research
from ..rules import laboratory_seasons as ls
from ..rules import supplement_work as sw
from ..world import takes_part_in_play
from .character_effects import _add_xp, age_character, gain_warping
from .lab_queue import (
    _effect_text,
    _invented_spell,
    _lab_text_book,
    _longevity_text,
    _with_effects,
    project_key,
)
from .plans import plan_for, plan_subject, set_plan, work_text

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
        # A new ritual replaces the old, with what experimenting left on it;
        # each step of potency moves the modifier by 1.
        steps = sum(e.potency for e in work.carried_effects)
        work.subject.aging.longevity_modifier = max(0, work.longevity + steps)
        work.subject.aging.longevity_effects = list(work.carried_effects)
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
    """Perform a Longevity Ritual again from its Lab Text, now:
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
    """What a season of enchanting does to its device; an
    effect instilled leaves a raw Lab Text in the laboratory."""
    device, effect = work.device, work.effect
    if device is None:
        return
    instilling = (es.LESSER_WORK, es.CHARGED_WORK, es.INSTIL)
    if effect is not None and plan.activity in instilling and work.finished:
        text = es.lab_text_of(saga, plan)
        if text is not None and not effect.experimental_effects:
            # A Lab Text reproduces the effect exactly, warts and all.
            effect.experimental_effects = [
                replace(e) for e in text.experimental_effects
            ]
            ex.apply_changes(effect, effect.experimental_effects)
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
    """What a season of familiar work does."""
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
    for instance in work.remove_vfs:
        if instance in character.virtues_flaws:
            cch.unapply_virtue(saga, character, instance)
            character.virtues_flaws.remove(instance)
    for instance in work.add_vfs:
        if instance.vf_id:
            character.virtues_flaws.append(instance)
            cch.apply_virtue(saga, character, instance)
    if plan.activity == "undergo_initiation":
        # This Initiation used up a step of each past Ordeal's reduction;
        # one past its third Initiation lowers nothing more.
        for ordeal in character.ordeals:
            ordeal.initiations_since += 1
        character.ordeals = [o for o in character.ordeals if o.initiations_since < 3]
        if work.ordeal:
            character.ordeals.append(Ordeal(work.ordeal))
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
        if not takes_part_in_play(character) or (
            not character.labor_points and not character.workshop_raw_materials
        ):
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


def apply_book_work(
    saga: Saga, character: Character, plan: SeasonPlan, work: bs.BookWork
) -> None:
    """A season of book work: points toward a summa, the
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
    if work.florilegium is not None:
        title, bound, bonus = work.florilegium
        codex = bk.new_codex(saga, title)
        codex.collection, codex.florilegium_bonus = book_kinds.FLORILEGIUM, bonus
        for book in saga.books:
            if book.id in bound:
                book.codex_id = codex.id
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
    """What a season of work on the laboratory does."""
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
    """What the Extraordinary Results do (applied
    automatically and noted in the Diary): Discovery xp; a Disaster's Warping,
    lab Flaws and wounds; a destroyed creation; the effects the creation
    keeps; research points. True when nothing else of the season applies."""
    chart = work.experiment
    assert chart is not None
    for subject, xp in chart.xp:
        _add_xp(magus, subject, xp)
    lines = list(chart.results)
    lines += _disaster(saga, magus, lab, plan, chart)
    lines += _extra_vis(saga, magus, plan, chart)
    lines += _bonus_spells(saga, magus, lab, chart)
    lines += _stories(saga, magus, lab, plan, chart)
    creation = plan.activity in _CREATIONS
    investigating = plan.activity == es.INVESTIGATE
    if investigating and ex.destroys(chart):
        # The item investigated is destroyed, unless an effect of its own
        # protects it with a level above the Lab Total.
        if chart.protected:
            lines.append("An effect of the item's own protects it: it survives.")
        elif work.device is not None:
            lines.append(_destroy(saga, magus, plan, work, whole=True))
    elif chart.zeroes >= 2 or (chart.failure and chart.failure_die == 0 and creation):
        lines.append(_destroy(saga, magus, plan, work, whole=chart.zeroes < 2))
    elif chart.effects and not chart.wasted:
        _keep_effects(saga, magus, plan, work, chart)
    # A goal named on the plan and not yet on the sheet is made, of the
    # kind the plan chose.
    goal = (
        ex.goal(magus, plan.research, plan.research_kind)
        if plan.research.strip()
        else None
    )
    stop = chart.wasted
    points = goal.points if goal is not None else 0
    kind = "seek"
    if plan.activity == ex.STABILIZE and goal is not None:
        stop = True
        kind = "stabilize"
        lines += _stabilize(saga, magus, lab, plan, work, goal)
    elif goal is not None and goal.insights > 0 and work.finished and not chart.wasted:
        kind = "invent insight"
        lines.append(_invent_insight(work, goal))
    elif goal is not None and chart.discovery and not chart.wasted:
        lines.append(_record_discovery(plan, work, goal))
    if goal is not None:
        _log_attempt(plan, lab, work, goal, kind, goal.points - points)
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


def _log_attempt(
    plan: SeasonPlan,
    lab: Laboratory,
    work: lab_seasons.LabWork,
    goal: Breakthrough,
    kind: str,
    points: int,
) -> None:
    """The season's line in the goal's Research log."""
    chart = work.experiment
    assert chart is not None
    stabilizing = kind == "stabilize"
    name = lab_seasons.made_name(work)
    if stabilizing:
        name = goal.discovered_from[-1] if goal.discovered_from else ""
    research.record(
        goal,
        ResearchAttempt(
            year=plan.year,
            season=plan.season,
            kind=kind,
            work=name,
            magnitude=(
                work.research_magnitude
                if stabilizing
                else spl.level_magnitude(work.level)
            ),
            lab_total=int(work.lab_total.total),
            risk=goal.discovery_risk if stabilizing else plan.risk,
            die=chart.die,
            botch_dice=chart.botch_dice,
            zeroes=chart.zeroes,
            move=chart.move,
            result=" ".join(chart.results),
            discovery=chart.discovery and not chart.wasted and not stabilizing,
            points=points,
            warping=(
                work.research_warping
                if stabilizing and (work.finished or chart.wasted or chart.no_benefit)
                else 0
            ),
            lab_id=lab.id,
            effects=[replace(e) for e in chart.effects],
        ),
    )


def _disaster(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    plan: SeasonPlan,
    chart: ex.Extraordinary,
) -> list[str]:
    """A botch's Warping for everyone in the lab, the lab Flaw it gives, and
    the wounds of a bad one; the Diary lines for the wounds."""
    lines: list[str] = []
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
    if chart.zeroes >= ex.DISASTER_CHOICE and chart.disaster_choice == "covenant":
        chart.stories.append(
            "The Disaster's after-effects threaten the whole covenant (the "
            "storyguide's story)."
        )
    elif chart.zeroes >= ex.DISASTER_CHOICE:
        for person in everyone:
            person.wounds.incapacitated = True
        for flaw in _DESTROYED:
            ls.add_vf(lab, flaw)
        lines.append(
            "The laboratory is destroyed: it is Deformed and Unstable and must "
            "be rebuilt from nothing. An Incapacitating Wound for everyone in "
            "the lab."
        )
    return lines


#: The Flaws of a laboratory a Disaster destroys, to be rebuilt from
#: nothing.
_DESTROYED = ("labvf_deformed", "labvf_unstable")


def _extra_vis(
    saga: Saga, magus: Character, plan: SeasonPlan, chart: ex.Extraordinary
) -> list[str]:
    """The extra vis a special result asked for, paid from the pool."""
    if not chart.extra_vis or chart.wasted:
        return []
    pool = lab_seasons.vis_pool(saga, magus, plan)
    for art, pawns in chart.extra_vis.items():
        key = art.lower()
        pool[key] = max(0, pool.get(key, 0) - pawns)
        if not pool[key]:
            del pool[key]
    return []


def _bonus_spells(
    saga: Saga, magus: Character, lab: Laboratory, chart: ex.Extraordinary
) -> list[str]:
    """The spells a special result let the magus also create: known, with
    a Lab Text in the laboratory."""
    lines = []
    for values in chart.bonus_spells:
        spell = spl.add_invented_spell(
            saga, magus, values["name"], values["technique"], values["form"]
        )
        for name, value in values.items():
            if name not in ("name", "technique", "form") and hasattr(spell, name):
                setattr(spell, name, value)
        spell.source = "Invented"
        if not any(k.spell_id == spell.id for k in magus.spells_known):
            magus.spells_known.append(KnownSpell(spell_id=spell.id))
        saga.books.append(_lab_text_book(saga, magus, lab, spell))
        lines.append(
            f"{magus.name} also creates {spell.name} ({spl.shorthand(spell)})."
        )
    return lines


def _stories(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    plan: SeasonPlan,
    chart: ex.Extraordinary,
) -> list[str]:
    """Each story event, a line in the lab's Diary entry and an open Story
    Event in the covenant's Diary."""
    covenant = saga.covenant(lab.covenant_id) if lab.covenant_id else None
    lines = []
    for story in chart.stories:
        lines.append(f"Story event: {story}")
        if covenant is not None:
            covenant.diary.append(
                CovenantDiaryEntry(
                    year=plan.year,
                    season=plan.season,
                    name=f"From {magus.name}'s experiment",
                    details=story,
                    category=STORY_EVENT,
                    status="Open",
                )
            )
    return lines


def _stabilize(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    plan: SeasonPlan,
    work: lab_seasons.LabWork,
    goal: Breakthrough,
) -> list[str]:
    """A season stabilizing a Discovery: its vis spent, a season counted (or
    the count lost), and once finished the points and a Lab Text of it;
    research Warping when it ends."""
    chart = work.experiment
    assert chart is not None
    lines: list[str] = []
    pool = lab_seasons.vis_pool(saga, magus, plan)
    for art, pawns in work.vis_cost.items():
        left = pool.get(art.lower(), 0) - pawns
        if left > 0:
            pool[art.lower()] = left
        else:
            pool.pop(art.lower(), None)
    if chart.wasted or chart.no_benefit:
        goal.stabilizing_seasons = 0
        goal.retry_season, goal.retry_year = next_season(plan.season, plan.year)
        lines.append(
            "The Discovery isn't stabilized: try again next season "
            f"({goal.retry_season} {goal.retry_year}), or it is lost."
        )
    else:
        goal.retry_season, goal.retry_year = "", 0
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
    return lines


def _invent_insight(work: lab_seasons.LabWork, goal: Breakthrough) -> str:
    """An insight's effect invented: its magnitude toward the goal."""
    magnitude = spl.level_magnitude(work.level)
    goal.points += magnitude
    goal.insights -= 1
    return (
        f"The insight's effect is invented: +{magnitude} points toward "
        f"{goal.name} ({goal.points}/{goal.target})."
    )


def _record_discovery(
    plan: SeasonPlan, work: lab_seasons.LabWork, goal: Breakthrough
) -> str:
    """A Discovery toward the goal, kept on it to stabilize later."""
    goal.pending_magnitude = spl.level_magnitude(work.level)
    goal.discovery_seasons = max(1, lab_seasons.seasons_left(work) + 1)
    goal.discovery_lab_total = int(work.lab_total.total)
    goal.discovery_risk = plan.risk
    goal.discovery_vis = sum(work.vis_cost.values())
    goal.discovery_vis_art = next(iter(work.vis_cost), "")
    made = work.spell or work.effect
    goal.discovery_technique = made.technique if made else plan.technique
    goal.discovery_form = made.form if made else plan.form
    goal.retry_season, goal.retry_year = "", 0
    name = lab_seasons.made_name(work)
    if name and name not in goal.discovered_from:
        goal.discovered_from.append(name)
    return (
        f"A Discovery toward {goal.name}: stabilize it (magnitude "
        f"{goal.pending_magnitude}) in a later season."
    )


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
    saga: Saga,
    magus: Character,
    plan: SeasonPlan,
    work: lab_seasons.LabWork,
    chart: ex.Extraordinary,
) -> None:
    """Side effects and modified effects stay with the creation ("warts and
    all"): an item's effect (or, investigating, the power the storyguide
    named) and a bond power take them at once, with any new Range,
    Duration or Target; a familiar's binding taints the bond; an invention
    and a Longevity Ritual carry them to the spell or ritual they make."""
    effects = list(chart.effects)
    theory = ls.magic_theory(magus)
    for effect in effects:
        effect.year, effect.season = plan.year, plan.season
        effect.magic_theory = theory
    device = work.device
    if plan.activity == es.INVESTIGATE and device is not None:
        for index, effect in enumerate(effects):
            target_id = chart.targets[index] if index < len(chart.targets) else ""
            power = next((e for e in device.effects if e.id == target_id), None)
            if power is None and device.effects:
                power = device.effects[0]
            if power is not None:
                power.experimental_effects.append(effect)
                ex.apply_changes(power, [effect])
    elif work.effect is not None:
        work.effect.experimental_effects += effects
        ex.apply_changes(work.effect, effects)
    elif work.power is not None:
        work.power.experimental_effects += effects
    elif work.familiar is not None and plan.activity == fs.BIND:
        work.familiar.experimental_effects += effects
    elif plan.activity in (lab_seasons.INVENT, lab_seasons.LONGEVITY):
        work.carried_effects = effects


def _goal_reached(magus: Character, goal) -> list[str]:
    """A research goal reaching its target grants what it names
    automatically: an Ability (the points as its xp), or a
    Virtue."""
    if goal.reached or goal.points < goal.target:
        return []
    goal.reached = True
    lines = [f"The {goal.kind} Breakthrough {goal.name} is made."]
    if goal.grant_kind == "Ability" and goal.grant:
        found = next((a for a in magus.abilities if a.name == goal.grant), None)
        if found is None:
            found = Ability(
                goal.grant,
                category="Arcane",
                xp_table=access.ability_xp_table(goal.grant),
            )
            magus.abilities.append(found)
        found.xp += goal.points
        lines.append(f"{goal.grant}: +{goal.points} xp.")
    elif goal.grant_kind == "Virtue" and goal.grant:
        magus.virtues_flaws.append(VirtueFlawInstance(goal.grant))
        lines.append("Its Virtue is added.")
    elif goal.grant_kind == "Parameter" and spell_parameters.parse_grant(goal.grant):
        names = ", ".join(p.name for p in spell_parameters.parse_grant(goal.grant))
        lines.append(f"Invent Spell now offers {magus.name} {names}.")
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


def set_up_new_lab(saga: Saga, magus: Character, outcome: rules.Outcome) -> Laboratory:
    """The first season of setting up a laboratory where there was none: it
    is made in the magus's covenant, theirs, with the Basic Flaw, and the
    season is written in its Diary."""
    plan = outcome.plan
    name = ls.new_lab_name(magus, plan)
    lab = Laboratory(
        id=storage.generate_unique_id(name, [lab.id for lab in saga.laboratories]),
        covenant_id=magus.covenant_id,
        name=name,
        owner_id=magus.id,
    )
    ls.add_vf(lab, ls.BASIC)
    lab.diary.append(
        DiaryEntry(
            year=plan.year,
            season=plan.season,
            name=rules.ACTIVITIES[ls.NEW].label,
            details=f"{magus.name}: the laboratory works, with the Basic Flaw "
            "until a second season's work in it.",
            activity=_LAB_DIARY_ACTIVITY[ls.BUILD],
        )
    )
    saga.laboratories.append(lab)
    outcome.new_lab_id = lab.id
    return lab


def plan_lab_finish(saga: Saga, outcome: rules.Outcome) -> SeasonPlan | None:
    """After a new laboratory's first season: its second, planned as lab
    work in it for the magus's next season (the saga's season once the
    date has moved on), unless they already have a plan for it."""
    magus = saga.character(outcome.character_id)
    lab = saga.laboratory(outcome.new_lab_id) if outcome.new_lab_id else None
    if magus is None or lab is None:
        return None
    season, year = next_season(outcome.plan.season, outcome.plan.year)
    if plan_for(saga, magus, season, year) is not None:
        return None
    plan = SeasonPlan(magus.id, year, season, ls.BUILD, lab_id=lab.id)
    set_plan(saga, plan)
    return plan


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
        if character is None:
            continue
        found.append(
            (
                outcome,
                research_text.move_card(
                    saga,
                    character,
                    outcome.plan.research.strip(),
                    outcome.plan.risk,
                    chart,
                ),
            )
        )
    return found


def take_discovery_move(saga: Saga, outcome: rules.Outcome, yes: bool) -> None:
    """Record the answer: with yes, a Discovery besides the roll's own
    result, and the move kept on the goal."""
    work = outcome.lab_work
    chart = work.experiment if work is not None else None
    character = saga.character(outcome.character_id)
    if work is None or chart is None or chart.discovery_shift is None:
        return
    if character is None or not yes:
        chart.discovery_shift = None
        return
    goal = ex.goal(character, outcome.plan.research, outcome.plan.research_kind)
    goal.discovery_shift = chart.discovery_shift
    ex.move_to_discovery(chart)
    outcome.notes = [
        n for n in outcome.notes if not n.startswith("Extraordinary Results: ")
    ] + ["Extraordinary Results: " + " ".join(chart.results)]
