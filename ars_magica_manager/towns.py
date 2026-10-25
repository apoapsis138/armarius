"""A town in detail (City & Guild): its charter, council and population,
its guilds, and its fairs and markets; and what is worked out from them:
its size, how many guilds a town of its size has in the saga's year, and
a fair's yearly income roll.

A fair a covenant trades at is a source of income to it: a town's
yearly fair is a Lesser source (40 pounds), a county fair a Typical one
(100), a fair that draws traders from across Europe a Greater one (250).
Each year its income changes by the book's Income Modification: a
stress die picks the effect, and the effect's multiplier is applied.

Kept in Neighbour.details: "charter", "council", "population", "guilds"
(each a Guild; its list is town_guilds.py's) and "fairs" (each {"name",
"kind", "season", "band", "income", "covenant_id", "last"}). The charter
in full is town_charter.py's, the court town_court.py's."""

from __future__ import annotations

import random
from typing import Any, Required, TypedDict, cast

from . import economics
from .commands import Command, Confirm, Refuse, SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import INCOME_TYPE_DEFAULTS, SEASONS, Neighbour, Saga, details_list
from .neighbour_lists import KindList, KindTab, list_ops
from .references import Fact
from .rules import dice
from .sections import FAIRS_SECTION

#: Who holds a town's charter.
CHARTERS: tuple[str, ...] = ("Noble lord", "Church", "Commune", "Faerie", "Infernal")

#: A fair's size, as the source of income it is to a covenant.
FAIR_BANDS: tuple[str, ...] = ("Lesser", "Typical", "Greater")

FAIR_KINDS: tuple[str, ...] = ("Fair", "Market")

#: How many guilds a town of each size has (up to that population), in
#: 1220, 1250 and 1300 (City & Guild p. 54).
GUILD_COUNTS: tuple[tuple[int, tuple[str, str, str]], ...] = (
    (1000, ("0 to 1", "0 to 2", "1 to 3")),
    (10000, ("0 to 3", "3 to 5", "5 to 10")),
    (20000, ("5 to 10", "50 to 200", "100 to 300")),
    (50000, ("5 to 20", "50 to 300", "100 to 500")),
)


# -- the record --


def population(neighbour: Neighbour) -> int | None:
    found = neighbour.details.get("population")
    return int(found) if found else None


class Guild(TypedDict, total=False):
    """A guild of the town (town_guilds.py): its trade, its kind (craft,
    service or merchant), the Craft its members practise, its hall, its
    dean and officials, and its members by rank."""

    trade: Required[str]
    kind: str
    craft: str
    hall: str
    dean: str
    officials: int | None
    senior: int | None
    masters: int | None
    journeymen: int | None
    apprentices: int | None


def guilds(neighbour: Neighbour) -> list[Guild]:
    return cast(list[Guild], details_list(neighbour, "guilds"))


class Fair(TypedDict, total=False):
    """A fair or market of the town: when it is held, the covenant
    trading there (by id), its income band or a fixed income, and the
    last year's takings."""

    name: Required[str]
    kind: str
    season: str
    covenant_id: str
    band: str
    income: int | None
    last: str


def fairs(neighbour: Neighbour) -> list[Fair]:
    return cast(list[Fair], details_list(neighbour, "fairs"))


# -- worked out --


def size(people: int) -> str:
    """A small, medium or large town, or a city."""
    if people < 1000:
        return "Small town"
    if people < 4000:
        return "Medium town"
    if people < 20000:
        return "Large town"
    return "City"


def guilds_expected(people: int, year: int) -> str:
    """How many guilds a town of `people` has in `year`."""
    column = 0 if year < 1250 else 1 if year < 1300 else 2
    for most, counts in GUILD_COUNTS:
        if people <= most:
            return counts[column]
    return GUILD_COUNTS[-1][1][column]


def facts(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    """The town, as its tab shows it."""
    d = neighbour.details
    people = population(neighbour)
    found = [
        Fact("Charter", d.get("charter") or ""),
        Fact("Council", f"{d['council']} seats" if d.get("council") else ""),
    ]
    if people is not None:
        found += [
            Fact("Population", f"{people:,} ({size(people).lower()})"),
            Fact(
                "Guilds",
                f"{len(guilds(neighbour))} recorded; a town its size has "
                f"{guilds_expected(people, saga.current_year)} in "
                f"{saga.current_year}",
            ),
        ]
    else:
        found += [Fact("Population", ""), Fact("Guilds", str(len(guilds(neighbour))))]
    if d.get("charter") == "Commune":
        found.append(Fact("Taxes", "A commune keeps its own"))
    return found


# -- the form --


def fields(_saga: Saga, neighbour: Neighbour | None) -> list[DialogField]:
    """What New Town and Edit add to the common fields."""
    d = neighbour.details if neighbour is not None else {}
    return [
        DialogField(
            "charter",
            "Charter",
            "select",
            d.get("charter") or None,
            options=pairs(CHARTERS),
            allow_blank=True,
            placeholder="(none)",
            hint="Who granted it: a lord, the Church, or the townsmen "
            "themselves as a commune.",
        ),
        DialogField("council", "Council (seats)", "optint", d.get("council")),
        DialogField(
            "population",
            "Population",
            "optint",
            d.get("population"),
            hint="Most towns hold only a few hundred.",
        ),
    ]


def problem(values: dict[str, Any]) -> str | None:
    for key, label in (("council", "A council"), ("population", "A population")):
        if (values.get(key) or 0) < 0:
            return f"{label} can't be fewer than none."
    return None


# -- fairs and markets --


def _trader(saga: Saga, fair: Fair) -> str:
    covenant = saga.covenant(fair.get("covenant_id"))
    return covenant.name if covenant is not None else ""


def fair_income(fair: Fair) -> int:
    """The fair's yearly income to the covenant that trades there."""
    income = fair.get("income")
    if income is None:
        return INCOME_TYPE_DEFAULTS.get(fair.get("band", "Lesser"), 40)
    return int(income)


def fairs_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Fairs and Markets ({len(fairs(neighbour))})"


def fairs_grid(saga: Saga, neighbour: Neighbour) -> Grid:
    """Each fair and market: when, and for a fair a covenant trades at,
    what it brings in and its last roll."""
    rows = []
    for fair in fairs(neighbour):
        traded = _trader(saga, fair)
        rows.append(
            [
                fair["name"],
                fair.get("kind", "Fair"),
                fair.get("season") or "",
                traded,
                f"{fair_income(fair)} pounds" if traded else "",
                fair.get("last", ""),
            ]
        )
    return Grid(
        ["Name", "Kind", "Season", "Traded at by", "Income", "Last roll"],
        rows,
        list(range(len(rows))),
        "No fairs or markets recorded.",
        caps=[22, 6, 6, 16, 10, 0],
    )


def fair_fields(
    saga: Saga, _neighbour: Neighbour, fair: Fair | None
) -> list[DialogField]:
    f = fair or {}
    return [
        DialogField("name", "Name", "text", f.get("name", ""), required=True),
        DialogField(
            "kind",
            "Kind",
            "select",
            f.get("kind", "Fair"),
            options=pairs(FAIR_KINDS),
            required=True,
        ),
        DialogField(
            "season",
            "Season",
            "select",
            f.get("season") or None,
            options=pairs(SEASONS),
            allow_blank=True,
            placeholder="(all year)",
        ),
        DialogField(
            "covenant_id",
            "Traded at by",
            "select",
            f.get("covenant_id"),
            options=[(escape(c.name), c.id) for c in saga.covenants],
            allow_blank=True,
            placeholder="(no covenant)",
            hint="A covenant that holds it as a source of income.",
        ),
        DialogField(
            "band",
            "Size",
            "select",
            f.get("band", "Lesser"),
            options=[
                ("Lesser: a town's yearly fair", "Lesser"),
                ("Typical: a county fair", "Typical"),
                ("Greater: draws traders from across Europe", "Greater"),
            ],
            required=True,
        ),
        DialogField(
            "income",
            "Income (pounds a year)",
            "optint",
            f.get("income"),
            hint="Blank for its size's: 40, 100 or 250.",
        ),
    ]


def _fair_problem(values: dict[str, Any]) -> str | None:
    if (values.get("income") or 0) < 0:
        return "Income can't be less than none."
    return None


def fair_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        neighbour,
        "fairs",
        "Fair or Market",
        fair_fields,
        lambda f: f["name"],
        validate=_fair_problem,
    )


def effect_of(die: dice.DieResult) -> str:
    """The Income Modification a stress die picks."""
    if die.botched:
        return "Slump"
    value = die.value
    if value == 0:
        return "Contraction"
    if value <= 2:
        return "Stagnation"
    if value <= 8:
        return "Status Quo"
    if value == 9:
        return "Growth"
    if value < 20:
        return "Expansion"
    return "Boom"


def roll_fair(
    saga: Saga, neighbour: Neighbour, index: int, rng: random.Random | None = None
) -> Command:
    """More's Roll Income on the chosen fair: a stress die picks the year's
    Income Modification, and the new income is kept if accepted."""
    listed = fairs(neighbour)
    if index >= len(listed):
        return Refuse("Roll Income", "Choose a fair first.")
    fair = listed[index]
    if not fair.get("covenant_id"):
        return Refuse(
            "Roll Income",
            f"No covenant trades at {escape(fair['name'])}: edit it to say "
            "which, and its income can be rolled.",
        )
    die = dice.stress_die(rng or random.Random(), saga=saga)
    effect = effect_of(die)
    before = fair_income(fair)
    after = economics.projected_income(before, effect)
    shown = "a botch" if die.botched else str(die.value)

    def apply() -> None:
        fair["income"] = after
        fair["last"] = (
            f"{saga.current_year}: {effect} "
            f"{economics.income_multiplier_text(effect)}, {before} to {after}"
        )

    change = (
        f"stays at {before}" if after == before else f"goes from {before} to {after}"
    )
    return Confirm(
        f"{escape(fair['name'])}: the stress die shows {shown}, {effect} "
        f"({economics.income_multiplier_text(effect)}). Its income {change} "
        "pounds a year.",
        apply,
        yes_label="Keep",
        title="Roll a Fair's Income",
    )


#: The Town tab: what is worked out, then its fairs and markets. The
#: guilds have a tab of their own (town_guilds.GUILDS_TAB).
TAB = KindTab(
    "Town",
    "tab-nb-town",
    (KindList(FAIRS_SECTION, fairs_title, fairs_grid, fair_ops),),
)
