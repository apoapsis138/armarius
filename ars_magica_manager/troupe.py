"""The Troupe: the saga's player characters and the covenants the troupe
plays, and the records the reader has bookmarked, for the desktop's The
Troupe chapter.

Bookmarks belong to whoever reads the saga, not to the saga itself. With
no sign-in on the desktop yet, they are kept in this computer's settings,
filed by saga; `bookmarks` and `save_bookmarks` are the only two
functions that know where, so keeping them for each signed-in Player
later changes only those two.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import settings, viewing, world
from .models import Character, Covenant, Saga
from .seasons.defaults import is_player_character

#: The settings key the bookmarks are kept under:
#: {saga id: [[kind, id], ...]}.
BOOKMARKS = "bookmarks"

#: What can be bookmarked, in the order the Bookmarked cards are grouped,
#: with each group's title.
KIND_TITLES: dict[str, str] = {
    "character": "Characters",
    "covenant": "Covenants",
    "laboratory": "Laboratories",
    "familiar": "Familiars",
    "tribunal": "Tribunals",
    "neighbour": "Neighbours",
    "creature": "Creatures",
}


@dataclass(frozen=True)
class Bookmark:
    """A bookmarked record: what kind it is (a KIND_TITLES key) and its id."""

    kind: str
    id: str


def bookmarks(saga_id: str) -> list[Bookmark]:
    """The records bookmarked in the saga, in the order they were
    bookmarked; an entry the settings can't read as one is left out."""
    filed = settings.load_settings().get(BOOKMARKS)
    entries = filed.get(saga_id, []) if isinstance(filed, dict) else []
    return [
        Bookmark(entry[0], entry[1])
        for entry in entries
        if isinstance(entry, list)
        and len(entry) == 2
        and entry[0] in KIND_TITLES
        and isinstance(entry[1], str)
    ]


def save_bookmarks(saga_id: str, marks: list[Bookmark]) -> None:
    """Keep `marks` as the saga's, leaving every other saga's as it was."""
    filed = settings.load_settings().get(BOOKMARKS)
    filed = dict(filed) if isinstance(filed, dict) else {}
    if marks:
        filed[saga_id] = [[mark.kind, mark.id] for mark in marks]
    else:
        filed.pop(saga_id, None)
    settings.update_settings(**{BOOKMARKS: filed})


def is_bookmarked(saga_id: str, kind: str, record_id: str) -> bool:
    return Bookmark(kind, record_id) in bookmarks(saga_id)


def set_bookmarked(saga_id: str, kind: str, record_id: str, on: bool) -> None:
    """Bookmark the record, or take its bookmark out."""
    mark = Bookmark(kind, record_id)
    marks = [m for m in bookmarks(saga_id) if m != mark]
    save_bookmarks(saga_id, [*marks, mark] if on else marks)


def player_characters(
    saga: Saga, apart: frozenset[str] | set[str] = frozenset()
) -> list[tuple[Covenant | None, list[Character]]]:
    """The characters a Player plays, by covenant: the troupe's covenants
    first, then the others, then those who belong to none (None). `apart`
    names (by id) characters left out, shown elsewhere."""
    played = [
        c for c in saga.characters if is_player_character(c) and c.id not in apart
    ]
    groups: list[tuple[Covenant | None, list[Character]]] = []
    for covenant in world.troupe_first(saga.covenants):
        members = [c for c in played if c.covenant_id == covenant.id]
        if members:
            groups.append((covenant, members))
    known = {c.id for c in saga.covenants}
    loose = [c for c in played if c.covenant_id not in known]
    if loose:
        groups.append((None, loose))
    return groups


def troupe_covenants(saga: Saga) -> list[Covenant]:
    """The covenants the troupe plays."""
    return [c for c in saga.covenants if c.played]


def record(saga: Saga, mark: Bookmark) -> object | None:
    """The record `mark` names, or None once it is gone from the saga."""
    if mark.kind == "familiar":
        return next((f for f in saga.familiars if f.id == mark.id), None)
    return getattr(saga, mark.kind)(mark.id)


def other_bookmarks(saga: Saga) -> list[tuple[str, list[object]]]:
    """The bookmarked records The Troupe doesn't already show (a player
    character or a troupe covenant), by kind in KIND_TITLES's order, each
    group in the order it was bookmarked; a record no longer in the saga
    is left out."""
    shown = {Bookmark("covenant", c.id) for c in troupe_covenants(saga)} | {
        Bookmark("character", c.id)
        for _, members in player_characters(saga)
        for c in members
    }
    marks = [m for m in bookmarks(saga.id) if m not in shown]
    groups = []
    for kind in KIND_TITLES:
        records = [record(saga, m) for m in marks if m.kind == kind]
        found = [r for r in records if r is not None and viewing.reads(r)]
        if found:
            groups.append((kind, found))
    return groups
