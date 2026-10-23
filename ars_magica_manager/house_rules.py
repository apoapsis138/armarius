"""User-made catalog entries kept with a saga: house rules, and
entries from books the shared catalogs don't carry.

Three kinds, each of the shape its shared catalog uses: character Virtues
and Flaws (VirtueFlawDef), laboratory Virtues and Flaws (LabVirtueFlawDef)
and covenant Boons and Hooks (CovenantBoonHookDef). They are text only for
now: a name, type, tier (which gives the points: Free 0, Minor 1, Major 3)
and description, with no effects the rules engine applies. A character's
or covenant's entry may also ask for choices when it is taken (its
`parameters`: "form", "ability"...), as the books' Puissant (Ability)
does. They cite no
book, so they are always in play -- unless they cite one of the saga's own
sources (Saga.sources), in or out of play like a book -- and pickers offer
them alongside the catalog's once the saga is the one in use
(catalog.use_saga).
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from . import catalog, sourcebooks, storage
from .markup import escape, fit, markdown_text
from .models import (
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    BOON_HOOK_RESOURCE,
    BOON_HOOK_SITUATION,
    BOON_HOOK_UNKNOWN,
    COVENANT_BOON_HOOK_CATEGORIES,
    VIRTUE_FLAW_TIER_COST,
    CovenantBoonHookDef,
    LabVirtueFlawDef,
    Saga,
    VirtueFlawDef,
)

CHARACTER, LABORATORY, COVENANT = "character", "laboratory", "covenant"
KINDS: tuple[str, ...] = (CHARACTER, LABORATORY, COVENANT)
KIND_LABELS: dict[str, str] = {
    CHARACTER: "Character Virtue or Flaw",
    LABORATORY: "Laboratory Virtue or Flaw",
    COVENANT: "Covenant Boon or Hook",
}
KIND_SHORT: dict[str, str] = {
    CHARACTER: "Character",
    LABORATORY: "Laboratory",
    COVENANT: "Covenant",
}
TYPES: dict[str, tuple[str, ...]] = {
    CHARACTER: ("Virtue", "Flaw"),
    LABORATORY: ("Virtue", "Flaw"),
    COVENANT: ("Boon", "Hook"),
}
#: The side that gives points (a negative cost).
_GIVES_POINTS = ("Flaw", "Hook")
TIERS: tuple[str, ...] = ("Minor", "Major", "Free")
#: The types each kind's book sorts its entries into.
CATEGORIES: dict[str, tuple[str, ...]] = {
    CHARACTER: (
        "General",
        "Hermetic",
        "Supernatural",
        "Social Status",
        "Personality",
        "Story",
        "Mystery",
        "Heroic",
        "Child",
        "Special",
    ),
    LABORATORY: ("Structure", "Outfittings", "Supernatural"),
    COVENANT: COVENANT_BOON_HOOK_CATEGORIES,
}
_ID_PREFIX: dict[str, str] = {
    CHARACTER: "custom_vf",
    LABORATORY: "custom_labvf",
    COVENANT: "custom_covbh",
}

Entry = VirtueFlawDef | LabVirtueFlawDef | CovenantBoonHookDef

#: The kinds whose entries may ask for choices (a laboratory Virtue's
#: parameters are what its effect is read from, not choices).
ASKING_KINDS: tuple[str, ...] = (CHARACTER, COVENANT)
#: The choices offered from a list rather than typed.
LISTED_CHOICES: tuple[str, ...] = (
    "characteristic",
    "ability",
    "art",
    "technique",
    "form",
    "realm",
    "blood",
)
#: Names a Boon's or Hook's own params already use.
_BOON_HOOK_KEYS = (
    BOON_HOOK_DETAIL,
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_UNKNOWN,
    BOON_HOOK_RESOURCE,
    BOON_HOOK_SITUATION,
)


def parse_choices(text: str) -> list[str]:
    """The choices an entry asks for, from "Form, Ability": lower case, in
    the order written, blanks left out."""
    return [name.strip().lower() for name in text.split(",") if name.strip()]


def choices_problem(kind: str, names: list[str]) -> str | None:
    """What's wrong with the choices an entry asks for, if anything."""
    if names and kind not in ASKING_KINDS:
        return "A laboratory Virtue or Flaw can't ask for choices."
    for name in names:
        if not all(part.isalpha() for part in name.split()):
            return f"Choice names are words only: {name!r}."
        if kind == COVENANT and name in _BOON_HOOK_KEYS:
            return f"{name.title()} is already a Boon's or Hook's own field."
    if len(set(names)) != len(names):
        return "Each choice can be asked for only once."
    return None


def entries_of(saga: Saga, kind: str) -> list[Any]:
    """The saga's own list for `kind` (the one to add to or remove from)."""
    return {
        CHARACTER: saga.custom_virtues_flaws,
        LABORATORY: saga.custom_lab_virtues_flaws,
        COVENANT: saga.custom_boons_hooks,
    }[kind]


def all_entries(saga: Saga) -> list[tuple[str, Entry]]:
    """Every user-made entry as (kind, entry), kind by kind in KINDS order,
    each kind in the order added."""
    return [(kind, entry) for kind in KINDS for entry in entries_of(saga, kind)]


def cost(entry_type: str, tier: str) -> int:
    """The points: 0 / 1 / 3 by tier; a Flaw or Hook gives them (negative)."""
    points = int(VIRTUE_FLAW_TIER_COST[tier])
    return -points if entry_type in _GIVES_POINTS else points


def points_text(entry_type: str, tier: str) -> str:
    """ "Minor Flaw: gives 1 point" / "Major Boon: costs 3 points"."""
    points = abs(cost(entry_type, tier))
    if not points:
        return f"Free {entry_type}: no points"
    verb = "gives" if entry_type in _GIVES_POINTS else "costs"
    return f"{tier} {entry_type}: {verb} {points} point{'s' if points != 1 else ''}"


def form_problem(
    saga: Saga, kind: str, values: dict[str, Any], existing: Entry | None = None
) -> str | None:
    """What's wrong with a form's values, if anything: a name is needed, and
    two user-made entries of one kind can't share a name, type and tier."""
    name = (values.get("name") or "").strip()
    if not name:
        return "Name is required."
    if problem := choices_problem(kind, values.get("parameters") or []):
        return problem
    for other in entries_of(saga, kind):
        if other is existing:
            continue
        if (other.name.lower(), other.type, other.tier) == (
            name.lower(),
            values.get("type"),
            values.get("tier"),
        ):
            return f"There is already a {other.tier} {other.type} called {other.name}."
    return None


def _fields(kind: str, values: dict[str, Any]) -> dict[str, Any]:
    entry_type, tier = values["type"], values["tier"]
    asks = (
        {"parameters": list(values.get("parameters") or [])}
        if kind in ASKING_KINDS
        else {}
    )
    return {
        **asks,
        "name": values["name"].strip(),
        "type": entry_type,
        "tier": tier,
        "cost": cost(entry_type, tier),
        "category": values.get("category") or CATEGORIES[kind][0],
        "repeatable": bool(values.get("repeatable")),
        "description": values.get("description") or "",
        "source": values.get("source") or "",
    }


def add(saga: Saga, kind: str, values: dict[str, Any]) -> Entry:
    """Add a user-made entry of `kind` from a form's values (name, type,
    tier, category, repeatable, description, the choices it asks for,
    and the saga source it cites, if any)."""
    fields = _fields(kind, values)
    listed = entries_of(saga, kind)
    taken = [e.id for e in listed] + list(_catalog_by_id(kind))
    entry_id = storage.generate_unique_id(f"{_ID_PREFIX[kind]}_{fields['name']}", taken)
    made: Entry
    if kind == CHARACTER:
        made = VirtueFlawDef(id=entry_id, **fields)
    elif kind == LABORATORY:
        made = LabVirtueFlawDef(id=entry_id, **fields)
    else:
        made = CovenantBoonHookDef(id=entry_id, **fields)
    listed.append(made)
    catalog.use_saga(saga)
    return made


def update(saga: Saga, kind: str, entry: Entry, values: dict[str, Any]) -> Entry:
    """Change a user-made entry (its id stays, so whoever holds it keeps
    it, with its new name and points): definitions are frozen, so the
    changed one takes the old one's place in the saga's list. Returns it."""
    changed = _replace(saga, kind, entry, **_fields(kind, values))
    catalog.use_saga(saga)
    return changed


def recite(saga: Saga, old: str, new: str) -> None:
    """Make the entries citing the saga source `old` cite `new`."""
    for kind, entry in all_entries(saga):
        if entry.source == old:
            _replace(saga, kind, entry, source=new)


def _replace(saga: Saga, kind: str, entry: Entry, **changes: Any) -> Entry:
    """`entry` with `changes`, in its place in the saga's list."""
    listed = entries_of(saga, kind)
    index = next(i for i, e in enumerate(listed) if e is entry)
    listed[index] = changed = replace(entry, **changes)
    return changed


def citing(saga: Saga, source: str) -> list[Entry]:
    """The user-made entries that cite the saga source `source`."""
    return [entry for _, entry in all_entries(saga) if entry.source == source]


def remove(saga: Saga, kind: str, entry: Entry) -> None:
    entries_of(saga, kind).remove(entry)
    catalog.use_saga(saga)


def _catalog_by_id(kind: str) -> dict[str, Any]:
    return {
        CHARACTER: catalog.load_virtue_flaw_catalog_by_id,
        LABORATORY: catalog.load_lab_virtue_flaw_catalog_by_id,
        COVENANT: catalog.load_covenant_boon_hook_catalog_by_id,
    }[kind]()


def used_by(saga: Saga, kind: str, entry: Entry) -> list[str]:
    """The names of the records holding the entry (it can't be deleted while
    any does: they would be left with an entry nothing describes)."""
    if kind == CHARACTER:
        holders = [
            c.name
            for c in saga.characters
            if any(vf.vf_id == entry.id for vf in c.virtues_flaws)
        ] + [
            f.name
            for f in saga.familiars
            if any(vf.vf_id == entry.id for vf in f.virtues_flaws)
        ]
    elif kind == LABORATORY:
        holders = [
            lab.name
            for lab in saga.laboratories
            if any(vf.vf_id == entry.id for vf in lab.virtues_flaws)
        ]
    else:
        holders = [
            c.name
            for c in saga.covenants
            if any(bh.vf_id == entry.id for bh in c.boons_hooks)
        ]
    return holders


# ------------------------------------------------------------------- text


_NAME_WIDTH = 26
_KIND_WIDTH = 11
_TYPE_WIDTH = 7
_TIER_WIDTH = 6
_POINTS_WIDTH = 6


def table_header() -> str:
    """The column titles; the two-character indent is the selector marker."""
    return (
        f"  {'Name':<{_NAME_WIDTH}} {'For':<{_KIND_WIDTH}} "
        f"{'Type':<{_TYPE_WIDTH}} {'Tier':<{_TIER_WIDTH}} "
        f"{'Points':>{_POINTS_WIDTH}}"
    )


def row_label(kind: str, entry: Entry) -> str:
    """One row (markup), lined up with `table_header` (the Category is in
    the details panel: the row has to fit a 120-column screen)."""
    return (
        f"{escape(fit(entry.name, _NAME_WIDTH))} "
        f"{KIND_SHORT[kind]:<{_KIND_WIDTH}} "
        f"{entry.type:<{_TYPE_WIDTH}} {entry.tier:<{_TIER_WIDTH}} "
        f"{(f'{int(entry.cost):+d}' if entry.cost else '0'):>{_POINTS_WIDTH}}"
    )


def detail_text(saga: Saga, chosen: tuple[str, Entry] | None) -> str:
    """The details panel (markup) for a chosen entry."""
    if chosen is None:
        return "[dim]Choose an entry to see who holds it; a adds one.[/]"
    kind, entry = chosen
    holders = used_by(saga, kind, entry)
    lines = [
        f"[b]{escape(entry.name)}[/]",
        f"[b]For:[/] {KIND_LABELS[kind]}   [b]Category:[/] {escape(entry.category)}",
        f"[b]Points:[/] {points_text(entry.type, entry.tier)}"
        + ("   May be taken more than once." if entry.repeatable else ""),
        f"[b]Held by:[/] {escape(', '.join(holders)) if holders else '(no one yet)'}",
    ]
    asks = getattr(entry, "parameters", []) if kind in ASKING_KINDS else []
    if asks:
        lines.insert(3, f"[b]Asks for:[/] {escape(', '.join(a.title() for a in asks))}")
    if entry.source:
        title = sourcebooks.title_of(entry.source, saga) or entry.source
        books = sourcebooks.saga_books(saga)
        state = "" if sourcebooks.in_play(entry.source, books) else " (not in play)"
        lines.insert(3, f"[b]Source:[/] {escape(title)}{state}")
    if entry.description.strip():
        lines += ["", markdown_text(entry.description.strip())]
    return "\n".join(lines)
