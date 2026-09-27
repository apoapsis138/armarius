"""Covenant rules computed from a Covenant and the Boon/Hook catalog:
Boon and Hook points, the effective Aura, and the modifiers its
Boons/Hooks carry."""

from __future__ import annotations

from .models import (
    Covenant,
    CovenantBoonHookDef,
    Modifier,
    round_away_from_zero,
)


def covenant_boon_points(
    covenant: Covenant, catalog_by_id: dict[str, CovenantBoonHookDef]
) -> int:
    """Total points the covenant's attached Boons cost."""
    return sum(
        definition.cost
        for bh in covenant.boons_hooks
        if (definition := catalog_by_id.get(bh.vf_id)) is not None
        and definition.type == "Boon"
    )


def covenant_hook_points(
    covenant: Covenant, catalog_by_id: dict[str, CovenantBoonHookDef]
) -> int:
    """Total points the covenant's attached Hooks provide (a positive
    number -- Hooks are stored with negative costs, like Flaws)."""
    return sum(
        -definition.cost
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
