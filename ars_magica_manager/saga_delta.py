"""A storyguide's change from a Remote seat: what changed in the whole saga,
folded into the host's (ADR 0014).

A storyguide's seat holds the whole saga, so its changes are not limited to
the records a player may change: any record, the saga's settings, and the
season itself when they advance it. A save sends only what changed since
the seat's last snapshot, as two maps of the same places, "before" (as the
snapshot had it) and "after" (as the storyguide left it). A place is a
top-level field of the saga ("current_year", "notify_npc_unplanned"), or one
record of a list of records, by id ("characters[mag1]"); a record missing
from "before" was added, one missing from "after" deleted.

The host folds it in with the three-way merge it uses for every hosted save
(merge.py, ADR 0005): the places the delta names are set to "before" and to
"after" over the host's own saga, and merged, so another's change made
meanwhile is kept unless it touched the same place. Two things stay the
host's: the saga's Players (who may join, and as what), and an advance made
from a date that is no longer the saga's (another storyguide advanced first).

Pattern: Command (one change to the whole saga), on the hosted saga's
three-way merge.
"""

from __future__ import annotations

import copy
import re
from dataclasses import asdict, dataclass, fields
from typing import Any

from . import storage, viewing
from .merge import merge
from .models import Saga

#: The saga's own fields only the host changes (ADR 0014).
HOST_ONLY = frozenset({"players"})
#: The fields that say which season it is.
DATE = ("current_season", "current_year")

Delta = tuple[dict[str, Any], dict[str, Any]]

_RECORD = re.compile(r"^(\w+)\[(.+)\]$")
_FIELDS = frozenset(f.name for f in fields(Saga))


class DeltaRefused(Exception):
    """The change can't be taken: it names something only the host changes,
    or a place the saga hasn't, or it was made from a season the saga has
    since left (`advanced`: "who|Summer 1221", who saved it last and the
    date it is now)."""

    def __init__(self, why: str, *, advanced: str = "") -> None:
        super().__init__(why)
        self.advanced = advanced


def _records(value: Any) -> bool:
    """Whether `value` is a list of records, each with an id."""
    return isinstance(value, list) and all(
        isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"]
        for item in value
    )


def saga_delta(base: dict[str, Any], now: dict[str, Any]) -> Delta:
    """What changed from `base` to `now` (both `asdict` of a saga), as
    (before, after); both empty when nothing did."""
    before: dict[str, Any] = {}
    after: dict[str, Any] = {}
    for key, is_ in now.items():
        was = base.get(key)
        if was == is_:
            continue
        if isinstance(was, list) and isinstance(is_, list) and _records(was + is_):
            old = {r["id"]: r for r in was}
            new = {r["id"]: r for r in is_}
            for record_id in [*old, *(i for i in new if i not in old)]:
                if old.get(record_id) == new.get(record_id):
                    continue
                place = f"{key}[{record_id}]"
                if record_id in old:
                    before[place] = old[record_id]
                if record_id in new:
                    after[place] = new[record_id]
        else:
            before[key], after[key] = was, is_
    return before, after


def _set(data: dict[str, Any], place: str, value: Any, present: bool) -> None:
    """Put `value` at `place` in `data` (a record removed when not `present`)."""
    found = _RECORD.match(place)
    if found is None:
        data[place] = value
        return
    key, record_id = found.groups()
    records = [r for r in data.get(key) or [] if r.get("id") != record_id]
    if present:
        at = next(
            (i for i, r in enumerate(data.get(key) or []) if r.get("id") == record_id),
            len(records),
        )
        records.insert(at, value)
    data[key] = records


def _key_of(place: str) -> str:
    found = _RECORD.match(place)
    return found.group(1) if found else place


@dataclass(frozen=True)
class Folded:
    """A storyguide's change made: the saga as it now is, where it overlapped
    a change made meanwhile (theirs kept), and whether it advanced the
    season (the host backs up first)."""

    saga: Saga
    overlaps: list[str]
    advanced: bool


#: The record lists with their own storyguide (viewing.ASSIGNABLE), and
#: those whose records are a character's (theirs is the character's).
_ASSIGNABLE = frozenset(
    {"characters", "covenants", "neighbours", "creatures", "tribunals"}
)
_CHARACTERS_OWN = {"laboratories": "owner_id", "familiars": "character_id"}


def _owner(saga: Saga, place: str) -> str:
    """Who runs the record at `place` in `saga`, as viewing.storyguide_of
    says ("" for a field of the saga, or a record not there)."""
    found = _RECORD.match(place)
    if found is None:
        return ""
    key, record_id = found.groups()
    record = next((r for r in getattr(saga, key, []) if r.id == record_id), None)
    return viewing.storyguide_of(record, saga) if record is not None else ""


def _refuse_others(
    saga: Saga,
    me: str,
    places: list[str],
    before: dict[str, Any],
    after: dict[str, Any],
) -> None:
    """Refuse a change to another storyguide's record, or one that takes
    a record for anyone but `me` or hands on one not theirs (ADR 0015)."""
    live = viewing.storyguide_ids(saga)
    for place in places:
        if not _RECORD.match(place):
            _refuse_character_lines(saga, me, place, before, after)
            continue
        owner = _owner(saga, place)
        if owner and owner != me:
            raise DeltaRefused(f"{place} is another storyguide's.")
        key = _key_of(place)
        record = after.get(place)
        if key in _CHARACTERS_OWN and isinstance(record, dict) and place not in before:
            # A new laboratory or familiar: its character must be the
            # storyguide's to change.
            character = saga.character(str(record.get(_CHARACTERS_OWN[key]) or ""))
            if character is not None and viewing.storyguide_of(character, saga) not in (
                "",
                me,
            ):
                raise DeltaRefused(f"{place} belongs to another storyguide's story.")
        if key not in _ASSIGNABLE or not isinstance(record, dict):
            continue
        given = str(record.get("storyguide_id") or "")
        given = given if given in live else ""
        if given not in ("", me) and owner != me:
            raise DeltaRefused(f"Only {place}'s own storyguide hands it on.")


def _refuse_character_lines(
    saga: Saga, me: str, place: str, before: dict[str, Any], after: dict[str, Any]
) -> None:
    """A list of the saga's without ids (season plans, lab projects): each
    line added, changed or taken out that is a character's must be a
    character the storyguide `me` may change."""
    was, now = before.get(place), after.get(place)
    if not isinstance(was, list) or not isinstance(now, list):
        return
    changed = [r for r in was if r not in now] + [r for r in now if r not in was]
    for line in changed:
        if not isinstance(line, dict) or "character_id" not in line:
            continue
        character = saga.character(str(line.get("character_id") or ""))
        if character is not None and viewing.storyguide_of(character, saga) not in (
            "",
            me,
        ):
            raise DeltaRefused(f"{place} names another storyguide's character.")


def fold(
    saga: Saga, before: dict[str, Any], after: dict[str, Any], *, by: str = ""
) -> Folded:
    """`saga` (the host's) with a storyguide's change folded in. Raises
    DeltaRefused for a change only the host may make, one to a record
    another storyguide runs (`by`: the id of the storyguide who made it),
    or one naming no place of the saga; ValueError, naming the field, for
    one it can't read."""
    theirs = asdict(saga)
    places = [*before, *(p for p in after if p not in before)]
    for place in places:
        key = _key_of(place)
        if key not in _FIELDS:
            raise DeltaRefused(f"The saga has no {key!r}.")
        if key in HOST_ONLY:
            raise DeltaRefused("Only the host changes the saga's Players.")
        if _RECORD.match(place) and not _records(theirs.get(key) or []):
            raise DeltaRefused(f"{key!r} is not a list of records.")
    if by:
        _refuse_others(saga, by, places, before, after)
    advancing = any(key in after for key in DATE)
    if advancing and any(before[key] != theirs[key] for key in DATE if key in before):
        now = f"{theirs['current_season']} {theirs['current_year']}"
        # Whoever saved the saga last (the advance, as a rule), by name.
        who = str(theirs.get("saved_by") or "Someone")
        raise DeltaRefused(
            f"{who} has already advanced the saga to {now}.",
            advanced=f"{who}|{now}",
        )
    base, ours = copy.deepcopy(theirs), copy.deepcopy(theirs)
    for place in places:
        _set(base, place, before.get(place), place in before)
        _set(ours, place, after.get(place), place in after)
    merged, overlaps = merge(base, ours, theirs)
    # The storyguide's saga, from another computer: its shape checked
    # before and after building, strictly (shapes.py).
    changed = storage.saga_from_data(merged, strict=True)
    return Folded(changed, overlaps, advancing)
