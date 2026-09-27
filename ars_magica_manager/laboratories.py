"""Laboratory rules computed from a Laboratory and the lab Virtue/Flaw
catalog: aura, occupied Size, room for Virtues, Base Safety and each
Characteristic's total, the Specialization scores and their caps -- and the
markup text of the lab sheet's lists and details panels (Virtues & Flaws,
Specializations, Rooms, Equipment & Stores, Raw Vis, Diary). Like the other
domain modules it returns markup text, never widgets."""

from __future__ import annotations

from collections.abc import Collection, Iterable, Sequence
from dataclasses import dataclass

from . import catalog
from .arts import ARTS, TECHNIQUES
from .markup import escape, markdown_inline
from .models import (
    LAB_ACTIVITY_SPECIALIZATIONS,
    LAB_SPECIALIZATIONS,
    DiaryEntry,
    Laboratory,
    LabSpecialtyEntry,
    LabVirtueFlawDef,
    NamedDescription,
)

#: The two Focus Flaws; a lab may only have one Focus at a time.
FOCUS_FLAW_IDS = frozenset({"labvf_lesser_focus", "labvf_greater_focus"})


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
    """Every Specialization the lab has points in (from any source, even if
    they sum to 0 or less), in LAB_SPECIALIZATIONS order."""
    sources: dict[str, list[tuple[str, int]]] = {}
    for entry in lab.specialties:
        if entry.specialization in LAB_SPECIALIZATIONS:
            sources.setdefault(entry.specialization, []).append(
                (_source_label(entry), entry.points)
            )
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


def caps_text(lab: Laboratory) -> str:
    """ "Activity 2/2, Art 3/4 (Techniques 1/2)": how many Specializations
    count against each cap, a count over its cap in the theme's error
    colour."""
    counted = counted_specializations(lab)
    parts = []
    for label, group, cap in _CAPS:
        count = len(counted & set(group))
        text = f"{label}{'s' if group is TECHNIQUES else ''} {count}/{cap}"
        parts.append(f"[$text-error]{text}[/]" if count > cap else text)
    activity, art, techniques = parts
    return f"{activity}, {art} ({techniques})"


def specialization_rows(lab: Laboratory) -> list[tuple[int | None, str]]:
    """The Specializations grid: an "Activity" and an "Art" header, each
    over its rows "Ignem  +3" (data index: position in LAB_SPECIALIZATIONS).
    One that's turned off is dimmed and struck through; one scoring 0 or
    less is dimmed."""
    scores = specialization_scores(lab)
    width = max((len(s.name) for s in scores), default=0)
    rows: list[tuple[int | None, str]] = []
    for header, group in (
        ("Activity", LAB_ACTIVITY_SPECIALIZATIONS),
        ("Art", ARTS),
    ):
        in_group = [s for s in scores if s.name in group]
        if not in_group:
            continue
        rows.append((None, header))
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
    comes from, and the caps."""
    caps = f"[b]Counting:[/] {caps_text(lab)}"
    if index is None:
        return (
            "[dim]Select a Specialization to see where its points come from; "
            "Space turns it off or on.[/]\n\n" + caps
        )
    name = LAB_SPECIALIZATIONS[index]
    score = next((s for s in specialization_scores(lab) if s.name == name), None)
    if score is None:
        return caps
    if score.points <= 0:
        status = "doesn't count (0 or less)"
    elif score.dropped:
        status = "turned off (Space turns it back on)"
    else:
        status = "counts (Space turns it off)"
    lines = [f"[b]{name} {score.points:+d}[/]: {status}", "", "[b]Sources:[/]"]
    lines += [f"  {points:+d}  {escape(label)}" for label, points in score.sources]
    return "\n".join([*lines, "", caps])


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
            head = "[$text-error]needs a Specialization[/]"
        rows.append((index, f"{head}  {escape(_source_label(entry))}"))
    return rows


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
        return "[dim]Select a Virtue or Flaw to read its rules.[/]"
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
    if definition.characteristic_modifiers:
        effects = ", ".join(
            f"{_characteristic_label(c)} {amount:+d}"
            for c, amount in definition.characteristic_modifiers.items()
        )
        lines.append(f"[b]Characteristics:[/] {effects}")
    lines += ["", "[b]Rules:[/]", escape(definition.description)]
    return "\n".join(lines)


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
    return "\n".join(f"[$text-error]{line}[/]" for line in lines)


def named_rows(entries: Sequence[NamedDescription]) -> list[tuple[int | None, str]]:
    """Rooms or Equipment & Stores as (index, name) rows."""
    return [(index, escape(entry.name)) for index, entry in enumerate(entries)]


def named_info_text(
    entries: Sequence[NamedDescription], index: int | None, noun: str
) -> str:
    """The details panel for a Room or Equipment & Stores entry: its name and
    the user's description (with **bold**/*italic*)."""
    if index is None:
        return f"[dim]Select {noun} to see its description.[/]"
    entry = entries[index]
    description = (
        markdown_inline(entry.description)
        if entry.description
        else "[dim](no description)[/]"
    )
    return f"[b]{escape(entry.name)}[/]\n\n{description}"


def raw_vis_rows(lab: Laboratory) -> list[tuple[int | None, str]]:
    """The lab's Raw Vis as (index into sorted(lab.raw_vis), "Art: N pawn(s)")
    rows, same as a character's."""
    return [
        (index, f"{art.title()}: {lab.raw_vis[art]} pawn(s)")
        for index, art in enumerate(sorted(lab.raw_vis))
    ]


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
