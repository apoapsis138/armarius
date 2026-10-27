"""House Acclaim, and the Reputation rules of the Houses that keep it.

House Bonisagus (Houses of Hermes: True Lineages pp. 21-22):

- House Acclaim is a free Reputation every magus Bonisagi has from
  character creation; it matters only within the House. It grows like an
  Ability (5, 15, 30 and 50 Acclaim points for scores 1 to 4), from
  finished research made public: the Research and Acclaim Points table.
  A Lab Text or tractatus taken into a folio earns twice its points. The
  word takes a year per Acclaim point gained to spread.
- The scores are the ranks: 1 boukoloi, 2 daduchos, 3 cannophori, 4
  dendrophori; a magus fresh from his Gauntlet has none, and the Primus
  is above them.
- A magus Bonisagi adds his House Acclaim to social rolls with magi of
  House Bonisagus (as a rule of thumb, any roll with Presence), and to
  Intrigue or Guile rolls resisting a maga Trianomae's influence, but
  never to Presence in certamen.
- He may add it to the season's roll to find an apprentice (Perception +
  stress die): it is added to that roll, not a roll of its own. A success
  finds one as normal; a failure still finds one, taken from another
  magus by right; failing by 5 or more antagonizes that magus, who must
  be compensated; a botch makes him the Major Story Flaw Enemies. TL
  gives the success as 12+, the ArM5 corebook's Ease Factor for the
  search (p. 106); the Definitive Edition lowered that to 9 (DE p. 269),
  and the Definitive Edition wins, so the search is against 9. Since the
  bonus can only help, it is always added for a magus of rank (Acclaim 1
  or more), and his botch is TL's Enemies rather than the corebook's
  dupe (a gap-fill: TL doesn't say which botch applies).
- Trianoma's cipher: decoding a secret note takes a day, Intelligence +
  Latin + stress die, succeeding when higher than 6 + the author's
  Communication + Intrigue; having decoded one before adds 3 (p. 21).
- An argument over a folio's contents (p. 23): Presence + Leadership, or
  Communication + Artes Liberales, + House Acclaim + stress die, the
  higher total winning.
- Rediscovering one of Conciatta's Minor Virtues is worth 15 Acclaim
  points, her True Understanding of the Realms 30 (Legends of Hermes p.
  45).

House Flambeau (Houses of Hermes: Societates p. 31):

- House Acclaim is a free Hermetic Reputation, known in the whole Order,
  usually starting at 0; Famous (or another Virtue granting a good
  Reputation) may be spent on it, and the Flaw Miles gives 5 experience
  points in it.
- Deeds of prowess, valour and honour before credible witnesses are
  experience points in it (Example Acclaim Awards); ignoble ones take
  experience away, and each year without a gain costs a point. It never
  falls below 0: an ignoble act at 0 starts a bad Reputation by the
  ordinary rules (DE p. 386).
- Certamen gains or loses Acclaim only when it settles a real dispute.

House Jerbiton's leagues (Houses of Hermes: Societates p. 53): between
two magi of the same league every Reputation counts 3 higher. A random
person has heard of a Reputation when a stress die + its score equals or
beats the Ease Factor for how far away he is (DE p. 28).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from ..models import Character, Saga, ScoredTrait
from . import dice, xp
from .apprentice_seasons import SEARCH_EASE
from .confidence import add_deeds
from .reputations import HEARD_EASE
from .rounding import round_down

BONISAGUS_SOURCE = (
    "Houses of Hermes: True Lineages, House Acclaim, pp. 21-22; Legends of "
    "Hermes, Bonisagus House Acclaim, p. 45"
)
FLAMBEAU_SOURCE = "Houses of Hermes: Societates, House Acclaim, p. 31"
CIPHER_SOURCE = "Houses of Hermes: True Lineages, The Cipher of Trianoma, p. 21"
FOLIO_SOURCE = "Houses of Hermes: True Lineages, Editorial Disagreements, p. 23"
LEAGUE_SOURCE = "Houses of Hermes: Societates, League Membership, p. 53"
HEARD_SOURCE = "Ars Magica Definitive Edition, Reputations, p. 28"
SOURCE = f"{BONISAGUS_SOURCE}; {FLAMBEAU_SOURCE}; {LEAGUE_SOURCE}"

BONISAGUS = "house_bonisagus"
FLAMBEAU = "house_flambeau"
JERBITON = "house_jerbiton"
#: The Reputation's name, and who has heard of it, by House.
ACCLAIM = "House Acclaim"
HERMETIC = "Hermetic"
REACH = {BONISAGUS: "House Bonisagus", FLAMBEAU: "the Order"}
HOUSE_NAMES = {BONISAGUS: "Bonisagus", FLAMBEAU: "Flambeau"}

#: The Bonisagi's ranks by House Acclaim score (TL p. 22).
RANKS: dict[int, str] = {
    0: "no rank",
    1: "Boukoloi",
    2: "Daduchos",
    3: "Cannophori",
    4: "Dendrophori",
}


@dataclass(frozen=True)
class Award:
    """One line of an Acclaim table: what was done, as the table puts its
    worth (`rule`), and how a figure the user gives (`amount`, its label)
    turns into points: `per` for each `per_of` of it (Quality/2 is 1 per
    2), or the fixed `points` when it needs none. A storyguide's award
    picks from `least` to `most` (`sign` -1 for a loss). `folio`: a text a
    folio doubles."""

    label: str
    rule: str
    points: int = 0
    amount: str = ""
    per: int = 1
    per_of: int = 1
    least: int = 0
    most: int = 0
    sign: int = 1
    folio: bool = False


#: House Bonisagus's Research and Acclaim Points (TL p. 21), with
#: Conciatta's rediscovered breakthroughs (LoH p. 45).
RESEARCH: dict[str, Award] = {
    "tractatus": Award(
        "Write an Art tractatus", "Quality/2", amount="Quality", per_of=2, folio=True
    ),
    "summa": Award("Write an Art summa", "Level/2", amount="Level", per_of=2),
    "spell": Award(
        "Invent an original spell",
        "1 a magnitude",
        amount="Magnitude of the spell",
        folio=True,
    ),
    "experiment": Award(
        "Invent an original spell by experimentation",
        "2 a magnitude",
        amount="Magnitude of the spell",
        per=2,
        folio=True,
    ),
    "talisman": Award("Create a Talisman", "2", 2),
    "familiar": Award(
        "Bind a familiar",
        "Magic Might/5",
        amount="Magic Might of the familiar",
        per_of=5,
    ),
    "apprentice": Award("Train an apprentice", "3", 3),
    "assist": Award(
        "Assist a magus of higher rank in the lab", "1 a project", amount="Projects"
    ),
    "stabilize": Award(
        "Stabilize a breakthrough",
        "3 a magnitude",
        amount="Magnitude of the spell",
        per=3,
    ),
    "minor_breakthrough": Award("Achieve a minor breakthrough", "15", 15),
    "major_breakthrough": Award("Achieve a major breakthrough", "30", 30),
    "conciatta_minor": Award("Rediscover one of Conciatta's Minor Virtues", "15", 15),
    "conciatta_realms": Award(
        "Rediscover Conciatta's True Understanding of the Realms", "30", 30
    ),
}

#: House Flambeau's Example Acclaim Awards, in experience points (HoH:S
#: p. 31); the tournament's places are `TOURNAMENT`'s.
DEEDS: dict[str, Award] = {
    "gauntlet": Award(
        "An exceptional Gauntlet, roleplayed",
        "2 to 5",
        amount="Experience",
        least=2,
        most=5,
    ),
    "march": Award("Took part in a Wizard's March", "+1", 1),
    "won_certamen": Award("Won a certamen settling a dispute", "+1", 1),
    "won_senior": Award(
        "Won a certamen settling a dispute, against a senior magus", "+2", 2
    ),
    "tournament": Award("A magical tournament", "by its place"),
    "brave": Award(
        "Fought bravely in a Wizard's War",
        "1 to 3",
        amount="Experience",
        least=1,
        most=3,
    ),
    "won_war": Award(
        "Won a Wizard's War",
        "2 x the foe's highest Reputation",
        amount="The foe's highest Reputation",
        per=2,
    ),
    "renounced": Award(
        "Slew a renounced magus",
        "3 x his highest Reputation",
        amount="His highest Reputation",
        per=3,
    ),
    "beast": Award(
        "Slew a supernatural beast", "Might/5", amount="Its Might", per_of=5
    ),
    "primus": Award(
        "Fulfilled a direct order of the Primus (a miles)",
        "the storyguide's award",
        amount="Experience",
        least=1,
        most=99,
    ),
    "glory": Award(
        "Another glorious deed",
        "the storyguide's award",
        amount="Experience",
        least=1,
        most=99,
    ),
    "idle": Award("A year without gaining any Acclaim", "-1", -1),
    "lost_certamen": Award("Lost a certamen settling a dispute", "-1", -1),
    "lost_junior": Award(
        "Lost a certamen settling a dispute, against a junior magus", "-2", -2
    ),
    "dishonest": Award(
        "Seemed dishonest or cowardly",
        "-1 or more an incident",
        amount="Experience lost",
        least=1,
        most=99,
        sign=-1,
    ),
    "ignoble": Award(
        "Another ignoble act",
        "the storyguide's penalty",
        amount="Experience lost",
        least=1,
        most=99,
        sign=-1,
    ),
}

#: A tournament's places: (what, experience), the competing point
#: counted in each (HoH:S p. 31).
TOURNAMENT: dict[str, tuple[str, int]] = {
    "competed": ("Competed", 1),
    "finalist": ("Was a finalist", 3),
    "champion": ("Was champion", 5),
    "dismal": ("A dismal performance", -2),
}

#: A miles's experience in House Acclaim from his Flaw (HoH:S p. 31).
MILES = "vf_miles"
MILES_XP = 5
#: The good Reputation Famous gives, which a Flambeau may put in House
#: Acclaim (DE p. 80; HoH:S p. 31).
FAMOUS = "vf_famous"
FAMOUS_SCORE = 4

#: Finding an apprentice with House Acclaim (TL p. 22) is the core search
#: with the score added: the Definitive Edition's Ease Factor (DE p. 269),
#: where TL repeats the ArM5 corebook's 12.
APPRENTICE_EASE = SEARCH_EASE
ANTAGONIZED_BY = 5
#: Trianoma's cipher (TL p. 21).
CIPHER_BASE = 6
CIPHER_PRACTICE = 3
#: Every Reputation between two magi of the same league (HoH:S p. 53).
LEAGUE_BONUS = 3


# -- whose Acclaim, and where it stands --


def house_of(character: Character) -> str | None:
    """The House whose Acclaim the magus keeps: Bonisagus or Flambeau."""
    house = character.hermetic.house
    return house if house in REACH else None


def is_acclaim(reputation: ScoredTrait) -> bool:
    return reputation.name.casefold().startswith(ACCLAIM.casefold())


def acclaim_of(character: Character) -> ScoredTrait | None:
    """His House Acclaim Reputation, if he has one."""
    return next((r for r in character.reputations if is_acclaim(r)), None)


def keeps_acclaim(character: Character) -> bool:
    """Whether he has House Acclaim to record: a magus of Bonisagus or
    Flambeau, or anyone who already holds one."""
    return house_of(character) is not None or acclaim_of(character) is not None


def total_xp(reputation: ScoredTrait) -> int:
    """All the experience in a Reputation: its score's, as an Ability's,
    and the points toward the next."""
    return xp.ability_xp(abs(reputation.score)) + reputation.deeds


def rank(score: int) -> str:
    """A magus Bonisagi's rank for his House Acclaim; past Dendrophori
    there is only the Primus, who is above the ranks."""
    return RANKS.get(max(0, min(score, 4)), RANKS[0])


def start(character: Character, house: str, famous: bool = False) -> ScoredTrait:
    """His House Acclaim, started: at 0, at 4 when a Flambeau puts his
    Famous in it, with a miles's 5 experience points (HoH:S p. 31)."""
    reputation = ScoredTrait(
        ACCLAIM, FAMOUS_SCORE if famous else 0, type=HERMETIC, reach=REACH[house]
    )
    if house == FLAMBEAU and has(character, MILES):
        add_deeds(reputation, MILES_XP)
    character.reputations.append(reputation)
    return reputation


def has(character: Character, vf_id: str) -> bool:
    return any(vf.vf_id == vf_id for vf in character.virtues_flaws)


# -- what a deed or a piece of research is worth --


def worth(award: Award, amount: int | None = None, in_folio: bool = False) -> int:
    """The Acclaim points (Bonisagus) or experience (Flambeau) an award
    gives, from the figure it needs; a folio doubles a text's."""
    if not award.amount:
        points = award.points
    elif award.most:
        points = award.sign * max(award.least, min(award.most, amount or 0))
    else:
        points = award.per * round_down(max(0, amount or 0) / award.per_of)
    return 2 * points if in_folio and award.folio else points


def lose(reputation: ScoredTrait, points: int) -> int:
    """Take experience from the Reputation, lowering its score as an
    Ability's would fall, never below 0. Returns the points it couldn't
    take, the Reputation having none left."""
    total = total_xp(reputation)
    left = max(0, total - max(0, points))
    score = xp.score_from_xp(left, xp.ABILITY_FACTOR)
    reputation.score = score
    reputation.deeds = left - xp.ability_xp(score)
    return max(0, points - total)


@dataclass(frozen=True)
class Change:
    """What an award did: the points, the score before and after, and any
    bad Reputation an ignoble act at 0 started or added to."""

    points: int
    before: int
    after: int
    bad: str = ""


def bad_reputation(character: Character, name: str, points: int) -> ScoredTrait:
    """An ignoble act at 0 House Acclaim: a new bad Hermetic Reputation at
    1 (DE p. 386), or the points as experience in the one named."""
    found = next((r for r in character.reputations if r.name == name), None)
    if found is None:
        found = ScoredTrait(name, -1, type=HERMETIC)
        character.reputations.append(found)
        return found
    add_deeds(found, points)
    return found


def apply(
    character: Character, reputation: ScoredTrait, points: int, bad_name: str = ""
) -> Change:
    """Add or take away the points; at 0 an ignoble act names a bad
    Reputation instead (Flambeau)."""
    before = reputation.score
    if points >= 0:
        add_deeds(reputation, points)
        return Change(points, before, reputation.score)
    at_zero = before == 0
    lose(reputation, -points)
    bad = ""
    if at_zero and bad_name.strip():
        bad = bad_reputation(character, bad_name.strip(), -points).name
    return Change(points, before, reputation.score, bad)


# -- the rolls --


def apprentice_search(total: int, botched: bool) -> str:
    """A magus Bonisagi of rank's season of searching: the core search's
    total (Perception + stress die) with his House Acclaim added (TL p.
    22), against the Definitive Edition's Ease Factor (DE p. 269)."""
    if botched:
        return (
            "a botch: the magus he took the apprentice from is so vehement "
            "an enemy that he gains the Major Story Flaw Enemies."
        )
    if total >= APPRENTICE_EASE:
        return "a Gifted child is found, as normal (add them as a character)."
    if APPRENTICE_EASE - total >= ANTAGONIZED_BY:
        return (
            "he takes an apprentice from another magus, as is his right, "
            "and has antagonized him: he must be compensated to be placated."
        )
    return "he takes an apprentice from another magus, as is his right."


def apprentice_bonus(character: Character) -> int:
    """House Acclaim added to the apprentice search: a magus Bonisagi of
    rank's (0 for anyone else)."""
    reputation = acclaim_of(character)
    if house_of(character) != BONISAGUS or reputation is None:
        return 0
    return max(0, reputation.score)


def cipher_ease(communication: int, intrigue: int) -> int:
    """What decoding a Trianomae's note must beat (TL p. 21)."""
    return CIPHER_BASE + communication + intrigue


def cipher_bonus(intelligence: int, latin: int, decoded_before: bool) -> int:
    return intelligence + latin + (CIPHER_PRACTICE if decoded_before else 0)


@dataclass(frozen=True)
class Rolled:
    """A roll made: the modifiers, the die, the total, and what it did."""

    modifiers: int
    die: int
    botched: bool
    total: int
    said: str


def roll(
    rng: random.Random, modifiers: int, saga: Saga | None = None
) -> tuple[int, int, bool]:
    """A stress die added to `modifiers`: (die, total, botched); a botch
    totals 0 at most."""
    rolled = dice.stress_die(rng, 1, saga=saga)
    total = min(0, modifiers) if rolled.botched else modifiers + rolled.value
    return rolled.value, total, rolled.botched


def decode_cipher(
    rng: random.Random,
    bonus: int,
    ease: int,
    saga: Saga | None = None,
) -> Rolled:
    die, total, botched = roll(rng, bonus, saga)
    if botched:
        said = "a botch: the note is misread."
    elif total > ease:
        said = f"higher than {ease}: the note is decoded."
    else:
        said = f"not higher than {ease}: the cipher holds."
    return Rolled(bonus, die, botched, total, said)


def folio_argument(
    rng: random.Random, bonus: int, opponent: int, saga: Saga | None = None
) -> Rolled:
    """An argument over a folio: the higher total wins (TL p. 23)."""
    die, total, botched = roll(rng, bonus, saga)
    if botched:
        said = "a botch: the argument is lost."
    elif total > opponent:
        said = f"beats {opponent}: the argument is won."
    elif total < opponent:
        said = f"below {opponent}: the argument is lost."
    else:
        said = f"ties {opponent}: neither carries it yet."
    return Rolled(bonus, die, botched, total, said)


def heard_eases(reputation_type: str) -> list[tuple[int, str]]:
    """The distances for the Reputation's type, with their Ease Factors
    (DE p. 28): the Hermetic or Ecclesiastical column, else the Local."""
    column = {"Ecclesiastical": 1, HERMETIC: 2}.get(reputation_type, 0)
    return [
        (ease, places[column]) for ease, places in HEARD_EASE.items() if places[column]
    ]


def heard_bonus(reputation: ScoredTrait, colleague: bool) -> int:
    """What the Reputation adds to the roll: its score (a bad one's size),
    3 more between colleagues of a Jerbiton league."""
    return abs(reputation.score) + (LEAGUE_BONUS if colleague else 0)


def heard_of(
    rng: random.Random,
    reputation: ScoredTrait,
    ease: int,
    colleague: bool = False,
    saga: Saga | None = None,
) -> Rolled:
    """Has someone heard of it: a stress die + the Reputation equals or
    beats the Ease Factor; the more it beats it by, the more he knows."""
    bonus = heard_bonus(reputation, colleague)
    die, total, botched = roll(rng, bonus, saga)
    if botched:
        said = "a botch: he has heard nothing, or something wrong."
    elif total >= ease:
        said = f"meets {ease} by {total - ease}: he has heard of it."
    else:
        said = f"below {ease}: he hasn't heard of it."
    return Rolled(bonus, die, botched, total, said)


def benefits(character: Character, reputation: ScoredTrait) -> list[str]:
    """What his House Acclaim does for him, in words."""
    score = max(0, reputation.score)
    if house_of(character) == BONISAGUS:
        return [
            f"Rank: {rank(score)}.",
            f"+{score} to social rolls with magi of House Bonisagus (any "
            "Presence roll, as a rule of thumb), and to Intrigue or Guile "
            "resisting a maga Trianomae; never to Presence in certamen.",
            f"+{score} to the season's search for an apprentice (Perception "
            f"+ stress die, against {APPRENTICE_EASE}); a failure still takes "
            "one from another magus.",
            "The word spreads a year for each Acclaim point gained.",
        ]
    if house_of(character) == FLAMBEAU:
        return [
            f"A Hermetic Reputation of {score}, known in the whole Order.",
            "Each year without a gain costs a point; it never falls below 0.",
        ]
    return []
