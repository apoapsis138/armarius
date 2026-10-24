"""The supernatural senses: the Ease Factors for Magic Sensitivity, Second
Sight and Sense Holiness and Unholiness, and for seeing into a regio
level.

- Magic Sensitivity: simple die + Perception + score, against 12 - aura
  for a Magic aura, 21 - magnitude for a spell or an enchanted item (its
  most powerful effect), 15 - Might / 5 for a magical creature. It also
  takes its score off the character's Magic Resistance (DE p. 168).
- Second Sight: Perception + score, almost always a simple roll, against
  6 + the magnitude of an illusion's spell (or of the Might behind it), 9
  for a naturally invisible thing, and a regio level as below (DE p. 170).
- Sense Holiness and Unholiness: Perception + score, against 9 for an
  area and 15 for a person or object; 0 for a demon and 15 for an angel
  hiding its nature, both of which must also be Penetrated. It is a Divine
  power (DE p. 170).
- Regio sight: Perception + Second Sight, Magic Sensitivity or (into a
  Divine or Infernal level) Sense Holiness + stress die, against 5 + 2 x the
  difference between the current and sought auras; from an aura of another
  realm the two auras are added instead (DE p. 421).
"""

from __future__ import annotations

from .rounding import round_down

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Five: Abilities, Magic "
    "Sensitivity, Second Sight, Sense Holiness and Unholiness, pp. 168-170"
)
REGIO_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Twelve: Realms, Entering and "
    "Leaving Regiones, p. 421"
)

MAGIC_SENSITIVITY = "Magic Sensitivity"
SECOND_SIGHT = "Second Sight"
SENSE_HOLINESS = "Sense Holiness and Unholiness"
SENSES = (MAGIC_SENSITIVITY, SECOND_SIGHT, SENSE_HOLINESS)

#: The Abilities that can see into a regio level of each realm.
REGIO_SENSES: dict[str, tuple[str, ...]] = {
    "Magic": (SECOND_SIGHT, MAGIC_SENSITIVITY),
    "Faerie": (SECOND_SIGHT, MAGIC_SENSITIVITY),
    "Divine": (SECOND_SIGHT, MAGIC_SENSITIVITY, SENSE_HOLINESS),
    "Infernal": (SECOND_SIGHT, MAGIC_SENSITIVITY, SENSE_HOLINESS),
}


def magic_aura_ease(aura: int) -> int:
    """Magic Sensitivity sensing a Magic aura."""
    return 12 - aura


def magic_effect_ease(magnitude: int) -> int:
    """Magic Sensitivity sensing a spell, or an enchanted item by its most
    powerful effect."""
    return 21 - magnitude


def magic_creature_ease(might: int) -> int:
    """Magic Sensitivity sensing a creature of Magic Might."""
    return 15 - round_down(might / 5)


def illusion_ease(magnitude: int) -> int:
    """Second Sight seeing through an illusion: its spell's magnitude, or
    the magnitude of the Might behind it."""
    return 6 + magnitude


INVISIBLE_EASE = 9  # Second Sight seeing a naturally invisible thing
AREA_EASE = 9  # Sense Holiness in a general area
PERSON_EASE = 15  # Sense Holiness in a person or object
DEMON_EASE = 0  # ...and it must Penetrate the demon's Magic Resistance
HIDDEN_ANGEL_EASE = 15  # ...likewise; an angel not hiding is sensed outright


def regio_sight_ease(
    current_aura: int, current_realm: str, sought_aura: int, sought_realm: str
) -> int:
    """Seeing into a regio level from where you stand: 5 + 2 x the
    difference in aura, or 5 + 2 x the two auras added when you stand in
    an aura of another realm."""
    if current_aura and current_realm != sought_realm:
        gap = current_aura + sought_aura
    else:
        gap = abs(sought_aura - current_aura)
    return 5 + 2 * gap


def ease_text(ability: str) -> str:
    """The Ease Factors an Ability's details show; "" for any other."""
    if ability == MAGIC_SENSITIVITY:
        return (
            "Ease Factors: a Magic aura 12 - aura; a spell or enchanted item "
            "21 - magnitude; a magical creature 15 - Might / 5. Its score "
            "comes off your Magic Resistance."
        )
    if ability == SECOND_SIGHT:
        return (
            "Ease Factors: an illusion 6 + its magnitude (or the Might's); a "
            "naturally invisible thing 9; a regio level 5 + 2 x the "
            "difference in aura (Regio Levels list each). Usually a simple roll."
        )
    if ability == SENSE_HOLINESS:
        return (
            "Ease Factors: an area 9; a person or object 15; a demon 0 and an "
            "angel hiding its nature 15, both only if you Penetrate. A Divine "
            "power: it takes the Divine column of the realm table."
        )
    return ""
