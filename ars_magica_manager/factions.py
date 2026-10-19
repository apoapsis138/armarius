"""A faction in detail (the core rules): what kind of faction it is, how
it decides, its rules, what it wants and what it offers, and how many
members it has. Its members who are characters are its links, on its
Standing tab.

Kept in Neighbour.details: "faction", "decides", "rules", "wants",
"offers" and "members"."""

from __future__ import annotations

from typing import Any

from .form_spec import DialogField, pairs
from .models import Neighbour, Saga
from .neighbour_lists import KindTab
from .sheets.character import Fact

FACTION_KINDS: tuple[str, ...] = (
    "Hedge coven",
    "Faerie court",
    "Gild",
    "Family",
    "Other",
)

DECIDES: tuple[str, ...] = ("Its leader", "A council", "A vote of all")


def facts(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    d = neighbour.details
    members = d.get("members")
    linked = len(neighbour.links)
    count = "" if members is None else str(members)
    if linked:
        count = f"{count}, {linked} linked" if count else f"{linked} linked"
    return [
        Fact("Faction", d.get("faction") or ""),
        Fact("Decides by", d.get("decides") or ""),
        Fact("Members", count),
        Fact("Its rules", d.get("rules", "")),
        Fact("Wants", d.get("wants", "")),
        Fact("Offers", d.get("offers", "")),
    ]


def fields(_saga: Saga, neighbour: Neighbour | None) -> list[DialogField]:
    """What New Faction and Edit add to the common fields."""
    d = neighbour.details if neighbour is not None else {}
    return [
        DialogField(
            "faction",
            "Faction",
            "select",
            d.get("faction") or None,
            options=pairs(FACTION_KINDS),
            allow_blank=True,
            placeholder="(not said)",
        ),
        DialogField(
            "decides",
            "Decides by",
            "select",
            d.get("decides") or None,
            options=pairs(DECIDES),
            allow_blank=True,
            placeholder="(not said)",
        ),
        DialogField("members", "Members", "optint", d.get("members")),
        DialogField(
            "rules",
            "Its rules",
            "text",
            d.get("rules", ""),
            placeholder="e.g. No member sells to a magus",
        ),
        DialogField("wants", "Wants", "text", d.get("wants", "")),
        DialogField("offers", "Offers", "text", d.get("offers", "")),
    ]


def problem(values: dict[str, Any]) -> str | None:
    if (values.get("members") or 0) < 0:
        return "Members can't be fewer than none."
    return None


TAB = KindTab("Faction", "tab-nb-faction", ())
