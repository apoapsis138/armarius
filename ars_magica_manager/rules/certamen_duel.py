"""A certamen duel played out (DE pp. 231-233), on rules.certamen's
totals:

- Initiative (Quickness + Finesse + a stress die) is rolled once; the one
  who wins it attacks first each round, then the other.
- Each attack: Attack Total (Presence + the Art attacked with + a stress
  die) against the defender's Defense Total (Perception + the other Art +
  a stress die); a tie goes to the defender. The Attack Advantage adds to
  the Weakening Total (Intelligence + Penetration); less the Resistance
  Total (Stamina + Parma Magica), every five points or fraction cost a
  Fatigue level, whose penalty then counts against Attack and Defense.
- A pawn of vis of the Art used adds 2 to Attack or Defense for a round,
  at most the Art's score in pawns a round.
- It ends when a duelist falls unconscious (the victor may cast a spell
  of the duel's Arts at him, his Parma Magica circumvented) or concedes
  (his Parma Magica and Magic Resistance then stand). A magus can botch
  (p. 231), and the book says no more of what it does: a botch stops the
  duel here, for the storyguide to say what comes of it and the rest to be
  played at the table.

Each side's plan is fixed for the whole duel: which Art he attacks with
(the Technique, the Form, or the better for him), the vis he spends a
round, and the Fatigue penalty at which he concedes. A magus who would
change his plan mid-duel plays it round by round at the table instead.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field, replace

from ..models import FATIGUE_LEVELS, Character, Saga
from . import certamen, dice
from .derived import fatigue_penalty

SOURCE = "Ars Magica Definitive Edition, Certamen, pp. 231-233"
#: How many rounds a duel is played at most before it is called a draw.
MOST_ROUNDS = 40
#: The +2 a pawn of vis adds for a round.
VIS_BONUS = 2
TECHNIQUE, FORM, BETTER = "technique", "form", "better"
ATTACKS: dict[str, str] = {
    BETTER: "With whichever Art is better for him",
    TECHNIQUE: "With the Technique",
    FORM: "With the Form",
}


@dataclass
class Plan:
    """One duelist's plan: the Art he attacks with, the pawns of vis he
    spends on attack and on defense each round (of the Art used), and the
    Fatigue penalty at which he concedes (None: he fights on until he
    falls)."""

    magus: Character
    attack: str = BETTER
    attack_vis: int = 0
    defence_vis: int = 0
    concede_at: int | None = 3


@dataclass
class Side:
    plan: Plan
    level: int
    vis_left: dict[str, int]
    vis_spent: dict[str, int] = field(default_factory=dict)

    @property
    def magus(self) -> Character:
        return replace(self.plan.magus, fatigue_level=FATIGUE_LEVELS[self.level])

    @property
    def penalty(self) -> int:
        return fatigue_penalty(
            FATIGUE_LEVELS[self.level], self.plan.magus.virtues_flaws
        )

    @property
    def down(self) -> bool:
        return self.level >= len(FATIGUE_LEVELS) - 1


@dataclass
class Duel:
    """What came of it: the rounds' lines, the winner (None for a draw) and
    how he won, and each side's Fatigue levels lost and vis spent."""

    lines: list[str]
    winner: Character | None
    how: str
    fatigue_lost: tuple[int, int]
    vis_spent: tuple[dict[str, int], dict[str, int]]


def _arts(side: Side, technique: str, form: str) -> tuple[str, str]:
    """(the Art he attacks with, the one he defends with)."""
    if side.plan.attack == TECHNIQUE:
        return technique, form
    if side.plan.attack == FORM:
        return form, technique
    totals = certamen.certamen_totals(side.magus, technique, form)
    if totals.attack_technique + totals.defence_form >= (
        totals.attack_form + totals.defence_technique
    ):
        return technique, form
    return form, technique


def _vis(side: Side, art: str, wanted: int) -> int:
    """The pawns he spends this round: what he wants, held and allowed."""
    key = art.lower()
    pawns = max(
        0,
        min(wanted, side.vis_left.get(key, 0), certamen.max_vis(side.plan.magus, art)),
    )
    if pawns:
        side.vis_left[key] -= pawns
        side.vis_spent[art] = side.vis_spent.get(art, 0) + pawns
    return pawns


def _total(
    totals: certamen.CertamenTotals, attacking: bool, art: str, technique: str
) -> int:
    if attacking:
        return totals.attack_technique if art == technique else totals.attack_form
    return totals.defence_technique if art == technique else totals.defence_form


def _attack(
    saga: Saga | None,
    rng: random.Random,
    attacker: Side,
    defender: Side,
    technique: str,
    form: str,
) -> str:
    art, _ = _arts(attacker, technique, form)
    _, guard = _arts(defender, technique, form)
    mine = certamen.certamen_totals(attacker.magus, technique, form)
    theirs = certamen.certamen_totals(defender.magus, technique, form)
    a_vis = _vis(attacker, art, attacker.plan.attack_vis)
    d_vis = _vis(defender, guard, defender.plan.defence_vis)
    a_die = dice.stress_die(rng, 1, saga=saga)
    d_die = dice.stress_die(rng, 1, saga=saga)
    name, other = attacker.plan.magus.name, defender.plan.magus.name
    botched = [n for n, die in ((name, a_die), (other, d_die)) if die.botched]
    if botched:
        raise Botched(" and ".join(botched))
    attack = _total(mine, True, art, technique) + a_die.value + VIS_BONUS * a_vis
    defence = _total(theirs, False, guard, technique) + d_die.value + VIS_BONUS * d_vis
    advantage = certamen.attack_advantage(attack, defence)
    if not advantage:
        return f"{name} attacks with {art}: {attack} against {other}'s {defence}; held."
    lost = certamen.fatigue_lost(mine.weakening_base + advantage, theirs.resistance)
    defender.level = min(len(FATIGUE_LEVELS) - 1, defender.level + lost)
    return (
        f"{name} attacks with {art}: {attack} against {other}'s {defence}, "
        f"Weakening {mine.weakening_base + advantage} against Resistance "
        f"{theirs.resistance}: {other} loses {lost} Fatigue level(s), now "
        f"{FATIGUE_LEVELS[defender.level]}."
    )


class Botched(Exception):
    """A die botched mid-duel (the duelist's name or names): the duel stops
    for the storyguide."""


def _concedes(side: Side) -> bool:
    limit = side.plan.concede_at
    return limit is not None and not side.down and -side.penalty >= limit


def play(
    saga: Saga | None,
    first: Plan,
    second: Plan,
    technique: str,
    form: str,
    rng: random.Random,
) -> Duel:
    """Play the duel out, round by round, as the two plans say."""
    sides = [
        Side(p, FATIGUE_LEVELS.index(p.magus.fatigue_level), dict(p.magus.raw_vis))
        for p in (first, second)
    ]
    before = [s.level for s in sides]
    lines: list[str] = []
    rolls = []
    for side in sides:
        totals = certamen.certamen_totals(side.magus, technique, form)
        die = dice.stress_die(rng, 1, saga=saga)
        rolls.append(totals.initiative + die.value)
    order = [0, 1] if rolls[0] >= rolls[1] else [1, 0]
    lines.append(
        f"Initiative: {first.magus.name} {rolls[0]}, {second.magus.name} "
        f"{rolls[1]}; {sides[order[0]].plan.magus.name} attacks first."
    )
    winner: Character | None = None
    how = "a draw: neither gave way"
    for number in range(1, MOST_ROUNDS + 1):
        for a, d in (order, order[::-1]):
            attacker, defender = sides[a], sides[d]
            try:
                said = _attack(saga, rng, attacker, defender, technique, form)
            except Botched as botch:
                how = (
                    f"{botch} botches in round {number}: the storyguide says what "
                    "comes of it, and the duel goes on at the table (DE p. 231)"
                )
                lines.append(f"Round {number}: {how}.")
                break
            lines.append(f"Round {number}: {said}")
            if defender.down:
                winner = attacker.plan.magus
                loser = defender.plan.magus.name
                how = (
                    f"{loser} falls unconscious: {winner.name} may cast a spell "
                    f"of {technique} {form} at {loser}, whose Parma Magica is "
                    "circumvented"
                )
                break
            if _concedes(defender):
                winner = attacker.plan.magus
                how = (
                    f"{defender.plan.magus.name} concedes at "
                    f"{FATIGUE_LEVELS[defender.level]}, Parma Magica still "
                    "standing"
                )
                break
        if winner is not None or "botches" in how:
            break
    return Duel(
        lines,
        winner,
        how,
        (sides[0].level - before[0], sides[1].level - before[1]),
        (sides[0].vis_spent, sides[1].vis_spent),
    )
