"""Magic beings by the book (Realms of Power: Magic): how a magic being
advances and keeps its magic, and the build of a Beast of Virtue, a
transformed animal, an awakened tree, a Magic Thing and an elemental.

- **Advancement** (pp. 51-54). A magic being's Might Score comes off every
  Advancement Total; each pawn of vis it eats takes 2 off that penalty
  (never adding to the Total). A Gifted one learning a Supernatural
  Ability also loses the sum of its other Supernatural Abilities, and eats
  at most its Might in pawns a season. Experience buys Qualities and
  Inferiorities at the table's costs (TRANSFORMATIONS); practising a
  Quality it has is a Study Total of 5. Eating its Might in pawns, it
  studies transformation without the Might penalty: a stress die + the
  aura, a botch die per 5 pawns on a 0, each botch a Minor Inferiority
  (three a Major). The book's example of 4 pawns eaten at Might 10 is
  13 xp from 15 (Errata p. 63 corrects the printed 7). Bound as a Hermetic
  magus's familiar, it learns as a human does instead, and keeps those
  Abilities if the bond breaks (Errata p. 63; DE p. 267).
- **Acclimation** (pp. 52-54). Each year a magic being loses a Quality or
  a point of Might unless it lives in a strong enough Magic aura
  (`aura_needed`; the Magic Realm counts as aura 10 for half its Might),
  affects or is affected by a magic-aligned being without Might enough
  seasons (`effect_seasons`), or eats Might / 2 pawns of vis, rounded up,
  rolling on the Vis Consumption chart (`vis_consumption`).
- **Beasts of Virtue** (pp. 55-56): Magic Animal and an Essential Virtue,
  never a Flaw that makes it a worse example of its kind (Lame, Blind);
  most have a magical Social Status; powers most often Lesser, Personal or
  Greater; its corpse holds a pawn a 5 Might or fraction.
- **Transformed animals** (pp. 78-79): no Might; a Minor Flaw at Warping
  Score 1 and another at 3, a Minor Virtue at 5, a Major Flaw for each
  Score after. From Magic: Warped Senses or (Form) Monstrosity, then
  Lesser Power at 5, then Hunger for (Form) Magic or Bound to Magic.
- **Awakened trees** (pp. 128-129): no Might (one a spirit animates with
  Manifestation has the power's activation cost as Might while it lasts),
  Cunning, fully
  awake in an aura of 6 or more; a Tree of Virtue holds 1 to 3 pawns.
- **Magic Things** (awakened items, p. 130; elementals, p. 135) never
  tire: they have No Fatigue.
- **Elementals** (Definitive Edition pp. 449-451, which win; RoP: Magic
  pp. 132-139): Size by Might, -18 at Might 1 and 3 more each magnitude
  (`elemental_size`); typical Characteristics by Might (`ELEMENTAL_
  CHARACTERISTICS`), four of them never negative before Size for each
  element (RoP: Magic p. 134); Poor Memory, Short Attention Span, Simple-
  Minded and Ways of the (Land); Brawl and Athletics (Swim for water) at
  its Might's magnitude; its element's attack power (Crush, Drown,
  Suffocate, Burn). It recovers Might only resting in an aura of Might / 5
  over a season, or eating vis (5 points a pawn of its Form, 2 of
  another); each wound takes its penalty from the Might Pool (DE p. 449-
  450).

Characters made for a story needn't balance (p. 34), so all of this is
advice, never a refusal.

Pattern: the same shape as rules.faerie_build and rules.spirit_build (one
function per kind of being over the creature, no new class); the tables
are plain dicts and tuples.
"""

from __future__ import annotations

import re

from ..models import Creature
from .creature_build import magnitude
from .rounding import round_up
from .spirit_build import GHOST_STATUSES

SOURCE = (
    "Realms of Power: Magic, Advancement pp. 51-54, Beasts of Virtue pp. "
    "55-56, Transformed Animals pp. 78-79, Awakened Trees and Items and "
    "Elementals pp. 128-139; Ars Magica Definitive Edition, Familiars "
    "p. 267, Elementals pp. 449-451; Errata p. 63"
)

MAGIC = "Magic"
MAGIC_ANIMAL = "vf_magic_animal"
MAGIC_THING = "vf_magic_thing"

# -- advancement and Acclimation --

#: Each pawn of vis eaten takes this off the Might penalty (p. 52).
VIS_OFF_PENALTY = 2
#: Practising a Quality it already has (p. 52).
PRACTICE_QUALITY = 5
#: Experience points for each transformation (p. 52).
TRANSFORMATIONS: tuple[tuple[int, str], ...] = (
    (
        0,
        "turn a Virtue into a Quality, a Flaw into an Inferiority, or one "
        "Quality or Inferiority into another of its type",
    ),
    (5, "gain a Minor Quality and a Minor Inferiority"),
    (10, "gain a Minor Quality"),
    (15, "gain a Major Quality and a Major Inferiority"),
    (
        20,
        "raise a Minor Quality to Major, a Minor Inferiority to a Minor "
        "Quality, or a Major Inferiority to Minor",
    ),
    (25, "gain a Major Quality and a Minor Inferiority"),
    (30, "gain a Major Quality"),
)
PAWNS_PER_BOTCH_DIE = 5
#: The Magic Realm, for one that visits it, is an aura of 10 for half its
#: Might (p. 53).
MAGIC_REALM_AURA = 10


def advancement_total(
    total: int,
    might: int,
    pawns: int = 0,
    gifted: bool = False,
    other_supernatural: int = 0,
) -> int:
    """What a magic being keeps of an Advancement Total: less its Might
    (and, Gifted and learning a Supernatural Ability, its other
    Supernatural Abilities' scores), 2 off that for each pawn eaten, a
    Gifted one eating at most its Might a season (p. 52)."""
    penalty = max(0, might) + (max(0, other_supernatural) if gifted else 0)
    if gifted:
        pawns = min(pawns, max(0, might))
    return max(0, total - max(0, penalty - VIS_OFF_PENALTY * max(0, pawns)))


def pawns_to_clear(
    might: int, gifted: bool = False, other_supernatural: int = 0
) -> int:
    """The pawns that take the whole Might penalty off (p. 52)."""
    penalty = max(0, might) + (max(0, other_supernatural) if gifted else 0)
    return round_up(penalty / VIS_OFF_PENALTY)


def transformation_cost(xp: int) -> list[str]:
    """What `xp` experience points can buy (p. 52), dearest first."""
    return [text for cost, text in reversed(TRANSFORMATIONS) if cost <= xp]


def vis_study_botch_dice(pawns: int) -> int:
    """Botch dice when vis eaten as a transformational source rolls a 0:
    one a 5 pawns (p. 52)."""
    return max(0, pawns) // PAWNS_PER_BOTCH_DIE


def aura_needed(might: int) -> tuple[int | None, int | None, int | None]:
    """The Magic aura that keeps Acclimation off when always within it,
    within it half the time, and visiting it often; None where no aura
    will (p. 53)."""
    step = round_up(max(0, might) / 5)
    always = max(1, step) if might <= 50 else None
    half = 5 + step if might <= 25 else None
    frequent = 8 + step if might <= 10 else None
    return always, half, frequent


def effect_seasons(level: int) -> tuple[int | None, int | None, int | None]:
    """Seasons a year of a constant, regular (daily) or occasional
    (weekly) effect, by its level or the being's Might, that keep
    Acclimation off; None where that kind won't (p. 54)."""
    if level <= 0:
        return None, None, None
    rows: tuple[tuple[int, tuple[int | None, int | None, int | None]], ...] = (
        (10, (4, None, None)),
        (20, (3, None, None)),
        (30, (2, 4, None)),
        (40, (1, 2, 4)),
        (50, (1, 1, 2)),
    )
    for top, seasons in rows:
        if level <= top:
            return seasons
    return 1, 1, 1


def vis_needed(might: int) -> int:
    """Pawns a year that keep Acclimation off: Might / 2, rounded up
    (p. 54)."""
    return round_up(max(0, might) / 2)


def vis_consumption(roll: int) -> str:
    """The Vis Consumption chart: what a stress roll brings a being that
    ate vis against Acclimation (one botch die a pawn; p. 54)."""
    if roll <= 0:
        return "a possible botch (a Minor Inferiority a botch), else no effect"
    if roll <= 4:
        return "no effect"
    if roll <= 6:
        return "a negative side effect"
    if roll <= 8:
        return "a positive side effect"
    if roll == 9:
        return "a special or story event"
    return f"transformation: {roll} experience points, without the Might penalty"


def is_magic_being(creature: Creature) -> bool:
    return creature.realm == MAGIC and creature.might > 0


def advancement_notes(creature: Creature) -> list[str]:
    """How a magic being advances and stays clear of Acclimation."""
    if not is_magic_being(creature):
        return []
    might = creature.might
    found = [
        f"each Advancement Total loses its Might ({might}), 2 less for each "
        f"pawn of vis it eats ({pawns_to_clear(might)} clear it; p. 52)"
    ]
    always, half, frequent = aura_needed(might)
    ways: list[str] = []
    if always is not None:
        aura = f"living in a Magic aura of {always}"
        if half is not None:
            aura += f" (half the time {half}"
            aura += f", visits {frequent})" if frequent is not None else ")"
        ways.append(aura)
    constant = effect_seasons(might)[0]
    if constant is not None:
        ways.append(
            f"affecting a magical being without Might {constant} season(s) a year"
        )
    ways.append(f"eating {vis_needed(might)} pawn(s) of vis a year")
    found.append("it keeps off Acclimation by " + ", or ".join(ways) + " (pp. 53-54)")
    found.append(
        "bound as a Hermetic magus's familiar, it learns as a human does, and "
        "keeps those Abilities if the bond breaks (Errata p. 63; DE p. 267)"
    )
    return found


# -- the being's Virtues and Flaws --


def _ids(creature: Creature) -> list[str]:
    return [vf.vf_id for vf in creature.virtues_flaws]


# -- Beasts of Virtue --

ESSENTIAL_VIRTUES = ("vf_essential_virtue", "vf_essential_virtue_major")
#: Flaws that make a beast a worse example of its kind (p. 55).
DEFECTS: dict[str, str] = {
    "vf_lame": "Lame",
    "vf_blind": "Blind",
    "vf_deaf": "Deaf",
    "vf_poor_eyesight": "Poor Eyesight",
    "vf_poor_hearing": "Poor Hearing",
    "vf_missing_eye": "Missing Eye",
    "vf_missing_ear": "Missing Ear",
    "vf_missing_hand": "Missing Hand",
    "vf_hunchback": "Hunchback",
    "vf_frail": "Frail",
}
#: The powers a Beast of Virtue most often has (p. 56).
USUAL_POWERS = ("Lesser Power", "Personal Power", "Greater Power")
VIS_PER_MIGHT = 5


def is_beast_of_virtue(creature: Creature) -> bool:
    """A magic animal built as a Beast of Virtue: one with an Essential
    Virtue, or "of Virtue" in its name."""
    if creature.realm != MAGIC or MAGIC_ANIMAL not in _ids(creature):
        return False
    return any(v in ESSENTIAL_VIRTUES for v in _ids(creature)) or (
        "of virtue" in creature.name.casefold()
    )


def beast_of_virtue_problems(creature: Creature) -> list[str]:
    if not is_beast_of_virtue(creature):
        return []
    ids = _ids(creature)
    found: list[str] = []
    if not any(v in ESSENTIAL_VIRTUES for v in ids):
        found.append(
            "A Beast of Virtue has an Essential Virtue for what typifies its "
            "species (p. 55)."
        )
    defects = sorted({DEFECTS[v] for v in ids if v in DEFECTS})
    if defects:
        found.append(
            "A Beast of Virtue is the epitome of its kind, without Flaws that "
            f"make it worse: {', '.join(defects)} (p. 55)."
        )
    return found


def beast_of_virtue_notes(creature: Creature) -> list[str]:
    if not is_beast_of_virtue(creature):
        return []
    ids = set(_ids(creature))
    found = [
        f"its corpse holds about {round_up(max(0, creature.might) / VIS_PER_MIGHT)} "
        "pawn(s) of vis (p. 55)"
    ]
    if not ids & set(GHOST_STATUSES):
        found.append(
            "most have a magical Social Status: Champion, Covenfolk, Master, "
            "Monster or Friend (p. 55)"
        )
    odd = sorted(
        {
            p.quality
            for p in creature.powers
            if p.quality and p.quality not in USUAL_POWERS
        }
    )
    if odd:
        found.append(
            f"its powers are most often Lesser, Personal or Greater, not "
            f"{', '.join(odd)} (p. 56)"
        )
    return found


# -- transformed animals --

#: The Virtues and Flaws Warping by Magic brings an animal (p. 79).
WARPED_MINOR_FLAWS = ("vf_warped_senses", "vf_form_monstrosity")
WARPED_VIRTUE = "vf_lesser_power"
WARPED_MAJOR_FLAWS = ("vf_hunger_for_form_magic", "vf_bound_to_realm")
FIRST_FLAW, SECOND_FLAW, VIRTUE_SCORE = 1, 3, 5


def warping_gains(score: int) -> tuple[int, int, int]:
    """The Minor Flaws, Minor Virtues and Major Flaws an animal has gained
    by its Warping Score (p. 78)."""
    minor = (score >= FIRST_FLAW) + (score >= SECOND_FLAW)
    virtue = int(score >= VIRTUE_SCORE)
    return minor, virtue, max(0, score - VIRTUE_SCORE)


def is_transformed(creature: Creature) -> bool:
    return not creature.realm and creature.warping_score > 0


def transformed_problems(creature: Creature) -> list[str]:
    if creature.realm and creature.warping_score > 0:
        return [
            "A creature with Might has no Warping Score; a transformed animal "
            "has no Might (DE p. 426; RoP: Magic p. 78)."
        ]
    if not is_transformed(creature):
        return []
    ids = _ids(creature)
    score = creature.warping_score
    minor, virtue, major = warping_gains(score)
    found: list[str] = []
    if sum(ids.count(v) for v in WARPED_MINOR_FLAWS) > minor:
        found.append(
            f"At Warping Score {score} Warping has brought {minor} Minor Flaw(s), "
            "fewer than its Warped Senses and Monstrosities (p. 78)."
        )
    if WARPED_VIRTUE in ids and not virtue:
        found.append("Warping brings Lesser Power only at Warping Score 5 (p. 79).")
    if sum(ids.count(v) for v in WARPED_MAJOR_FLAWS) > major:
        found.append(
            f"At Warping Score {score} Warping has brought {major} Major Flaw(s), "
            "fewer than its Hungers and Bound to Magic (p. 78)."
        )
    return found


def transformed_notes(creature: Creature) -> list[str]:
    if not is_transformed(creature):
        return []
    minor, virtue, major = warping_gains(creature.warping_score)
    gained = [f"{minor} Minor Flaw(s)"]
    if virtue:
        gained.append("a Minor Virtue")
    if major:
        gained.append(f"{major} Major Flaw(s)")
    found = [
        f"Warping Score {creature.warping_score} has brought "
        + ", ".join(gained)
        + "; from Magic, Warped Senses or (Form) Monstrosity, Lesser Power at "
        "5, then Hunger for (Form) Magic or Bound to Magic (pp. 78-79)"
    ]
    if virtue:
        found.append(
            "with its Minor Virtue, the same sort of aura no longer Warps it (p. 78)"
        )
    return found


# -- awakened trees and Magic Things --

TREE_WORDS = re.compile(
    r"\b(tree|oak|ash|willow|rowan|hazel|blackthorn|birch|yew|elm|alder|"
    r"beech|hawthorn|pine|linden)\b",
    re.IGNORECASE,
)
MANIFESTATION = "manifestation"
FULLY_AWAKE_AURA = 6


def is_tree(creature: Creature) -> bool:
    return creature.realm in ("", MAGIC) and bool(TREE_WORDS.search(creature.name))


def tree_problems(creature: Creature) -> list[str]:
    if not is_tree(creature):
        return []
    found: list[str] = []
    manifestation = next(
        (p for p in creature.powers if MANIFESTATION in p.name.casefold()), None
    )
    if (
        creature.might > 0
        and manifestation is None
        and MAGIC_THING not in _ids(creature)
    ):
        found.append(
            "An awakened or animated tree, or a Tree of Virtue, has no Might; one "
            "a spirit animates with Manifestation has the power's activation cost "
            "as Might (pp. 128-129)."
        )
    elif (
        manifestation is not None
        and manifestation.might_cost > 0
        and creature.might != manifestation.might_cost
    ):
        found.append(
            f"A tree a spirit animates has Might equal to Manifestation's "
            f"activation cost ({manifestation.might_cost}) while it lasts, not "
            f"{creature.might} (p. 128)."
        )
    if not creature.cunning:
        found.append("An awakened tree has Cunning, not Intelligence (p. 128).")
    return found


def tree_notes(creature: Creature) -> list[str]:
    if not is_tree(creature):
        return []
    return [
        f"fully awake in a Magic aura of {FULLY_AWAKE_AURA} or more, lethargic as "
        "the aura weakens (p. 128)",
        "a Tree of Virtue holds 1 to 3 pawns; harvesting or Enriching it drains "
        "its power (p. 129)",
    ]


def magic_thing_problems(creature: Creature) -> list[str]:
    if creature.realm != MAGIC or MAGIC_THING not in _ids(creature):
        return []
    if creature.tires:
        return ["A Magic Thing never tires: it has No Fatigue (p. 135)."]
    return []


# -- elementals --

ELEMENTS: dict[str, str] = {
    "Terram": "earth",
    "Aquam": "water",
    "Auram": "air",
    "Ignem": "fire",
}
#: Each element's power for its natural attack (RoP: Magic p. 135).
ATTACK_POWERS = {"earth": "Crush", "water": "Drown", "air": "Suffocate", "fire": "Burn"}
#: Characteristics never negative (before Size) by element (p. 134).
NO_NEGATIVE: dict[str, tuple[str, ...]] = {
    "earth": ("strength", "stamina", "dexterity", "quickness"),
    "water": ("strength", "stamina", "intelligence", "perception"),
    "air": ("intelligence", "perception", "presence", "communication"),
    "fire": ("presence", "communication", "dexterity", "quickness"),
}
SHORT = {
    "intelligence": "Cun",
    "perception": "Per",
    "presence": "Pre",
    "communication": "Com",
    "strength": "Str",
    "stamina": "Sta",
    "dexterity": "Dex",
    "quickness": "Qik",
}
#: Every elemental's Flaws, and its Ways of the (Land) (p. 134).
ELEMENTAL_FLAWS: dict[str, str] = {
    "vf_poor_memory": "Poor Memory",
    "vf_short_attention_span": "Short Attention Span",
    "vf_simple_minded": "Simple-Minded",
}
WAYS = "vf_ways_of_the_land"
#: Typical Characteristics by Might (DE p. 450; RoP: Magic p. 135).
ELEMENTAL_CHARACTERISTICS: dict[int, tuple[int, ...]] = {
    1: (2, 2, 1, 1, 1, 0, -1, -1),
    5: (3, 2, 1, 1, 0, 0, -1, -2),
    10: (3, 3, 1, 1, 0, 0, -1, -3),
    15: (4, 3, 2, 1, 0, 0, -2, -4),
    20: (6, 5, 2, 2, 1, 0, -5, -6),
    25: (7, 6, 2, 2, 1, 0, -6, -7),
    30: (8, 6, 2, 2, 1, 0, -6, -8),
    35: (9, 7, 2, 2, 1, 0, -7, -9),
    40: (10, 8, 2, 2, 1, 0, -8, -10),
    45: (11, 9, 2, 2, 1, 0, -9, -11),
    50: (12, 9, 2, 2, 1, 0, -9, -12),
}
SMALLEST_SIZE, SIZE_PER_MAGNITUDE = -18, 3
#: An elemental recovers Might only resting in an aura of Might / 5, and
#: by vis: 5 points a pawn of its Form, 2 of another (DE p. 449).
SAME_FORM_POINTS, OTHER_FORM_POINTS = 5, 2


def elemental_size(might: int) -> int:
    """Size by Might: -18 at 1, 3 more for each magnitude, levels under 5
    each counting as one, as a spell's (DE p. 450; RoP: Magic p. 135)."""
    might = max(1, might)
    steps = might - 1 if might <= 5 else 4 + round_up(might / 5) - 1
    return SMALLEST_SIZE + SIZE_PER_MAGNITUDE * steps


def typical_characteristics(might: int) -> tuple[int, ...]:
    """The table's row at or below the Might (DE p. 450)."""
    row = max((m for m in ELEMENTAL_CHARACTERISTICS if m <= max(1, might)), default=1)
    return ELEMENTAL_CHARACTERISTICS[row]


def element_of(creature: Creature) -> str | None:
    """Its element, for a Magic creature written as an elemental: aligned
    to an elemental Form, with an elemental's Flaws or "elemental" in its
    name."""
    if creature.realm != MAGIC or creature.might_form not in ELEMENTS:
        return None
    ids = _ids(creature)
    if "elemental" in creature.name.casefold() or any(
        v in ELEMENTAL_FLAWS for v in ids
    ):
        return ELEMENTS[creature.might_form]
    return None


def _ability(creature: Creature, name: str) -> int:
    wanted = name.casefold()
    return max(
        (a.level for a in creature.abilities if a.name.casefold() == wanted),
        default=0,
    )


def elemental_problems(creature: Creature) -> list[str]:
    element = element_of(creature)
    if element is None:
        return []
    found: list[str] = []
    size = elemental_size(creature.might)
    if creature.size != size:
        found.append(
            f"An elemental of Might {creature.might} is Size {size:+d} (DE p. 450)."
        )
    ids = _ids(creature)
    missing = [name for v, name in ELEMENTAL_FLAWS.items() if v not in ids]
    if WAYS not in ids:
        missing.append("Ways of the (Land)")
    if missing:
        found.append(f"Every elemental has {', '.join(missing)} (p. 134).")
    attack = ATTACK_POWERS[element]
    if not any(p.name.casefold() == attack.casefold() for p in creature.powers):
        found.append(f"Every {element} elemental has the power {attack} (p. 135).")
    least = magnitude(creature.might)
    moving = "Swim" if element == "water" else "Athletics"
    low = [name for name in ("Brawl", moving) if _ability(creature, name) < least]
    if low:
        found.append(
            f"An elemental has {' and '.join(low)} of at least its Might's "
            f"magnitude, {least} (p. 134)."
        )
    ch = creature.characteristics
    before_size = {
        name: getattr(ch, name)
        + (creature.size if name == "quickness" else 0)
        - (2 * creature.size if name == "strength" else 0)
        for name in NO_NEGATIVE[element]
    }
    negative = [SHORT[name] for name, value in before_size.items() if value < 0]
    if negative:
        found.append(
            f"A{'n' if element in ('earth', 'air') else ''} {element} elemental's "
            f"{', '.join(negative)} are never negative before Size (p. 134)."
        )
    return found


def elemental_notes(creature: Creature) -> list[str]:
    if element_of(creature) is None:
        return []
    might = creature.might
    row = ", ".join(
        f"{v:+d}".replace("+0", "0") for v in typical_characteristics(might)
    )
    return [
        f"typical Characteristics {row}, then Qik - Size and Str + 2 x Size "
        "(DE p. 450; RoP: Magic p. 134)",
        f"it recovers Might only resting a season in an aura of "
        f"{round_up(max(0, might) / 5)} or more, or eating vis: "
        f"{SAME_FORM_POINTS} points a pawn of {creature.might_form}, "
        f"{OTHER_FORM_POINTS} of another Art (DE p. 449)",
        "each wound takes its penalty from the Might Pool (Incapacitating 5), "
        "and the pieces knocked off hold a pawn of vis for each 5 points of "
        "penalty (DE pp. 450-451)",
    ]


# -- all of it --


def problems(creature: Creature) -> list[str]:
    """What a magic being built by Realms of Power: Magic would have that
    this one lacks (advice)."""
    return [
        *beast_of_virtue_problems(creature),
        *transformed_problems(creature),
        *tree_problems(creature),
        *magic_thing_problems(creature),
        *elemental_problems(creature),
    ]


def notes(creature: Creature) -> list[str]:
    """What its build gives a magic being, a transformed animal or a tree."""
    return [
        *beast_of_virtue_notes(creature),
        *elemental_notes(creature),
        *transformed_notes(creature),
        *tree_notes(creature),
        *advancement_notes(creature),
    ]
