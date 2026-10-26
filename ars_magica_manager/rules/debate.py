"""Debate at Tribunal (Houses of Hermes: Societates, House Tytalus, The
Fine Arts of Debate), worked like certamen:

    Initiative = Perception + stress die
    Attack     = Communication + Attack Ability + Attack Modifier + stress die
    Defence    = Intelligence + Defence Ability + stress die
    Weakening  = Presence + Attack Advantage
    Resistance = highest positive Reputation + Confidence Score (+3 Strong
                 Willed)

The Attack Abilities are Folk Ken, Intrigue and Artes Liberales, the
Defence Abilities Charm, Guile and Leadership; each pairing gives the
attacker a modifier (ATTACK_MODIFIERS). A hit beats the Defence Total
and costs ceil((Weakening - Resistance) / 5) debate Fatigue levels when
positive; levels lost are penalties to both totals (Clear Thinker eases
them by one). The debate ends when one side has lost 5 levels or the
rounds run out; the side that lost fewer is the victor, and the
difference is its Argument Strength.

Each testimony a side holds is used once, in a round of its choosing:
the prosecution's to raise an Attack Total, the defence's a Defence
Total. A proposal (a motion) loses Argument Strength by how far it
changes the Code, and 1 more at the Grand Tribunal; its proposer debates
the whole Tribunal, a different questioner each round. A flawed thesis
starts levels down, and a side argued knowing it false loses its
Truthful Trait from each Defence Total (The Power of Truth). Certamen
may take a debate's place, binding the case, in a personal charge
between two magi that names no violation of the Code (not an appeal,
since certamen can't over-rule a Tribunal, DE p. 230); or settle one
point of a case, its Fatigue levels lost counting as the debate's.

The Argument Strength wins the victor a share of the neutral votes, and
from 5 up a share of the hostile ones (SWAY)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field, replace

from ..models import Character
from . import code_of_hermes, dice, hermetic_law, reputations, work_virtues
from .lab import ability_score
from .rounding import round_nearest, round_up

SOURCE = (
    "Houses of Hermes: Societates, House Tytalus, The Fine Art of Debate, "
    "pp. 90-93; Ars Magica Definitive Edition, Certamen (p. 230)"
)

ATTACKS = ("Folk Ken", "Intrigue", "Artes Liberales")
DEFENCES = ("Charm", "Guile", "Leadership")
#: The subjects of Artes Liberales a debating attack uses.
DEBATE_SUBJECTS = ("logic", "rhetoric")

#: The attacker's modifier, by its Attack Ability and the defender's
#: Defence Ability.
ATTACK_MODIFIERS: dict[tuple[str, str], int] = {
    ("Folk Ken", "Charm"): 3,
    ("Folk Ken", "Guile"): -3,
    ("Folk Ken", "Leadership"): 0,
    ("Intrigue", "Charm"): 0,
    ("Intrigue", "Guile"): 3,
    ("Intrigue", "Leadership"): -3,
    ("Artes Liberales", "Charm"): -3,
    ("Artes Liberales", "Guile"): 0,
    ("Artes Liberales", "Leadership"): 3,
}

#: Debate Fatigue levels that end a debate at once.
KNOCKED_OUT = 5

#: The rounds a praeco usually allows (the book: typically 5-10).
DEFAULT_ROUNDS = 5
MAX_ROUNDS = 10

#: What each kind of proposal costs its Argument Strength.
PROPOSALS: dict[str, int] = {"Clarification": 0, "Addition": -1, "Alteration": -3}

#: Argument Strength -> (its name, % of the neutral vote, % of the
#: hostile vote) the victor wins; 7 and more are a Landslide.
SWAY: dict[int, tuple[str, int, int]] = {
    1: ("Inconclusive", 0, 0),
    2: ("Edge", 10, 0),
    3: ("Upper Hand", 20, 0),
    4: ("Clear Victory", 30, 0),
    5: ("Triumphant Victory", 40, 10),
    6: ("Momentous Victory", 50, 20),
    7: ("Landslide Victory", 60, 30),
}

#: A testimony's bonus by who gives it, looked for in its words (the
#: most a line names wins; a Quaesitor's examination adds +3 more).
TESTIMONY_WORDS: tuple[tuple[tuple[str, ...], int], ...] = (
    (("magus", "maga", "magi", "peer"), 3),
    (("apprentice", "familiar", "servant", "grog"), 2),
)


def testimony_bonus(words: str) -> int:
    """A testimony's bonus: +1 written or from a mundane, +2 from a social
    inferior, +3 from a peer; +3 more if a Quaesitor examined it."""
    text = words.casefold()
    bonus = 1
    for found, value in TESTIMONY_WORDS:
        if any(word in text for word in found):
            bonus = max(bonus, value)
    if "quaesitor" in text:
        bonus += 3
    return bonus


@dataclass(frozen=True)
class Debater:
    """What a debater brings: the scores the totals use. A speaker with no
    scores written down debates at a skill (SKILLS)."""

    name: str
    perception: int = 0
    communication: int = 0
    intelligence: int = 0
    presence: int = 0
    attacks: dict[str, int] = field(default_factory=dict)
    defences: dict[str, int] = field(default_factory=dict)
    resistance: int = 0
    clear_thinker: bool = False
    found: bool = False
    #: The Power of Truth (p. 91): the debate Fatigue levels a flawed or
    #: despised thesis starts with, and what is taken from each Defence
    #: Total by arguing a side known to be false (the Truthful Trait).
    handicap: int = 0
    falsehood: int = 0

    def attack(self) -> str:
        """The Attack Ability it is best at (the first on a tie)."""
        return max(ATTACKS, key=lambda a: self.attacks.get(a, 0))

    def defence(self) -> str:
        return max(DEFENCES, key=lambda d: self.defences.get(d, 0))


#: A magus at Tribunal with nothing written down: 2 in each Ability.
AVERAGE_ABILITY = 2

#: How well a speaker with no scores written down debates (the rules give
#: no figures, so these are the app's): each Characteristic a debate uses,
#: each Attack and Defence Ability, and the Reputation that is their
#: Resistance. Middling is an ordinary magus.
MIDDLING, ABLE, FORMIDABLE = "Middling", "Able", "Formidable"
SKILLS: dict[str, tuple[int, int, int]] = {
    MIDDLING: (0, AVERAGE_ABILITY, 0),
    ABLE: (1, 4, 0),
    FORMIDABLE: (2, 6, 3),
}


def skilled(name: str, skill: str = MIDDLING) -> Debater:
    """`name` debating at `skill` (SKILLS), for a speaker with no scores."""
    characteristic, ability, reputation = SKILLS.get(skill, SKILLS[MIDDLING])
    return Debater(
        name,
        perception=characteristic,
        communication=characteristic,
        intelligence=characteristic,
        presence=characteristic,
        attacks=dict.fromkeys(ATTACKS, ability),
        defences=dict.fromkeys(DEFENCES, ability),
        resistance=reputation,
    )


def has_scores(character: Character) -> bool:
    """Whether `character` has any score a debate uses written down: a
    Characteristic or one of the Attack and Defence Abilities."""
    c = character.characteristics
    if any((c.perception, c.communication, c.intelligence, c.presence)):
        return True
    return any(sum(ability_score(character, a)) for a in (*ATTACKS, *DEFENCES))


def debater(name: str, character: Character | None, skill: str = MIDDLING) -> Debater:
    """`name` as a debater: `character`'s scores, or (with none written
    down) a speaker's of `skill`."""
    if character is None or not has_scores(character):
        return skilled(name, skill)
    c = character.characteristics
    reputation = reputations.highest_good(character.reputations)
    names = {vf.vf_id for vf in character.virtues_flaws}
    strong = 3 if "vf_strong_willed" in names else 0
    return Debater(
        name,
        perception=c.perception,
        communication=c.communication,
        intelligence=c.intelligence,
        presence=c.presence,
        attacks={a: sum(ability_score(character, a)) for a in ATTACKS}
        | {
            "Artes Liberales": sum(ability_score(character, "Artes Liberales"))
            + sum(
                n for _, n in work_virtues.artes_liberales(character, DEBATE_SUBJECTS)
            )
        },
        defences={d: sum(ability_score(character, d)) for d in DEFENCES},
        resistance=reputation + character.background.confidence_score + strong,
        clear_thinker="vf_clear_thinker" in names,
        found=True,
    )


#: The penalty for each debate Fatigue level lost, as the Fatigue
#: levels give it (Winded 0, Weary -1, Tired -3, Dazed -5).
_PENALTIES = (0, 0, -1, -3, -5)


def fatigue_penalty(lost: int, clear_thinker: bool) -> int:
    penalty = _PENALTIES[min(lost, len(_PENALTIES) - 1)]
    if clear_thinker and penalty < 0:
        penalty += 1
    return penalty


@dataclass
class Debate:
    """A debate worked out round by round: the levels each side lost (the
    prosecution's first), the rounds it ran and a line for each."""

    lost: list[int]
    rounds: int
    lines: list[str]

    @property
    def victor(self) -> int | None:
        """0 the prosecution, 1 the defence, None a tie."""
        if self.lost[0] == self.lost[1]:
            return None
        return 0 if self.lost[0] < self.lost[1] else 1

    @property
    def strength(self) -> int:
        return abs(self.lost[0] - self.lost[1])


def _roll(rng: random.Random) -> int:
    die = dice.stress_die(rng)
    return 0 if die.botched else die.value


def run(
    sides: tuple[Debater, Debater],
    testimony: tuple[list[int], list[int]],
    rounds: int,
    rng: random.Random,
    panel: list[Debater] | None = None,
) -> Debate:
    """Debate `rounds` rounds (or until a side is knocked out). Each side
    attacks with its best Attack Ability and defends with its best Defence
    Ability, and uses its best unused testimony in each round (the
    prosecution on attack, the defence on defence). A side starts with its
    handicap's levels lost, and a side arguing what it knows is false
    loses its falsehood from each Defence Total.

    With a `panel`, the second side is the whole Tribunal facing a
    proposal (p. 92): each round a different one of the panel questions
    the proposer, in turn, and the levels it loses are the Tribunal's."""
    lost = [
        min(KNOCKED_OUT, max(0, sides[0].handicap)),
        min(KNOCKED_OUT, max(0, sides[1].handicap)),
    ]
    left = [sorted(testimony[0], reverse=True), sorted(testimony[1], reverse=True)]
    lines: list[str] = []
    played = 0
    if KNOCKED_OUT in lost:
        return Debate(lost, played, lines)
    for number in range(1, max(1, rounds) + 1):
        played = number
        second = panel[(number - 1) % len(panel)] if panel else sides[1]
        speaking = (sides[0], second)
        first = (
            0
            if speaking[0].perception + _roll(rng) >= second.perception + _roll(rng)
            else 1
        )
        for attacker in (first, 1 - first):
            defender = 1 - attacker
            a, d = speaking[attacker], speaking[defender]
            attack_ability, defence_ability = a.attack(), d.defence()
            boost = left[0].pop(0) if attacker == 0 and left[0] else 0
            guard = left[1].pop(0) if defender == 1 and left[1] else 0
            attack = (
                a.communication
                + a.attacks.get(attack_ability, 0)
                + ATTACK_MODIFIERS[(attack_ability, defence_ability)]
                + fatigue_penalty(lost[attacker], a.clear_thinker)
                + boost
                + _roll(rng)
            )
            defence = (
                d.intelligence
                + d.defences.get(defence_ability, 0)
                + fatigue_penalty(lost[defender], d.clear_thinker)
                + guard
                - d.falsehood
                + _roll(rng)
            )
            if attack <= defence:
                lines.append(
                    f"Round {number}: {a.name}'s {attack_ability} ({attack}) "
                    f"fails against {d.name}'s {defence_ability} ({defence})."
                )
                continue
            weakening = a.presence + attack - defence
            hit = (
                0
                if weakening <= d.resistance
                else round_up((weakening - d.resistance) / 5)
            )
            # Knocked out at five levels: no more can be lost.
            lost[defender] = min(KNOCKED_OUT, lost[defender] + hit)
            lines.append(
                f"Round {number}: {a.name}'s {attack_ability} ({attack}) beats "
                f"{d.name}'s {defence_ability} ({defence}): "
                f"{hit} level{'' if hit == 1 else 's'} lost."
            )
            if lost[defender] >= KNOCKED_OUT:
                return Debate(lost, played, lines)
    return Debate(lost, played, lines)


def sway(strength: int) -> tuple[str, int, int]:
    """The Argument Strength's name and the shares of the neutral and
    hostile votes it wins."""
    if strength <= 0:
        return ("No victory", 0, 0)
    return SWAY[min(strength, max(SWAY))]


def swayed(strength: int, neutral: int, hostile: int) -> tuple[int, int]:
    """How many neutral and hostile votes the victor wins."""
    _name, from_neutral, from_hostile = sway(strength)
    return (
        min(neutral, round_nearest(neutral * from_neutral / 100)),
        min(hostile, round_nearest(hostile * from_hostile / 100)),
    )


# -- proposals, the Power of Truth and certamen (pp. 91-93) --

#: A proposal heard at the Grand Tribunal loses 1 more Argument Strength,
#: on top of its kind's penalty (p. 93).
GRAND_TRIBUNAL_PENALTY = -1

#: Where a proposal is heard: the Tribunal's own Peripheral Code, the
#: same with a recommendation to the next Grand Tribunal (a regional
#: Tribunal can change only its Peripheral Code, p. 93), or the Grand
#: Tribunal itself.
LOCAL, RECOMMENDED, AT_GRAND = "local", "recommended", "grand"
PROPOSAL_FORUMS: dict[str, str] = {
    LOCAL: "The Peripheral Code",
    RECOMMENDED: "The Peripheral Code, and recommended to the Grand Tribunal",
    AT_GRAND: "Heard at the Grand Tribunal (1 more off its strength)",
}


def proposal_penalty(kind: str, forum: str = LOCAL) -> int:
    """What a proposal of `kind` costs its Argument Strength where it is
    heard (both 0 or less)."""
    penalty = PROPOSALS.get(kind, 0)
    return penalty + (GRAND_TRIBUNAL_PENALTY if forum == AT_GRAND else 0)


#: How a side argues (the Power of Truth, p. 91): in good faith; knowing
#: its side is false (its Truthful Trait comes off each Defence Total);
#: or a patently flawed or despised thesis, which starts the debate
#: already a level or more down (the storyguide judges how many).
GOOD_FAITH, KNOWN_FALSE = "good", "false"
FLAWED = {"flawed_1": 1, "flawed_2": 2, "flawed_3": 3}
THESES: dict[str, str] = {
    GOOD_FAITH: "In good faith",
    KNOWN_FALSE: "Knowing it false (its Truthful Trait counts against it)",
    "flawed_1": "A flawed thesis: starts 1 level down",
    "flawed_2": "A despised thesis: starts 2 levels down",
    "flawed_3": "A preposterous thesis: starts 3 levels down",
}


def truthful(character: Character | None) -> int:
    """The character's Truthful Personality Trait, if positive (0 for none):
    what arguing a side it knows is false takes from its Defence Totals.
    A deceitful Trait gives no bonus (p. 91)."""
    if character is None:
        return 0
    return max(
        (
            t.score
            for t in character.personality_traits
            if t.name.strip().casefold() == "truthful"
        ),
        default=0,
    )


def arguing(side: Debater, thesis: str, character: Character | None) -> Debater:
    """`side` as it argues `thesis` (THESES)."""
    if thesis == KNOWN_FALSE:
        return replace(side, falsehood=truthful(character))
    if thesis in FLAWED:
        return replace(side, handicap=FLAWED[thesis])
    return side


#: How a charge is heard: by debate; by certamen in the debate's place,
#: whose result binds the case with no vote; or by certamen on one point
#: of it, whose actual Fatigue levels lost stand in for the debate's
#: (p. 92, Using Certamen Instead of Debate).
BY_DEBATE, BY_CERTAMEN, ON_A_POINT = "debate", "certamen", "point"
HEARD_BY: dict[str, str] = {
    BY_DEBATE: "Debate",
    BY_CERTAMEN: "Certamen in its place (binding, no vote)",
    ON_A_POINT: "Certamen on one point (its Fatigue levels lost count)",
}


def binding_certamen_bar(kind: str, charge: str, *, between_magi: bool) -> str:
    """Why certamen can't take the place of a case's debate, or "" when it
    may. It may decide a personal charge between two magi (p. 92), but it
    can't over-rule a Tribunal, so not an appeal against its ruling, nor
    require a violation of the Code or a magus to overlook one, so not a
    charge of one (DE p. 230). A motion changes the Code and is debated.
    Certamen on one point of a bigger case is still allowed: it doesn't
    decide the vote."""
    if kind == "motion":
        return "A motion is debated: certamen can't change the Code."
    if kind == "appeal":
        return (
            "Certamen can't over-rule a Tribunal (DE p. 230): an appeal "
            "against its ruling is debated."
        )
    if not between_magi:
        return (
            "Binding certamen decides only a personal charge between two magi "
            "(Houses of Hermes: Societates p. 92)."
        )
    crime = code_of_hermes.high_crime(charge)
    named = crime.name if crime is not None else None
    if named is None:
        low = hermetic_law.low_crime(charge)
        named = low[0] if low is not None else None
    if named is not None:
        return (
            f"The charge is a violation of the Code ({named}): certamen can't "
            "require one or a magus to overlook one (DE p. 230)."
        )
    return ""
