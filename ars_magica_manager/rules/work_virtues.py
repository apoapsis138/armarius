"""Virtues and Flaws that change a working season, a business's year, a
total with one subject of Artes Liberales, or a year's Warping, each a
function of the character (and of where they live):

- Labor Points (City & Guild): Perfect Eye for Commodity gains 3 x the
  Wealth Multiplier a year; Bigamist's second household costs 6 x it a year
  (3 x it while posing as of lower status: the "status" parameter "lower").
  Independent Craftsman counts Craft, Profession and Leadership three lower
  working with others, which the workshop's assistants (the plan's Other)
  can't show, so it is a note. Necessary Realm Aura for (Ability): -3 to
  every total with the Ability outside an aura of its realm, Labor Points
  included.
- Artes Liberales by subject (Art & Academe): Academic Concentration adds
  +3 for its subject and -1 for the other six; Aristotelian Training adds
  +1 for grammar, logic and rhetoric. A Laboratory Horoscope is astronomy;
  a debate's Artes Liberales attack is logic and rhetoric.
- A year's Warping: Raised from the Dead gains one a year; Immortality of
  the Forest gains one a year instead of an Aging roll; Susceptibility to
  Warping adds one more in any year that gave Warping from any source.
"""

from __future__ import annotations

from ..models import Character, Saga
from . import realms

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Four: Virtues and Flaws "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Four:"
    "_Virtues_and_Flaws)"
)
ACADEME_SOURCE = (
    "Art & Academe, Chapter Two: The Liberal Arts "
    "(https://www.redcap.org/page/Art_%26_Academe_Open_Content)"
)

PERFECT_EYE = "vf_perfect_eye_for_commodity"
BIGAMIST = "vf_bigamist"
INDEPENDENT = "vf_independent_craftsman"
NECESSARY_AURA = "vf_necessary_realm_aura_for_ability"
CONCENTRATION = "vf_academic_concentration_subject"
ARISTOTELIAN = "vf_aristotelian_training"
RAISED = "vf_raised_from_the_dead"
FOREST = "vf_immortality_of_the_forest"
SUSCEPTIBLE = "vf_susceptibility_to_warping"

PERFECT_EYE_PER_WM = 3
BIGAMIST_PER_WM = 6
BIGAMIST_LOWER_PER_WM = 3
INDEPENDENT_PENALTY = 3
NECESSARY_AURA_PENALTY = 3
CONCENTRATION_BONUS = 3
CONCENTRATION_PENALTY = 1
ARISTOTELIAN_SUBJECTS = ("grammar", "logic", "rhetoric")
SUBJECTS = (
    "grammar",
    "logic",
    "rhetoric",
    "arithmetic",
    "geometry",
    "astronomy",
    "music",
)
#: Names of a realm's aura besides its own (Dominion is the Divine's).
_REALM_NAMES = {"dominion": "divine"}


def _with(character: Character, vf_id: str) -> list[dict[str, str]]:
    return [vf.params for vf in character.virtues_flaws if vf.vf_id == vf_id]


def has(character: Character, vf_id: str) -> bool:
    return bool(_with(character, vf_id))


# -- Labor Points -------------------------------------------------------------


def yearly_labor(character: Character, wealth_multiplier: int) -> list[tuple[str, int]]:
    """The Labor Points a business's year gains (+) or costs (-) beyond its
    upkeep, with the Virtue or Flaw that gives each."""
    found: list[tuple[str, int]] = []
    for params in _with(character, PERFECT_EYE):
        commodity = params.get("commodity", "")
        name = (
            f"Perfect Eye for {commodity}" if commodity else "Perfect Eye for Commodity"
        )
        found.append((name, PERFECT_EYE_PER_WM * wealth_multiplier))
    for params in _with(character, BIGAMIST):
        lower = params.get("status", "").strip().lower() == "lower"
        per = BIGAMIST_LOWER_PER_WM if lower else BIGAMIST_PER_WM
        found.append(("Bigamist", -per * wealth_multiplier))
    return found


def _realm(name: str) -> str:
    key = name.strip().lower()
    return _REALM_NAMES.get(key, key)


def aura_penalty(saga: Saga, character: Character, ability: str) -> int:
    """Necessary Realm Aura for (Ability): the penalty to a total with
    `ability` where the character lives (0 inside the right aura)."""
    aura, realm = realms.home_aura(saga, character)
    for params in _with(character, NECESSARY_AURA):
        if params.get("ability", "").strip().lower() != ability.lower():
            continue
        wanted = _realm(params.get("realm", ""))
        if not wanted:
            continue
        if aura <= 0 or _realm(realm) != wanted:
            return -NECESSARY_AURA_PENALTY
    return 0


def independent_note(character: Character, ability: str) -> str:
    """Independent Craftsman's reminder for a season with `ability`
    ("" when it doesn't apply)."""
    if not has(character, INDEPENDENT):
        return ""
    if not (ability.startswith(("Craft", "Profession")) or ability == "Leadership"):
        return ""
    return (
        f"Independent Craftsman: {ability} counts {INDEPENDENT_PENALTY} lower "
        "working with assistants or as one (the Other modifier)."
    )


# -- Artes Liberales by subject ----------------------------------------------


def artes_liberales(
    character: Character, subjects: tuple[str, ...]
) -> list[tuple[str, int]]:
    """What Academic Concentration and Aristotelian Training add to an
    Artes Liberales total in any of `subjects` (the best fit of each)."""
    found: list[tuple[str, int]] = []
    for params in _with(character, CONCENTRATION):
        chosen = params.get("subject", "").strip().lower()
        if not chosen:
            continue
        if chosen in subjects:
            found.append((f"Academic Concentration ({chosen})", CONCENTRATION_BONUS))
        else:
            found.append((f"Academic Concentration ({chosen})", -CONCENTRATION_PENALTY))
    if has(character, ARISTOTELIAN) and set(subjects) & set(ARISTOTELIAN_SUBJECTS):
        found.append(("Aristotelian Training", 1))
    return found


# -- a year's Warping ---------------------------------------------------------


def forest_replaces_aging(character: Character) -> bool:
    """Immortality of the Forest: a Warping Point instead of an Aging roll."""
    return has(character, FOREST)


def yearly_warping(character: Character) -> list[tuple[str, int]]:
    """The Warping Points the character's Virtues and Flaws give every year."""
    found: list[tuple[str, int]] = []
    if has(character, RAISED):
        found.append(("Raised from the Dead", 1))
    if has(character, FOREST):
        found.append(("Immortality of the Forest", 1))
    return found


def susceptible(character: Character) -> bool:
    return has(character, SUSCEPTIBLE)
