"""Laboratory rules computed from a Laboratory and the lab Virtue/Flaw
catalog: aura, occupied Size, room for Virtues, Base Safety and each
Characteristic's total."""

from __future__ import annotations

from .models import Laboratory, LabVirtueFlawDef


def lab_aura_total(lab: Laboratory, covenant_aura: int) -> int:
    """The lab's effective aura: the covenant's inherited aura plus the lab's
    own manual modifier."""
    return covenant_aura + lab.aura_modifier


def lab_net_vf_points(
    lab: Laboratory, catalog_by_id: dict[str, LabVirtueFlawDef]
) -> float:
    """Current Virtue points minus Flaw points attached to the lab."""
    return sum(
        catalog_by_id[vf.vf_id].cost
        for vf in lab.virtues_flaws
        if vf.vf_id in catalog_by_id
    )


def lab_occupied_size(
    lab: Laboratory, catalog_by_id: dict[str, LabVirtueFlawDef]
) -> float:
    """OCCUPIED SIZE: current Virtue points - Flaw points - Refinement."""
    return lab_net_vf_points(lab, catalog_by_id) - lab.characteristics.refinement


def lab_free_virtues(
    lab: Laboratory, catalog_by_id: dict[str, LabVirtueFlawDef]
) -> float:
    """How many more points of Virtues (minus Flaws) the lab has room for:
    (Size + Refinement) - current Virtue points minus Flaw points."""
    limit = lab.characteristics.size + lab.characteristics.refinement
    return limit - lab_net_vf_points(lab, catalog_by_id)


def lab_base_safety(
    lab: Laboratory, catalog_by_id: dict[str, LabVirtueFlawDef]
) -> float:
    """BASE SAFETY OF LAB: Refinement - occupied Size (if positive)."""
    occupied = lab_occupied_size(lab, catalog_by_id)
    return lab.characteristics.refinement - max(occupied, 0)


def lab_characteristic_total(
    lab: Laboratory,
    catalog_by_id: dict[str, LabVirtueFlawDef],
    characteristic: str,
) -> tuple[int, int, int, int]:
    """(manual, virtue_sum, flaw_sum, total) for one of LAB_CHARACTERISTICS.

    manual + virtue_sum + flaw_sum = total, per the user's explicit
    formula: the manual component is a free player adjustment on top of
    whatever the lab's attached Virtues/Flaws contribute.
    """
    manual = getattr(lab.characteristics, characteristic)
    virtue_sum = 0
    flaw_sum = 0
    for vf in lab.virtues_flaws:
        entry = catalog_by_id.get(vf.vf_id)
        if entry is None:
            continue
        amount = entry.characteristic_modifiers.get(characteristic, 0)
        if entry.type == "Virtue":
            virtue_sum += amount
        else:
            flaw_sum += amount
    return manual, virtue_sum, flaw_sum, manual + virtue_sum + flaw_sum
