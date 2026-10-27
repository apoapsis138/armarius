"""The supplement seasons' registry: what one activity is (SimpleActivity),
what its season does beyond experience (SupplementWork), and the table of
registered activities with their outcome and the check that stops a plan.

Pattern: Registry (a dict plus register()), each entry a Strategy. Each
book's season work is a module of this package that registers its own
activities when imported, so adding one never touches another book's.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field

from ...models import (
    Book,
    Character,
    ElixirIngredient,
    Formula,
    Ordination,
    Progress,
    ProjectWork,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from .. import activity_groups as groups

#: A supplement cited by its redcap.org page.
CH = "(https://www.redcap.org/page/{})"

#: Who plans an activity: companions, magi, or anyone planned.
COMPANIONS = ("companion", "mythic companion")
MAGI = ("magus",)
ANYONE = ("magus", "companion", "mythic companion")

#: Each source's book, as sourcebooks.SOURCEBOOKS abbreviates it.
_BOOKS: dict[str, str] = {}


def source(citation: str, book: str) -> str:
    """Record `citation` as a source from `book` (a sourcebooks.SOURCEBOOKS
    abbreviation) and return it, for an activity's `source`."""
    _BOOKS[citation] = book
    return citation


@dataclass(frozen=True)
class SimpleActivity:
    """One supplement activity: its Source Quality (None: typed, as `hint`
    says), who may plan it, and the story it belongs to."""

    key: str
    label: str
    summary: str
    source: str
    story: str
    quality: int | None = 2
    hint: str = ""
    who: tuple[str, ...] = ANYONE
    #: No experience (a season spent, logged in the Diary).
    no_xp: bool = False
    #: Faith Points gained.
    faith: int = 0
    #: No longer offered (another activity does it now); kept so an older
    #: plan still loads and says what to plan instead.
    retired: bool = False
    #: What the season is for (activity_groups), as the picker groups it.
    group: str = ""
    #: The season's experience goes into its work (a formula researched),
    #: not into the subject's score.
    xp_to_work: bool = False

    @property
    def book(self) -> str:
        """The sourcebook (sourcebooks.SOURCEBOOKS abbreviation) the activity
        comes from: offered only while the saga has it in play."""
        return _BOOKS[self.source]


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
    #: That Aging roll is a young craftsman's: a simple die for the stress
    #: die, and a 13 brings no Crisis (City & Guild p. 74).
    aging_young: bool = False
    #: Experience gained in Abilities: (Ability, xp).
    ability_xp: list[tuple[str, int]] = field(default_factory=list)
    #: Experience in a (Craft) or (Profession) Reputation: (trade, xp), a
    #: negative amount lowering it (City & Guild pp. 74, 76).
    reputation_xp: list[tuple[str, int]] = field(default_factory=list)
    #: The Ordeal an Initiation inflicted ("Minor"/"Medium"/"Major").
    ordeal: str = ""
    #: What an Initiation's sacrifice gives up (SeasonPlan.sacrifice).
    sacrifice: str = ""
    #: The Quests an Initiation's rite performed (Character.quests).
    quests: list[str] = field(default_factory=list)
    #: Labor Points taken from another's store: (character id, points).
    labor_from: list[tuple[str, int]] = field(default_factory=list)
    #: Stirpes Invigorated: (name, Form, Might or level) each.
    stirpes: list[tuple[str, str, int]] = field(default_factory=list)
    #: An Initiation gave its Virtue (only that spends a step of each past
    #: Ordeal's reduction).
    initiated: bool = False
    #: A summa's new Level (inspeximus): (book id, level).
    summa_level: tuple[str, int] | None = None
    #: Experimental philosophy: formulae designed (researched), the
    #: formulae whose Laboratory Text a first concoction wrote, and doses
    #: made (gear name, doses).
    formula_designs: list[Formula] = field(default_factory=list)
    lab_texts: list[str] = field(default_factory=list)
    products: list[tuple[str, int]] = field(default_factory=list)
    #: Academic Reputation experience (Art & Academe p. 103): (whose: a
    #: character id, "" for the one planned; xp, negative toward a Bad one).
    academic_xp: list[tuple[str, int]] = field(default_factory=list)
    #: A book's Quality raised (an edited lecture commentary): (book id,
    #: Quality points), the book marked glossed so it is raised once.
    book_quality: list[tuple[str, int]] = field(default_factory=list)
    #: House Verditius's Hubris (rules.verditius): the trait's score when
    #: this Initiation brings it first (0: none made), the experience it
    #: gains, and the points the Increased Hubris Ordeal adds.
    hubris_start: int = 0
    hubris_xp: int = 0
    hubris_rises: int = 0
    #: Raw vis the season spends (Art -> pawns), taken from the pool the
    #: plan's `vis_from` names (vis.season_pool).
    vis_cost: dict[str, int] = field(default_factory=dict)
    #: The Lesser Elixir reinvented with this ingredient (rules.tmre_alchemy).
    elixir_ingredient: ElixirIngredient | None = None
    #: An ordination examination sat this season (rules.clergy), kept on
    #: the character's Church tab when the season is applied.
    ordination: Ordination | None = None
    #: Hermetic Projects: works done on a project this season (a master
    #: mason's), as (project id, work), kept in its works when applied.
    project_works: list[tuple[str, ProjectWork]] = field(default_factory=list)
    #: House Criamon: the station's Virtue an avenue reached (rules.criamon),
    #: its season kept on The Enigma when the season is applied.
    enigma_station: str = ""


#: What a season does beyond experience, written into `result` (rolls made
#: with the Random; None when the season is only previewed).
Outcome = Callable[
    [Saga, Character, SeasonPlan, random.Random | None, SupplementWork], None
]
#: What stops a plan of the activity (an empty list when nothing does).
Check = Callable[[Saga, Character, SeasonPlan], list[str]]


def experience_only(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """The outcome of a season that gives experience (or is only logged)
    and does nothing more."""


def nothing_stops(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    """The check of an activity that any plan of it may carry out."""
    return []


@dataclass(frozen=True)
class SeasonWork:
    """A registered supplement activity, its outcome and its check."""

    activity: SimpleActivity
    outcome: Outcome
    check: Check = nothing_stops


#: Every registered activity by its key, in the order registered.
REGISTRY: dict[str, SeasonWork] = {}


def register(
    activity: SimpleActivity, outcome: Outcome, check: Check = nothing_stops
) -> None:
    """Add `activity`, what its season does and what stops a plan of it.
    An activity is registered once."""
    if activity.key in REGISTRY:
        raise ValueError(f"The season activity {activity.key!r} is registered twice.")
    REGISTRY[activity.key] = SeasonWork(activity, outcome, check)


def activities() -> tuple[SimpleActivity, ...]:
    """Every registered activity, by its group's place in the picker, then
    by label (as the activity picker lists them)."""
    place = {group: index for index, group in enumerate(groups.GROUPS)}
    return tuple(
        sorted(
            (entry.activity for entry in REGISTRY.values()),
            key=lambda a: (place.get(a.group, len(place)), a.label.lower()),
        )
    )


def work(
    saga: Saga, character: Character, plan: SeasonPlan, rng: random.Random | None
) -> SupplementWork:
    """What the season does (rolls made with `rng`)."""
    result = SupplementWork()
    entry = REGISTRY.get(plan.activity)
    if entry is not None:
        entry.outcome(saga, character, plan, rng, result)
    return result


def problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    """What stops a supplement season with a mechanical side."""
    entry = REGISTRY.get(plan.activity)
    return entry.check(saga, character, plan) if entry is not None else []


# -- helpers more than one book's season work uses ----------------------------

WEALTH_MULTIPLIER = {"poor": 2, "average": 3, "wealthy": 6}


def wealth(character: Character) -> str:
    ids = {vf.vf_id for vf in character.virtues_flaws}
    if "vf_wealthy" in ids:
        return "wealthy"
    if "vf_poor" in ids:
        return "poor"
    return "average"


def multiplier(character: Character) -> int:
    return WEALTH_MULTIPLIER[wealth(character)]


def characteristic(character: Character, plan: SeasonPlan, default: str) -> int:
    """The plan's Characteristic's score (`default` when it names none)."""
    name = (plan.characteristic or default).lower()
    return getattr(character.characteristics, name, 0)


def subject_ability(plan: SeasonPlan) -> str:
    """The Ability the plan's experience goes into ("" if an Art or none)."""
    subject = next((a.subject for a in plan.allocations if a.subject), "")
    kind, _, name = subject.partition(":")
    return name if kind == "ability" else ""


def progress_of(character: Character, kind: str, name: str) -> Progress | None:
    return next(
        (p for p in character.progress if p.kind == kind and p.name == name), None
    )


def needs_subject(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    """A season worked with an Ability needs it chosen."""
    if not subject_ability(plan):
        return ["Choose the Ability the season works with."]
    return []


def needs_name(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    """A season toward something named (a pilgrimage, an animal, a work, a
    formula) needs the name."""
    if not plan.title.strip():
        return ["Name it (the pilgrimage, the animal, the work, the formula)."]
    return []
