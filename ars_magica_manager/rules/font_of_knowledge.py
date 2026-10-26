"""Font of Knowledge: an untrained Ability used as if its score were 2
(DE p. 165; Antagonists p. 109, the Dragon Abbot's Virtue, the same rule).

Intelligence + Font of Knowledge + stress die against 6 + 3 x the times
he has drawn on it that day, failures counted too. Succeeding, he may
attempt a task with an Ability he lacks as if he had it at 2. The Virtue
(Minor, Supernatural) gives the Ability at 1 (DE p. 82). The errata have
nothing on it."""

from __future__ import annotations

from ..models import Character
from .scores import ability_level

SOURCE = (
    "Ars Magica Definitive Edition, Font of Knowledge, pp. 82, 165; Antagonists p. 109"
)
ABILITY = "Font of Knowledge"
VIRTUE = "vf_font_of_knowledge"
BASE_EASE = 6
EASE_PER_USE = 3
#: The score an untrained Ability counts as.
AS_IF_SCORE = 2


def holds(character: Character) -> bool:
    return any(a.name == ABILITY for a in character.abilities) or any(
        vf.vf_id == VIRTUE for vf in character.virtues_flaws
    )


def ease(uses_today: int) -> int:
    """6 + 3 x the uses already made today."""
    return BASE_EASE + EASE_PER_USE * max(0, uses_today)


def total(character: Character) -> int:
    """Intelligence + Font of Knowledge, before the stress die."""
    return character.characteristics.intelligence + ability_level(character, ABILITY)


def untrained(character: Character, ability: str) -> bool:
    """Whether he lacks `ability` (a score of 0): only an untrained Ability
    is drawn from the Font."""
    return ability_level(character, ability) <= 0
