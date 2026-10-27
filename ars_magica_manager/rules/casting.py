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
  a regio), +2 fast casting, +1 for a failed Concentration roll, -1 per
  point of Mastery (Golden Cord too, but never to 0 that way). Each zero
  on them is a Warping Point; two or more from one botch risk Twilight
  (DE p. 227).
- Dedicated vis of the spell's own Technique and Form adds +4 a pawn, not
  +2, and its pawns count double for botch dice (RoP: Magic p. 122).
- Options (DE pp. 216-218): fast casting (Spontaneous, or a spell with the
  Fast Casting Mastery ability) takes 10 off the score, adds 2 botch dice
  and allows no vis; ceremonial casting adds Artes Liberales +
  Philosophiae (at least one with experience) and props (+1 to +5),
  instead of words and gestures. Vis is limited to the score in its Art;
  extra pawns on a Ritual still add +2 each.
- Spell Mastery's special abilities (DE pp. 225-226) are matched by name:
  Quiet Casting (5 off the words penalty, each), Still Casting (no
  gestures penalty), Penetration (the score added to Penetration), and the
  rest shown with the spell.
- A talisman's attunement: the best one that applies adds to the score
  while the magus touches it (DE p. 260).
- A Deficiency halves a total that uses its Art, as a requisite too (DE
  pp. 125, 312). Method Caster's +3 is lost with any other words or
  gestures (DE p. 98).
- A Ritual's Fatigue past unconsciousness becomes a wound: one level more
  Light, two Medium, three Heavy, four Incapacitating (DE p. 213).

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
from . import (
    aura_kinds,
    casting_virtues,
    effects,
    enchantment,
    options,
    realm_insight,
    realms,
    scores,
)
from . import hybrid_magic as hybrid
from .breakdown import Breakdown, Line
from .derived import carried_load, encumbrance, fatigue_penalty, wound_penalty
from .lab import ability_score, art_score
from .rounding import round_down

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 7: Hermetic Magic, Casting Spells, "
    "pp. 213-218"
)
MASTERY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 7: Hermetic Magic, Spell Mastery, "
    "pp. 225-226"
)
BOTCH_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 7: Hermetic Magic, Botches, p. 227"
)
TALISMAN_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Talisman, p. 260"
)
FAST_PENALTY = -10
FAST_BOTCH_DICE = 2
MOST_PROPS = 5
METHOD_CASTER = "vf_method_caster"
CEREMONIAL_SPONTANEOUS = "vf_ceremonial_spontaneous_magic"
UNSTRUCTURED_CASTER = "vf_unstructured_caster"
WEAK_SPONTANEOUS = "vf_weak_spontaneous_magic"
DIFFICULT_SPONTANEOUS = "vf_difficult_spontaneous_magic"
DIEDNE_MAGIC = "vf_diedne_magic"
#: How a magus may cast Spontaneous spells (spontaneous_mode).
NORMAL, WEAK, DIFFICULT, NO_SPONTANEOUS, DIEDNE = (
    "normal",
    "weak",
    "difficult",
    "none",
    "diedne",
)
#: The Mastery special abilities the app reads, by the name a magus gives
#: them (DE pp. 225-226).
QUIET_CASTING = "quiet casting"
STILL_CASTING = "still casting"
FAST_CASTING = "fast casting"
CEREMONIAL_CASTING = "ceremonial casting"
PENETRATION_MASTERY = "penetration"
RESISTANCE_MASTERY = "magic resistance"
IMPERTURBABLE = "imperturbable casting"
MULTIPLE_CASTING = "multiple casting"
PRECISE_CASTING = "precise casting"
QUICK_CASTING = "quick casting"
#: A Ritual's Fatigue past unconsciousness: the wound for each level more.
RITUAL_WOUNDS = ("light", "medium", "heavy", "incapacitating")

#: Words and gestures (Casting Score modifiers).
WORDS: dict[str, int] = {"Loud": 1, "Firm": 0, "Quiet": -5, "None": -10}
#: A speech impediment: -2 to the Casting Score of a spell cast with words.
AFFLICTED_TONGUE = "vf_afflicted_tongue"
AFFLICTED_TONGUE_PENALTY = -2
AFFLICTED_SOURCE = "Ars Magica Definitive Edition, Afflicted Tongue, p. 119"
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
    fast: bool = False,
    ceremonial: bool = False,
    props: int = 0,
    talisman: int = 0,
    mastery_abilities: dict[str, int] | None = None,
    sordida_pawns: int = 0,
    dedicated_pawns: int = 0,
    aura_kind: str = "",
) -> Breakdown:
    """The Casting Score, with its terms. `aura_kind` is the aura's kind
    (rules.aura_kinds): a Magic aura aligned with one of the spell's Arts
    counts again (RoP: Magic p. 16). A Ritual or ceremonial casting
    uses loud words and exaggerated gestures at some point, so `words` and
    `gestures` don't apply to it. A Ritual's `vis_pawns` are those beyond
    what it needs, each +2; fast casting allows none. `mastery_abilities`
    are the spell's Mastery special abilities (mastery_counts).
    `sordida_pawns` of them are Infernal vis under the Harsher Infernal
    vis option: +5 each instead of +2 (RoP: The Infernal p. 19).
    `dedicated_pawns` of them are dedicated vis of the spell's own
    Technique and Form: +4 each (RoP: Magic p. 122)."""
    abilities = mastery_abilities or {}
    ritual, ceremonial = _how_cast(magus, spontaneous, ritual, ceremonial)
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
    # Wounds and Fatigue take from every roll and total (DE pp. 403-404).
    wounded = wound_penalty(magus.wounds, magus.virtues_flaws)
    if wounded:
        lines.append(Line("Wounds", amount=wounded, source=SOURCE))
    tired = fatigue_penalty(magus.fatigue_level, magus.virtues_flaws)
    if tired:
        lines.append(Line("Fatigue", amount=tired, source=SOURCE))
    label, amount = hybrid.aura_label(
        magus, aura_realm, aura, ritual=ritual, casting=True
    )
    lines.append(Line(label, amount=amount, source=realms.SOURCE))
    lines += aura_kinds.aligned_lines(
        aura_kind, aura_realm, aura, (technique, form, *requisites)
    )
    whole = ritual or ceremonial
    relief = {
        "casting_words": 5 * abilities.get(QUIET_CASTING, 0),
        "casting_gestures": 5 if abilities.get(STILL_CASTING) else 0,
    }
    for kind, chosen, table, label in (
        ("casting_words", words, WORDS, "words"),
        ("casting_gestures", gestures, GESTURES, "gestures"),
    ):
        amount, name = _voice(
            magus, kind, form, 0 if whole else table[chosen], relief[kind]
        )
        if amount:
            lines.append(
                Line(name or f"{chosen} {label}", amount=amount, source=SOURCE)
            )
    if words != "None" and _has(magus, AFFLICTED_TONGUE):
        lines.append(
            Line(
                "Afflicted Tongue",
                amount=AFFLICTED_TONGUE_PENALTY,
                source=AFFLICTED_SOURCE,
            )
        )
    if mastery:
        lines.append(Line("Spell Mastery", amount=mastery, source=MASTERY_SOURCE))
    if fast:
        lines.append(Line("Fast casting", amount=FAST_PENALTY, source=SOURCE))
    elif vis_pawns:
        lines += _vis_lines(
            vis_pawns, sordida_pawns, ritual=ritual, dedicated=dedicated_pawns
        )
    if ritual or ceremonial:
        lines += _ritual_lines(magus, aura_realm, aura)
    if ceremonial and props:
        lines.append(
            Line(
                "Ceremonial props",
                amount=max(0, min(props, MOST_PROPS)),
                source=SOURCE,
            )
        )
    if talisman:
        lines.append(
            Line("Talisman attunement", amount=talisman, source=TALISMAN_SOURCE)
        )
    base = sum(line.amount or 0 for line in lines)
    kind = "spontaneous_total" if spontaneous else "casting_total"
    activity = None if spontaneous else ("ritual" if ritual else "formulaic")
    own = (technique.casefold(), form.casefold())
    used = (*own, *(r.casefold() for r in requisites))
    # Method Caster's bonus needs the method: firm words, bold gestures.
    method = whole or (words, gestures) == ("Firm", "Bold")
    found = [
        e
        for e in effects.collect([scores.character_source(magus.virtues_flaws)], kind)
        if e.modifier.activity in (None, activity)
        and (method or e.entry.id != METHOD_CASTER)
        and (
            e.target is None
            # A Deficiency counts where its Art is a requisite too.
            or e.target.casefold()
            in (used if e.modifier.multiplier is not None else own)
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


def _ritual_lines(
    magus: Character, aura_realm: str = realms.HERMETIC, aura: int = 0
) -> list[Line]:
    """Artes Liberales + Philosophiae (one of them the aura's realm's Lore
    under Insight of the Realms, when better), or a hybrid magus's Method +
    Power when better."""
    found = {
        ability: sum(ability_score(magus, ability))
        for ability in realm_insight.LEARNING
    }
    chosen = realm_insight.learning_scores(found, magus, aura_realm, aura)
    learned = [
        Line(
            label,
            amount=score,
            source=SOURCE if label in found else realm_insight.SOURCE,
        )
        for label, score in chosen.items()
        if score
    ]
    # (Ceremonial casting needs experience in one of them: can_ceremonial.)
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


def _voice(
    magus: Character, kind: str, form: str, base: int, mastered: int = 0
) -> tuple[int, str]:
    """The words (or gestures) term: the chosen one's, or a Flaw's when
    worse (Mute casts as with no words), less any Virtue's relief (Quiet
    Magic) and the spell's Mastery (`mastered`: Quiet or Still Casting),
    never past 0; and the Flaw it comes from, if any."""
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
    relief = sum(int(e.amount or 0) for e in found if e not in flaws) + mastered
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
    casting_requisites: Sequence[str] = (),
    **kwargs: Any,
) -> Breakdown:
    """The spell's Casting Score: its own requisites and any casting
    requisites chosen for this casting count (DE p. 312)."""
    return casting_score(
        magus,
        spell.technique,
        spell.form,
        aura=aura,
        aura_realm=aura_realm,
        requisites=[*spell.requisites, *casting_requisites],
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
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Casting Tablets, pp. 263-264"
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


def _how_cast(
    magus: Character, spontaneous: bool, ritual: bool, ceremonial: bool
) -> tuple[bool, bool]:
    """(ritual, ceremonial) as the magus's Flaws make them: Ceremonial
    Spontaneous Magic casts Spontaneous spells only ceremonially (DE p.
    122); Unstructured Caster casts Formulaic spells as Rituals, with their
    vis (DE p. 149)."""
    held = {vf.vf_id for vf in magus.virtues_flaws}
    if spontaneous and CEREMONIAL_SPONTANEOUS in held:
        ceremonial = True
    if not spontaneous and not ritual and UNSTRUCTURED_CASTER in held:
        ritual = True
    return ritual, ceremonial


def spontaneous_mode(magus: Character) -> str:
    """Which divisions a magus's Spontaneous magic may use: Weak
    Spontaneous Magic only / 5, never exerting (DE p. 153); Difficult only
    exerting, / 2 (p. 126); both, none at all; Diedne Magic / 5 or / 2 on a
    stress die without Fatigue, and the lowest Art doubled exerting (p. 76)."""
    held = {vf.vf_id for vf in magus.virtues_flaws}
    weak, difficult = WEAK_SPONTANEOUS in held, DIFFICULT_SPONTANEOUS in held
    if weak and difficult:
        return NO_SPONTANEOUS
    if weak:
        return WEAK
    if difficult:
        return DIFFICULT
    return DIEDNE if DIEDNE_MAGIC in held else NORMAL


def non_fatiguing_level(magus: Character, score: Breakdown) -> int | None:
    """The level a Spontaneous spell reaches without Fatigue, before any
    die: score / 5, or score / 2 (plus a stress die) with Diedne Magic;
    None when the magus can't cast without exerting himself."""
    mode = spontaneous_mode(magus)
    if mode in (DIFFICULT, NO_SPONTANEOUS):
        return None
    total: float = score.total
    for line in score.lines:
        if line.multiplier is not None:
            total *= line.multiplier
    return round_down(total / (2 if mode == DIEDNE else 5))


def spontaneous_total(score: Breakdown, die: int | None = None) -> int:
    """A Spontaneous Casting Total from the spontaneous Casting Score
    (casting_score(..., spontaneous=True)): its total / 5 without a die
    (no Fatigue), (total + stress die) / 2 with one (a Fatigue level), with
    any multiplier the score carries (a Deficiency halves it), rounded down
    once."""
    total: float = score.total + (die or 0)
    for line in score.lines:
        if line.multiplier is not None:
            total *= line.multiplier
    return round_down(total / (5 if die is None else 2))


def can_ceremonial(magus: Character) -> bool:
    """Ceremonial casting needs experience in Artes Liberales or
    Philosophiae (DE p. 218)."""
    return any(
        a.name in ("Artes Liberales", "Philosophiae") and a.xp > 0
        for a in magus.abilities
    )


def vis_limit_problem(
    magus: Character, art: str, pawns: int, *, other_art: str = "", other: int = 0
) -> str:
    """Why `pawns` of `art` vis (and `other` of `other_art`) is more than
    the magus can use in one casting: each Art's pawns at most its score
    (DE p. 216). "" when it isn't."""
    for name, count in ((art, pawns), (other_art, other)):
        if name and count > art_score(magus, name)[0]:
            return (
                f"{count} pawns of {name} vis: {magus.name} can use at most "
                f"{art_score(magus, name)[0]} (the {name} score)."
            )
    return ""


def mastery_counts(abilities: Sequence[Any]) -> dict[str, int]:
    """A spell's Mastery special abilities by name (lower case), each the
    times it was taken (Quiet Casting may be taken twice)."""
    found: dict[str, int] = {}
    for ability in abilities:
        name = str(getattr(ability, "name", "")).strip().casefold()
        if name:
            found[name] = found.get(name, 0) + 1
    return found


FAST_CASTER = "vf_fast_caster"
FAST_CASTER_BONUS = 3
TWILIGHT_PRONE = "vf_twilight_prone"
#: Concentration takes three times the Wound Penalty, instead of the
#: normal penalty (DE p. 215).
CONCENTRATION_WOUND_MULTIPLE = 3


def _has(magus: Character, vf_id: str) -> bool:
    return any(vf.vf_id == vf_id for vf in magus.virtues_flaws)


def _wounds(magus: Character) -> int:
    return wound_penalty(magus.wounds, magus.virtues_flaws)


def _fatigue(magus: Character) -> int:
    return fatigue_penalty(magus.fatigue_level, magus.virtues_flaws)


def fast_casting_speed(magus: Character, quick: int = 0) -> int:
    """Fast Casting Speed before the stress die: Quickness + Finesse, +1
    for each Quick Casting on a mastered spell, +3 with Fast Caster, less
    the Wound and Fatigue penalties (DE pp. 80, 217, 226, 404); each spell
    after the first that round takes -6 more."""
    return (
        magus.characteristics.quickness
        + sum(ability_score(magus, "Finesse"))
        + quick
        + (FAST_CASTER_BONUS if _has(magus, FAST_CASTER) else 0)
        + _wounds(magus)
        + _fatigue(magus)
    )


def concentration_base(magus: Character, imperturbable: int = 0) -> int:
    """A Concentration roll before the stress die: Stamina +
    Concentration, + the Mastery score with Imperturbable Casting, with
    three times the Wound Penalty (instead of the normal one) and the
    Fatigue penalty (DE pp. 215, 225, 404)."""
    return (
        magus.characteristics.stamina
        + sum(ability_score(magus, "Concentration"))
        + imperturbable
        + CONCENTRATION_WOUND_MULTIPLE * _wounds(magus)
        + _fatigue(magus)
    )


def aiming_base(magus: Character, precise: int = 0) -> int:
    """An aiming roll before the die: Perception + Finesse, +1 for each
    Precise Casting, less the Wound and Fatigue penalties and -3 for each
    of Clumsy and Inconstant Magic (DE pp. 122, 134); +6 for each
    size step past a basic Individual, -1 for each target of a Multiple
    Casting (DE pp. 223, 226, 404)."""
    return (
        magus.characteristics.perception
        + sum(ability_score(magus, "Finesse"))
        + precise
        + _wounds(magus)
        + _fatigue(magus)
        + casting_virtues.finesse_penalty(magus)
    )


#: What a pawn of Infernal vis adds to a Casting Total under the Harsher
#: Infernal vis option (vis sordida), instead of standard vis's +2.
INFERNAL_VIS_BONUS = 5
INFERNAL_VIS_SOURCE = "Realms of Power: The Infernal, Infernal Vis, p. 19"
#: A pawn of dedicated vis of the spell's own Technique and Form.
DEDICATED_VIS_BONUS = 4
DEDICATED_VIS_SOURCE = "Realms of Power: Magic, Dedicated Vis, p. 122"


def _vis_lines(
    pawns: int, sordida: int, *, ritual: bool, dedicated: int = 0
) -> list[Line]:
    """Vis spent in casting: +2 a pawn, +4 for a pawn of dedicated vis of
    the spell's own Arts, or +5 for a pawn of Infernal vis under the
    Harsher Infernal vis option."""
    label = "extra pawns of vis" if ritual else "pawns of vis"
    sordida = max(0, min(sordida, pawns))
    dedicated = max(0, min(dedicated, pawns - sordida))
    found = []
    if dedicated:
        found.append(
            Line(
                f"{dedicated} {label}, dedicated",
                amount=DEDICATED_VIS_BONUS * dedicated,
                source=DEDICATED_VIS_SOURCE,
            )
        )
    if pawns > sordida + dedicated:
        plain = pawns - sordida - dedicated
        found.append(Line(f"{plain} {label}", amount=2 * plain, source=SOURCE))
    if sordida:
        found.append(
            Line(
                f"{sordida} {label}, Infernal",
                amount=INFERNAL_VIS_BONUS * sordida,
                source=INFERNAL_VIS_SOURCE,
            )
        )
    return found


def infernal_vis_text(saga: Saga | None, pawns: int, **dice: Any) -> str:
    """What `pawns` of Infernal vis do to a casting: its botch dice (with
    `dice`, botch_dice's other terms), and under the harsher option its +5
    a pawn."""
    found = botch_dice(vis_pawns=pawns, infernal_vis_pawns=pawns, saga=saga, **dice)
    if options.is_on(saga, "harsher_infernal_vis"):
        return (
            f"+{INFERNAL_VIS_BONUS * pawns} to the total ({INFERNAL_VIS_BONUS} "
            f"a pawn); {found} botch dice, never fewer than {pawns}"
        )
    return f"{found} botch dice (doubled)"


def botch_warping(zeros: int, *, prone: bool = False) -> tuple[int, bool]:
    """A spell botch's Warping Points (one for each zero on the botch
    dice) and whether they risk Wizard's Twilight: two or more, or one for
    a magus who is Twilight Prone (DE pp. 148, 227)."""
    return max(0, zeros), zeros >= (1 if prone else 2)


def twilight_prone(magus: Character) -> bool:
    return _has(magus, TWILIGHT_PRONE)


def ritual_fatigue(levels_left: int, lost: int) -> tuple[int, str | None]:
    """A Ritual's long-term Fatigue: the levels the magus can lose (down
    to unconscious) and the wound the rest becomes, if any (DE p. 213)."""
    taken = max(0, min(lost, levels_left))
    more = lost - taken
    if more <= 0:
        return taken, None
    return taken, RITUAL_WOUNDS[min(more, len(RITUAL_WOUNDS)) - 1]


def botch_dice(
    *,
    vis_pawns: int = 0,
    aura_realm: str = realms.HERMETIC,
    aura: int = 0,
    in_regio: bool = False,
    boundary_dice: int = 0,
    fast: bool = False,
    distracted: bool = False,
    mastery: int = 0,
    golden_cord: int = 0,
    infernal_vis_pawns: int = 0,
    dedicated_vis_pawns: int = 0,
    saga: Saga | None = None,
    virtues_flaws: Sequence[VirtueFlawInstance] = (),
    magus: Character | None = None,
) -> int:
    """How many botch dice a stressed casting roll that shows 0 rolls.
    Infernal vis (counted in `vis_pawns` too) doubles them (DE p. 422); with
    the saga's harsher option, each pawn adds 3 instead (vis sordida), and
    no Virtue, Golden Cord or Mastery takes them below its pawns (RoP: The
    Infernal p. 19). A foreign aura
    adds its points, twice that in a regio level, unless `magus` is attuned
    to it (Faerie Magic). The caster's
    Virtues and Flaws (Cautious Sorcerer, Careless Sorcerer, Deaf...) count
    before the Golden Cord and Mastery reduce them; spells are
    cast with words and gestures. A failed Concentration roll
    (`distracted`) adds one (DE p. 215). Dedicated vis of the spell's own
    Arts (counted in `vis_pawns` too) counts double (RoP: Magic p. 122).
    A Magic Realm boundary adds its level (`boundary_dice`, from
    sites.boundary_botch_dice) while the aura is Magic, as casting is a
    roll the Magic aura helps (RoP: Magic p. 22).
    """
    dedicated = max(0, min(dedicated_vis_pawns, vis_pawns))
    dice = (
        1
        + vis_pawns
        + dedicated
        + (FAST_BOTCH_DICE if fast else 0)
        + (1 if distracted else 0)
    )
    if hybrid.ignores_infernal_vis(magus):
        infernal_vis_pawns = 0  # Chthonic Magic: no ill effects
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
    if aura_realm == realms.HERMETIC:
        dice += max(0, boundary_dice)
    change, _ = scores.botch_dice_change(
        virtues_flaws, ("casting", "casting_words", "casting_gestures")
    )
    dice = scores.with_botch_change(dice, change)
    if golden_cord:
        dice = max(1, dice - golden_cord)  # the cord can't take it to 0
    dice = max(0, dice - mastery)  # Mastery can
    if infernal_vis_pawns and options.is_on(saga, "harsher_infernal_vis"):
        # Nothing takes vis sordida's botch dice below its pawns.
        dice = max(dice, infernal_vis_pawns)
    return dice


def golden_cord(saga: Saga | None, magus: Character) -> int:
    """The Golden Cord of the magus's bound familiar (0 without one): it
    takes that many botch dice off his spellcasting (DE pp. 227, 267)."""
    if saga is None:
        return 0
    familiar = saga.familiar_of(magus.id)
    return familiar.golden_cord if familiar is not None else 0


def talisman_attunements(saga: Saga | None, magus: Character) -> list[tuple[int, str]]:
    """The attunements of the magus's talisman, best first, as (bonus,
    what it applies to): while touching it, the best that applies adds to
    his Casting Scores (DE p. 260)."""
    if saga is None:
        return []
    device = enchantment.talisman_of(saga, magus)
    if device is None:
        return []
    found = [(a.bonus, a.applies_to or a.shape) for a in device.attunements if a.bonus]
    return sorted(found, key=lambda pair: -pair[0])
