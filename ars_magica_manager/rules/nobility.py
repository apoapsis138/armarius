"""Lords of Men's politics: what Gratitude buys, a lord's Affinity, and the
Noble Reputation (Lords of Men pp. 7-8, 21-22, 25-27).

- Gratitude is earned for service beyond a character's station (0 for a
  secret service, 1 for a story that favours the lord by the way, 2 for
  one aimed at him, 5 for a renowned feat) and redeemed for higher office,
  land or goods (p. 7). The Advancement Requirements Table (p. 8) prices
  each step: serf to freeman, warrior to knight, knight to bacheler and
  bacheler to carissimus 5; a manor, added manors, banneret to baron of a
  minor lord, appointment as baron and an officer of a greater baron 10;
  minor baron to baron of the king 20. Most steps also need a story event,
  a Reputation or Abilities, which are the troupe's to judge; a higher
  office brings the Virtues that suit it (Landed Noble, Great Noble,
  Temporal Influence; p. 7).
- Affinity Leadership (pp. 21-22): a bonus to social rolls among a
  region's nobles, land-holding churchmen and unchartered towns' councils:
  +1 a landholding noble of banneret stature, +2 an officer or baron of a
  minor lord, +3 an officer or minor baron of the king, +4 a greater
  baron, +5 the senior noble beneath the king in the region; halved
  (rounded down) where two warring affinities divide the area.
- Noble Reputation (pp. 25-26) is a fourth kind beside Local, Hermetic and
  Ecclesiastical. Entering feudal life starts it at 1; each season of great
  deeds notable to the landed class is 1 experience point, and some events
  give more (crusading +1 a season, knighting a squire one trained 1, a
  noble liege 3, a royal liege 6, study with a supernatural creature its
  Might / 5). The prize Reputation for a knight is Prudhomme. Rolls to have
  heard of a noble use the distance and status tables on p. 26.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from ..models import ScoredTrait
from .rounding import round_down

SOURCE = (
    "Lords of Men, The Gratitude System and Advancement Requirements Table, "
    "pp. 7-8; Affinity Leadership, pp. 21-22; Noble Reputation, pp. 25-26"
)

NOBLE = "Noble"
PRUDHOMME = "Prudhomme"


# -- Gratitude --


#: What a story earns, by how it served the lord (p. 7).
GRATITUDE_EARNED: dict[int, str] = {
    0: "a service the lord can't own to",
    1: "a story whose outcome favours the lord by the way",
    2: "a story aimed at the lord's good, with that outcome",
    5: "a feat renowned for its difficulty, done for the lord",
}


@dataclass(frozen=True)
class Reward:
    """One row of the Advancement Requirements Table: the change, the
    Gratitude it costs, what else it asks, what it costs the lord who grants
    it, and the Social Status Virtue it brings (if any)."""

    key: str
    change: str
    gratitude: int
    requires: str = ""
    granter: str = ""
    virtue: str = ""


#: The Advancement Requirements Table (p. 8), in its order, with a last
#: row for the money and goods a lord may pay instead (p. 7). The officer
#: posts are folded into "officer of a greater baron", whose 10 Gratitude
#: the table's footnote sets; the other officers' rows give only Abilities.
REWARDS: tuple[Reward, ...] = (
    Reward("freeman", "Serf to freeman", 5, "", "the serf's worth"),
    Reward(
        "knight",
        "Warrior to knight",
        5,
        "",
        "his gear, 5 pounds at least",
        "Knight",
    ),
    Reward(
        "bacheler",
        "Knight to bacheler",
        5,
        "a knight's Abilities, and the Abilities and Personality Traits that "
        "suit the lord's mesnie",
        "his ongoing support",
    ),
    Reward(
        "carissimus",
        "Bacheler to carissimus",
        5,
        "a bacheler already, and a story event",
        "nothing",
    ),
    Reward(
        "manor",
        "Bacheler to lord of the manor",
        10,
        "marriage to an heiress, land claimed in war, or land come back to the lord",
        "the manor's revenues",
        "Landed Noble",
    ),
    Reward(
        "manors",
        "Added manors",
        10,
        "a Reputation for loyalty to the lord, and land free by a line's "
        "end, war, assart or appanage",
        "the added manors' revenues",
    ),
    Reward(
        "minor_baron",
        "Banneret to baron of a minor lord",
        10,
        "at least 15 more manors, and a Reputation for loyalty to the lord",
        "nothing, unless the manors are the lord's",
    ),
    Reward(
        "royal_baron",
        "Minor baron to baron of the king",
        20,
        "notice by the king, service to a lord the king doesn't mind "
        "offending, and usually a successful treason against him",
        "nothing",
        "Great Noble",
    ),
    Reward(
        "baron",
        "Appointment as baron",
        10,
        "a suitable marriage and an officer's post",
        "nothing",
    ),
    Reward(
        "officer",
        "Officer of a greater baron or higher",
        10,
        "Landed Noble at least, a Reputation for loyalty to the lord, a "
        "vacant office and the office's own Abilities (a marshal Leadership "
        "5; a butler, steward or treasurer Profession: Steward 2)",
        "nothing, but the last holder loses the post",
        "Temporal Influence",
    ),
    Reward("goods", "Money, goods or a lesser favour", 1, "", "what he gives"),
)

REWARDS_BY_KEY: dict[str, Reward] = {r.key: r for r in REWARDS}


def reward_label(reward: Reward) -> str:
    return f"{reward.change} ({reward.gratitude} Gratitude)"


def redeem_problem(owed: int, reward: Reward, spent: int) -> str | None:
    """Why `spent` points of `owed` can't buy `reward`, or None."""
    if spent < 1:
        return "Spend at least 1 point."
    if spent > owed:
        return f"He owes only {owed} point{'' if owed == 1 else 's'}."
    if reward.key != "goods" and spent < reward.gratitude:
        return f"{reward.change} needs {reward.gratitude} Gratitude."
    return None


# -- Affinity --


#: Affinity bonuses by standing (p. 21), from none to the region's senior
#: noble.
AFFINITY: dict[int, str] = {
    0: "None: below banneret",
    1: "A landholding noble of banneret stature",
    2: "An officer or baron of a minor lord",
    3: "An officer or minor baron of the king",
    4: "A greater baron",
    5: "The senior noble under the king in the region",
}


def affinity_bonus(standing: int, divided: bool) -> int:
    """The Affinity bonus to social rolls among the region's landed class,
    halved, rounded down, where two warring affinities divide it."""
    bonus = max(0, min(5, standing))
    return round_down(bonus / 2) if divided else bonus


#: What the bonus helps with (p. 22).
AFFINITY_USES = (
    "mustering the local minor nobility, settling their disputes, "
    "swaying their advice, their attitude to the Church, and refereeing a "
    "tournament"
)


# -- Noble Reputation --


#: Experience points toward a Noble Reputation (p. 26), by what was done.
NOBLE_DEEDS: dict[str, tuple[str, int]] = {
    "season": ("A season of great deeds noted by the landed class", 1),
    "crusade": ("A season at war in a distant land (on top of the war's)", 1),
    "squire": ("Knighting a successful squire he trained", 1),
    "noble_liege": ("Gaining a noble liege", 3),
    "royal_liege": ("Gaining a royal liege", 6),
}


def noble_xp(done: Iterable[str], might: int = 0) -> int:
    """The experience points `done` (NOBLE_DEEDS keys) give, with study
    under a supernatural creature of Might `might` adding Might / 5 (taken
    as rounded down)."""
    return sum(NOBLE_DEEDS[k][1] for k in done if k in NOBLE_DEEDS) + round_down(
        max(0, might) / 5
    )


def is_noble(reputation: ScoredTrait) -> bool:
    return reputation.type == NOBLE or PRUDHOMME.casefold() in (
        reputation.name.casefold()
    )


def prudhomme_index(reputations: list[ScoredTrait]) -> int | None:
    """The Reputation tournaments read as his Prudhomme: one so named, else
    his highest good Noble Reputation; None for neither."""
    named = [
        i
        for i, r in enumerate(reputations)
        if PRUDHOMME.casefold() in r.name.casefold()
    ]
    if named:
        return named[0]
    noble = [i for i, r in enumerate(reputations) if r.type == NOBLE and r.score > 0]
    return max(noble, key=lambda i: reputations[i].score, default=None)


def prudhomme(reputations: list[ScoredTrait]) -> int:
    """His Prudhomme Reputation's score (0 for none)."""
    index = prudhomme_index(reputations)
    return max(0, reputations[index].score) if index is not None else 0


#: The Ease Factor of a roll to know of a noble, by distance (p. 26).
NOBLE_DISTANCE_EASE: dict[str, int] = {
    "Same shire or county": 3,
    "Adjoining counties": 6,
    "Same kingdom": 9,
    "Rival kingdom": 12,
}

#: Status modifiers to that roll: choose one (p. 26).
NOBLE_STATUS: dict[str, int] = {
    "A commoner in a noble's service": 6,
    "A landholder of lower status than the one rolling": 3,
    "A landholder of the same status": 0,
    "A landholder of higher status": -3,
    "A vassal of the one rolling": -6,
}

#: Further modifiers: all that apply (p. 26).
NOBLE_EXTRAS: dict[str, int] = {
    "A widow not holding in her own right, or a noble's heir": 3,
    "An acknowledged lover or bastard": 6,
}


def noble_roll_ease(distance: str, status: str, extras: Iterable[str] = ()) -> int:
    """The Ease Factor of a roll to know of a noble: the distance's, plus
    one status modifier and every extra that applies."""
    return (
        NOBLE_DISTANCE_EASE[distance]
        + NOBLE_STATUS.get(status, 0)
        + sum(NOBLE_EXTRAS[e] for e in extras if e in NOBLE_EXTRAS)
    )
