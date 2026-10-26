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

The schools of certamen (HoH: True Lineages pp. 135-139) are rows in
`certamen_styles`; styled_totals() and traded() add what a row changes to
these totals.

No screen uses attack_advantage(), fatigue_lost(), max_vis() or the style
functions yet: they are the rules for screens still to come, and only the
tests call them.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from ..models import Character
from . import certamen_styles as styles
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


def fatigue_lost(
    weakening_total: int,
    resistance_total: int,
    *,
    divisor: int = 5,
    most: int | None = None,
) -> int:
    """Fatigue levels a hit costs: ceil((Weakening - Resistance) / 5) when
    positive (1-5 -> 1, 6-10 -> 2...). A Scissor's hit after a skipped
    attack divides by 3 (4 in his style), and a Saggitarius' hit costs at
    `most` 1 (HoH: TL p. 138)."""
    excess = weakening_total - resistance_total
    levels = 0 if excess <= 0 else round_up(excess / divisor)
    return levels if most is None else min(levels, most)


def max_vis(magus: Character, art: str) -> int:
    """Pawns of an Art's vis usable in one round: the score in that Art."""
    return art_score(magus, art)[0]


# -- Styles of certamen (HoH: True Lineages pp. 135-139) ---------------------


def school_of(magus: Character) -> styles.CertamenStyle | None:
    """The school the magus was trained in, or None when none is recorded."""
    school = magus.hermetic.certamen_school
    return styles.style(school) if school else None


def _rule(magus: Character, style_id: str, follower: bool) -> styles.StyleRule:
    """The style's rule for this way of fighting; ValueError when the magus
    can't fight so (a follower must belong to the school, a House's style
    is its members' alone, and some styles have no followers)."""
    found = styles.style(style_id)
    if found.house and magus.hermetic.house != found.house:
        raise ValueError(f"The {found.name} is for members of {found.house} only")
    if follower and magus.hermetic.certamen_school != style_id:
        raise ValueError(f"{magus.name} is not a follower of the {found.name}")
    rule = found.rule(follower)
    if rule is None:
        way = "follower of" if follower else "duelist in the style of"
        raise ValueError(f"No {way} the {found.name} is known")
    return rule


def _is(art: str, name: str) -> bool:
    return art.casefold() == name.casefold()


def style_score(magus: Character, style_id: str, technique: str) -> int:
    """The score a style's limits count in: Finesse, or a Bestiarius'
    Heartbeast in a Muto duel (HoH: TL p. 136)."""
    if style_id == "bestiarius" and _is(technique, "Muto"):
        return sum(ability_score(magus, "Heartbeast"))
    return sum(ability_score(magus, "Finesse"))


def styled_totals(
    magus: Character, technique: str, form: str, style_id: str, *, follower: bool
) -> CertamenTotals:
    """The duel's totals for a magus fighting as a follower of a school, or
    in its style: the Definitive Edition's totals, with what the style
    changes for the whole duel (only the Bestiarius' Heartbeast does).

    A follower uses Heartbeast for Finesse (the Initiative Total's, DE
    p. 231) only in a Muto duel, and adds twice it to Resistance only in
    Muto Corpus or Muto Animal; a Bjornaer fighting in the style adds his
    Heartbeast to Resistance in every duel, as the text gives no limit
    (HoH: TL p. 136)."""
    _rule(magus, style_id, follower)
    totals = certamen_totals(magus, technique, form)
    if style_id != "bestiarius":
        return totals
    heartbeast = sum(ability_score(magus, "Heartbeast"))
    if not follower:
        return replace(totals, resistance=totals.resistance + heartbeast)
    if not _is(technique, "Muto"):
        return totals
    totals = replace(totals, initiative=magus.characteristics.quickness + heartbeast)
    if _is(form, "Corpus") or _is(form, "Animal"):
        totals = replace(totals, resistance=totals.resistance + 2 * heartbeast)
    return totals


def trade_limit(
    magus: Character, style_id: str, technique: str, *, follower: bool
) -> int:
    """The most points the style's trade takes in one round (0 for a style
    with none)."""
    trade = _rule(magus, style_id, follower).trade
    if trade is None:
        return 0
    return trade.up_to * style_score(magus, style_id, technique)


def _shift(totals: CertamenTotals, total: str, by: int) -> CertamenTotals:
    if total == styles.ATTACK:
        return replace(
            totals,
            attack_technique=totals.attack_technique + by,
            attack_form=totals.attack_form + by,
        )
    if total == styles.DEFENCE:
        return replace(
            totals,
            defence_form=totals.defence_form + by,
            defence_technique=totals.defence_technique + by,
        )
    if total == styles.INITIATIVE:
        return replace(totals, initiative=totals.initiative + by)
    if total == styles.RESISTANCE:
        return replace(totals, resistance=totals.resistance + by)
    # The next rounds' Attack Advantage (advantage_cost), or a noose's
    # gain that only a declined hit spends.
    return totals


def traded(
    magus: Character,
    totals: CertamenTotals,
    style_id: str,
    technique: str,
    points: int,
    *,
    follower: bool,
) -> CertamenTotals:
    """A round's totals after the style's trade of `points`: each point
    raises its gain and lowers its cost by the row's amounts."""
    trade = _rule(magus, style_id, follower).trade
    if trade is None:
        raise ValueError(f"The {styles.style(style_id).name} makes no trade")
    limit = trade_limit(magus, style_id, technique, follower=follower)
    if not 0 <= points <= limit:
        raise ValueError(f"A trade of {points} is outside 0-{limit}")
    totals = _shift(totals, trade.cost, -trade.cost_per * points)
    return _shift(totals, trade.gain, trade.gain_per * points)


def advantage_cost(style_id: str, points: int, *, follower: bool) -> int:
    """What a trade takes off the Attack Advantage in each of the next
    three rounds: the Retiarius', twice the points (HoH: TL p. 138)."""
    rule = styles.style(style_id).rule(follower)
    trade = None if rule is None else rule.trade
    if trade is None or trade.cost != styles.ADVANTAGE:
        return 0
    return trade.cost_per * points


def held_back(
    magus: Character,
    totals: CertamenTotals,
    style_id: str,
    technique: str,
    *,
    follower: bool,
) -> CertamenTotals:
    """A round's totals when the duelist declines to attack: a
    Hoplomachus' Defence gains three times his Finesse, twice in his
    style (HoH: TL p. 137)."""
    times = _rule(magus, style_id, follower).hold_back
    return _shift(
        totals, styles.DEFENCE, times * style_score(magus, style_id, technique)
    )


def worn_resistance(
    resistance_total: int, finesse: int, style_id: str, *, follower: bool
) -> int:
    """The foe's Resistance after a Velitus declines a hit's damage: less
    Finesse // 2, which may go below zero, or Finesse // 3 in his style,
    to no less than zero (HoH: TL p. 138)."""
    rule = styles.style(style_id).rule(follower)
    if rule is None or rule.resistance_cut is None:
        return resistance_total
    worn = resistance_total - finesse // rule.resistance_cut
    return worn if rule.below_zero else max(0, worn)


def school_text(magus: Character) -> str:
    """The sheet's note on the magus's school of certamen ("" when none is
    recorded)."""
    school = school_of(magus)
    if school is None:
        return ""
    rule = school.follower
    summary = f": {rule.summary}" if rule is not None else ""
    house = (
        " (not his House's style)"
        if school.house and magus.hermetic.house != school.house
        else ""
    )
    return (
        f"Certamen school: {school.name}, the {school.school}{house}"
        f"{summary} (HoH: TL p. {school.page})."
    )
