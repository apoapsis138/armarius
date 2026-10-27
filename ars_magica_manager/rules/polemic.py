"""Polemic, diatribe and apologia, and Charter Strength (Transforming
Mythic Europe, The Tools of Politics, pp. 27-36). The Definitive Edition
has no such rules, and the errata correct none of these pages.

Polemic (pp. 27-35):

- An argument's reach sets its Prevailing Wisdom (p. 29): one concerning
  a magus 3 or his Reputation if higher, a covenant 6, a Tribunal 9, a
  House 12, the Order 15.
- A polemic is a summa or tractatus on any knowledge Ability (Code of
  Hermes or Order of Hermes Lore suit the Order's affairs, an Area Lore
  with the troupe's agreement); a tractatus counts as level 5 (p. 28). Diatribes and apologia are
  written on the same Ability as the work they answer, after a season
  studying it (pp. 28, 31, 35).
- Circulating (pp. 29-30): 6 copies for a Tribunal, 9 for a House, 18
  for the Order. Each season after they are released: the highest of
  the circulator's Reputations, good or bad, or his House Acclaim + the
  level + a simple die, +1 for each season already spent and +1 for each
  new work bound into every copy, against 15, 18 or 24. Each season is
  a distraction of 5, 10 or 15 days. A sponsor may circulate it with his
  own Reputation.
- A polemic's author gains Supporter of (ideal) 1 once it is out
  (p. 31); a diatribe's Opposed to (ideal) 1, an apologia's Supporter of
  (ideal) 1, come "on writing or circulating" (pp. 33, 35): the author
  on writing it, a circulator who isn't the author on circulating it.
  One who has it already gains 5 experience toward it instead, and no
  one gains it twice from the same text.
- The Argument Total (p. 31): one per argument. The polemic's Quality
  less the Prevailing Wisdom, plus each circulated apologia's Quality,
  less each circulated diatribe's, whoever wrote it (p. 33). At Tribunal it is spent as experience on the Art table
  (DE p. 49): 1 for +1, 3 for +2, 6 for +3, 10 for +4; a negative total
  buys a penalty the same way. The bonus or penalty goes on every Attack
  and Defense roll of the proponent in that debate, on top of Houses of
  Hermes: Societates's (pp. 92-93). A case hears one argument for each
  side: adding several arguments' bonuses together is a house rule.
- Won, the bonus carries to later Tribunals; lost, at the first or a
  later Tribunal, it is gone (p. 35).

Charter Strength, an optional rule (p. 36):

- Drafting a charter is a season's work for each side's notaries: the
  principal notary rolls Intelligence + Civil and Canon Law (Common Law
  in England, and only it there) + a stress die, with 3 botch dice less
  one for each notary beyond the first; a botch leaves that side's
  strength at 0.
- Seeking a loophole is a season examining the charter, then
  Intelligence + the same law + a stress die: higher than the other
  side's strength finds legal grounds to break provisions. The book
  gives it no botch dice; the app rolls one, and a botch (DE p. 7) is a
  total of 0 and some ill the storyguide decides.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import APOLOGIA, DIATRIBE, POLEMIC, Character, ScoredTrait
from . import xp
from .confidence import add_deeds
from .lab import ability_score

SOURCE = (
    "Transforming Mythic Europe, The Tools of Politics, Writing and "
    "Responding to Polemic, pp. 27-35, and Optional Rule: Charter Strength, "
    "p. 36; Ars Magica Definitive Edition, the Art advancement table, p. 49"
)

#: The Prevailing Wisdom by reach (TME p. 29); a magus's is the higher of
#: 3 and his Reputation.
PREVAILING_WISDOM: dict[str, int] = {
    "magus": 3,
    "covenant": 6,
    "tribunal": 9,
    "house": 12,
    "order": 15,
}
REACH_NAMES: dict[str, str] = {
    "magus": "a magus",
    "covenant": "a covenant",
    "tribunal": "a Tribunal",
    "house": "a House",
    "order": "the Order",
}

#: A text's audience: (copies needed, Circulation Ease Factor, days of
#: distraction each season) (TME p. 29).
CIRCULATION: dict[str, tuple[int, int, int]] = {
    "tribunal": (6, 15, 5),
    "house": (9, 18, 10),
    "order": (18, 24, 15),
}
AUDIENCE_NAMES: dict[str, str] = {
    "tribunal": "a Tribunal",
    "house": "a House",
    "order": "the Order",
}

#: A tractatus's level for circulating it (TME pp. 28-29).
TRACTATUS_LEVEL = 5

#: The Abilities the book suggests a polemic on the Order be written on
#: (TME p. 28), Area Lore with the troupe's agreement; any knowledge
#: Ability will do.
SUGGESTED_ABILITIES: tuple[str, ...] = (
    "Code of Hermes",
    "Order of Hermes Lore",
    "Area Lore",
)

#: The catalog's categories of knowledge Abilities, and the General
#: Abilities that are knowledge too: its Lores.
KNOWLEDGE_CATEGORIES: tuple[str, ...] = ("Academic", "Arcane")


def is_knowledge(category: str, name: str) -> bool:
    """Whether an Ability of `category` named `name` is a knowledge
    Ability a polemic may be written on (TME p. 28): an Academic or
    Arcane Ability, or a General one that is a Lore."""
    return category in KNOWLEDGE_CATEGORIES or (
        category == "General" and "Lore" in name
    )


#: The experience a circulated text gives a Reputation its author has
#: already (TME pp. 31, 33, 35).
REPUTATION_XP = 5

#: The Ability a charter's notaries use, and England's (TME p. 36).
CIVIL_LAW = "Civil and Canon Law"
COMMON_LAW = "Common Law"

#: Botch dice for drafting a charter, before the extra notaries (p. 36).
DRAFT_BOTCH_DICE = 3


# -- polemic --


def prevailing_wisdom(reach: str, magus_reputation: int = 0) -> int:
    """The level of the opinion an argument moves (TME p. 29)."""
    base = PREVAILING_WISDOM.get(reach, PREVAILING_WISDOM["tribunal"])
    return max(base, magus_reputation) if reach == "magus" else base


def text_level(book_type: str, level: int | None) -> int:
    """A text's level for circulating it: a tractatus counts as 5, a
    summa its own level."""
    if book_type == "Tractatus":
        return TRACTATUS_LEVEL
    return level or 0


def circulation_reputation(character: Character | None) -> int:
    """The Reputation a circulator rolls with: the highest of his
    Reputations, good or bad, House Acclaim among them (TME p. 29)."""
    if character is None:
        return 0
    return max((abs(r.score) for r in character.reputations), default=0)


def circulation_total(reputation: int, level: int, seasons: int, bundled: int) -> int:
    """The Circulation Total before its simple die: Reputation + level,
    +1 for each season already spent and +1 for each new work bound into
    every copy (TME pp. 29-30)."""
    return reputation + level + max(0, seasons) + max(0, bundled)


def ease_factor(audience: str) -> int:
    return CIRCULATION.get(audience, CIRCULATION["tribunal"])[1]


def copies(audience: str) -> int:
    return CIRCULATION.get(audience, CIRCULATION["tribunal"])[0]


def distraction_days(audience: str) -> int:
    return CIRCULATION.get(audience, CIRCULATION["tribunal"])[2]


def circulates(total: int, die: int, audience: str) -> bool:
    """Whether the Circulation Total with its simple die meets the
    audience's Ease Factor."""
    return total + die >= ease_factor(audience)


def needs_study(kind: str) -> bool:
    """A diatribe or apologia is written only after a season studying the
    work it answers (TME pp. 31, 35)."""
    return kind in (DIATRIBE, APOLOGIA)


def sign(kind: str) -> int:
    """How a circulated text's Quality counts toward the Argument Total:
    a diatribe's against it, the others' for it (TME pp. 31-35)."""
    return -1 if kind == DIATRIBE else 1


@dataclass(frozen=True)
class Counted:
    """A text as the Argument Total counts it: its kind, its Quality and
    whether it is circulated."""

    kind: str
    quality: int
    circulated: bool


def argument_total(wisdom: int, texts: list[Counted]) -> int | None:
    """The Argument Total (TME p. 31): the circulated polemic's Quality
    less the Prevailing Wisdom, + each circulated apologia's Quality, −
    each circulated diatribe's. None until a polemic is out."""
    polemics = [t for t in texts if t.kind == POLEMIC and t.circulated]
    if not polemics:
        return None
    total = max(t.quality for t in polemics) - wisdom
    for text in texts:
        if text.circulated and text.kind != POLEMIC:
            total += sign(text.kind) * text.quality
    return total


def debate_bonus(total: int | None) -> int:
    """The bonus (or penalty) an Argument Total buys as experience on the
    Art table (TME p. 31; DE p. 49): 1 for +1, 3 for +2, 6 for +3..."""
    if total is None:
        return 0
    score = xp.score_from_xp(abs(total), xp.ART_FACTOR)
    return score if total >= 0 else -score


def reputation_name(kind: str, ideal: str) -> str:
    """The Reputation a circulated text gives its author (TME pp. 31, 33,
    35): Supporter of (ideal) for a polemic or apologia, Opposed to (ideal)
    for a diatribe."""
    lead = "Opposed to" if kind == DIATRIBE else "Supporter of"
    return f"{lead} {ideal.strip() or 'the argument'}"


def gain_reputation(character: Character, name: str, reach: str) -> str:
    """Give `character` the Reputation `name` at 1, or 5 experience toward
    it if he has it (TME pp. 31, 33, 35); what happened, in words."""
    found = next(
        (
            r
            for r in character.reputations
            if r.name.strip().casefold() == name.strip().casefold()
        ),
        None,
    )
    if found is None:
        character.reputations.append(ScoredTrait(name, 1, type="Hermetic", reach=reach))
        return f"{character.name} gained {name} 1 ({reach})."
    before = found.score
    add_deeds(found, REPUTATION_XP)
    raised = f", now {found.score}" if found.score != before else ""
    return f"{character.name} gained {REPUTATION_XP} experience in {name}{raised}."


# -- Charter Strength (optional) --


def law_of(in_england: bool) -> str:
    """The law a charter's notaries use: Common Law in England, Civil and
    Canon Law elsewhere (TME p. 36)."""
    return COMMON_LAW if in_england else CIVIL_LAW


def law_score(character: Character | None, in_england: bool = False) -> tuple[str, int]:
    """The notary's law, as (its name, his score in it): only Common Law
    for a charter in England, only Civil and Canon Law elsewhere (TME
    p. 36)."""
    law = law_of(in_england)
    if character is None:
        return law, 0
    return law, sum(ability_score(character, law))


def charter_total(character: Character | None, in_england: bool = False) -> int:
    """Intelligence + the charter's law, before the stress die."""
    if character is None:
        return 0
    return character.characteristics.intelligence + law_score(character, in_england)[1]


def draft_botch_dice(notaries: int) -> int:
    """Botch dice for drafting: 3, less one for each notary beyond the
    first (TME p. 36); `notaries` counts them all."""
    return max(0, DRAFT_BOTCH_DICE - max(0, notaries - 1))


def finds_loophole(total: int, strength: int) -> bool:
    """Whether a search's total (with its die) finds a loophole: higher
    than the other side's Charter Strength (TME p. 36)."""
    return total > strength
