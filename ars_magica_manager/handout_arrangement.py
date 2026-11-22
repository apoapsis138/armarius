"""A player's own arrangement of their Handouts (handout_list.py): their
own title for a Handout, pins, and folders one level deep.

Kept in a small file of that Player's beside the saga, in the Show folder
(`shows/<saga id>/handouts-<player id>.json`, ADR 0020), written only by
the host: the saga's Players are the host's alone (ADR 0014), so a Remote
seat changes it by asking (`arrange_handouts`), not by a saga change. Only
that Player reads or changes it; not even the storyguide.

Pattern: each change is a Command (Arrange) the host carries out, under
the file's lock; `readable` is the Protection Proxy's one rule for it."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

from . import handout_list, shapes, shows
from .files import held_lock, write_atomic
from .models import Saga

#: Why another reader is refused a Player's arrangement.
NOT_YOURS = "Only you arrange your Handouts."
#: Why a Player id no file could be named by is refused.
NO_FILE = "Your Handouts can't be arranged from here."
#: What a list calls a Handout in no folder, so no folder may take it.
NO_FOLDER = "(no folder)"
#: The longest title a player may give a Handout, and folder name.
MOST_TITLE, MOST_FOLDER = 200, 80
#: The most a file of arrangement may be read back as.
FILE_CAP = 512 * 1024


@dataclass
class Place:
    """Where a player keeps one Handout (by handout_list.Kept.key): its
    folder ("": none), their own title ("": the one it was shown under),
    and whether it is pinned."""

    key: str
    folder: str = ""
    title: str = ""
    pinned: bool = False

    @property
    def plain(self) -> bool:
        """Whether it changes nothing, so needn't be kept."""
        return not (self.folder or self.title or self.pinned)


@dataclass
class Arrangement:
    """A player's folders, in the order made, and their Places."""

    folders: list[str] = field(default_factory=list)
    places: list[Place] = field(default_factory=list)

    def place(self, key: str) -> Place:
        return next((p for p in self.places if p.key == key), Place(key))


@dataclass(frozen=True)
class Arrange:
    """One change to a Handout's place: each given value replaces its
    own ("" puts back the shown title, or takes it out of its folder)."""

    key: str
    title: str | None = None
    pinned: bool | None = None
    folder: str | None = None


@dataclass(frozen=True)
class Arranged:
    """A Handout as its player's list shows it."""

    kept: handout_list.Kept
    title: str
    folder: str
    pinned: bool


def to_data(kept: Arrangement) -> dict[str, object]:
    """An arrangement as plain data, to send its player's seat."""
    return asdict(kept)


def from_data(data: object) -> Arrangement:
    """An arrangement the host sent, its shape checked (shapes.build);
    ValueError naming the field for the wrong shape."""
    return shapes.build(Arrangement, data)


def readable(player_id: str, reader: str) -> bool:
    """Whether `reader` may read or change Player `player_id`'s
    arrangement: that Player alone."""
    return bool(player_id) and reader == player_id


def path_of(saga_id: str, player_id: str) -> Path:
    """Where Player `player_id`'s arrangement is kept; ValueError for an
    id no file could be named by."""
    if not shapes.is_plain_id(player_id):
        raise ValueError(f"A Player id can't name a file: {player_id!r}")
    return shows.folder_of(saga_id) / f"handouts-{player_id}.json"


def load(saga_id: str, player_id: str) -> Arrangement:
    """Player `player_id`'s arrangement; none for a file missing, too
    large or damaged (the Handouts then read as shown)."""
    path = path_of(saga_id, player_id)
    try:
        if path.stat().st_size > FILE_CAP:
            return Arrangement()
        return shapes.build(Arrangement, json.loads(path.read_text("utf-8")))
    except OSError, UnicodeDecodeError, ValueError, RecursionError:
        return Arrangement()


def why_not_words(call: Arrange) -> str | None:
    """Why the title or folder `call` gives may not be kept, or None: each
    within its length, and the character rule (shapes.why_not_words)."""
    for words, most, what in (
        (call.title, MOST_TITLE, "A title"),
        (call.folder, MOST_FOLDER, "A folder's name"),
    ):
        if words is None:
            continue
        if len(words) > most:
            return f"{what} may be at most {most} characters."
        problem = shapes.why_not_words(words)
        if problem:
            return problem
    if call.folder is not None and call.folder.strip() == NO_FOLDER:
        return f"A folder can't be called {NO_FOLDER}."
    return None


def _why_not(call: Arrange, shown: set[str]) -> str | None:
    if call.key not in shown:
        return "That Handout isn't in your list."
    return why_not_words(call)


def _changed(found: Arrangement, call: Arrange) -> Arrangement:
    place = found.place(call.key)
    place = replace(
        place,
        title=place.title if call.title is None else call.title.strip(),
        pinned=place.pinned if call.pinned is None else call.pinned,
        folder=place.folder if call.folder is None else call.folder.strip(),
    )
    places = [p for p in found.places if p.key != call.key]
    if not place.plain:
        places.append(place)
    used = {p.folder for p in places if p.folder}
    folders = [f for f in found.folders if f in used]
    folders += [f for f in sorted(used) if f not in folders]
    return Arrangement(folders, places)


def arrange(saga: Saga, player_id: str, call: Arrange, *, by: str) -> str | None:
    """Carry out `call` on Player `player_id`'s arrangement, for `by`:
    None once it is kept, else why not (the host's own check; a seat's
    form asks the same first)."""
    if not readable(player_id, by):
        return NOT_YOURS
    if not shapes.is_plain_id(player_id):
        return NO_FILE
    shown = {k.key for k in handout_list.of_player(saga, player_id)}
    problem = _why_not(call, shown)
    if problem:
        return problem
    path = path_of(saga.id, player_id)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with held_lock(path.with_suffix(".lock")):
            found = _changed(load(saga.id, player_id), call)
            write_atomic(path, json.dumps(asdict(found), ensure_ascii=False))
    except OSError:
        return "Your Handouts couldn't be saved just now."
    return None


def arrangement_of(saga_id: str, player_id: str, reader: str) -> Arrangement | str:
    """Player `player_id`'s arrangement, for `reader` (that Player alone),
    or why not."""
    if not readable(player_id, reader):
        return NOT_YOURS
    if not shapes.is_plain_id(player_id):
        return NO_FILE
    return load(saga_id, player_id)


def arranged(found: Sequence[handout_list.Kept], kept: Arrangement) -> list[Arranged]:
    """`found` (newest first) as their player keeps them: those in no
    folder first, then each folder in the order made, pinned first within
    each, each under their own title. A list headed by folder then heads
    each folder once."""
    shown = [
        Arranged(
            k,
            kept.place(k.key).title or k.title,
            kept.place(k.key).folder,
            kept.place(k.key).pinned,
        )
        for k in found
    ]
    order = {"": 0, **{f: i + 1 for i, f in enumerate(kept.folders)}}
    return sorted(
        shown, key=lambda a: (order.get(a.folder, len(order)), a.folder, not a.pinned)
    )
