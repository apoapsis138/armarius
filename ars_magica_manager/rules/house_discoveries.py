"""House Bonisagus's example discoveries, once a magus has them: the six
Parma Magica folds of Arma Magica, Parmulae, Figurine Magic and
realm-aligned spells (Houses of Hermes: True Lineages pp. 30-34).

A magus has a discovery when one of his research goals of that name is
reached (rules.integrations names them): he made it, or was taught it and
the troupe recorded it as his. What each then does:

- A fold changes the Parma Magica score before it is multiplied by 5 for
  Magic Resistance (never below 0; the Form bonus always counts): Ablativa
  doubles it but each resisted Penetration wears it down; Absorbea,
  Repercussa and Condensa (against the other Forms) halve it, rounded up;
  Condensa doubles it against its chosen Form, which needs that Art at
  twice the Parma score; Custodia gives no Parma resistance but adds twice
  Parma to Defense; Restricta is Parma - 3, wrapped round someone touched.
  A magus may know as many folds as his Parma Magica score; only one fold
  is raised at a time (p. 31).
- A Parmula is a lesser enchanted device of level 44 (Rego Vim 30, constant
  use) giving Magic Resistance 30 for a year: one season, a Rego Vim Lab
  Total of twice the level, 5 pawns of Rego or Vim vis, +4 for jewelry
  (p. 32).
- Figurine Magic: Dexterity + Craft: Sculptor against 6 (wax) or 9 (wood)
  to carve it, then Intelligence + Figurine Magic + aura against 9, +3 for a
  Minor General Virtue, +6 a Minor Supernatural one, +1 a magnitude for a
  spell; wax lasts two seasons, wood four (p. 33).
- A realm-aligned spell is invented with Magic Theory limited to the Realm
  Lore; cast in an aura it uses the Realm-Aligned Spell Interaction Table
  instead of the usual one, and its botch dice fall by that Realm Lore
  (p. 34)."""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character
from .lab import ability_score, art_score
from .lab_virtues import has
from .rounding import round_up

SOURCE = "Houses of Hermes: True Lineages, Bonisagus, Example Discoveries, pp. 30-34"

# -- knowing one --


def knows(magus: Character, name: str) -> bool:
    """Whether one of the magus's reached research goals is `name` (its
    name holds it, whatever the case: "Arma Magica: Parma Ablativa" is
    known by "Parma Ablativa")."""
    wanted = name.casefold()
    return any(
        goal.reached and wanted in goal.name.casefold() for goal in magus.breakthroughs
    )


# -- the Parma Magica folds --


@dataclass(frozen=True)
class Fold:
    name: str
    #: What it does, a sentence for the sheet.
    does: str


ABLATIVA, ABSORBEA, CONDENSA = "Parma Ablativa", "Parma Absorbea", "Parma Condensa"
CUSTODIA, REPERCUSSA, RESTRICTA = (
    "Parma Custodia",
    "Parma Repercussa",
    "Parma Restricta",
)

FOLDS: dict[str, Fold] = {
    f.name: f
    for f in (
        Fold(
            ABLATIVA,
            "double Parma, less each resisted Penetration; ten minutes to raise, "
            "and another fold may be raised once it falls to 0",
        ),
        Fold(
            ABSORBEA,
            "half Parma; a resisted spell's Penetration (half, or all for the "
            "same Arts) may add to the next spell's Casting Total on a Stamina "
            "+ Concentration stress roll above it",
        ),
        Fold(
            CONDENSA,
            "double Parma against one Form chosen when raised (that Art at "
            "least twice Parma), half against the rest",
        ),
        Fold(CUSTODIA, "no Parma resistance; twice Parma added to Defense"),
        Fold(REPERCUSSA, "half Parma; a spell it stops is turned at a target seen"),
        Fold(
            RESTRICTA,
            "Parma - 3, wrapped round someone touched: their spells beyond "
            "Personal must penetrate it",
        ),
    )
}


def known_folds(magus: Character) -> list[str]:
    """The folds the magus knows, at most his Parma Magica score of them."""
    parma = sum(ability_score(magus, "Parma Magica"))
    return [name for name in FOLDS if knows(magus, name)][: max(0, parma)]


def folded_parma(parma: int, fold: str, *, chosen_form: bool = False) -> int:
    """The Parma Magica score a fold counts for Magic Resistance (p. 31);
    `chosen_form` for Parma Condensa against its own Form."""
    if fold == ABLATIVA:
        found = 2 * parma
    elif fold in (ABSORBEA, REPERCUSSA):
        found = round_up(parma / 2)
    elif fold == CONDENSA:
        found = 2 * parma if chosen_form else round_up(parma / 2)
    elif fold == CUSTODIA:
        found = 0
    elif fold == RESTRICTA:
        found = parma - 3
    else:
        found = parma
    return max(0, found)


def fold_resistance(
    magus: Character, form: str, fold: str, *, chosen_form: bool = False
) -> int:
    """The magus's Magic Resistance against `form` with `fold` raised: the
    Form score + 5 x the folded Parma (no aura)."""
    score, bonus = art_score(magus, form)
    parma = sum(ability_score(magus, "Parma Magica"))
    return max(
        0, score + bonus + 5 * folded_parma(parma, fold, chosen_form=chosen_form)
    )


def custodia_defense(magus: Character) -> int:
    """Parma Custodia's bonus to Defense: twice Parma Magica."""
    return 2 * max(0, sum(ability_score(magus, "Parma Magica")))


def condensa_needs(parma: int) -> int:
    """The Art score a Form must have to be Parma Condensa's: twice Parma."""
    return 2 * parma


# -- Parmulae --

PARMULA_LEVEL = 44
PARMULA_RESISTANCE = 30
PARMULA_VIS = 5
PARMULA_JEWELRY = 4
PARMULA_LAB_TOTAL = 2 * PARMULA_LEVEL

# -- Figurine Magic --

FIGURINE_MAGIC = "vf_figurine_magic"
FIGURINE_CARVE = {"wax": 6, "wood": 9}
FIGURINE_SEASONS = {"wax": 2, "wood": 4}
FIGURINE_BASE = 9
FIGURINE_POWER = {"Minor General Virtue": 3, "Minor Supernatural Virtue": 6}


def figurine_ease(power: str, magnitude: int = 0) -> int:
    """The Ease Factor to imbue a figurine with `power` ("Minor General
    Virtue", "Minor Supernatural Virtue", or "spell" of `magnitude`)."""
    if power == "spell":
        return FIGURINE_BASE + max(0, magnitude)
    return FIGURINE_BASE + FIGURINE_POWER.get(power, 0)


# -- realm-aligned spells --

#: The Realm-Aligned Spell Interaction Table (p. 34): for a spell aligned
#: to the key's realm, what each aura's strength is multiplied by (a half
#: rounds down as the core table's does).
ALIGNED_TABLE: dict[str, dict[str, float]] = {
    "Magic": {"Magic": 0, "Divine": -3, "Faerie": 0.5, "Infernal": -1},
    "Faerie": {"Magic": 0.5, "Divine": -4, "Faerie": 0, "Infernal": -2},
    "Infernal": {"Magic": -1, "Divine": -5, "Faerie": -1, "Infernal": 0},
}
#: The realms a spell may be aligned to: Hermetic magic can't free itself
#: of the Divine.
ALIGNMENTS = tuple(ALIGNED_TABLE)


def aligned_aura_modifier(alignment: str, aura_realm: str, aura: int) -> int:
    """What an aura adds to a realm-aligned spell's Casting Total."""
    factor = ALIGNED_TABLE.get(alignment, {}).get(aura_realm, 0)
    return int(factor * aura) if factor >= 0 else round(factor * aura)


def aligned_magic_theory(magic_theory: int, realm_lore: int) -> int:
    """The Magic Theory a realm-aligned spell is invented with: no more
    than the Realm Lore."""
    return min(magic_theory, realm_lore)


def aligned_botch_dice(dice: int, realm_lore: int) -> int:
    """Botch dice less the Realm Lore, down to none."""
    return max(0, dice - max(0, realm_lore))


LORES = {"Magic": "Magic Lore", "Faerie": "Faerie Lore", "Infernal": "Infernal Lore"}


# -- for the sheet --


def reminders(magus: Character) -> list[str]:
    """A sentence (plain text) for each discovery the magus has."""
    found: list[str] = []
    parma = sum(ability_score(magus, "Parma Magica"))
    for name in known_folds(magus):
        folded = folded_parma(parma, name)
        found.append(
            f"{name}: {FOLDS[name].does} (Parma {parma} counts {folded} for "
            f"resistance{', Defense +' + str(custodia_defense(magus)) if name == CUSTODIA else ''})."
        )
    if knows(magus, "Parmulae"):
        found.append(
            f"Parmulae: a lesser device of level {PARMULA_LEVEL} gives Magic "
            f"Resistance {PARMULA_RESISTANCE} for a year ({PARMULA_VIS} pawns, "
            f"Rego Vim Lab Total {PARMULA_LAB_TOTAL}, jewelry +{PARMULA_JEWELRY})."
        )
    if has(magus, FIGURINE_MAGIC):
        skill = sum(ability_score(magus, "Figurine Magic"))
        found.append(
            "Figurine Magic: carve with Dexterity + Craft: Sculptor against 6 "
            "(wax, a month, lasts two seasons) or 9 (wood, two months, a year); "
            f"imbue with Intelligence + Figurine Magic ({skill}) + aura against "
            "9, +3 for a Minor General Virtue, +6 a Minor Supernatural one, +1 "
            "a magnitude for a Touch, Individual spell; no vis, Penetration 0."
        )
    if knows(magus, "Realm-aligned spells"):
        lores = ", ".join(
            f"{realm} {sum(ability_score(magus, lore))}"
            for realm, lore in LORES.items()
        )
        found.append(
            "Realm-aligned spells: invented with Magic Theory no higher than the "
            "Realm Lore; cast with the aligned table, and the Lore off the botch "
            f"dice ({lores})."
        )
    return found
