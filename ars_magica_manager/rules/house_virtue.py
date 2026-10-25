"""The free House Virtue an apprentice gains from his parens (DE p. 272).

In seven Houses (the four True Lineages, Bonisagus, Guernicus, Mercere and
Tremere, and the Societates Flambeau, Jerbiton and Tytalus) the apprentice
takes on the parens's House Virtue over 10 seasons of one-to-one work with
him: being taught Arts, Arcane Abilities or spells, and helping in his
laboratory. Without the 10 seasons there is no House Virtue. The Mystery
Cult Houses (Bjornaer, Criamon, Merinita, Verditius) Initiate it instead,
and an Ex Miscellanea apprentice's package is the troupe's to decide.

The apprentice learns the House Virtue his parens has; where the House
offers a choice (Flambeau's Puissant Perdo or Ignem) and the parens has
both, the parens chooses. Here the parens opening the apprentice's Arts or
teaching him a Hermetic Virtue counts as a one-to-one season too (DE p.
271 makes teaching a Virtue the year's personal instruction).

An apprentice is someone not yet a magus who names a magus of the saga as
parens. Each season of such work counts once (a `Progress` record of kind
"house_virtue" on the apprentice); at the tenth the Virtue is added when
the parens has exactly one of the House's, else the Diary says to choose.
"""

from __future__ import annotations

from collections.abc import Sequence

from .. import catalog
from ..models import (
    Character,
    DiaryEntry,
    Progress,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from . import apprentice_seasons as aps
from .activities import TAUGHT
from .lab_seasons import TAUGHT_SPELLS
from .laboratory_seasons import ASSIST

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Acquiring House "
    "Virtues, p. 272"
)
SEASONS_NEEDED = 10
KIND = "house_virtue"
#: The Houses whose House Virtue comes from 10 seasons with the parens.
COUNTING_HOUSES = (
    "house_bonisagus",
    "house_guernicus",
    "house_mercere",
    "house_tremere",
    "house_flambeau",
    "house_jerbiton",
    "house_tytalus",
)


def parens_of(saga: Saga, apprentice: Character) -> Character | None:
    """The magus the apprentice names as parens, if he is one of the
    saga's and the apprentice isn't yet a magus."""
    name = apprentice.hermetic.parens.strip()
    if apprentice.type == "magus" or not name:
        return None
    return next(
        (c for c in saga.characters if c.type == "magus" and c.name == name), None
    )


def _arcane(subject: str) -> bool:
    kind, _, what = subject.partition(":")
    if kind == "art":
        return True
    if kind != "ability":
        return False
    return any(
        a.name == what and a.category == "Arcane"
        for a in catalog.load_ability_catalog()
    )


def one_to_one(saga: Saga, plan: SeasonPlan) -> Character | None:
    """The apprentice a season of one-to-one work with his parens counts
    for: the apprentice taught Arts, Arcane Abilities or spells by him, or
    helping in his laboratory, or the parens opening his Arts or teaching
    him a Hermetic Virtue (None for any other season)."""
    character = saga.character(plan.character_id)
    if character is None:
        return None
    if plan.activity in (aps.OPEN_ARTS, aps.TEACH_VIRTUE):
        student = saga.character(plan.subject_id)
        if student is not None and parens_of(saga, student) is character:
            return student
        return None
    parens = parens_of(saga, character)
    if parens is None or plan.teacher_id != parens.id:
        return None
    if plan.activity in (TAUGHT_SPELLS, ASSIST):
        return character
    if plan.activity == TAUGHT and any(_arcane(a.subject) for a in plan.allocations):
        return character
    return None


def record(apprentice: Character) -> Progress | None:
    return next((p for p in apprentice.progress if p.kind == KIND), None)


def seasons_with_parens(apprentice: Character) -> int:
    """The seasons of one-to-one work with the parens counted so far."""
    found = record(apprentice)
    return found.points if found is not None else 0


def _parens_virtues(parens: Character, house_id: str) -> list[VirtueFlawInstance]:
    """The House's Virtues the parens has, as his instances."""
    house = catalog.load_house_catalog_by_id().get(house_id)
    if house is None:
        return []
    found: list[VirtueFlawInstance] = []
    for option in house.virtues:
        params = {k: str(v).casefold() for k, v in (option.get("params") or {}).items()}
        for vf in parens.virtues_flaws:
            mine = {k: str(v).casefold() for k, v in vf.params.items()}
            if vf.vf_id == option.get("vf_id") and all(
                mine.get(k) == v for k, v in params.items()
            ):
                found.append(vf)
    return found


def count_seasons(saga: Saga, plans: Sequence[SeasonPlan]) -> list[Character]:
    """Count the applied `plans`' one-to-one seasons toward each
    apprentice's House Virtue, once a season each, and at the tenth add it
    (or write in the Diary that the parens must choose). Returns the
    apprentices whose count reached 10 this season."""
    reached: list[Character] = []
    for plan in plans:
        apprentice = one_to_one(saga, plan)
        parens = parens_of(saga, apprentice) if apprentice is not None else None
        if apprentice is None or parens is None:
            continue
        house_id = parens.hermetic.house or ""
        if house_id not in COUNTING_HOUSES:
            continue
        found = record(apprentice)
        if found is None:
            house = catalog.load_house_catalog_by_id().get(house_id)
            found = Progress(KIND, house.name if house else house_id, SEASONS_NEEDED)
            apprentice.progress.append(found)
        if found.done or (found.last_season, found.last_year) == (
            plan.season,
            plan.year,
        ):
            continue
        found.points += 1
        found.last_season, found.last_year = plan.season, plan.year
        if found.points >= SEASONS_NEEDED:
            found.done = True
            _gain(apprentice, parens, house_id, plan)
            reached.append(apprentice)
    return reached


def _gain(
    apprentice: Character, parens: Character, house_id: str, plan: SeasonPlan
) -> None:
    """The House Virtue at the tenth season: added when it is plain which,
    with a Diary entry either way."""
    options = _parens_virtues(parens, house_id)
    have = [vf for vf in options if vf in apprentice.virtues_flaws]
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    if have:
        text = f"{apprentice.name} already has the House Virtue."
    elif len(options) == 1:
        vf = options[0]
        apprentice.virtues_flaws.append(VirtueFlawInstance(vf.vf_id, dict(vf.params)))
        entry = by_id.get(vf.vf_id)
        text = (
            f"Ten seasons of one-to-one work with {parens.name}: "
            f"{apprentice.name} gains the House Virtue, "
            f"{entry.name if entry else vf.vf_id}."
        )
    else:
        text = (
            f"Ten seasons of one-to-one work with {parens.name}: "
            f"{apprentice.name} gains the free House Virtue {parens.name} has"
            + (" (the parens chooses which)" if options else "")
            + "; add it on the Virtues tab."
        )
    apprentice.diary.append(
        DiaryEntry(
            year=plan.year,
            season=plan.season,
            name="The House Virtue",
            details=f"{text}\nRule: {SOURCE}",
        )
    )
