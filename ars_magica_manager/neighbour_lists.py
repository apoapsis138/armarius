"""The lists a kind of neighbour keeps in its details (a lord's castles,
a town's guilds and fairs), the tab that shows them, and the Add, Edit
and Delete every such list shares.

A list is kept in Neighbour.details under its name, as a list of plain
dicts, so a kind needs no model of its own and an old save loads them
unchanged."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, cast

from .commands import Command, Confirm, Form, SectionOps
from .form_spec import DialogField
from .grids import Grid
from .markup import escape
from .models import Neighbour, Saga, details_list
from .references import Fact

Entry = dict[str, Any]


@dataclass(frozen=True)
class LedgerEntry:
    """A row of a list drawn as an entry ruled off on the desktop's page
    rather than a table's row: a mark in the margin, its heading, an
    italic line beside it, a badge (its words and the theme colour that
    tones it), its words and a note under them; `subtitle` heads it in
    the inspector."""

    title: str
    rubric: str = ""
    meta: str = ""
    badge: str = ""
    tone: str = "label"
    body: str = ""
    note: str = ""
    subtitle: str = ""


@dataclass(frozen=True)
class Toggle:
    """A chip above a list on the desktop: its words, whether it is lit,
    and what clicking it does (`flip`, run as a step)."""

    label: str
    on: bool
    flip: Callable[[], None]


@dataclass(frozen=True)
class KindList:
    """A list a kind shows: its section's id and title, its rows, and its
    Add, Edit and Delete. `info` is a row (by its key) in full, as markup
    for the desktop's inspector, when that holds more than its columns;
    without it the inspector shows the row's columns (Grid.row_text)."""

    section_id: str
    title: Callable[[Saga, Neighbour], str]
    grid: Callable[[Saga, Neighbour], Grid]
    ops: Callable[[Saga, Neighbour], SectionOps]
    info: Callable[[Saga, Neighbour, int], str] | None = None
    #: A line shown above the list (what a town its size is expected to
    #: have), as markup; "" for none.
    header: Callable[[Saga, Neighbour], str] | None = None
    #: Each row as an entry ruled off on the desktop's page, in the
    #: grid's order (a tomb's curses); None draws the grid as a table.
    ledger: Callable[[Saga, Neighbour], list[LedgerEntry]] | None = None
    #: Chips above the list on the desktop, each turning part of it on or
    #: off (a history's records); the terminal sets the same in a form.
    toggles: Callable[[Saga, Neighbour], list[Toggle]] | None = None


@dataclass(frozen=True)
class KindBlock:
    """A section of worked-out text a kind's tab shows between its lists
    (a town charter's terms, what the charter gives): its `facts` (a grid
    of them on the desktop), its `text` as markup, then `columns`, side by
    side, each a column of markup; `edit` is the section's one Edit, named
    `edit_label` on the desktop. It follows the list whose section is
    `after` ("" puts it first)."""

    section_id: str
    title: str
    text: Callable[[Saga, Neighbour], str] | None = None
    edit: Callable[[Saga, Neighbour], Command] | None = None
    edit_label: str = "Edit"
    after: str = ""
    columns: Callable[[Saga, Neighbour], list[str]] | None = None
    facts: Callable[[Saga, Neighbour], list[Fact]] | None = None
    #: Drawn as a gloss box on the desktop (a check shown beside the
    #: figures it checks), not as a section.
    gloss: bool = False
    #: A description in the book face after the facts (markdown); "" for
    #: none.
    prose: Callable[[Saga, Neighbour], str] | None = None
    #: The terminal sets its facts three to a line, joined by dots,
    #: rather than one to a line.
    facts_inline: bool = False
    #: Its title worked out from the record (a lord's marriage's terms
    #: named for the couple); None: `title`.
    heading: Callable[[Saga, Neighbour], str] | None = None

    def titled(self, saga: Saga, neighbour: Neighbour) -> str:
        """The block's title for `neighbour`."""
        return self.title if self.heading is None else self.heading(saga, neighbour)


@dataclass(frozen=True)
class KindTab:
    """The tab (a chapter, on the desktop) a kind adds to its neighbours'
    sheets: what is worked out for it, then its lists, with any blocks of
    worked-out text between them."""

    title: str
    tab_id: str
    lists: tuple[KindList, ...]
    #: Shown after the Standing tab rather than before it (a lord's Diary).
    after_standing: bool = False
    blocks: tuple[KindBlock, ...] = ()
    #: The desktop chapter's icon (an artwork concept); "" for the kind's.
    icon: str = ""
    #: What the terminal's details panel says before a row is chosen; ""
    #: for a tab without one (the panel shows a chosen row's `info`).
    panel: str = ""
    #: Whether the tab shows for this neighbour (a place's Tomb, only on
    #: a tomb); None: always.
    shown: Callable[[Neighbour], bool] | None = None

    def shows(self, neighbour: Neighbour) -> bool:
        """Whether the tab is on `neighbour`'s sheet."""
        return self.shown is None or self.shown(neighbour)

    def parts(self) -> list[KindList | KindBlock]:
        """The tab's lists and blocks in the order shown."""
        shown: list[KindList | KindBlock] = [b for b in self.blocks if not b.after]
        for entry in self.lists:
            shown.append(entry)
            shown += [b for b in self.blocks if b.after == entry.section_id]
        return shown


def tab_ops(saga: Saga, neighbour: Neighbour, tab: KindTab) -> dict[str, SectionOps]:
    """The operations of a tab's lists and its blocks with an Edit, by
    section."""
    return {
        **{entry.section_id: entry.ops(saga, neighbour) for entry in tab.lists},
        **{
            block.section_id: block_ops(saga, neighbour, block)
            for block in tab.blocks
            if block.edit is not None
        },
    }


def block_ops(saga: Saga, neighbour: Neighbour, block: KindBlock) -> SectionOps:
    """A block's one Edit, as its section's operations."""
    edit = block.edit
    if edit is None:
        return SectionOps()
    return SectionOps(edit=lambda _row: edit(saga, neighbour))


def list_ops[E: Mapping[str, object]](
    saga: Saga,
    neighbour: Neighbour,
    name: str,
    noun: str,
    fields: Callable[[Saga, Neighbour, E | None], list[DialogField]],
    describe: Callable[[E], str],
    validate: Callable[[dict[str, Any]], str | None] | None = None,
    after: Callable[[], None] = lambda: None,
) -> SectionOps:
    """Add, Edit and Delete on the list `name`: a form of `fields` titled
    "Add a `noun`" (or an), and a confirmation naming `describe(entry)`; `after`
    runs once each has changed the list. `E` is the list's own type of
    entry (a TypedDict); the form's values are written into it as they
    are."""

    article = "an" if noun[:1] in "AEIOU" else "a"

    def entries() -> list[E]:
        return cast(list[E], details_list(neighbour, name))

    def form(entry: E | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            if entry is None:
                entries().append(cast(E, dict(values)))
            else:
                cast(Entry, entry).update(values)
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
