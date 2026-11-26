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
  current one. A record's `id`, and each link to another record
  (RECORD_LINKS), must hold a plain id or nothing (ADR 0028).
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
import re
import types
import typing
import unicodedata
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

#: A plain id: lowercase letters, digits, _ and -, starting with a letter or
#: digit, at most 200 characters. Ids name files and are joined into paths,
#: so one from someone else's file must be no more than a name (ADR 0028).
PLAIN_ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,199}")

#: The links checked as plain ids besides each record's own `id`: those that
#: point at another of the saga's records. Other fields ending `_id` hold
#: catalog keys or keys the app puts together ("design:<key>", a lab
#: project's), which never name a file.
RECORD_LINKS = frozenset(
    {
        "saga_id",
        "covenant_id",
        "character_id",
        "owner_id",
        "lab_id",
        "laboratory_id",
        "assigned_lab_id",
        "new_lab_id",
        "author_id",
        "teacher_id",
        "student_id",
        "maker_id",
        "founder_id",
        "creature_id",
        "neighbour_id",
        "tribunal_id",
        "book_id",
        "codex_id",
        "device_id",
        "more_book_ids",
        "assistant_ids",
        "handler_ids",
    }
)

#: A saga's own id may also be one the headless admin's saga import took
#: before plain ids (capitals allowed): still only a name, and its file is
#: named for it already.
_ADMIN_SAGA_ID = re.compile(r"[A-Za-z0-9_-]{1,200}")


def is_plain_id(text: str) -> bool:
    """Whether `text` is a plain id (PLAIN_ID)."""
    return PLAIN_ID.fullmatch(text) is not None


# -- words typed into the Chronicle --

_EMOJI = "Emoji and picture symbols"
_INVISIBLE = "Invisible characters"
_CONTROL = "Control characters"
_UNKNOWN = "Characters with no meaning"


def _emoji_part(code: int) -> bool:
    """A character that is part of an emoji though not a symbol itself:
    variation selectors, skin-tone modifiers, the keycap ring."""
    return (
        0xFE00 <= code <= 0xFE0F
        or 0xE0100 <= code <= 0xE01EF
        or 0x1F3FB <= code <= 0x1F3FF
        or code == 0x20E3
    )


def _refused_kind(char: str) -> str | None:
    """Which kind of refused character `char` is, or None if it may be
    typed: letters and their marks in any language, digits, punctuation,
    maths and currency signs, spaces and a line break."""
    if char == "\n":
        return None
    code = ord(char)
    if _emoji_part(code):
        return _EMOJI
    category = unicodedata.category(char)
    if category == "So":
        return _EMOJI
    if category == "Cf":
        return _INVISIBLE
    if category in ("Cc", "Zl", "Zp"):
        return _CONTROL
    if category in ("Co", "Cs", "Cn"):
        return _UNKNOWN
    return None


def why_not_words(text: str) -> str | None:
    """Why `text` may not be put in the Chronicle, naming the first
    character refused, or None when it may. Emoji are refused, and so are
    the invisible characters (zero-width, or changing the text's direction)
    that could disguise a name or a link."""
    for char in text:
        kind = _refused_kind(char)
        if kind is None:
            continue
        shown = char if kind == _EMOJI else f"U+{ord(char):04X}"
        return f"{kind} can't be used here ({shown})."
    return None


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
    #: TYPED: the keys it must hold.
    required: tuple[str, ...] = ()


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
            required=_required_keys(hint),
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


def _required_keys(hint: Any) -> tuple[str, ...]:
    """The keys TypedDict `hint` must hold: `__required_keys__` (each
    class's own totality, inherited keys included), corrected by the
    `Required` and `NotRequired` it can't see in annotations written as
    text (`from __future__ import annotations`)."""
    total_keys = frozenset(getattr(hint, "__required_keys__", frozenset()))
    found = typing.get_type_hints(hint, include_extras=True)
    return tuple(
        key
        for key, each in found.items()
        if get_origin(each) is typing.Required
        or (key in total_keys and get_origin(each) is not typing.NotRequired)
    )


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
def _id_fields(cls: type) -> tuple[str, ...]:
    """The fields of `cls` holding ids: its own, and its links to other
    records (RECORD_LINKS)."""
    return tuple(
        name for name, _ in _record(cls) if name == "id" or name in RECORD_LINKS
    )


def _plain_ids(data: dict[Any, Any], cls: type) -> None:
    for name in _id_fields(cls):
        value = data.get(name)
        found = value if isinstance(value, list) else [value]
        if any(isinstance(v, str) and v and not _plain(v, cls, name) for v in found):
            refused = _Refused("not a plain id")
            refused.parts.append(name)
            raise refused


def _plain(value: str, cls: type, name: str) -> bool:
    if is_plain_id(value):
        return True
    return (
        cls.__name__ == "Saga"
        and name == "id"
        and bool(_ADMIN_SAGA_ID.fullmatch(value))
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


def check_raw(
    data: object, cls: type, *, strict: bool = False, plain_ids: bool = True
) -> None:
    """Refuse (ValueError) data of the wrong kind of container for record
    `cls`, or an id that isn't plain (see the module's docstring). Without
    `plain_ids` ids aren't checked: an import, which gives each record it
    brings in an id of its own."""
    try:
        _raw_record(data, cls, strict, plain_ids)
    except _Refused as refused:
        raise _named(refused) from None


def check_field(cls: type, name: str, value: object) -> None:
    """Refuse (ValueError, naming it) `value` for field `name` of record
    `cls` as check_raw would, or a field `cls` hasn't: a single change to a
    record, such as an overlay's."""
    plan = dict(_record(cls)).get(name)
    if plan is None:
        raise ValueError(f"{name}: not a field of {cls.__name__}")
    try:
        _plain_ids({name: value}, cls)  # names the field itself
        try:
            _raw(value, plan, False, True)
        except _Refused as refused:
            refused.parts.append(name)
            raise
    except _Refused as refused:
        raise _named(refused) from None


def _raw_record(data: object, cls: type, strict: bool, plain_ids: bool) -> None:
    if not isinstance(data, dict):
        raise _Refused(f"expected a record ({cls.__name__})")
    if plain_ids:
        _plain_ids(data, cls)
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
            _raw(value, plan, strict, plain_ids)
        except _Refused as refused:
            refused.parts.append(name)
            raise


def _raw(value: object, plan: _Plan, strict: bool, plain_ids: bool) -> None:
    kind = plan.kind
    if value is None:
        if plan.allows_none or kind == ANY:
            return
        raise _Refused("missing")
    if kind == RECORD:
        _raw_record(value, plan.cls, strict, plain_ids)
    elif kind == SEQUENCE:
        # A tuple only from `asdict` (a saga checked before it is saved):
        # JSON has none.
        if not isinstance(value, list | tuple):
            raise _Refused("expected a list")
        sized = plan.cls[1]
        if not sized and plan.inner[0].kind == ANY:
            return
        for index, entry in enumerate(value):
            if sized and index >= len(plan.inner):
                break
            try:
                _raw(
                    entry,
                    plan.inner[index] if sized else plan.inner[0],
                    strict,
                    plain_ids,
                )
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
                _raw(entry, inner, strict, plain_ids)
            except _Refused as refused:
                refused.parts.append(f"[{key}]")
                raise
    elif kind == UNION:
        first: _Refused | None = None
        for arm in plan.inner:
            try:
                _raw(value, arm, strict, plain_ids)
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


def why_not_fits(value: object, hint: Any) -> str | None:
    """Why `value`, a dict read back from JSON with no record to build (a
    Chronicle entry's body), isn't of type `hint` (a TypedDict) exactly,
    naming where; None when it is. Every key a TypedDict requires is there,
    a JSON list stands for a tuple, and a tuple of fixed size has that many
    items."""
    try:
        _fits(value, _plan(hint))
    except _Refused as refused:
        return str(_named(refused))
    return None


def _fits(value: object, plan: _Plan) -> None:
    kind = plan.kind
    if value is None or kind not in (SEQUENCE, TYPED, MAPPING, UNION):
        _built(value, plan)
    elif kind == SEQUENCE:
        if not isinstance(value, list | tuple):
            raise _Refused("expected a list")
        items = typing.cast("list[object]", value)
        sized = plan.cls[1]
        if sized and len(items) != len(plan.inner):
            raise _Refused(f"expected {len(plan.inner)} items")
        for index, item in enumerate(items):
            try:
                _fits(item, plan.inner[index] if sized else plan.inner[0])
            except _Refused as refused:
                refused.parts.append(_item(item, index))
                raise
    elif kind == UNION:
        first: _Refused | None = None
        for arm in plan.inner:
            try:
                _fits(value, arm)
            except _Refused as refused:
                first = first or refused
            else:
                return
        assert first is not None  # a union has arms
        raise first
    else:
        _fits_mapping(value, plan)


def _fits_mapping(value: object, plan: _Plan) -> None:
    if not isinstance(value, dict):
        raise _Refused("expected a record")
    entries = typing.cast(dict[object, object], value)
    for key in plan.required:
        if key not in entries:
            refused = _Refused("missing")
            refused.parts.append(key)
            raise refused
    plans = _typed(plan) if plan.kind == TYPED else None
    for key, entry in entries.items():
        inner = plans.get(str(key)) if plans is not None else plan.inner[1]
        if inner is None:
            continue
        try:
            if plans is None:
                _fits(key, plan.inner[0])
            _fits(entry, inner)
        except _Refused as refused:
            refused.parts.append(str(key) if plans is not None else f"[{key}]")
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
