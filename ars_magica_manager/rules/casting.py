"""Casting Scores and Casting Totals (STORY-802).

    Casting Score = Technique + Form + Stamina - Encumbrance + aura modifier
                    + words and gestures + Spell Mastery + 2 per pawn of vis
                    (+ Artes Liberales + Philosophiae for a Ritual)

- Formulaic: Casting Total = Casting Score + die (simple when calm, stress
  under pressure). Total >= level: cast; up to 10 short: cast, 1 Fatigue
  level; more: fails, 1 Fatigue level.
- Ritual: Casting Score + Artes Liberales + Philosophiae + stress die; one
  pawn of vis per magnitude; long-term Fatigue by how far it falls short.
- Spontaneous: fatiguing (Casting Score + stress die) / 2, costing a Fatigue
  level; non-fatiguing Casting Score / 5, no die. The source gives no
  rounding, so both round down (the default rule).
- With requisites, each Art counts at the lowest of it and its requisites.
- Botch dice: 1, +1 per pawn of vis, +1 per point of a non-Magic aura (x2 in
  a regio), +2 fast casting, -1 per point of Mastery (Golden Cord too, but
  never to 0 that way).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..arts import FORMS, TECHNIQUES
from ..models import Character, Saga, Spell, VirtueFlawInstance
from . import effects, options, realms, scores
from .breakdown import Breakdown, Line
from .derived import carried_load, encumbrance
from .lab import ability_score, art_score
from .rounding import round_down

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Seven: Hermetic Magic, Casting "
    "Spells "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Seven:"
    "_Hermetic_Magic#Casting_Spells)"
)

#: Words and gestures (Casting Score modifiers).
WORDS: dict[str, int] = {"Loud": 1, "Firm": 0, "Quiet": -5, "None": -10}
GESTURES: dict[str, int] = {"Exaggerated": 1, "Bold": 0, "Subtle": -2, "None": -5}


@dataclass(frozen=True)
class Outcome:
    cast: bool
    fatigue: int
    #: Formulaic Fatigue is short-term; a Ritual's is long-term.
    long_term: bool = False


def _lowest(magus: Character, art: str, requisites: Sequence[str]) -> tuple[str, int]:
    """The Art (among `art` and its same-kind requisites) with the lowest
    score, counting fixed bonuses."""
    kind = TECHNIQUES if art in TECHNIQUES else FORMS
    candidates = [art, *(r for r in requisites if r in kind)]
    scored = [(name, sum(art_score(magus, name))) for name in candidates]
    return min(scored, key=lambda pair: pair[1])


def casting_score(
    magus: Character,
    technique: str,
    form: str,
    *,
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
    requisites: Sequence[str] = (),
    words: str = "Firm",
    gestures: str = "Bold",
    mastery: int = 0,
    vis_pawns: int = 0,
    ritual: bool = False,
    spontaneous: bool = False,
) -> Breakdown:
    """The Casting Score, with its terms. A Ritual uses loud words and
    exaggerated gestures at some point, so `words` and `gestures` don't
    apply to it."""
    lines: list[Line] = []
    for art in (technique, form):
        name, score = _lowest(magus, art, requisites)
        label = art if name == art else f"{art} (requisite {name})"
        lines.append(Line(label, amount=score, source=SOURCE))
    lines.append(Line("Stamina", amount=magus.characteristics.stamina, source=SOURCE))
    load = carried_load(magus.inventory)
    enc = encumbrance(load, magus.characteristics.strength)
    if enc:
        lines.append(Line("Encumbrance", amount=-enc, source=SOURCE))
    lines.append(
        Line(
            f"Aura ({aura_realm} {aura})",
            amount=realms.aura_modifier(realms.HERMETIC, aura_realm, aura),
            source=realms.SOURCE,
        )
    )
    if not ritual:
        if WORDS[words]:
            lines.append(Line(f"{words} words", amount=WORDS[words], source=SOURCE))
        if GESTURES[gestures]:
            lines.append(
                Line(f"{gestures} gestures", amount=GESTURES[gestures], source=SOURCE)
            )
    if mastery:
        lines.append(Line("Spell Mastery", amount=mastery, source=SOURCE))
    if vis_pawns and not ritual:
        lines.append(
            Line(f"{vis_pawns} pawns of vis", amount=2 * vis_pawns, source=SOURCE)
        )
    if ritual:
        for ability in ("Artes Liberales", "Philosophiae"):
            score = sum(ability_score(magus, ability))
            if score:
                lines.append(Line(ability, amount=score, source=SOURCE))
    base = sum(line.amount or 0 for line in lines)
    kind = "spontaneous_total" if spontaneous else "casting_total"
    activity = None if spontaneous else ("ritual" if ritual else "formulaic")
    found = [
        e
        for e in effects.collect([scores.character_source(magus.virtues_flaws)], kind)
        if e.modifier.activity in (None, activity)
        and (
            e.target is None
            or e.target.casefold() in (technique.casefold(), form.casefold())
        )
    ]
    combined = effects.combine(
        base, [e for e in found if e.modifier.amount is not None]
    )
    # A multiplier (Deficient Art) acts on the Casting Total, die included,
    # so it's listed but left out of the score: see casting_total().
    multipliers = [
        Line(e.entry.name, multiplier=e.modifier.multiplier, source="character")
        for e in found
        if e.modifier.multiplier is not None
    ]
    return Breakdown(
        total=combined.total, lines=lines + combined.lines[1:] + multipliers
    )


def casting_total(score: Breakdown, die: int) -> int:
    """A Casting Total: the score plus the die, then any multiplier the
    score carries (Deficient Art halves it), rounded down."""
    total: float = score.total + die
    for line in score.lines:
        if line.multiplier is not None:
            total *= line.multiplier
    return round_down(total)


def spell_casting_score(
    magus: Character,
    spell: Spell,
    *,
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
    mastery: int = 0,
    **kwargs,
) -> Breakdown:
    return casting_score(
        magus,
        spell.technique,
        spell.form,
        aura=aura,
        aura_realm=aura_realm,
        requisites=spell.requisites,
        mastery=mastery,
        ritual=spell.ritual,
        **kwargs,
    )


def formulaic_outcome(total: int, level: int) -> Outcome:
    short = level - total
    if short <= 0:
        return Outcome(True, 0)
    return Outcome(short <= 10, 1)


def ritual_outcome(total: int, level: int) -> Outcome:
    short = level - total
    if short <= 0:
        return Outcome(True, 1, long_term=True)
    if short <= 5:
        return Outcome(True, 2, long_term=True)
    if short <= 10:
        return Outcome(True, 3, long_term=True)
    if short <= 15:
        return Outcome(False, 4, long_term=True)
    return Outcome(False, 5, long_term=True)


def spontaneous_fatiguing(score: int, die: int) -> int:
    return round_down((score + die) / 2)


def spontaneous_non_fatiguing(score: int) -> int:
    return round_down(score / 5)


def botch_dice(
    *,
    vis_pawns: int = 0,
    aura_realm: str = realms.HERMETIC,
    aura: int = 0,
    in_regio: bool = False,
    fast: bool = False,
    mastery: int = 0,
    golden_cord: int = 0,
    infernal_vis_pawns: int = 0,
    saga: Saga | None = None,
    virtues_flaws: Sequence[VirtueFlawInstance] = (),
) -> int:
    """How many botch dice a stressed casting roll that shows 0 rolls.
    Infernal vis (counted in `vis_pawns` too) doubles them; with the saga's
    harsher option, each pawn adds 3 instead (vis sordida). The caster's
    Virtues and Flaws (Cautious Sorcerer, Careless Sorcerer, Deaf...) count
    before the Golden Cord and Mastery reduce them (STORY-820); spells are
    cast with words and gestures."""
    dice = 1 + vis_pawns + (2 if fast else 0)
    if infernal_vis_pawns:
        if options.is_on(saga, "harsher_infernal_vis"):
            dice += 2 * infernal_vis_pawns  # +3 per pawn, 1 of it counted above
        else:
            dice *= 2
    dice += realms.extra_botch_dice(
        realms.HERMETIC, aura_realm, aura, in_regio=in_regio
    )
    change, _ = scores.botch_dice_change(
        virtues_flaws, ("casting", "casting_words", "casting_gestures")
    )
    dice = scores.with_botch_change(dice, change)
    if golden_cord:
        dice = max(1, dice - golden_cord)  # the cord can't take it to 0
    return max(0, dice - mastery)  # Mastery can
