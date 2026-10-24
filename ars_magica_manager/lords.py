"""A lord in detail (Lords of Men): his title, wealth and manors, his
seat and castles, and the Gratitude he owes the troupe; and what is
worked out from them: his income and what he has to spend, the army his
title raises, and what he owes his liege.

Where the book gives two figures for the same thing, the lower is used:
a landed noble has 2 pounds to spend (5 if wealthy), not 10 (20); a duke
raises 75 knights, not 125; scutage is 2 pounds a knight, not 3.

Kept in Neighbour.details: "title", "wealth", "manors", "seat",
"castles" (each {"name", "garrison", "defences", "supplies"}) and
"gratitude" (each {"who", "points", "why"}: "who" a character's id)."""

from __future__ import annotations

from typing import Any, Required, TypedDict, cast

from . import battles, place_events, references, sieges
from .armies import TITLES, WEALTH, army_of, title, wealth
from .commands import SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import Neighbour, Saga, details_list
from .neighbour_lists import KindList, KindTab, list_ops
from .references import Fact
from .sections import (
    BATTLES_SECTION,
    CASTLES_SECTION,
    DIARY_SECTION,
    GRATITUDE_SECTION,
    LORD_SIEGES_SECTION,
)

#: A manor's yearly income to its lord, in pounds.
MANOR_INCOME = 20

#: Scutage, in pounds a knight, paid in place of knight service.
SCUTAGE = 2

#: Days of knight service owed a year.
SERVICE_DAYS = 40

#: What a lord has left to spend each year, in pounds, by title and
#: wealth.
SURPLUS: dict[str, dict[str, int]] = {
    "landed": {"Poor": 0, "Average": 2, "Wealthy": 5},
    "baron": {"Poor": 0, "Average": 40, "Wealthy": 100},
    "count": {"Poor": 0, "Average": 100, "Wealthy": 250},
    "duke": {"Poor": 0, "Average": 250, "Wealthy": 500},
}

#: A landed noble's free seasons a year, by wealth.
FREE_SEASONS: dict[str, int] = {"Poor": 1, "Average": 2, "Wealthy": 3}


#: Gratitude: what each total earns from the lord, from Lords of Men's
#: advancement table.
GRATITUDE_STEPS: tuple[tuple[int, str], ...] = (
    (5, "knighthood or freedom"),
    (10, "a manor"),
    (20, "a barony"),
)


# -- the record --


def manors(neighbour: Neighbour) -> int:
    return max(0, int(neighbour.details.get("manors") or 0))


class Castle(TypedDict, total=False):
    """A castle the lord holds: its garrison, defences and supplies."""

    name: Required[str]
    garrison: str
    defences: str
    supplies: str


def castles(neighbour: Neighbour) -> list[Castle]:
    return cast(list[Castle], details_list(neighbour, "castles"))


class Gratitude(TypedDict, total=False):
    """What the lord owes a character (by id): the points and why."""

    who: str
    points: int
    why: str


def gratitude(neighbour: Neighbour) -> list[Gratitude]:
    return cast(list[Gratitude], details_list(neighbour, "gratitude"))


# -- worked out --


def income(neighbour: Neighbour) -> int:
    """His manors' yearly income, in pounds."""
    return manors(neighbour) * MANOR_INCOME


def surplus(neighbour: Neighbour) -> int:
    """What he has left to spend each year, in pounds."""
    return SURPLUS[title(neighbour)][wealth(neighbour)]


def relief(neighbour: Neighbour) -> int:
    """What his heir pays his liege to inherit: a year's income, at most 5
    pounds a manor, and at most 100 for a baron or greater."""
    owed = min(income(neighbour), 5 * manors(neighbour))
    return owed if title(neighbour) == "landed" else min(owed, 100)


def dues(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    """What he owes the neighbour he answers to: none if he answers to no
    one."""
    liege = saga.neighbour(neighbour.answers_to)
    if liege is None:
        return []
    knights = manors(neighbour)
    return [
        Fact(
            "Owes",
            f"{liege.name}: {knights} knight{'' if knights == 1 else 's'} for "
            f"{SERVICE_DAYS} days, or {knights * SCUTAGE} pounds scutage",
            references.refs(liege),
        ),
        Fact("Aids", f"{knights} pounds; relief {relief(neighbour)} pounds"),
    ]


def earns(points: int) -> str:
    """What `points` of Gratitude are enough for, and the next step:
    "Knighthood or freedom; 10 for a manor"."""
    reached = [what for need, what in GRATITUDE_STEPS if points >= need]
    ahead = next(
        ((need, what) for need, what in GRATITUDE_STEPS if points < need), None
    )
    parts = [reached[-1]] if reached else []
    if ahead is not None:
        parts.append(f"{ahead[0]} for {ahead[1]}")
    words = "; ".join(parts)
    return words[:1].upper() + words[1:]


def facts(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    """The fief, as the lord's tab shows it."""
    t, w = title(neighbour), wealth(neighbour)
    found = [
        Fact("Title", f"{TITLES[t]}, {w.lower()}"),
        Fact("Seat", neighbour.details.get("seat", "")),
        Fact("Manors", str(manors(neighbour))),
        Fact("Income", f"{income(neighbour)} pounds a year"),
        Fact("To spend", f"{surplus(neighbour)} pounds a year"),
    ]
    if t == "landed":
        free = FREE_SEASONS[w]
        found.append(Fact("Free time", f"{free} season{'' if free == 1 else 's'}"))
    found.append(Fact("Army", army_of(t, w).text()))
    return found + dues(saga, neighbour)


# -- the form --


def fields(_saga: Saga, neighbour: Neighbour | None) -> list[DialogField]:
    """What New Lord and Edit add to the common fields."""
    d = neighbour.details if neighbour is not None else {}
    return [
        DialogField(
            "title",
            "Title",
            "select",
            d.get("title", "landed"),
            options=[(name, key) for key, name in TITLES.items()],
            required=True,
        ),
        DialogField(
            "wealth",
            "Wealth",
            "select",
            d.get("wealth", "Average"),
            options=pairs(WEALTH),
            required=True,
        ),
        DialogField(
            "manors",
            "Manors",
            "int",
            d.get("manors", 1),
            hint="A baron holds about 20, a count 50.",
        ),
        DialogField(
            "seat", "Seat", "text", d.get("seat", ""), placeholder="e.g. Arnsberg"
        ),
    ]


def problem(values: dict[str, Any]) -> str | None:
    if (values.get("manors") or 0) < 0:
        return "Manors can't be fewer than none."
    return None


# -- castles --


def castles_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Castles ({len(castles(neighbour))})"


def castles_grid(_saga: Saga, neighbour: Neighbour) -> Grid:
    rows = [
        [c["name"], c.get("garrison", ""), c.get("defences", ""), c.get("supplies", "")]
        for c in castles(neighbour)
    ]
    return Grid(
        ["Castle", "Garrison", "Defences", "Supplies"],
        rows,
        list(range(len(rows))),
        "No castles recorded.",
        caps=[22, 16, 22, 0],
        stretch=3,
    )


def castle_fields(
    _saga: Saga, _neighbour: Neighbour, castle: Castle | None
) -> list[DialogField]:
    c = castle or {}
    return [
        DialogField("name", "Name", "text", c.get("name", ""), required=True),
        DialogField(
            "garrison",
            "Garrison",
            "text",
            c.get("garrison", ""),
            placeholder="e.g. 4 knights, 20 serjeants",
        ),
        DialogField(
            "defences",
            "Defences",
            "text",
            c.get("defences", ""),
            placeholder="e.g. stone keep, moat",
        ),
        DialogField(
            "supplies",
            "Supplies",
            "text",
            c.get("supplies", ""),
            placeholder="e.g. a season's siege",
        ),
    ]


def castle_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        neighbour,
        "castles",
        "Castle",
        castle_fields,
        lambda c: c["name"],
    )


# -- Gratitude --


def _who(saga: Saga, entry: Gratitude) -> str:
    character = saga.character(entry.get("who"))
    return character.name if character is not None else "(gone)"


def gratitude_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Gratitude ({len(gratitude(neighbour))})"


def gratitude_grid(saga: Saga, neighbour: Neighbour) -> Grid:
    """Who he owes, how much, and what it is enough for."""
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, entry in enumerate(gratitude(neighbour)):
        points = int(entry.get("points") or 0)
        if points >= GRATITUDE_STEPS[0][0]:
            styles[(index, 1)] = "$text-success"
        rows.append(
            [_who(saga, entry), str(points), earns(points), entry.get("why", "")]
        )
    return Grid(
        ["Owed to", "Points", "Earns", "For"],
        rows,
        list(range(len(rows))),
        "He owes no one Gratitude: a story that serves him earns 1 or 2 points, "
        "a renowned feat 5.",
        styles,
        caps=[20, 6, 40, 0],
        stretch=3,
    )


def gratitude_fields(
    saga: Saga, _neighbour: Neighbour, entry: Gratitude | None
) -> list[DialogField]:
    e = entry or {}
    return [
        DialogField(
            "who",
            "Owed to",
            "select",
            e.get("who") or (saga.characters[0].id if saga.characters else None),
            options=[(escape(c.name), c.id) for c in saga.characters],
            required=True,
        ),
        DialogField(
            "points",
            "Points",
            "int",
            e.get("points", 1),
            hint="1 or 2 for a story that serves him, 5 for a renowned feat.",
        ),
        DialogField(
            "why",
            "For",
            "text",
            e.get("why", ""),
            placeholder="e.g. Rescued his son from the Ruhr",
        ),
    ]


def gratitude_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        neighbour,
        "gratitude",
        "Debt of Gratitude",
        gratitude_fields,
        lambda e: f"the Gratitude owed to {_who(saga, e)}",
        validate=_points_problem,
    )


def _points_problem(values: dict[str, Any]) -> str | None:
    if (values.get("points") or 0) < 0:
        return "Points can't be fewer than none."
    return None


TAB = KindTab(
    "Fief",
    "tab-nb-fief",
    (
        KindList(CASTLES_SECTION, castles_title, castles_grid, castle_ops),
        KindList(GRATITUDE_SECTION, gratitude_title, gratitude_grid, gratitude_ops),
        KindList(
            BATTLES_SECTION,
            battles.LORD_TITLE,
            battles.LORD_GRID,
            battles.LORD_OPS,
            battles.info_for,
        ),
        KindList(
            LORD_SIEGES_SECTION,
            sieges.title,
            sieges.grid,
            sieges.ops,
            sieges.info_for,
        ),
    ),
)


def diary_grid(_saga: Saga, lord: Neighbour) -> Grid:
    return place_events.diary_rows(
        lord,
        "Nothing written yet: each Battle Event, and each fight or siege he is "
        "linked to, is written here.",
    )


#: His Diary: what befell him and his lands, kept as a place's is.
DIARY_TAB = KindTab(
    "Diary",
    "tab-nb-lord-diary",
    (
        KindList(
            DIARY_SECTION, place_events.diary_title, diary_grid, place_events.diary_ops
        ),
    ),
    after_standing=True,
)
