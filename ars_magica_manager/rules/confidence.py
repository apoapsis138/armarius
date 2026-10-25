"""Confidence Points at the end of a session (DE p. 29) and Reputations
grown by deeds (DE p. 386).

- A character played for a significant length of the session, who
  contributed to it, earns a Confidence Point for each of: a personal goal
  achieved, a contribution to a group goal, success in a difficult task
  (once a session), entertaining roleplaying, and a bonus the storyguide
  thinks deserved (once a session). Two or three a session is typical.
  The Confidence Score rises only after long-term events (a Tytalus
  apprenticeship's fifteen years raise it by one).
- A noteworthy deed before witnesses who will talk starts a Reputation at
  1; each later one that draws attention to the character, and doesn't
  contradict the Reputation, is an experience point in it, as for an
  Ability: ten deeds take a Reputation from 1 to 2.
- A bad Reputation is replaced only by starting a new one with a deed
  spectacular enough to start a Reputation (DE pp. 386-387). Deeds that
  support the new one count toward it; other noteworthy deeds still count
  toward the old one until the new one's score passes the old one's, and
  then toward the new one. From then on, whenever the new one has the
  experience to rise, the character may lower the old one by a point
  instead. An old Reputation lowered to 0 is gone.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character, ScoredTrait

SOURCE = "Ars Magica Definitive Edition, Getting New Confidence Points, p. 29"
REPUTATION_SOURCE = "Ars Magica Definitive Edition, Changing Reputations, pp. 386-387"

#: The five awards, each one Confidence Point.
AWARDS: dict[str, str] = {
    "personal_goal": "Achieved a personal goal",
    "group_goal": "Contributed to a group goal",
    "difficult_task": "Succeeded in a difficult task",
    "roleplaying": "Entertainingly well roleplayed",
    "bonus": "A bonus the storyguide thinks deserved",
}
#: The xp to raise a score by one, as for an Ability: 5 x the new score.
XP_PER_LEVEL = 5


def points_earned(played: bool, awards: set[str]) -> int:
    """The Confidence Points a session earns: one an award, for a character
    played for a significant time who contributed (none otherwise)."""
    return len(awards & set(AWARDS)) if played else 0


def add_deeds(reputation: ScoredTrait, deeds: int) -> int:
    """Count `deeds` noteworthy deeds toward the Reputation, raising its
    score (its magnitude, for a bad one) as an Ability rises. Returns the
    levels gained."""
    reputation.deeds += max(0, deeds)
    sign = -1 if reputation.score < 0 else 1
    level = abs(reputation.score)
    gained = 0
    while reputation.deeds >= XP_PER_LEVEL * (level + 1):
        reputation.deeds -= XP_PER_LEVEL * (level + 1)
        level += 1
        gained += 1
    reputation.score = sign * level
    return gained


@dataclass(frozen=True)
class Replacing:
    """What a session's deeds did to a new Reputation and the bad one it
    replaces: the levels each gained and the points the old one lost."""

    new_gained: int = 0
    old_gained: int = 0
    old_lowered: int = 0


def _ahead(new: ScoredTrait, old: ScoredTrait) -> bool:
    return abs(new.score) > abs(old.score)


def _to_new(new: ScoredTrait, old: ScoredTrait, lower_old: bool) -> tuple[int, int]:
    """One deed toward the new Reputation: (its levels gained, the old
    one's points lost). Once the new one is ahead, the experience that
    would raise it may lower the old one instead."""
    cost = XP_PER_LEVEL * (abs(new.score) + 1)
    if lower_old and old.score != 0 and _ahead(new, old) and new.deeds + 1 >= cost:
        new.deeds = new.deeds + 1 - cost
        old.score += 1 if old.score < 0 else -1
        return 0, 1
    return add_deeds(new, 1), 0


def count_replacing(
    new: ScoredTrait,
    old: ScoredTrait,
    supporting: int,
    general: int,
    *,
    lower_old: bool = False,
) -> Replacing:
    """Count a session's deeds while `new` replaces the bad Reputation
    `old`: `supporting` deeds go to the new one, `general` ones to the old
    one until the new one passes it (one deed at a time, so a rise partway
    through counts). With `lower_old`, a rise of the new one once it is
    ahead lowers the old one instead."""
    new_gained = old_gained = old_lowered = 0
    for _ in range(max(0, supporting)):
        gained, lowered = _to_new(new, old, lower_old)
        new_gained, old_lowered = new_gained + gained, old_lowered + lowered
    for _ in range(max(0, general)):
        if _ahead(new, old) or old.score == 0:
            gained, lowered = _to_new(new, old, lower_old)
            new_gained, old_lowered = new_gained + gained, old_lowered + lowered
        else:
            old_gained += add_deeds(old, 1)
    return Replacing(new_gained, old_gained, old_lowered)


def replaced(reputations: list[ScoredTrait], new: ScoredTrait) -> ScoredTrait | None:
    """The Reputation `new` is replacing, if it is still listed."""
    if not new.replaces:
        return None
    return next(
        (r for r in reputations if r is not new and r.name == new.replaces), None
    )


def drop_spent(reputations: list[ScoredTrait]) -> list[str]:
    """Remove the replaced Reputations lowered to 0, and clear what the new
    ones replace; the names removed."""
    gone = {
        old.name
        for new in reputations
        if (old := replaced(reputations, new)) is not None and old.score == 0
    }
    for new in reputations:
        if new.replaces in gone:
            new.replaces = ""
    reputations[:] = [r for r in reputations if r.name not in gone or r.score != 0]
    return sorted(gone)


def award(character: Character, points: int) -> None:
    character.background.confidence_points += max(0, points)
