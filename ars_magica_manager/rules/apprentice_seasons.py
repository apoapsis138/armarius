"""Apprentices, planned on the magus's sheet.

- Searching for an apprentice: a season, stress die + Perception against 9
  to find a Gifted child (then added to the saga as a character).
- Opening the Arts: a season teaching the apprentice, who gains a score of
  0 in all fifteen Arts, and a Deficiency in every Art where the master's
  score is below 5. A child with Supernatural Abilities needs an Intellego
  Vim Lab Total too (not worked out here).
- Teaching the apprentice each year is the ordinary Teach activity.
- Teaching a Hermetic Virtue: a season, one student; Source Quality =
  Communication + Teaching + 3 + 6, against 15 (Minor) or 21 (Major) + 3
  for each Minor and 9 for each Major Hermetic Virtue the student has.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .. import catalog
from ..arts import FORMS, TECHNIQUES
from ..models import ArtScore, Character, Saga, SeasonPlan, VirtueFlawInstance

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Opening the Arts "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eight:"
    "_Laboratory#Opening_the_Arts)"
)
SEARCH_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Finding Your "
    "Apprentice (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Eight:_Laboratory#Finding_Your_Apprentice)"
)
VIRTUE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 4: Virtues and Flaws, Teaching "
    "Hermetic Virtues (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Four:_Virtues_and_Flaws)"
)

SEARCH = "search_apprentice"
OPEN_ARTS = "open_arts"
TEACH_VIRTUE = "teach_hermetic_virtue"
ACTIVITIES: tuple[str, ...] = (SEARCH, OPEN_ARTS, TEACH_VIRTUE)
SEARCH_EASE = 9
DEFICIENT_AT = 5


@dataclass
class ApprenticeWork:
    """What a season with an apprentice or student does."""

    #: Opening the Arts: the Deficiencies (Art names) the apprentice gets.
    deficiencies: list[str] = field(default_factory=list)
    #: Teaching a Virtue: the Source Quality and the target it must reach.
    quality: int = 0
    target: int = 0
    notes: list[str] = field(default_factory=list)

    @property
    def succeeds(self) -> bool:
        return self.quality >= self.target


def ability(character: Character, name: str) -> int:
    found = next((a for a in character.abilities if a.name == name), None)
    return found.level if found else 0


def gifted(character: Character) -> bool:
    return character.type == "magus" or any(
        vf.vf_id in catalog.GIFT_IDS for vf in character.virtues_flaws
    )


def _hermetic(character: Character) -> tuple[int, int]:
    """(Minor, Major) Hermetic Virtues `character` has."""
    by_id = {e.id: e for e in catalog.load_virtue_flaw_catalog()}
    minor = major = 0
    for vf in character.virtues_flaws:
        entry = by_id.get(vf.vf_id)
        if entry is None or entry.type != "Virtue" or entry.category != "Hermetic":
            continue
        if entry.tier == "Major":
            major += 1
        elif entry.tier == "Minor":
            minor += 1
    return minor, major


def work(
    saga: Saga, magus: Character, plan: SeasonPlan
) -> tuple[list[str], ApprenticeWork | None]:
    if plan.activity == SEARCH:
        return [], ApprenticeWork()
    student = saga.character(plan.subject_id)
    if student is None or student is magus:
        return ["Choose the apprentice or student."], None
    if not gifted(student):
        return [f"{student.name} doesn't have The Gift."], None
    if plan.activity == OPEN_ARTS:
        if any(student.arts.get(a.lower()) is not None for a in (*TECHNIQUES, *FORMS)):
            return [f"{student.name}'s Arts are already open."], None
        deficient = [
            art
            for art in (*TECHNIQUES, *FORMS)
            if (magus.arts.get(art.lower()) or ArtScore()).level < DEFICIENT_AT
        ]
        result = ApprenticeWork(deficiencies=deficient)
        if any(a.category == "Supernatural" for a in student.abilities):
            result.notes.append(
                f"{student.name} has Supernatural Abilities: opening the Arts "
                "also needs an Intellego Vim Lab Total (DE Ch. 8)."
            )
        return [], result
    # Teaching a Hermetic Virtue.
    by_id = {e.id: e for e in catalog.load_virtue_flaw_catalog()}
    virtue = by_id.get(plan.effect_id or "")
    if virtue is None:
        return ["Choose the Hermetic Virtue to teach."], None
    if not any(vf.vf_id == virtue.id for vf in magus.virtues_flaws):
        return [f"{magus.name} doesn't have {virtue.name}."], None
    if any(vf.vf_id == virtue.id for vf in student.virtues_flaws):
        return [f"{student.name} already has {virtue.name}."], None
    if ability(student, "Magic Theory") < 1:
        return [f"{student.name} needs Magic Theory."], None
    minor, major = _hermetic(student)
    target = (21 if virtue.tier == "Major" else 15) + 3 * minor + 9 * major
    quality = magus.characteristics.communication + ability(magus, "Teaching") + 9
    return [], ApprenticeWork(quality=quality, target=target)


def teachable_virtues(magus: Character) -> list[tuple[str, str]]:
    """(name, id) of the magus's Hermetic Virtues."""
    by_id = {e.id: e for e in catalog.load_virtue_flaw_catalog()}
    found = []
    for vf in magus.virtues_flaws:
        entry = by_id.get(vf.vf_id)
        if (
            entry is not None
            and entry.type == "Virtue"
            and entry.category == "Hermetic"
        ):
            found.append((entry.name, entry.id))
    return found


def open_arts(student: Character, work_: ApprenticeWork) -> None:
    """Give the apprentice his Arts at 0, and the Deficiencies."""
    for art in (*TECHNIQUES, *FORMS):
        student.arts.setdefault(art.lower(), ArtScore())
    for art in work_.deficiencies:
        vf_id = "vf_deficient_technique" if art in TECHNIQUES else "vf_deficient_form"
        key = "technique" if art in TECHNIQUES else "form"
        student.virtues_flaws.append(VirtueFlawInstance(vf_id, params={key: art}))
