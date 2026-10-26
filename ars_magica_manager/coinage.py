"""The coins of the Byzantine lands, as data, and a sum of money told in
them.

SOURCE: The Sundered Eagle, Chapter Four: Culture & Customs, Coinage
(pp. 44-45): the gold hyperpyron (the Westerners' bezant) is a sixth of a
Mythic pound, 40 pence; the electrum aspron a third of a hyperpyron; the
billon a sixteenth of an aspron (a little under a penny); the copper
tetarteron an eighteenth of a billon. The Venetian grosso, the
Mediterranean's coin of trade, is 2 pence, so a bezant is 20 grossos.
The Definitive Edition (p. 187) makes the Mythic pound a pound of silver
and leaves local coinages to the Tribunal books; the 240 pence to the
pound are City & Guild's (goods.PENCE_PER_POUND). No errata touch these
pages.

Pattern: a table of coins (plain data) and two functions over it."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .goods import PENCE_PER_POUND


@dataclass(frozen=True)
class Coin:
    """A coin: its name and plural, what else it is called, its metal and
    its worth in Mythic pence (exact)."""

    name: str
    plural: str
    metal: str
    pence: Fraction
    also: str = ""


HYPERPYRON = Coin("hyperpyron", "hyperpyra", "gold", Fraction(40), also="bezant")
ASPRON = Coin("aspron", "aspra", "electrum", HYPERPYRON.pence / 3)
BILLON = Coin("billon", "billons", "copper and silver", ASPRON.pence / 16)
TETARTERON = Coin("tetarteron", "tetartera", "copper", BILLON.pence / 18)
GROSSO = Coin("grosso", "grossos", "silver", Fraction(2), also="Venetian grosso")

#: The Byzantine emperors' coins, the most valuable first.
BYZANTINE: tuple[Coin, ...] = (HYPERPYRON, ASPRON, BILLON, TETARTERON)

#: Every coin of the Theban lands, the grosso of the Latins' trade last.
COINS: tuple[Coin, ...] = (*BYZANTINE, GROSSO)


def count(coin: Coin, number: int) -> str:
    """ "1 hyperpyron", "3 aspra"."""
    return f"{number} {coin.name if number == 1 else coin.plural}"


def in_coins(pence: float | Fraction, coins: tuple[Coin, ...] = BYZANTINE) -> str:
    """A sum in pence told in `coins`, the largest first: "6 hyperpyra",
    "1 hyperpyron, 1 aspron and 4 billons". What is left under the
    smallest coin is dropped; nothing at all is "no coin"."""
    rest = Fraction(pence).limit_denominator(10**6)
    negative = rest < 0
    rest = abs(rest)
    parts = []
    for coin in coins:
        number, rest = divmod(rest, coin.pence)
        if number:
            parts.append(count(coin, int(number)))
    if not parts:
        return "no coin"
    words = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    return f"−{words}" if negative else words


def pounds_in_coins(pounds: float, coins: tuple[Coin, ...] = BYZANTINE) -> str:
    """A sum in Mythic pounds told in `coins` (12 pounds: "72 hyperpyra")."""
    return in_coins(Fraction(pounds).limit_denominator(10**6) * PENCE_PER_POUND, coins)


def worth(coin: Coin, other: Coin) -> Fraction:
    """How many of `other` a `coin` is worth (a bezant: 20 grossos)."""
    return coin.pence / other.pence
