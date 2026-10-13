"""What a sheet's Add, Edit and Delete buttons do, independent of how
they are drawn.

A command is one step the user answers: a form to fill (`Form`), a list
to choose from (`Choose`) or a question to confirm (`Confirm`). Answering
it runs its `apply`, which changes the saga and returns the next step: a
further command (choose an Ability, then fill in its score), the notes to
show the user, or None when there is nothing more. A `Refuse`, as the
first step or the next, says why the button can't act, changing nothing. A front-end runs the
steps, then saves the saga and redraws the page.

`SectionOps` holds a section's three verbs, as actions.SECTION_VERBS
names them: `add` builds the first step of adding a row, `edit` and
`remove` the first step of changing or deleting the chosen row (by its
index in the section's list).
"""

from __future__ import annotations

from collections.abc import Callable, MutableSequence, Sequence
from dataclasses import dataclass, field
from typing import Any

from .form_spec import DialogField
from .markup import escape


@dataclass(frozen=True)
class Form:
    """A form of `fields`; `apply` gets its values when it is saved.
    `validate` (the values -> an error, or None) can refuse a save the
    fields alone allow; `live` (the values -> markup) is a line under the
    fields kept up to date as the user types."""

    title: str
    fields: Callable[[], list[DialogField]]
    apply: Callable[[dict[str, Any]], Any]
    validate: Callable[[dict[str, Any]], str | None] | None = None
    live: Callable[[dict[str, Any]], str] | None = None
    save_label: str = "Save"


@dataclass(frozen=True)
class Choice:
    """One entry of a `Choose`: what it shows (markup), the value chosen,
    its details (markup, shown beside the list) and extra words a search
    matches besides the label."""

    label: str
    value: Any
    detail: str = ""
    search: str = ""


@dataclass(frozen=True)
class Choose:
    """A list to choose one entry from, searchable; `apply` gets the
    chosen entry's value."""

    title: str
    choices: Callable[[], list[Choice]]
    apply: Callable[[Any], Any]
    empty: str = "Nothing to choose from."


@dataclass(frozen=True)
class Confirm:
    """A yes-or-no question (markup); `apply` runs on Yes."""

    question: str
    apply: Callable[[], Any]
    yes_label: str = "Delete"


@dataclass(frozen=True)
class Refuse:
    """Why a button can't act here (markup), shown with nothing changed
    and nothing saved: "X is held by Y: remove it there first"."""

    title: str
    why: str


Command = Form | Choose | Confirm | Refuse


@dataclass(frozen=True)
class SectionOps:
    """A section's Add, Edit and Delete: each builds the first step (Edit
    and Delete for the chosen row's index). None: the section hasn't
    that verb."""

    add: Callable[[], Command] | None = None
    edit: Callable[[int], Command] | None = None
    remove: Callable[[int], Command] | None = None
    #: Each row's name, as the section lists them (for the front-end to
    #: say which row Edit and Delete will act on).
    rows: Callable[[], list[str]] = field(default=list)


def delete(entries: MutableSequence[Any], index: int, name: str) -> Confirm:
    """ "Delete <name>?", deleting `entries[index]` on Yes."""

    def apply() -> None:
        del entries[index]

    return Confirm(f"Delete {escape(name)}?", apply)


def notes(*lines: str) -> list[str]:
    """The notes a step returns, leaving out empty lines."""
    return [line for line in lines if line]


def names(entries: Sequence[Any], attribute: str = "name") -> Callable[[], list[str]]:
    """A section's row names: each entry's `attribute`."""
    return lambda: [getattr(entry, attribute) or "(unnamed)" for entry in entries]
