"""Warping and Wizard's Twilight.

- The Warping Score advances like an Ability on Warping Points: n takes
  5 x n(n + 1) / 2 points in all.
- Automatic sources, each Winter: a Longevity Ritual (+1 a year) and living
  in a strong aura of another realm (6: 1, 7: 1, 8: 2, 9: 4, 10: 12 a
  year; a magus gains none from a Magic aura).
- Gaining 2+ points from one event takes a magus to the edge of Twilight:
  Stamina + Concentration + Vim Form Bonus + stress die against Warping
  Score + the points + Enigmatic Wisdom + the local aura + a stress die (no
  botch). She may choose to enter instead. Failing enters Twilight:
  Intelligence + Enigmatic Wisdom + stress die against Warping Score +
  stress die, each with 1 + the points as botch dice, decides whether it is
  comprehended (a botch on the Twilight's side leaves it 0 to beat).
- Its time goes by Warping Score: comprehended, each point Intelligence +
  die beats the Twilight's total by is a step shorter (below a Diameter, a
  moment); a botched comprehension a step longer for each zero, with a
  bad effect, and reaching row 10 is Final Twilight. It adds a
  simple die of Warping Points; the effects are sized by all the points
  gained: 2 xp a point, a Virtue (or Flaw) at 7 or more, a spell of that
  many magnitudes (DE pp. 228-230).
- Warping touches non-magi too: a Minor Flaw at Score 1 and 3, a Minor
  supernatural Virtue at 5 (no more points from auras of its kind), a
  Major Flaw at 6 and each point after; a Might score or Demonic Blood is
  immune (DE pp. 75, 389, 391). A body in Twilight doesn't age (DE p. 229).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..models import SEASONS, Character, ConstantEffect, Saga
from . import dice, effects
from .derived import form_bonus
from .scores import ability_level, character_source

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Warping, pp. 389-391"
)
TWILIGHT_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 7: Hermetic Magic, Wizard's "
    "Twilight, pp. 228-230"
)
#: What a non-magus's Warping Score brings (DE p. 391).
MUNDANE_EFFECTS: dict[int, str] = {
    1: "a Minor Flaw from the main source of the Warping",
    3: "a second Minor Flaw",
    5: (
        "a Minor supernatural Virtue attuned to the main source (no more "
        "Warping from living in auras of its kind; the app takes the main "
        "source to be the aura where they live, so note the Virtue's realm "
        "if effects were the main source instead)"
    ),
    6: "a Major Flaw from the main sources of the Warping",
}
#: The Score from which a non-magus gains no more points from auras.
ATTUNED_SCORE = 5
#: The time table's last row, Final Twilight.
FINAL_STEP = 10

#: Warping Points a year from living always within a strong aura.
AURA_POINTS: dict[int, int] = {6: 1, 7: 1, 8: 2, 9: 4, 10: 12}
#: How much of their time a character spends in the aura (DE p. 390):
#: always (living, working and sleeping there), half (sleeping there but
#: working elsewhere, or two weeks in and two out), frequent visits (about
#: a quarter), or away.
ALWAYS, HALF, FREQUENT, AWAY = "always", "half", "frequent", "away"
AURA_TIMES: dict[str, str] = {
    ALWAYS: "Always: lives, works and sleeps there",
    HALF: "Half the time",
    FREQUENT: "Frequent visits (about a quarter)",
    AWAY: "Lives elsewhere",
}
#: The points a year for half the time and frequent visits; 0.5 is one
#: point every second year.
PART_TIME_POINTS: dict[str, dict[int, float]] = {
    HALF: {6: 0, 7: 0.5, 8: 1, 9: 2, 10: 4},
    FREQUENT: {6: 0, 7: 0, 8: 0, 9: 1, 10: 2},
}
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


def opened_to_arts(character: Character) -> bool:
    """A magus, or anyone else whose Hermetic Arts are opened (any Art with
    experience): who a laboratory Disaster's Warping takes to the edge of
    Twilight."""
    return character.type == "magus" or any(
        art.xp > 0 for art in character.arts.values()
    )


def immune(character: Character) -> bool:
    """Whether nothing warps the character: a Might score (Demonic Blood
    gives one) makes them part of a realm already (DE pp. 75, 389)."""
    return bool(
        effects.collect([character_source(character.virtues_flaws)], "warping_immune")
    )


def in_twilight(saga: Saga, character: Character) -> bool:
    """Whether the character is lost in Twilight this season (their body,
    if it stayed, doesn't age: DE p. 229)."""
    until = character.aging.twilight_until
    if not until:
        return False
    season, _, year = until.partition(" ")
    if season not in SEASONS or not year.isdigit():
        return False
    return (saga.current_year, SEASONS.index(saga.current_season)) <= (
        int(year),
        SEASONS.index(season),
    )


def mundane_effects(before: int, after: int) -> list[str]:
    """What a non-magus gains as their Warping Score goes from `before` to
    `after` (DE p. 391)."""
    found: list[str] = []
    for score in range(before + 1, after + 1):
        what = MUNDANE_EFFECTS.get(min(score, 6))
        if what:
            found.append(f"Warping Score {score}: {what}.")
    return found


def aura_points(aura: int, time: str = ALWAYS, year: int = 0) -> int:
    """Warping Points a year from an aura of this strength, by how much of
    their time they spend in it (one point every second year falls in an
    even year)."""
    if aura < 6 or time == AWAY:
        return 0
    strength = min(aura, 10)
    if time not in PART_TIME_POINTS:
        return AURA_POINTS.get(strength, 0)
    each = PART_TIME_POINTS[time].get(strength, 0)
    if 0 < each < 1:
        return 1 if year % 2 == 0 else 0
    return int(each)


@dataclass
class TwilightResult:
    entered: bool
    comprehended: bool = False
    time: str = ""
    seasons: int = 0
    extra_points: int = 0
    notes: list[str] = field(default_factory=list)


def twilight(
    character: Character,
    gained: int,
    aura: int,
    rng: random.Random,
    saga: Saga | None = None,
    *,
    enter: bool = False,
) -> TwilightResult:
    """The avoidance roll (and, failing it, Twilight) after `gained` points
    from one event, already added to the character's Warping. With
    `enter`, the magus chooses Twilight and makes no avoidance roll."""
    a = character.aging
    wisdom = ability_level(character, "Enigmatic Wisdom")
    stats = character.characteristics
    vim = form_bonus(character, "Vim")
    notes: list[str] = []
    botched = False
    if enter:
        notes.append("The magus chooses to enter Twilight.")
    else:
        mine = dice.stress_die(rng, 1, saga=saga)
        theirs = dice.stress_die(rng, 0, saga=saga).value
        resist = (
            stats.stamina + ability_level(character, "Concentration") + vim + mine.value
        )
        against = a.warping_score + gained + wisdom + aura + theirs
        notes.append(
            f"Avoiding Twilight: {resist} (Vim Form Bonus {vim:+d}) against "
            f"{against}" + (" (botched)" if mine.botched else "") + "."
        )
        botched = mine.botched
        if not botched and resist >= against:
            notes.append("The magus regains control in two minutes.")
            return TwilightResult(False, notes=notes)
    extra = dice.simple_die(rng)
    botch_dice = 1 + gained
    my_die = dice.stress_die(rng, botch_dice, saga=saga)
    their_die = dice.stress_die(rng, botch_dice, saga=saga)
    comprehend = stats.intelligence + wisdom + my_die.value
    twilight_total = 0 if their_die.botched else a.warping_score + their_die.value
    understood = not botched and not my_die.botched and comprehend > twilight_total
    step = a.warping_score
    if understood:
        # Without Enigmatic Wisdom, each point past the Twilight's total is
        # a step shorter.
        step -= max(0, stats.intelligence + my_die.value - twilight_total)
    elif my_die.botched:
        step += my_die.botches
    time, seasons = _twilight_time(step, a.warping_score, rng, saga)
    notes.append(
        f"Twilight: {'comprehended' if understood else 'not comprehended'} "
        f"({comprehend} against {twilight_total}"
        + (", botched" if my_die.botched else "")
        + f"); it lasts {time}; +{extra} more Warping Points."
    )
    notes.append(_effects_note(understood, gained + extra))
    return TwilightResult(True, understood, time, seasons, extra, notes)


def _twilight_time(
    step: int, score: int, rng: random.Random, saga: Saga | None
) -> tuple[str, int]:
    """The real time a Twilight takes at this step of the table (step 1
    a Diameter, the Warping Score's step its base time), and its seasons."""
    # Row 10 is Final Twilight, reached by a Warping Score of 10 or by a
    # botch's steps down the same table (DE p. 228).
    if score >= 10 or step >= FINAL_STEP:
        return "eternity (Final Twilight)", 10_000
    if step < 1:
        return "a mere moment", 0
    if step == FINAL_STEP - 1:
        years = 7 + dice.stress_die(rng, 0, saga=saga).value
        return f"{years} years", 4 * years
    return TWILIGHT_TIME[step - 1]


def _effects_note(understood: bool, points: int) -> str:
    """The storyguide's choice of Twilight's effects, sized by the points
    gained in all (DE pp. 229-230)."""
    xp = 2 * points
    if understood:
        virtue = (
            "a Major Hermetic or Supernatural Virtue"
            if points > 10
            else "a Minor Hermetic or Supernatural Virtue"
            if points >= 7
            else "no Virtue (fewer than 7 points)"
        )
        return (
            f"The storyguide chooses its effects ({points} points): a good "
            f"Twilight Scar, and {xp} xp in an Art, Magic Theory or Enigmatic "
            f"Wisdom, {virtue}, or a new spell of {points} magnitudes."
        )
    flaw = (
        "a Major Hermetic or Supernatural Flaw"
        if points >= 10
        else "a Minor Hermetic or Supernatural Flaw"
        if points >= 7
        else "no Flaw (fewer than 7 points)"
    )
    return (
        f"The storyguide chooses its effects ({points} points): a bad Twilight "
        f"Scar, and {xp} xp lost from an Art, Magic Theory or Enigmatic Wisdom, "
        f"{flaw}, or spells of {points} magnitudes lost."
    )


CONSTANT_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Warping, Constant "
    "Supernatural Effects, pp. 390-391"
)
#: A season's point for a powerful effect not made for the subject, on top
#: of the year's.
SEASONS_A_YEAR = 4


def constant_points(effect: ConstantEffect) -> int:
    """The Warping Points a constant effect gives each year: 1, and for a
    powerful one neither cast by nor designed for the subject 1 a season
    more (DE p. 391)."""
    if effect.powerful and not effect.designed_for:
        return 1 + SEASONS_A_YEAR
    return 1


def first_point(effect: ConstantEffect) -> int:
    """The Warping Point a powerful effect not made for the subject gives
    when it begins (DE p. 390)."""
    return 1 if effect.powerful and not effect.designed_for else 0
