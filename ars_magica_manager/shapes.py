"""The shape check: data coming in has the form the records expect, or it is
refused with a ValueError naming the field ("characters[mag1].background").

Two passes (ADR 0012), because every record's own `from_dict` migrates older
saves (renamed keys, text that became a list) before the values are typed:

* `check_raw(data, cls)`, before building: containers only. Where a field
  holds a record there is a dict, where it holds a list there is a list,
  and where it holds a plain value there is no dict or list -- what a
  `from_dict` needs in order not to fail on the wrong kind of thing. With
  `strict` (data from the network, written by the same version of the app),
  a key the record doesn't have is refused too, and no older shape is
  allowed. LEGACY lists the older shapes a `from_dict` still turns into the
  current one.
* `check_built(record)`, after building: every value against its field's
  type, exactly (an int stands for a float; None only where a field allows
  it; a bool is not an int).

The field types are the dataclasses' own annotations, each turned once into
a small plan (`_plan`) that the walks follow. The field's name in a refusal
is put together only on the way out of a refusal, so a sound saga costs
no names.

Pattern: a validator at the trust boundary; one function walking the
annotations, no class hierarchy.
"""

from __future__ import annotations

import dataclasses
import types
import typing
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from typing import Any, Literal, Union, get_args, get_origin, is_typeddict

#: Older shapes a `from_dict` still reads, by "Record.field" ("*.field" for
#: every record with that field): the kinds of value allowed there besides
#: the current one. Never over the network (`strict`): the same version
#: wrote that data.
LEGACY: dict[str, tuple[type, ...]] = {
    # Secrets were one piece of text before they were a list
    # (models.common.read_secrets).
    "*.secrets": (str,),
}

# The kinds of plan.
ANY, RECORD, SEQUENCE, MAPPING, TYPED, UNION, LITERAL, BOOL, INT, FLOAT, OTHER = range(
    11
)


@dataclass(frozen=True)
class _Plan:
    kind: int
    allows_none: bool = False
    #: RECORD: the dataclass; SEQUENCE: (container type, sized); OTHER: the type.
    cls: Any = None
    #: SEQUENCE: the items' plans (one, or one a place for a sized tuple);
    #: MAPPING: (key, value); UNION: each arm; TYPED: by `keys`.
    inner: tuple[_Plan, ...] = ()
    keys: tuple[str, ...] = ()
    #: LITERAL: the values allowed.
    values: tuple[object, ...] = ()


_PLAIN = {bool: BOOL, int: INT, float: FLOAT}


@cache
def _plan(hint: Any) -> _Plan:
    allows_none = False
    if get_origin(hint) in (Union, types.UnionType):
        args = tuple(a for a in get_args(hint) if a is not type(None))
        allows_none = len(args) < len(get_args(hint))
        hint = args[0] if len(args) == 1 else Union[args]  # noqa: UP007
    if hint is Any or hint is object:
        return _Plan(ANY, True)
    origin = get_origin(hint)
    if dataclasses.is_dataclass(hint) and isinstance(hint, type):
        return _Plan(RECORD, allows_none, hint)
    if origin in (list, tuple, set, frozenset):
        args = get_args(hint)
        sized = origin is tuple and bool(args) and args[-1] is not Ellipsis
        items = args if sized else (args[0] if args else Any,)
        return _Plan(
            SEQUENCE, allows_none, (origin, sized), tuple(_plan(a) for a in items)
        )
    if is_typeddict(hint):
        found = typing.get_type_hints(hint)
        return _Plan(
            TYPED,
            allows_none,
            inner=tuple(_plan(h) for h in found.values()),
            keys=tuple(found),
        )
    if origin in (dict, Mapping) or hint is dict:
        key, value = get_args(hint) or (Any, Any)
        return _Plan(MAPPING, allows_none, inner=(_plan(key), _plan(value)))
    if origin in (Union, types.UnionType):
        return _Plan(UNION, allows_none, inner=tuple(_plan(a) for a in get_args(hint)))
    if origin is Literal:
        return _Plan(LITERAL, allows_none, values=get_args(hint))
    if hint in _PLAIN:
        return _Plan(_PLAIN[hint], allows_none)
    if isinstance(hint, type):
        return _Plan(OTHER, allows_none, hint)
    return _Plan(ANY, True)  # a Callable or a type variable: not data from a file


@cache
def _record(cls: type) -> tuple[tuple[str, _Plan], ...]:
    """`cls`'s fields and their plans (the models write types as strings)."""
    hints = typing.get_type_hints(cls)
    return tuple((f.name, _plan(hints[f.name])) for f in dataclasses.fields(cls))


@cache
def _names(cls: type) -> frozenset[str]:
    return frozenset(name for name, _ in _record(cls))


@cache
def _required(cls: type) -> tuple[str, ...]:
    """The fields of `cls` with no default: a record without one can't be
    built."""
    return tuple(
        f.name
        for f in dataclasses.fields(cls)
        if f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING
    )


@cache
def _legacy(cls: type, name: str) -> tuple[type, ...]:
    return LEGACY.get(f"{cls.__name__}.{name}", ()) + LEGACY.get(f"*.{name}", ())


@cache
def _typed(plan: _Plan) -> dict[str, _Plan]:
    return dict(zip(plan.keys, plan.inner, strict=True))


class _Refused(Exception):
    """A refusal on its way out, gathering the field's name as it goes."""

    def __init__(self, why: str) -> None:
        super().__init__(why)
        self.why = why
        #: The field's name, innermost first.
        self.parts: list[str] = []


def _named(refused: _Refused) -> ValueError:
    path = ""
    for part in reversed(refused.parts):
        path += part if part.startswith("[") or not path else f".{part}"
    return ValueError(f"{path}: {refused.why}" if path else refused.why)


def _item(item: object, index: int) -> str:
    """A list item's name: its id when it has one, else its place."""
    found = item.get("id") if isinstance(item, dict) else getattr(item, "id", None)
    return f"[{found}]" if isinstance(found, str) and found else f"[{index}]"


# -- before building ---------------------------------------------------------


def check_raw(data: object, cls: type, *, strict: bool = False) -> None:
    """Refuse (ValueError) data of the wrong kind of container for record
    `cls` (see the module's docstring)."""
    try:
        _raw_record(data, cls, strict)
    except _Refused as refused:
        raise _named(refused) from None


def _raw_record(data: object, cls: type, strict: bool) -> None:
    if not isinstance(data, dict):
        raise _Refused(f"expected a record ({cls.__name__})")
    if strict:
        names = _names(cls)
        for key in data:
            if key not in names:
                refused = _Refused(f"not a field of {cls.__name__}")
                refused.parts.append(str(key))
                raise refused
    for name in _required(cls):
        if name not in data:
            refused = _Refused("missing")
            refused.parts.append(name)
            raise refused
    for name, plan in _record(cls):
        if plan.kind == ANY or name not in data:
            continue
        value = data[name]
        if plan.kind >= LITERAL and type(value) not in (dict, list):
            continue  # a plain value where one belongs (inline: the commonest)
        if not strict and isinstance(value, _legacy(cls, name)):
            continue
        try:
            _raw(value, plan, strict)
        except _Refused as refused:
            refused.parts.append(name)
            raise


def _raw(value: object, plan: _Plan, strict: bool) -> None:
    kind = plan.kind
    if value is None:
        if plan.allows_none or kind == ANY:
            return
        raise _Refused("missing")
    if kind == RECORD:
        _raw_record(value, plan.cls, strict)
    elif kind == SEQUENCE:
        if not isinstance(value, list):
            raise _Refused("expected a list")
        sized = plan.cls[1]
        if not sized and plan.inner[0].kind == ANY:
            return
        for index, entry in enumerate(value):
            if sized and index >= len(plan.inner):
                break
            try:
                _raw(entry, plan.inner[index] if sized else plan.inner[0], strict)
            except _Refused as refused:
                refused.parts.append(_item(entry, index))
                raise
    elif kind in (MAPPING, TYPED):
        if not isinstance(value, dict):
            raise _Refused("expected a record")
        plans = _typed(plan) if kind == TYPED else None
        if plans is None and plan.inner[1].kind == ANY:
            return
        for key, entry in value.items():
            inner = plans.get(key) if plans is not None else plan.inner[1]
            if inner is None:
                continue
            try:
                _raw(entry, inner, strict)
            except _Refused as refused:
                refused.parts.append(f"[{key}]")
                raise
    elif kind == UNION:
        first: _Refused | None = None
        for arm in plan.inner:
            try:
                _raw(value, arm, strict)
            except _Refused as refused:
                first = first or refused
            else:
                return
        assert first is not None  # a union has arms
        raise first
    elif kind != ANY and isinstance(value, dict | list):
        raise _Refused("expected a single value")


# -- a number typed or saved ---------------------------------------------------


def whole(value: object, default: int = 0) -> int:
    """A whole number from a value typed into a form or saved in a loose
    table: an int as it is, text of one read, and `default` for blank,
    text that isn't one, or anything else (a list, a record)."""
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip() or default)
        except ValueError:
            return default
    return default


def real(value: object, default: float = 0.0) -> float:
    """As `whole`, for a number that may have a fraction."""
    if isinstance(value, bool):
        return default
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip() or default)
        except ValueError:
            return default
    return default


# -- building a plain record -------------------------------------------------


def build[T](cls: type[T], data: object) -> T:
    """Record `cls` built from `data` as `asdict` wrote it, its records
    (and lists and dicts of them) built too, every key checked (strict) and
    every value typed: for a plain record with no `from_dict` of its own,
    such as a file the app keeps for itself. ValueError naming the field."""
    check_raw(data, cls, strict=True)
    try:
        record = _build_record(data, cls)
    except _Refused as refused:
        raise _named(refused) from None
    check_built(record)
    return record


def _build_record[T](data: object, cls: type[T]) -> T:
    fields = typing.cast(dict[str, object], data)
    values: dict[str, object] = {}
    for field in dataclasses.fields(typing.cast(Any, cls)):
        if field.name not in fields:
            if (
                field.default is dataclasses.MISSING
                and field.default_factory is dataclasses.MISSING
            ):
                refused = _Refused("missing")
                refused.parts.append(field.name)
                raise refused
            continue
        try:
            values[field.name] = _build_value(
                fields[field.name], dict(_record(cls))[field.name]
            )
        except _Refused as refused:
            refused.parts.append(field.name)
            raise
    return cls(**values)


def _build_value(value: object, plan: _Plan) -> object:
    if value is None:
        return None
    if plan.kind == RECORD:
        return _build_record(value, plan.cls)
    if plan.kind == SEQUENCE and plan.inner[0].kind == RECORD and not plan.cls[1]:
        items = typing.cast(list[object], value)
        return plan.cls[0](_build_value(item, plan.inner[0]) for item in items)
    if plan.kind == MAPPING and plan.inner[1].kind == RECORD:
        entries = typing.cast(dict[str, object], value)
        return {k: _build_value(v, plan.inner[1]) for k, v in entries.items()}
    return value


# -- after building ----------------------------------------------------------


def check_built(record: object) -> None:
    """Refuse (ValueError) a built record any of whose values isn't of its
    field's type (see the module's docstring)."""
    try:
        _built_record(record)
    except _Refused as refused:
        raise _named(refused) from None


def _built_record(record: object) -> None:
    for name, plan in _record(type(record)):
        kind = plan.kind
        if kind == ANY:
            continue
        value = getattr(record, name)
        # The commonest fields checked inline, without a call.
        if kind == OTHER and plan.cls is str and type(value) is str:
            continue
        if kind == INT and type(value) is int:
            continue
        if kind == BOOL and type(value) is bool:
            continue
        try:
            _built(value, plan)
        except _Refused as refused:
            refused.parts.append(name)
            raise


def _built(value: object, plan: _Plan) -> None:
    kind = plan.kind
    if value is None:
        if plan.allows_none or kind == ANY:
            return
        raise _Refused("missing")
    if kind == ANY:
        return
    if kind == RECORD:
        if not isinstance(value, plan.cls):
            raise _Refused(f"expected {plan.cls.__name__}")
        _built_record(value)
        return
    if kind == SEQUENCE:
        _built_sequence(value, plan)
        return
    if kind in (MAPPING, TYPED):
        _built_mapping(value, plan)
        return
    if kind == UNION:
        first: _Refused | None = None
        for arm in plan.inner:
            try:
                _built(value, arm)
            except _Refused as refused:
                first = first or refused
            else:
                return
        assert first is not None  # a union has arms
        raise first
    if kind == LITERAL:
        if value not in plan.values:
            raise _Refused(f"not one of {', '.join(map(repr, plan.values))}")
        return
    kind_of = type(value)
    if kind == BOOL:
        ok = kind_of is bool
    elif kind == INT:
        ok = isinstance(value, int) and kind_of is not bool
    elif kind == FLOAT:
        ok = isinstance(value, int | float) and kind_of is not bool
    else:
        ok = isinstance(value, plan.cls)
    if not ok:
        name = (
            plan.cls.__name__
            if kind == OTHER
            else ("bool", "int", "float")[kind - BOOL]
        )
        raise _Refused(f"expected {name}, not {kind_of.__name__}")


def _built_sequence(value: object, plan: _Plan) -> None:
    container, sized = plan.cls
    if not isinstance(value, container):
        raise _Refused(f"expected a {container.__name__}")
    if not sized and plan.inner[0].kind == ANY:
        return
    for index, entry in enumerate(typing.cast("typing.Iterable[object]", value)):
        if sized and index >= len(plan.inner):
            break
        try:
            _built(entry, plan.inner[index] if sized else plan.inner[0])
        except _Refused as refused:
            refused.parts.append(_item(entry, index))
            raise


def _built_mapping(value: object, plan: _Plan) -> None:
    if not isinstance(value, dict):
        raise _Refused("expected a record")
    entries = typing.cast(dict[object, object], value)
    if plan.kind == TYPED:
        plans = _typed(plan)
        for key, entry in entries.items():
            inner = plans.get(str(key))
            if inner is None:
                continue
            try:
                _built(entry, inner)
            except _Refused as refused:
                refused.parts.append(f"[{key}]")
                raise
        return
    key_plan, value_plan = plan.inner
    if key_plan.kind == ANY and value_plan.kind == ANY:
        return
    for key, entry in entries.items():
        try:
            _built(key, key_plan)
            _built(entry, value_plan)
        except _Refused as refused:
            refused.parts.append(f"[{key}]")
            raise
