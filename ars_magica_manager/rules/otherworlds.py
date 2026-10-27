"""The realms themselves: a place that lies in the Magic Realm or the
Faerie Realm rather than in the mundane world, and the Magic Realm's
boundaries, vestiges, travel and Twilight Void.

A place (or one of its regio levels) names the realm it lies in by its
"world" detail; `WORLDS` is the lookup the aura reads (rules.sites). A
regio level may be one: crossing a Magic regio's boundary can lead into
the Magic Realm (RoP: Magic p. 20), and an entrance to Faerieland from a
faerie regio is a regio level of aura 10 (RoP: Faerie p. 16).

**The Magic Realm** (Realms of Power: Magic pp. 20-28):

- Its whole extent has a Magic aura of 10 (p. 20). Nearly every place in
  it lies within a realm boundary of level 0-10, which adds to magic done
  there like an aura, on top of the 10: the place's "boundary" detail, so
  its aura is 10 + the boundary (the book's "modified level of the
  aura", p. 22). A boundary is aligned with a Form, like an aligned aura:
  that Form's effects add the boundary again (Corpus 4: +18 to Corpus,
  +14 to the rest). Powers of other realms take no bonus from it. Every
  roll the aura helps takes as many extra botch dice as the boundary's
  level. Each season (the modified aura / 10, rounded up) pawns of vis of
  its Form appear there, fading within the season if not harvested.
- Those in it gain no experience: a season's experience comes as as many
  pawns of vis of one Art the player picks; a part season splits between
  vis and experience as an interrupted study does. No Aging rolls, though
  years still pass. Diameter, Sun and Moon last to the season's end, Year
  for as long as the target stays. Arcane Connections to things outside
  are interrupted, and none decay while there.
- Travel through a boundary or a vestige (pp. 22-23): only someone with
  Magic Might, Second Sight or Magic Sensitivity, who may lead others.
  Stress die + Perception + an Ability + the Form's bonus (Form / 5)
  against ((10 - the level) x 3) - Familiarity, the best one only; the
  aura doesn't count. By how much it passes is the Speed Level on the
  Twilight Void's journey chart; a leader concentrating (stress die +
  Stamina + Concentration + Form bonus) sets a new one while he does.
  Each botch on either roll is a step slower; below 0, stranded.
- In the Twilight Void (p. 24) no one eats, ages, heals or recovers
  long-term Fatigue. Leaving the path: Twilight Comprehension, Int +
  Enigmatic Wisdom + stress die against Warping Score (or Might / 5) +
  stress die. Passed, an Essential Trait +1 (and the total less
  Enigmatic Wisdom may speed the journey); failed, -1. Then a simple die:
  twice it in experience gained (or lost) in an Art or Ability (as vis if
  the player likes), and that many Warping Points for one without Might.
  Parma Magica and every spell duration end on entering or leaving it;
  Arcane Connections to or from the traveler fall a step on going in.
- Advancement (p. 26): the vis gathered may transform one without Might,
  one change a season (VIS_TRANSFORMATIONS).
- Magic Realm magic (pp. 26-28): Hermetic magic can't touch boundaries or
  vestiges without a Minor Breakthrough of 30 points, begun only after
  dealing with them there; or a pawn of gathered vis per magnitude buys
  an Insight into one effect (one a season).

**The Faerie Realm** (Realms of Power: Faerie p. 24): an aura of Faerie 10
throughout: Hermetic magic +5, and ten extra botch dice of their own
(rolled apart: their botches are strange rather than dangerous). The
realm table (rules.realms) already gives both from the aura.

Pattern: a dict lookup (the world's name -> its realm and aura) read by
the aura, and plain functions for the rest.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..arts import FORMS
from .rounding import round_down, round_up

SOURCE = "Realms of Power: Magic, The Magic Realm, pp. 20-28"
FAERIE_REALM_SOURCE = (
    "Realms of Power: Faerie, Environment and the Faerie Aura, p. 24; "
    "Finding a Regio Entrance, p. 16"
)


@dataclass(frozen=True)
class World:
    """A realm a place can lie in: its realm and the aura it has
    throughout."""

    name: str
    realm: str
    aura: int
    source: str


MAGIC_REALM, FAERIE_REALM = "Magic Realm", "Faerie Realm"

#: The worlds a place or regio level can lie in, by its "world" detail.
WORLDS: dict[str, World] = {
    w.name: w
    for w in (
        World(MAGIC_REALM, "Magic", 10, SOURCE),
        World(FAERIE_REALM, "Faerie", 10, FAERIE_REALM_SOURCE),
    )
}

#: The book each world comes from (sourcebooks abbreviations).
WORLD_BOOKS: dict[str, str] = {MAGIC_REALM: "RoP:M", FAERIE_REALM: "RoP:F"}

#: A boundary's or vestige's level runs from 0 to this.
MOST_LEVEL = 10
#: "An average vestige" (p. 23).
AVERAGE_VESTIGE = 4


def world_of(words: object) -> World | None:
    """The world `words` names, whatever its case; None for the mundane."""
    wanted = str(words or "").strip().casefold()
    return next((w for w in WORLDS.values() if w.name.casefold() == wanted), None)


def boundary_level(value: object) -> int:
    """A boundary or vestige level typed in a place's details, 0 to 10."""
    try:
        level = int(str(value or 0))
    except ValueError:
        return 0
    return max(0, min(MOST_LEVEL, level))


def boundary_form(words: object) -> str:
    """The Form a boundary is aligned with ("" when `words` names none)."""
    wanted = str(words or "").strip().casefold()
    return next((f for f in FORMS if f.casefold() == wanted), "")


def realm_aura(boundary: int) -> int:
    """The Magic Realm's aura where a boundary of that level lies: its own
    10 and the boundary."""
    return WORLDS[MAGIC_REALM].aura + boundary_level(boundary)


def boundary_bonus(boundary: int, form: str, arts: tuple[str, ...]) -> int:
    """What the Magic Realm adds to a magic act using `arts` within a
    boundary aligned with `form`: 10 + the boundary, and the boundary again
    when one of the Arts is its Form (p. 22)."""
    level = boundary_level(boundary)
    aligned = bool(form) and form.casefold() in {a.casefold() for a in arts}
    return realm_aura(level) + (level if aligned else 0)


def boundary_botch_dice(boundary: int) -> int:
    """The extra botch dice a boundary adds to each roll the aura helps."""
    return boundary_level(boundary)


def boundary_vis(boundary: int) -> int:
    """The pawns of vis of its Form a boundary gives each season: the
    modified aura / 10, rounded up (p. 22)."""
    return round_up(realm_aura(boundary) / 10)


# -- a season there (p. 20) --


def season_vis(experience: int, part: float = 1.0) -> tuple[int, int]:
    """A season's `experience` for one in the Magic Realm for `part` of it:
    (pawns of vis, experience points), the vis for the time there and the
    experience for the rest, split as an interrupted season is."""
    part = max(0.0, min(1.0, part))
    vis = round_down(experience * part)
    return vis, experience - vis


#: What a spell duration becomes in the Magic Realm (p. 20).
REALM_DURATIONS: dict[str, str] = {
    "Diameter": "to the season's end",
    "Sun": "to the season's end",
    "Moon": "to the season's end",
    "Year": "for as long as the target stays",
}


def ages_there(world: str) -> bool:
    """Whether one living in `world` makes Aging rolls (not in the Magic
    Realm, though the years still count)."""
    return world != MAGIC_REALM


# -- travel through boundaries and vestiges (pp. 22-23) --

#: The Familiarity modifiers by what the traveler knows of the
#: destination; only the best counts.
FAMILIARITY: dict[str, int] = {
    "Knows its name or a description": 1,
    "Has seen it": 3,
    "Has visited it": 6,
    "An Arcane Connection to it": 15,
}
#: Abilities that give Familiarity: their score, or score x the multiple.
FAMILIARITY_ABILITIES: dict[str, int] = {
    "Enigmatic Wisdom": 1,
    "Magic Lore": 1,
    "Area Lore: Magic Realm": 3,
}


def familiarity(known: str = "", abilities: dict[str, int] | None = None) -> int:
    """The best Familiarity modifier: what the traveler knows of the
    destination, or an Ability's (score, or Area Lore x 3)."""
    found = [FAMILIARITY.get(known, 0)]
    for name, score in (abilities or {}).items():
        multiple = FAMILIARITY_ABILITIES.get(name, 0)
        found.append(multiple * max(0, score))
    return max(found)


def travel_ease(level: int, familiar: int = 0) -> int:
    """The Ease Factor to see through and pass a boundary or vestige:
    (10 - its level) x 3 - Familiarity."""
    return (MOST_LEVEL - boundary_level(level)) * 3 - max(0, familiar)


def can_travel(
    has_magic_might: bool, second_sight: bool, magic_sensitivity: bool
) -> bool:
    """Whether a character can lead the way through a boundary or vestige."""
    return has_magic_might or second_sight or magic_sensitivity


#: The Twilight Void's journey chart: from each Speed Level up, how long.
JOURNEYS: tuple[tuple[int, str], ...] = (
    (0, "seven years and a stress die more (no botch)"),
    (3, "seven years"),
    (6, "a year"),
    (9, "a season"),
    (12, "a month (Moon)"),
    (15, "a day"),
    (18, "until sunrise or sunset (Sun)"),
    (21, "two hours"),
    (24, "two minutes (Diameter)"),
    (27, "one minute"),
    (30, "a moment"),
)
STRANDED = "for ever: stranded in the Void"


def speed_level(total: int, ease: int, botches: int = 0) -> int:
    """The Speed Level a travel roll gives: how far it passes the Ease
    Factor, a step (3) slower for each botch."""
    return total - ease - 3 * max(0, botches)


def journey(speed: int) -> str:
    """How long the journey through the Void takes at `speed`."""
    if speed < 0:
        return STRANDED
    return [text for least, text in JOURNEYS if speed >= least][-1]


def void_speed(speed: int, comprehension: int, enigmatic_wisdom: int) -> int:
    """A Speed Level after a comprehended experience in the Void: the
    comprehension total less Enigmatic Wisdom, when that is faster."""
    return max(speed, comprehension - enigmatic_wisdom)


@dataclass(frozen=True)
class Comprehension:
    """What straying from the path in the Twilight Void did."""

    passed: bool
    trait: int
    experience: int
    warping: int


def void_comprehension(
    total: int, against: int, simple_die: int, *, has_might: bool
) -> Comprehension:
    """A Twilight Comprehension roll in the Void: Int + Enigmatic Wisdom +
    stress die (`total`) against Warping Score or Might / 5 + stress die
    (`against`). An Essential Trait +1 or -1, then twice the simple die in
    experience gained or lost, and the die in Warping for one without
    Might (p. 24)."""
    passed = total >= against
    xp = 2 * max(0, simple_die)
    return Comprehension(
        passed,
        1 if passed else -1,
        xp if passed else -xp,
        0 if has_might else max(0, simple_die),
    )


def comprehension_against(warping_score: int, might: int | None = None) -> int:
    """The Warping Score a Comprehension roll beats: Might / 5 for one
    with Might (a stress die is added to it)."""
    return round_down(might / 5) if might is not None else warping_score


# -- advancement (p. 26) --

#: What a pawn count of the vis gathered there buys one without Might, one
#: transformation a season (Hermetic, Supernatural or General Virtues and
#: Flaws that suit the journey; none that only matter at creation).
VIS_TRANSFORMATIONS: dict[int, str] = {
    0: "Change a Virtue or Flaw for another of its kind and size",
    5: "Gain a Minor Virtue and a Minor Flaw",
    10: "Gain a Minor Virtue",
    15: "Gain a Major Virtue and a Major Flaw",
    20: "Raise a Minor Virtue to Major, a Minor Flaw to a Minor Virtue, or a "
    "Major Flaw to Minor",
    25: "Gain a Major Virtue and a Minor Flaw",
    30: "Gain a Major Virtue",
}


def transformations(pawns: int) -> list[str]:
    """Every transformation `pawns` of gathered vis can pay for."""
    return [text for cost, text in VIS_TRANSFORMATIONS.items() if cost <= pawns]


# -- Magic Realm magic (pp. 26-28) --

#: Breakthrough Points of the Minor Breakthrough that opens the guidelines.
BREAKTHROUGH_POINTS = 30


def created_boundary(level: int) -> int:
    """The boundary a Creo spell of that level makes where there is none:
    its magnitude less 4 (a base 25 effect makes level 1)."""
    return max(0, round_down(level / 5) - 4)


def insight_magnitude(pawns: int) -> int:
    """The magnitude of the effect an Insight bought with gathered vis
    gives: one a pawn."""
    return max(0, pawns)


def world_text(world: str, boundary: int = 0, form: str = "") -> str:
    """What lying in `world` does, as a place's facts say it."""
    if world == FAERIE_REALM:
        return (
            "the Faerie Realm: Faerie 10 throughout; Hermetic magic +5 with "
            "ten botch dice of their own (rolled apart, their botches "
            "strange rather than dangerous)"
        )
    if world != MAGIC_REALM:
        return ""
    level = boundary_level(boundary)
    form = boundary_form(form)
    parts = [f"the Magic Realm: Magic 10 + a boundary of {level}"]
    if level:
        parts.append(f"+{level} botch dice on rolls the aura helps")
    parts.append(
        f"{boundary_vis(level)} pawn{'s' if boundary_vis(level) != 1 else ''}"
        f" of {form or 'its Form'} vis a season (fading if not taken)"
    )
    parts.append(
        "no experience (a season's comes as vis) and no Aging rolls; "
        "Diameter, Sun and Moon last to the season's end, Year while there"
    )
    parts.append(
        "to travel on through it (Magic Might, Second Sight or Magic "
        f"Sensitivity), Per + Ability + Form / 5 against {travel_ease(level)} "
        "less Familiarity"
    )
    return "; ".join(parts)
