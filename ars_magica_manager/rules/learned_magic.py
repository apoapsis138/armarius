"""Learned magic of the Divine and the Solomonic integrations.

**Ars Notoria** (Realms of Power: The Divine pp. 97-100; Errata p. 49):

- Finding a copy: a season, Intelligence + Divine Lore + a stress die
  against 21; a botch finds some other book (p. 97).
- Reading it needs 4 in Latin, Greek, Hebrew and Chaldean, and Artes
  Liberales 4 (p. 97). It is a tractatus of Quality 20: unGifted readers
  learn Divine Lore from it, a Gifted one may learn the Supernatural
  Ability Ars Notoria by the usual rules for a first Supernatural Ability
  (DE p. 383); too low a total wastes the season (p. 98). Only this text
  can first teach it; later study is normal.
- Recitation Score = Intelligence + Ars Notoria + modifiers for the season
  before (p. 98's table); the Recitation Total adds a stress die. Each of
  the seven Rings must be learned in order, the first time taking a
  season; Ease Factor 6 + 3 x the Ring's level + 1 a season of duration,
  3 + ... once the Ring is known, which then takes 10 days less the score
  (at least one) (p. 99). A Ring's benefits don't stack: a second
  recitation only lengthens it. A botch is unworthiness (p. 98).
- The Rings (pp. 99-100): I Philosophiae +100 xp and Communication +3 (to
  +5), Spring or Autumn; II Theology +100 xp and Intelligence +3 (to +5),
  Winter; III Medicine +100 xp and Greater Purifying Touch for one chosen
  disease, any season; IV the Patron Angel, a teacher; V sense a being's
  realm, Perception + Ars Notoria + stress die against 6 + its Magic
  Resistance / 5, without Penetration (Errata p. 49), and one of its
  powers for each 5 the roll is over its Magic Resistance, Summer; VI
  divination, Perception + Ars Notoria against the question's Ease
  Factor, Spring; VII simple dice become stress dice that never botch.
- The temporary xp are kept apart: when the Ring ends, the 100 xp go
  (p. 99's example).
- Each point of Ars Notoria takes 3 off the Divine aura's penalty to the
  character's other magic; an active Ring means no Warping from a Divine
  aura (p. 100). rules.hybrid_magic applies the first to Hermetic magic.

**Jewish mysticism** (RoP:D pp. 141-144; the Errata has nothing on these
pages): Gematria from a book other than the Torah takes a stress die, and
no book on an Art or an Accelerated Ability can be used (p. 141); Shinnui
Shem's aging bonus, once a life (p. 141); awakening and empowering a golem
and its madness table (pp. 142-143); the Merkavah Total that reveals a
True Name and its discipline roll (p. 144). The catalog's Kabbalists
tradition (data/tradition_catalog.json) holds the totals' wording.

**Solomonic integrations** (The Cradle and the Crescent pp. 44-45; the
Errata has nothing on these pages): what the storyguide spends Fatra
Bayna's Spirit and Corruption Points on (p. 44), and the sahir's three
breakthroughs (Solomonic Devices, Spontaneous Solomonic Spells,
Independent Solomonic Magic). The Hermetic ones (Hermetic True Names,
Scientates Suleimanis, Hermetic Realm Initiation) are research goals in
rules.integrations.

Pattern: plain rule functions over numbers and a character, with the
Rings and tables as data, like rules.holy_powers.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import SEASONS, Character
from . import holy_powers
from .languages import understanding_score
from .rounding import round_down
from .scores import ability_level

SOURCE = (
    "Realms of Power: The Divine, Ars Notoria pp. 97-100 and Jewish Mysticism "
    "pp. 141-144; Errata p. 49; The Cradle and the Crescent, Integration pp. 44-45"
)

ARS_NOTORIA = "Ars Notoria"
ARS_NOTORIA_VIRTUE = "vf_ars_notoria"

# -- Ars Notoria: the text ------------------------------------------------

#: Intelligence + Divine Lore + a stress die against this finds a copy (p. 97).
FIND_TEXT_EASE = 21
#: The text is a tractatus of this Quality (p. 98).
TEXT_QUALITY = 20
#: Its four languages and the score needed in each, and Artes Liberales
#: for their four alphabets (p. 97).
TEXT_LANGUAGES: tuple[str, ...] = ("Latin", "Greek", "Hebrew", "Chaldean")
TEXT_LANGUAGE_SCORE = 4
TEXT_ARTES_LIBERALES = 4
#: Chaldean is "an ancient Aramaic language" (p. 97): a save may call it
#: either.
_CHALDEAN_NAMES = ("Chaldean", "Aramaic")
#: The experience a first season must give for a score of 1 (DE p. 383).
FIRST_SEASON_XP = 5
#: The Social Statuses that, with The Gift, may start play with Ars
#: Notoria besides a magus (p. 98; the Virtue, p. 93).
STARTING_STATUSES: tuple[str, ...] = ("vf_magister_in_artibus", "vf_clerk", "vf_priest")


def find_text_total(character: Character, die: int) -> int:
    """A season's search for a copy: Intelligence + Divine Lore + the
    stress die (p. 97)."""
    return (
        character.characteristics.intelligence
        + ability_level(character, "Divine Lore")
        + die
    )


def language_score(character: Character, language: str) -> int:
    """The character's score in one of the text's languages."""
    names = _CHALDEAN_NAMES if language == "Chaldean" else (language,)
    return max(understanding_score(character, name) for name in names)


def reading_shortfalls(character: Character) -> list[str]:
    """What the character lacks to read the text: each language and Artes
    Liberales below 4 ("Greek 2 of 4"); empty when he can (p. 97)."""
    short = [
        f"{language} {score} of {TEXT_LANGUAGE_SCORE}"
        for language in TEXT_LANGUAGES
        if (score := language_score(character, language)) < TEXT_LANGUAGE_SCORE
    ]
    artes = ability_level(character, "Artes Liberales")
    if artes < TEXT_ARTES_LIBERALES:
        short.append(f"Artes Liberales {artes} of {TEXT_ARTES_LIBERALES}")
    return short


def first_study_xp(supernatural_penalty: int) -> int:
    """What a Gifted reader's first season from the text gives Ars Notoria:
    its Quality less his penalty for other Supernatural Abilities and
    opened Arts (rules.study.supernatural_penalty, DE p. 383). Below 5 he
    learns nothing and the season is wasted (p. 98)."""
    xp = TEXT_QUALITY - supernatural_penalty
    return xp if xp >= FIRST_SEASON_XP else 0


def starting_problems(character: Character, *, gifted: bool) -> list[str]:
    """Why a character may not start play with Ars Notoria: it needs The
    Gift and a magus, Magister in Artibus, Clerk or Priest (p. 98), and a
    Christian believer (p. 97); the languages may come from the Virtue's
    50 xp, so they are not checked here."""
    problems: list[str] = []
    if not gifted:
        problems.append("Ars Notoria needs The Gift (RoP:D p. 98).")
    held = {vf.vf_id for vf in character.virtues_flaws}
    if character.type != "magus" and not held & set(STARTING_STATUSES):
        problems.append(
            "Only magi, and those with Magister in Artibus, Clerk or Priest, "
            "start play with Ars Notoria (RoP:D p. 98)."
        )
    return problems


# -- Ars Notoria: reciting the Rings --------------------------------------


@dataclass(frozen=True)
class Modifier:
    """A Recitation Score modifier from the season before (p. 98)."""

    name: str
    amount: int
    note: str = ""


#: p. 98's table. The amounts that vary are worked by the functions below
#: (fasting a season at a time, other Supernatural Abilities, True Faith).
#: The book prints "Dishonorable Major Virtue or Flaw -3", read as a Major
#: Personality Flaw to match its other lines.
MODIFIERS: tuple[Modifier, ...] = (
    Modifier("Fasting", 1, "a season, bread and water"),
    Modifier("Chastity", 1),
    Modifier("Honorable Minor Personality Flaw", 1, "compassionate, pious"),
    Modifier("Honorable Major Personality Flaw", 3),
    Modifier("Dishonorable Minor Personality Flaw", -1, "ambitious, envious"),
    Modifier("Dishonorable Major Personality Flaw", -3),
    Modifier("Venial sin", -3),
    Modifier("Mortal sin", -9),
)
#: The storyguide's own adjustment runs from -3 to +3 (p. 98).
STORYGUIDE_RANGE = (-3, 3)

#: Divine Supernatural Abilities, whose scores are not subtracted (p. 98):
#: Sense Holiness and Unholiness, the Holy Methods and Powers, and the
#: Kabbalists' Methods.
DIVINE_ABILITIES: frozenset[str] = frozenset(
    {
        "Sense Holiness and Unholiness",
        ARS_NOTORIA,
        "Kabbalah",
        "Gematria",
        "Merkavah",
        *holy_powers.METHODS,
        *holy_powers.VARIANTS,
        *holy_powers.COMBINATIONS,
    }
)


def supernatural_modifier(character: Character, supernatural: frozenset[str]) -> int:
    """Minus the score of each of the character's Supernatural Abilities
    (`supernatural`, their names) that isn't Divine (p. 98)."""
    return -sum(
        a.level
        for a in character.abilities
        if a.name in supernatural and a.name not in DIVINE_ABILITIES
    )


def fasting_ease(season: int) -> int:
    """The Stamina + stress die roll to keep a fast in its `season`th
    consecutive season: 6, one more each season. A failure ends the fast;
    a botch gives Aging Points enough to lose a point of Stamina (p. 98)."""
    if season < 1:
        raise ValueError("A fast's first season is 1")
    return 6 + season - 1


def recitation_score(
    character: Character,
    *,
    modifiers: int = 0,
    supernatural: frozenset[str] = frozenset(),
) -> int:
    """Intelligence + Ars Notoria + modifiers, the supernatural penalty and
    True Faith (p. 98). `modifiers` is the sum of the table's lines that
    apply, fasting and the storyguide's included."""
    return (
        character.characteristics.intelligence
        + ability_level(character, ARS_NOTORIA)
        + modifiers
        + supernatural_modifier(character, supernatural)
        + max(0, character.background.true_faith_score)
    )


def ring_ease(level: int, seasons: int, *, known: bool) -> int:
    """A Ring's Ease Factor: 6 (3 once the Ring is known) + 3 x its level
    + 1 a season it is to last (p. 99)."""
    if not 1 <= level <= len(RINGS):
        raise ValueError(f"The Rings of Solomon run 1 to {len(RINGS)}")
    if seasons < 1:
        raise ValueError("A Ring lasts at least a season")
    return (3 if known else 6) + 3 * level + seasons


def recitation_days(score: int) -> int:
    """Days to recite a known Ring again: 10 less Ars Notoria, at least
    one; the first recitation takes a season (p. 99)."""
    return max(1, 10 - score)


def may_learn(level: int, learned: int) -> bool:
    """Whether a Ring may be recited: one already learned, or the next in
    order (`learned` is the highest learned so far); earlier Rings'
    benefits needn't still be in effect (p. 99)."""
    return 1 <= level <= learned + 1


@dataclass(frozen=True)
class Ring:
    level: int
    name: str
    #: The seasons it may be recited in (all four when the book sets none).
    seasons: tuple[str, ...]
    gives: str
    #: Temporary xp it gives in an Academic Ability, and in which.
    ability: str = ""
    xp: int = 0
    #: The Characteristic it raises by CHARACTERISTIC_RISE, to at most +5.
    characteristic: str = ""
    #: The Virtue it grants while it lasts.
    virtue: str = ""
    page: int = 99


#: What Rings I and II add to a Characteristic, and the most it can reach.
CHARACTERISTIC_RISE = 3
CHARACTERISTIC_CAP = 5
#: The xp Rings I to III give.
RING_XP = 100

RINGS: tuple[Ring, ...] = (
    Ring(
        1,
        "First Ring of Solomon",
        ("Spring", "Autumn"),
        "Philosophiae +100 xp and Communication +3 (to at most +5)",
        "Philosophiae",
        RING_XP,
        "communication",
    ),
    Ring(
        2,
        "Second Ring of Solomon",
        ("Winter",),
        "Theology +100 xp and Intelligence +3 (to at most +5)",
        "Theology",
        RING_XP,
        "intelligence",
    ),
    Ring(
        3,
        "Third Ring of Solomon",
        SEASONS,
        "Medicine +100 xp and Greater Purifying Touch for one disease chosen "
        "at each recitation",
        "Medicine",
        RING_XP,
        virtue="vf_greater_purifying_touch",
    ),
    Ring(
        4,
        "Fourth Ring of Solomon",
        SEASONS,
        "The Patron Angel, with a Guardian Angel's powers, who teaches only "
        "you; it may end any Ring if you stray",
        virtue="vf_patron_angel",
    ),
    Ring(
        5,
        "Fifth Ring of Solomon",
        ("Summer",),
        "Sense a being's realm: Perception + Ars Notoria + stress die against "
        "6 + its Magic Resistance / 5, no Penetration needed; a power for each "
        "5 over its Magic Resistance",
        page=100,
    ),
    Ring(
        6,
        "Sixth Ring of Solomon",
        ("Spring",),
        "Divination of God's plan: a day's fast, then Perception + Ars "
        "Notoria + stress die against the question's Ease Factor",
        page=100,
    ),
    Ring(
        7,
        "Seventh Ring of Solomon",
        SEASONS,
        "Perfect understanding: simple dice become stress dice, which never "
        "botch; the Patron Angel ends it at any pride",
        page=100,
    ),
)

#: p. 98: a botch's possible costs, as the storyguide chooses.
BOTCH_COSTS: tuple[str, ...] = (
    "Ars Notoria xp lost equal to the Ease Factor",
    "a Minor Flaw until atoned for",
    "Ars Notoria benefits in effect lost",
    "a time when no orations can be made",
)


def ring(level: int) -> Ring:
    if not 1 <= level <= len(RINGS):
        raise ValueError(f"The Rings of Solomon run 1 to {len(RINGS)}")
    return RINGS[level - 1]


def season_allowed(level: int, season: str) -> bool:
    """Whether the Ring may be recited in `season` (pp. 99-100)."""
    return season in ring(level).seasons


def raised_characteristic(current: int) -> int:
    """A Characteristic under Ring I or II: +3, to at most +5; one already
    higher stays as it is (p. 99)."""
    return max(current, min(current + CHARACTERISTIC_RISE, CHARACTERISTIC_CAP))


def xp_after_ring(xp: int, granted: int = RING_XP) -> int:
    """An Ability's xp once a Ring's benefit ends: its xp less what the
    Ring gave (p. 99: 140 xp less 100 leaves 40)."""
    return max(0, xp - granted)


def sense_realm_ease(magic_resistance: int) -> int:
    """The Fifth Ring's Ease Factor: 6 + the being's Magic Resistance / 5,
    rounded down as the book gives no rounding (p. 100; Errata p. 49)."""
    return 6 + round_down(max(0, magic_resistance) / 5)


def powers_learned(roll: int, magic_resistance: int) -> int:
    """Powers the Fifth Ring tells of, weakest first: one when the roll is
    5 or more over the Magic Resistance, one more each 5 beyond (p. 100)."""
    over = roll - magic_resistance
    return 0 if over < 5 else round_down(over / 5)


@dataclass(frozen=True)
class Question:
    ease: int
    question: str


#: The Sixth Ring's sample questions (p. 100).
DIVINATIONS: tuple[Question, ...] = (
    Question(9, "Tomorrow's weather"),
    Question(9, "The short-term results of an immediate personal action"),
    Question(12, "The long-term results of an immediate personal action"),
    Question(12, "An auspicious time for a ritual or formulaic casting"),
    Question(12, "The short-term results of another's actions"),
    Question(15, "The long-term results of another's actions"),
    Question(18, "An important piece of an individual's possible future"),
)


def auspicious_bonus(character: Character) -> int:
    """What a successful divination of an auspicious time adds to the
    Casting Total: the Ars Notoria score (p. 100)."""
    return ability_level(character, ARS_NOTORIA)


#: Each point of Ars Notoria takes this off a Divine aura's penalty (p. 100).
DIVINE_RELIEF = 3


def divine_aura_relief(character: Character, penalty: int) -> int:
    """A Divine aura's penalty to the character's other magic, less 3 a
    point of Ars Notoria, never above 0 (p. 100). A bonus is unchanged."""
    if penalty >= 0:
        return penalty
    return min(0, penalty + DIVINE_RELIEF * ability_level(character, ARS_NOTORIA))


def divine_aura_warps(*, ring_active: bool) -> bool:
    """Whether a Divine aura gives the practitioner Warping: not while a
    Ring is in effect (p. 100)."""
    return not ring_active


#: The Patron Angel's teaching statistics (p. 99).
PATRON_ANGEL_TEACHER: dict[str, int] = {
    "Communication": 3,
    "Artes Liberales": 7,
    "Civil and Canon Law": 7,
    "Medicine": 7,
    "Philosophiae": 7,
    "Teach": 7,
    "Theology": 7,
}


# -- Jewish mysticism -----------------------------------------------------


def gematria_book_usable(*, accelerated: bool) -> bool:
    """Whether Gematria may read a book: not one on an Art or an
    Accelerated Ability (p. 141)."""
    return not accelerated


def gematria_needs_stress_die(*, torah: bool) -> bool:
    """A book other than the Torah takes a stress die (p. 141)."""
    return not torah


def shinnui_shem_bonus(
    character: Character, *, die: int, book_quality: int, aura: int
) -> int:
    """Shinnui Shem's bonus to Aging Rolls: (simple die + Intelligence +
    Gematria + Understanding + the book's Quality + Dominion aura) / 5,
    rounded down. It ends at the next Aging Point, comes once a life, and
    doesn't add to other supernatural aging bonuses; the renaming also
    severs every Arcane Connection to him (p. 141)."""
    total = (
        die
        + character.characteristics.intelligence
        + ability_level(character, "Gematria")
        + ability_level(character, "Understanding")
        + book_quality
        + aura
    )
    return max(0, round_down(total / 5))


#: Awakening a golem: the total's Ease Factor, and the Might cap as a
#: multiple of the leader's Kabbalah (p. 142).
AWAKEN_EASE = 30
MIGHT_CAP_MULTIPLE = 5


def golem_total(
    character: Character, *, aura: int = 0, ceremony: int = 0, removed: int = 0
) -> int:
    """The Awaken (or Empower) Golem Total: Intelligence + Kabbalah +
    Wonders + Ceremony bonus (each helper's Intelligence + Kabbalah) +
    Dominion aura; removing a power adds its level to an Empower Total
    (pp. 142-143)."""
    return (
        character.characteristics.intelligence
        + ability_level(character, "Kabbalah")
        + ability_level(character, "Wonders")
        + ceremony
        + aura
        + removed
    )


def banked(total: int, ease: int) -> int:
    """A season's points toward a golem's Might, a power, or a True Name:
    what the total exceeds the Ease Factor by (pp. 142, 144)."""
    return max(0, total - ease)


def golem_might(points: int, die: int, kabbalah: int) -> int:
    """The awakened golem's Divine Might: the points banked + the last
    season's stress die, at most five times the leader's Kabbalah (p. 142;
    p. 143's example: 15 + 8 = 23)."""
    return min(points + die, MIGHT_CAP_MULTIPLE * kabbalah)


def golem_botch_dice(kabbalists: int) -> int:
    """One botch die per kabbalist taking part (p. 142)."""
    return max(1, kabbalists)


def power_gained(points: int, level: int) -> bool:
    """A golem gains a power once the points banked reach its level (p. 142)."""
    return points >= level


def power_room(might: int, magnitudes: int) -> int:
    """Magnitudes of powers the golem may still take: as many as its
    Divine Might in all (p. 142); a use costs Might equal to the power's
    magnitude."""
    return max(0, might - magnitudes)


#: A madness roll's results, by the lowest roll (p. 143); a botch is
#: Madness itself, and 15+ rolls twice more.
MADNESS_TABLE: tuple[tuple[int, str], ...] = (
    (15, "Roll twice more"),
    (10, "Loyal to Community -1"),
    (5, "Vengeful +1"),
    (0, "Trusting -1"),
)


def golem_madness(roll: int, *, botch: bool = False) -> str:
    """What a madness roll does to a golem (p. 143): when a kabbalist who
    woke it suffers a tragedy of hubris, it is told to break a mitzvah, or
    it is taken from its community. The changes are permanent."""
    if botch:
        return "Madness"
    return next(effect for least, effect in MADNESS_TABLE if roll >= least)


#: A golem's starting traits (p. 142's insert).
GOLEM_ABILITIES: dict[str, int] = {
    "(Area) Lore": 5,
    "Awareness": 1,
    "Brawl": 5,
    "Charm": 3,
    "Concentration": 1,
    "Hebrew": 5,
}
GOLEM_VIRTUES: tuple[str, ...] = ("vf_unaging", "vf_improved_characteristics")
GOLEM_FLAWS: tuple[str, ...] = ("vf_weak_willed",)
GOLEM_TRAITS: dict[str, int] = {
    "Loyal to its Community": 3,
    "Trusting": 3,
    "Vengeful": -3,
}

#: The Merkavah Total's True Name: +5 Penetration against the being (p. 144).
TRUE_NAME_PENETRATION = 5
#: Studying or using Merkavah alone: a Disciplined stress roll against 9
#: at the season's end (p. 144).
MERKAVAH_DISCIPLINE_EASE = 9


def merkavah_total(character: Character, *, aura: int = 0, ceremony: int = 0) -> int:
    """Stamina + Merkavah + Adjuration + Ceremony bonus (each helper's
    Stamina + Merkavah) + Dominion aura, against the being's Might; each
    season costs a long-term Fatigue level, kept till the end (p. 144)."""
    return (
        character.characteristics.stamina
        + ability_level(character, "Merkavah")
        + ability_level(character, "Adjuration")
        + ceremony
        + aura
    )


def true_name_revealed(points: int, might: int) -> bool:
    """The True Name comes once the points banked exceed the Might (p. 144)."""
    return points > might


def merkavah_discipline(roll: int, *, botch: bool = False) -> str:
    """The Disciplined roll's outcome (p. 144): "" on success."""
    if botch:
        return (
            "Plagued by Supernatural Entity (Story Flaw): Infernal spirits are alerted"
        )
    if roll < MERKAVAH_DISCIPLINE_EASE:
        return "Obsession: the same source again next season, for no benefit"
    return ""


# -- The Cradle and the Crescent: Fatra Bayna and the sahirs' research ------


@dataclass(frozen=True)
class SpendEffect:
    cost: int
    effect: str


#: What the storyguide may spend Spirit Points on after Fatra Bayna (p. 44).
SPIRIT_POINT_EFFECTS: tuple[SpendEffect, ...] = (
    SpendEffect(1, "Warping Score x 5 xp in a summoning or Solomonic art"),
    SpendEffect(1, "A new naranj of level up to Warping Score x 5"),
    SpendEffect(1, "Warping Score x 5 pawns of fitting vis"),
    SpendEffect(1, "3 Confidence Points"),
    SpendEffect(3, "Confidence Score +1"),
    SpendEffect(
        3,
        "+1 to social rolls (not summoning or casting), offsetting the Gift's "
        "penalty but not its distrust",
    ),
    SpendEffect(3, "A fitting Minor Virtue, or a Minor Flaw removed"),
)
#: And Corruption Points (p. 44).
CORRUPTION_POINT_EFFECTS: tuple[SpendEffect, ...] = (
    SpendEffect(1, "An Aging roll now, adding the Warping Score"),
    SpendEffect(1, "A Heavy Wound"),
    SpendEffect(1, "Bad Reputation 2 among that realm's spirits, or +1 to it"),
    SpendEffect(3, "-1 to social rolls, on top of the Gift"),
    SpendEffect(3, "A fitting Minor Flaw, or a Minor Virtue lost"),
)


def fatra_bayna_reward(warping_score: int) -> int:
    """The xp, naranj level or pawns of vis a 1-point Spirit Point effect
    gives: Warping Score x 5 (p. 44)."""
    return 5 * max(0, warping_score)


@dataclass(frozen=True)
class SolomonicBreakthrough:
    """A breakthrough a sahir researches from Hermetic magic (p. 45)."""

    name: str
    kind: str
    gives: str
    virtue: str = ""


SOLOMONIC_BREAKTHROUGHS: tuple[SolomonicBreakthrough, ...] = (
    SolomonicBreakthrough(
        "Solomonic Devices",
        "Minor",
        "Devices that hold their effect on their own, with no spirit bound "
        "into them; from studying Hermetic enchanted items.",
    ),
    SolomonicBreakthrough(
        "Spontaneous Solomonic Spells",
        "Major",
        "Formulaic spells cast spontaneously, as magi do; from studying Magic Theory.",
        "vf_spontaneous_solomonic_spells",
    ),
    SolomonicBreakthrough(
        "Independent Solomonic Magic",
        "Solomonic",
        "Spells cast and kept up with no spirit channelling them; needs a "
        "Hermetic Technique and Form initiated and Magic Theory studied.",
        "vf_independent_solomonic_magic",
    ),
)


def spontaneous_solomonic(total: int, *, fatiguing: bool) -> int:
    """A Spontaneous Solomonic spell's Casting Total (p. 44): losing a
    Fatigue level, the total (with its stress die) / 2; otherwise, with no
    die, / 5; rounded down as a magus's (DE p. 214)."""
    return round_down(total / (2 if fatiguing else 5))


def independent_solomonic(total: int, summoning_strength: int) -> int:
    """An Independent Solomonic spell's Casting Total: without the
    Summoning Strength a spirit adds; its Penetration is the sahir's own,
    and an unGifted sahir's has no maximum level (p. 44)."""
    return total - summoning_strength
