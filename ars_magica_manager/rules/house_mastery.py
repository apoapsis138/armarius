"""The Spell Mastery special abilities of the true lineages and the
societates, beyond the Definitive Edition's (rules.casting reads those):
House Mercere's (Houses of Hermes: True Lineages pp. 99-100: the Cult of
Mercury's Adaptive, Disguised, Lab Mastery, Learn From Mistakes and
Stalwart; the Mutantes' Boosted, Harnessed and Tethered; Ceremonial
Casting is the Definitive Edition's own). Societates (p. 33) reprints the
Mercurian ones; its Imperturbable, Obfuscated, Precise and Quick Casting
and its Fast Trigger for enchanted items are in the Definitive Edition
(pp. 226, 257), which the app follows.

Adaptive Casting follows the Errata (p. 46), which replaces True Lineages
p. 99's General-spells-only rule: the mastery's score and special
abilities serve whenever the magus casts a spell similar to the mastered
one (the Definitive Edition's Similar Spells, p. 260), and when two or more
masteries apply to one spell only one of them is used, its score with its
own abilities.

A teacher with the ability is needed for some of the xp (True Lineages p.
99); the app takes the troupe's word for it. Each is named on the spell as
typed, whatever its case."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from ..models import Spell
from .rounding import round_up

SOURCE = (
    "Houses of Hermes: True Lineages, Mercere, Mastered Spell Special Abilities, "
    "pp. 99-100; Houses of Hermes: Societates, Spell Mastery Special Abilities, "
    "p. 33; Errata p. 46; Ars Magica Definitive Edition, Obfuscated Casting, "
    "p. 226, Similar Spells, p. 260"
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


def problems(abilities: Mapping[str, int], *, ritual: bool) -> list[str]:
    """What the spell can't take of its abilities."""
    found = []
    if TETHERED in abilities and ritual:
        found.append("Tethered Casting can't be taken for a Ritual.")
    return found


def notes(abilities: Mapping[str, int], score: int, *, ritual: bool) -> list[str]:
    """What these special abilities do for the spell (plain text phrases,
    as rules.casting's are shown)."""
    found: list[str] = []
    if abilities.get(ADAPTIVE):
        found.append(
            "its Mastery and abilities serve on any similar spell cast, one "
            "mastery at a time (Errata p. 46)"
        )
    if abilities.get(BOOSTED):
        found.append(
            "+1 magnitude of Range, Duration, Target or size a pawn of vis, a "
            "botch die more each, cast at its own level (past Formulaic limits "
            "only for a Ritual; Errata p. 46)"
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


def similar(spell: Spell, other: Spell) -> bool:
    """Whether `other` is similar to `spell` (DE, Similar Spells, p. 260):
    the same Technique and Form, and the same effect (the same base level)
    at another Range, Duration or Target, or a related effect at the same
    Range, Duration and Target. The book leaves it to the troupe and says
    to be generous, so this is the generous reading."""
    if spell.id == other.id or (spell.technique, spell.form) != (
        other.technique,
        other.form,
    ):
        return False
    same_base = spell.base_level is not None and spell.base_level == other.base_level
    params = (spell.range, spell.duration, spell.target)
    return same_base or (
        all(params) and params == (other.range, other.duration, other.target)
    )


@dataclass(frozen=True)
class Adaptive:
    """A mastered spell with Adaptive Casting whose mastery may be used
    to cast a similar spell: its name, Mastery score and special abilities
    (by name, the times taken)."""

    name: str
    score: int
    abilities: Mapping[str, int]


def adaptive_masteries(
    spell: Spell, mastered: Sequence[tuple[Spell, int, Mapping[str, int]]]
) -> list[Adaptive]:
    """The masteries of `mastered` (each spell with its Mastery score and
    abilities) that Adaptive Casting lets the magus use when casting
    `spell`: those of similar spells (Errata p. 46). Only one of them, or
    the spell's own, serves for a casting: its score with its abilities."""
    return [
        Adaptive(other.name, score, abilities)
        for other, score, abilities in mastered
        if score > 0 and abilities.get(ADAPTIVE) and similar(spell, other)
    ]


def adaptive_note(own_score: int, options: Sequence[Adaptive]) -> str:
    """The casting line for the masteries Adaptive Casting offers on a
    spell: one at a time, never added together (Errata p. 46)."""
    if not options:
        return ""

    def described(option: Adaptive) -> str:
        names = ", ".join(
            name.title() + (f" x{times}" if times > 1 else "")
            for name, times in option.abilities.items()
        )
        return f"{option.name}'s (score {option.score}: {names})"

    instead = " instead of its own" if own_score else ""
    return (
        "Adaptive Casting: it may be cast with the mastery of a similar spell"
        f"{instead}, "
        + " or ".join(described(o) for o in options)
        + "; only one mastery's score and abilities serve a casting (Errata p. 46)."
    )
