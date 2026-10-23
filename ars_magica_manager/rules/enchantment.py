"""Enchanted devices as the rules read them: a device's capacity for
effects (its materials and size, or a talisman's), each effect's level
with its modifications and the vis it takes to instil, whether the
device has been opened, and a magus's talisman. The devices' lists,
forms and text are enchanted_devices.py's."""

from __future__ import annotations

from collections.abc import Sequence

from ..arts import FORMS, TECHNIQUES
from ..models import (
    CHARGED,
    EFFECT_FREQUENCIES,
    ENCHANT_MATERIALS,
    ENCHANT_SIZES,
    INVESTED,
    PAY_HIGHEST,
    Character,
    DeviceComponent,
    EnchantedDevice,
    InstilledEffect,
    Saga,
)
from .rounding import round_down, round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Enchantments "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eight:"
    "_Laboratory#Enchantments)"
)


#: Level additions for the effect modifications (DE ch. 8, Effect
#: Modifications), as (InstilledEffect flag, label, levels).
MODIFICATIONS: tuple[tuple[str, str, int], ...] = (
    ("maintains_concentration", "Item maintains concentration", 5),
    ("restricted_use", "Restricted use", 3),
    ("environmental_trigger", "Environmental trigger", 3),
    ("fast_trigger", "Fast trigger", 5),
    ("linked_trigger", "Linked trigger", 3),
)


def held_by(saga: Saga, kind: str, holder_id: str) -> list[EnchantedDevice]:
    """The devices `kind` `holder_id` holds, its talismans first, then in the
    order they were added."""
    held = [
        d
        for d in saga.enchanted_devices
        if d.holder_kind == kind and d.holder_id == holder_id
    ]
    return sorted(held, key=lambda d: not is_talisman(d))


def is_talisman(device: EnchantedDevice) -> bool:
    return device.type == INVESTED and device.talisman


def talisman_magus_id(device: EnchantedDevice) -> str | None:
    """Whose talisman `device` is: its maker, else the character holding it."""
    if device.maker_id:
        return device.maker_id
    return device.holder_id if device.holder_kind == "character" else None


def talisman_of(saga: Saga, character: Character) -> EnchantedDevice | None:
    """The character's talisman, if they have one."""
    return next(
        (
            d
            for d in saga.enchanted_devices
            if is_talisman(d) and talisman_magus_id(d) == character.id
        ),
        None,
    )


def component_capacity(component: DeviceComponent) -> int:
    """Material base x size multiplier (DE ch. 8, Material and Size Tables)."""
    return ENCHANT_MATERIALS.get(component.material, 0) * ENCHANT_SIZES.get(
        component.size, 0
    )


def talisman_capacity(saga: Saga, device: EnchantedDevice) -> int | None:
    """The magus's highest Technique + highest Form (DE ch. 8, Talisman
    Attunement), or None with no magus to take them from."""
    magus = saga.character(talisman_magus_id(device))
    if magus is None:
        return None

    def highest(arts: Sequence[str]) -> int:
        return max(
            (magus.arts[a.lower()].level for a in arts if a.lower() in magus.arts),
            default=0,
        )

    return highest(TECHNIQUES) + highest(FORMS)


def material_capacity(device: EnchantedDevice) -> int | None:
    """What the components' Material and Size give: their sum, or the highest
    one for a compound invested item paid that way (DE ch. 8, Preparation
    for Enchantment); None with no components."""
    if not device.components:
        return None
    capacities = [component_capacity(c) for c in device.components]
    if device.type == INVESTED and device.payment == PAY_HIGHEST:
        return max(capacities)
    return sum(capacities)


def computed_capacity(saga: Saga, device: EnchantedDevice) -> int | None:
    """The capacity in pawns as the rules give it (None: nothing to work it
    out from, or a Charged Item, which has none)."""
    if device.type == CHARGED:
        return None
    if is_talisman(device):
        return talisman_capacity(saga, device)
    return material_capacity(device)


def capacity(saga: Saga, device: EnchantedDevice) -> int | None:
    """The capacity in pawns: the override if set, else worked out."""
    if device.capacity_override is not None:
        return device.capacity_override
    return computed_capacity(saga, device)


def is_opened(saga: Saga, device: EnchantedDevice) -> bool:
    total = capacity(saga, device)
    return total is not None and device.pawns_opened >= total


def level_breakdown(
    device: EnchantedDevice, effect: InstilledEffect
) -> list[tuple[str, int]]:
    """What makes up the modified level (DE ch. 8, Designing the Effect):
    the effect level, the uses-per-day addition (not on a Charged Item),
    Penetration (+1 per 2 points) and each modification."""
    parts = [("level", effect.level)]
    if device.type != CHARGED:
        uses = EFFECT_FREQUENCIES.get(effect.uses_per_day, 0)
        if uses:
            parts.append((f"{uses_text(effect.uses_per_day)}", uses))
    if effect.penetration > 0:
        parts.append((f"Pen {effect.penetration}", round_down(effect.penetration / 2)))
    parts += [
        (label, levels)
        for flag, label, levels in MODIFICATIONS
        if getattr(effect, flag)
    ]
    return parts


def computed_modified_level(device: EnchantedDevice, effect: InstilledEffect) -> int:
    return sum(levels for _, levels in level_breakdown(device, effect))


def modified_level(device: EnchantedDevice, effect: InstilledEffect) -> int:
    """The modified level: the override if set, else worked out."""
    if effect.modified_level_override is not None:
        return effect.modified_level_override
    return computed_modified_level(device, effect)


def computed_vis(device: EnchantedDevice, effect: InstilledEffect) -> int:
    """Pawns of vis to instil it: modified level / 10, rounded up (DE ch. 8,
    Instilling the Effect); none for a Charged Item."""
    if device.type == CHARGED:
        return 0
    return round_up(modified_level(device, effect) / 10)


def vis_cost(device: EnchantedDevice, effect: InstilledEffect) -> int:
    if effect.vis_override is not None:
        return effect.vis_override
    return computed_vis(device, effect)


def pawns_used(device: EnchantedDevice) -> int:
    """The capacity the effects take: the vis of every effect, including
    partly instilled and unknown ones."""
    return sum(vis_cost(device, effect) for effect in device.effects)


def uses_text(uses_per_day: str) -> str:
    return "unlimited" if uses_per_day == "Unlimited" else f"{uses_per_day}/day"


def effect_name(effect: InstilledEffect) -> str:
    return effect.name if effect.known else "(unknown power)"
