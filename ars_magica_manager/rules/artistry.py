"""Artists (Art & Academe, Chapter Eight: Artists, pp. 123-135), as plain
rules: a work of art's Aesthetic Quality and the time it takes, an
artist's experimentation, the Artist Reputation and what it brings,
finding and keeping a sponsor, performing, art made by magic, a maestro's
magic instilled in his art, and the legendary artist.

- Aesthetic Quality (pp. 123-124): Dexterity + Craft for a piece
  produced, Communication + Profession for one performed (a poet's Craft:
  Poetry with Communication), + bonuses: Free Expression +3 (DE p. 82: +3
  on every roll to create a new work of art) and Inspirational +3, each;
  Puissant (Ability) +2; twice the time +1; overtime +1 and an Aging roll
  when the piece is done; a third of Artes Liberales (rounded up) for a
  piece using a liberal art; a muse's sacrificed Might, +1 per 5; a
  maestro or legendary artist working in an aura of his own realm, the
  aura / 5 (rounded up); Hermetic Inclination's Form Bonus (p. 134: the
  Form / 5, rounded up, DE p. 206); Life-Linked Art's self-inflicted
  wound, +1 Light, +3 Medium, +6 Heavy (p. 134); Artist Reputation 10,
  +3 (p. 127). Experimenting adds a simple die / 2 (rounded up) and rolls
  a stress die on the Artist Experimentation Results table. Halving the
  time halves the Aesthetic Quality (rounded down, the default).
- Time (pp. 124-125): a season's piece, two small pieces in a season, a
  year's piece, a castle or church a year per Size point, a cathedral ten
  years per Size point; times the Aesthetic Quality / 10, rounded up.
  Assistants, no more than his Leadership, each take 3.5 days off a
  season's piece, a week off a year's and a month off a decades' one, to
  no less than half the time; halving it (and assistants after) to no
  less than a quarter. Prolific Artist takes a quarter off, and allows no
  assistants (p. 134).
- Artist Reputation (pp. 126-127): named for the Craft or Profession,
  rising as an Ability, by its own experience only. The app keeps it as
  one score with City & Guild's (Craft) Reputation of the same trade (C&G
  p. 74), which both books' xp sources feed: its reading, not either
  book's. A season creating a
  piece of Aesthetic Quality over three times the Reputation earns 1 xp;
  the table of other gains and losses is REPUTATION_EVENTS. From 6, +1
  to impress socially per point over 5; 7 attracts a minor muse; 8 signs
  his work and gains a Confidence point; 9 attracts a major muse; 10 +3
  to every piece and no more losses (but truly deplorable deeds cost a
  simple die of whole points); 11 the muse takes him: a legendary artist.
- A muse (p. 129): minor up to Might 15 (sacrifices 5), major up to 30
  (sacrifices 15); the bond gives 1 Warping Point a year (3 a major one).
- A legendary artist (p. 129): Might twice his highest Craft or
  Profession, that many powers, none of a magnitude above the
  Characteristic his art uses.
- Performing (p. 125), in abnormal conditions: Communication or Dexterity
  + Profession + a stress die against the Aesthetic Quality / 2.
- Studying a piece (p. 126): its Aesthetic Quality / 2 as the source.
- A sponsor (pp. 130-132): a season; Communication + Bargain + Artist
  Reputation + a stress die against 12 + SPONSOR_MODIFIERS + the sponsor's
  social Virtue + his highest business or social Reputation; +3 for
  asking the same sponsor again, +3 after a Perception + Folk Ken roll of
  12 to pick him. Which sponsors a Reputation needs is SPONSOR_NEEDS. A
  season off a piece loses the sponsor on a simple die of 6 or more. A
  character sponsoring pays at least a Mythic Pound per point of Artist
  Reputation for a season's piece.
- Art made by magic (p. 132): Intelligence + Finesse, -6 when an artist
  makes several in a season, -9 a season's piece, -12 a year's, -15 a
  longer one; no artist can study it.
- A maestro's magic (pp. 134-135): with Hermetic Inclination in (Form), a
  Personal, constant spell-like effect of that Form, no requisites,
  instilled as the piece is made: Dexterity + Craft + Form (Communication
  + Profession for a performer) + the aura's realm interaction, the
  points over the effect's level each season, until they reach it; a
  Fatigue level per 10 levels (rounded up) lost while he works on it.

The errata (pp. 12, 61) correct nothing on these pages.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import ArtworkPlan, Character, ScoredTrait
from . import confidence, derived, realms
from .lab import ability_score
from .rounding import round_down, round_up
from .scores import ability_level

SOURCE = "Art & Academe, Chapter Eight: Artists, pp. 123-135"
MAGIC_SOURCE = "Art & Academe, Chapter Eight: Artists, Art and Magic, p. 132"

FREE_EXPRESSION = "vf_free_expression"
INSPIRATIONAL = "vf_inspirational"
MAESTRO = "vf_maestro"
INCLINATION = "vf_hermetic_inclination_in_form"
LIFE_LINKED = "vf_life_linked_art"
PROLIFIC = "vf_prolific_artist"
ARTISTIC_RENOWN = "vf_artistic_renown"

VIRTUE_BONUS = 3
DOUBLE_TIME_BONUS = 1
OVERTIME_BONUS = 1
#: A third of Artes Liberales, rounded up.
LIBERAL_ARTS_DIVISOR = 3
#: +1 for each 5 points of Might a muse sacrifices.
MUSE_MIGHT_PER_POINT = 5
AURA_DIVISOR = 5
WOUND_BONUS = {"Light": 1, "Medium": 3, "Heavy": 6}
#: Artist Reputation 10's bonus to every piece.
PINNACLE = 10
PINNACLE_BONUS = 3
QUALITY_PER_STEP = 10

#: A piece's base time in days, and what each assistant takes off it,
#: by the base (models.ARTWORK_BASES). A season is 13 weeks.
SEASON_DAYS = 91
YEAR_DAYS = 4 * SEASON_DAYS
BASE_DAYS = {
    "season": SEASON_DAYS,
    "pair": SEASON_DAYS,
    "year": YEAR_DAYS,
    "years": YEAR_DAYS,
    "decades": 10 * YEAR_DAYS,
}
ASSISTANT_DAYS = {
    "season": 3.5,
    "pair": 3.5,
    "year": 7,
    "years": 7,
    "decades": 30,
}
BASE_LABELS = {
    "season": "a season's piece (a mural, portrait, tapestry, romance, song...)",
    "pair": "two small pieces in a season (two poems, songs or brooches)",
    "year": "a year's piece (a stone façade, an ornate reliquary)",
    "years": "a castle or church: a year per Size point",
    "decades": "a cathedral: ten years per Size point",
}

#: The Artist Experimentation Results table (p. 124): (highest roll,
#: result key); a botch is a disaster, 11+ the artist praised.
EXPERIMENT_TABLE: tuple[tuple[int, str], ...] = (
    (4, "ruined"),
    (6, "disparaged"),
    (8, "no_effect"),
    (10, "work_praised"),
)
EXPERIMENT_TEXT = {
    "disaster": "Disaster: the work is destroyed and he is hurt; the Artist "
    "Reputation drops a whole point (several botches may give a Minor General "
    "Flaw: Lame, Missing Eye, Disfigured...)",
    "ruined": "The work is ruined",
    "disparaged": "Reputation disparaged: the work loses 1 Quality and the Artist "
    "Reputation a whole point",
    "no_effect": "No ill effects: the bonus stands",
    "work_praised": "Artwork praised: xp in the Artist Reputation equal to its "
    "Aesthetic Quality",
    "artist_praised": "Artist praised: enough xp to raise the Artist Reputation a "
    "whole level",
}

#: Gains and losses of Artist Reputation xp (p. 126): key -> (label, xp);
#: None is an amount the troupe gives (a muse's or creature's Might, an
#: instructor's Reputation, a piece's Aesthetic Quality).
REPUTATION_EVENTS: dict[str, tuple[str, int | None]] = {
    "craft_raised": ("Raised the Craft or Profession", 1),
    "benefactor": ("Gained a benefactor", 3),
    "patron": ("Gained a patron", 6),
    "muse": ("Attracted a muse (its Might's magnitude)", None),
    "feast": ("Hosted a feast or event, giving up a season", 1),
    "became_patron": ("Became patron to a younger artist", 1),
    "travelled": ("Travelled to a distant country to study its art", 1),
    "studied_master": (
        "Studied with an artist 2 or more higher (his Reputation, once)",
        None,
    ),
    "studied_creature": ("Studied with a supernatural creature (its magnitude)", None),
    "adventure": ("An adventure that broadcast his skill", 1),
    "lost_patron": ("Lost a patron", -12),
    "abandoned_work": (
        "Ruined or abandoned a piece experimenting (its Aesthetic Quality)",
        None,
    ),
    "barred": ("Excommunicated, exiled or barred from a society", -15),
    "signed_early": ("Signed a piece without Reputation 8", -10),
    "below_quality": ("Made a below-quality piece on purpose", -5),
}
#: The events whose amount the troupe gives, and whether it is a loss.
TYPED_EVENTS = {
    "muse": False,
    "studied_master": False,
    "studied_creature": False,
    "abandoned_work": True,
}

SOCIAL_FROM = 6
MINOR_MUSE_AT = 7
SIGN_AT = 8
MAJOR_MUSE_AT = 9
LEGENDARY_AT = 11
MINOR_MUSE_MIGHT = 15
MAJOR_MUSE_MIGHT = 30
MINOR_MUSE_GIFT = 5
MAJOR_MUSE_GIFT = 15
MINOR_MUSE_WARPING = 1
MAJOR_MUSE_WARPING = 3

SPONSOR_EASE = 12
#: The kind of sponsorship asked for (p. 131): key -> (label, Ease change).
SPONSOR_KINDS: dict[str, tuple[str, int]] = {
    "benefactor": ("A benefactor (one piece)", -3),
    "second": ("A benefactor's second piece", 3),
    "more": ("A benefactor's pieces past two", 6),
    "patron": ("A benefactor to become his patron", 9),
    "new_patron": ("A patron", 0),
}
#: The sponsor's Social Status Virtue (p. 131).
SPONSOR_STATUS: dict[str, tuple[str, int]] = {
    "free": ("A free Social Virtue", 0),
    "minor": ("A Minor Social Virtue", 3),
    "major": ("A Major Social Virtue", 6),
}
SPONSOR_REPEAT_BONUS = 3
SPONSOR_SCOUT_BONUS = 3
SCOUT_EASE = 12
#: A sponsor abandons an artist who takes a season off on this simple die.
ABANDON_ON = 6
#: The Artist Reputation xp a new sponsor gives (p. 126).
SPONSOR_XP = {"benefactor": 3, "second": 0, "more": 0, "patron": 6, "new_patron": 6}

#: Art made by magic: the penalty by how long the piece would take.
MAGIC_PENALTY = {"pair": -6, "season": -9, "year": -12, "years": -15, "decades": -15}

FATIGUE_PER_LEVELS = 10


# -- Aesthetic Quality -------------------------------------------------------


@dataclass(frozen=True)
class Aesthetic:
    """A work of art's Aesthetic Quality and each term of it."""

    quality: int
    terms: tuple[str, ...]


def performed(craft: str) -> bool:
    """Whether a piece made with `craft` is performed (Communication): a
    Profession, or Craft: Poetry (p. 123)."""
    return craft.startswith("Profession") or craft == "Craft: Poetry"


def characteristic_name(craft: str, chosen: str = "") -> str:
    """The Characteristic a piece uses: the one chosen, else Communication
    for a performance, Dexterity for a piece produced."""
    return chosen or ("communication" if performed(craft) else "dexterity")


def _ids(character: Character) -> set[str]:
    return {vf.vf_id for vf in character.virtues_flaws}


def is_maestro(character: Character) -> bool:
    return MAESTRO in _ids(character)


def inclination_form(character: Character) -> str:
    """The Form of the character's Hermetic Inclination ("" for none)."""
    return next(
        (
            vf.params.get("form", "")
            for vf in character.virtues_flaws
            if vf.vf_id == INCLINATION
        ),
        "",
    )


def base_quality(
    character: Character, craft: str, characteristic: str = ""
) -> Aesthetic:
    """The Characteristic + the Craft or Profession (+ Puissant) + Free
    Expression and Inspirational: what every piece he makes starts from."""
    name = characteristic_name(craft, characteristic)
    score = getattr(character.characteristics, name, 0)
    level, puissant = ability_score(character, craft)
    terms = [f"{name.title()} {score:+d}", f"+ {craft} {level}"]
    total = score + level
    if puissant:
        terms.append(f"+ Puissant {puissant}")
        total += puissant
    ids = _ids(character)
    for vf_id, label in (
        (FREE_EXPRESSION, "Free Expression"),
        (INSPIRATIONAL, "Inspirational"),
    ):
        if vf_id in ids:
            terms.append(f"+ {label} {VIRTUE_BONUS}")
            total += VIRTUE_BONUS
    return Aesthetic(total, tuple(terms))


def aligned_aura_bonus(
    character: Character, plan: ArtworkPlan, reputation: int = 0
) -> int:
    """The aura / 5 (rounded up), for a maestro or a legendary artist (an
    Artist Reputation of 11) working in an aura of the realm his nature
    is aligned with (p. 124); never the aura itself, and nothing for
    anyone else. Grifo's mural in a Divine aura 3 is 19 by this rule: the
    book's example (p. 134) leaves the +1 out."""
    special = is_maestro(character) or reputation >= LEGENDARY_AT
    if not (special and plan.realm and plan.aura > 0):
        return 0
    if plan.aura_realm != plan.realm:
        return 0
    return round_up(plan.aura / AURA_DIVISOR)


def aesthetic_quality(
    character: Character,
    craft: str,
    plan: ArtworkPlan,
    *,
    characteristic: str = "",
    reputation: int = 0,
    other: int = 0,
    experiment_die: int = 0,
) -> Aesthetic:
    """The piece's Aesthetic Quality with every bonus the plan takes;
    `experiment_die` is the simple die an experiment rolled (0: none
    yet)."""
    start = base_quality(character, craft, characteristic)
    terms, total = list(start.terms), start.quality

    def add(label: str, amount: int) -> None:
        nonlocal total
        if amount:
            terms.append(f"{'+' if amount > 0 else '-'} {label} {abs(amount)}")
            total += amount

    add("twice the time", DOUBLE_TIME_BONUS if plan.double_time else 0)
    add("overtime", OVERTIME_BONUS if plan.overtime else 0)
    if plan.liberal_arts:
        add(
            "Artes Liberales / 3",
            round_up(
                ability_level(character, "Artes Liberales") / LIBERAL_ARTS_DIVISOR
            ),
        )
    add("a muse's Might", round_down(max(0, plan.muse_might) / MUSE_MIGHT_PER_POINT))
    add("aligned aura", aligned_aura_bonus(character, plan, reputation))
    form = inclination_form(character)
    if form:
        add(f"{form} Form Bonus", derived.form_bonus(character, form))
    if LIFE_LINKED in _ids(character):
        add(f"{plan.wound} wound", WOUND_BONUS.get(plan.wound, 0))
    add("Artist Reputation 10", PINNACLE_BONUS if reputation >= PINNACLE else 0)
    add("other", other)
    if plan.experiment and experiment_die:
        add("experiment", round_up(experiment_die / 2))
    if plan.rushed:
        halved = round_down(total / 2)
        terms.append(f"halved for half the time: {halved}")
        total = halved
    return Aesthetic(total, tuple(terms))


# -- time --------------------------------------------------------------------


@dataclass(frozen=True)
class CreationTime:
    """How long a piece takes: its days, the seasons that means, and why."""

    days: float
    seasons: int
    notes: tuple[str, ...]


def most_assistants(character: Character) -> int:
    """His Leadership (with Puissant): as many assistants as he may use."""
    level, bonus = ability_score(character, "Leadership")
    return max(0, level + bonus)


def creation_time(
    character: Character, plan: ArtworkPlan, quality: int
) -> CreationTime:
    """The time to make a piece of Aesthetic Quality `quality` (its full
    quality, before halving the time)."""
    base = BASE_DAYS.get(plan.base, SEASON_DAYS)
    if plan.base in ("years", "decades"):
        base *= max(1, plan.size)
    steps = max(1, round_up(quality / QUALITY_PER_STEP))
    normal = base * steps
    notes = [f"{steps} x the base time for Aesthetic Quality {quality}"]
    days = float(normal)
    if PROLIFIC in _ids(character):
        days *= 0.75
        notes.append("Prolific Artist: a quarter less, no assistants")
    floor = normal / 2
    if plan.rushed:
        days /= 2
        floor = normal / 4
        notes.append("half the time (half the Quality)")
    helpers = (
        0
        if PROLIFIC in _ids(character)
        else min(max(0, plan.assistants), most_assistants(character))
    )
    if helpers:
        cut = helpers * ASSISTANT_DAYS.get(plan.base, 3.5)
        days = max(min(days, floor), days - cut)
        notes.append(
            f"{helpers} assistant(s): {cut:g} days off, to no less than {floor:g}"
        )
    if plan.double_time:
        days *= 2
        notes.append("twice the time")
    return CreationTime(days, max(1, round_up(days / SEASON_DAYS)), tuple(notes))


# -- experimentation ------------------------------------------------------------


def experiment_result(roll: int, botched: bool) -> str:
    """The Artist Experimentation Results row a stress die reads."""
    if botched:
        return "disaster"
    return next((key for top, key in EXPERIMENT_TABLE if roll <= top), "artist_praised")


# -- Artist Reputation --------------------------------------------------------


def trade(craft: str) -> str:
    """The trade a Craft or Profession names ("Craft: Painting" ->
    "Painting"), which names its Artist Reputation."""
    return craft.partition(":")[2].strip() or craft


def artist_reputation(character: Character, craft: str) -> ScoredTrait | None:
    """The Artist Reputation of `craft`'s trade. It is the same record as
    City & Guild's (Craft) Reputation (p. 74): one score per trade, fed by
    both books' xp sources. Neither book says the two are one Reputation;
    merging them is the app's reading."""
    name = trade(craft).casefold()
    return next(
        (
            r
            for r in character.reputations
            if r.name.casefold() == name and r.score >= 0
        ),
        None,
    )


def reputation_score(character: Character, craft: str) -> int:
    found = artist_reputation(character, craft)
    return found.score if found is not None else 0


def season_xp(quality: int, reputation: int) -> int:
    """A season creating a piece: 1 xp when its Aesthetic Quality is over
    three times the Artist Reputation."""
    return 1 if quality > 3 * reputation else 0


def xp_to_next(reputation: ScoredTrait | None) -> int:
    """The xp that raises the Reputation one whole level."""
    if reputation is None:
        return confidence.XP_PER_LEVEL
    return confidence.XP_PER_LEVEL * (reputation.score + 1) - reputation.deeds


def xp_of_a_level(reputation: ScoredTrait | None) -> int:
    """The xp that takes the Reputation down one whole level, its xp
    toward the next kept."""
    if reputation is None or reputation.score <= 0:
        return 0
    return confidence.XP_PER_LEVEL * reputation.score


def loses_nothing(reputation: int) -> bool:
    """From Artist Reputation 10 he no longer loses Reputation xp."""
    return reputation >= PINNACLE


def benefits(reputation: int) -> list[str]:
    """What an Artist Reputation brings (pp. 126-127)."""
    lines: list[str] = []
    if reputation >= SOCIAL_FROM:
        lines.append(
            f"+{reputation - SOCIAL_FROM + 1} to social rolls his renown sways "
            "(never a season's work)"
        )
    if reputation >= MINOR_MUSE_AT:
        lines.append(
            "a muse watches him"
            + (
                " (a major one: Plagued by Supernatural Entity)"
                if reputation >= MAJOR_MUSE_AT
                else " (a minor one)"
            )
        )
    if reputation >= SIGN_AT:
        lines.append("he signs his work, known throughout the land; +1 Confidence")
    if reputation >= PINNACLE:
        lines.append("+3 to every piece; Reputation xp is never lost")
    if reputation >= LEGENDARY_AT:
        lines.append("his muse takes him: a legendary artist")
    return lines


def muse_kind(might: int) -> str:
    """A muse by its Might: minor to 15, major to 30 (p. 129)."""
    if might <= MINOR_MUSE_MIGHT:
        return "minor"
    if might <= MAJOR_MUSE_MIGHT:
        return "major"
    return "too mighty"


def muse_warping(might: int) -> int:
    """The Warping Points a muse's bond gives a year."""
    return MINOR_MUSE_WARPING if muse_kind(might) == "minor" else MAJOR_MUSE_WARPING


@dataclass(frozen=True)
class Legend:
    """A legendary artist's Might, powers and their highest magnitude."""

    might: int
    powers: int
    magnitude: int


def legendary(character: Character, craft: str, characteristic: str = "") -> Legend:
    """Might twice his highest Craft or Profession, that many powers, none
    above the Characteristic his art uses (p. 129)."""
    best = max(
        (
            a.level
            for a in character.abilities
            if a.name.startswith(("Craft", "Profession"))
        ),
        default=0,
    )
    name = characteristic_name(craft, characteristic)
    return Legend(2 * best, best, max(0, getattr(character.characteristics, name, 0)))


# -- sponsors and performing --------------------------------------------------


def sponsor_ease(kind: str, status: str, sponsor_reputation: int) -> int:
    """The Ease Factor to win a sponsor."""
    return (
        SPONSOR_EASE
        + SPONSOR_KINDS[kind][1]
        + SPONSOR_STATUS[status][1]
        + max(0, sponsor_reputation)
    )


def sponsor_total(character: Character, craft: str) -> int:
    """Communication + Bargain + Artist Reputation."""
    level, bonus = ability_score(character, "Bargain")
    return (
        character.characteristics.communication
        + level
        + bonus
        + reputation_score(character, craft)
    )


def scout_total(character: Character) -> int:
    """Perception + Folk Ken, to pick the likeliest sponsor."""
    level, bonus = ability_score(character, "Folk Ken")
    return character.characteristics.perception + level + bonus


def sponsor_needs(reputation: int) -> str:
    """The sponsor an Artist Reputation needs (p. 131)."""
    if reputation >= SIGN_AT:
        return (
            "a patron (no benefactors) with a Major Social Status Virtue and "
            "Wealthy or a business or social Reputation of 4"
        )
    if reputation >= SOCIAL_FROM:
        return (
            "a business or social Reputation of 3 and a Minor Social Status "
            "Virtue; or a Minor one and Wealthy; or a Major one"
        )
    if reputation >= 4:
        return "a business or social Reputation of 2 or more"
    return "anyone with money to spare"


def sponsor_cost(reputation: int, seasons: int = 1) -> int:
    """At least a Mythic Pound per point of Artist Reputation for a
    season's piece (more for a longer one, troupe's call: x seasons)."""
    return max(1, reputation) * max(1, seasons)


def performance_ease(quality: int) -> int:
    """A performance in abnormal conditions: against Aesthetic Quality / 2."""
    return round_down(quality / 2)


def performance_total(
    character: Character, craft: str, characteristic: str = ""
) -> int:
    name = characteristic_name(craft, characteristic)
    level, bonus = ability_score(character, craft)
    return getattr(character.characteristics, name, 0) + level + bonus


def study_quality(quality: int) -> int:
    """A piece studied by an artist of its Craft: Aesthetic Quality / 2."""
    return round_down(quality / 2)


def magical_quality(character: Character, base: str) -> int:
    """Art made by magic: Intelligence + Finesse less the base's penalty."""
    level, bonus = ability_score(character, "Finesse")
    return (
        character.characteristics.intelligence
        + level
        + bonus
        + MAGIC_PENALTY.get(base, -9)
    )


# -- a maestro's magic ----------------------------------------------------------


def instill_total(character: Character, craft: str, plan: ArtworkPlan) -> int:
    """Dexterity + Craft + Form (Communication + Profession for a
    performer) + the aura's realm interaction for his realm."""
    form = inclination_form(character)
    level, bonus = ability_score(character, craft)
    name = "communication" if performed(craft) else "dexterity"
    art = character.arts.get(form.lower()) if form else None
    total = getattr(character.characteristics, name, 0) + level + bonus
    total += art.level if art is not None else 0
    if plan.realm and plan.aura_realm and plan.aura:
        total += realms.aura_modifier(plan.realm, plan.aura_realm, plan.aura)
    return total


def instill_fatigue(level: int) -> int:
    """Fatigue levels lost while he works: one per 10 levels, rounded up."""
    return round_up(max(0, level) / FATIGUE_PER_LEVELS)


def instill_problem(character: Character, craft: str, plan: ArtworkPlan) -> str | None:
    if not plan.instill_level:
        return None
    if not inclination_form(character):
        return (
            "Only a maestro with Hermetic Inclination in a Form can instill magic "
            "as he makes his art (A&A p. 135)."
        )
    if instill_total(character, craft, plan) <= plan.instill_level:
        return (
            f"His instilling total {instill_total(character, craft, plan)} doesn't "
            f"pass the effect's level {plan.instill_level} (A&A p. 135)."
        )
    return None
