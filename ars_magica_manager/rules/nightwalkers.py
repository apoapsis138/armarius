"""Nightwalkers: straying, the phantasticum, fertility battles and
processions (Hedge Magic, Revised Edition, Chapter Six: Nightwalkers,
pp. 103-119). Straying is a Virtue's power with no Ability score; its
rolls are fixed Ease Factors against ordinary Abilities, gathered here,
with the catalog's casting rules for the ones the sheet shows.

- Insensibility by drug takes 10 - Concentration minutes (at least one);
  someone drugged resists with Stamina against 6 (p. 106).
- Straying costs a Long-Term Fatigue level for any time up to an hour
  (even a few minutes), two for a whole night, one more for talking to
  people at the destination (pp. 106, 108).
- Spirit travel: Stamina + Athletics against 3 to 15 by how well the
  place is known, +3 for each object carried beyond the tradition's
  own; some journeys always succeed (p. 107). Leading a willing spirit
  along is Stamina + Leadership against 3 more; drawing one out on the
  spot is against 3 (p. 108).
- Turning tangible or intangible, or human or animal, takes three
  rounds, or a Stamina + Concentration roll against 15 in combat (p. 107).
- An animal phantasticum keeps the character's Intelligence; each other
  Characteristic is the lower of two negatives, the higher of two
  positives, or the sum of a negative and a positive (p. 107); a taltós
  in flame shape the same against a Might 10 elemental's (p. 116).
- A hostile phantasticum makes the unresisting drowsy: Concentration +
  Stamina against 3 to stay awake (p. 108).
- Fertility battles: the outcome sets the year's harvest, and with
  Covenants the income roll's result (p. 108).
- Recognising a fellow nightwalker awake: Perception + Awareness against
  15 (met in battle) or 12 (in processions) - his Reputation, 3 less if
  they meet monthly awake, 6 less weekly; an Infernal witch 18 -
  Reputation (p. 110).
- The dead: intimidating a ghost is Presence + Leadership against 6 +
  its Brave, each side's willing fighters adding to its roll or Ease
  Factor; questioning one is Presence + Charm or Leadership against 3, 6
  or 9 by the answer's length (p. 111).

Rules: the pages cited on each function.
"""

from __future__ import annotations

from collections.abc import Mapping

from ..models import Character
from ..models.holdings import INCOME_EFFECTS

SOURCE = "Hedge Magic, Revised Edition, Nightwalkers, pp. 103-119"
TRADITION_ID = "trad_nightwalkers"
NIGHTWALKER = "vf_nightwalker"
VERSATILE = "vf_versatile_phantasticum"

#: Spirit travel's Ease Factors by how well the place is known (p. 107).
TRAVEL_EASE: dict[str, int] = {
    "seen daily": 3,
    "seen this week": 6,
    "seen this year": 9,
    "visited, route known": 12,
    "never visited, route or Arcane Connection known": 15,
}
#: Each object carried beyond the tradition's accoutrements.
CARRIED_OBJECT = 3
#: Journeys that need no roll (pp. 107-108).
SURE_JOURNEYS = (
    "to one's own caul",
    "where one is summoned or led to battle or procession",
    "to one's True Love, or leading another to theirs",
    "along a known route at ordinary speed",
)
LEAD_ASTRAY_STEP = 3
DRAW_ASTRAY_EASE = 3
DRUG_RESIST_EASE = 6
DREAM_RECALL_EASE = 12
FORM_CHANGE_ROUNDS = 3
FORM_CHANGE_COMBAT_EASE = 15
DROWSINESS_EASE = 3
SEEK_FOE_EASE = 9
#: Seeing an intangible phantasticum with Second Sight (p. 104).
SECOND_SIGHT_EASE = 9
HALF_TALTOS_EASE = 6
#: Questioning the dead, by the answer's length (p. 111).
QUESTION_EASE: dict[str, int] = {
    "yes or no": 3,
    "a sentence": 6,
    "up to six sentences": 9,
}
GHOST_INTIMIDATION_BASE = 6

#: A fertility battle's outcome for the nightwalkers' side, worst first,
#: and the Covenants Income Modification result each stands for (p. 108).
BATTLE_OUTCOMES: tuple[tuple[str, str], ...] = (
    ("utterly defeated and harried through the countryside", "Slump"),
    ("routed", "Contraction"),
    ("forced from the field in good order", "Stagnation"),
    ("wins the field", "Status Quo"),
    ("routs its enemies", "Growth"),
    ("harries routed enemies through the night", "Expansion"),
    ("traps and annihilates the enemy militia", "Boom"),
)
assert {effect for _, effect in BATTLE_OUTCOMES} == set(INCOME_EFFECTS)

#: A flame-shaped taltós's Characteristics before his own are combined
#: in: a Might 10 fire elemental's, Cunning replaced by his Intelligence
#: (p. 116).
FLAME_SHAPE: dict[str, int] = {
    "perception": -8,
    "communication": -8,
    "presence": 0,
    "strength": 4,
    "stamina": 2,
    "dexterity": 4,
    "quickness": 2,
}
FLAME_DAMAGE = 5

_CHARACTERISTICS = (
    "perception",
    "strength",
    "stamina",
    "presence",
    "communication",
    "dexterity",
    "quickness",
)


def is_nightwalker(character: Character) -> bool:
    return any(vf.vf_id == NIGHTWALKER for vf in character.virtues_flaws)


# ---------------------------------------------------------------------------
# Straying


def insensibility_minutes(concentration: int) -> int:
    """Minutes a drug takes to make him insensible: 10 - Concentration, at
    least one (p. 106); a hamr's trance takes as long (p. 105)."""
    return max(10 - concentration, 1)


def straying_fatigue(*, whole_night: bool = False, talked: bool = False) -> int:
    """Long-Term Fatigue levels a straying costs: one for any time up to
    an hour (the book gives no free time below the hour), two for a whole
    night, and one more for talking with people at its end (pp. 106,
    108)."""
    levels = 2 if whole_night else 1
    return levels + (1 if talked else 0)


def travel_ease(place: str, objects: int = 0) -> int:
    """Spirit travel's Ease Factor: the place's (TRAVEL_EASE) + 3 a carried
    object (p. 107)."""
    if place not in TRAVEL_EASE:
        raise ValueError(f"Unknown place {place!r}; one of {list(TRAVEL_EASE)}")
    return TRAVEL_EASE[place] + CARRIED_OBJECT * max(objects, 0)


def travel_total(character: Character, athletics: int, die: int) -> int:
    """Stamina + Athletics + a die (p. 107)."""
    return character.characteristics.stamina + athletics + die


def lead_astray_ease(place: str, objects: int = 0) -> int:
    """Leading a willing spirit along: Stamina + Leadership against the
    journey's Ease Factor + 3 (p. 108)."""
    return travel_ease(place, objects) + LEAD_ASTRAY_STEP


def recognition_ease(reputation: int, *, battle: bool = True, waking: str = "") -> int:
    """Perception + Awareness to know a militia's member awake: 15 - his
    Reputation if met in battle, 12 - it from processions; 3 less if they
    meet awake monthly, 6 less weekly (p. 110)."""
    ease = (15 if battle else 12) - reputation
    return ease - {"": 0, "monthly": 3, "weekly": 6}[waking]


def witch_recognition_ease(reputation: int) -> int:
    """Knowing an Infernal witch fought at night: 18 - her Reputation
    (p. 110)."""
    return 18 - reputation


# ---------------------------------------------------------------------------
# The phantasticum


def combined_characteristic(own: int, form: int) -> int:
    """One Characteristic of an animal or flame phantasticum (pp. 107,
    116): the lower of two negatives, the higher of two positives, else
    the two added."""
    if own < 0 and form < 0:
        return min(own, form)
    if own > 0 and form > 0:
        return max(own, form)
    return own + form


def phantastic_characteristics(
    character: Character, form: Mapping[str, int]
) -> dict[str, int]:
    """The phantasticum's Characteristics against the form's (`form` by
    lower-case name; one it doesn't give is 0): Intelligence stays his."""
    own = character.characteristics
    found = {"intelligence": own.intelligence}
    for name in _CHARACTERISTICS:
        found[name] = combined_characteristic(getattr(own, name), form.get(name, 0))
    return found


def form_change(*, in_combat: bool) -> str:
    """Switching tangible and intangible, or human and animal shape (p. 107)."""
    if in_combat:
        return f"Stamina + Concentration against {FORM_CHANGE_COMBAT_EASE}"
    return f"{FORM_CHANGE_ROUNDS} rounds"


def stays_awake(character: Character, concentration: int, die: int) -> bool:
    """Concentration + Stamina + a die against 3 keeps someone without
    Magic Resistance awake before a hostile phantasticum (p. 108)."""
    return concentration + character.characteristics.stamina + die >= DROWSINESS_EASE


# ---------------------------------------------------------------------------
# Fertility battles and the dead


def battle_income(outcome: str) -> str:
    """The Covenants Income Modification result a fertility battle's
    outcome stands for, in place of the stress die (p. 108)."""
    for name, effect in BATTLE_OUTCOMES:
        if name == outcome:
            return effect
    raise ValueError(f"Unknown outcome {outcome!r}")


def harvest(outcome: str) -> str:
    """The harvest a battle leaves until the next: a rout of the enemy a
    bountiful one, a win the usual one, a loss failed crops and poor
    fishing (p. 108)."""
    effect = battle_income(outcome)
    rank = INCOME_EFFECTS.index(effect)
    status_quo = INCOME_EFFECTS.index("Status Quo")
    if rank > status_quo:
        return "bountiful"
    return "normal" if rank == status_quo else "failed"


def intimidation_ease(brave: int, ghost_allies: int = 0) -> int:
    """Intimidating a ghost: 6 + its Brave, + any dead willing to fight
    beside it (p. 111)."""
    return GHOST_INTIMIDATION_BASE + brave + max(ghost_allies, 0)


def intimidation_total(
    character: Character, leadership: int, die: int, allies: int = 0
) -> int:
    """Presence + Leadership + a die, + the nightwalkers willing to fight
    beside him (p. 111)."""
    return character.characteristics.presence + leadership + die + max(allies, 0)


def question_ease(answer: str) -> int:
    """Questioning the dead by Presence + Charm (or Leadership): 3, 6 or 9
    by the answer's length; one question a ghost a night (p. 111)."""
    if answer not in QUESTION_EASE:
        raise ValueError(f"Unknown answer {answer!r}; one of {list(QUESTION_EASE)}")
    return QUESTION_EASE[answer]
