"""The totals and tables of single hedge traditions that are more than a
casting rule: what a season of elementalist Refining yields, an Augustan
animation's Might and awakening, a Fertility Ritual's Trait Points, a
learned magician's amulet charges, Canaanite necromancy's and a lector
priest's Ease Factors, and Geomancy's stylus bonuses.

Elementalist Refining (Hedge Magic RE pp. 26-27): a season with no roll;
the Refining Total (Intelligence + the type's Ability + Refining + Form +
aura) sets what it makes:

- a longevity potion: Total / 5 to Aging rolls (the lowest Form as a
  requisite), for (age / 5) pawns, rounded up, and no more vis than the
  Forms' sum;
- medicinal: a year's Characteristic potion, + Total / 5, to at most
  half the Form's score;
- philosophical: Total / 10 pawns of vis from an aura; vis moved, up to
  Total / 5 pawns (half of another Form's lost);
- theurgical: Might restored or drained by the Total less the being's
  Might (half for an unrelated Form), a pawn of vis a 5 Might points.

Rounding where the book gives none is down (DE p. 6): the potions'
bonuses, extraction and the caps; only the potion's vis, age / 5, is
printed as rounded up.

Rules: the books cited on each function.
"""

from __future__ import annotations

from collections.abc import Callable

from ..models import Character, Saga
from . import hedge_casting as hc
from . import hyperborean
from .casting import magnitude
from .rounding import round_down, round_up

SOURCE = "Hedge Magic, Revised Edition, Elementalists, Refining, pp. 26-27"
AUGUSTAN_SOURCE = "Rival Magic, The Augustan Brotherhood, Animo, pp. 61-64"
FERTILITY_SOURCE = "Ancient Magic, Fertility Magic, The Fertility Ritual, pp. 56-58"

ELEMENTALIST_FORMS = (
    "Elementalist Air",
    "Elementalist Earth",
    "Elementalist Fire",
    "Elementalist Water",
)
#: The (Type) Refining Virtues, whose type parameter names the kind of
#: Refining (Hedge Magic RE p. 20).
REFINING_VIRTUES = ("vf_type_refining_major", "vf_type_refining")
REFINING_TYPES = ("medicinal", "philosophical", "theurgical")


def refining_types(character: Character) -> list[str]:
    """The types of Refining the character practises (all three when no
    Virtue names one, so the yields are shown for the troupe)."""
    found = []
    for vf in character.virtues_flaws:
        if vf.vf_id in REFINING_VIRTUES:
            kind = str(vf.params.get("type", "")).strip().lower()
            if kind in REFINING_TYPES and kind not in found:
                found.append(kind)
    return found or list(REFINING_TYPES)


def longevity_bonus(total: int) -> int:
    """A Refining longevity potion's bonus to Aging rolls."""
    return max(0, round_down(total / 5))


def longevity_pawns(age: int) -> int:
    """Its vis: the drinker's age / 5, rounded up, as for a Longevity
    Ritual (DE p. 261)."""
    return max(0, round_up(age / 5))


def characteristic_potion(total: int, form_score: int) -> int:
    """The highest a medicinal potion can take a Characteristic: + Total
    / 5, to at most half the associated Form."""
    return min(round_down(total / 5), round_down(form_score / 2))


def extracted_vis(total: int) -> int:
    """Pawns an elemental philosopher draws from an aura in a season."""
    return max(0, round_down(total / 10))


def vis_moved(total: int) -> int:
    """The most pawns an elemental philosopher moves in a season."""
    return max(0, round_down(total / 5))


def might_change(total: int, might: int, *, same_form: bool, opposed: bool) -> int:
    """Might Points a theurgical Refining restores (same Form) or drains
    (opposed Form): the Total over the being's Might, half of it rounded
    down for any other Form."""
    excess = max(0, total - might)
    return excess if same_form or opposed else round_down(excess / 2)


def refining_yields(saga: Saga, character: Character, total: int) -> list[str]:
    """What a season's Refining Total makes, by the character's types."""
    forms = [
        hc.score(character, f) for f in ELEMENTALIST_FORMS if hc.holds(character, f)
    ]
    lowest = min(forms) if forms else 0
    born = character.background.year_born
    age = saga.current_year - born if born is not None else None
    pawns = (
        f"{longevity_pawns(age)} pawns at age {age}"
        if age is not None
        else "age / 5 pawns, rounded up"
    )
    lines = [
        f"Longevity potion: +{longevity_bonus(total)} to Aging rolls until a "
        f"crisis, for {pawns} (at most {sum(forms)}, the Forms' sum).",
    ]
    kinds = refining_types(character)
    if "medicinal" in kinds:
        lines.append(
            f"Characteristic potion for a year: +{round_down(total / 5)}, to at most "
            f"+{round_down(max(forms, default=0) / 2)} (half the Form used)."
        )
    if "philosophical" in kinds:
        lines.append(
            f"Vis from an aura: {extracted_vis(total)} pawns of the element; or move "
            f"up to {vis_moved(total)} pawns (half of another Form's is lost)."
        )
    if "theurgical" in kinds:
        lines.append(
            f"A being's Might: restored or drained by {total} less its Might "
            "(half for an unrelated Form); a pawn of vis a 5 points, at most "
            "Might / 5."
        )
    if lowest and forms:
        lines.append(f"The lowest Elementalist Form is {lowest}.")
    return lines


#: Season notes by a tradition activity's key (a Strategy registry): what
#: the season's Lab Total makes.
SEASON_YIELDS: dict[str, Callable[[Saga, Character, int], list[str]]] = {
    "elementalist_refining": refining_yields,
    # The Hyperborean hymns (Ancient Magic pp. 106-108, 116-117).
    "hymnist_infuse_power": hyperborean.infuse_yields,
    "hymnist_enchant_relic": hyperborean.relic_yields,
}


def season_notes(saga: Saga, character: Character, key: str, total: int) -> list[str]:
    found = SEASON_YIELDS.get(key)
    return found(saga, character, total) if found is not None else []


#: Worked-out lines under a tradition's pool, by "tradition id:pool name",
#: and under its Warping, by tradition id (Strategy registries).
POOL_NOTES: dict[str, Callable[[Character], list[str]]] = {
    f"{hyperborean.TRADITION_ID}:{hyperborean.POWER_POOL}": hyperborean.levels_lines,
}
WARPING_NOTES: dict[str, Callable[[Character, int], list[str]]] = {
    hyperborean.TRADITION_ID: hyperborean.illumination_lines,
}


def pool_notes(character: Character, tradition_id: str, pool: str) -> list[str]:
    found = POOL_NOTES.get(f"{tradition_id}:{pool}")
    return found(character) if found is not None else []


def warping_notes(character: Character, tradition_id: str, aura: int) -> list[str]:
    found = WARPING_NOTES.get(tradition_id)
    return found(character, aura) if found is not None else []


# ---------------------------------------------------------------------------
# The Augustan Brotherhood's animations (Rival Magic pp. 61-64)


def animation_might(size: int, material_points: int) -> int:
    """An animation's base Magic Might: (10 + Size + the material's base
    points) / 2, rounded down (Rival Magic p. 62)."""
    return round_down((10 + size + material_points) / 2)


def awakening_ease(might: int, *, mobile: bool, aware: bool) -> int:
    """Awakening its spirit: Pre + Animo + Virgilian Theory + aura + a
    stress die against its Might, +6 if it moves, +6 if it is aware of its
    surroundings (p. 63)."""
    return might + (6 if mobile else 0) + (6 if aware else 0)


def most_inscribed_ease(might: int) -> int:
    """The highest Ease Factor of a rite inscribed in it: twice its Might
    (p. 64)."""
    return 2 * might


def rite_vis(ease: int) -> int:
    """Pawns a ritual rite or an inscription takes: its Ease Factor / 6,
    rounded up (pp. 54, 64)."""
    return max(0, round_up(ease / 6))


RITUAL_EASE = 33


def rite_is_ritual(ease: int, *, target: str = "", duration: str = "") -> bool:
    """Ease Factor 33 or more, a Boundary or City Target, or Year Duration
    make a rite a ritual (pp. 54-55)."""
    return ease >= RITUAL_EASE or target in ("Boundary", "City") or duration == "Year"


# ---------------------------------------------------------------------------
# The Fertility Ritual (Ancient Magic pp. 56-58)

#: Trait Points each chosen trait costs (p. 57).
TRAIT_COSTS: dict[str, int] = {
    "Major Virtue or Flaw": 3,
    "Minor Virtue or Flaw": 1,
    "The Gift": 3,
    "Gender": 1,
    "Another general feature": 1,
    "Looks like a named person": 3,
}


def trait_points(lab_total: int, *, own_child: bool = False) -> int:
    """Trait Points a Fertility Ritual may spend: 1 a 10 points (or
    fraction) of the Creo Corpus Lab Total, or a 5 for a maga's own
    child (p. 57)."""
    return max(0, round_up(lab_total / (5 if own_child else 10)))


def trait_cost(choices: dict[str, int]) -> int:
    """The Trait Points (and pawns of vis, p. 58) the chosen traits cost:
    {TRAIT_COSTS key: how many}. The chosen Virtues and Flaws need not
    balance; a player character born of it gains balancing traits by
    adulthood (p. 58)."""
    return sum(TRAIT_COSTS[name] * count for name, count in choices.items())


def repeat_warping(cost: int) -> int:
    """Warping for repeating a ritual while its first child lives: half
    its Trait cost, rounded up (pp. 58-59)."""
    return round_up(cost / 2)


# ---------------------------------------------------------------------------
# Single Ease Factors and bonuses


def necromancy_ease(level: int) -> int:
    """Canaanite Necromancy's Ease Factor: 3 x the magnitude of the
    Hermetic effect it matches (an InCo 15 effect: 9; Ancient Magic
    p. 30)."""
    return 3 * magnitude(level)


def amulet_charges(lab_total: int, level: int) -> int:
    """A learned magician's amulet: (Lab Total - level) / 5 charges,
    rounded up; none below the level (Hedge Magic RE p. 86)."""
    if lab_total < level:
        return 0
    return max(1, round_up((lab_total - level) / 5))


def charta_total(lab_total: int) -> int:
    """A charta's total: half the Lab Total (Hedge Magic RE p. 86)."""
    return round_down(lab_total / 2)


def scroll_ease(level: int) -> int:
    """Reading a lector priest's scroll: Com + Coptic + a die against 3 +
    1 a magnitude of its effect (Lands of the Nile p. 51)."""
    return 3 + magnitude(level)


STATUE_CONSECRATION = 18

#: Geomancy's Ease Factors by the question's importance, the complexity
#: added (the highest one applies), and the styluses that add +3 when the
#: question fits them (Between Sand and Sea pp. 110-111).
GEOMANCY_IMPORTANCE: dict[str, int] = {"Major": 9, "Minor": 12, "Trivial": 15}
GEOMANCY_COMPLEXITY: dict[str, int] = {
    "Single word": 0,
    "Short sentence": 3,
    "A proper noun": 3,
    "Lengthy explanation": 6,
}
STYLUS_BONUSES: dict[str, str] = {
    "Dagger": "war and physical conflict",
    "Human bone": "health",
    "Broken glass or mirror shard": "finding things",
    "Wooden stick": "natural places and crops",
    "Metal nail": "buildings and dwellings",
    "Animal bone": "jinn",
}
STYLUS_BONUS = 3


def geomancy_ease(importance: str, complexity: str = "Single word") -> int:
    return GEOMANCY_IMPORTANCE[importance] + GEOMANCY_COMPLEXITY[complexity]


def stylus_bonus(stylus: str, fits: bool) -> int:
    """+3 from a stylus whose subject fits the question; a finger, wax or
    paper gives none (p. 111)."""
    return STYLUS_BONUS if fits and stylus in STYLUS_BONUSES else 0
