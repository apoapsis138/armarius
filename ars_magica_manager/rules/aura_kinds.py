"""An aura's kind: what sets one aura apart from another of its realm and
strength, and what that does to those inside it.

Each realm's kind is one field of the place (its surface) or of a regio
level, named by `KIND_KEYS`, the lookup the rest of the rules read:

- **Magic: an alignment** (RoP: Magic pp. 15-16). No aura has more than
  one. Aligned with an Art, the aura's strength counts again in the
  Casting Score of a spell using that Art (as Technique, Form or
  requisite) and in a Lab Total of that Art, and a creature whose Might is
  of that Form pays a Might Point less for a power that costs any; an
  opposed Art takes no penalty. Aligned with Healing, half the aura
  (rounded up) adds to Recovery Totals for wounds and disease; with Luck,
  +1 (+2 from 5 to 8, +3 above) to rolls where luck matters, for all;
  Distracting, Concentration rolls come more often and from 5 their Ease
  Factors are 3 higher. Any other alignment is a feeling (Aggressive,
  Carefree, Fearful...): after a few minutes there, those without a Magic
  power (The Gift) take it as a temporary Personality Trait, or a change
  to one, of +1 (aura 1-3), +2 (4-6) or +3 (7-10), never to an Essential
  Trait (the Aura Effect Table, p. 15). Up to 5 such auras are safe to
  live in; above it those living there without a Magic power slowly warp.
  An Intellego Vim spell of level 4 discerns an alignment (p. 14).
- **Faerie: its tints** (RoP: Faerie p. 104), "Drawn to Children +3;
  Light +2". Everyone in the aura takes each as a temporary Personality
  Trait, which cannot exceed the aura. Tinting is a ceremony (fading a
  point a day) or a season's influence (a point a season): stress die +
  Presence + Concentration against 3 x the Trait's value (up to 10), and
  never above the tinter's Sympathy Trait. Some auras are tinted for good.
- **Divine: Dominion or Empyreal** (RoP: The Divine pp. 7-12). The two
  work alike in play; they differ in source (p. 12: no difference, system
  wise). Both wane and wax: one less at night, one more on Sundays and
  holy days (p. 7 for Divine auras as a whole, the numbers p. 10; DE
  p. 418), and both hold sway over another realm's aura of the same
  strength (p. 11). The Dominion comes from worship; an Empyreal aura
  from no congregation: a person
  or relic of 5 or more Faith Points, a miracle (1 per five levels above
  45, while its effect lasts), or a holy creature's home (1 more each
  season it dwells there, up to its Might / 10; pp. 12-13). Mundane folk
  are moved by a Divine aura (the pious to love and awe, the sinful to
  guilt; the Gifted feel their Gift falter, pp. 8-9), which the rules
  leave to the troupe.

Pattern: a dict lookup (realm -> the field its kind is kept in), and
plain functions; the effects are Breakdown Lines where an aura counts.
"""

from __future__ import annotations

import re
from typing import Any

from ..arts import FORMS, TECHNIQUES
from .breakdown import Line
from .rounding import round_up

ALIGNED_SOURCE = "Realms of Power: Magic, Aligned Auras, pp. 15-16"
TINT_SOURCE = "Realms of Power: Faerie, Tinted Auras, p. 104"
EMPYREAL_SOURCE = (
    "Realms of Power: The Divine, Divine Auras in Play, The Dominion and "
    "Empyreal Auras, pp. 7-13"
)
SOURCE = f"{ALIGNED_SOURCE}; {TINT_SOURCE}; {EMPYREAL_SOURCE}"

#: The field each realm's kind is kept in, on a place's details or a regio
#: level. A realm not here has no kind.
KIND_KEYS: dict[str, str] = {
    "Magic": "alignment",
    "Faerie": "tints",
    "Divine": "divine_kind",
}

ARTS: tuple[str, ...] = (*TECHNIQUES, *FORMS)

#: The alignments that are neither an Art nor a feeling, by the word kept.
HEALING, LUCK, DISTRACTING = "Healing", "Luck", "Distracting"
OTHER_ALIGNMENTS: dict[str, str] = {
    "healing": HEALING,
    "luck": LUCK,
    "lucky": LUCK,
    "distracting": DISTRACTING,
}
#: The feelings the book gives as examples (any other Trait may be one).
FEELINGS: tuple[str, ...] = ("Aggressive", "Carefree", "Communicative", "Respectful")

#: Above this an aligned aura warps those who live in it without a Magic
#: power (p. 15).
SAFE_ALIGNED = 5
#: From this, a Distracting aura raises Concentration Ease Factors by
#: DISTRACTING_EASE.
DISTRACTING_FROM = 5
DISTRACTING_EASE = 3

DOMINION, EMPYREAL = "Dominion", "Empyreal"
DIVINE_KINDS: tuple[str, ...] = (DOMINION, EMPYREAL)
#: People and relics radiate an Empyreal aura from this many Faith Points.
EMPYREAL_FAITH = 5

#: The highest a tint can be.
MOST_TINT = 10


def kind_of(details: dict[str, Any], realm: str) -> str:
    """The kind of an aura of `realm` kept in `details` (a place's details
    or a regio level), "" when its realm has none or none is set."""
    key = KIND_KEYS.get(realm)
    return str(details.get(key) or "").strip() if key else ""


# -- Magic: alignment --


def aligned_art(alignment: str) -> str:
    """The Art an alignment names ("" for any other alignment)."""
    wanted = alignment.strip().casefold()
    return next((a for a in ARTS if a.casefold() == wanted), "")


def alignment_kind(alignment: str) -> str:
    """ "art", the other alignment's name (Healing, Luck, Distracting),
    "feeling", or "" for none."""
    if not alignment.strip():
        return ""
    if aligned_art(alignment):
        return "art"
    return OTHER_ALIGNMENTS.get(alignment.strip().casefold(), "feeling")


def feeling_adjustment(aura: int) -> int:
    """The Aura Effect Table: +1 (1-3), +2 (4-6), +3 (7 and more)."""
    if aura <= 0:
        return 0
    return 1 if aura <= 3 else 2 if aura <= 6 else 3


def luck_bonus(aura: int) -> int:
    """A lucky aura's bonus: +1, +2 from 5 to 8, +3 above."""
    if aura <= 0:
        return 0
    return 1 if aura < 5 else 2 if aura <= 8 else 3


def healing_bonus(aura: int) -> int:
    """A healing aura's Recovery Total bonus: half the aura, rounded up."""
    return round_up(max(0, aura) / 2)


def distracting_ease(aura: int) -> int:
    """What a Distracting aura adds to Concentration Ease Factors."""
    return DISTRACTING_EASE if aura >= DISTRACTING_FROM else 0


def art_bonus(alignment: str, realm: str, aura: int, arts: tuple[str, ...]) -> int:
    """What an Art-aligned Magic aura adds again to a total using `arts`:
    the aura's strength, when one of them is its Art."""
    art = aligned_art(alignment) if realm == "Magic" else ""
    used = {a.casefold() for a in arts}
    return max(0, aura) if art and art.casefold() in used else 0


def aligned_lines(
    alignment: str, realm: str, aura: int, arts: tuple[str, ...]
) -> list[Line]:
    """The Casting Score or Lab Total line an Art-aligned aura adds ([]
    when it adds none)."""
    amount = art_bonus(alignment, realm, aura, arts)
    if not amount:
        return []
    return [
        Line(
            f"Aura aligned with {aligned_art(alignment)}",
            amount=amount,
            source=ALIGNED_SOURCE,
        )
    ]


def healing_line(alignment: str, realm: str, aura: int) -> Line | None:
    """The Recovery Total line a Healing aura adds."""
    if realm != "Magic" or alignment_kind(alignment) != HEALING:
        return None
    amount = healing_bonus(aura)
    if not amount:
        return None
    return Line("Healing aura", amount=amount, source=ALIGNED_SOURCE)


def power_cost(cost: int, might_form: str, alignment: str, realm: str) -> int:
    """A Might power's cost in a Magic aura aligned with the creature's
    Might Form: a point less, when it costs any."""
    art = aligned_art(alignment) if realm == "Magic" else ""
    if cost > 0 and art and art in FORMS and art.casefold() == might_form.casefold():
        return cost - 1
    return cost


def alignment_effects(alignment: str, aura: int) -> str:
    """What a Magic aura's alignment does, as the place's facts say it
    ("" for none)."""
    kind = alignment_kind(alignment)
    if not kind:
        return ""
    if kind == "art":
        art = aligned_art(alignment)
        text = (
            f"aligned with {art}: +{max(0, aura)} more to Casting Scores of "
            f"spells using {art} and to {art} Lab Totals"
        )
        if art in FORMS:
            text += f"; a creature of {art} Might pays a Might Point less for a power"
    elif kind == HEALING:
        text = f"Healing: +{healing_bonus(aura)} to Recovery Totals"
    elif kind == LUCK:
        text = f"Luck: +{luck_bonus(aura)} to rolls where luck matters, for all"
    elif kind == DISTRACTING:
        ease = distracting_ease(aura)
        text = "Distracting: Concentration rolls come more often"
        if ease:
            text += f", their Ease Factors +{ease}"
    else:
        trait = alignment.strip()
        text = (
            f"{trait}: those without The Gift or another Magic power take "
            f"{trait} +{feeling_adjustment(aura)} while here (never an "
            "Essential Trait)"
        )
    if aura > SAFE_ALIGNED:
        text += "; those living here without a Magic power slowly warp"
    return text


# -- Faerie: tints --

_TINT = re.compile(r"^\s*(.+?)\s*([+-]\s*\d+)\s*$")


def parse_tints(words: str) -> list[tuple[str, int]] | None:
    """The tints `words` names ("Drawn to Children +3; Light +2"), or None
    when a part isn't a Trait and a value."""
    found: list[tuple[str, int]] = []
    for part in re.split(r"[;,]", words or ""):
        if not part.strip():
            continue
        match = _TINT.match(part)
        if match is None:
            return None
        found.append((match.group(1), int(match.group(2).replace(" ", ""))))
    return found


def tints(words: str, aura: int) -> list[tuple[str, int]]:
    """Each tint's Trait and value, no stronger than the aura."""
    most = max(0, aura)
    return [
        (trait, max(-most, min(most, value)))
        for trait, value in parse_tints(words) or []
        if value
    ]


def tint_ease(value: int) -> int:
    """Tinting an aura (stress die + Presence + Concentration): 3 x the
    Trait's value, up to 10."""
    return 3 * min(MOST_TINT, abs(value))


def tint_effects(words: str, aura: int) -> str:
    found = tints(words, aura)
    if not found:
        return ""
    traits = ", ".join(f"{trait} {value:+d}" for trait, value in found)
    text = f"tinted: everyone here takes {traits} while here"
    if len(found) > 1:
        text += ", pulled several ways at once"
    return text


# -- Divine: Dominion or Empyreal --


def divine_kind(words: str) -> str:
    """Dominion or Empyreal; a Divine aura is the Dominion unless set."""
    return EMPYREAL if words.strip().casefold() == EMPYREAL.casefold() else DOMINION


def divine_aura(
    aura: int, kind: str = DOMINION, *, night: bool = False, holy_day: bool = False
) -> int:
    """A Divine aura's strength at a time, Dominion or Empyreal alike: one
    less at night and one more on Sundays and holy days."""
    del kind  # both kinds wax and wane the same way
    return max(0, aura - (1 if night else 0) + (1 if holy_day else 0))


def miracle_empyreal(level: int) -> int:
    """The Empyreal aura a miracle leaves while its effect lasts: 1 at
    level 50, a point more each five levels above."""
    return max(0, (level - 45) // 5)


def creature_empyreal(might: int, seasons: int) -> int:
    """The Empyreal aura of a holy creature's home: 1 a season it dwells
    there, up to its Divine Might / 10."""
    return max(0, min(seasons, might // 10))


def radiates_empyreal(faith_points: int) -> bool:
    """Whether a person or relic radiates an Empyreal aura."""
    return faith_points >= EMPYREAL_FAITH


def divine_effects(words: str, aura: int) -> str:
    empyreal = divine_kind(words) == EMPYREAL
    name = "Empyreal: from no worship; " if empyreal else "Dominion: "
    if aura <= 0:
        return "Empyreal: from no worship" if empyreal else ""
    return (
        f"{name}{max(0, aura - 1)} at night, {aura + 1} on Sundays and "
        "holy days; holds against another realm's aura of its strength"
    )


# -- any aura --

_EFFECTS = {
    "Magic": alignment_effects,
    "Faerie": tint_effects,
    "Divine": divine_effects,
}


def effects_text(details: dict[str, Any], realm: str, aura: int) -> str:
    """What the aura's kind does, as the place's facts say it ("" for
    none)."""
    describe = _EFFECTS.get(realm)
    if describe is None:
        return ""
    return describe(kind_of(details, realm), aura)


def problem(values: dict[str, Any]) -> str | None:
    """A form's kind fields that don't read (the tints' Traits)."""
    words = str(values.get(KIND_KEYS["Faerie"]) or "")
    if words.strip() and (values.get("realm") or "Magic") == "Faerie":
        found = parse_tints(words)
        if found is None:
            return 'Write each tint as a Trait and a value: "Drawn to Children +3".'
        if any(abs(value) > MOST_TINT for _, value in found):
            return f"A tint is at most +{MOST_TINT} or -{MOST_TINT}."
    return None
