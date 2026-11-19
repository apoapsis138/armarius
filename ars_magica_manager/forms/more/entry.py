"""One More or New action, everything about it in one record: the registry
(forms/more) holds one per action, and the menus, the pages and
`available` ask it."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ...actions import ActionFacts, MenuItem, NodeKind
from ...commands import Command
from ..menu_refresh import Refresh
from ..page import Page


@dataclass(frozen=True)
class MoreAction:
    """A More (or New) action: its key, the letter and label its menu shows,
    its first step and what it changes, where it shows and when it is
    offered."""

    key: str
    letter: str
    label: str
    #: Its first step on a page (commands.py). None: each front-end draws
    #: and runs it itself (a row's own button, a list of its own).
    step: Callable[[Page], Command] | None = None
    #: What it changes, for a front-end to save and redraw afterwards.
    refresh: Refresh | None = None
    #: "more", or "new" for an action that makes a record.
    menu: str = "more"
    #: The one section it is offered in, if only one.
    section: str | None = None
    #: False: no page offers it in its More; it is drawn as a section's or
    #: row's own button instead.
    on_page: bool = True
    #: Where a page sets it out itself: each (kind of page, chapter or
    #: section title). None: wherever its section is shown; () nowhere
    #: but More (Restore: each list's own button).
    places: tuple[tuple[NodeKind, str], ...] | None = None
    #: When it is offered, by the record on show (asked first).
    on_record: Callable[[ActionFacts], bool] | None = None
    #: When it is offered, by the section focus is in.
    in_section: Callable[[ActionFacts, str], bool] | None = None

    @property
    def item(self) -> MenuItem:
        """Its line in the menu."""
        return MenuItem(self.letter, self.key, self.label)

    def offered(self, facts: ActionFacts) -> bool:
        """Its own rule: the record on show, else the section focus is in
        (its one section, if it names one), else anywhere."""
        if self.on_record is not None:
            return self.on_record(facts)
        section = facts.active_section() or ""
        if self.in_section is not None:
            return self.in_section(facts, section)
        if self.section is not None:
            return section == self.section
        return True
