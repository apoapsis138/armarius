"""A lord's manors, kennels, mews and stables, and his household (Lords of
Men); a covenant that holds land keeps the same Manors tab.

- A manor is about 600 acres, a third more or less without being
  exceptional, and yields its lord 20 pounds a year (LoM p. 72). A mill or
  bakery the fief holds by custom is already inside that figure (p. 85).
- Its peasant land: a hide is 120-144 acres and yields 4 pounds; a virgate
  24-32 acres, its family worth about a pound a year; a bovate half a
  virgate; a cottar ten acres or less. Roughly 20% of families hold a
  virgate, 30% a bovate and 50% are cottars (p. 72). Land is an allod,
  demesne, glebe, rented to free peasants, villein land or waste (p. 75).
- The lord's demesne flock averages 600 sheep, over 1,000 on marshland and
  300 in wooded country; it is two-thirds of the manor's sheep. The
  swineherd keeps pigs a quarter of the flock's number. A winter crop is
  sown at 2 bushels an acre and yields 8; a spring crop 4 and 16 (p. 76).
- The manor court's dues (pp. 79-82) are kept as ticks and notes: the
  book gives no sums for them, and tallage may be as high as the lord
  wishes.
- Kennels, mews and stables (pp. 58-61): capacity, maintenance, staff and
  Living Conditions by quality (p. 60; the Excellent stables row as the
  errata moves it, errata p. 74: capacity 40, 3 pounds a horse, 12 staff,
  +2). Up to a third again of the capacity may be young or breeding
  stock. A stable of his rank costs a lord nothing (a knight's Standard,
  an earl's Excellent); a covenant pays for anything better than
  Standard; kennels and mews always pay. Superior and better need a
  specialist (p. 59); a positive Living Conditions modifier needs one with
  the Profession at twice it (p. 60). Unpaid maintenance drops the quality
  a class at once, and the animals fall 15% (rounded up) each season it
  goes unpaid (p. 59). Each winter, a stress die + Intelligence + Animal
  Handling, or + the Profession (Marshal, Falconer, Master of Kennels),
  against 9: a failure drops a class until a later success restores it,
  maintenance unchanged; a botch is a catastrophe (pp. 60-61).
- The household (pp. 9-12): its size (a lord of the manor about 10, a
  landed knight 16, a banneret 24, a baron 40, an earl 140), the mesnie of
  household knights, the heirs and the custom of inheritance (p. 10; a
  widow keeps a third for her support, p. 11), and hunting rights (p. 48).
- Buying land costs 30 to 50 times its yearly income (p. 85); a strong
  laborer with proper tools clears an acre of lightly wooded land a month
  doing nothing else (p. 84, errata p. 74).
- A covenant's income is its sources' (Covenants pp. 56-58), so its
  manors are shown beside its Agriculture (and Livestock) source as a
  check, never added to it; each troupe may farm its land any way it
  likes (LoM p. 73), and the oldest covenants hold allods (p. 85).

Kept in a lord's Neighbour.details, and in Covenant.manors for a covenant:
"manor_list" (each Manor), "establishments" (each Establishment),
"household" (Household; a lord's only), and for a covenant
"agriculture_source" and "livestock_source" (income source ids)."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Required, TypedDict, cast

from . import lords, place_events
from .armies import title
from .commands import Command, Form, Refuse, SectionOps, notes
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import BULLET, escape
from .models import (
    Character,
    Covenant,
    IncomeSource,
    Neighbour,
    Saga,
    SeasonRecordLine,
    details_list,
)
from .neighbour_lists import KindBlock, KindList, KindTab, list_ops, tab_ops
from .references import Fact
from .rules import dice, scores
from .sections import (
    ESTABLISHMENTS_SECTION,
    HOUSEHOLD_SECTION,
    MANOR_CHECK_SECTION,
    MANORS_SECTION,
)

SOURCE = (
    "Lords of Men, Chapter Six pp. 71-87, Chapter Two pp. 9-12, Chapter Five "
    "pp. 48, 58-61, Chapter Three pp. 30-33; Errata p. 74; Covenants pp. 56-58"
)
LOM = "LoM"

#: A manor's usual size in acres, and how far it may stray (p. 72).
MANOR_ACRES = 600
ACRES_SPREAD = 1 / 3

#: What a hide and a virgater family are worth to the lord a year (p. 72).
HIDE_INCOME = 4
VIRGATE_INCOME = 1

#: The usual spread of peasant families: virgaters, bovaters, cottars (p. 72).
SPREAD = (20, 30, 50)

#: How the manor is farmed: large fields, turned over to sheep, or another
#: way (individual plots, herding) where the soil doesn't suit large fields
#: (pp. 72-73).
FARMING: tuple[str, ...] = ("Large fields", "Sheep", "Other")
SHEEP = "Sheep"

#: The demesne flock by the lie of the land (p. 76): marshland "over a
#: thousand".
FLOCKS: dict[str, int] = {"Open": 600, "Marsh": 1000, "Wooded": 300}
TERRAIN_WORDS = {"Open": "open land", "Marsh": "marshland", "Wooded": "wooded land"}
#: The lord's share of a manor's sheep, and the swineherd's pigs against
#: the flock (p. 76).
LORDS_SHARE = 2 / 3
PIGS_PER_SHEEP = 1 / 4

#: Bushels sown an acre and reaped from it (p. 76).
WINTER_CROP = (2, 8)
SPRING_CROP = (4, 16)

#: The manor's land by its legal status (p. 75), as acres.
LAND_USES: tuple[tuple[str, str], ...] = (
    ("demesne", "Demesne"),
    ("rented", "Rented"),
    ("villeins", "Villeins"),
    ("glebe", "Glebe"),
    ("waste", "Waste"),
)

#: The manor court's fines and dues (pp. 79-82): key, name, and the book's
#: word on each.
DUES: tuple[tuple[str, str, str], ...] = (
    ("entry", "Entry fine", "for taking up land; less for poor land"),
    ("heriot", "Heriot", "a death duty: often the best beast"),
    ("mortuary", "Mortuary", "the second-best beast, for the Church's tithe"),
    ("tallage", "Tallage", "as high as the lord wishes; some manors commute it"),
    ("merchet", "Merchet", "to marry; more for a big dowry or a move"),
    ("leywrite", "Leywrite", "on a woman unmarriageable"),
    ("childwrite", "Childwrite", "on an unmarried pregnancy"),
    ("celibacy", "Fine for celibacy", "yearly, unmarried more than a year"),
    ("fined_elsewhere", "Fine for being fined", "after another court's fine"),
)


def due_key(key: str) -> str:
    return f"due_{key}"


class Manor(TypedDict, total=False):
    """A manor: its size, farming and land, its peasant holdings, flock and
    crops (acres sown), what it holds by custom, and its court's dues (a
    tick each, `due_<key>`, and `court` in words)."""

    name: Required[str]
    acres: int | None
    farming: str
    terrain: str
    allod: bool
    demesne: int | None
    rented: int | None
    villeins: int | None
    glebe: int | None
    waste: int | None
    hides: int | None
    virgates: int | None
    bovates: int | None
    cottars: int | None
    sheep: int | None
    winter: int | None
    spring: int | None
    mill: bool
    bakery: bool
    court: str
    note: str


def manor_list(holder: Neighbour) -> list[Manor]:
    return cast(list[Manor], details_list(holder, "manor_list"))


def _n(value: object) -> int:
    return value if isinstance(value, int) else 0


# -- what a manor yields --


def manor_yield(_manor: Manor) -> int:
    """A manor's yearly income to its lord: 20 pounds, its customary mill
    and bakery included (pp. 72, 85)."""
    return lords.MANOR_INCOME


def total_yield(holder: Neighbour) -> int:
    return sum(manor_yield(m) for m in manor_list(holder))


def total_acres(holder: Neighbour) -> int:
    return sum(_n(m.get("acres")) for m in manor_list(holder))


def by_custom(manor: Manor) -> list[str]:
    return [w for w in ("mill", "bakery") if manor.get(w)]


def unusual_size(acres: int | None) -> bool:
    """Whether a manor of `acres` is more than a third off 600 (p. 72)."""
    if not acres:
        return False
    return abs(acres - MANOR_ACRES) > MANOR_ACRES * ACRES_SPREAD


def spread(manor: Manor) -> tuple[int, int, int] | None:
    """The share of virgater, bovater and cottar families, in percent."""
    counts = [_n(manor.get(k)) for k in ("virgates", "bovates", "cottars")]
    families = sum(counts)
    if not families:
        return None
    v, b, _c = (round(100 * c / families) for c in counts)
    return v, b, 100 - v - b


def peasant_worth(manor: Manor) -> int:
    """What its hides and virgaters are worth to the lord a year (p. 72)."""
    return _n(manor.get("hides")) * HIDE_INCOME + _n(manor.get("virgates")) * (
        VIRGATE_INCOME
    )


def flock(manor: Manor) -> int:
    """The lord's demesne flock: as entered, or the usual for its land."""
    sheep = manor.get("sheep")
    if isinstance(sheep, int):
        return sheep
    return FLOCKS.get(manor.get("terrain") or "Open", FLOCKS["Open"])


def manor_sheep(manor: Manor) -> int:
    """All the manor's sheep: the demesne flock is two-thirds of them."""
    return round(flock(manor) / LORDS_SHARE)


def crops(manor: Manor) -> list[tuple[str, int, int, int]]:
    """Each crop sown: its season, acres, bushels sown and reaped."""
    found = []
    for key, (sown, reaped) in (("winter", WINTER_CROP), ("spring", SPRING_CROP)):
        acres = _n(manor.get(key))
        if acres:
            found.append((key, acres, acres * sown, acres * reaped))
    return found


# -- the Manors list --


def manors_title(_saga: Saga, holder: Neighbour) -> str:
    return f"Manors ({len(manor_list(holder))})"


def manors_header(_saga: Saga, holder: Neighbour) -> str:
    listed = manor_list(holder)
    if not listed:
        return ""
    return (
        f"[$label]Yield:[/] [b]{total_yield(holder)} pounds[/] a year "
        f"[dim]({len(listed)} x {lords.MANOR_INCOME}, {LOM} p. 72)[/]  ·  "
        f"[$label]Land:[/] {total_acres(holder):,} acres"
    )


def _acres(value: object) -> str:
    return f"{value:,}" if isinstance(value, int) else ""


def manors_grid(_saga: Saga, holder: Neighbour) -> Grid:
    rows, styles = [], {}
    for i, m in enumerate(manor_list(holder)):
        rows.append(
            [
                m["name"],
                _acres(m.get("acres")),
                *(_acres(m.get(k)) for k in ("demesne", "rented", "villeins", "waste")),
                f"{manor_yield(m)} £",
                ", ".join(by_custom(m)),
            ]
        )
        if unusual_size(m.get("acres")):
            styles[(i, 1)] = "$text-warning"
    return Grid(
        [
            "Manor",
            "Acres",
            "Demesne",
            "Rented",
            "Villeins",
            "Waste",
            "Yield",
            "By custom",
        ],
        rows,
        list(range(len(rows))),
        "No manors listed: a manor is about 600 acres and yields its lord 20 "
        f"pounds a year ({LOM} p. 72).",
        styles=styles,
        caps=[20, 6, 7, 6, 8, 6, 5, 0],
        stretch=7,
    )


def _tick(held: bool, words: str, note: str = "") -> str:
    tail = f" [dim]({escape(note)})[/]" if note else ""
    if held:
        return f"[$text-success]{BULLET}[/] {escape(words)}{tail}"
    return f"[dim]– {escape(words)}[/]"


def manor_info(_saga: Saga, holder: Neighbour, row: int) -> str:
    listed = manor_list(holder)
    if row >= len(listed):
        return ""
    m = listed[row]
    lines: list[str] = []
    head = [f"{_acres(m.get('acres')) or '?'} acres", m.get("farming") or FARMING[0]]
    if m.get("allod"):
        head.append("an allod: no lord above it")
    lines.append(f"[i]{escape(' · '.join(head))}[/]")
    if unusual_size(m.get("acres")):
        lines.append(
            "[$text-warning]More than a third off the usual 600 acres "
            f"({LOM} p. 72).[/]"
        )
    if m.get("note"):
        lines.append(escape(m.get("note", "")))
    custom = by_custom(m)
    lines.append(
        f"[$label]Yield:[/] [b]{manor_yield(m)} pounds[/] a year"
        + (
            f"; its {' and '.join(custom)} by custom already inside it "
            f"[dim]({LOM} p. 85)[/]"
            if custom
            else f" [dim]({LOM} p. 72)[/]"
        )
    )
    uses = [(label, m.get(key)) for key, label in LAND_USES]
    if any(isinstance(v, int) for _l, v in uses):
        lines.append(
            "[$label]Land[/] [dim](p. 75)[/]: "
            + ", ".join(
                f"{label.lower()} {_acres(v)}"
                for label, v in uses
                if isinstance(v, int)
            )
            + " acres"
        )
    holdings = [
        (word, m.get(key))
        for key, word in (
            ("hides", "hides"),
            ("virgates", "virgates"),
            ("bovates", "bovates"),
            ("cottars", "cottars"),
        )
    ]
    if any(isinstance(v, int) for _w, v in holdings):
        land = f"[$label]Peasant land[/] [dim]({LOM} p. 72)[/]: " + ", ".join(
            f"{w} [b]{_n(v)}[/]" for w, v in holdings
        )
        shares = spread(m)
        if shares is not None:
            land += (
                f"; {shares[0]}% virgaters, {shares[1]}% bovaters, {shares[2]}% "
                "cottars [dim](20/30/50 usual)[/]"
            )
        worth = peasant_worth(m)
        if worth:
            land += (
                f"; worth about {worth} pounds to the lord [dim](4 a hide, 1 a "
                "virgate)[/]"
            )
        lines.append(land)
    terrain = m.get("terrain") or "Open"
    usual = (
        ""
        if isinstance(m.get("sheep"), int)
        else f" (usual on {TERRAIN_WORDS.get(terrain, 'open land')})"
    )
    lines.append(
        f"[$label]Flock[/] [dim]({LOM} p. 76)[/]: [b]{flock(m):,}[/] demesne "
        f"sheep{usual}, two-thirds of the manor's {manor_sheep(m):,}; pigs about "
        f"{round(flock(m) * PIGS_PER_SHEEP):,}"
    )
    sown = crops(m)
    if sown:
        lines.append(
            f"[$label]Crops[/] [dim]({LOM} p. 76)[/]: "
            + "; ".join(
                f"{season} {acres:,} acres, {seed:,} bushels sown to {crop:,}"
                for season, acres, seed, crop in sown
            )
        )
    ticks = [_tick(bool(m.get(due_key(k))), name) for k, name, _w in DUES]
    lines.append("")
    lines.append(
        f"[$label]Manor court[/] [dim]({LOM} pp. 79-82)[/]:  " + "   ".join(ticks[:3])
    )
    lines += ["   ".join(ticks[3:6]), "   ".join(ticks[6:])]
    if m.get("court"):
        lines.append(escape(m.get("court", "")))
    return "\n".join(lines)


def manor_fields(
    _saga: Saga, _holder: Neighbour, manor: Manor | None
) -> list[DialogField]:
    m = cast(dict[str, Any], manor or {})
    found = [
        DialogField("name", "Name", "text", m.get("name", ""), required=True),
        DialogField(
            "acres",
            "Acres",
            "optint",
            m.get("acres", MANOR_ACRES if manor is None else None),
            hint="About 600, a third more or less (LoM p. 72).",
        ),
        DialogField(
            "farming",
            "Farmed as",
            "select",
            m.get("farming") or FARMING[0],
            options=pairs(FARMING),
            hint="Large fields suit heavy soils; a manor turned over to sheep "
            "needs few hands (pp. 72-73).",
        ),
        DialogField(
            "terrain",
            "Its land",
            "select",
            m.get("terrain") or "Open",
            options=[(TERRAIN_WORDS[k].capitalize(), k) for k in FLOCKS],
            hint="Sets the usual flock: 600 sheep, over 1,000 on marshland, 300 "
            "in wooded land (p. 76).",
        ),
        DialogField(
            "allod",
            "Held as an allod",
            "check",
            bool(m.get("allod")),
            hint="Held outright, with no lord above it (pp. 75, 85).",
        ),
    ]
    found += [
        DialogField(key, f"{label} (acres)", "optint", m.get(key))
        for key, label in LAND_USES
    ]
    found += [
        DialogField(
            "hides",
            "Hides",
            "optint",
            m.get("hides"),
            hint="120-144 acres each, 4 pounds to the lord (p. 72).",
        ),
        DialogField(
            "virgates",
            "Virgates",
            "optint",
            m.get("virgates"),
            hint="24-32 acres each; about 20% of families.",
        ),
        DialogField(
            "bovates",
            "Bovates",
            "optint",
            m.get("bovates"),
            hint="Half a virgate; about 30% of families.",
        ),
        DialogField(
            "cottars",
            "Cottars",
            "optint",
            m.get("cottars"),
            hint="Ten acres or less; about half of families.",
        ),
        DialogField(
            "sheep",
            "Demesne flock (sheep)",
            "optint",
            m.get("sheep"),
            placeholder="(the usual for its land)",
        ),
        DialogField(
            "winter",
            "Winter crop (acres)",
            "optint",
            m.get("winter"),
            hint="Sown at 2 bushels an acre, reaps 8 (p. 76).",
        ),
        DialogField(
            "spring",
            "Spring crop (acres)",
            "optint",
            m.get("spring"),
            hint="Sown at 4 bushels an acre, reaps 16 (p. 76).",
        ),
        DialogField(
            "mill",
            "A mill by custom",
            "check",
            bool(m.get("mill")),
            hint="Already inside its 20 pounds (p. 85).",
        ),
        DialogField("bakery", "A bakery by custom", "check", bool(m.get("bakery"))),
    ]
    found += [
        DialogField(due_key(k), name, "check", bool(m.get(due_key(k))), hint=words)
        for k, name, words in DUES
    ]
    found += [
        DialogField(
            "court",
            "The dues in words",
            "text",
            m.get("court", ""),
            placeholder="e.g. heriot the best beast; tallage commuted to 2 pounds",
        ),
        DialogField("note", "Note", "text", m.get("note", "")),
    ]
    return found


def _manor_problem(values: dict[str, Any]) -> str | None:
    for key in (
        "acres",
        *(k for k, _l in LAND_USES),
        "hides",
        "virgates",
        "bovates",
        "cottars",
        "sheep",
        "winter",
        "spring",
    ):
        value = values.get(key)
        if isinstance(value, int) and value < 0:
            return "Acres and counts can't be fewer than none."
    acres = values.get("acres")
    used = sum(_n(values.get(k)) for k, _l in LAND_USES)
    if isinstance(acres, int) and used > acres:
        return f"Its land by use comes to {used:,} acres, more than its {acres:,}."
    return None


def manor_ops(saga: Saga, holder: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        holder,
        "manor_list",
        "Manor",
        manor_fields,
        lambda m: m["name"],
        validate=_manor_problem,
    )


# -- kennels, mews and stables --

KINDS: tuple[str, ...] = ("Kennels", "Mews", "Stables")
QUALITIES: tuple[str, ...] = ("Shoddy", "Standard", "Superior", "Excellent", "Royal")

#: Whose each quality befits (p. 60).
BEFITS: dict[str, str] = {
    "Shoddy": "an inn or farm",
    "Standard": "a knight",
    "Superior": "a noble",
    "Excellent": "a great noble",
    "Royal": "a king",
}

#: The Profession each establishment's specialist has (pp. 59-61).
PROFESSIONS: dict[str, str] = {
    "Kennels": "Profession: Master of Kennels",
    "Mews": "Profession: Falconer",
    "Stables": "Profession: Marshal",
}
ANIMALS: dict[str, str] = {"Kennels": "hounds", "Mews": "birds", "Stables": "horses"}
ANIMAL_HANDLING = "Animal Handling"

#: The Winter Roll's Ease Factor (p. 60), and the share of animals lost
#: each season its maintenance goes unpaid (p. 59).
WINTER_EASE = 9
UNPAID_LOSS = 0.15


@dataclass(frozen=True)
class Grade:
    """A row of the p. 60 tables: capacity, maintenance in pounds a year
    (a head for stables), staff, and the animals' Living Conditions."""

    capacity: int
    upkeep: int
    staff: int
    living: int
    per_head: bool = False


#: The Kennels, Mews and Stables tables (p. 60), the Excellent stables
#: as the errata moves them (errata p. 74). The Royal kennels' capacity is
#: "150+".
TABLES: dict[str, dict[str, Grade]] = {
    "Kennels": {
        "Shoddy": Grade(8, 0, 0, -1),
        "Standard": Grade(16, 1, 2, 0),
        "Superior": Grade(48, 5, 6, 1),
        "Excellent": Grade(80, 20, 12, 2),
        "Royal": Grade(150, 100, 36, 3),
    },
    "Mews": {
        "Shoddy": Grade(3, 0, 0, -1),
        "Standard": Grade(6, 0, 1, 0),
        "Superior": Grade(15, 5, 3, 1),
        "Excellent": Grade(30, 10, 5, 2),
        "Royal": Grade(100, 100, 10, 3),
    },
    "Stables": {
        "Shoddy": Grade(3, 0, 0, -1),
        "Standard": Grade(6, 1, 2, 0, per_head=True),
        "Superior": Grade(18, 2, 6, 1, per_head=True),
        "Excellent": Grade(40, 3, 12, 2, per_head=True),
        "Royal": Grade(250, 5, 36, 3, per_head=True),
    },
}

#: The stable a lord keeps at no cost, by his title (p. 59: a knight's
#: Standard, an earl's Excellent; the app takes a landed noble's to be a
#: noble's, Superior, and a baron's, count's or duke's a great noble's),
#: and a covenant's (anything better than Standard costs it).
FREE_STABLE: dict[str, str] = {
    "landed": "Superior",
    "baron": "Excellent",
    "count": "Excellent",
    "duke": "Excellent",
}
COVENANT_FREE_STABLE = "Standard"


class Establishment(TypedDict, total=False):
    """Kennels, mews or stables: their quality as built, the classes lost to
    failed Winter Rolls (`lowered`), the animals, whether this year's
    maintenance is unpaid, the specialist (and his Intelligence and
    Profession score, for the roll), and the last roll."""

    kind: Required[str]
    quality: str
    lowered: int
    animals: int | None
    unpaid: bool
    specialist: str
    intelligence: int | None
    profession: int | None
    roll: str
    note: str


def establishments(holder: Neighbour) -> list[Establishment]:
    return cast(list[Establishment], details_list(holder, "establishments"))


def _quality(entry: Establishment) -> str:
    found = entry.get("quality") or "Standard"
    return found if found in QUALITIES else "Standard"


def _kind(entry: Establishment) -> str:
    return entry["kind"] if entry.get("kind") in TABLES else "Stables"


def quality_now(entry: Establishment) -> str:
    """Its quality now: as built, less the classes lost to failed Winter
    Rolls (p. 60)."""
    at = QUALITIES.index(_quality(entry)) - max(0, _n(entry.get("lowered")))
    return QUALITIES[max(0, at)]


def grade(entry: Establishment) -> Grade:
    """The p. 60 row it works by now."""
    return TABLES[_kind(entry)][quality_now(entry)]


def is_covenant(holder: Neighbour) -> bool:
    return holder.kind == COVENANT_HOLDER


def free_stable(holder: Neighbour) -> str:
    """The best stable its owner keeps at no cost (p. 59)."""
    if is_covenant(holder):
        return COVENANT_FREE_STABLE
    return FREE_STABLE[title(holder)]


def upkeep(holder: Neighbour, entry: Establishment) -> int:
    """Its maintenance in pounds a year, by its quality as built (a failed
    Winter Roll leaves it unchanged, p. 61): stables a head, nothing for a
    stable that befits its owner; kennels and mews always pay (p. 59)."""
    kind, quality = _kind(entry), _quality(entry)
    row = TABLES[kind][quality]
    if kind == "Stables" and QUALITIES.index(quality) <= QUALITIES.index(
        free_stable(holder)
    ):
        return 0
    if row.per_head:
        return row.upkeep * _n(entry.get("animals"))
    return row.upkeep


def most_animals(entry: Establishment) -> int:
    """Its capacity and a third again of young and breeding stock (p. 58)."""
    capacity = grade(entry).capacity
    return capacity + capacity // 3


def needs_specialist(entry: Establishment) -> bool:
    """Superior and better need a specialist (p. 59)."""
    return QUALITIES.index(quality_now(entry)) >= QUALITIES.index("Superior")


def keeps_living(entry: Establishment) -> bool | None:
    """Whether its positive Living Conditions hold: a specialist with the
    Profession at twice it (p. 60); None with no positive modifier or no
    score entered."""
    living = grade(entry).living
    score = entry.get("profession")
    if living <= 0 or not isinstance(score, int):
        return None
    return score >= 2 * living


def season_loss(animals: int) -> int:
    """The animals an unpaid season loses: 15%, rounded up (p. 59)."""
    return math.ceil(animals * UNPAID_LOSS)


def one_class_down(quality: str) -> str:
    return QUALITIES[max(0, QUALITIES.index(quality) - 1)]


def estab_title(_saga: Saga, holder: Neighbour) -> str:
    return f"Establishments ({len(establishments(holder))})"


def estab_grid(_saga: Saga, holder: Neighbour) -> Grid:
    rows, styles = [], {}
    for i, e in enumerate(establishments(holder)):
        g, now = grade(e), quality_now(e)
        quality = now if now == _quality(e) else f"{now} (lowered)"
        animals = _n(e.get("animals"))
        cost = upkeep(holder, e)
        rows.append(
            [
                _kind(e),
                quality,
                f"{animals} of {g.capacity}",
                f"{cost} £" + (" unpaid" if e.get("unpaid") else ""),
                str(g.staff),
                f"{g.living:+d}",
                e.get("specialist") or "—",
            ]
        )
        if now != _quality(e):
            styles[(i, 1)] = "$text-warning"
        if animals > most_animals(e):
            styles[(i, 2)] = "$text-warning"
        if e.get("unpaid"):
            styles[(i, 3)] = "$text-error"
        if needs_specialist(e) and not e.get("specialist"):
            styles[(i, 6)] = "$text-error"
    return Grid(
        [
            "Establishment",
            "Quality",
            "Animals",
            "Upkeep",
            "Staff",
            "Living",
            "Specialist",
        ],
        rows,
        list(range(len(rows))),
        f"No kennels, mews or stables. Every noble keeps Standard stables as part "
        f"of his estate; kennels and mews must be built ({LOM} p. 58).",
        styles=styles,
        caps=[13, 18, 10, 12, 5, 6, 0],
        stretch=6,
    )


def estab_info(_saga: Saga, holder: Neighbour, row: int) -> str:
    listed = establishments(holder)
    if row >= len(listed):
        return ""
    e = listed[row]
    kind, built, now = _kind(e), _quality(e), quality_now(e)
    g = grade(e)
    animals = _n(e.get("animals"))
    lines = [
        f"[i]{now}, as befits {BEFITS[now]}: capacity {g.capacity} {ANIMALS[kind]}, "
        f"{g.staff} staff, Living Conditions {g.living:+d} [dim]({LOM} p. 60)[/][/]"
    ]
    if now != built:
        lines.append(
            f"[$text-warning]Down from {built} after a failed Winter Roll: a later "
            "success brings it back a class (p. 60).[/]"
        )
    lines.append(
        f"[$label]Animals:[/] {animals}"
        + (
            f" [$text-warning](more than its {g.capacity} and a third again of young "
            f"and breeding stock, {most_animals(e)})[/]"
            if animals > most_animals(e)
            else f" [dim](up to {most_animals(e)} with young and breeding stock, "
            "p. 58)[/]"
        )
    )
    cost = upkeep(holder, e)
    row_ = TABLES[kind][built]
    if cost == 0 and kind == "Stables" and row_.upkeep:
        why = (
            "a covenant keeps Standard stables free, and pays for better"
            if is_covenant(holder)
            else f"a stable that befits him costs nothing; his is "
            f"{free_stable(holder)} or less"
        )
        upkeep_line = f"[$label]Upkeep:[/] none [dim]({why}, p. 59)[/]"
    elif row_.per_head:
        upkeep_line = (
            f"[$label]Upkeep:[/] [b]{cost} pounds[/] a year [dim]({row_.upkeep} a "
            f"horse for {animals}, p. 60)[/]"
        )
    else:
        upkeep_line = (
            f"[$label]Upkeep:[/] [b]{cost} pounds[/] a year [dim](p. 60; kennels "
            "and mews always pay, p. 59)[/]"
        )
    if kind == "Stables" and built == "Excellent":
        upkeep_line += " [dim](the row as the errata moves it, errata p. 74)[/]"
    lines.append(upkeep_line)
    if is_covenant(holder) and cost:
        lines.append(
            "[dim]Not in the Treasury's figures: enter it with the covenant's "
            "expenditure if it pays it.[/]"
        )
    if e.get("unpaid"):
        lines.append(
            f"[$text-error]Upkeep unpaid: it fell a class at once, and loses 15% of "
            f"its {ANIMALS[kind]} (rounded up) each season until paid (p. 59).[/]"
        )
    specialist = e.get("specialist", "")
    profession = PROFESSIONS[kind]
    if specialist:
        score = e.get("profession")
        lines.append(
            f"[$label]Specialist:[/] {escape(specialist)}"
            + (f" [dim]({profession} {score})[/]" if isinstance(score, int) else "")
        )
    elif needs_specialist(e):
        lines.append(
            f"[$text-error]{now} needs a specialist with {profession} (p. 59).[/]"
        )
    keeps = keeps_living(e)
    if keeps is False:
        lines.append(
            f"[$text-warning]Its {g.living:+d} Living Conditions needs {profession} "
            f"{2 * g.living} or more, or someone with Animal Handling "
            f"{3 * g.living} giving it a season a year (p. 60).[/]"
        )
    total = _n(e.get("intelligence")) + _n(e.get("profession"))
    lines.append(
        f"[$label]Winter Roll:[/] stress die + Intelligence + {profession} or "
        f"{ANIMAL_HANDLING} against {WINTER_EASE}"
        + (
            f": the specialist's {total} needs a die of [b]{max(WINTER_EASE - total, 1)}+[/]"
            if specialist and isinstance(e.get("profession"), int)
            else ""
        )
        + " [dim](pp. 60-61)[/]"
    )
    if e.get("roll"):
        lines.append(f"[dim]{escape(e.get('roll', ''))}[/]")
    if e.get("note"):
        lines.append(escape(e.get("note", "")))
    return "\n".join(lines)


def estab_fields(
    _saga: Saga, _holder: Neighbour, entry: Establishment | None
) -> list[DialogField]:
    e = cast(dict[str, Any], entry or {})
    return [
        DialogField(
            "kind",
            "Kind",
            "select",
            e.get("kind") or "Stables",
            options=pairs(KINDS),
            required=True,
        ),
        DialogField(
            "quality",
            "Quality",
            "select",
            e.get("quality") or "Standard",
            options=[(f"{q} ({BEFITS[q]})", q) for q in QUALITIES],
            required=True,
            hint="As built; a failed Winter Roll lowers it for a while (p. 60).",
        ),
        DialogField("animals", "Animals", "optint", e.get("animals")),
        DialogField(
            "unpaid",
            "This year's upkeep is unpaid",
            "check",
            bool(e.get("unpaid")),
            hint="It falls a class at once, and loses 15% of its animals each "
            "season until paid (p. 59).",
        ),
        DialogField(
            "specialist",
            "Specialist",
            "text",
            e.get("specialist", ""),
            placeholder="e.g. Ulrich the marshal",
            hint="Superior and better need one (p. 59).",
        ),
        DialogField(
            "intelligence", "His Intelligence", "optint", e.get("intelligence")
        ),
        DialogField(
            "profession",
            "His Profession score",
            "optint",
            e.get("profession"),
            hint="Marshal, Falconer or Master of Kennels: twice the Living "
            "Conditions keeps them (p. 60).",
        ),
        DialogField("note", "Note", "text", e.get("note", "")),
    ]


def _estab_problem(values: dict[str, Any]) -> str | None:
    animals = values.get("animals")
    if isinstance(animals, int) and animals < 0:
        return "Animals can't be fewer than none."
    return None


def estab_ops(saga: Saga, holder: Neighbour) -> SectionOps:
    """Add, Edit and Delete; marking the upkeep unpaid drops the quality a
    class at once (p. 59)."""
    base = list_ops(
        saga,
        holder,
        "establishments",
        "Establishment",
        estab_fields,
        lambda e: _kind(e),
        validate=_estab_problem,
    )

    def form(entry: Establishment | None) -> Form:
        def apply(values: dict[str, Any]) -> list[str] | None:
            was_unpaid = entry is not None and bool(entry.get("unpaid"))
            if entry is None:
                target = cast(Establishment, dict(values))
                establishments(holder).append(target)
            else:
                cast(dict[str, Any], entry).update(values)
                target = entry
            quality = _quality(target)
            if not values.get("unpaid") or was_unpaid or quality == QUALITIES[0]:
                return None
            target["quality"] = one_class_down(quality)
            return notes(
                f"Its upkeep unpaid, the {_kind(target).lower()} fall to "
                f"{target['quality']} at once ({LOM} p. 59)."
            )

        return Form(
            "Add an Establishment" if entry is None else "Edit an Establishment",
            lambda: estab_fields(saga, holder, entry),
            apply,
            validate=_estab_problem,
            save_label="Add" if entry is None else "Save",
        )

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(establishments(holder)[index]),
        remove=base.remove,
        rows=base.rows,
    )


# -- the Winter Roll --

WINTER_ROLL = "Winter Roll"


@dataclass(frozen=True)
class Husbandry:
    """The Winter Roll's terms: who rolls, with what, and the total."""

    who: str
    ability: str
    intelligence: int
    score: int

    @property
    def total(self) -> int:
        return self.intelligence + self.score


def husbandry(saga: Saga, entry: Establishment, values: dict[str, Any]) -> Husbandry:
    ability = (
        ANIMAL_HANDLING
        if values.get("ability") == "handling"
        else PROFESSIONS[_kind(entry)]
    )
    character: Character | None = saga.character(values.get("who") or "")
    if character is not None:
        return Husbandry(
            character.name,
            ability,
            character.characteristics.intelligence,
            scores.ability_level(character, ability),
        )
    return Husbandry(
        entry.get("specialist") or "The specialist",
        ability,
        _n(values.get("intelligence")),
        _n(values.get("score")),
    )


def winter_fields(saga: Saga, entry: Establishment) -> list[DialogField]:
    def no_sheet(values: dict[str, Any]) -> bool:
        return not values.get("who")

    return [
        DialogField(
            "who",
            "Who rolls",
            "select",
            None,
            options=[(escape(c.name), c.id) for c in saga.characters],
            allow_blank=True,
            placeholder="(the specialist, without a sheet)",
        ),
        DialogField(
            "ability",
            "With",
            "select",
            "profession",
            options=[
                (PROFESSIONS[_kind(entry)], "profession"),
                (ANIMAL_HANDLING, "handling"),
            ],
            required=True,
        ),
        DialogField(
            "intelligence",
            "Intelligence",
            "optint",
            entry.get("intelligence"),
            show_if=no_sheet,
        ),
        DialogField(
            "score", "Score in it", "optint", entry.get("profession"), show_if=no_sheet
        ),
    ]


def winter_live(saga: Saga, entry: Establishment) -> Any:
    def live(values: dict[str, Any]) -> str:
        h = husbandry(saga, entry, values)
        need = WINTER_EASE - h.total
        lines = [
            f"[b]{escape(_kind(entry))}[/]  [$label]{quality_now(entry)}[/]",
            f"Stress die + [b]{h.total}[/] [dim]= Intelligence {h.intelligence:+d} + "
            f"{escape(h.ability)} {h.score}[/]  against [b]{WINTER_EASE}[/]",
            f"Well run on a die of [b]{max(need, 1)} or more[/]"
            + (" (any roll but a botch)" if need <= 0 else "")
            + f"; a failure drops it a class, a botch is a catastrophe [dim]({LOM} "
            "pp. 60-61)[/].",
        ]
        if saga.current_season != "Winter":
            lines.append(
                f"[dim]It is rolled each winter; it is {saga.current_season} now.[/]"
            )
        return "\n".join(lines)

    return live


#: What a botched Winter Roll may bring (p. 61).
CATASTROPHES = "a fire, disease among the animals, theft, or a story to resolve"


def winter_roll(
    saga: Saga, holder: Neighbour, index: int, rng: random.Random | None = None
) -> Command:
    """More's Winter Roll on the chosen establishment (pp. 60-61): a
    success brings a lowered one back a class; a failure drops it a class,
    maintenance unchanged; a botch is a catastrophe besides."""
    listed = establishments(holder)
    if index >= len(listed):
        return Refuse(WINTER_ROLL, "Choose kennels, mews or stables first.")
    entry = listed[index]

    def apply(values: dict[str, Any]) -> list[str]:
        h = husbandry(saga, entry, values)
        die = dice.stress_die(rng or random.Random(), saga=saga)
        roll = dice.Roll(h.total, die, WINTER_EASE)
        shown = "a botch" if die.botched else str(die.value)
        before = quality_now(entry)
        lowered = _n(entry.get("lowered"))
        if roll.succeeded:
            entry["lowered"] = max(0, lowered - 1)
            outcome = (
                f"Well run: back to {quality_now(entry)}."
                if lowered
                else "Well run this year."
            )
        else:
            if QUALITIES.index(before) > 0:
                entry["lowered"] = lowered + 1
            outcome = (
                f"Poorly run: down to {quality_now(entry)} until a later success; "
                "its maintenance is unchanged."
            )
        entry["roll"] = (
            f"{saga.current_season} {saga.current_year}: {h.who}, die {shown} + "
            f"{h.total} = {roll.total} against {WINTER_EASE}"
            + (": a catastrophe" if die.botched else "")
        )
        lines = [
            f"The die shows {shown}: {h.total} + {shown} = {roll.total} against "
            f"{WINTER_EASE}.",
            outcome,
        ]
        if die.botched:
            lines.append(
                f"A botch: a catastrophe strikes the {_kind(entry).lower()}: "
                f"{CATASTROPHES} ({LOM} p. 61)."
            )
        return notes(*lines)

    return Form(
        f"{WINTER_ROLL}: {escape(_kind(entry))}",
        lambda: winter_fields(saga, entry),
        apply,
        live=winter_live(saga, entry),
        save_label="Roll",
        help_id=ESTABLISHMENTS_SECTION,
        inspector="The Winter",
    )


def season_losses(saga: Saga) -> list[SeasonRecordLine]:
    """Each establishment whose upkeep is unpaid loses 15% of its animals
    (rounded up) as the season ends (p. 59): a line for each."""
    holders: list[tuple[Neighbour, str | None]] = [
        (n, None) for n in saga.neighbours if n.details.get("establishments")
    ]
    holders += [
        (manors_of(c), c.id) for c in saga.covenants if c.manors.get("establishments")
    ]
    lines = []
    for holder, covenant_id in holders:
        for entry in establishments(holder):
            animals = _n(entry.get("animals"))
            if not entry.get("unpaid") or not animals:
                continue
            lost = season_loss(animals)
            entry["animals"] = animals - lost
            lines.append(
                SeasonRecordLine(
                    "",
                    holder.name,
                    covenant_id,
                    "Upkeep unpaid",
                    _kind(entry),
                    f"Lost {lost} of {animals} {ANIMALS[_kind(entry)]} ({LOM} p. 59).",
                )
            )
    return lines


# -- the household --

INHERITANCE: dict[str, str] = {
    "Primogeniture": "all to the heir he names, or the eldest, or the strongest "
    "his liege chooses",
    "Divided among sons": "his lands split between his sons",
}
#: The household's usual size (p. 9).
HOUSEHOLDS = (
    "a lord of the manor about 10, a landed knight 16, a banneret 24, a baron "
    "40, an earl 140"
)
WIDOWS_SHARE = "a third of his estate for her support, likely lost if she remarries"


class Household(TypedDict, total=False):
    """A lord's household: its size, his mesnie, his heirs, the custom his
    lands pass by, and his hunting rights."""

    retinue: int | None
    mesnie: str
    heirs: str
    custom: str
    hunting: str


def household(holder: Neighbour) -> Household:
    found = holder.details.setdefault("household", {})
    if not isinstance(found, dict):
        raise ValueError(f"A lord's household should be a mapping, not {found!r}.")
    return cast(Household, found)


def household_facts(saga: Saga, holder: Neighbour) -> list[Fact]:
    h = household(holder)
    size = h.get("retinue")
    custom = h.get("custom") or ""
    liege = saga.neighbour(holder.answers_to)
    relief = (
        f"relief {lords.relief(holder)} pounds to {liege.name}"
        if liege is not None
        else "no liege to pay relief to"
    )
    return [
        Fact(
            "Retinue",
            (f"{size}: " if isinstance(size, int) else "") + h.get("mesnie", ""),
        ),
        Fact("Heirs", h.get("heirs", "")),
        Fact(
            "Inheritance",
            f"{custom}: {INHERITANCE[custom]}; {relief}"
            if custom in INHERITANCE
            else relief,
        ),
        Fact("Hunting", h.get("hunting", "")),
    ]


def household_text(_saga: Saga, holder: Neighbour) -> str:
    size = household(holder).get("retinue")
    usual = f"[dim]Households run {HOUSEHOLDS} ({LOM} p. 9)"
    if isinstance(size, int):
        return usual + ".[/]"
    return usual + "; his knights of the mesnie are counted in it (p. 11).[/]"


def household_fields(holder: Neighbour) -> list[DialogField]:
    h = household(holder)
    return [
        DialogField(
            "retinue",
            "Household (people)",
            "optint",
            h.get("retinue"),
            hint=f"Loosely, {HOUSEHOLDS} (p. 9).",
        ),
        DialogField(
            "mesnie",
            "Mesnie",
            "text",
            h.get("mesnie", ""),
            placeholder="e.g. 6 knights and 10 serjeants, 12 servants",
            hint="His household knights: a wealthy lord has eight to ten (p. 11).",
        ),
        DialogField(
            "heirs",
            "Heirs",
            "text",
            h.get("heirs", ""),
            placeholder="e.g. Dieter (14), then Berthold (11)",
        ),
        DialogField(
            "custom",
            "His lands pass by",
            "select",
            h.get("custom") or None,
            options=pairs(tuple(INHERITANCE)),
            allow_blank=True,
            placeholder="(not said)",
            hint="With no son, they are divided between his daughters (p. 10).",
        ),
        DialogField(
            "hunting",
            "Hunting rights",
            "text",
            h.get("hunting", ""),
            placeholder="e.g. free warren on all five manors; a chase by grant",
            hint="Warrens, chases and parks are his alone; forests the king's "
            "(pp. 48, 79).",
        ),
    ]


def _household_problem(values: dict[str, Any]) -> str | None:
    size = values.get("retinue")
    if isinstance(size, int) and size < 0:
        return "A household can't be fewer than none."
    return None


def edit_household(_saga: Saga, holder: Neighbour) -> Command:
    return Form(
        "Edit the Household",
        lambda: household_fields(holder),
        lambda values: cast(dict[str, Any], household(holder)).update(values),
        validate=_household_problem,
    )


# -- Settle an Inheritance --

SETTLE = "Settle an Inheritance"


def _first_heir(holder: Neighbour) -> str:
    heirs = household(holder).get("heirs") or ""
    first = heirs.replace(" then ", ",").split(",")[0].strip()
    return first.split(" (")[0].strip()


def settle_fields(holder: Neighbour) -> list[DialogField]:
    def divided(values: dict[str, Any]) -> bool:
        return values.get("custom") != "Primogeniture"

    return [
        DialogField(
            "heir",
            "Heir",
            "text",
            _first_heir(holder),
            required=True,
            hint="Who holds the lands now; he becomes the record's ruler.",
        ),
        DialogField(
            "custom",
            "By",
            "select",
            household(holder).get("custom") or "Primogeniture",
            options=[
                ("Primogeniture", "Primogeniture"),
                ("Divided among sons", "Divided among sons"),
                ("Divided among daughters (no son)", "Divided among daughters"),
            ],
            required=True,
        ),
        DialogField(
            "share",
            "Heirs sharing the lands",
            "optint",
            2,
            show_if=divided,
        ),
        DialogField(
            "widow",
            "A widow survives him",
            "check",
            False,
            hint=f"She keeps {WIDOWS_SHARE} (p. 11).",
        ),
        DialogField("note", "Note", "text", "", placeholder="e.g. died at Bouvines"),
    ]


def _settle_problem(values: dict[str, Any]) -> str | None:
    share = values.get("share")
    if values.get("custom") != "Primogeniture" and (
        not isinstance(share, int) or share < 1
    ):
        return "Say how many share the lands."
    return None


def settle(saga: Saga, holder: Neighbour, values: dict[str, Any]) -> list[str]:
    """The heir takes the lands (p. 10): he becomes the record's ruler, the
    relief owed his liege and the widow's third are noted, and the Diary
    keeps it."""
    heir = str(values.get("heir") or "").strip()
    custom = str(values.get("custom") or "Primogeniture")
    before = holder.ruler or holder.name
    holder.ruler = heir
    lines = [f"{heir} inherits from {before} ({custom.lower()})."]
    listed = manor_list(holder)
    count = len(listed) or lords.manors(holder)
    share = values.get("share")
    if custom != "Primogeniture" and isinstance(share, int) and share > 1:
        lines.append(
            f"The {count} manors are divided between {share} heirs, about "
            f"{count // share} each: give each heir's manors a record of their own "
            f"({LOM} p. 10)."
        )
    liege = saga.neighbour(holder.answers_to)
    if liege is not None:
        lines.append(f"He owes {liege.name} relief of {lords.relief(holder)} pounds.")
    if values.get("widow"):
        lines.append(f"The widow keeps {WIDOWS_SHARE} ({LOM} p. 11).")
    note = str(values.get("note") or "").strip()
    place_events.diary(holder).append(
        {
            "year": saga.current_year,
            "season": saga.current_season,
            "text": " ".join([*lines[:1], note]).strip(),
        }
    )
    lines.append("Edit the Household to name his heirs now.")
    return notes(*lines)


def settle_form(saga: Saga, holder: Neighbour) -> Command:
    return Form(
        SETTLE,
        lambda: settle_fields(holder),
        lambda values: settle(saga, holder, values),
        validate=_settle_problem,
        help_id=HOUSEHOLD_SECTION,
    )


# -- Buy a Manor --

BUY = "Buy a Manor"
#: Land costs 30 to 50 times its yearly income (p. 85).
PRICE_LOW, PRICE_HIGH = 30, 50


def buy_fields(saga: Saga, holder: Neighbour) -> list[DialogField]:
    found = [
        DialogField("name", "Name", "text", "", required=True),
        DialogField("acres", "Acres", "optint", MANOR_ACRES),
        DialogField(
            "price",
            "Price (pounds)",
            "int",
            40 * lords.MANOR_INCOME,
            hint=f"30 to 50 times its {lords.MANOR_INCOME} pounds a year (LoM p. 85).",
        ),
    ]
    covenant = holder_covenant(saga, holder)
    if covenant is not None:
        found.append(
            DialogField(
                "pay",
                f"Pay it from the covenant's Wealth ({covenant.economics.wealth} "
                "pounds)",
                "check",
                True,
            )
        )
    found.append(DialogField("note", "Note", "text", ""))
    return found


def buy_live(values: dict[str, Any]) -> str:
    price = _n(values.get("price"))
    times = price / lords.MANOR_INCOME
    lines = [
        f"[b]{price:,} pounds[/] is {times:g} times its {lords.MANOR_INCOME} pounds a "
        f"year; the book's range is {PRICE_LOW} to {PRICE_HIGH} "
        f"({PRICE_LOW * lords.MANOR_INCOME:,} to {PRICE_HIGH * lords.MANOR_INCOME:,}) "
        f"[dim]({LOM} p. 85)[/].",
        "[dim]Lower if the seller keeps some of its rights or you take on its "
        "dues; better for coin in hand than by installments; higher when the "
        "seller's lord takes a cut.[/]",
    ]
    if price and not PRICE_LOW <= times <= PRICE_HIGH:
        lines.append("[$text-warning]Outside the book's 30 to 50 times.[/]")
    return "\n".join(lines)


def buy(saga: Saga, holder: Neighbour, values: dict[str, Any]) -> list[str]:
    name = str(values.get("name") or "").strip()
    price = _n(values.get("price"))
    manor: Manor = {"name": name, "acres": values.get("acres")}
    if values.get("note"):
        manor["note"] = str(values["note"])
    manor_list(holder).append(manor)
    lines = [f"Bought the manor of {name} for {price:,} pounds."]
    covenant = holder_covenant(saga, holder)
    if covenant is not None:
        if values.get("pay"):
            covenant.economics.wealth -= price
            lines.append(
                f"Paid from its Wealth: {covenant.economics.wealth} pounds left."
            )
    else:
        place_events.diary(holder).append(
            {"year": saga.current_year, "season": saga.current_season, "text": lines[0]}
        )
    lines.append(
        "Its 20 pounds a year are its lord's from now"
        + (
            "; shown beside the income source, not added to it."
            if covenant is not None
            else "."
        )
    )
    return notes(*lines)


def _buy_problem(saga: Saga, holder: Neighbour, values: dict[str, Any]) -> str | None:
    price = values.get("price")
    if not isinstance(price, int) or price <= 0:
        return "Say what it costs."
    covenant = holder_covenant(saga, holder)
    if covenant is not None and values.get("pay") and price > covenant.economics.wealth:
        return f"The covenant has only {covenant.economics.wealth} pounds."
    return None


def buy_form(saga: Saga, holder: Neighbour) -> Command:
    return Form(
        BUY,
        lambda: buy_fields(saga, holder),
        lambda values: buy(saga, holder, values),
        validate=lambda values: _buy_problem(saga, holder, values),
        live=buy_live,
        save_label="Buy",
        help_id=MANORS_SECTION,
    )


# -- Assart --

ASSART = "Assart"


def assart_fields(manor: Manor) -> list[DialogField]:
    return [
        DialogField(
            "laborers",
            "Laborers",
            "int",
            1,
            hint="Strong laborers with proper tools, doing no other work.",
        ),
        DialogField("months", "Months", "int", 1),
        DialogField(
            "into",
            "The new land is",
            "select",
            "demesne",
            options=[(label, key) for key, label in LAND_USES if key != "waste"],
            required=True,
        ),
        DialogField(
            "acres",
            "Acres cleared",
            "optint",
            None,
            placeholder="(a laborer an acre a month)",
            hint="Type it for villeins clearing between their duties, much "
            "slower (LoM p. 84), or for magic.",
        ),
    ]


def cleared(values: dict[str, Any]) -> int:
    """The acres cleared: as typed, or an acre of lightly wooded land a
    laborer a month (p. 84)."""
    typed = values.get("acres")
    if isinstance(typed, int):
        return typed
    return _n(values.get("laborers")) * _n(values.get("months"))


def assart_live(manor: Manor) -> Any:
    def live(values: dict[str, Any]) -> str:
        acres = cleared(values)
        waste = _n(manor.get("waste"))
        return "\n".join(
            [
                f"[b]{acres} acres[/] of {escape(manor['name'])}'s waste "
                f"([dim]{waste:,} acres[/]) made {values.get('into') or 'demesne'} "
                f"[dim]({LOM} p. 84)[/].",
                "[dim]Clearing goes onto faerie lands, for a time (p. 78); land "
                "cleared by magic overnight alarms the neighbouring lords (p. 84).[/]",
            ]
        )

    return live


def _assart_problem(manor: Manor, values: dict[str, Any]) -> str | None:
    acres = cleared(values)
    if acres <= 0:
        return "Nothing would be cleared."
    waste = _n(manor.get("waste"))
    if acres > waste:
        return (
            f"{manor['name']} has only {waste:,} acres of waste: edit the manor to "
            "say how much."
            if not waste
            else f"{manor['name']} has only {waste:,} acres of waste."
        )
    return None


def assart(
    saga: Saga, holder: Neighbour, manor: Manor, values: dict[str, Any]
) -> list[str]:
    acres = cleared(values)
    into = str(values.get("into") or "demesne")
    manor["waste"] = _n(manor.get("waste")) - acres
    record = cast(dict[str, Any], manor)
    record[into] = _n(record.get(into)) + acres
    label = dict(LAND_USES)[into].lower()
    line = f"Assarted {acres} acres of {manor['name']}'s waste into {label}."
    if not is_covenant(holder):
        place_events.diary(holder).append(
            {"year": saga.current_year, "season": saga.current_season, "text": line}
        )
    return notes(line, f"Its waste is {manor['waste']:,} acres now.")


def assart_form(saga: Saga, holder: Neighbour, index: int) -> Command:
    listed = manor_list(holder)
    if index >= len(listed):
        return Refuse(ASSART, "Choose a manor first.")
    manor = listed[index]
    return Form(
        f"{ASSART}: {escape(manor['name'])}",
        lambda: assart_fields(manor),
        lambda values: assart(saga, holder, manor, values),
        validate=lambda values: _assart_problem(manor, values),
        live=assart_live(manor),
        save_label="Clear",
        help_id=MANORS_SECTION,
    )


# -- a covenant's manors --

#: The kind an adapted covenant's record carries.
COVENANT_HOLDER = "covenant"


def manors_of(covenant: Covenant) -> Neighbour:
    """The covenant's manors as a lord's record (an Adapter): its details
    are the covenant's manors themselves, so what the lists and forms
    change is kept on the covenant."""
    return Neighbour(
        id=covenant.id,
        name=covenant.name,
        kind=COVENANT_HOLDER,
        details=covenant.manors,
    )


def holder_covenant(saga: Saga, holder: Neighbour) -> Covenant | None:
    return saga.covenant(holder.id) if is_covenant(holder) else None


def _source(covenant: Covenant, key: str, holder: Neighbour) -> IncomeSource | None:
    wanted = holder.details.get(key)
    return next((s for s in covenant.economics.income_sources if s.id == wanted), None)


def _check_line(name: str, source: IncomeSource, listed: list[Manor]) -> list[str]:
    figure = sum(manor_yield(m) for m in listed)
    this_year = source.current_income
    gap = figure - this_year
    if gap > 0:
        compared = f"[$text-warning]{gap} pounds above the source this year[/]"
    elif gap < 0:
        compared = f"[$text-warning]{-gap} pounds below the source this year[/]"
    else:
        compared = "[$text-success]the source's figure exactly[/]"
    lines = [
        f"[$label]{name} source:[/] [b]{escape(source.name or '(unnamed)')}[/] "
        f"({source.type}): [b]{this_year} pounds[/] this year, after its Income "
        "Modification [dim](Covenants p. 57)[/]",
    ]
    if source.note.strip():
        lines.append(f"[dim]{escape(source.note.strip())}[/]")
    lines.append(
        f"[$label]Its manors' check:[/] {len(listed)} x {lords.MANOR_INCOME} = "
        f"[b]{figure} pounds[/] [dim]({LOM} p. 72)[/]: {compared}"
    )
    return lines


def check_text(saga: Saga, holder: Neighbour) -> str:
    """The manors beside the covenant's Agriculture source (and Livestock,
    for its sheep manors), as a check against the source's income this
    year; never added to the covenant's income."""
    covenant = holder_covenant(saga, holder)
    if covenant is None:
        return ""
    listed = manor_list(holder)
    farms = [m for m in listed if m.get("farming") != SHEEP]
    flocks = [m for m in listed if m.get("farming") == SHEEP]
    agriculture = _source(covenant, "agriculture_source", holder)
    livestock = _source(covenant, "livestock_source", holder)
    lines: list[str] = []
    if agriculture is not None:
        lines += _check_line("Agriculture", agriculture, farms if livestock else listed)
    if livestock is not None and flocks:
        lines += _check_line("Livestock", livestock, flocks)
    if not lines:
        lines.append(
            "[$label]Choose the source of income these manors describe (Edit): "
            "its Agriculture source, and its Livestock source for manors turned "
            "over to sheep.[/]"
        )
    lines.append(
        "[dim]Shown beside the source as a check, never added: the covenant's "
        "income is its sources' surplus after their operating costs (Covenants pp. "
        "56-58).[/]"
    )
    return "\n".join(lines)


def check_fields(saga: Saga, holder: Neighbour) -> list[DialogField]:
    covenant = holder_covenant(saga, holder)
    sources = covenant.economics.income_sources if covenant is not None else []
    options = [(escape(s.name or "(unnamed)"), s.id) for s in sources]
    return [
        DialogField(
            "agriculture_source",
            "Agriculture source",
            "select",
            holder.details.get("agriculture_source"),
            options=options,
            allow_blank=True,
            placeholder="(none)",
            hint="The source of income its farmed manors describe (Covenants p. 58).",
        ),
        DialogField(
            "livestock_source",
            "Livestock source",
            "select",
            holder.details.get("livestock_source"),
            options=options,
            allow_blank=True,
            placeholder="(none)",
            hint="A separate source, for manors turned over to sheep (p. 60).",
        ),
    ]


def edit_check(saga: Saga, holder: Neighbour) -> Command:
    return Form(
        "The Manors beside the Income",
        lambda: check_fields(saga, holder),
        lambda values: holder.details.update(values),
    )


def covenant_ops(saga: Saga, covenant: Covenant) -> dict[str, SectionOps]:
    """The covenant's Manors tab's lists and its check, edited as a lord's."""
    return tab_ops(saga, manors_of(covenant), COVENANT_TAB)


# -- the tabs --

MANORS_LIST = KindList(
    MANORS_SECTION, manors_title, manors_grid, manor_ops, manor_info, manors_header
)
ESTABLISHMENTS_LIST = KindList(
    ESTABLISHMENTS_SECTION, estab_title, estab_grid, estab_ops, estab_info
)
PANEL = "[dim]Choose a manor or an establishment to see it in full.[/]"

#: A lord's Manors tab, after his Fief.
LORD_TAB = KindTab(
    "Manors",
    "tab-nb-manors",
    (MANORS_LIST, ESTABLISHMENTS_LIST),
    blocks=(
        KindBlock(
            HOUSEHOLD_SECTION,
            "Household",
            household_text,
            edit_household,
            edit_label="Edit Household",
            after=ESTABLISHMENTS_SECTION,
            facts=household_facts,
        ),
    ),
    icon="place",
    panel=PANEL,
)

#: A covenant's Manors tab, after its Economics: the check beside its
#: income first.
COVENANT_TAB = KindTab(
    "Manors",
    "tab-cov-manors",
    (MANORS_LIST, ESTABLISHMENTS_LIST),
    blocks=(
        KindBlock(
            MANOR_CHECK_SECTION,
            "Beside the Income",
            check_text,
            edit_check,
            edit_label="Choose the Sources",
            gloss=True,
        ),
    ),
    icon="place",
    panel=PANEL,
)
