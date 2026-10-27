"""The Mysteries Revised Edition's Divination & Augury (Chapter Seven,
pp. 58-63) and Hermetic Astrology (Chapter Six, pp. 47-57), with the
Errata's corrections (p. 50).

Divination & Augury (a Major Supernatural Virtue) and Hermetic Dream
Interpreter (its dream-reading variant) give the Supernatural Ability
Divination at 1 (p. 59). A divination answers one question as a
Momentary, non-Ritual Intellego spell of any Form would (no Sense
targets); its Ease Factor is that spell's level (pp. 59-60).

    Casual:     stress die + Perception + Divination + aura
                + the omens' bonus (+0 to +3, rarely +4 or +5)   (one round)
    Ceremonial: stress die + Intelligence + Divination + aura
                + ceremonial bonus (the method, +1 to +5)
                + sympathetic bonus (the Arcane Connection's and the
                  sympathetic connections' multipliers, DE pp. 219-220)
                + magical bonus (a Scrying Device: its level / 10, up)
                                        (15 minutes per 5 of Ease Factor)
    Penetration = the Divination Total + Penetration bonus - Ease Factor

Not open-ended: the total makes the Ease Factor or fails (p. 62). The
Errata (p. 50) strikes "or Casual" from the bonuses' introduction, so
the three bonuses are the ceremony's only. The horoscope connections
count only for a diviner using Astrology (p. 62).

Hermetic Dream Interpreter (pp. 62-63): ceremonial divination through a
night's dreams, or a symbolic reading (stress die + Intelligence +
Divination, no aura) read against the Ease Factor table, and Dream
Calling (stress die + Presence + Divination + aura against 6).

Hermetic Astrology: Int + Artes Liberales (Astronomy) rolls (the
`horoscope_score` lab_virtues keeps):

- Daily Horoscope (an hour) and Nativity Horoscope (a day), each against
  9 (DE p. 220; TMRE p. 56).
- Periapt Horoscope (p. 48): against 9 on the equinox or solstice; a
  single-use Lab Text for a charged device: Lab Total / 5 charges
  (rounded up), an effect up to 5 x Astronomy. A botch wastes the season.
- Astrological Durations (Celestial Magic, pp. 49-50): a die + Int +
  Astronomy against 6 + the units wanted; a Daily Horoscope or the exact
  time measured each -3, precision +3, then a magical armillary sphere
  halves it. A miss is out by up to the shortfall; a botch botches the
  spell. Signs last a year at most.
- Favorable Hour (p. 50): against 3 x the bonus (+1 to +5); a botch is
  the bonus as a penalty for the hour.
- Astrologically linked enchantments (pp. 50-51): to a target, +2 for its
  Nativity Horoscope and the Arcane Connection's multiplier on the Lab
  Total; to a cycle, the Astronomy score on the Penetration or the
  frequency levels in its signs, the same as a penalty in the opposed
  element's.
- The magical armillary sphere (pp. 51-54): designed (Int + Astronomy) and
  crafted (Dex + Craft: Mechanisms or Clocks; Blacksmith at -3 and three
  more botch dice) against 12 each, 15 when one designs and another
  crafts, 3 less copying a precise sphere; a season's work. Opened as a
  skull-sized device, then Know the Heavens and Track the Heavens; set to
  another place with Int + Astronomy against 9.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass

from ..models import Character, SeasonPlan
from . import dice, lab_virtues, realms
from .breakdown import Breakdown, Line
from .lab import ability_score
from .penetration import ARCANE_CONNECTIONS, MAX_SYMPATHY, Sympathy
from .rounding import round_down, round_up

SOURCE = (
    "The Mysteries Revised Edition, Chapter Seven: Divination & Augury, "
    "pp. 58-63; Errata p. 50"
)
DREAM_SOURCE = "The Mysteries Revised Edition, Hermetic Dream Interpreter, pp. 62-63"
ASTROLOGY_SOURCE = (
    "The Mysteries Revised Edition, Chapter Six: Hermetic Astrology, pp. 47-51"
)
SPHERE_SOURCE = (
    "The Mysteries Revised Edition, The Magical Armillary Sphere, pp. 51-54; "
    "Errata p. 50"
)
HOROSCOPE_SOURCE = (
    "Ars Magica Definitive Edition, Sympathetic Connections, p. 220; The "
    "Mysteries Revised Edition, Astrological Correspondences, p. 56"
)

#: The Supernatural Ability, and the Virtues that give it (p. 59).
DIVINATION = "Divination"
AUGURY = "vf_divination_and_augury"
DREAMER = "vf_hermetic_dream_interpreter"
MORE_METHODS = "vf_additional_divination_method"
PERIAPT = "vf_periapt"
GIVES_DIVINATION = (AUGURY, DREAMER)

CASUAL, CEREMONIAL, SYMBOLIC, DREAM_CALLING = (
    "casual",
    "ceremonial",
    "symbolic",
    "dream_calling",
)
KINDS: dict[str, str] = {
    CASUAL: "Casual Divination (one round)",
    CEREMONIAL: "Ceremonial Divination",
    SYMBOLIC: "Symbolic dream interpretation",
    DREAM_CALLING: "Dream Calling",
}
#: The storyguide's bonus for apt omens in a casual divination: +0 to +3,
#: very rarely +4 or +5 (p. 62).
OMENS_MAX = 5
#: A method's ceremonial bonus, +1 to +5 (p. 62).
CEREMONIAL_MAX = 5
DREAM_CALLING_EASE = 6
#: What a symbolic reading reaches, by the Ease Factor table's bands (p. 63).
SYMBOLIC_READINGS: tuple[tuple[int, str], ...] = (
    (9, "an outline of the dreamer's state"),
    (12, "some of the reasons for the dream"),
    (15, "more of the reasons for the dream"),
    (18, "hints of its underlying causes and consequences"),
)


@dataclass(frozen=True)
class Method:
    """A method of divination from the Ceremonial Augury Phenomena table
    (p. 61): what is watched, the questions it suits with their bonus, and
    the Virtue it needs."""

    name: str
    phenomenon: str
    uses: tuple[tuple[str, int], ...] = ()
    requires: str = ""
    #: The bonus as the table words it when it isn't a list of uses.
    note: str = ""


METHODS: tuple[Method, ...] = (
    Method(
        "Aeromancy", "patterns in the air", (("health of nobles", 3), ("weather", 5))
    ),
    Method("Alectryomancy", "chickens eating", (("Corpus", 2), ("Mentem", 3))),
    Method("Aleuromancy", "flour burned or cooked", (("Herbam", 2), ("crops", 5))),
    Method(
        "Alomancy",
        "thrown salt",
        (("Aquam", 1), ("Terram", 2), ("weather", 3)),
    ),
    Method("Alphitomancy", "barley bread eaten", (("guilt or innocence", 5),)),
    Method(
        "Apantomancy", "chance meetings with animals", (("locations and buildings", 3),)
    ),
    Method("Ashagalomancy", "cast bones", (("ghosts", 3), ("Corpus", 4))),
    Method(
        "Astrology",
        "the heavens",
        (("any question", 5),),
        requires="vf_planetary_magic",
        note="+5, with the Daily and Nativity Horoscopes",
    ),
    Method(
        "Axinomancy",
        "a balanced hatchet",
        (("search for treasure", 3), ("detect thieves", 5)),
    ),
    Method("Belomancy", "arrows shot in the air", (("Auram", 1), ("battle", 3))),
    Method("Botanomancy", "burned sticks carved with questions", (("Herbam", 5),)),
    Method(
        "Capnomancy",
        "fumes of burning poppies",
        (("Imaginem", 2), ("dreams", 2), ("mental illness", 3)),
    ),
    Method(
        "Causimomancy",
        "objects placed in a fire",
        (("curses and bindings", 3), ("Ignem", 2)),
    ),
    Method(
        "Cephalomancy",
        "the severed head of a goat or donkey",
        (("Animal", 5), ("travel", 5)),
    ),
    Method("Ceroscopy", "wax dripped in water", (("marriage", 1), ("happiness", 3))),
    Method("Cleidomancy", "a key dangled from the Bible", (("sin", 3), ("lying", 5))),
    Method(
        "Cleromancy",
        "cast dice or lots",
        (("courts of justice", 2), ("business", 3), ("money", 5)),
    ),
    Method(
        "Crystalomancy",
        "crystal-gazing",
        (("friends", 1), ("enemies", 2), ("Vim", 3)),
    ),
    Method(
        "Dream Interpretation",
        "dreams",
        (("any question", 5),),
        requires=DREAMER,
    ),
    Method("Geomancy", "patterns in earth", (("kingdoms", 2), ("Terram", 5))),
    Method(
        "Haruspicy",
        "the entrails of sacrificed animals",
        (("Animal", 4), ("disease", 5)),
    ),
    Method("Hippomancy", "horses", (("nobles", 3), ("war", 4))),
    Method("Hydromancy", "water", (("judgments", 3), ("Aquam", 5))),
    Method("Lecanomancy", "bowls of fluid", (("ghosts", 5), ("spirits", 3))),
    Method("Myomancy", "mice and rats", (("battle", 2), ("disaster", 5))),
    Method(
        "Numerology",
        "the numerologist's book",
        requires="vf_hermetic_numerology",
        note="the book's bonus (Chapter Eleven)",
    ),
    Method(
        "Onomancy",
        "names compared",
        (("Mentem", 2), ("Corpus", 3), ("conflict resolution", 5)),
    ),
    Method("Ooscopy", "eggs burned or cooked", (("youth", 4), ("children", 5))),
    Method("Ophiomancy", "serpents", (("spirits", 3), ("sciences", 4))),
    Method("Phyllorhodomancy", "rose leaves", (("love", 3), ("desire", 5))),
    Method("Pyromancy", "flames", (("Ignem", 5),)),
    Method(
        "Rhabdomancy",
        "divining rods",
        (("hidden objects", 4), ("things underground", 5)),
    ),
    Method("Scapulomancy", "roasted shoulder blades", (("farming", 2), ("herds", 5))),
    Method("Scrying", "reflecting surfaces", (("clairvoyance", 5),)),
)
BY_NAME: dict[str, Method] = {m.name.lower(): m for m in METHODS}


def method(name: str) -> Method | None:
    """The table's method of that name (any case), or None."""
    return BY_NAME.get(name.strip().lower())


def method_text(found: Method) -> str:
    """'Pyromancy (flames): Ignem +5' -- a method's line from the table."""
    bonuses = found.note or ", ".join(f"{use} +{bonus}" for use, bonus in found.uses)
    return f"{found.name} ({found.phenomenon}): {bonuses}"


def _has(character: Character, vf_id: str) -> bool:
    return lab_virtues.has(character, vf_id)


def diviner(character: Character) -> bool:
    """Whether the character divines Hermetically: Divination & Augury or
    Hermetic Dream Interpreter (p. 59)."""
    return any(_has(character, vf_id) for vf_id in GIVES_DIVINATION)


def dreamer(character: Character) -> bool:
    return _has(character, DREAMER)


def methods(character: Character) -> list[str]:
    """The methods the character has: each Virtue's method as typed (the
    table's spelling when it names one), and Dream Interpretation with
    Hermetic Dream Interpreter."""
    found: list[str] = []
    for vf in character.virtues_flaws:
        if vf.vf_id in (AUGURY, MORE_METHODS):
            typed = str(vf.params.get("method") or "").strip()
            if typed:
                known = method(typed)
                found.append(known.name if known else typed)
    if dreamer(character):
        found.append("Dream Interpretation")
    return list(dict.fromkeys(found))


def method_problem(character: Character, name: str) -> str:
    """Why the character can't use this method ("" when he can): Astrology
    needs Planetary Magic, Numerology Hermetic Numerology (p. 59)."""
    found = method(name)
    if found is None or not found.requires or found.requires == DREAMER:
        return ""
    if found.requires == "vf_planetary_magic" and _has(
        character, lab_virtues.CELESTIAL
    ):
        return ""
    if _has(character, found.requires):
        return ""
    needs = (
        "Planetary Magic" if "planetary" in found.requires else "Hermetic Numerology"
    )
    return f"{found.name} needs {needs} (p. 59)."


def astrology(name: str) -> bool:
    return name.strip().lower() == "astrology"


def divination_score(character: Character) -> int:
    """Divination with its fixed bonus (0 without it)."""
    return sum(ability_score(character, DIVINATION))


def magical_bonus(effect_level: int) -> int:
    """A Scrying Device's bonus: +1 per 2 magnitudes, its effect's level
    over 10 rounded up; levels for uses a day don't count (p. 63)."""
    return round_up(max(0, effect_level) / 10)


def ceremony_minutes(ease: int) -> int:
    """How long a ceremonial divination takes: 15 minutes for each 5 of
    the Ease Factor (one magnitude), part of one counting whole (p. 62)."""
    return 15 * max(1, round_up(max(0, ease) / 5))


def sympathetic_lines(
    arcane_connection: str | None,
    sympathies: Sequence[Sympathy],
    *,
    by_astrology: bool,
) -> list[Line]:
    """The sympathetic bonus's lines: the Arcane Connection's multiplier
    and each connection's (at most +2 each, DE p. 219). The horoscopes
    count only divining by Astrology (p. 62)."""
    lines: list[Line] = []
    if arcane_connection is not None:
        lines.append(
            Line(
                f"Arcane Connection ({arcane_connection})",
                amount=ARCANE_CONNECTIONS[arcane_connection],
                source=SOURCE,
            )
        )
    for sympathy in sympathies:
        if "horoscope" in sympathy.name.lower() and not by_astrology:
            continue
        lines.append(
            Line(sympathy.name, amount=min(sympathy.bonus, MAX_SYMPATHY), source=SOURCE)
        )
    return lines


@dataclass(frozen=True)
class Divination:
    """One divination's circumstances, as the form gathers them."""

    kind: str = CEREMONIAL
    ease: int = 0
    aura: int = 0
    aura_realm: str = realms.HERMETIC
    specialty: bool = False
    #: Casual: the storyguide's bonus for apt omens.
    omens: int = 0
    #: Ceremonial: the method used and its bonus, the Arcane Connection
    #: (an ARCANE_CONNECTIONS key) and sympathetic connections, and the
    #: Scrying Device's effect level (0: none).
    method: str = ""
    ceremonial: int = 0
    arcane_connection: str | None = None
    sympathies: tuple[Sympathy, ...] = ()
    device_level: int = 0


def ease_of(divination: Divination) -> int:
    """The Ease Factor rolled against: Dream Calling's is 6, a symbolic
    reading has none (its total is read against the table)."""
    if divination.kind == DREAM_CALLING:
        return DREAM_CALLING_EASE
    return max(0, divination.ease)


def total(character: Character, divination: Divination) -> Breakdown:
    """The Divination Total before the die, line by line (pp. 60-63)."""
    kind = divination.kind
    characteristic = {
        CASUAL: ("Perception", character.characteristics.perception),
        DREAM_CALLING: ("Presence", character.characteristics.presence),
    }.get(kind, ("Intelligence", character.characteristics.intelligence))
    source = DREAM_SOURCE if kind in (SYMBOLIC, DREAM_CALLING) else SOURCE
    lines = [
        Line(characteristic[0], amount=characteristic[1], source=source),
        Line(DIVINATION, amount=divination_score(character), source=source),
    ]
    if divination.specialty:
        lines.append(Line("Specialty", amount=1, source=source))
    if kind != SYMBOLIC:
        aura = realms.aura_modifier(
            realms.HERMETIC, divination.aura_realm, divination.aura
        )
        if aura:
            lines.append(
                Line(f"{divination.aura_realm} aura", amount=aura, source=source)
            )
    if kind == CASUAL and divination.omens:
        lines.append(
            Line(
                "Apt omens",
                amount=max(0, min(divination.omens, OMENS_MAX)),
                source=SOURCE,
            )
        )
    if kind == CEREMONIAL:
        if divination.ceremonial:
            lines.append(
                Line(
                    f"Ceremonial bonus ({divination.method or 'the method'})",
                    amount=max(0, min(divination.ceremonial, CEREMONIAL_MAX)),
                    source=SOURCE,
                )
            )
        lines += sympathetic_lines(
            divination.arcane_connection,
            divination.sympathies,
            by_astrology=astrology(divination.method),
        )
        if divination.device_level:
            lines.append(
                Line(
                    f"Scrying Device (level {divination.device_level})",
                    amount=magical_bonus(divination.device_level),
                    source=SOURCE,
                )
            )
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def botch_dice(divination: Divination) -> int:
    """One botch die, and one more per point of a non-Magic aura (a
    symbolic reading is unaffected by aura, p. 63)."""
    if divination.kind == SYMBOLIC:
        return 1
    return 1 + realms.extra_botch_dice(
        realms.HERMETIC, divination.aura_realm, max(0, divination.aura)
    )


def penetration(divination_total: int, ease: int, penetration_bonus: int) -> int:
    """Divination Total + Penetration bonus - Ease Factor (p. 60)."""
    return divination_total + penetration_bonus - ease


def symbolic_reading(rolled: int) -> str:
    """What a symbolic reading of a dream reaches (p. 63)."""
    found = "nothing clear: the dream's symbols stay a muddle"
    for threshold, reading in SYMBOLIC_READINGS:
        if rolled >= threshold:
            found = reading
    return found


def outcome(divination: Divination, rolled: dice.Roll) -> str:
    """What the roll did, in a sentence."""
    shown = "a botch" if rolled.die.botched else str(rolled.die.value)
    head = f"{rolled.modifiers:+d} + {shown} = {rolled.total}"
    if divination.kind == SYMBOLIC:
        if rolled.die.botched:
            return f"{head}: a botch -- the reading misleads (p. 63)."
        return f"{head}: {symbolic_reading(rolled.total)} (p. 63)."
    ease = ease_of(divination)
    if rolled.die.botched:
        return f"{head} against {ease}: a botch."
    if divination.kind == DREAM_CALLING:
        if rolled.succeeded:
            return (
                f"{head} against {ease}: tonight he dreams of the subject, "
                "a dream to interpret later (p. 63)."
            )
        return f"{head} against {ease}: the dream wanders elsewhere."
    if rolled.succeeded:
        return f"{head} against {ease}: the divination answers truly."
    return f"{head} against {ease}: no answer (not open-ended, p. 62)."


# -- Hermetic Astrology -------------------------------------------------------

#: Daily and Nativity Horoscopes, the Periapt Horoscope, and adjusting a
#: magical armillary sphere: Int + Astronomy against 9.
HOROSCOPE_EASE = 9
PERIAPT_EASE = 9
ADJUST_SPHERE_EASE = 9
DURATION_BASE = 6
#: An Astrological Duration's units, by the Duration it stands for (p. 49).
DURATION_UNITS: dict[str, str] = {
    "Diameter": "Astrological Minutes",
    "Sun": "Astrological Hours",
    "Moon": "Astrological Days",
    "Year": "Astrological Signs",
}
#: Signs last a year at most (p. 49).
MAX_SIGNS = 12
#: The Ease Factor's options (p. 50).
DAILY_HOROSCOPE_STEP = -3
MEASURED_TIME_STEP = -3
PRECISION_STEP = 3
#: A Favorable Hour's or Laboratory Horoscope's bonus: +1 to +5.
BONUS_MAX = 5
#: An astrological link to a target: the Nativity Horoscope's bonus.
NATIVITY_BONUS = 2


def astronomy_total(character: Character) -> int:
    """Intelligence + Artes Liberales (Astronomy) (lab_virtues')."""
    return lab_virtues.horoscope_score(character)


def astronomy_score(character: Character) -> int:
    """Artes Liberales (Astronomy) alone: what a Periapt's level and an
    astrological cycle's adjustment use (pp. 48, 51)."""
    return (
        lab_virtues.horoscope_score(character) - character.characteristics.intelligence
    )


def duration_ease(
    units: int,
    *,
    daily_horoscope: bool = False,
    measured: bool = False,
    precision: bool = False,
    sphere: bool = False,
) -> int:
    """6 + the units wanted, -3 with a Daily Horoscope for the place, -3
    with the exact time measured, +3 for a precise end; a magical armillary
    sphere then halves it (rounded down), p. 50."""
    ease = DURATION_BASE + max(0, units)
    ease += DAILY_HOROSCOPE_STEP if daily_horoscope else 0
    ease += MEASURED_TIME_STEP if measured else 0
    ease += PRECISION_STEP if precision else 0
    ease = max(0, ease)
    return round_down(ease / 2) if sphere else ease


def calm_calculation(*, measured: bool, daily_horoscope: bool, sphere: bool) -> bool:
    """Whether the duration may be worked with a simple die: the exact time
    known and a Daily Horoscope or a sphere, checked over a Diameter
    (p. 50)."""
    return measured and (daily_horoscope or sphere)


def duration_outcome(rolled: dice.Roll, units: int, unit: str) -> str:
    """An Astrological Duration's calculation (p. 49)."""
    shown = "a botch" if rolled.die.botched else str(rolled.die.value)
    ease = rolled.ease_factor or 0
    head = f"{rolled.modifiers:+d} + {shown} = {rolled.total} against {ease}"
    if rolled.die.botched:
        return f"{head}: a botch -- the spell botches."
    if rolled.succeeded:
        return f"{head}: the spell lasts {units} {unit}, as reckoned."
    miss = ease - rolled.total
    return (
        f"{head}: miscalculated -- it lasts anywhere from {max(0, units - miss)} "
        f"to {units + miss} {unit} (the storyguide's choice; he finds out when "
        "it ends)."
    )


def favorable_hour_ease(bonus: int) -> int:
    """Three times the bonus wanted (p. 50)."""
    return 3 * max(1, min(bonus, BONUS_MAX))


def favorable_hour_outcome(rolled: dice.Roll, bonus: int) -> str:
    shown = "a botch" if rolled.die.botched else str(rolled.die.value)
    head = (
        f"{rolled.modifiers:+d} + {shown} = {rolled.total} against {rolled.ease_factor}"
    )
    if rolled.die.botched:
        return f"{head}: a botch -- spells cast in that hour take -{bonus}."
    if rolled.succeeded:
        return f"{head}: +{bonus} to spells cast in the favorable hour."
    return f"{head}: the reckoning is wrong; the hour brings nothing."


def favorable_hour(rng: random.Random) -> int:
    """The storyguide's quick favorable hour (p. 50): a simple die read 0-9
    times 10, plus a simple die, divided by 4 rounded up, 25 rerolled: an
    hour 1-24, counted from midnight."""
    while True:
        hour = round_up(((dice.simple_die(rng) % 10) * 10 + dice.simple_die(rng)) / 4)
        if hour != 25:
            return hour


def horoscope_outcome(rolled: dice.Roll, what: str) -> str:
    """A Daily, Nativity or Periapt Horoscope against 9."""
    shown = "a botch" if rolled.die.botched else str(rolled.die.value)
    head = (
        f"{rolled.modifiers:+d} + {shown} = {rolled.total} against {rolled.ease_factor}"
    )
    if rolled.die.botched:
        return f"{head}: a botch -- the {what} is faulty and he doesn't know it."
    if rolled.succeeded:
        return f"{head}: the {what} is sound."
    return f"{head}: the {what} is faulty, and he knows it."


def periapt_charges(lab_total: int) -> int:
    """A Periapt Horoscope's charges: as from a Lab Text, the Lab Total over
    5 rounded up (p. 48; DE p. 262)."""
    return max(1, round_up(max(0, lab_total) / 5))


def periapt_max_level(character: Character) -> int:
    """The highest effect a Periapt Horoscope instills: 5 x Astronomy."""
    return 5 * max(0, astronomy_score(character))


def linked_bonus(arcane_connection: str | None) -> int:
    """An enchantment linked to one target: the Nativity Horoscope's +2 and
    the Arcane Connection's multiplier on the Lab Total (p. 50)."""
    return NATIVITY_BONUS + (
        ARCANE_CONNECTIONS[arcane_connection] if arcane_connection else 0
    )


#: The signs of each element, and the element each opposes (pp. 51, 56).
ELEMENT_SIGNS: dict[str, tuple[str, ...]] = {
    "Fire": ("Aries", "Leo", "Sagittarius"),
    "Water": ("Cancer", "Scorpio", "Pisces"),
    "Air": ("Libra", "Aquarius", "Gemini"),
    "Earth": ("Capricorn", "Taurus", "Virgo"),
}
OPPOSED: dict[str, str] = {
    "Fire": "Water",
    "Water": "Fire",
    "Air": "Earth",
    "Earth": "Air",
}
#: Frequency levels: 0 is once a day, 10 unlimited (DE's Effect Frequency).
MAX_FREQUENCY_LEVELS = 10


def element_of(sign: str) -> str:
    return next((e for e, signs in ELEMENT_SIGNS.items() if sign in signs), "")


def cycle_frequency(levels: int, adjustment: int) -> int | None:
    """A cyclic effect's frequency levels in a sign that moves them by
    `adjustment`: past 10 counts 10 (unlimited), below 0 it can't be used
    (None), p. 51."""
    moved = levels + adjustment
    if moved < 0:
        return None
    return min(moved, MAX_FREQUENCY_LEVELS)


# -- The magical armillary sphere ----------------------------------------------

DESIGN_EASE = 12
CRAFT_EASE = 12
#: One designs, another crafts under his eye: both +3; copying a precise
#: sphere: both -3 (p. 52).
BY_ANOTHER_STEP = 3
COPYING_STEP = -3
#: Craft: Blacksmith in place of Mechanisms or Clocks.
BLACKSMITH_PENALTY = -3
BLACKSMITH_BOTCH_DICE = 3
CRAFTS = ("Craft: Mechanisms", "Craft: Clocks")
BLACKSMITH = "Craft: Blacksmith"
#: Craft the Mechanism's two rolls (p. 52; Errata p. 50: CrTe 20, Ind).
SPELL_DESIGN_EASE = 18
SPELL_FINESSE_EASE = 18
#: Pawns to open it as an invested device, by its metal (p. 53).
OPENING_PAWNS: dict[str, int] = {"base metal": 15, "silver": 18, "gold": 30}
#: Its two effects: Know the Heavens (InVi 29) and Track the Heavens (ReTe
#: 28), seven spaces and seven pawns together (p. 53).
KNOW_THE_HEAVENS = 29
TRACK_THE_HEAVENS = 28
SPHERE_EFFECT_PAWNS = 7
#: The designer only testing another's work: a seven-day distraction.
TESTING_DAYS = 7


def design_ease(*, by_another: bool = False, copying: bool = False) -> int:
    return (
        DESIGN_EASE
        + (BY_ANOTHER_STEP if by_another else 0)
        + (COPYING_STEP if copying else 0)
    )


def craft_ease(*, by_another: bool = False, copying: bool = False) -> int:
    return (
        CRAFT_EASE
        + (BY_ANOTHER_STEP if by_another else 0)
        + (COPYING_STEP if copying else 0)
    )


def best_craft(character: Character) -> tuple[str, int, int]:
    """The Craft he builds a sphere with: (Ability, score with the
    penalty, extra botch dice); Mechanisms or Clocks, else Blacksmith at
    -3 and three more botch dice ("" with none)."""
    fine = [(name, sum(ability_score(character, name))) for name in CRAFTS]
    fine = [(name, score) for name, score in fine if score]
    if fine:
        name, score = max(fine, key=lambda pair: pair[1])
        return name, score, 0
    smith = sum(ability_score(character, BLACKSMITH))
    if smith:
        return BLACKSMITH, smith + BLACKSMITH_PENALTY, BLACKSMITH_BOTCH_DICE
    return "", 0, 0


def sphere_outcome(rolled: dice.Roll, what: str) -> str:
    """A design or craft roll: a failure leaves it flawed, a botch hides the
    flaw until it botches a calculation that matters (pp. 52-53)."""
    shown = "a botch" if rolled.die.botched else str(rolled.die.value)
    head = (
        f"{rolled.modifiers:+d} + {shown} = {rolled.total} against {rolled.ease_factor}"
    )
    if rolled.die.botched:
        return (
            f"{head}: the {what} hides a subtle flaw, found only when it "
            "botches an important calculation."
        )
    if rolled.succeeded:
        return f"{head}: the {what} is sound."
    return f"{head}: the {what} is flawed."


# -- Celestial Magic's Laboratory Horoscope opening a device ----------------


def horoscope_opening(magus: Character, plan: SeasonPlan) -> tuple[int, str]:
    """The pawns a Celestial magus's Laboratory Horoscope takes off opening
    an invested device (at least one is still paid), and what to say of it
    (p. 49). Only a horoscope whose die is typed on the plan counts; one
    rolled as the season is played can't change the vis already set."""
    wanted = max(0, min(plan.horoscope, BONUS_MAX))
    if not wanted or not lab_virtues.has(magus, lab_virtues.CELESTIAL):
        return 0, ""
    needed = 3 * wanted
    if plan.horoscope_die is None:
        return 0, (
            f"Celestial Magic: a Laboratory Horoscope +{wanted} would take {wanted} "
            "off the pawns; type its die on the plan to count it (TMRE p. 49)."
        )
    if plan.horoscope_die + astronomy_total(magus) >= needed:
        return wanted, (
            f"Celestial Magic: the Laboratory Horoscope takes {wanted} off the "
            "pawns, at least one paid; the spaces stay as they are (TMRE p. 49)."
        )
    return 0, ""
