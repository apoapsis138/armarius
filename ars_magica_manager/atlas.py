"""The Atlas: a saga's maps and the records pinned on them.

A map belongs to its Tribunal (Tribunal.maps), or to the saga when it
belongs to none (Saga.maps); its picture is copied into the maps folder
beside the portraits, named by a hash of its bytes, so two maps of the
same picture share one file and a missing file shows a blank page with
the pins still on it. The pins are the saga's (Saga.pins): a pack's base
pins and the troupe's own, each a record's kind and id at a position
given as fractions of the map's width and height.

Which pins a map shows is worked out each time from the pins and the
records, as Connections are: a record with a pin of its own shows there;
one without shows at the pin of the place it is in, however far out (a
laboratory in its covenant, a regio on its forest); and a mobile
covenant follows the Place of its stop in force, even past a pin of its
own. Nothing derived is kept, so nothing goes stale.

A map's scale is set from its own scale bar (two points and the length
the bar stands for), since a drawn map is to no projection: distances
are straight lines across the picture, never latitude and longitude.

SOURCE: a league is three miles (Grand Grimoire of Hermetic Spells p. 48;
Transforming Mythic Europe p. 108). The Definitive Edition uses leagues
for its ranges and transport spells but gives no length; its travel
times are in miles (p. 408). The Errata says nothing of either.

Pattern: a pin is a references.Ref drawn at a position, so each
front-end opens it with the kind-to-opener dict it already has for
links (Strategy, reduced to a dict). For anyone but the storyguide
(viewing.py: a player, or Player view on a screen the players watch) the
pins are filtered: a secret pin, and every record shown at it, is left
off, and so is a record the players don't know of. A secret pin hides
only itself; an unknown record hides only itself, so a known record at an
unknown place's pin still shows there, without the place's name.
"""

from __future__ import annotations

import hashlib
import math
import shutil
import struct
from collections.abc import Callable, Collection, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import creatures, mobile_covenants, neighbours, storage, viewing
from .commands import Choice, ChooseFile, Confirm, Form, Picked, notes
from .form_spec import DialogField
from .markup import escape
from .models import (
    AtlasMap,
    Covenant,
    Creature,
    Laboratory,
    Neighbour,
    Pin,
    Saga,
    Tribunal,
)
from .references import Ref
from .rules import sites

#: The kinds of picture a map can be.
SUFFIXES = (".png", ".webp", ".jpg", ".jpeg")

#: The kinds of record a pin of its own can place (a Ref's kinds); a
#: laboratory shows at its covenant's or place's pin.
PIN_KINDS: tuple[str, ...] = ("covenants", "neighbours", "creatures")

#: Every kind the Atlas shows, as its filter lists them.
SHOWN_KINDS: tuple[str, ...] = ("covenants", "laboratories", "neighbours", "creatures")
KIND_LABELS: dict[str, str] = {
    "covenants": "Covenants",
    "laboratories": "Laboratories",
    "neighbours": "Neighbours and places",
    "creatures": "Creatures",
}

#: How far a new picture's proportions may stray from the old one's
#: before the form says to check the pins.
_PROPORTION_SLACK = 0.01

#: The forms' own help pages.
HELP_ID = "atlas-map-form"
SCALE_HELP_ID = "atlas-scale"


# -- pictures --


def picture_size(data: bytes) -> tuple[int, int]:
    """A PNG's, JPEG's or WebP's width and height in pixels, read from
    its header; ValueError for anything else."""
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        width, height = struct.unpack(">II", data[16:24])
        return width, height
    if data[:2] == b"\xff\xd8":
        return _jpeg_size(data)
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return _webp_size(data)
    raise ValueError("That isn't a PNG, JPEG or WebP picture.")


def _jpeg_size(data: bytes) -> tuple[int, int]:
    """A JPEG's size, from its first start-of-frame marker."""
    at = 2
    while at + 9 <= len(data):
        if data[at] != 0xFF:
            at += 1
            continue
        marker = data[at + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7 or marker == 0xFF:
            at += 1 if marker == 0xFF else 2
            continue
        (length,) = struct.unpack(">H", data[at + 2 : at + 4])
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack(">HH", data[at + 5 : at + 9])
            return width, height
        at += 2 + length
    raise ValueError("That JPEG has no size in its header.")


def _webp_size(data: bytes) -> tuple[int, int]:
    """A WebP's size, from its first chunk (lossy, lossless or extended)."""
    chunk = data[12:16]
    if chunk == b"VP8 " and len(data) >= 30:
        width, height = struct.unpack("<HH", data[26:30])
        return width & 0x3FFF, height & 0x3FFF
    if chunk == b"VP8L" and len(data) >= 25:
        (bits,) = struct.unpack("<I", data[21:25])
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8X" and len(data) >= 30:
        width = int.from_bytes(data[24:27], "little") + 1
        height = int.from_bytes(data[27:30], "little") + 1
        return width, height
    raise ValueError("That WebP has no size in its header.")


def store_picture(source: Path) -> tuple[str, int, int]:
    """Copy `source` into the maps folder, named by a hash of its bytes
    (kept as it is when that copy is already there); its file name, width
    and height."""
    data = source.read_bytes()
    width, height = picture_size(data)
    suffix = ".jpg" if source.suffix.lower() == ".jpeg" else source.suffix.lower()
    name = hashlib.sha256(data).hexdigest()[:20] + suffix
    folder = storage.maps_dir()
    folder.mkdir(parents=True, exist_ok=True)
    if not (folder / name).is_file():
        shutil.copyfile(source, folder / name)
    return name, width, height


def picture_path(atlas_map: AtlasMap) -> Path | None:
    """The map's picture, if it has one and the file is there."""
    if not atlas_map.picture:
        return None
    found = storage.maps_dir() / atlas_map.picture
    return found if found.is_file() else None


# -- the maps --


def maps(saga: Saga) -> list[tuple[AtlasMap, Tribunal | None]]:
    """Every map in the saga with its Tribunal: the Tribunals' in order,
    then the saga's own."""
    found: list[tuple[AtlasMap, Tribunal | None]] = [
        (m, t) for t in saga.tribunals for m in t.maps
    ]
    return found + [(m, None) for m in saga.maps]


def find_map(saga: Saga, map_id: str | None) -> tuple[AtlasMap, Tribunal | None] | None:
    """The map with this id and its Tribunal, if there is one."""
    return next(((m, t) for m, t in maps(saga) if m.id == map_id), None)


def map_label(atlas_map: AtlasMap, tribunal: Tribunal | None) -> str:
    """How a map is named in a list: its name, and its Tribunal's."""
    return f"{atlas_map.name} ({tribunal.name})" if tribunal else atlas_map.name


def _holder(saga: Saga, tribunal_id: str | None) -> list[AtlasMap]:
    found = saga.tribunal(tribunal_id)
    return found.maps if found is not None else saga.maps


def add_map(
    saga: Saga,
    name: str,
    tribunal_id: str | None = None,
    *,
    picture: str = "",
    width: int = 0,
    height: int = 0,
    credit: str = "",
) -> AtlasMap:
    """A new map of `tribunal_id` (the saga's own for None)."""
    made = AtlasMap(
        storage.generate_unique_id(name, [m.id for m, _t in maps(saga)]),
        name,
        picture,
        width,
        height,
        credit,
    )
    _holder(saga, tribunal_id).append(made)
    return made


def move_map(saga: Saga, atlas_map: AtlasMap, tribunal_id: str | None) -> None:
    """Make the map `tribunal_id`'s (the saga's own for None)."""
    for _m, tribunal in maps(saga):
        held = tribunal.maps if tribunal is not None else saga.maps
        if atlas_map in held:
            held.remove(atlas_map)
            break
    _holder(saga, tribunal_id).append(atlas_map)


def remove_map(saga: Saga, atlas_map: AtlasMap) -> None:
    """Take the map out of the saga, and every pin on it. Its picture
    stays in the maps folder, where another saga's map may share it."""
    for _m, tribunal in maps(saga):
        held = tribunal.maps if tribunal is not None else saga.maps
        if atlas_map in held:
            held.remove(atlas_map)
            break
    saga.pins = [pin for pin in saga.pins if pin.map_id != atlas_map.id]


# -- the records --


def record(saga: Saga, kind: str, record_id: str | None) -> Any | None:
    """The record a pin names, if it is still in the saga."""
    lookups: dict[str, Callable[[str | None], Any | None]] = {
        "covenants": saga.covenant,
        "neighbours": saga.neighbour,
        "creatures": saga.creature,
        "laboratories": saga.laboratory,
    }
    lookup = lookups.get(kind)
    return lookup(record_id) if lookup is not None else None


def _records(saga: Saga) -> Iterator[tuple[str, Any]]:
    yield from (("covenants", c) for c in saga.covenants)
    yield from (("laboratories", lab) for lab in saga.laboratories)
    yield from (("neighbours", n) for n in saga.neighbours)
    yield from (("creatures", c) for c in saga.creatures)


def concept(kind: str, found: Any) -> str:
    """The artwork concept a record's pin shows: a covenant's turret, a
    ruin, a neighbour's kind, a creature's realm."""
    if isinstance(found, Covenant):
        return "covenant"
    if isinstance(found, Neighbour):
        return neighbours.icon_concept(found)
    if isinstance(found, Creature):
        return creatures.icon_concept(found)
    return "laboratory" if kind == "laboratories" else "place"


def kind_word(found: Any) -> str:
    """What a pin's record is, in a word or two: a covenant, a
    neighbour's kind (a Place, a Town...), a creature, a laboratory."""
    if isinstance(found, Covenant):
        return "Covenant"
    if isinstance(found, Neighbour):
        return neighbours.kind_of(found).name
    if isinstance(found, Creature):
        return "Creature"
    return "Laboratory" if isinstance(found, Laboratory) else ""


def summary(found: Any) -> str:
    """The line a pin's hover shows under its name."""
    if isinstance(found, Covenant | Neighbour):
        return found.summary
    if isinstance(found, Creature):
        return found.appearance
    if isinstance(found, Laboratory):
        return found.location
    return ""


def _parent(saga: Saga, found: Any) -> tuple[str, Any] | None:
    """The record `found` sits in: a laboratory's place or covenant, a
    covenant's, neighbour's or creature's place."""
    if isinstance(found, Laboratory):
        if found.place_id:
            place = saga.neighbour(found.place_id)
            if place is not None:
                return "neighbours", place
        covenant = saga.covenant(found.covenant_id)
        return ("covenants", covenant) if covenant is not None else None
    if isinstance(found, Covenant | Neighbour | Creature) and found.place_id:
        place = saga.neighbour(found.place_id)
        return ("neighbours", place) if place is not None else None
    return None


def _travelling(saga: Saga, found: Any) -> Neighbour | None:
    """A mobile covenant's Place now: its stop in force's."""
    if not isinstance(found, Covenant) or not mobile_covenants.shows(found):
        return None
    stop = sites.covenant_stop(saga, found)
    return sites.place(saga, stop.place_id) if stop is not None else None


@dataclass(frozen=True)
class ShownPin:
    """A record as a map shows it: the Ref that opens it, where it is
    (fractions of the map's width and height), its symbol's concept and
    hover line, its own pin (None when it shows at another record's), and
    the record it shows at ("" at its own pin)."""

    ref: Ref
    x: float
    y: float
    concept: str
    summary: str
    pin: Pin | None
    at: str = ""

    @property
    def secret(self) -> bool:
        return self.pin is not None and self.pin.secret


def shown_pins(
    saga: Saga,
    map_id: str,
    *,
    table: bool | None = None,
    kinds: Collection[str] | None = None,
) -> list[ShownPin]:
    """The records `map_id` shows, each where it is: at its own pin, a
    mobile covenant at its stop's Place, the rest at the pin of the place
    they are in. With `table` (by default, whenever anyone but the
    storyguide is looking), a secret pin and every record shown at it are
    left off, and so is a record the players don't know of. `kinds`
    narrows them to those kinds of record."""
    if table is None:
        table = not viewing.storyguide_reads()
    looking = viewing.current()

    def secret_to_me(pin: Pin) -> bool:
        """A secret pin hidden here: from the table, and from a storyguide
        whose record it isn't (ADR 0015)."""
        if not pin.secret:
            return False
        if table:
            return True
        return not viewing.ref_held(saga, Ref(pin.kind, pin.record_id, ""), looking)

    def hidden(found: Any) -> bool:
        return (table and not viewing.is_known(found)) or not viewing.readable(
            looking, found, saga
        )

    own = {
        (pin.kind, pin.record_id): pin
        for pin in saga.pins
        if pin.map_id == map_id and not pin.hidden and not secret_to_me(pin)
    }

    def where(kind: str, found: Any, seen: frozenset[str]) -> tuple[Pin, Any] | None:
        """The pin `found` shows at, and the record it belongs to."""
        if found.id in seen:
            return None
        seen |= {found.id}
        moving = _travelling(saga, found)
        if moving is not None:
            return where("neighbours", moving, seen)
        pin = own.get((kind, found.id))
        if pin is not None:
            return pin, found
        parent = _parent(saga, found)
        return where(*parent, seen) if parent is not None else None

    shown: list[ShownPin] = []
    for kind, found in _records(saga):
        if kinds is not None and kind not in kinds:
            continue
        if hidden(found):
            continue
        located = where(kind, found, frozenset())
        if located is None:
            continue
        pin, host = located
        mine = host is found
        shown.append(
            ShownPin(
                Ref(kind, found.id, found.name),
                pin.x,
                pin.y,
                concept(kind, found),
                summary(found),
                pin if mine else None,
                "" if mine or hidden(host) else host.name,
            )
        )
    return shown


def maps_showing(saga: Saga, kind: str, record_id: str) -> list[AtlasMap]:
    """The maps a record shows on, for its page's Show on Map."""
    return [
        m
        for m, _t in maps(saga)
        if any(
            s.ref.kind == kind and s.ref.id == record_id
            for s in shown_pins(saga, m.id, kinds=(kind,))
        )
    ]


# -- the scale --

#: Miles in a league (see SOURCE).
LEAGUE_MILES = 3.0
#: The units a scale bar's length is typed in, and their miles.
UNITS: dict[str, float] = {"leagues": LEAGUE_MILES, "miles": 1.0}

Point = tuple[float, float]


def has_scale(atlas_map: AtlasMap) -> bool:
    return len(atlas_map.scale_bar) == 4 and atlas_map.scale_miles > 0


def _span(atlas_map: AtlasMap, a: Point, b: Point) -> float:
    """How far apart two points of the map are, in the picture's own
    units (its shape: its pixels, or a placeholder's sides)."""
    width, height = _shape(atlas_map)
    return math.hypot((a[0] - b[0]) * width, (a[1] - b[1]) * height)


def set_scale(
    atlas_map: AtlasMap, a: Point, b: Point, length: float, unit: str
) -> None:
    """The map's scale: its bar runs from `a` to `b` and stands for
    `length` `unit`s."""
    if length <= 0 or unit not in UNITS:
        raise ValueError("A scale bar's length should be above 0, in leagues or miles.")
    if _span(atlas_map, a, b) == 0:
        raise ValueError("A scale bar's two ends should be apart.")
    atlas_map.scale_bar = [a[0], a[1], b[0], b[1]]
    atlas_map.scale_miles = length * UNITS[unit]


def miles_between(atlas_map: AtlasMap, a: Point, b: Point) -> float | None:
    """The straight-line miles between two points of the map; None while
    it has no scale."""
    if not has_scale(atlas_map):
        return None
    x1, y1, x2, y2 = atlas_map.scale_bar
    bar = _span(atlas_map, (x1, y1), (x2, y2))
    return _span(atlas_map, a, b) / bar * atlas_map.scale_miles


def _figure(value: float) -> str:
    return f"{value:.1f}".rstrip("0").rstrip(".") if value < 10 else f"{value:.0f}"


def distance_words(miles: float) -> str:
    """A distance as the Atlas says it: leagues, then miles."""
    leagues = miles / LEAGUE_MILES
    league_word = "league" if _figure(leagues) == "1" else "leagues"
    mile_word = "mile" if _figure(miles) == "1" else "miles"
    return (
        f"{_figure(leagues)} {league_word} ({_figure(miles)} {mile_word}) "
        "in a straight line"
    )


def scale_words(atlas_map: AtlasMap) -> str:
    """What the map's scale bar stands for."""
    if not has_scale(atlas_map):
        return "No scale yet: Set Scale measures the map's scale bar."
    leagues = atlas_map.scale_miles / LEAGUE_MILES
    return (
        f"Scale: the bar is {_figure(leagues)} leagues "
        f"({_figure(atlas_map.scale_miles)} miles)."
    )


def _spot(saga: Saga, map_id: str, kind: str, record_id: str) -> Point | None:
    shown = next(
        (s for s in shown_pins(saga, map_id, kinds=(kind,)) if s.ref.id == record_id),
        None,
    )
    return (shown.x, shown.y) if shown is not None else None


def miles_apart(saga: Saga, a: tuple[str, str], b: tuple[str, str]) -> float | None:
    """The straight-line miles between two records (each a Ref's kind and
    id), on the first map with a scale that shows both; None when none
    does."""
    for atlas_map, _tribunal in maps(saga):
        if not has_scale(atlas_map):
            continue
        here, there = _spot(saga, atlas_map.id, *a), _spot(saga, atlas_map.id, *b)
        if here is not None and there is not None:
            return miles_between(atlas_map, here, there)
    return None


def scale_fields(atlas_map: AtlasMap) -> list[DialogField]:
    """Set Scale's form: what the bar just measured stands for."""
    leagues = atlas_map.scale_miles / LEAGUE_MILES if has_scale(atlas_map) else None
    return [
        DialogField(
            "length",
            "The bar is",
            "optfloat",
            leagues,
            required=True,
            hint="The length its scale bar is marked with.",
        ),
        DialogField(
            "unit",
            "In",
            "select",
            "leagues",
            options=[("Leagues (3 miles each)", "leagues"), ("Miles", "miles")],
        ),
    ]


def scale_form(atlas_map: AtlasMap, a: Point, b: Point) -> Form:
    """After the bar's two ends are clicked: how long it is."""

    def problem(values: dict[str, Any]) -> str | None:
        length = values.get("length")
        return None if length is not None and length > 0 else "Give a length above 0."

    return Form(
        f"Scale of {escape(atlas_map.name)}",
        lambda: scale_fields(atlas_map),
        lambda values: set_scale(
            atlas_map, a, b, values["length"], values.get("unit") or "leagues"
        ),
        validate=problem,
        help_id=SCALE_HELP_ID,
    )


# -- the pins --


def pin_of(saga: Saga, map_id: str, kind: str, record_id: str) -> Pin | None:
    """The record's pin on the map (a hidden one too), if it has one."""
    return next(
        (
            pin
            for pin in saga.pins
            if pin.map_id == map_id and pin.kind == kind and pin.record_id == record_id
        ),
        None,
    )


def place_pin(
    saga: Saga, map_id: str, kind: str, record_id: str, x: float, y: float
) -> Pin:
    """Put the record on the map at (x, y): its pin moved there, a pack's
    pin hidden from the saga shown again, or a new pin."""
    x, y = min(1.0, max(0.0, x)), min(1.0, max(0.0, y))
    pin = pin_of(saga, map_id, kind, record_id)
    if pin is None:
        pin = Pin(map_id, kind, record_id, x, y)
        saga.pins.append(pin)
    pin.x, pin.y, pin.hidden = x, y, False
    return pin


def remove_pin(saga: Saga, pin: Pin) -> None:
    """Take the pin off its map: a pack's is hidden from the saga, so the
    next import of the pack doesn't bring it back; the troupe's goes."""
    if pin.from_pack:
        pin.hidden = True
    elif pin in saga.pins:
        saga.pins.remove(pin)


def pinnable(saga: Saga, map_id: str) -> list[Choice]:
    """The records Place on Map offers: those that can have a pin of their
    own and have none showing on the map, each with its kind."""
    placed = {
        (pin.kind, pin.record_id)
        for pin in saga.pins
        if pin.map_id == map_id and not pin.hidden
    }
    found: list[Choice] = []
    for kind, held in _records(saga):
        if kind not in PIN_KINDS or (kind, held.id) in placed:
            continue
        label = KIND_LABELS[kind]
        if isinstance(held, Neighbour):
            label = neighbours.kind_of(held).name
        found.append(
            Choice(
                escape(held.name),
                Ref(kind, held.id, held.name),
                escape(label),
                search=label,
                facets=(("Kind", KIND_LABELS[kind]),),
            )
        )
    return found


# -- the map form --


def _picture_name(value: object) -> str:
    return Path(str(value)).name if value else "None chosen"


def _choose_picture(_current: object) -> ChooseFile:
    home = Path.home()
    start = home / "Pictures" if (home / "Pictures").is_dir() else home
    return ChooseFile(
        "A map's picture",
        SUFFIXES[0],
        start,
        lambda chosen: Picked(str(chosen)),
        more=SUFFIXES[1:],
    )


def map_fields(saga: Saga, atlas_map: AtlasMap | None = None) -> list[DialogField]:
    """The map form's fields: its name, its Tribunal, its picture and its
    credit line."""
    held = find_map(saga, atlas_map.id) if atlas_map is not None else None
    tribunal = held[1] if held is not None else None
    return [
        DialogField(
            "name", "Name", "text", atlas_map.name if atlas_map else "", required=True
        ),
        DialogField(
            "tribunal",
            "Tribunal",
            "select",
            tribunal.id if tribunal else None,
            options=[(t.name, t.id) for t in saga.tribunals],
            allow_blank=True,
            hint="Blank: the saga's own map, for a region with no Tribunal.",
        ),
        DialogField(
            "picture",
            "Picture",
            "picker",
            atlas_map.picture if atlas_map else "",
            allow_blank=True,
            display=_picture_name,
            choose=_choose_picture,
            hint="A PNG, WebP or JPEG; it is copied into the maps folder.",
        ),
        DialogField(
            "width",
            "Placeholder width",
            "optint",
            _shape(atlas_map)[0],
            hint="With no picture yet, a placeholder is drawn in the shape of "
            "the map to come (3 by 2, or its size in pixels), so the pins keep "
            "their places when the picture arrives.",
            show_if=lambda values: not values.get("picture"),
        ),
        DialogField(
            "height",
            "Placeholder height",
            "optint",
            _shape(atlas_map)[1],
            show_if=lambda values: not values.get("picture"),
        ),
        DialogField(
            "credit",
            "Credit",
            "text",
            atlas_map.credit if atlas_map else "",
            placeholder="Who drew it, and its licence",
        ),
    ]


#: A placeholder's shape when none is given: wider than tall, as most
#: maps of a region are.
PLACEHOLDER_SHAPE = (3, 2)


def _shape(atlas_map: AtlasMap | None) -> tuple[int, int]:
    """The shape the map's placeholder is drawn in: its size, else 3 by 2."""
    if atlas_map is not None and atlas_map.width and atlas_map.height:
        return atlas_map.width, atlas_map.height
    return PLACEHOLDER_SHAPE


def _new_picture(atlas_map: AtlasMap | None, value: object) -> Path | None:
    """The picture file the form chose, when it is a new one."""
    if not value or (atlas_map is not None and value == atlas_map.picture):
        return None
    return Path(str(value))


def map_problem(atlas_map: AtlasMap | None, values: dict[str, Any]) -> str | None:
    """Why the form can't save: a chosen file that can't be read as a
    picture, or a placeholder given only one of its sides."""
    chosen = _new_picture(atlas_map, values.get("picture"))
    if chosen is None:
        if values.get("picture"):
            return None
        width, height = values.get("width"), values.get("height")
        if (width is None) != (height is None) or any(
            n is not None and n < 1 for n in (width, height)
        ):
            return "Give the placeholder both a width and a height, above 0."
        return None
    try:
        picture_size(chosen.read_bytes())
    except OSError:
        return f"{escape(chosen.name)} can't be read."
    except ValueError as error:
        return escape(str(error))
    return None


def _apply_map(
    saga: Saga, atlas_map: AtlasMap | None, values: dict[str, Any]
) -> list[str]:
    tribunal_id = values.get("tribunal") or None
    if atlas_map is None:
        atlas_map = add_map(saga, values["name"], tribunal_id)
    else:
        atlas_map.name = values["name"]
        move_map(saga, atlas_map, tribunal_id)
    atlas_map.credit = values.get("credit") or ""
    said: list[str] = []
    chosen = _new_picture(atlas_map, values.get("picture"))
    if chosen is not None:
        old = (atlas_map.width, atlas_map.height)
        atlas_map.picture, atlas_map.width, atlas_map.height = store_picture(chosen)
        if _strays(old, (atlas_map.width, atlas_map.height)) and any(
            pin.map_id == atlas_map.id for pin in saga.pins
        ):
            said.append(
                "The new picture's proportions differ from the old one's: the "
                "pins keep their places across it, so check them."
            )
    elif not values.get("picture"):
        width, height = values.get("width"), values.get("height")
        atlas_map.picture = ""
        atlas_map.width, atlas_map.height = (
            (width, height) if width and height else PLACEHOLDER_SHAPE
        )
    return notes(*said)


def _strays(old: tuple[int, int], new: tuple[int, int]) -> bool:
    if not all(old) or not all(new):
        return False
    return abs(old[0] / old[1] - new[0] / new[1]) > _PROPORTION_SLACK * (
        old[0] / old[1]
    )


def map_form(saga: Saga, atlas_map: AtlasMap | None = None) -> Form:
    """Add a map, or edit `atlas_map`."""
    return Form(
        f"Edit {escape(atlas_map.name)}" if atlas_map else "New Map",
        lambda: map_fields(saga, atlas_map),
        lambda values: _apply_map(saga, atlas_map, values),
        validate=lambda values: map_problem(atlas_map, values),
        save_label="Save" if atlas_map else "Add",
        help_id=HELP_ID,
    )


def remove_map_step(saga: Saga, atlas_map: AtlasMap) -> Confirm:
    """Remove the map, after asking."""
    count = sum(1 for pin in saga.pins if pin.map_id == atlas_map.id)
    pins = f" and its {count} pin{'s' if count != 1 else ''}" if count else ""
    return Confirm(
        f"Remove the map {escape(atlas_map.name)}{pins}? Its records stay in the saga.",
        lambda: remove_map(saga, atlas_map),
        yes_label="Remove",
    )
