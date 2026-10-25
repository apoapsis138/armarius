"""The Goods catalog's rules, without a front-end: which goods a saga lists,
what a printed price is worth, a purity's price, and money in pounds,
shillings and pence.

SOURCE: City & Guild, Chapter VIII: The Goods of Europe -- the three
commodity classes (p. 134), the commercial sources of trade goods
(pp. 138-140), weights and measures and the Prices of Goods table
(pp. 140-142); the Appendix -- medieval money (p. 143) and the Price List
of common goods with its quality multipliers (p. 144); Errata (Ars Magica
5th Edition) p. 57, which corrects p. 140's pound to 1/2,240 of a ton.

The table's prices are kept as printed. Silver stays 2,420 a ton: the
table is built on it (gold's 24,200 is ten times silver, and the
gemstones' and pearls' per-ounce notes match their columns over 2,420
pounds of 16 ounces), while the errata's 2,240 is the weight of a ton.
The p. 144 multipliers belong to the common goods only: the commodities'
own columns have other ratios.
"""

from __future__ import annotations

from . import catalog
from .models import COMMODITY, GoodDef, GoodPurity, Saga

#: The catalog's key in Saga Content's catalogs (saga_content.CATALOGS),
#: which Saga.hidden_catalogs and Saga.hidden_entries name.
CATALOG_KEY = "goods"

#: The table's quality columns, in order (C&G pp. 141-142; no Excellent).
QUALITIES = ("Shoddy", "Standard", "Superior", "Expensive")

#: The three commodity classes (C&G p. 134), by key.
CLASSES = {"bulk": "Bulk", "manufactured": "Manufactured", "luxury": "Luxury"}

#: Weights (C&G p. 140, with the errata's ton, p. 57).
OUNCES_PER_POUND = 16
POUNDS_PER_TON = 2240
#: The pounds in a ton the price table is built on: p. 140 as printed.
TABLE_POUNDS_PER_TON = 2420

#: Money (C&G p. 143): 12 pence to the shilling, 20 shillings to the pound.
PENCE_PER_SHILLING = 12
PENCE_PER_POUND = 240

#: A common good's price by quality, as a multiple of its standard price
#: (C&G p. 144); Wondrous is "x5 or more".
COMMON_MULTIPLIERS = (
    ("Shoddy", 0.5),
    ("Standard", 1),
    ("Superior", 2),
    ("Excellent", 5),
)

#: The table's marks: none to be had at that quality, priced by purity.
UNOBTAINABLE, BY_PURITY = "#", "*"


def price_value(printed: str) -> float | None:
    """What a printed price is worth in pounds a ton ("1,650*" is 1,650,
    "2,000 (fake)" 2,000); None for "#", "*", "n/a" or a blank."""
    words = printed.replace(" (fake)", "").rstrip("*").replace(",", "")
    try:
        return float(words)
    except ValueError:
        return None


def is_commodity(good: GoodDef) -> bool:
    return good.kind == COMMODITY


def by_purity(good: GoodDef) -> bool:
    """Whether the table marks the good * (priced by purity)."""
    return good.purity is not None


def takes_purities(good: GoodDef) -> bool:
    """Whether a purity of the good can be priced: it is priced by purity
    and has a pure price (alum's three prices are kinds, not purities)."""
    return good.purity is not None and good.purity.pure_price is not None


def price_at_purity(pure_price: float, percent: float) -> float:
    """A purity's price a ton: the pure price times its metal content
    (C&G p. 140)."""
    return pure_price * percent / 100


def purity_percent(price: float, pure_price: float) -> float:
    """The metal content a purity's price stands for, in percent."""
    return price / pure_price * 100


def per_ounce(price: float) -> float:
    """A price a ton as a price an ounce, over the ton the table is built
    on (TABLE_POUNDS_PER_TON pounds of 16 ounces)."""
    return price / (TABLE_POUNDS_PER_TON * OUNCES_PER_POUND)


def listed(saga: Saga) -> list[GoodDef]:
    """The goods the saga's Goods tab lists, in order: the catalog's
    commodities by class (bulk, manufactured, luxury), then its common
    goods, each in the book's order, less those the saga hides (the whole catalog switched off, or single
    goods), then the saga's own."""
    hidden = set(saga.hidden_entries.get(CATALOG_KEY, ()))
    whole = CATALOG_KEY in saga.hidden_catalogs
    shared = [
        g
        for g in catalog.load_goods_catalog()
        if g.source and not whole and g.id not in hidden
    ]
    order = list(CLASSES)
    commodities = sorted(
        (g for g in shared if is_commodity(g)),
        key=lambda g: (
            order.index(g.commodity_class) if g.commodity_class in order else len(order)
        ),
    )
    common = [g for g in shared if not is_commodity(g)]
    return [*commodities, *common, *saga.custom_goods]


def is_own(saga: Saga, good: GoodDef) -> bool:
    return any(g is good for g in saga.custom_goods)


def purities_of(saga: Saga, good: GoodDef) -> list[GoodPurity]:
    """The purities the saga has added to `good`."""
    return [p for p in saga.good_purities if p.good_id == good.id]


def new_good_id(saga: Saga, name: str) -> str:
    """An id for a new good of the saga's own, unlike any other."""
    base = "custom_good_" + (
        "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_") or "good"
    )
    taken = {g.id for g in saga.custom_goods}
    ident, n = base, 2
    while ident in taken:
        ident, n = f"{base}_{n}", n + 1
    return ident


def new_purity_id(saga: Saga) -> str:
    taken = {p.id for p in saga.good_purities}
    n = 1
    while f"purity_{n}" in taken:
        n += 1
    return f"purity_{n}"


def number(value: float) -> str:
    """A price as the table writes one: thousands with commas, a fraction
    only when there is one (2.5)."""
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def _fraction(value: float) -> str:
    """A whole number, or one with a half or quarter (2½, ¼)."""
    whole = int(value)
    part = {0.25: "¼", 0.5: "½", 0.75: "¾"}.get(value - whole)
    if part is not None:
        return f"{whole}{part}" if whole else part
    return number(value)


def coins(pence: float) -> str:
    """A sum in pence as the app writes money, shortly: "15 s", "10 d",
    "2½ £" (C&G p. 143's 12 pence to the shilling, 240 to the pound)."""
    if pence >= PENCE_PER_POUND and (pence * 2) % PENCE_PER_POUND == 0:
        return f"{_fraction(pence / PENCE_PER_POUND)} £"
    if pence >= PENCE_PER_SHILLING and (pence * 2) % PENCE_PER_SHILLING == 0:
        return f"{_fraction(pence / PENCE_PER_SHILLING)} s"
    return f"{_fraction(pence)} d"


def coins_range(pence: tuple[float, float]) -> str:
    """A common good's price shortly: one sum, or "6–16 d"."""
    low, high = pence
    if low == high:
        return coins(low)
    low_text, high_text = coins(low), coins(high)
    if low_text[-1] == high_text[-1]:
        return f"{low_text[:-2]}–{high_text}"
    return f"{low_text} – {high_text}"


def pounds_shillings_pence(pence: float) -> str:
    """A sum in pence in full: "1 £ 7 s 6 d", "½ d"."""
    pounds, rest = divmod(pence, PENCE_PER_POUND)
    shillings, rest = divmod(rest, PENCE_PER_SHILLING)
    parts = []
    if pounds:
        parts.append(f"{int(pounds)} £")
    if shillings:
        parts.append(f"{int(shillings)} s")
    if rest or not parts:
        parts.append(f"{_fraction(rest)} d")
    return " ".join(parts)
