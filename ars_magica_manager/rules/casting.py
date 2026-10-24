"""Casting Scores and Casting Totals.

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
- Words and gestures: Mute or No Hands cast as with no words or gestures;
  Quiet Magic and Subtle Magic take 5 off those penalties (to 0), Deft
  Form all of them in its Form.
- Fatigue: Enfeebled doubles the levels a spell costs, Withstand Casting
  takes one off (never below 1) and Vulnerable Casting adds one; Mythic
  Blood costs none for a Formulaic spell cast up to 10 short and three
  fewer for a Ritual.
- A hybrid magus (rules.hybrid_magic): Holy or Chthonic Magic changes
  what an aura adds, and a Ritual may add Method + Power instead of Artes
  Liberales + Philosophiae.
- Botch dice: 1, +1 per pawn of vis, +1 per point of a non-Magic aura (x2 in
  a regio), +2 fast casting, -1 per point of Mastery (Golden Cord too, but
  never to 0 that way).

No screen uses formulaic_outcome(), ritual_outcome(), tablet_outcome(),
spontaneous_fatiguing(), spontaneous_non_fatiguing() yet: they are the rules
for screens still to come, and only the tests call them.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from ..arts import FORMS, TECHNIQUES
from ..models import Character, Saga, Spell, VirtueFlawInstance
from . import effects, options, realms, scores
from . import hybrid_magic as hybrid
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
    label, amount = hybrid.aura_label(magus, aura_realm, aura)
    lines.append(Line(label, amount=amount, source=realms.SOURCE))
    for kind, chosen, table, label in (
        ("casting_words", words, WORDS, "words"),
        ("casting_gestures", gestures, GESTURES, "gestures"),
    ):
        amount, name = _voice(magus, kind, form, 0 if ritual else table[chosen])
        if amount:
            lines.append(
                Line(name or f"{chosen} {label}", amount=amount, source=SOURCE)
            )
    if mastery:
        lines.append(Line("Spell Mastery", amount=mastery, source=SOURCE))
    if vis_pawns and not ritual:
        lines.append(
            Line(f"{vis_pawns} pawns of vis", amount=2 * vis_pawns, source=SOURCE)
        )
    if ritual:
        lines += _ritual_lines(magus)
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
    combined = effects.combine(base, [e for e in found if e.amount is not None])
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


def _ritual_lines(magus: Character) -> list[Line]:
    """Artes Liberales + Philosophiae, or a hybrid magus's Method +
    Power when better."""
    learned = [
        Line(ability, amount=score, source=SOURCE)
        for ability in ("Artes Liberales", "Philosophiae")
        if (score := sum(ability_score(magus, ability)))
    ]
    pair = hybrid.ritual_pair(magus)
    if pair is None or pair.total <= sum(line.amount or 0 for line in learned):
        return learned
    return [
        Line(
            f"{pair.method} + {pair.power} ({pair.style.name})",
            amount=pair.total,
            source=pair.style.source,
        )
    ]


def _voice(magus: Character, kind: str, form: str, base: int) -> tuple[int, str]:
    """The words (or gestures) term: the chosen one's, or a Flaw's when
    worse (Mute casts as with no words), less any Virtue's relief (Quiet
    Magic), never past 0; and the Flaw it comes from, if any."""
    found = [
        e
        for e in effects.collect([scores.character_source(magus.virtues_flaws)], kind)
        if e.target is None or e.target.casefold() == form.casefold()
    ]
    flaws = [e for e in found if (e.amount or 0) < 0]
    amount, name = base, ""
    worst = min(flaws, key=lambda e: e.amount or 0, default=None)
    if worst is not None and (worst.amount or 0) < amount:
        amount, name = int(worst.amount or 0), worst.entry.name
    relief = sum(int(e.amount or 0) for e in found if e not in flaws)
    if amount < 0 and relief:
        amount = min(0, amount + relief)
    return amount, name


def fatigue_levels(
    levels: int, virtues_flaws: Sequence[VirtueFlawInstance], activity: str | None
) -> int:
    """The Fatigue levels a spell costs the caster, from the `levels` the
    rules give: Enfeebled doubles them, Withstand and Vulnerable Casting
    take one off (never below 1) or add one, Mythic Blood takes them off
    for its kind of casting. A spell that costs none still costs none."""
    if levels <= 0:
        return levels
    found = effects.collect(
        [scores.character_source(virtues_flaws)], "casting_fatigue", activity=activity
    )
    for e in found:
        if e.modifier.multiplier is not None:
            levels = round_down(levels * e.modifier.multiplier)
    general = sum(int(e.amount or 0) for e in found if e.modifier.activity is None)
    levels = max(1, levels + general)
    own = sum(int(e.amount or 0) for e in found if e.modifier.activity is not None)
    return max(0, levels + own)


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
    **kwargs: Any,
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


TABLET_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Eight: Laboratory, Casting "
    "Tablets (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Eight:_Laboratory)"
)


def tablet_casting_score(
    magus: Character,
    spell: Spell,
    *,
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
) -> Breakdown:
    """Casting from a Casting Tablet: Stamina + Technique + Form + Aura
    (with Virtues, Flaws and requisites), no Mastery, vis or words and
    gestures -- the author fixed the rest. The same for a Ritual."""
    return casting_score(
        magus,
        spell.technique,
        spell.form,
        aura=aura,
        aura_realm=aura_realm,
        requisites=spell.requisites,
    )


@dataclass(frozen=True)
class TabletOutcome:
    cast: bool
    fatigue: int
    warping: int = 0
    #: Two or more Warping Points: a check for Twilight.
    twilight: bool = False
    #: A Ritual's Fatigue is long-term; a Formulaic spell's short-term.
    long_term: bool = False


#: Casting Total - spell level: (at least, Fatigue levels, Warping Points);
#: anything lower fails.
TABLET_BANDS: tuple[tuple[int, int, int], ...] = (
    (0, 1, 0),
    (-10, 2, 0),
    (-20, 3, 0),
    (-30, 4, 1),
)


def magnitude(level: int) -> int:
    """A spell's magnitude: its level / 5, rounded up (at least 1)."""
    return max(1, -(-level // 5))


def tablet_outcome(total: int, level: int, *, ritual: bool = False) -> TabletOutcome:
    """What casting from a tablet does (the table replaces the usual one)."""
    margin = total - level
    for floor, fatigue, warping in TABLET_BANDS:
        if margin >= floor:
            return TabletOutcome(True, fatigue, warping, long_term=ritual)
    points = magnitude(level)
    return TabletOutcome(False, 5, points, twilight=points >= 2, long_term=ritual)


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
    magus: Character | None = None,
) -> int:
    """How many botch dice a stressed casting roll that shows 0 rolls.
    Infernal vis (counted in `vis_pawns` too) doubles them; with the saga's
    harsher option, each pawn adds 3 instead (vis sordida). A foreign aura
    adds its points, twice that in a regio level, unless `magus` is attuned
    to it (Faerie Magic). The caster's
    Virtues and Flaws (Cautious Sorcerer, Careless Sorcerer, Deaf...) count
    before the Golden Cord and Mastery reduce them; spells are
    cast with words and gestures."""
    dice = 1 + vis_pawns + (2 if fast else 0)
    if infernal_vis_pawns:
        if options.is_on(saga, "harsher_infernal_vis"):
            dice += 2 * infernal_vis_pawns  # +3 per pawn, 1 of it counted above
        else:
            dice *= 2
    if magus is not None:
        dice += hybrid.foreign_botch_dice(magus, aura_realm, aura, in_regio=in_regio)
    else:
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
