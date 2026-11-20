"""Where the reader is: the page on show, as a kind and an id.

Both front-ends ask "which record is on show?" (to delete it, export it,
name it, offer its actions, tell who else has it open). A Where answers
from the saga each time, so it outlives a reload of the saga and can say
when its record has gone (deleted, here or by another player).
"""

from __future__ import annotations

from dataclasses import dataclass

from . import familiars as fam
from . import sessions, stores
from .actions import NodeKind
from .models import (
    Character,
    Covenant,
    Creature,
    Familiar,
    Laboratory,
    Neighbour,
    Saga,
    Session,
    Tribunal,
)

Record = Covenant | Character | Laboratory | Familiar | Tribunal | Neighbour | Creature

#: The pages of one record, and how a reference names its kind
#: (references.KINDS, presence.py).
RECORD_KINDS: dict[NodeKind, str] = {
    NodeKind.CHARACTER: "characters",
    NodeKind.COVENANT: "covenants",
    NodeKind.LABORATORY: "laboratories",
    NodeKind.FAMILIAR: "familiars",
    NodeKind.TRIBUNAL: "tribunals",
    NodeKind.NEIGHBOUR: "neighbours",
    NodeKind.CREATURE: "creatures",
    NodeKind.SESSION: "sessions",
}

#: A covenant's lists, the id the covenant's (None: the saga's unassigned).
_GROUPS: dict[NodeKind, str] = {
    NodeKind.CHARACTER_GROUP: "Characters",
    NodeKind.LABORATORY_GROUP: "Laboratories",
}

#: The pages of the whole saga, and what they are called (the saga's own
#: page by the saga's name).
_SAGA_PAGES: dict[NodeKind, str] = {
    NodeKind.SAGA: "",
    NodeKind.SAGA_CONTENT: "Saga Content",
    NodeKind.SEASONS: "Seasons",
    NodeKind.ARMARIUM: stores.STORES[stores.ARMARIUM].title,
    NodeKind.CUSTODIA: stores.STORES[stores.CUSTODIA].title,
    NodeKind.REGION: "The Region",
    NodeKind.NEIGHBOUR_GROUP: "The Region",
    NodeKind.BESTIARY: "The Bestiary",
    NodeKind.CONFLICTS: "Conflicts",
}

_KIND_OF: dict[type, NodeKind] = {
    Character: NodeKind.CHARACTER,
    Covenant: NodeKind.COVENANT,
    Laboratory: NodeKind.LABORATORY,
    Familiar: NodeKind.FAMILIAR,
    Tribunal: NodeKind.TRIBUNAL,
    Neighbour: NodeKind.NEIGHBOUR,
    Creature: NodeKind.CREATURE,
    Session: NodeKind.SESSION,
}


@dataclass(frozen=True)
class Where:
    """A page: what kind, and whose. `id` is the record's for a record's
    page, the covenant's for a covenant's lists, and None for a page of the
    whole saga."""

    kind: NodeKind = NodeKind.SAGA
    id: str | None = None

    @classmethod
    def of(cls, record: Record | Session) -> Where:
        """The page of `record`."""
        return cls(_KIND_OF[type(record)], record.id)

    # -- the record --

    @property
    def shows_record(self) -> bool:
        """A page of one record (not a list, nor the whole saga)."""
        return self.kind in RECORD_KINDS

    @property
    def whole_saga(self) -> bool:
        """A page of the whole saga: its own, the Region, the stores..."""
        return self.kind in _SAGA_PAGES

    def record(self, saga: Saga) -> Record | None:
        """The record on show, if this is a record's page and it is still
        in the saga."""
        if not self.shows_record or self.id is None:
            return None
        if self.kind == NodeKind.FAMILIAR:
            return next((f for f in saga.familiars if f.id == self.id), None)
        if self.kind == NodeKind.SESSION:
            return None  # not a named record: Where.session finds it
        find = {
            NodeKind.CHARACTER: saga.character,
            NodeKind.COVENANT: saga.covenant,
            NodeKind.LABORATORY: saga.laboratory,
            NodeKind.TRIBUNAL: saga.tribunal,
            NodeKind.NEIGHBOUR: saga.neighbour,
            NodeKind.CREATURE: saga.creature,
        }[self.kind]
        return find(self.id)

    def gone(self, saga: Saga) -> bool:
        """The page's record is no longer in the saga."""
        if self.kind == NodeKind.SESSION:
            return self.session(saga) is None
        return self.shows_record and self.record(saga) is None

    def presence_key(self) -> str | None:
        """The record on show as presence.py names it ("characters:mag1"),
        or None for a page that isn't one record's."""
        kind = RECORD_KINDS.get(self.kind)
        return f"{kind}:{self.id}" if kind and self.id else None

    def name(self, saga: Saga) -> str:
        """What the page is called: its record's name, or what it lists."""
        if self.kind == NodeKind.SAGA:
            return saga.name
        if self.kind in _SAGA_PAGES:
            return _SAGA_PAGES[self.kind]
        if self.kind in _GROUPS:
            covenant = saga.covenant(self.id)
            where = f" in {covenant.name}" if covenant is not None else ""
            return f"{_GROUPS[self.kind]}{where}"
        if self.kind == NodeKind.SESSION:
            session = self.session(saga)
            return sessions.title(session) if session is not None else ""
        record = self.record(saga)
        if record is None:
            return ""
        return record.name or "(unnamed)"

    def creation_record(self, saga: Saga) -> Character | Covenant | Laboratory | None:
        """The record whose creation mode the page shows: a character's,
        covenant's or laboratory's."""
        record = self.record(saga)
        return record if isinstance(record, Character | Covenant | Laboratory) else None

    # -- the records the page's actions ask about (page.Page) --

    def covenant(self, saga: Saga) -> Covenant | None:
        """The covenant the page belongs to: its own, a list's, or the
        covenant of the character, laboratory or familiar's magus on show."""
        if self.kind in (NodeKind.COVENANT, *_GROUPS):
            return saga.covenant(self.id)
        if self.kind == NodeKind.LABORATORY:
            lab = saga.laboratory(self.id)
            return saga.covenant(lab.covenant_id) if lab is not None else None
        character = self.character(saga)
        return saga.covenant(character.covenant_id) if character is not None else None

    def character(self, saga: Saga) -> Character | None:
        """The character on show, or the magus of the familiar on show."""
        if self.kind == NodeKind.CHARACTER:
            return saga.character(self.id)
        familiar = self.familiar(saga)
        return fam.magus_of(saga, familiar) if familiar is not None else None

    def laboratory(self, saga: Saga) -> Laboratory | None:
        return saga.laboratory(self.id) if self.kind == NodeKind.LABORATORY else None

    def familiar(self, saga: Saga) -> Familiar | None:
        record = self.record(saga) if self.kind == NodeKind.FAMILIAR else None
        return record if isinstance(record, Familiar) else None

    def tribunal(self, saga: Saga) -> Tribunal | None:
        return saga.tribunal(self.id) if self.kind == NodeKind.TRIBUNAL else None

    def neighbour(self, saga: Saga) -> Neighbour | None:
        return saga.neighbour(self.id) if self.kind == NodeKind.NEIGHBOUR else None

    def creature(self, saga: Saga) -> Creature | None:
        return saga.creature(self.id) if self.kind == NodeKind.CREATURE else None

    def session(self, saga: Saga) -> Session | None:
        return sessions.find(saga, self.id) if self.kind == NodeKind.SESSION else None
