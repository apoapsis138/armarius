"""Covenant rules computed from a Covenant and the Boon/Hook catalog:
Boon and Hook points, the effective Aura, and the modifiers its
Boons/Hooks carry."""

from __future__ import annotations

from .models import (
    BOON_HOOK_UNKNOWN,
    Character,
    Covenant,
    CovenantBoonHookDef,
    CovenantSituationDef,
    Modifier,
    Saga,
    VirtueFlawInstance,
    boon_hook_params,
    new_instance_id,
)
from .rules import effects, realms

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
) -> float:
    """Total points the covenant's attached Boons cost."""
    return sum(
        boon_hook_points(bh, definition)
        for bh in covenant.boons_hooks
        if (definition := catalog_by_id.get(bh.vf_id)) is not None
        and definition.type == "Boon"
    )


def covenant_hook_points(
    covenant: Covenant, catalog_by_id: dict[str, CovenantBoonHookDef]
) -> float:
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
    """The covenant's Aura score (rules.realms.covenant_aura): its base
    `aura` plus every `covenant_aura` modifier of its Boons/Hooks. This is
    what its laboratories inherit."""
    return int(realms.covenant_aura(covenant, catalog_by_id).total)


def home_aura(saga: Saga, character: Character) -> tuple[int, str]:
    """The aura (score, realm) a character lives in: their covenant's
    effective Aura (its Boons and Hooks included); 0 Magic without one. The
    one place this is worked out (STORY-1129: casting totals, vis study,
    aging and warping all use it)."""
    from . import catalog

    covenant = saga.covenant(character.covenant_id)
    if covenant is None:
        return 0, realms.HERMETIC
    boons = catalog.load_covenant_boon_hook_catalog_by_id()
    return covenant_effective_aura(covenant, boons), covenant.aura_realm


def covenant_source(
    covenant: Covenant, catalog_by_id: dict[str, CovenantBoonHookDef]
) -> effects.EffectSource:
    """The covenant's Boons and Hooks as a source for the shared effect
    lookup (rules.effects)."""
    return effects.EffectSource("covenant", covenant.boons_hooks, catalog_by_id)


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
    both count. The covenant end of the shared lookup (rules.effects)."""
    return [
        (effect.entry, effect.modifier)  # type: ignore[misc]
        for effect in effects.collect(
            [covenant_source(covenant, catalog_by_id)], applies_to, activity=activity
        )
    ]


def covenant_modifier_total(
    covenant: Covenant,
    catalog_by_id: dict[str, CovenantBoonHookDef],
    applies_to: str,
    activity: str | None = None,
) -> float:
    """The sum of the flat `amount`s of covenant_modifiers()."""
    return effects.amount_total(
        effects.collect(
            [covenant_source(covenant, catalog_by_id)], applies_to, activity=activity
        )
    )


# -- Covenant Situations and what doesn't fit together (STORY-703) --

MINOR_POVERTY = "covbh_hook_minor_poverty"
MAJOR_POVERTY = "covbh_hook_major_poverty"


def situation_instances(situation: CovenantSituationDef) -> list[VirtueFlawInstance]:
    """The Boons, Hooks and Free Choices a Covenant Situation adds, one
    instance each time an entry is taken."""
    return [
        VirtueFlawInstance(
            vf_id=entry["vf_id"],
            params=boon_hook_params(entry.get("detail", ""), ""),
            id=new_instance_id(),
        )
        for entry in situation.entries
        for _ in range(entry.get("count", 1))
    ]


def situation_points(
    situation: CovenantSituationDef, catalog_by_id: dict[str, CovenantBoonHookDef]
) -> tuple[float, float]:
    """(Hook points, Boon points) a Covenant Situation comes to."""
    hooks = boons = 0.0
    for entry in situation.entries:
        definition = catalog_by_id.get(entry["vf_id"])
        if definition is None:
            continue
        points = abs(definition.cost) * entry.get("count", 1)
        if definition.type == "Hook":
            hooks += points
        else:
            boons += points
    return hooks, boons


def boon_hook_problems(
    covenant: Covenant, catalog_by_id: dict[str, CovenantBoonHookDef]
) -> list[str]:
    """What doesn't fit together among the covenant's Boons and Hooks
    (plain text): two the catalog says exclude each other (the Minor
    Poverty Hook with Secondary Income or Wealth), and income the Poverty
    Hook doesn't allow -- Minor: one Lesser source only; Major: none."""
    held = [bh.vf_id for bh in covenant.boons_hooks if bh.vf_id in catalog_by_id]
    problems: list[str] = []

    def label(vf_id: str) -> str:
        definition = catalog_by_id[vf_id]
        return f"{definition.name} ({definition.tier} {definition.type})"

    seen: set[tuple[str, str]] = set()
    for vf_id in held:
        for other in catalog_by_id[vf_id].excludes:
            pair = (vf_id, other)
            if other in held and other in catalog_by_id and pair not in seen:
                seen.add(pair)
                seen.add((other, vf_id))
                problems.append(f"{label(vf_id)} can't be taken with {label(other)}.")
    sources = covenant.economics.income_sources
    if MAJOR_POVERTY in held and sources:
        problems.append(
            f"Poverty (Major Hook): the covenant has no source of income, but "
            f"{len(sources)} listed."
        )
    elif MINOR_POVERTY in held and (
        len(sources) > 1 or any(s.type != "Lesser" for s in sources)
    ):
        listed = ", ".join(f"{s.name or 'unnamed'} ({s.type})" for s in sources)
        problems.append(
            "Poverty (Minor Hook): the covenant has one Lesser source of income "
            f"only, but has {listed}."
        )
    return problems
