"""After the apocalypse of Dies Irae: the Lunar aura, and what the fall of
the lunar sphere does to Hermetic magic (Dies Irae pp. 36-38).

- **The Lunar aura** (p. 36). Where matter of the fallen sphere rests, a
  Lunar aura grows, as strong as the matter is plentiful. A season's work
  clearing it (or Rego Craft Magic) lowers it by 1; the matter carried
  off, unless destroyed by magic, raises another Lunar aura by 1 or
  starts a new one at 1 for each point. Lunar is "a new Supernatural
  Realm": a place, regio level or covenant whose aura's realm is Lunar
  has a Lunar aura, offered while the book is in play
  (rules.realms.aura_realms).
- **Realm interaction** (p. 37): the replacement table, `MULTIPLE`, with
  the Lunar realm added. A Lunar aura costs Magic and Faerie powers 5 x
  the aura, Infernal ones the aura, and Divine ones nothing; Lunar powers
  lose the aura in Magic, Faerie and Infernal auras and 3 x it in a
  Divine one. Creatures and effects from the lunar sphere use Lunar
  powers. The other realms' rows are the core table's.
- **Durations** (p. 37). With the heavens stopped, Diameter, Sun, Moon
  and Year fail, and with them Parma Magica and the Aegis of the Hearth;
  Momentary, Concentration and Ring still work. Each replacement
  (`DURATIONS`) is a Minor Breakthrough of 30 points (150 levels of
  experimental effects); a new Parma or Aegis takes 60. A spell may use a
  duration not yet formalized as a non-standard one, a magnitude higher.
- **What is spared** (p. 38): the powers of supernatural beasts, and
  Divine and Infernal powers, save for the aura's penalties; Objects of
  Virtue and extraordinary vis work as before.

An aura may be Lunar (rules.realms.AURA_REALMS), and rules.realms takes
this table's Lunar row and column into its own, so totals worked in a
Lunar aura take it like any other realm's. Records (creatures,
traditions, Virtues) still belong to one of the four realms
(models.REALMS).

Pattern: a dict lookup (power realm, aura realm) -> multiple, like the
core realm table (rules.realms), and plain functions.
"""

from __future__ import annotations

from .rounding import round_down

SOURCE = "Dies Irae, Magic After the Apocalypse, pp. 36-38"

LUNAR = "Lunar"
REALMS: tuple[str, ...] = (LUNAR, "Magic", "Divine", "Faerie", "Infernal")

#: The replacement Realm Interaction Table: (power realm, aura realm) ->
#: multiple of the aura (0.5 a half, rounded down; 0 no effect).
MULTIPLE: dict[tuple[str, str], float] = {
    (LUNAR, LUNAR): 1,
    ("Magic", LUNAR): -5,
    ("Divine", LUNAR): 0,
    ("Faerie", LUNAR): -5,
    ("Infernal", LUNAR): -1,
    (LUNAR, "Magic"): -1,
    ("Magic", "Magic"): 1,
    ("Divine", "Magic"): 0,
    ("Faerie", "Magic"): 0.5,
    ("Infernal", "Magic"): -1,
    (LUNAR, "Divine"): -3,
    ("Magic", "Divine"): -3,
    ("Divine", "Divine"): 1,
    ("Faerie", "Divine"): -4,
    ("Infernal", "Divine"): -5,
    (LUNAR, "Faerie"): -1,
    ("Magic", "Faerie"): 0.5,
    ("Divine", "Faerie"): 0,
    ("Faerie", "Faerie"): 1,
    ("Infernal", "Faerie"): -1,
    (LUNAR, "Infernal"): -1,
    ("Magic", "Infernal"): -1,
    ("Divine", "Infernal"): 0,
    ("Faerie", "Infernal"): -2,
    ("Infernal", "Infernal"): 1,
}


def modifier(power_realm: str, aura_realm: str, aura: int) -> int:
    """What an aura adds to (or takes from) a power of `power_realm`, by
    the replacement table."""
    multiple = MULTIPLE.get((power_realm, aura_realm))
    if multiple is None:
        raise ValueError(f"No realm pair {power_realm!r}, {aura_realm!r}")
    return round_down(multiple * max(0, aura))


def cleared(aura: int, seasons: int) -> tuple[int, int]:
    """Clearing a Lunar aura for `seasons`: (the aura left, the points of
    Lunar aura the moved matter makes elsewhere)."""
    left = max(0, aura - max(0, seasons))
    return left, aura - left


#: Each common duration: (whether it still works, what may replace it).
DURATIONS: dict[str, tuple[bool, str]] = {
    "Momentary": (True, ""),
    "Ring": (True, ""),
    "Concentration": (True, ""),
    "Diameter": (False, "The Burning of a Taper"),
    "Sun": (False, "At the Waking or the Sleeping"),
    "Moon": (False, "300 Miles"),
    "Year": (False, "The Weight of Years (a Ritual: until an Aging roll)"),
}
#: Breakthrough Points of each new duration (a Minor Breakthrough), and
#: of a new Parma Magica or Aegis of the Hearth.
DURATION_BREAKTHROUGH = 30
PARMA_BREAKTHROUGH = 60


def duration_works(duration: str) -> bool:
    """Whether a spell or device duration still works after the fall; one
    the table doesn't name is judged by the storyguide (True)."""
    return DURATIONS.get(duration, (True, ""))[0]


def replacement(duration: str) -> str:
    """The new duration magi may research for a failed one ("" if none)."""
    return DURATIONS.get(duration, (True, ""))[1]


def unformalized_magnitudes(magnitudes: int) -> int:
    """A replacement duration used before its breakthrough: one magnitude
    more than it would be."""
    return magnitudes + 1


def aura_text(aura: int) -> str:
    """What a Lunar aura does, as a place's facts say it ("" for none)."""
    if aura <= 0:
        return ""
    return (
        f"Lunar {aura}: Hermetic and Faerie powers {modifier('Magic', LUNAR, aura):+d}, "
        f"Infernal {modifier('Infernal', LUNAR, aura):+d}, Divine untouched; "
        "a season's clearing takes 1 away (the matter moved makes 1 "
        "elsewhere); since the fall, Diameter, Sun, Moon and Year fail "
        "everywhere, and Parma Magica and the Aegis with them"
    )
