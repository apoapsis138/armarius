"""How far a character can push himself in a day (Grogs pp. 51-52).

- On foot: 15 + 2 x Athletics miles on good roads (5 to 10 fewer cross
  country), Encumbrance taken off Athletics first; it costs two Long-Term
  Fatigue levels, and after as many days as his Athletics he regains only
  one a night.
- On horseback: 30 + 2 x Ride (10 to 20 fewer cross country), and 2 x Ride
  more for each change of horse; without Ride, 20 miles and always one
  Long-Term Fatigue level. The horse tires as its rider does.
- Without pushing, the Travel Fatigue table's typical day: 15 miles on foot,
  30 on a horse, 15 by cart or river boat, 18 by coach.
- Planning a new journey of more than a week: Intelligence + Area Lore
  against 12 cuts the time by a tenth. A group goes at its slowest.
"""

from __future__ import annotations

from ..models import Character
from . import derived
from .scores import ability_level

SOURCE = "Grogs, Guides and Messengers and Travel Speeds, pp. 51-52"

FOOT_BASE = 15
HORSE_BASE = 30
#: Miles a day on a horse without the Ride Ability.
UNSKILLED_RIDER = 20
PLANNING_EASE = 12
#: Typical miles a day without Long-Term Fatigue, and with it.
TYPICAL_DAY: dict[str, tuple[int, int | None]] = {
    "Foot": (15, 20),
    "Horse": (30, 40),
    "Cart or wagon": (15, None),
    "Coach": (18, 24),
    "River vessel": (15, None),
    "Small sailing ship": (50, None),
    "Galley": (80, None),
}


def forced_march(character: Character) -> int:
    """Miles a day on foot on good roads, pushing hard."""
    load = derived.carried_load(character.inventory)
    enc = derived.encumbrance(load, character.characteristics.strength)
    athletics = ability_level(character, "Athletics") - enc
    return max(0, FOOT_BASE + 2 * athletics)


def forced_ride(character: Character, changes: int = 0) -> int:
    """Miles a day on horseback on good roads, pushing hard, with this many
    changes of horse (up to three, when they wait ready)."""
    ride = ability_level(character, "Ride")
    if ride <= 0:
        return UNSKILLED_RIDER
    return HORSE_BASE + 2 * ride * (1 + max(0, changes))
