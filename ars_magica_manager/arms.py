"""Arms: a covenant's (or a lord's, town's or faction's) shield, a value
object of five choices (how the field is divided, its two tinctures, the
charge and the charge's tincture) and a motto. The blazon is written
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

#: The charges, by name, each with how the blazon names it.
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
}

#: The kinds of neighbour that bear arms.
BEARERS = frozenset({"lord", "town", "faction"})


@dataclass(frozen=True)
class Arms:
    """A shield: `field` alone for a plain one, or divided with `second`;
    an optional `charge` in `charge_tincture`; and a motto."""

    field: str = "Azure"
    division: str = "Plain"
    second: str = "Argent"
    charge: str = ""
    charge_tincture: str = "Or"
    motto: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Arms | None:
        """The arms kept on a record; None for a record with none."""
        if not data or data.get("field") not in TINCTURES:
            return None
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
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
    """Whether `record` can bear arms: a covenant, or a lord, town or
    faction."""
    kind = getattr(record, "kind", None)
    return hasattr(record, "arms") and (kind is None or kind in BEARERS)


def blazon(arms: Arms) -> str:
    """ "Per bend azure and argent, a tower or"."""
    if arms.divided:
        words = f"{arms.division} {arms.field.lower()} and {arms.second.lower()}"
    else:
        words = arms.field
    if arms.charge in CHARGES:
        words += f", {CHARGES[arms.charge]} {arms.charge_tincture.lower()}"
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
    hole cuts out of the solid shapes it lies on."""

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

#: Where the charge sits on the shield: its square's corner and side.
CHARGE_BOX = (0.21, HEIGHT * 0.15, 0.58)


def _in_charge(charge: str, x: float, y: float) -> bool:
    left, top, side = CHARGE_BOX
    u, v = (x - left) / side, (y - top) / side
    if not (0 <= u <= 1 and 0 <= v <= 1):
        return False
    shapes = CHARGE_SHAPES[charge]
    if any(s.hole and s.contains(u, v) for s in shapes):
        return False
    return any(not s.hole and s.contains(u, v) for s in shapes)


def tincture_at(arms: Arms, x: float, y: float) -> str | None:
    """The tincture at (x, y) on the shield, or None off it."""
    if not _inside(shield_outline(), x, y):
        return None
    if arms.charge in CHARGE_SHAPES and _in_charge(arms.charge, x, y):
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
    """Arms of `record`: its five choices and motto, the blazon written as
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
