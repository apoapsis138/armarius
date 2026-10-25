"""What the Saga Content view manages -- no UI in here: the books in play,
the saga's own sources, and the shared catalogs (or single entries) the
saga hides.

The catalogs a saga can hide are a registry, one entry per catalog in the
style of the activity registry: its label and how to list its shared
entries, so the view and the hide picker treat every catalog alike and a
new catalog is one entry. Which kind of entry each holds is
catalog.SAGA_CATALOG_KINDS, where the pickers' hidden() check lives.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from . import catalog, sourcebooks, traditions
from . import house_rules as hr
from .markup import escape, fit, markdown_text
from .models import Saga, SagaSource


@dataclass(frozen=True)
class SagaCatalog:
    """One shared catalog a saga can hide, whole or entry by entry."""

    key: str
    label: str
    #: Every shared entry (the saga's own entries left out).
    shared: Callable[[], Sequence[Any]]


def _shared(load: Callable[[], Sequence[Any]]) -> Callable[[], list[Any]]:
    """The entries `load` lists, less the saga's own ones (the user-made
    entries use_saga merges into the Virtue/Flaw, Lab Virtue/Flaw and
    Boon/Hook catalogs)."""

    def shared() -> list[Any]:
        return [e for e in load() if not e.id.startswith("custom_")]

    return shared


CATALOGS: dict[str, SagaCatalog] = {
    c.key: c
    for c in (
        SagaCatalog(
            "virtues_flaws",
            "Virtues & Flaws",
            _shared(catalog.load_virtue_flaw_catalog),
        ),
        SagaCatalog(
            "lab_virtues_flaws",
            "Laboratory Virtues & Flaws",
            _shared(catalog.load_lab_virtue_flaw_catalog),
        ),
        SagaCatalog(
            "boons_hooks",
            "Boons & Hooks",
            _shared(catalog.load_covenant_boon_hook_catalog),
        ),
        SagaCatalog("abilities", "Abilities", catalog.load_ability_catalog),
        SagaCatalog("spells", "Spells", catalog.load_spell_catalog),
        SagaCatalog(
            "shapes_materials",
            "Shapes & Materials",
            catalog.load_shape_material_catalog,
        ),
        SagaCatalog("goods", "Goods", _shared(catalog.load_goods_catalog)),
    )
}
assert CATALOGS.keys() == catalog.SAGA_CATALOG_KINDS.keys()


# -------------------------------------------------------------- books in play


def every_book(saga: Saga) -> list[str]:
    """Every book the saga can have in play, in order: the core book, the
    supplements, then the saga's own sources."""
    return [sourcebooks.CORE, *sourcebooks.SUPPLEMENTS, *sourcebooks.saga_sources(saga)]


def is_in_play(saga: Saga, book: str) -> bool:
    return sourcebooks.in_play(book, sourcebooks.saga_books(saga))


def set_books_in_play(saga: Saga, ticked: Iterable[str]) -> None:
    """Put the `ticked` supplements and sources in play, and every other
    one out (the core book is always in play)."""
    saga.books_in_play = sourcebooks.normalized(ticked, sourcebooks.saga_sources(saga))
    catalog.use_saga(saga)


# ------------------------------------------------------------- saga sources


def source_problem(
    saga: Saga, values: dict[str, Any], existing: SagaSource | None = None
) -> str | None:
    """What's wrong with a source form's values, if anything."""
    taken = [s.abbreviation for s in saga.sources if s is not existing]
    return sourcebooks.source_problem(values.get("abbreviation") or "", taken) or None


def add_source(saga: Saga, values: dict[str, Any]) -> SagaSource:
    """Add a source of the saga's own; it starts in play."""
    source = SagaSource(
        abbreviation=values["abbreviation"].strip(),
        title=(values.get("title") or "").strip(),
    )
    saga.sources.append(source)
    if saga.books_in_play is not None:
        saga.books_in_play.append(source.abbreviation)
    catalog.use_saga(saga)
    return source


def update_source(saga: Saga, source: SagaSource, values: dict[str, Any]) -> None:
    """Change a source; a new abbreviation is carried to the entries citing
    it and to the books in play."""
    old = source.abbreviation
    new = values["abbreviation"].strip()
    source.title = (values.get("title") or "").strip()
    if new != old:
        hr.recite(saga, old, new)
        if saga.books_in_play is not None:
            saga.books_in_play = [new if b == old else b for b in saga.books_in_play]
        source.abbreviation = new
    catalog.use_saga(saga)


def remove_source(saga: Saga, source: SagaSource) -> None:
    """Remove a source no entry cites (see hr.citing)."""
    saga.sources.remove(source)
    if saga.books_in_play is not None:
        saga.books_in_play = [b for b in saga.books_in_play if b != source.abbreviation]
    catalog.use_saga(saga)


# ----------------------------------------------------------------- catalogs


def hidden_ids(saga: Saga, key: str) -> list[str]:
    return list(saga.hidden_entries.get(key, []))


def set_catalog_shown(saga: Saga, key: str, shown: bool) -> None:
    """Offer the shared catalog `key` in the saga's pickers, or not (its
    user-made entries are always offered)."""
    hidden = [k for k in saga.hidden_catalogs if k != key]
    if not shown:
        hidden.append(key)
    saga.hidden_catalogs = [k for k in CATALOGS if k in hidden]
    catalog.use_saga(saga)


def hide_entry(saga: Saga, key: str, entry_id: str) -> None:
    ids = hidden_ids(saga, key)
    if entry_id not in ids:
        saga.hidden_entries[key] = [*ids, entry_id]
    catalog.use_saga(saga)


def show_entry(saga: Saga, key: str, entry_id: str) -> None:
    ids = [i for i in hidden_ids(saga, key) if i != entry_id]
    if ids:
        saga.hidden_entries[key] = ids
    else:
        saga.hidden_entries.pop(key, None)
    catalog.use_saga(saga)


def hidden_entries(saga: Saga) -> list[tuple[str, Any]]:
    """The single entries the saga hides, as (catalog key, entry), by
    catalog then name. An id no longer in its catalog is left out."""
    found: list[tuple[str, Any]] = []
    for key, info in CATALOGS.items():
        ids = set(hidden_ids(saga, key))
        if ids:
            entries = [e for e in info.shared() if e.id in ids]
            found += [(key, e) for e in sorted(entries, key=lambda e: e.name)]
    return found


# --------------------------------------------------------------------- text

_ABBR_WIDTH = 10
_TITLE_WIDTH = 48
_LABEL_WIDTH = 28
_COUNT_WIDTH = 8


def _column(text: str, width: int) -> str:
    return text.ljust(width)


def _dim(text: str, width: int) -> str:
    """A column's text, dimmed (padded first, so the markup takes no room)."""
    return f"[dim]{text.ljust(width)}[/]"


def books_header() -> str:
    return f"  {'In play':<8} {'Book':<{_ABBR_WIDTH}} Title"


def book_row(saga: Saga, book: str) -> str:
    """One row of the Books in Play list (markup)."""
    if book == sourcebooks.CORE:
        mark = _column("always", 8)
    else:
        mark = _column("yes", 8) if is_in_play(saga, book) else _dim("no", 8)
    title = sourcebooks.title_of(book, saga)
    own = book in sourcebooks.saga_sources(saga)
    return (
        f"{mark} {escape(fit(book, _ABBR_WIDTH))} "
        f"{escape(fit(title, _TITLE_WIDTH)).rstrip()}"
        + ("  [dim](the saga's own)[/]" if own else "")
    )


def book_detail(saga: Saga, book: str | None) -> str:
    if book is None:
        return "[dim]Choose a book or source for its details; e picks the books.[/]"
    title = sourcebooks.title_of(book, saga)
    lines = [f"[b]{escape(title)}[/] ({escape(book)})"]
    if book == sourcebooks.CORE:
        lines.append("The core book: always in play.")
    else:
        lines.append("In play." if is_in_play(saga, book) else "Not in play.")
    if book in sourcebooks.saga_sources(saga):
        cited = hr.citing(saga, book)
        lines.append(
            f"The saga's own source, cited by {len(cited)} House "
            f"Rule{'s' if len(cited) != 1 else ''}."
        )
    return "\n".join(lines)


def traditions_header() -> str:
    return f"  {'On':<8} {'Book':<{_ABBR_WIDTH}} Tradition"


def tradition_rows(saga: Saga) -> list[str]:
    """One row per non-Hermetic tradition whose book is in play (markup):
    whether the troupe has turned it on (traditions.in_play's order)."""
    rows = []
    for tradition in traditions.in_play(saga):
        on = traditions.is_on(saga, tradition.id)
        mark = _column("yes", 8) if on else _dim("no", 8)
        rows.append(
            f"{mark} {escape(fit(tradition.source, _ABBR_WIDTH))} "
            f"{escape(tradition.name)}"
        )
    return rows


def tradition_detail(saga: Saga, index: int | None) -> str:
    """The chosen tradition: what it is, and whether it is offered."""
    shown = traditions.in_play(saga)
    if index is None or index >= len(shown):
        return (
            "[dim]Choose a tradition for its details; e picks the traditions "
            "this saga offers.[/]"
        )
    tradition = shown[index]
    on = traditions.is_on(saga, tradition.id)
    return "\n".join(
        [
            f"[b]{escape(tradition.name)}[/] "
            f"({escape(sourcebooks.titles(tradition.source))}, {tradition.realm})",
            escape(tradition.description),
            "Offered: characters can join it."
            if on
            else "Not offered: turn it on to let characters join it.",
        ]
    )


def sources_header() -> str:
    return f"  {'Source':<{_ABBR_WIDTH}} {'Title':<{_TITLE_WIDTH}} Entries"


def source_row(saga: Saga, source: SagaSource) -> str:
    return (
        f"{escape(fit(source.abbreviation, _ABBR_WIDTH))} "
        f"{escape(fit(source.title, _TITLE_WIDTH))} "
        f"{len(hr.citing(saga, source.abbreviation))}"
    )


def source_detail(saga: Saga, source: SagaSource | None) -> str:
    if source is None:
        return "[dim]Choose a source for its details; a adds one.[/]"
    cited = hr.citing(saga, source.abbreviation)
    state = "In play" if is_in_play(saga, source.abbreviation) else "Not in play"
    lines = [
        f"[b]{escape(source.title or source.abbreviation)}[/] "
        f"({escape(source.abbreviation)})",
        f"{state}. Cited by: "
        + (escape(", ".join(e.name for e in cited)) if cited else "(no entry yet)"),
    ]
    return "\n".join(lines)


def catalogs_header() -> str:
    return (
        f"  {'Catalog':<{_LABEL_WIDTH}} {'Offered':<8} "
        f"{'Entries':>{_COUNT_WIDTH}} {'Hidden':>{_COUNT_WIDTH}}"
    )


def catalog_row(saga: Saga, key: str) -> str:
    info = CATALOGS[key]
    shown = key not in saga.hidden_catalogs
    return (
        f"{escape(fit(info.label, _LABEL_WIDTH))} "
        f"{_column('yes', 8) if shown else _dim('no', 8)} "
        f"{len(info.shared()):>{_COUNT_WIDTH}} "
        f"{len(hidden_ids(saga, key)):>{_COUNT_WIDTH}}"
    )


def catalog_detail(saga: Saga, key: str | None) -> str:
    if key is None:
        return "[dim]Choose a catalog or entry for its details; e offers a catalog.[/]"
    info = CATALOGS[key]
    shown = key not in saga.hidden_catalogs
    lines = [
        f"[b]{escape(info.label)}[/]",
        f"{len(info.shared())} shared entries; "
        + (
            "offered in this saga's pickers."
            if shown
            else "not offered: pickers list only the saga's own entries "
            "(F3 shows the others)."
        ),
        f"Single entries hidden: {len(hidden_ids(saga, key))}.",
    ]
    return "\n".join(lines)


def hidden_header() -> str:
    return f"  {'Entry':<{_TITLE_WIDTH}} Catalog"


def hidden_row(key: str, entry: Any) -> str:
    return f"{escape(fit(entry.name, _TITLE_WIDTH))} {CATALOGS[key].label}"


def hidden_detail(chosen: tuple[str, Any] | None) -> str:
    if chosen is None:
        return "[dim]Choose an entry for its details; a hides another.[/]"
    key, entry = chosen
    lines = [
        f"[b]{escape(entry.name)}[/]",
        f"{CATALOGS[key].label}, from {escape(getattr(entry, 'source', '') or '?')}"
        ". Hidden in this saga.",
    ]
    description = getattr(entry, "description", "") or ""
    if description.strip():
        lines += ["", markdown_text(description.strip())]
    return "\n".join(lines)
