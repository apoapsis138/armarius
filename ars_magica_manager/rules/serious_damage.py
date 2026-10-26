"""Art & Academe's optional rule, Lasting Consequences of Serious Damage
(Chapter Three: Medicine, Injury, p. 43), under the Art & Academe medicine
saga option.

When an Incapacitating wound is dealt, the character makes a Stamina roll
against 6 at once; a failure leaves a lasting complication, a Minor Flaw
fitting where the wound struck, as Surgical Intervention lists them (p.
62: the head Disfigured, Missing Eye or Missing Ear; the torso Disfigured
or Fragile Constitution; a limb Disfigured, Lame, Missing Hand or Palsied
Hands). The storyguide picks the Flaw; the app says which fit and writes
it in the Diary. A wound that only worsens to Incapacitating later is not
"dealt", and needs no roll.

The Definitive Edition has no such rule (its wounds heal or kill, DE pp.
404-405); this adds to it and changes nothing there.
"""

from __future__ import annotations

import random

from ..models import Character, Saga
from . import chirurgy, dice

SOURCE = "Art & Academe, Optional Rule: Lasting Consequences of Serious Damage, p. 43"
EASE = 6
INCAPACITATING = "incapacitating"


def applies(saga: Saga | None) -> bool:
    return chirurgy.on(saga)


def flaws(location: str) -> tuple[str, ...]:
    """The Minor Flaws fitting a wound to `location` (A&A p. 62)."""
    return chirurgy.LOCATIONS.get(location, chirurgy.LOCATIONS["torso"])[1]


def roll(
    saga: Saga | None, character: Character, location: str, rng: random.Random
) -> list[str]:
    """The Stamina roll for an Incapacitating wound just dealt: the lines
    saying how it went ([] when the rule is off). A botch fails."""
    if not applies(saga):
        return []
    die = dice.stress_die(rng, saga=saga)
    total = character.characteristics.stamina + (0 if die.botched else die.value)
    said = f"Stamina roll for lasting damage: {total} against {EASE}"
    if not die.botched and total >= EASE:
        return [f"{said}, no lasting complication."]
    where = location if location in chirurgy.LOCATIONS else "torso"
    *rest, last = flaws(where)
    choices = f"{', '.join(rest)} or {last}" if rest else last
    return [
        f"{said}{', botched' if die.botched else ''}: a lasting complication, "
        f"a Minor Flaw fitting the {where} ({choices}; A&A p. 43)."
    ]
