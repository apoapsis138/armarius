"""The disputatio, the schoolmen's formal debate (Art & Academe, Chapter
Eight: Universities, Disputatio), settled like certamen. The opponent
states first; the respondent replies, then states in turn, and the
opponent replies: one exchange, for each of the judge's questions
(usually 7, 9 or 12):

    Attack     = Communication + Ability + stress die
    Defence    = Perception + Ability + stress die
    Advantage  = Attack - Defence (when the Attack is higher)
    Weakening  = Intelligence + Advantage
    Resistance = Presence + highest positive Academic Reputation

The Ability is the subject's: Artes Liberales, Philosophiae, Theology or
Civil and Canon Law. A Weakening Total above the Resistance costs the
defender a symbolic Fatigue level for each 5 points or part of 5 by which
it does (as certamen does); the levels lost are penalties to the rolls,
and five of them lose the disputatio. Otherwise, when the questions run
out, the side that lost fewer wins (the same: a draw). A judge may set an
Ease Factor (6 among students, 9 baccalaureates, 12 a candidate's
examination) that an Attack must reach, or the statement is wasted.

Afterwards each disputer rolls Stamina + stress die against the number
of exchanges: a failure loses a real Long-Term Fatigue level, and a
botch one more for each 0 on the botch dice.

The winner of an epideictic or deliberative disputatio gains an
experience point toward a Good Academic Reputation, or gives the loser
one toward a Bad one (no more than once a season); the winner of a
forensic one proves his case.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..models import Character
from . import debate, dice, work_virtues
from .lab import ability_score
from .rounding import round_up

SOURCE = (
    "Art & Academe, Chapter Eight: Universities, Disputatio "
    "(https://www.redcap.org/page/Art_%26_Academe)"
)

SUBJECTS = (
    "Artes Liberales",
    "Philosophiae",
    "Theology: Christian",
    "Theology: Islam",
    "Theology: Judaism",
    "Civil and Canon Law",
)
KINDS = ("epideictic", "deliberative", "forensic")
DEFAULT_EXCHANGES = 9
MAX_EXCHANGES = 12
KNOCKED_OUT = 5
#: The penalty for disputing Gifted before a crowd.
GIFT_BEFORE_CROWD = -3

#: Virtues and Flaws: (the total they change, how much, the kind of
#: disputatio they need, or "" for any).
VIRTUES: dict[str, tuple[str, int, str]] = {
    "vf_afflicted_tongue": ("attack", -2, ""),
    "vf_incomprehensible": ("attack", -6, ""),
    "vf_good_teacher": ("attack", 3, "deliberative"),
    "vf_inspirational": ("attack", 3, "epideictic"),
    "vf_short_attention_span": ("defence", -3, ""),
    "vf_piercing_gaze": ("weakening", 3, ""),
    "vf_strong_willed": ("resistance", 3, ""),
    "vf_poor_disputer": ("die", -3, ""),
}
ARISTOTELIAN = "vf_aristotelian_training"
CLEAR_THINKER = "vf_clear_thinker"
ENFEEBLED = "vf_enfeebled"
GIFTED = ("vf_the_gift", "vf_blatant_gift")
GENTLE_GIFT = "vf_gentle_gift"


@dataclass(frozen=True)
class Disputer:
    """What a disputer brings, each total's fixed part worked out."""

    name: str
    attack: int
    defence: int
    intelligence: int
    weakening: int
    resistance: int
    #: Added to every die roll (Poor Disputer, the Gift before a crowd).
    die: int = 0
    clear_thinker: bool = False
    enfeebled: bool = False
    stamina: int = 0
    #: What each Virtue and Flaw counted adds, for the form's line.
    counted: list[str] = field(default_factory=list)


def academic_reputation(character: Character) -> int:
    """The character's highest positive Academic Reputation (0 for none)."""
    return max([0, *(r.score for r in character.reputations if r.type == "Academic")])


def subject_score(character: Character, subject: str) -> int:
    """The subject's Ability (Puissant counted), with Academic
    Concentration's logic or rhetoric when the subject is Artes
    Liberales."""
    score = sum(ability_score(character, subject))
    if subject == "Artes Liberales":
        score += sum(
            n
            for _, n in work_virtues.artes_liberales(character, debate.DEBATE_SUBJECTS)
        )
    return score


def disputer(
    character: Character, subject: str, kind: str, *, crowd: bool = False
) -> Disputer:
    """`character` disputing `subject` in a disputatio of `kind`; `crowd`:
    before a crowd, where the Gift costs 3 on each roll."""
    c = character.characteristics
    ability = subject_score(character, subject)
    ids = {vf.vf_id for vf in character.virtues_flaws}
    totals = {"attack": 0, "defence": 0, "weakening": 0, "resistance": 0, "die": 0}
    counted: list[str] = []
    for vf_id, (total, amount, needs) in VIRTUES.items():
        if vf_id in ids and (not needs or needs == kind):
            totals[total] += amount
            counted.append(f"{_label(vf_id)} {amount:+d} {total}")
    if ARISTOTELIAN in ids:
        for total in ("attack", "defence", "weakening", "resistance"):
            totals[total] += 1
        counted.append("Aristotelian Training +1 each total")
    if crowd and _off_putting(character, ids):
        totals["die"] += GIFT_BEFORE_CROWD
        counted.append(f"The Gift before a crowd {GIFT_BEFORE_CROWD:+d} each roll")
    return Disputer(
        character.name,
        attack=c.communication + ability + totals["attack"],
        defence=c.perception + ability + totals["defence"],
        intelligence=c.intelligence,
        weakening=totals["weakening"],
        resistance=c.presence + academic_reputation(character) + totals["resistance"],
        die=totals["die"],
        clear_thinker=CLEAR_THINKER in ids,
        enfeebled=ENFEEBLED in ids,
        stamina=c.stamina,
        counted=counted,
    )


def _off_putting(character: Character, ids: set[str]) -> bool:
    """Whether the character's Gift unsettles a crowd (a Gentle Gift
    doesn't)."""
    gifted = character.type == "magus" or bool(ids & set(GIFTED))
    return gifted and GENTLE_GIFT not in ids


def _label(vf_id: str) -> str:
    return vf_id.removeprefix("vf_").replace("_", " ").title()


def levels_lost(weakening: int, resistance: int) -> int:
    """Symbolic Fatigue levels a Weakening Total costs: one for each 5
    points (or part of 5) by which it beats the Resistance Total."""
    if weakening <= resistance:
        return 0
    return round_up((weakening - resistance) / 5)


@dataclass
class Disputatio:
    """A disputatio worked out exchange by exchange: the levels each side
    lost (the opponent's first), the exchanges it ran and a line for
    each statement."""

    lost: list[int]
    exchanges: int
    lines: list[str]

    @property
    def winner(self) -> int | None:
        """0 the opponent, 1 the respondent, None a draw."""
        if self.lost[0] == self.lost[1]:
            return None
        return 0 if self.lost[0] < self.lost[1] else 1


def _roll(rng: random.Random) -> int:
    die = dice.stress_die(rng)
    return 0 if die.botched else die.value


def _modifier(side: Disputer, lost: int, exchange: int) -> int:
    """What a side adds to a roll in `exchange` (from 1): its fixed die
    modifier, its levels' penalty, and Enfeebled's -1 an exchange after
    the first."""
    tired = side.enfeebled and exchange > 1
    return (
        side.die
        + debate.fatigue_penalty(lost, side.clear_thinker)
        - (exchange - 1 if tired else 0)
    )


def run(
    sides: tuple[Disputer, Disputer],
    exchanges: int,
    rng: random.Random,
    ease: int = 0,
) -> Disputatio:
    """Dispute `exchanges` questions, or until a side has lost five
    levels: the opponent (sides[0]) states first in each."""
    lost = [0, 0]
    lines: list[str] = []
    played = 0
    for number in range(1, max(1, exchanges) + 1):
        played = number
        said = [
            _statement(sides, attacker, lost, number, rng, ease) for attacker in (0, 1)
        ]
        lines.append(f"{number}. " + " ".join(s for s in said if s))
        if KNOCKED_OUT in lost:
            break
    return Disputatio(lost, played, lines)


def _statement(
    sides: tuple[Disputer, Disputer],
    attacker: int,
    lost: list[int],
    number: int,
    rng: random.Random,
    ease: int,
) -> str:
    """One side's statement and the other's reply in question `number`,
    as a line's half ("" once the disputatio is over); `lost` is updated."""
    if KNOCKED_OUT in lost:
        return ""
    defender = 1 - attacker
    a, d = sides[attacker], sides[defender]
    attack = a.attack + _modifier(a, lost[attacker], number) + _roll(rng)
    if ease and attack < ease:
        return f"{a.name} {attack}: short of {ease}, unanswered."
    defence = d.defence + _modifier(d, lost[defender], number) + _roll(rng)
    if attack <= defence:
        return f"{a.name} {attack}, {d.name} answers {defence}."
    weakening = a.intelligence + a.weakening + attack - defence
    hit = levels_lost(weakening, d.resistance)
    lost[defender] = min(KNOCKED_OUT, lost[defender] + hit)
    return (
        f"{a.name} {attack} beats {defence}: Weakening {weakening} v "
        f"{d.resistance}, {d.name} -{hit}."
    )


def over_exertion(
    side: Disputer, exchanges: int, rng: random.Random
) -> tuple[int, int]:
    """The over-exertion check afterwards: (its total, Long-Term Fatigue
    levels lost). Stamina + stress die against the exchanges; a failure
    loses one level, a botch one more for each 0 on the botch dice."""
    die = dice.stress_die(rng)
    total = side.stamina + die.value
    if die.botched:
        return total, 1 + die.botches
    return total, 0 if total >= exchanges else 1


def reward(kind: str, winner: str, loser: str) -> str:
    """What winning gives, as a line for the Diary."""
    if kind == "forensic":
        return f"{winner} proves the case."
    return (
        f"{winner} gains an experience point toward a Good Academic "
        f"Reputation, or gives {loser} one toward a Bad Academic Reputation "
        "(once a season at most)."
    )
