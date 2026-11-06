"""A custom: how a land lives, as a book's background describes it (its
honour and kin, its tongues and manners, its law, its trade and roads, a
treaty, a legend), with the rules it brings and the place it belongs to.

It is a neighbour that holds no attitude toward the troupe and has no
liege, as a place has none: it is the land's lore, listed in the
Region's Customs and Lore. Kept in Neighbour.details: "rules" (the
rules it brings, with their pages), "wants" and "offers" (what those
who keep it want of the troupe, and what they give)."""

from __future__ import annotations

from .form_spec import DialogField
from .models import Neighbour, Saga
from .neighbour_lists import KindTab
from .references import Fact


def facts(_saga: Saga, custom: Neighbour) -> list[Fact]:
    d = custom.details
    return [
        Fact("Its rules", d.get("rules", "")),
        Fact("Wants", d.get("wants", "")),
        Fact("Offers", d.get("offers", "")),
    ]


def fields(_saga: Saga, custom: Neighbour | None) -> list[DialogField]:
    """What New Custom and Edit add to the common fields."""
    d = custom.details if custom is not None else {}
    return [
        DialogField(
            "rules",
            "Its rules",
            "text",
            d.get("rules", ""),
            placeholder="e.g. Hof and ohof: a magus who shows hof gains",
            hint="What it means in play, with the book's page.",
        ),
        DialogField("wants", "Wants", "text", d.get("wants", "")),
        DialogField("offers", "Offers", "text", d.get("offers", "")),
    ]


TAB = KindTab("Custom", "tab-nb-custom", ())
