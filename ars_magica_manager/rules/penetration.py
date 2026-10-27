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
halve the Penetration Total (Weak Magic). Against a target with Secret
Name no sympathetic connection works (DE p. 235).

No screen uses aegis_penalty() yet: it is a rule for a screen still to come,
and only the tests call it.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..models import Character, Saga, VirtueFlawInstance, character_age
from . import divine_state, effects, gauntlet, options, realms, senses
from . import hybrid_magic as hybrid
from .breakdown import Breakdown, Line
from .derived import OFFICE_RESISTANCE
from .lab import ability_score, art_score
from .rounding import round_down
from .scores import character_source

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 7: Hermetic Magic, Penetration, "
    "Arcane Connections and Magic Resistance, pp. 215, 219-221"
)
FAITH_SOURCE = "Realms of Power: The Divine, True Faith, pp. 56-61"

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
SECRET_NAME = "vf_secret_name"
SECRET_NAME_SOURCE = "Ars Magica Definitive Edition, Secret Name, p. 235"


def penetration_bonus(
    magus: Character,
    *,
    arcane_connection: str | None = None,
    sympathies: Sequence[Sympathy] = (),
    mastery: int = 0,
    specialty: bool = False,
    target: Character | None = None,
) -> Breakdown:
    """(Penetration + specialty + Penetration Mastery) x the multiplier.
    The sympathetic connections count for nothing against a `target` with
    Secret Name."""
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
        nameless = target is not None and any(
            vf.vf_id == SECRET_NAME for vf in target.virtues_flaws
        )
        if nameless and sympathies:
            lines.append(
                Line(
                    "Secret Name: no sympathetic connection works",
                    amount=0,
                    source=SECRET_NAME_SOURCE,
                )
            )
        for sympathy in () if nameless else sympathies:
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
        e.name
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
    return multiplier, [e.name for e in found]


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
    effect_realm: str = realms.HERMETIC,
) -> Breakdown:
    """A Hermetic magus's Magic Resistance against a spell of `form`: the
    Form, 5 x Parma Magica while raised (Parma less 3 while shared), and the
    aura's modifier; never below 0. Susceptibility to Faerie or Infernal
    Power halves it against `effect_realm`'s effects (DE p. 146)."""
    score, bonus = art_score(magus, form)
    form_part, limited = _resistance_multiplier(magus, "form_resistance", form)
    lines = [
        Line(
            form + (f" ({', '.join(limited)})" if limited else ""),
            amount=round_down((score + bonus) * form_part),
            source=SOURCE,
        )
    ]
    # An apprentice can't invoke his Parma Magica before its final key,
    # given after the Oath (DE p. 169; Apprentices p. 61).
    if parma_raised and not gauntlet.parma_withheld(magus):
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
    label, modifier = hybrid.aura_label(magus, aura_realm, aura)
    if modifier:
        lines.append(Line(label, amount=modifier, source=realms.SOURCE))
    if effect_realm in SUSCEPTIBILITIES and _has(magus, SUSCEPTIBILITIES[effect_realm]):
        lines.append(
            Line(
                f"Susceptibility to {effect_realm} Power",
                multiplier=0.5,
                source=SUSCEPTIBILITY_SOURCE,
            )
        )
    sensitivity, sensitivity_bonus = ability_score(magus, senses.MAGIC_SENSITIVITY)
    if sensitivity + sensitivity_bonus > 0:
        lines.append(
            Line(
                senses.MAGIC_SENSITIVITY,
                amount=-(sensitivity + sensitivity_bonus),
                source=senses.SOURCE,
            )
        )
    total = sum(line.amount or 0 for line in lines)
    if any(line.multiplier for line in lines):
        total = round_down(total / 2)
    return Breakdown(total=max(0, total), lines=lines)


#: Words in a character's religion that make them one of the faithful the
#: Dominion option protects; a blank religion counts, as most of Mythic
#: Europe shares in the Divine.
FAITHFUL = ("christian", "catholic", "orthodox", "jew", "jewish", "muslim", "islam")


def faithful(character: Character) -> bool:
    """A Christian, Jew or Muslim, as the Dominion option reads them."""
    religion = character.background.religion.casefold()
    return not religion.strip() or any(word in religion for word in FAITHFUL)


def faith_magic_resistance(
    character: Character,
    saga: Saga | None = None,
    *,
    dominion_aura: int | None = None,
) -> int:
    """The Magic Resistance a character has without Parma: the highest of
    True Faith's (Score x 10, DE p. 419), a Church office's or crown's
    with the relic they rely on added to it (DE pp. 419-420), and Strong
    Angelic Heritage's Divine Might (DE p. 109). With the saga's optional
    Dominion rule, at least 5 x the Dominion aura for the faithful; the
    aura is where the character lives unless `dominion_aura` says
    otherwise. (Resistances from different sources don't add, but a
    relic's adds to an office's, DE p. 420.)"""
    resistance = max(
        10 * character.background.true_faith_score
        + divine_state.form_resistance(character)
        + (GUARDIAN_ANGEL_MR if _has(character, GUARDIAN_ANGEL) else 0),
        office_resistance(character) + relic_resistance(character),
        angelic_might(character, saga),
    )
    if saga is not None and options.is_on(saga, "dominion_magic_resistance"):
        if dominion_aura is None:
            aura, realm = realms.present_aura(saga, character)
            dominion_aura = aura if realm == "Divine" else 0
        if faithful(character):
            resistance = max(resistance, 5 * dominion_aura)
    return resistance


def aegis_penalty(aegis_level: int) -> int:
    """What the Aegis of the Hearth takes from the Casting Total of a
    foreign spell cast inside it: half its level, rounded down."""
    return -round_down(aegis_level / 2)


# -- resistance by office, relic, heritage and realm --

SUSCEPTIBILITY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 4: Susceptibility, p. 146"
)
SUSCEPTIBILITIES = {
    "Faerie": "vf_susceptibility_to_faerie_power",
    "Infernal": "vf_susceptibility_to_infernal_power",
}
OFFICES = OFFICE_RESISTANCE
STRONG_ANGELIC_HERITAGE = "vf_strong_angelic_heritage"
#: A Guardian Angel's Magic Resistance, which adds to True Faith's but to
#: nothing else (DE p. 84).
GUARDIAN_ANGEL, GUARDIAN_ANGEL_MR = "vf_guardian_angel", 15
ANGELIC_YEARS = 20


def _has(character: Character, vf_id: str) -> bool:
    return any(vf.vf_id == vf_id for vf in character.virtues_flaws)


def office_resistance(character: Character) -> int:
    """An office's Magic Resistance; none while its Commanding Aura is
    withdrawn (a legatus missus astray, or one excommunicated, until
    penance: DE pp. 74, 420)."""
    if divine_state.aura_withdrawn(character):
        return 0
    return OFFICES.get(character.background.church_rank, 0)


def office_soak(character: Character) -> int:
    """An office's Soak bonus: its Magic Resistance / 5 (a relic's adds
    nothing to Soak) (DE p. 420)."""
    return office_resistance(character) // 5


def relic_resistance(character: Character) -> int:
    """Ten times the Faith of the one relic the character relies on (DE p.
    419)."""
    return 10 * max(0, character.background.relic_faith)


def angelic_might(character: Character, saga: Saga | None) -> int:
    """Strong Angelic Heritage's Divine Might, age / 20 (rounded down),
    which is Magic Resistance (DE p. 109); 0 without the Virtue or an age."""
    if saga is None or not _has(character, STRONG_ANGELIC_HERITAGE):
        return 0
    age = character_age(character.background.year_born, saga.current_year)
    return max(0, (age or 0) // ANGELIC_YEARS)


def creature_resistance(might: int, realm: str, aura_realm: str, aura: int) -> int:
    """A creature's Magic Resistance: its Might + the aura's modifier for
    its realm (DE p. 412)."""
    return max(0, might + realms.aura_modifier(realm, aura_realm, aura))


def resistance_from(character: Character, saga: Saga | None = None) -> str:
    """Where faith_magic_resistance comes from, in words: "Archbishop 10 +
    relic 20", "Strong Angelic Heritage", "True Faith", or "the Dominion"."""
    office, relic = office_resistance(character), relic_resistance(character)
    total = faith_magic_resistance(character, saga)
    if office or relic:
        parts = [f"{character.background.church_rank} {office}"] if office else []
        parts += [f"relic {relic}"] if relic else []
        if office + relic == total:
            return " + ".join(parts)
    if angelic_might(character, saga) == total and total:
        return "Strong Angelic Heritage"
    angel = GUARDIAN_ANGEL_MR if _has(character, GUARDIAN_ANGEL) else 0
    faith = 10 * character.background.true_faith_score
    form = divine_state.form_resistance(character)
    if faith + form + angel == total and total:
        return " + ".join(
            [
                *(["True Faith"] if faith else []),
                *(["Divine Form"] if form else []),
                *(["Guardian Angel"] if angel else []),
            ]
        )
    return "the Dominion"
