"""Scores from experience points: an Art's or Ability's score is derived from
the total xp spent on it, never stored (STORY-806).

- Art: reaching score n costs n(n+1)/2 xp in total; the step from n-1 to n
  costs n.
- Ability: reaching score n costs 5n(n+1)/2 xp in total; the step costs 5n.

The xp is always the running total: it never resets when a score is
reached (score 1 at 5 xp, score 2 at 15).
"""

from __future__ import annotations

from dataclasses import dataclass

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Advancement Table "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Three:"
    "_Characters#Advancement_Table)"
)

#: xp per score step: an Art's step to score n costs n, an Ability's 5n.
ART_FACTOR = 1
ABILITY_FACTOR = 5


def xp_for_score(score: int, factor: int) -> int:
    """Total xp needed to reach `score` (0 for a score of 0 or less)."""
    score = max(score, 0)
    return factor * score * (score + 1) // 2


def score_from_xp(xp: int, factor: int) -> int:
    """The score `xp` total experience buys (the highest score whose total
    cost is no more than `xp`)."""
    score = 0
    while xp_for_score(score + 1, factor) <= xp:
        score += 1
    return score


def art_xp(score: int) -> int:
    """Total xp for an Art score (score 5 -> 15)."""
    return xp_for_score(score, ART_FACTOR)


def ability_xp(score: int) -> int:
    """Total xp for an Ability score (score 5 -> 75)."""
    return xp_for_score(score, ABILITY_FACTOR)


@dataclass(frozen=True)
class Progress:
    """Where a total xp figure stands: the score it buys, the total xp
    spent (it keeps counting up; it never resets when a score is reached)
    and the total the next score needs."""

    score: int
    total: int
    next_total: int

    @property
    def to_next(self) -> int:
        """xp still needed to reach the next score."""
        return self.next_total - self.total


def progress(xp: int, factor: int) -> Progress:
    total = max(xp, 0)
    score = score_from_xp(total, factor)
    return Progress(
        score=score, total=total, next_total=xp_for_score(score + 1, factor)
    )


def migrate_level_xp(level: int, xp: int, factor: int) -> tuple[int, bool]:
    """Total xp for a pair saved before scores were derived, when a score
    and its xp were typed separately; also whether the pair was ambiguous.

    - xp that buys exactly `level` is already a total: kept.
    - xp below the next step's cost is progress toward it (the sheet's X(Z)
      notation): the total is the level's cost plus that xp.
    - Anything else can't be read either way: the typed score is kept (xp
      set to its cost) and the pair is reported as ambiguous.
    """
    level = max(level, 0)
    if score_from_xp(xp, factor) == level and xp >= 0:
        return xp, False
    if 0 <= xp < factor * (level + 1):
        return xp_for_score(level, factor) + xp, False
    return xp_for_score(level, factor), True
