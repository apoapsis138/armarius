"""Mythic Locations' Temple of Mercury: the recovered Mercurian rituals.

- Reading (p. 96-97): anyone who reads Latin and has a Magic Theory score
  learns a Mercurian Lab Text's Arts, magnitude and gist in a day; that
  reading can't be cast or invented from.
- Translating (p. 97): a laboratory season adds the Lab Total in the
  ritual's Arts less its level; at twice the level the text is a Hermetic
  copy (so a Lab Total of three times the level does it in one season).
  Each translated ritual adds the highest magnitude translated so far to
  later translations (not to invention). Experimenting is allowed.
- Inventing (p. 97): from the Hermetic copy by the usual Lab Text rule
  (DE p. 262: one season when the Lab Total at least equals the level),
  exactly as written: Range, Duration and Target can't be changed. Any
  magus with the copy may invent it.
- Casting (p. 97): as Hermetic Rituals of their Arts (so a Ritual's vis,
  rules.casting_virtues.ritual_vis), dispelled as Hermetic, plainly
  non-Hermetic to anyone with Magic Theory.
- The rituals' own rules (pp. 97-100): Purification (its up to five
  Aging Points come off the Characteristics the player chooses, as the
  DE leaves that choice to the player too, DE pp. 391-392; most points
  first is only the default), Raising the
  Auxiliaries, Penetrate the Regio Skin, Blessing of Mercury,
  Transformation of Flesh to Spirit, Wizard's Initiation (it never works),
  Consecration of Mercury's House.
- The aqueduct that fills the Scrying Pool and the baths (p. 96): repair,
  upkeep and the Aquam vis source (p. 97).

The DE's own rule for decoding another magus's Lab Texts (DE p. 263: the
whole Lab Total a season, done at the level) is for a magus's
abbreviations; Mythic Locations gives the Mercurian texts this harder rule
of their own, and the app follows it for them.

Pattern: the rituals are spell catalog data (data/spell_catalog.json,
source "ML") read by these plain functions; the integrations they open
are rows in rules.integrations.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from ..arts import ARTS
from ..models import Character, Spell
from . import aging
from .lab import ability_score, lab_text_usable, points_per_season
from .powers import magnitude
from .rounding import round_up

SOURCE = (
    "Mythic Locations, The Temple of Mercury, pp. 96-101 (the Mercurian "
    "rituals and the aqueduct); Ars Magica Definitive Edition, Laboratory "
    "Texts pp. 262-263, Mercurian Magic p. 98"
)

#: The recovered rituals in the spell catalog (ML pp. 97-100). The
#: Wizard's Communion "rituals" (p. 100) are the DE's own spell.
RITUAL_IDS: tuple[str, ...] = (
    "spell_purification",
    "spell_the_scrying_pool",
    "spell_raising_the_auxiliaries_for_a_day",
    "spell_penetrate_the_regio_skin",
    "spell_blessing_of_mercury",
    "spell_transformation_of_flesh_to_spirit",
    "spell_wizard_s_initiation",
    "spell_consecration_of_mercury_s_house",
    "spell_commune_with_mercury",
)
PURIFICATION = "spell_purification"
TRANSFORMATION = "spell_transformation_of_flesh_to_spirit"
WIZARDS_INITIATION = "spell_wizard_s_initiation"
CONSECRATION = "spell_consecration_of_mercury_s_house"
#: The rituals cast only in a consecrated temple of Mercury.
NEED_TEMPLE: tuple[str, ...] = (
    PURIFICATION,
    "spell_raising_the_auxiliaries_for_a_day",
    "spell_blessing_of_mercury",
    TRANSFORMATION,
    WIZARDS_INITIATION,
    "spell_commune_with_mercury",
)

LATIN = "Dead Language: Latin"
MAGIC_THEORY = "Magic Theory"


def is_mercurian(spell: Spell | None) -> bool:
    return spell is not None and spell.id in RITUAL_IDS


# -- reading, translating, inventing (p. 97) -------------------------------

#: Days to read one Mercurian Lab Text for its gist.
READING_DAYS = 1
#: A translation is done at this many times the ritual's level.
TRANSLATION_FACTOR = 2


def can_read(character: Character) -> bool:
    """Whether `character` can read a Mercurian Lab Text for its gist:
    Latin and a Magic Theory score."""
    return (
        ability_score(character, LATIN)[0] > 0
        and ability_score(character, MAGIC_THEORY)[0] > 0
    )


def translation_bonus(translated_levels: Iterable[int]) -> int:
    """The bonus to a translation's Lab Total: the highest magnitude of the
    Mercurian rituals already translated (0 for the first)."""
    return max((magnitude(level) for level in translated_levels), default=0)


def translation_points(lab_total: int, level: int, bonus: int = 0) -> int:
    """The points a season of translating adds: the Lab Total (with the
    bonus for rituals already translated) less the ritual's level."""
    return points_per_season(lab_total + bonus, level)


def points_needed(level: int) -> int:
    return TRANSLATION_FACTOR * level


def seasons_to_translate(lab_total: int, level: int, bonus: int = 0) -> int | None:
    """Seasons to translate a ritual's text at a steady Lab Total, or None
    when the total isn't above the level."""
    points = translation_points(lab_total, level, bonus)
    if points <= 0:
        return None
    return round_up(points_needed(level) / points)


@dataclass(frozen=True)
class Translation:
    points: int
    gained: int
    finished: bool


def translate_season(
    points_before: int, lab_total: int, level: int, bonus: int = 0
) -> Translation:
    """One season of translating: the points after it, those it added, and
    whether the Hermetic copy is done."""
    gained = translation_points(lab_total, level, bonus)
    points = points_before + gained
    return Translation(points, gained, points >= points_needed(level))


def can_invent(lab_total: int, level: int) -> bool:
    """Inventing from the translated copy, a Lab Text: one season when the
    Lab Total at least equals the level, with nothing about it changed."""
    return lab_text_usable(lab_total, level)


# -- Purification, CrCo 40 (pp. 97-98) -------------------------------------

PURIFIED_YEARS = 5
PURIFIED_AGING_POINTS = 5


def purification_problems(caster: Character, target: Character) -> list[str]:
    """Why Purification can't be cast on `target` (empty when it can)."""
    problems: list[str] = []
    if caster.id == target.id:
        problems.append("The caster can't cast Purification on himself.")
    if target.aging.decrepitude < 1:
        problems.append(f"{target.name} has no Decrepitude: the ritual does nothing.")
    return problems


def purification_choice_problem(
    target: Character, taken_from: Mapping[str, int]
) -> str:
    """Why `taken_from` (Characteristic -> Aging Points taken off it) isn't
    a choice Purification allows ("" if it is): at most five in all, and
    no more off a Characteristic than it has."""
    points = target.aging.aging_points
    if any(n < 0 for n in taken_from.values()):
        return "Aging Points taken off can't be negative."
    if sum(taken_from.values()) > PURIFIED_AGING_POINTS:
        return f"Purification takes off at most {PURIFIED_AGING_POINTS} Aging Points."
    for name, n in taken_from.items():
        if n > points.get(name, 0):
            return (
                f"{name.capitalize()} has only {points.get(name, 0)} Aging "
                f"Point(s) to take off."
            )
    return ""


def default_purification(target: Character) -> dict[str, int]:
    """The default choice of where Purification's Aging Points come off:
    the Characteristics with the most first."""
    points = target.aging.aging_points
    chosen: dict[str, int] = {}
    left = PURIFIED_AGING_POINTS
    for name in sorted(points, key=lambda n: -points[n]):
        taken = min(left, points[name])
        if left <= 0:
            break
        if taken > 0:
            chosen[name] = taken
            left -= taken
    return chosen


def purify(
    target: Character,
    age: int | None,
    taken_from: Mapping[str, int] | None = None,
) -> list[str]:
    """Purification's effect: Decrepitude down a score, apparent age down
    five years, and up to five Aging Points off the Characteristics the
    player chooses (`taken_from`, Characteristic -> points; the book sets
    no order, so None takes them off those with the most first). The real
    age, and so the aging roll, is unchanged. Returns what changed; raises
    ValueError for a choice the ritual doesn't allow."""
    record = target.aging
    if record.decrepitude < 1:
        return []
    chosen = default_purification(target) if taken_from is None else taken_from
    if why := purification_choice_problem(target, chosen):
        raise ValueError(why)
    score = record.decrepitude - 1
    record.decrepitude = score
    record.decrepitude_points = aging.points_for_score(score)
    changes = [f"Decrepitude {score + 1} -> {score}."]
    seen = record.apparent_age if record.apparent_age is not None else age
    if seen is not None:
        record.apparent_age = max(0, seen - PURIFIED_YEARS)
        changes.append(f"Looks {record.apparent_age} (was {seen}).")
    for name, taken in chosen.items():
        if taken <= 0:
            continue
        record.aging_points[name] -= taken
        changes.append(f"{taken} Aging Point(s) off {name.capitalize()}.")
    return changes


# -- the other rituals (pp. 98-100) ----------------------------------------

#: Raising the Auxiliaries for a Day: +1 Attack and Defense to up to 100,
#: fighting as trained groups; it doesn't stack.
AUXILIARIES_BONUS = 1
AUXILIARIES_MAX = 100
#: Penetrate the Regio Skin: Dex + Finesse against 6 to place the opening.
REGIO_SKIN_EASE = 6
#: Blessing of Mercury: +3 to every Casting and Lab Total for a year.
BLESSING_BONUS = 3
#: Transformation of Flesh to Spirit raises an aura to at most 10.
AURA_CAP = 10
#: Recognizing Trianoma's sacrifice in it: Int + Order of Hermes Lore.
TRIANOMA_EASE = 3
#: Wizard's Initiation never works, and adds a botch die.
INITIATION_BOTCH_DICE = 1
#: Consecration: an Intellego Vim effect of the eleventh magnitude finds
#: (and a Perdo Vim one may dispel) the consecration; everyone with Faith
#: Points inside loses one.
CONSECRATION_LEVEL = 55
CONSECRATION_FAITH_LOSS = 1


def regio_skin_placed(dexterity: int, finesse: int, roll: int) -> bool:
    return dexterity + finesse + roll >= REGIO_SKIN_EASE


def transformation_problems(
    leader: Character, aura: int, penetration: int
) -> list[str]:
    """Why Transformation of Flesh to Spirit leaves the aura as it is
    (empty when it rises by one): every Art of the leader at least twice
    the aura, a Penetration above five times it, and the aura under 10."""
    problems: list[str] = []
    if aura >= AURA_CAP:
        problems.append(f"The aura is already {AURA_CAP}, the most it can reach.")
    low = [art for art in ARTS if _art(leader, art) < 2 * aura]
    if low:
        problems.append(f"Arts under twice the aura ({2 * aura}): {', '.join(low)}.")
    if penetration <= 5 * aura:
        problems.append(f"Penetration {penetration} isn't above {5 * aura}.")
    return problems


def transformation_aura(leader: Character, aura: int, penetration: int) -> int:
    """The aura after the ritual (the caster dies either way)."""
    if transformation_problems(leader, aura, penetration):
        return aura
    return aura + 1


def _art(magus: Character, art: str) -> int:
    score = magus.arts.get(art.lower())
    return score.level if score else 0


def initiation_works() -> bool:
    """Wizard's Initiation fails whatever the Casting Total (p. 101: it
    stopped working with the Age of Pisces)."""
    return False


def consecrated_aura(magic_aura: int) -> int:
    """The temple's Magic aura after the Consecration: 1 where it had
    none; one it already had isn't raised. It can't be dispelled."""
    return max(1, magic_aura)


# -- the aqueduct (p. 96) and its vis (p. 97) ------------------------------

#: Repair: 20 man-years at two seasons a year.
AQUEDUCT_REPAIR_SEASONS = 40
#: Upkeep: five workers every season, or the season counts as neglected.
AQUEDUCT_WORKERS = 5
#: Catching up costs one man-year a neglected season, at most the repair.
AQUEDUCT_CATCH_UP_SEASONS = 2
#: The spring's Aquam vis, collected at dawn on the Summer solstice.
AQUEDUCT_VIS = 5


def neglect_ease(seasons_neglected: int) -> int:
    """The simple die's Ease Factor against the aqueduct clogging at the
    end of a season without upkeep: 3 + each season in a row neglected."""
    return 3 + max(0, seasons_neglected)


def clogs(roll: int, seasons_neglected: int) -> bool:
    return seasons_neglected > 0 and roll < neglect_ease(seasons_neglected)


def catch_up_seasons(seasons_neglected: int) -> int:
    """Worker-seasons of repair, on top of the upkeep, before the water
    flows again."""
    return min(
        AQUEDUCT_REPAIR_SEASONS,
        AQUEDUCT_CATCH_UP_SEASONS * max(0, seasons_neglected),
    )


# -- the spell's details panel ---------------------------------------------


def spell_lines(spell: Spell) -> list[str]:
    """What the details panel adds for a Mercurian ritual (plain text)."""
    if not is_mercurian(spell) or spell.level is None:
        return []
    level = spell.level
    lines = [
        f"Mercurian ritual (Mythic Locations p. 97): translate its Lab Text "
        f"first, in a laboratory: each season adds the Lab Total less {level}, "
        f"done at {points_needed(level)} points (one season at a Lab Total of "
        f"{3 * level}). Earlier translations add their highest magnitude. "
        "Then invent it from the copy as a Lab Text, exactly as written.",
    ]
    if spell.id in NEED_TEMPLE:
        lines.append("Cast only in a temple consecrated to Mercury.")
    if spell.id == WIZARDS_INITIATION:
        lines.append("It never works, and adds a botch die (Mythic Locations p. 101).")
    return lines
