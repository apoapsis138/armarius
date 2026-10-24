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
  Ability: ten deeds take a Reputation from 1 to 2. A bad Reputation is
  replaced only by starting a new one.
"""

from __future__ import annotations

from ..models import Character, ScoredTrait

SOURCE = "Ars Magica Definitive Edition, Getting New Confidence Points, p. 29"
REPUTATION_SOURCE = "Ars Magica Definitive Edition, Changing Reputations, p. 386"

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


def award(character: Character, points: int) -> None:
    character.background.confidence_points += max(0, points)
