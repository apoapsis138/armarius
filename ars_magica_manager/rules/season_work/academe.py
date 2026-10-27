"""Art & Academe's seasons: recording lectures, universities (an exam at
a season's end, against 6 or 12), vernacular literature, formulas and
experimental philosophy's remedies, medicine, an apothecary's store, and
works of art (progress records carried season to season)."""

from __future__ import annotations

import random
from dataclasses import replace

from ... import book_kinds, catalog
from ...models import ArtworkPlan, Book, Character, Formula, Saga, SeasonPlan
from .. import activity_groups as groups
from .. import (
    apothecary,
    artistry,
    book_seasons,
    dice,
    philosophy,
    reputations,
    scholarship,
)
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
#: Free Expression's and Inspirational's bonus to create a work of art.
ARTWORK_VIRTUE_BONUS = artistry.VIRTUE_BONUS
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
    saga: Saga,
    character: Character,
    kind: str,
    level: int,
    doses: int,
    result: SupplementWork,
) -> None:
    """The ingredients' Labor Points: from his own store when he keeps one,
    else the store of his covenant's best apothecary (apothecary.supplier;
    A&A pp. 65, 75, 77)."""
    cost = philosophy.labor_cost(kind, level, doses)
    made = f"{doses} dose(s) of a level {level} {kind}"
    store = apothecary.supplier(saga, character) if cost else None
    if not cost:
        result.notes.append(f"{made}: no ingredients (parchment and ink).")
    elif store is character:
        result.labor_points -= cost
        result.notes.append(f"{made}: {cost} Labor Points from his own store.")
    elif store is not None:
        result.labor_from.append((store.id, cost))
        result.notes.append(
            f"{made}: {cost} Labor Points of ingredients from {store.name}'s "
            "apothecary's store."
        )
    else:
        result.notes.append(
            f"{made}: {cost} Labor Points of ingredients from an apothecary's "
            "store; no apothecary keeps one here, so take them off by hand."
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
        _ingredients(saga, character, kind, level, max(1, plan.extra_vis), result)
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
        _ingredients(saga, character, kind, level, doses, result)
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
    _ingredients(saga, character, kind, level, 1, result)


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


def _art_of(plan: SeasonPlan) -> ArtworkPlan:
    return plan.artwork if plan.artwork is not None else ArtworkPlan()


def _experiment(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random,
    result: SupplementWork,
) -> tuple[artistry.Aesthetic, str]:
    """The experiment: a simple die / 2 (rounded up) on the Aesthetic
    Quality, then at once a stress die on the Artist Experimentation
    Results, both in one step (A&A p. 124). The book gives no season for
    a piece of several; rolling them in the finishing season is the app's
    choice, since a plan keeps nothing between seasons. A ruined piece
    costs Reputation xp equal to its presumed Aesthetic Quality (p. 126),
    the Quality with the die's bonus."""
    craft = subject_ability(plan)
    die = dice.simple_die(rng)
    found = artistry.aesthetic_quality(
        character,
        craft,
        _art_of(plan),
        characteristic=plan.characteristic,
        reputation=artistry.reputation_score(character, craft),
        other=plan.other_modifier,
        experiment_die=die,
    )
    roll = dice.stress_die(rng, 1, saga=saga)
    outcome = artistry.experiment_result(roll.value, roll.botched)
    shown = "a botch" if roll.botched else str(roll.value)
    result.notes.append(
        f"Experimenting: simple die {die} (+{round_up(die / 2)}); the stress die "
        f"{shown}: {artistry.EXPERIMENT_TEXT[outcome]} (A&A p. 124)."
    )
    return found, outcome


def _experiment_reputation(
    character: Character,
    craft: str,
    quality: int,
    outcome: str,
    result: SupplementWork,
) -> int:
    """What the experiment's result does to the Artist Reputation; returns
    the piece's Quality after it (a disparaged piece loses 1)."""
    name = artistry.trade(craft)
    found = artistry.artist_reputation(character, craft)
    rep = found.score if found is not None else 0
    if outcome == "work_praised":
        result.reputation_xp.append((name, max(0, quality)))
    elif outcome == "artist_praised":
        result.reputation_xp.append((name, artistry.xp_to_next(found)))
    elif artistry.loses_nothing(rep):
        if outcome in ("disaster", "ruined", "disparaged"):
            result.notes.append("Artist Reputation 10: he loses no Reputation xp.")
    elif outcome in ("disaster", "disparaged"):
        lost = artistry.xp_of_a_level(found)
        if lost:
            result.reputation_xp.append((name, -lost))
    elif outcome == "ruined":
        result.reputation_xp.append((name, -max(0, quality)))
    return quality - 1 if outcome == "disparaged" else quality


def _create_art(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    name = plan.title.strip()
    craft = subject_ability(plan)
    art = _art_of(plan)
    rep = artistry.reputation_score(character, craft)

    def quality_of(piece: ArtworkPlan) -> artistry.Aesthetic:
        return artistry.aesthetic_quality(
            character,
            craft,
            piece,
            characteristic=plan.characteristic,
            reputation=rep,
            other=plan.other_modifier,
        )

    found = quality_of(art)
    time = artistry.creation_time(
        character, art, quality_of(replace(art, rushed=False)).quality
    )
    record = progress_of(character, "artwork", name)
    before = record.points if record is not None and not record.done else 0
    finishing = before + 1 >= time.seasons
    result.progress.append(("artwork", name, time.seasons, 1))
    result.notes.append(
        f"Aesthetic Quality {found.quality} = {' '.join(found.terms)}; "
        f"{time.days:g} days ({'; '.join(time.notes)}): {time.seasons} season(s)"
        " (A&A pp. 123-125)."
    )
    quality, outcome = found.quality, ""
    if finishing and art.experiment:
        if rng is None:
            result.notes.append("The experiment is rolled when the season is played.")
        else:
            tried, outcome = _experiment(saga, character, plan, rng, result)
            quality = _experiment_reputation(
                character, craft, tried.quality, outcome, result
            )
    if outcome not in ("disaster", "ruined") and artistry.season_xp(quality, rep):
        result.reputation_xp.append((artistry.trade(craft), 1))
        result.notes.append(
            f"Aesthetic Quality over three times his {artistry.trade(craft)} "
            f"Reputation {rep}: 1 xp in it (A&A p. 126)."
        )
    if art.instill_level:
        _instill(character, craft, art, name, result)
    if not finishing:
        return
    if outcome in ("disaster", "ruined"):
        result.notes.append(f"{name} is lost: nothing to show for it.")
        return
    pieces = " (two pieces)" if art.base == "pair" else ""
    result.notes.append(f"{name} finished{pieces}: Aesthetic Quality {quality}.")
    if art.overtime:
        result.aging_roll = True
        result.notes.append("Overtime: an Aging roll now it is done (A&A p. 124).")
    if art.base not in ("years", "decades"):
        weeks = max(0.0, time.days / 2 / 7 - art.assistants)
        result.notes.append(
            f"An Arcane Connection to him for {weeks:g} weeks (half the time to "
            "make it, a week less for each assistant; A&A p. 125)."
        )


def _instill(
    character: Character,
    craft: str,
    art: ArtworkPlan,
    name: str,
    result: SupplementWork,
) -> None:
    """A maestro's spell-like effect instilled as he works (A&A p. 135)."""
    total = artistry.instill_total(character, craft, art)
    points = max(0, total - art.instill_level)
    result.progress.append(("instilling", name, art.instill_level, points))
    result.notes.append(
        f"Instilling a level {art.instill_level} effect: total {total}, {points} "
        f"point(s) toward it; {artistry.instill_fatigue(art.instill_level)} "
        "Fatigue level(s) lost while he works on it (A&A p. 135)."
    )


def _create_art_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    """A work of art is named and made with a Craft or Profession; its
    assistants, wound and magic must be his to use (A&A pp. 124-135)."""
    named = needs_name(saga, character, plan)
    if named:
        return named
    craft = subject_ability(plan)
    if craft and not craft.startswith(("Craft", "Profession")):
        return ["A work of art is made with a Craft or Profession (A&A p. 123)."]
    art = _art_of(plan)
    found: list[str] = []
    ids = {vf.vf_id for vf in character.virtues_flaws}
    if art.assistants and artistry.PROLIFIC in ids:
        found.append("A Prolific Artist works too fast for assistants (A&A p. 134).")
    elif art.assistants > artistry.most_assistants(character):
        found.append(
            f"{character.name} can use at most {artistry.most_assistants(character)} "
            "assistants (his Leadership, A&A p. 125)."
        )
    if art.wound and artistry.LIFE_LINKED not in ids:
        found.append("Only Life-Linked Art adds a self-inflicted wound (A&A p. 134).")
    if art.rushed and art.double_time:
        found.append("Choose half the time or twice the time, not both.")
    problem = artistry.instill_problem(character, craft, art)
    if problem:
        found.append(problem)
    return found


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
    _lecture_xp(saga, teacher, result)


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
        "Create a work of art",
        "The work's Aesthetic Quality and the time to make it; Artist "
        "Reputation xp. Exposure 2.",
        ACADEME,
        "920",
        who=COMPANIONS,
        group=groups.WORK,
    ),
    _create_art,
    _create_art_problems,
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


# -- scholars: editing lectures, seeking a post (A&A pp. 89, 102-103) --------

SCHOLAR_SOURCE = (
    "Art & Academe, Chapter Six, Acquiring a Teaching Position, p. 89; Chapter "
    "Seven, Lecture Commentaries and Academic Reputations, pp. 102-103"
)
SEEK_POST = "seek_post"
EDIT_LECTURES = "edit_lectures"
#: An edited lecture commentary's Quality gain, before the writer's Virtues.
EDIT_QUALITY = 1


def _lecture_xp(saga: Saga, teacher: Character, result: SupplementWork) -> None:
    """Every second lecture commentary of a teacher's earns him an Academic
    Reputation xp (A&A p. 103)."""
    made = 1 + sum(
        1
        for b in saga.books
        if b.opus == book_kinds.LECTURE_COMMENTARY and b.author_id == teacher.id
    )
    if made % 2 == 0:
        result.academic_xp.append((teacher.id, 1))
        result.notes.append(
            f"{teacher.name}'s lecture commentaries come to {made}: 1 xp toward "
            "his Good Academic Reputation (A&A p. 103)."
        )


def _own_commentary(saga: Saga, character: Character, plan: SeasonPlan) -> Book | None:
    book = next((b for b in saga.books if b.id == plan.book_id), None)
    if book is None or book.opus != book_kinds.LECTURE_COMMENTARY:
        return None
    return book if book.author_id == character.id else None


def _edit_lectures(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    book = _own_commentary(saga, character, plan)
    if book is None:
        return
    gain = EDIT_QUALITY + book_seasons.quality_bonus(character)
    result.book_quality.append((book.id, gain))
    result.notes.append(
        f"{book.name} edited: Quality {book.quality or 0} + {gain} = "
        f"{(book.quality or 0) + gain} (A&A p. 102)."
    )


def _edit_lectures_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    book = _own_commentary(saga, character, plan)
    if book is None:
        return ["Choose a lecture commentary of his own lectures to edit."]
    if book.glossed:
        return [f"{book.name} has been edited (or glossed) already."]
    return []


def _status_categories() -> dict[str, tuple[str, str]]:
    return {
        vf_id: (entry.category, entry.tier)
        for vf_id, entry in catalog.load_virtue_flaw_catalog_by_id().items()
    }


def post_ability(character: Character, post: str) -> str:
    """The Ability a post's roll uses: the best of those that suit it."""
    _label, _ease, abilities, _needs = scholarship.POSTS[post]
    return max(abilities, key=lambda a: ability_level(character, a))


def post_bonus(character: Character) -> int:
    return scholarship.status_bonus(character, _status_categories())


def _seek_post(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    post = plan.title.strip()
    if post not in scholarship.POSTS:
        return
    label, ease, _abilities, _needs = scholarship.POSTS[post]
    ability = post_ability(character, post)
    base = scholarship.post_total(character, ability, post_bonus(character))
    result.notes.append(
        f"Seeking {label.lower()}: Presence + {ability} + Academic Reputations + "
        f"Virtues = {base}, + a stress die against {ease} (A&A p. 89)."
    )
    if rng is None:
        result.notes.append("The roll is made when the season is played.")
        return
    die = dice.stress_die(rng, 1, saga=saga)
    if die.botched:
        result.notes.append(
            "A botch: the season is wasted, and the rejection costs a Medium "
            "Wound or a Bad Reputation (the troupe's choice)."
        )
        return
    total = base + die.value
    if total < ease:
        result.notes.append(f"{total} against {ease}: no post; the season is wasted.")
        return
    result.notes.append(f"{total} against {ease}: {label.lower()}'s post is his.")
    result.academic_xp.append(("", 1))
    result.notes.append("1 xp toward his Good Academic Reputation (A&A p. 103).")
    if post == "cathedral_teacher":
        count = scholarship.student_dice(character)
        students = sum(dice.simple_die(rng) for _ in range(count))
        result.notes.append(
            f"{students} students come ({count} simple dice); he can teach "
            f"{scholarship.students_taught(character)} (A&A p. 84)."
        )


def _seek_post_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    post = plan.title.strip()
    if post not in scholarship.POSTS:
        return ["Choose the post he seeks."]
    problem = scholarship.post_problem(character, post)
    return [problem] if problem else []


register(
    SimpleActivity(
        EDIT_LECTURES,
        "Edit a lecture commentary",
        "A season rewriting a commentary of his own lectures: its Quality + 1 "
        "and his writing Virtues, once. Exposure 2.",
        ACADEME,
        "931",
        who=COMPANIONS,
        group=groups.WRITING,
    ),
    _edit_lectures,
    _edit_lectures_problems,
)
register(
    SimpleActivity(
        SEEK_POST,
        "Seek a teaching or clerkly post",
        "A season looking: Presence + the post's Ability + Academic "
        "Reputations + Virtues + a stress die against 12, 15 or 18.",
        ACADEME,
        "931",
        who=COMPANIONS,
        no_xp=True,
        group=groups.WORK,
    ),
    _seek_post,
    _seek_post_problems,
)
