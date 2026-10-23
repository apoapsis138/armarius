"""Laboratory rules computed from a Laboratory and the lab Virtue/Flaw
catalog: aura, occupied Size, room for Virtues, Base Safety and each
Characteristic's total, the Features' points and Focus, the Specialization
scores and their caps -- and the markup text of the lab sheet's lists and
details panels (Virtues & Flaws, Specializations, Features, Rooms,
Equipment & Stores, Raw Vis, Diary). Like the other
domain modules it returns markup text, never widgets."""

from __future__ import annotations

from collections import Counter
from collections.abc import Collection, Iterable, Mapping, Sequence

from . import catalog, sourcebooks
from .arts import ARTS, TECHNIQUES
from .markup import escape, markdown_text, problem, todo
from .models import (
    FEATURE_VIRTUE_POINTS,
    FOCUS_FLAWS,
    ITEM_VIRTUES,
    LAB_ACTIVITY_SPECIALIZATIONS,
    LAB_SPECIALIZATIONS,
    ArcaneConnection,
    DiaryEntry,
    LabFeature,
    LabItemBenefit,
    Laboratory,
    LabSpecialtyEntry,
    LabSpecialtyGrant,
    LabVirtueFlawDef,
    Modifier,
    NamedDescription,
    Saga,
    VirtueFlawInstance,
)
from .rules import effects, enchantment, lab_items
from .rules.lab_stats import (
    lab_free_virtues,
    servant,
    specialization_scores,
    specialty_source_label,
    vf_params,
)
from .tables import Table

#: The two Focus Flaws; a lab may only have one Focus at a time.
FOCUS_FLAW_IDS = frozenset(FOCUS_FLAWS)


def vf_points(lab: Laboratory, vf_type: str) -> float:
    """The points the lab's Virtues or Flaws (`vf_type`) come to, each side
    counted on its own (Minor 1, Major 3, Free 0; one a magic item grants,
    0)."""
    lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
    granted = lab_items.granted_ids(lab)
    return sum(
        abs(lab_items.space_cost(lab, vf, definition, granted))
        for vf in lab.virtues_flaws
        if (definition := lab_catalog.get(vf.vf_id)) is not None
        and definition.type == vf_type
    )


def migrate_specialty_stand_ins(
    lab: Laboratory, catalog_by_id: Mapping[str, LabVirtueFlawDef] | None = None
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
    catalog_by_id: Mapping[str, LabVirtueFlawDef],
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


# -- a Virtue's servant --


def entered_intelligence(saga: Saga | None, instance: VirtueFlawInstance) -> int | None:
    """The Intelligence a Virtue's effect is read from: its grog's, else the
    typed number; None when neither is there."""
    params = vf_params(saga, instance) if saga is not None else instance.params
    try:
        return int(str(params.get("intelligence", "")).strip())
    except ValueError:
        return None


def reading_text(
    saga: Saga | None,
    instance: VirtueFlawInstance,
    modifier: Modifier,
) -> str:
    """A Characteristic read from a parameter, in plain words: "Safety +2
    (Kurt's Intelligence +3, halved, rounded up)", or "Safety
    +(Intelligence, halved, rounded up)" until one is entered."""
    label = _characteristic_label(modifier.target or "")
    value = entered_intelligence(saga, instance)
    if value is None:
        return f"{label} +(Intelligence{_divided(modifier)})"
    amount = effects.resolve_amount(modifier, {modifier.amount_param or "": str(value)})
    return f"{label} {amount or 0:+g} ({reading_detail(saga, instance, modifier)})"


def reading_detail(
    saga: Saga | None, instance: VirtueFlawInstance, modifier: Modifier
) -> str:
    """Where an amount read from a parameter comes from: "Kurt's
    Intelligence +3, halved, rounded up", "Intelligence +2"."""
    value = entered_intelligence(saga, instance)
    grog = servant(saga, instance) if saga is not None else None
    who = f"{grog.name}'s Intelligence" if grog is not None else "Intelligence"
    shown = "not entered" if value is None else f"{value:+d}"
    return f"{who} {shown}{_divided(modifier)}"


def _divided(modifier: Modifier) -> str:
    divisor = modifier.amount_divisor
    if divisor == 1:
        return ""
    if divisor == 2:
        return ", halved, rounded up"
    return f", divided by {divisor}, rounded up"


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
    points. (A Feature that never had a Virtue stays, flagged.) A magic
    item effect installed as a Virtue that went goes too
    (rules.lab_items.prune)."""
    lab_items.prune(lab)
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


def item_delete_note(lab: Laboratory, instance: VirtueFlawInstance) -> str:
    """What deleting a lab Virtue/Flaw does to its magic items, for the
    confirmation ("" when nothing)."""
    benefit = lab_items.granting(lab, instance)
    if benefit is not None:
        return (
            f" {benefit.name or 'Its magic item'} stays installed, granting "
            "nothing until it is edited."
        )
    installed = sum(1 for b in lab.item_benefits if b.virtue_id == instance.id)
    if installed:
        name = _item_name(lab, instance.id) or "the item"
        return (
            f" What {name} gives the lab goes too ({installed} "
            f"{_plural(installed, 'effect')})."
        )
    return ""


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


# -- Magic items --


def item_name(saga: Saga, benefit: LabItemBenefit) -> str:
    """ "Rowan Lectern: Steady Page" (plain text)."""
    effect = lab_items.effect_of(saga, benefit)
    device = lab_items.device_of(saga, benefit)
    name = device.name if device else benefit.name or "(device gone)"
    return f"{name}: {enchantment.effect_name(effect)}" if effect else name


def item_gives(lab: Laboratory, benefit: LabItemBenefit) -> str:
    """What the effect gives, plain text: "Auspicious Shape" or "Texts +2,
    Safety +1"."""
    if benefit.granted_id:
        granted = next(
            (vf for vf in lab.virtues_flaws if vf.id == benefit.granted_id), None
        )
        if granted is None:
            return "(its Virtue is gone)"
        return catalog.describe_virtue_flaw(
            granted, catalog.load_lab_virtue_flaw_catalog_by_id()
        )
    parts = [f"{g.specialization} {g.points:+d}" for g in benefit.specializations]
    parts += [
        f"{_characteristic_label(g.characteristic)} {g.points:+d}"
        for g in benefit.characteristics
    ]
    return ", ".join(parts) or "(nothing yet)"


def items_title(lab: Laboratory) -> str:
    return f"Magic Items ({len(lab.item_benefits)})"


def item_rows(saga: Saga, lab: Laboratory) -> list[tuple[int | None, str]]:
    """Each magic item effect as (index, "Rowan Lectern: Steady Page  (Texts
    +2)"), with the first thing wrong in the theme's error colour."""
    rows: list[tuple[int | None, str]] = []
    for index, benefit in enumerate(lab.item_benefits):
        label = (
            f"{escape(item_name(saga, benefit))}  "
            f"[dim]({escape(item_gives(lab, benefit))})[/]"
        )
        problems = lab_items.problems(saga, lab, benefit)
        if problems:
            label += f"  {todo(problems[0])}"
        rows.append((index, label))
    return rows


def item_info_text(saga: Saga, lab: Laboratory, index: int | None) -> str:
    """The details panel for a magic item effect: the device and effect,
    how it is installed, what it gives, the levels it uses, and what's
    wrong."""
    if index is None:
        return "[dim]Select a magic item to see its details.[/]"
    benefit = lab.item_benefits[index]
    host = next((vf for vf in lab.virtues_flaws if vf.id == benefit.virtue_id), None)
    lines = [f"[b]{escape(item_name(saga, benefit))}[/]"]
    if host is not None:
        installed = (
            "Enchantment of the laboratory (Free Virtue)"
            if host.vf_id == lab_items.ENCHANTMENT
            else "Magic Item, very large (Minor Virtue)"
            if lab_items.is_very_large(host)
            else "Magic Item (Free Virtue)"
        )
        lines.append(f"[b]Installed as:[/] {installed}")
    level = lab_items.level_of(saga, benefit)
    if level is not None:
        lines.append(f"[b]Effect level:[/] {level}")
    if benefit.granted_id:
        lines.append(
            f"[b]Grants:[/] {escape(item_gives(lab, benefit))} "
            "(no space, no Build Points; its effects apply as usual)"
        )
    else:
        lines.append(f"[b]Gives:[/] {escape(item_gives(lab, benefit))}")
        lines.append(
            f"[b]Levels used:[/] {lab_items.levels_needed(benefit)}"
            + (f" of {level}" if level is not None else "")
            + " (10 a Specialization point, 20 a Characteristic point)"
        )
    lines += [
        todo(f"{p[0].upper()}{p[1:]}.") for p in lab_items.problems(saga, lab, benefit)
    ]
    lines += ["", f"[dim]Source: {escape(lab_items.SOURCE)}[/]"]
    return "\n".join(lines)


# -- Specializations --

#: How many Specializations count at once (ArM5 p.115): Activities, Arts,
#: and Techniques among those Arts.
MAX_ACTIVITY_SPECIALIZATIONS = 2
MAX_ART_SPECIALIZATIONS = 4
MAX_TECHNIQUE_SPECIALIZATIONS = 2


def counted_specializations(saga: Saga, lab: Laboratory) -> set[str]:
    """The Specializations that count: scored above 0 and not turned off."""
    return {score.name for score in specialization_scores(saga, lab) if score.counts}


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


def toggle_specialization(saga: Saga, lab: Laboratory, name: str) -> str | None:
    """Turn a Specialization off, or back on: None when done, else why not
    (it scores 0 or less, or turning it on would break a cap)."""
    score = next((s for s in specialization_scores(saga, lab) if s.name == name), None)
    if score is None or score.points <= 0:
        return f"{name} scores 0 or less, so it doesn't count either way."
    if not score.dropped:
        lab.dropped_specializations.append(name)
        return None
    broken = _broken_cap(counted_specializations(saga, lab) | {name})
    if broken is not None:
        label, cap = broken
        return (
            f"Can't turn {name} on: {cap} {label} Specializations already count, "
            "the most a laboratory can have. Turn one off first."
        )
    lab.dropped_specializations.remove(name)
    return None


def reconcile_dropped(
    saga: Saga, lab: Laboratory, previously_counted: Collection[str]
) -> None:
    """After a change that can add points: a Specialization that newly
    counts (not in `previously_counted`) is turned off if it would break a
    cap; ones that already counted stay on. Names with no points from any
    source any more are forgotten."""
    scores = specialization_scores(saga, lab)
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
    "[dim]Select a Specialization, Feature, Magic Item or Room to see its details.[/]"
)
INVENTORY_PANEL_HINT = (
    "[dim]Select Raw Vis, stores, a connection, a device or a book to see its "
    "details.[/]"
)


def _cap_count(saga: Saga, lab: Laboratory, group: Sequence[str], cap: int) -> str:
    """ "(3 of 4)": how many of `group` count against their cap, in the
    theme's error colour when over it."""
    count = len(counted_specializations(saga, lab) & set(group))
    text = f"({count} of {cap})"
    return f"[$text-error]{text}[/]" if count > cap else text


def specialization_rows(saga: Saga, lab: Laboratory) -> list[tuple[int | None, str]]:
    """The Specializations grid: an "Activity (1 of 2)" and an "Art (3 of
    4)" header (how many count against the cap), each over its rows "Ignem
    +3" (data index: position in LAB_SPECIALIZATIONS). One that's turned off
    is dimmed and struck through; one scoring 0 or less is dimmed."""
    scores = specialization_scores(saga, lab)
    width = max((len(s.name) for s in scores), default=0)
    rows: list[tuple[int | None, str]] = []
    for header, group, cap in (
        ("Activity", LAB_ACTIVITY_SPECIALIZATIONS, MAX_ACTIVITY_SPECIALIZATIONS),
        ("Art", ARTS, MAX_ART_SPECIALIZATIONS),
    ):
        in_group = [s for s in scores if s.name in group]
        rows.append((None, f"{header} {_cap_count(saga, lab, group, cap)}"))
        for score in in_group:
            label = f"{score.name:<{width}}  {score.points:+d}"
            if score.dropped and score.points > 0:
                label = f"[dim strike]{label}[/]"
            elif not score.counts:
                label = f"[dim]{label}[/]"
            rows.append((LAB_SPECIALIZATIONS.index(score.name), label))
    return rows


def specialization_info_text(saga: Saga, lab: Laboratory, index: int | None) -> str:
    """The details panel for the Specialization at `index` (into
    LAB_SPECIALIZATIONS): its score and whether it counts, where each point
    comes from, and for a Technique how many Techniques count (at most 2 of
    the 4 Arts)."""
    if index is None:
        return ATTRIBUTES_PANEL_HINT
    name = LAB_SPECIALIZATIONS[index]
    score = next((s for s in specialization_scores(saga, lab) if s.name == name), None)
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
        techniques = _cap_count(saga, lab, TECHNIQUES, MAX_TECHNIQUE_SPECIALIZATIONS)
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
        rows.append((index, f"{head}  {escape(specialty_source_label(entry))}"))
    return rows


def specialty_entry_info_text(lab: Laboratory, index: int | None) -> str:
    """The details panel for a hand-entered Specialization source."""
    if index is None:
        return ATTRIBUTES_PANEL_HINT
    entry = lab.specialties[index]
    if not entry.specialization:
        return f"[b]{escape(specialty_source_label(entry))}[/]\n\n" + todo(
            "Names no Activity or Art: edit it (e) to choose its Specialization."
        )
    return (
        f"[b]{entry.specialization} {entry.points:+d}[/]\n"
        f"[b]Source:[/] {escape(specialty_source_label(entry))}\n\n"
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
            f"({escape(_tier_note(lab, vf, definition))})",
        )
        for index, vf in enumerate(lab.virtues_flaws)
        if (definition := lab_catalog.get(vf.vf_id)) is not None
        and definition.type == vf_type
    ]


def _item_name(lab: Laboratory, virtue_id: str) -> str:
    """The device a Magic Item or Enchantment Virtue is, by the name its
    effects were saved with ("" when none is installed as it)."""
    return next(
        (b.name for b in lab.item_benefits if b.virtue_id == virtue_id and b.name), ""
    )


def _tier_note(
    lab: Laboratory, vf: VirtueFlawInstance, definition: LabVirtueFlawDef
) -> str:
    """ "Minor"; "Minor, from the Rowan Lectern" for one a magic item grants
    (taking no space); "Free, the Rowan Lectern" for the item's own Virtue
    ("Minor, very large, ..." when it takes space)."""
    benefit = lab_items.granting(lab, vf)
    if benefit is not None:
        return f"{definition.tier}, from {benefit.name or 'a magic item'}"
    if vf.vf_id in ITEM_VIRTUES:
        parts = [lab_items.tier(lab, vf, definition)]
        if lab_items.is_very_large(vf):
            parts.append("very large")
        if name := _item_name(lab, vf.id):
            parts.append(name)
        return ", ".join(parts)
    return definition.tier


def vf_info_text(lab: Laboratory, index: int | None, saga: Saga | None = None) -> str:
    """The details panel for the lab Virtue/Flaw at `index`: name, category,
    tier and points, its effect on the Characteristics (a Servant's read
    from its grog's Intelligence, given the `saga`), and the rules."""
    if index is None:
        return "[dim]Select a Virtue or Flaw to see its details.[/]"
    lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
    instance = lab.virtues_flaws[index]
    definition = lab_catalog.get(instance.vf_id)
    if definition is None:
        return escape(f"{instance.vf_id} (not in catalog)")
    tier = lab_items.tier(lab, instance, definition)
    cost = lab_items.space_cost(lab, instance, definition)
    lines = [
        f"[b]Name:[/] {escape(catalog.describe_virtue_flaw(instance, lab_catalog))}",
        f"[b]Category:[/] {definition.category}",
        f"[b]Tier:[/] {tier} {definition.type} ({_points(cost)})",
    ]
    benefit = lab_items.granting(lab, instance)
    if benefit is not None:
        lines.append(
            f"[b]Granted by:[/] {escape(benefit.name or 'a magic item')} "
            f"(as {definition.tier}: no space, no Build Points)"
        )
    if instance.vf_id in ITEM_VIRTUES:
        name = _item_name(lab, instance.id)
        size = (
            ", very large: a Minor Virtue" if lab_items.is_very_large(instance) else ""
        )
        lines.append(
            f"[b]Item:[/] {escape(name) if name else '(none installed)'}{size}"
        )
    if "servant" in definition.parameters:
        grog = servant(saga, instance) if saga is not None else None
        lines.append(
            f"[b]Servant:[/] {escape(grog.name) if grog else '(none: Intelligence typed)'}"
        )
    lines += _vf_effect_lines(instance, definition, saga=saga)
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
    saga: Saga | None = None,
) -> list[str]:
    """A lab Virtue/Flaw's Specialization grants and effects on the
    Characteristics, one details-panel line each."""
    lines = []
    grants = specialization_grant_text(instance, definition, unchosen=unchosen)
    if grants:
        lines.append(f"[b]Specializations:[/] {grants}")
    effects = characteristic_effect_texts(instance, definition, saga)
    if effects:
        lines.append(f"[b]Characteristics:[/] {escape(', '.join(effects))}")
    return lines


def characteristic_effect_texts(
    instance: VirtueFlawInstance,
    definition: LabVirtueFlawDef,
    saga: Saga | None = None,
) -> list[str]:
    """What it does to the Characteristics, in plain words, catalog order:
    "Safety +2 (Kurt's Intelligence +3, halved, rounded up)",
    "Aesthetics +1"."""
    return [
        reading_text(saga, instance, modifier)
        for modifier in definition.characteristic_readings
    ] + [
        f"{_characteristic_label(c)} {amount:+g}"
        for c, amount in definition.characteristic_modifiers.items()
    ]


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


def vf_warnings(lab: Laboratory, saga: Saga | None = None) -> str:
    """What's wrong with the lab's Virtues & Flaws as a whole, one line
    each in the theme's error colour -- or "" when nothing is: more Virtue
    points (net of Flaws) than Size + Refinement allow, more than one
    Focus, a Specialization not chosen, or a Virtue whose Safety is read
    from an Intelligence with none entered or its grog gone."""
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
        if definition is not None and definition.characteristic_readings:
            lines += _reading_warnings(saga, vf, definition)
    return "\n".join(problem(line) for line in lines)


def _reading_warnings(
    saga: Saga | None, instance: VirtueFlawInstance, definition: LabVirtueFlawDef
) -> list[str]:
    """A Virtue whose effect is read from an Intelligence: its grog gone
    (the typed number, if any, is used instead), or nothing entered."""
    lines = []
    named = instance.params.get("servant")
    if saga is not None and named and servant(saga, instance) is None:
        lines.append(
            f"{definition.name}: its servant is no longer one of the saga's grogs"
            " (the typed Intelligence is used)."
        )
    if entered_intelligence(saga, instance) is None:
        whom = (
            "no servant or Intelligence"
            if "servant" in definition.parameters
            else "no Intelligence"
        )
        lines.append(f"{definition.name}: {whom} entered, so it adds no Safety.")
    return lines


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
        markdown_text(entry.description)
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
        lines += ["", markdown_text(c.description)]
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


def diary_table(diary: Sequence[DiaryEntry]) -> Table:
    """Diary entries as a table (markup), in diary_rows' order."""
    return Table(
        ["Year", "Season", "Activity", "Entry"],
        [
            [
                str(entry.year),
                entry.season,
                escape(entry.activity or "-"),
                escape(entry.name),
            ]
            for entry in diary
        ],
        markup=True,
        stretch=3,
    )


def diary_info_text(diary: Sequence[DiaryEntry], index: int | None) -> str:
    """The details panel for a Diary entry: its name, date, Activity Type and
    the user's details (with **bold**/*italic*)."""
    if index is None:
        return "[dim]Select a Diary entry to see its details.[/]"
    entry = diary[index]
    details = markdown_text(entry.details) if entry.details else "[dim](no details)[/]"
    return "\n".join(
        [
            f"[b]{escape(entry.name)}[/]",
            f"[b]Date:[/] {entry.season} {entry.year}",
            f"[b]Activity:[/] {escape(entry.activity) or '(not set)'}",
            "",
            details,
        ]
    )
