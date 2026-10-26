"""An apprentice's magic and the end of his apprenticeship, from
Apprentices (Chapter Five: Adulescentia), while that book is in play:

- **Cantations** (pp. 44-48): low-level formulaic spells an apprentice is
  taught, by the Definitive Edition's Learning Spells from a Teacher (DE
  p. 251, which the season of Learn Spells already applies: the levels at
  most the parens' highest Lab Total, each spell at most the apprentice's
  own). The optional rule (p. 46, a saga option): a spontaneous spell cast
  at least as many times as its level may be bought as a formulaic spell
  with that adventure's experience, one point a level; by adult magi too,
  and with no level cap (none in the book). Never a Ritual: spontaneous
  magic never replicates a Ritual's effect (DE p. 311).
- **Failing an apprentice** (pp. 58-59): losing the Gift, always the
  player's choice. Lost for good, the Gift goes and Failed Apprentice (a
  Minor Social Status, DE p. 80) replaces Apprentice; suppressed, the
  character gains the Major Hermetic Flaw Suppressed Gift and keeps his
  Supernatural Virtues and Abilities.
- **The Gauntlet** (pp. 59-61): the parens' test, passed at his
  satisfaction; failed, another year as an apprentice; after three
  failures the Quaesitores set one of their own. Keeping an apprentice
  more than 20 years is a low crime in many Tribunals, punished by an
  instant Gauntlet and a rook of vis (10 pawns, DE p. 212) for each year
  past 15. Instead of a story, an apprentice who has served his seasons
  may simply pass, or roll Intelligence + an Ability fitting his House +
  stress die against 9 (a botch: something dire). Parma Magica's final
  key is given only after the Oath (DE p. 169): until then his score in
  it gives no Magic Resistance.

Pattern: plain functions; the More forms (forms.gauntlet) keep the result.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .. import catalog
from ..models import Character, Saga, VirtueFlawInstance
from . import childhood, dice, options
from .creation_character import DEFAULT_APPRENTICESHIP_AGE, age
from .scores import ability_level

SOURCE = (
    "Apprentices, Chapter Five: Adulescentia, Apprenticeship's End: The Gauntlet, "
    "pp. 59-61"
)
FAILING_SOURCE = (
    "Apprentices, Chapter Five: Adulescentia, Failing an Apprentice and Losing "
    "the Gift, pp. 58-59"
)
CANTATION_SOURCE = (
    "Apprentices, Chapter Four: Pueritia, Cantations, pp. 44-48 (Optional Rule: "
    "Learning Cantations in Play, p. 46)"
)

#: The option that lets a spontaneous spell become a formulaic one.
CANTATIONS_IN_PLAY = "cantations_in_play"

APPRENTICE_IDS = frozenset({"vf_apprentice", "vf_apprentice_rhine_tribunal"})
FAILED_APPRENTICE = "vf_failed_apprentice"
SUPPRESSED_GIFT = "vf_suppressed_gift"
HERMETIC_MAGUS = "vf_hermetic_magus"
#: What goes with the Gift when it is lost for good.
GIFT_VIRTUES = catalog.GIFT_IDS | {"vf_gentle_gift", "vf_blatant_gift"}

#: The optional roll's Ease Factor (p. 60).
GAUNTLET_EASE = 9
#: Failed Gauntlets before the Quaesitores set one (p. 60).
QUAESITOR_AFTER = 3
#: An apprenticeship's usual length, and the years past which keeping an
#: apprentice is a low crime (p. 60).
APPRENTICESHIP_YEARS = 15
KEPT_TOO_LONG = 20
#: Pawns in a rook of vis (DE p. 212).
ROOK = 10

#: Diary entries the Gauntlet writes.
PASSED = "The Gauntlet passed"
FAILED = "The Gauntlet failed"

#: How the Gauntlet is decided (p. 60).
STORY, AUTOMATIC, ROLLED = "story", "automatic", "rolled"
METHODS: dict[str, str] = {
    STORY: "Played as a story: the parens judges it",
    AUTOMATIC: "Passed without a story (the seasons of study served)",
    ROLLED: "Rolled: Intelligence + an Ability + stress die against 9",
}
#: A story's verdict.
PASS, FAIL = "pass", "fail"

#: Losing the Gift (p. 59).
LOST, SUPPRESSED = "lost", "suppressed"
LOSSES: dict[str, str] = {
    LOST: "Lost for good: Failed Apprentice replaces Apprentice",
    SUPPRESSED: "Suppressed: the Major Hermetic Flaw Suppressed Gift",
}


def in_play(saga: Saga | None) -> bool:
    return childhood.in_play(saga)


def _ids(character: Character) -> set[str]:
    return {vf.vf_id for vf in character.virtues_flaws}


def apprentice(character: Character) -> bool:
    """Whether the character holds the Apprentice Social Status."""
    return bool(_ids(character) & APPRENTICE_IDS)


def gifted(character: Character) -> bool:
    return childhood.gifted(character)


def years_served(saga: Saga, character: Character) -> int | None:
    """Years since the apprenticeship began (at the age the sheet gives,
    or 10); None with no age."""
    years = age(saga, character)
    if years is None:
        return None
    start = character.hermetic.age_of_apprenticeship
    start = start if start is not None else DEFAULT_APPRENTICESHIP_AGE
    return max(0, years - start)


def failures(character: Character) -> int:
    """Gauntlets failed so far, as the Diary records them."""
    return sum(1 for entry in character.diary if entry.name == FAILED)


def kept_too_long(served: int | None) -> bool:
    return served is not None and served > KEPT_TOO_LONG


def punishment_pawns(served: int | None) -> int:
    """A rook of vis for each year past 15, owed by a parens convicted of
    keeping his apprentice too long (p. 60)."""
    if served is None:
        return 0
    return ROOK * max(0, served - APPRENTICESHIP_YEARS)


def gauntlet_notes(saga: Saga, character: Character) -> list[str]:
    """What the apprenticeship's length and past failures say."""
    served = years_served(saga, character)
    lines: list[str] = []
    if served is not None:
        lines.append(f"{served} years an apprentice.")
        if kept_too_long(served):
            lines.append(
                f"More than {KEPT_TOO_LONG} years: a low crime in many Tribunals; "
                "convicted, the parens forgoes the Gauntlet and pays "
                f"{punishment_pawns(served)} pawns (a rook a year past "
                f"{APPRENTICESHIP_YEARS})."
            )
    failed = failures(character)
    if failed >= QUAESITOR_AFTER:
        lines.append(
            f"{failed} Gauntlets failed: a Quaesitor sets this one, overriding "
            "the parens."
        )
    elif failed:
        lines.append(f"{failed} failed before.")
    return lines


def roll_base(character: Character, ability: str) -> int:
    return character.characteristics.intelligence + ability_level(character, ability)


@dataclass(frozen=True)
class Verdict:
    passed: bool
    botched: bool = False
    line: str = ""


def rolled(
    saga: Saga, character: Character, ability: str, rng: random.Random
) -> Verdict:
    """The optional roll: Intelligence + the Ability + stress die against 9."""
    base = roll_base(character, ability)
    roll = dice.roll(rng, base, ease_factor=GAUNTLET_EASE, saga=saga)
    if roll.die.botched:
        return Verdict(
            False,
            True,
            f"Intelligence + {ability} {base:+d}: botched. Something dire "
            "happened on the Gauntlet.",
        )
    return Verdict(
        bool(roll.succeeded),
        False,
        f"Intelligence + {ability} {base:+d} + {roll.die.value} = {roll.total} "
        f"against {GAUNTLET_EASE}: " + ("passed." if roll.succeeded else "failed."),
    )


def pass_gauntlet(character: Character) -> list[str]:
    """He becomes a magus: Hermetic Magus replaces Apprentice, and the
    final key of Parma Magica is his once he swears the Oath."""
    character.virtues_flaws = [
        vf for vf in character.virtues_flaws if vf.vf_id not in APPRENTICE_IDS
    ]
    if HERMETIC_MAGUS not in _ids(character):
        character.virtues_flaws.append(VirtueFlawInstance(HERMETIC_MAGUS))
    character.type = "magus"
    parma = ability_level(character, "Parma Magica")
    return [
        "Hermetic Magus replaces Apprentice: he swears the Oath of Hermes and "
        "is given Parma Magica's final key"
        + (f" (Parma Magica {parma} now protects him)." if parma else "."),
    ]


def fail_gauntlet(character: Character) -> list[str]:
    failed = failures(character) + 1
    return [
        "Another year as an apprentice before he tries again"
        + (
            "; after this, the Quaesitores set his Gauntlet."
            if failed >= QUAESITOR_AFTER
            else "."
        )
    ]


def lose_gift(character: Character, how: str) -> list[str]:
    """The Gift lost for good or suppressed (p. 59)."""
    if how == SUPPRESSED:
        if SUPPRESSED_GIFT not in _ids(character):
            character.virtues_flaws.append(VirtueFlawInstance(SUPPRESSED_GIFT))
        return [
            "Suppressed Gift: no Hermetic magic, no new Supernatural or Hermetic "
            "Virtues while it lasts; his Supernatural Virtues and Abilities still "
            "work. How it returns is the troupe's story."
        ]
    was_apprentice = apprentice(character)
    character.virtues_flaws = [
        vf
        for vf in character.virtues_flaws
        if vf.vf_id not in GIFT_VIRTUES and vf.vf_id not in APPRENTICE_IDS
    ]
    if was_apprentice and FAILED_APPRENTICE not in _ids(character):
        character.virtues_flaws.append(VirtueFlawInstance(FAILED_APPRENTICE))
    # A magus's record counts as Gifted by its type: without the Gift he
    # goes on as a companion.
    if character.type == "magus":
        character.type = "companion"
    return [
        "The Gift is gone: no spells, no magic of any kind, and his Supernatural "
        "Virtues and Abilities no longer work."
        + (" Failed Apprentice replaces Apprentice." if was_apprentice else "")
    ]


def parma_withheld(character: Character) -> bool:
    """An apprentice's Parma Magica gives no Magic Resistance before the
    final key, given after the Oath (DE p. 169; Apprentices p. 61)."""
    return apprentice(character)


# -- cantations learned in play --


def cantations_in_play(saga: Saga | None) -> bool:
    return options.is_on(saga, CANTATIONS_IN_PLAY)


def cantation_problem(level: int, times_cast: int, known: bool) -> str | None:
    """Why a spontaneous spell can't become formulaic (None: it can)."""
    if known:
        return "He knows that spell already."
    if level < 1:
        return "Give the spell's level."
    if times_cast < level:
        return (
            f"Cast at least {level} times (its level) to learn it this way; "
            f"{times_cast} so far."
        )
    return None


def cantation_cost(level: int) -> int:
    """Adventure experience spent: one point a level (p. 46)."""
    return max(0, level)
