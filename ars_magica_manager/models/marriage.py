"""A marriage between two people of the saga's world: who, when, the bride's
family and the figures her dowry is worked out from, the custom that
governs it, the consents, and how it ended. What these mean is
rules.marriage's (Lords of Men pp. 10-11, 81; City & Guild p. 113 with
the errata p. 57; the Definitive Edition pp. 148, 512-513).

A marriage is kept once, in the saga, and shown on the page of each house
it joins (a lord's), so the two families never hold copies that could
disagree.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import SEASONS, known_fields
from .traits import new_instance_id

#: Where a marriage stands.
BETROTHED, MARRIED, ENDED = "betrothed", "married", "ended"
MARRIAGE_STATES: tuple[str, ...] = (BETROTHED, MARRIED, ENDED)
#: How it ended: he died first, she died first, or they parted
#: (separated, or the marriage was annulled).
HUSBAND_DIED, WIFE_DIED, PARTED = "husband", "wife", "part"
MARRIAGE_ENDINGS: tuple[str, ...] = (HUSBAND_DIED, WIFE_DIED, PARTED)
#: The bride's family, which sets how her dowry is worked out.
NOBLE, MERCHANT, VILLEIN = "noble", "merchant", "villein"
MARRIAGE_FAMILIES: tuple[str, ...] = (NOBLE, MERCHANT, VILLEIN)
#: The custom her dowry is held under (Lords of Men p. 11), or another the
#: troupe sets. Italy and much of France share how he holds it, but only
#: Italy's says where it goes when she dies first, so they are two choices
#: ("italy" was saved for both before they split; it now means Italy).
ITALY, FRANCE_MANAGES, FRANCE, ENGLAND, OTHER_CUSTOM = (
    "italy",
    "france_manages",
    "france",
    "england",
    "other",
)
MARRIAGE_CUSTOMS: tuple[str, ...] = (
    ITALY,
    FRANCE_MANAGES,
    FRANCE,
    ENGLAND,
    OTHER_CUSTOM,
)
#: The statement once shared by both kinds of bride ("paid in rights or
#: goods"), saved before it split into a noble's (other rights, not land or
#: money: LoM p. 11) and a merchant's (assets, land among them, not money:
#: C&G p. 113); a saved one is read as her kind's.
OLD_GOODS_POINT, NOBLE_RIGHTS_POINT, MERCHANT_ASSETS_POINT = "goods", "rights", "assets"
#: A merchant bride's father's Social Status against the groom's (C&G
#: p. 113).
SAME_STATUS, ONE_HIGHER, TWO_HIGHER, LOWER = "same", "one", "two", "lower"
MERCHANT_STANDINGS: tuple[str, ...] = (SAME_STATUS, ONE_HIGHER, TWO_HIGHER, LOWER)
#: How a spouse links to a record: a saga character, or a lord himself.
CHARACTER_REF, NEIGHBOUR_REF = "character:", "neighbour:"


@dataclass
class Marriage:
    """A marriage, or a betrothal.

    Each spouse is a saga record (`bride_ref` / `groom_ref`: "character:"
    or "neighbour:" and its id) or a name typed in (`bride` / `groom`).
    `bride_house` and `groom_house` are the lords (neighbour ids) whose
    pages show it, besides a spouse who is a lord himself. `points` are
    the keys (rules.marriage.POINTS) of the statements true of the bride
    that make a dowry larger; `dowry` is what was agreed, in the troupe's
    words. `ended` is how it ended ("" while it stands).
    """

    id: str = field(default_factory=new_instance_id)
    bride: str = ""
    bride_ref: str = ""
    groom: str = ""
    groom_ref: str = ""
    bride_house: str | None = None
    groom_house: str | None = None
    season: str = "Spring"
    year: int = 1220
    state: str = BETROTHED
    family: str = NOBLE
    heiress: bool = False
    #: A noble family's land, in manors; the eldest son's patrimony kept
    #: out of the division (the French sphere), which takes the eldest son
    #: out of it too; her parents' children, herself and the eldest son
    #: among them (for a merchant, his children less married daughters).
    lands: int = 0
    patrimony: int = 0
    children: int = 1
    #: A merchant father's yearly profit, in pounds, and his Social
    #: Status against the groom's.
    profit: int = 0
    standing: str = SAME_STATUS
    points: list[str] = field(default_factory=list)
    custom: str = FRANCE
    dowry: str = ""
    her_consent: bool = True
    father_consent: bool = True
    #: Close kin, or one of them already married: a canon crime.
    kin: bool = False
    note: str = ""
    ended: str = ""
    end_season: str = ""
    end_year: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Marriage:
        """A saved marriage, checked: a wrong value names the marriage."""
        d = known_fields(cls, data)
        name = (
            f"{d.get('bride') or d.get('bride_ref') or '?'} and "
            f"{d.get('groom') or d.get('groom_ref') or '?'}"
        )
        for key, allowed in (
            ("state", MARRIAGE_STATES),
            ("family", MARRIAGE_FAMILIES),
            ("custom", MARRIAGE_CUSTOMS),
            ("standing", MERCHANT_STANDINGS),
            ("season", SEASONS),
        ):
            if key in d and d[key] not in allowed:
                raise ValueError(
                    f"Marriage of {name}: unknown {key} {d[key]!r}; must be one "
                    f"of {allowed}"
                )
        if d.get("ended") and d["ended"] not in MARRIAGE_ENDINGS:
            raise ValueError(
                f"Marriage of {name}: unknown ending {d['ended']!r}; must be one "
                f"of {MARRIAGE_ENDINGS}"
            )
        if d.get("end_season") and d["end_season"] not in SEASONS:
            raise ValueError(f"Marriage of {name}: unknown season {d['end_season']!r}")
        for key in ("bride_ref", "groom_ref"):
            ref = d.get(key) or ""
            if ref and not ref.startswith((CHARACTER_REF, NEIGHBOUR_REF)):
                raise ValueError(
                    f"Marriage of {name}: {key} {ref!r} should name a "
                    "character or a neighbour"
                )
        for key in ("year", "lands", "patrimony", "children", "profit"):
            value = d.get(key, 0)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"Marriage of {name}: {key} must be a whole number")
            if value < 0:
                raise ValueError(f"Marriage of {name}: {key} can't be negative")
        end_year = d.get("end_year")
        if end_year is not None and (
            isinstance(end_year, bool) or not isinstance(end_year, int)
        ):
            raise ValueError(f"Marriage of {name}: end_year must be a whole number")
        points = d.get("points") or []
        if not isinstance(points, list) or not all(isinstance(p, str) for p in points):
            raise ValueError(f"Marriage of {name}: points must be a list of keys")
        swap = (
            MERCHANT_ASSETS_POINT if d.get("family") == MERCHANT else NOBLE_RIGHTS_POINT
        )
        d["points"] = list(
            dict.fromkeys(swap if p == OLD_GOODS_POINT else p for p in points)
        )
        return cls(**d)
