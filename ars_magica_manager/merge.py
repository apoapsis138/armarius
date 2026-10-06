"""Merging a saga's changes into the file other copies of the app also save
to.

When the storyguide hosts the app, each browser tab runs its own copy, each
with the saga in memory. Saving the whole saga from one copy would wipe
whatever another copy saved since. Instead a save is a three-way merge of
plain saga data (the dicts dataclasses.asdict makes):

- `base`: the saga as this copy last loaded or saved it,
- `ours`: the saga as this copy has it now,
- `theirs`: the saga as the file has it now.

What this copy changed since `base` is applied to `theirs`; everything else
stays as the file has it. Dicts merge key by key, and lists of records with
ids (characters, books, a covenant's diary entries...) merge record by
record, so two people changing different things both keep their changes.
When both changed the same value, ours -- the later save -- wins, and the
place is reported as a conflict.
"""

from __future__ import annotations

from typing import Any

#: Stands for a dict key or record that isn't there.
_MISSING: Any = object()


def merge(base: Any, ours: Any, theirs: Any) -> tuple[Any, list[str]]:
    """`ours`' changes since `base` applied to `theirs`, and where both had
    changed the same value differently (ours was kept), as paths such as
    "characters[mag1].name"."""
    conflicts: list[str] = []
    merged = _merge(base, ours, theirs, "", conflicts)
    return merged, conflicts


def _merge(base: Any, ours: Any, theirs: Any, where: str, conflicts: list[str]) -> Any:
    if _same(ours, base):
        return theirs  # we changed nothing here
    if _same(theirs, base) or _same(ours, theirs):
        return ours  # only we changed it (or both the same way)
    if isinstance(ours, dict) and isinstance(theirs, dict):
        return _merge_dicts(base, ours, theirs, where, conflicts)
    if (
        isinstance(ours, list)
        and isinstance(theirs, list)
        and _records(ours)
        and _records(theirs)
        and (base is _MISSING or _records(base))
    ):
        return _merge_records(base, ours, theirs, where, conflicts)
    conflicts.append(where or "(the saga)")
    return ours


def _same(a: Any, b: Any) -> bool:
    return a is b or (a is not _MISSING and b is not _MISSING and a == b)


def _merge_dicts(
    base: Any, ours: dict, theirs: dict, where: str, conflicts: list[str]
) -> dict:
    base = base if isinstance(base, dict) else {}
    merged: dict[str, Any] = {}
    for key in [*theirs, *(k for k in ours if k not in theirs)]:
        value = _merge(
            base.get(key, _MISSING),
            ours.get(key, _MISSING),
            theirs.get(key, _MISSING),
            f"{where}.{key}" if where else key,
            conflicts,
        )
        if value is not _MISSING:
            merged[key] = value
    return merged


def _records(value: Any) -> bool:
    """Whether `value` is a list of records with distinct ids."""
    if not isinstance(value, list):
        return False
    ids = [item.get("id") for item in value if isinstance(item, dict)]
    return (
        len(ids) == len(value)
        and all(isinstance(i, str) and i for i in ids)
        and len(set(ids)) == len(ids)
    )


def _merge_records(
    base: Any, ours: list, theirs: list, where: str, conflicts: list[str]
) -> list:
    """Record by record, by id: in the file's order, then the records this
    copy added."""
    by_id = {
        name: {r["id"]: r for r in records}
        for name, records in (
            ("base", base if isinstance(base, list) else []),
            ("ours", ours),
            ("theirs", theirs),
        )
    }
    order = [r["id"] for r in theirs]
    order += [r["id"] for r in ours if r["id"] not in by_id["theirs"]]
    merged = []
    for record_id in order:
        value = _merge(
            by_id["base"].get(record_id, _MISSING),
            by_id["ours"].get(record_id, _MISSING),
            by_id["theirs"].get(record_id, _MISSING),
            f"{where}[{record_id}]",
            conflicts,
        )
        if value is not _MISSING:
            merged.append(value)
    return merged
