"""A faction in detail (the core rules): what kind of faction it is, how
it decides, its rules, what it wants and what it offers, and how many
members it has. Its members who are characters are its links, on its
Standing tab. Its Diary is kept as a place's is (place_events).

A hedge coven may name the tradition its members follow (a tradition
catalog id), so its page says which tradition record they are played
from.

Kept in Neighbour.details: "faction", "decides", "tradition", "rules",
"wants", "offers", "members" and "diary"."""

from __future__ import annotations

from typing import Any

from . import memberships, place_events, traditions
from .form_spec import DialogField, pairs
from .grids import Grid
from .models import Neighbour, Saga
from .neighbour_lists import KindList, KindTab
from .references import Fact
from .sections import DIARY_SECTION

#: What a faction is. The books name no list of kinds; these sort what
#: the Tribunal books describe as companies of their own, Other last.
FACTION_KINDS: tuple[str, ...] = (
    "Hedge coven",
    "Faerie court",
    "Gild",
    "Family",
    "Hermetic group",
    "People or tribe",
    "Spirits and beings",
    "Faith or sect",
    "Council or assembly",
    "Military order",
    "Brigands and mercenaries",
    "Religious community",
    "Estate or rank",
    "Other",
)

DECIDES: tuple[str, ...] = ("Its leader", "A council", "A vote of all")


def facts(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    d = neighbour.details
    members = d.get("members")
    named = len(memberships.roster(neighbour))
    count = "" if members is None else str(members)
    if named:
        count = f"{count}, {named} named" if count else f"{named} named"
    return [
        Fact("Faction", d.get("faction") or ""),
        Fact("Decides by", d.get("decides") or ""),
        Fact("Tradition", tradition_name(d.get("tradition") or "")),
        Fact("Members", count),
        Fact("Its rules", d.get("rules", "")),
        Fact("Wants", d.get("wants", "")),
        Fact("Offers", d.get("offers", "")),
    ]


def tradition_name(tradition_id: str) -> str:
    """The tradition's name, or the id of one the catalog no longer has."""
    if not tradition_id:
        return ""
    found = traditions.find(tradition_id)
    return found.name if found is not None else tradition_id


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
        DialogField(
            "tradition",
            "Tradition",
            "select",
            d.get("tradition") or None,
            options=[(t.name, t.id) for t in traditions.all_traditions()],
            allow_blank=True,
            placeholder="(none)",
            hint="The hedge tradition its members follow, if any.",
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


TAB = KindTab("Faction", "tab-nb-faction", (memberships.MEMBERS,))


def diary_grid(_saga: Saga, faction: Neighbour) -> Grid:
    return place_events.diary_rows(
        faction, "Nothing written yet: add what the faction has done, season by season."
    )


#: Its Diary: what the faction has done, kept as a place's is.
DIARY_TAB = KindTab(
    "Diary",
    "tab-nb-faction-diary",
    (
        KindList(
            DIARY_SECTION,
            place_events.diary_title,
            diary_grid,
            place_events.diary_ops,
        ),
    ),
)
