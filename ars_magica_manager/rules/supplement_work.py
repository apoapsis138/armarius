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

from dataclasses import dataclass, field

from .. import catalog
from ..models import Book, Character, Progress, Saga, SeasonPlan
from . import dice
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
    add_vfs: list[str] = field(default_factory=list)
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
    by_id = {e.id: e for e in catalog.load_virtue_flaw_catalog()}
    virtue = by_id.get(plan.effect_id or "")
    tier = virtue.tier if virtue is not None else "Minor"
    mystagogue = saga.character(plan.teacher_id) or character
    has_it = any(vf.vf_id == plan.effect_id for vf in mystagogue.virtues_flaws)
    target = INITIATION_TARGET[(tier if tier == "Major" else "Minor", has_it)]
    if character.ordeal and character.initiations_since_ordeal < 3:
        target -= ORDEAL_REDUCTION[character.ordeal][character.initiations_since_ordeal]
    return max(9, target)


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
        if not plan.effect_id:
            return ["Choose the Mystery Virtue initiated."]
        if saga.character(plan.teacher_id) is None:
            return ["Choose the Mystagogue (the Initiate for self-initiation)."]
        if not plan.title.strip():
            return ["Name the Mystagogue's (Mystery Cult) Lore."]
    if key in ("pilgrimage", "tame_animal", "create_art", "research_formula") and (
        not plan.title.strip()
    ):
        return ["Name it (the pilgrimage, the animal, the work, the formula)."]
    if key == "tame_animal" and plan.book_level is None:
        return ["Type the animal's Might."]
    if key == "record_lectures" and saga.character(plan.teacher_id) is None:
        return ["Choose the teacher whose lectures are recorded."]
    if key == "inspeximus":
        book = next((b for b in saga.books if b.id == plan.book_id), None)
        if book is None or book.type not in ("Art Summa", "Ability Summa"):
            return ["Choose the summa to annotate."]
        if book.author != character.name:
            return ["An inspeximus annotates the author's own summa."]
    if key == "bind_catalog" and character.raw_vis.get("vim", 0) < 1:
        return [f"Binding the catalog takes 1 pawn of Vim; {character.name} has none."]
    return []


def work(saga: Saga, character: Character, plan: SeasonPlan, rng) -> SupplementWork:
    """What the season does (rolls made with `rng`)."""
    key = plan.activity
    result = SupplementWork()
    wm = multiplier(character)
    name = plan.title.strip()
    craft = _subject_ability(plan)
    if key in ("working_season", "tournament", "apothecary"):
        default = {
            "working_season": "communication"
            if craft.startswith("Profession")
            else "dexterity",
            "tournament": "dexterity",
            "apothecary": "intelligence",
        }[key]
        lp = (
            _characteristic(character, plan, default) + ability(character, craft)
        ) * wm
        result.labor_points = lp
        result.notes.append(
            f"Labor Points: ({(plan.characteristic or default).title()} + {craft}) x "
            f"{wm} ({wealth(character)}) = {lp}."
        )
    elif key == "workshop_production":
        total = workshop_total(character, plan, craft)
        level = plan.book_level if plan.book_level is not None else 6
        if plan.experimenting and rng is None:
            result.notes.append(
                "Exertion: its dice are rolled when the season is played."
            )
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
        quality = quality_for(total, level)
        lp = (
            _characteristic(character, plan, "dexterity") + ability(character, craft)
        ) * wm
        result.labor_points = lp
        result.notes.append(
            f"Workshop Total {total} against Craft Level {level}: {quality} goods. "
            f"Labor Points {lp}."
        )
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
    elif key == "make_excellent_item":
        level = plan.book_level if plan.book_level is not None else 15
        total = workshop_total(character, plan, craft)
        gained = max(0, total - level)
        result.progress.append(("item", name or "an excellent item", level, gained))
        result.notes.append(
            f"Workshop Total {total} - Craft Level {level} = {gained} toward it."
        )
    elif key == "merchant_venture":
        lp = plan.other_modifier
        result.labor_points = lp
        result.notes.append(f"Labor Points from the venture: {lp}.")
    elif key == "improve_workshop":
        step = name.lower()
        if step == "innovation":
            cost = INNOVATION_COST[character.workshop_innovation + 1]
            result.innovation = 1
        else:
            cost = RAW_MATERIALS_COST[character.workshop_raw_materials + 1]
            result.raw_materials = 1
        result.labor_points = -cost
        result.notes.append(f"{step.title()} +1, for {cost} Labor Points.")
    elif key == "produce_remedies":
        level = plan.book_level or 0
        doses = max(1, plan.extra_vis)
        cost = round_up(level * doses / REMEDY_LEVELS_PER_POINT)
        result.labor_points = -cost
        result.notes.append(
            f"{doses} dose(s) of a level {level} product: {cost} apothecary Labor "
            "Points."
        )
    elif key == "medical_season":
        result.notes.append(
            f"Can care for {ability(character, 'Chirurgy')} patients (palliative) "
            f"and treat {ability(character, 'Medicine')} (therapy) alongside, or "
            "five times as many as the season's whole work."
        )
    elif key == "create_art":
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
    elif key == "research_formula":
        xp = plan.source_quality if plan.source_quality is not None else FORMULA_XP
        result.progress.append(("formula", name, FORMULA_XP, xp))
        result.notes.append(
            f"{xp} xp toward the formula {name} ({FORMULA_XP} make it)."
        )
    elif key == "attend_university":
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
    elif key == "pilgrimage":
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
    elif key == "care_of_souls":
        theme = name or "the sermons' theme"
        result.notes.append(
            f"For the following year, willing congregants get +1 to activities "
            f"fitting {theme}."
        )
    elif key == "tame_animal":
        might = plan.book_level or 0
        gift = (
            3
            if any(vf.vf_id in catalog.GIFT_IDS for vf in character.virtues_flaws)
            else 0
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
    elif key == "search_lacuna" and plan.die is None and rng is None:
        result.notes.append("The search is rolled when the season is played.")
    elif key == "search_lacuna":
        die = (
            plan.die
            if plan.die is not None
            else dice.stress_die(rng, 1, saga=saga).value
        )
        lore = max(
            (a.level for a in character.abilities if a.name.startswith("Area Lore")),
            default=0,
        )
        total = character.characteristics.intelligence + lore + die
        result.notes.append(
            f"Int + Area Lore + die = {total} against 9: "
            + ("the obvious lacunae are found." if total >= 9 else "none found.")
        )
    elif key == "undergo_initiation":
        mystagogue = saga.character(plan.teacher_id) or character
        total = (
            mystagogue.characteristics.presence
            + ability(mystagogue, name)
            + plan.other_modifier
        )
        target = initiation_target(saga, character, plan)
        if total >= target:
            result.add_vfs.append(plan.effect_id or "")
            if plan.device_id:
                result.add_vfs.append(plan.device_id)
                result.ordeal = plan.research_kind or "Minor"
        result.notes.append(
            f"Initiation Total {total} (Presence + {name} + Script {plan.other_modifier}) "
            f"against {target}: "
            + ("initiated." if total >= target else "not initiated.")
        )
    elif key == "record_lectures":
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
                author=teacher.name,
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
    elif key == "inspeximus":
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
    elif key == "bind_catalog":
        result.notes.append(
            "The library catalog bound: an Arcane Connection to the library and "
            "each book in it, for 1 pawn of Vim."
        )
    return result
