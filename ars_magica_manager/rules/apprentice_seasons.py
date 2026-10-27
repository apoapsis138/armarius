"""Apprentices, planned on the magus's sheet.

- Searching for an apprentice: a season, stress die + Perception against 9
  to find a Gifted child (then added to the saga as a character).
- Opening the Arts: a season teaching the apprentice, who gains a score of
  0 in all fifteen Arts, and a Deficiency in every Art where the master's
  score is below 5. A child with Supernatural Abilities needs the master's
  Intellego Vim Lab Total (in his laboratory) to reach 5 x each Ability,
  at least 10 for a Minor Virtue's and 30 for a Major's (10 or 30 for a
  power with no Ability), all added together. Reaching it, they are lost;
  only at double it or more may the master keep them
  (`SeasonPlan.keep_supernatural`) or convert each into a Virtue of its
  size he has and can perform (a similar one he lacks at the troupe's
  word), which is done on the Virtues tab (DE p. 271). An inborn Ex Miscellanea tradition Virtue is
  exempt (DE p. 270): the troupe leaves it off. A Gift already Opened by a
  non-Hermetic tradition adds 30 to the total needed (Rival Magic p. 6).
- Teaching the apprentice each year is the ordinary Teach activity.
- Teaching a Hermetic Virtue: a season, one student; Source Quality =
  Communication + Teaching + 3 + 6 and the teaching Virtues (Good Teacher),
  +3 or +9 with a Minor or Major Hermetic Flaw of the teacher's taught with
  it (the student gains it too), against 15 (Minor) or 21 (Major) + 3 for
  each Minor and 9 for each Major Hermetic Virtue the student has (DE p.
  271).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .. import catalog
from ..arts import FORMS, TECHNIQUES
from ..models import (
    ArtScore,
    Character,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from . import lab, lab_stats, study
from .creation_access import traditions_of
from .effects import fill_name
from .scores import ability_level

SUPERNATURAL_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Opening the Arts, "
    "pp. 270-271"
)
SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Opening the Arts, pp. "
    "270-271"
)
SEARCH_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Finding Your Apprentice, p. "
    "269"
)
VIRTUE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Teaching Hermetic Virtues, "
    "p. 271"
)

SEARCH = "search_apprentice"
OPEN_ARTS = "open_arts"
TEACH_VIRTUE = "teach_hermetic_virtue"
ACTIVITIES: tuple[str, ...] = (SEARCH, OPEN_ARTS, TEACH_VIRTUE)
SEARCH_EASE = 9
#: A Hermetic Flaw taught with the Virtue (DE p. 271).
FLAW_BONUS = {"Minor": 3, "Major": 9}
DEFICIENT_AT = 5


@dataclass
class ApprenticeWork:
    """What a season with an apprentice or student does."""

    #: Opening the Arts: the Deficiencies (Art names) the apprentice gets.
    deficiencies: list[str] = field(default_factory=list)
    #: Opening the Arts: the Supernatural Abilities and Virtues (ids) it
    #: takes away.
    lost_abilities: list[str] = field(default_factory=list)
    lost_virtues: list[str] = field(default_factory=list)
    #: Teaching a Virtue: the Source Quality and the target it must reach,
    #: and the Flaw taught with it.
    quality: int = 0
    target: int = 0
    flaw_id: str = ""
    notes: list[str] = field(default_factory=list)

    @property
    def succeeds(self) -> bool:
        return self.quality >= self.target


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
        found = _supernatural(saga, magus, student, plan, result)
        if found:
            return [found], None
        if student.traditions:
            result.notes.append(
                f"If {student.name}'s Gift was Opened to a hedge tradition, the "
                "Intellego Vim Lab Total needs 30 more (Hedge Magic RE, "
                "Introduction)."
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
    if ability_level(student, "Magic Theory") < 1:
        return [f"{student.name} needs Magic Theory."], None
    minor, major = _hermetic(student)
    target = (21 if virtue.tier == "Major" else 15) + 3 * minor + 9 * major
    # Teaching a Virtue is lab work, so the lab's Teaching Specialization
    # counts (DE p. 291).
    quality = study.teaching_quality(magus, 1) + lab_stats.teaching_bonus(
        saga, saga.laboratory(magus.assigned_lab_id)
    )
    work_ = ApprenticeWork(quality=quality, target=target)
    flaw = by_id.get(plan.taught_flaw_id or "")
    if flaw is not None:
        if not any(vf.vf_id == flaw.id for vf in magus.virtues_flaws):
            return [f"{magus.name} doesn't have {flaw.name}."], None
        work_.quality += FLAW_BONUS.get(flaw.tier, 0)
        work_.flaw_id = flaw.id
    return [], work_


#: What a Gift Opened by a non-Hermetic tradition adds to the Intellego
#: Vim Lab Total needed (Rival Magic p. 6).
OPENED_ELSEWHERE = 30


def supernatural_needs(student: Character) -> list[tuple[str, int, str | None]]:
    """What each of the apprentice's Supernatural Abilities and powers
    needs of the Intellego Vim Lab Total: (Ability name or "", level,
    the Virtue's id)."""
    by_id = {e.id: e for e in catalog.load_virtue_flaw_catalog()}
    virtues = {
        e.name: (vf.vf_id, e.tier)
        for vf in student.virtues_flaws
        if (e := by_id.get(vf.vf_id)) is not None
        and e.type == "Virtue"
        and e.category == "Supernatural"
    }
    found: list[tuple[str, int, str | None]] = []
    for ability in student.abilities:
        if ability.category != "Supernatural":
            continue
        vf_id, tier = virtues.pop(ability.name, (None, "Minor"))
        least = 30 if tier == "Major" else 10
        found.append(
            (ability.name, max(5 * ability_level(student, ability.name), least), vf_id)
        )
    for vf_id, tier in virtues.values():
        found.append(("", 30 if tier == "Major" else 10, vf_id))
    return found


def _supernatural(
    saga: Saga,
    magus: Character,
    student: Character,
    plan: SeasonPlan,
    result: ApprenticeWork,
) -> str:
    """The Intellego Vim Lab Total a child's Supernatural Abilities need:
    why the Arts can't be opened, or what is lost (on `result`)."""
    needs = supernatural_needs(student)
    # A Gift already Opened by a non-Hermetic tradition adds 30 to the
    # Lab Total needed (Rival Magic p. 6).
    opened = any(t.opening is not None for t in traditions_of(student))
    if not needs and not opened:
        return ""
    level = sum(n for _, n, _ in needs) + (OPENED_ELSEWHERE if opened else 0)
    laboratory = saga.laboratory(magus.assigned_lab_id)
    if laboratory is None:
        return (
            f"{student.name} has Supernatural Abilities: opening the Arts needs "
            f"{magus.name}'s Intellego Vim Lab Total, so give him a laboratory."
        )
    total = int(lab.lab_total(saga, magus, "Intellego", "Vim", laboratory).total)
    if total < level:
        return (
            f"Opening {student.name}'s Arts needs an Intellego Vim Lab Total of "
            f"{level}"
            + (" (+30 for a Gift already Opened)" if opened else "")
            + f"; {magus.name}'s is {total}."
        )
    keep = plan.keep_supernatural and total >= 2 * level
    if keep:
        result.notes.append(
            f"Intellego Vim Lab Total {total}, at least double {level}: "
            f"{student.name} keeps the Supernatural Abilities."
        )
        return ""
    result.lost_abilities = [name for name, _, _ in needs if name]
    result.lost_virtues = [vf_id for _, _, vf_id in needs if vf_id]
    result.notes.append(
        f"Intellego Vim Lab Total {total} against {level}: "
        f"{student.name}'s Supernatural Abilities are lost"
        + (
            " (at double it they could be kept, or converted on the Virtues tab)."
            if total >= 2 * level
            else "."
        )
    )
    return ""


def teachable_virtues(
    magus: Character, *, flaws: bool = False
) -> list[tuple[str, str]]:
    """(name, id) of the magus's Hermetic Virtues (or his Hermetic Flaws)."""
    by_id = {e.id: e for e in catalog.load_virtue_flaw_catalog()}
    found = []
    for vf in magus.virtues_flaws:
        entry = by_id.get(vf.vf_id)
        if (
            entry is not None
            and entry.type == ("Flaw" if flaws else "Virtue")
            and entry.category == "Hermetic"
        ):
            found.append((fill_name(entry.name, vf.params), entry.id))
    return found


def open_arts(student: Character, work_: ApprenticeWork) -> None:
    """Give the apprentice his Arts at 0, and the Deficiencies."""
    for art in (*TECHNIQUES, *FORMS):
        student.arts.setdefault(art.lower(), ArtScore())
    student.abilities = [
        a for a in student.abilities if a.name not in work_.lost_abilities
    ]
    student.virtues_flaws = [
        vf for vf in student.virtues_flaws if vf.vf_id not in work_.lost_virtues
    ]
    for art in work_.deficiencies:
        vf_id = "vf_deficient_technique" if art in TECHNIQUES else "vf_deficient_form"
        key = "technique" if art in TECHNIQUES else "form"
        student.virtues_flaws.append(VirtueFlawInstance(vf_id, params={key: art}))
