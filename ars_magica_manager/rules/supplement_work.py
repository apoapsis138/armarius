"""What the supplement activities do beyond experience: all of them are modelled.

- Labor Points (City & Guild): a working season gives (Characteristic +
  Craft or Profession) x the Wealth Multiplier (Poor 2, average 3, Wealthy
  6); a business costs 36 a year (+5 per point of Raw Materials).
- Workshops (City & Guild): Workshop Total = Characteristic + Craft +
  Innovation + Raw Materials (+ assistants, a manual, a specialty: the
  plan's Other); the quality it reaches (Standard 6, Superior 12, Excellent
  15). Exertion adds a simple die, rolls the exertion table and an Aging
  roll. A craft manual (Artes Liberales 1, 1 Labor Point) scores Craft / 3.
- Excellent and wondrous items, pilgrimages, taming, works of art and
  formulas are progress records on the character, carried season to season.
- Initiation (The Mysteries): the Mystagogue's Presence + Lore + the
  Script's bonus against 15 / 18 (Minor) or 21 / 30 (Major), less a past
  Ordeal's reduction.
- Universities (Art & Academe): an exam at a season's end, against 6 or 12.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .. import book_kinds, book_value, catalog
from ..models import (
    Book,
    Character,
    Progress,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from . import dice, work_virtues
from .rounding import round_down, round_up

SOURCE = (
    "City & Guild, Chapter Two: Labor and Livelihood "
    "(https://www.redcap.org/page/City_%26_Guild_Chapter_Two:_Labor_and_Livelihood)"
)
WEALTH_MULTIPLIER = {"poor": 2, "average": 3, "wealthy": 6}
BUSINESS_UPKEEP = 36
RAW_MATERIALS_UPKEEP = 5
#: Workshop improvement costs in Labor Points, by the score it reaches.
INNOVATION_COST = {1: 100, 2: 200, 3: 300}
RAW_MATERIALS_COST = {1: 50, 2: 100, 3: 150}
#: Quality reached by a Workshop Total (at the basic Craft Level 6).
QUALITIES: tuple[tuple[int, str], ...] = (
    (15, "Excellent"),
    (12, "Superior"),
    (6, "Standard"),
    (0, "Shoddy"),
)
EXERTION = (
    (3, "no special result"),
    (5, "disappointing ramifications (harder materials, a glut, an enemy)"),
    (7, "no benefit: the simple die isn't added"),
    (8, "a story event"),
    (9, "invention: a simple die of Labor Points toward Innovation"),
    (11, "increased Reputation: a simple die of xp in the Craft Reputation"),
)
_ACADEME = "https://www.redcap.org/page/Art_%26_Academe_Open_Content#{}"
MANUAL_SOURCE = (
    "City & Guild, Chapter Four: Crafts, Craftsman Manuals "
    "(https://www.redcap.org/page/City_and_Guild_Chapter_Four:_Crafts"
    "#Craftsman_Manuals)"
)
#: A craft manual's score: the author's Craft / MANUAL_DIVISOR, rounded up.
MANUAL_DIVISOR = 3
REMEDIES_SOURCE = "Art & Academe, Chapter Five: Experimental Philosophy (" + (
    _ACADEME.format("Chapter_Five:_Experimental_Philosophy") + ")"
)
#: Theriacs and reagents cost level x doses / REMEDY_LEVELS_PER_POINT
#: apothecary Labor Points, rounded up.
REMEDY_LEVELS_PER_POINT = 5
ARTWORK_SOURCE = "Art & Academe, Chapter Eight: Artists, Time Spent Creating (" + (
    _ACADEME.format("Time_Spent_Creating") + ")"
)
#: Seasons to make a work of art: Aesthetic Quality / ARTWORK_QUALITY_PER_SEASON,
#: rounded up (at least one).
ARTWORK_QUALITY_PER_SEASON = 10
#: Free Expression's bonus to create a work of art (Ars Magica Definitive
#: Edition, Chapter Four: Virtues and Flaws); Inspirational's here is
#: (source to confirm).
ARTWORK_VIRTUE_BONUS = 3
FORMULA_SOURCE = (
    "Art & Academe, Chapter Five: Experimental Philosophy, Researching "
    "Formulae (" + _ACADEME.format("Researching_Formulae") + ")"
)
#: Experience that makes one formula, and a season of research's default.
FORMULA_XP = 5
LECTURES_SOURCE = (
    "Art & Academe, Chapter Seven: Universities, Lecture Commentaries ("
    + (_ACADEME.format("Lecture_Commentaries") + ")")
)
#: A recorded lecture's Quality: the teacher's Communication + the scribe's
#: Profession: Scribe / LECTURES_SCRIBE_DIVISOR (no rounding stated: down).
LECTURES_SCRIBE_DIVISOR = 2
#: Initiation Target Levels: (Virtue tier, the Mystagogue has it).
INITIATION_TARGET = {
    ("Minor", True): 15,
    ("Minor", False): 18,
    ("Major", True): 21,
    ("Major", False): 30,
}
#: A past Ordeal's reduction to the next three Initiations, by size.
ORDEAL_REDUCTION = {
    "Minor": (3, 3, 1),
    "Medium": (6, 4, 2),
    "Major": (9, 6, 3),
}
EXAMS = {"baccalaureus": 6, "magister": 12, "doctor": 12}
PILGRIMAGE_SEASON = 3


@dataclass
class SupplementWork:
    """What a supplement season does besides experience."""

    notes: list[str] = field(default_factory=list)
    labor_points: int = 0
    #: Progress made: (kind, name, target, points); a record is made if new.
    progress: list[tuple[str, str, int, int]] = field(default_factory=list)
    books: list[Book] = field(default_factory=list)
    add_vfs: list[VirtueFlawInstance] = field(default_factory=list)
    #: Virtues or Flaws an Ordeal takes away.
    remove_vfs: list[VirtueFlawInstance] = field(default_factory=list)
    formulas: list[str] = field(default_factory=list)
    innovation: int = 0
    raw_materials: int = 0
    #: An Aging roll this season (workshop exertion, overtime on art).
    aging_roll: bool = False
    #: The Ordeal an Initiation inflicted ("Minor"/"Medium"/"Major").
    ordeal: str = ""
    #: A summa's new Level (inspeximus): (book id, level).
    summa_level: tuple[str, int] | None = None


def ability(character: Character, name: str) -> int:
    found = next((a for a in character.abilities if a.name == name), None)
    return found.level if found else 0


def wealth(character: Character) -> str:
    ids = {vf.vf_id for vf in character.virtues_flaws}
    if "vf_wealthy" in ids:
        return "wealthy"
    if "vf_poor" in ids:
        return "poor"
    return "average"


def multiplier(character: Character) -> int:
    return WEALTH_MULTIPLIER[wealth(character)]


def _characteristic(character: Character, plan: SeasonPlan, default: str) -> int:
    name = (plan.characteristic or default).lower()
    return getattr(character.characteristics, name, 0)


def _subject_ability(plan: SeasonPlan) -> str:
    subject = next((a.subject for a in plan.allocations if a.subject), "")
    kind, _, name = subject.partition(":")
    return name if kind == "ability" else ""


def progress_of(character: Character, kind: str, name: str) -> Progress | None:
    return next(
        (p for p in character.progress if p.kind == kind and p.name == name), None
    )


def workshop_total(character: Character, plan: SeasonPlan, craft: str) -> int:
    return (
        _characteristic(character, plan, "dexterity")
        + ability(character, craft)
        + character.workshop_innovation
        + character.workshop_raw_materials
        + plan.other_modifier
    )


def quality_for(total: int, craft_level: int) -> str:
    """The best quality the Workshop Total reaches, the thresholds moved
    with the Craft Level (basic 6)."""
    shift = craft_level - 6
    return next(label for top, label in QUALITIES if total >= top + shift)


def initiation_target(saga: Saga, character: Character, plan: SeasonPlan) -> int:
    virtue = catalog.load_virtue_flaw_catalog_by_id().get(plan.effect_id or "")
    tier = virtue.tier if virtue is not None else "Minor"
    mystagogue = saga.character(plan.teacher_id) or character
    has_it = _initiated(plan) in mystagogue.virtues_flaws
    target = INITIATION_TARGET[(tier if tier == "Major" else "Minor", has_it)]
    return max(9, target - ordeal_reduction(character))


def ordeal_reduction(character: Character) -> int:
    """How much the character's past Ordeals lower their next Initiation's
    Target: only the one that lowers it most counts."""
    return max(
        (
            ORDEAL_REDUCTION[o.size][o.initiations_since]
            for o in character.ordeals
            if o.size in ORDEAL_REDUCTION and o.initiations_since < 3
        ),
        default=0,
    )


def _initiated(plan: SeasonPlan) -> VirtueFlawInstance:
    """The Virtue an Initiation grants, with what it names."""
    return VirtueFlawInstance(plan.effect_id or "", dict(plan.effect_params))


#: The kinds of Ordeal: the Initiate gains a Flaw, loses a Virtue, or has a
#: Minor Flaw raised to a related Major one.
GAIN_FLAW, LOSE_VIRTUE, RAISE_FLAW = "gain", "lose", "raise"
ORDEAL_KINDS = {
    GAIN_FLAW: "Gains a Flaw",
    LOSE_VIRTUE: "Loses a Virtue",
    RAISE_FLAW: "Raises a Minor Flaw to Major",
}


def ordeal_kind(plan: SeasonPlan) -> str:
    """The plan's kind of Ordeal ("" for none); an older plan's Flaw is
    gained."""
    return plan.ordeal_kind or (GAIN_FLAW if plan.device_id else "")


def _ordeal_gained(plan: SeasonPlan) -> VirtueFlawInstance | None:
    if ordeal_kind(plan) not in (GAIN_FLAW, RAISE_FLAW) or not plan.device_id:
        return None
    return VirtueFlawInstance(plan.device_id, dict(plan.ordeal_params))


def _ordeal_lost(plan: SeasonPlan) -> VirtueFlawInstance | None:
    if ordeal_kind(plan) not in (LOSE_VIRTUE, RAISE_FLAW) or not plan.ordeal_lost_id:
        return None
    return VirtueFlawInstance(plan.ordeal_lost_id, dict(plan.ordeal_lost_params))


def ordeal_size(plan: SeasonPlan) -> str:
    """The Ordeal's size, from what it costs: a Minor Flaw gained or Minor
    Virtue lost is Minor, a Major one Major, a Flaw raised Medium ("" with
    no Ordeal)."""
    kind = ordeal_kind(plan)
    if kind == RAISE_FLAW:
        return "Medium"
    if not plan.ordeal_kind and plan.device_id:
        return plan.research_kind or "Minor"
    costs = _ordeal_gained(plan) or _ordeal_lost(plan)
    entry = catalog.load_virtue_flaw_catalog_by_id().get(costs.vf_id) if costs else None
    return entry.tier if entry is not None and entry.tier in ORDEAL_REDUCTION else ""


def _house_lore(character: Character, lore: str) -> bool:
    """Whether `lore` is the Lore of the House `character` belongs to
    ("House Bjornaer Lore" for house_bjornaer)."""
    house = (character.hermetic.house or "").removeprefix("house_")
    return bool(house) and house.replace("_", " ") in lore.lower()


def _initiation_problem(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    """What stops an Initiation plan ("" if nothing). No Mystagogue chosen
    is a self-initiation. The Initiate needs the Lore at 1 unless it is the
    Lore of their own House; the Mystagogue must know it."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    virtue = by_id.get(plan.effect_id or "")
    if virtue is None:
        return "Choose the Mystery Virtue initiated."
    if virtue.side != "Virtue":
        return f"{virtue.name} is not a Virtue: choose the Virtue initiated."
    lore = plan.title.strip()
    if not lore:
        return "Name the Mystagogue's (Mystery Cult) Lore."
    mystagogue = saga.character(plan.teacher_id) or character
    if ability(mystagogue, lore) < 1:
        return f"{mystagogue.name} doesn't know {lore}."
    if ability(character, lore) < 1 and not _house_lore(character, lore):
        return f"{character.name} needs {lore} 1 to be Initiated."
    return _ordeal_problem(character, plan)


def _ordeal_problem(character: Character, plan: SeasonPlan) -> str:
    """What is wrong with an Initiation's Ordeal ("" if nothing)."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    kind = ordeal_kind(plan)
    if not kind:
        return ""
    gained, lost = _ordeal_gained(plan), _ordeal_lost(plan)
    flaw = by_id.get(gained.vf_id) if gained else None
    if kind in (GAIN_FLAW, RAISE_FLAW):
        if flaw is None:
            return "Choose the Flaw the Ordeal gives."
        if flaw.side != "Flaw":
            return f"{flaw.name} is not a Flaw: choose the Flaw the Ordeal gives."
    if kind == GAIN_FLAW:
        assert flaw is not None
        if flaw.tier not in ORDEAL_REDUCTION:
            return f"{flaw.name} is a {flaw.tier} Flaw: an Ordeal's is Minor or Major."
        return ""
    entry = by_id.get(lost.vf_id) if lost else None
    if lost is None or entry is None or lost not in character.virtues_flaws:
        return (
            "Choose the Virtue the Ordeal takes away."
            if kind == LOSE_VIRTUE
            else "Choose the Minor Flaw the Ordeal raises."
        )
    if kind == LOSE_VIRTUE:
        if entry.side != "Virtue" or entry.tier not in ORDEAL_REDUCTION:
            return f"{entry.name} can't be lost to an Ordeal: choose a Minor or Major Virtue."
        return ""
    assert flaw is not None
    if entry.side != "Flaw" or entry.tier != "Minor":
        return f"{entry.name} is not a Minor Flaw: choose the Minor Flaw raised."
    if flaw.tier != "Major":
        return f"{flaw.name} is not a Major Flaw: choose the Major Flaw it becomes."
    return ""


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
    if made >= ability(teacher, name):
        return [
            f"{teacher.name} has {made} lecture commentaries on {name}: the most "
            f"a score of {ability(teacher, name)} allows."
        ]
    return []


def problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    """What stops a supplement season with a mechanical side."""
    key = plan.activity
    if key in ("working_season", "tournament", "apothecary") and not _subject_ability(
        plan
    ):
        return ["Choose the Ability the season works with."]
    if key == "workshop_production" and not _subject_ability(plan):
        return ["Choose the Craft."]
    if key == "improve_workshop":
        step = plan.title.strip().lower()
        if step not in ("innovation", "raw materials"):
            return ["Choose Innovation or Raw Materials to improve."]
        score = (
            character.workshop_innovation
            if step == "innovation"
            else character.workshop_raw_materials
        )
        costs = INNOVATION_COST if step == "innovation" else RAW_MATERIALS_COST
        if score >= 3:
            return [f"{step.title()} is already at its most (3)."]
        if character.labor_points < costs[score + 1]:
            return [
                f"Raising {step.title()} to {score + 1} costs {costs[score + 1]} "
                f"Labor Points; {character.name} has {character.labor_points}."
            ]
    if key == "undergo_initiation":
        found = _initiation_problem(saga, character, plan)
        if found:
            return [found]
    if key in ("pilgrimage", "tame_animal", "create_art", "research_formula") and (
        not plan.title.strip()
    ):
        return ["Name it (the pilgrimage, the animal, the work, the formula)."]
    if key == "tame_animal" and plan.book_level is None:
        return ["Type the animal's Might."]
    if key == "record_lectures":
        teacher = saga.character(plan.teacher_id)
        if teacher is None:
            return ["Choose the teacher whose lectures are recorded."]
        return _lecture_problems(saga, teacher, plan)
    if key == "inspeximus":
        book = next((b for b in saga.books if b.id == plan.book_id), None)
        if book is None or book.type not in ("Art Summa", "Ability Summa"):
            return ["Choose the summa to annotate."]
        if book.author != character.name:
            return ["An inspeximus annotates the author's own summa."]
    if key == "read_commentary":
        return [
            "Plan Read a book instead: it now adds a commentary's, a "
            "florilegium's or a gloss's Quality bonus itself."
        ]
    if key == "bind_catalog" and character.raw_vis.get("vim", 0) < 1:
        return [f"Binding the catalog takes 1 pawn of Vim; {character.name} has none."]
    return []


def _working_season(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    wm = multiplier(character)
    craft = _subject_ability(plan)
    default = {
        "working_season": "communication"
        if craft.startswith("Profession")
        else "dexterity",
        "tournament": "dexterity",
        "apothecary": "intelligence",
    }[plan.activity]
    penalty = work_virtues.aura_penalty(saga, character, craft)
    lp = (
        _characteristic(character, plan, default) + ability(character, craft) + penalty
    ) * wm
    result.labor_points = lp
    away = f" {penalty:+d} (Necessary Realm Aura)" if penalty else ""
    result.notes.append(
        f"Labor Points: ({(plan.characteristic or default).title()} + {craft}{away}) x "
        f"{wm} ({wealth(character)}) = {lp}."
    )


def _workshop_production(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    wm = multiplier(character)
    name = plan.title.strip()
    craft = _subject_ability(plan)
    total = workshop_total(character, plan, craft)
    level = plan.book_level if plan.book_level is not None else 6
    if plan.experimenting and rng is None:
        result.notes.append("Exertion: its dice are rolled when the season is played.")
    elif plan.experimenting:
        die = dice.simple_die(rng)
        roll = dice.stress_die(rng, 1, saga=saga)
        outcome = (
            "disaster (the storyguide's ruinous event)"
            if roll.botched
            else next((text for top, text in EXERTION if roll.value <= top), None)
            or "increased understanding: a simple die of xp in the Craft"
        )
        if roll.value in (6, 7) and not roll.botched:
            die = 0
        total += die
        result.aging_roll = True
        result.notes.append(
            f"Exertion: + simple die {die}; the exertion roll {roll.value}: "
            f"{outcome}. An Aging roll this season."
        )
    penalty = work_virtues.aura_penalty(saga, character, craft)
    total += penalty
    quality = quality_for(total, level)
    lp = (
        _characteristic(character, plan, "dexterity")
        + ability(character, craft)
        + penalty
    ) * wm
    result.labor_points = lp
    result.notes.append(
        f"Workshop Total {total} against Craft Level {level}: {quality} goods. "
        f"Labor Points {lp}."
    )
    if penalty:
        result.notes.append(
            f"Necessary Realm Aura for {craft}: {penalty} to the total and the "
            "Labor Points outside its aura."
        )
    if note := work_virtues.independent_note(character, craft):
        result.notes.append(note)
    if plan.quick:
        if ability(character, "Artes Liberales") < 1:
            result.notes.append("No craft manual: it needs Artes Liberales 1.")
        else:
            score = round_up(ability(character, craft) / MANUAL_DIVISOR)
            result.labor_points -= 1
            result.books.append(
                Book(
                    id=f"manual_{character.id}_{plan.year}_{plan.season.lower()}",
                    name=name or f"{craft} manual",
                    type="Other",
                    author=character.name,
                    owner_kind="character",
                    owner_id=character.id,
                    year_published=plan.year,
                    description=f"A craft manual on {craft}: +{score} to a "
                    "literate reader's Workshop Total (City & Guild).",
                )
            )
            result.notes.append(
                f"A craft manual written (+{score}), for 1 Labor Point."
            )


def _make_excellent_item(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    name = plan.title.strip()
    craft = _subject_ability(plan)
    level = plan.book_level if plan.book_level is not None else 15
    total = workshop_total(character, plan, craft)
    gained = max(0, total - level)
    result.progress.append(("item", name or "an excellent item", level, gained))
    result.notes.append(
        f"Workshop Total {total} - Craft Level {level} = {gained} toward it."
    )


def _merchant_venture(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    lp = plan.other_modifier
    result.labor_points = lp
    result.notes.append(f"Labor Points from the venture: {lp}.")


def _improve_workshop(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    name = plan.title.strip()
    step = name.lower()
    if step == "innovation":
        cost = INNOVATION_COST[character.workshop_innovation + 1]
        result.innovation = 1
    else:
        cost = RAW_MATERIALS_COST[character.workshop_raw_materials + 1]
        result.raw_materials = 1
    result.labor_points = -cost
    result.notes.append(f"{step.title()} +1, for {cost} Labor Points.")


def _produce_remedies(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    level = plan.book_level or 0
    doses = max(1, plan.extra_vis)
    cost = round_up(level * doses / REMEDY_LEVELS_PER_POINT)
    result.labor_points = -cost
    result.notes.append(
        f"{doses} dose(s) of a level {level} product: {cost} apothecary Labor Points."
    )


def _medical_season(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    result.notes.append(
        f"Can care for {ability(character, 'Chirurgy')} patients (palliative) "
        f"and treat {ability(character, 'Medicine')} (therapy) alongside, or "
        "five times as many as the season's whole work."
    )


def _create_art(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    name = plan.title.strip()
    craft = _subject_ability(plan)
    if craft.startswith(("Profession", "Craft: Poetry")):
        base = character.characteristics.communication
    else:
        base = character.characteristics.dexterity
    ids = {vf.vf_id for vf in character.virtues_flaws}
    aq = base + ability(character, craft) + plan.other_modifier
    if ids & {"vf_inspirational", "vf_free_expression"}:
        aq += ARTWORK_VIRTUE_BONUS
    seasons = max(1, round_up(aq / ARTWORK_QUALITY_PER_SEASON))
    result.progress.append(("artwork", name, seasons, 1))
    result.notes.append(f"Aesthetic Quality {aq}; {seasons} season(s) to make it.")


def _research_formula(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    name = plan.title.strip()
    xp = plan.source_quality if plan.source_quality is not None else FORMULA_XP
    result.progress.append(("formula", name, FORMULA_XP, xp))
    result.notes.append(f"{xp} xp toward the formula {name} ({FORMULA_XP} make it).")


def _attend_university(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    name = plan.title.strip()
    craft = _subject_ability(plan)
    result.progress.append(("university", "University", 0, 1))
    exam = name.lower()
    if exam in EXAMS and rng is None:
        result.notes.append(f"The {exam} exam is rolled when the season is played.")
    elif exam in EXAMS:
        reps = sum(
            t.score for t in character.reputations if "academic" in t.name.lower()
        )
        subject = "Artes Liberales" if exam != "doctor" else craft or "Theology"
        die = dice.stress_die(rng, 1, saga=saga)
        total = (
            character.characteristics.communication
            + ability(character, subject)
            + reps
            + die.value
        )
        passed = not die.botched and total >= EXAMS[exam]
        result.notes.append(
            f"The {exam} exam: {total} against {EXAMS[exam]}: "
            + ("passed." if passed else "failed (another year first).")
        )


def _pilgrimage(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    name = plan.title.strip()
    target = plan.book_level if plan.book_level in (18, 30) else 18
    gained = PILGRIMAGE_SEASON + max(0, plan.other_modifier)
    result.progress.append(("pilgrimage", name, target, gained))
    result.notes.append(
        f"+{PILGRIMAGE_SEASON} for the season"
        + (
            f", +{plan.other_modifier} for elements overcome"
            if plan.other_modifier
            else ""
        )
        + f" toward Target Level {target}."
    )


def _care_of_souls(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    name = plan.title.strip()
    theme = name or "the sermons' theme"
    result.notes.append(
        f"For the following year, willing congregants get +1 to activities "
        f"fitting {theme}."
    )


def _tame_animal(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    name = plan.title.strip()
    might = plan.book_level or 0
    gift = (
        3 if any(vf.vf_id in catalog.GIFT_IDS for vf in character.virtues_flaws) else 0
    )
    points = max(
        0,
        character.characteristics.intelligence
        + ability(character, "Animal Handling")
        + ability(character, "Animal Ken")
        - might
        - gift,
    )
    result.progress.append(("taming", name, max(1, might), points))
    result.notes.append(
        f"Int + Animal Handling + Animal Ken - Might {might}"
        + (" - the Gift 3" if gift else "")
        + f" = {points} toward taming {name}."
    )


def _search_lacuna(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    if plan.die is None and rng is None:
        result.notes.append("The search is rolled when the season is played.")
        return
    die = plan.die if plan.die is not None else dice.stress_die(rng, 1, saga=saga).value
    lore = max(
        (a.level for a in character.abilities if a.name.startswith("Area Lore")),
        default=0,
    )
    total = character.characteristics.intelligence + lore + die
    result.notes.append(
        f"Int + Area Lore + die = {total} against 9: "
        + ("the obvious lacunae are found." if total >= 9 else "none found.")
    )


def _undergo_initiation(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    name = plan.title.strip()
    mystagogue = saga.character(plan.teacher_id) or character
    total = (
        mystagogue.characteristics.presence
        + ability(mystagogue, name)
        + plan.other_modifier
    )
    target = initiation_target(saga, character, plan)
    size = ordeal_size(plan)
    if total >= target:
        result.add_vfs.append(_initiated(plan))
        if gained := _ordeal_gained(plan):
            result.add_vfs.append(gained)
        if lost := _ordeal_lost(plan):
            result.remove_vfs.append(lost)
        result.ordeal = size
    ordeal = f" {size} Ordeal." if size and total >= target else ""
    result.notes.append(
        f"Initiation Total {total} (Presence + {name} + Script {plan.other_modifier}) "
        f"against {target}: "
        + ("initiated." if total >= target else "not initiated.")
        + ordeal
    )


def _record_lectures(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    name = plan.title.strip()
    teacher = saga.character(plan.teacher_id)
    assert teacher is not None
    quality = teacher.characteristics.communication + round_down(
        ability(character, "Profession: Scribe") / LECTURES_SCRIBE_DIVISOR
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


def _inspeximus(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    book = next(b for b in saga.books if b.id == plan.book_id)
    art = (book.art or "").lower()
    now = (
        character.arts[art].level
        if art in character.arts
        else ability(character, book.ability)
    )
    then = plan.book_level if plan.book_level is not None else (book.level or 0) * 2
    new = min(
        (book.level or 0) + round_down(max(0, now - then) / 3), round_down(now / 2)
    )
    result.summa_level = (book.id, new)
    result.notes.append(f"{book.name} annotated: Level {book.level} -> {new}.")


def _bind_catalog(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    result.notes.append(
        "The library catalog bound: an Arcane Connection to the library and "
        "each book in it, for 1 pawn of Vim."
    )


#: What each supplement activity does, by its key (Strategy, as a table).
def _library_research(
    saga: Saga, character: Character, plan: SeasonPlan, rng, result: SupplementWork
) -> None:
    """The research roll's total before the die: Intelligence + the Ability
    + the better of the covenant library's bonus for it and its best
    encyclopedia's (Covenants, Use: Research; Art & Academe,
    Encyclopedias)."""
    name = _subject_ability(plan)
    if not name:
        return
    covenant = saga.covenant(character.covenant_id)
    found = (
        book_value.encyclopedias(saga, covenant, name) if covenant is not None else []
    )
    library = (
        book_value.library_level(saga, covenant, name) if covenant is not None else 0
    )
    best = max([library, *(e.bonus for e in found)])
    source = ""
    if best:
        source = (
            f"the library +{library}"
            if best == library
            else f"{found[0].name} +{found[0].bonus}"
        )
    total = character.characteristics.intelligence + ability(character, name) + best
    text = f"Research roll: Intelligence + {name}"
    text += f" + {source}" if source else " (no library bonus)"
    result.notes.append(
        f"{text} = {total} + a die, against the storyguide's Ease Factor."
    )


_WORK: dict[str, Callable[[Saga, Character, SeasonPlan, Any, SupplementWork], None]] = {
    "working_season": _working_season,
    "tournament": _working_season,
    "apothecary": _working_season,
    "workshop_production": _workshop_production,
    "make_excellent_item": _make_excellent_item,
    "merchant_venture": _merchant_venture,
    "improve_workshop": _improve_workshop,
    "produce_remedies": _produce_remedies,
    "medical_season": _medical_season,
    "create_art": _create_art,
    "research_formula": _research_formula,
    "attend_university": _attend_university,
    "pilgrimage": _pilgrimage,
    "care_of_souls": _care_of_souls,
    "tame_animal": _tame_animal,
    "search_lacuna": _search_lacuna,
    "undergo_initiation": _undergo_initiation,
    "record_lectures": _record_lectures,
    "inspeximus": _inspeximus,
    "bind_catalog": _bind_catalog,
    "library_research": _library_research,
}


def work(saga: Saga, character: Character, plan: SeasonPlan, rng) -> SupplementWork:
    """What the season does (rolls made with `rng`)."""
    result = SupplementWork()
    handler = _WORK.get(plan.activity)
    if handler is not None:
        handler(saga, character, plan, rng, result)
    return result
