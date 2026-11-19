"""What a More action changes, so a front-end that runs its first step
(menu.command) knows what to save and redraw afterwards.

An action with an entry here needs no handler of its own in the terminal:
it builds the page's `page.Page`, runs the action's first step, then saves
and redraws the sections named. Where an action is offered is not where its
result lands (Cast a Power is offered on Aging & Warping and also writes the
Diary), so these are data of their own. An action with no entry is run by a
handler the front-end writes.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import NamedTuple

from ..models import Saga
from ..sections import (
    NEIGHBOUR_INFO_SECTION,
)

#: The top panels whose title marks a record known to the players or
#: hidden, or names its storyguide.
INFO_SECTIONS = (
    NEIGHBOUR_INFO_SECTION,
    "section-cr-info",
    "section-cov-info",
    "section-char-info",
)


class Refresh(NamedTuple):
    """The sections to redraw once the action's steps are answered."""

    sections: tuple[str, ...] = ()
    #: The change can rename or add records in the navigation tree.
    tree: bool = False
    #: False for a calculator, which changes nothing and so saves nothing.
    saves: bool = True
    #: The sheet is built again afterwards: the change adds or removes
    #: tabs (a tradition's, a sketch's).
    reshow: bool = False
    #: The change can reach anything on the page (an import, a file read
    #: over the record): all of it, and its book and spell lists, drawn again.
    whole_page: bool = False
    #: The saga's date or details changed: its clock, the seasons and
    #: everything that shows them drawn again.
    date: bool = False
    #: The kind of record the action makes (a saga_index kind, such as
    #: "covenants"): its page is opened afterwards, at its Creation
    #: Worksheet while it is In Creation.
    made: str | None = None


def changes(
    *sections: str,
    tree: bool = False,
    reshow: bool = False,
    whole_page: bool = False,
    date: bool = False,
) -> Refresh:
    return Refresh(sections, tree, reshow=reshow, whole_page=whole_page, date=date)


def makes(kind: str) -> Refresh:
    """A New action: the tree gains the record, and its page is opened."""
    return Refresh(tree=True, made=kind)


def calculator() -> Refresh:
    return Refresh(saves=False)


#: Where each kind of record a New action makes is listed.
_LISTED: dict[str, Callable[[Saga], list[str]]] = {
    "covenants": lambda saga: [c.id for c in saga.covenants],
    "tribunals": lambda saga: [t.id for t in saga.tribunals],
    "neighbours": lambda saga: [n.id for n in saga.neighbours],
    "creatures": lambda saga: [c.id for c in saga.creatures],
    "characters": lambda saga: [c.id for c in saga.characters],
    "laboratories": lambda saga: [lab.id for lab in saga.laboratories],
    "familiars": lambda saga: [f.id for f in saga.familiars],
}


def listed(saga: Saga, kind: str) -> list[str]:
    """The ids of the saga's records of `kind`, in order."""
    return _LISTED[kind](saga)


def made_since(saga: Saga, kind: str, before: set[str]) -> str | None:
    """The record of `kind` made since `before` was listed (the last, if
    several were), or None."""
    fresh = [i for i in listed(saga, kind) if i not in before]
    return fresh[-1] if fresh else None


def told(end: object) -> list[str]:
    """What a finished action has to say: its notes, or an outcome's
    message (Undo Last Season's)."""
    if isinstance(end, list):
        return [str(line) for line in end]
    message = getattr(end, "message", None)
    return [message] if isinstance(message, str) and message else []
