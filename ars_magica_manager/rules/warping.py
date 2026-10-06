"""Warping and Wizard's Twilight.

- The Warping Score advances like an Ability on Warping Points: n takes
  5 x n(n + 1) / 2 points in all.
- Automatic sources, each Winter: a Longevity Ritual (+1 a year) and living
  in a strong aura of another realm (6: 1, 7: 1, 8: 2, 9: 4, 10: 12 a
  year; a magus gains none from a Magic aura).
- Gaining 2+ points from one event takes a magus to the edge of Twilight:
  Stamina + Concentration + stress die against Warping Score + the points +
  Enigmatic Wisdom + the aura + a stress die (no botch). Failing enters
  Twilight: Intelligence + Enigmatic Wisdom + stress die against Warping
  Score + stress die decides whether it is comprehended; the time it takes
  goes by Warping Score; it adds a simple die of Warping Points more.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..models import Character
from . import dice

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Warping "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Warping)"
)
TWILIGHT_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Wizard's "
    "Twilight (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Ten:_Long-Term_Events#Wizard.27s_Twilight)"
)

#: Warping Points a year from living always within a strong aura.
AURA_POINTS: dict[int, int] = {6: 1, 7: 1, 8: 2, 9: 4, 10: 12}
#: Time in Twilight by Warping Score, and the seasons it takes (0: less
#: than a season).
TWILIGHT_TIME: tuple[tuple[str, int], ...] = (
    ("a Diameter (2 minutes)", 0),
    ("two hours", 0),
    ("a Sun", 0),
    ("a day", 0),
    ("a Moon", 0),
    ("a season", 1),
    ("a year", 4),
    ("seven years", 28),
)


def points_for(score: int) -> int:
    return 5 * score * (score + 1) // 2


def score_for(points: int) -> int:
    score = 0
    while points_for(score + 1) <= points:
        score += 1
    return score


def total_points(character: Character) -> int:
    a = character.aging
    return points_for(a.warping_score) + a.warping_points


def set_total(character: Character, total: int) -> None:
    """Store `total` Warping Points as the Score and the points toward the
    next."""
    a = character.aging
    a.warping_score = score_for(max(0, total))
    a.warping_points = max(0, total) - points_for(a.warping_score)


def aura_points(aura: int) -> int:
    """Warping Points a year from living within an aura of this strength."""
    if aura < 6:
        return 0
    return AURA_POINTS.get(min(aura, 10), 0)


def ability(character: Character, name: str) -> int:
    found = next((a for a in character.abilities if a.name == name), None)
    return found.level if found else 0


@dataclass
class TwilightResult:
    entered: bool
    comprehended: bool = False
    time: str = ""
    seasons: int = 0
    extra_points: int = 0
    notes: list[str] = field(default_factory=list)


def twilight(
    character: Character, gained: int, aura: int, rng, saga=None
) -> TwilightResult:
    """The avoidance roll (and, failing it, Twilight) after `gained` points
    from one event, already added to the character's Warping."""
    a = character.aging
    wisdom = ability(character, "Enigmatic Wisdom")
    stats = character.characteristics
    mine = dice.stress_die(rng, 1, saga=saga)
    theirs = dice.stress_die(rng, 0, saga=saga).value
    resist = stats.stamina + ability(character, "Concentration") + mine.value
    against = a.warping_score + gained + wisdom + aura + theirs
    notes = [
        f"Avoiding Twilight: {resist} against {against}"
        + (" (botched)" if mine.botched else "")
        + "."
    ]
    if not mine.botched and resist >= against:
        notes.append("The magus regains control in two minutes.")
        return TwilightResult(False, notes=notes)
    extra = dice.simple_die(rng)
    comprehend = stats.intelligence + wisdom + dice.stress_die(rng, 1, saga=saga).value
    twilight_total = a.warping_score + dice.stress_die(rng, 0, saga=saga).value
    understood = not mine.botched and comprehend > twilight_total
    step = a.warping_score
    if a.warping_score >= 10:
        time, seasons = "eternity (Final Twilight)", 10_000
    elif a.warping_score == 9:
        years = 7 + dice.stress_die(rng, 0, saga=saga).value
        time, seasons = f"{years} years", 4 * years
    else:
        time, seasons = TWILIGHT_TIME[max(0, step - 1)]
    notes.append(
        f"Twilight: {'comprehended' if understood else 'not comprehended'} "
        f"({comprehend} against {twilight_total}); it lasts {time}; +{extra} "
        "more Warping Points."
    )
    notes.append(
        "The storyguide chooses its effects: a Twilight Scar, and "
        + (
            "knowledge, a Virtue or a spell."
            if understood
            else "lost knowledge, a Flaw or lost spells."
        )
    )
    return TwilightResult(True, understood, time, seasons, extra, notes)
