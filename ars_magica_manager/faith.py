"""True Faith (DE Chapter Twelve: Realms, "True Faith").

Like Confidence, True Faith has a Score and Points. The True Faith Major
Virtue gives a Score of 1 and one Faith Point, and only a character with the
Virtue may have a Score. Anyone may hold Faith Points (sacraments,
pilgrimage, other holy endeavours); spent ones don't come back, but each
dawn a character regains Faith Points up to their Score. A Score of 2 or
more makes the character a Mythic Companion (RoP:D). The Score's Magic
Resistance (Score x 10) is worked out by the rules (rules.penetration)."""

from __future__ import annotations

from .models import Character

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
    troupe may know better."""
    warnings = []
    if score and not has_true_faith(character):
        warnings.append("Only a character with the True Faith Virtue has a Score.")
    if score >= 2 and character_type != "mythic companion":
        warnings.append("A True Faith Score of 2 or more is for a Mythic Companion.")
    return warnings
