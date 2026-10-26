"""Conciatta's breakthroughs: the Hermetic Virtues that turn a magus's
Realm Lores on auras (Legends of Hermes pp. 14-16).

- **Confluence of the Realms** (Minor): a lab text's realm may be changed
  when it is used again, so a realm-specific spell gets a variant aligned
  to another realm; and vis may be extracted in an aura of any realm, the
  extraction total taking the usual aura modifier, the vis being that
  aura's (with its side effects).
- **Insight of the Realms** (Minor): in a Ritual or ceremonial casting
  within (or about) a realm, the realm's Lore may stand in for Artes
  Liberales or for Philosophiae; and the realm's Lore can find and see
  through a regio boundary in place of Second Sight or Sense Holiness and
  Unholiness, as an ability aligned to the aura it is in.
- **True Understanding of the Realms** (Major): in an aura of another
  realm, its strength counts less by his score in that realm's Lore (not
  below 0), for its penalty and its extra botch dice; where the aura gives
  a bonus (Hermetic magic in a Faerie aura), the bonus stays and only the
  botch dice fall. The aura's other effects (an aligned aura's feeling,
  an Abyssal regio's loss of Characteristics) fall by it too. It is part
  of his Gift, as his sigil is: his devices keep the Lore he had when he
  made each effect for their Penetration, his talisman his Lore now.

Each takes 30 research points to integrate (True Understanding 45, or 30
once one of the others is integrated).

The Lores are Dominion Lore, Faerie Lore, Infernal Lore and Magic Lore.
"""

from __future__ import annotations

from ..models import Character
from . import scores

SOURCE = "Legends of Hermes, Conciatta, New Virtues, pp. 14-16"

CONFLUENCE = "vf_confluence_of_the_realms"
INSIGHT = "vf_insight_of_the_realms"
TRUE_UNDERSTANDING = "vf_true_understanding_of_the_realms"

#: Each realm's Lore.
LORES: dict[str, str] = {
    "Magic": "Magic Lore",
    "Faerie": "Faerie Lore",
    "Divine": "Dominion Lore",
    "Infernal": "Infernal Lore",
}

#: The Abilities a Ritual or ceremonial casting's learning comes from,
#: one of which Insight of the Realms lets the realm's Lore replace.
LEARNING: tuple[str, ...] = ("Artes Liberales", "Philosophiae")

#: The research points to integrate each.
INTEGRATION: dict[str, int] = {CONFLUENCE: 30, INSIGHT: 30, TRUE_UNDERSTANDING: 45}
#: True Understanding's, once Confluence or Insight is integrated.
TRUE_UNDERSTANDING_AFTER = 30


def has(magus: Character, vf_id: str) -> bool:
    return any(vf.vf_id == vf_id for vf in magus.virtues_flaws)


def lore(magus: Character, realm: str) -> int:
    """His score in `realm`'s Lore, Puissant counted (0 without it)."""
    name = LORES.get(realm)
    if name is None:
        return 0
    found = next((a for a in magus.abilities if a.name == name), None)
    if found is None:
        return 0
    return found.level + scores.ability_bonus(magus.virtues_flaws, name)[0]


def understood(magus: Character, aura_realm: str) -> int:
    """How much of an aura of another realm True Understanding of the
    Realms takes away: his score in its Lore (0 without the Virtue, or in
    a Magic aura, his own)."""
    if aura_realm == "Magic" or not has(magus, TRUE_UNDERSTANDING):
        return 0
    return max(0, lore(magus, aura_realm))


def effective_aura(magus: Character, aura_realm: str, aura: int) -> int:
    """The aura's strength as it weighs on him: less his Lore of its realm
    under True Understanding of the Realms, never below 0."""
    return max(0, aura - understood(magus, aura_realm))


def ritual_lore(magus: Character, aura_realm: str, aura: int) -> tuple[str, int] | None:
    """The realm's Lore Insight of the Realms lets a Ritual or ceremonial
    casting in an aura of that realm use for Artes Liberales or
    Philosophiae: (its name, its score), or None without the Virtue, the
    aura, or any Lore."""
    if aura <= 0 or not has(magus, INSIGHT) or aura_realm not in LORES:
        return None
    score = lore(magus, aura_realm)
    return (LORES[aura_realm], score) if score > 0 else None


def learning_scores(
    found: dict[str, int], magus: Character, aura_realm: str, aura: int
) -> dict[str, int]:
    """A Ritual's Artes Liberales and Philosophiae scores (`found`), the
    lower one replaced by the realm's Lore under Insight of the Realms when
    that is better: {label: score}."""
    insight = ritual_lore(magus, aura_realm, aura)
    if insight is None:
        return found
    name, score = insight
    lowest = min(LEARNING, key=lambda key: found.get(key, 0))
    if score <= found.get(lowest, 0):
        return found
    swapped = {key: value for key, value in found.items() if key != lowest}
    swapped[f"{name} (for {lowest}, Insight of the Realms)"] = score
    return swapped


def regio_abilities(magus: Character, realm: str) -> tuple[str, ...]:
    """The realm's Lore, when Insight of the Realms lets it find and see
    through that realm's regio boundaries (() otherwise)."""
    if not has(magus, INSIGHT) or realm not in LORES:
        return ()
    return (LORES[realm],)
