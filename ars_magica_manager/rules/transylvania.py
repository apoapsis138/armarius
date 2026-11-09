"""Against the Dark's creatures and character options: the Tribunal's
vampires and the kukudhi a player may play, the dragon-born kin of the
zmajevi, and the shapeshifting crowned kings.

- Vampires (pp. 114-121) are faeries that take a dead person's shape and
  feed on blood and fear. Every vampire has a physical form, a level of
  cognizance and a Social Interaction Virtue or Flaw (as every faerie
  does), Feast of the Dead, a Traditional Ward of sunlight and the Lesser
  Power Sap the Life (p. 116). Each has one to three of the precautions
  that stop it forming (p. 115), one to three limitations it obeys, which
  are traditional wards (p. 116), and one way to kill it for good
  (p. 117). It passes through stages: an unseen zduhacz for seven (or
  forty) days, a shapeless gadja for forty days, the dead one's shape (a
  platenik), and after seven years a kukudhi living far away among
  people, no longer kept indoors by day though direct sun still hurts it
  (p. 115). Vampires are busiest from St Andrew's Eve to St George's Eve.
- A kukudhi may be a player character, best in a high-power saga among
  older magi (pp. 115-116). As a faerie player character (Realms of
  Power: Faerie pp. 45-46) its Virtues are up to 10 points balanced by
  Flaws in place of a companion, or 1 free and up to 20 more at 2 for each
  Flaw point in place of a magus, and it has 15 x (the magi's average age
  - 5) + 120 Pretense points.
- The dragon-born (p. 108) are Magic Kin (Realms of Power: Magic p. 89):
  a zmaj's human children, whose Inherited Virtues are Greater Immunity
  (fire), a Personal Power mirroring one of the father's, and
  Self-Confident, and whose Common Flaw is greed for women or gold. Second
  Sight sees their slit pupils and the sheen of scales on their skin.
- A crowned king (Magic Resistance 10, DE p. 420) of Slavic, Magyar or
  Vlach blood also has the Major Supernatural Virtue Shapeshifter free,
  with the forms of a wolf, a lion and a dragon, the Divine allowing the
  dragon (p. 122).

The book's own vampires needn't balance (p. 117), so the vampire checks
are advice, never refusals. The Errata (p. 84) corrects none of these
pages.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .. import catalog
from ..models import Background, Character, Creature, Saga, character_age
from . import faerie_build
from .creation_base import CHARACTER_CHECKS, Check, Record, check

SOURCE = (
    "Against the Dark: The Transylvanian Tribunal, Dragon-Born p. 108, "
    "Vampires pp. 114-121, Divine Werewolves p. 122; Realms of Power: Faerie "
    "pp. 45-46; Realms of Power: Magic p. 89; Ars Magica Definitive Edition "
    "p. 420"
)

FEAST_OF_THE_DEAD = "vf_feast_of_the_dead"
LESSER_POWER = "vf_lesser_power"
TRADITIONAL_WARD = "vf_traditional_ward"
SOVEREIGN_WARD = "vf_sovereign_ward"
RESTRICTED_MIGHT = ("vf_restricted_might", "vf_restricted_might_major")
SAP_THE_LIFE = "Sap the Life"
SUNLIGHT_WORDS = ("sun", "daylight", "light of day")

#: The names the book gives vampires (pp. 114-121): a Faerie creature
#: named with one of them is a vampire.
VAMPIRE_WORDS = (
    "vampire",
    "kukudhi",
    "platenik",
    "ubour",
    "drakus",
    "moroi",
    "moroaic",
    "oiocoi",
    "lampir",
    "upir",
    "vukodla",
    "farkaskoldus",
    "blautsauger",
    "pricolici",
    "zduhacz",
    "sjenovik",
    "luderc",
    "nekrstenik",
    "ustrel",
    "sjanka",
    "ljugat",
    "gadja",
)
KUKUDHI = "kukudhi"

#: The precautions that stop a vampire forming: each vampire has one to
#: three, all of which must be met (p. 115).
PRECAUTIONS: tuple[str, ...] = (
    "Cut off the heels",
    "Hamstring the corpse",
    "Place its head under the knees",
    "Turn the body face down",
    "Drive thorns or nails into the soles of the feet",
    "Place a nail or thorn under the tongue",
    "Fill the mouth with garlic and salt",
    "Drive thorns under the fingernails",
    "Put small stones in the ears, mouth and navel",
    "Bind the hands behind the back",
    "Put a red-hot needle through the heart",
    "Drive a nail where the corpse's head lay",
    "Scatter the place of death with millet, red thread or thorns",
    "Place millet in the coffin",
    "Bind the coffin with wild roses or ivy",
    "Stick nine distaffs in the soil above the coffin",
    "Bury the body in a swamp or forest",
    "Bury the body at a crossroads",
    "Drive an iron spike through the head",
    "Drive an aspen or hawthorn stake through the navel, heart or behind",
    "Pile stones on the grave",
)
MOST_PRECAUTIONS = 3
PRECAUTION_WORD = "precaution"
#: A vampire's physical form: a faerie's (RoP: Faerie p. 50), or the
#: incorporeal vampire's Intangible Flesh (p. 119).
FORMS = faerie_build.REQUIRED[0][1]
BODILESS = ("vf_intangible_flesh",)


@dataclass(frozen=True)
class Limitation:
    """A rule a vampire obeys (p. 116), and the words a ward naming it
    holds."""

    rule: str
    words: tuple[str, ...]
    #: How often the book says vampires have it ("" when it doesn't say).
    how_common: str = ""


#: The limitations a vampire picks one to three of: traditional wards
#: whose rituals feed it (p. 116).
LIMITATIONS: tuple[Limitation, ...] = (
    Limitation(
        "Cannot leave its resting place during the day",
        ("resting place", "grave by day", "coffin by day"),
        "almost universal",
    ),
    Limitation("Cannot spend Might points on a Saturday", (), "very common"),
    Limitation(
        "Cannot harm anyone born on a Saturday",
        ("born on a saturday", "born on saturday"),
        "very common",
    ),
    Limitation("Cannot cross a line of thorns", ("thorn",)),
    Limitation("Cannot leave millet uncounted", ("millet",)),
    Limitation("Cannot cross running water", ("running water",)),
    Limitation(
        "Repulsed by garlic: no passing a garlic ward, nor attacking one "
        "smeared with it",
        ("garlic",),
    ),
    Limitation("Repulsed by black hawthorn", ("hawthorn",)),
    Limitation("Cannot pass a tangle of red thread", ("red thread",)),
    Limitation("Cannot approach while stories are told", ("stories", "story")),
    Limitation("Cannot ask the same question three times", ("question",)),
    Limitation("Repelled by the Cross and by prayers", ("cross", "prayer")),
)
RESTING_PLACE = LIMITATIONS[0]
SATURDAY_MIGHT = LIMITATIONS[1]
MOST_LIMITATIONS = 3

#: The ways to kill a vampire for good: each vampire has one (p. 117).
#: Killed any other way it re-forms in days or weeks.
DISPATCH: tuple[str, ...] = (
    "Exhume the body on a Saturday (or Sunday)",
    "Women or virgins exhume the body",
    "Burn the heart or liver",
    "Cut the heart or liver to pieces with a scythe",
    "Throw the heart or liver into running water",
    "Immolate the body",
    "Decapitate the body",
    "Drive a hawthorn (or aspen) stake through the navel (or heart)",
)

#: Common Virtues and Flaws of vampires (p. 116), as (catalog id, params).
COMMON_VIRTUES: tuple[tuple[str, dict[str, str]], ...] = (
    ("vf_greater_immunity", {"hazard": "edged weapons"}),
    ("vf_time_or_place_of_power", {}),
    ("vf_tough", {}),
)
COMMON_FLAWS: tuple[tuple[str, dict[str, str]], ...] = (
    ("vf_might_recovery_requires_vitality", {}),
    ("vf_restricted_might_major", {}),
    ("vf_sovereign_ward", {"ward": "those born on Saturdays"}),
    ("vf_vulnerable_to_substance", {"substance": "garlic or thorns"}),
)


@dataclass(frozen=True)
class VampirePower:
    """A power vampires commonly have (pp. 116-117), as the book designs
    it: its Virtue, Arts and level, Might cost, the Initiative's penalty
    from Quickness (None for a constant power) and what it does."""

    name: str
    virtue: str
    arts: str
    level: int
    cost: int
    init: int | None
    rdt: str
    does: str


POWERS: tuple[VampirePower, ...] = (
    VampirePower(
        "Cause Drowsiness",
        "Lesser Power",
        "ReMe",
        15,
        3,
        -6,
        "Touch, Sun, Ind",
        "puts a human it touches to sleep",
    ),
    VampirePower(
        "Eidolon",
        "Lesser Power",
        "CrIm",
        20,
        4,
        -8,
        "Touch, Sun, Ind",
        "an illusory form it can see and hear, moving and speaking as it "
        "directs, one for each copy of the power",
    ),
    VampirePower(
        SAP_THE_LIFE,
        "Lesser Power",
        "PeCo",
        15,
        3,
        -6,
        "Touch, Mom, Ind",
        "a disease starting at a Light Wound that takes two Fatigue levels "
        "until it abates; each week a Recovery roll of 12 holds steady and "
        "18 improves (Art & Academe: a Serious disease of Severity 15), "
        "treated with Faerie Lore or Medicine",
    ),
    VampirePower(
        "Ghost Touch",
        "Focus Power",
        "ReTe",
        25,
        1,
        -5,
        "varies",
        "moves loose objects, 5 lb for 1 point and double for each more; "
        "hurled, +5 damage a point; physical attacks must penetrate",
    ),
    VampirePower(
        "Flight",
        "Personal Power",
        "ReFo",
        15,
        2,
        None,
        "Per, Sun, Ind",
        "constant: it can fly, though not fight while flying fast",
    ),
    VampirePower(
        "Invisibility",
        "Personal Power",
        "PeIm",
        15,
        2,
        -2,
        "Per, Sun, Ind",
        "a personal Veil of Invisibility",
    ),
    VampirePower(
        "Silent Motion",
        "Personal Power",
        "PeIm",
        10,
        1,
        None,
        "Per, Sun, Ind",
        "constant: it moves without a sound",
    ),
    VampirePower(
        "Supernatural Agility",
        "Personal Power",
        "ReCo",
        25,
        3,
        None,
        "Per, Sun, Ind",
        "constant: minor supernatural feats with its Athletics Pretense",
    ),
)

#: The vampire's life (p. 115), as (stage, days it lasts; None: until the
#: next stage by years).
ZDUHACZ, GADJA, PLATENIK = "zduhacz", "gadja", "platenik"
ZDUHACZ_DAYS = (7, 40)
GADJA_DAYS = 40
KUKUDHI_YEARS = 7
DAYS_A_YEAR = 365


def life_stage(days_dead: int, *, haunting_days: int = ZDUHACZ_DAYS[0]) -> str:
    """The stage of a vampire `days_dead` days after the death it took
    on: an unseen zduhacz for seven days (or forty: `haunting_days`), a
    gadja for forty days, a platenik in the dead one's shape, and a
    kukudhi after seven years (p. 115). It moves on only if it survives
    each stage."""
    if haunting_days not in ZDUHACZ_DAYS:
        raise ValueError(
            f"A zduhacz haunts for {ZDUHACZ_DAYS[0]} or {ZDUHACZ_DAYS[1]} days, "
            f"not {haunting_days}"
        )
    if days_dead < haunting_days:
        return ZDUHACZ
    if days_dead < haunting_days + GADJA_DAYS:
        return GADJA
    if days_dead < KUKUDHI_YEARS * DAYS_A_YEAR:
        return PLATENIK
    return KUKUDHI


#: Vampires are most active from St Andrew's Eve (30 November) to St
#: George's Eve (23 April), when most dhampirs are sired (p. 115).
ACTIVE_FROM, ACTIVE_TO = (11, 30), (4, 23)


def vampires_active(month: int, day: int) -> bool:
    """Whether the date falls in the vampires' busy season (p. 115)."""
    return (month, day) >= ACTIVE_FROM or (month, day) <= ACTIVE_TO


# -- a vampire creature --


def _named(creature: Creature, word: str) -> bool:
    return word in creature.name.casefold()


def _param_text(creature: Creature) -> list[tuple[str, str]]:
    """(vf_id, its params' text, lower case) for each Virtue and Flaw."""
    return [
        (vf.vf_id, " ".join(str(v) for v in vf.params.values()).casefold())
        for vf in creature.virtues_flaws
    ]


def _has_sap(creature: Creature) -> bool:
    word = SAP_THE_LIFE.casefold()
    if any(word in p.name.casefold() for p in creature.powers):
        return True
    return any(
        vf_id == LESSER_POWER and word in text for vf_id, text in _param_text(creature)
    )


def is_vampire(creature: Creature) -> bool:
    """A faerie vampire: Faerie, and named as the book names vampires, or
    with both Feast of the Dead and Sap the Life (pp. 114-121). The
    Infernal broukolak (p. 120) is a demon, not one of these."""
    if creature.realm != faerie_build.FAERIE:
        return False
    if any(_named(creature, word) for word in VAMPIRE_WORDS):
        return True
    ids = {vf.vf_id for vf in creature.virtues_flaws}
    return FEAST_OF_THE_DEAD in ids and _has_sap(creature)


def is_kukudhi(creature: Creature) -> bool:
    """An old vampire living among people, the one a player may play
    (pp. 115-116)."""
    return is_vampire(creature) and _named(creature, KUKUDHI)


def _wards(creature: Creature) -> list[str]:
    return [
        text
        for vf_id, text in _param_text(creature)
        if vf_id in (TRADITIONAL_WARD, SOVEREIGN_WARD)
    ]


def limitations_of(creature: Creature) -> list[Limitation]:
    """The limitations of p. 116 its wards name (and Restricted Might,
    the Saturday one), in the book's order."""
    wards = _wards(creature)
    ids = {vf.vf_id for vf in creature.virtues_flaws}
    found = []
    for limitation in LIMITATIONS:
        if limitation is SATURDAY_MIGHT:
            if ids & set(RESTRICTED_MIGHT):
                found.append(limitation)
        elif any(word in ward for ward in wards for word in limitation.words):
            found.append(limitation)
    return found


def problems(creature: Creature) -> list[str]:
    """What a vampire built by the book has that this one lacks (advice,
    pp. 115-117)."""
    if not is_vampire(creature):
        return []
    ids = {vf.vf_id for vf in creature.virtues_flaws}
    found: list[str] = []
    if FEAST_OF_THE_DEAD not in ids:
        found.append("Every vampire has Feast of the Dead (p. 116).")
    if not any(word in ward for ward in _wards(creature) for word in SUNLIGHT_WORDS):
        found.append(
            "Every vampire has a Traditional Ward of sunlight, which hurts it in "
            "the light of day (p. 116)."
        )
    if not _has_sap(creature):
        found.append("Every vampire has the Lesser Power Sap the Life (p. 116).")
    if not faerie_build.built_by_the_book(creature):
        missing = [
            what
            for what, options, _ in faerie_build.REQUIRED[:3]
            if not ids & {*options, *(BODILESS if options is FORMS else ())}
        ]
        if missing:
            found.append(f"A vampire has {', '.join(missing)} (p. 116).")
    limitations = limitations_of(creature)
    if not limitations:
        found.append(
            "None of p. 116's limitations is among its wards: a vampire obeys one "
            "to three (running water, garlic, thorns and the rest)."
        )
    elif len(limitations) > MOST_LIMITATIONS:
        found.append(
            f"{len(limitations)} of p. 116's limitations: a vampire obeys one to three."
        )
    if is_kukudhi(creature):
        found += _kukudhi_problems(creature, ids, limitations)
    return found


def _kukudhi_problems(
    creature: Creature, ids: set[str], limitations: list[Limitation]
) -> list[str]:
    found = []
    if RESTING_PLACE in limitations:
        found.append(
            "A kukudhi has lost the vampire's bond to its resting place by day "
            "(p. 115)."
        )
    if not ids & {"vf_passes_for_human", "vf_infiltrator", "vf_infiltrator_major"}:
        found.append(
            "A kukudhi passes for human, taking a trade and a family (p. 115): "
            "Passes for Human, or Infiltrator (RoP: Faerie p. 51)."
        )
    return found


def notes(creature: Creature) -> list[str]:
    """What the book says of this vampire: its limitations, what to choose
    for it, and, for a kukudhi, how it lives."""
    if not is_vampire(creature):
        return []
    found = []
    limitations = limitations_of(creature)
    if limitations:
        found.append(
            "obeys "
            + "; ".join(lim.rule.split(":")[0].lower() for lim in limitations)
            + " (p. 116)"
        )
    if PRECAUTION_WORD not in creature.notes.casefold():
        found.append(
            "its notes should say the one to three precautions that stop it "
            "forming (p. 115) and the one way to kill it for good (p. 117); "
            "slain otherwise, it re-forms in days or weeks"
        )
    if is_kukudhi(creature):
        found.append(
            "a kukudhi lives far from its old home with a trade and a family; "
            "direct sun still hurts it, and its children are dhampirs (p. 115)"
        )
    return found


# -- a kukudhi as a player character (RoP: Faerie pp. 45-46) --

COMPANION_MOST_VIRTUES = 10
MAGUS_FREE_VIRTUES, MAGUS_MOST_VIRTUES, MAGUS_PER_FLAW = 1, 20, 2
#: The magi's age the book's faeries assume when none is known (p. 46).
DEFAULT_MAGI_AGE = 21


@dataclass(frozen=True)
class FaerieBalance:
    """A faerie player character's Virtue and Flaw points."""

    virtue_points: int
    flaw_points: int

    @property
    def as_companion(self) -> bool:
        """Up to 10 points of Virtues balanced by Flaws."""
        return (
            self.virtue_points <= COMPANION_MOST_VIRTUES
            and self.virtue_points <= self.flaw_points
        )

    @property
    def as_magus(self) -> bool:
        """1 free, then up to 20 points of Virtues, 2 for each Flaw point."""
        bought = max(0, self.virtue_points - MAGUS_FREE_VIRTUES)
        return (
            bought <= MAGUS_MOST_VIRTUES and bought <= MAGUS_PER_FLAW * self.flaw_points
        )


def balance(creature: Creature) -> FaerieBalance:
    """Its Virtue and Flaw points, by the catalog's costs (Free ones cost
    nothing)."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    virtues = flaws = 0
    for vf in creature.virtues_flaws:
        entry = by_id.get(vf.vf_id)
        if entry is None:
            continue
        cost = int(entry.cost)
        if cost > 0:
            virtues += cost
        else:
            flaws -= cost
    return FaerieBalance(virtues, flaws)


def magi_age(saga: Saga) -> int:
    """The magus player characters' average age this year (rounded
    down): those a player plays, or every magus if none is marked, or 21
    when no magus has a year of birth (RoP: Faerie p. 46)."""
    magi = [c for c in saga.characters if c.type == "magus"]
    played = [c for c in magi if _played(c.background)] or magi
    ages = [
        age
        for c in played
        if (age := character_age(c.background.year_born, saga.current_year)) is not None
    ]
    return sum(ages) // len(ages) if ages else DEFAULT_MAGI_AGE


def _played(background: Background) -> bool:
    return bool(
        background.player_ids or background.everyone_plays or background.player.strip()
    )


def pretenses_spent(creature: Creature) -> int:
    return sum(a.xp for a in creature.abilities)


def player_notes(saga: Saga, creature: Creature) -> list[str]:
    """A kukudhi made as a player character: its Virtues against a
    companion's and a magus's, and its Pretense points (RoP: Faerie pp.
    45-46; Against the Dark pp. 115-116)."""
    if not is_kukudhi(creature):
        return []
    points = balance(creature)
    fits = [
        what
        for what, ok in (
            ("a companion", points.as_companion),
            ("a magus", points.as_magus),
        )
        if ok
    ]
    age = magi_age(saga)
    pretenses = faerie_build.pretense_points(creature, age)
    spent = pretenses_spent(creature)
    return [
        f"{points.virtue_points} Virtue points, {points.flaw_points} Flaw points: "
        + (
            f"balanced to replace {' or '.join(fits)}"
            if fits
            else "not balanced to replace a companion (up to 10, balanced) or a "
            "magus (1 free, then 2 for each Flaw point, up to 20)"
        )
        + " (RoP: Faerie p. 45)",
        f"{pretenses} Pretense points at the magi's age of {age}, {spent} spent "
        "(RoP: Faerie p. 46)",
        "best in a high-power saga among older magi (Against the Dark p. 116)",
    ]


# -- the dragon-born (p. 108) --

#: A dragon-born's Inherited Virtues and Common Flaw: those of Magic Kin
#: (Realms of Power: Magic p. 89), as (catalog id, params).
DRAGON_BORN_VIRTUES: tuple[tuple[str, dict[str, str]], ...] = (
    ("vf_greater_immunity", {"hazard": "fire"}),
    ("vf_personal_power", {}),
    ("vf_self_confident", {}),
)
#: The book's "Greedy (women or gold)": the Definitive Edition's Greedy is
#: for food and drink (DE p. 132), so greed for gold is Avaricious and for
#: women Lecherous.
DRAGON_BORN_FLAWS = ("vf_avaricious", "vf_lecherous")


@dataclass(frozen=True)
class KinPower:
    """A Personal Power the book gives as an example for the dragon-born."""

    name: str
    #: The book prints the base and modifiers but names no Arts.
    level: int
    rdt: str
    penetration: int
    does: str


#: Each costs a Fatigue level to use (p. 108); a Personal Power holds 25
#: levels, the rest buying Penetration (DE, Personal Power).
DRAGON_BORN_POWERS: tuple[KinPower, ...] = (
    KinPower(
        "Lungs of the Fish",
        20,
        "Per, Moon, Part",
        0,
        "breathes water, born of a dragon that lived under a lake",
    ),
    KinPower(
        "Hands of the Fiery Beast",
        15,
        "Per, Conc, Part",
        10,
        "hands hot as molten iron, setting alight what they hold and burning "
        "whom they touch",
    ),
)


# -- crowned kings (p. 122) --

CROWNED_KING = "King (crowned)"
SHAPESHIFTER = "vf_shapeshifter"
ROYAL_FORMS = ("wolf", "lion", "dragon")
#: The starts of words in a king's race or nationality that make his
#: blood Slavic, Magyar or Vlach.
ROYAL_PEOPLES = (
    "slav",
    "serb",
    "croat",
    "bulgar",
    "bosnia",
    "ruthen",
    "rus",
    "pole",
    "polish",
    "czech",
    "bohemia",
    "moravia",
    "magyar",
    "hungar",
    "vlach",
    "wallach",
    "romania",
    "rumania",
)


def royal_shapeshifter(character: Character) -> bool:
    """Whether the character is a crowned king of Slavic, Magyar or Vlach
    blood, who has Shapeshifter free (p. 122)."""
    words = re.findall(r"\w+", character.background.race_nationality.casefold())
    return character.background.church_rank == CROWNED_KING and any(
        word.startswith(people) for word in words for people in ROYAL_PEOPLES
    )


def royal_shapeshifter_index(character: Character) -> int | None:
    """The index of the Shapeshifter a crowned king of those peoples holds
    free, or None."""
    if not royal_shapeshifter(character):
        return None
    return next(
        (i for i, vf in enumerate(character.virtues_flaws) if vf.vf_id == SHAPESHIFTER),
        None,
    )


@check("virtues_flaws", CHARACTER_CHECKS)
def royal_shapeshifter_checks(saga: Saga, record: Record) -> list[Check]:
    if not isinstance(record, Character) or not royal_shapeshifter(record):
        return []
    held = royal_shapeshifter_index(record) is not None
    return [
        Check(
            "virtues_flaws",
            "A crowned Slavic, Magyar or Vlach king has Shapeshifter free",
            "pass" if held else "advice",
            (
                "Shapeshifter taken, outside the balance: a wolf, a lion or a dragon"
                if held
                else "Shapeshifter not taken: it is free, with the forms of a wolf, "
                "a lion and a dragon"
            ),
            "Against the Dark p. 122",
        )
    ]
