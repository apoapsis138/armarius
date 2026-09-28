"""The covenant's Diary tab (STORY-406): its rows, details panel and the
Loyalty points its entries add into the Loyalty block's Actions and Events.
Pounds and vis on an entry are a record only (Phase 4 covenant finances)."""

from __future__ import annotations

from collections.abc import Sequence

from . import catalog
from .arts import ART_ABBREVIATIONS
from .markup import escape, markdown_inline
from .models import (
    SEASONS,
    STORY_EVENT,
    Covenant,
    CovenantDiaryEntry,
)

#: Roughly how many stories overcome a Hook (Covenants, ch. 2).
STORIES_TO_OVERCOME: dict[str, int] = {"Minor": 6, "Major": 20}


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
    details = (
        markdown_inline(entry.details) if entry.details else "[dim](no details)[/]"
    )
    return "\n".join([*lines, "", details])
