"""The Mysteries of House Merinita (Houses of Hermes: Mystery Cults pp.
85-106; the Definitive Edition's Merinita section, pp. 236-240, wins where
they differ; Errata p. 55).

The Mystery Cult (pp. 85-86, 88): the House's Outer Mystery is Faerie
Magic (DE p. 236), and one who holds it belongs to the House. Its Lore is
House Merinita Lore (the Ability catalog's "Mystery Cult Lore: Merinita");
an Initiate needs it at 1 for an Inner Mystery (p. 88). The Inner
Mysteries fall into schools (p. 86): the Arcadian (Arcadian Travel,
Animae Magic, Becoming), Folk (Charm Magic, Story Magic, Symbolic Magic)
and Illusion Mysteries (Spell Timing, Glamour, Perpetuity) need Faerie
Magic; Binding the Gift is the House's own; the Nature Mysteries
(Awakening, Wilding, Guardian of Nature) need their own Outer Mystery,
Nature Lore. Glamour always brings Vulnerable Magic as its Ordeal,
with a condition the magus doesn't have it for already (pp. 87, 102);
Perpetuity usually brings Unnatural Magic. The House's
lineages' sample Scripts are the tradition catalog's
"trad_merinita_mysteries".

The Inner Mysteries' rules, as functions the seasons and notes can use:
faerie familiars and their three faerie cords (pp. 89-90, and Faerie
Chains of the Familiar Slave), Binding the Gift's cords on social rolls
(pp. 91-92), Arcadian Travel's trods (p. 92), Animae Magic's guidelines
(pp. 92-95; Errata p. 55), Becoming's transformation rituals (pp. 93, 96;
Errata p. 55), charms and Charm Magic (pp. 88, 96-98), Story Magic
(p. 98), Symbolic Magic (pp. 98-99), Glamour (pp. 101-102), and the
Nature Mysteries: Nature Lore, Awakening, Wilding and Guardian of Nature
(pp. 102-106; Errata p. 55). Faerie Magic's own rules (the Ability, its
parameters, Spell Timing's Durations, Perpetuity's) are in
rules.lab_virtues, rules.spell_levels and rules.casting_virtues.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from ..models import FATIGUE_LEVELS, Character, Laboratory, Saga, VirtueFlawInstance
from . import lab, lab_virtues
from .breakdown import Breakdown, Line
from .casting import magnitude
from .rounding import round_down, round_up
from .spell_levels import RITUAL_MINIMUM

MC = "Houses of Hermes: Mystery Cults"
SOURCE = f"{MC}, House Merinita, Merinita Mysteries, pp. 85-106"
ERRATA = "Errata p. 55"
INITIATION_SOURCE = f"{MC}, Merinita Mysteries p. 85, House Merinita Lore p. 88"

#: The cult's Lore, as the Ability catalog names it; the book's own name
#: and a shorter one count too.
CULT_LORE = "Mystery Cult Lore: Merinita"
LORE_NAMES = (CULT_LORE, "House Merinita Lore", "Merinita Lore")
#: The tradition catalog entry holding the lineages' sample Scripts.
CULT_TRADITION = "trad_merinita_mysteries"
FAERIE_MAGIC = "vf_faerie_magic"
NATURE_LORE = "vf_nature_lore"
#: The Lore an Initiate needs for an Inner Mystery (p. 88).
LORE_FOR_INNER = 1

ARCADIAN, FOLK, ILLUSION, NATURE, HOUSE = (
    "Arcadian",
    "Folk",
    "Illusion",
    "Nature",
    "House",
)
#: The Inner Mysteries (p. 86): Virtue -> (school, tier).
INNER_MYSTERIES: dict[str, tuple[str, str]] = {
    "vf_binding_the_gift": (HOUSE, "Minor"),
    "vf_arcadian_travel": (ARCADIAN, "Minor"),
    "vf_animae_magic": (ARCADIAN, "Major"),
    "vf_becoming": (ARCADIAN, "Major"),
    "vf_charm_magic": (FOLK, "Minor"),
    "vf_story_magic": (FOLK, "Major"),
    "vf_symbolic_magic": (FOLK, "Major"),
    "vf_spell_timing": (ILLUSION, "Minor"),
    "vf_glamour": (ILLUSION, "Major"),
    "vf_perpetuity": (ILLUSION, "Major"),
    "vf_awakening": (NATURE, "Minor"),
    "vf_wilding": (NATURE, "Major"),
    "vf_guardian_of_nature": (NATURE, "Major"),
}
#: The Outer Mystery each school's Mysteries need (pp. 85, 102-104).
SCHOOL_NEEDS: dict[str, str] = {
    ARCADIAN: FAERIE_MAGIC,
    FOLK: FAERIE_MAGIC,
    ILLUSION: FAERIE_MAGIC,
    NATURE: NATURE_LORE,
}
OUTER_NAMES = {FAERIE_MAGIC: "Faerie Magic", NATURE_LORE: "Nature Lore"}
GLAMOUR = "vf_glamour"
PERPETUITY = "vf_perpetuity"
VULNERABLE_MAGIC = "vf_vulnerable_magic"
UNNATURAL_MAGIC = "vf_unnatural_magic"
#: Mysteries whose Initiation always gives a Flaw, a Major Ordeal (p. 102).
ALWAYS_GIVES: dict[str, str] = {GLAMOUR: VULNERABLE_MAGIC}
#: Mysteries whose Initiation usually gives a Flaw (p. 102).
USUALLY_GIVES: dict[str, str] = {PERPETUITY: UNNATURAL_MAGIC}


def _score(character: Character, ability: str) -> int:
    level, bonus = lab.ability_score(character, ability)
    return level + bonus


def is_merinita(magus: Character | None) -> bool:
    """Whether `magus` has the House's Outer Mystery, Faerie Magic."""
    return magus is not None and lab_virtues.has(magus, FAERIE_MAGIC)


def cult_lore(magus: Character) -> int:
    """The magus's House Merinita Lore (the best of its names)."""
    return max((_score(magus, name) for name in LORE_NAMES), default=0)


def faerie_magic(magus: Character) -> int:
    """The magus's Faerie Magic Ability (0 without it)."""
    return lab_virtues.faerie_magic(magus)


def inner_mystery_problem(initiate: Character, vf_id: str) -> str:
    """What stops an Initiation into one of the House's Inner Mysteries
    ("" if nothing, or for any other Virtue): a school's Outer Mystery
    (Faerie Magic, or Nature Lore for the Nature Mysteries), and House
    Merinita Lore 1 for all but the Nature Mysteries, which are learned
    outside the House's Lore (pp. 88, 102-103)."""
    found = INNER_MYSTERIES.get(vf_id)
    if found is None:
        return ""
    school, tier = found
    needs = SCHOOL_NEEDS.get(school)
    if needs and not lab_virtues.has(initiate, needs):
        return (
            f"{initiate.name} hasn't the Outer Mystery {OUTER_NAMES[needs]}: the "
            f"{school} Mysteries build on it ({SOURCE})."
        )
    if school != NATURE and cult_lore(initiate) < LORE_FOR_INNER:
        return (
            f"{initiate.name} needs House Merinita Lore {LORE_FOR_INNER} to be "
            f"Initiated into a {tier} Inner Mystery ({INITIATION_SOURCE})."
        )
    return ""


def ordeal_flaw(
    vf_id: str, plan_flaw: str = "", condition: str = ""
) -> VirtueFlawInstance | None:
    """The Flaw an Inner Mystery's Initiation always gives (Glamour:
    Vulnerable Magic, a Major Ordeal, p. 102), with the plan's `condition`,
    unless the plan's own Ordeal is that Flaw already. None for any other
    Virtue."""
    flaw = ALWAYS_GIVES.get(vf_id)
    if flaw is None or plan_flaw == flaw:
        return None
    params = {"condition": condition.strip()} if condition.strip() else {}
    return VirtueFlawInstance(flaw, params)


def _conditions_held(initiate: Character, vf_id: str) -> set[str]:
    return {
        vf.params.get("condition", "").strip().casefold()
        for vf in initiate.virtues_flaws
        if vf.vf_id == vf_id
    }


def condition_problem(
    initiate: Character,
    vf_id: str,
    condition: str,
    plan_flaw: VirtueFlawInstance | None,
) -> str:
    """What is wrong with the condition of the Flaw Glamour's Initiation
    always gives ("" if nothing, or for any other Virtue): it must be
    named, and differ from any the magus has the Flaw with already, since
    Vulnerable Magic is taken again only with a new condition (pp. 87,
    102). `plan_flaw`: the plan's own Ordeal Flaw, when it names
    Vulnerable Magic itself."""
    flaw = ALWAYS_GIVES.get(vf_id)
    if flaw is None:
        return ""
    if plan_flaw is not None and plan_flaw.vf_id == flaw:
        condition = plan_flaw.params.get("condition", "")
    if not condition.strip():
        return (
            "Name the condition of the Vulnerable Magic Glamour brings: it "
            f"always comes with a new one ({GLAMOUR_SOURCE})."
        )
    if condition.strip().casefold() in _conditions_held(initiate, flaw):
        return (
            f"{initiate.name} has Vulnerable Magic ({condition.strip()}) "
            "already: Glamour's must have a different condition "
            f"({MC} pp. 87, 102)."
        )
    return ""


def initiation_notes(vf_id: str) -> list[str]:
    """What an Inner Mystery's Initiation brings besides its Virtue."""
    if vf_id in ALWAYS_GIVES:
        return [
            "Glamour always brings the Major Flaw Vulnerable Magic as its "
            "Ordeal, with a condition the magus doesn't have it for already "
            "(Houses of Hermes: Mystery Cults pp. 87, 102)."
        ]
    if vf_id in USUALLY_GIVES:
        return [
            "Merinitae who learn Perpetuity usually gain Unnatural Magic in "
            "their Initiation (Houses of Hermes: Mystery Cults p. 102)."
        ]
    return []


# -- Faerie familiars and the three faerie cords (pp. 89-90) -----------------

FAMILIAR_SOURCE = (
    f"{MC}, Enchanting a Faerie Familiar and the Three Faerie Cords, pp. 89-90"
)
POSITIVE_CORDS = ("golden", "silver", "bronze")
NEGATIVE_CORDS = ("leaden", "iron", "tin")
#: What each negative cord costs maga and familiar (p. 90).
NEGATIVE_CORD_EFFECTS: dict[str, str] = {
    "leaden": (
        "its value in more botch dice using her powers in the Dominion or "
        "touching a holy object, and off her rolls to resist Divine influence"
    ),
    "iron": (
        "its value off all her rolls while touching iron and off Soak against "
        "iron weapons, and in more botch dice using her powers in an Infernal aura"
    ),
    "tin": (
        "outside a supernatural aura, its value off her Personality, natural "
        "resistance, healing, deprivation and Aging rolls, and off her Soak"
    ),
}
#: Faerie Chains of the Familiar Slave: its level is at least the
#: creature's Might + 15 (p. 90).
SLAVE_CHAINS_MARGIN = 15


def can_bind_faerie(magus: Character) -> bool:
    """Whether the magus may bind a faerie as a familiar: only with the
    Outer Mystery of Faerie Magic (p. 89)."""
    return is_merinita(magus)


def might_per_fatigue(might: int) -> int:
    """Might Points each Fatigue level is worth between a maga and her
    faerie familiar: its Might / 5 (Shared Powers, Shared Fatigue,
    p. 89)."""
    return round_down(max(0, might) / 5)


def fatigue_cost(might: int, reached: str) -> int:
    """The Might Points a faerie familiar spends to take a Fatigue level
    for its maga: the value of the level she would reach (Winded 1, Weary
    2, ...) x its Might / 5 (p. 89; Might 10, Winded 2, Weary 4)."""
    levels: tuple[str, ...] = FATIGUE_LEVELS
    if reached not in levels[1:]:
        raise ValueError(f"{reached!r} isn't a Fatigue level she can reach.")
    return levels.index(reached) * might_per_fatigue(might)


def cord_to_age(positive: Mapping[str, int], negative: Mapping[str, int]) -> str:
    """Which cord of a faerie familiar's bond takes this year's Aging
    Point ("" for none): the highest cord on whichever side, positive or
    negative, totals more; none while the two sides are equal (p. 90). A
    faerie bond with no negative cords ages its highest positive cord
    (p. 89). A tie for highest goes to the first cord named."""
    plus = sum(max(0, v) for v in positive.values())
    minus = sum(max(0, v) for v in negative.values())
    if plus == minus:
        return ""
    side = positive if plus > minus else negative
    return max(side, key=lambda name: side[name])


def aged_cord(score: int, aging_points: int) -> tuple[int, int]:
    """A cord after `aging_points`: it drops by one once its points pass
    its score, as a Characteristic ages (+3 falls to +2 after four years,
    to +1 three more, to 0 two more, p. 89). Returns the new score and the
    points left toward the next drop."""
    while score > 0 and aging_points > score:
        aging_points -= score + 1
        score -= 1
    return score, max(0, aging_points) if score else 0


def bond_breaks(positive: Mapping[str, int]) -> bool:
    """Whether a faerie familiar's bond breaks at the year's end: all three
    positive cords have fallen to 0 (p. 89)."""
    return all(positive.get(name, 0) <= 0 for name in POSITIVE_CORDS)


def familiar_slave_level(might: int) -> int:
    """The least level of Faerie Chains of the Familiar Slave (CrVi Gen,
    Ritual) for a creature of `might`: Might + 15, and a Ritual's 20
    (p. 90)."""
    return max(RITUAL_MINIMUM, max(0, might) + SLAVE_CHAINS_MARGIN)


# -- Binding the Gift (pp. 91-92) ----------------------------------------------

BINDING_GIFT_SOURCE = f"{MC}, Binding the Gift, pp. 91-92"
#: The kind of being or circumstance -> the cord that counts for it: the
#: positive cords add, the negative ones subtract (pp. 91-92).
CORD_FOR: dict[str, str] = {
    "magical": "golden",
    "faerie": "silver",
    "animal": "bronze",
    "divine": "leaden",
    "infernal": "iron",
    "iron": "iron",
    "mundane": "tin",
}


def binding_gift_modifier(cords: Mapping[str, int], kinds: Iterable[str]) -> int:
    """Binding the Gift's change to a social roll: the strongest positive
    cord that applies to the being, less the strongest negative one; one
    of each side counts at most (p. 92). `kinds` are CORD_FOR's keys
    (a being with faerie and magical aspects: both)."""
    applying = {CORD_FOR[k] for k in kinds if k in CORD_FOR}
    best = max((cords.get(c, 0) for c in applying if c in POSITIVE_CORDS), default=0)
    worst = max((cords.get(c, 0) for c in applying if c in NEGATIVE_CORDS), default=0)
    return best - worst


# -- Arcadian Travel (p. 92) ---------------------------------------------------

TRAVEL_SOURCE = f"{MC}, Arcadian Travel, p. 92"
#: A charm for a place the maga has never been (p. 92).
UNSEEN_CHARM_EASE: dict[str, int] = {"mundane": 12, "regio": 15, "arcadia": 18}
REGIO, LEAVE_REGIO, TO_ARCADIA, LEAVE_ARCADIA = (
    "regio",
    "leave regio",
    "arcadia",
    "leave arcadia",
)
ARCANE_CONNECTION_EASE = 6
ARCADIA_STEP = 13


def trod_ease(
    destination: str, level: int = 0, *, arcane_connection: bool = False
) -> int:
    """The Ease Factor to open a trod (p. 92): to a regio level, its level
    x 3; out of a regio, the current level x 3; into Arcadia, (13 - the
    current aura) x 3; out of it, (13 - the destination's aura) x 3. An
    Arcane Connection to the destination takes 6 off. `level` is that
    level or aura."""
    if destination in (REGIO, LEAVE_REGIO):
        ease = 3 * max(0, level)
    elif destination in (TO_ARCADIA, LEAVE_ARCADIA):
        ease = 3 * (ARCADIA_STEP - level)
    else:
        raise ValueError(f"{destination!r} isn't a trod's destination.")
    return ease - ARCANE_CONNECTION_EASE * arcane_connection


def travel_total(magus: Character, ability: str, aura: int) -> Breakdown:
    """The Arcadian Travel Total before its stress die: Perception + the
    Ability the charm was made with + the aura, Faerie or Magic as is
    better (p. 92)."""
    lines = [
        Line(
            "Perception", amount=magus.characteristics.perception, source=TRAVEL_SOURCE
        ),
        Line(ability, amount=_score(magus, ability), source=TRAVEL_SOURCE),
        Line("Aura", amount=aura, source=TRAVEL_SOURCE),
    ]
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def trod_companions(magus: Character) -> int:
    """How many others a trod takes with her: her Faerie Magic (p. 92)."""
    return faerie_magic(magus)


# -- Animae Magic (pp. 92-95; Errata p. 55) -------------------------------------

ANIMAE_SOURCE = f"{MC}, Animae Magic and its Guidelines, pp. 92-95; {ERRATA}"
#: The Animae guidelines (pp. 94-95): (Technique, Form, level, what). An
#: anima's Might is added to the guideline's level.
ANIMAE_GUIDELINES: tuple[tuple[str, str, int, str], ...] = (
    ("Creo", "Animal", 10, "a faerie insect"),
    ("Creo", "Animal", 15, "a faerie bird, reptile, fish or amphibian"),
    ("Creo", "Animal", 20, "a faerie mammal"),
    ("Creo", "Animal", 25, "a faerie with animal parts, or of several animals"),
    ("Muto", "Animal", 10, "an animal into a faerie"),
    ("Muto", "Animal", 15, "something of animal products into a faerie"),
    ("Muto", "Animal", 20, "something of several animals or their products"),
    ("Creo", "Aquam", 10, "a water faerie"),
    ("Muto", "Aquam", 5, "a liquid into a faerie"),
    ("Creo", "Auram", 10, "a faerie of the air"),
    ("Muto", "Auram", 5, "a weather phenomenon into a faerie"),
    ("Creo", "Corpus", 10, "an obviously nonhuman faerie"),
    ("Creo", "Corpus", 15, "a faerie that looks basically human"),
    ("Muto", "Corpus", 15, "human remains into a faerie"),
    ("Muto", "Corpus", 20, "human remains in an unusual shape, or several bodies"),
    ("Muto", "Corpus", 25, "human and animal remains together (Animal requisite)"),
    ("Creo", "Herbam", 5, "a faerie of the wood"),
    ("Muto", "Herbam", 4, "a plant or plant product into a faerie"),
    ("Creo", "Ignem", 15, "a faerie of fire, heat or light"),
    ("Muto", "Ignem", 10, "fire, heat or light into a faerie"),
    ("Creo", "Imaginem", 3, "an illusory faerie of one sense (+1 magnitude a sense)"),
    (
        "Muto",
        "Imaginem",
        3,
        "an image of one sense into a faerie (+1 magnitude a sense)",
    ),
    ("Creo", "Mentem", 10, "a faerie in a person's mind"),
    ("Creo", "Mentem", 15, "a faerie ghost"),
    ("Muto", "Mentem", 5, "an emotion, memory or thought into a faerie"),
    ("Muto", "Mentem", 15, "a faerie released from a mind (requisites for its form)"),
    ("Creo", "Terram", 3, "a faerie of sand, dirt, mud or clay"),
    ("Creo", "Terram", 5, "a faerie of stone or glass"),
    ("Creo", "Terram", 15, "a faerie of base metal"),
    ("Creo", "Terram", 25, "a faerie of precious metal"),
    ("Creo", "Terram", 35, "a faerie of gemstone"),
    ("Muto", "Terram", 4, "dirt, sand, mud or clay into a faerie"),
    ("Muto", "Terram", 5, "stone or glass into a faerie"),
    ("Muto", "Terram", 10, "metal or gemstone into a faerie"),
    ("Creo", "Vim", 4, "a faerie daimon"),
    ("Muto", "Vim", 2, "vis into a faerie, 5 Might a pawn, the vis used up"),
)
#: A Muto Vim anima turns an existing spell of up to its own level + 5
#: into a faerie, not a spell as it is cast (p. 95; Errata p. 55).
MUTO_VIM_SPELL_MARGIN = 5
VIS_MIGHT_PER_PAWN = 5


def animae_base(guideline: int, might: int) -> int:
    """An Animae spell's base level: the guideline's, plus the anima's
    Might (p. 94: a faerie insect of Might 1 is base 11)."""
    return guideline + max(0, might)


def vis_anima_might(pawns: int) -> int:
    """The Might of a faerie made from vis (MuVi 2): 5 a pawn (p. 95)."""
    return VIS_MIGHT_PER_PAWN * max(0, pawns)


def animae_problem(magus: Character, technique: str) -> str:
    """What stops an Animae spell ("" if nothing): only an initiate may
    use the guidelines, and they are Creo or Muto (pp. 92, 94)."""
    if not lab_virtues.has(magus, "vf_animae_magic"):
        return f"{magus.name} hasn't been Initiated into Animae Magic."
    if technique not in ("Creo", "Muto"):
        return "Animae spells are Creo or Muto."
    return ""


# -- Becoming (pp. 93, 96; Errata p. 55) ----------------------------------------

BECOMING_SOURCE = f"{MC}, Becoming, pp. 93, 96; {ERRATA}"
BECOMING = "vf_becoming"
BODY, MIND, SPIRIT = "body", "mind", "spirit"
#: What each transformation does (p. 93; the Errata deletes the line
#: letting the transformed mind still master spells).
TRANSFORMATIONS: dict[str, str] = {
    BODY: (
        "she no longer ages and has no Fatigue levels (a Confidence Point "
        "stands in for exertion); her apparent age is fixed"
    ),
    MIND: (
        "she needs no sleep: two more free seasons a year, not for lab work, "
        "and up to sixteen days from the lab without loss; she learns no new "
        "Ability and invents only spells similar to ones she knows"
    ),
    SPIRIT: (
        "she gives up The Gift for Faerie Might (half the Becoming Lab "
        "Total), is immune to Warping, and pays a Might Point a magnitude to "
        "cast or work in the lab"
    ),
}
BODY_AGE = 35
DECREPITUDE_LEVELS = 5
ORDEAL_FACTOR = 5


def body_level(age: int, decrepitude: int) -> int:
    """Transforming the Body's level: (true age - 35) + 5 x Decrepitude
    (p. 93), never below 0."""
    return max(0, age - BODY_AGE + DECREPITUDE_LEVELS * decrepitude)


def mind_level(magus: Character) -> int:
    """Transforming the Mind's level: the total of her Ability scores."""
    return sum(a.level for a in magus.abilities)


def spirit_level(magus: Character) -> int:
    """Transforming the Spirit's level: the total of her Art scores."""
    return sum(score.level for score in magus.arts.values())


def ritual_level(magus: Character, part: str, age: int = 0) -> int:
    """The level of the transformation of `part` (BODY needs her age)."""
    if part == BODY:
        return body_level(age, magus.aging.decrepitude)
    if part == MIND:
        return mind_level(magus)
    if part == SPIRIT:
        return spirit_level(magus)
    raise ValueError(f"{part!r} isn't a Becoming transformation.")


def with_ordeals(level: int, reduction: int) -> int:
    """A transformation's level less five times the Ordeal's reduction,
    from past Initiations or one suffered in its season (a Major Flaw
    then: 45, 30, 15 off the next three, p. 93). `reduction` is what the
    Ordeal takes off an Initiation's Target."""
    return max(0, level - ORDEAL_FACTOR * max(0, reduction))


def total_limit(magus: Character) -> int:
    """The Becoming Lab Total's cap until she has Faerie Might: Warping
    Score x Faerie Magic (p. 93)."""
    return magus.aging.warping_score * faerie_magic(magus)


def becoming_total(
    saga: Saga,
    magus: Character,
    technique: str,
    form: str,
    laboratory: Laboratory,
    *,
    has_might: bool = False,
) -> Breakdown:
    """The Lab Total for a transformation ritual in Technique and Form,
    the lesser of it and Warping Score x Faerie Magic until she has a
    Might Score (p. 93)."""
    total = lab.lab_total(saga, magus, technique, form, laboratory)
    limit = total_limit(magus)
    if has_might or total.total <= limit:
        return total
    return Breakdown(
        total=limit,
        lines=[
            *total.lines,
            Line(
                f"Capped at Warping Score x Faerie Magic, {limit}",
                amount=limit - total.total,
                source=BECOMING_SOURCE,
            ),
        ],
    )


def becoming_problems(magus: Character, level: int, total: int) -> list[str]:
    """What stops a transformation ritual: the Mystery, and a Lab Total of
    at least its level."""
    found: list[str] = []
    if not lab_virtues.has(magus, BECOMING):
        found.append(f"{magus.name} hasn't been Initiated into Becoming.")
    if total < level:
        found.append(f"Lab Total {total} is below the ritual's level, {level}.")
    return found


def faerie_might(total: int) -> int:
    """The Might Score Transforming the Spirit gives: half the Becoming
    Lab Total, rounded down (p. 93)."""
    return round_down(max(0, total) / 2)


def empowered_cost(spell_level: int, ritual_level: int) -> int:
    """The Empowered Faerie's Might cost for a power: its magnitude, one
    less for each 5 levels the ritual exceeds the spell's level, so twice
    the level costs nothing (p. 96)."""
    excess = max(0, ritual_level - spell_level)
    return max(0, magnitude(spell_level) - excess // 5)


# -- Charms and Charm Magic (pp. 88, 96-98) -------------------------------------

CHARM_SOURCE = f"{MC}, Charms p. 88, Charm Magic pp. 96-98"
CHARM_MAGIC = "vf_charm_magic"
#: The charm categories (p. 98).
CATEGORIES = ("Adage", "Aspect", "Character", "Event", "Item", "Place")
#: A charm's roll: 6 for a temporary charm, 9 a permanent one, +3 for each
#: further concept in one charm; the target as its own charm is
#: Intelligence + Finesse against 6 (pp. 88, 97).
CHARM_EASE = 6
PERMANENT_CHARM_EASE = 9
CONCEPT_EASE = 3
TARGET_CHARM_EASE = 6
#: A charm as a symbolic representation: +2 to the Penetration multiplier
#: with an Arcane Connection (p. 88; DE p. 238).
SYMBOLIC_MULTIPLIER = 2


def charm_ease(concepts: int = 1, *, permanent: bool = False) -> int:
    """The Ease Factor to make a charm of `concepts` concepts."""
    base = PERMANENT_CHARM_EASE if permanent else CHARM_EASE
    return base + CONCEPT_EASE * max(0, concepts - 1)


def charm_bonus(charms: Sequence[tuple[str, str]]) -> int:
    """Charm Magic's Casting Total bonus: +1 a charm and +1 a category
    among them (p. 97; one charm alone +2). `charms` are (charm,
    category) pairs."""
    unknown = [c for _, c in charms if c not in CATEGORIES]
    if unknown:
        raise ValueError(f"{', '.join(unknown)} isn't a charm category.")
    return len(charms) + len({c for _, c in charms})


def charm_problems(magus: Character, charms: Sequence[tuple[str, str]]) -> list[str]:
    """What stops charms in a spell: Charm Magic, and no more charms than
    her Faerie Magic (p. 97)."""
    found: list[str] = []
    if not lab_virtues.has(magus, CHARM_MAGIC):
        found.append(f"{magus.name} hasn't been Initiated into Charm Magic.")
    most = faerie_magic(magus)
    if len(charms) > most:
        found.append(f"A spell holds at most {most} charms, her Faerie Magic.")
    return found


def charm_multiplier(charms: Sequence[tuple[str, str]]) -> int:
    """What Charm Magic's charms add to the Penetration multiplier with an
    Arcane Connection: +2, and +1 for each category past the first
    (p. 97)."""
    categories = len({c for _, c in charms})
    return SYMBOLIC_MULTIPLIER + max(0, categories - 1) if charms else 0


def charm_mastery_xp(spell_level: int) -> int:
    """Mastery experience that ties one more charm to a Formulaic spell:
    a point a magnitude (p. 98)."""
    return magnitude(spell_level)


# -- Story Magic (p. 98) -------------------------------------------------------

STORY_SOURCE = f"{MC}, Story Magic, p. 98"
STORY_CHARM_EASE = 9
#: What a story charm gives when a figure is needed: +3 to the rolls it
#: touches for the scene; using it costs a Confidence Point.
STORY_BONUS = 3
STORY_CONFIDENCE = 1


# -- Symbolic Magic (pp. 98-99) --------------------------------------------------

SYMBOLIC_SOURCE = f"{MC}, Symbolic Magic, pp. 98-99"
SYMBOLIC_MAGIC = "vf_symbolic_magic"
SYMBOL = "Symbol"
#: Charms each Symbol parameter needs, and so the Faerie Magic (p. 99).
SYMBOL_CHARMS = 3
SYMBOL_EASE = 12


def device_charm_bonus(charms: Sequence[tuple[str, str]]) -> int:
    """Symbolic Magic's charms on an invested device: twice Charm Magic's
    bonus, added to the Lab Total (p. 98)."""
    return 2 * charm_bonus(charms)


def device_charm_line(
    magus: Character, charms: Sequence[tuple[str, str]]
) -> Line | None:
    """The charms on a Lab Total for instilling an effect (None when she
    can't use them or there are none)."""
    if not charms or not lab_virtues.has(magus, SYMBOLIC_MAGIC):
        return None
    if len(charms) > faerie_magic(magus):
        return None
    return Line(
        "Charms (Symbolic Magic)",
        amount=device_charm_bonus(charms),
        source=SYMBOLIC_SOURCE,
    )


def symbol_problems(
    magus: Character, range_: str, duration: str, target: str
) -> list[str]:
    """What stops a Symbol ritual: Symbolic Magic, and Faerie Magic 3 for
    each Symbol parameter's three charms (all three: 9) (p. 99)."""
    count = sum(1 for name in (range_, duration, target) if name == SYMBOL)
    if not count:
        return []
    found: list[str] = []
    if not lab_virtues.has(magus, SYMBOLIC_MAGIC):
        found.append(f"{magus.name} hasn't been Initiated into Symbolic Magic.")
    needed = SYMBOL_CHARMS * count
    if faerie_magic(magus) < needed:
        found.append(
            f"{count} Symbol parameter(s) need {needed} charms, so Faerie Magic "
            f"{needed} ({SYMBOLIC_SOURCE})."
        )
    return found


# -- Glamour (pp. 101-102) ---------------------------------------------------------

GLAMOUR_SOURCE = f"{MC}, Glamour, pp. 101-102"
#: The guidelines: Creo Imaginem 10 makes a glamour, Muto Imaginem 10
#: changes a target into one (with its Form as requisite).
GLAMOUR_GUIDELINES: tuple[tuple[str, int, str], ...] = (
    ("Creo", 10, "Create a glamour"),
    ("Muto", 10, "Change a target into glamour (requisite of its Form)"),
)


def glamour_magnitudes(
    *, intricate: bool = False, directed: bool = False, animate_to_still: bool = False
) -> int:
    """The magnitudes a glamour adds (p. 101): +1 intricate (a known
    subject, clear words, moving parts), +2 moving at the caster's
    direction, +2 to make an animate target inanimate."""
    return intricate + 2 * directed + 2 * animate_to_still


# -- The Nature Mysteries (pp. 102-106; Errata p. 55) ---------------------------

NATURE_SOURCE = f"{MC}, Nature Mysteries, pp. 102-106; {ERRATA}"
#: Nature Lore counts 3 less outside her home region (p. 103).
AWAY_FROM_HOME = 3
#: The only experience Nature Lore grows by (p. 103); its Source Quality
#: is the area's aura.
NATURE_LORE_XP = ("adventure", "practice", "exposure")
#: What each Nature Lore score allows (p. 103).
NATURE_LORE_EFFECTS: dict[int, str] = {
    0: "finds an area's important sites and major dangers in a few hours",
    1: "knows the place, its denizens and sites; limited communication",
    2: "senses its supernatural things and its regiones' boundaries",
    3: "finds vis there once a season in a few days",
    4: "its residents are neutral; she knows when danger is near",
    5: "speaks fluently with its nature; most denizens respect her",
    6: "an acknowledged ally: residents come when called",
    7: "speaks with its denizens by thought, and summons help",
    8: "targets any part as through a permanent Arcane Connection",
    9: "all its denizens obey her",
}
#: The area Size modifiers (p. 103): modifier -> how wide.
AREA_SIZES: dict[int, str] = {
    1: "one pace across (a well)",
    2: "ten paces (a great boulder)",
    3: "100 paces (a grove)",
    4: "1,000 paces (a frozen plain)",
    5: "10,000 paces (the North Wind)",
}
AWAKENING_BASE = 25
AWAKENING_LEVELS_PER_PAWN = 5
POWER_LEVELS_PER_PAWN = 10
POWER_LEVELS_PER_MIGHT = 10
PAWNS_PER_MIGHT = 5
GUARDIAN_WARPING = 1


def nature_lore_score(score: int, *, at_home: bool = True) -> int:
    """Nature Lore as it counts: 3 less outside her home region."""
    return score if at_home else score - AWAY_FROM_HOME


def nature_lore_effects(score: int) -> list[str]:
    """What a Nature Lore score allows, each step up to it (negative scores
    nothing)."""
    return [text for step, text in NATURE_LORE_EFFECTS.items() if step <= score]


def awakening_level(
    *,
    might: int = 0,
    size: int = 0,
    aura: int = 0,
    area_size: int = 0,
    spirit: bool = False,
) -> int:
    """Awakening's level (p. 104): 25 + Might + 5 x Size for a creature,
    (aura + the area's Size modifier) x 5 for an aura's spirit (Might 5,
    Size -3: 15; aura 5 over +5: 50)."""
    if spirit:
        return 5 * (aura + area_size)
    return AWAKENING_BASE + might + 5 * size


def awakening_total(
    magus: Character, nature_lore: str, technique: str, form: str, aura: int
) -> Breakdown:
    """The Awakening Total: Intelligence + Nature Lore + Technique + Form
    + the aura of the wild place (Nature Lore in place of Magic Theory,
    no laboratory) (p. 104)."""
    lines = [
        Line(
            "Intelligence",
            amount=magus.characteristics.intelligence,
            source=NATURE_SOURCE,
        ),
        Line(nature_lore, amount=_score(magus, nature_lore), source=NATURE_SOURCE),
        Line(
            technique, amount=sum(lab.art_score(magus, technique)), source=NATURE_SOURCE
        ),
        Line(form, amount=sum(lab.art_score(magus, form)), source=NATURE_SOURCE),
        Line("Aura", amount=aura, source=NATURE_SOURCE),
    ]
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def awakening_vis(level: int) -> int:
    """Awakening's vis: a pawn per five levels or fraction (p. 104)."""
    return max(1, round_up(max(0, level) / AWAKENING_LEVELS_PER_PAWN))


def awakened_might(aura: int) -> int:
    """The Magic Might an awakened being gains, if it has none: aura x 5."""
    return 5 * max(0, aura)


def power_levels_cap(pawns: int) -> int:
    """The most levels of powers an awakened being may hold: 10 x the
    pawns its Awakening took (p. 104)."""
    return POWER_LEVELS_PER_PAWN * max(0, pawns)


def power_might_cost(level: int, pawns: int = 0) -> int:
    """An awakened being's power's Might cost: 1 per 10 levels or
    fraction, 1 less for each 5 pawns of its Arts spent instilling it
    (p. 104); at least 0."""
    cost = round_up(max(0, level) / POWER_LEVELS_PER_MIGHT)
    return max(0, cost - max(0, pawns) // PAWNS_PER_MIGHT)


def wilding_pawns(nature_lore: int) -> int:
    """Wilding's season gives Nature Lore x 2 pawns of temporary vis of
    the vessel's Form, to be used within days (pp. 104-105)."""
    return 2 * max(0, nature_lore)


def guardian_ease(aura: int, area_size: int) -> int:
    """Guardian of Nature's ritual: Presence + Nature Lore + stress die
    against the aura x the area's Size modifier (p. 105); it costs a
    Fatigue level and the aura's level in pawns of vis."""
    return aura * area_size


#: The wound a guardian spirit takes when her locus is tamed or
#: unnaturally destroyed (p. 106).
LOCUS_WOUNDS: dict[str, str] = {
    "an object": "Light",
    "part of the area": "Medium",
    "a group of objects": "Heavy",
}
