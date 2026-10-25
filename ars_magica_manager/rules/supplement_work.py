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

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .. import book_kinds, book_value, catalog
from ..models import (
    Book,
    Character,
    InitiationScript,
    Progress,
    Saga,
    SeasonPlan,
    TraditionDef,
    VirtueFlawInstance,
    next_season,
)
from . import dice, enchantment, mysteries, realms, reputations, work_virtues
from . import tradition_seasons as ts
from .apprentice_seasons import gifted
from .creation_finish import touched_by_the_fay
from .rounding import round_down, round_up
from .scores import ability_level

SOURCE = "City & Guild, Chapter Two: Labor and Livelihood, pp. 37-40"
WEALTH_MULTIPLIER = {"poor": 2, "average": 3, "wealthy": 6}
#: Craft Levels: an excellent item's at the basic level, and a wondrous
#: item's base before its magnitude and uses (City & Guild pp. 67, 72).
EXCELLENT_LEVEL = 15
WONDROUS_BASE = 12
TOUCHED_BY_REALM = "vf_touched_by_realm"
#: Touched by (Realm) for horseshoes alone (Grogs p. 76): one Form, powers
#: on the horse or the ground it treads, Craft: Farrier with Intelligence
#: or Dexterity.
MYTHIC_FARRIER = "vf_mythic_farrier"
FARRIER_CHARACTERISTICS = ("intelligence", "dexterity")
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
MANUAL_SOURCE = "City & Guild, Chapter Four: Crafts, Craftsman Manuals, p. 73"
#: A craft manual's score: the author's Craft / MANUAL_DIVISOR, rounded up.
MANUAL_DIVISOR = 3
REMEDIES_SOURCE = "Art & Academe, Chapter Five: Experimental Philosophy, pp. 67-78"
#: Theriacs and reagents cost level x doses / REMEDY_LEVELS_PER_POINT
#: apothecary Labor Points, rounded up.
REMEDY_LEVELS_PER_POINT = 5
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
INITIATION_TARGET = mysteries.TARGET_LEVELS
ORDEAL_REDUCTION = mysteries.ORDEAL_REDUCTIONS
EXAMS = {"baccalaureus": 6, "magister": 12, "doctor": 12}
#: Before each exam: the seasons at university in all (3 years; 5 more;
#: 10 in all) and the net Good Academic Reputation (Art & Academe p. 100).
EXAM_SEASONS = {"baccalaureus": 12, "magister": 32, "doctor": 40}
EXAM_REPUTATION = {"baccalaureus": 1, "magister": 2, "doctor": 3}
#: A doctor must already hold the magister (DE p. 76).
MAGISTER = "vf_magister_in_artibus"
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
    #: An Initiation gave its Virtue (only that spends a step of each past
    #: Ordeal's reduction).
    initiated: bool = False
    #: A summa's new Level (inspeximus): (book id, level).
    summa_level: tuple[str, int] | None = None


#: Labor Points to move up a step: Poor to average, average to Wealthy,
#: Wealthy to Poor in the next social class (City & Guild p. 38).
STATION_COST = {"poor": 120, "average": 360, "wealthy": 1080}


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


#: Taming's points last only over consecutive seasons (DE p. 384).
CONSECUTIVE_KINDS = ("taming",)
TAMING_SOURCE = "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Training Creatures, pp. 384-386"
#: The Gift's penalty to taming a mundane beast, a social activity (DE pp.
#: 204, 384): none with the Gentle Gift, 6 with the Blatant Gift.
GIFT_TAMING = {"vf_gentle_gift": 0, "vf_blatant_gift": 6}


def kept_points(record: Progress | None, season: str, year: int) -> int:
    """The points a record still holds for a season's work: all of them,
    unless it is taming and the last season on it wasn't the one before."""
    if record is None or record.done:
        return 0
    if record.kind not in CONSECUTIVE_KINDS or record.last_year is None:
        return record.points
    if next_season(record.last_season, record.last_year) != (season, year):
        return 0
    return record.points


def gift_penalty(character: Character) -> int:
    """What The Gift takes off taming a mundane beast (3; 0 Gentle, 6
    Blatant)."""
    ids = {vf.vf_id for vf in character.virtues_flaws}
    for vf_id, penalty in GIFT_TAMING.items():
        if vf_id in ids:
            return penalty
    return 3 if ids & set(catalog.GIFT_IDS) else 0


MASTER_OF_CREATURES = "vf_master_of_form_creatures"


def master_of_creatures(character: Character) -> str | None:
    """The Form a Master of (Form) Creatures tames, or None."""
    for vf in character.virtues_flaws:
        if vf.vf_id == MASTER_OF_CREATURES:
            return str(vf.params.get("form") or "").title() or "?"
    return None


def more_tamed(points: int, might: int, handling: int) -> int:
    """How many more creatures of the same species a season's points tame
    beside the first, when they are enough for one in a season: shared out,
    at most the tamer's Animal Handling more (DE p. 384)."""
    need = max(1, might)
    if points < need:
        return 0
    return min(handling, points // need - 1)


def beast_might(confidence: int) -> int:
    """A mundane beast's effective Might for taming: 1 + 2 x its
    Confidence Score (DE p. 384)."""
    return 1 + 2 * max(0, confidence)


def workshop_total(character: Character, plan: SeasonPlan, craft: str) -> int:
    return (
        _characteristic(character, plan, "dexterity")
        + ability_level(character, craft)
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
    """The Initiation's Target: the Hermetic Target Level by the Virtue's
    tier and whether the Mystagogue knows it, or a hedge Script's own Ease
    Factor (+ 3 / + 9 when he doesn't know the power), less a past
    Ordeal's reduction."""
    virtue = catalog.load_virtue_flaw_catalog_by_id().get(plan.effect_id or "")
    mystagogue = saga.character(plan.teacher_id) or character
    knows = knows_power(mystagogue, plan)
    hedge = ts.hedge_script(plan.hedge_script)
    if hedge is not None:
        _, script = hedge
        tier = (
            virtue.tier
            if virtue is not None and virtue.tier in mysteries.UNKNOWN_POWER
            else mysteries.script_tier(script.ease_factor, script.gains)
        )
        ease = script.ease_factor
        if mystagogue is character and script.self_ease_factor:
            ease = script.self_ease_factor
        return int(
            mysteries.hedge_target(ease, tier, knows, ordeal_reduction(character)).total
        )
    tier = virtue.tier if virtue is not None else "Minor"
    target = INITIATION_TARGET[(tier if tier == "Major" else "Minor", knows)]
    return max(mysteries.MINIMUM_TARGET, target - ordeal_reduction(character))


def knows_power(mystagogue: Character, plan: SeasonPlan) -> bool:
    """Whether the Mystagogue knows the power initiated: he holds the
    Virtue, with what it names, or the plan says he knows it (a hedge
    power that is an Ability, say)."""
    return plan.knows_power or (
        bool(plan.effect_id) and _initiated(plan) in mystagogue.virtues_flaws
    )


def ordeal_reduction(character: Character) -> int:
    """How much the character's past Ordeals lower their next Initiation's
    Target: only the one that lowers it most counts, and none for an
    unGifted Initiate."""
    if not mysteries.ordeals_count(character):
        return 0
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
    hedge = ts.hedge_script(plan.hedge_script)
    if plan.hedge_script and hedge is None:
        return "That hedge Script is no longer in the catalog: choose another."
    virtue = by_id.get(plan.effect_id or "")
    if virtue is None and hedge is None:
        return "Choose the Mystery Virtue initiated."
    if virtue is not None and virtue.side != "Virtue":
        return f"{virtue.name} is not a Virtue: choose the Virtue initiated."
    mystagogue = saga.character(plan.teacher_id) or character
    if hedge is not None:
        found = _hedge_problem(character, mystagogue, *hedge)
        if found:
            return found
    else:
        lore = plan.title.strip()
        if not lore:
            return "Name the Mystagogue's (Mystery Cult) Lore."
        if ability_level(mystagogue, lore) < 1:
            return f"{mystagogue.name} doesn't know {lore}."
        if ability_level(character, lore) < 1 and not _house_lore(character, lore):
            return f"{character.name} needs {lore} 1 to be Initiated."
    return (
        _script_problem(plan)
        or (_mystery_problem(saga, character, virtue.id) if virtue else "")
        or _ordeal_problem(character, plan)
        or mysteries.ungifted_problem(
            character,
            mystagogue,
            knows_power(mystagogue, plan),
            bool(ordeal_kind(plan)),
        )
    )


def _hedge_problem(
    initiate: Character,
    mystagogue: Character,
    tradition: TraditionDef,
    script: InitiationScript,
) -> str:
    """What stops an Initiation by a hedge tradition's Script ("" if
    nothing): the Mystagogue must belong to the tradition and know its
    Lore, a tradition without self-initiation can't Initiate itself, a
    Script for the Gifted needs a Gifted Initiate, and one that requires
    scores (the elementalists' minimums, HMRE pp. 30-31; the learned
    magicians' master's test, pp. 88-89) fails an Initiate without them."""
    rule = tradition.initiation
    assert rule is not None  # ts.hedge_script finds Scripts only in a rule
    if tradition.id not in mystagogue.traditions:
        return (
            f"{mystagogue.name} isn't one of the {tradition.name}: the "
            "Mystagogue must be."
        )
    if mystagogue is initiate and not rule.self_initiation:
        return f"The {tradition.name} can't Initiate themselves: choose a Mystagogue."
    if rule.lore and ts.lore_score(mystagogue, rule.lore) < 1:
        return f"{mystagogue.name} doesn't know {rule.lore}."
    if script.who == "gifted" and not gifted(initiate):
        return f"{script.name} is for the Gifted, and {initiate.name} is unGifted."
    short = [
        f"{ability} {least}"
        for ability, least in script.requires
        if ts.lore_score(initiate, ability) < least
    ]
    if short:
        return (
            f"{script.name} always fails for an Initiate without "
            f"{', '.join(short)}: {initiate.name} is short of it."
        )
    return ""


def _script_problem(plan: SeasonPlan) -> str:
    """An experimental Script is neither varied nor beyond +3 risk."""
    if not plan.experimental_script:
        return ""
    if plan.script_variation:
        return "An experimental Script isn't also varied: choose one or the other."
    if not 0 <= plan.risk <= mysteries.MAX_SCRIPT_RISK:
        return f"An experimental Script's risk is 0 to +{mysteries.MAX_SCRIPT_RISK}."
    return ""


def _mystery_problem(saga: Saga, character: Character, vf_id: str) -> str:
    """What a Mystery's own rule says stops its Initiation ("" if nothing):
    Secret Name fails for one with a talisman or a familiar (DE p. 235);
    Faerie Magic needs one touched by the fay, by a fay Virtue or Flaw or
    a Warping Point from a faerie (DE p. 236; the app can't tell where
    Warping came from, so any counts)."""
    if vf_id == mysteries.SECRET_NAME:
        if enchantment.talisman_of(saga, character) is not None:
            return (
                f"{character.name} has a talisman: Secret Name's Initiation "
                "fails (DE p. 235)."
            )
        if saga.familiar_of(character.id) is not None:
            return (
                f"{character.name} has a familiar: Secret Name's Initiation "
                "fails (DE p. 235)."
            )
    if vf_id == mysteries.FAERIE_MAGIC and not (
        touched_by_the_fay(character)
        or character.aging.warping_points
        or character.aging.warping_score
    ):
        return (
            f"{character.name} hasn't been touched by the fay (a fay Virtue or "
            "Flaw, or a Warping Point from a faerie): Faerie Magic can't be "
            "Initiated (DE p. 236)."
        )
    return ""


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
    if made >= ability_level(teacher, name):
        return [
            f"{teacher.name} has {made} lecture commentaries on {name}: the most "
            f"a score of {ability_level(teacher, name)} allows."
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
    if key == "attend_university" and plan.title.strip().lower() in EXAMS:
        exam = plan.title.strip().lower()
        studied = 1 + sum(
            r.points for r in character.progress if r.kind == "university"
        )
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
    if key == "improve_station":
        cost = STATION_COST[wealth(character)]
        if character.labor_points < cost:
            return [
                f"Moving up from {wealth(character)} costs {cost} Labor Points "
                f"(City & Guild p. 38); {character.name} has "
                f"{character.labor_points}."
            ]
    held = {vf.vf_id for vf in character.virtues_flaws}
    if key == "make_wondrous_item" and not held & {TOUCHED_BY_REALM, MYTHIC_FARRIER}:
        return [
            f"Only a craftsman Touched by (Realm) makes wondrous items "
            f"(City & Guild p. 70); {character.name} isn't."
        ]
    if (
        key == "make_wondrous_item"
        and TOUCHED_BY_REALM not in held
        and (plan.characteristic or "dexterity") not in FARRIER_CHARACTERISTICS
    ):
        return [
            "A Mythic Farrier's Craft Total is Intelligence or Dexterity + "
            "Craft: Farrier (Grogs p. 76)."
        ]
    if key == "make_wondrous_item" and not touched_realm(character):
        return [
            "Name the realm of his Touched by (Realm) or Mythic Farrier "
            "Virtue: Magic, Faerie, Divine or Infernal (City & Guild p. 71; "
            "a farrier most likely Magic or Faerie, Infernal possible, Grogs "
            "p. 76)."
        ]
    if key == "make_wondrous_item" and plan.teacher_id == character.id:
        return ["The assistant is someone other than the craftsman."]
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
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
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
        _characteristic(character, plan, default)
        + ability_level(character, craft)
        + penalty
    ) * wm
    result.labor_points = lp
    away = f" {penalty:+d} (Necessary Realm Aura)" if penalty else ""
    result.notes.append(
        f"Labor Points: ({(plan.characteristic or default).title()} + {craft}{away}) x "
        f"{wm} ({wealth(character)}) = {lp}."
    )


def _workshop_production(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    wm = multiplier(character)
    name = plan.title.strip()
    craft = _subject_ability(plan)
    total = workshop_total(character, plan, craft)
    level = plan.book_level if plan.book_level is not None else 6
    if plan.experimenting and rng is None:
        result.notes.append("Exertion: its dice are rolled when the season is played.")
    elif plan.experimenting and rng is not None:
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
        + ability_level(character, craft)
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
        if ability_level(character, "Artes Liberales") < 1:
            result.notes.append("No craft manual: it needs Artes Liberales 1.")
        else:
            score = round_up(ability_level(character, craft) / MANUAL_DIVISOR)
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


def excellent_bonus(total: int, level: int, craft: int) -> int | None:
    """An excellent item's bonus: +1 for every 3 points the Workshop Total
    is over its Craft Level, at most the Craft / 3, rounded up (City &
    Guild p. 69); None when the total falls short."""
    if total < level:
        return None
    return min((total - level) // 3, round_up(craft / 3))


def _make_excellent_item(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """An excellent item: made in the one season if the Workshop Total
    reaches its Craft Level (15 at the basic level)."""
    name = plan.title.strip() or "an excellent item"
    craft = _subject_ability(plan)
    level = plan.book_level if plan.book_level is not None else EXCELLENT_LEVEL
    total = workshop_total(character, plan, craft)
    bonus = excellent_bonus(total, level, ability_level(character, craft))
    if bonus is None:
        result.notes.append(
            f"Workshop Total {total} is below the Craft Level {level}: no "
            "excellent item this season."
        )
        return
    result.progress.append(("item", name, 1, 1))
    result.notes.append(
        f"Workshop Total {total} against Craft Level {level}: {name} is made, "
        f"+{bonus} to a feature (City & Guild p. 69)."
    )


def _improve_station(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """A season moving up: Poor to average (120 Labor Points), average to
    Wealthy (360); from Wealthy (1,080) to Poor in the next social class,
    whose Social Status the troupe changes by hand."""
    now = wealth(character)
    cost = STATION_COST[now]
    result.labor_points = -cost
    if now == "poor":
        result.remove_vfs.append(VirtueFlawInstance("vf_poor"))
        result.notes.append(f"Poor to average, for {cost} Labor Points.")
    elif now == "average":
        result.add_vfs.append(VirtueFlawInstance("vf_wealthy"))
        result.notes.append(f"Average to Wealthy, for {cost} Labor Points.")
    else:
        result.remove_vfs.append(VirtueFlawInstance("vf_wealthy"))
        result.add_vfs.append(VirtueFlawInstance("vf_poor"))
        result.notes.append(
            f"Wealthy to Poor in the next social class, for {cost} Labor "
            "Points: change the Social Status Virtue on the Virtues tab."
        )


def _make_wondrous_item(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """A wondrous item: each season the Workshop Total is over its Craft
    Level (12 + the effect's magnitude + its uses a day) adds the difference
    toward it, until the points equal the Craft Level (City & Guild pp.
    71-72)."""
    name = plan.title.strip() or "a wondrous item"
    craft = _subject_ability(plan)
    level = plan.book_level if plan.book_level is not None else WONDROUS_BASE
    total = workshop_total(character, plan, craft)
    parts: list[str] = []
    aura = wondrous_aura(character, plan)
    if aura:
        total += aura
        parts.append(f"aura {aura:+d}")
    if plan.site_aura is None:
        result.notes.append(
            "No aura entered where he works: none counted (City & Guild p. 72)."
        )
    helper = saga.character(plan.teacher_id) if plan.teacher_id else None
    if helper is not None:
        helped = round_down(ability_level(helper, craft) / 2)
        total += helped
        parts.append(f"{helper.name}'s help +{helped}")
    gained = max(0, total - level)
    result.progress.append(("item", name, level, gained))
    why = f" ({', '.join(parts)})" if parts else ""
    result.notes.append(
        f"Workshop Total {total}{why} - Craft Level {level} = {gained} toward it. "
        "One assistant at most (City & Guild p. 72): count no other in Other."
    )
    if not any(vf.vf_id == TOUCHED_BY_REALM for vf in character.virtues_flaws):
        result.notes.append(
            "Mythic Farrier: horseshoes only, in the one Form chosen, their "
            "power on the horse or the ground it treads (Grogs p. 76)."
        )


def touched_realm(character: Character) -> str:
    """The realm a wondrous craftsman's power comes from, as his Touched by
    (Realm) or Mythic Farrier names it: one of the four realms (City &
    Guild p. 71; a farrier most likely Magic or Faerie, Grogs p. 76); ""
    when it names none of them."""
    for vf in character.virtues_flaws:
        if vf.vf_id in (TOUCHED_BY_REALM, MYTHIC_FARRIER):
            named = str(vf.params.get("realm", "")).strip().title()
            named = {"Magical": realms.HERMETIC}.get(named, named)
            return named if named in realms.REALMS else ""
    return ""


def wondrous_aura(character: Character, plan: SeasonPlan) -> int:
    """The aura's modifier to a wondrous item's Workshop Total: the aura the
    craftsman works in (the plan's), by the Realm Interaction table for
    his power's realm (City & Guild p. 72; DE pp. 410-411)."""
    aura, aura_realm = plan.site_aura or 0, plan.site_realm or realms.HERMETIC
    realm = touched_realm(character)
    if aura <= 0 or aura_realm not in realms.REALMS or not realm:
        return 0
    return realms.aura_modifier(realm, aura_realm, aura)


def _merchant_venture(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    lp = plan.other_modifier
    result.labor_points = lp
    result.notes.append(f"Labor Points from the venture: {lp}.")


def _improve_workshop(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
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
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    level = plan.book_level or 0
    doses = max(1, plan.extra_vis)
    cost = round_up(level * doses / REMEDY_LEVELS_PER_POINT)
    result.labor_points = -cost
    result.notes.append(
        f"{doses} dose(s) of a level {level} product: {cost} apothecary Labor Points."
    )


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
    craft = _subject_ability(plan)
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


def _attend_university(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    name = plan.title.strip()
    craft = _subject_ability(plan)
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


def _pilgrimage(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
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
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    name = plan.title.strip()
    theme = name or "the sermons' theme"
    result.notes.append(
        f"For the following year, willing congregants get +1 to activities "
        f"fitting {theme}."
    )


def _tame_animal(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    name = plan.title.strip()
    might = plan.book_level or 0
    gift = gift_penalty(character)
    handling = ability_level(character, "Animal Handling")
    ken = ability_level(character, "Animal Ken")
    master = master_of_creatures(character)
    if master is not None:
        # A Master of (Form) Creatures tames with his Magic Lore in place of
        # Might (DE p. 385).
        base, label = ability_level(character, "Magic Lore"), "Magic Lore"
        creature = next((c for c in saga.creatures if c.name == name), None)
        if creature is not None and creature.might_form not in ("", master):
            result.notes.append(
                f"A Master of {master} Creatures tames only creatures of {master}: "
                f"{name} is of {creature.might_form}."
            )
    else:
        base, label = character.characteristics.intelligence, "Int"
    points = max(0, base + handling + ken - might - gift)
    record = progress_of(character, "taming", name)
    if (
        record is not None
        and record.points
        and not kept_points(record, plan.season, plan.year)
    ):
        result.notes.append(
            f"The {record.points} points toward taming {name} are lost: the "
            "seasons weren't consecutive (DE p. 384)."
        )
    result.progress.append(("taming", name, max(1, might), points))
    result.notes.append(
        f"{label} + Animal Handling + Animal Ken - Might {might}"
        + (f" - the Gift {gift}" if gift else "")
        + f" = {points} toward taming {name}."
    )
    more = more_tamed(points, might, handling)
    if more:
        result.notes.append(
            f"Enough to tame {more} more of the same kind this season, sharing "
            "the points (at most Animal Handling more, DE p. 384)."
        )


def _search_lacuna(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    if plan.die is not None:
        die = plan.die
    elif rng is not None:
        die = dice.stress_die(rng, 1, saga=saga).value
    else:
        result.notes.append("The search is rolled when the season is played.")
        return
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
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    mystagogue = saga.character(plan.teacher_id) or character
    trait, name, lore, script = _initiation_terms(mystagogue, plan)
    target = initiation_target(saga, character, plan)
    size = ordeal_size(plan)
    risk = 0
    rite_failed = False
    if plan.experimental_script:
        if rng is None:
            result.notes.append(
                "An experimental Script's dice are rolled when the season is played."
            )
            return
        rite_failed, risk = _experiment_with_script(
            saga, character, mystagogue, plan, rng, lore, script, result
        )
        script += plan.script_sympathy
    elif plan.script_variation in mysteries.VARY_EASE:
        if rng is None:
            result.notes.append(
                f"Varying the Script ({plan.script_variation}) is rolled when the "
                "season is played."
            )
            return
        varied = _vary_script(saga, mystagogue, plan, rng, lore, script, result)
        if varied is None:
            return
        script = varied
    value = getattr(mystagogue.characteristics, trait.lower(), 0)
    full = value + lore + script + risk
    # Each month lost takes a third of the original total, rounded up; an
    # Initiation it makes fail still costs the Ordeal (TMRE p. 12).
    months = max(0, min(plan.months_lost, 3))
    total = max(0, full - months * round_up(full / 3))
    distracted = months > 0 and full >= target > total and not rite_failed
    initiated = total >= target and not rite_failed
    # An experimental rite is carried out, Ordeals and all, before it is
    # checked, so a failed one still costs its Ordeal (TMRE p. 18).
    suffered = initiated or distracted or rite_failed
    if initiated:
        result.initiated = True
        if plan.effect_id:
            result.add_vfs.append(_initiated(plan))
    if suffered:
        if gained := _ordeal_gained(plan):
            result.add_vfs.append(gained)
        if lost := _ordeal_lost(plan):
            result.remove_vfs.append(lost)
        result.ordeal = size
    ordeal = f" {size} Ordeal." if size and suffered else ""
    lost_text = f", {months} month(s) lost from {full}" if months else ""
    risk_text = f" + risk {risk}" if risk else ""
    hedge = ts.hedge_script(plan.hedge_script)
    gains = (
        f" Add what it gives by hand: {hedge[1].gains}."
        if initiated and hedge is not None and not plan.effect_id and hedge[1].gains
        else ""
    )
    result.notes.append(
        f"Initiation Total {total} ({trait} + {name} + Script {script}{risk_text}"
        f"{lost_text}) against {target}: "
        + (
            "initiated."
            if initiated
            else "not initiated; the rite failed, but its Ordeal is still "
            "suffered (TMRE p. 18)."
            if rite_failed
            else "not initiated; the distractions failed it, so the Ordeal is "
            "still suffered and the Initiation must be repeated (TMRE p. 12)."
            if distracted
            else "not initiated."
        )
        + ordeal
        + gains
    )


def _initiation_terms(
    mystagogue: Character, plan: SeasonPlan
) -> tuple[str, str, int, int]:
    """The Initiation Total's terms: the Characteristic, the Lore's name
    and the Mystagogue's score in it, and the Script's bonus (a hedge
    Script's own, plus what the plan adds)."""
    hedge = ts.hedge_script(plan.hedge_script)
    if hedge is None:
        name = plan.title.strip()
        return "Presence", name, ability_level(mystagogue, name), plan.other_modifier
    tradition, script = hedge
    rule = tradition.initiation
    assert rule is not None  # ts.hedge_script finds Scripts only in a rule
    return (
        rule.characteristic,
        ts.hedge_lore(tradition),
        ts.lore_score(mystagogue, rule.lore),
        script.bonus + plan.other_modifier,
    )


def _vary_script(
    saga: Saga,
    mystagogue: Character,
    plan: SeasonPlan,
    rng: random.Random,
    lore: int,
    script: int,
    result: SupplementWork,
) -> int | None:
    """Roll the one change to the Script: its new bonus, or None when the
    change fails and so the Initiation does (DE p. 389)."""
    ease = mysteries.VARY_EASE[plan.script_variation]
    die = dice.stress_die(rng, 1, saga=saga)
    vary = die.value + mystagogue.characteristics.intelligence + lore
    if die.botched or vary < ease:
        result.notes.append(
            f"Varying the Script: {vary} against {ease}: failed, so the "
            "Initiation fails; the Script as it was may be tried another "
            "season (DE p. 389)."
        )
        return None
    script += plan.variation_bonus
    result.notes.append(
        f"Varying the Script: {vary} against {ease}: the Script bonus is now {script}."
    )
    return script


def _experiment_with_script(
    saga: Saga,
    initiate: Character,
    mystagogue: Character,
    plan: SeasonPlan,
    rng: random.Random,
    lore: int,
    proposed: int,
    result: SupplementWork,
) -> tuple[bool, int]:
    """An experimental Script's two rolls: the Extraordinary Results chart,
    then the rite's validity against 9 (15 on another Initiate) + the
    proposed bonus. Whether the rite failed, and the risk the Initiation
    Total adds (TMRE p. 18)."""
    rite = mysteries.experimental_rite(rng, plan.risk, saga)
    result.notes += rite.notes
    ease = mysteries.validity_ease(proposed, mystagogue is initiate)
    die = dice.simple_die(rng)
    valid = die + plan.risk + mystagogue.characteristics.intelligence + lore
    result.notes.append(
        f"The rite's validity: die {die} + risk {plan.risk} + Intelligence + Lore "
        f"= {valid} against {ease}: "
        + ("valid." if valid >= ease else "invalid, so no Virtue is gained.")
    )
    return rite.no_virtue or valid < ease, plan.risk if rite.risk_counts else 0


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


def _inspeximus(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    book = next(b for b in saga.books if b.id == plan.book_id)
    art = (book.art or "").lower()
    now = (
        character.arts[art].level
        if art in character.arts
        else ability_level(character, book.ability)
    )
    then = plan.book_level if plan.book_level is not None else (book.level or 0) * 2
    new = min(
        (book.level or 0) + round_down(max(0, now - then) / 3), round_down(now / 2)
    )
    result.summa_level = (book.id, new)
    result.notes.append(f"{book.name} annotated: Level {book.level} -> {new}.")


def _bind_catalog(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    result.notes.append(
        "The library catalog bound: an Arcane Connection to the library and "
        "each book in it, for 1 pawn of Vim."
    )


#: What each supplement activity does, by its key (Strategy, as a table).
def _library_research(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
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
    total = (
        character.characteristics.intelligence + ability_level(character, name) + best
    )
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
    "make_wondrous_item": _make_wondrous_item,
    "improve_station": _improve_station,
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


def work(
    saga: Saga, character: Character, plan: SeasonPlan, rng: random.Random | None
) -> SupplementWork:
    """What the season does (rolls made with `rng`)."""
    result = SupplementWork()
    handler = _WORK.get(plan.activity)
    if handler is not None:
        handler(saga, character, plan, rng, result)
    return result
