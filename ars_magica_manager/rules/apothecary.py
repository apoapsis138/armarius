"""The apothecary's store (Art & Academe, The Practice of the Apothecary,
pp. 63-66).

- **Medicinals** come in four degrees of hot, cold, dry or moist: the
  first imperceptible, the second stronger without harm, the third
  interfering with the body's function, the fourth destroying tissue:
  every fourth-degree medicinal is a poison (p. 64).
- **Poisons**: Profession: Apothecary knows them. Making one usually
  needs a special search for its ingredients, and only a simple poison (a
  Light Wound, resisted at Ease Factor 6 or less) is made without its
  formula (p. 65; rules.philosophy).
- **The store**: a season keeping it earns (Intelligence + Profession:
  Apothecary) x the Wealth Multiplier Labor Points (City & Guild's, season
  work "apothecary"). It loses 36 a year (the business's upkeep), and 3
  more a year for each physician whose regimens it supplies; each theriac
  or reagent made from it, and each ligature, takes its Labor Points too
  (p. 65).
- **A physician with an apothecary** takes the apothecary's Profession:
  Apothecary off the penalty for having no medicinals (rules.disease).
- **Preserving** an ingredient: Dexterity + Profession: Apothecary against
  the Ease Factor of how long it keeps (weeks 3 to indefinitely 18); a
  preserved plant or animal Arcane Connection kept longer than it lasts
  lasts a category longer (p. 64).
- **Searching** for an ingredient, instead of drawing on the store:
  Perception + Profession: Apothecary + a stress die against 9, a month a
  search; success finds a Labor Point's worth, and each point over finds
  another or halves the time; a botch finds none. Local Area Lore lowers
  the Ease Factor, as does each assistant (no more than Leadership, each
  with Profession: Apothecary 1 or Area Lore 2) and a spell such as Hunt
  for the Wild Herb (-3); hard ground and winter raise it. What is found
  pays for one need; it never adds to the store's Labor Points (pp. 65-66).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character, Saga
from . import medicine
from .lab import ability_score
from .scores import ability_level

SOURCE = "Art & Academe, The Practice of the Apothecary, pp. 63-66"
PROFESSION = "Profession: Apothecary"

#: The four degrees of a medicinal (p. 64); the fourth is a poison.
DEGREES: dict[int, str] = {
    1: "a mild action, imperceptible to the senses",
    2: "a greater action, without perceptibly interfering with the body",
    3: "evident interference with the body's function, not yet harmful",
    4: "destruction or death of tissue: a poison",
}
POISON_DEGREE = 4

#: Labor Points a year for each physician whose regimens the store
#: supplies (p. 65).
REGIMEN_LABOR = 3

#: How long a preserved ingredient keeps, and the Ease Factor (p. 64).
PRESERVE_EASE: tuple[tuple[str, int], ...] = (
    ("Weeks", 3),
    ("Months", 6),
    ("Seasons", 9),
    ("Years", 12),
    ("Decades", 15),
    ("Indefinitely", 18),
)

SEARCH_EASE = 9
#: The modifiers to a search's Ease Factor (p. 66).
INHOSPITABLE, BARREN = "inhospitable", "barren"
TERRAIN: dict[str, int] = {"": 0, INHOSPITABLE: 1, BARREN: 3}
TERRAIN_LABELS: dict[str, str] = {
    "": "Ordinary ground",
    INHOSPITABLE: "Inhospitable (heavy snow...) +1",
    BARREN: "Barren (desert, bare rock) +3",
}
WINTER = 2
SEARCH_SPELL = -3
#: What an assistant needs: Profession: Apothecary 1 or the Area Lore 2.
ASSISTANT_PROFESSION = 1
ASSISTANT_AREA_LORE = 2


def profession(character: Character) -> int:
    """The character's Profession: Apothecary (with Puissant)."""
    return sum(ability_score(character, PROFESSION))


def keeps_store(character: Character) -> bool:
    """Whether the character has an apothecary's store to draw on: any
    Profession: Apothecary."""
    return ability_level(character, PROFESSION) >= 1


def supplier(saga: Saga, physician: Character) -> Character | None:
    """The apothecary whose store supplies a physician's regimens: his own
    if he keeps one, else the best apothecary at his covenant (anyone in
    the saga when he has none)."""
    if keeps_store(physician):
        return physician
    near = [
        c
        for c in saga.characters
        if c is not physician
        and keeps_store(c)
        and (physician.covenant_id is None or c.covenant_id == physician.covenant_id)
    ]
    return max(near, key=profession, default=None)


def physicians_supplied(saga: Saga, apothecary: Character) -> list[Character]:
    """The physicians keeping regimens on this apothecary's store."""
    return [
        c
        for c in saga.characters
        if medicine.clients(saga, c) and supplier(saga, c) is apothecary
    ]


def regimen_drain(saga: Saga, apothecary: Character) -> int:
    """The Labor Points a year the regimens the store supplies take."""
    return REGIMEN_LABOR * len(physicians_supplied(saga, apothecary))


# -- preserving ----------------------------------------------------------------


def preserve_base(character: Character) -> int:
    """Dexterity + Profession: Apothecary, the roll before its die."""
    return character.characteristics.dexterity + profession(character)


def preserve_ease(duration: str) -> int:
    return dict(PRESERVE_EASE)[duration]


def kept_for(total: int) -> str:
    """The longest a preserving roll's total keeps an ingredient ("" for
    not even weeks)."""
    reached = [name for name, ease in PRESERVE_EASE if total >= ease]
    return reached[-1] if reached else ""


# -- searching -----------------------------------------------------------------


@dataclass(frozen=True)
class Search:
    """What a search for ingredients is rolled against."""

    area_lore: int = 0
    assistants: int = 0
    terrain: str = ""
    winter: bool = False
    spell: bool = False

    def ease(self) -> int:
        """The Ease Factor: 9, less Area Lore and each assistant, +1 or +3
        for the ground, +2 in winter, -3 under a finding spell (p. 66)."""
        return (
            SEARCH_EASE
            - self.area_lore
            - self.assistants
            + TERRAIN[self.terrain]
            + (WINTER if self.winter else 0)
            + (SEARCH_SPELL if self.spell else 0)
        )


def search_base(character: Character) -> int:
    """Perception + Profession: Apothecary, the roll before its die."""
    return character.characteristics.perception + profession(character)


def most_assistants(character: Character) -> int:
    """An apothecary leads one searching assistant per point of Leadership."""
    return ability_level(character, "Leadership")


def found_points(total: int, ease: int) -> int:
    """Labor Points' worth found in a month's search (0: none); each point
    over the Ease Factor may instead halve the time (p. 65)."""
    return 0 if total < ease else 1 + total - ease
