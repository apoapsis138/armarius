"""Penetration and Magic Resistance.

    Penetration Total = Casting Total + Penetration Bonus - spell level
    Penetration Bonus = (Penetration + Penetration Mastery) x multiplier
    multiplier        = 1 + Arcane Connection + sympathetic connections

A spell affects a target with Magic Resistance only if its Penetration
Total is greater (a target with none is always affected).

    Hermetic magus: MR = the spell's Form + 5 x Parma Magica (while raised)
                         + the aura's modifier for a Magic power
    True Faith:     MR = True Faith Score x 10
    Might:          MR = Might

The optional Dominion rule gives the faithful 5 x the Dominion aura.
Virtues and Flaws can take the Form's part away against one Form (Limited
Magic Resistance), halve Parma's part against one (Flawed Parma Magica), or
halve the Penetration Total (Weak Magic).

No screen uses aegis_penalty() yet: it is a rule for a screen still to come,
and only the tests call it.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..models import Character, Saga, VirtueFlawInstance
from . import effects, options, realms
from .breakdown import Breakdown, Line
from .lab import ability_score, art_score
from .rounding import round_down
from .scores import character_source

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Seven: Hermetic Magic, Penetration, "
    "Arcane Connections and Magic Resistance "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Seven:"
    "_Hermetic_Magic#Penetration)"
)
FAITH_SOURCE = (
    "Realms of Power: The Divine, True Faith "
    "(https://www.redcap.org/page/Realms_of_Power:_The_Divine_Open_Content)"
)

#: How long an Arcane Connection lasts -> what it adds to the multiplier.
ARCANE_CONNECTIONS: dict[str, int] = {
    "Hours or days": 1,
    "Weeks or months": 2,
    "Years or decades": 3,
    "Indefinitely": 4,
}


@dataclass(frozen=True)
class Sympathy:
    """A sympathetic connection: usable only with an Arcane Connection, and
    no single one adds more than +2."""

    name: str
    bonus: int


SYMPATHIES: tuple[Sympathy, ...] = (
    Sympathy("Blood relative of the target", 1),
    Sympathy("Target's signature", 1),
    Sympathy("Target's nickname or birth name", 1),
    Sympathy("Name used in the target's secret rituals", 1),
    Sympathy("Target's horoscope for today", 1),
    Sympathy("Target's nativity horoscope", 2),
    Sympathy("Symbolic representation", 2),
)
MAX_SYMPATHY = 2


def penetration_bonus(
    magus: Character,
    *,
    arcane_connection: str | None = None,
    sympathies: Sequence[Sympathy] = (),
    mastery: int = 0,
    specialty: bool = False,
) -> Breakdown:
    """(Penetration + specialty + Penetration Mastery) x the multiplier."""
    score, bonus = ability_score(magus, "Penetration")
    lines = [Line("Penetration", amount=score + bonus, source=SOURCE)]
    if specialty:
        lines.append(Line("Specialty", amount=1, source=SOURCE))
    if mastery:
        lines.append(Line("Penetration Mastery", amount=mastery, source=SOURCE))
    ability = sum(line.amount or 0 for line in lines)
    multiplier = 1
    if arcane_connection is not None:
        multiplier += ARCANE_CONNECTIONS[arcane_connection]
        lines.append(
            Line(
                f"Arcane Connection ({arcane_connection})",
                multiplier=ARCANE_CONNECTIONS[arcane_connection],
                source=SOURCE,
            )
        )
        for sympathy in sympathies:
            add = min(sympathy.bonus, MAX_SYMPATHY)
            multiplier += add
            lines.append(Line(sympathy.name, multiplier=add, source=SOURCE))
    return Breakdown(total=ability * multiplier, lines=lines)


def penetration_total(
    casting_total: int,
    bonus: int,
    level: int,
    virtues_flaws: Sequence[VirtueFlawInstance] = (),
) -> int:
    """Casting Total + Penetration bonus - level, then any Virtue's or
    Flaw's multiplier (Weak Magic halves it), rounded down."""
    total = casting_total + bonus - level
    for effect in effects.collect(
        [character_source(virtues_flaws)], "penetration_total"
    ):
        if effect.modifier.multiplier is not None and total > 0:
            total = round_down(total * effect.modifier.multiplier)
    return total


def penetration_halved_by(virtues_flaws: Sequence[VirtueFlawInstance]) -> list[str]:
    """The Virtues and Flaws that multiply the Penetration Total."""
    return [
        e.entry.name
        for e in effects.collect([character_source(virtues_flaws)], "penetration_total")
        if e.modifier.multiplier is not None
    ]


def _resistance_multiplier(
    magus: Character, applies_to: str, form: str
) -> tuple[float, list[str]]:
    found = [
        e
        for e in effects.collect(
            [character_source(magus.virtues_flaws)], applies_to, target=form
        )
        if e.target is not None and e.modifier.multiplier is not None
    ]
    multiplier = 1.0
    for e in found:
        multiplier *= e.modifier.multiplier or 0
    return multiplier, [e.entry.name for e in found]


def penetrates(penetration: int, magic_resistance: int | None) -> bool:
    """Whether a Penetration Total beats Magic Resistance (strictly); a
    target with none (None) is always affected."""
    return magic_resistance is None or penetration > magic_resistance


def magic_resistance(
    magus: Character,
    form: str,
    *,
    parma_raised: bool = True,
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
    sharing: bool = False,
) -> Breakdown:
    """A Hermetic magus's Magic Resistance against a spell of `form`: the
    Form, 5 x Parma Magica while raised (Parma less 3 while shared), and the
    aura's modifier; never below 0."""
    score, bonus = art_score(magus, form)
    form_part, limited = _resistance_multiplier(magus, "form_resistance", form)
    lines = [
        Line(
            form + (f" ({', '.join(limited)})" if limited else ""),
            amount=round_down((score + bonus) * form_part),
            source=SOURCE,
        )
    ]
    if parma_raised:
        parma, parma_bonus = ability_score(magus, "Parma Magica")
        parma += parma_bonus
        if sharing:
            parma = parma - 3 if parma > 3 else 0
        if parma > 0:
            parma_part, flawed = _resistance_multiplier(magus, "parma_resistance", form)
            lines.append(
                Line(
                    f"Parma Magica {parma} x 5"
                    + (f" ({', '.join(flawed)})" if flawed else ""),
                    amount=round_down(5 * parma * parma_part),
                    source=SOURCE,
                )
            )
    modifier = realms.aura_modifier(realms.HERMETIC, aura_realm, aura)
    if modifier:
        lines.append(
            Line(f"Aura ({aura_realm} {aura})", amount=modifier, source=realms.SOURCE)
        )
    return Breakdown(total=max(0, sum(line.amount or 0 for line in lines)), lines=lines)


def faith_magic_resistance(
    character: Character,
    saga: Saga | None = None,
    *,
    dominion_aura: int = 0,
) -> int:
    """True Faith's Magic Resistance (Score x 10); with the saga's optional
    Dominion rule, at least 5 x the Dominion aura for the faithful."""
    resistance = 10 * character.background.true_faith_score
    if options.is_on(saga, "dominion_magic_resistance"):
        resistance = max(resistance, 5 * dominion_aura)
    return resistance


def aegis_penalty(aegis_level: int) -> int:
    """What the Aegis of the Hearth takes from the Casting Total of a
    foreign spell cast inside it: half its level, rounded down."""
    return -round_down(aegis_level / 2)
