"""Gifted children, generated: a child with The Gift a magus might take
as apprentice, with a name, an age, the kind of Gift and a hint or two of
what they may become, from a random source the caller seeds so the same
children come back each time they are shown. Hibernia's Coill Trí owe the
Order seven at each meeting, one from each of their túatha; their tithe
is given out by hand or by simulated bidding (`bid`).

A child is a plain dict, so a meeting's record holds it as it is:
{"name", "sex", "age", "tuath", "ceannaire", "gift" (one of GIFTS),
"hints": [...], "origin", "false_gift"}.

Pattern: plain functions over a seeded random.Random and a names data
file; no class is needed."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from functools import cache
from typing import Any

from . import DATA_DIR
from .arts import FORMS, TECHNIQUES

NAMES_PATH = DATA_DIR / "irish_names.json"

#: The kinds of Gift, and how many in twenty children have each.
GIFTS: dict[str, int] = {"The Gift": 14, "Gentle Gift": 3, "Blatant Gift": 3}

#: The chance in twenty that a child offered has no true Gift, which only
#: a magus's examination shows.
FALSE_GIFT_IN_20 = 1

#: How many children the Coill Trí owe, one for each túath.
TITHE = 7

#: The ages a child may be offered at.
YOUNGEST, ELDEST = 5, 12

_TRAITS = (
    "Affinity with {art}",
    "Puissant {art}",
    "Second Sight",
    "Strong-Willed",
    "Book Learner",
    "Free Expression",
    "Inventive Genius",
    "Cautious Sorcerer",
    "Deficient {technique}",
    "Hedge-magic in the family",
    "Visions",
    "Restless",
)

_ORIGINS = (
    "the {kin} of a herdsman, whose cattle would not go near the child",
    "the {kin} of a fisher on a western lough, who calls the fish by name",
    "the {kin} of a smith, sent away after the forge fire answered a temper",
    "fostered by a druid's household since infancy",
    "an orphan the túath raised after a winter fever",
    "the {kin} of a minor chieftain, given up to settle a debt of honour",
    "the {kin} of a weaver, whose dreams come true too often",
    "found alone at a holy well, and never claimed",
    "the {kin} of a bard, who speaks with birds",
    "the {kin} of a farmer whose fields thrive and whose neighbours fear it",
)


@cache
def names() -> dict[str, tuple[str, ...]]:
    """The given names a child may have, by "male" and "female"."""
    data = json.loads(NAMES_PATH.read_text(encoding="utf-8"))
    return {sex: tuple(data[sex]) for sex in ("male", "female")}


def default_tuatha() -> list[tuple[str, str]]:
    """Seven unnamed túatha, for a Tribunal that has named none."""
    ordinals = ("First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh")
    return [(f"The {word} Túath", "") for word in ordinals]


def child(
    rng: random.Random, tuath: str = "", ceannaire: str = "", year: int = 0
) -> dict[str, Any]:
    """One Gifted child, offered by `tuath` through its `ceannaire`."""
    sex = rng.choice(("male", "female"))
    given = rng.choice(names()[sex])
    parent = rng.choice(names()["male"])
    kin = "son" if sex == "male" else "daughter"
    name = f"{given} {'mac' if sex == 'male' else 'ingen'} {parent}"
    gift = rng.choices(list(GIFTS), weights=list(GIFTS.values()))[0]
    hints = [
        trait.format(
            art=rng.choice(TECHNIQUES + FORMS), technique=rng.choice(TECHNIQUES)
        )
        for trait in rng.sample(_TRAITS, rng.randint(1, 2))
    ]
    age = rng.randint(YOUNGEST, ELDEST)
    found = {
        "name": name,
        "sex": sex,
        "age": age,
        "tuath": tuath,
        "ceannaire": ceannaire,
        "gift": gift,
        "hints": hints,
        "origin": rng.choice(_ORIGINS).format(kin=kin),
        "false_gift": rng.randint(1, 20) <= FALSE_GIFT_IN_20,
    }
    if year:
        found["born"] = year - age
    return found


def tithe(
    rng: random.Random, tuatha: list[tuple[str, str]], year: int = 0
) -> list[dict[str, Any]]:
    """A child from each túath (name, ceannaire), seven in all; missing
    túatha are filled with unnamed ones."""
    filled = list(tuatha[:TITHE]) + default_tuatha()[len(tuatha) : TITHE]
    return [child(rng, name, ceannaire, year) for name, ceannaire in filled]


def label(found: dict[str, Any]) -> str:
    """ "Áine ingen Domnaill, 9, Gentle Gift", or "..., 9, a false Gift"."""
    gift = "a false Gift" if found.get("false_gift") else found["gift"]
    return f"{found['name']}, {found['age']}, {gift}"


def summary(found: dict[str, Any]) -> str:
    """What is known of the child, in a sentence or two."""
    words = f"{found['name']}, aged {found['age']}: {found['origin']}."
    if found.get("hints"):
        words += " Signs of " + ", ".join(found["hints"]) + "."
    if found.get("false_gift"):
        words += " Examined, the child has no true Gift."
    return words


# -- the bidding --


@dataclass
class Bidder:
    """A covenant that may bid for the children: the magi it would give
    one to (those without an apprentice) and the vis it can pay."""

    covenant_id: str
    name: str
    masters: list[str]
    pawns: int


@dataclass
class Award:
    """Where one child went: the covenant and magus who won them and the
    pawns paid, with every bid made (covenant name, pawns), highest
    first. A child no one bid for, or with no true Gift, goes nowhere."""

    covenant_id: str | None = None
    master_id: str | None = None
    price: int = 0
    bids: list[tuple[str, int]] = field(default_factory=list)


def _wanted(found: dict[str, Any]) -> int:
    """How a Gift sways a bid: a Gentle Gift is sought, a Blatant shunned."""
    return {"Gentle Gift": 2, "Blatant Gift": -2}.get(found.get("gift", ""), 0)


def bid(
    rng: random.Random, children: list[dict[str, Any]], bidders: list[Bidder]
) -> list[Award]:
    """The children given out by bidding, in order: each covenant with a
    magus lacking an apprentice and vis to pay bids a roll of a die, two
    pawns for each such magus and a tenth of its vis, as much as it holds;
    the highest bid wins the child for its first such magus, paid from its
    vis. A child with no true Gift is turned away unbid."""
    awards: list[Award] = []
    for found in children:
        if found.get("false_gift"):
            awards.append(Award())
            continue
        bids: list[tuple[int, int, Bidder]] = []
        for order, bidder in enumerate(bidders):
            if not bidder.masters or bidder.pawns < 1:
                continue
            offer = (
                rng.randint(1, 10)
                + 2 * len(bidder.masters)
                + bidder.pawns // 10
                + _wanted(found)
            )
            offer = max(1, min(bidder.pawns, offer))
            bids.append((offer, -order, bidder))
        bids.sort(key=lambda b: (b[0], b[1]), reverse=True)
        if not bids:
            awards.append(Award())
            continue
        price, _, winner = bids[0]
        winner.pawns -= price
        awards.append(
            Award(
                winner.covenant_id,
                winner.masters.pop(0),
                price,
                [(b[2].name, b[0]) for b in bids],
            )
        )
    return awards
