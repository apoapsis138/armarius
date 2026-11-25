"""A Player's Handouts, to read (handout_list.py): a player's own, opened
from the page of any character they play; any Player's for the
storyguide, from that Player's row in Saga Management's Players. Choose a
Handout, then, when it was shown more than once, which copy; its copy
opens as a Show's does.

A player's own list is as they arrange it (handout_arrangement.py):
pinned first, under their own titles, filtered by folder, Session, kind
and Story, searched by title and the copies' words; choosing a Handout
offers Open, Rename, Pin or Unpin and Move to folder. The storyguide reads
another's list as shown, never their arrangement.

Where the list comes from: a Remote seat asks its host (Remote Proxy), the
host's own copy works it out from its Chronicles.

Pattern: Command steps (Choose, then a Form or the copy), with the
Choose's own filters (facets), the same on both front-ends; whose list
and arrangement a reader may read is one rule each (Protection Proxy:
handout_list.readable, handout_arrangement.readable)."""

from __future__ import annotations

from typing import Any, Protocol

from .. import (
    at_table,
    chronicle,
    handout_arrangement,
    handout_list,
    shows,
    virtual_tabletop,
)
from ..commands import Choice, Choose, Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Character, Saga
from . import show as show_forms

TITLE = "Handouts"
HELP_ID = "handouts"


class Reads(Protocol):
    """Where a Player's Handouts are read: the seat's Table, or the
    host's own Chronicles."""

    def handouts(self, player_id: str) -> list[handout_list.Kept] | str: ...

    def open_handout(self, copy: handout_list.Copy) -> shows.Shown | str: ...

    def arrangement(self, player_id: str) -> handout_arrangement.Arrangement | str: ...

    def search_handouts(self, player_id: str, words: str) -> set[str] | str: ...

    def arrange(
        self, player_id: str, call: handout_arrangement.Arrange
    ) -> str | None: ...


class HostReads:
    """The host's own copy: each list worked out from its Chronicles, as
    `who` may read it."""

    def __init__(self, saga: Saga, who: str) -> None:
        self.saga, self.who = saga, who

    def handouts(self, player_id: str) -> list[handout_list.Kept] | str:
        if not handout_list.readable(self.saga, player_id, self.who):
            return handout_list.NOT_YOURS
        return handout_list.of_player(self.saga, player_id)

    def open_handout(self, copy: handout_list.Copy) -> shows.Shown | str:
        return handout_list.open_copy(self.saga, copy, self.who)

    def arrangement(self, player_id: str) -> handout_arrangement.Arrangement | str:
        return handout_arrangement.arrangement_of(self.saga.id, player_id, self.who)

    def search_handouts(self, player_id: str, words: str) -> set[str] | str:
        if not handout_list.readable(self.saga, player_id, self.who):
            return handout_list.NOT_YOURS
        return handout_list.matching(self.saga, player_id, words)

    def arrange(self, player_id: str, call: handout_arrangement.Arrange) -> str | None:
        return handout_arrangement.arrange(self.saga, player_id, call, by=self.who)


def here(saga: Saga) -> Reads:
    """Where whoever uses this copy reads Handouts: through the Remote
    seat while one is attached, else this computer's Chronicles."""
    seat = at_table.seat()
    return seat if seat is not None else HostReads(saga, chronicle.here())


def _date(time: str) -> str:
    return time[:10]


def _open(reads: Reads, copy: handout_list.Copy) -> Command:
    found = reads.open_handout(copy)
    if isinstance(found, str):
        return Refuse(TITLE, escape(found))
    return show_forms.copy_form(found)


def _copies(reads: Reads, kept: handout_list.Kept) -> Command:
    """One Handout: its copy, or, shown more than once, which copy."""
    if len(kept.copies) == 1:
        return _open(reads, kept.copies[0])
    return Choose(
        escape(kept.title),
        lambda: [
            Choice(escape(f"{_date(c.time)}: {c.title}"), index)
            for index, c in enumerate(kept.copies)
        ],
        lambda index: _open(reads, kept.copies[index]),
        help_id=HELP_ID,
    )


#: What a player's own list filters by (Choice.facets).
FILTERS = ("Folder", "Session", "Kind", "Story")
#: What to do with one of the player's own Handouts.
OPEN, RENAME, PIN, MOVE = "open", "rename", "pin", "move"
#: The list's first entry: search the words of the copies, on the host.
SEARCH = "@search"
_KINDS = {
    handout_list.RECORD: "Record",
    handout_list.PICTURE: "Picture",
    handout_list.WRITTEN: "Written",
}


def _label(title: str, kept: handout_list.Kept) -> str:
    shown = len(kept.copies)
    last = _date(kept.copies[0].time)
    return (
        f"{title} (shown {shown} times, last {last})"
        if shown > 1
        else (f"{title} ({last})")
    )


def _facets(shown: handout_arrangement.Arranged) -> tuple[tuple[str, str], ...]:
    """A Handout's filter values. In no folder, its Folder is "": it is
    listed first, under no heading. The Session is the host's name for it
    (a seat holds only tonight's)."""
    newest = shown.kept.copies[0]
    return (
        ("Folder", shown.folder),
        ("Session", newest.session),
        ("Kind", _KINDS.get(shown.kept.kind, "")),
        ("Story", newest.story or "(no story)"),
    )


def _search(kept: handout_list.Kept) -> str:
    """What the list's own search reads: every copy's title (the copies'
    words are searched by the host: Search their words)."""
    return " ".join(c.title for c in kept.copies)


def _current(
    reads: Reads, player_id: str, kept: handout_list.Kept
) -> handout_arrangement.Arranged:
    """`kept` as its player keeps it now, read afresh."""
    found = reads.arrangement(player_id)
    if isinstance(found, str):
        found = handout_arrangement.Arrangement()
    [shown] = handout_arrangement.arranged([kept], found)
    return shown


def arranging(reads: Reads, player_id: str, kept: handout_list.Kept) -> Command:
    """One of the player's own Handouts: open it, or rename, pin or file
    it, each step reading its arrangement afresh."""
    key = kept.key

    def change(call: handout_arrangement.Arrange) -> list[str]:
        refused = reads.arrange(player_id, call)
        return notes(refused) if refused else []

    def renamed(values: dict[str, Any]) -> handout_arrangement.Arrange:
        return handout_arrangement.Arrange(key, title=str(values.get("title") or ""))

    def moved(values: dict[str, Any]) -> handout_arrangement.Arrange:
        folder = str(values.get("new_folder") or "").strip()
        return handout_arrangement.Arrange(
            key, folder=folder or str(values.get("folder") or "")
        )

    def rename() -> Form:
        return Form(
            "Rename the Handout",
            lambda: [
                DialogField(
                    "title",
                    "Title",
                    "text",
                    _current(reads, player_id, kept).title,
                    hint="Yours alone; blank puts back the title it was shown under.",
                )
            ],
            lambda values: change(renamed(values)),
            validate=lambda values: handout_arrangement.why_not_words(renamed(values)),
            help_id=HELP_ID,
        )

    def move() -> Form:
        found = reads.arrangement(player_id)
        folders = (
            found.folders if isinstance(found, handout_arrangement.Arrangement) else []
        )
        return Form(
            "Move to a folder",
            lambda: [
                DialogField(
                    "folder",
                    "Folder",
                    "select",
                    _current(reads, player_id, kept).folder,
                    options=[
                        (handout_arrangement.NO_FOLDER, ""),
                        *((f, f) for f in folders),
                    ],
                ),
                DialogField(
                    "new_folder",
                    "Or a new folder",
                    "text",
                    "",
                    hint="Folders are one level deep; one empties away.",
                ),
            ],
            lambda values: change(moved(values)),
            validate=lambda values: handout_arrangement.why_not_words(moved(values)),
            help_id=HELP_ID,
        )

    def pin() -> list[str]:
        pinned = _current(reads, player_id, kept).pinned
        return change(handout_arrangement.Arrange(key, pinned=not pinned))

    steps = {OPEN: lambda: _copies(reads, kept), RENAME: rename, PIN: pin, MOVE: move}

    def words() -> list[Choice]:
        pinned = _current(reads, player_id, kept).pinned
        said = {
            OPEN: "Open",
            RENAME: "Rename",
            PIN: "Unpin" if pinned else "Pin",
            MOVE: "Move to folder",
        }
        return [Choice(said[step], step) for step in steps]

    return Choose(
        escape(_current(reads, player_id, kept).title),
        words,
        lambda step: steps[step](),
        help_id=HELP_ID,
    )


def _arranged_choices(
    reads: Reads, player_id: str, found: list[handout_list.Kept]
) -> list[Choice]:
    """The player's Handouts as they keep them now, read afresh each time
    the list is drawn, each valued by its key."""
    kept = reads.arrangement(player_id)
    if isinstance(kept, str):
        kept = handout_arrangement.Arrangement()
    return [
        Choice(
            escape(_label(s.title, s.kept)),
            s.kept.key,
            search=_search(s.kept),
            facets=_facets(s),
        )
        for s in handout_arrangement.arranged(found, kept)
    ]


def _searching(reads: Reads, player_id: str, found: list[handout_list.Kept]) -> Form:
    """Search the words of the player's Handouts' copies, on the host; then
    the Handouts that hold them, as the list shows them."""
    by_key = {k.key: k for k in found}

    def results(values: dict[str, Any]) -> Command:
        words = str(values.get("words") or "").strip()
        keys = reads.search_handouts(player_id, words)
        if isinstance(keys, str):
            return Refuse(TITLE, escape(keys))
        wanted = words.lower().split()
        titled = {k.key for k in found if all(w in _search(k).lower() for w in wanted)}
        hits = [k for k in found if k.key in keys | titled]
        return Choose(
            f"{TITLE} holding {escape(words)}",
            lambda: _arranged_choices(reads, player_id, hits),
            lambda key: arranging(reads, player_id, by_key[key]),
            empty="None of your Handouts holds those words.",
            help_id=HELP_ID,
            filters=FILTERS,
        )

    return Form(
        "Search their words",
        lambda: [
            DialogField(
                "words",
                "Words",
                "text",
                "",
                hint="Each word must be in a Handout's title or its copy's text.",
            )
        ],
        results,
        save_label="Search",
        help_id=HELP_ID,
    )


def handouts(reads: Reads, saga: Saga, player_id: str, whose: str = "") -> Command:
    """Player `player_id`'s Handouts, read through `reads`; `whose` names
    them in the title (none: the reader's own, which they arrange: pinned
    first, under their titles, filtered by folder, Session, kind and Story,
    searched by title and text). Another's read newest first, as shown."""
    found = reads.handouts(player_id)
    if isinstance(found, str):
        return Refuse(TITLE, escape(found))
    if whose:
        return Choose(
            f"{escape(whose)}'s {TITLE}",
            lambda: [
                Choice(escape(_label(k.title, k)), index)
                for index, k in enumerate(found)
            ],
            lambda index: _copies(reads, found[index]),
            empty="Nothing has been shown to them yet.",
            help_id=HELP_ID,
        )
    del saga
    kept = reads.arrangement(player_id)
    if isinstance(kept, str):
        return Refuse(TITLE, escape(kept))
    by_key = {k.key: k for k in found}

    def chosen(value: str) -> Command:
        if value == SEARCH:
            return _searching(reads, player_id, found)
        return arranging(reads, player_id, by_key[value])

    return Choose(
        TITLE,
        lambda: (
            [
                Choice("Search their words...", SEARCH),
                *_arranged_choices(reads, player_id, found),
            ]
            if found
            else []
        ),
        chosen,
        empty="Nothing has been shown to you yet.",
        help_id=HELP_ID,
        filters=FILTERS,
    )


def plays(character: Character, who: str) -> bool:
    """Whether `who` plays `character` (a shared one: any Player)."""
    b = character.background
    return bool(who) and (who in b.player_ids or b.everyone_plays)


def offered_on(saga: Saga, record: Any) -> bool:
    """Handouts, on the page of a character whoever uses this copy plays,
    while the Virtual Tabletop (Preview) is on."""
    del saga
    return (
        virtual_tabletop.on()
        and isinstance(record, Character)
        and plays(record, chronicle.here())
    )


def mine(saga: Saga, record: Any) -> Command:
    """The Handouts of whoever uses this copy, opened from the page of a
    character they play."""
    if not offered_on(saga, record):
        return Refuse(TITLE, "Handouts are opened from a character you play.")
    return handouts(here(saga), saga, chronicle.here())


def of_player(saga: Saga, row: int | None) -> Command:
    """The Handouts of the Player chosen in Players, for the storyguide."""
    if row is None or not 0 <= row < len(saga.players):
        return Refuse(TITLE, "Choose a Player first.")
    player = saga.players[row]
    return handouts(here(saga), saga, player.id, player.name)
