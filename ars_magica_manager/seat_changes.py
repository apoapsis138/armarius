"""A change a Remote seat sends: one record, merged back onto the full saga
(ADR 0010).

A seat holds its Seat view (seat_view.py), so the record a Player edits
lacks what is hidden from them. A change carries the record twice, as it
was in the Seat view and as the Player left it. `apply_change`:

1. merges the Player's edit onto the host's record as that Player sees it
   now (three-way, merge.py: where both changed the same place, the
   Player's later save wins and the place is reported);
2. puts back what is hidden from the Player, from the host's full record:
   the record's Secrets (only the storyguide writes them), its links and
   Diary lines about records the Player doesn't know of, and a research
   target kept hidden;
3. checks the whole saga before and after with players.guard_changes, the
   one rule for what a Player may change, and refuses anything else.

Season plans and lab projects have no id: they are named by their
character and season, or their character and spell.

Pattern: Command (one change, one record) through the Protection Proxy
players.guard_changes, on the hosted saga's three-way merge.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from . import players, storage, viewing, world
from .merge import merge
from .models import CovenantDiaryEntry, Link, Player, Saga, known_fields
from .seat_view import looking_as, seat_view

#: The saga lists a Player may change a record of (players.guard_changes
#: says which records of them): their own records' lists and the shared
#: ones, from players.py, so a list a player may change is never left out
#: of what a seat sends.
CHANGEABLE = players.OWN_RECORDS | {"books", "spells", "enchanted_devices"}

Record = dict[str, Any]


class ChangeRefused(Exception):
    """The Player may not make this change (or it names nothing).
    `field`: for a change of the wrong shape, which field and why
    ("characters[mag1].background: expected a record"), for the host's log."""

    def __init__(self, why: str, *, field: str = "") -> None:
        super().__init__(why)
        self.field = field


@dataclass(frozen=True)
class Applied:
    """A change made: the saga as it now is, and where the Player's edit
    overlapped one made meanwhile (their later save kept)."""

    saga: Saga
    overlaps: list[str]


def record_key(kind: str, record: Record) -> str:
    """How a change names a record: its id, or for a season plan or lab
    project, its character and season (or spell)."""
    if kind == "season_plans":
        return (
            f"{record.get('character_id')}|{record.get('year')}|{record.get('season')}"
        )
    if kind == "lab_projects":
        return f"{record.get('character_id')}|{record.get('spell_id')}"
    return str(record.get("id", ""))


def _find(records: list[Record], kind: str, key: str) -> int | None:
    return next((i for i, r in enumerate(records) if record_key(kind, r) == key), None)


def apply_change(
    saga: Saga,
    player: Player,
    kind: str,
    key: str,
    before: Record | None,
    after: Record | None,
) -> Applied:
    """`saga` with the Player's change to one record made: `before` the
    record as their Seat view had it (None: they added it), `after` as they
    left it (None: they deleted it). Raises ChangeRefused when they may not,
    or the change names no record."""
    if kind not in CHANGEABLE or (before is None and after is None):
        raise ChangeRefused(f"Nothing to change in {kind!r}.")
    for given in (before, after):
        if given is not None and record_key(kind, given) != key:
            raise ChangeRefused("The change names another record.")
    reader = viewing.viewer_for(Player(id=player.id, name=player.name, role="player"))
    full = asdict(saga)
    seen = asdict(seat_view(saga, reader))
    host_full = _at(full[kind], kind, key)
    host_seen = _at(seen[kind], kind, key)
    if host_full is not None and host_seen is None:
        raise ChangeRefused("The record is not one the Player may read.")
    overlaps: list[str] = []
    if after is None:
        result = None
    else:
        visible, overlaps = (
            merge(before, after, host_seen) if host_seen else (after, [])
        )
        result = (
            _with_hidden(kind, visible, host_full, saga, reader)
            if host_full is not None
            else visible
        )
    changed = dict(full)
    changed[kind] = _replaced(full[kind], kind, key, result)
    kept, refused = players.guard_changes(player, full, changed)
    if refused:
        raise ChangeRefused(f"Not the Player's to change: {', '.join(refused)}.")
    try:
        # The Player's record, from another computer: its shape is checked
        # before and after building (shapes.py), strictly, as this app's
        # own version wrote it.
        changed_saga = storage.saga_from_data(kept, strict=True)
    except (KeyError, ValueError) as unreadable:
        raise ChangeRefused(
            "The change isn't a record this app can read.", field=str(unreadable)[:200]
        ) from unreadable
    return Applied(changed_saga, [f"{kind}.{o}" for o in overlaps])


def _at(records: list[Record], kind: str, key: str) -> Record | None:
    index = _find(records, kind, key)
    return records[index] if index is not None else None


def _replaced(
    records: list[Record], kind: str, key: str, result: Record | None
) -> list[Record]:
    index = _find(records, kind, key)
    kept = list(records)
    if index is None:
        if result is not None:
            kept.append(result)
    elif result is None:
        del kept[index]
    else:
        kept[index] = result
    return kept


def _with_hidden(
    kind: str, visible: Record, host_full: Record, saga: Saga, reader: viewing.Viewer
) -> Record:
    """`visible` (the record as the Player may see it, with their change)
    with what is hidden from them put back from the host's full record."""
    record = dict(visible)
    if "secrets" in host_full:
        # Only the storyguide writes Secrets: the host's stand.
        record["secrets"] = host_full["secrets"]
    with looking_as(reader, saga):
        if "links" in host_full:
            hidden = [
                link
                for link in host_full["links"]
                if not _link_readable(saga, link, reader)
            ]
            record["links"] = [*record.get("links", []), *hidden]
        if kind == "covenants":
            hidden_lines = [
                line
                for line in host_full.get("diary", [])
                if not _diary_line_readable(saga, line, reader)
            ]
            record["diary"] = [*record.get("diary", []), *hidden_lines]
    if kind == "characters":
        targets = {
            b.get("name"): b.get("target")
            for b in host_full.get("breakthroughs", [])
            if b.get("hidden_target") and not b.get("reached")
        }
        record["breakthroughs"] = [
            {**b, "target": targets[b.get("name")]}
            if b.get("name") in targets
            and b.get("hidden_target")
            and not b.get("reached")
            else b
            for b in record.get("breakthroughs", [])
        ]
    return record


def _link_readable(saga: Saga, link: Record, reader: viewing.Viewer) -> bool:
    """As seat_view asks it: a link to a record gone, or one the reader
    may read."""
    target = world.link_target(saga, Link(**known_fields(Link, link)))
    return target is None or viewing.may_read(reader, target)


def _diary_line_readable(saga: Saga, line: Record, reader: viewing.Viewer) -> bool:
    entry = CovenantDiaryEntry(**known_fields(CovenantDiaryEntry, line))
    return viewing.diary_readable(saga, entry, reader)
