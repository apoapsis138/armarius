"""The armour a character wears, and what it adds to Soak and Load.

A character wears one whole suit (the Definitive Edition's partial or full
armour, Armor Table p. 400), or an outfit of Lords of Men's pieces
(Expanded Armor Table, p. 140): body armour, a surcoat, greaves and a
helmet, one of each. An outfit's pieces add their Protection and their Load
together, keeping fractions until the end and then rounding up. Full body
armour already includes greaves, so greaves worn with it add nothing. Of
the two, the one that protects better is the one worn; of several pieces
for the same place, the best.

A piece filled from the catalog keeps the book's fractions (+2.5, Load 1.5)
while its whole figures are still the ones the form filled in (the book's,
rounded up); a piece typed in, or changed, counts as typed.

The coat of plates follows the Surcoats table (+2, Load 2, p. 140). The
Glossary (p. 141) says to use a metal scale cuirass's statistics instead
(+3, Load 3): the book contradicts itself, and the app follows the table.

How well a piece is made adds to its Protection (Superior +1, Excellent its
bonus); a Superior helmet's bonus counts only against blows to the head, so
not in the standing Soak (Lords of Men p. 136).

Complex armour design (Lords of Men p. 142, optional): the Protection a
material gives each part of the body it covers, summed, times its Load
Factor for its Load; every material's together, rounded up at the end.
No screen uses design() yet: it is a rule for a screen still to come, and
only the tests call it.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence

from .. import catalog
from ..models import Possession
from ..models.arms import ARMOR_SLOTS, BODY, GREAVES, HELMET
from ..models.holdings import GEAR_TYPES_BY_KIND
from . import equipment
from .breakdown import Line
from .rounding import round_up

SOURCE = "Lords of Men, Arms and Armor, Expanded Armor Rules, pp. 139-142"
SUIT_SOURCE = "Ars Magica Definitive Edition, Chapter Eleven: Armor Table, p. 400"
DESIGN_SOURCE = "Lords of Men, Arms and Armor, Option: Complex Armor Design, p. 142"
FULL_ARMOR = GEAR_TYPES_BY_KIND["armor"][1]

#: Complex Armor Design Table (Lords of Men p. 142): each material's
#: Protection over each part of the body, and its Load Factor.
BODY_PARTS: tuple[str, ...] = (
    "Torso",
    "Hips and Thighs",
    "Shins",
    "Upper Arms",
    "Forearms",
)
DESIGN_TABLE: dict[str, tuple[tuple[float, ...], float]] = {
    "Padded": ((1, 0, 0, 0, 0), 1.5),
    "Boiled Leather": ((2, 0.5, 0.5, 0, 0), 1.5),
    "Reinforced": ((2, 0.5, 0.5, 0.5, 0), 1),
    "Rigid Scale": ((2, 1, 0.5, 0.5, 0.5), 1),
    "Metal Scale": ((3, 1, 0.5, 1, 0.5), 1),
    "Mail": ((3, 1, 1, 1, 1), 0.5),
    "Plate": ((3, 1, 1, 0.5, 0.5), 1),
    "Plate and Mail": ((4, 2, 1, 2, 1), 0.5),
}


def is_piece(item: Possession) -> bool:
    """Armour worn as one piece of an outfit, not a whole suit."""
    return item.kind == "armor" and item.armor_slot in ARMOR_SLOTS


def figures(item: Possession) -> tuple[float, float]:
    """A piece's exact (Protection, Load): the book's fractions while the
    whole figures are still the book's rounded up, else the typed ones."""
    piece = catalog.load_armor_piece_catalog_by_id().get(item.gear_id or "")
    if (
        piece is not None
        and item.armor_protection == round_up(piece.protection)
        and item.load == round_up(piece.load)
    ):
        return piece.protection, piece.load
    return float(item.armor_protection), float(item.load)


def _full(body: Possession) -> bool:
    piece = catalog.load_armor_piece_catalog_by_id().get(body.gear_id or "")
    return piece.full if piece is not None else body.gear_type == FULL_ARMOR


def outfit(inventory: Sequence[Possession]) -> list[Possession]:
    """The pieces worn, in ARMOR_SLOTS order: the best of each place, and no
    greaves with full body armour."""
    best: dict[str, Possession] = {}
    for item in inventory:
        if not is_piece(item):
            continue
        held = best.get(item.armor_slot)
        if held is None or figures(item)[0] > figures(held)[0]:
            best[item.armor_slot] = item
    body = best.get(BODY)
    if body is not None and _full(body):
        best.pop(GREAVES, None)
    return [best[slot] for slot in ARMOR_SLOTS if slot in best]


def _made(item: Possession) -> int:
    """What how well a piece is made adds to the standing Soak (not a
    helmet's)."""
    return 0 if item.armor_slot == HELMET else equipment.quality_bonus(item)


def outfit_protection(pieces: Sequence[Possession]) -> int:
    """The outfit's Protection, rounded up at the end."""
    return round_up(sum(figures(p)[0] + _made(p) for p in pieces))


def outfit_load(pieces: Sequence[Possession]) -> int:
    """The outfit's Load, rounded up at the end."""
    return round_up(sum(figures(p)[1] for p in pieces))


def worn(inventory: Sequence[Possession]) -> list[Possession]:
    """What the character wears: the best whole suit, or the outfit of
    pieces when it protects better; [] for no armour."""
    suits = [item for item in inventory if item.kind == "armor" and not is_piece(item)]
    suit = max(suits, key=lambda item: item.armor_protection, default=None)
    pieces = outfit(inventory)
    if pieces and (suit is None or outfit_protection(pieces) > suit.armor_protection):
        return pieces
    return [suit] if suit is not None else []


def protection(inventory: Sequence[Possession]) -> int:
    """The worn armour's Protection, before Virtues and Flaws."""
    armour = worn(inventory)
    if armour and is_piece(armour[0]):
        return outfit_protection(armour)
    return sum(item.armor_protection + equipment.quality_bonus(item) for item in armour)


def load(inventory: Sequence[Possession]) -> int:
    """The worn armour's Load: a suit's times how many are held (as
    carried_load always counted it), an outfit's summed and rounded up."""
    armour = worn(inventory)
    if armour and is_piece(armour[0]):
        return outfit_load(armour)
    return sum(item.load * max(item.quantity, 1) for item in armour)


def soak_lines(inventory: Sequence[Possession]) -> list[Line]:
    """Soak's armour lines: the suit, or each piece with its exact
    Protection, how well each is made, and the rounding up."""
    armour = worn(inventory)
    lines: list[Line] = []
    pieces = bool(armour) and is_piece(armour[0])
    for item in armour:
        amount = figures(item)[0] if pieces else item.armor_protection
        if amount:
            lines.append(
                Line(item.name, amount=amount, source=SOURCE if pieces else SUIT_SOURCE)
            )
        made = _made(item) if pieces else equipment.quality_bonus(item)
        if made:
            lines.append(
                Line(
                    f"{item.make} armour",
                    amount=made,
                    source=equipment.QUALITY_SOURCE,
                )
            )
    exact = sum(line.amount or 0 for line in lines)
    if pieces and exact != round_up(exact):
        lines.append(Line("Rounded up", amount=round_up(exact) - exact, source=SOURCE))
    return lines


def design(
    covered: Mapping[str, Collection[str]],
) -> tuple[int, int]:
    """Complex armour design: (Protection, Load) of armour made of each
    material in `covered` over the BODY_PARTS listed for it."""
    protection_total = 0.0
    load_total = 0.0
    for material, parts in covered.items():
        if material not in DESIGN_TABLE:
            raise ValueError(f"Unknown armour material {material!r}")
        unknown = set(parts) - set(BODY_PARTS)
        if unknown:
            raise ValueError(f"Unknown parts of the body: {sorted(unknown)}")
        values, factor = DESIGN_TABLE[material]
        prot = sum(values[BODY_PARTS.index(part)] for part in parts)
        protection_total += prot
        load_total += prot * factor
    return round_up(protection_total), round_up(load_total)
