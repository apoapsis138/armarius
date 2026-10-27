"""Aging and Decrepitude: the yearly roll made in Winter.

- Rolled every Winter from the first after 35 (50 with Strong Faerie Blood),
  or at any age under a Longevity Ritual (then, before that age, 10+ counts
  as 9).
- Aging Total = a stress die (no botch) + age / 10 (rounded up) - Living
  Conditions - the Longevity Ritual's modifier - the familiar's bronze cord,
  plus the Virtues and Flaws that change aging rolls (Faerie Blood -1).
  Virtues and Flaws can also change the Living Conditions (Mild Aging +1),
  the roll to survive a Crisis, or keep Aging Points off the
  Characteristics (Unaging).
- 3+ adds a year of apparent age; 10+ gives Aging Points on the table; 13
  and 22+ give enough to reach the next Decrepitude score, and a Crisis.
- A Characteristic's Aging Points above the absolute value of its score
  lower it by 1 and start again. Every Aging Point is also a Decrepitude
  point: 5 = 1, 15 = 2, 30 = 3, 50 = 4, 75 = 5.
- An animal grog's kind has its own start and age modifier, and rolls
  in other seasons too (rules.animal_aging).
- Age Quickly and Demonic Blood: the effective age is twice the real age
  (used for the roll and a Longevity Ritual's vis), with two rolls a year.
- Nobody in Twilight ages (DE p. 229).
- A Crisis: a simple die + age / 10 + Decrepitude on the Crisis table; a
  Longevity Ritual guarantees survival, then ends. The survivor spends the
  next season recovering.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..models import Character, Saga
from . import animal_aging, dice, effects, sites
from .scores import character_source

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Aging, pp. 391-393"
)

START_AGE = 35
#: Decrepitude scores and the points each needs.
DECREPITUDE_POINTS: tuple[int, ...] = (0, 5, 15, 30, 50, 75)
CHARACTERISTICS = (
    "intelligence",
    "perception",
    "strength",
    "stamina",
    "presence",
    "communication",
    "dexterity",
    "quickness",
)
#: The Aging table's single-Characteristic rows (10-12 is the player's
#: choice: the app takes the highest score).
_TABLE: dict[int, tuple[str, ...]] = {
    14: ("quickness",),
    15: ("stamina",),
    16: ("perception",),
    17: ("presence",),
    18: ("strength", "stamina"),
    19: ("dexterity", "quickness"),
    20: ("communication", "presence"),
    21: ("intelligence", "perception"),
}
#: The Crisis table: (highest total, result, survival difficulty or None).
CRISIS: tuple[tuple[int, str, int | None], ...] = (
    (8, "Bedridden a week", None),
    (14, "Bedridden a month", None),
    (15, "Minor illness", 3),
    (16, "Serious illness", 6),
    (17, "Major illness", 9),
    (18, "Critical illness", 12),
)
TERMINAL = "Terminal illness (only CrCo 40 saves)"


def decrepitude_score(points: int) -> int:
    return max(i for i, need in enumerate(DECREPITUDE_POINTS) if points >= need)


def points_for_score(score: int) -> int:
    return DECREPITUDE_POINTS[max(0, min(score, 5))]


def _effects(character: Character, applies_to: str) -> list[effects.Effect]:
    return effects.collect([character_source(character.virtues_flaws)], applies_to)


def _amount(character: Character, applies_to: str) -> int:
    return int(effects.amount_total(_effects(character, applies_to)))


def start_age(character: Character) -> int:
    """The age the character's aging rolls start at."""
    found = [e.amount or 0 for e in _effects(character, "aging_start")]
    animal = animal_aging.start_age(character)
    return int(max([START_AGE if animal is None else animal, *found]))


def unaging(character: Character) -> bool:
    """Whether Aging Points never lower the character's Characteristics."""
    return bool(_effects(character, "unaging"))


def living_conditions(character: Character, living: int) -> int:
    """The Living Conditions modifier with the character's Virtues and
    Flaws (Mild Aging +1, Poor Living Conditions -1)."""
    return living + _amount(character, "living_conditions")


def aging_rate(character: Character) -> int:
    """How many years of effective age each year adds: 2 with Age Quickly
    or Demonic Blood (DE pp. 76, 119), else 1."""
    found = [int(e.amount or 1) for e in _effects(character, "aging_rate")]
    return max([1, *found])


def add_points(character: Character, name: str, points: int) -> list[str]:
    """Add Aging Points to a Characteristic: they count toward
    Decrepitude, and once more than its score (ignoring the sign) it falls
    by one and they start again, unless the character's Aging Points never
    lower Characteristics. Returns what changed."""
    aging = character.aging
    aging.decrepitude_points += points
    aging.decrepitude = decrepitude_score(aging.decrepitude_points)
    return place_points(character, name, points)


#: How an aging roll's "any Characteristic" point is written in the
#: Aging Points due: its Decrepitude is already counted (DE p. 392: the
#: Crisis rolls with it), so placing it adds only to the Characteristic.
ANY_POINT = "Aging roll"


def place_points(character: Character, name: str, points: int) -> list[str]:
    """Put Aging Points whose Decrepitude is counted into a
    Characteristic: once more than its score (ignoring the sign) it falls
    by one and they start again, unless Aging Points never lower the
    character's Characteristics. Returns what changed."""
    aging = character.aging
    aging.aging_points[name] = aging.aging_points.get(name, 0) + points
    score = getattr(character.characteristics, name)
    if aging.aging_points[name] > abs(score) and not unaging(character):
        setattr(character.characteristics, name, score - 1)
        aging.aging_points[name] = 0
        return [f"{name.title()} falls to {score - 1:+d}."]
    return []


AGE_QUICKLY = "vf_age_quickly"


def quick_since(character: Character) -> int | None:
    """The year Age Quickly began, when the Flaw names one (a curse or a
    magical disaster later in life, DE p. 119); None: from birth."""
    for vf in character.virtues_flaws:
        if vf.vf_id == AGE_QUICKLY:
            since = vf.params.get("since", "").strip()
            return int(since) if since.isdigit() else None
    return None


def _quick_from(character: Character) -> int | None:
    """The real age at which the faster aging began (None: from birth)."""
    since, born = quick_since(character), character.background.year_born
    return None if since is None or born is None else max(0, since - born)


def effective_age(character: Character, age: int) -> int:
    """The age the aging table and a Longevity Ritual use: the real age,
    or for one who ages twice as fast, twice it from birth (Demonic Blood,
    DE p. 76) or from the year Age Quickly began."""
    rate = aging_rate(character)
    start = _quick_from(character)
    if rate == 1 or start is None:
        return age * rate
    return age if age <= start else start + (age - start) * rate


def rolls_per_year(character: Character, age: int | None = None) -> int:
    """Aging rolls each Winter: two for one who ages twice as fast, once
    the faster aging has begun."""
    start = _quick_from(character)
    if start is not None and age is not None and age <= start:
        return 1
    return aging_rate(character)


def rolls_this_year(character: Character, age: int | None) -> bool:
    """Whether the character makes an aging roll this Winter: from the age
    aging starts, or with a Longevity Ritual; never a being of Magic the
    Great Elixir made immortal (TMRE p. 44)."""
    if age is None or character.being_of_magic:
        return False
    return age >= start_age(character) or character.aging.longevity_modifier > 0


@dataclass
class AgingResult:
    """What a year's aging roll does to one character (not yet applied)."""

    character_id: str
    total: int
    die: int
    apparent: bool = False
    points: dict[str, int] = field(default_factory=dict)
    #: Aging Points "in any Characteristic": how many, the player choosing
    #: where (DE p. 392); `suggested` is where they would fall, highest
    #: Characteristic first, as the form's default.
    any_points: int = 0
    suggested: list[str] = field(default_factory=list)
    crisis: bool = False
    crisis_text: str = ""
    #: Whether the Longevity Ritual ends (it saw the character through a
    #: Crisis).
    ritual_ends: bool = False
    notes: list[str] = field(default_factory=list)


def roll(
    character: Character,
    age: int,
    living: int,
    bronze_cord: int,
    rng: random.Random,
    saga: Saga | None = None,
    *,
    young: bool = False,
) -> AgingResult:
    """The year's aging roll for `character` aged `age`. A `young` roll
    (workshop exertion under 35) takes a simple die for the stress die,
    and its 13 brings no Crisis (City & Guild p. 74)."""
    die = dice.simple_die(rng) if young else dice.stress_die(rng, 0, saga=saga).value
    for_age = animal_aging.age_modifier(character, age)
    longevity = character.aging.longevity_modifier
    # The Lesser Elixir, in a dose of his own ritual (TMRE p. 42).
    elixir = character.alchemy.elixir_bonus if character.alchemy is not None else 0
    living = living_conditions(character, living)
    virtues = _effects(character, "aging_roll")
    if saga is not None:
        virtues += sites.character_effects(saga, character, "aging_roll")
    total = (
        die
        + for_age
        - living
        - longevity
        - (elixir if longevity else 0)
        - bronze_cord
        + int(effects.amount_total(virtues))
    )
    if age < start_age(character) and longevity and total >= 10:
        total = 9
    result = AgingResult(character.id, total, die)
    parts = [f"die {die}", f"+ age {for_age}"]
    if living:
        parts.append(f"- Living Conditions {living:+d}")
    if longevity:
        parts.append(f"- Longevity Ritual {longevity}")
    if longevity and elixir:
        parts.append(f"- Lesser Elixir {elixir}")
    if bronze_cord:
        parts.append(f"- bronze cord {bronze_cord}")
    for effect in virtues:
        amount = int(effect.amount or 0)
        parts.append(f"{'+' if amount >= 0 else '-'} {effect.name} {abs(amount)}")
    result.notes.append(f"Aging Total {total} ({' '.join(parts)}).")
    if total >= 3:
        result.apparent = True
    stats = character.characteristics
    if 10 <= total <= 12:
        result.any_points = 1
        result.suggested = [max(CHARACTERISTICS, key=lambda c: getattr(stats, c))]
    elif total in _TABLE:
        result.points = {name: 1 for name in _TABLE[total]}
    elif total == 13 or total >= 22:
        score = decrepitude_score(character.aging.decrepitude_points)
        needed = points_for_score(score + 1) - character.aging.decrepitude_points
        needed = max(1, needed)
        # Suggested over the Characteristics, highest first.
        order = sorted(CHARACTERISTICS, key=lambda c: -getattr(stats, c))
        result.any_points = needed
        result.suggested = [order[i % len(order)] for i in range(needed)]
        result.crisis = not (young and total == 13)
    return result


#: What Decrepitude 4 and 5 mean (DE p. 392; Unaging, p. 114).
FRAIL, DYING = 4, 5


def frailty(character: Character) -> str:
    """What the character's Decrepitude means once it reaches 4: frail,
    rolling on the Crisis Table for stressful activity (not for the
    Unaging), or at 5 bedridden and dying; "" below 4."""
    score = character.aging.decrepitude
    if score >= DYING:
        return (
            "Decrepitude 5: bedridden, dying within a few months; no mortal "
            "help can save them (DE p. 392)."
        )
    if score >= FRAIL and not unaging(character):
        return (
            "Decrepitude 4: extremely frail; a long journey, a fight or other "
            "stressful activity means a roll on the Crisis Table (DE p. 392)."
        )
    return ""


LEPROSY = "vf_leprosy"


def leper(character: Character) -> bool:
    """Leprosy: a Heavy Wound at every Aging Crisis (DE p. 135)."""
    return any(vf.vf_id == LEPROSY for vf in character.virtues_flaws)


#: The Crisis results that can kill: an illness with a survival roll, or
#: worse (DE p. 392).
_HARMLESS_CRISES = tuple(label for _, label, against in CRISIS if against is None)


def fatal_crisis(text: str) -> bool:
    """Whether a Crisis (as crisis() wrote it) is potentially fatal: not
    only bedridden for a week or a month."""
    return not any(f": {label}." in text for label in _HARMLESS_CRISES)


#: Medical attention through a crisis (DE p. 392).
PHYSICIAN = (
    "An attendant's Int + Medicine against 6 adds his Medicine score to it; "
    "only one doctor helps, and his botch takes 3 off (DE p. 392)."
)


def crisis(
    character: Character,
    age: int,
    decrepitude: int,
    rng: random.Random,
    saga: Saga | None = None,
) -> tuple[str, bool]:
    """Roll the Crisis: (what happens, whether the Longevity Ritual ends).
    Survival rolls are reported, not decided (the storyguide, medicine and
    magic can change them)."""
    die = dice.simple_die(rng)
    total = die + animal_aging.age_modifier(character, age) + decrepitude
    ritual = character.aging.longevity_modifier > 0
    what, against = TERMINAL, None
    for top, label, difficulty in CRISIS:
        if total <= top:
            what, against = label, difficulty
            break
    text = f"Aging Crisis: {total} (die {die}): {what}."
    if ritual:
        text += " The Longevity Ritual sees the character through, then ends."
    elif against is not None:
        bonus = _effects(character, "crisis_survival")
        extra = "".join(f" + {e.name} {int(e.amount or 0)}" for e in bonus)
        text += f" Survival: Stamina{extra} stress roll against {against}."
        text += " " + PHYSICIAN
    return text, ritual
