"""The Spell Mastery special abilities of the true lineages and the
societates, beyond the Definitive Edition's (rules.casting reads those):
House Mercere's (Houses of Hermes: True Lineages pp. 99-100: the Cult of
Mercury's Adaptive, Disguised, Lab Mastery, Learn From Mistakes and
Stalwart; the Mutantes' Boosted, Harnessed and Tethered; Ceremonial
Casting is the Definitive Edition's own). Societates (p. 33) reprints the
Mercurian ones; its Imperturbable, Obfuscated, Precise and Quick Casting
and its Fast Trigger for enchanted items are in the Definitive Edition
(pp. 226, 257), which the app follows.

A teacher with the ability is needed for some of the xp (True Lineages p.
99); the app takes the troupe's word for it. Each is named on the spell as
typed, whatever its case."""

from __future__ import annotations

from collections.abc import Mapping

from .rounding import round_up

SOURCE = (
    "Houses of Hermes: True Lineages, Mercere, Mastered Spell Special Abilities, "
    "pp. 99-100; Houses of Hermes: Societates, Spell Mastery Special Abilities, "
    "p. 33; Ars Magica Definitive Edition, Obfuscated Casting, p. 226"
)

ADAPTIVE = "adaptive casting"
BOOSTED = "boosted casting"
DISGUISED = "disguised casting"
HARNESSED = "harnessed casting"
LAB_MASTERY = "lab mastery"
LEARN_FROM_MISTAKES = "learn from mistakes"
STALWART = "stalwart casting"
TETHERED = "tethered casting"
OBFUSCATED = "obfuscated casting"

#: Who teaches each (a magus may learn them only from one who has it).
TAUGHT_BY: dict[str, str] = {
    ADAPTIVE: "Cult of Mercury",
    DISGUISED: "Cult of Mercury",
    LAB_MASTERY: "Cult of Mercury",
    LEARN_FROM_MISTAKES: "Cult of Mercury",
    STALWART: "Cult of Mercury",
    BOOSTED: "Mutantes",
    HARNESSED: "Mutantes",
    TETHERED: "Mutantes",
}
#: Learn From Mistakes: the xp toward Mastery, once a session.
MISTAKE_XP = 5


def stalwart_ritual_fatigue(levels: int) -> int:
    """Stalwart Casting on a Ritual: half the Fatigue levels, rounded up,
    at least one, and short-term rather than long-term."""
    return max(1, round_up(levels / 2)) if levels > 0 else 0


def problems(abilities: Mapping[str, int], *, ritual: bool, general: bool) -> list[str]:
    """What the spell can't take of its abilities."""
    found = []
    if ADAPTIVE in abilities and not general:
        found.append("Adaptive Casting is for General spells only.")
    if TETHERED in abilities and ritual:
        found.append("Tethered Casting can't be taken for a Ritual.")
    return found


def notes(
    abilities: Mapping[str, int], score: int, *, ritual: bool, general: bool
) -> list[str]:
    """What these special abilities do for the spell (plain text phrases,
    as rules.casting's are shown)."""
    found: list[str] = []
    if abilities.get(ADAPTIVE) and general:
        found.append("its Mastery and abilities at any level of it")
    if abilities.get(BOOSTED):
        found.append(
            "+1 magnitude of Range, Duration or Target a pawn of vis (Year or "
            "Boundary only for a Ritual)"
        )
    if abilities.get(DISGUISED):
        found.append(f"sigil hidden or mimicked (+{score} to pass for another's)")
    if abilities.get(HARNESSED):
        found.append("ended at will by concentrating")
    if abilities.get(LAB_MASTERY):
        found.append(f"+{score} to Lab Totals for similar effects")
    if abilities.get(LEARN_FROM_MISTAKES):
        found.append(f"+{MISTAKE_XP} Mastery xp the first botch or one-short a session")
    if abilities.get(STALWART):
        found.append(
            "half the Fatigue, short-term (a Ritual)"
            if ritual
            else "no Fatigue for a low total"
        )
    if abilities.get(TETHERED) and not ritual:
        found.append("control given to another, or held in an object")
    if abilities.get(OBFUSCATED):
        found.append(f"its Form harder to tell (+{score} to the Ease Factor)")
    return found
