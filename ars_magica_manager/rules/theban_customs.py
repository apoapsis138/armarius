"""Byzantine customs (The Sundered Eagle, Chapter 4: Culture & Customs and
Chapter 12's Divine pages), as plain rules: the rolls and totals the
Theban customs' More actions use.

- Hermetic correspondence (p. 44): composing a rhetorical letter takes a
  day; Communication + a relevant Lore against 6 for a straightforward
  message, higher for a subtler one. Reading its purpose is Intelligence
  + a relevant Lore against the same Ease Factor.
- The Oath Invocation roll (p. 48): Communication + Charm + a simple die,
  +6 if Styx was named in the oath, against 15 + a simple die. Heard, the
  spirit may punish the oath-breaker with a Flaw: any General Flaw, or a
  Lesser or Greater Malediction (the book's six examples are catalog
  entries). A Major Flaw only from an entity of Might 40 or more,
  otherwise a Minor one.
- Greek Fire (p. 47): an alchemical reagent (Art & Academe p. 76, level
  15). Each season making it rolls a stress die that matters only if it
  botches, with a botch die for every dose being made; a botch is an
  explosion. The laboratory's Safety takes botch dice away (Covenants p.
  111; DE p. 288). A master alchemist can lead as many subordinates as
  his Leadership. The hand-held siphon's figures are SIPHON.
- Icons (pp. 133-134): only someone in Holy Orders with Theology 3 or more
  can paint an eikon. Holy Orders are the ordained male clergy, sub-deacon
  and up (DE p. 500, p. 74): a monk or nun as such is not in them, so a
  monk counts only with a priest's or senior cleric's Virtue. Its Aesthetic Quality is Dexterity + Craft:
  Painting + bonuses: +1 for each season of Standard gilding or
  bejewelling, +3 for each Excellent result, and the painter's Pious
  trait if the saint is his patron. An eikon adds its Aesthetic Quality /
  5 (rounded up) to invoking its saint (or, an icon of Christ, God's
  aid). Venerating it takes an hour of contemplation, or in an emergency
  a Fatigue level and Presence + Concentration against 15. Eikons have
  no Divine Might; acheiropoieta, icons not made by hand, are powerful
  relics.
- A mother's curse (p. 136): a Lesser Malediction, -3 to every roll in
  one area of expertise (military, academic or professional) her child
  has, laid for a good reason; lifted only by completing the task she set
  or by divine intervention.

The Definitive Edition's Lesser Malediction (Minor, Supernatural) and
Greater Malediction (Major, Supernatural) are the Flaws these curses take
(DE pp. 132, 135); the errata change nothing used here."""

from __future__ import annotations

import random
from dataclasses import dataclass

from ..models import Character, Saga
from . import artistry, dice
from .rounding import round_up
from .scores import ability_level, botch_dice_change, with_botch_change

SOURCE = (
    "The Sundered Eagle pp. 44, 47, 48, 133-134, 136; Art & Academe p. 76; "
    "Covenants p. 111; Definitive Edition pp. 132, 135, 288"
)
TSE = "TSE"

# -- Hermetic correspondence (p. 44) --

#: A straightforward message's Ease Factor; subtler ones are higher.
LETTER_EASE = 6
COMPOSE = "compose"
READ = "read"
LETTER_MODES: dict[str, str] = {
    COMPOSE: "Compose a letter (Communication + Lore)",
    READ: "Read a letter's purpose (Intelligence + Lore)",
}


def lores(character: Character) -> list[str]:
    """The character's Lore Abilities, the highest first."""
    held = [a for a in character.abilities if "Lore" in a.name]
    return [a.name for a in sorted(held, key=lambda a: -a.level)]


@dataclass(frozen=True)
class Letter:
    """A correspondence roll's terms: what it adds to its die, against
    what, and each term as words."""

    total: int
    ease: int
    terms: tuple[str, ...]


def letter(character: Character, mode: str, lore: str, subtlety: int) -> Letter:
    """Communication (composing) or Intelligence (reading) + the Lore,
    against 6 + how much subtler the message is."""
    c = character.characteristics
    if mode == READ:
        name, score = "Intelligence", c.intelligence
    else:
        name, score = "Communication", c.communication
    level = ability_level(character, lore) if lore else 0
    terms = [f"{name} {score:+d}", f"+ {lore or 'no Lore'} {level}"]
    return Letter(score + level, LETTER_EASE + max(0, subtlety), tuple(terms))


# -- the Oath Invocation roll (p. 48) --

OATH_EASE = 15
STYX_BONUS = 6
#: The Might from which a spirit or saint can lay a Major Flaw.
MAJOR_MIGHT = 40


@dataclass(frozen=True)
class Invocation:
    """An Oath Invocation roll: the invoker's total and simple die, and the
    Ease Factor's simple die."""

    total: int
    die: int
    ease_die: int

    @property
    def rolled(self) -> int:
        return self.total + self.die

    @property
    def ease(self) -> int:
        return OATH_EASE + self.ease_die

    @property
    def heard(self) -> bool:
        return self.rolled >= self.ease


def oath_total(character: Character, styx: bool) -> tuple[int, tuple[str, ...]]:
    """Communication + Charm, +6 with Styx named in the oath."""
    com = character.characteristics.communication
    charm = ability_level(character, "Charm")
    terms = [f"Communication {com:+d}", f"+ Charm {charm}"]
    if styx:
        terms.append(f"+ {STYX_BONUS} Styx")
    return com + charm + (STYX_BONUS if styx else 0), tuple(terms)


def invoke_oath(character: Character, styx: bool, rng: random.Random) -> Invocation:
    total, _ = oath_total(character, styx)
    return Invocation(total, dice.simple_die(rng), dice.simple_die(rng))


def punishment_tier(might: int | None) -> str:
    """ "Major" from a Might of 40 or more, else "Minor"."""
    return "Major" if (might or 0) >= MAJOR_MIGHT else "Minor"


#: The book's maledictions for oath-breakers, as catalog Flaws, by tier,
#: the plain Malediction Flaws last (any other curse of that weight).
MALEDICTIONS: dict[str, tuple[str, ...]] = {
    "Minor": (
        "vf_lesser_malediction_ashen_food",
        "vf_lesser_malediction_mephitic_odor",
        "vf_lesser_malediction_rotting_clothes",
        "vf_lesser_malediction",
    ),
    "Major": (
        "vf_greater_malediction_toad_of_lies",
        "vf_greater_malediction_opening_wounds",
        "vf_greater_malediction_breaking_tools",
        "vf_greater_malediction",
    ),
}


def maledictions(might: int | None) -> tuple[str, ...]:
    """The maledictions an entity of `might` can lay: a Minor one always,
    a Major one too from Might 40."""
    if punishment_tier(might) == "Major":
        return (*MALEDICTIONS["Minor"], *MALEDICTIONS["Major"])
    return MALEDICTIONS["Minor"]


# -- Greek Fire (p. 47) --

#: Greek Fire's reagent level (Art & Academe p. 76).
GREEK_FIRE_LEVEL = 15
#: The hand-held siphon, a missile weapon used with Profession: Naffatun:
#: (Init, Attack, Defense, Damage, Range in paces, minimum Strength, Load,
#: Cost). A shield's Defense adds to Soak instead; a dose is 10 sprays.
SIPHON = (-2, 4, 0, 10, 5, 2, 3, "Expensive")
SPRAYS_PER_DOSE = 10


def greek_fire_botch_dice(character: Character, doses: int, safety: int) -> int:
    """One botch die per dose, less the laboratory's Safety (never below
    none), with the Virtues and Flaws that change a laboratory's botch
    dice."""
    count = max(0, doses - safety)
    change, _ = botch_dice_change(character.virtues_flaws, ("laboratory",))
    return with_botch_change(count, change)


@dataclass(frozen=True)
class Batch:
    """A season's Greek Fire: the botch dice and the stress die."""

    botch_dice: int
    die: dice.DieResult

    @property
    def exploded(self) -> bool:
        return self.die.botched


def make_greek_fire(
    character: Character,
    doses: int,
    safety: int,
    rng: random.Random,
    *,
    saga: Saga | None = None,
) -> Batch:
    count = greek_fire_botch_dice(character, doses, safety)
    return Batch(count, dice.stress_die(rng, count, saga=saga))


# -- icons (pp. 133-134) --

#: The Social Status Virtues that put a character in Holy Orders, the
#: ordained clergy from sub-deacon up (DE p. 500, p. 74; The Sundered
#: Eagle p. 133). Religious alone does not: monks are not ordained as such,
#: and women may not take holy orders. A Clerk may be a sub-deacon or
#: deacon, but the Virtue does not say he is, so it does not count.
HOLY_ORDERS = frozenset(
    {
        "vf_priest",
        "vf_brother_chaplain",
        "vf_eastern_priest",
        "vf_senior_clergy",
    }
)
THEOLOGY = "Theology: Christian"
THEOLOGY_NEEDED = 3
PAINTING = "Craft: Painting"
#: The bonus to Aesthetic Quality for a season of decoration, by its result.
STANDARD_DECORATION = 1
EXCELLENT_DECORATION = 3
EMERGENCY_EASE = 15
#: Kinds of record on a church's relics list.
RELIC = "relic"
EIKON = "eikon"
ACHEIROPOIETON = "acheiropoieton"
RELIC_KINDS: dict[str, str] = {
    RELIC: "Relic",
    EIKON: "Icon (an eikon)",
    ACHEIROPOIETON: "Icon not made by hand (acheiropoieton)",
}


def icon_problem(character: Character) -> str | None:
    """Why the character can't paint an eikon, if they can't."""
    if not {vf.vf_id for vf in character.virtues_flaws} & HOLY_ORDERS:
        return (
            "Only someone in Holy Orders (an ordained priest or senior "
            "cleric) can paint an eikon."
        )
    if ability_level(character, THEOLOGY) < THEOLOGY_NEEDED:
        return f"An eikon's painter needs {THEOLOGY} {THEOLOGY_NEEDED} or more."
    return None


def pious(character: Character) -> int:
    """The character's Pious Personality Trait (0 without one)."""
    return next(
        (t.score for t in character.personality_traits if t.name.casefold() == "pious"),
        0,
    )


@dataclass(frozen=True)
class Eikon:
    """An eikon's Aesthetic Quality and each term of it."""

    quality: int
    terms: tuple[str, ...]


def eikon(
    character: Character,
    standard: int = 0,
    excellent: int = 0,
    patron: bool = False,
    other: int = 0,
) -> Eikon:
    """Dexterity + Craft: Painting (with Puissant, Free Expression and
    Inspirational, as any work of art's, Art & Academe p. 124) + the
    decoration's bonuses (+1 each Standard season, +3 each Excellent
    result) + Pious if the saint is the painter's patron (a positive trait
    only) + other bonuses."""
    start = artistry.base_quality(character, PAINTING, "dexterity")
    terms, total = list(start.terms), start.quality
    decoration = STANDARD_DECORATION * max(0, standard) + EXCELLENT_DECORATION * max(
        0, excellent
    )
    if decoration:
        terms.append(f"+ decoration {decoration}")
        total += decoration
    devotion = max(0, pious(character)) if patron else 0
    if devotion:
        terms.append(f"+ Pious {devotion}")
        total += devotion
    if other:
        terms.append(f"{'+' if other > 0 else '-'} other {abs(other)}")
        total += other
    return Eikon(total, tuple(terms))


def invocation_bonus(quality: int) -> int:
    """What venerating an eikon adds to invoking its saint: its Aesthetic
    Quality / 5, rounded up (never below 0)."""
    return max(0, round_up(quality / 5))


def emergency_total(character: Character) -> int:
    """Presence + Concentration, for venerating an icon in an emergency."""
    return character.characteristics.presence + ability_level(
        character, "Concentration"
    )


# -- a mother's curse (p. 136) --

MOTHERS_CURSE = "vf_lesser_malediction_mothers_curse"
CURSE_PENALTY = -3
EXPERTISE: tuple[str, ...] = ("military", "academic", "professional")
