"""Selling finished goods: a craftsman haggling over a sale, when the story
calls for the roll rather than leaving the sale off-stage.

- A typical customer: Presence + Bargain + a simple die against Ease
  Factor 9. Success sells for 10% over the standard cost, each point over
  9 another 10%, at most 50% over; failure sells at the standard cost.
- An important storyguide character or another player: Presence + Bargain
  + a stress die against his Communication + Bargain + a stress die. The
  craftsman's margin raises the price as above; the customer's lowers it
  10% a point, at most 50% off. A botch sells for next to nothing.
- Superior and excellent goods sell for more, unregulated by the guild;
  the standard cost is the guild's price for standard goods (p. 75).

The standard cost is the troupe's: this is not the Goods catalog's
commodity prices.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character
from .rounding import round_down
from .scores import ability_level

SOURCE = "City & Guild, Selling Finished Goods, pp. 74-76"

#: The typical customer's Ease Factor.
EASE = 9
#: Each point of success (or of the customer's advantage) moves the price
#: this many percent, at most CAP either way.
STEP = 10
CAP = 50
TYPICAL = "typical"
IMPORTANT = "important"
CUSTOMERS: dict[str, str] = {
    TYPICAL: "A typical customer (simple die against 9)",
    IMPORTANT: "An important character or another player (opposed stress dice)",
}


def bargain_total(character: Character) -> int:
    """Presence + Bargain, before the die."""
    return character.characteristics.presence + ability_level(character, "Bargain")


def typical_change(total: int) -> int:
    """The percent over the standard cost a roll of `total` against Ease
    Factor 9 sells for: 10 at 9, 10 more each point over, at most 50; 0
    when it fails."""
    if total < EASE:
        return 0
    return min(CAP, STEP * (total - EASE + 1))


def opposed_change(mine: int, theirs: int) -> int:
    """The percent the price moves when the craftsman's total meets the
    customer's: up 10 a point he wins by, down 10 a point he loses by, at
    most 50 either way; 0 on a tie."""
    return max(-CAP, min(CAP, STEP * (mine - theirs)))


@dataclass(frozen=True)
class Sale:
    """A sale's outcome: the percent the price moved, the price in pence
    (0 for a botch: next to nothing), and whether it botched."""

    change: int
    price: int
    botched: bool = False


def sale(
    standard: int,
    customer: str,
    mine: int,
    theirs: int = 0,
    botched: bool = False,
) -> Sale:
    """What the goods sell for: `standard` pence at the standard cost, the
    craftsman's roll `mine` (Presence + Bargain + die) and, against an
    important customer, the customer's `theirs`."""
    if customer == IMPORTANT and botched:
        return Sale(0, 0, True)
    change = (
        opposed_change(mine, theirs) if customer == IMPORTANT else typical_change(mine)
    )
    return Sale(change, round_down(standard * (100 + change) / 100))
