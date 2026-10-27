"""A magus's alchemy (The Mysteries Revised Edition, Chapter Five, pp.
39-46): a Philosophic Alchemy digestion running beside his other work,
and the Lesser Elixir's special ingredients. The rules are
rules.tmre_alchemy's."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import known_fields

#: What a digestion makes: raw vis, or ready-opened enchantment spaces.
DIGEST_VIS, DIGEST_SPACES = "vis", "spaces"
DIGEST_PRODUCTS: tuple[str, ...] = (DIGEST_VIS, DIGEST_SPACES)


def _whole(value: object, what: str) -> int:
    """`value` as a whole number, or a ValueError naming `what`."""
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError(f"{what} {value!r} isn't a number.")
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{what} {value!r} isn't a whole number.") from None


@dataclass
class Digestion:
    """An alchemical vis extraction settled to digest by itself
    (Philosophic Alchemy): the laboratory, what it makes (`product`), the
    Form of its vis ("" for Vim), the vessel's Shape and Material bonus,
    the device that takes ready-opened spaces (and whether they are extra
    room on top of its capacity rather than pawns of it already opened),
    whose raw vis receives the pawns, its first season, how many seasons
    it takes (4 with the Minor Virtue, 1 with the Major) and each season's
    Lab Total so far."""

    lab_id: str | None = None
    product: str = DIGEST_VIS
    form: str = ""
    shape_bonus: int = 0
    device_id: str | None = None
    extra_room: bool = False
    vis_from: str = ""
    season: str = ""
    year: int = 0
    seasons: int = 1
    totals: list[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Digestion:
        d = known_fields(cls, data)
        product = str(d.get("product") or DIGEST_VIS)
        if product not in DIGEST_PRODUCTS:
            raise ValueError(f"A digestion's product {product!r} is not vis or spaces.")
        d["product"] = product
        d["extra_room"] = bool(d.get("extra_room"))
        for key in ("shape_bonus", "year", "seasons"):
            if key in d:
                d[key] = _whole(d[key], f"A digestion's {key}")
        d["totals"] = [
            _whole(t, "A digestion's season Lab Total") for t in d.get("totals") or []
        ]
        return cls(**d)


@dataclass
class ElixirIngredient:
    """One special ingredient of the Lesser Elixir: its Shape and Material
    bonus, whether the alchemist devised it himself (by Vulgar Alchemy;
    its points are doubled) and the year it was added."""

    name: str
    bonus: int = 0
    devised: bool = False
    year: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ElixirIngredient:
        d = known_fields(cls, data)
        d["name"] = str(d.get("name") or "")
        d["bonus"] = _whole(d.get("bonus") or 0, "An Elixir ingredient's bonus")
        d["devised"] = bool(d.get("devised"))
        if d.get("year") is not None:
            d["year"] = _whole(d["year"], "An Elixir ingredient's year")
        return cls(**d)


@dataclass
class Alchemy:
    """A magus's alchemy: the digestion running (None: none), the Lesser
    Elixir's ingredients and the Elixir Level its formula was last devised
    at, whether a dose of it is the Longevity Ritual now in force (an
    Aging Crisis or a new ritual ends it), his attempts at the Great
    Elixir since the last success, and the age the Great Elixir made him
    a being of Magic at (None: it hasn't; later tests keep that age's Ease
    Factor)."""

    digestion: Digestion | None = None
    ingredients: list[ElixirIngredient] = field(default_factory=list)
    elixir_level: int = 0
    elixir_active: bool = False
    great_attempts: int = 0
    immortal_age: int | None = None

    @property
    def elixir_bonus(self) -> int:
        """What the Lesser Elixir adds to the Longevity Ritual's modifier
        while a dose of it is in force (TMRE p. 42)."""
        return self.elixir_level if self.elixir_active else 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Alchemy:
        d = known_fields(cls, data)
        if d.get("digestion") is not None:
            d["digestion"] = Digestion.from_dict(d["digestion"])
        d["ingredients"] = [
            ElixirIngredient.from_dict(i) for i in d.get("ingredients") or []
        ]
        for key in ("elixir_level", "great_attempts"):
            if key in d:
                d[key] = _whole(d[key], f"The alchemy's {key}")
        if d.get("immortal_age") is not None:
            d["immortal_age"] = _whole(d["immortal_age"], "The alchemy's immortal_age")
        d["elixir_active"] = bool(d.get("elixir_active"))
        return cls(**d)
