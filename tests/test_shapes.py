"""The shape check (shapes.py): data coming in has the form the records
expect, or is refused with the field named; sound data, every shipped pack
and every test saga pass it."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

import pytest
from support import everything_saga

from ars_magica_manager import catalog, packs, shapes, storage, transfer
from ars_magica_manager.models import Character, Saga
from ars_magica_manager.models.common import Secret


def _data() -> dict:
    return json.loads(json.dumps(asdict(everything_saga())))


def _refused(data: object, *, strict: bool = False) -> str:
    with pytest.raises(ValueError) as refused:
        storage.saga_from_data(data, strict=strict)
    return str(refused.value)


def test_a_sound_saga_passes_both_ways():
    data = _data()
    saga = storage.saga_from_data(data, strict=True)
    assert saga.name == everything_saga().name
    shapes.check_built(saga)


def test_a_list_where_a_record_belongs_is_refused_by_its_field():
    data = _data()
    first = data["characters"][0]
    first["background"] = ["not", "a", "record"]
    assert _refused(data).startswith(f"characters[{first['id']}].background:")


def test_a_record_where_a_list_belongs_is_refused():
    data = _data()
    data["characters"] = {"oops": 1}
    assert _refused(data) == "characters: expected a list"


def test_a_list_where_a_plain_value_belongs_is_refused():
    data = _data()
    first = data["characters"][0]
    first["name"] = ["Leandro"]
    assert _refused(data) == f"characters[{first['id']}].name: expected a single value"


def test_a_plain_value_of_the_wrong_type_is_refused_after_building():
    data = _data()
    first = data["characters"][0]
    first["background"]["year_born"] = "long ago"
    message = _refused(data)
    assert message == (
        f"characters[{first['id']}].background.year_born: expected int, not str"
    )


def test_a_bool_is_not_a_number_and_none_only_where_allowed():
    data = _data()
    data["current_year"] = True
    assert _refused(data) == "current_year: expected int, not bool"
    data = _data()
    data["name"] = None
    assert _refused(data) == "name: missing"


def test_a_record_without_a_field_it_needs_is_refused():
    data = _data()
    first = data["characters"][0]
    del first["name"]
    assert _refused(data) == f"characters[{first['id']}].name: missing"


def test_not_a_saga_at_all():
    assert _refused(["a list"]) == "expected a record (Saga)"


def test_over_the_network_unknown_keys_and_older_shapes_are_refused():
    data = _data()
    data["characters"][0]["smuggled"] = "x"
    first = data["characters"][0]["id"]
    assert _refused(data, strict=True) == (
        f"characters[{first}].smuggled: not a field of Character"
    )
    storage.saga_from_data(data)  # a file may hold a newer copy's keys
    data = _data()
    data["covenants"][0]["secrets"] = "an older save's words"
    storage.saga_from_data(data)  # read from a file: the older shape
    assert "secrets" in _refused(data, strict=True)


def test_an_int_stands_for_a_float():
    @dataclass
    class Measure:
        length: float = 0.0
        tags: list[str] = field(default_factory=list)

    shapes.check_built(Measure(3))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match=r"tags\[0\]: expected str, not int"):
        shapes.check_built(Measure(1.5, [3]))  # type: ignore[list-item]


def test_build_makes_a_plain_record_and_names_what_is_wrong():
    @dataclass
    class Entry:
        when: float
        secret: Secret
        names: dict[str, int] = field(default_factory=dict)

    built = shapes.build(
        Entry, {"when": 1, "secret": {"title": "t"}, "names": {"a": 1}}
    )
    assert built.secret == Secret(title="t")
    with pytest.raises(ValueError, match="^when: missing$"):
        shapes.build(Entry, {"secret": {}})
    with pytest.raises(ValueError, match=r"^names\[a\]: expected int, not str$"):
        shapes.build(Entry, {"when": 1, "secret": {}, "names": {"a": "1"}})
    with pytest.raises(ValueError, match="not a field of Entry"):
        shapes.build(Entry, {"when": 1, "secret": {}, "extra": 0})


def test_numbers_typed_or_saved():
    assert shapes.whole("12") == 12
    assert shapes.whole(" ", 5) == 5
    assert shapes.whole(["12"], 7) == 7
    assert shapes.whole(True, 3) == 3
    assert shapes.whole(4.0) == 4
    assert shapes.real("2.5") == 2.5
    assert shapes.real({"a": 1}) == 0.0


def test_every_shipped_pack_passes():
    refused = []
    for path in sorted(packs.SHIPPED_DIR.glob(f"*{transfer.SUFFIX}")):
        try:
            data = transfer.read(path)
            if "overlay" in data:
                continue  # laid over a saga's own, never built whole
            built = Saga.from_dict(
                data["saga"], lab_feature_names=catalog.lab_feature_names()
            )
            shapes.check_built(built)
        except ValueError as problem:
            refused.append(f"{path.name}: {problem}")
    assert not refused, "\n".join(refused)


def test_a_character_of_a_type_the_app_does_not_know_is_refused():
    saga = Saga("s", "S", characters=[Character("c", "Cara", "Magus")])  # type: ignore[arg-type]
    with pytest.raises(ValueError, match=r"characters\[c\]\.type: not one of"):
        shapes.check_built(saga)
