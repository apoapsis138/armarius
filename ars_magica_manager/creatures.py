"""The Bestiary: the saga's creatures, each a stat block (models.Creature)
found at a place and linked to the records round it.

What is worked out rather than typed: a power's Penetration (Might less
five per Might Point it costs, plus any Penetration bonus, as the core
rules give it), the wound ranges for the creature's Size, and the
creatures found at a place.

Pattern: Composite of trait value objects. A creature is assembled from
the same small parts a Character and a Familiar use, rather than being a
kind of Character; the rules here are plain functions."""

from __future__ import annotations

from . import references, storage, viewing, world
from .models import BodyVis, Creature, CreaturePower, Saga
from .rules import derived, realms, scores

#: What the Bestiary calls a creature with no realm.
MUNDANE = "Mundane"


def add(saga: Saga, name: str) -> Creature:
    """A new creature called `name`, added to the Bestiary."""
    creature = Creature(
        id=storage.generate_unique_id(name, [c.id for c in saga.creatures]),
        name=name,
    )
    saga.creatures.append(creature)
    return creature


def listed(saga: Saga) -> list[Creature]:
    """The Bestiary in order, by name: the creatures whoever is looking
    may read (viewing.shown)."""
    return sorted(viewing.shown(saga.creatures), key=lambda c: c.name.casefold())


def vis_text(vis: BodyVis) -> str:
    """ "2 pawns of Animal, in its head"."""
    pawns = "1 pawn" if vis.pawns == 1 else f"{vis.pawns} pawns"
    where = f", {vis.where}" if vis.where else ""
    return f"{pawns} of {vis.art or 'vis'}{where}"


def has_might(creature: Creature) -> bool:
    """Whether the creature belongs to a realm and so has a Might Score."""
    return bool(creature.realm)


def might_text(creature: Creature) -> str:
    """ "Magic Might 8 (Animal)", or "Mundane" for a beast with no realm."""
    if not has_might(creature):
        return MUNDANE
    form = f" ({creature.might_form})" if creature.might_form else ""
    return f"{creature.realm} Might {creature.might}{form}"


def penetration_ability(creature: Creature, power: CreaturePower) -> int:
    """What the creature's Penetration Ability adds to the power, worked
    out as for a magus: its score and any Puissant bonus, plus 1 when its
    specialty is the power or the power's Form. Without the Ability it
    adds nothing."""
    ability = next((a for a in creature.abilities if a.name == "Penetration"), None)
    if ability is None:
        return 0
    bonus, _ = scores.ability_bonus(creature.virtues_flaws, "Penetration")
    specialty = (ability.specialty or "").strip().lower()
    matches = specialty and specialty in (power.name.lower(), power.form.lower())
    return ability.level + bonus + (1 if matches else 0)


def penetration(
    creature: Creature, power: CreaturePower, *, aura: int = 0, aura_realm: str = ""
) -> int:
    """The power's Penetration: the creature's Might Score less five times
    the power's Might Point cost, plus its Penetration Ability and any
    other bonus the power has, and the aura's modifier for its realm where
    it is used (no roll is made, so it applies directly; DE p. 412). It
    may be zero or less, when the power affects only what has no Magic
    Resistance. The Bestiary shows it without an aura."""
    modifier = (
        realms.aura_modifier(creature.realm, aura_realm, aura)
        if aura and aura_realm and has_might(creature)
        else 0
    )
    return (
        creature.might
        - 5 * power.might_cost
        + penetration_ability(creature, power)
        + power.penetration_bonus
        + modifier
    )


def wound_ranges(creature: Creature) -> list[tuple[str, int, int | None]]:
    """The creature's Damage Table, by its Size."""
    return derived.wound_ranges(creature.size)


def linked_from(saga: Saga, creature: Creature) -> list[str]:
    """The names of the records that link to the creature."""
    return [record.name for record, _ in world.links_to(saga, "creatures", creature.id)]


def deletion_consequences(saga: Saga, creature: Creature) -> list[str]:
    """What deleting the creature does besides removing it."""
    names = linked_from(saga, creature)
    if not names:
        return []
    return [f"The links to it from {', '.join(names)} go; nothing else changes."]


def delete(saga: Saga, creature: Creature) -> None:
    """Remove the creature, and every link to it."""
    for record, link in world.links_to(saga, "creatures", creature.id):
        record.links.remove(link)
    references.forget_ruler(saga, creature)
    saga.creatures.remove(creature)


def icon_concept(creature: Creature) -> str:
    """The artwork concept a creature's picture shows: its realm's, or a
    beast's (the familiar's) for a mundane one."""
    return creature.realm.lower() if creature.realm else "familiar"
