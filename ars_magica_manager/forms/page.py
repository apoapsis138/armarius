"""The page on show as the core's actions ask about it (actions.ActionFacts):
the saga, what kind of page and whose (a where.Where), the section asked
about, and what only the front-end knows (where focus is, who may act, the
chosen rows, where a download goes). Built with page_at.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .. import giving, seat, transfer, viewing
from ..actions import NodeKind
from ..models import (
    Character,
    Covenant,
    Creature,
    Familiar,
    Laboratory,
    Neighbour,
    Saga,
    Tribunal,
)
from ..where import Where

#: The record a page shows, as deletion and actions take it.
Record = Covenant | Character | Laboratory | Familiar | Tribunal | Neighbour | Creature


#: Sends a file straight to the reader (a file name, its bytes and media
#: type): a browser copy of the terminal downloads it instead of writing
#: it to a folder on the host.
Deliver = Callable[[str, bytes, str], None]


#: The covenant's Income list, whose chosen source Improve Income acts on.
INCOME_SECTION = "section-eco-income"


@dataclass(frozen=True)
class Page:
    """The page on show, as actions.available asks about it
    (actions.ActionFacts): the saga, what kind of page, whose, and the
    section a command is being asked about (None: the page itself)."""

    saga: Saga
    kind: NodeKind | None
    covenant: Covenant | None = None
    character: Character | None = None
    laboratory: Laboratory | None = None
    familiar: Familiar | None = None
    tribunal: Tribunal | None = None
    neighbour: Neighbour | None = None
    creature: Creature | None = None
    section: str | None = None
    #: The book chosen in the Library or Lab Texts list on show, if any.
    chosen_book: str | None = None
    #: The row chosen in `section`'s list, when the front-end knows it (the
    #: terminal does; the desktop's row buttons act on their own row).
    row: int | None = None
    #: Where an export goes instead of a file, when the front-end has one.
    deliver: Deliver | None = None
    # -- what only the front-end knows (the terminal's; the desktop sets
    # each action out where it applies) --
    #: Focus is on the record itself (its tree node or top panel), not on
    #: one of its sections.
    on_the_record: bool = True
    #: Whether whoever is reading may run an action here, when the
    #: front-end knows better than the seat (the terminal's signed-in
    #: player, a Steward planning seasons).
    may: Callable[[str], bool] | None = None
    #: What More's Give would give: the chosen row's gift.
    gift: Callable[[], giving.Gift | None] | None = None
    #: Whether a device action can act on the chosen device row.
    device_actions: Callable[[str], bool] | None = None
    #: False where there is nowhere to send a file (over SSH).
    sends_files: bool = True
    #: The chosen row of any section's list, when the front-end knows it.
    rows: Callable[[str], int | None] | None = None

    # -- actions.ActionFacts --

    @property
    def selected_kind(self) -> NodeKind | None:
        return self.kind

    @property
    def selected_covenant(self) -> Covenant | None:
        return self.covenant

    @property
    def selected_character(self) -> Character | None:
        return self.character

    @property
    def selected_laboratory(self) -> Laboratory | None:
        return self.laboratory

    def active_section(self) -> str | None:
        return self.section

    def player_may(self, action: str) -> bool:
        if self.may is not None:
            return self.may(action)
        # The storyguide's own window anything; a player seated here
        # (seat.py) what they may do to the record on show.
        return seat.may_act(
            self.saga, viewing.current().player, action, self.record_to_delete()
        )

    def on_record(self) -> bool:
        return self.on_the_record

    def creation_record(self) -> Character | Covenant | Laboratory | None:
        if self.kind == NodeKind.CHARACTER:
            return self.character
        if self.kind == NodeKind.COVENANT:
            return self.covenant
        if self.kind == NodeKind.LABORATORY:
            return self.laboratory
        return None

    def device_action_enabled(self, action: str) -> bool:
        return self.device_actions(action) if self.device_actions else False

    def to_give(self) -> giving.Gift | None:
        # The desktop gives from each row's own Give.
        return self.gift() if self.gift is not None else None

    def record_to_export(self) -> transfer.Record | None:
        return self.creation_record()

    def record_to_delete(self) -> Record | None:
        if self.kind == NodeKind.FAMILIAR:
            return self.familiar
        if self.kind == NodeKind.TRIBUNAL:
            return self.tribunal
        if self.kind == NodeKind.NEIGHBOUR:
            return self.neighbour
        if self.kind == NodeKind.CREATURE:
            return self.creature
        return self.creation_record()

    def can_send_files(self) -> bool:
        return self.sends_files

    def chosen_row(self, section: str) -> int | None:
        if self.rows is not None:
            return self.rows(section)
        # The desktop's row buttons act on their own list's chosen row.
        return self.row if section == self.section else None


def page_at(saga: Saga, where: Where, **extras: Any) -> Page:
    """The Page for `where`: a character's or laboratory's covenant comes
    with it, and a familiar's magus (Where.covenant, Where.character).
    `extras` are the front-end's own: the section and row, the chosen
    book, where a download goes."""
    return Page(
        saga,
        where.kind,
        covenant=where.covenant(saga),
        character=where.character(saga),
        laboratory=where.laboratory(saga),
        familiar=where.familiar(saga),
        tribunal=where.tribunal(saga),
        neighbour=where.neighbour(saga),
        creature=where.creature(saga),
        **extras,
    )


def page_for(
    saga: Saga,
    kind: NodeKind | None,
    *,
    covenant_id: str | None = None,
    character_id: str | None = None,
    laboratory_id: str | None = None,
    familiar_id: str | None = None,
    tribunal_id: str | None = None,
    neighbour_id: str | None = None,
    creature_id: str | None = None,
) -> Page:
    """page_at the page of `kind` whose id is given."""
    if kind is None:
        return Page(saga, None)
    record_id = (
        character_id
        or laboratory_id
        or familiar_id
        or tribunal_id
        or neighbour_id
        or creature_id
        or covenant_id
    )
    return page_at(saga, Where(kind, record_id))
