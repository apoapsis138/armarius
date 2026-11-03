"""The Atlas's core (atlas.py): maps on Tribunals and the saga, pictures
copied by hash, pins placed, moved, hidden and kept secret, and which
records a map shows where: at their own pin, at their place's, and a
mobile covenant at its stop's."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

import pytest

from ars_magica_manager import atlas, storage
from ars_magica_manager.models import (
    AtlasMap,
    Covenant,
    CovenantStop,
    Creature,
    Laboratory,
    Neighbour,
    Pin,
    Saga,
    Tribunal,
)


def _png(width: int, height: int) -> bytes:
    """A real, one-colour PNG of the size asked for."""

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    rows = b"".join(b"\x00" + b"\xff\xff\xff" * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def _jpeg(width: int, height: int) -> bytes:
    """A JPEG's header as far as its frame's size, after an APP0 block."""
    app0 = (
        b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x01\x01\x00" + bytes(7)
    )
    sof = b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, height, width, 1) + bytes(3)
    return b"\xff\xd8" + app0 + sof


def _webp_lossless(width: int, height: int) -> bytes:
    bits = (width - 1) | ((height - 1) << 14)
    body = b"VP8L" + struct.pack("<I", 5) + b"\x2f" + struct.pack("<I", bits)
    return b"RIFF" + struct.pack("<I", 4 + len(body)) + b"WEBP" + body


def _webp_extended(width: int, height: int) -> bytes:
    body = (
        b"VP8X"
        + struct.pack("<I", 10)
        + bytes(4)
        + (width - 1).to_bytes(3, "little")
        + (height - 1).to_bytes(3, "little")
    )
    return b"RIFF" + struct.pack("<I", 4 + len(body)) + b"WEBP" + body


@pytest.mark.parametrize(
    "data",
    [_png(30, 20), _jpeg(30, 20), _webp_lossless(30, 20), _webp_extended(30, 20)],
    ids=["png", "jpeg", "webp-lossless", "webp-extended"],
)
def test_a_pictures_size_is_read_from_its_header(data: bytes):
    assert atlas.picture_size(data) == (30, 20)


def test_a_file_that_isnt_a_picture_is_refused():
    with pytest.raises(ValueError, match="isn't a PNG"):
        atlas.picture_size(b"GIF89a....")


def test_a_picture_is_copied_once_by_its_bytes(tmp_path: Path):
    first = tmp_path / "rhine.png"
    first.write_bytes(_png(40, 20))
    again = tmp_path / "copy of rhine.PNG"
    again.write_bytes(_png(40, 20))
    name, width, height = atlas.store_picture(first)
    assert (width, height) == (40, 20)
    assert atlas.store_picture(again)[0] == name
    assert [p.name for p in storage.maps_dir().iterdir()] == [name]


def _saga() -> Saga:
    """A Tribunal; a covenant in a forest with a laboratory, a regio inside
    the forest with a creature, a town, and a mobile covenant."""
    forest = Neighbour("forest", "The Black Forest", kind="place")
    regio = Neighbour("regio", "The Grey Regio", kind="place", place_id="forest")
    town = Neighbour("town", "Basel", kind="town")
    harbour = Neighbour("harbour", "The Harbour", kind="place")
    return Saga(
        "s",
        "Saga",
        tribunals=[Tribunal("rhine", "The Rhine")],
        covenants=[
            Covenant("cov", "s", "Durenmar", place_id="forest"),
            Covenant(
                "ship",
                "s",
                "The Ark",
                stops=[CovenantStop(1219, "Spring", "harbour")],
            ),
        ],
        laboratories=[Laboratory("lab", "cov", "The Tower")],
        neighbours=[forest, regio, town, harbour],
        creatures=[Creature("wolf", "Grey Wolf", place_id="regio")],
    )


def _shown(saga: Saga, map_id: str, **options: object) -> dict[str, tuple]:
    return {
        s.ref.name: (s.x, s.y, s.at)
        for s in atlas.shown_pins(saga, map_id, **options)  # type: ignore[arg-type]
    }


def test_records_show_at_their_own_pin_or_at_the_place_they_are_in():
    saga = _saga()
    m = atlas.add_map(saga, "The Rhine", "rhine")
    atlas.place_pin(saga, m.id, "neighbours", "forest", 0.5, 0.25)
    atlas.place_pin(saga, m.id, "neighbours", "town", 0.1, 0.9)
    shown = _shown(saga, m.id)
    assert shown["The Black Forest"] == (0.5, 0.25, "")
    # A covenant in the forest, its laboratory, the regio in the forest
    # and the creature in the regio all show at the forest's pin.
    assert shown["Durenmar"] == (0.5, 0.25, "The Black Forest")
    assert shown["The Tower"] == (0.5, 0.25, "The Black Forest")
    assert shown["The Grey Regio"] == (0.5, 0.25, "The Black Forest")
    assert shown["Grey Wolf"] == (0.5, 0.25, "The Black Forest")
    assert shown["Basel"] == (0.1, 0.9, "")
    # A pin of its own wins over its place's.
    atlas.place_pin(saga, m.id, "covenants", "cov", 0.6, 0.3)
    shown = _shown(saga, m.id)
    assert shown["Durenmar"] == (0.6, 0.3, "")
    assert shown["The Tower"] == (0.6, 0.3, "Durenmar")


def test_a_mobile_covenant_follows_its_stop_past_a_pin_of_its_own():
    saga = _saga()
    saga.current_year, saga.current_season = 1220, "Summer"
    m = atlas.add_map(saga, "The Rhine", "rhine")
    atlas.place_pin(saga, m.id, "covenants", "ship", 0.9, 0.9)
    assert "The Ark" not in _shown(saga, m.id)
    atlas.place_pin(saga, m.id, "neighbours", "harbour", 0.3, 0.7)
    assert _shown(saga, m.id)["The Ark"] == (0.3, 0.7, "The Harbour")


def test_a_place_inside_itself_shows_nowhere():
    saga = _saga()
    saga.neighbours[0].place_id = "regio"
    m = atlas.add_map(saga, "The Rhine", "rhine")
    assert _shown(saga, m.id) == {}


def test_the_table_view_leaves_off_a_secret_pin_and_all_shown_at_it():
    saga = _saga()
    m = atlas.add_map(saga, "The Rhine", "rhine")
    atlas.place_pin(saga, m.id, "neighbours", "forest", 0.5, 0.25).secret = True
    atlas.place_pin(saga, m.id, "neighbours", "town", 0.1, 0.9)
    assert len(_shown(saga, m.id)) == 6
    assert list(_shown(saga, m.id, table=True)) == ["Basel"]


def test_the_kinds_shown_can_be_narrowed():
    saga = _saga()
    m = atlas.add_map(saga, "The Rhine", "rhine")
    atlas.place_pin(saga, m.id, "neighbours", "forest", 0.5, 0.25)
    assert list(_shown(saga, m.id, kinds=("covenants",))) == ["Durenmar"]


def test_a_packs_pin_taken_off_stays_off_until_placed_again():
    saga = _saga()
    m = atlas.add_map(saga, "The Rhine", "rhine")
    saga.pins.append(Pin(m.id, "neighbours", "town", 0.1, 0.9, from_pack=True))
    own = atlas.place_pin(saga, m.id, "neighbours", "forest", 0.5, 0.5)
    atlas.remove_pin(saga, saga.pins[0])
    atlas.remove_pin(saga, own)
    assert [(p.record_id, p.hidden) for p in saga.pins] == [("town", True)]
    assert "Basel" not in _shown(saga, m.id)
    assert "Basel" in [c.value.name for c in atlas.pinnable(saga, m.id)]
    atlas.place_pin(saga, m.id, "neighbours", "town", 0.2, 0.8)
    assert len(saga.pins) == 1 and not saga.pins[0].hidden
    assert _shown(saga, m.id)["Basel"] == (0.2, 0.8, "")


def test_place_on_map_offers_what_has_no_pin_and_a_pin_stays_on_the_map():
    saga = _saga()
    m = atlas.add_map(saga, "The Rhine", "rhine")
    atlas.place_pin(saga, m.id, "neighbours", "forest", 1.4, -0.2)
    assert (saga.pins[0].x, saga.pins[0].y) == (1.0, 0.0)
    offered = [c.value.name for c in atlas.pinnable(saga, m.id)]
    assert "The Black Forest" not in offered
    assert {"Durenmar", "Basel", "Grey Wolf"} <= set(offered)
    # A laboratory shows at its covenant's pin, and isn't placed itself.
    assert "The Tower" not in offered


def test_a_map_belongs_to_its_tribunal_or_the_saga_and_takes_its_pins_with_it():
    saga = _saga()
    rhine = atlas.add_map(saga, "The Rhine", "rhine")
    alone = atlas.add_map(saga, "The Rhine", None)
    assert alone.id != rhine.id
    assert saga.tribunals[0].maps == [rhine] and saga.maps == [alone]
    assert atlas.map_label(rhine, saga.tribunals[0]) == "The Rhine (The Rhine)"
    atlas.move_map(saga, alone, "rhine")
    assert saga.tribunals[0].maps == [rhine, alone] and saga.maps == []
    atlas.place_pin(saga, rhine.id, "neighbours", "town", 0.1, 0.1)
    atlas.place_pin(saga, alone.id, "neighbours", "town", 0.2, 0.2)
    atlas.remove_map(saga, rhine)
    assert [p.map_id for p in saga.pins] == [alone.id]
    assert atlas.maps_showing(saga, "neighbours", "town") == [alone]


def test_the_map_form_copies_its_picture_and_warns_of_new_proportions(tmp_path):
    saga = _saga()
    wide = tmp_path / "wide.png"
    wide.write_bytes(_png(40, 20))
    form = atlas.map_form(saga)
    values = {"name": "The Rhine", "tribunal": "rhine", "picture": str(wide)}
    assert form.validate is not None and form.validate(values) is None
    assert form.apply(values) == []
    [made] = saga.tribunals[0].maps
    assert (made.width, made.height) == (40, 20)
    assert atlas.picture_path(made) is not None
    atlas.place_pin(saga, made.id, "neighbours", "town", 0.5, 0.5)
    tall = tmp_path / "tall.png"
    tall.write_bytes(_png(20, 40))
    edit = atlas.map_form(saga, made)
    said = edit.apply({"name": "The Rhine", "tribunal": None, "picture": str(tall)})
    assert said and "proportions" in said[0]
    assert saga.maps == [made] and saga.tribunals[0].maps == []
    assert saga.pins[0].x == 0.5
    junk = tmp_path / "notes.png"
    junk.write_text("not a picture")
    assert "isn't a PNG" in (edit.validate or (lambda _v: ""))(
        {"name": "x", "picture": str(junk)}
    )


def test_maps_and_pins_round_trip_and_older_saves_load_without():
    saga = _saga()
    m = atlas.add_map(saga, "The Rhine", "rhine", picture="ab.png", width=4, height=3)
    atlas.place_pin(saga, m.id, "neighbours", "town", 0.25, 0.5).secret = True
    storage.save_saga(saga)
    loaded = storage.load_saga(saga.id)
    assert loaded.tribunals[0].maps == [m]
    assert loaded.pins == saga.pins
    old = Saga.from_dict(
        {"id": "o", "name": "Old", "tribunals": [{"id": "t", "name": "T"}]}
    )
    assert old.pins == [] and old.maps == [] and old.tribunals[0].maps == []


def test_a_damaged_pin_is_reported_when_loading():
    with pytest.raises(ValueError, match="pin's x"):
        Pin.from_dict({"map_id": "m", "kind": "neighbours", "record_id": "r", "x": "a"})


def test_a_map_with_no_picture_keeps_a_placeholders_shape():
    saga = _saga()
    form = atlas.map_form(saga)
    check = form.validate or (lambda _values: None)
    assert "both a width and a height" in (
        check({"name": "Rhine", "picture": "", "width": 4, "height": None}) or ""
    )
    form.apply(
        {"name": "Rhine", "tribunal": "rhine", "picture": "", "width": 4, "height": 3}
    )
    form.apply({"name": "Alps", "tribunal": None, "picture": ""})
    [rhine] = saga.tribunals[0].maps
    [alps] = saga.maps
    assert (rhine.width, rhine.height) == (4, 3)
    assert (alps.width, alps.height) == atlas.PLACEHOLDER_SHAPE


def test_a_scale_bar_gives_straight_line_distances_in_leagues_and_miles():
    m = AtlasMap("rhine", "The Rhine", width=400, height=200)
    assert atlas.miles_between(m, (0, 0), (1, 1)) is None
    with pytest.raises(ValueError, match="apart"):
        atlas.set_scale(m, (0.1, 0.9), (0.1, 0.9), 10, "leagues")
    # The bar is 100 pixels long and marked 10 leagues: 30 miles.
    atlas.set_scale(m, (0.0, 0.9), (0.25, 0.9), 10, "leagues")
    assert m.scale_miles == 30
    # 300 pixels across and 100 down make 316 pixels: 94.9 miles.
    miles = atlas.miles_between(m, (0.0, 0.0), (0.75, 0.5))
    assert miles == pytest.approx(94.87, abs=0.01)
    assert atlas.distance_words(miles) == "32 leagues (95 miles) in a straight line"
    assert atlas.distance_words(3) == "1 league (3 miles) in a straight line"
    assert atlas.distance_words(1) == "0.3 leagues (1 mile) in a straight line"
    atlas.set_scale(m, (0.0, 0.9), (0.25, 0.9), 12, "miles")
    assert "the bar is 4 leagues (12 miles)" in atlas.scale_words(m)


def test_the_scale_form_sets_the_scale_and_refuses_a_bar_of_nothing():
    m = AtlasMap("rhine", "The Rhine", width=3, height=2)
    form = atlas.scale_form(m, (0.1, 0.5), (0.4, 0.5))
    assert form.validate is not None
    assert form.validate({"length": 0, "unit": "miles"}) == "Give a length above 0."
    form.apply({"length": 20, "unit": "miles"})
    assert (m.scale_bar, m.scale_miles) == ([0.1, 0.5, 0.4, 0.5], 20)


def test_two_records_are_measured_on_a_map_with_a_scale_that_shows_both():
    saga = _saga()
    blank = atlas.add_map(saga, "Unscaled", "rhine", width=4, height=2)
    scaled = atlas.add_map(saga, "Scaled", "rhine", width=4, height=2)
    for m in (blank, scaled):
        atlas.place_pin(saga, m.id, "neighbours", "forest", 0.0, 0.0)
        atlas.place_pin(saga, m.id, "neighbours", "town", 0.75, 0.0)
    assert atlas.miles_apart(saga, ("covenants", "cov"), ("neighbours", "town")) is None
    atlas.set_scale(scaled, (0.0, 1.0), (0.25, 1.0), 1, "leagues")
    # Durenmar is in the forest, so it is measured from the forest's pin.
    assert atlas.miles_apart(
        saga, ("covenants", "cov"), ("neighbours", "town")
    ) == pytest.approx(9)
    assert (
        atlas.miles_apart(saga, ("covenants", "cov"), ("creatures", "nobody")) is None
    )


def test_a_damaged_scale_is_reported_when_loading():
    with pytest.raises(ValueError, match="scale bar"):
        AtlasMap.from_dict({"id": "m", "name": "M", "scale_bar": [1, 2]})
