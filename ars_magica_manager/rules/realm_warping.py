"""Warping by realm: what Warping brings a character as its main source
differs, and so does what 2 or more points at once set off.

The Definitive Edition counts every realm's Warping Points alike (DE p.
389) and gives one set of effects for a non-magus (p. 391): the realms'
books keep those Scores and only colour what is gained. The app counts the
points from each realm as they come (Aging.warping_realms) and takes the
realm with the most as the main source, the aura where they live while
nothing is counted.

- **Effects by realm** (one strategy per realm, `EFFECTS`), for a
  non-magus outside any tradition. Magic: the DE's own (p. 391). Faerie
  (Realms of Power: Faerie p. 119): at 1 a glamour may take the Minor
  Flaw's place, a Reputation from a prominent story, rising with each
  Score; at 3 Faerie Antipathy (Minor) or Lesser Malediction, and with a
  glamour a need to live up to the Reputation once a season (Deprivation
  otherwise; a month from 4, a week from 5, a day from 6); at 5 a minor
  faerie Virtue, and with a glamour a +1 Sympathy Trait; from 6 a
  supernatural Flaw each Score, and with a glamour a -1 Sympathy Trait at
  6, +1 at 7 and so on. Divine (RoP: The Divine p. 62): Flaws that punish
  sin or push piety to extremes, from the book's lists of common Minor and
  Major Flaws. Infernal (RoP: The Infernal p. 17, with the Errata p. 56
  naming Aptitude for (Sin) in place of Paragon Through Sin): a sinful
  Minor Personality Flaw at 1; Offensive to Animals (venial sins) or
  Tainted with Evil (mortal sins, Infernal powers) at 3; an Infernal Minor
  Virtue at 5; Age Quickly, Enfeebled or Plagued by a Demon from 6. Each
  realm's Virtue at 5 stops Warping from auras of that realm (DE p. 391).
- **2 or more points at once** (one strategy per realm, `RESPONSES`). A
  magus (or anyone opened to the Arts, for a laboratory's Warping) goes to
  the edge of Wizard's Twilight (DE pp. 228-230; rules.warping), even
  with True Faith (RoP: The Divine p. 63), unless he is an infernalist
  (Vituperation: the False Gift brings it in place of Twilight, RoP: The
  Infernal p. 124), a homunculus wizard (Faerie Calling, RoP: Faerie p.
  118), or has Miraculous Abilities and the troupe chose the Divine Ascent
  as his one form of Warping (Aging.seeks_ascent; RoP: The Divine p. 63).
  Otherwise a tradition's own
  answer: the Divine Ascent for a holy character (a holy tradition, or a
  holy Power or Method held), Vituperation for an infernalist, Faerie
  Calling for one of a Faerie tradition; Divine, Infernal and Magic come
  before Faerie (RoP: Faerie p. 120).

  - Divine Ascent (RoP: The Divine p. 63): Presence + Concentration (or
    Meditation) + stress die (with its botch die) against Warping Score
    + the points + True Faith + the aura + stress die (no botch). Failing,
    he ascends: more
    Warping Points by the margin (no further Ascent), for (Warping Score
    + every point gained - True Faith, at least 1) days, months from
    Warping Score 6; his body stays, untouchable, or vanishes. He has the
    same form for life: Divine Gloom (as many xp to holy Abilities as
    Warping Points, and as many lost from mundane ones), Divine Form
    (Magic Resistance and Penetration from the Warping Score) or Divine
    Unity (the Warping Score added to the virtue's Personality Trait;
    pp. 63-65). There is no Final Ascent. A mystic of The Church (rules.
    mysticism) always ascends, magus or not: a contemplative to the Divine
    Form, a monist to the Divine Gloom, and a monist at a single point
    (The Church pp. 21, 23).
  - Vituperation (RoP: The Infernal p. 95; rules.infernalists):
    Stamina + Concentration + Confidence Score + stress die against
    Warping Score + the points + Hierarchy + the aura + stress die (no
    botch); he may accept it unrolled. Failing, he is torn away for as
    long as Twilight's table gives his Warping Score, then makes an Aging
    roll adding it. Once that is over his Confidence Score rises by 1 if
    below his Warping Score or Decrepitude, and he gains a Confidence
    Point a Warping Point unless he botched: the Aging roll is the
    player's, so the Diary says what is then due rather than changing it.
  - Faerie Calling (RoP: Faerie p. 120): dazed until the scene ends, acting
    at Perception + Awareness + stress die against 3 x (Warping Score +
    the points); the dream is played out, then Perception + Concentration
    + stress die (with its botch die) against 3 x (Warping Score - Faerie
    Rank): above it a +1
    Sympathy Trait (or +1 to one), else a -1. It says from which Faerie
    Rank the Calling is a good one, and, for one whose Personality Traits
    hold Sympathy Traits, which his is (rules.faerie_sympathy).

- **Leaving Faerie** (RoP: Faerie pp. 29-30). The final fable score sets
  how long each day in Faerie lasts in the mundane world (0: an hour, 1:
  12 hours, 2: a day, 3: three days, 4: a week, 5: a month, 6: a season,
  7+: a year). Each Warping Point a character takes as he leaves lowers it
  by 1; a group leaving together takes the lowest, the others taking the
  points to match. These points never bring Twilight.
- **Instant travel** (Transforming Mythic Europe pp. 112, 114). An
  instant transport of level 30 or more is a powerful effect: a Warping
  Point each transit unless the effect was cast by or designed for the one
  carried (DE p. 390); a Hermes' Portal or Mercere's Portal gives none, as
  its target is the portal's far end. Each transit is its own event, so no
  number of them brings Twilight. The book's Flaws at 5 transits and
  another at 15, and a Minor Virtue at 75, follow the Warping Scores; the
  DE puts the second Flaw at Score 3 (30 points), and the app follows it.

Pattern: Strategy, one per realm in each dict (as rules.aura_change keeps
one per realm for its aura's year).
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable
from dataclasses import dataclass

from .. import catalog
from ..models import Character, Saga
from . import dice, faerie_sympathy, hybrid_magic, infernalists, mysticism
from . import divine_state as ds
from . import warping as warping_rules
from .realms import home_aura
from .scores import ability_level

FAERIE_SOURCE = (
    "Realms of Power: Faerie, Homunculi Wizards, p. 118; Faerie Warping and "
    "Faerie Calling, pp. 119-120"
)
LEAVING_SOURCE = (
    "Realms of Power: Faerie, Chapter Two: Leaving Faerie, Warping and the "
    "Passage of Time, pp. 29-30"
)
DIVINE_SOURCE = "Realms of Power: The Divine, Divine Warping, pp. 62-65"
INFERNAL_SOURCE = (
    "Realms of Power: The Infernal, Infernal Warping, pp. 17-18 (Errata p. 56); "
    "Vituperation, p. 95; False Magic, p. 124"
)
TRAVEL_SOURCE = (
    "Transforming Mythic Europe, Warping Gained from Instant Transportation, "
    "pp. 112, 114"
)
SOURCE = (
    f"{warping_rules.SOURCE}; {FAERIE_SOURCE}; {LEAVING_SOURCE}; {DIVINE_SOURCE}; "
    f"{INFERNAL_SOURCE}; {TRAVEL_SOURCE}"
)

MAGIC, FAERIE, DIVINE, INFERNAL = "Magic", "Faerie", "Divine", "Infernal"

# ---------------------------------------------------------------------------
# Counting Warping by realm


def record(character: Character, realm: str, points: int) -> None:
    """Count `points` Warping Points from `realm`."""
    if points <= 0:
        return
    counts = character.aging.warping_realms
    counts[realm or MAGIC] = counts.get(realm or MAGIC, 0) + points


def main_realm(saga: Saga, character: Character) -> str:
    """The realm most of the counted Warping came from (a tie goes to the
    aura where they live, then the first by name); that aura's realm while
    none is counted."""
    _, home = home_aura(saga, character)
    counts = character.aging.warping_realms
    if not counts:
        return home or MAGIC
    top = max(counts.values())
    tied = sorted(realm for realm, points in counts.items() if points == top)
    return home if home in tied else tied[0]


# ---------------------------------------------------------------------------
# Effects by realm, for a non-magus

#: What a Warping Score brings, by realm: a function from the Score to its
#: text ("" for nothing at that Score).
EffectsStrategy = Callable[[int], str]


def _magic_effects(score: int) -> str:
    return warping_rules.MUNDANE_EFFECTS.get(min(score, 6), "")


_FAERIE: dict[int, str] = {
    1: (
        "a Minor Flaw, or in its place a glamour of their own: a Reputation "
        "(a Flaw) from a prominent story, at 1 and rising with each Warping "
        "Score (RoP: Faerie p. 119)"
    ),
    3: (
        "Faerie Antipathy (Minor) or Lesser Malediction; with a glamour, a "
        "need to act on its Reputation once a season, or Deprivation"
    ),
    4: "with a glamour, the need comes every month",
    5: (
        "a minor faerie Virtue (Faerie Sympathy (Minor), Lesser Benediction, "
        "Lesser Immunity, Second Sight): no more Warping from Faerie auras; "
        "with a glamour, a +1 Sympathy Trait tied to the Reputation, and the "
        "need every week"
    ),
}


def _faerie_effects(score: int) -> str:
    if score < 6:
        return _FAERIE.get(score, "")
    glamour = (
        "a -1 Sympathy Trait, and the need every day"
        if score == 6
        else "another -1 Sympathy point"
        if score % 2 == 0
        else "another +1 Sympathy point"
    )
    return (
        "a supernatural Flaw (Greater Malediction, Magical Air...); with a "
        f"glamour, {glamour}"
    )


_DIVINE: dict[int, str] = {
    1: (
        "a Minor Flaw that punishes sin or pushes piety to an extreme "
        "(Compassionate, Compulsion (prayer, self-flagellation), Continence, "
        "Disfigured (stigmata), Driven, Fear, Fragile Constitution, Generous, "
        "Humble, Lame, Obsessed, Pious, Soft-Hearted, Susceptibility to Divine "
        "or Infernal Power, Temperate, Visions: RoP: The Divine p. 62)"
    ),
    3: "a second Minor Flaw from the same list",
    5: "a Minor Divine Virtue: no more Warping from Divine auras",
    6: "a Major Flaw (Blind, Deaf, Driven (Major), Enfeebled, Pious (Major))",
}


def _divine_effects(score: int) -> str:
    return _DIVINE.get(min(score, 6), "")


_INFERNAL: dict[int, str] = {
    1: (
        "a Minor Personality Flaw of sin (Avaricious, Envious, Greedy, Hatred, "
        "Lecherous, Proud or Wrathful as a Minor Flaw, or Delusion, Obsessed, "
        "Compulsion; Weak-Willed for many venial sins: RoP: The Infernal p. 17)"
    ),
    3: (
        "Offensive to Animals if mostly from venial sins, Tainted with Evil if "
        "from mortal sins or Infernal powers"
    ),
    5: (
        "an Infernal Minor Virtue (Enticer of Multitudes, Infernal Protection, "
        "Gender Shift, Aptitude for (Sin), Infernal Blessings (Minor)): no more "
        "Warping from Infernal auras"
    ),
    6: "Age Quickly or Enfeebled, or a demon sent to keep him (Plagued by a Demon)",
}


def _infernal_effects(score: int) -> str:
    return _INFERNAL.get(min(score, 6), "")


EFFECTS: dict[str, EffectsStrategy] = {
    MAGIC: _magic_effects,
    FAERIE: _faerie_effects,
    DIVINE: _divine_effects,
    INFERNAL: _infernal_effects,
}


def effects(before: int, after: int, realm: str) -> list[str]:
    """What a non-magus gains as their Warping Score goes from `before` to
    `after`, with Warping mostly from `realm`."""
    strategy = EFFECTS.get(realm, _magic_effects)
    found: list[str] = []
    for score in range(before + 1, after + 1):
        what = strategy(score)
        if what:
            found.append(f"Warping Score {score} ({realm} Warping): {what}.")
    return found


#: What instant transport's Warping tends to bring, by Warping Score.
TRAVEL_EFFECTS: dict[int, str] = {
    1: (
        "a Flaw from instant transport suits it: Motion Sickness, No Sense of "
        "Direction, or Lesser Malediction (lonely and low away from home)"
    ),
    3: "the second Flaw may be another of those",
    5: "the Virtue may be Wilderness Sense or Homing Instinct",
}


def travel_effects(before: int, after: int) -> list[str]:
    """The book's suggestions for the effects of Warping from transits."""
    return [
        f"Instant transport (TME p. 114): {TRAVEL_EFFECTS[score]}."
        for score in range(before + 1, after + 1)
        if score in TRAVEL_EFFECTS
    ]


# ---------------------------------------------------------------------------
# 2 or more points at once


#: What 2 or more points at once set off, by the realm of the response: the
#: character, the points, the aura where it happened, the dice, the saga and
#: whether he chose it. Each returns warping.TwilightResult's shape.
Response = Callable[
    [Character, int, int, random.Random, Saga | None, bool],
    warping_rules.TwilightResult,
]

#: Each response's name, as its Diary entry is called.
NAMES: dict[str, str] = {
    MAGIC: "Wizard's Twilight",
    DIVINE: "Divine Ascent",
    INFERNAL: infernalists.VITUPERATION,
    FAERIE: "Faerie Calling",
}
#: Each response's rule, for the Diary.
SOURCES: dict[str, str] = {
    MAGIC: warping_rules.TWILIGHT_SOURCE,
    DIVINE: DIVINE_SOURCE,
    INFERNAL: infernalists.SOURCE,
    FAERIE: FAERIE_SOURCE,
}
#: A tradition's Warping rule names the response its members have.
_TRADITION_RULES: dict[str, str] = {name: realm for realm, name in NAMES.items()}
#: Divine, Infernal and Magic come before Faerie (RoP: Faerie p. 120).
_PRECEDENCE = (DIVINE, INFERNAL, FAERIE)


def holy(character: Character) -> bool:
    """Whether the character holds a holy Method or Power (a Miraculous
    Ability): the Divine Ascent's mark outside a holy tradition."""
    methods, powers = hybrid_magic.methods_and_powers(DIVINE)
    return any(a.level > 0 and a.name in methods | powers for a in character.abilities)


#: The False Gift brings Vituperation in place of Twilight (RoP: The
#: Infernal p. 124); a homunculus wizard has Faerie Calling (RoP: Faerie
#: p. 118).
FALSE_GIFT = "vf_the_false_gift"
HOMUNCULUS_WIZARD = "vf_homunculus_wizard"


def may_seek_ascent(character: Character) -> bool:
    """Whether the troupe may choose the Divine Ascent in place of Twilight
    for the character: a magus who also has Miraculous Abilities (RoP: The
    Divine p. 63)."""
    return character.type == "magus" and holy(character)


def _magus_realm(character: Character, found: set[str], held: set[str]) -> str:
    """A Hermetic magus's answer: Twilight, unless he has the Divine Ascent
    by the troupe's choice (with Miraculous Abilities: RoP: The Divine p.
    63), is an infernalist (Vituperation; the False Gift, RoP: The Infernal
    p. 124) or a homunculus wizard (Faerie Calling, RoP: Faerie p. 118)."""
    instead: set[str] = set()
    if (character.aging.seeks_ascent and holy(character)) or ds.path(character):
        instead.add(DIVINE)
    if FALSE_GIFT in held or INFERNAL in found:
        instead.add(INFERNAL)
    if HOMUNCULUS_WIZARD in held:
        instead.add(FAERIE)
    return next((realm for realm in _PRECEDENCE if realm in instead), MAGIC)


def response_realm(character: Character, *, opened: bool = False) -> str | None:
    """The realm whose answer 2 or more Warping Points at once set off for
    the character, or None: Twilight for a magus (with `opened`, anyone
    opened to the Arts) unless he is an infernalist, a homunculus wizard or
    chose the Divine Ascent; else their tradition's own (Divine Ascent,
    Vituperation, Faerie Calling), or the Divine Ascent for a holder of
    holy powers."""
    traditions = catalog.load_tradition_catalog_by_id()
    found: set[str] = set()
    for tradition_id in character.traditions:
        tradition = traditions.get(tradition_id)
        if tradition is not None and tradition.warping is not None:
            realm = _TRADITION_RULES.get(tradition.warping.name)
            if realm:
                found.add(realm)
    held = {vf.vf_id for vf in character.virtues_flaws}
    magus = (
        warping_rules.opened_to_arts(character) if opened else character.type == "magus"
    )
    if magus:
        return _magus_realm(character, found, held)
    if holy(character) or ds.path(character):
        found.add(DIVINE)
    if FALSE_GIFT in held:
        found.add(INFERNAL)
    if HOMUNCULUS_WIZARD in held:
        found.add(FAERIE)
    return next((realm for realm in _PRECEDENCE if realm in found), None)


def _twilight(
    character: Character,
    gained: int,
    aura: int,
    rng: random.Random,
    saga: Saga | None,
    enter: bool,
) -> warping_rules.TwilightResult:
    return warping_rules.twilight(character, gained, aura, rng, saga, enter=enter)


#: From this Warping Score an Ascent is counted in months.
ASCENT_MONTHS_AT = 6
MONTHS_A_SEASON = 3


def ascent_time(score: int, points: int, faith: int) -> tuple[int, str, int]:
    """An Ascent's length: (how many, "days" or "months", the seasons it
    takes) for a Warping Score, every point gained and True Faith."""
    count = max(1, score + points - faith)
    if score >= ASCENT_MONTHS_AT:
        return count, "months", count // MONTHS_A_SEASON
    return count, "days", 0


def divine_ascent(
    character: Character,
    gained: int,
    aura: int,
    rng: random.Random,
    saga: Saga | None,
    enter: bool,
) -> warping_rules.TwilightResult:
    """The roll to avoid the Divine Ascent and, failing it, the Ascent
    (RoP: The Divine p. 63). With `enter` he seeks it: no roll, and no
    points for a margin."""
    a = character.aging
    faith = character.background.true_faith_score
    notes: list[str] = []
    extra = 0
    if enter:
        notes.append("The holy character seeks the Ascent: no roll to avoid it.")
    else:
        focus = max(
            ability_level(character, "Concentration"),
            ability_level(character, "Meditation"),
        )
        mine = dice.stress_die(rng, 1, saga=saga)
        theirs = dice.stress_die(rng, 0, saga=saga).value
        resist = character.characteristics.presence + focus + mine.value
        against = a.warping_score + gained + faith + aura + theirs
        notes.append(
            f"Divine Ascension: {resist} (Presence + Concentration or "
            f"Meditation) against {against} (True Faith {faith}, aura {aura})"
            + (" (botched)" if mine.botched else "")
            + "."
        )
        if resist >= against:
            notes.append("Too tied to the mundane world, he does not ascend.")
            return warping_rules.TwilightResult(False, notes=notes)
        extra = against - resist
    count, unit, seasons = ascent_time(a.warping_score, gained + extra, faith)
    notes.append(
        f"He ascends for {count} {unit}, +{extra} more Warping Points (no "
        "further Ascent from them); his body stays, untouched by any power, "
        "or vanishes until it ends."
    )
    points = gained + extra
    if ds.path(character):
        # A mystic's path decides the form (The Church pp. 21, 23).
        first = not ds.ascents(character)
        ds.note_ascent(character)
        notes += mysticism.ascent_lines(character, points if first else extra)
    else:
        notes.append(
            "The form chosen at his first Ascent stays for life: Divine Gloom "
            f"({points} xp among Dominion Lore and holy Abilities, and {points} xp "
            "lost from mundane ones), Divine Form (Magic Resistance and "
            "Penetration from his Warping Score) or Divine Unity (his Warping "
            "Score added to the virtue's Personality Trait). No Final Ascent."
        )
    return warping_rules.TwilightResult(
        True, time=f"{count} {unit}", seasons=seasons, extra_points=extra, notes=notes
    )


def confidence_due(character: Character, gained: int, *, botched: bool) -> str:
    """What a Vituperation does to his Confidence (RoP: The Infernal p.
    95): a Confidence Point a Warping Point gained, none if he botched the
    avoidance roll, which depends on nothing the Aging roll decides, so it
    is given at once (vituperation does it); and once the ordeal and its
    Aging roll are over, the Score rises by 1 if it is below his Warping
    Score or his Decrepitude (which that Aging roll may raise)."""
    background, aging = character.background, character.aging
    _, points = infernalists.confidence_after(character, gained, botched=botched)
    gain = (
        "no Confidence Points (the avoidance roll botched)"
        if botched
        else f"+{points} Confidence Points, given now"
    )
    if background.confidence_score < aging.warping_score:
        rise = (
            f"his Confidence Score rises from {background.confidence_score} to "
            f"{background.confidence_score + 1} (below his Warping Score "
            f"{aging.warping_score})"
        )
    else:
        rise = (
            f"his Confidence Score ({background.confidence_score}) rises by 1 "
            "only if that Aging roll leaves his Decrepitude above it (now "
            f"{aging.decrepitude})"
        )
    return f"{gain[0].upper()}{gain[1:]}; once the ordeal and that Aging roll are over, {rise}."


def vituperation(
    character: Character,
    gained: int,
    aura: int,
    rng: random.Random,
    saga: Saga | None,
    enter: bool,
) -> warping_rules.TwilightResult:
    """The roll to resist Vituperation and, failing it, the ordeal (RoP:
    The Infernal p. 95). His Confidence Points come at once; the Score's
    rise waits on the ordeal and its Aging roll, so the Diary says it."""
    notes: list[str] = []
    botched = False
    if enter:
        notes.append("The infernalist accepts Vituperation without the roll.")
    else:
        mine = dice.stress_die(rng, 1, saga=saga)
        theirs = dice.stress_die(rng, 0, saga=saga).value
        resist = infernalists.avoid_total(character) + mine.value
        against = infernalists.against_total(character, gained, aura) + theirs
        botched = mine.botched
        notes.append(
            f"Resisting Vituperation: {resist} (Stamina + Concentration + "
            f"Confidence) against {against} (Hierarchy "
            f"{infernalists.hierarchy(character)}, aura {aura})"
            + (" (botched)" if botched else "")
            + "."
        )
        if not botched and resist >= against:
            notes.append("He masters the forces in two minutes.")
            return warping_rules.TwilightResult(False, notes=notes)
    score = character.aging.warping_score
    time, seasons = warping_rules.time_for_score(score, rng, saga)
    notes.append(
        f"Torn away as if in Hell for {time}; then an Aging roll adding his "
        f"Warping Score ({score}), with no Longevity Ritual (last year's Living "
        "Conditions if it lasted a season or less)."
    )
    notes.append(confidence_due(character, gained, botched=botched))
    _, points = infernalists.confidence_after(character, gained, botched=botched)
    character.background.confidence_points += points
    return warping_rules.TwilightResult(True, time=time, seasons=seasons, notes=notes)


#: A Faerie Calling's Ease Factors are three times the Warping Score less
#: or plus something.
CALLING_FACTOR = 3


def good_calling_rank(score: int, total: int) -> int:
    """The lowest Faerie Rank for which a Calling's total beats 3 x
    (Warping Score - Faerie Rank)."""
    return math.floor(score - total / CALLING_FACTOR) + 1


def faerie_calling(
    character: Character,
    gained: int,
    aura: int,
    rng: random.Random,
    saga: Saga | None,
    enter: bool,
) -> warping_rules.TwilightResult:
    """A Faerie Calling (RoP: Faerie p. 120): the Ease Factor to act while
    it lasts, and the roll that resolves it, read against Faerie Rank."""
    stats = character.characteristics
    score = character.aging.warping_score
    act = CALLING_FACTOR * (score + gained)
    die = dice.stress_die(rng, 1, saga=saga)
    total = stats.perception + ability_level(character, "Concentration") + die.value
    rank = good_calling_rank(score, total)
    notes = [
        "Faerie Calling: dazed until the scene ends; to act, Perception + "
        f"Awareness + stress die against {act}.",
        "When the dream is played out (about fifteen minutes): Perception + "
        f"Concentration + stress die {total}"
        + (" (botched)" if die.botched else "")
        + f" against 3 x (Warping Score {score} - Faerie Rank). With a Faerie Rank of {rank} or more it is a good "
        "Calling (a new +1 Sympathy Trait, or +1 to a fitting one); otherwise "
        "a bad one (-1). Rank 10 or more on a good one, or -10 or less on a "
        "bad one, and he becomes a faerie for good.",
    ]
    held = faerie_sympathy.faerie_rank(character.personality_traits)
    if held is not None:
        notes.append(
            f"His Sympathy Traits make his Faerie Rank {held:+d}: a "
            + ("good" if held >= rank else "bad")
            + " Calling."
        )
    return warping_rules.TwilightResult(True, time="a scene", notes=notes)


RESPONSES: dict[str, Response] = {
    MAGIC: _twilight,
    DIVINE: divine_ascent,
    INFERNAL: vituperation,
    FAERIE: faerie_calling,
}


def respond(
    realm: str,
    character: Character,
    gained: int,
    aura: int,
    rng: random.Random,
    saga: Saga | None = None,
    *,
    enter: bool = False,
) -> warping_rules.TwilightResult:
    """The realm's answer to `gained` points at once, already added."""
    return RESPONSES[realm](character, gained, aura, rng, saga, enter)


# ---------------------------------------------------------------------------
# Leaving Faerie

#: How long each day in Faerie lasts in the mundane world, by fable score
#: (7 and more: a year), as (its name, hours).
_HOUR, _DAY = 1, 24
_WEEK, _MONTH, _SEASON, _YEAR = 7 * _DAY, 30 * _DAY, 91 * _DAY, 365 * _DAY
FABLE_DAYS: tuple[tuple[str, int], ...] = (
    ("an hour", _HOUR),
    ("12 hours", 12 * _HOUR),
    ("a day", _DAY),
    ("three days", 3 * _DAY),
    ("a week", _WEEK),
    ("a month", _MONTH),
    ("a season", _SEASON),
    ("a year", _YEAR),
)
_UNITS: tuple[tuple[str, int], ...] = (
    ("year", _YEAR),
    ("month", _MONTH),
    ("week", _WEEK),
    ("day", _DAY),
    ("hour", _HOUR),
)


@dataclass(frozen=True)
class FaerieReturn:
    """A return from Faerie: the effective fable score, how long each day
    there lasted, and how long passed in all."""

    effective: int
    each_day: str
    passed: str
    hours: int


def _span(hours: int) -> str:
    for name, size in _UNITS:
        if hours >= size:
            count = hours // size
            return f"{'about ' if hours % size else ''}{count} {name}" + (
                "s" if count > 1 else ""
            )
    return "no time"


def leaving_faerie(days: int, fable: int, taken: int = 0) -> FaerieReturn:
    """The mundane time `days` in Faerie took at a final fable score of
    `fable`, with `taken` Warping Points taken on leaving."""
    effective = max(0, fable - max(0, taken))
    each_day, hours = FABLE_DAYS[min(effective, len(FABLE_DAYS) - 1)]
    total = max(0, days) * hours
    return FaerieReturn(effective, each_day, _span(total), total)


def matching_points(fable: int, effective: int) -> int:
    """The Warping Points a traveller with fable score `fable` takes to
    leave with a group at the lowest effective score, `effective`."""
    return max(0, fable - effective)


def leaving_note(days: int, fable: int, taken: int) -> str:
    """The Diary's line for a return from Faerie."""
    back = leaving_faerie(days, fable, taken)
    return (
        f"Left Faerie after {days} day(s) at fable score {fable}, taking "
        f"{taken} Warping Point(s): effective fable score {back.effective}, "
        f"each day lasted {back.each_day}, {back.passed} in the mundane world. "
        "No Twilight from these points; a group leaving together takes the "
        "lowest effective score (RoP: Faerie p. 30)."
    )


# ---------------------------------------------------------------------------
# Instant travel

#: An instant transport of this level or more is a powerful effect.
POWERFUL_LEVEL = 30


def transit_points(
    level: int,
    *,
    designed_for: bool = False,
    cast_by_target: bool = False,
    portal: bool = False,
) -> int:
    """The Warping Point one transit gives the one carried: 1 for an
    effect of level 30+, none when they cast it or it was made for them,
    and none through a Hermes' or Mercere's Portal."""
    if portal or designed_for or cast_by_target or level < POWERFUL_LEVEL:
        return 0
    return 1


def transits_note(transits: int) -> str:
    """The Diary's line for Warping from instant transport."""
    return (
        f"{transits} instant transit(s), a Warping Point each (TME p. 114): "
        "each is its own event, so none brings Twilight."
    )
