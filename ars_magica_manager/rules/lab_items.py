"""Magic items in a laboratory (Covenants, Magic Items for Laboratories;
DE ch. 8): what each effect of an item installed in the lab gives it.

An item is installed as a Free Magic Item Virtue (Minor when very large),
or as an Enchantment of the lab itself. Each of its effects then either

- duplicates a laboratory Virtue or Flaw and simply grants it: gained at
  once, with no space cost (and so no Build Points at creation), its
  modifications applied as usual; or
- buys points by its final level: one Specialization point for every 10
  levels, one Characteristic point for every 20.

An item gives the lab nothing while its device is kept elsewhere: its
points and the Virtue it grants count only while the device is here.
An effect must be new to the lab: granting a Virtue it has already is
flagged. An item made into a Feature is not this: its Feature Virtue is
paid for as usual (laboratories.py's Features).

The points an item buys reach the lab's totals through `item_source`, an
EffectSource like the lab's own Virtues, so the totals read them the same
way.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from ..models import (
    ITEM_DEVICE_PARAM,
    ITEM_SIZE_PARAM,
    ITEM_VIRTUES,
    VERY_LARGE,
    EnchantedDevice,
    InstilledEffect,
    LabItemBenefit,
    Laboratory,
    LabVirtueFlawDef,
    Modifier,
    Saga,
    VirtueFlawInstance,
)
from . import effects, enchantment

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Magic Items for "
    "Laboratories, p. 298; Covenants, Chapter 9: Laboratory, Magic Items for "
    "Laboratories, p. 121"
)

MAGIC_ITEM = "labvf_magic_item"
ENCHANTMENT = "labvf_enchantment"
#: Levels of an effect per point it buys.
LEVELS_PER_SPECIALIZATION = 10
LEVELS_PER_CHARACTERISTIC = 20
#: A very large Magic Item takes space as a Minor Virtue.
VERY_LARGE_COST = 1
VERY_LARGE_TIER = "Minor"


def is_very_large(instance: VirtueFlawInstance) -> bool:
    return (
        instance.vf_id == MAGIC_ITEM
        and instance.params.get(ITEM_SIZE_PARAM) == VERY_LARGE
    )


def granted_ids(lab: Laboratory) -> set[str]:
    """The ids of the lab's Virtue/Flaw instances a magic item grants."""
    return {b.granted_id for b in lab.item_benefits if b.granted_id}


def granting(lab: Laboratory, instance: VirtueFlawInstance) -> LabItemBenefit | None:
    """The magic item effect that grants `instance`, if one does."""
    return next((b for b in lab.item_benefits if b.granted_id == instance.id), None)


def space_cost(
    lab: Laboratory,
    instance: VirtueFlawInstance,
    definition: LabVirtueFlawDef,
    granted: set[str] | None = None,
) -> float:
    """The points of space `instance` takes: none when a magic item grants
    it, a Minor Virtue's for a very large Magic Item, else its catalog
    cost. (`granted`: granted_ids(lab), when the caller has it.)"""
    if instance.id in (granted_ids(lab) if granted is None else granted):
        return 0
    if is_very_large(instance):
        return VERY_LARGE_COST
    return definition.cost


def tier(
    lab: Laboratory,
    instance: VirtueFlawInstance,
    definition: LabVirtueFlawDef,
    granted: set[str] | None = None,
) -> str:
    """Its tier for Build Points: "Free" when a magic item grants it, Minor
    for a very large Magic Item, else the catalog's."""
    if instance.id in (granted_ids(lab) if granted is None else granted):
        return "Free"
    if is_very_large(instance):
        return VERY_LARGE_TIER
    return definition.tier


# -- the device and effect a benefit names --


def device_of(saga: Saga, benefit: LabItemBenefit) -> EnchantedDevice | None:
    return next((d for d in saga.enchanted_devices if d.id == benefit.device_id), None)


def effect_of(saga: Saga, benefit: LabItemBenefit) -> InstilledEffect | None:
    device = device_of(saga, benefit)
    if device is None:
        return None
    return next((e for e in device.effects if e.id == benefit.effect_id), None)


def level_of(saga: Saga, benefit: LabItemBenefit) -> int | None:
    """The final level of the benefit's effect, None when it's gone."""
    device, effect = device_of(saga, benefit), effect_of(saga, benefit)
    if device is None or effect is None:
        return None
    return enchantment.modified_level(device, effect)


def levels_needed(benefit: LabItemBenefit) -> int:
    """The levels the benefit's points take: 10 a Specialization point,
    20 a Characteristic point."""
    return LEVELS_PER_SPECIALIZATION * sum(
        g.points for g in benefit.specializations
    ) + LEVELS_PER_CHARACTERISTIC * sum(g.points for g in benefit.characteristics)


def budget_problem(
    level: int, specialization_points: int, characteristic_points: int
) -> str:
    """Why points don't fit an effect of `level` ("" when they do)."""
    needed = (
        LEVELS_PER_SPECIALIZATION * specialization_points
        + LEVELS_PER_CHARACTERISTIC * characteristic_points
    )
    if needed <= level:
        return ""
    return (
        f"These points need a level {needed} effect (10 levels a Specialization "
        f"point, 20 a Characteristic point); this one is level {level}."
    )


def held_devices(saga: Saga, lab: Laboratory) -> list[EnchantedDevice]:
    """The devices kept in the laboratory: those a magic item can be."""
    return enchantment.held_by(saga, "laboratory", lab.id)


def item_virtue(lab: Laboratory, device_id: str) -> VirtueFlawInstance | None:
    """The Magic Item or Enchantment Virtue a device is installed as."""
    return next(
        (
            vf
            for vf in lab.virtues_flaws
            if vf.vf_id in ITEM_VIRTUES
            and vf.params.get(ITEM_DEVICE_PARAM) == device_id
        ),
        None,
    )


# -- what's wrong --


def problems(saga: Saga, lab: Laboratory, benefit: LabItemBenefit) -> list[str]:
    """What's wrong with one magic item effect: its device or effect gone,
    the device kept elsewhere, more points than its level buys, or a
    granted Virtue the lab has already."""
    device = device_of(saga, benefit)
    if device is None:
        return ["its device is gone"]
    found = []
    if not is_kept(saga, lab, benefit):
        found.append(f"{device.name} isn't kept in this laboratory: it gives nothing")
    level = level_of(saga, benefit)
    if level is None:
        found.append("its effect is gone")
    elif levels_needed(benefit) > level:
        found.append(
            f"its points need level {levels_needed(benefit)}, the effect is {level}"
        )
    if benefit.granted_id:
        granted = next(
            (vf for vf in lab.virtues_flaws if vf.id == benefit.granted_id), None
        )
        if granted is None:
            found.append("the Virtue it grants is gone")
        elif any(
            vf.vf_id == granted.vf_id and vf.id != granted.id
            for vf in lab.virtues_flaws
        ):
            found.append("the lab has that Virtue already: an effect must be new")
    return found


# -- adding and removing --


def remove(lab: Laboratory, benefit: LabItemBenefit) -> None:
    """Remove a magic item effect with the Virtue it granted, and its item's
    Magic Item or Enchantment Virtue once no other effect is installed as
    it."""
    lab.item_benefits.remove(benefit)
    gone = {benefit.granted_id} if benefit.granted_id else set()
    if benefit.virtue_id and not any(
        b.virtue_id == benefit.virtue_id for b in lab.item_benefits
    ):
        gone.add(benefit.virtue_id)
    lab.virtues_flaws[:] = [vf for vf in lab.virtues_flaws if vf.id not in gone]


def prune(lab: Laboratory) -> None:
    """After a Virtue or Flaw is removed: an effect installed as a Magic
    Item or Enchantment Virtue that went goes too, and one whose granted
    Virtue went is left with no grant (flagged)."""
    ids = {vf.id for vf in lab.virtues_flaws}
    lab.item_benefits[:] = [
        b for b in lab.item_benefits if b.virtue_id is None or b.virtue_id in ids
    ]
    for benefit in lab.item_benefits:
        if benefit.granted_id and benefit.granted_id not in ids:
            benefit.granted_id = None


def forget_device(saga: Saga, device_id: str, effect_id: str | None = None) -> None:
    """A device (or one of its effects) is deleted or destroyed: every
    laboratory loses what it gave."""
    for lab in saga.laboratories:
        for benefit in [
            b
            for b in lab.item_benefits
            if b.device_id == device_id and effect_id in (None, b.effect_id)
        ]:
            remove(lab, benefit)


# -- the points, as an effect source --


@dataclass(frozen=True)
class _ItemEntry:
    """A magic item effect's points, shaped as a catalog entry so the
    effect lookup reads them like a Virtue's modifiers."""

    id: str
    name: str
    type: str = "Virtue"
    modifiers: list[Modifier] = field(default_factory=list)


def _entry(benefit: LabItemBenefit) -> _ItemEntry:
    modifiers = [
        Modifier(
            applies_to="lab_specialization", target=g.specialization, amount=g.points
        )
        for g in benefit.specializations
    ] + [
        Modifier(
            applies_to="lab_characteristic", target=g.characteristic, amount=g.points
        )
        for g in benefit.characteristics
    ]
    return _ItemEntry(
        benefit.id, f"{benefit.name or 'Magic item'} (magic item)", modifiers=modifiers
    )


def is_kept(saga: Saga, lab: Laboratory, benefit: LabItemBenefit) -> bool:
    """Whether the benefit's device is kept in the lab: an item gives the
    lab nothing while it is elsewhere."""
    device = device_of(saga, benefit)
    return device is not None and (device.holder_kind, device.holder_id) == (
        "laboratory",
        lab.id,
    )


def away_grants(saga: Saga, lab: Laboratory) -> set[str]:
    """The ids of the Virtues granted by items not kept in the lab now."""
    return {
        b.granted_id
        for b in lab.item_benefits
        if b.granted_id and not is_kept(saga, lab, b)
    }


def item_source(saga: Saga | None, lab: Laboratory) -> effects.EffectSource:
    """The points the lab's magic items buy, as an EffectSource: one
    instance per effect whose device is kept in the lab (every effect,
    with no saga to look in), its entry carrying a modifier per point
    grant."""
    kept = [b for b in lab.item_benefits if saga is None or is_kept(saga, lab, b)]
    entries: Mapping[str, _ItemEntry] = {b.id: _entry(b) for b in kept}
    instances = [VirtueFlawInstance(vf_id=b.id, id=b.id) for b in kept]
    return effects.EffectSource("magic item", instances, entries)
