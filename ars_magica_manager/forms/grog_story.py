"""More's Story Experience on a grog's This Season: the experience a story
gives a grog, applied at once and noted in the Diary, and counted against
the year's update (Grogs p. 67): each award takes a season of it, in the
order exposure, vocational, practice, exposure.

The award is an Adventure's: a Source Quality of 5 to 10, split among the
Abilities the story used, at most 5 to any one (DE p. 376).
"""

from __future__ import annotations

from typing import Any

from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Character, DiaryEntry, GrogYear, Saga
from ..rules import activities
from ..seasons.character_effects import _add_xp

TITLE = "Story Experience"
HELP_ID = "grog-story-xp"
SOURCE = (
    "Grogs p. 67 (story experience for grogs); Ars Magica Definitive "
    "Edition, Adventure, p. 376"
)
#: How many Abilities one award may be split among on the form.
MOST_SUBJECTS = 3


def fields(character: Character) -> list[DialogField]:
    names = sorted({a.name for a in character.abilities})
    options = [(escape(n), n) for n in names]
    found = [
        DialogField(
            "story",
            "The story",
            "text",
            "",
            placeholder="e.g. The wolves of the high pasture",
        ),
    ]
    for i in range(MOST_SUBJECTS):
        found += [
            DialogField(
                f"ability_{i}",
                "Ability" if i == 0 else f"Ability {i + 1}",
                "select",
                None,
                options=options,
                allow_blank=True,
                placeholder="(none)",
                hint="The Abilities the story used: the award is split among "
                "them, at most 5 to one (DE p. 376)."
                if i == 0
                else "",
            ),
            DialogField(
                f"xp_{i}",
                "Experience" if i == 0 else f"Experience {i + 1}",
                "int",
                5 if i == 0 else 0,
            ),
        ]
    return found


def gains(values: dict[str, Any]) -> list[tuple[str, int]]:
    """(Ability, xp) the award gives, as the form names them."""
    found: list[tuple[str, int]] = []
    for i in range(MOST_SUBJECTS):
        name = values.get(f"ability_{i}") or ""
        xp = int(values.get(f"xp_{i}") or 0)
        if name and xp > 0:
            found.append((name, xp))
    return found


def problem(values: dict[str, Any]) -> str | None:
    given = gains(values)
    if not given:
        return "Choose an Ability and the experience it gains."
    if any(xp > activities.ADVENTURE_PER_SUBJECT for _, xp in given):
        return (
            f"At most {activities.ADVENTURE_PER_SUBJECT} experience goes to one "
            "Ability from a story (DE p. 376)."
        )
    total = sum(xp for _, xp in given)
    if total > activities.ADVENTURE_MAX:
        return (
            f"A story gives {activities.ADVENTURE_MIN} to "
            f"{activities.ADVENTURE_MAX} experience in all (DE p. 376); this "
            f"is {total}."
        )
    return None


def apply(saga: Saga, character: Character, values: dict[str, Any]) -> list[str]:
    given = gains(values)
    for name, xp in given:
        _add_xp(character, activities.ability_subject(name), xp)
    if character.grog_year is None:
        character.grog_year = GrogYear()
    character.grog_year.story_awards += 1
    awards = character.grog_year.story_awards
    summary = ", ".join(f"{escape(n)} +{xp}" for n, xp in given)
    lines = [
        f"{escape(character.name)} gains {summary}.",
        f"{awards} story award{'s' if awards > 1 else ''} this year: the Winter "
        "update loses a season for each (Grogs p. 67).",
    ]
    story = str(values.get("story") or "").strip() or "a story"
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            f"Story experience: {story}",
            "\n".join([*lines, f"Rules: {SOURCE}"]),
            activity="Adventure",
        )
    )
    return notes(*lines)


def story_form(saga: Saga, character: Character | None) -> Command:
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    if activities.is_planned(character):
        return Refuse(
            TITLE,
            f"{escape(character.name)} plans seasons: plan an Adventure on This "
            "Season instead.",
        )
    return Form(
        f"{TITLE}: {escape(character.name)}",
        lambda: fields(character),
        lambda values: apply(saga, character, values),
        validate=problem,
        help_id=HELP_ID,
    )
