"""The lists a kind of neighbour keeps in its details (a lord's castles,
a town's guilds and fairs), the tab that shows them, and the Add, Edit
and Delete every such list shares.

A list is kept in Neighbour.details under its name, as a list of plain
dicts, so a kind needs no model of its own and an old save loads them
unchanged."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .commands import Command, Confirm, Form, SectionOps
from .form_spec import DialogField
from .grids import Grid
from .markup import escape
from .models import Neighbour, Saga

Entry = dict[str, Any]


@dataclass(frozen=True)
class KindList:
    """A list a kind shows: its section's id and title, its rows, and its
    Add, Edit and Delete."""

    section_id: str
    title: Callable[[Saga, Neighbour], str]
    grid: Callable[[Saga, Neighbour], Grid]
    ops: Callable[[Saga, Neighbour], SectionOps]


@dataclass(frozen=True)
class KindTab:
    """The tab (a chapter, on the desktop) a kind adds to its neighbours'
    sheets: what is worked out for it, then its lists."""

    title: str
    tab_id: str
    lists: tuple[KindList, ...]


def details_list(neighbour: Neighbour, name: str) -> list[Entry]:
    """The list `name` in the neighbour's details, made empty if
    missing."""
    found = neighbour.details.setdefault(name, [])
    assert isinstance(found, list)
    return found


def list_ops(
    saga: Saga,
    neighbour: Neighbour,
    name: str,
    noun: str,
    fields: Callable[[Saga, Neighbour, Entry | None], list[DialogField]],
    describe: Callable[[Entry], str],
    validate: Callable[[dict[str, Any]], str | None] | None = None,
    after: Callable[[], None] = lambda: None,
) -> SectionOps:
    """Add, Edit and Delete on the list `name`: a form of `fields` titled
    "Add a `noun`" (or an), and a confirmation naming `describe(entry)`; `after`
    runs once each has changed the list."""

    article = "an" if noun[:1] in "AEIOU" else "a"

    def entries() -> list[Entry]:
        return details_list(neighbour, name)

    def form(entry: Entry | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = entry if entry is not None else {}
            target.update(values)
            if entry is None:
                entries().append(target)
            after()

        return Form(
            f"Add {article} {noun}" if entry is None else f"Edit {article} {noun}",
            lambda: fields(saga, neighbour, entry),
            apply,
            validate=validate,
            save_label="Add" if entry is None else "Save",
        )

    def remove(index: int) -> Command:
        entry = entries()[index]

        def delete() -> None:
            entries().remove(entry)
            after()

        return Confirm(f"Delete {escape(describe(entry))}?", delete)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(entries()[index]),
        remove=remove,
        rows=lambda: [describe(e) for e in entries()],
    )
