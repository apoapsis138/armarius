"""The Goods catalog's entries (goods_catalog.json, and a saga's own goods)
and the purities a saga adds to them. The rules that read them are in
goods.py."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .common import known_fields

#: A price as City & Guild's Prices of Goods table prints it: a number
#: (commas and a decimal point allowed), "#" none to be had, "*" priced by
#: purity, "n/a", or blank; a number may carry a "*" (one purity's price)
#: or " (fake)".
PRICE_PATTERN = re.compile(
    r"^(|#|\*|n/a|\d{1,3}(,\d{3})+(\.\d+)?\*?|\d+(\.\d+)?\*?|"
    r"\d{1,3}(,\d{3})*( \(fake\)))$"
)

#: A good is a commodity, priced a tun or ton by quality (C&G pp. 140-142),
#: or a common good, priced each (C&G p. 144).
COMMODITY, COMMON = "commodity", "common"
GOOD_KINDS = (COMMODITY, COMMON)


@dataclass(frozen=True)
class PurityExample:
    """One price the book prints for a purity (silver's 250*), named by its
    quality column."""

    label: str
    price: str


@dataclass(frozen=True)
class Purity:
    """How a good marked * is priced: its pure (Expensive) price a ton,
    which a lesser purity's price is by its metal content (C&G p. 140);
    None when the book gives no pure price (alum's three prices are its
    three kinds). `examples` are the book's own purity prices."""

    pure_price: float | None = None
    note: str = ""
    examples: tuple[PurityExample, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Purity:
        d = dict(data)
        d["examples"] = tuple(
            PurityExample(**known_fields(PurityExample, e))
            for e in d.get("examples", [])
        )
        return cls(**known_fields(cls, d))


@dataclass
class GoodDef:
    """A good of the Goods catalog, or of the saga's own: its commodity
    class (C&G p. 134), how it is sold, its four prices as the table
    prints them (Shoddy, Standard, Superior, Expensive; a common good
    has only Standard, and its price in pence), its purity, the per-ounce
    figures of a good sold by the ounce, and where it is bought in bulk."""

    id: str
    name: str
    kind: str = COMMODITY
    #: "bulk", "manufactured" or "luxury" (a common good has none).
    commodity_class: str = ""
    #: The page that describes it.
    class_page: str = ""
    sold_by: str = "ton"
    prices: tuple[str, str, str, str] = ("", "", "", "")
    #: A common good's standard price in pence, lowest and highest.
    pence: tuple[float, float] | None = None
    #: The page of its price.
    page: int | None = None
    #: How it is sold, when not by the ton.
    sale: str = ""
    note: str = ""
    sources: tuple[str, ...] = ()
    purity: Purity | None = None
    #: A good sold by the ounce: its price an ounce by quality column.
    per_ounce: tuple[str, ...] = ()
    per_ounce_note: str = ""
    #: The book ("C&G"), or "" for the saga's own.
    source: str = ""
    #: The saga's own good: what the troupe wrote about it.
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GoodDef:
        """Raises ValueError naming the good for a price the table couldn't
        print or a kind that isn't one."""
        d = dict(data)
        name = d.get("name") or d.get("id") or "?"
        prices = tuple(str(p) for p in d.get("prices", ("", "", "", "")))
        if len(prices) != 4:
            raise ValueError(f"The good {name} needs four prices, not {len(prices)}.")
        kind = d.get("kind", COMMODITY)
        if kind not in GOOD_KINDS:
            raise ValueError(f"The good {name} is of no kind {kind!r}.")
        pence = d.get("pence")
        if kind == COMMODITY:
            for price in prices:
                if not PRICE_PATTERN.match(price):
                    raise ValueError(f"The good {name} has a price {price!r}.")
        elif not pence or len(pence) != 2:
            raise ValueError(f"The common good {name} needs its price in pence.")
        d["prices"] = prices
        d["pence"] = (float(pence[0]), float(pence[1])) if pence else None
        d["sources"] = tuple(d.get("sources", ()))
        d["per_ounce"] = tuple(str(p) for p in d.get("per_ounce", ()))
        purity = d.get("purity")
        d["purity"] = Purity.from_dict(purity) if purity else None
        return cls(**known_fields(cls, d))


@dataclass
class GoodPurity:
    """A purity the saga adds to a good priced by purity: its name and its
    metal content, in percent of the pure good."""

    id: str
    good_id: str
    label: str
    percent: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GoodPurity:
        return cls(**known_fields(cls, data))
