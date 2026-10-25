"""True Faith (DE Chapter Twelve: Realms, "True Faith").

Like Confidence, True Faith has a Score and Points. The True Faith Major
Virtue gives a Score of 1 and one Faith Point, and only a character with the
Virtue may have a Score. Anyone may hold Faith Points (sacraments,
pilgrimage, other holy endeavours); spent ones don't come back, but each
dawn a character regains Faith Points up to their Score. A character
made with a Score of 2 or more is a Mythic Companion (RoP: The Divine
p. 57); one who wins a higher Score in play (p. 58) stays what they are.
The Score's Magic
Resistance (Score x 10) is worked out by the rules (rules.penetration)."""

from __future__ import annotations

from .models import Character, DiaryEntry, Saga, VirtueFlawInstance

#: The True Faith Virtue's catalog id.
TRUE_FAITH_ID = "vf_true_faith"


def has_true_faith(character: Character) -> bool:
    return any(vf.vf_id == TRUE_FAITH_ID for vf in character.virtues_flaws)


def shows_faith(character: Character) -> bool:
    """Whether the sheet shows True Faith: the character has the Virtue, or
    a Score or Faith Points anyway."""
    b = character.background
    return has_true_faith(character) or bool(b.true_faith_score or b.faith_points)


def faith_warnings(character: Character, score: int, character_type: str) -> list[str]:
    """What's wrong with a True Faith Score of `score` for `character` (of
    `character_type`, which the form may be changing): warnings only, the
    troupe may know better. The Mythic Companion warning is for a character
    still In Creation: a Score raised in play is no warning."""
    warnings = []
    if score and not has_true_faith(character):
        warnings.append(
            "Only a character with the True Faith Virtue has a Score."
            if character.in_creation or score <= character.background.true_faith_score
            else "Won in play: saving adds the True Faith Virtue (RoP: The "
            "Divine p. 58)."
        )
    if score >= 2 and character.in_creation and character_type != "mythic companion":
        warnings.append("A True Faith Score of 2 or more is for a Mythic Companion.")
    return warnings


#: Where faith won in play is described.
GAIN_SOURCE = "Realms of Power: The Divine pp. 57-58"


def gain_in_play(saga: Saga, character: Character, score: int, points: int) -> str:
    """Faith won in play (a quest, a pilgrimage, the climax of a story:
    RoP: The Divine p. 58): the character's True Faith Score becomes
    `score` and their Faith Points `points`. A Score won this way brings
    the True Faith Virtue with it, since only the Virtue gives a Score
    (p. 57). Written in the Diary; the line, or "" when nothing rose."""
    b = character.background
    gained = []
    if score > b.true_faith_score:
        gained.append(f"True Faith Score {b.true_faith_score} to {score}")
    if points > b.faith_points:
        gained.append(f"{points - b.faith_points} Faith Point(s)")
    if not gained:
        return ""
    if score > 0 and not has_true_faith(character):
        character.virtues_flaws.append(VirtueFlawInstance(vf_id=TRUE_FAITH_ID))
        gained.append("the True Faith Virtue")
    line = "Faith won in play: " + ", ".join(gained) + "."
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            "Faith won in play",
            f"{line}\nRules: {GAIN_SOURCE}",
        )
    )
    return line
