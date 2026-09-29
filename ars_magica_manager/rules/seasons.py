"""Seasonal activities (STORY-903): which activities a character may plan for
a season, and what a planned season gives.

A plan is what the user typed (models.SeasonPlan); its outcome is always
worked out here from the saga as it stands, never stored. Advancing the
season works out every plan's outcome first and only then applies them
(ars_magica_manager.seasons), so a season's results never change that same
season's figures.

Who plans a season (DE Ch. 10, Assigning Seasons): a magus has four free
seasons a year; a companion (Mythic or not) works two seasons a year,
earning Exposure in their job, and has two free ones. Grogs aren't planned
season by season: they're updated once a year (Grogs, Ch. 5; STORY-924).

Activities built so far, each an Advancement Total (rules.study):

- Work / Exposure: Source Quality 2 in an Ability or Art used that season,
  or 1 each in two.
- Practice: Source Quality 4 in one Ability (languages among native
  speakers 8, Area Lore 5-7, forced practice of a trade 5: typed), or 5 in
  a spell's Mastery. Arts can't be practised.
- Adventure: Source Quality 5-10, split among the Abilities and Arts used,
  at most 5 to each.
- Other: anything else, logged in the Diary without an automatic result
  until its own story is built.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from ..arts import ART_BY_NAME, ARTS
from ..models import Character, Saga, SeasonPlan, XpAllocation
from . import xp
from .study import StudyResult, season_of_study

ASSIGNING_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Assigning "
    "Seasons (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Ten:_Long-Term_Events#Assigning_Seasons)"
)
EXPOSURE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Exposure "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Exposure)"
)
PRACTICE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Practice "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Practice)"
)
ADVENTURE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Adventure "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Adventure)"
)
DISTRACTION_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Distractions "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Distractions)"
)

#: The rule behind seasons as a whole (every rules module cites one).
SOURCE = ASSIGNING_SOURCE

#: The character types planned season by season (grogs are updated yearly).
PLANNED_TYPES: tuple[str, ...] = ("magus", "companion", "mythic companion")
#: The types that work two seasons a year (Assigning Seasons).
WORKING_TYPES: tuple[str, ...] = ("companion", "mythic companion")
#: Working seasons a companion owes each year.
WORKING_SEASONS_PER_YEAR = 2

OTHER = "other"
EXPOSURE = "exposure"
PRACTICE = "practice"
ADVENTURE = "adventure"

#: Exposure's Source Quality, split 1 + 1 between two subjects.
EXPOSURE_QUALITY = 2
PRACTICE_QUALITY = 4
MASTERY_PRACTICE_QUALITY = 5
ADVENTURE_MIN, ADVENTURE_MAX = 5, 10
#: At most this much of an Adventure's Source Quality goes to one subject.
ADVENTURE_PER_SUBJECT = 5
#: How many subjects a plan can name (Adventure's split).
MAX_SUBJECTS = 3


@dataclass(frozen=True)
class Activity:
    """One seasonal activity: who may plan it, and the rule behind it."""

    key: str
    label: str
    summary: str
    source: str
    who: tuple[str, ...] = PLANNED_TYPES
    #: A companion's working season (Assigning Seasons).
    working: bool = False
    #: Whether it gives experience (Other doesn't, until its story).
    gives_xp: bool = True
    #: Whether time lost to distractions lowers it.
    distractable: bool = False


ACTIVITIES: dict[str, Activity] = {
    a.key: a
    for a in (
        Activity(
            EXPOSURE,
            "Work / Exposure",
            "A season working, or using Abilities or Arts without studying: "
            "2 xp in one, or 1 each in two. A companion's working season.",
            EXPOSURE_SOURCE,
            working=True,
            distractable=True,
        ),
        Activity(
            PRACTICE,
            "Practice",
            "Practising one Ability (Source Quality 4; languages among native "
            "speakers 8, Area Lore 5-7, forced practice of a trade 5), or a "
            "spell's Mastery (5). Arts can't be practised.",
            PRACTICE_SOURCE,
            distractable=True,
        ),
        Activity(
            ADVENTURE,
            "Adventure",
            "Adventure experience: the storyguide's Source Quality (5-10), "
            "split among the Abilities and Arts used, at most 5 to each.",
            ADVENTURE_SOURCE,
        ),
        Activity(
            OTHER,
            "Other",
            "Anything else the season is spent on, logged in the Diary with "
            "your notes. No experience is worked out for it.",
            ASSIGNING_SOURCE,
            gives_xp=False,
        ),
    )
}


def is_planned(character: Character) -> bool:
    """Whether `character` is planned season by season (not a grog)."""
    return character.type in PLANNED_TYPES


def activities_for(character: Character) -> list[Activity]:
    """The activities `character` may plan, in menu order."""
    return [a for a in ACTIVITIES.values() if character.type in a.who]


# -- subjects: what a season's experience goes into ---------------------------


def _split(subject: str) -> tuple[str, str]:
    kind, _, name = subject.partition(":")
    return kind, name


def ability_subject(name: str) -> str:
    return f"ability:{name}"


def art_subject(art: str) -> str:
    return f"art:{ART_BY_NAME.get(art.lower(), art)}"


def mastery_subject(spell_id: str) -> str:
    return f"mastery:{spell_id}"


def subjects(
    character: Character, spell_names: dict[str, str]
) -> list[tuple[str, str]]:
    """(label, subject) for everything `character` could gain experience in:
    their Abilities, then (magi) the Arts, then (magi) the Mastery of each
    known spell. `spell_names` maps spell ids to names."""
    options = [
        (ability.name, ability_subject(ability.name)) for ability in character.abilities
    ]
    if character.type == "magus":
        options += [(art, art_subject(art)) for art in ARTS]
        options += [
            (
                f"Mastery: {spell_names.get(known.spell_id, known.spell_id)}",
                mastery_subject(known.spell_id),
            )
            for known in character.spells_known
        ]
    return options


def subject_label(subject: str, spell_names: dict[str, str]) -> str:
    kind, name = _split(subject)
    if kind == "mastery":
        return f"Mastery: {spell_names.get(name, name)}"
    return name


def has_subject(character: Character, subject: str) -> bool:
    """Whether `character` has `subject` to gain experience in."""
    kind, name = _split(subject)
    if kind == "ability":
        return any(a.name == name for a in character.abilities)
    if kind == "art":
        return character.type == "magus" and name.lower() in ART_BY_NAME
    if kind == "mastery":
        return any(k.spell_id == name for k in character.spells_known)
    return False


def subject_xp(character: Character, subject: str) -> int:
    """The total xp `character` has in `subject` (0 if none yet)."""
    kind, name = _split(subject)
    if kind == "ability":
        ability = next((a for a in character.abilities if a.name == name), None)
        return ability.xp if ability else 0
    if kind == "art":
        score = character.arts.get(name.lower())
        return score.xp if score else 0
    if kind == "mastery":
        known = next((k for k in character.spells_known if k.spell_id == name), None)
        return known.mastery_xp if known else 0
    return 0


def subject_factor(subject: str) -> int:
    """xp per score step: Arts 1, Abilities and Mastery 5."""
    return xp.ART_FACTOR if _split(subject)[0] == "art" else xp.ABILITY_FACTOR


# -- checking and working out a plan -----------------------------------------


def source_quality(plan: SeasonPlan) -> int | None:
    """The plan's Source Quality: typed, or the rule's default."""
    if plan.source_quality is not None:
        return plan.source_quality
    if plan.activity == EXPOSURE:
        return EXPOSURE_QUALITY
    if plan.activity == PRACTICE:
        mastery = any(_split(a.subject)[0] == "mastery" for a in plan.allocations)
        return MASTERY_PRACTICE_QUALITY if mastery else PRACTICE_QUALITY
    return None


def allocations(plan: SeasonPlan) -> list[XpAllocation]:
    """The plan's subjects with the Source Quality each gets: Exposure's 2
    points go to one subject, or 1 each to two; Practice's all go to its one
    subject; Adventure's are as typed."""
    chosen = [a for a in plan.allocations if a.subject]
    if plan.activity == EXPOSURE:
        each = EXPOSURE_QUALITY // max(1, len(chosen[:2]))
        return [XpAllocation(a.subject, each) for a in chosen[:2]]
    if plan.activity == PRACTICE:
        quality = source_quality(plan) or 0
        return [XpAllocation(a.subject, quality) for a in chosen[:1]]
    if plan.activity == ADVENTURE:
        return chosen
    return []


def problems(character: Character, plan: SeasonPlan) -> list[str]:
    """Why `plan` can't be carried out as it stands (empty when it can)."""
    activity = ACTIVITIES.get(plan.activity)
    if not is_planned(character):
        return [
            "Grogs aren't planned season by season: they're updated once a "
            "year (Grogs, Chapter 5)."
        ]
    if activity is None:
        return [f"Unknown activity {plan.activity!r}."]
    if character.type not in activity.who:
        return [f"A {character.type} can't do {activity.label}."]
    if not activity.gives_xp:
        return []
    found: list[str] = []
    chosen = [a for a in plan.allocations if a.subject]
    if not chosen:
        found.append("Choose what the experience goes into.")
    for allocation in chosen:
        if not has_subject(character, allocation.subject):
            found.append(
                f"{character.name} doesn't have {_split(allocation.subject)[1]}."
            )
    if len({a.subject for a in chosen}) < len(chosen):
        found.append("The same subject is named twice.")
    if not 0 <= plan.months_lost <= 3:
        found.append("Months lost must be 0 to 3.")
    if plan.activity == EXPOSURE and len(chosen) > 2:
        found.append("Exposure goes into one subject, or is split between two.")
    if plan.activity == PRACTICE:
        if len(chosen) > 1:
            found.append("Practice improves one subject.")
        if any(_split(a.subject)[0] == "art" for a in chosen):
            found.append(
                "Arts can't be practised: study them from vis or books "
                "(DE Ch. 10, Practice)."
            )
        quality = source_quality(plan)
        if quality is not None and quality < 1:
            found.append("Source Quality must be at least 1.")
    if plan.activity == ADVENTURE:
        quality = plan.source_quality
        if quality is None or not ADVENTURE_MIN <= quality <= ADVENTURE_MAX:
            found.append(
                f"An Adventure's Source Quality is {ADVENTURE_MIN} to "
                f"{ADVENTURE_MAX} (the storyguide's choice)."
            )
        elif sum(a.points for a in chosen) != quality:
            found.append(
                f"Split all {quality} points of Source Quality: "
                f"{sum(a.points for a in chosen)} are split."
            )
        if any(not 1 <= a.points <= ADVENTURE_PER_SUBJECT for a in chosen):
            found.append(
                f"Each subject gets 1 to {ADVENTURE_PER_SUBJECT} points of an "
                "Adventure's Source Quality."
            )
    return found


@dataclass
class XpGain:
    """Experience a season gives one subject: the working and the totals
    before and after."""

    subject: str
    result: StudyResult
    before: int  # total xp before the season

    @property
    def after(self) -> int:
        return self.before + self.result.xp


@dataclass
class Outcome:
    """What a planned season gives, worked out from the saga before the
    season: nothing is applied here."""

    character_id: str
    plan: SeasonPlan
    activity: Activity | None
    gains: list[XpGain] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def outcome(character: Character, plan: SeasonPlan) -> Outcome:
    """What `plan` gives `character`, from their current figures."""
    activity = ACTIVITIES.get(plan.activity)
    found = problems(character, plan)
    result = Outcome(character.id, plan, activity, problems=found)
    if found or activity is None or not activity.gives_xp:
        return result
    months = plan.months_lost if activity.distractable else 0
    for allocation in allocations(plan):
        kind, name = _split(allocation.subject)
        study = season_of_study(
            character,
            name,
            allocation.points,
            activity=plan.activity,
            is_art=kind == "art",
            months_lost=months,
        )
        result.gains.append(
            XpGain(allocation.subject, study, subject_xp(character, allocation.subject))
        )
    return result


def outcomes(saga: Saga, plans: Sequence[SeasonPlan]) -> list[Outcome]:
    """Every plan's outcome, all worked out before any is applied (a plan
    for a character no longer in the saga is skipped)."""
    worked: list[Outcome] = []
    for plan in plans:
        character = saga.character(plan.character_id)
        if character is not None:
            worked.append(outcome(character, plan))
    return worked
