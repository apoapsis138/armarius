"""A demon built by the book (Realms of Power: The Infernal, Chapter Four:
The Infernal Legions, pp. 28-44): its order and rank, the Infernal Might
they allow, the traits and Powers every demon and its order share, and
what a True Name, its weakness and an Infernal aura do.

- Every demon has Infernal Might 1 or more and a Personality Trait for its
  sin, and no virtuous trait (p. 30). Its order sets the most Might it has
  without rank (Tempters, Accusers, Furies 20; Aerial Powers, Deluders,
  Avengers of Evil 25; Vessels of Iniquity, Spirits of Deceit, False Gods
  30), and a rank adds to it: Master +5, Lord +10, Duke +15, Prince +20,
  some ranks impossible in the lesser orders (p. 30).
- Its Hierarchy score is the highest of its Infernal Reputations and its
  rank's equivalent (Master 3, Lord 5, Duke 7, Prince 9) (p. 31).
- It buys physical Characteristics with as many points as its Might (n
  costs n(n+1)/2, a negative gives as much back), none below Might / 5 -
  10; its mental ones with 0 to 7 (p. 31).
- Every demon has Coagulation (1 point per 10 Might; an Infernal ghost
  has none, a Vessel of Iniquity Form of Wickedness instead), Obsession
  and Envisioning (pp. 31-32), and one weakness (p. 34); its order adds
  its own Personality Traits, Virtues and Powers (pp. 37-44).
- Learning its weakness: Int + Infernal Lore against 9 + Might / 5, 3
  less for a family's demon (p. 34). Its True Name is an Arcane
  Connection, +5 to the Penetration multiplier against it, and costs 5
  experience points of Infernal Lore (pp. 34-35). Second Sight sees it
  against 9 + the magnitude of its Might (p. 33). It regains all its
  Might in 24 - 2 x an Infernal aura hours, none in a Divine aura
  (pp. 35-36); its corpse holds a pawn of vis a magnitude of Might (p. 29).

The Definitive Edition's demons and the Tribunal books' aren't written
this way (p. 29), so a demon is checked only when its Order names one of
the nine; and a story's demons needn't balance: these are advice, never
refusals.

Pattern: the same shape as rules.faerie_build (one function per realm
over the creature, no new class).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Creature
from .creation_characteristics import cost
from .rounding import round_down, round_up

SOURCE = "Realms of Power: The Infernal, Chapter Four: The Infernal Legions, pp. 28-44"

INFERNAL = "Infernal"


@dataclass(frozen=True)
class Order:
    """One of the nine demonic orders: the most Might it has before rank,
    the ranks it can't hold, and what its demons share."""

    name: str
    most_might: int
    impossible: tuple[str, ...]
    traits: tuple[str, ...]
    powers: tuple[str, ...]
    virtues: tuple[str, ...] = ()
    #: The words its name is found by in a demon's Order.
    words: tuple[str, ...] = ()
    page: int = 0


ORDERS: tuple[Order, ...] = (
    Order(
        "False Gods",
        30,
        (),
        ("Proud +6",),
        ("Shroud the Stench of the Pit", "The Wealth of Nations", "His Master's Voice"),
        words=("false god", "pseudothe", "teraph"),
        page=37,
    ),
    Order(
        "Spirits of Deceit",
        30,
        (),
        ("Trustworthy -5", "Deceitful +6"),
        (
            "Change Form",
            "Trust of the Innocent",
            "Forked Tongue of the Serpent",
            "The Serpent's Oracle",
        ),
        words=("spirit of deceit", "spirits of deceit", "sheqer"),
        page=38,
    ),
    Order(
        "Vessels of Iniquity",
        30,
        (),
        ("Hateful +6", "Depraved +6"),
        ("Form of Wickedness", "Form of Man", "Contagious Obsession"),
        words=("vessel", "rephaim", "rephah"),
        page=39,
    ),
    Order(
        "Avengers of Evil",
        25,
        (),
        ("Merciful -3", "Relentless +5", "Passionless +4"),
        ("Punish the Sinner",),
        words=("avenger", "angel of punishment", "angels of punishment", "habbalah"),
        page=40,
    ),
    Order(
        "Deluders",
        25,
        (),
        ("Credible +3", "Sly +2"),
        ("Delusion",),
        virtues=("Puissant Guile",),
        words=("deluder", "praestigiator", "memun", "juggling impostor"),
        page=41,
    ),
    Order(
        "Aerial Powers",
        25,
        (),
        ("Untamable +5",),
        ("Elemental Control", "Recalcitrance"),
        words=("aerial power", "potestas", "gibbor"),
        page=42,
    ),
    Order(
        "Furies",
        20,
        ("Prince",),
        ("Wrathful +4", "Self-Controlled -6"),
        ("Waxing Tide of Humors", "Beserker Rage", "Endurance of the Enraged"),
        virtues=("Berserk",),
        words=("fury", "furies", "furia", "enim"),
        page=42,
    ),
    Order(
        "Accusers",
        20,
        ("Duke", "Prince"),
        ("Cruel +6",),
        ("Betrayal of the Heart", "Whispers Behind the Back"),
        words=("accuser", "criminator", "mastin"),
        page=43,
    ),
    Order(
        "Tempters",
        20,
        ("Duke", "Prince"),
        ("Selfish +5",),
        (),
        virtues=("Weak-Willed",),
        words=("tempter", "evil spirit", "tentator", "maligeni", "shed", "kakodaemon"),
        page=43,
    ),
)

#: Each rank: the Might it adds and the Reputation it equals (p. 30).
RANKS: dict[str, tuple[int, int]] = {
    "Master": (5, 3),
    "Lord": (10, 5),
    "Duke": (15, 7),
    "Prince": (20, 9),
}

#: The Powers every demon has (pp. 31-32).
COMMON_POWERS = ("Coagulation", "Obsession", "Envisioning")
#: An Infernal ghost: no Coagulation, no physical form (p. 36).
GHOST_WORDS = ("ghost",)
#: The virtues no demon shows of its own will (p. 30).
VIRTUOUS = (
    "faith",
    "faithful",
    "hope",
    "hopeful",
    "charity",
    "charitable",
    "prudence",
    "prudent",
    "temperance",
    "temperate",
    "fortitude",
    "justice",
    "just",
)
PHYSICAL = ("strength", "stamina", "dexterity", "quickness")
MENTAL = ("intelligence", "perception", "presence", "communication")
MENTAL_POINTS = 7

TRUE_NAME_XP = 5
TRUE_NAME_PENETRATION = 5
WEAKNESS_EASE, FAMILY_EASE = 9, 3
SECOND_SIGHT_EASE = 9


def is_demon(creature: Creature) -> bool:
    return creature.realm == INFERNAL


def order_of(creature: Creature) -> Order | None:
    """The order its Order names, None when it names none of the nine."""
    text = creature.order.casefold()
    for order in ORDERS:
        if order.name.casefold() in text or any(w in text for w in order.words):
            return order
    return None


def rank_of(creature: Creature) -> str:
    """The rank its Order names ("" with none)."""
    words = creature.order.replace(",", " ").split()
    return next((r for r in RANKS if r in words), "")


def is_ghost(creature: Creature) -> bool:
    return any(w in creature.order.casefold() for w in GHOST_WORDS)


def most_might(creature: Creature) -> int | None:
    """The most Infernal Might its order and rank allow (p. 30)."""
    order = order_of(creature)
    if order is None:
        return None
    return order.most_might + RANKS.get(rank_of(creature), (0, 0))[0]


def hierarchy(creature: Creature) -> int:
    """Its Hierarchy score: the highest of its Infernal Reputations and
    its rank's equivalent Reputation (p. 31)."""
    rank = RANKS.get(rank_of(creature), (0, 0))[1]
    reputations = [r.score for r in creature.reputations]
    return max([rank, *reputations])


def coagulation_cost(might: int) -> int:
    """Coagulation's cost: 1 Might Point per 10 Might, or fraction (p. 31)."""
    return max(1, round_up(might / 10))


def lowest_physical(might: int) -> int:
    """The lowest a demon's physical Characteristic may be (p. 31)."""
    return round_down(might / 5) - 10


def physical_points(creature: Creature) -> int:
    """What its physical Characteristics cost (p. 31)."""
    ch = creature.characteristics
    return sum(cost(getattr(ch, name)) for name in PHYSICAL)


def mental_points(creature: Creature) -> int:
    ch = creature.characteristics
    return sum(cost(getattr(ch, name)) for name in MENTAL)


def might_magnitude(might: int) -> int:
    return max(0, round_up(might / 5))


def weakness_ease(might: int, *, family: bool = False) -> int:
    """Int + Infernal Lore against this to know a demon's weakness (p. 34)."""
    return WEAKNESS_EASE + round_down(might / 5) - (FAMILY_EASE if family else 0)


def second_sight_ease(might: int) -> int:
    """Second Sight's Ease Factor to see a demon (p. 33)."""
    return SECOND_SIGHT_EASE + might_magnitude(might)


def hours_to_recover(aura_realm: str, aura: int) -> int | None:
    """The hours a demon takes to regain all its Might: a day, less 2 an
    hour of Infernal aura; never in a Divine aura (None) (pp. 35-36)."""
    if aura_realm == "Divine" and aura > 0:
        return None
    if aura_realm == INFERNAL:
        return max(1, 24 - 2 * max(0, aura))
    return 24


def corpse_vis(might: int) -> int:
    """The pawns of vis a slain demon's corpse typically holds (p. 29)."""
    return might_magnitude(might)


def _has_power(creature: Creature, name: str) -> bool:
    wanted = name.casefold()
    return any(wanted in p.name.casefold() for p in creature.powers)


def _trait_names(creature: Creature) -> set[str]:
    return {t.name.casefold() for t in creature.personality_traits}


def problems(creature: Creature) -> list[str]:
    """What a demon built by Realms of Power: The Infernal would have that
    this one lacks, or has that a demon can't (advice)."""
    order = order_of(creature)
    if not is_demon(creature) or order is None:
        return []
    found: list[str] = []
    rank = rank_of(creature)
    if rank in order.impossible:
        found.append(f"No demon of the {order.name} is a {rank} (p. 30).")
    top = most_might(creature)
    if creature.might < 1:
        found.append("Every demon has at least 1 Infernal Might (p. 30).")
    elif top is not None and creature.might > top:
        found.append(
            f"The {order.name}{' as a ' + rank if rank else ''} have Infernal "
            f"Might up to {top}, not {creature.might} (p. 30)."
        )
    if creature.hierarchy is not None and creature.hierarchy != hierarchy(creature):
        found.append(
            f"Its rank and Reputations make a Hierarchy of {hierarchy(creature)} "
            "(p. 31)."
        )
    if not creature.personality_traits:
        found.append("Every demon has a Personality Trait for its sin (p. 30).")
    virtuous = sorted(
        t.name
        for t in creature.personality_traits
        if t.score > 0 and t.name.casefold() in VIRTUOUS
    )
    if virtuous:
        found.append(f"No demon shows {', '.join(virtuous)} (p. 30).")
    names = _trait_names(creature)
    missing_traits = [
        t for t in order.traits if t.rsplit(" ", 1)[0].casefold() not in names
    ]
    if missing_traits:
        found.append(
            f"The {order.name} have {', '.join(missing_traits)} (p. {order.page})."
        )
    needed = [
        p
        for p in COMMON_POWERS
        if not (
            p == "Coagulation"
            and (is_ghost(creature) or order.name == "Vessels of Iniquity")
        )
    ]
    missing = [p for p in (*needed, *order.powers) if not _has_power(creature, p)]
    if missing:
        found.append(f"Missing Powers: {', '.join(missing)} (pp. 31-32, {order.page}).")
    if not creature.weakness:
        found.append("Every demon has a weakness (p. 34).")
    if not is_ghost(creature):
        might = max(1, creature.might)
        spent = physical_points(creature)
        if spent > might:
            found.append(
                f"Its physical Characteristics cost {spent} points, more than its "
                f"Might of {might} (p. 31)."
            )
        low = lowest_physical(might)
        ch = creature.characteristics
        under = [n.title() for n in PHYSICAL if getattr(ch, n) < low]
        if under:
            found.append(f"{', '.join(under)} below {low} (Might / 5 - 10, p. 31).")
    if mental_points(creature) > MENTAL_POINTS:
        found.append(
            f"Its mental Characteristics cost {mental_points(creature)} points; "
            f"most demons have {MENTAL_POINTS} (p. 31)."
        )
    return found


def notes(creature: Creature) -> list[str]:
    """What the books' rules make of a demon: its weakness and True Name,
    Second Sight, recovery and corpse."""
    if not is_demon(creature):
        return []
    might = max(0, creature.might)
    found = [
        f"weakness known on Int + Infernal Lore {weakness_ease(might)}+ (p. 34)",
        f"Second Sight sees it on {second_sight_ease(might)}+ (p. 33)",
        f"its True Name: {TRUE_NAME_XP} xp of Infernal Lore, an Arcane "
        f"Connection and +{TRUE_NAME_PENETRATION} to the Penetration "
        "multiplier (pp. 34-35)",
        "all its Might back in a day, 2 hours sooner a point of Infernal "
        "aura, none in a Divine aura (p. 36)",
        f"its corpse holds about {corpse_vis(might)} pawn(s) of vis (p. 29)",
    ]
    if not is_ghost(creature) and might:
        found.append(f"Coagulation costs {coagulation_cost(might)} (p. 31)")
    return found
