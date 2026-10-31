"""Overlays: what a supplement adds to the Tribunal packs and what it
overwrites there, as a file of its own (packs.OVERLAY). A Tribunal pack
stays as its own book has it, so a saga without the supplement matches
that book.

A supplement's parts are ordinary parts of each Tribunal's Builder, run
only when asked for. Its overlay is the difference between the pack built
with them and the pack built without, so nothing is written twice."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .. import packs, transfer
from ..models import Saga
from . import PACKS, PACKS_DIR, BookPack

#: The saga's lists a supplement can change a record of, by the name
#: packs.OVERLAY_KINDS knows them under.
LISTS = tuple(packs.OVERLAY_KINDS)


@dataclass(frozen=True)
class Overlay:
    """A supplement's overlay: its file's stem, the book's abbreviation,
    its name, and its credit line."""

    key: str
    book: str
    name: str
    source: str


OVERLAYS: dict[str, Overlay] = {}


def register(overlay: Overlay) -> None:
    OVERLAYS[overlay.key] = overlay


def _changes(base: Saga, full: Saga) -> list[dict[str, Any]]:
    """Each field the supplement changes on a record the Tribunal pack
    already has: the record's kind and name, the field, and what it was
    and becomes."""
    found = []
    for kind in LISTS:
        before = {r.id: r for r in getattr(base, kind)}
        for record in getattr(full, kind):
            old = before.get(record.id)
            if old is None:
                continue
            was, now = asdict(old), asdict(record)
            for key in now:
                if packs.without_random_ids(was[key]) != packs.without_random_ids(
                    now[key]
                ):
                    found.append(
                        {
                            "list": kind,
                            "name": record.name,
                            "kind": getattr(record, "kind", ""),
                            "field": key,
                            "was": was[key],
                            "value": now[key],
                        }
                    )
    return found


def section(pack: BookPack, overlay: Overlay) -> dict[str, Any]:
    """What `overlay` does to one Tribunal pack: the records it adds, as a
    pack of their own, and the fields it changes."""
    base, full = pack.assemble().saga, pack.assemble((overlay.book,)).saga

    def new(records: list[Any], old: list[Any]) -> list[Any]:
        held = {r.id for r in old}
        return [r for r in records if r.id not in held]

    added = transfer.bundle_data(
        full,
        packs.PACK,
        overlay.name,
        covenants=new(full.covenants, base.covenants),
        characters=new(full.characters, base.characters),
        laboratories=new(full.laboratories, base.laboratories),
        tribunals=full.tribunals,
        neighbours=new(full.neighbours, base.neighbours),
        creatures=new(full.creatures, base.creatures),
    )
    return {
        "tribunal": full.tribunals[0].name if full.tribunals else "",
        "pack": added,
        "changes": _changes(base, full),
    }


def data(overlay: Overlay) -> dict[str, Any]:
    """The overlay as JSON-ready data: an empty pack, by its book and
    name, holding one section for each Tribunal pack it touches."""
    sections = [
        section(pack, overlay)
        for pack in PACKS.values()
        if overlay.book in pack.supplements
    ]
    first = sections[0]["pack"]
    return {
        **{k: v for k, v in first.items() if k not in ("saga", "links", "stubs")},
        "saga": {},
        "name": overlay.name,
        "book": overlay.book,
        "source": overlay.source,
        packs.OVERLAY: sections,
    }


def path_of(overlay: Overlay) -> Any:
    return PACKS_DIR / f"{overlay.key}{transfer.SUFFIX}"


register(
    Overlay(
        "through_the_aegis",
        "TtA",
        "Through the Aegis",
        "Through the Aegis: Developed Covenants, by Atlas Games; summarised, "
        "not quoted.",
    )
)
