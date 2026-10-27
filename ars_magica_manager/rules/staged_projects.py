"""Hermetic Projects' staged projects: the Burning City, the Intangible
Assassin and the Living Corpse. Most of each chapter is its spells and
devices, which the troupe invents as lab work; what is kept here is the
chapter's stages and its own rules. (No errata touches these rules: the
errata's Hermetic Projects entries correct spells' levels only.)

The Burning City (Hermetic Projects pp. 9-28):

- Its hazards (pp. 13-14) are injuries and poisons on rules.harm's
  tables: lava is +15, multiplied by how much it covers (+30 a limb, +45
  half the body, +60 immersion), each round; armour counts only while
  less than half the body is covered. Boiling mud and water +3, likewise
  multiplied. Within 30 yards of molten lava, +3 heat each Diameter.
  Within 15 paces of a crater or a river of lava the fumes call for an air
  Deprivation check every 30 seconds and, each Diameter, a Stamina check
  against 6 or a Medium Wound. Falling rocks in an eruption do +5 to +20.
- Vulcan's Warning Bell (pp. 16-17) warns of an eruption a stress die of
  days ahead; on a 0 the botch die's number is hours, and a botch gives no
  warning at all.
- Its laboratory Virtues, Flaws and Features (pp. 19, 26-27) are in the
  lab catalogs.

The Intangible Assassin (Hermetic Projects pp. 77-95):

- Gathering Arcane Connections (pp. 86-93): spilled blood, or the blood
  on the weapon that drew it, lasts years (pp. 87-88); a book or Lab Text
  he wrote lasts weeks after the writing (p. 90); his breath, caught in a
  phial, lasts hours (p. 91). The sympathetic connections (a blood
  relative, his names, his signature, horoscopes, a symbolic
  representation, pp. 91-93) are rules.penetration's.
- The Aegis problem (pp. 94-95): Guttering of the Home-Fires suppresses
  an Aegis of less than half its level + 3 magnitudes; Removing the
  Hearth's Keystone dispels one of less than its level + 3 magnitudes + a
  stress die. Both must Penetrate the Aegis. A magus casting from inside
  a hostile Aegis loses half its level from his Casting Total (p. 79).

The Living Corpse (Hermetic Projects pp. 96-118), when a magus becomes
one:

- The ghost his spirit becomes (pp. 107-108), by one of two options. One:
  a simple die on the chart (1 no spirit, 2 another realm's ghost, 3
  mindless, 4-5 an animating spirit, 6-7 a specter, 8 a shade, 9-10 an
  apparition). Two: his stress die + aura + Magic Lore + Vim Form Bonus
  against the storyguide's stress die (no botch) + all his Personality
  Traits' values + his highest Divine, Infernal or Faerie Lore; lower is
  a ghost of that other realm, a botch none, equal or higher a magic
  ghost, 3 more a specter, 6 a shade, 9 an apparition. Only a specter, if
  any magic ghost, for the unGifted.
- His starting Magic Might by the saga's power and the ghost (pp.
  108-109), its vis one pawn for every 5 of Might, rounded up (p. 109).
- The experience to buy back his Abilities, by the ghost's Season (p.
  110): an animating spirit Spring, 120; a specter Summer, 360; a shade
  Autumn, 720; an apparition Winter, 1200.
- His one Personality Trait: his highest, doubled (p. 111).
- His Virtues (p. 109): The Gift becomes Magic Spirit, and he gains
  Transformed (Being) and Magical Air (none for the Gentle Gift; Blatant
  Magical Air for the Blatant).
- A corpse animated days after death (p. 108): its Mental
  Characteristics are gone, and each Physical one falls 1 a day, to -5,
  where it stays a year.
- After (p. 114): no aging, Warping or Final Twilight; he can't be
  Incapacitated, and does no lab work."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from ..models import Saga
from ..models.hermetic_projects import (
    BURNING_CITY,
    INTANGIBLE_ASSASSIN,
    LIVING_CORPSE,
)
from . import dice

HP = "Hermetic Projects"
SOURCE = "Hermetic Projects, Chapters Two, Five and Six, pp. 9-118"

#: Each staged project's stages, in the chapter's order, with its pages.
STAGES: dict[str, tuple[tuple[str, str], ...]] = {
    BURNING_CITY: (
        ("Find a volcano", "pp. 12-13"),
        ("Raise or wake a volcano", "p. 13"),
        ("Protect the people", "pp. 14-16"),
        ("Control the volcano", "pp. 16-17"),
        ("Build in the crater", "pp. 17-19"),
        ("Live in the crater", "pp. 19-24"),
        ("Deal with its inhabitants", "pp. 24-26"),
        ("Fit out the laboratories", "pp. 26-27"),
    ),
    INTANGIBLE_ASSASSIN: (
        ("The tunnel spells", "pp. 78-81"),
        ("Manipulating the tunnel", "pp. 81-82"),
        ("Defending against tunnels", "pp. 82-83"),
        ("Effects to cast through them", "pp. 83-86"),
        ("Gathering connections", "pp. 86-93"),
        ("Raising the Casting Total", "pp. 93-94"),
        ("The Aegis of the Hearth", "pp. 94-95"),
    ),
    LIVING_CORPSE: (
        ("Bind a ghost to a vessel", "pp. 96-97"),
        ("Animate the corpse", "p. 97"),
        ("Pass control to the ghost", "pp. 97-98"),
        ("Enchant the devices", "pp. 98-105"),
        ("The transformation", "pp. 106-108"),
    ),
}

#: What each staged project is, in a line.
KIND_LINES: dict[str, str] = {
    BURNING_CITY: "a covenant built in the heart of a volcano",
    INTANGIBLE_ASSASSIN: "the tunnel spells and their kin, for Wizard's War",
    LIVING_CORPSE: "a ghost bound to an animated corpse, to outlast death",
}


def stage_names(kind: str) -> list[str]:
    return [name for name, _ in STAGES.get(kind, ())]


def stage_pages(kind: str, name: str) -> str:
    return next((pages for stage, pages in STAGES.get(kind, ()) if stage == name), "")


# -- the Burning City ----------------------------------------------------------

#: Vulcan's Warning Bell (pp. 16-17).
BELL_SOURCE = "Hermetic Projects, Vulcan's Warning Bell, pp. 16-17"


@dataclass(frozen=True)
class Warning:
    """The bell's warning: in days or hours, or none (a botch)."""

    amount: int
    unit: str
    botches: int = 0

    def words(self) -> str:
        if not self.unit:
            return "The bell gives no warning: the eruption comes unheralded."
        plural = "" if self.amount == 1 else "s"
        return f"The bell rings {self.amount} {self.unit}{plural} before the eruption."


def warning_bell(rng: random.Random, saga: Saga | None = None) -> Warning:
    """A stress die of days; on a 0 the botch die's face is the hours, and
    a botch (that die's own 0) gives no warning."""
    die = dice.stress_die(rng, saga=saga)
    if not (die.stress and die.value == 0):
        return Warning(die.value, "day")
    hours = die.botch_faces[0] if die.botch_faces else 0
    if hours == 0:
        return Warning(0, "", 1)
    return Warning(hours, "hour")


# -- the Intangible Assassin ---------------------------------------------------

GATHER_SOURCE = "Hermetic Projects, Gathering Connections, pp. 86-93"


@dataclass(frozen=True)
class Gathering:
    """A way of gathering an Arcane Connection to a quarry, and how long
    it lasts (rules.penetration.ARCANE_CONNECTIONS's key)."""

    key: str
    label: str
    lasts: str
    pages: str


GATHERINGS: tuple[Gathering, ...] = (
    Gathering(
        "blood", "His spilled blood, caught in a phial", "Years or decades", "pp. 86-88"
    ),
    Gathering("weapon", "The weapon that drew his blood", "Years or decades", "p. 87"),
    Gathering(
        "text",
        "A book or Lab Text he has written lately",
        "Weeks or months",
        "p. 90",
    ),
    Gathering("breath", "His breath, sealed in a phial", "Hours or days", "p. 91"),
)
GATHERING_BY_KEY: dict[str, Gathering] = {g.key: g for g in GATHERINGS}

AEGIS_SOURCE = "Hermetic Projects, The Problem of the Aegis of the Hearth, pp. 94-95"
GUTTERING, KEYSTONE = "guttering", "keystone"
#: Three magnitudes, in levels (p. 94).
AEGIS_REACH = 15


def guttering_reach(level: int) -> int:
    """The Aegis Guttering of the Home-Fires suppresses must be less than
    half its level + 3 magnitudes."""
    return level // 2 + AEGIS_REACH


def keystone_reach(level: int, die: int) -> int:
    """The Aegis Removing the Hearth's Keystone dispels must be less than
    its level + 3 magnitudes + the stress die."""
    return level + AEGIS_REACH + die


# -- the Living Corpse ---------------------------------------------------------

CORPSE_SOURCE = "Hermetic Projects, The Living Corpse, pp. 106-111"
NO_SPIRIT, OTHER_REALM, MINDLESS, ANIMATING, SPECTER, SHADE, APPARITION = (
    "none",
    "other realm",
    "mindless",
    "animating spirit",
    "specter",
    "shade",
    "apparition",
)
GHOST_WORDS: dict[str, str] = {
    NO_SPIRIT: "No spirit remains, now or ever",
    OTHER_REALM: "A ghost of another realm",
    MINDLESS: "A mindless spirit, Magic Might 0 and no powers",
    ANIMATING: "A simple animating spirit, like a revenant's",
    SPECTER: "A magic ghost: a specter",
    SHADE: "A magic ghost: a shade",
    APPARITION: "A magic ghost: an apparition",
}
#: Option One's chart (pp. 107-108): the simple die -> the ghost.
CHART: dict[int, str] = {
    1: NO_SPIRIT,
    2: OTHER_REALM,
    3: MINDLESS,
    4: ANIMATING,
    5: ANIMATING,
    6: SPECTER,
    7: SPECTER,
    8: SHADE,
    9: APPARITION,
    10: APPARITION,
}
#: Option Two: how far above the storyguide's roll each ghost is (p. 108).
CONTEST_STEPS: tuple[tuple[int, str], ...] = ((9, APPARITION), (6, SHADE), (3, SPECTER))
POWERS: tuple[str, ...] = ("Low", "Medium", "High", "Legendary")
#: Starting Magic Might by the saga's power and the ghost (pp. 108-109).
STARTING_MIGHT: dict[str, dict[str, int]] = {
    "Low": {SPECTER: 0, SHADE: 5, APPARITION: 10},
    "Medium": {SPECTER: 3, SHADE: 10, APPARITION: 20},
    "High": {SPECTER: 5, SHADE: 15, APPARITION: 30},
    "Legendary": {SPECTER: 10, SHADE: 25, APPARITION: 50},
}
#: The ghost's Season and the experience to buy back Abilities (p. 110).
SEASON_XP: dict[str, tuple[str, int]] = {
    ANIMATING: ("Spring", 120),
    SPECTER: ("Summer", 360),
    SHADE: ("Autumn", 720),
    APPARITION: ("Winter", 1200),
}
#: How far each Physical Characteristic falls, at most, before a year
#: dead turns it "n/a" (p. 108).
DECAY_FLOOR = -5
DECAY_YEAR_DAYS = 365
GIFTED_ONLY = (SHADE, APPARITION)


def chart(roll: int) -> str:
    """Option One: the ghost a simple die gives."""
    return CHART[min(max(roll, 1), 10)]


def contest(player: int, storyguide: int, botched: bool) -> str:
    """Option Two: the ghost the player's death roll against the
    storyguide's gives."""
    if botched:
        return NO_SPIRIT
    if player < storyguide:
        return OTHER_REALM
    margin = player - storyguide
    found = next((ghost for step, ghost in CONTEST_STEPS if margin >= step), "")
    return found or SPECTER


def ungifted(ghost: str) -> str:
    """An unGifted character's magic ghost is only ever a specter."""
    return SPECTER if ghost in GIFTED_ONLY else ghost


def starting_might(power: str, ghost: str) -> int:
    return STARTING_MIGHT.get(power, STARTING_MIGHT["Medium"]).get(ghost, 0)


def vis_pawns(might: int) -> int:
    """One pawn of its Form for every 5 points of Might, rounded up."""
    return math.ceil(might / 5) if might > 0 else 0


def decay(days: int) -> int | None:
    """What each Physical Characteristic loses for a corpse animated
    `days` after death: 1 a day to -5, None ("n/a") after a year."""
    if days > DECAY_YEAR_DAYS:
        return None
    return max(-days, DECAY_FLOOR)


def magical_air(gift: str) -> str:
    """The Flaw his Gift becomes: none for the Gentle Gift, Blatant
    Magical Air for the Blatant, Magical Air otherwise (p. 109)."""
    if gift == "Gentle":
        return ""
    if gift == "Blatant":
        return "Blatant Magical Air"
    return "Magical Air"
