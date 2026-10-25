"""A laboratory's own statistics, as the Lab Total reads them: the Build
Points its Size and Virtues cost, the Virtues it gets free, its
characteristics (Safety, Health, Aesthetics and the rest) with what its
Virtues, Flaws and servants add, its aura, and its Specializations. The
Laboratory sheet's lists and text are laboratories.py's."""

from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass

from .. import catalog
from ..models import (
    LAB_SPECIALIZATIONS,
    Character,
    Laboratory,
    LabSpecialtyEntry,
    LabVirtueFlawDef,
    Saga,
    VirtueFlawInstance,
)
from . import effects, lab_items
from .rounding import round_down

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Creating a Laboratory, p. "
    "250"
)


def lab_aura_total(lab: Laboratory, covenant_aura: int) -> int:
    """The lab's effective aura: the covenant's inherited aura plus the lab's
    own manual modifier."""
    return covenant_aura + lab.aura_modifier


def lab_net_vf_points(
    lab: Laboratory, catalog_by_id: Mapping[str, LabVirtueFlawDef]
) -> float:
    """Current Virtue points minus Flaw points attached to the lab: those a
    magic item grants take no space, a very large Magic Item a Minor
    Virtue's (rules.lab_items)."""
    granted = lab_items.granted_ids(lab)
    return sum(
        lab_items.space_cost(lab, vf, catalog_by_id[vf.vf_id], granted)
        for vf in lab.virtues_flaws
        if vf.vf_id in catalog_by_id
    )


def lab_occupied_size(
    lab: Laboratory, catalog_by_id: Mapping[str, LabVirtueFlawDef]
) -> float:
    """OCCUPIED SIZE: current Virtue points - Flaw points - Refinement."""
    return lab_net_vf_points(lab, catalog_by_id) - lab.characteristics.refinement


def lab_free_virtues(
    lab: Laboratory, catalog_by_id: Mapping[str, LabVirtueFlawDef]
) -> float:
    """How many more points of Virtues (minus Flaws) the lab has room for:
    (Size + Refinement) - current Virtue points minus Flaw points."""
    limit = lab.characteristics.size + lab.characteristics.refinement
    return limit - lab_net_vf_points(lab, catalog_by_id)


#: A laboratory's Build Points at covenant creation (DE ch. 8, Build Point
#: Cost for Starting Laboratories): Size x 20, and each Virtue (Free
#: Virtues and Flaws cost nothing).
LAB_SIZE_BUILD_POINTS = 20


LAB_VIRTUE_BUILD_POINTS: dict[str, int] = {"Minor": 10, "Major": 20}


def lab_build_points(lab: Laboratory) -> int:
    """The laboratory's Build Points, worked out (never typed): Size x 20
    plus 10 for each Minor Virtue and 20 for each Major one. A Virtue a
    magic item grants costs nothing (the item is priced as an enchanted
    item); a very large Magic Item is a Minor Virtue."""
    lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
    granted = lab_items.granted_ids(lab)
    points = LAB_SIZE_BUILD_POINTS * lab.characteristics.size
    for vf in lab.virtues_flaws:
        entry = lab_catalog.get(vf.vf_id)
        if entry is not None and entry.type == "Virtue":
            tier = lab_items.tier(lab, vf, entry, granted)
            points += LAB_VIRTUE_BUILD_POINTS.get(tier, 0)
    return points


def lab_base_safety(
    lab: Laboratory, catalog_by_id: Mapping[str, LabVirtueFlawDef]
) -> float:
    """BASE SAFETY OF LAB: Refinement - occupied Size (if positive)."""
    occupied = lab_occupied_size(lab, catalog_by_id)
    return lab.characteristics.refinement - max(occupied, 0)


def lab_characteristic_total(
    lab: Laboratory,
    catalog_by_id: Mapping[str, LabVirtueFlawDef],
    characteristic: str,
    saga: Saga | None,
) -> tuple[int, int, int, int]:
    """(manual, virtue_sum, flaw_sum, total) for one of LAB_CHARACTERISTICS.

    manual + virtue_sum + flaw_sum = total, per the user's explicit
    formula: the manual component is a free player adjustment on top of
    whatever the lab's attached Virtues/Flaws contribute. A Servant who is
    one of the `saga`'s grogs counts with the grog's Intelligence, and a
    magic item counts only while its device is kept in the lab (with no
    saga, every one counts).
    """
    manual = getattr(lab.characteristics, characteristic)
    found = characteristic_effects(lab, catalog_by_id, characteristic, saga)
    virtue_sum = int(effects.amount_total(e for e in found if not e.is_negative_side))
    flaw_sum = int(effects.amount_total(e for e in found if e.is_negative_side))
    total = manual + virtue_sum + flaw_sum
    if characteristic == "aesthetics":
        # The change counts with the side that made it, so the parts still
        # add up to the total.
        change = aesthetics_after(lab, total) - total
        if change > 0:
            virtue_sum += change
        else:
            flaw_sum += change
        total += change
    return manual, virtue_sum, flaw_sum, total


#: Aesthetics halved after everything else (Covenants pp. 118-119), then
#: held to -1 at most in a lab with no light (DE p. 296).
HALVES_AESTHETICS = ("labvf_invisible", "labvf_shrouded")
LIGHTLESS = "labvf_lightless"
LIGHTLESS_AESTHETICS = -1


def aesthetics_after(lab: Laboratory, total: int) -> int:
    """The lab's Aesthetics once Invisible or Shrouded halves it (rounded
    down) and Lightless holds it to -1."""
    ids = {vf.vf_id for vf in lab.virtues_flaws}
    if ids & set(HALVES_AESTHETICS):
        total = round_down(total / 2)
    if LIGHTLESS in ids:
        total = min(total, LIGHTLESS_AESTHETICS)
    return total


def lab_safety(
    lab: Laboratory,
    catalog_by_id: Mapping[str, LabVirtueFlawDef],
    saga: Saga | None,
) -> int:
    """The lab's Safety, as its botch dice read it: the Base Safety
    (Refinement - occupied Size, rounded down) plus the Characteristic's
    typed, Virtue and Flaw parts."""
    base = round_down(lab_base_safety(lab, catalog_by_id))
    return base + lab_characteristic_total(lab, catalog_by_id, "safety", saga)[3]


def characteristic_effects(
    lab: Laboratory,
    catalog_by_id: Mapping[str, LabVirtueFlawDef],
    characteristic: str,
    saga: Saga | None,
) -> list[effects.Effect]:
    """What the lab's Virtues and Flaws, and the points its magic items
    buy, do to one Characteristic, one effect each
    (lab_characteristic_total adds them up)."""
    return effects.collect(
        [laboratory_source(lab, catalog_by_id, saga), lab_items.item_source(saga, lab)],
        "lab_characteristic",
        target=characteristic,
    )


def laboratory_source(
    lab: Laboratory,
    catalog_by_id: Mapping[str, LabVirtueFlawDef] | None = None,
    saga: Saga | None = None,
) -> effects.EffectSource:
    """The lab's Virtues and Flaws as a source for the shared effect
    lookup; given the `saga`, a Servant who is one of its grogs reads the
    grog's Intelligence (vf_params), and a Virtue a magic item grants
    counts only while the item's device is kept in the lab."""
    if catalog_by_id is None:
        catalog_by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    real = [vf for vf in lab.virtues_flaws if vf.id not in illusory(lab, catalog_by_id)]
    if saga is None:
        return effects.EffectSource("laboratory", real, catalog_by_id)
    away = lab_items.away_grants(saga, lab)
    instances = [vf for vf in real if vf.id not in away]
    return effects.EffectSource(
        "laboratory", instances, catalog_by_id, lambda vf: vf_params(saga, vf)
    )


#: The Flaws whose balancing Virtue is only an illusion (DE p. 296).
ILLUSIONS = ("labvf_lesser_illusion", "labvf_greater_illusion")


def illusory(
    lab: Laboratory, catalog_by_id: Mapping[str, LabVirtueFlawDef]
) -> set[str]:
    """The ids of the lab's Virtues that a Lesser or Greater Illusion names
    as its illusory one: they have no effect (DE p. 296). Each Illusion
    negates one Virtue of the name it gives."""
    wanted = [
        vf.params.get("illusory", "").strip().casefold()
        for vf in lab.virtues_flaws
        if vf.vf_id in ILLUSIONS
    ]
    found: set[str] = set()
    for name in filter(None, wanted):
        match = next(
            (
                vf.id
                for vf in lab.virtues_flaws
                if vf.id not in found
                and vf.vf_id in catalog_by_id
                and catalog_by_id[vf.vf_id].type == "Virtue"
                and catalog_by_id[vf.vf_id].name.casefold() == name
            ),
            None,
        )
        if match is not None:
            found.add(match)
    return found


def servant(saga: Saga, instance: VirtueFlawInstance) -> Character | None:
    """The grog a Virtue names as its servant, or None: none named, or the
    character named is gone or no longer a grog."""
    character = saga.character(instance.params.get("servant") or None)
    return character if character is not None and character.type == "grog" else None


def vf_params(saga: Saga, instance: VirtueFlawInstance) -> dict[str, str]:
    """The Virtue's parameters, with its servant's Intelligence in place of
    the typed one when it names a grog of the saga: the grog's sheet is
    read each time, so a change to it follows."""
    grog = servant(saga, instance)
    if grog is None:
        return dict(instance.params)
    return {**instance.params, "intelligence": str(grog.characteristics.intelligence)}


@dataclass(frozen=True)
class SpecializationScore:
    """One Specialization's total over every source. It doesn't count when
    it's turned off (in lab.dropped_specializations) or scores 0 or less."""

    name: str
    points: int
    #: (where the points come from, how many), in the order found.
    sources: tuple[tuple[str, int], ...]
    dropped: bool

    @property
    def counts(self) -> bool:
        return self.points > 0 and not self.dropped


def specialty_source_label(entry: LabSpecialtyEntry) -> str:
    return entry.source or "(no source given)"


def specialization_scores(saga: Saga, lab: Laboratory) -> list[SpecializationScore]:
    """Every Specialization the lab has points in (from its Features, their
    Focus, its Virtues, its magic items and the hand-entered sources, even if they sum to 0 or less), in
    LAB_SPECIALIZATIONS order."""
    found: list[tuple[str, str, int]] = []  # (Specialization, source, points)
    for feature in lab.features:
        found += [
            (g.specialization, f"{feature.name} (Feature)", g.points)
            for g in feature.allocations
        ]
        found += [
            (g.specialization, f"{feature.name} (Focus)", g.points)
            for g in feature.focus_allocations
        ]
    source = laboratory_source(lab, saga=saga)
    found += [
        (effect.target or "", effect.entry.name, int(effect.amount or 0))
        for effect in effects.collect(
            [source, lab_items.item_source(saga, lab)], "lab_specialization"
        )
    ]
    found += [
        (entry.specialization, specialty_source_label(entry), entry.points)
        for entry in lab.specialties
    ]
    sources: dict[str, list[tuple[str, int]]] = {}
    for name, label, points in found:
        if name in LAB_SPECIALIZATIONS:
            sources.setdefault(name, []).append((label, points))
    # Undecorated and the like: each Specialization scoring 2 or more loses
    # a point (read once the other sources are summed).
    for effect in effects.collect([source], "lab_specialization_high"):
        for name, entries in sources.items():
            if sum(points for _, points in entries) >= 2:
                entries.append((effect.entry.name, int(effect.amount or 0)))
    return [
        SpecializationScore(
            name,
            sum(points for _, points in sources[name]),
            tuple(sources[name]),
            name in lab.dropped_specializations,
        )
        for name in LAB_SPECIALIZATIONS
        if name in sources
    ]


#: The lab Flaws that limit what kind of work a laboratory can do.
MISSING_EQUIPMENT = "labvf_missing_equipment"
ELEMENTARY = "labvf_elementary"
RESTRICTION = "labvf_restriction"


def forbidden(lab: Laboratory, categories: Collection[str]) -> str | None:
    """Why lab work of these activity categories (Spells, Items, Texts...)
    can't be done in `lab`: Missing Equipment names it, Restriction forbids
    it, or Elementary allows only another (DE pp. 295-296); None if it can."""
    if not categories:
        return None
    for vf in lab.virtues_flaws:
        chosen = {
            v for k, v in vf.params.items() if k in ("activity", "second_activity")
        }
        if vf.vf_id == MISSING_EQUIPMENT and chosen & set(categories):
            return f"{lab.name} has Missing Equipment: no {', '.join(sorted(chosen & set(categories)))} work."
        if vf.vf_id == RESTRICTION and vf.params.get("forbidden") in categories:
            return f"{lab.name}'s Restriction forbids {vf.params['forbidden']} work."
        if vf.vf_id == ELEMENTARY and chosen and not chosen & set(categories):
            return f"{lab.name} is Elementary: only {', '.join(sorted(chosen))} work."
    return None


#: Where the Teaching and Texts Specializations are described (DE pp.
#: 290-291).
SPECIALIZATION_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 11: The Laboratory, "
    "Specializations, pp. 290-291"
)
#: The Teaching Specialization adds at most this much (DE p. 291).
TEACHING_CAP = 3


def specialty_points(saga: Saga, lab: Laboratory | None, name: str) -> int:
    """The points `lab` has in the Specialization `name`, if it counts (0
    for no lab)."""
    if lab is None:
        return 0
    return next(
        (
            s.points
            for s in specialization_scores(saga, lab)
            if s.name == name and s.counts
        ),
        0,
    )


def teaching_bonus(saga: Saga, lab: Laboratory | None) -> int:
    """What the Teaching Specialization adds to a Training or Teaching
    Source Quality when the season is spent in the lab: its points, at
    most +3 (DE p. 291)."""
    return min(TEACHING_CAP, specialty_points(saga, lab, "Teaching"))


def texts_bonus(saga: Saga, lab: Laboratory | None) -> int:
    """What the Texts Specialization adds to Profession: Scribe when
    copying and to the Language when writing: +1 for each full 3 points
    (DE p. 291)."""
    return specialty_points(saga, lab, "Texts") // 3
