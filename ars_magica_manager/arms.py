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
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from typing import Any

from .commands import Form
from .form_spec import DialogField
from .markup import escape

#: The tinctures, metals first. Each front-end's themes give the colour
#: each is painted in.
TINCTURES = ("Or", "Argent", "Gules", "Azure", "Vert", "Sable", "Purpure")
METALS = frozenset({"Or", "Argent"})

DIVISIONS = ("Plain", "Per pale", "Per fess", "Per bend", "Quarterly", "Per chevron")

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
    "Wheel": "a wheel",
    "Fleur-de-lis": "a fleur-de-lis",
}

#: How many of the charge a shield may bear, and the word for each.
COUNTS: dict[int, str] = {1: "one", 2: "two", 3: "three"}

#: The charges whose plural isn't the word with an s.
_PLURALS = {"Cross": "crosses", "Fleur-de-lis": "fleurs-de-lis"}

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
        if known.get("count") not in COUNTS:
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
        if _kind(on) == _kind(ground):
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


@dataclass(frozen=True)
class Shape:
    """A polygon or a circle (`radius` set, `points` its one centre); a
    hole cuts out of the solid shapes before it, so a shape after it (a
    wheel's spokes inside its rim) is whole."""

    points: tuple[Point, ...]
    radius: float = 0.0
    hole: bool = False

    def contains(self, x: float, y: float) -> bool:
        if self.radius:
            cx, cy = self.points[0]
            return (x - cx) ** 2 + (y - cy) ** 2 <= self.radius**2
        return _inside(self.points, x, y)


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


def _star() -> Shape:
    points = []
    for i in range(10):
        r = 0.5 if i % 2 == 0 else 0.2
        a = -math.pi / 2 + i * math.pi / 5
        points.append((0.5 + r * math.cos(a), 0.53 + r * math.sin(a)))
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

#: Each charge's shapes, in a unit square.
CHARGE_SHAPES: dict[str, tuple[Shape, ...]] = {
    "Tower": (
        _rect(0.2, 0.3, 0.8, 1.0),
        _rect(0.2, 0.1, 0.32, 0.3),
        _rect(0.44, 0.1, 0.56, 0.3),
        _rect(0.68, 0.1, 0.8, 0.3),
        _rect(0.42, 0.68, 0.58, 1.0, hole=True),
    ),
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
    "Star": (_star(),),
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
    "Cross": (_rect(0.4, 0.04, 0.6, 0.96), _rect(0.12, 0.28, 0.88, 0.48)),
    "Crescent": (_circle(0.5, 0.5, 0.42), _circle(0.62, 0.38, 0.36, hole=True)),
    "Tree": (_circle(0.5, 0.36, 0.32), _rect(0.43, 0.6, 0.57, 0.98)),
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


def _mirrored(*half: Point) -> Shape:
    """A polygon symmetric about x = 0.5, from its right half given top
    to bottom; the left half is the mirror, bottom to top."""
    left = [(1 - x, y) for x, y in reversed(half)]
    return Shape((*half, *left))


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


# An eagle displayed: head turned to its right, wings spread, tail
# fanned. Its right half, top to bottom, mirrored for the left; the head
# and beak are added over it.
CHARGE_SHAPES["Eagle"] = (
    _mirrored(
        (0.5, 0.14),
        (0.56, 0.24),
        (0.6, 0.3),
        (0.74, 0.2),
        (0.9, 0.08),
        (0.99, 0.02),
        (0.96, 0.18),
        (0.9, 0.17),
        (0.95, 0.32),
        (0.87, 0.3),
        (0.9, 0.45),
        (0.8, 0.42),
        (0.78, 0.54),
        (0.66, 0.56),
        (0.66, 0.7),
        (0.62, 0.78),
        (0.74, 0.82),
        (0.76, 0.9),
        (0.66, 0.88),
        (0.72, 0.99),
        (0.5, 0.93),
    ),
    _circle(0.45, 0.14, 0.1),
    _poly((0.36, 0.1), (0.25, 0.17), (0.37, 0.19)),
)

# A lion rampant: on its hind legs, forepaws raised, tail up. One
# polygon, read clockwise from the raised forepaw.
CHARGE_SHAPES["Lion"] = (
    _poly(
        (0.30, 0.04),
        (0.40, 0.06),
        (0.44, 0.16),
        (0.52, 0.26),
        (0.62, 0.42),
        (0.70, 0.56),
        (0.84, 0.66),
        (0.92, 0.82),
        (0.88, 0.96),
        (0.74, 0.96),
        (0.76, 0.80),
        (0.68, 0.72),
        (0.62, 0.84),
        (0.64, 0.96),
        (0.50, 0.96),
        (0.50, 0.80),
        (0.54, 0.66),
        (0.46, 0.58),
        (0.34, 0.64),
        (0.22, 0.66),
        (0.20, 0.58),
        (0.32, 0.52),
        (0.36, 0.44),
        (0.26, 0.40),
        (0.12, 0.34),
        (0.06, 0.24),
        (0.14, 0.20),
        (0.24, 0.30),
        (0.26, 0.22),
        (0.16, 0.18),
        (0.12, 0.10),
        (0.22, 0.12),
    ),
    _poly(
        (0.64, 0.46),
        (0.74, 0.36),
        (0.82, 0.26),
        (0.92, 0.28),
        (0.94, 0.40),
        (0.86, 0.36),
        (0.80, 0.44),
        (0.72, 0.54),
    ),
)

# A wheel of six spokes (the wheel of Mainz).
CHARGE_SHAPES["Wheel"] = (
    _circle(0.5, 0.5, 0.46),
    _circle(0.5, 0.5, 0.36, hole=True),
    *(_spoke(i * math.pi / 3, 0.0, 0.4, 0.1) for i in range(6)),
    _circle(0.5, 0.5, 0.12),
)

# A fleur-de-lis: the middle petal, the two curling side petals and
# the band that binds them.
CHARGE_SHAPES["Fleur-de-lis"] = (
    _mirrored(
        (0.5, 0.02),
        (0.6, 0.18),
        (0.6, 0.5),
        (0.56, 0.62),
        (0.6, 0.8),
        (0.58, 0.98),
        (0.5, 0.9),
    ),
    _poly(
        (0.6, 0.28),
        (0.7, 0.16),
        (0.84, 0.14),
        (0.96, 0.26),
        (0.95, 0.44),
        (0.84, 0.54),
        (0.6, 0.5),
    ),
    _poly(
        (0.4, 0.28),
        (0.3, 0.16),
        (0.16, 0.14),
        (0.04, 0.26),
        (0.05, 0.44),
        (0.16, 0.54),
        (0.4, 0.5),
    ),
    _rect(0.3, 0.52, 0.7, 0.64),
    _rect(0.6, 0.56, 0.9, 0.64),
    _rect(0.1, 0.56, 0.4, 0.64),
)

#: Where one charge sits on the shield: its square's corner and side.
CHARGE_BOX = (0.21, HEIGHT * 0.15, 0.58)

#: Where the charges sit by their count: two side by side, three as two
#: and one, as heralds place them.
Box = tuple[float, float, float]
CHARGE_BOXES: dict[int, tuple[Box, ...]] = {
    1: (CHARGE_BOX,),
    2: ((0.07, HEIGHT * 0.2, 0.4), (0.53, HEIGHT * 0.2, 0.4)),
    3: (
        (0.09, HEIGHT * 0.06, 0.36),
        (0.55, HEIGHT * 0.06, 0.36),
        (0.32, HEIGHT * 0.46, 0.36),
    ),
}


def charge_boxes(arms: Arms) -> tuple[Box, ...]:
    """The squares `arms`' charges are drawn in."""
    return CHARGE_BOXES.get(arms.count, CHARGE_BOXES[1])


def _in_charge(charge: str, box: Box, x: float, y: float) -> bool:
    left, top, side = box
    u, v = (x - left) / side, (y - top) / side
    if not (0 <= u <= 1 and 0 <= v <= 1):
        return False
    inside = False
    for shape in CHARGE_SHAPES[charge]:
        if shape.contains(u, v):
            inside = not shape.hole
    return inside


def tincture_at(arms: Arms, x: float, y: float) -> str | None:
    """The tincture at (x, y) on the shield, or None off it."""
    if not _inside(shield_outline(), x, y):
        return None
    if arms.charge in CHARGE_SHAPES and any(
        _in_charge(arms.charge, box, x, y) for box in charge_boxes(arms)
    ):
        return arms.charge_tincture
    if any(s.contains(x, y) for s in DIVISION_AREAS.get(arms.division, ())):
        return arms.second
    return arms.field


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
            show_if=lambda v: bool(v.get("field")) and bool(v.get("charge")),
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
        count=int(values.get("count") or 1) if values.get("charge") else 1,
    )


def arms_text(arms: Arms | None) -> str:
    """The blazon, and any warning on the line under it (markup)."""
    if arms is None:
        return "[$text-muted]No arms.[/]"
    lines = [f"[b]{escape(blazon(arms))}[/]"]
    if arms.motto:
        lines.append(f"[i]{escape(arms.motto)}[/]")
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
