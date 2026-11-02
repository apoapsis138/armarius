"""Covenant rules computed from a Covenant and the Boon/Hook catalog:
Boon and Hook points, the effective Aura, and the modifiers its
Boons/Hooks carry."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from .models import (
    BOON_HOOK_DETAIL,
    BOON_HOOK_RESOURCE,
    BOON_HOOK_SITUATION,
    BOON_HOOK_UNKNOWN,
    Covenant,
    CovenantBoonHookDef,
    CovenantSituationDef,
    IncomeSource,
    Modifier,
    Possession,
    VirtueFlawInstance,
    boon_hook_params,
    new_instance_id,
)
from .rules import effects

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
    covenant: Covenant, catalog_by_id: Mapping[str, CovenantBoonHookDef]
) -> float:
    """Total points the covenant's attached Boons cost."""
    return sum(
        boon_hook_points(bh, definition)
        for bh in covenant.boons_hooks
        if (definition := catalog_by_id.get(bh.vf_id)) is not None
        and definition.type == "Boon"
    )


def covenant_hook_points(
    covenant: Covenant, catalog_by_id: Mapping[str, CovenantBoonHookDef]
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


def covenant_source(
    covenant: Covenant, catalog_by_id: Mapping[str, CovenantBoonHookDef]
) -> effects.EffectSource:
    """The covenant's Boons and Hooks as a source for the shared effect
    lookup (rules.effects)."""
    return effects.EffectSource("covenant", covenant.boons_hooks, catalog_by_id)


def covenant_modifiers(
    covenant: Covenant,
    catalog_by_id: Mapping[str, CovenantBoonHookDef],
    applies_to: str,
    activity: str | None = None,
) -> list[tuple[CovenantBoonHookDef, Modifier]]:
    """Every modifier of type `applies_to` on the covenant's Boons/Hooks, with
    the entry it comes from -- one pair per attached *instance*, so a Boon
    taken three times appears three times (effects stack). Given an
    `activity`, modifiers for that activity and general ones (no activity)
    both count. The covenant end of the shared lookup (rules.effects)."""
    return [
        (cast(CovenantBoonHookDef, effect.entry), effect.modifier)
        for effect in effects.collect(
            [covenant_source(covenant, catalog_by_id)], applies_to, activity=activity
        )
    ]


# -- Covenant Situations and what doesn't fit together --

MINOR_POVERTY = "covbh_hook_minor_poverty"
MAJOR_POVERTY = "covbh_hook_major_poverty"
#: The Unknown Hook as its own Major entry: the same Hook as a Minor Hook
#: marked Unknown (DE p. 182), so the two shouldn't both be taken.
UNKNOWN_HOOK = "covbh_hook_major_unknown"
#: The Prestige Boons and the Reputation each gives the covenant (DE pp.
#: 183-184), for the group it names.
PRESTIGE_REPUTATION: dict[str, int] = {
    "covbh_boon_minor_prestige": 3,
    "covbh_boon_major_prestige": 9,
}


def prestige_shortfall(
    covenant: Covenant, catalog_by_id: Mapping[str, CovenantBoonHookDef]
) -> list[str] | None:
    """The Prestige Boons whose Reputation isn't on the covenant's list,
    each as "Prestige (Major Boon) - group: a Reputation of 9"; None
    without a Prestige Boon. Each Boon needs its own good Reputation of at
    least its score, the highest Boons matched first."""
    boons = sorted(
        (bh for bh in covenant.boons_hooks if bh.vf_id in PRESTIGE_REPUTATION),
        key=lambda bh: -PRESTIGE_REPUTATION[bh.vf_id],
    )
    if not boons:
        return None
    left = sorted((r.score for r in covenant.reputations if r.score > 0), reverse=True)
    missing: list[str] = []
    for bh in boons:
        need = PRESTIGE_REPUTATION[bh.vf_id]
        if left and left[0] >= need:
            left.pop(0)
            continue
        definition = catalog_by_id.get(bh.vf_id)
        name = (
            f"{definition.name} ({definition.tier} Boon)"
            if definition is not None
            else bh.vf_id
        )
        detail = bh.params.get(BOON_HOOK_DETAIL)
        missing.append(
            f"{name}{f' - {detail}' if detail else ''}: a Reputation of {need}"
        )
    return missing


def situation_instances(situation: CovenantSituationDef) -> list[VirtueFlawInstance]:
    """The Boons, Hooks and Free Choices a Covenant Situation adds, one
    instance each time an entry is taken, each marked with the Situation."""
    return [
        VirtueFlawInstance(
            vf_id=entry["vf_id"],
            params=boon_hook_params(
                entry.get("detail", ""),
                "",
                {BOON_HOOK_SITUATION: situation.id},
            ),
            id=new_instance_id(),
        )
        for entry in situation.entries
        for _ in range(entry.get("count", 1))
    ]


def situation_in_use(covenant: Covenant) -> tuple[str, int] | None:
    """The Covenant Situation the covenant's Boons and Hooks came from (its
    id) and how many of them are still there, or None."""
    found = [
        bh.params[BOON_HOOK_SITUATION]
        for bh in covenant.boons_hooks
        if bh.params.get(BOON_HOOK_SITUATION)
    ]
    return (found[0], len(found)) if found else None


def use_situation(covenant: Covenant, added: list[VirtueFlawInstance]) -> None:
    """Apply a Situation's Boons and Hooks (situation_instances), first
    removing those an earlier Situation brought (a Resource Hook's source
    loses its mark). Ones the user added stay."""
    for bh in [b for b in covenant.boons_hooks if b.params.get(BOON_HOOK_SITUATION)]:
        link_resource(covenant, bh, "")
        covenant.boons_hooks.remove(bh)
    covenant.boons_hooks.extend(added)


def situation_points(
    situation: CovenantSituationDef, catalog_by_id: Mapping[str, CovenantBoonHookDef]
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
    covenant: Covenant, catalog_by_id: Mapping[str, CovenantBoonHookDef]
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
    unknown_entry = held.count(UNKNOWN_HOOK)
    marked = [
        label(bh.vf_id)
        for bh in covenant.boons_hooks
        if bh.vf_id in catalog_by_id
        and boon_hook_is_unknown(bh, catalog_by_id[bh.vf_id])
    ]
    if unknown_entry and marked:
        problems.append(
            f"The Unknown Hook is counted twice: {label(UNKNOWN_HOOK)} and "
            f"{', '.join(marked)} marked Unknown are the same Hook (a Minor Hook "
            "chosen to be Unknown counts as Major); keep one."
        )
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


# -- Resource Hooks: which source they are about --

#: The Hooks that are about one of the covenant's vis or income sources,
#: and the source's flag each sets: Contested and Indiscreet Resources
#: (the source gives nothing until it is secured) and Dwindling Resource.
RESOURCE_HOOKS: dict[str, str] = {
    "covbh_hook_minor_contested_resource": "contested",
    "covbh_hook_minor_indiscreet_resource": "contested",
    "covbh_hook_major_indiscreet_resource": "contested",
    "covbh_hook_minor_dwindling_resource": "dwindling",
}


def resource_sources(covenant: Covenant) -> list[tuple[str, str]]:
    """The sources a Resource Hook can be about, as (label, id): the
    covenant's vis sources, then its sources of income."""
    vis = [
        (f"Vis source: {p.name or 'unnamed'}", p.id)
        for p in covenant.possessions
        if p.kind == "vis_source"
    ]
    income = [
        (f"Income: {s.name or 'unnamed'} ({s.type})", s.id)
        for s in covenant.economics.income_sources
    ]
    return vis + income


def _source_by_id(covenant: Covenant, source_id: str):
    for possession in covenant.possessions:
        if possession.kind == "vis_source" and possession.id == source_id:
            return possession
    for source in covenant.economics.income_sources:
        if source.id == source_id:
            return source
    return None


def linked_source(covenant: Covenant, instance: VirtueFlawInstance):
    """The vis or income source a Resource Hook is about, or None."""
    source_id = instance.params.get(BOON_HOOK_RESOURCE, "")
    return _source_by_id(covenant, source_id) if source_id else None


def link_resource(
    covenant: Covenant, instance: VirtueFlawInstance, source_id: str
) -> None:
    """Tie a Resource Hook to the source it is about ("" unties it),
    setting that source's Contested or Dwindling and clearing it on a
    source no other Hook still names."""
    flag = RESOURCE_HOOKS.get(instance.vf_id)
    if flag is None:
        return
    old = linked_source(covenant, instance)
    if source_id:
        instance.params[BOON_HOOK_RESOURCE] = source_id
    else:
        instance.params.pop(BOON_HOOK_RESOURCE, None)
    new = linked_source(covenant, instance)
    if new is not None:
        setattr(new, flag, True)
    if old is not None and old is not new:
        still = any(
            other is not instance
            and RESOURCE_HOOKS.get(other.vf_id) == flag
            and linked_source(covenant, other) is old
            for other in covenant.boons_hooks
        )
        if not still:
            setattr(old, flag, False)


#: One story secures a contested resource for five years (DE p. 181).
SECURED_YEARS = 5


def contested_now(resource: Possession | IncomeSource, year: int) -> bool:
    """Whether a contested resource gives nothing this year: not secured
    through it."""
    return resource.contested and (resource.secured_until or 0) < year


def settle_resource(resource: Possession | IncomeSource, year: int) -> None:
    """A story in `year` secures the resource, that year included."""
    resource.secured_until = year + SECURED_YEARS - 1


def contest_detail(covenant: Covenant, source_id: str) -> str:
    """What the Resource Hook on a source is about, without the source's
    own name when its detail opens with it ("the Rents: the baron's penny")."""
    for instance in covenant.boons_hooks:
        if instance.params.get(BOON_HOOK_RESOURCE) == source_id:
            detail = str(instance.params.get(BOON_HOOK_DETAIL) or "")
            return detail.split(": ", 1)[-1]
    return ""


def resource_standing(
    covenant: Covenant, resource: Possession | IncomeSource, year: int
) -> str:
    """A contested resource's standing in words: unsettled, or until when
    it is secured ("" for a resource nobody contests)."""
    if not resource.contested:
        return ""
    detail = contest_detail(covenant, resource.id)
    state = (
        "Contested, unsettled"
        if contested_now(resource, year)
        else f"Secured through {resource.secured_until}"
    )
    return f"{state}: {detail}" if detail else state


def unlinked_resource_hooks(
    covenant: Covenant, catalog_by_id: Mapping[str, CovenantBoonHookDef]
) -> list[str]:
    """The Resource Hooks not yet tied to a source, by name (and detail)."""
    return [
        catalog_by_id[bh.vf_id].name
        + (
            f" - {bh.params[BOON_HOOK_DETAIL]}"
            if bh.params.get(BOON_HOOK_DETAIL)
            else ""
        )
        for bh in covenant.boons_hooks
        if bh.vf_id in RESOURCE_HOOKS
        and bh.vf_id in catalog_by_id
        and linked_source(covenant, bh) is None
    ]
