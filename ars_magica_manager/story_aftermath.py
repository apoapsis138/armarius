"""A chapter's aftermath: closing a chapter of a story asks once for its
whole cast what the story gave them (DE pp. 376-377, Adventure; p. 265,
distractions; Grogs p. 67, story experience for grogs).

First the Adventure's Source Quality (5 to 10, set by the storyguide) and,
for each of the cast, whether they take it: a magus who plans seasons
chooses between the Adventure and keeping the season's laboratory work
with the days away filled in; anyone else takes it or not. Then, for each
who takes it, the Arts and Abilities it went to: at most 5 of its Source
Quality to one, and no more than the Source Quality in all.

What it writes:

* a character who plans seasons gets an Adventure plan for the chapter's
  season, through the activity registry like a hand-made one. The Source
  Quality is the season's, however many adventures it held (DE p. 376):
  a second chapter in the same season updates that plan (raising the
  Source Quality, adding subjects up to the limits) and never doubles it;
* a magus keeping his laboratory work has the chapter's days added to his
  plan's days away;
* a grog (who doesn't plan seasons) gets the experience at once, as More's
  Story Experience gives it (Grogs p. 67).

Cancel at any step leaves the chapter open, to close later (Needs You
lists it). Confidence and noteworthy deeds stay with each character's End
of Session.

Pattern: Command: each question is a commands step, so both front-ends
ask the same; the plans go through the activity registry (Strategy) and
are checked as hand-made ones are."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from . import story_chapters
from .commands import Command, Form, notes
from .form_spec import DialogField
from .markup import escape
from .models import (
    CHAPTER,
    Character,
    Covenant,
    CovenantDiaryEntry,
    DiaryEntry,
    GrogYear,
    Saga,
    SeasonPlan,
    XpAllocation,
)
from .rules import activities as rules
from .seasons.character_effects import _add_xp
from .seasons.plans import plan_for, set_plan

TITLE = "Close the Chapter"
HELP_ID = "close-chapter"
SOURCE = (
    "Ars Magica Definitive Edition, Adventure, pp. 376-377; distractions, "
    "p. 265; Grogs p. 67"
)

#: What a magus who plans seasons chooses.
ADVENTURE, LAB = "adventure", "lab"
#: How many subjects each character's form offers.
MOST_SUBJECTS = 4


def cast_of(saga: Saga, chapter: CovenantDiaryEntry) -> list[Character]:
    found = (saga.character(i) for i in chapter.cast)
    return [c for c in found if c is not None]


def _is_magus(character: Character) -> bool:
    return character.type == "magus"


def open_chapters(saga: Saga) -> list[tuple[Covenant, CovenantDiaryEntry]]:
    """The chapters with a cast whose aftermath hasn't been asked."""
    return [
        (covenant, entry)
        for covenant in saga.covenants
        for entry in covenant.diary
        if entry.category == CHAPTER and entry.cast and not entry.closed
    ]


def close_chapter(
    saga: Saga, covenant: Covenant, chapter: CovenantDiaryEntry
) -> Command:
    """The first step: the Source Quality and who takes the Adventure."""
    cast = cast_of(saga, chapter)
    if not cast:
        chapter.closed = True
        return Form(
            TITLE,
            lambda: [DialogField("_none", "", "info", "No one went: nothing to ask.")],
            lambda _values: None,
            save_label="Close",
            help_id=HELP_ID,
        )

    def fields() -> list[DialogField]:
        found = [
            DialogField(
                "quality",
                "Source Quality",
                "int",
                _season_quality(saga, cast, chapter) or rules.ADVENTURE_MIN,
                hint=f"{rules.ADVENTURE_MIN} to {rules.ADVENTURE_MAX}: how much the "
                "story taught (DE p. 376). One for the season, however many "
                "adventures it held.",
            )
        ]
        for character in cast:
            if _is_magus(character) and rules.is_planned(character):
                found += [
                    DialogField(
                        f"take_{character.id}",
                        escape(character.name),
                        "select",
                        ADVENTURE,
                        options=[
                            ("Takes the Adventure", ADVENTURE),
                            ("Keeps his laboratory work", LAB),
                        ],
                    ),
                ]
            else:
                found.append(
                    DialogField(
                        f"take_{character.id}",
                        f"{escape(character.name)} takes the Adventure",
                        "check",
                        True,
                    )
                )
        return found

    def problem(values: dict[str, Any]) -> str | None:
        quality = values.get("quality")
        if not isinstance(quality, int) or not (
            rules.ADVENTURE_MIN <= quality <= rules.ADVENTURE_MAX
        ):
            return (
                f"The Source Quality is {rules.ADVENTURE_MIN} to "
                f"{rules.ADVENTURE_MAX} (DE p. 376)."
            )
        return None

    def apply(values: dict[str, Any]) -> Command | list[str]:
        quality = int(values["quality"])
        takers, keepers = [], []
        for character in cast:
            choice = values.get(f"take_{character.id}")
            if choice in (True, ADVENTURE):
                takers.append(character)
            elif choice == LAB:
                keepers.append(character)
        said = [_keep_lab(saga, c, chapter) for c in keepers]
        return _subjects(saga, chapter, quality, takers, said)

    return Form(
        f"{TITLE}: {escape(chapter.name)}",
        fields,
        apply,
        validate=problem,
        save_label="Next",
        help_id=HELP_ID,
    )


def _season_quality(
    saga: Saga, cast: list[Character], chapter: CovenantDiaryEntry
) -> int | None:
    """The Source Quality an Adventure planned this season already has."""
    for character in cast:
        plan = plan_for(saga, character, chapter.season, chapter.year)
        if plan is not None and plan.activity == rules.ADVENTURE:
            return plan.source_quality
    return None


def _keep_lab(saga: Saga, character: Character, chapter: CovenantDiaryEntry) -> str:
    """A magus keeping his laboratory work: the chapter's days away added
    to his plan for its season (DE p. 265)."""
    plan = plan_for(saga, character, chapter.season, chapter.year)
    days = chapter.days or 0
    if plan is None or not days:
        return f"{character.name} keeps his season's work."
    set_plan(saga, replace(plan, days_away=plan.days_away + days))
    return f"{character.name} keeps his laboratory work, {days} days away."


def _subjects(
    saga: Saga,
    chapter: CovenantDiaryEntry,
    quality: int,
    takers: list[Character],
    said: list[str],
) -> Command | list[str]:
    """Each taker's subjects in turn; then the chapter is closed."""
    if not takers:
        chapter.closed = True
        return notes(*said, f"{chapter.name}: the chapter is closed.")
    character, rest = takers[0], takers[1:]

    def apply(values: dict[str, Any]) -> Command | list[str]:
        given = gains(values)
        said.append(_award(saga, character, chapter, quality, given))
        return _subjects(saga, chapter, quality, rest, said)

    return Form(
        f"The Adventure: {escape(character.name)}",
        lambda: subject_fields(character, quality),
        apply,
        validate=lambda values: subject_problem(values, quality),
        save_label="Next" if rest else "Close the Chapter",
        help_id=HELP_ID,
    )


def subject_options(character: Character) -> list[tuple[str, str]]:
    arts = [(art.title(), rules.art_subject(art)) for art in sorted(character.arts)]
    abilities = [
        (escape(a.name), rules.ability_subject(a.name))
        for a in sorted(character.abilities, key=lambda a: a.name)
    ]
    return arts + abilities


def subject_fields(character: Character, quality: int) -> list[DialogField]:
    options = subject_options(character)
    found: list[DialogField] = []
    for i in range(MOST_SUBJECTS):
        found += [
            DialogField(
                f"subject_{i}",
                "Subject" if i == 0 else f"Subject {i + 1}",
                "select",
                None,
                options=options,
                allow_blank=True,
                placeholder="(none)",
                hint=f"Source Quality {quality}, split among the Arts and "
                "Abilities the story used: at most 5 to one. An Art counts only "
                "if it was used on stage (DE p. 377)."
                if i == 0
                else "",
            ),
            DialogField(
                f"points_{i}",
                "Points" if i == 0 else f"Points {i + 1}",
                "int",
                min(quality, rules.ADVENTURE_PER_SUBJECT) if i == 0 else 0,
            ),
        ]
    return found


def gains(values: dict[str, Any]) -> list[tuple[str, int]]:
    """(subject, points) as the form names them; the same subject twice
    counts once, its points added."""
    found: dict[str, int] = {}
    for i in range(MOST_SUBJECTS):
        subject = values.get(f"subject_{i}") or ""
        points = int(values.get(f"points_{i}") or 0)
        if subject and points > 0:
            found[subject] = found.get(subject, 0) + points
    return list(found.items())


def subject_problem(values: dict[str, Any], quality: int) -> str | None:
    given = gains(values)
    if not given:
        return "Choose a subject and the points it gets."
    if any(points > rules.ADVENTURE_PER_SUBJECT for _, points in given):
        return (
            f"At most {rules.ADVENTURE_PER_SUBJECT} of the Source Quality goes "
            "to one subject (DE p. 377)."
        )
    total = sum(points for _, points in given)
    if total > quality:
        return f"The points add up to {total}, more than the Source Quality {quality}."
    return None


def _award(
    saga: Saga,
    character: Character,
    chapter: CovenantDiaryEntry,
    quality: int,
    given: list[tuple[str, int]],
) -> str:
    """Write the Adventure: a plan for one who plans seasons (merged with
    the season's Adventure if there is one), the experience at once for a
    grog."""
    if not rules.is_planned(character):
        return _grog_award(saga, character, chapter, given)
    plan = plan_for(saga, character, chapter.season, chapter.year)
    if plan is not None and plan.activity == rules.ADVENTURE:
        kept = {a.subject: a.points for a in plan.allocations}
        for subject, points in given:
            kept[subject] = min(
                rules.ADVENTURE_PER_SUBJECT, max(kept.get(subject, 0), points)
            )
        quality = max(quality, plan.source_quality or 0)
        kept = _within(kept, quality)
        set_plan(
            saga,
            replace(
                plan,
                source_quality=quality,
                allocations=[XpAllocation(s, p) for s, p in kept.items()],
            ),
        )
        return f"{character.name}'s Adventure this season updated (Source Quality {quality})."
    set_plan(
        saga,
        SeasonPlan(
            character.id,
            chapter.year,
            chapter.season,
            rules.ADVENTURE,
            [XpAllocation(s, p) for s, p in given],
            source_quality=quality,
            details=chapter.name,
        ),
    )
    return (
        f"{character.name}: an Adventure planned for {chapter.season} {chapter.year}."
    )


def _within(kept: dict[str, int], quality: int) -> dict[str, int]:
    """The subjects with no more points in all than the Source Quality:
    the later ones cut back first."""
    found: dict[str, int] = {}
    left = quality
    for subject, points in kept.items():
        take = min(points, left)
        if take > 0:
            found[subject] = take
            left -= take
    return found


def _grog_award(
    saga: Saga,
    character: Character,
    chapter: CovenantDiaryEntry,
    given: list[tuple[str, int]],
) -> str:
    """Story experience for a grog, at once, counted against the year's
    update (Grogs p. 67)."""
    for subject, points in given:
        _add_xp(character, subject, points)
    if character.grog_year is None:
        character.grog_year = GrogYear()
    character.grog_year.story_awards += 1
    summary = ", ".join(f"{rules.subject_label(s, {})} +{p}" for s, p in given)
    character.diary.append(
        DiaryEntry(
            chapter.year,
            chapter.season,
            f"Story experience: {chapter.name}",
            f"{summary}.\nRules: {SOURCE}",
            activity="Adventure",
        )
    )
    return f"{character.name} gains {summary}."


# Take Up the Tale and How the Tale Ended go on to the aftermath.
story_chapters.AFTERMATH.append(close_chapter)
