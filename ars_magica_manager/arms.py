"""Arms: a covenant's (or a lord's, town's, church's or faction's)
shield, a value object of six choices (how the field is divided, its two
tinctures, the charge, how many of it and the charge's tincture) and a
motto. The blazon is written
from them, a colour laid on a colour (or a metal on a metal) is warned
of, and the shield's shapes are given here as plain geometry, so each
front-end paints the same shield its own way: the desktop with painter
paths, the terminal in half-blocks."""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from . import svg_paths
from .artwork import CHARGE_DRAWINGS
from .commands import Form
from .form_spec import DialogField
from .markup import escape

#: The tinctures, metals first, then the colours, then the fur. Each
#: front-end's themes give the colour each is painted in.
TINCTURES = ("Or", "Argent", "Gules", "Azure", "Vert", "Sable", "Purpure", "Ermine")
METALS = frozenset({"Or", "Argent"})

#: A fur is neither metal nor colour, so the rule of tincture leaves it
#: alone. It is painted as its ground strewn with its spots: ermine is
#: argent with sable tails.
FURS: dict[str, tuple[str, str]] = {"Ermine": ("Argent", "Sable")}

DIVISIONS = (
    "Plain",
    "Per pale",
    "Per fess",
    "Per bend",
    "Quarterly",
    "Per chevron",
    "Bendy",
    "Checky",
)

#: The charges, by name, each with how the blazon names one of it.
CHARGES: dict[str, str] = {
    "Tower": "a tower",
    "Book": "a book",
    "Key": "a key",
    "Star": "a star",
    "Sword": "a sword",
    "Crown": "a crown",
    "Cross": "a cross",
    "Crescent": "a crescent",
    "Tree": "a tree",
    "Chalice": "a chalice",
    "Eagle": "an eagle",
    "Lion": "a lion",
    "Lion, tail knotted": "a lion queue-nowed",
    "Wheel": "a wheel",
    "Fleur-de-lis": "a fleur-de-lis",
    "Bend": "a bend",
}

#: The charges that are ordinaries: drawn across the whole shield, and
#: borne once.
ORDINARIES = frozenset({"Bend"})

#: How many of the charge a shield may bear, and the word for each.
COUNTS: dict[int, str] = {1: "one", 2: "two", 3: "three"}

#: The charges whose plural isn't the word with an s.
_PLURALS = {
    "Cross": "crosses",
    "Fleur-de-lis": "fleurs-de-lis",
    "Lion, tail knotted": "lions queue-nowed",
}

#: The kinds of neighbour that bear arms: a church's are its bishop's or
#: abbey's.
BEARERS = frozenset({"lord", "town", "church", "faction"})


@dataclass(frozen=True)
class Arms:
    """A shield: `field` alone for a plain one, or divided with `second`;
    an optional `charge` in `charge_tincture`, borne `count` times; and a
    motto."""

    field: str = "Azure"
    division: str = "Plain"
    second: str = "Argent"
    charge: str = ""
    charge_tincture: str = "Or"
    motto: str = ""
    count: int = 1

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Arms | None:
        """The arms kept on a record; None for a record with none."""
        if not data or data.get("field") not in TINCTURES:
            return None
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        if known.get("count") not in COUNTS or known.get("charge") in ORDINARIES:
            known["count"] = 1
        return cls(**known)

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @property
    def divided(self) -> bool:
        return self.division != "Plain"

    def tinctures(self) -> tuple[str, ...]:
        """The field's tinctures: one, or two when it is divided."""
        return (self.field, self.second) if self.divided else (self.field,)


def arms_of(record: Any) -> Arms | None:
    return Arms.from_dict(getattr(record, "arms", None))


def bears_arms(record: Any) -> bool:
    """Whether `record` can bear arms: a covenant, or a lord, town, church
    or faction."""
    kind = getattr(record, "kind", None)
    return hasattr(record, "arms") and (kind is None or kind in BEARERS)


def charge_words(charge: str, count: int) -> str:
    """ "a tower", "three crowns"."""
    if count <= 1:
        return CHARGES[charge]
    plural = _PLURALS.get(charge, f"{charge.lower()}s")
    return f"{COUNTS.get(count, str(count))} {plural}"


def blazon(arms: Arms) -> str:
    """ "Per bend azure and argent, a tower or"; "Gules, three crowns or"."""
    if arms.divided:
        words = f"{arms.division} {arms.field.lower()} and {arms.second.lower()}"
    else:
        words = arms.field
    if arms.charge in CHARGES:
        words += (
            f", {charge_words(arms.charge, arms.count)} {arms.charge_tincture.lower()}"
        )
    return words


def _kind(tincture: str) -> str:
    if tincture in FURS:
        return "fur"
    return "metal" if tincture in METALS else "colour"


def warning(arms: Arms) -> str:
    """What a herald would say against the arms, or "": a charge in the
    tincture of the field it lies on is lost against it, and a colour on
    a colour (or a metal on a metal) breaks the rule of tincture, which
    is allowed but frowned on."""
    if arms.divided and arms.field == arms.second:
        return (
            f"Divided {arms.field.lower()} and {arms.field.lower()} is a plain field."
        )
    if arms.charge not in CHARGES:
        return ""
    on = arms.charge_tincture
    for ground in arms.tinctures():
        if on == ground:
            return (
                f"{on} on {ground.lower()}: the {arms.charge.lower()} is lost "
                "against the field."
            )
    for ground in arms.tinctures():
        if _kind(on) == _kind(ground) != "fur":
            kind = _kind(on)
            return (
                f"{on} on {ground.lower()} is {kind} on {kind}: heralds would "
                "frown, but it's allowed."
            )
    return ""


# -------------------------------------------------------------- geometry

#: The shield's height, its width being 1.
HEIGHT = 1.2

Point = tuple[float, float]

#: A square on the shield: its top left corner and its side.
Box = tuple[float, float, float]


@dataclass(frozen=True)
class Shape:
    """A polygon, a circle (`radius` set, `points` its one centre), or a
    drawing of several rings filled even-odd (`rings` set: a traced
    outline, its inner rings cut out of it); a hole cuts out of the
    solid shapes before it, so a shape after it (a wheel's spokes inside
    its rim) is whole."""

    points: tuple[Point, ...]
    radius: float = 0.0
    hole: bool = False
    rings: tuple[tuple[Point, ...], ...] = ()

    def contains(self, x: float, y: float) -> bool:
        if self.radius:
            cx, cy = self.points[0]
            return (x - cx) ** 2 + (y - cy) ** 2 <= self.radius**2
        if self.rings:
            return sum(_inside(ring, x, y) for ring in self.rings) % 2 == 1
        return _inside(self.points, x, y)


def drawing(d: str, box: tuple[float, float, float, float]) -> Shape:
    """A charge drawn as SVG path data, its viewBox `box` fitted to the
    unit square."""
    return Shape((), rings=tuple(svg_paths.fitted(d, box)))


def layers(path: Path) -> dict[str, Shape]:
    """A charge file cleaned by tools/clean_charge.py: its layers by id
    (body, lines, armed), each a drawing fitted to the unit square by the
    file's viewBox."""
    text = path.read_text(encoding="utf-8")
    found = re.search(r'viewBox="([^"]+)"', text)
    if found is None:
        raise ValueError(f"{path.name} has no viewBox")
    left, top, width, height = (float(v) for v in found.group(1).split())
    return {
        name: drawing(d, (left, top, width, height))
        for name, d in re.findall(r'<path id="(\w+)" d="([^"]+)"', text)
    }


def _inside(points: Sequence[Point], x: float, y: float) -> bool:
    """Whether (x, y) lies in the polygon (even-odd)."""
    inside = False
    j = len(points) - 1
    for i, (xi, yi) in enumerate(points):
        xj, yj = points[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def _rect(x0: float, y0: float, x1: float, y1: float, hole: bool = False) -> Shape:
    return Shape(((x0, y0), (x1, y0), (x1, y1), (x0, y1)), hole=hole)


def _circle(cx: float, cy: float, r: float, hole: bool = False) -> Shape:
    return Shape(((cx, cy),), r, hole)


def _poly(*points: Point) -> Shape:
    return Shape(tuple(points))


def shield_outline(steps: int = 12) -> tuple[Point, ...]:
    """The shield's edge: straight sides, curving to a point at the
    base."""
    shoulder = HEIGHT * 0.5
    right = []
    for i in range(steps + 1):
        t = i / steps
        # A quadratic curve from the right shoulder to the point.
        x = (1 - t) ** 2 * 1 + 2 * (1 - t) * t * 1 + t**2 * 0.5
        y = (1 - t) ** 2 * shoulder + 2 * (1 - t) * t * (HEIGHT * 0.88) + t**2 * HEIGHT
        right.append((x, y))
    left = [(1 - x, y) for x, y in reversed(right[:-1])]
    return ((0.0, 0.0), (1.0, 0.0), *right, *left)


#: The part of the shield in the second tincture, by division.
_FESS = HEIGHT * 0.45
DIVISION_AREAS: dict[str, tuple[Shape, ...]] = {
    "Plain": (),
    "Per pale": (_rect(0.5, 0, 1, HEIGHT),),
    "Per fess": (_rect(0, _FESS, 1, HEIGHT),),
    "Per bend": (_poly((0, 0), (1, HEIGHT), (0, HEIGHT)),),
    "Quarterly": (_rect(0.5, 0, 1, _FESS), _rect(0, _FESS, 0.5, HEIGHT)),
    "Per chevron": (
        _poly(
            (0, HEIGHT * 0.9),
            (0.5, HEIGHT * 0.4),
            (1, HEIGHT * 0.9),
            (1, HEIGHT),
            (0, HEIGHT),
        ),
    ),
}


def _band(c0: float, c1: float) -> Shape:
    """The strip of the shield between two lines parallel to its bend
    (top left to bottom right), y - HEIGHT x = c0 and = c1, running past
    the shield's edges."""
    return _poly(
        (-1, c0 - HEIGHT),
        (2, c0 + 2 * HEIGHT),
        (2, c1 + 2 * HEIGHT),
        (-1, c1 - HEIGHT),
    )


#: Bendy of six: every other of six bends across the shield.
_BEND_STEP = 2 * HEIGHT / 6
DIVISION_AREAS["Bendy"] = tuple(
    _band(-HEIGHT + i * _BEND_STEP, -HEIGHT + (i + 1) * _BEND_STEP)
    for i in range(1, 6, 2)
)

#: Checky: squares a fifth of the shield wide, alternating.
_CHECK = 0.2
DIVISION_AREAS["Checky"] = tuple(
    _rect(col * _CHECK, row * _CHECK, (col + 1) * _CHECK, (row + 1) * _CHECK)
    for row in range(round(HEIGHT / _CHECK))
    for col in range(5)
    if (row + col) % 2
)

#: A drawn charge's line work (painted in `line_tincture`) and its claws
#: and tongue (in `armed_tincture`), over its silhouette, by charge.
CHARGE_LINES: dict[str, Shape | None] = {}
CHARGE_ARMED: dict[str, Shape | None] = {}


def line_tincture(arms: Arms) -> str:
    """A charge's line work is sable, or argent on a sable charge."""
    return "Argent" if arms.charge_tincture == "Sable" else "Sable"


def armed_tincture(arms: Arms) -> str:
    """A beast's claws and tongue are gules, or azure where gules would
    vanish (a gules beast, or a gules field)."""
    return "Azure" if "Gules" in (arms.charge_tincture, arms.field) else "Gules"


#: Each charge's shapes, in a unit square.
CHARGE_SHAPES: dict[str, tuple[Shape, ...]] = {
    "Book": (
        _poly((0.04, 0.2), (0.47, 0.3), (0.47, 0.9), (0.04, 0.8)),
        _poly((0.53, 0.3), (0.96, 0.2), (0.96, 0.8), (0.53, 0.9)),
    ),
    "Key": (
        _circle(0.5, 0.24, 0.22),
        _circle(0.5, 0.24, 0.1, hole=True),
        _rect(0.44, 0.44, 0.56, 1.0),
        _rect(0.56, 0.74, 0.74, 0.82),
        _rect(0.56, 0.88, 0.74, 0.96),
    ),
    "Sword": (
        _poly((0.5, 0.0), (0.57, 0.1), (0.57, 0.68), (0.43, 0.68), (0.43, 0.1)),
        _rect(0.24, 0.68, 0.76, 0.76),
        _rect(0.45, 0.76, 0.55, 0.9),
        _circle(0.5, 0.94, 0.07),
    ),
    "Crown": (
        _poly(
            (0.08, 0.85),
            (0.08, 0.3),
            (0.29, 0.55),
            (0.5, 0.2),
            (0.71, 0.55),
            (0.92, 0.3),
            (0.92, 0.85),
        ),
    ),
    "Chalice": (
        _poly(
            (0.18, 0.08),
            (0.82, 0.08),
            (0.72, 0.45),
            (0.56, 0.56),
            (0.56, 0.8),
            (0.74, 0.88),
            (0.74, 0.97),
            (0.26, 0.97),
            (0.26, 0.88),
            (0.44, 0.8),
            (0.44, 0.56),
            (0.28, 0.45),
        ),
    ),
}


def _spoke(angle: float, inner: float, outer: float, width: float) -> Shape:
    """A bar from the hub to the rim of a wheel centred on (0.5, 0.5)."""
    dx, dy = math.cos(angle), math.sin(angle)
    px, py = -dy * width / 2, dx * width / 2
    return _poly(
        (0.5 + dx * inner + px, 0.5 + dy * inner + py),
        (0.5 + dx * outer + px, 0.5 + dy * outer + py),
        (0.5 + dx * outer - px, 0.5 + dy * outer - py),
        (0.5 + dx * inner - px, 0.5 + dy * inner - py),
    )


# The charges drawn from Wikimedia Commons files (see NOTICE.md): each
# silhouette in the charge's tincture, its line work and any claws and
# tongue painted over it.
for _name, _path in CHARGE_DRAWINGS.items():
    _drawn = layers(_path)
    CHARGE_SHAPES[_name] = (_drawn["body"],)
    CHARGE_LINES[_name] = _drawn.get("lines")
    CHARGE_ARMED[_name] = _drawn.get("armed")

# A wheel of six spokes (the wheel of Mainz).
CHARGE_SHAPES["Wheel"] = (
    _circle(0.5, 0.5, 0.46),
    _circle(0.5, 0.5, 0.36, hole=True),
    *(_spoke(i * math.pi / 3, 0.0, 0.4, 0.1) for i in range(6)),
    _circle(0.5, 0.5, 0.12),
)


def _bend(half_width: float) -> Shape:
    """A band along the line from the top left corner to the bottom
    right, in the shield's own coordinates."""
    length = math.hypot(1, HEIGHT)
    nx, ny = -HEIGHT / length * half_width, 1 / length * half_width
    start, end = (-0.2, -0.2 * HEIGHT), (1.2, 1.2 * HEIGHT)
    return _poly(
        (start[0] + nx, start[1] + ny),
        (end[0] + nx, end[1] + ny),
        (end[0] - nx, end[1] - ny),
        (start[0] - nx, start[1] - ny),
    )


#: An ordinary's shapes are in the shield's coordinates (its width 1),
#: not a charge's unit square.
CHARGE_SHAPES["Bend"] = (_bend(0.14),)

#: An ermine tail: three dots over a spreading tail, in a unit square.
ERMINE_SPOT: tuple[Shape, ...] = (
    _circle(0.5, 0.12, 0.12),
    _circle(0.24, 0.3, 0.11),
    _circle(0.76, 0.3, 0.11),
    _poly(
        (0.5, 0.3), (0.62, 0.62), (0.86, 1.0), (0.5, 0.82), (0.14, 1.0), (0.38, 0.62)
    ),
)


def _fur_boxes() -> tuple[Box, ...]:
    """Where a fur's spots sit, in the shield's coordinates: rows a fifth
    of the shield apart, every other row shifted half a step."""
    step, side = 0.25, 0.11
    boxes = []
    for row in range(round(HEIGHT / step) + 1):
        shift = step / 2 if row % 2 else 0.0
        for col in range(5):
            x = shift + col * step + (step - side) / 2
            if x + side <= 1:
                boxes.append((x, row * step + 0.05, side))
    return tuple(boxes)


#: Where one charge sits on the shield: its square's corner and side.
CHARGE_BOX = (0.21, HEIGHT * 0.15, 0.58)

#: Where the charges sit by their count: two side by side, three as two
#: and one, as heralds place them.
CHARGE_BOXES: dict[int, tuple[Box, ...]] = {
    1: (CHARGE_BOX,),
    2: ((0.07, HEIGHT * 0.2, 0.4), (0.53, HEIGHT * 0.2, 0.4)),
    3: (
        (0.09, HEIGHT * 0.06, 0.36),
        (0.55, HEIGHT * 0.06, 0.36),
        (0.32, HEIGHT * 0.46, 0.36),
    ),
}


#: An ordinary's one box: the whole shield.
WHOLE_SHIELD: Box = (0.0, 0.0, 1.0)

#: Where a fur's spots sit.
FUR_BOXES = _fur_boxes()


def charge_boxes(arms: Arms) -> tuple[Box, ...]:
    """The squares `arms`' charges are drawn in: the whole shield for an
    ordinary."""
    if arms.charge in ORDINARIES:
        return (WHOLE_SHIELD,)
    return CHARGE_BOXES.get(arms.count, CHARGE_BOXES[1])


def _in_shapes(shapes: Sequence[Shape], box: Box, x: float, y: float) -> bool:
    left, top, side = box
    u, v = (x - left) / side, (y - top) / side
    # A charge's square is a unit one; an ordinary's box runs the
    # shield's full height.
    if not (0 <= u <= 1 and 0 <= v <= HEIGHT):
        return False
    inside = False
    for shape in shapes:
        if shape.contains(u, v):
            inside = not shape.hole
    return inside


def painted(tincture: str, x: float, y: float) -> str:
    """The plain tincture painted at (x, y) of a field or charge in
    `tincture`: a fur's ground, or its spot colour on a spot."""
    if tincture not in FURS:
        return tincture
    ground, spots = FURS[tincture]
    on_spot = any(_in_shapes(ERMINE_SPOT, box, x, y) for box in FUR_BOXES)
    return spots if on_spot else ground


def tincture_at(arms: Arms, x: float, y: float) -> str | None:
    """The plain tincture painted at (x, y) on the shield (a fur resolved
    to its ground or spots), or None off it."""
    if not _inside(shield_outline(), x, y):
        return None
    if arms.charge in CHARGE_SHAPES and any(
        _in_shapes(CHARGE_SHAPES[arms.charge], box, x, y) for box in charge_boxes(arms)
    ):
        return painted(arms.charge_tincture, x, y)
    if any(s.contains(x, y) for s in DIVISION_AREAS.get(arms.division, ())):
        return painted(arms.second, x, y)
    return painted(arms.field, x, y)


def pixels(arms: Arms, width: int) -> list[list[str | None]]:
    """The shield as rows of `width` square pixels, each its tincture (None
    off the shield), sampled at each pixel's centre."""
    height = round(width * HEIGHT)
    return [
        [tincture_at(arms, (c + 0.5) / width, (r + 0.5) / width) for c in range(width)]
        for r in range(height)
    ]


# ------------------------------------------------------------------ form


def _pairs(names: Sequence[str]) -> list[tuple[str, str]]:
    return [(n, n) for n in names]


def arms_fields(arms: Arms | None) -> list[DialogField]:
    shown = arms or Arms()
    return [
        DialogField(
            "field",
            "Field",
            "select",
            arms.field if arms else None,
            options=_pairs(TINCTURES),
            allow_blank=True,
            hint="Leave it blank for no arms.",
        ),
        DialogField(
            "division",
            "Division",
            "select",
            shown.division,
            options=_pairs(DIVISIONS),
            required=True,
            show_if=lambda v: bool(v.get("field")),
        ),
        DialogField(
            "second",
            "Second tincture",
            "select",
            shown.second,
            options=_pairs(TINCTURES),
            required=True,
            show_if=lambda v: bool(v.get("field")) and v.get("division") != "Plain",
        ),
        DialogField(
            "charge",
            "Charge",
            "select",
            shown.charge or None,
            options=[(words.capitalize(), name) for name, words in CHARGES.items()],
            allow_blank=True,
            show_if=lambda v: bool(v.get("field")),
        ),
        DialogField(
            "count",
            "How many",
            "select",
            str(shown.count),
            options=[(word.capitalize(), str(n)) for n, word in COUNTS.items()],
            required=True,
            show_if=lambda v: (
                bool(v.get("field"))
                and bool(v.get("charge"))
                and v.get("charge") not in ORDINARIES
            ),
        ),
        DialogField(
            "charge_tincture",
            "Charge tincture",
            "select",
            shown.charge_tincture,
            options=_pairs(TINCTURES),
            required=True,
            show_if=lambda v: bool(v.get("field")) and bool(v.get("charge")),
        ),
        DialogField(
            "motto",
            "Motto",
            "text",
            shown.motto,
            show_if=lambda v: bool(v.get("field")),
        ),
    ]


def from_values(values: dict[str, Any]) -> Arms | None:
    """The arms the form's values make; None with no field."""
    if not values.get("field"):
        return None
    return Arms(
        field=values["field"],
        division=values.get("division") or "Plain",
        second=values.get("second") or "Argent",
        charge=values.get("charge") or "",
        charge_tincture=values.get("charge_tincture") or "Or",
        motto=(values.get("motto") or "").strip(),
        count=int(values.get("count") or 1)
        if values.get("charge") and values.get("charge") not in ORDINARIES
        else 1,
    )


def arms_text(arms: Arms | None) -> str:
    """The motto, the blazon under it, and any warning on the line under
    that (markup). The motto is the bearer's own words, so it leads."""
    if arms is None:
        return "[$text-muted]No arms.[/]"
    lines = [f"[b][i]{escape(arms.motto)}[/][/]"] if arms.motto else []
    lines.append(escape(blazon(arms)))
    said = warning(arms)
    if said:
        lines.append(f"[$text-warning]{escape(said)}[/]")
    return "\n".join(lines)


def arms_form(record: Any) -> Form:
    """Arms of `record`: its six choices and motto, the blazon written as
    they are chosen, and the shield drawn beside them."""

    def apply(values: dict[str, Any]) -> None:
        made = from_values(values)
        record.arms = made.to_dict() if made is not None else {}

    return Form(
        f"Arms of {escape(record.name)}",
        lambda: arms_fields(arms_of(record)),
        apply,
        live=lambda values: arms_text(from_values(values)),
        picture=from_values,
        help_id="arms",
    )
