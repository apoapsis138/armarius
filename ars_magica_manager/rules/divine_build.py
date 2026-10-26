"""Divine beings and angels by the book (Realms of Power: The Divine,
Divine Beings and Heaven's Host, pp. 16-26; Ars Magica Definitive
Edition, Creatures of the Divine and Angelic Powers, pp. 488-489).

- **Divine beings** (RoP: Divine p. 16): any creature with Divine Might,
  saint, holy beast or angel. Such a creature uses the normal rules for
  Magic Resistance and Penetration, can't have True Faith, and is never
  bothered by The Gift (DE p. 488).
- **Angels** (pp. 18-21) belong to a Choir, an archangel to its own Choir
  and the Archangels' too (p. 25). Every angel has Divine Might 1 or more
  and Love of God +5 (p. 19), and the powers Angelic Mantle (2 points,
  +12, Corpus), Enfolding (2 or 10, +10, Vim) and Envisioning (1 or 5, +0,
  Mentem), as the DE gives them too (p. 489). Its mental Characteristics
  are +1 for each 10 points of Might or fraction (Might 1-10 +1, 90 +9);
  its Mantle's physical ones are bought with the usual 7 points, more for
  a powerful angel (p. 19).
- Each Choir (pp. 21-26) has a least Divine Might, two Personality Traits
  and its powers: Seraphim (35), Cherubim and Thrones (25), Dominations
  and Potentates (10), Authorities and Principalities (5; an Authority's
  Might follows its office), Archangels (50), Angels (1).
- Its senses and magic (pp. 20-21): a True Name is an Arcane Connection
  and +5 to the Penetration multiplier; its speech, illumination, has
  Penetration 0 plus its Penetration Ability; in spirit form only Mentem
  and Vim reach it and it has no Wounds or Fatigue, in its Mantle the
  Form of its Might; magic can't make it act against its Personality
  Traits; Might below 0 destroys it; Hermetic magic can't summon or
  compel it; it knows every aura and is never hindered by one, and has
  Second Sight of its Might / 5 for finding regiones.
- The Grigori, the fallen tenth Choir (p. 26), are trapped in their
  Mantle: slain without the Might for a new one, they die.

The Definitive Edition's angels, and the Tribunal books', name no Choir,
so an angel is checked only when its Order names one; and a story's angels
needn't balance: these are advice, never refusals.

Pattern: the same shape as rules.infernal_build (one function per realm
over the creature, no new class); each Choir is a row of data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..models import Creature, CreaturePower
from .creation_characteristics import cost
from .rounding import round_down, round_up

SOURCE = (
    "Realms of Power: The Divine, Divine Beings and Heaven's Host, pp. 16-26; "
    "Ars Magica Definitive Edition, Creatures of the Divine, pp. 488-489"
)

DIVINE = "Divine"
TRUE_FAITH = "vf_true_faith"


@dataclass(frozen=True)
class AngelicPower:
    """A power as a Choir's stat block prints it: the Might Points it may
    cost (`more` when it costs that or more), its Initiative and Form."""

    name: str
    costs: tuple[int, ...]
    init: int
    form: str
    more: bool = False

    def cost_text(self) -> str:
        text = " or ".join(str(c) for c in self.costs)
        return f"{text}{' or more' if self.more else ''} point(s)"

    def fits(self, power: CreaturePower) -> bool:
        """Whether the typed cost and Initiative are the book's."""
        if power.init != self.init:
            return False
        if self.more:
            return power.might_cost >= min(self.costs)
        return power.might_cost in self.costs


@dataclass(frozen=True)
class Choir:
    """One of the Choirs: the least Divine Might its angels have, the
    Personality Traits and powers they share, and the words its name is
    found by in an angel's Order."""

    name: str
    least_might: int
    traits: tuple[tuple[str, int], ...]
    powers: tuple[AngelicPower, ...]
    pattern: str
    page: int


#: The powers every angel has (RoP: Divine p. 19; DE p. 489).
ANGELIC_POWERS: tuple[AngelicPower, ...] = (
    AngelicPower("Angelic Mantle", (2,), 12, "Corpus"),
    AngelicPower("Enfolding", (2, 10), 10, "Vim"),
    AngelicPower("Envisioning", (1, 5), 0, "Mentem"),
)
LOVE_OF_GOD = ("Love of God", 5)

CHOIRS: tuple[Choir, ...] = (
    Choir(
        "Seraphim",
        35,
        (("Honest", 4), ("Tireless", 4)),
        (
            AngelicPower("Heavenly Fire", (1,), 15, "Ignem"),
            AngelicPower("Smite Evil", (1,), 15, "Vim", more=True),
        ),
        r"\bseraph",
        21,
    ),
    Choir(
        "Cherubim",
        25,
        (("Contemplative", 4), ("Wise", 4)),
        (
            AngelicPower("Divine Insight", (3,), 0, "Mentem"),
            AngelicPower("The Chariot", (30,), 1, "Auram"),
        ),
        r"\bcherub",
        22,
    ),
    Choir(
        "Thrones",
        25,
        (("Knowledgeable", 4), ("Stern", 4)),
        (
            AngelicPower("Deliverance of the Righteous", (5,), 10, "Corpus"),
            AngelicPower("Divine Justice", (3,), 1, "Mentem"),
            AngelicPower("Radiant Mirror", (30,), 0, "Auram"),
        ),
        r"\bthrones?\b|\bofanim",
        22,
    ),
    Choir(
        "Dominations",
        10,
        (("Commanding", 4), ("Servile", -4)),
        (
            AngelicPower("Divine Direction", (0, 5), 0, "Vim"),
            AngelicPower("Liberate the Sinful", (5,), 0, "Mentem"),
        ),
        r"\bdomination|\bdominions?\b|\bchasmalim",
        23,
    ),
    Choir(
        "Authorities",
        5,
        (("Principled", 4), ("Unwavering", 4)),
        (AngelicPower("Divine Authority", (0,), 0, "Varies"),),
        r"\bauthorit",
        23,
    ),
    Choir(
        "Potentates",
        10,
        (("Harmonious", 4), ("Loving", 4)),
        (
            AngelicPower("Divine Balance", (1,), 1, "Varies", more=True),
            AngelicPower("Mysterious Path", (4,), 0, "Varies"),
        ),
        r"\bpotentate",
        23,
    ),
    Choir(
        "Principalities",
        5,
        (("Bureaucratic", 4), ("Regal", 4)),
        (
            AngelicPower("Incalculable Strength of Heaven", (5,), 0, "Vim", more=True),
            AngelicPower("Sway the Hearts of Man", (10,), 0, "Mentem", more=True),
        ),
        r"\bprincipalit",
        24,
    ),
    Choir(
        "Archangels",
        50,
        (("Radiant", 4), ("Rational", 4)),
        (
            AngelicPower("Irresistible Light", (20,), 20, "Vim"),
            AngelicPower("Infinite Divisibility", (0,), 0, "Vim"),
        ),
        r"\barchangel",
        25,
    ),
    Choir(
        "Angels",
        1,
        (("Loving", 4), ("Compassionate", 4)),
        (
            AngelicPower("Divine Guidance", (1,), 1, "Mentem"),
            AngelicPower("Heavenly Servant", (1,), 5, "Vim"),
        ),
        r"(?<!arch)\bangels?\b",
        26,
    ),
)

#: The fallen tenth Choir, without a stat block (p. 26).
GRIGORI = re.compile(r"\bgrigori|\bwatchers?\b", re.IGNORECASE)

#: What a Principality's two powers cost, by the area or people they
#: cover (p. 24); Sway the Hearts of Man's temper is +2, 5 points more
#: for each +1.
PRINCIPALITY_COSTS: dict[str, int] = {
    "a family": 5,
    "a hamlet or village": 10,
    "a town or city": 15,
    "a duchy": 20,
    "a kingdom or nation": 30,
    "an empire": 40,
}
SWAY_TEMPER, SWAY_STEP = 2, 5
#: Smite Evil's level: 10 for each Might Point spent (p. 21).
SMITE_LEVELS_PER_POINT = 10
#: Irresistible Light's damage and the Might it strips (p. 25).
LIGHT_DAMAGE, LIGHT_STRIPS = 40, 10

#: A True Name's bonus to the Penetration multiplier (p. 20).
TRUE_NAME_PENETRATION = 5
#: The points a Mantle's physical Characteristics are bought with (p. 19,
#: citing ArM5 p. 30).
MANTLE_POINTS = 7
PHYSICAL = ("strength", "stamina", "dexterity", "quickness")
MENTAL = ("intelligence", "perception", "presence", "communication")
SHORT = {
    "intelligence": "Int",
    "perception": "Per",
    "presence": "Pre",
    "communication": "Com",
}


def is_divine(creature: Creature) -> bool:
    return creature.realm == DIVINE


def choirs_of(creature: Creature) -> list[Choir]:
    """The Choirs its Order names, the Archangels last (an archangel keeps
    its first Choir's traits too, p. 25); none for a creature of another
    realm."""
    if not is_divine(creature):
        return []
    text = creature.order.casefold()
    found = [c for c in CHOIRS if re.search(c.pattern, text)]
    return sorted(found, key=lambda c: c.name == "Archangels")


def is_grigori(creature: Creature) -> bool:
    return is_divine(creature) and bool(GRIGORI.search(creature.order))


def is_angel(creature: Creature) -> bool:
    """An angel built by Realms of Power: The Divine: its Order names a
    Choir, or the Grigori."""
    return bool(choirs_of(creature)) or is_grigori(creature)


def least_might(creature: Creature) -> int:
    """The least Divine Might its Choirs allow (pp. 21-26), 1 for any
    angel (p. 19)."""
    return max([1, *(c.least_might for c in choirs_of(creature))])


def mental_score(might: int) -> int:
    """An angel's Int, Per, Pre and Com: +1 for each 10 points of Divine
    Might or fraction (p. 19)."""
    return max(1, round_up(max(0, might) / 10))


def mantle_points(creature: Creature) -> int:
    """What its Mantle's physical Characteristics cost (p. 19)."""
    ch = creature.characteristics
    return sum(cost(getattr(ch, name)) for name in PHYSICAL)


def second_sight(might: int) -> int:
    """The Second Sight an angel has for finding non-Divine regiones:
    its Might / 5 (p. 21)."""
    return round_down(max(0, might) / 5)


def illumination_penetration(creature: Creature) -> int:
    """Its speech's Penetration: 0 plus its Penetration Ability (p. 20)."""
    return max(
        (a.level for a in creature.abilities if a.name.casefold() == "penetration"),
        default=0,
    )


def smite_evil_level(points: int) -> int:
    """Smite Evil's level, as Demon's Eternal Oblivion: 10 a Might Point
    spent (p. 21)."""
    return SMITE_LEVELS_PER_POINT * max(1, points)


def sway_cost(area: str, temper: int = SWAY_TEMPER) -> int:
    """What Sway the Hearts of Man costs over an area for a temper (+2,
    then 5 points for each +1 more; p. 24)."""
    return PRINCIPALITY_COSTS[area] + SWAY_STEP * max(0, temper - SWAY_TEMPER)


def radiant_mirror_influence(might: int) -> int:
    """A Throne's Holy Influence Total with Radiant Mirror: its Might / 2
    (p. 22)."""
    return round_down(max(0, might) / 2)


def _power(creature: Creature, name: str) -> CreaturePower | None:
    wanted = name.casefold()
    return next((p for p in creature.powers if wanted in p.name.casefold()), None)


def _trait(creature: Creature, name: str) -> int | None:
    wanted = name.casefold()
    return next(
        (t.score for t in creature.personality_traits if t.name.casefold() == wanted),
        None,
    )


def _trait_problems(creature: Creature) -> list[str]:
    found: list[str] = []
    wanted: list[tuple[tuple[str, int], int]] = [(LOVE_OF_GOD, 19)]
    for choir in choirs_of(creature):
        wanted += [(t, choir.page) for t in choir.traits]
    for (name, score), page in wanted:
        has = _trait(creature, name)
        if has != score:
            now = "" if has is None else f", not {has:+d}"
            found.append(f"{name} {score:+d}{now} (p. {page})")
    return found


def _power_problems(creature: Creature) -> tuple[list[str], list[str]]:
    """The powers it lacks, and those whose typed cost or Initiative
    differ from the book's."""
    missing: list[str] = []
    differ: list[str] = []
    rows: list[tuple[AngelicPower, int]] = [(p, 19) for p in ANGELIC_POWERS]
    for choir in choirs_of(creature):
        rows += [(p, choir.page) for p in choir.powers]
    for row, page in rows:
        power = _power(creature, row.name)
        if power is None:
            missing.append(f"{row.name} (p. {page})")
        elif not row.fits(power):
            differ.append(
                f"{row.name} costs {row.cost_text()}, Init {row.init:+d}, not "
                f"{power.might_cost}, {power.init:+d} (p. {page})"
            )
    return missing, differ


def problems(creature: Creature) -> list[str]:
    """What a divine being, or an angel built by Realms of Power: The
    Divine, would have that this one lacks, or has that it can't
    (advice)."""
    if not is_divine(creature):
        return []
    found: list[str] = []
    if any(vf.vf_id == TRUE_FAITH for vf in creature.virtues_flaws):
        found.append("A creature with Divine Might can't have True Faith (DE p. 488).")
    if not is_angel(creature):
        return found
    least = least_might(creature)
    if creature.might < least:
        names = ", ".join(c.name for c in choirs_of(creature)) or "an angel"
        found.append(
            f"{names}: Divine Might no less than {least}, not {creature.might} "
            "(pp. 19-26)."
        )
    traits = _trait_problems(creature)
    if traits:
        found.append(f"Personality Traits by the book: {'; '.join(traits)}.")
    missing, differ = _power_problems(creature)
    if missing:
        found.append(f"Missing powers: {', '.join(missing)}.")
    if differ:
        found.append("; ".join(differ) + ".")
    score = mental_score(creature.might)
    ch = creature.characteristics
    off = [SHORT[n] for n in MENTAL if getattr(ch, n) != score]
    if creature.might > 0 and off:
        found.append(
            f"At Divine Might {creature.might} an angel's Int, Per, Pre and Com "
            f"are {score:+d}: {', '.join(off)} differ (p. 19)."
        )
    return found


def notes(creature: Creature) -> list[str]:
    """What the books' rules make of an angel: its Mantle, senses, True
    Name and the magic that reaches it, and The Gift."""
    if not is_angel(creature):
        return []
    might = max(0, creature.might)
    form = (
        f"its Might's Form, {creature.might_form}"
        if creature.might_form
        else "its Might's Form"
    )
    found = [
        f"its Mantle's physical Characteristics cost {mantle_points(creature)} "
        f"point(s); the book buys them with {MANTLE_POINTS}, more for a "
        "powerful angel (p. 19)",
        f"in spirit form only Mentem and Vim reach it, and it has no Wounds or "
        f"Fatigue; in its Mantle, spells of {form} (p. 21)",
        "magic can't make it act against its Personality Traits; Might below 0 "
        "destroys it; Hermetic magic can't summon or compel it (p. 21)",
        f"its True Name: an Arcane Connection and +{TRUE_NAME_PENETRATION} to "
        "the Penetration multiplier (p. 20)",
        f"its illumination penetrates at {illumination_penetration(creature)} (p. 20)",
        f"it knows every aura, never hindered by one, and finds regiones with "
        f"Second Sight {second_sight(might)} (p. 21)",
        "it never minds The Gift, judging deeds and hearts (DE pp. 488-489)",
    ]
    names = {c.name for c in choirs_of(creature)}
    if "Seraphim" in names:
        found.append(
            f"Smite Evil is level {SMITE_LEVELS_PER_POINT} a Might Point, faeries "
            "too (p. 21)"
        )
    if "Thrones" in names:
        found.append(
            f"Radiant Mirror raises a Divine aura by 2, its Holy Influence Total "
            f"{radiant_mirror_influence(might)} (p. 22)"
        )
    if "Principalities" in names:
        costs = ", ".join(f"{k} {v}" for k, v in PRINCIPALITY_COSTS.items())
        found.append(
            f"its powers cost by the area: {costs}; Sway's temper +{SWAY_TEMPER}, "
            f"{SWAY_STEP} more a +1; Penetration doubled against Infernal Might "
            "(p. 24)"
        )
    if "Archangels" in names:
        found.append(
            f"Irresistible Light: +{LIGHT_DAMAGE} damage to every non-Divine being "
            f"it senses (doubled against Infernal Might), {LIGHT_STRIPS} Might "
            f"stripped, Penetration its full Might ({might}) (p. 25)"
        )
    if is_grigori(creature):
        found.append(
            "a Watcher is trapped in its Mantle: slain without the Might for a new "
            "one, it dies (p. 26)"
        )
    return found
