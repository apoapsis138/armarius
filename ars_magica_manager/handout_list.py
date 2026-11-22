"""Each Player's Handouts: what every Show left with them, across
Sessions, newest first.

A Show is a Handout for each Player it was shown to: those chosen, or,
for the Table, every Player at that Session (chronicle.at_session).
Showing the same record or picture again adds a dated copy under the same
Handout. A withdrawn Show is on no list.

The list is worked out from the Shows the Chronicles keep (shows.py's
`every_show`), not kept in the saga: the Chronicle is the one record of
what was shown, written by whichever copy made the Show (the host's
window, or its listener for a seat), so the list can't drift from it and
Withdraw takes a Handout off with no step of its own.

Pattern: Protection Proxy. `readable` decides whose list a reader may
read: their own, or any Player's for the storyguide."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from . import chronicle, sessions, shapes, shows, viewing
from .models import Saga, Session

#: What a Handout holds: a copy of a record, or a picture.
RECORD, PICTURE = "record", "picture"


@dataclass(frozen=True)
class Copy:
    """One Show of a Handout: its copy (by the Show's id), the title it
    was given, when, at which Session, and the entry's number there."""

    show_id: str
    title: str
    time: str
    session_id: str
    number: int
    picture: str = ""
    #: The Story chapter it was shown under, by name ("": none).
    story: str = ""
    #: Its Session as the list names it, by its place among the saga's
    #: (session_label): a seat holds only tonight's Session to ask.
    session: str = ""


@dataclass
class Kept:
    """A Handout in a Player's list: what was shown (a record's
    kind:id, or a picture's folder/name), its kind, and each copy, newest
    first. Its title is the newest copy's."""

    key: str
    kind: str
    copies: list[Copy] = field(default_factory=list)

    @property
    def title(self) -> str:
        return self.copies[0].title if self.copies else ""

    @property
    def newest(self) -> tuple[str, int]:
        """When its newest copy was shown, the entry's number breaking a
        tie within the same second."""
        return _when(self.copies[0]) if self.copies else ("", 0)


def _when(copy: Copy) -> tuple[str, int]:
    return copy.time, copy.number


def _key(entry: chronicle.Entry) -> tuple[str, str]:
    """What a Show showed, as a key and its kind: a record by kind and id,
    else the saga picture it copied (by folder and name; a Show made
    before it was kept, by its copy's own name)."""
    ref = entry.body.get("ref")
    if isinstance(ref, list) and len(ref) >= 2:
        return f"{ref[0]}:{ref[1]}", RECORD
    source = entry.body.get("source")
    if isinstance(source, list) and len(source) == 2:
        return f"picture:{source[0]}/{source[1]}", PICTURE
    return f"picture:{entry.body.get('picture', '')}", PICTURE


def _shown_to(saga: Saga, session: Session, entry: chronicle.Entry, who: str) -> bool:
    """Whether Show `entry` was for Player `who`: chosen, or at the
    Session for a Show to the Table."""
    if entry.audience.to == chronicle.TABLE:
        return who in chronicle.at_session(saga, session)
    return entry.audience.to == chronicle.CHOSEN and who in entry.audience.players


def session_label(saga: Saga, session: Session) -> str:
    """How a Handout's list names `session`: its place among the saga's
    Sessions and its title, so two on one day, or both undated, differ."""
    place = next((i for i, s in enumerate(saga.sessions) if s is session), -1)
    return f"{place + 1}. {sessions.title(session)}"


#: The words of each copy, by saga and Show id, read once: a copy is never
#: changed once made.
_WORDS: dict[tuple[str, str], str] = {}


def _words(saga_id: str, show_id: str) -> str:
    """Show `show_id`'s copy's words, lower-cased ("" for a picture, or a
    copy that can't be read)."""
    found = _WORDS.get((saga_id, show_id))
    if found is None:
        try:
            found = shows.from_copy(shows.read_copy(saga_id, show_id)).text.lower()
        except ValueError:
            found = ""
        _WORDS[saga_id, show_id] = found
    return found


def matching(saga: Saga, who: str, words: str) -> set[str]:
    """The keys of Player `who`'s Handouts whose copies hold every one of
    `words` (a search over what was shown; titles are searched where the
    list is drawn). Each copy is read once and kept."""
    wanted = words.lower().split()
    if not wanted:
        return set()
    return {
        kept.key
        for kept in of_player(saga, who)
        if any(
            all(w in _words(saga.id, c.show_id) for w in wanted) for c in kept.copies
        )
    }


def of_player(saga: Saga, who: str) -> list[Kept]:
    """Player `who`'s Handouts, newest first. Only the Chronicles are read,
    never a copy's file."""
    found: dict[str, Kept] = {}
    for session, entry, gone in shows.every_show(saga):
        if gone or not _shown_to(saga, session, entry, who):
            continue
        key, kind = _key(entry)
        kept = found.setdefault(key, Kept(key, kind))
        kept.copies.append(
            Copy(
                str(entry.body.get("show", "")),
                str(entry.body.get("title", "")),
                entry.time,
                session.id,
                entry.number,
                str(entry.body.get("picture", "")),
                str(entry.body.get("story", "")),
                session_label(saga, session),
            )
        )
    for kept in found.values():
        kept.copies.sort(key=_when, reverse=True)
    return sorted(found.values(), key=lambda k: k.newest, reverse=True)


#: Why a reader is refused another Player's Handouts.
NOT_YOURS = "Those Handouts aren't yours to read."
#: The most a list may be when sent to a seat.
LIST_CAP = 2 * 1024 * 1024


def to_data(found: list[Kept]) -> list[dict[str, Any]]:
    """A list as plain data, to send a seat."""
    return [asdict(kept) for kept in found]


def from_data(data: object) -> list[Kept]:
    """A list sent by the host, its shape checked (shapes.build);
    ValueError naming the field for the wrong shape."""
    if not isinstance(data, list):
        raise ValueError("The Handouts sent should be a list.")
    return [shapes.build(Kept, item) for item in data]


def open_copy(saga: Saga, copy: Copy, reader: str) -> shows.Shown | str:
    """A Handout's copy, read from the host's own folder, while `reader`
    sees its Show and it isn't withdrawn (shows.seen); else why not."""
    entry = shows.seen(saga, copy.show_id, reader)
    if entry is None:
        return shows.WITHDRAWN_NOTE
    try:
        return shows.opened(saga.id, entry)
    except ValueError as problem:
        return str(problem)


def readable(saga: Saga, player_id: str, reader: str) -> bool:
    """Whether `reader` may read Player `player_id`'s Handouts: their own,
    or any Player's for a storyguide (viewing)."""
    if reader == player_id:
        return True
    return chronicle.viewer_of(saga, reader).is_storyguide or (reader == viewing.HOST)
