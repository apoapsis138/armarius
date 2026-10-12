"""Certamen totals, before the stress die:

    Initiative = Quickness + Finesse
    Attack     = Presence + one Art (the Technique or the Form)
    Defence    = Perception + the other Art
    Weakening  = Intelligence + Penetration + Attack Advantage
    Resistance = Stamina + Parma Magica (not x5)

A hit needs the Attack Total to beat the Defence Total (a tie goes to the
defender), and costs ceil((Weakening - Resistance) / 5) Fatigue levels when
positive. Each pawn of vis matching the Art adds +2 to Attack or Defence for
a round, up to the score in that Art. Fatigue penalties apply to Attack and
Defence.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character
from .derived import fatigue_penalty
from .lab import ability_score, art_score
from .rounding import round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Seven: Hermetic Magic, Certamen "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Seven:"
    "_Hermetic_Magic#Certamen)"
)


@dataclass(frozen=True)
class CertamenTotals:
    initiative: int
    #: Attacking with the Technique (and defending with the Form)...
    attack_technique: int
    defence_form: int
    #: ...or attacking with the Form (and defending with the Technique).
    attack_form: int
    defence_technique: int
    weakening_base: int  # before the Attack Advantage
    resistance: int


def _art(magus: Character, art: str) -> int:
    return sum(art_score(magus, art))


def certamen_totals(magus: Character, technique: str, form: str) -> CertamenTotals:
    c = magus.characteristics
    penalty = fatigue_penalty(magus.fatigue_level, magus.virtues_flaws)
    tech, frm = _art(magus, technique), _art(magus, form)
    return CertamenTotals(
        initiative=c.quickness + sum(ability_score(magus, "Finesse")),
        attack_technique=c.presence + tech + penalty,
        defence_form=c.perception + frm + penalty,
        attack_form=c.presence + frm + penalty,
        defence_technique=c.perception + tech + penalty,
        weakening_base=c.intelligence + sum(ability_score(magus, "Penetration")),
        resistance=c.stamina + sum(ability_score(magus, "Parma Magica")),
    )


def attack_advantage(attack_total: int, defence_total: int) -> int:
    """How far the attack beat the defence; 0 when it didn't (a tie goes to
    the defender)."""
    return max(0, attack_total - defence_total)


def fatigue_lost(weakening_total: int, resistance_total: int) -> int:
    """Fatigue levels a hit costs: ceil((Weakening - Resistance) / 5) when
    positive (1-5 -> 1, 6-10 -> 2...)."""
    excess = weakening_total - resistance_total
    return 0 if excess <= 0 else round_up(excess / 5)


def max_vis(magus: Character, art: str) -> int:
    """Pawns of an Art's vis usable in one round: the score in that Art."""
    return art_score(magus, art)[0]
