"""A church in detail (The Church, Realms of Power: The Divine): what
kind of church it is, its order, when worship began there (and ended),
and its relics; and what is worked out from them: its Dominion aura and
each relic's Might.

A church's aura comes from its kind (The Church): a chapel 3, a parish
church 4, a large church, a monastery or a cathedral 5. With the Dominion
growth option (Realms of Power: The Divine) the aura grows with the years
of worship instead: 3 when the site is consecrated, 4 after a year, and 5
after a decade, never above its kind's; once worship stops it fades to
nothing over as long as the site was in use. Whether or not the option
is on, a relic with a Faith score above 5 raises it by 1 for each point
above 5 (RoP: The Divine p. 12).

A relic has a Faith score, and as many Faith Points; its Divine Might is
10 for each point of it, and its bearer gains
as much Magic Resistance; touching it is worth +1 to an invocation of its
saint (Realms of Power: The Divine).

Kept in Neighbour.details: "church", "order", "founded", "abandoned" and
"relics" (each {"name", "saint", "faith"})."""

from __future__ import annotations

from typing import Any, Required, TypedDict, cast

from . import sourcebooks
from .commands import SectionOps
from .form_spec import DialogField
from .grids import Grid
from .models import Neighbour, Saga, details_list
from .neighbour_lists import KindList, KindTab, list_ops
from .references import Fact
from .rules import options
from .sections import RELICS_SECTION

#: The kinds of church, and each one's Dominion aura.
CHURCH_KINDS: dict[str, int] = {
    "Chapel": 3,
    "Parish church": 4,
    "Large urban church": 5,
    "Monastery or nunnery": 5,
    "Bishop's cathedral": 5,
    "Archbishop's cathedral": 5,
}

#: The Dominion growth option's key (rules.options).
GROWTH = "dominion_growth"


# -- the record --


def church_kind(neighbour: Neighbour) -> str:
    found = neighbour.details.get("church")
    return found if found in CHURCH_KINDS else "Parish church"


class Relic(TypedDict, total=False):
    """A relic the church holds: its name, its saint and its Faith score."""

    name: Required[str]
    saint: str
    faith: int


def relics(neighbour: Neighbour) -> list[Relic]:
    return cast(list[Relic], details_list(neighbour, "relics"))


def _faith(relic: Relic) -> int:
    return max(0, int(relic.get("faith") or 0))


# -- worked out --


def grown(base: int, years: int) -> int:
    """The aura a site of `base` has after `years` of weekly worship."""
    return min(base, 3 if years < 1 else 4 if years < 10 else 5)


def relic_bonus(saga: Saga, neighbour: Neighbour) -> int:
    """What its holiest relic adds to its aura: 1 for each point of Faith
    score above 5 (RoP: The Divine p. 12), with or without the growth
    option."""
    if not sourcebooks.in_play("RoP:D", sourcebooks.saga_books(saga)):
        return 0
    strongest = max((_faith(r) for r in relics(neighbour)), default=0)
    return max(0, strongest - 5)


def aura(saga: Saga, neighbour: Neighbour) -> int:
    """Its Dominion aura this year."""
    base = CHURCH_KINDS[church_kind(neighbour)]
    if not options.is_on(saga, GROWTH):
        return base + relic_bonus(saga, neighbour)
    founded = neighbour.details.get("founded")
    if founded is None:
        rating = base
    else:
        ended = neighbour.details.get("abandoned")
        until = saga.current_year if ended is None else min(ended, saga.current_year)
        rating = grown(base, until - founded)
        if ended is not None and saga.current_year > ended:
            span = max(1, ended - founded)
            faded = rating * (saga.current_year - ended) // span
            return max(0, rating - faded)
    return rating + relic_bonus(saga, neighbour)


def aura_text(saga: Saga, neighbour: Neighbour) -> str:
    rating = aura(saga, neighbour)
    if not options.is_on(saga, GROWTH):
        return f"Dominion {rating}"
    founded = neighbour.details.get("founded")
    ended = neighbour.details.get("abandoned")
    if ended is not None and saga.current_year > ended:
        return f"Dominion {rating}, fading since {ended}"
    if founded is not None:
        return f"Dominion {rating}, worship since {founded}"
    return f"Dominion {rating}"


def facts(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    d = neighbour.details
    return [
        Fact("Church", church_kind(neighbour)),
        Fact("Order", d.get("order", "")),
        Fact("Aura", aura_text(saga, neighbour)),
        Fact("Relics", str(len(relics(neighbour)))),
    ]


# -- the form --


def fields(saga: Saga, neighbour: Neighbour | None) -> list[DialogField]:
    """What New Church and Edit add to the common fields."""
    d = neighbour.details if neighbour is not None else {}
    found = [
        DialogField(
            "church",
            "Church",
            "select",
            d.get("church", "Parish church"),
            options=[(f"{k} (aura {a})", k) for k, a in CHURCH_KINDS.items()],
            required=True,
        ),
        DialogField(
            "order",
            "Order",
            "text",
            d.get("order", ""),
            placeholder="e.g. Benedictine, or the secular clergy",
        ),
    ]
    if sourcebooks.in_play("RoP:D", sourcebooks.saga_books(saga)):
        found += [
            DialogField(
                "founded",
                "Worship since (year)",
                "optint",
                d.get("founded"),
                hint="With the Dominion growth option, its aura grows from this year.",
            ),
            DialogField(
                "abandoned",
                "Abandoned in (year)",
                "optint",
                d.get("abandoned"),
                hint="Its aura fades once worship stops.",
            ),
        ]
    return found


def problem(values: dict[str, Any]) -> str | None:
    founded, ended = values.get("founded"), values.get("abandoned")
    if founded is not None and ended is not None and ended < founded:
        return "It can't be abandoned before worship began."
    return None


# -- relics --


def relics_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Relics ({len(relics(neighbour))})"


def relics_grid(saga: Saga, neighbour: Neighbour) -> Grid:
    """Each relic: its saint, Faith Points, Might, the Magic Resistance it
    gives its bearer and what touching it adds to invoking its saint."""
    divine = sourcebooks.in_play("RoP:D", sourcebooks.saga_books(saga))
    rows = []
    for relic in relics(neighbour):
        faith = _faith(relic)
        rows.append(
            [
                relic["name"],
                relic.get("saint", ""),
                str(faith),
                str(10 * faith),
                str(10 * faith),
                "+1" if divine else "",
            ]
        )
    return Grid(
        ["Relic", "Saint", "Faith", "Might", "Bearer's MR", "Touched"],
        rows,
        list(range(len(rows))),
        "No relics recorded.",
        caps=[30, 18, 5, 5, 11, 0],
    )


def relic_fields(
    _saga: Saga, _neighbour: Neighbour, relic: Relic | None
) -> list[DialogField]:
    r = relic or {}
    return [
        DialogField(
            "name",
            "Relic",
            "text",
            r.get("name", ""),
            required=True,
            placeholder="e.g. A finger of St. Patroclus",
        ),
        DialogField("saint", "Saint", "text", r.get("saint", "")),
        DialogField(
            "faith",
            "Faith score",
            "int",
            r.get("faith", 1),
            hint="As many Faith Points; Might is 10 times it. Most relics "
            "have 1 or 2, the greatest 5 or more (RoP: The Divine p. 45).",
        ),
    ]


def _faith_problem(values: dict[str, Any]) -> str | None:
    if (values.get("faith") or 0) < 0:
        return "A Faith score can't be below 0."
    return None


def relic_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        neighbour,
        "relics",
        "Relic",
        relic_fields,
        lambda r: r["name"],
        validate=_faith_problem,
    )


TAB = KindTab(
    "Church",
    "tab-nb-church",
    (KindList(RELICS_SECTION, relics_title, relics_grid, relic_ops),),
)
