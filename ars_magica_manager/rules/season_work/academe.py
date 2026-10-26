"""Art & Academe's seasons: recording lectures, universities (an exam at
a season's end, against 6 or 12), vernacular literature, formulas and
experimental philosophy's remedies, medicine, an apothecary's store, and
works of art (progress records carried season to season)."""

from __future__ import annotations

import random

from ... import book_kinds
from ...models import Book, Character, Formula, Saga, SeasonPlan
from .. import activity_groups as groups
from .. import apothecary, dice, philosophy, reputations
from ..rounding import round_down, round_up
from ..scores import ability_level
from .base import (
    CH,
    COMPANIONS,
    SimpleActivity,
    SupplementWork,
    experience_only,
    needs_name,
    needs_subject,
    progress_of,
    register,
    source,
    subject_ability,
)
from .city_guild import _working_season

ACADEME = source("Art & Academe " + CH.format("Art_%26_Academe_Open_Content"), "A&A")
REMEDIES_SOURCE = "Art & Academe, Chapter Five: Experimental Philosophy, pp. 67-78"
#: Theriacs and reagents cost level x doses / REMEDY_LEVELS_PER_POINT
#: apothecary Labor Points, rounded up.
REMEDY_LEVELS_PER_POINT = philosophy.LEVELS_PER_LABOR_POINT
ARTWORK_SOURCE = "Art & Academe, Chapter Eight: Artists, Time Spent Creating, p. 124"
#: Seasons to make a work of art: Aesthetic Quality / ARTWORK_QUALITY_PER_SEASON,
#: rounded up (at least one).
ARTWORK_QUALITY_PER_SEASON = 10
#: Free Expression's bonus to create a work of art (Ars Magica Definitive
#: Edition, Chapter Four: Virtues and Flaws); Inspirational's here is
#: (source to confirm).
ARTWORK_VIRTUE_BONUS = 3
FORMULA_SOURCE = (
    "Art & Academe, Chapter Five: Experimental Philosophy, Researching Formulae, p. 70"
)
#: Experience that makes one formula, and a season of research's default.
FORMULA_XP = 5
LECTURES_SOURCE = (
    "Art & Academe, Chapter Seven: Universities, Lecture Commentaries, p. 102"
)
#: A recorded lecture's Quality: the teacher's Communication + the scribe's
#: Profession: Scribe / LECTURES_SCRIBE_DIVISOR (no rounding stated: down).
LECTURES_SCRIBE_DIVISOR = 2
EXAMS = {"baccalaureus": 6, "magister": 12, "doctor": 12}
#: Before each exam: the seasons at university in all (3 years; 5 more;
#: 10 in all) and the net Good Academic Reputation (Art & Academe p. 100).
EXAM_SEASONS = {"baccalaureus": 12, "magister": 32, "doctor": 40}
EXAM_REPUTATION = {"baccalaureus": 1, "magister": 2, "doctor": 3}
#: A doctor must already hold the magister (DE p. 76).
MAGISTER = "vf_magister_in_artibus"


# -- checks --------------------------------------------------------------------


def _lecture_problems(saga: Saga, teacher: Character, plan: SeasonPlan) -> list[str]:
    """Lecture commentaries (Art & Academe): on an Academic or Arcane
    Ability, never a Hermetic Art; a teacher's number of them is at most
    his score in the Ability."""
    subject = next((a.subject for a in plan.allocations if a.subject), "")
    kind, _, name = subject.partition(":")
    if kind == "art":
        return ["Teaching the Arts is too interactive to record as lectures."]
    if not name:
        return []
    made = sum(
        1
        for b in saga.books
        if b.opus == book_kinds.LECTURE_COMMENTARY
        and b.author_id == teacher.id
        and b.ability == name
    )
    if made >= ability_level(teacher, name):
        return [
            f"{teacher.name} has {made} lecture commentaries on {name}: the most "
            f"a score of {ability_level(teacher, name)} allows."
        ]
    return []


def _record_lectures_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    teacher = saga.character(plan.teacher_id)
    if teacher is None:
        return ["Choose the teacher whose lectures are recorded."]
    return _lecture_problems(saga, teacher, plan)


def _university_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    exam = plan.title.strip().lower()
    if exam not in EXAMS:
        return []
    studied = 1 + sum(r.points for r in character.progress if r.kind == "university")
    if studied < EXAM_SEASONS[exam]:
        return [
            f"The {exam} exam needs {EXAM_SEASONS[exam]} seasons at "
            f"university; with this one {character.name} has {studied} "
            "(Art & Academe p. 100)."
        ]
    if exam == "doctor" and not any(
        vf.vf_id == MAGISTER for vf in character.virtues_flaws
    ):
        return [
            f"The doctor exam needs a magister first: {character.name} "
            "hasn't the Magister in Artibus Virtue (DE p. 76)."
        ]
    net = reputations.net_academic(character.reputations)
    if net < EXAM_REPUTATION[exam]:
        return [
            f"The {exam} exam needs a Good Academic Reputation of "
            f"{EXAM_REPUTATION[exam]} (less any Bad one); {character.name} "
            f"has {net} (Art & Academe p. 100)."
        ]
    return []


# -- outcomes ------------------------------------------------------------------


def _formula_of(
    character: Character, plan: SeasonPlan
) -> tuple[Formula | None, str, int]:
    """The plan's formula (None when its design isn't recorded), its kind
    and the level worked at (the plan's, else the formula's)."""
    known = philosophy.design(character, plan.title.strip())
    if known is not None:
        level = known.level if plan.book_level is None else plan.book_level
        return known, known.kind, level
    kind = philosophy.kind_of(subject_ability(plan)) or philosophy.THERIAC
    return None, kind, plan.book_level or 0


def _ingredients(
    character: Character, kind: str, level: int, doses: int, result: SupplementWork
) -> None:
    """The ingredients' Labor Points: from his own store when he keeps one,
    else an apothecary's (A&A pp. 65, 75, 77)."""
    cost = philosophy.labor_cost(kind, level, doses)
    made = f"{doses} dose(s) of a level {level} {kind}"
    if not cost:
        result.notes.append(f"{made}: no ingredients (parchment and ink).")
    elif apothecary.keeps_store(character):
        result.labor_points -= cost
        result.notes.append(f"{made}: {cost} Labor Points from his own store.")
    else:
        result.notes.append(
            f"{made}: {cost} Labor Points of ingredients from an apothecary's "
            "store (take them off the apothecary's Labor Points)."
        )


def _produce_remedies(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    known, kind, level = _formula_of(character, plan)
    name = plan.title.strip()
    if known is None:
        # A formula with no design recorded: its typed level and doses.
        _ingredients(character, kind, level, max(1, plan.extra_vis), result)
        return
    total = philosophy.lab_total(character, kind, plan.other_modifier)
    result.notes.append(f"Lab Total: {total.line()}, against level {level}.")
    work = philosophy.concoction(total.total, level, known.lab_text)
    if work.problem:
        result.notes.append(work.problem)
        return
    product = philosophy.product_name(name, kind)
    if known.lab_text:
        doses = min(plan.extra_vis, work.doses) if plan.extra_vis > 0 else work.doses
        result.products.append((product, doses))
        result.notes.append(
            f"With its Laboratory Text: {doses} dose(s) of {name} (a Lab Total "
            f"of {total.total} makes up to {work.doses})."
        )
        _ingredients(character, kind, level, doses, result)
        return
    record = progress_of(character, "concoction", name)
    before = record.points if record is not None and not record.done else 0
    result.progress.append(("concoction", name, level, work.points))
    if before + work.points < level:
        result.notes.append(
            f"{work.points} points toward concocting {name} the first time "
            f"({before + work.points}/{level})."
        )
        return
    result.lab_texts.append(name)
    result.products.append((product, 1))
    result.notes.append(f"{name} concocted: a dose, and its Laboratory Text written.")
    _ingredients(character, kind, level, 1, result)


def _produce_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    """A formula concocted must be learned, have a level and a Lab Total
    that reaches it (A&A pp. 70-71)."""
    name = plan.title.strip()
    known, kind, level = _formula_of(character, plan)
    if known is None:
        if plan.book_level is None:
            return ["Choose the formula, or type the product's level."]
        return []
    if name not in character.formulas:
        return [
            f"{character.name} hasn't learned the formula {name} yet: research "
            "it first (A&A p. 70)."
        ]
    if level <= 0:
        return [f"Type the level of {name}."]
    total = philosophy.lab_total(character, kind, plan.other_modifier).total
    problem = philosophy.concoction(total, level, known.lab_text).problem
    return [f"{problem} (A&A p. 71)"] if problem else []


def _medical_season(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    result.notes.append(
        f"Can care for {ability_level(character, 'Chirurgy')} patients (palliative) "
        f"and treat {ability_level(character, 'Medicine')} (therapy) alongside, or "
        "five times as many as the season's whole work."
    )


def _create_art(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    name = plan.title.strip()
    craft = subject_ability(plan)
    if craft.startswith(("Profession", "Craft: Poetry")):
        base = character.characteristics.communication
    else:
        base = character.characteristics.dexterity
    ids = {vf.vf_id for vf in character.virtues_flaws}
    aq = base + ability_level(character, craft) + plan.other_modifier
    if ids & {"vf_inspirational", "vf_free_expression"}:
        aq += ARTWORK_VIRTUE_BONUS
    seasons = max(1, round_up(aq / ARTWORK_QUALITY_PER_SEASON))
    result.progress.append(("artwork", name, seasons, 1))
    result.notes.append(f"Aesthetic Quality {aq}; {seasons} season(s) to make it.")


def _research_formula(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    name = plan.title.strip()
    xp = plan.source_quality if plan.source_quality is not None else FORMULA_XP
    result.progress.append(("formula", name, FORMULA_XP, xp))
    result.notes.append(f"{xp} xp toward the formula {name} ({FORMULA_XP} make it).")
    kind = philosophy.kind_of(subject_ability(plan))
    if kind:
        result.formula_designs.append(Formula(name, kind, plan.book_level or 0))


def _research_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    """A formula is named, and researched in its Academic Ability."""
    named = needs_name(saga, character, plan)
    if named:
        return named
    ability = subject_ability(plan)
    if ability and not philosophy.kind_of(ability):
        return [
            "A formula is researched in Artes Liberales (an inception), "
            "Philosophiae (a reagent) or Medicine (a theriac) (A&A p. 70)."
        ]
    return []


def _attend_university(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    name = plan.title.strip()
    craft = subject_ability(plan)
    result.progress.append(("university", "University", 0, 1))
    exam = name.lower()
    if exam in EXAMS and rng is None:
        result.notes.append(f"The {exam} exam is rolled when the season is played.")
    elif exam in EXAMS and rng is not None:
        reps = reputations.net_academic(character.reputations)
        subject = "Artes Liberales" if exam != "doctor" else craft or "Theology"
        die = dice.stress_die(rng, 1, saga=saga)
        total = (
            character.characteristics.communication
            + ability_level(character, subject)
            + reps
            + die.value
        )
        passed = not die.botched and total >= EXAMS[exam]
        result.notes.append(
            f"The {exam} exam: {total} against {EXAMS[exam]}: "
            + ("passed." if passed else "failed (another year first).")
        )


def _record_lectures(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    name = plan.title.strip()
    teacher = saga.character(plan.teacher_id)
    assert teacher is not None
    quality = teacher.characteristics.communication + round_down(
        ability_level(character, "Profession: Scribe") / LECTURES_SCRIBE_DIVISOR
    )
    subject = next((a.subject for a in plan.allocations if a.subject), "")
    kind, _, what = subject.partition(":")
    result.books.append(
        Book(
            id=f"lectures_{character.id}_{plan.year}_{plan.season.lower()}",
            name=name or f"Lectures of {teacher.name}",
            type="Tractatus",
            opus=book_kinds.LECTURE_COMMENTARY,
            author=teacher.name,
            author_id=teacher.id,
            owner_kind="character",
            owner_id=character.id,
            year_published=plan.year,
            subject_kind="Art" if kind == "art" else "Ability",
            art=what if kind == "art" else "",
            ability=what if kind == "ability" else "",
            quality=quality,
        )
    )
    result.notes.append(f"A tractatus of the lectures, Quality {quality}.")


register(
    SimpleActivity(
        "record_lectures",
        "Record a teacher's lectures",
        "A scribe's season: a tractatus of Quality = the teacher's "
        "Communication + Scribe / 2. Exposure 2 in Profession: Scribe.",
        ACADEME,
        "913",
        group=groups.WRITING,
    ),
    _record_lectures,
    _record_lectures_problems,
)
register(
    SimpleActivity(
        "attend_university",
        "Attend university",
        "A student's season: the lecturer's Source Quality; exams at its end.",
        ACADEME,
        "920",
        None,
        "the lecture's Source Quality",
        COMPANIONS,
        group=groups.STUDY,
    ),
    _attend_university,
    _university_problems,
)
register(
    SimpleActivity(
        "vernacular_literature",
        "Read vernacular literature",
        "Exposure in Abilities the storyguide chooses.",
        ACADEME,
        "920",
        who=COMPANIONS,
        group=groups.STUDY,
    ),
    experience_only,
)
register(
    SimpleActivity(
        "research_formula",
        "Research a formula",
        "Five xp make one formula (an inception, reagent or theriac); "
        "they go into the formula, not the Ability.",
        ACADEME,
        "920",
        5,
        who=COMPANIONS,
        group=groups.STUDY,
        xp_to_work=True,
    ),
    _research_formula,
    _research_problems,
)
register(
    SimpleActivity(
        "medical_season",
        "Medical seasonal work",
        "Care, therapy, regimens, finding ingredients: patients treated; "
        "Exposure 2 in Medicine.",
        ACADEME,
        "920",
        who=COMPANIONS,
        group=groups.WORK,
    ),
    _medical_season,
)
register(
    SimpleActivity(
        "produce_remedies",
        "Produce reagents, theriacs or inceptions",
        "Concoct a formula in a laboratory: a first concoction gathers Lab "
        "Total - level points; with its Laboratory Text, Lab Total / 5 "
        "doses. Exposure 2.",
        ACADEME,
        "920",
        who=COMPANIONS,
        group=groups.WORK,
    ),
    _produce_remedies,
    _produce_problems,
)
register(
    SimpleActivity(
        "apothecary",
        "Keep an apothecary's store",
        "Labor Points. Exposure 2.",
        ACADEME,
        "920",
        who=COMPANIONS,
        group=groups.WORK,
    ),
    _working_season,
    needs_subject,
)
register(
    SimpleActivity(
        "create_art",
        "Create a work of art / seek a sponsor",
        "The work's Aesthetic Quality; Reputation. Exposure 2.",
        ACADEME,
        "920",
        who=COMPANIONS,
        group=groups.WORK,
    ),
    _create_art,
    needs_name,
)
register(
    SimpleActivity(
        "study_artwork",
        "Study another artist's work",
        "A season observing a work made with the same Craft or Profession, "
        "not your own: Source Quality = its Aesthetic Quality / 2; each work "
        "is studied once, like a tractatus (Art & Academe p. 126, with Atlas "
        "Games' errata).",
        ACADEME,
        "920",
        None,
        "half the work's Aesthetic Quality, a work not studied before",
        COMPANIONS,
        group=groups.STUDY,
    ),
    experience_only,
)
