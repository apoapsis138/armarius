"""A saga's own Abilities, kept with the saga beside the Ability catalog:
mostly a Supernatural Ability the troupe designs for a tradition of House
Ex Miscellanea or for a storyguide's character, without a front-end.

SOURCE: Houses of Hermes: Societates, Supernatural Abilities, pp. 103-106
-- the Basics and the totals (p. 104), Designing a Supernatural Ability
(pp. 104-105), Accelerated Abilities (p. 104, with Errata (Ars Magica 5th
Edition) p. 60: they are not limited in level at character creation),
and the examples (pp. 105-106). Ars Magica Definitive Edition, Chapter
Five: Abilities, Abilities With No Score, p. 157: a Supernatural Ability
needs one experience point to be used at all, and in most cases a Virtue
to put experience into it.

A designed Ability is the Ability of a Major Supernatural Virtue (p. 104),
though the Definitive Edition also has Minor Virtues that grant an Ability
(Second Sight, p. 106), so its Virtue may be made Minor instead; the app
grants a Supernatural Ability to whoever has a Virtue of its name
(rules.creation_access.granted_supernatural), so adding one can add that
Virtue to the saga's own Virtues too. An Ability on a record is kept by
its name, so renaming one renames it where it is held (and its Virtue).
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from . import catalog, storage
from .markup import escape
from .models import (
    ABILITY_CATEGORIES,
    REALMS,
    SUPERNATURAL_CATEGORIES,
    AbilityDef,
    Saga,
    VirtueFlawDef,
    VirtueFlawTier,
)
from .models.definitions import ROLL_CHARACTERISTICS

SOURCE = (
    "Houses of Hermes: Societates, Supernatural Abilities, pp. 103-106; "
    "Errata (Ars Magica 5th Edition) p. 60; Ars Magica Definitive Edition, "
    "Abilities With No Score, p. 157"
)

#: What the saga's own Abilities may be (a hedge tradition's Arts come
#: with their tradition, not from here).
CATEGORIES: tuple[str, ...] = tuple(c for c in ABILITY_CATEGORIES if c != "Hedge Art")
SUPERNATURAL = "Supernatural"
CHARACTERISTICS = ROLL_CHARACTERISTICS
#: The realm a magus Ex Miscellanea's Ability is assumed to have (p. 104).
DEFAULT_REALM = "Magic"
ID_PREFIX = "custom_ability"
#: A Virtue the form adds beside the Ability: a designed Ability is a
#: Major Supernatural Virtue (p. 104), or Minor when the troupe chooses,
#: as Second Sight is (DE p. 106); its cost by tier.
VIRTUE_TIER: VirtueFlawTier = "Major"
VIRTUE_COSTS: dict[VirtueFlawTier, int] = {"Major": 3, "Minor": 1}
VIRTUE_TIERS: tuple[str, ...] = tuple(VIRTUE_COSTS)


def supernatural(ability: AbilityDef) -> bool:
    return ability.category in SUPERNATURAL_CATEGORIES


def accelerated(ability: AbilityDef) -> bool:
    """On the Art experience table: an Accelerated Ability (p. 104)."""
    return ability.xp_table == "art"


def find(saga: Saga, name: str) -> AbilityDef | None:
    """The saga's own Ability called `name` (any case), if there is one."""
    wanted = name.strip().lower()
    return next((a for a in saga.custom_abilities if a.name.lower() == wanted), None)


def _every_ability(saga: Saga) -> list[AbilityDef]:
    """The catalog's Abilities and `saga`'s own, whichever saga is in use."""
    in_use = catalog.saga_abilities()
    shared = [a for a in catalog.load_ability_catalog() if a not in in_use]
    return [*shared, *saga.custom_abilities]


def _every_virtue_flaw(saga: Saga) -> list[VirtueFlawDef]:
    """The catalog's Virtues and Flaws and `saga`'s own (a saga's own ids
    start "custom_", as house_rules makes them)."""
    shared = [
        vf
        for vf in catalog.load_virtue_flaw_catalog()
        if not vf.id.startswith("custom_")
    ]
    return [*shared, *saga.custom_virtues_flaws]


# -------------------------------------------------------------- holders


def _records(saga: Saga) -> list[Any]:
    """Every record that holds Abilities: characters, familiars, creatures."""
    return [*saga.characters, *saga.familiars, *saga.creatures]


def used_by(saga: Saga, ability: AbilityDef) -> list[str]:
    """The names of the records holding the Ability (it can't be deleted
    while any does)."""
    return [
        record.name
        for record in _records(saga)
        if any(held.name == ability.name for held in record.abilities)
    ]


def paired_virtue(saga: Saga, ability: AbilityDef) -> VirtueFlawDef | None:
    """The saga's own Supernatural Virtue of the Ability's name, which
    grants it."""
    return next(
        (
            vf
            for vf in saga.custom_virtues_flaws
            if vf.name == ability.name and vf.category == SUPERNATURAL
        ),
        None,
    )


# ----------------------------------------------------------------- form


def form_problem(
    saga: Saga, values: dict[str, Any], existing: AbilityDef | None = None
) -> str | None:
    """What's wrong with a form's values, if anything: a name no catalog
    or saga Ability has, a known category, realm and Characteristic, and
    no change of experience table while the Ability is held (its score
    would change under its holders)."""
    name = (values.get("name") or "").strip()
    if not name:
        return "Name is required."
    if "{" in name or "}" in name:
        return "An Ability's name can't have { or }."
    category = values.get("category") or SUPERNATURAL
    if category not in CATEGORIES:
        return f"Category must be one of {', '.join(CATEGORIES)}."
    realm = values.get("realm") or ""
    if realm and realm not in REALMS:
        return f"Realm must be one of {', '.join(REALMS)}."
    characteristic = values.get("characteristic") or ""
    if characteristic and characteristic not in CHARACTERISTICS:
        return f"Characteristic must be one of {', '.join(CHARACTERISTICS)}."
    for other in _every_ability(saga):
        if existing is not None and other.id == existing.id:
            continue
        if other.name.lower() == name.lower():
            whose = "the saga" if other in saga.custom_abilities else "the catalog"
            return f"{escape(other.name)} is already an Ability of {whose}."
    if (
        existing is not None
        and used_by(saga, existing)
        and bool(values.get("accelerated")) != accelerated(existing)
    ):
        return (
            f"{escape(existing.name)} is held, so whether it is Accelerated "
            "can't change: its holders' scores would."
        )
    return None


def _fields(values: dict[str, Any]) -> dict[str, Any]:
    category = values.get("category") or SUPERNATURAL
    special = category in SUPERNATURAL_CATEGORIES
    return {
        "name": values["name"].strip(),
        "category": category,
        "realm": (values.get("realm") or "") if special else "",
        "characteristic": values.get("characteristic") or "",
        "xp_table": "art" if special and values.get("accelerated") else "ability",
        "description": values.get("description") or "",
        "source": values.get("source") or "",
    }


def add(saga: Saga, values: dict[str, Any]) -> AbilityDef:
    """Add one of the saga's own Abilities from a form's values (name,
    category, realm, characteristic, accelerated, description, source).
    With `with_virtue`, a Supernatural one also gets its Supernatural
    Virtue among the saga's own Virtues (Major, or the `virtue_tier`
    chosen), unless a Virtue of its name is already offered."""
    fields = _fields(values)
    taken = [a.id for a in _every_ability(saga)]
    made = AbilityDef(
        id=storage.generate_unique_id(f"{ID_PREFIX}_{fields['name']}", taken),
        **fields,
    )
    saga.custom_abilities.append(made)
    if values.get("with_virtue") and supernatural(made):
        tier: VirtueFlawTier = (
            "Minor" if values.get("virtue_tier") == "Minor" else VIRTUE_TIER
        )
        _add_virtue(saga, made, tier)
    catalog.use_saga(saga)
    return made


def _add_virtue(
    saga: Saga, ability: AbilityDef, tier: VirtueFlawTier = VIRTUE_TIER
) -> None:
    known = _every_virtue_flaw(saga)
    if ability.name.lower() in {vf.name.lower() for vf in known}:
        return
    taken = [vf.id for vf in known]
    saga.custom_virtues_flaws.append(
        VirtueFlawDef(
            id=storage.generate_unique_id(f"custom_vf_{ability.name}", taken),
            name=ability.name,
            type="Virtue",
            category=SUPERNATURAL,
            tier=tier,
            cost=VIRTUE_COSTS[tier],
            description=(
                f"Grants the Supernatural Ability {ability.name} (the saga's own; "
                "Houses of Hermes: Societates p. 104)."
            ),
            source=ability.source,
        )
    )


def update(saga: Saga, ability: AbilityDef, values: dict[str, Any]) -> AbilityDef:
    """Change one of the saga's own Abilities (its id stays). A new name or
    category goes to every record holding it, and a new name to its
    paired Virtue. Returns the changed Ability."""
    changed = replace(ability, **_fields(values))
    index = next(i for i, a in enumerate(saga.custom_abilities) if a is ability)
    saga.custom_abilities[index] = changed
    for record in _records(saga):
        for held in record.abilities:
            if held.name == ability.name:
                held.name = changed.name
                held.category = changed.category
    virtue = paired_virtue(saga, ability)
    if virtue is not None and changed.name != ability.name:
        at = saga.custom_virtues_flaws.index(virtue)
        saga.custom_virtues_flaws[at] = replace(virtue, name=changed.name)
    catalog.use_saga(saga)
    return changed


def remove(saga: Saga, ability: AbilityDef) -> None:
    """Delete one of the saga's own Abilities (its paired Virtue stays: it
    may be held, and is deleted on its own)."""
    saga.custom_abilities.remove(ability)
    catalog.use_saga(saga)


# ----------------------------------------------------------------- text


def roll_text(ability: AbilityDef) -> str:
    """ "Presence + Control Fertility" (the Characteristic is the
    storyguide's to choose when none is given)."""
    return f"{ability.characteristic or 'Characteristic'} + {ability.name}"


def summary(ability: AbilityDef) -> str:
    """One line for a card: category, realm, Accelerated."""
    parts = [ability.category]
    if ability.realm:
        parts.append(ability.realm)
    if accelerated(ability):
        parts.append("Accelerated")
    return ", ".join(parts)


def rules_lines(ability: AbilityDef) -> list[str]:
    """How a Supernatural Ability is used, as markup lines short enough
    for the details panel (HoH: Societates p. 104; nothing for another
    category)."""
    if not supernatural(ability):
        return []
    level = "its Casting Total" if accelerated(ability) else "5 x its score"
    lines = [
        f"[b]Casting Total:[/] {escape(roll_text(ability))} + aura + die, "
        "against the Ease Factor the storyguide sets. [b]Penetration:[/] "
        "Casting Total - Ease Factor + Penetration bonus.",
        f"[b]As a spell:[/] level {level}. Vis up to its score in pawns: +1 "
        "and a botch die each.",
    ]
    if accelerated(ability):
        lines.append(
            "[b]Accelerated:[/] on the Art table; Puissant gives +2; not "
            "studied from vis (Societates p. 104); not limited at creation "
            "(Errata p. 60)."
        )
    return lines


def detail_lines(saga: Saga, ability: AbilityDef) -> list[str]:
    """The details panel's lines (markup) for one of the saga's own
    Abilities: what it is, its Virtue, who holds it, and its rules."""
    holders = used_by(saga, ability)
    held = f"[b]Held by:[/] {escape(', '.join(holders)) if holders else '(no one yet)'}"
    lines = [
        f"[b]{escape(ability.name)}[/]",
        f"[b]For:[/] Ability   [b]Category:[/] {escape(summary(ability))}",
    ]
    if supernatural(ability):
        virtue = paired_virtue(saga, ability)
        granted = (
            f"the {virtue.tier} Virtue {escape(virtue.name)}"
            if virtue is not None
            else "a Virtue of its name"
        )
        lines.append(f"[b]Granted by:[/] {granted}   {held}")
        return [*lines, "", *rules_lines(ability)]
    return [*lines, f"[b]Rolls:[/] {escape(roll_text(ability))}   {held}"]
