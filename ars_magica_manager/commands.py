"""What a sheet's Add, Edit and Delete buttons do, independent of how
they are drawn.

A command is one step the user answers: a form to fill (`Form`), a list
to choose from (`Choose`), a question to confirm (`Confirm`) or a file to
read (`ChooseFile`); an `Act` asks nothing and runs at once. Answering
it runs its `apply`, which changes the saga and returns the next step: a
further command (choose an Ability, then fill in its score), the notes to
show the user, None when there is nothing more, a `Then`: the steps so
far kept and saved, and another begun, or a `Go`: another record's page
to open. A form field's chooser
runs the same steps and ends with a `Picked` value instead. A `Refuse`, as the
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
from pathlib import Path
from typing import Any

from .form_spec import DialogField
from .markup import escape


@dataclass(frozen=True)
class FormCard:
    """A form's check field drawn as a card: `key` is the field's ("" for a
    choice that can't be changed, which `fixed` then names), `summary` and
    `count` its lines, `detail` (markup) what its inspector shows. A card
    that isn't `usable` is faded and can't be switched, and keeps its value."""

    key: str
    title: str
    summary: str
    count: str
    detail: str
    usable: bool = True
    fixed: str = ""


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
    #: The button that leaves without saving (Close for a calculator).
    cancel_label: str = "Cancel"
    #: A picture drawn beside the live line from the values, by each
    #: front-end its own way: an arms.Arms (or None for none).
    picture: Callable[[dict[str, Any]], Any] | None = None
    #: The form's own help page (help/*.md), if it has one.
    help_id: str = ""
    #: When set, the live text is an inspector: a framed panel at the
    #: form's foot under this heading, saying what the choices so far will
    #: do, rather than a bare line.
    inspector: str = ""
    #: When set, a front-end with the room draws the form's check fields
    #: as these cards beside an inspector, under the line `cards_lead`; the
    #: values it gives `apply` are the fields' all the same.
    cards: Callable[[], list[FormCard]] | None = None
    cards_lead: str = ""


@dataclass(frozen=True)
class Choice:
    """One entry of a `Choose`: what it shows (markup), the value chosen,
    its details (markup, shown beside the list) and extra words a search
    matches besides the label."""

    label: str
    value: Any
    detail: str = ""
    search: str = ""
    #: The entry's value for each of its Choose's `filters`, as (filter,
    #: value) pairs: ("Type", "Study").
    facets: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Choose:
    """A list to choose one entry from, searchable; `apply` gets the
    chosen entry's value. `others` are the entries not offered (from a
    book not in play, or ones the rules say this record can't take),
    listed too only when the user asks to see everything, each marked
    with why (`not_offered`)."""

    title: str
    choices: Callable[[], list[Choice]]
    apply: Callable[[Any], Any]
    empty: str = "Nothing to choose from."
    others: Callable[[], list[Choice]] | None = None
    #: The list's own help page (help/*.md), if it has one.
    help_id: str = ""
    #: The filters offered above the list, in order, each narrowing it to
    #: the entries with the value chosen (Choice.facets); with any, the
    #: list is headed by each entry's value of the first.
    filters: tuple[str, ...] = ()
    #: Entries listed first, under RECENT, while no filter is chosen and
    #: nothing is typed (repeats of entries further down).
    recent: Callable[[], list[Choice]] | None = None


#: The heading a Choose's recent entries are listed under.
RECENT = "Recent"


def facet(choice: Choice, name: str) -> str:
    """`choice`'s value for the filter `name` ("" for none)."""
    return next((value for key, value in choice.facets if key == name), "")


def filter_values(choices: Sequence[Choice], name: str) -> list[str]:
    """The values the filter `name` offers: each one some entry has, in
    the order the entries first have them."""
    return list(dict.fromkeys(v for c in choices if (v := facet(c, name))))


def passes(choice: Choice, chosen: dict[str, str | None]) -> bool:
    """Whether `choice` has every filter value `chosen` (filter -> value;
    None: any). Each filter is a test an entry passes or not, and the list
    shows those passing them all (Specification, reduced to a dict of
    wanted values)."""
    return all(
        value is None or facet(choice, name) == value for name, value in chosen.items()
    )


def heading(step: Choose, choice: Choice) -> str:
    """The heading `choice` is listed under: its value of the first
    filter ("" for a list without filters)."""
    return facet(choice, step.filters[0]) if step.filters else ""


def not_offered(choice: Choice, why: str) -> Choice:
    """`choice` as Show everything lists it: marked with why it isn't
    offered."""
    return Choice(
        f"{choice.label}  [dim]({escape(why)})[/]",
        choice.value,
        f"[$text-warning]Not offered: {escape(why)}[/]\n{choice.detail}",
        f"{choice.search} {why}",
        choice.facets,
    )


@dataclass(frozen=True)
class Confirm:
    """A yes-or-no question (markup); `apply` runs on Yes. `title` heads
    it where a front-end titles its questions ("" for its own)."""

    question: str
    apply: Callable[[], Any]
    yes_label: str = "Delete"
    title: str = ""


@dataclass(frozen=True)
class Refuse:
    """Why a button can't act here (markup), shown with nothing changed
    and nothing saved: "X is held by Y: remove it there first"."""

    title: str
    why: str


@dataclass(frozen=True)
class Act:
    """A step with nothing to ask: `apply` runs at once (a button that
    just does its work, such as adding the Virtues a magus must have).
    `title` heads the notes it ends with, where a front-end titles them."""

    apply: Callable[[], Any]
    title: str = ""


@dataclass(frozen=True)
class ChooseFile:
    """A file to read, chosen the front-end's own way (the terminal's list
    of files, the desktop's Open window): `suffix` the kind of file
    (".csv"), opening on the folder `start`; `apply` gets the chosen
    file's path. With `save`, a file to write instead (the desktop's Save
    window), `start` naming the file it suggests."""

    title: str
    suffix: str
    start: Path
    apply: Callable[[Path], Any]
    #: Other kinds of file it takes too (".jpg" beside ".png", ".zip"
    #: beside ".json" for an export that carries its pictures).
    more: tuple[str, ...] = ()
    save: bool = False

    @property
    def suffixes(self) -> tuple[str, ...]:
        return (self.suffix, *self.more)


@dataclass(frozen=True)
class Picked:
    """What a form field's chooser (form_spec.DialogField.choose) ends
    with: the field's new value. Nothing in the saga changes."""

    value: Any


@dataclass(frozen=True)
class Go:
    """What a step ends with when it opens another record: the front-end
    shows the page of `ref` (a references.Ref). Nothing in the saga
    changes, so nothing is saved."""

    ref: Any


@dataclass(frozen=True)
class Then:
    """What a step ends with when another should follow once this one is
    kept: the front-end saves the saga and redraws the page as if the
    steps had ended, then shows `step` (holding a Tribunal's step opens
    the next). Cancelling `step` leaves what was kept."""

    step: Any


Command = Form | Choose | Confirm | Act | Refuse | ChooseFile


def picked(form: Callable[[dict[str, Any]], Any]) -> Callable[[dict[str, Any]], Picked]:
    """A Form's apply that hands back what `form` builds from the values
    as the chosen value."""
    return lambda values: Picked(form(values))


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
