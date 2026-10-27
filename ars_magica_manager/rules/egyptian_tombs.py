"""Tombs designed like covenants, and the traps, curses, talismans and
wards that guard them (Lands of the Nile), as plain rules.

- Traps (LotN pp. 32-33): when a trap springs, each character says one
  thing he does and rolls only for that, against the trap's base Ease
  Factor, which the storyguide moves by 3, 6 or more either way for the
  action. Actions go in Quickness order, but the character in danger is
  always first and the trap always last; those who fail and are not
  helped suffer the trap. A magus answers with a Fast-Cast spell, judged
  on its own and not against the trap's Ease Factor.
- Talismans and wards (pp. 35, 42): overcome without magic against
  6 + the effect's magnitude for a talisman that harms or imprisons, and
  9 + magnitude for a ward that repels or hides; anyone whose Magic
  Resistance is at least the enchantment's Penetration passes untouched.
  A magnitude is the level divided by five, rounded up (DE p. 213).
- Designing a tomb (p. 40): a burial ground's preternatural tether is 1
  a century of use, at most 5; the tomb's kind gives its base Magic aura
  and Build Points (a major monarch 5 and 500, a royal consort or minor
  monarch 4 and 250, a lesser royal or high priest 3 and 100, a non-royal
  dignitary 3 and 50); decay lowers the aura; up to 10 points of Hooks
  buy Boons. Other resources (inscriptions as a library, guardians and
  ghosts as specialists, vis) cost what a covenant's do (DE Chapter 6;
  LotN pp. 42, 44).
- Curses (pp. 34, 40-41): two Build Points for every five levels; a curse
  written without force costs nothing. One beyond Hermetic magic is a
  Lesser (base 10) or Greater (base 30) Malediction, of Special Duration
  (no magnitudes), lasting until dispelled and Warping its victims. A
  curse triggers when its condition is broken or its text is defaced;
  once it has struck its uses for the day, the text can be destroyed
  safely.
- Talismans and wards cost two Build Points for every five levels
  (p. 41). The book's examples round up: On Lowering the Waters, level
  28, costs 12 (p. 42).
- Traps (p. 44): 3 / 6 / 9 / 12 Build Points by harm (delay or scare;
  minor injury to +10 or imprisonment; serious injury to +15; often
  fatal, +20 or more), plus 0 / 1 / 3 / 6 / 9 for an Ease Factor to avoid
  of 3 / 6 / 9 / 12 / 15. Spotting a trigger first (Per + Awareness)
  gives time to deal with it; its Ease Factor assumes torches: -3 in
  perfect light, +3 by a single flame, +6 in near darkness.
- Magical craftwork (pp. 55-56): without Hedge Magic, amulets are
  designed as Hermetic items; with it, as Learned Magic. The colours of
  Egyptian amulets are flavour (`COLOURS`).

The errata (pp. 86-87) correct nothing on these pages, and the
Definitive Edition has no tomb rules of its own. The Tomb of Cleopatra
(p. 46) prints 6 Build Points for her fear curse, a CrMe 25 effect, where
the rule (p. 41) gives 10: the 6 fits a level-15 effect, so it is a
misprint, and the tomb's curses come to 42, not 38. The rule is followed
here."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

SOURCE = (
    "Lands of the Nile: traps, puzzles and magical defenses pp. 32-35; "
    "designing tombs and mortuaries pp. 40-46; magical craftwork pp. 55-56. "
    "Magnitude: ArM5 Definitive Edition p. 213."
)
L = "LotN"


@dataclass(frozen=True)
class TombKind:
    """What a tomb's kind gives: its base Magic aura and Build Points."""

    key: str
    name: str
    aura: int
    build_points: int


#: The kinds of tomb, greatest first (p. 40).
KINDS: dict[str, TombKind] = {
    k.key: k
    for k in (
        TombKind("major_monarch", "Tomb of a major monarch", 5, 500),
        TombKind("minor_monarch", "Tomb of a royal consort or minor monarch", 4, 250),
        TombKind("lesser_royal", "Tomb of a lesser royal or high priest", 3, 100),
        TombKind("dignitary", "Tomb of a non-royal dignitary", 3, 50),
    )
}
DEFAULT_KIND = "dignitary"

#: The most points of Hooks a tomb may have (p. 40).
MOST_HOOKS = 10
#: The highest tether a burial ground's centuries give (p. 40).
MOST_TETHER = 5


def kind(key: str) -> TombKind:
    """The tomb kind `key`; the least for one no longer known."""
    return KINDS.get(key) or KINDS[DEFAULT_KIND]


def tether_score(centuries: int) -> int:
    """A burial ground's preternatural tether: 1 a century of use, at
    most 5 (p. 40)."""
    return max(0, min(centuries, MOST_TETHER))


def tomb_aura(key: str, decay: int = 0) -> int:
    """The tomb's Magic aura: its kind's base, less what decay has taken
    (p. 40), never below 0."""
    return max(0, kind(key).aura - max(decay, 0))


# -- enchantments --


def magnitude(level: int) -> int:
    """An effect's magnitude: its level / 5, rounded up (DE p. 213)."""
    return max(0, -(-level // 5))


def enchantment_build_points(level: int) -> int:
    """Two Build Points for every five levels of effect, rounded up (pp.
    41-42)."""
    return 2 * magnitude(level)


#: The kinds of curse (pp. 40-41).
EFFECT = "Hermetic effect"
LESSER = "Lesser Malediction"
GREATER = "Greater Malediction"
HOLLOW = "Hollow (no force)"
CURSE_KINDS: tuple[str, ...] = (EFFECT, LESSER, GREATER, HOLLOW)
#: A Malediction's base level (p. 41).
MALEDICTION_BASE: dict[str, int] = {LESSER: 10, GREATER: 30}


def curse_build_points(curse_kind: str, level: int) -> int:
    """A curse's Build Points: two for every five levels; nothing for one
    written without force (p. 41)."""
    return 0 if curse_kind == HOLLOW else enchantment_build_points(level)


def curse_problem(curse_kind: str, level: int) -> str | None:
    """Why a curse's level can't be: below a Malediction's base, or no
    level for a curse with force."""
    if curse_kind == HOLLOW:
        return None
    base = MALEDICTION_BASE.get(curse_kind)
    if base is not None and level < base:
        return f"A {curse_kind} is at least level {base} (LotN p. 41)."
    if level < 1:
        return "A curse with force has a level; a hollow one costs nothing."
    return None


#: A talisman harms or imprisons; a ward repels or hides (p. 42).
TALISMAN, WARD = "Talisman", "Ward"
ENCHANTMENT_KINDS: tuple[str, ...] = (TALISMAN, WARD)
#: The base of the Ease Factor to overcome one without magic (pp. 35, 42).
OVERCOME_BASE: dict[str, int] = {TALISMAN: 6, WARD: 9}


def overcome_ease(enchantment_kind: str, level: int) -> int:
    """The Ease Factor to overcome a talisman or ward without magic: 6 or
    9 + the effect's magnitude (p. 42)."""
    return OVERCOME_BASE.get(enchantment_kind, OVERCOME_BASE[TALISMAN]) + magnitude(
        level
    )


def passes_untouched(magic_resistance: int | None, penetration: int) -> bool:
    """Whether a character's Magic Resistance (None: none at all) carries
    him past an enchantment of this Penetration without a roll (p. 42)."""
    return magic_resistance is not None and magic_resistance >= penetration


# -- traps --


@dataclass(frozen=True)
class Harm:
    """What a trap does to its victim, and its Build Points (p. 44)."""

    key: str
    name: str
    build_points: int


HARMS: dict[str, Harm] = {
    h.key: h
    for h in (
        Harm("scare", "Delay or scare, no harm", 3),
        Harm("minor", "Minor injury (to +10) or imprisonment", 6),
        Harm("serious", "Serious injury (to +15)", 9),
        Harm("fatal", "Often fatal (+20 or more)", 12),
    )
}

#: An Ease Factor to avoid a trap -> what it adds to its Build Points
#: (p. 44), and how the book names it.
AVOID: dict[int, int] = {3: 0, 6: 1, 9: 3, 12: 6, 15: 9}
AVOID_WORDS: dict[int, str] = {
    3: "simple",
    6: "easy",
    9: "average",
    12: "hard",
    15: "very hard",
}


def trap_build_points(harm: str, ease: int) -> int:
    """A trap's Build Points: its harm's, plus its Ease Factor's (p. 44)."""
    found = HARMS.get(harm)
    if found is None:
        raise ValueError(f"No trap harms as {harm!r}: one of {', '.join(HARMS)}.")
    if ease not in AVOID:
        raise ValueError(
            f"A trap's Ease Factor to avoid is one of {', '.join(map(str, AVOID))}."
        )
    return found.build_points + AVOID[ease]


#: The light the troupe carries -> what it adds to the Ease Factor of
#: spotting a trap's trigger, which assumes torches and lanterns (p. 44).
LIGHT: dict[str, int] = {
    "Torches or lanterns": 0,
    "Perfect light": -3,
    "A single flame": 3,
    "Near darkness": 6,
}


def spot_ease(base: int, light: str) -> int:
    """The Ease Factor of spotting a trigger (Per + Awareness) in this
    light (p. 44)."""
    return base + LIGHT.get(light, 0)


def action_ease(base: int, adjustment: int) -> int:
    """A character's Ease Factor against a trap: its base, moved by the
    storyguide for the action tried (p. 33)."""
    return base + adjustment


def action_order(actors: Sequence[tuple[str, int, bool]]) -> list[str]:
    """Who acts when a trap springs, each (name, Quickness, in danger):
    the one in danger first, then by Quickness, highest first; the trap
    acts after them all (p. 33). Ties keep the order given."""
    ranked = sorted(
        enumerate(actors), key=lambda pair: (not pair[1][2], -pair[1][1], pair[0])
    )
    return [actor[0] for _index, actor in ranked]


FAST_CAST = (
    "A magus answers with a Fast-Cast spell, judged on its own and not "
    f"against the trap's Ease Factor ({L} p. 33)."
)


# -- magical craftwork --


#: What the colour of an Egyptian amulet means (p. 55): flavour only.
COLOURS: dict[str, str] = {
    "Black": "the colour of magic",
    "Green": "widely used, perhaps because it draws faeries",
    "Blue": "invoking the gods",
    "Yellow, orange and some reds": "fire magic (one colour to an Egyptian)",
    "Red": "evil magic, Apep and Seth, controlling their servants, and curses",
}
