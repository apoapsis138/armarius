"""Faerie sympathy: Sympathy Traits, Faerie Rank and sympathetic influence
(Realms of Power: Faerie, Chapter Five, pp. 102-104; Errata p. 68), and
the Olympian gods' Sympathy Traits (The Sundered Eagle p. 127).

- A **Sympathy Trait** is a Personality Trait kept with the kind
  `SYMPATHY`: a mystic bond with a narrow class of things (never a whole
  Form), usually +1 to +3, rarely above +6, +10 all but a faerie. Used as
  the specialty of a fitting non-Supernatural Ability it adds its score
  in place of the +1, the roll becomes a stress roll and a botch Warps;
  only the best fitting Trait counts. A negative Trait, where it applies,
  comes off every Ability, and the worst one adds its value in botch dice
  to every botch roll (p. 102).
- **Raising one** (p. 103): with experience as an Ability, to no more
  than the Warping Score; practising one a season gives 5 xp. A negative
  Trait rises only while the Warping Score is above its size: 10 xp from
  -1 to 0, 15 from -2 to -1, 20 from -3 to -2. Errata p. 68: it may rise
  to 0 and on to +1. A 1 on a stress die using a Trait gives it an xp, a
  botch takes one away (the other way round for a negative Trait), beyond
  the Warping limit.
- **Faerie Rank** (p. 103) is the best positive Trait plus the worst
  negative one: Winter +4 and Summer -2 make 2; Dancing +1 and Stone -5
  make -4.
- **Temporary Sympathy Traits** (pp. 103-105, 127): those from
  sympathetic influence or a Grant rite are kept with the kind
  `TEMPORARY`. They work as Sympathy Traits (a specialty, a folk charm,
  a rite's limit, the worst negative one's botch dice) but don't count
  toward Faerie Rank, can't be raised by experience and aren't limited by
  the Warping Score. Traits an aura's tint gives are plain Personality
  Traits (p. 104).
- **Sympathetic influence** (pp. 103-104): a ceremony of ten minutes led
  by someone with Faerie Lore 1 (a Confidence Point from each taking part;
  it lasts a week at most) or a season of free time spent with the
  subject (it lasts up to a year), then simple die + Presence +
  Leadership: 9 gives a Trait of 1, 15 of 2, 24 of 3 (the most). A fitting
  Personality Trait or Flaw is needed; a fitting Sympathy Trait may be
  Leadership's specialty, on a stress die. (Tinting an aura is
  rules.aura_kinds.)
- **The Olympians** (The Sundered Eagle p. 127): a Faerie God's blood
  from one of the twelve Olympians or Hestia chooses from that god's
  Sympathy Traits.

Pattern: plain functions over the traits list, and the tables as dicts.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..models import ScoredTrait

SOURCE = (
    "Realms of Power: Faerie, Sympathy, pp. 102-104; Errata p. 68; The "
    "Sundered Eagle, Sympathy Traits of the Olympians, p. 127"
)

#: The kind a Personality Trait has when it is a Sympathy Trait.
SYMPATHY = "Sympathy"
#: The kind of a temporary Sympathy Trait, from sympathetic influence or a
#: Grant rite (pp. 103, 127).
TEMPORARY = "Sympathy, temporary"
#: A season's practice of a Sympathy Trait (p. 103).
PRACTICE_XP = 5
#: Experience points per step, as an Ability's (5 x the new score), and a
#: negative Trait's (5 x (its size + 1)) (p. 103).
XP_PER_STEP = 5
#: Sympathetic influence: the least total for each Trait value (p. 103).
INFLUENCE: tuple[tuple[int, int], ...] = ((24, 3), (15, 2), (9, 1))
INFLUENCE_SOURCE = "Realms of Power: Faerie, Sympathetic Influence, pp. 103-104"


def is_sympathy(trait: ScoredTrait) -> bool:
    """Whether it is a Sympathy Trait, lasting or temporary."""
    return trait.type in (SYMPATHY, TEMPORARY)


def is_temporary(trait: ScoredTrait) -> bool:
    return trait.type == TEMPORARY


def sympathy_traits(traits: Sequence[ScoredTrait]) -> list[ScoredTrait]:
    """The Sympathy Traits among a character's Personality Traits,
    temporary ones included."""
    return [t for t in traits if is_sympathy(t)]


def lasting_traits(traits: Sequence[ScoredTrait]) -> list[ScoredTrait]:
    """The Sympathy Traits that aren't temporary: those Faerie Rank counts
    and experience raises (pp. 103-104, 127)."""
    return [t for t in traits if t.type == SYMPATHY]


def faerie_rank(traits: Sequence[ScoredTrait]) -> int | None:
    """The best positive lasting Sympathy Trait plus the worst negative
    one; None with no lasting Sympathy Traits (p. 103; temporary ones don't
    count, pp. 104, 127)."""
    scores = [t.score for t in lasting_traits(traits)]
    if not scores:
        return None
    return max([0, *scores]) + min([0, *scores])


def extra_botch_dice(traits: Sequence[ScoredTrait]) -> int:
    """The botch dice the worst negative Sympathy Trait adds (p. 102)."""
    return -min([0, *(t.score for t in sympathy_traits(traits))])


def xp_to_raise(score: int) -> int:
    """The experience points that raise a Sympathy Trait by one: as an
    Ability's for 0 and up, 5 x (its size + 1) for a negative one (p. 103;
    Errata p. 68 lets a negative one rise through 0)."""
    if score >= 0:
        return XP_PER_STEP * (score + 1)
    return XP_PER_STEP * (-score + 1)


def can_raise(score: int, warping_score: int) -> bool:
    """Whether experience may raise the Trait: a positive one to no more
    than the Warping Score, a negative one only while the Warping Score is
    above its size (p. 103)."""
    if score < 0:
        return warping_score > -score
    return score + 1 <= warping_score


def influence_value(total: int) -> int:
    """The Sympathy Trait (plus or minus) a sympathetic influence roll
    gives: 9 for 1, 15 for 2, 24 for 3, the most (p. 103)."""
    return next((value for least, value in INFLUENCE if total >= least), 0)


def rank_text(traits: Sequence[ScoredTrait], warping_score: int) -> str:
    """The sheet's line: Faerie Rank, from which Traits, the temporary
    ones apart, and how far xp may raise them; "" with no Sympathy
    Traits."""
    if not sympathy_traits(traits):
        return ""
    rank = faerie_rank(traits)
    named = ", ".join(f"{t.name} {t.score:+d}" for t in lasting_traits(traits))
    line = (
        f"Faerie Rank: {rank:+d} (Sympathy Traits {named})"
        if rank is not None
        else "Faerie Rank: none"
    )
    temporary = [t for t in traits if is_temporary(t)]
    if temporary:
        line += (
            "; temporary "
            + ", ".join(f"{t.name} {t.score:+d}" for t in temporary)
            + " (not in the Rank, not raised by xp; pp. 103, 127)"
        )
    botches = extra_botch_dice(traits)
    if botches:
        line += f"; {botches} more botch dice where a negative Trait applies"
    if rank is None:
        return line
    return (
        line + f"; experience raises a Trait to at most Warping Score "
        f"{warping_score}, 5 xp a season of practice (RoP: Faerie pp. 102-103)"
    )


# -- the Olympians --


@dataclass(frozen=True)
class Olympian:
    """A god's positive and negative Sympathy Traits."""

    positive: tuple[str, ...]
    negative: str

    def text(self) -> str:
        return f"{', '.join(self.positive)}; {self.negative} (negative)"


#: The Sympathy Traits of the Olympians (The Sundered Eagle p. 127).
OLYMPIANS: dict[str, Olympian] = {
    "Zeus": Olympian(("Thunder & Lightning", "Kings", "Sky"), "Fidelity"),
    "Hera": Olympian(("Women", "Children", "Vengeance"), "Men"),
    "Poseidon": Olympian(("Sea", "Earthquakes", "Horses"), "Calm"),
    "Demeter": Olympian(("Fertility", "Plants", "Domesticated Animals"), "Winter"),
    "Apollon": Olympian(("Light", "Prophecy", "Healing"), "Passion"),
    "Artemis": Olympian(("Wild Animals", "Pursuit", "Diseases"), "Men"),
    "Athene": Olympian(("Wisdom", "Tactics", "Culture"), "Direct Action"),
    "Ares": Olympian(("Violence", "Weapons", "Fear"), "Bravery"),
    "Aphrodite": Olympian(("Attraction", "Desire", "Beauty"), "Avoiding Attention"),
    "Hephaistos": Olympian(("Iron", "Volcanoes", "Precious Metals"), "Beauty"),
    "Hermes": Olympian(("Money", "Trickery", "News"), "Avoiding Trouble"),
    "Dionysos": Olympian(("Wine", "Madness", "Initiation"), "Rational Action"),
    "Hestia": Olympian(("Family", "Hearth", "Virginity"), "Self Promotion"),
}
OLYMPIANS_SOURCE = "The Sundered Eagle, Sympathy Traits of the Olympians, p. 127"


def olympian(name: str) -> Olympian | None:
    """The god by name, in any case; None for one not on the table."""
    wanted = name.strip().casefold()
    return next((g for n, g in OLYMPIANS.items() if n.casefold() == wanted), None)
