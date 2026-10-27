"""House Flambeau's tournaments (Houses of Hermes: Societates pp. 20-22),
open to any magus, the great one at Castra Solis for five days about the
summer solstice of every leap year.

- Certamen, a single-elimination bracket the officials seed so the
  strongest meet last: each match is the best of three duels, with 15
  minutes' rest between duels and an hour between matches. The youngest
  magus (by Hermetic age; a coin decides a tie) chooses the Form and the
  oldest the Technique, in place of the aggressor's Technique and the
  defender's Form (DE p. 231); either may veto the other's choice as
  usual, but not in both the first and second duel, so each has his own
  first choice once. The winner may not cast a spell on the loser.
- Dimicatio: real spells cast forceless, each answered by a fast-cast
  defence (DE p. 83), the first spell to reach the foe's Parma winning;
  a spell that penetrates is foul play, investigated at once. At Castra
  Solis a magus who won at least two certamen matches may enter. As a
  rule of thumb a defence of half the incoming spell's level suffices.
- Forceless casting: the caster keeps the spell's Penetration Total at 0
  or below, so it can't affect a magus with Magic Resistance 0 or more,
  unless he botches.
- The wizards' melee: teams of a magus and five grogs, each magus trying
  to touch the other with a forceless spell; Touch and Personal spells
  only (Voice on one's own grogs in some), blunted weapons (-3 Damage),
  damage spells of the third magnitude or less, or none (Castra Solis
  bans them); vis and enchanted devices within the same limits.
- Prizes: a rook of vis (ten pawns) is a moderate one.

A tournament is worth House Acclaim to a Flambeau (rules.acclaim).
"""

from __future__ import annotations

from .rounding import round_up

SOURCE = "Houses of Hermes: Societates, Flambeau Tournaments, pp. 20-22"

#: Duels a certamen match is won by, of three.
DUELS_TO_WIN = 2
DUELS = 3
REST_MINUTES = 15
#: Certamen matches won to enter the dimicatio at Castra Solis.
DIMICATIO_WINS = 2
#: The most Penetration a forceless spell may have.
FORCELESS_PENETRATION = 0
#: The wizards' melee.
MELEE_GROGS = 5
BLUNTED_DAMAGE = -3
MELEE_DAMAGE_MAGNITUDE = 3
#: A moderate prize, in pawns of vis.
MODERATE_PRIZE = 10


def choosers(age_a: int, age_b: int) -> tuple[str, str] | None:
    """Who chooses the Art in a tournament duel, by Hermetic age: ("a" or
    "b" for the Form, then the Technique); None when they are the same
    age and a coin toss decides."""
    if age_a == age_b:
        return None
    return ("a", "b") if age_a < age_b else ("b", "a")


def may_veto(duel: int, vetoed_first: bool) -> bool:
    """Whether a duelist may veto his opponent's choice of Art in the
    match's `duel` (1, 2 or 3): not in the second if he did in the first."""
    return not (duel == 2 and vetoed_first)


def match_won(wins: int, losses: int) -> bool | None:
    """True once two duels are won, False once two are lost, None while
    the match goes on."""
    if wins >= DUELS_TO_WIN:
        return True
    if losses >= DUELS_TO_WIN:
        return False
    return None


def may_enter_dimicatio(matches_won: int) -> bool:
    return matches_won >= DIMICATIO_WINS


def forceless(penetration_total: int) -> int:
    """A forceless spell's Penetration Total: no more than 0."""
    return min(penetration_total, FORCELESS_PENETRATION)


def defence_level(spell_level: int) -> int:
    """The fast-cast defence that usually suffices: half the spell's level,
    rounded up (the rule of thumb; the storyguide judges whether the Arts
    fit)."""
    return round_up(max(0, spell_level) / 2)


def melee_damage_allowed(magnitude: int, castra_solis: bool = False) -> bool:
    """Whether a damaging spell may be cast in the wizards' melee: of the
    third magnitude or less, and never at Castra Solis."""
    return not castra_solis and magnitude <= MELEE_DAMAGE_MAGNITUDE
