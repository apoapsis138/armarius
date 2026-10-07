"""Laboratory rules computed from a Laboratory and the lab Virtue/Flaw
catalog: aura, occupied Size, room for Virtues, Base Safety and each
Characteristic's total, the Features' points and Focus, the Specialization
scores and their caps -- and the markup text of the lab sheet's lists and
details panels (Virtues & Flaws, Specializations, Features, Rooms,
Equipment & Stores, Raw Vis, Diary). Like the other
domain modules it returns markup text, never widgets."""

from __future__ import annotations

from collections import Counter
from collections.abc import Collection, Iterable, Sequence
from dataclasses import dataclass

from . import catalog, sourcebooks
from .arts import ARTS, TECHNIQUES
from .markup import escape, markdown_inline, problem, todo
from .models import (
    FEATURE_VIRTUE_POINTS,
    FOCUS_FLAWS,
    LAB_ACTIVITY_SPECIALIZATIONS,
    LAB_SPECIALIZATIONS,
    ArcaneConnection,
    DiaryEntry,
    LabFeature,
    Laboratory,
    LabSpecialtyEntry,
    LabSpecialtyGrant,
    LabVirtueFlawDef,
    NamedDescription,
    VirtueFlawInstance,
)
from .rules import effects

#: The two Focus Flaws; a lab may only have one Focus at a time.
FOCUS_FLAW_IDS = frozenset(FOCUS_FLAWS)


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


def vf_points(lab: Laboratory, vf_type: str) -> float:
    """The points the lab's Virtues or Flaws (`vf_type`) come to, each side
    counted on its own (Minor 1, Major 3, Free 0)."""
    lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
    return sum(
        abs(definition.cost)
        for vf in lab.virtues_flaws
        if (definition := lab_catalog.get(vf.vf_id)) is not None
        and definition.type == vf_type
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


#: A laboratory's Build Points at covenant creation (DE ch. 8, Build Point
#: Cost for Starting Laboratories): Size x 20, and each Virtue (Free
#: Virtues and Flaws cost nothing).
LAB_SIZE_BUILD_POINTS = 20
LAB_VIRTUE_BUILD_POINTS: dict[str, int] = {"Minor": 10, "Major": 20}


def lab_build_points(lab: Laboratory) -> int:
    """The laboratory's Build Points, worked out (never typed): Size x 20
    plus 10 for each Minor Virtue and 20 for each Major one."""
    lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
    points = LAB_SIZE_BUILD_POINTS * lab.characteristics.size
    for vf in lab.virtues_flaws:
        entry = lab_catalog.get(vf.vf_id)
        if entry is not None and entry.type == "Virtue":
            points += LAB_VIRTUE_BUILD_POINTS.get(entry.tier, 0)
    return points


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
    found = effects.collect(
        [laboratory_source(lab, catalog_by_id)],
        "lab_characteristic",
        target=characteristic,
    )
    virtue_sum = int(effects.amount_total(e for e in found if not e.is_negative_side))
    flaw_sum = int(effects.amount_total(e for e in found if e.is_negative_side))
    return manual, virtue_sum, flaw_sum, manual + virtue_sum + flaw_sum


def migrate_specialty_stand_ins(
    lab: Laboratory, catalog_by_id: dict[str, LabVirtueFlawDef] | None = None
) -> None:
    """Older saves typed a Virtue's Specialization grant in as a
    source named after it (Subterranean: Terram +1). Now the catalog carries
    the grant, so such an entry is dropped when the Virtue grants exactly
    that, or, for a choice, becomes the Virtue's choice."""
    if catalog_by_id is None:
        catalog_by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    kept: list[LabSpecialtyEntry] = []
    for entry in lab.specialties:
        if not _absorb_stand_in(lab, entry, catalog_by_id):
            kept.append(entry)
    lab.specialties[:] = kept


def _absorb_stand_in(
    lab: Laboratory,
    entry: LabSpecialtyEntry,
    catalog_by_id: dict[str, LabVirtueFlawDef],
) -> bool:
    source = entry.source.strip().casefold()
    for vf in lab.virtues_flaws:
        definition = catalog_by_id.get(vf.vf_id)
        if definition is None or definition.name.casefold() != source:
            continue
        for target, points in definition.specialization_grants:
            if points != entry.points:
                continue
            if target == entry.specialization:
                return True
            if (
                target == "{specialization}"
                and unchosen_specialization(vf, definition)
                and entry.specialization in definition.choices["specialization"]
            ):
                vf.params = {**vf.params, "specialization": entry.specialization}
                return True
    return False


def laboratory_source(
    lab: Laboratory, catalog_by_id: dict[str, LabVirtueFlawDef] | None = None
) -> effects.EffectSource:
    """The lab's Virtues and Flaws as a source for the shared effect lookup."""
    if catalog_by_id is None:
        catalog_by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    return effects.EffectSource("laboratory", lab.virtues_flaws, catalog_by_id)


# -- Features --


def feature_virtue(lab: Laboratory, feature: LabFeature) -> VirtueFlawInstance | None:
    """The Lesser/Greater Feature Virtue the Feature is built on, or None."""
    return next(
        (
            vf
            for vf in lab.virtues_flaws
            if vf.id == feature.virtue_id and vf.vf_id in FEATURE_VIRTUE_POINTS
        ),
        None,
    )


def feature_budget(lab: Laboratory, feature: LabFeature) -> int | None:
    """The points the Feature's Virtue gives it (1 or 3), None without one."""
    virtue = feature_virtue(lab, feature)
    return FEATURE_VIRTUE_POINTS[virtue.vf_id] if virtue else None


def features_title(lab: Laboratory) -> str:
    """ "Features (1 of 2)": the lab's Features against its Lesser and
    Greater Feature Virtues, one Feature each."""
    virtues = sum(1 for vf in lab.virtues_flaws if vf.vf_id in FEATURE_VIRTUE_POINTS)
    return f"Features ({len(lab.features)} of {virtues})"


def focus_points(virtue_vf_id: str) -> int:
    """The extra points a Focus gives a Feature on this Virtue (2 or 4)."""
    return next(
        points for virtue, points in FOCUS_FLAWS.values() if virtue == virtue_vf_id
    )


def focus_budget(lab: Laboratory, feature: LabFeature) -> int | None:
    """The Focus's extra points for a Feature that is the lab's Focus."""
    virtue = feature_virtue(lab, feature)
    return focus_points(virtue.vf_id) if feature.focus and virtue else None


def tier_word(virtue_vf_id: str) -> str:
    """ "Lesser" or "Greater"."""
    return "Greater" if virtue_vf_id == "labvf_greater_feature" else "Lesser"


def feature_options(feature_id: str | None) -> tuple[str, ...]:
    """The Specializations a Feature's points may go to: the catalog
    Feature's, or every Activity and Art for a custom one."""
    definition = catalog.load_lab_feature_catalog_by_id().get(feature_id or "")
    return definition.specializations if definition else LAB_SPECIALIZATIONS


def feature_type_name(feature: LabFeature) -> str:
    definition = catalog.load_lab_feature_catalog_by_id().get(feature.feature_id or "")
    return definition.name if definition else "Custom"


def free_feature_virtues(
    lab: Laboratory, feature: LabFeature | None = None
) -> list[VirtueFlawInstance]:
    """The lab's Lesser/Greater Feature Virtues no Feature is built on (the
    one `feature` itself is on counts as free)."""
    taken = {f.virtue_id for f in lab.features if f is not feature and f.virtue_id}
    return [
        vf
        for vf in lab.virtues_flaws
        if vf.vf_id in FEATURE_VIRTUE_POINTS and vf.id not in taken
    ]


def can_focus(lab: Laboratory, feature: LabFeature | None, virtue_vf_id: str) -> bool:
    """Whether a Feature on a `virtue_vf_id` Virtue may be the lab's Focus:
    the lab has the matching Focus Flaw (Lesser Focus for a Lesser Feature)
    and no other Feature is the Focus already."""
    has_flaw = any(
        FOCUS_FLAWS.get(vf.vf_id, ("", 0))[0] == virtue_vf_id
        for vf in lab.virtues_flaws
    )
    return has_flaw and not any(f.focus for f in lab.features if f is not feature)


def grants_from_points(points: Iterable[str]) -> list[LabSpecialtyGrant]:
    """One Specialization per point (["Ignem", "Ignem", "Aquam"]) as grants
    (Ignem 2, Aquam 1), in first-seen order."""
    return [LabSpecialtyGrant(name, n) for name, n in Counter(points).items()]


def points_from_grants(grants: Iterable[LabSpecialtyGrant]) -> list[str]:
    """The inverse of grants_from_points()."""
    return [g.specialization for g in grants for _ in range(g.points)]


def _grants_text(grants: Sequence[LabSpecialtyGrant]) -> str:
    return ", ".join(f"{g.specialization} {g.points:+d}" for g in grants)


def feature_problems(lab: Laboratory, feature: LabFeature) -> list[str]:
    """What still needs doing on a Feature: a Virtue to build it on, points
    to allocate."""
    budget = feature_budget(lab, feature)
    if budget is None:
        return ["needs a Feature Virtue"]
    problems = []
    unallocated = budget - sum(g.points for g in feature.allocations)
    if unallocated > 0:
        problems.append(f"{unallocated} {_plural(unallocated, 'point')} to allocate")
    focus = focus_budget(lab, feature)
    if focus is not None:
        unallocated = focus - sum(g.points for g in feature.focus_allocations)
        if unallocated > 0:
            problems.append(
                f"{unallocated} Focus {_plural(unallocated, 'point')} to allocate"
            )
    return problems


def _plural(count: int, word: str) -> str:
    return word if count == 1 else f"{word}s"


def prune_features(lab: Laboratory) -> None:
    """After a Virtue or Flaw is removed: a Feature whose Virtue went goes
    too, and a Focus with no matching Focus Flaw left is cleared with its
    points. (A Feature that never had a Virtue stays, flagged.)"""
    ids = {vf.id for vf in lab.virtues_flaws}
    lab.features[:] = [
        f for f in lab.features if f.virtue_id is None or f.virtue_id in ids
    ]
    for feature in lab.features:
        virtue = feature_virtue(lab, feature)
        if feature.focus and (
            virtue is None or not can_focus(lab, feature, virtue.vf_id)
        ):
            feature.focus = False
            feature.focus_allocations = []


def feature_on(lab: Laboratory, virtue: VirtueFlawInstance) -> LabFeature | None:
    """The Feature built on a lab Virtue, if any."""
    return next((f for f in lab.features if f.virtue_id == virtue.id), None)


def focus_feature(lab: Laboratory) -> LabFeature | None:
    return next((f for f in lab.features if f.focus), None)


def feature_rows(lab: Laboratory) -> list[tuple[int | None, str]]:
    """Features as (index, "Large Brass Cauldron  (Cauldron, Lesser, Focus)")
    rows, with the first thing still to do in the theme's error colour."""
    rows: list[tuple[int | None, str]] = []
    for index, feature in enumerate(lab.features):
        virtue = feature_virtue(lab, feature)
        details = [feature_type_name(feature)]
        if virtue is not None:
            details.append(tier_word(virtue.vf_id))
        if feature.focus:
            details.append("Focus")
        label = f"{escape(feature.name)}  [dim]({', '.join(details)})[/]"
        problems = feature_problems(lab, feature)
        if problems:
            label += f"  {todo(problems[0])}"
        rows.append((index, label))
    return rows


def feature_info_text(lab: Laboratory, index: int | None) -> str:
    """The details panel for a Feature: its type and Virtue, what its points
    may go to and where they went, its Focus, what's still to do, and the
    catalog description."""
    if index is None:
        return "[dim]Select a Feature to see its details.[/]"
    feature = lab.features[index]
    virtue = feature_virtue(lab, feature)
    definition = catalog.load_lab_feature_catalog_by_id().get(feature.feature_id or "")
    lines = [
        f"[b]{escape(feature.name)}[/]",
        f"[b]Type:[/] {feature_type_name(feature)}",
    ]
    if virtue is not None:
        budget = FEATURE_VIRTUE_POINTS[virtue.vf_id]
        lines.append(
            f"[b]Virtue:[/] {tier_word(virtue.vf_id)} Feature "
            f"({budget} {_plural(budget, 'point')})"
        )
    offers = (
        ", ".join(definition.specializations) if definition else "any Activity or Art"
    )
    lines.append(f"[b]Offers:[/] {offers}")
    lines.append(f"[b]Points:[/] {_grants_text(feature.allocations) or '(none yet)'}")
    if feature.focus and virtue is not None:
        tier = tier_word(virtue.vf_id)
        penalty = 2 if tier == "Greater" else 1
        lines.append(
            f"[b]Focus:[/] {_grants_text(feature.focus_allocations) or '(none yet)'} "
            f"({tier} Focus: -{penalty} General Quality on activities it doesn't aid)"
        )
    lines += [todo(f"{p[0].upper()}{p[1:]}.") for p in feature_problems(lab, feature)]
    if definition is not None:
        lines += ["", escape(definition.description)]
    return "\n".join(lines)


# -- Specializations --

#: How many Specializations count at once (ArM5 p.115): Activities, Arts,
#: and Techniques among those Arts.
MAX_ACTIVITY_SPECIALIZATIONS = 2
MAX_ART_SPECIALIZATIONS = 4
MAX_TECHNIQUE_SPECIALIZATIONS = 2


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


def _source_label(entry: LabSpecialtyEntry) -> str:
    return entry.source or "(no source given)"


def specialization_scores(lab: Laboratory) -> list[SpecializationScore]:
    """Every Specialization the lab has points in (from its Features, their
    Focus and the hand-entered sources, even if they sum to 0 or less), in
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
    source = laboratory_source(lab)
    found += [
        (effect.target or "", effect.entry.name, int(effect.modifier.amount or 0))
        for effect in effects.collect([source], "lab_specialization")
    ]
    found += [
        (entry.specialization, _source_label(entry), entry.points)
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
                entries.append((effect.entry.name, int(effect.modifier.amount or 0)))
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


def counted_specializations(lab: Laboratory) -> set[str]:
    """The Specializations that count: scored above 0 and not turned off."""
    return {score.name for score in specialization_scores(lab) if score.counts}


#: Each cap: its name in messages, the Specializations it covers, its size.
_CAPS = (
    ("Activity", LAB_ACTIVITY_SPECIALIZATIONS, MAX_ACTIVITY_SPECIALIZATIONS),
    ("Art", ARTS, MAX_ART_SPECIALIZATIONS),
    ("Technique", TECHNIQUES, MAX_TECHNIQUE_SPECIALIZATIONS),
)


def _broken_cap(names: Iterable[str]) -> tuple[str, int] | None:
    """The first cap `names` go over, as (its name, its size), or None."""
    names = set(names)
    for label, group, cap in _CAPS:
        if len(names & set(group)) > cap:
            return label, cap
    return None


def _within_caps(names: Iterable[str]) -> bool:
    return _broken_cap(names) is None


def toggle_specialization(lab: Laboratory, name: str) -> str | None:
    """Turn a Specialization off, or back on: None when done, else why not
    (it scores 0 or less, or turning it on would break a cap)."""
    score = next((s for s in specialization_scores(lab) if s.name == name), None)
    if score is None or score.points <= 0:
        return f"{name} scores 0 or less, so it doesn't count either way."
    if not score.dropped:
        lab.dropped_specializations.append(name)
        return None
    broken = _broken_cap(counted_specializations(lab) | {name})
    if broken is not None:
        label, cap = broken
        return (
            f"Can't turn {name} on: {cap} {label} Specializations already count, "
            "the most a laboratory can have. Turn one off first."
        )
    lab.dropped_specializations.remove(name)
    return None


def reconcile_dropped(lab: Laboratory, previously_counted: Collection[str]) -> None:
    """After a change that can add points: a Specialization that newly
    counts (not in `previously_counted`) is turned off if it would break a
    cap; ones that already counted stay on. Names with no points from any
    source any more are forgotten."""
    scores = specialization_scores(lab)
    counted = {s.name for s in scores if s.counts and s.name in previously_counted}
    for score in scores:
        if not score.counts or score.name in counted:
            continue
        if _within_caps(counted | {score.name}):
            counted.add(score.name)
        else:
            lab.dropped_specializations.append(score.name)
    present = {s.name for s in scores}
    lab.dropped_specializations[:] = [
        name for name in lab.dropped_specializations if name in present
    ]


#: The lab sheet's Attributes and Inventory tabs' shared details panel,
#: with nothing chosen.
ATTRIBUTES_PANEL_HINT = (
    "[dim]Select a Specialization, Feature or Room to see its details.[/]"
)
INVENTORY_PANEL_HINT = (
    "[dim]Select Raw Vis, stores, a connection, a device or a book to see its "
    "details.[/]"
)


def _cap_count(lab: Laboratory, group: Sequence[str], cap: int) -> str:
    """ "(3 of 4)": how many of `group` count against their cap, in the
    theme's error colour when over it."""
    count = len(counted_specializations(lab) & set(group))
    text = f"({count} of {cap})"
    return f"[$text-error]{text}[/]" if count > cap else text


def specialization_rows(lab: Laboratory) -> list[tuple[int | None, str]]:
    """The Specializations grid: an "Activity (1 of 2)" and an "Art (3 of
    4)" header (how many count against the cap), each over its rows "Ignem
    +3" (data index: position in LAB_SPECIALIZATIONS). One that's turned off
    is dimmed and struck through; one scoring 0 or less is dimmed."""
    scores = specialization_scores(lab)
    width = max((len(s.name) for s in scores), default=0)
    rows: list[tuple[int | None, str]] = []
    for header, group, cap in (
        ("Activity", LAB_ACTIVITY_SPECIALIZATIONS, MAX_ACTIVITY_SPECIALIZATIONS),
        ("Art", ARTS, MAX_ART_SPECIALIZATIONS),
    ):
        in_group = [s for s in scores if s.name in group]
        rows.append((None, f"{header} {_cap_count(lab, group, cap)}"))
        for score in in_group:
            label = f"{score.name:<{width}}  {score.points:+d}"
            if score.dropped and score.points > 0:
                label = f"[dim strike]{label}[/]"
            elif not score.counts:
                label = f"[dim]{label}[/]"
            rows.append((LAB_SPECIALIZATIONS.index(score.name), label))
    return rows


def specialization_info_text(lab: Laboratory, index: int | None) -> str:
    """The details panel for the Specialization at `index` (into
    LAB_SPECIALIZATIONS): its score and whether it counts, where each point
    comes from, and for a Technique how many Techniques count (at most 2 of
    the 4 Arts)."""
    if index is None:
        return ATTRIBUTES_PANEL_HINT
    name = LAB_SPECIALIZATIONS[index]
    score = next((s for s in specialization_scores(lab) if s.name == name), None)
    if score is None:
        return ATTRIBUTES_PANEL_HINT
    if score.points <= 0:
        status = "doesn't count (0 or less)"
    elif score.dropped:
        status = "turned off (Space turns it back on)"
    else:
        status = "counts (Space turns it off)"
    lines = [f"[b]{name} {score.points:+d}[/]: {status}", "", "[b]Sources:[/]"]
    lines += [f"  {points:+d}  {escape(label)}" for label, points in score.sources]
    if name in TECHNIQUES:
        techniques = _cap_count(lab, TECHNIQUES, MAX_TECHNIQUE_SPECIALIZATIONS)
        lines += ["", f"[b]Techniques counting:[/] {techniques}"]
    return "\n".join(lines)


def specialty_entry_rows(lab: Laboratory) -> list[tuple[int | None, str]]:
    """The hand-entered Specialization sources as (index, "Terram  +1
    Subterranean") rows; old text that named no Specialization says so in
    the theme's error colour."""
    width = max((len(e.specialization) for e in lab.specialties), default=0)
    rows: list[tuple[int | None, str]] = []
    for index, entry in enumerate(lab.specialties):
        if entry.specialization:
            head = f"{entry.specialization:<{width}}  {entry.points:+d}"
        else:
            head = todo("needs a Specialization")
        rows.append((index, f"{head}  {escape(_source_label(entry))}"))
    return rows


def specialty_entry_info_text(lab: Laboratory, index: int | None) -> str:
    """The details panel for a hand-entered Specialization source."""
    if index is None:
        return ATTRIBUTES_PANEL_HINT
    entry = lab.specialties[index]
    if not entry.specialization:
        return f"[b]{escape(_source_label(entry))}[/]\n\n" + todo(
            "Names no Activity or Art: edit it (e) to choose its Specialization."
        )
    return (
        f"[b]{entry.specialization} {entry.points:+d}[/]\n"
        f"[b]Source:[/] {escape(_source_label(entry))}\n\n"
        f"[dim]Counts towards {entry.specialization} in Specializations.[/]"
    )


# -- the sheet's lists and details panels --


def _points(cost: float) -> str:
    """ "3 pts", "1 pt", "Free"."""
    points = abs(cost)
    if not points:
        return "Free"
    return f"{points:g} {'pt' if points == 1 else 'pts'}"


def _characteristic_label(characteristic: str) -> str:
    return characteristic.replace("_", " ").title()


def vf_rows(lab: Laboratory, vf_type: str) -> list[tuple[int | None, str]]:
    """The lab's Virtues or Flaws (`vf_type`) as (true index into
    lab.virtues_flaws, "Name (Tier)") rows."""
    lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
    return [
        (
            index,
            f"{escape(catalog.describe_virtue_flaw(vf, lab_catalog))} "
            f"({definition.tier})",
        )
        for index, vf in enumerate(lab.virtues_flaws)
        if (definition := lab_catalog.get(vf.vf_id)) is not None
        and definition.type == vf_type
    ]


def vf_info_text(lab: Laboratory, index: int | None) -> str:
    """The details panel for the lab Virtue/Flaw at `index`: name, category,
    tier and points, its effect on the Characteristics, and the rules."""
    if index is None:
        return "[dim]Select a Virtue or Flaw to see its details.[/]"
    lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
    instance = lab.virtues_flaws[index]
    definition = lab_catalog.get(instance.vf_id)
    if definition is None:
        return escape(f"{instance.vf_id} (not in catalog)")
    lines = [
        f"[b]Name:[/] {escape(catalog.describe_virtue_flaw(instance, lab_catalog))}",
        f"[b]Category:[/] {definition.category}",
        f"[b]Tier:[/] {definition.tier} {definition.type} ({_points(definition.cost)})",
    ]
    lines += _vf_effect_lines(instance, definition)
    if instance.vf_id in FEATURE_VIRTUE_POINTS:
        feature = feature_on(lab, instance)
        lines.append(
            f"[b]Feature:[/] {escape(feature.name) if feature else '(none: free)'}"
        )
    elif instance.vf_id in FOCUS_FLAWS:
        feature = focus_feature(lab)
        lines.append(f"[b]Focus of:[/] {escape(feature.name) if feature else '(none)'}")
    lines += ["", "[b]Rules:[/]", escape(definition.description)]
    return "\n".join(lines)


def vf_entry_text(definition: LabVirtueFlawDef) -> str:
    """A catalog Laboratory Virtue/Flaw as the picker shows it under the
    list: category, tier and points, its effects, the rules and its book."""
    lines = [
        f"[b]Category:[/] {definition.category}",
        f"[b]Tier:[/] {definition.tier} {definition.type} ({_points(definition.cost)})",
    ]
    if definition.repeatable:
        lines.append("[dim]A laboratory may have it more than once.[/]")
    lines += _vf_effect_lines(
        VirtueFlawInstance(vf_id=definition.id), definition, unchosen="you choose"
    )
    lines += ["", escape(definition.description)]
    lines += ["", f"[dim]Source: {escape(sourcebooks.titles(definition.source))}[/]"]
    return "\n".join(lines)


def _vf_effect_lines(
    instance: VirtueFlawInstance,
    definition: LabVirtueFlawDef,
    *,
    unchosen: str = "not chosen",
) -> list[str]:
    """A lab Virtue/Flaw's Specialization grants and effects on the
    Characteristics, one details-panel line each."""
    lines = []
    grants = specialization_grant_text(instance, definition, unchosen=unchosen)
    if grants:
        lines.append(f"[b]Specializations:[/] {grants}")
    if definition.characteristic_modifiers:
        effects = ", ".join(
            f"{_characteristic_label(c)} {amount:+d}"
            for c, amount in definition.characteristic_modifiers.items()
        )
        lines.append(f"[b]Characteristics:[/] {effects}")
    return lines


def unchosen_specialization(
    instance: VirtueFlawInstance, definition: LabVirtueFlawDef
) -> bool:
    """True when the Virtue/Flaw lets the owner choose a Specialization and
    none has been chosen (a lab from an older save)."""
    return "specialization" in definition.choices and not instance.params.get(
        "specialization"
    )


def specialization_grant_text(
    instance: VirtueFlawInstance,
    definition: LabVirtueFlawDef,
    *,
    unchosen: str = "not chosen",
) -> str:
    """Its Specialization grants in words: "Experimentation +1, Muto +2"; a
    choice not yet made reads "(Muto or Rego, not chosen) +2", with
    `unchosen` in place of "not chosen"."""
    parts = []
    for target, points in definition.specialization_grants:
        if target == "{specialization}":
            chosen = instance.params.get("specialization")
            options = definition.choices["specialization"]
            if chosen:
                target = chosen
            elif len(options) <= 3:
                target = f"({' or '.join(options)}, {unchosen})"
            else:
                target = f"({unchosen})"
        parts.append(f"{target} {points:+g}")
    for modifier in definition.modifiers:
        if modifier.applies_to == "lab_specialization_high":
            parts.append(f"{modifier.amount:+g} to each scoring 2 or more")
    return ", ".join(parts)


def vf_warnings(lab: Laboratory) -> str:
    """What's wrong with the lab's Virtues & Flaws as a whole, one line
    each in the theme's error colour -- or "" when nothing is: more Virtue
    points (net of Flaws) than Size + Refinement allow, or more than one
    Focus."""
    lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
    lines = []
    free = lab_free_virtues(lab, lab_catalog)
    if free < 0:
        limit = lab.characteristics.size + lab.characteristics.refinement
        lines.append(
            f"Over capacity by {-free:g} "
            f"(Virtues less Flaws may total Size + Refinement = {limit})."
        )
    focuses = sum(1 for vf in lab.virtues_flaws if vf.vf_id in FOCUS_FLAW_IDS)
    if focuses > 1:
        lines.append(f"{focuses} Focus Flaws: a laboratory may only have one Focus.")
    for vf in lab.virtues_flaws:
        definition = lab_catalog.get(vf.vf_id)
        if definition is not None and unchosen_specialization(vf, definition):
            lines.append(
                f"{definition.name}: its Specialization isn't chosen "
                "(remove it and add it again to choose)."
            )
    return "\n".join(problem(line) for line in lines)


def named_rows(entries: Sequence[NamedDescription]) -> list[tuple[int | None, str]]:
    """Rooms or Equipment & Stores as (index, name) rows."""
    return [(index, escape(entry.name)) for index, entry in enumerate(entries)]


def named_info_text(
    entries: Sequence[NamedDescription], index: int | None, noun: str
) -> str:
    """The details panel for a Room or Equipment & Stores entry: its name and
    the user's description (with **bold**/*italic*)."""
    if index is None:
        return f"[dim]Select {noun} to see its details.[/]"
    entry = entries[index]
    description = (
        markdown_inline(entry.description)
        if entry.description
        else "[dim](no description)[/]"
    )
    return f"[b]{escape(entry.name)}[/]\n\n{description}"


def connection_state(connection: ArcaneConnection) -> str:
    """ "fixed", or how long it lasts ("temporary" when not typed)."""
    if connection.fixed:
        return "fixed"
    return f"lasts {connection.lasts}" if connection.lasts else "temporary"


def connection_rows(lab: Laboratory) -> list[tuple[int | None, str]]:
    """The lab's Arcane Connections as (index, "to  state") rows."""
    width = max((len(c.to) for c in lab.arcane_connections), default=0)
    return [
        (
            index,
            f"{escape(c.to.ljust(width))}  [dim]{escape(connection_state(c))}[/]",
        )
        for index, c in enumerate(lab.arcane_connections)
    ]


def connection_info_text(lab: Laboratory, index: int | None) -> str:
    """The details panel for an Arcane Connection."""
    if index is None:
        return INVENTORY_PANEL_HINT
    c = lab.arcane_connections[index]
    lines = [f"[b]Arcane Connection to {escape(c.to)}[/]"]
    if c.fixed and c.fixed_year is not None:
        lines.append(f"Fixed in {c.fixed_season} {c.fixed_year} (lasts indefinitely).")
    elif c.fixed:
        lines.append("Fixed (lasts indefinitely).")
    else:
        lines.append(
            f"Temporary: {escape(connection_state(c))}. Fixing it takes a season "
            "of lab work and 1 pawn of Vim (plan it on the Planning tab)."
        )
    if c.source:
        lines.append(f"From: {escape(c.source)}")
    if c.description:
        lines += ["", markdown_inline(c.description)]
    return "\n".join(lines)


def raw_vis_rows(lab: Laboratory) -> list[tuple[int | None, str]]:
    """The lab's Raw Vis as (index into sorted(lab.raw_vis), "Art: N pawn(s)")
    rows, same as a character's."""
    return [
        (index, f"{art.title()}: {lab.raw_vis[art]} pawn(s)")
        for index, art in enumerate(sorted(lab.raw_vis))
    ]


def raw_vis_info_text(lab: Laboratory, index: int | None) -> str:
    """The details panel for a Raw Vis row: its Art and pawns."""
    if index is None:
        return INVENTORY_PANEL_HINT
    art = sorted(lab.raw_vis)[index]
    pawns = lab.raw_vis[art]
    return f"[b]{art.title()} vis[/]\n{pawns} {_plural(pawns, 'pawn')}"


def diary_rows(diary: Sequence[DiaryEntry]) -> list[tuple[int | None, str]]:
    """Diary entries as (index, "1220 Spring  Invent Spell  Pilum of Fire")
    rows, in the order they were written; the Activity column is padded to
    the longest one so the names line up, and a dash when it isn't set."""
    activities = [entry.activity or "-" for entry in diary]
    width = max((len(a) for a in activities), default=0)
    return [
        (
            index,
            f"{entry.year} {entry.season:<6}  {activity:<{width}}  "
            f"{escape(entry.name)}",
        )
        for index, (entry, activity) in enumerate(zip(diary, activities, strict=True))
    ]


def diary_info_text(diary: Sequence[DiaryEntry], index: int | None) -> str:
    """The details panel for a Diary entry: its name, date, Activity Type and
    the user's details (with **bold**/*italic*)."""
    if index is None:
        return "[dim]Select a Diary entry to see its details.[/]"
    entry = diary[index]
    details = (
        markdown_inline(entry.details) if entry.details else "[dim](no details)[/]"
    )
    return "\n".join(
        [
            f"[b]{escape(entry.name)}[/]",
            f"[b]Date:[/] {entry.season} {entry.year}",
            f"[b]Activity:[/] {escape(entry.activity) or '(not set)'}",
            "",
            details,
        ]
    )
