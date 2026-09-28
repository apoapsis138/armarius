"""Covenant rules computed from a Covenant and the Boon/Hook catalog:
Boon and Hook points, the effective Aura, and the modifiers its
Boons/Hooks carry."""

from __future__ import annotations

from .models import (
    BOON_HOOK_UNKNOWN,
    Covenant,
    CovenantBoonHookDef,
    Modifier,
    VirtueFlawInstance,
    round_away_from_zero,
)

#: What an Unknown Minor Hook counts for balancing: as a Major Hook.
UNKNOWN_HOOK_POINTS = 3


def boon_hook_is_unknown(
    instance: VirtueFlawInstance, definition: CovenantBoonHookDef
) -> bool:
    """Whether an attached Hook is marked Unknown -- honoured only for a
    catalog entry that may be Unknown, so a stale mark counts for nothing."""
    return definition.unknown and instance.params.get(BOON_HOOK_UNKNOWN) == "yes"


def boon_hook_points(
    instance: VirtueFlawInstance, definition: CovenantBoonHookDef
) -> float:
    """The points one attached Boon costs or Hook provides (positive either
    way): its catalog cost, or UNKNOWN_HOOK_POINTS for an Unknown Hook."""
    if boon_hook_is_unknown(instance, definition):
        return UNKNOWN_HOOK_POINTS
    return abs(definition.cost)


def covenant_boon_points(
    covenant: Covenant, catalog_by_id: dict[str, CovenantBoonHookDef]
) -> int:
    """Total points the covenant's attached Boons cost."""
    return sum(
        boon_hook_points(bh, definition)
        for bh in covenant.boons_hooks
        if (definition := catalog_by_id.get(bh.vf_id)) is not None
        and definition.type == "Boon"
    )


def covenant_hook_points(
    covenant: Covenant, catalog_by_id: dict[str, CovenantBoonHookDef]
) -> int:
    """Total points the covenant's attached Hooks provide (a positive
    number -- Hooks are stored with negative costs, like Flaws); an Unknown
    Minor Hook provides 3."""
    return sum(
        boon_hook_points(bh, definition)
        for bh in covenant.boons_hooks
        if (definition := catalog_by_id.get(bh.vf_id)) is not None
        and definition.type == "Hook"
    )


def covenant_effective_aura(
    covenant: Covenant, catalog_by_id: dict[str, CovenantBoonHookDef]
) -> int:
    """The covenant's Aura score: its base `aura` plus every `covenant_aura`
    modifier of its Boons/Hooks (each Minor Aura Boon adds 1). This is what
    its laboratories inherit."""
    return covenant.aura + round_away_from_zero(
        covenant_modifier_total(covenant, catalog_by_id, "covenant_aura")
    )


def covenant_modifiers(
    covenant: Covenant,
    catalog_by_id: dict[str, CovenantBoonHookDef],
    applies_to: str,
    activity: str | None = None,
) -> list[tuple[CovenantBoonHookDef, Modifier]]:
    """Every modifier of type `applies_to` on the covenant's Boons/Hooks, with
    the entry it comes from -- one pair per attached *instance*, so a Boon
    taken three times appears three times (effects stack). Given an
    `activity`, modifiers for that activity and general ones (no activity)
    both count, per Modifier's rules.

    This is the covenant end of the one lookup every total will use (DESIGN.md
    section 5.1): Virtues & Flaws on characters and
    laboratories will be collected the same way."""
    found = []
    for instance in covenant.boons_hooks:
        entry = catalog_by_id.get(instance.vf_id)
        if entry is None:
            continue
        for modifier in entry.modifiers:
            if modifier.applies_to != applies_to:
                continue
            if activity is not None and modifier.activity not in (None, activity):
                continue
            found.append((entry, modifier))
    return found


def covenant_modifier_total(
    covenant: Covenant,
    catalog_by_id: dict[str, CovenantBoonHookDef],
    applies_to: str,
    activity: str | None = None,
) -> float:
    """The sum of the flat `amount`s of covenant_modifiers(). (No covenant
    effect uses a multiplier yet; how multipliers stack with amounts is for
    the Totals Engine to settle.)"""
    return sum(
        modifier.amount or 0
        for _, modifier in covenant_modifiers(
            covenant, catalog_by_id, applies_to, activity
        )
    )
