"""Devotion to the saints, and invoking and threatening them, as plain
rules (The Church pp. 11-15; Realms of Power: The Divine pp. 85-91).

- Invoking a saint (RoP: The Divine p. 87; The Church p. 13): once a day,
  Communication + Charm + modifiers + a simple die against 15 + a simple
  die (the storyguide's, rolled in secret). Heard, the saint uses one of
  his powers for the petitioner; refused, he may ask again tomorrow. The
  modifiers: at the saint's tomb +1, a Divine aura +its level, the feast
  day +3, a pilgrimage in his honour within the year +2, a donation +1 to
  +3, imminent peril +2, True Faith +1 a point of Score; an unchristian
  act in the last month -1 to -3, no donation within a year -3, a miracle
  received within the month -20, and -15 for a saint other than a patron.
- Devotion (The Church pp. 12-15): a reverence for a saint (or the
  Virgin, or an aspect of Christ) that advances as an Ability does, but
  only on Devotion Points, never experience, and has no Specialty. Its
  score, the Devotion Total, is added to invoking that saint, and anyone
  with a Devotion Point toward a saint may invoke him without the -15. At
  creation a Christian with a positive Pious trait has Devotion Points
  equal to it (the Pious Flaw counts 3, its Major form 6) to share among
  as many saints; impious characters have no Devotions. A later change
  to Pious changes nothing. Neglecting the saint's feast costs at least
  3 Devotion Points (and the day is lost to the season).
- Patron saints (The Church p. 13): anyone may have one, Pious or not;
  anyone may ask the Blessed Virgin; anyone may call on a saint whose
  traditional concern is the matter at hand (a sacramental counts so,
  p. 13); and with any of these there is no -15. Anyone of Irish birth
  may call on Saints Patrick, Brigid and Columba as patrons (The
  Contested Isle p. 134).
- Relics (The Church p. 13, followed over RoP: The Divine p. 87 where
  they differ): with The Church in play, a relic of the saint invoked adds +2
  for each of its Faith Points to the Devotion Total, no more than once a
  day, for one person who tends or carries it (or who spends a day of
  intense veneration at its shrine, with the custodians' leave), and
  takes away the -15 for an unfamiliar saint. This replaces RoP: The
  Divine's "touching the saint's relic +1"; the relic counts once. A
  relic of another saint, or any relic for a troupe not using The
  Church, keeps the +1. True Faith's +1 a point is separate.
- Icons (The Sundered Eagle pp. 133-134): a venerated eikon of the saint
  adds its Aesthetic Quality / 5, rounded up (rules.theban_customs).
- Indulgences, vigils and fasts (The Church pp. 11-12): an indulgence
  costs the poor about 6 pennies, the wealthy a pound or more, for each
  season of penance it remits; with a season of charitable works after
  it, it may bring as many experience points in a Reputation for Piety,
  and one temporary Faith Point. A vigil's night of prayer costs a
  Fatigue level until a full night's sleep, and gives a Confidence Point
  to spend the next day on a named virtuous task. A season's fast gives
  +1 (not cumulative) to invoking a saint, and a Fatigue level all
  season.
- Threatening a saint (RoP: The Divine pp. 87-88), after an invocation
  he refused: Presence + Leadership + modifiers + a stress die against 9
  + a fifth of his Divine Might (rounded down: the book gives no
  rounding, and its printed Mights are all multiples of 5, so only a
  custom Might is rounded, the app's choice); Confidence may be spent, Faith Points
  not. Succeed, and he grants the miracle at once (one in his powers);
  fail, and he hears none of the petitioner's prayers for a month; fail
  by 10 or more, and he lays a minor curse (one costing 1 Might) and
  grants nothing for a season; botch, and his curse falls.

The Definitive Edition has none of this but True Faith and relics (DE p.
419): a relic's Faith Points serve its bearer as Confidence, ten times its
Faith score is his Magic Resistance, and one may rely on one relic at a
time. The errata change nothing here (RoP: The Divine's errata, p. 49,
only re-add the Relic Virtue as the DE has it)."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass

from ..models import Character, Progress
from . import dice, xp
from .scores import ability_level
from .theban_customs import Invocation, pious

SOURCE = (
    "The Church pp. 11-15; Realms of Power: The Divine pp. 85-91; The "
    "Sundered Eagle pp. 133-137; The Contested Isle pp. 134-138; DE p. 419"
)
TC = "TC"
ROPD = "RoP:D"

#: The kinds of the character's progress records devotion keeps: a
#: Devotion (points toward a saint), the patron saint, a season's fast.
DEVOTION = "devotion"
PATRON = "patron saint"
FAST = "fast"

#: Every kind devotion keeps.
KINDS = (DEVOTION, PATRON, FAST)

INVOKE_EASE = 15
THREAT_EASE = 9

#: The Pious Personality Flaws, and the Devotion Points each gives at
#: creation (The Church p. 12).
PIOUS_FLAWS: dict[str, int] = {"vf_pious": 3, "vf_pious_major": 6}

#: The invocation modifiers (RoP: The Divine p. 87; The Church p. 12).
TOMB = 1
FEAST_DAY = 3
PILGRIMAGE = 2
PERIL = 2
FASTING = 1
NO_DONATION = -3
MIRACLE_LATELY = -20
UNFAMILIAR = -15
#: Touching a relic, RoP: The Divine's way; and The Church's, per Faith Point.
RELIC_TOUCHED = 1
RELIC_PER_FAITH = 2

#: The threat modifiers (RoP: The Divine p. 88).
THREATS: dict[str, tuple[str, int]] = {
    "bones": ("Exposing his bones", 1),
    "whipping": ("Defiling his relics", 2),
    "berating": ("Berating him before others", 1),
    "barring": ("Barring others from him", 3),
    "peril": ("Imminent peril", 1),
}
#: A miss this far below the Ease Factor brings a minor curse.
CURSED_MISS = 10

#: Neglecting a saint's feast costs at least this many Devotion Points.
FEAST_NEGLECTED = 3

#: Indulgences (The Church p. 12): the price of a season remitted.
POOR_PRICE = 6
WEALTHY_PRICE = 240
PIETY = "Piety"


# -- the names of saints --

_TITLES = re.compile(r"^(?:the |saints? |st\.? |sts\.? |naomh |hagios |agios )+")
#: Other names for the Blessed Virgin.
_MARY = {
    "mary",
    "virgin mary",
    "blessed virgin",
    "blessed virgin mary",
    "virgin",
    "queen of heaven",
    "theotokos",
    "mother of god",
    "our lady",
}


def saint_key(name: str) -> str:
    """A saint's name for comparing: lower case, without "Saint", "St." or
    "the" ("St. Peter" and "Saint Peter" match); every name of the Virgin
    is "mary"."""
    plain = " ".join(name.casefold().replace(",", " ").split())
    plain = _TITLES.sub("", plain).strip()
    return "mary" if plain in _MARY else plain


def same_saint(a: str, b: str) -> bool:
    """Whether two names are one saint's: the same key, or one is the
    other without its "of ..." ("Kevin" and "Kevin of Glendalough")."""
    if not a.strip() or not b.strip():
        return False
    first, second = saint_key(a), saint_key(b)
    return first == second or first.split(" of ")[0] == second.split(" of ")[0]


# -- Devotions --


def devotions(character: Character) -> list[Progress]:
    """The character's Devotions, as progress records of Devotion Points."""
    return [p for p in character.progress if p.kind == DEVOTION]


def devotion(character: Character, saint: str) -> Progress | None:
    return next((p for p in devotions(character) if same_saint(p.name, saint)), None)


def score(points: int) -> int:
    """A Devotion's score from its Devotion Points, as an Ability's from
    experience (DE p. 49)."""
    return xp.score_from_xp(max(0, points), xp.ABILITY_FACTOR)


def devotion_total(character: Character, saint: str) -> int:
    """The character's score in Devotion to `saint` (0 without one)."""
    found = devotion(character, saint)
    return score(found.points) if found is not None else 0


def devoted(character: Character, saint: str) -> bool:
    """Whether the character has a Devotion Point toward the saint: enough
    to invoke him as a patron (The Church p. 13)."""
    found = devotion(character, saint)
    return found is not None and found.points > 0


def add_points(character: Character, saint: str, points: int) -> Progress:
    """Devotion Points gained (or lost, when negative: never below 0)
    toward `saint`, a new Devotion when he has none."""
    found = devotion(character, saint)
    if found is None:
        found = Progress(DEVOTION, saint.strip())
        character.progress.append(found)
    found.points = max(0, found.points + points)
    return found


def devotion_label(record: Progress) -> str:
    """ "Saint Bartholomew 1 (6)": the score and its Devotion Points."""
    return f"{record.name} {score(record.points)} ({record.points})"


def patron(character: Character) -> str:
    """The character's patron saint ("" for none)."""
    return next((p.name for p in character.progress if p.kind == PATRON), "")


def set_patron(character: Character, saint: str) -> None:
    character.progress[:] = [p for p in character.progress if p.kind != PATRON]
    if saint.strip():
        character.progress.append(Progress(PATRON, saint.strip()))


def lines(character: Character) -> list[str]:
    """The Planning tab's lines: his patron saint and his Devotions (none
    when he has neither)."""
    found = []
    if saint := patron(character):
        found.append(f"Patron saint: {saint}")
    held = devotions(character)
    if held:
        found.append("Devotions: " + ", ".join(devotion_label(p) for p in held))
    return found


def creation_points(character: Character) -> int:
    """The Devotion Points a Christian starts with: his positive Pious
    trait, the Pious Flaw counting 3 and its Major form 6 (The Church p.
    12); 0 for the impious."""
    ids = {vf.vf_id for vf in character.virtues_flaws}
    from_flaw = max((n for vf_id, n in PIOUS_FLAWS.items() if vf_id in ids), default=0)
    return max(0, pious(character), from_flaw)


def creation_problem(character: Character, saint: str, points: int) -> str | None:
    """Why `points` more Devotion Points toward `saint` at creation exceed
    what Pious allows: no more saints, nor points, than it."""
    allowed = creation_points(character)
    held = devotions(character)
    spent = sum(p.points for p in held) + max(0, points)
    saints = len(held) + (0 if devotion(character, saint) else 1)
    if not allowed:
        return "Only a character with a positive Pious trait starts with Devotions."
    if saints > allowed:
        return f"No more than {allowed} Devotions at creation (his Pious)."
    if spent > allowed:
        return f"Only {allowed} Devotion Points at creation (his Pious)."
    return None


# -- fasting --


def keep_fast(character: Character, season: str, year: int) -> None:
    """Mark the season a fast: one record, the latest season's."""
    found = next((p for p in character.progress if p.kind == FAST), None)
    if found is None:
        found = Progress(FAST, "Fast")
        character.progress.append(found)
    found.last_season, found.last_year = season, year


def fasting(character: Character, season: str, year: int) -> bool:
    return any(
        p.kind == FAST and (p.last_season, p.last_year) == (season, year)
        for p in character.progress
    )


# -- relics --


def relic_bonus(faith: int, of_the_saint: bool, the_church: bool) -> int:
    """What a relic adds to invoking: with The Church's rules, +2 a Faith
    Point for the saint's own relic; otherwise (another saint's, or
    without them) the +1 for touching it."""
    if of_the_saint and the_church:
        return RELIC_PER_FAITH * max(0, faith)
    return RELIC_TOUCHED


# -- invoking --


@dataclass(frozen=True)
class Situation:
    """Where and how the petitioner invokes: each modifier's facts.
    `relic_faith` is None with no relic; `donation` is -3 (none within a
    year), 0, or 1 to 3 given now; `appropriate`: the saint's concern is
    the matter at hand, or the rite is a sacramental."""

    tomb: bool = False
    aura: int = 0
    feast_day: bool = False
    pilgrimage: bool = False
    relic_faith: int | None = None
    relic_of_the_saint: bool = False
    icon: int = 0
    donation: int = 0
    peril: bool = False
    fasting: bool = False
    unchristian: int = 0
    miracle_lately: bool = False
    appropriate: bool = False
    irish: bool = False


@dataclass(frozen=True)
class Petition:
    """An invocation's total, each term as words, and why the -15 does not
    apply ("" when it does)."""

    total: int
    terms: tuple[str, ...]
    familiar: str


def familiar(
    character: Character,
    saint: str,
    situation: Situation,
    *,
    anyone: bool = False,
    irish_patron: bool = False,
    the_church: bool = True,
) -> str:
    """Why invoking `saint` needs no -15 ("" when it does): his patron, a
    Devotion, the Virgin (`anyone`), a matter in his care, his relic held
    (The Church's rule), an Irish patron for one of Irish birth."""
    if same_saint(patron(character), saint):
        return "his patron saint"
    if the_church and devoted(character, saint):
        return "devoted to the saint"
    if anyone or saint_key(saint) == "mary":
        return "anyone may ask the Blessed Virgin"
    if situation.appropriate:
        return "the matter is in the saint's care"
    if (
        the_church
        and situation.relic_faith is not None
        and situation.relic_of_the_saint
    ):
        return "he holds the saint's relic"
    if irish_patron and situation.irish:
        return "a patron of Ireland, and he is Irish-born"
    return ""


def petition(
    character: Character,
    saint: str,
    situation: Situation,
    *,
    anyone: bool = False,
    irish_patron: bool = False,
    the_church: bool = True,
) -> Petition:
    """Communication + Charm + the modifiers: with The Church's rules, the
    Devotion Total and The Church's relic bonus and fast."""
    c = character.characteristics
    charm = ability_level(character, "Charm")
    terms = [f"Communication {c.communication:+d}", f"+ Charm {charm}"]
    total = c.communication + charm

    def add(label: str, value: int) -> None:
        nonlocal total
        if value:
            terms.append(f"{'+' if value > 0 else '-'} {label} {abs(value)}")
            total += value

    s = situation
    if the_church:
        add("Devotion", devotion_total(character, saint))
    if s.relic_faith is not None:
        add("relic", relic_bonus(s.relic_faith, s.relic_of_the_saint, the_church))
    add("icon", max(0, s.icon))
    add("tomb", TOMB if s.tomb else 0)
    add("Divine aura", max(0, s.aura))
    add("feast day", FEAST_DAY if s.feast_day else 0)
    add("pilgrimage", PILGRIMAGE if s.pilgrimage else 0)
    add("donation", s.donation if s.donation in (NO_DONATION, 1, 2, 3) else 0)
    add("peril", PERIL if s.peril else 0)
    add("True Faith", max(0, character.background.true_faith_score))
    add("fasting", FASTING if s.fasting and the_church else 0)
    add("unchristian act", -min(3, max(0, s.unchristian)))
    add("miracle this month", MIRACLE_LATELY if s.miracle_lately else 0)
    reason = familiar(
        character,
        saint,
        s,
        anyone=anyone,
        irish_patron=irish_patron,
        the_church=the_church,
    )
    add("not a patron", 0 if reason else UNFAMILIAR)
    return Petition(total, tuple(terms), reason)


def invoke(total: int, rng: random.Random) -> Invocation:
    """The petitioner's simple die and the storyguide's, against 15 + it."""
    return Invocation(total, dice.simple_die(rng), dice.simple_die(rng))


def chance(total: int) -> float:
    """The chance `total` + a simple die meets 15 + another simple die."""
    hits = sum(
        1
        for mine in range(1, 11)
        for theirs in range(1, 11)
        if total + mine >= INVOKE_EASE + theirs
    )
    return hits / 100


# -- threatening --


def threat_ease(might: int) -> int:
    """9 + a fifth of the saint's Divine Might (p. 88)."""
    # The book gives no rounding: every printed Might is a multiple of 5,
    # so rounding a custom one down is the app's own choice.
    return THREAT_EASE + max(0, might) // 5


def threat_total(
    character: Character,
    chosen: tuple[str, ...],
    *,
    miracle_lately: bool = False,
    unfamiliar: bool = False,
    confidence: int = 0,
) -> tuple[int, tuple[str, ...]]:
    """Presence + Leadership + the threat's modifiers (+3 a Confidence
    Point spent)."""
    c = character.characteristics
    leadership = ability_level(character, "Leadership")
    terms = [f"Presence {c.presence:+d}", f"+ Leadership {leadership}"]
    total = c.presence + leadership
    for key in chosen:
        label, value = THREATS[key]
        terms.append(f"+ {label.lower()} {value}")
        total += value
    if miracle_lately:
        terms.append(f"- miracle this month {-MIRACLE_LATELY}")
        total += MIRACLE_LATELY
    if unfamiliar:
        terms.append(f"- unfamiliar saint {-UNFAMILIAR}")
        total += UNFAMILIAR
    if confidence > 0:
        terms.append(f"+ Confidence {3 * confidence}")
        total += 3 * confidence
    return total, tuple(terms)


THREAT_GRANTED = "granted"
THREAT_ANNOYED = "annoyed"
THREAT_CURSED = "cursed"
THREAT_BOTCHED = "botched"

#: What each outcome of a threat means (RoP: The Divine p. 88).
THREAT_OUTCOMES: dict[str, str] = {
    THREAT_GRANTED: "The saint grants the miracle at once (one of his powers).",
    THREAT_ANNOYED: "The saint is annoyed: he answers none of his petitions "
    "for a month.",
    THREAT_CURSED: "The saint lays a minor curse on him (one costing 1 Might) "
    "and grants him nothing for a season.",
    THREAT_BOTCHED: "The saint lays his curse on him.",
}


def threat_outcome(roll: dice.Roll) -> str:
    """Granted, annoyed, cursed (a miss by 10 or more) or botched."""
    if roll.die.botched:
        return THREAT_BOTCHED
    if roll.succeeded:
        return THREAT_GRANTED
    margin = roll.margin or 0
    return THREAT_CURSED if margin <= -CURSED_MISS else THREAT_ANNOYED


# -- gaining Devotion Points (The Church pp. 14-15) --


@dataclass(frozen=True)
class Gain:
    """A way of gaining Devotion Points: what it is, its usual points
    (low, high) and the book's guidance."""

    label: str
    low: int
    high: int
    hint: str


CREATION = "creation"
NEGLECT = "neglect"
GAINS: dict[str, Gain] = {
    CREATION: Gain(
        "At creation (his Pious)",
        1,
        1,
        "Points equal to his positive Pious trait (the Pious Flaw 3, its "
        "Major form 6), among as many saints (p. 12).",
    ),
    "season": Gain(
        "A season of personal devotion at a shrine",
        5,
        5,
        "Prayer and meditation for a season: 5; the only experience is "
        "exposure in Church or Dominion Lore (p. 14).",
    ),
    "endowment": Gain(
        "Endowing a church, chapel or monastery to the saint",
        5,
        50,
        "5 for a small chapel founded without a story, up to 50 for a "
        "cathedral at the saga's heart (p. 14).",
    ),
    "guild_joined": Gain(
        "Joining a guild dedicated to the saint",
        3,
        3,
        "3 on joining (p. 14).",
    ),
    "guild_rank": Gain(
        "Journeyman or master of the saint's guild",
        2,
        2,
        "2 each on becoming journeyman and master (p. 14).",
    ),
    "site": Gain(
        "Visiting a site of the saint",
        1,
        10,
        "Tomb, major relic, martyrdom or great miracle: 1 in his home town; "
        "5 or more for a season's journey or out of his way; 10 for a "
        "hazardous story of a season's travel. Usually once (p. 14).",
    ),
    "artwork": Gain(
        "Sponsoring church art of the saint",
        1,
        10,
        "The finished work's Aesthetic Quality, usually through a story; "
        "only the best work for each saint counts (p. 14).",
    ),
    "hagiography": Gain(
        "Studying a hagiography",
        1,
        10,
        "A season with a book wholly on the saint: its Quality / 2; a "
        "general work on many saints, 1 once for each (p. 14).",
    ),
    "cultus": Gain(
        "Furthering the saint's cultus",
        1,
        30,
        "The Petitioning Ease Factor, for recognition, a work cleared of "
        "heresy or a church to him consecrated (p. 14).",
    ),
    "miracle": Gain(
        "Witnessing a genuine miracle of the saint",
        5,
        10,
        "5 to 10; 10 only when it saved his life. None, or a loss, for a "
        "miracle that thwarts him or one asked for trivially (p. 14).",
    ),
    "procession": Gain(
        "The saint's feast day procession",
        1,
        5,
        "1 when it is part of a story or costs him; 1 to 5 more for "
        "honouring the saint beyond the usual or sponsoring the feast "
        "(pp. 14-15).",
    ),
    "pilgrimage": Gain(
        "A pilgrimage in the saint's honour",
        1,
        10,
        "As the pilgrimage's rules give, and its badge (p. 15).",
    ),
    "vision": Gain(
        "A dream or vision from the saint",
        1,
        1,
        "1, for a character with Visions or Premonitions, in a story (p. 15).",
    ),
    NEGLECT: Gain(
        "Neglecting the saint's feast day (a loss)",
        -FEAST_NEGLECTED,
        -FEAST_NEGLECTED,
        "At least 3 lost, more as the troupe decides; the day is lost to "
        "the season (p. 14).",
    ),
    "other": Gain("Something else the troupe allows", 1, 10, ""),
}


# -- indulgences (The Church p. 12) --


def indulgence_price(seasons: int, wealthy: bool) -> int:
    """In pennies: about 6 a season for the poor, at least a pound (240)
    a season for the wealthy."""
    return max(0, seasons) * (WEALTHY_PRICE if wealthy else POOR_PRICE)
