"""The covenant's Diary tab: its rows, details panel and the
Loyalty points its entries add into the Loyalty block's Actions and Events.
Pounds and vis on an entry are a record only (Phase 4 covenant finances)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from . import catalog
from .arts import ART_ABBREVIATIONS
from .markup import escape, markdown_inline
from .models import (
    BOON_HOOK_DETAIL,
    SEASONS,
    STORY_EVENT,
    STORY_EVENT_STATUSES,
    Covenant,
    CovenantDiaryEntry,
)

#: Roughly how many stories overcome a Hook (Covenants, ch. 2).
STORIES_TO_OVERCOME: dict[str, int] = {"Minor": 6, "Major": 20}


@dataclass(frozen=True)
class Pool:
    """A Boon or Hook holding Build Points that come to light in play,
    through the Story Events linked to it."""

    name: str
    kind: str  # "Boon" or "Hook"
    #: What a Story Event's points do to the pool: "unlocked" / "found
    #: illusory".
    verb: str
    #: What's left of the pool: "still hidden" / "still believed real".
    rest: str


#: The pools' size: each Boon or Hook holds 250 Build Points.
POOL_POINTS = 250

#: The Boons and Hooks with a pool, by catalog id: Hidden Resources (ArM5
#: ch. 6, Minor Resources Boons: resources not yet available) and
#: Illusory Resources (Covenants ch. 2, Minor Resources Hooks:
#: improvements that don't really exist).
HIDDEN_RESOURCES = "covbh_boon_minor_hidden_resources"
ILLUSORY_RESOURCES = "covbh_hook_minor_illusory_resources"
POOLS: dict[str, Pool] = {
    HIDDEN_RESOURCES: Pool("Hidden Resources", "Boon", "unlocked", "still hidden"),
    ILLUSORY_RESOURCES: Pool(
        "Illusory Resources", "Hook", "found illusory", "still believed real"
    ),
}


def pool_of(covenant: Covenant, boon_hook_id: object) -> Pool | None:
    """The pool of the covenant's Boon/Hook `boon_hook_id`, or None if it
    has none (or isn't attached)."""
    if not boon_hook_id:
        return None
    return next(
        (
            POOLS[bh.vf_id]
            for bh in covenant.boons_hooks
            if bh.id == boon_hook_id and bh.vf_id in POOLS
        ),
        None,
    )


def unlocks(covenant: Covenant, boon_hook_id: str) -> list[int]:
    """Indexes into the Diary, in date order, of the Story Events that
    count against this Boon's or Hook's pool: linked to it, with points,
    and Resolved."""
    return [
        i
        for i in date_order(covenant.diary)
        if (entry := covenant.diary[i]).category == STORY_EVENT
        and entry.boon_hook_id == boon_hook_id
        and entry.build_points
        and entry.status == STORY_EVENT_STATUSES[1]
    ]


def unlocked(covenant: Covenant, boon_hook_id: str, *, skip: int | None = None) -> int:
    """The Build Points of this pool come to light so far (leaving out the
    Diary entry at `skip`, the one being edited)."""
    return sum(
        covenant.diary[i].build_points or 0
        for i in unlocks(covenant, boon_hook_id)
        if i != skip
    )


def pool_note(covenant: Covenant, boon_hook_id: str) -> str:
    """ "120 of 250 unlocked" (or "found illusory")."""
    pool = pool_of(covenant, boon_hook_id)
    verb = pool.verb if pool else "used"
    return f"{unlocked(covenant, boon_hook_id)} of {POOL_POINTS} {verb}"


def pool_short(covenant: Covenant, boon_hook_id: str) -> str:
    """ "120/250 BP": the pool note for a Boon's or Hook's row, kept short
    so the row fits its column."""
    return f"{unlocked(covenant, boon_hook_id)}/{POOL_POINTS} BP"


def pool_lines(covenant: Covenant, boon_hook_id: str) -> list[str]:
    """A pool's details-panel lines (markup): how much of it has come to
    light, and the Story Events that brought it."""
    lines = [f"[b]Build Points:[/] {pool_note(covenant, boon_hook_id)}"]
    for i in unlocks(covenant, boon_hook_id):
        entry = covenant.diary[i]
        lines.append(
            f"  {entry.season} {entry.year}  {escape(entry.name)}: {entry.build_points}"
        )
    return lines


def points_problem(
    covenant: Covenant, values: dict[str, object], skip: int | None
) -> str | None:
    """Why a Diary form's Build Points can't be saved, or None: above 0,
    and a Resolved Story Event can't take its Boon or Hook past its
    pool."""
    points = values.get("build_points")
    if not isinstance(points, int):
        return None
    if points <= 0:
        return "Build Points must be more than 0."
    boon_hook_id = values.get("boon_hook_id")
    pool = pool_of(covenant, boon_hook_id)
    if (
        values.get("status") != STORY_EVENT_STATUSES[1]
        or pool is None
        or not isinstance(boon_hook_id, str)
    ):
        return None
    left = POOL_POINTS - unlocked(covenant, boon_hook_id, skip=skip)
    if points > left:
        return f"Only {left} of this {pool.kind}'s {POOL_POINTS} Build Points are left."
    return None


def pools_text(covenant: Covenant) -> str:
    """The Build tab's Hidden and Illusory Resources blocks (markup),
    kept apart from the Initial / Current totals; "" for a covenant with
    neither."""
    blocks = []
    for vf_id, pool in POOLS.items():
        held = [bh for bh in covenant.boons_hooks if bh.vf_id == vf_id and bh.id]
        if not held:
            continue
        total = POOL_POINTS * len(held)
        found = sum(unlocked(covenant, bh.id) for bh in held)
        lines = [f"[b]{pool.name}[/] [dim](not in the totals above)[/]"]
        for bh in held:
            # The heading already names the pool: each line is its detail.
            name = bh.params.get(BOON_HOOK_DETAIL, "").strip() or "(no detail)"
            lines.append(f"  {escape(name)}: {pool_note(covenant, bh.id)}")
        lines.append(
            f"  Pool {total}, {pool.verb} {found}, {pool.rest} {total - found}"
        )
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def diary_loyalty(covenant: Covenant) -> int:
    """The Loyalty points of every Diary entry, added up."""
    return sum(entry.loyalty or 0 for entry in covenant.diary)


def actions_and_events(covenant: Covenant) -> int:
    """The Loyalty block's Actions and Events: the Diary's points plus the
    manual adjustment stored on the Loyalty block."""
    return diary_loyalty(covenant) + covenant.loyalty.actions_and_events


def date_order(diary: Sequence[CovenantDiaryEntry]) -> list[int]:
    """Indexes into `diary`, by year then season, ties in the order entered."""
    return sorted(
        range(len(diary)),
        key=lambda i: (diary[i].year, SEASONS.index(diary[i].season), i),
    )


def _number(value: float) -> str:
    return f"{value:+g}"


def amounts(entry: CovenantDiaryEntry) -> str:
    """The set amounts, compactly: "-12 £  +3 Vi  -3 Loyalty"."""
    parts = []
    if entry.pounds is not None:
        parts.append(f"{_number(entry.pounds)} £")
    if entry.vis_pawns is not None:
        art = ART_ABBREVIATIONS.get(entry.vis_art, entry.vis_art)
        parts.append(f"{entry.vis_pawns:+d} {art}".rstrip())
    if entry.loyalty is not None:
        parts.append(f"{entry.loyalty:+d} Loyalty")
    if entry.build_points is not None:
        parts.append(f"{entry.build_points} Build Points")
    return "  ".join(parts)


def rows(diary: Sequence[CovenantDiaryEntry]) -> list[tuple[int | None, str]]:
    """Diary entries as (index, "1220 Spring  Purchases & Sales  Bought a
    mill  -12 £") rows in date order; the category column is padded to the
    longest one, and a Story Event shows its [Open]/[Resolved] status."""
    categories = [entry.category or "-" for entry in diary]
    width = max((len(c) for c in categories), default=0)
    result: list[tuple[int | None, str]] = []
    for index in date_order(diary):
        entry = diary[index]
        label = (
            f"{entry.year} {entry.season:<6}  {categories[index]:<{width}}  "
            f"{escape(entry.name)}"
        )
        if entry.category == STORY_EVENT and entry.status:
            label += f"  \\[{entry.status}]"
        if extra := amounts(entry):
            label += f"  [dim]{escape(extra)}[/]"
        result.append((index, label))
    return result


def _ordinal(number: int) -> str:
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def linked_story_note(covenant: Covenant, index: int) -> str:
    """For a Story Event linked to a Hook: which story against that Hook it
    is, in date order, and roughly how many overcome it ("" otherwise)."""
    entry = covenant.diary[index]
    if entry.category != STORY_EVENT or not entry.boon_hook_id:
        return ""
    instance = next(
        (bh for bh in covenant.boons_hooks if bh.id == entry.boon_hook_id), None
    )
    definition = (
        catalog.load_covenant_boon_hook_catalog_by_id().get(instance.vf_id)
        if instance is not None
        else None
    )
    if definition is None or definition.type != "Hook":
        return ""
    linked = [
        i
        for i in date_order(covenant.diary)
        if covenant.diary[i].category == STORY_EVENT
        and covenant.diary[i].boon_hook_id == entry.boon_hook_id
    ]
    needed = STORIES_TO_OVERCOME.get(definition.tier)
    note = f"{_ordinal(linked.index(index) + 1)} story against this Hook"
    if needed is not None:
        note += f"; a {definition.tier} Hook takes about {needed} to overcome"
    return note


def boon_hook_label(covenant: Covenant, boon_hook_id: str | None) -> str:
    """The linked Boon/Hook's name, or a note that it's gone."""
    if not boon_hook_id:
        return ""
    instance = next((bh for bh in covenant.boons_hooks if bh.id == boon_hook_id), None)
    if instance is None:
        return "(no longer attached)"
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    definition = by_id.get(instance.vf_id)
    kind = definition.type if definition is not None else "Boon/Hook"
    return f"{catalog.describe_boon_hook(instance, by_id)} ({kind})"


def info_text(covenant: Covenant, index: int | None) -> str:
    """The details panel for a Diary entry."""
    if index is None:
        return "[dim]Select a Diary entry to see its details.[/]"
    entry = covenant.diary[index]
    lines = [
        f"[b]{escape(entry.name)}[/]",
        f"[b]Date:[/] {entry.season} {entry.year}",
        f"[b]Category:[/] {escape(entry.category) or '(not set)'}",
    ]
    if entry.pounds is not None:
        lines.append(f"[b]Pounds:[/] {_number(entry.pounds)}")
    if entry.vis_pawns is not None:
        art = escape(entry.vis_art) or "(Art not set)"
        lines.append(f"[b]Vis:[/] {entry.vis_pawns:+d} pawns of {art}")
    if entry.loyalty is not None:
        lines.append(f"[b]Loyalty points:[/] {entry.loyalty:+d}")
    if entry.category == STORY_EVENT:
        lines.append(f"[b]Status:[/] {entry.status or 'Open'}")
        if entry.revisit_year is not None:
            lines.append(f"[b]Revisit:[/] {entry.revisit_year}")
        if linked := boon_hook_label(covenant, entry.boon_hook_id):
            lines.append(f"[b]Linked to:[/] {escape(linked)}")
        if note := linked_story_note(covenant, index):
            lines.append(f"[dim]{escape(note)}[/]")
        if entry.build_points is not None:
            pool = pool_of(covenant, entry.boon_hook_id)
            verb = pool.verb if pool else "unlocked"
            lines.append(f"[b]Build Points {verb}:[/] {entry.build_points}")
            if pool is not None and entry.boon_hook_id:
                note = pool_note(covenant, entry.boon_hook_id)
                if entry.status != STORY_EVENT_STATUSES[1]:
                    note += "; these count once the event is Resolved"
                lines.append(f"[dim]{pool.name}: {note}[/]")
    details = (
        markdown_inline(entry.details) if entry.details else "[dim](no details)[/]"
    )
    return "\n".join([*lines, "", details])
