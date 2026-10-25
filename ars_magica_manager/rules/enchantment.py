"""Enchanted devices as the rules read them: a device's capacity for
effects (its materials and size, or a talisman's), each effect's level
with its modifications and the vis it takes to instil, whether the
device has been opened, and a magus's talisman. The devices' lists,
forms and text are enchanted_devices.py's."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from ..arts import FORMS, TECHNIQUES
from ..models import (
    CHARGED,
    EFFECT_FREQUENCIES,
    ENCHANT_MATERIALS,
    ENCHANT_SIZES,
    INVESTED,
    PAY_HIGHEST,
    BondPower,
    Character,
    DeviceComponent,
    EnchantedDevice,
    InstilledEffect,
    Saga,
)
from .rounding import round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Enchantments, pp. 252-260"
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


def covenant_devices(
    saga: Saga, covenant_id: str, *, every_lab: bool = False
) -> list[EnchantedDevice]:
    """The enchanted devices a covenant's Build Points pay for: those it
    holds, then those held by its starting laboratories (`every_lab`: by
    any of its laboratories)."""
    found = held_by(saga, "covenant", covenant_id)
    for lab in saga.laboratories:
        if lab.covenant_id == covenant_id and (every_lab or lab.starting):
            found += held_by(saga, "laboratory", lab.id)
    return found


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


def _level_parts(
    level: int,
    uses_per_day: str | None,
    penetration: int,
    modifications: Sequence[tuple[str, int]],
    *,
    weak: bool = False,
) -> list[tuple[str, int]]:
    """The effect level, the uses-per-day addition (None: none, as on a
    Charged Item), Penetration (a level per 2 points, rounded up) and each
    modification's levels (DE pp. 256-258)."""
    parts = [("level", level)]
    if uses_per_day is not None:
        uses = EFFECT_FREQUENCIES.get(uses_per_day, 0)
        if uses:
            parts.append((f"{uses_text(uses_per_day)}", uses))
    if penetration > 0 and weak:
        # Weak Magic gives half the benefit: +1 a level (DE p. 152).
        parts.append((f"Pen {penetration} (Weak Magic)", penetration))
    elif penetration > 0:
        # Each added level gives +2 Penetration, so an odd score takes the
        # next level up (DE p. 257).
        parts.append((f"Pen {penetration}", round_up(penetration / 2)))
    return parts + list(modifications)


def level_breakdown(
    device: EnchantedDevice, effect: InstilledEffect
) -> list[tuple[str, int]]:
    """What makes up the modified level (DE ch. 8, Designing the Effect):
    the effect level, the uses-per-day addition (not on a Charged Item),
    Penetration (a level per 2 points, rounded up) and each modification."""
    return _level_parts(
        effect.level,
        None if device.type == CHARGED else effect.uses_per_day,
        effect.penetration,
        [
            (label, levels)
            for flag, label, levels in MODIFICATIONS
            if getattr(effect, flag)
        ],
        weak=effect.weak_penetration,
    )


#: The modifications a familiar's bond power can take: its powers target
#: only the magus and familiar, who control each other's, so a restriction
#: on who may use it has no meaning (DE pp. 267-268).
BOND_MODIFICATIONS: tuple[tuple[str, str, int], ...] = tuple(
    m for m in MODIFICATIONS if m[0] != "restricted_use"
)


def frequency_of(uses: int) -> str:
    """The Effect Frequency row a bond power's count of uses a day is
    priced at: the row at or above it, and 0 (or more than 50) unlimited
    (DE p. 256)."""
    counts = sorted(int(k) for k in EFFECT_FREQUENCIES if k.isdigit())
    return next((str(c) for c in counts if uses > 0 and c >= uses), "Unlimited")


def bond_power_breakdown(power: BondPower) -> list[tuple[str, int]]:
    """What makes up a bond power's modified level. Investing a power in
    the bond follows the rules for an invested device's effect (DE pp.
    267-268), so a worked-out power adds its uses per day, Penetration and
    modifications to its effect level; otherwise its Level is the modified
    level as typed."""
    if not power.worked_out:
        return [("level", power.level)]
    return _level_parts(
        power.level,
        frequency_of(power.uses_per_day),
        power.penetration,
        [
            (label, levels)
            for flag, label, levels in BOND_MODIFICATIONS
            if getattr(power, flag)
        ],
    )


def bond_power_level(power: BondPower) -> int:
    """The modified level a bond power is instilled at: what the Lab Total
    must exceed, the points it needs and its vis (a pawn per 10 levels)."""
    return sum(levels for _, levels in bond_power_breakdown(power))


def split_vis(
    arts: Sequence[str], chosen: str, other: int, pawns: int
) -> dict[str, int]:
    """The pawns of each Art an effect, a bond power or a familiar's
    binding is paid with: each pawn may be of the work's Technique or its
    Form, in any mix (DE pp. 258, 266-268). `other` of the Art that isn't
    `chosen` (at most `pawns`), the rest of `chosen`; Arts paying none are
    left out."""
    second = next((a for a in arts if a and a != chosen), "")
    of_other = min(max(0, other), pawns) if second else 0
    cost = {chosen: pawns - of_other, second: of_other}
    return {art: n for art, n in cost.items() if art and n}


def vis_shortfall(split: Mapping[str, int], pool: Mapping[str, int], whose: str) -> str:
    """What raw vis `split` (pawns of each Art) is short of in `pool`
    (keyed by lower-case Art), said of `whose` ("Lucia's"), or ""."""
    for art, needed in split.items():
        held = pool.get(art.lower(), 0)
        if held < needed:
            return f"It takes {needed} pawns of {art} vis; {whose} raw vis has {held}."
    return ""


# -- using a device (DE p. 259, Using Enchanted Devices) --

USE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Using Enchanted "
    "Devices, p. 259; Fast Trigger, p. 257"
)
#: A Fast Trigger's Initiative bonus (DE p. 257).
FAST_TRIGGER_INITIATIVE = 3


def use_initiative(effect: InstilledEffect, quickness: int) -> int:
    """What a device's effect goes off at before the stress die: the
    wielder's Quickness, +3 with a Fast Trigger. No Fatigue is rolled."""
    return quickness + (FAST_TRIGGER_INITIATIVE if effect.fast_trigger else 0)


def uses_left_today(effect: InstilledEffect) -> int | None:
    """How many more times the effect can be used today (None:
    unlimited)."""
    if not effect.uses_per_day.isdigit():
        return None
    return max(0, int(effect.uses_per_day) - effect.uses_today)


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


def pawns_used(device: EnchantedDevice, starting: InstilledEffect | None = None) -> int:
    """The capacity the effects take: the vis of every effect instilled or
    begun (an effect's vis is spent in its first season), unknown ones
    included, and of `starting`, the one about to be begun. An effect
    planned but not begun takes none yet (DE p. 258)."""
    return sum(
        vis_cost(device, effect)
        for effect in device.effects
        if effect is starting
        or effect.instilling_progress is None
        or effect.instilling_progress > 0
    )


def uses_text(uses_per_day: str) -> str:
    return "unlimited" if uses_per_day == "Unlimited" else f"{uses_per_day}/day"


def effect_name(effect: InstilledEffect) -> str:
    return effect.name if effect.known else "(unknown power)"
