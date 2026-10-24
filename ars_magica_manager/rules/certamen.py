"""Certamen totals, before the stress die:

    Initiative = Quickness + Finesse
    Attack     = Presence + one Art (the Technique or the Form)
    Defence    = Perception + the other Art
    Weakening  = Intelligence + Penetration + Attack Advantage
    Resistance = Stamina + Parma Magica (not x5)

A hit needs the Attack Total to beat the Defence Total (a tie goes to the
defender), and costs ceil((Weakening - Resistance) / 5) Fatigue levels when
positive. Each pawn of vis matching the Art adds +2 to Attack or Defence for
a round, up to the score in that Art. Wound and Fatigue penalties apply to
Attack and Defence, and a Deficient Art halves the total it is in (DE pp.
125, 404). Every Tremere has a Minor Magical Focus in certamen: the lower
of the two Arts counts double, and no other Focus applies (DE p. 233).

No screen uses attack_advantage(), fatigue_lost(), max_vis() yet: they are
the rules for screens still to come, and only the tests call them.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character
from . import effects, scores
from .derived import fatigue_penalty, wound_penalty
from .lab import ability_score, art_score
from .rounding import round_down, round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 7: Hermetic Magic, Certamen, pp. 231-233"
)
TREMERE = "house_tremere"
FOCUS = "vf_minor_magical_focus"


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


def certamen_focus(magus: Character) -> bool:
    """Whether the magus has the Tremere Focus in certamen: a member of
    House Tremere, or a Minor Magical Focus named for certamen."""
    return magus.hermetic.house == TREMERE or any(
        vf.vf_id == FOCUS and "certamen" in str(vf.params.get("focus", "")).casefold()
        for vf in magus.virtues_flaws
    )


def _halving(magus: Character, art: str) -> float:
    """What a Deficiency in `art` does to a certamen total using it."""
    found = effects.collect(
        [scores.character_source(magus.virtues_flaws)], "casting_total"
    )
    factor = 1.0
    for e in found:
        if (
            e.modifier.multiplier is not None
            and e.target is not None
            and e.target.casefold() == art.casefold()
        ):
            factor *= e.modifier.multiplier
    return factor


def certamen_totals(magus: Character, technique: str, form: str) -> CertamenTotals:
    c = magus.characteristics
    # Wounds and Fatigue take from every roll (DE pp. 403-404).
    penalty = fatigue_penalty(magus.fatigue_level, magus.virtues_flaws) + wound_penalty(
        magus.wounds, magus.virtues_flaws
    )
    tech, frm = _art(magus, technique), _art(magus, form)
    if certamen_focus(magus):
        if tech <= frm:
            tech *= 2
        else:
            frm *= 2

    def total(base: int, art: int, name: str) -> int:
        return round_down((base + art + penalty) * _halving(magus, name))

    return CertamenTotals(
        initiative=c.quickness + sum(ability_score(magus, "Finesse")),
        attack_technique=total(c.presence, tech, technique),
        defence_form=total(c.perception, frm, form),
        attack_form=total(c.presence, frm, form),
        defence_technique=total(c.perception, tech, technique),
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
